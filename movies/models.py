from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')

    def __str__(self):
        return str(self.id) + ' - ' + self.name

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
    
class HiddenMovie(models.Model): 
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta: 
        unique_together = ('user', 'movie')

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
    
class MoviePetition(models.Model):
    id = models.AutoField(primary_key=True)
    movie_title = models.CharField(max_length=255)
    description = models.TextField(help_text="Why should this movie be added?")
    petitioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='petitions')
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.id} - {self.movie_title}"
    
    def get_vote_count(self):
        """Returns the total number of votes for this petition"""
        return self.votes.count()
    
    def user_has_voted(self, user):
        """Check if a user has already voted on this petition"""
        if not user.is_authenticated:
            return False
        return self.votes.filter(user=user).exists()
    
class PetitionVote(models.Model):
    id = models.AutoField(primary_key=True)
    petition = models.ForeignKey(MoviePetition, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('petition', 'user') 
        ordering = ['-voted_at']
    
    def __str__(self):
        return f"{self.user.username} voted for {self.petition.movie_title}"