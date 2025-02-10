from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import pandas as pd
import time


class TradingViewScraper:
    """
    Web scraper for extracting crypto news from TradingView.
    
    Uses Selenium WebDriver to dynamically scrape news articles and their content.
    Features:
    - Headless browser operation
    - Infinite scroll handling
    - Retry mechanism for resilient scraping
    - Article content extraction
    - Automatic data structuring into pandas DataFrame
    """
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--window-size=1920,1080')

    def get_articles_with_retry(self, driver, articles_locator, max_retries=5):
        for attempt in range(max_retries):
            try:
                return driver.find_elements(*articles_locator)
            except StaleElementReferenceException:
                if attempt == max_retries - 1:
                    raise
                time.sleep(3)
        return []

    def scrape_tradingview_news(self):
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get('https://www.tradingview.com/news-flow/?market=crypto')

            wait = WebDriverWait(driver, 20)
            articles_locator = (By.CSS_SELECTOR, "article.card-exterior-Us1ZHpvJ")

            articles = wait.until(EC.presence_of_all_elements_located(articles_locator))

            all_article_ids = set()
            news_data = []

            no_new_articles_count = 0

            while no_new_articles_count < 20:
                try:
                    articles = self.get_articles_with_retry(driver, articles_locator)
                    current_count = len(articles)

                    for article in articles:
                        try:
                            article_id = article.find_element(By.XPATH, "..").get_attribute('data-id')
                            if article_id in all_article_ids:
                                continue

                            title = article.find_element(By.CSS_SELECTOR, "div[data-name='news-headline-title']").get_attribute('data-overflow-tooltip-text')
                            time_element = article.find_element(By.CSS_SELECTOR, "relative-time").get_attribute('event-time')
                            source = article.find_element(By.CSS_SELECTOR, "span.provider-TUPxzdRV").text
                            url = article.find_element(By.XPATH, "..").get_attribute('href')

                            if all([article_id, title, time_element, source]):
                                news_data.append({
                                    'id': article_id,
                                    'title': title,
                                    'time': time_element,
                                    'source': source,
                                    'url': url
                                })
                                all_article_ids.add(article_id)

                        except (StaleElementReferenceException, NoSuchElementException):
                            continue

                    if articles:
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",articles[-1])
                        time.sleep(2)

                    new_articles = self.get_articles_with_retry(driver, articles_locator)
                    if len(new_articles) > current_count:
                        no_new_articles_count = 0
                    else:
                        no_new_articles_count += 1

                except StaleElementReferenceException:
                    time.sleep(5)
                    continue

            df = pd.DataFrame(news_data)
            return df

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

        finally:
            driver.quit()

    def extract_article_content(self, driver, url):
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 15)

            paragraphs = driver.find_elements(By.CSS_SELECTOR, "div.body-KX2tCBZq p")
            paragraph_texts = " \n\n ".join([p.text for p in paragraphs if p.text])
            return paragraph_texts
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return "", ""

    def scrape_tradingview_articles(self, df):
        driver = webdriver.Chrome(options=self.chrome_options)

        for index, row in df.iterrows():
            url = row['url']
            article_text = self.extract_article_content(driver, url)
            df.at[index, 'text'] = article_text
            time.sleep(2)

        driver.quit()
        return df

    def initialize_scrapper(self):
        df = self.scrape_tradingview_news()
        df = self.scrape_tradingview_articles(df)
        return df
