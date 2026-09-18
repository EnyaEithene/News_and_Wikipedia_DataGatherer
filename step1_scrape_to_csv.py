"""Downloads news articles from their respective RSS feeds and saves them in a CSV file.

This script accesses RSS feeds for various news websites, extracts article data, and saves
it in a CSV file. The script includes functions to parse RSS feeds and to scrape articles
from specified sources, handling rate limiting and potential errors.

Functions:
    parse_rss(source, max_articles): Extracts articles from a specified RSS feed.
    scrape_to_csv(sources, max_articles, output_csv): Saves extracted articles to a CSV file.

Usage:
    Run the script as a standalone program with the desired parameters for the sources,
    maximum number of articles, and output CSV file name.

Dependencies:
    - requests
    - beautifulsoup4
    - pandas
    - os
    - time
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}    # Required for requests


# Dictionary with all the news websites and their RSS feed
RSS_FEEDS = {
    'digi24':  'https://www.digi24.ro/rss',
    'hotnews': 'https://www.hotnews.ro/rss',
    'g4media': 'https://www.g4media.ro/feed',
    'adevarul': 'https://adevarul.ro/rss',
    'libertatea': 'https://www.libertatea.ro/feed',
    'mediafax': 'https://www.mediafax.ro/rss',
    'ziarulfinanciar': 'https://www.zf.ro/rss',
    'ziare.com': 'https://ziare.com/rss'
}

def parse_rss(source, max_articles=10):
    """Parse and extract articles from a given RSS feed.

    This function accesses the RSS feed of a specified news source and extracts
    a specified number of articles. It retrieves the title, description, link,
    publication date, category, and a cleaned version of the description.

    Args:
        source (str): The name of the news source as defined in the `RSS_FEEDS` dictionary.
        max_articles (int, optional): The maximum number of articles to extract from the RSS feed.
                                      Defaults to 10.

    Returns:
        list: A list of dictionaries, each containing the extracted data for an article, including:
              - 'source': The name of the news source.
              - 'title': The title of the article.
              - 'description': The cleaned description text of the article.
              - 'link': The URL link to the article.
              - 'pub_date': The publication date of the article.
              - 'category': The category of the article.
              - 'tags': A placeholder for tags, currently set as an empty string.

    Notes:
        - The function uses the `requests` library to fetch the RSS feed and `BeautifulSoup` to parse it.
        - The description is cleaned by removing HTML tags using `BeautifulSoup`.
        - The function handles missing fields by assigning empty strings or default values.
        - The function prints the number of articles found from the specified source.
    """

    # Fetching RSS Feeds
    url = RSS_FEEDS[source]
    print(f"Fetching RSS from {source}...")
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'xml')

    # Gathering the articles
    articles = []
    for item in soup.find_all('item')[:max_articles]:

        # Extracting the relevant data of the articles
        title       = item.find('title').text.strip()       if item.find('title')       else ''
        description = item.find('description').text.strip() if item.find('description') else ''
        link        = item.find('link').text.strip()        if item.find('link')        else ''
        pub_date    = item.find('pubDate').text.strip()     if item.find('pubDate')     else ''
        category    = item.find('category').text.strip()    if item.find('category')    else ''
        clean_desc  = BeautifulSoup(description, 'html.parser').get_text()

        # Adding it to the list in a proper format
        articles.append({
            'source':      source,
            'title':       title,
            'description': clean_desc,
            'link':        link,
            'pub_date':    pub_date,
            'category':    category,  # <- verify/correct manually (type of news)
            'tags':        '',        # <- fill manually (comma-separated keywords)
        })

    print(f"Found {len(articles)} articles from {source}.")
    return articles

def scrape_to_csv(sources=None, max_articles=10, output_csv='articles_to_label.csv'):
    """Scrape articles from specified RSS feeds and save them to a CSV file.

    This function fetches articles from the given RSS feeds, extracts relevant data,
    and saves them to a CSV file. If no sources are specified, it uses all entries
    from the `RSS_FEEDS` dictionary. The function handles rate limiting and manages
    potential errors during the scraping process.

    Args:
        sources (list of str, optional): List of news sources to scrape articles from.
            If not provided, all sources in the `RSS_FEEDS` dictionary are used.
            Defaults to None.
        max_articles (int, optional): Maximum number of articles to scrape from each source.
            Defaults to 10.
        output_csv (str, optional): Name of the CSV file to save the extracted articles.
            Defaults to 'articles_to_label.csv'.

    Returns:
        None: Saves the extracted articles to the specified CSV file and prints status messages.
    """

    # Takes all sources mentioned at the beginning of the file if none are specified
    if sources is None:
        sources = list(RSS_FEEDS.keys())

    # Collects the articles from all the sources specified
    all_articles = []
    for source in sources:
        try:
            articles = parse_rss(source, max_articles=max_articles)
            all_articles.extend(articles)
            time.sleep(1)
        except Exception as e:
            print(f"Failed to fetch RSS from {source}: {e}")

    df = pd.DataFrame(all_articles)

    # Append to existing CSV if it exists (avoid duplicates by link)
    if os.path.exists(output_csv):
        df_existing = pd.read_csv(output_csv)
        df = pd.concat([df_existing, df]).drop_duplicates(subset='link').reset_index(drop=True)
        print(f"Merged with existing CSV. Total articles: {len(df)}")
    
    # Exports the article data in a new or existing CSV file
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\nDone. {len(all_articles)} new articles exported to '{output_csv}'.")
    print("Open the CSV, verify/correct 'category' and fill in 'tags', then run step2_csv_to_pdf.py.")


# Calls the function to scrape the news articles from their RSS feeds
if __name__ == '__main__':
    scrape_to_csv(
        sources=['digi24', 
                 'hotnews', 
                 'g4media', 
                 'adevarul',
                 'libertatea',
                 'mediafax',
                 'ziarulfinanciar',
                 'ziare.com'],
        max_articles=15,
        output_csv='articles_to_label.csv'
    )
