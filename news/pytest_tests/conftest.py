from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

@pytest.fixture
def author(django_user_model):  
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):  
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client

@pytest.fixture
def news(author):
    news = News.objects.create(  
        title='Заголовок',
        text='Текст заметки',
    )
    return news

@pytest.fixture
def comment(author, news, COMMENT_TEXT):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT
    )
    
    return comment

@pytest.fixture
def id_for_args(news):
    return (news.id,) 

@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News(title=f'Новость {index}', text='Просто текст.',
            date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news

@pytest.fixture
def home_url():
    return reverse('news:home')

@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))

@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))

@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))

@pytest.fixture
def all_comments(news, author):
    now = timezone.now()
    for index in range(10):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()   

@pytest.fixture
def COMMENT_TEXT():
    return 'Текст комментария'

@pytest.fixture
def NEW_COMMENT_TEXT():
    return 'Обновлённый комментарий'

@pytest.fixture
def form_data(COMMENT_TEXT):
    return {'text': COMMENT_TEXT}

@pytest.fixture
def new_form_data(NEW_COMMENT_TEXT):
    return {'text': NEW_COMMENT_TEXT}