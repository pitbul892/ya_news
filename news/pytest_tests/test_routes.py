# .Главная страница доступна анонимному пользователю.
# .Страница отдельной новости доступна анонимному пользователю.
# .Страницы удаления и редактирования комментария доступны автору комментария.
# .При попытке перейти на страницу редактирования или удаления комментария
# анонимный пользователь перенаправляется на страницу авторизации.
# .Авторизованный пользователь не может зайти на страницы редактирования
# или удаления чужих комментариев (возвращается ошибка 404).
# .Страницы регистрации пользователей, входа в учётную запись и
# выхода из неё доступны анонимным пользователям.
from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects
# Главная страница доступна анонимному пользователю.
# Страница отдельной новости доступна анонимному пользователю.
# Страницы регистрации пользователей, входа в учётную запись 
# и выхода из неё доступны анонимным пользователям.
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
))
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK 

# Страницы удаления и редактирования комментария доступны автору комментария.
# Авторизованный пользователь не может зайти на страницы редактирования или
# удаления чужих комментариев (возвращается ошибка 404).
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)

@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)

def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status 

# При попытке перейти на страницу редактирования или удаления
# комментария анонимный пользователь перенаправляется на страницу авторизации.
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_args')),
        ('news:delete', pytest.lazy_fixture('id_for_args')),
    ),
)
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url) 