from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, HiddenMovie, MoviePetition, PetitionVote, Purchase
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Sum
from cart.models import Item 

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    if request.user.is_authenticated:
        hidden_movie_ids = HiddenMovie.objects.filter(user=request.user).values_list('movie_id', flat=True)
        movies = movies.exclude(id__in=hidden_movie_ids)
        
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    template_data['search_term'] = search_term 
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def hide_movie(request, id):
    movie = get_object_or_404(Movie, id=id)
    HiddenMovie.objects.get_or_create(user=request.user, movie=movie)
    return redirect('movies.index')

@login_required
def hidden_movies(request):
    hidden = HiddenMovie.objects.filter(user=request.user)
    template_data = {
        'title': 'Hidden Movies',
        'hidden_movies': [h.movie for h in hidden]
    }
    return render(request, 'movies/hidden.html', {'template_data': template_data})

@login_required
def unhide_movie(request, id):
    hidden = get_object_or_404(HiddenMovie, user=request.user, movie_id=id)
    hidden.delete()
    return redirect('movies.hidden')

# Your existing views stay the same...
# (index, show, create_review, edit_review, delete_review, hide_movie, hidden_movies, unhide_movie)

# Add these new views at the bottom:

def petitions_list(request):
    """Display all movie petitions, sorted by vote count"""
    petitions = MoviePetition.objects.filter(is_approved=False, is_rejected=False)
    
    # Add vote count to each petition for sorting
    petitions_with_votes = []
    for petition in petitions:
        petition.vote_count = petition.get_vote_count()
        petition.user_voted = petition.user_has_voted(request.user)
        petitions_with_votes.append(petition)
    
    # Sort by vote count (highest first)
    petitions_with_votes.sort(key=lambda x: x.vote_count, reverse=True)
    
    template_data = {
        'title': 'Movie Petitions',
        'petitions': petitions_with_votes
    }
    return render(request, 'movies/petitions_list.html', {'template_data': template_data})


@login_required
def create_petition(request):
    """Allow users to create a new movie petition"""
    if request.method == 'GET':
        template_data = {
            'title': 'Request a Movie'
        }
        return render(request, 'movies/create_petition.html', {'template_data': template_data})
    
    elif request.method == 'POST':
        movie_title = request.POST.get('movie_title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not movie_title or not description:
            messages.error(request, 'Both movie title and description are required.')
            return redirect('movies.create_petition')
        
        # Create the petition
        petition = MoviePetition()
        petition.movie_title = movie_title
        petition.description = description
        petition.petitioner = request.user
        petition.save()
        
        messages.success(request, f'Your petition for "{movie_title}" has been created!')
        return redirect('movies.petitions_list')


@login_required
def vote_petition(request, petition_id):
    """Allow users to vote for a movie petition"""
    petition = get_object_or_404(MoviePetition, id=petition_id)
    
    # Check if user already voted
    if petition.user_has_voted(request.user):
        messages.info(request, 'You have already voted for this petition.')
    else:
        # Create the vote
        vote = PetitionVote()
        vote.petition = petition
        vote.user = request.user
        vote.save()
        
        messages.success(request, f'Your vote for "{petition.movie_title}" has been recorded!')
    
    return redirect('movies.petitions_list')


@login_required
def unvote_petition(request, petition_id):
    """Allow users to remove their vote from a petition"""
    petition = get_object_or_404(MoviePetition, id=petition_id)
    
    try:
        vote = PetitionVote.objects.get(petition=petition, user=request.user)
        vote.delete()
        messages.success(request, f'Your vote for "{petition.movie_title}" has been removed.')
    except PetitionVote.DoesNotExist:
        messages.info(request, 'You have not voted for this petition.')
    
    return redirect('movies.petitions_list')

@staff_member_required
def top_customer_view(request):
    top_customer = Item.objects.values('order__user__username').annotate(
        movie_count=Sum('quantity')  # Sum of quantities purchased
    ).order_by('-movie_count').first()
    
    template_data = {
        'title': 'Top Customer',
        'top_customer': top_customer
    }
    return render(request, 'movies/top_customer.html', {'template_data': template_data})