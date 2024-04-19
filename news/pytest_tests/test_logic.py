# .Анонимный пользователь не может отправить комментарий.
# .Авторизованный пользователь может отправить комментарий.
# .Если комментарий содержит запрещённые слова, он не будет
# .опубликован, а форма вернёт ошибку.
# Авторизованный пользователь может редактировать или удалять
# свои комментарии.
# Авторизованный пользователь не может редактировать или удалять
# чужие комментарии.
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


# Авторизованный пользователь может отправить комментарий.
def test_user_can_create_comment(news, COMMENT_TEXT, author_client,
                                 author, detail_url, form_data):
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    new_news = Comment.objects.get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_news.text == COMMENT_TEXT
    assert new_news.news == news
    assert new_news.author == author

# Анонимный пользователь не может отправить комментарий.
def test_anonymous_user_cant_create_comment(client, detail_url, form_data):
    response = client.post(detail_url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)

# Если комментарий содержит запрещённые слова, он не будет
# опубликован, а форма вернёт ошибку.
def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0

# Авторизованный пользователь может удалять свои комментарии.
def test_author_can_delete_comment(author_client, delete_url, detail_url):
    response = author_client.post(delete_url)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 0

# Авторизованный пользователь не может удалять чужие комментарии.
def test_user_cant_delete_comment_of_another_user(not_author_client, delete_url, detail_url):
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1

# Авторизованный пользователь может редактировать свои комментарии.
def test_author_can_edit_comment(NEW_COMMENT_TEXT, new_form_data, comment,
                                author_client, edit_url, detail_url):
    response = author_client.post(edit_url, data=new_form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


# Авторизованный пользователь не может редактировать чужие комментарии.
def test_user_cant_edit_comment_of_another_user(new_form_data, comment,
                        not_author_client, edit_url):
    response = not_author_client.post(edit_url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_bd = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_bd.text


