import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

URL = os.environ.get("FINBI_PUBLIC_URL", "https://kafka2306.github.io/finBI/")


def wait_text(driver, selector, predicate, timeout=90):
    def _ready(_driver):
        text = _driver.find_element(By.CSS_SELECTOR, selector).text
        return text if predicate(text) else False

    return WebDriverWait(driver, timeout).until(_ready)


def click_chart_date(driver, date, timeout=30):
    selector = f"circle.chart-hit[data-date='{date}']"

    def _click(_driver):
        element = _driver.find_element(By.CSS_SELECTOR, selector)
        _driver.execute_script(
            "arguments[0].dispatchEvent(new MouseEvent('click', {bubbles:true}));",
            element,
        )
        return True

    WebDriverWait(driver, timeout).until(_click)


def run_viewport(width, height):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size={width},{height}")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(URL)
        wait_text(driver, "#status", lambda value: "比較完了" in value)

        metadata = driver.find_element(By.CSS_SELECTOR, "#metadata").text
        assert "2026-07-20 → 2026-07-23" in metadata, metadata
        assert "2026-07-24T20:17:00Z" in metadata, metadata

        source = driver.find_element(By.CSS_SELECTOR, "#source-link").get_attribute("href")
        assert source and "fred.stlouisfed.org" in source, source

        # The first chart pick re-renders the SVG and enters the explicit
        # two-point selection state. Re-resolve the second point after that
        # re-render instead of retaining a stale Selenium element.
        click_chart_date(driver, "2026-07-20")
        wait_text(driver, "#status", lambda value: "次に終了日" in value)
        click_chart_date(driver, "2026-07-23")

        wait_text(driver, "#status", lambda value: "比較完了" in value)
        headline = driver.find_element(By.CSS_SELECTOR, "#headline").text
        story = driver.find_element(By.CSS_SELECTOR, "#story").text
        assert "+11.00 bp" in headline, headline
        assert "4.60%" in story and "4.71%" in story, story
        assert "+0.11 percentage point" in story, story

        start_value = driver.find_element(By.CSS_SELECTOR, "#start").get_attribute("value")
        end_value = driver.find_element(By.CSS_SELECTOR, "#end").get_attribute("value")
        assert start_value == "2026-07-20", start_value
        assert end_value == "2026-07-23", end_value

        overflow = driver.execute_script(
            "return document.documentElement.scrollWidth > document.documentElement.clientWidth;"
        )
        assert not overflow, f"horizontal overflow at {width}x{height}"
    finally:
        driver.quit()


def main():
    for width, height in ((1280, 900), (390, 844)):
        run_viewport(width, height)
        time.sleep(1)


if __name__ == "__main__":
    main()
