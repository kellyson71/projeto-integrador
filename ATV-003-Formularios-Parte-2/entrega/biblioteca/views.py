from django.shortcuts import get_object_or_404, redirect, render

from .forms import AuthorForm, BookForm
from .models import Author, Book


def listar_livros(request):
    livros = Book.objects.select_related("author").prefetch_related("categories")
    return render(request, "biblioteca/lista_livros.html", {"livros": livros})


def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    return render(
        request,
        "biblioteca/author_detail.html",
        {"author": author, "livros": author.books.prefetch_related("categories")},
    )


def author_create(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            return redirect("biblioteca:author_detail", pk=author.pk)
    else:
        form = AuthorForm()
    return render(request, "biblioteca/author_form.html", {"form": form})


def book_form(request, pk=None):
    if pk is not None:
        livro = get_object_or_404(Book, pk=pk)
    else:
        livro = None

    if request.method == "POST":
        form = BookForm(request.POST, instance=livro)
        if form.is_valid():
            livro = form.save()
            return redirect("biblioteca:author_detail", pk=livro.author.pk)
    else:
        form = BookForm(instance=livro)

    return render(request, "biblioteca/book_form.html", {"form": form, "livro": livro})
