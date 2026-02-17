import json
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scraper import scrape_articles, ensure_spanish


def run_test():
    options = Options()

    # SDK automatically reads browserstack.yml
    driver = webdriver.Chrome(options=options)

    try:
        # Set session name in BrowserStack dashboard
        executor_object = {
            'action': 'setSessionName',
            'arguments': {
                'name': "ElPais Scraper Test"
            }
        }
        driver.execute_script(
            'browserstack_executor: {}'.format(json.dumps(executor_object))
        )

        ensure_spanish(driver)
        scrape_articles(driver)

        # Mark test as passed
        driver.execute_script(
            'browserstack_executor: {}'.format(json.dumps({
                "action": "setSessionStatus",
                "arguments": {
                    "status": "passed",
                    "reason": "Scraping completed successfully"
                }
            }))
        )

    except Exception as e:
        driver.execute_script(
            'browserstack_executor: {}'.format(json.dumps({
                "action": "setSessionStatus",
                "arguments": {
                    "status": "failed",
                    "reason": str(e)
                }
            }))
        )
        raise

    finally:
        driver.quit()


def main():
    run_test()


if __name__ == "__main__":
    main()
