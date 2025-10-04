from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('<int:id>/review/create/', views.create_review, name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='movies.delete_review'),
    path('hide/<int:id>/', views.hide_movie, name='movies.hide'),
    path('unhide/<int:id>/', views.unhide_movie, name='movies.unhide'),
    path('hidden/', views.hidden_movies, name='movies.hidden'),
    path('petitions/', views.petitions_list, name='movies.petitions_list'),
    path('petitions/create/', views.create_petition, name='movies.create_petition'),
    path('petitions/<int:petition_id>/vote/', views.vote_petition, name='movies.vote_petition'),
    path('petitions/<int:petition_id>/unvote/', views.unvote_petition, name='movies.unvote_petition'),
]