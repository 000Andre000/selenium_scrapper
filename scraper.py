import os
import time
import re
import requests
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from googletrans import Translator
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


BASE_URL = "https://elpais.com/"
OPINION_URL = "https://elpais.com/opinion/"

translator = Translator()

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def ensure_spanish(driver):
    driver.get(BASE_URL)
    time.sleep(3)

    html_lang = driver.find_element(By.TAG_NAME, "html").get_attribute("lang")
    if "es" not in html_lang:
        print("Website not in Spanish!")
    else:
        print("Website is in Spanish.")

def download_image(img_url, index):
    if not img_url:
        return

    os.makedirs("images", exist_ok=True)
    img_data = requests.get(img_url).content
    with open(f"images/article_{index}.jpg", "wb") as handler:
        handler.write(img_data)


def scrape_articles(driver):
    wait = WebDriverWait(driver, 10)

    driver.get(OPINION_URL)

    # Wait for articles to load
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))

    # Collect first 5 article links FIRST (important!)
    article_elements = driver.find_elements(By.CSS_SELECTOR, "article h2 a")[:5]
    article_links = [a.get_attribute("href") for a in article_elements]

    translated_titles = []

    for i, link in enumerate(article_links):
        try:
            driver.get(link)

            # Wait for article title
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

            title = driver.find_element(By.TAG_NAME, "h1").text
            print(f"\n📰 Article {i+1}")
            print("Title (ES):", title)

            # Get first 5 paragraphs
            paragraphs = driver.find_elements(By.CSS_SELECTOR, "article p")
            content = "\n".join([p.text for p in paragraphs[:5]])

            print("Content (ES):\n", content[:500], "...")

            # Download cover image if exists
            try:
                img = driver.find_element(By.CSS_SELECTOR, "figure img")
                img_url = img.get_attribute("src")
                download_image(img_url, i+1)
            except:
                print("No cover image found.")

            # Translate title
            translated = translator.translate(title, src='es', dest='en').text
            translated_titles.append(translated)
            print("Title (EN):", translated)

        except Exception as e:
            print("Error processing article:", e)

    return translated_titles

def analyze_repeated_words(translated_titles):
    all_words = []

    for title in translated_titles:
        words = re.findall(r'\b\w+\b', title.lower())
        all_words.extend(words)

    word_counts = Counter(all_words)

    print("\n🔁 Repeated Words (>2 times):")

    repeated = False
    for word, count in word_counts.items():
        if count > 2:
            print(f"{word}: {count}")
            repeated = True

    if not repeated:
        print("No words repeated more than twice.")



def main():
    driver = setup_driver()

    try:
        ensure_spanish(driver)
        translated_titles = scrape_articles(driver)
        analyze_repeated_words(translated_titles)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
