"""
URL configuration for Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('authors/', views.AuthorListView.as_view(), name='book-author'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),  
    path('authors/<int:pk>', views.AuthorbookDetailView.as_view(),name='author-wise-detail' ),
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    # path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
    path('borrow/<uuid:pk>',views.BookLoanView.as_view(), name='loan-book'),
    path('addbook/', views.add_book, name='add-book'),
    path('addgenre/',views.add_genre, name='add-genre'),
    path('addauthor/',views.add_author, name='add-author')
]
