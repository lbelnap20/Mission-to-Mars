#!/usr/bin/env python
# coding: utf-8

# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd 
import datetime as dt
import logging

logger = logging.getLogger()


def scrape_all():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres" : hemispheres(browser)
    }
    

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
            return None, None

    return news_title, news_p

# ### Featured Images

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    try: 
    # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


# ### Mars Facts

def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except Exception:
        return logger.exception("None")

    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    return df.to_html()

def hemispheres(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Get a List of All the Hemispheres
    html = browser.html
    img_soup = soup(html, 'html.parser')
    links = img_soup.find_all('div', class_='item')
    hemisphere_image_urls = []

    try:
        for item in range(len(links)):
            hemisphere = {}
            # Open each hemisphere page
            full_image_elem = browser.find_by_tag('h3')[item]
            full_image_elem.click()
                
            # Get hemisphere title
            hemisphere["title"] = browser.find_by_css("h2.title").text
                
            # Find sample image
            sample_element = browser.find_link_by_text("Sample").first
            hemisphere["img_url"] = sample_element["href"]
            
            # Add to list
            hemisphere_image_urls.append(hemisphere)
    
            # Go back to main page
            browser.back()
    except AttributeError:
        return None

    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())



