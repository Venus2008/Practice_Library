from django.shortcuts import render,get_object_or_404,redirect
from .models import *
from django.views.generic import DetailView
from django.views import generic
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
User = get_user_model() 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django import forms
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.urls import reverse,reverse_lazy
from django.utils import timezone
from django.views.generic.edit import UpdateView
from django.forms import DateInput
from django.contrib import messages
from .forms import *

@login_required(login_url='/accounts/login')
def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_genres=Genre.objects.count()
    num_specific_book=Book.objects.filter(title__icontains='Life').count()
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres':num_genres,
        'num_specific_book': num_specific_book,
        'num_visits': num_visits,
    }
    return render(request,'index.html', context=context)


class BookListView(LoginRequiredMixin,generic.ListView):
    model=Book
    context_object_name = 'book_list'     # your own name for the list as a template variable
    template_name = 'book_list.html'  # Specify your own template name/location
    paginate_by=5
    login_url = '/accounts/login/'
    

    def book_detail_view(request, pk):
        book = get_object_or_404(Book, pk=pk)
        return render(request, 'book_details.html', {'book': book})
    

class BookDetailView(LoginRequiredMixin,generic.DetailView):
    model=Book
    context_object_name= 'book'
    template_name = 'book_detail.html'
    login_url = '/accounts/login/'
    
    
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context


class AuthorListView(LoginRequiredMixin,generic.ListView):
    model = Author
    context_object_name= 'author_detail'
    template_name = 'author_name.html'
    login_url = '/accounts/login/'

    def author_book_detail_view(request, pk):
        book = get_object_or_404(Book, pk=pk)
        return render(request, 'author_book_details.html', {'book': book})

   
class AuthorbookDetailView(LoginRequiredMixin,generic.DetailView):
    model=Book
    context_object_name='author'
    template_name='author_book_details.html'
    login_url = '/accounts/login/'


class AuthorDetailView(generic.DetailView):
    model = Author
    context_object_name = 'author_detail'
    template_name = '/author_name.html'
    

user, created = User.objects.get_or_create(
    username='Venus',
    defaults={
        'email': 'venuskh.tagline@gmail.com',
        'first_name': 'Venus',
        'last_name': 'Khiraiya'
    }
)

if created:
    user.set_password('mypassword')
    user.save()
    
class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

class BookInstanceForm(forms.ModelForm):
    class Meta:
        model=BookInstance
        fields=['due_back']
        widgets = {
            'due_back': DateInput(attrs={'type': 'date'})  
        }   


    def clean_due_back(self):
        due_date = self.cleaned_data['due_back']
        today = timezone.now().date()
       
        if due_date < today:
            raise ValidationError("Due date cannot be in the past.")
        if due_date > today + datetime.timedelta(weeks=3):
            raise ValidationError("Due date cannot be more than 3 weeks from today.")
        return due_date

            


class BookLoanView(LoginRequiredMixin,UpdateView):
    model=BookInstance
    context_object_name='book_borrow'
    template_name='book_borrow.html'
    form_class=BookInstanceForm

    def form_valid(self, form):
        book_instance=form.save(commit=False)
        book_instance.borrower=self.request.user
        book_instance.status='o'
        book_instance.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('loan-book', kwargs={'pk': self.object.pk})
    
@login_required
def add_book(request):
    if request.method=="POST":
        title=request.POST.get('title')
        author_id = request.POST.get('author_id')
        language=request.POST.get('language')
        summary=request.POST.get('summary')
        isbn=request.POST.get('isbn')
        genre_ids = request.POST.getlist('genre')
        image=request.FILES.get('image')
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            messages.error(request, "Author not found.")
            return redirect('add-book')
        


        book=Book.objects.create(
            title=title,
            language=language,
            summary=summary,
            isbn=isbn,
            author=author,
            image=image,
        )
        if genre_ids:
            book.genre.set(genre_ids) 

        messages.success(request, "Book added successfully!")
        return redirect ('add-book')
    books=Book.objects.all()
    queryset_genres=Genre.objects.all()
    queryset_authors=Author.objects.all()
    context={'books':books,'genres':queryset_genres,'authors':queryset_authors,'is_edit':False,'book':None}
    return render (request, 'book_form.html', context)

@login_required
def delete_book(request,id):
    queryset=Book.objects.get(id=id)
    BookInstance.objects.filter(book=id).delete()
    queryset.delete()
    return redirect ('books')

@login_required
def edit_book(request,id):
    queryset=get_object_or_404(Book,id=id)
    if request.method =='POST':
        title=request.POST.get('title')
        author_id = request.POST.get('author_id')
        language=request.POST.get('language')
        summary=request.POST.get('summary')
        isbn=request.POST.get('isbn')
        genre_ids = request.POST.getlist('genre')
        image=request.FILES.get('image')
        try:
            author = get_object_or_404(Author,id=author_id)
        except Author.DoesNotExist:
            messages.error(request, "Author not found.")
            return redirect('add-book')
        
        queryset.title=title
        queryset.author=author
        queryset.language=language
        queryset.summary=summary
        queryset.isbn=isbn
        queryset.genre.set(genre_ids)
        if image:
            queryset.image=image
        queryset.save()

        messages.success(request, "Book updated successfully!")
        return redirect ('books')
    queryset_author=Author.objects.all()
    queryset_genre=Genre.objects.all()
    return render(request, 'book_form.html', {
        'book': queryset,
        'authors': queryset_author,
        'genres': queryset_genre,
        'is_edit':True
    })

@login_required
def add_author(request):
    if request.method=='POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        date_of_birth=request.POST.get('date_of_birth')
        date_of_death=request.POST.get('date_of_death')
        language=request.POST.get('language')

        Author.objects.create(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            date_of_death=date_of_death,
            language=language,
        )
        return redirect('add-author')
    queryset=Author.objects.all()
    context={'author':queryset}
    return render(request, 'add_author.html',context)


@login_required
def add_genre(request):
    if request.method=='POST':
      name=request.POST.get('name')
      if name:
        Genre.objects.create(name=name)
      return redirect ('add-genre')
      
    queryset=Genre.objects.all()
    return render(request, 'add_genre.html', {'genres': queryset})
    



#--------------------------------------------------------------------------------------------------------------------------------

# class RenewBookForm(forms.Form):
#     renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

#     def clean_renewal_date(self):
#         data = self.cleaned_data['renewal_date']

#         # Check if a date is not in the past.
#         if data < datetime.date.today():
#             raise ValidationError(_('Invalid date - renewal in past'))

#         # Check if a date is in the allowed range (+4 weeks from today).
#         if data > datetime.date.today() + datetime.timedelta(weeks=4):
#             raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

#         # Remember to always return the cleaned data.
#         return data


# def renew_book_librarian(request, pk):
#     book_instance = get_object_or_404(BookInstance, pk=pk)

#     # If this is a POST request then process the Form data
#     if request.method == 'POST':

#         # Create a form instance and populate it with data from the request (binding):
#         form = RenewBookForm(request.POST)

#         # Check if the form is valid:
#         if form.is_valid():
#             # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
#             book_instance.due_back = form.cleaned_data['renewal_date']
#             book_instance.save()

#             # redirect to a new URL:
#             return HttpResponseRedirect(reverse('all-borrowed'))

#     # If this is a GET (or any other method) create the default form.
#     else:
#         proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
#         form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

#     context = {
#         'form': form,
#         'book_instance': book_instance,
#     }

#     return render(request, 'catalog/book_renew_librarian.html', context)