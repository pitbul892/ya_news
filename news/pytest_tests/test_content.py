# .Количество новостей на главной странице — не более 10.
# .Новости отсортированы от самой свежей к самой старой.
# .Свежие новости в начале списка.
# Комментарии на странице отдельной новости отсортированы
# в хронологическом порядке: старые в начале списка, новые — в конце.
# Анонимному пользователю недоступна форма для отправки комментария
# на странице отдельной новости, а авторизованному доступна.

import pytest

from django.conf import settings

from news.forms import CommentForm
# Количество новостей на главной странице — не более 10.
@pytest.mark.django_db
def test_news_count(author_client, home_url, all_news):
    response = author_client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

# Новости отсортированы от самой свежей к самой старой.
def test_news_order(author_client, home_url, all_news):
    response = author_client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates 

# Комментарии на странице отдельной новости отсортированы
def test_comments_order(author_client, detail_url,news, all_comments):
    response = author_client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps

# Анонимному пользователю недоступна форма для отправки комментария
# на странице отдельной новости,
def test_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context

# а авторизованному доступна.       
def test_authorized_client_has_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm) 
