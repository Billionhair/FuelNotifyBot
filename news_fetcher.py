import feedparser
import requests
from datetime import datetime, timedelta
import os

def fetch_news_from_rss(queries, hours_back=24):
    """
    Fetch news articles from various RSS feeds based on search queries.
    Returns articles with title, link, published date, and summary.
    """
    articles = []
    
    rss_feeds = [
        "https://www.abc.net.au/news/feed/51120/rss.xml",
        "https://www.news.com.au/content-feeds/latest-news-national/",
        "http://feeds.feedburner.com/theage/rss/national",
    ]
    
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    
    for feed_url in rss_feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:
                try:
                    published_time = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') and entry.published_parsed else datetime.now()
                except:
                    published_time = datetime.now()
                
                if published_time < cutoff_time:
                    continue
                
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', str(datetime.now())),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'source': feed.feed.get('title', 'Unknown Source')
                }
                articles.append(article)
        except Exception as e:
            print(f"Error fetching from {feed_url}: {e}")
            continue
    
    return articles

def fetch_news_from_newsapi(query, api_key=None):
    """
    Fetch news from NewsAPI (requires API key).
    Falls back to RSS if no API key provided.
    """
    if not api_key:
        return []
    
    try:
        from newsapi import NewsApiClient
        newsapi = NewsApiClient(api_key=api_key)
        
        all_articles = newsapi.get_everything(
            q=query,
            language='en',
            sort_by='publishedAt',
            from_param=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        )
        
        articles = []
        for article in all_articles.get('articles', [])[:20]:
            articles.append({
                'title': article.get('title', ''),
                'link': article.get('url', ''),
                'published': article.get('publishedAt', ''),
                'summary': article.get('description', ''),
                'source': article.get('source', {}).get('name', 'Unknown')
            })
        
        return articles
    except Exception as e:
        print(f"Error fetching from NewsAPI: {e}")
        return []

def search_articles_for_keywords(articles, keywords):
    """
    Search articles for keyword matches in title and summary.
    Returns matched articles with match score.
    """
    matched_articles = []
    
    for article in articles:
        text_to_search = f"{article['title']} {article['summary']}".lower()
        matches = []
        
        for keyword in keywords:
            if keyword.lower() in text_to_search:
                matches.append(keyword)
        
        if matches:
            article['matched_keywords'] = matches
            article['match_score'] = len(matches)
            matched_articles.append(article)
    
    matched_articles.sort(key=lambda x: x['match_score'], reverse=True)
    return matched_articles
