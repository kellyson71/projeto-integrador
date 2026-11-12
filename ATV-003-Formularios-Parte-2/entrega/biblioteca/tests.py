from datetime import date
from django.test import Client, TestCase
from django.urls import reverse

from .models import Author, Book, Category


class AuthorCreateTests(TestCase):
    def setUp(self):
        self.url = reverse("biblioteca:author_create")

    def test_get_mostra_formulario(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Nome")
        self.assertContains(resposta, "Nacionalidade")
        self.assertContains(resposta, "csrfmiddlewaretoken")

    def test_nome_obrigatorio(self):
        resposta = self.client.post(self.url, {"name": "", "nationality": ""})
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Este campo é obrigatório.")
        self.assertEqual(Author.objects.count(), 0)

    def test_nacionalidade_em_branco(self):
        resposta = self.client.post(self.url, {"name": "Machado de Assis", "nationality": ""})
        autor = Author.objects.get()
        self.assertRedirects(resposta, reverse("biblioteca:author_detail", args=[autor.pk]))

    def test_sem_token_csrf_e_rejeitado(self):
        cliente = Client(enforce_csrf_checks=True)
        resposta = cliente.post(self.url, {"name": "Fulano", "nationality": ""})
        self.assertEqual(resposta.status_code, 403)
        self.assertEqual(Author.objects.count(), 0)


class BookCreateTests(TestCase):
    def setUp(self):
        self.url = reverse("biblioteca:book_create")
        self.autor = Author.objects.create(name="Graciliano Ramos", nationality="Brasileira")
        self.cat1 = Category.objects.create(name="Romance")
        self.cat2 = Category.objects.create(name="Regionalismo")

    def test_get_mostra_formulario_novo_livro(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Novo livro")
        self.assertContains(resposta, "<button type=\"submit\">Novo livro</button>")
        self.assertContains(resposta, "Graciliano Ramos")

    def test_categorias_aparecem_como_checkboxes(self):
        resposta = self.client.get(self.url)
        self.assertContains(resposta, 'type="checkbox"')
        self.assertContains(resposta, "Romance")
        self.assertContains(resposta, "Regionalismo")

    def test_criar_livro_com_sucesso_redireciona_para_autor(self):
        dados = {
            "title": "Vidas Secas",
            "author": self.autor.pk,
            "year": 1938,
            "available": True,
            "categories": [self.cat1.pk, self.cat2.pk],
        }
        resposta = self.client.post(self.url, dados)
        livro = Book.objects.get(title="Vidas Secas")
        self.assertRedirects(resposta, reverse("biblioteca:author_detail", args=[self.autor.pk]))
        self.assertEqual(livro.year, 1938)
        self.assertEqual(livro.categories.count(), 2)

    def test_criar_livro_sem_categoria_e_aceito(self):
        dados = {
            "title": "São Bernardo",
            "author": self.autor.pk,
            "year": 1934,
            "available": True,
        }
        resposta = self.client.post(self.url, dados)
        livro = Book.objects.get(title="São Bernardo")
        self.assertRedirects(resposta, reverse("biblioteca:author_detail", args=[self.autor.pk]))
        self.assertEqual(livro.categories.count(), 0)


class BookEditTests(TestCase):
    def setUp(self):
        self.autor = Author.objects.create(name="Clarice Lispector", nationality="Brasileira")
        self.cat = Category.objects.create(name="Ficção")
        self.livro = Book.objects.create(
            title="A Hora da Estrela",
            author=self.autor,
            year=1977,
            available=True,
        )
        self.livro.categories.add(self.cat)
        self.url = reverse("biblioteca:book_edit", args=[self.livro.pk])

    def test_get_abre_preenchido_com_modo_editar_livro(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Editar livro")
        self.assertContains(resposta, "<button type=\"submit\">Editar livro</button>")
        self.assertContains(resposta, "A Hora da Estrela")
        self.assertContains(resposta, "1977")

    def test_post_edita_livro_e_redireciona_para_autor(self):
        dados = {
            "title": "A Hora da Estrela - Edição Especial",
            "author": self.autor.pk,
            "year": 1977,
            "available": False,
            "categories": [self.cat.pk],
        }
        resposta = self.client.post(self.url, dados)
        self.assertRedirects(resposta, reverse("biblioteca:author_detail", args=[self.autor.pk]))
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.title, "A Hora da Estrela - Edição Especial")
        self.assertFalse(self.livro.available)

    def test_editar_livro_inexistente_retorna_404(self):
        url_inexistente = reverse("biblioteca:book_edit", args=[99999])
        resposta_get = self.client.get(url_inexistente)
        self.assertEqual(resposta_get.status_code, 404)
        resposta_post = self.client.post(url_inexistente, {"title": "X", "author": self.autor.pk, "year": 2000})
        self.assertEqual(resposta_post.status_code, 404)


class BookValidationTests(TestCase):
    def setUp(self):
        self.url = reverse("biblioteca:book_create")
        self.autor = Author.objects.create(name="Jorge Amado", nationality="Brasileira")

    def test_espacos_sobrando_no_titulo_sao_removidos_antes_de_salvar(self):
        dados = {
            "title": "   Capitães    da   Areia   ",
            "author": self.autor.pk,
            "year": 1937,
            "available": True,
        }
        resposta = self.client.post(self.url, dados)
        self.assertRedirects(resposta, reverse("biblioteca:author_detail", args=[self.autor.pk]))
        livro = Book.objects.get(author=self.autor)
        self.assertEqual(livro.title, "Capitães da Areia")

    def test_titulo_com_menos_de_3_caracteres_apos_limpeza_e_rejeitado(self):
        dados = {
            "title": "   ab   ",
            "author": self.autor.pk,
            "year": 1937,
            "available": True,
        }
        resposta = self.client.post(self.url, dados)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "O título precisa ter pelo menos 3 caracteres")
        self.assertEqual(Book.objects.count(), 0)

    def test_titulo_somente_espacos_e_rejeitado(self):
        dados = {
            "title": "      ",
            "author": self.autor.pk,
            "year": 1937,
            "available": True,
        }
        resposta = self.client.post(self.url, dados)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Book.objects.count(), 0)

    def test_ano_posterior_ao_ano_atual_e_rejeitado(self):
        ano_futuro = date.today().year + 1
        dados = {
            "title": "Livro do Futuro",
            "author": self.autor.pk,
            "year": ano_futuro,
            "available": True,
        }
        resposta = self.client.post(self.url, dados)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, f"O ano de publicação não pode ser posterior ao ano atual ({date.today().year})")
        self.assertEqual(Book.objects.count(), 0)

    def test_ano_atual_e_ano_passado_sao_aceitos(self):
        ano_atual = date.today().year
        dados = {
            "title": "Livro Deste Ano",
            "author": self.autor.pk,
            "year": ano_atual,
            "available": True,
        }
        resposta = self.client.post(self.url, dados)
        self.assertRedirects(resposta, reverse("biblioteca:author_detail", args=[self.autor.pk]))
        self.assertTrue(Book.objects.filter(title="Livro Deste Ano").exists())


class BookNavigationTests(TestCase):
    def setUp(self):
        self.autor = Author.objects.create(name="José de Alencar", nationality="Brasileira")
        self.livro = Book.objects.create(
            title="Iracema",
            author=self.autor,
            year=1865,
            available=True,
        )

    def test_links_na_lista_de_livros(self):
        resposta = self.client.get(reverse("biblioteca:listar_livros"))
        self.assertContains(resposta, f'href="{reverse("biblioteca:book_create")}"')
        self.assertContains(resposta, f'href="{reverse("biblioteca:book_edit", args=[self.livro.pk])}"')

    def test_link_editar_na_pagina_do_autor(self):
        resposta = self.client.get(reverse("biblioteca:author_detail", args=[self.autor.pk]))
        self.assertContains(resposta, f'href="{reverse("biblioteca:book_edit", args=[self.livro.pk])}"')
