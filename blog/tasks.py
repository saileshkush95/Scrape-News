import time

from asgiref.sync import async_to_sync
import newspaper

from config.celery import app


@app.task
def scrape_news_site(*args, **kwargs):
    root_url = kwargs.get("url")
    print(root_url, "root url")
    if not root_url:
        return ""
    try:
        news_website = newspaper.build(root_url)
        if not news_website:
            return ""
    except Exception as e:
        return ""

    print(news_website.articles)

    for _article in news_website.articles:
        time.sleep(10)
        try:
            article = newspaper.Article(_article.url)
            article.download()
            article.parse()
        except Exception as e:
            pass
