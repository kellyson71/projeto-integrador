Biblioteca em Django com cadastro e edição de livros via ModelForm (`BookForm`). Uma única view atende novo livro e edição compartilhando o template `book_form.html`, com alternância de título e botão e retorno 404 para livros inexistentes. Ao salvar, redireciona para a página do autor do livro. Há links de edição na lista e na página do autor, com validações no formulário para limpar espaços extras do título (mínimo de 3 caracteres) e impedir ano posterior ao ano atual.

Para rodar: `pip install django`, `python manage.py migrate` e `python manage.py runserver`.
Para executar os testes: `python manage.py test`.
