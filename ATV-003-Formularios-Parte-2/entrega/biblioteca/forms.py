from datetime import date
from django import forms

from .models import Author, Book


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["name", "nationality"]
        labels = {
            "name": "Nome",
            "nationality": "Nacionalidade",
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "year", "available", "categories"]
        labels = {
            "title": "Título",
            "author": "Autor",
            "year": "Ano",
            "available": "Disponível",
            "categories": "Categorias",
        }
        widgets = {
            "categories": forms.CheckboxSelectMultiple(),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "")
        title_limpo = " ".join(title.split())
        if len(title_limpo) < 3:
            raise forms.ValidationError(
                "O título precisa ter pelo menos 3 caracteres após a remoção de espaços extras. Informe um título válido."
            )
        return title_limpo

    def clean_year(self):
        year = self.cleaned_data.get("year")
        if year is not None:
            ano_atual = date.today().year
            if year > ano_atual:
                raise forms.ValidationError(
                    f"O ano de publicação não pode ser posterior ao ano atual ({ano_atual}). Informe um ano igual ou anterior a {ano_atual}."
                )
        return year
