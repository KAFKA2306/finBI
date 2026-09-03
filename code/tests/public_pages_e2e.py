import os
import time
from urllib.parse import parse_qs, urlparse

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


def assert_period_query(driver, expected_start, expected_end):
    query = parse_qs(urlparse(driver.current_url).query)
    assert query.get("start") == [expected_start], query
    assert query.get("end") == [expected_end], query


def assert_fx_view(driver):
    wait_text(driver, "#fx-status", lambda value: "read-only investor2 output" in value)
    assert (
        driver.find_element(By.CSS_SELECTOR, "#fx-schema").text
        == "investor2.fx-overlay.v1"
    )
    assert (
        driver.find_element(By.CSS_SELECTOR, "#fx-overlay-status").text == "UNVERIFIED"
    )
    assert driver.find_element(By.CSS_SELECTOR, "#fx-current-exposure").text == "—"
    assert driver.find_element(By.CSS_SELECTOR, "#fx-incremental-exposure").text == "—"

    reason = driver.find_element(By.CSS_SELECTOR, "#fx-reason").text
    assert "canonical realized daily swap history" in reason, reason
    assert "actual portfolio position snapshot" in reason, reason

    links = [
        element.get_attribute("href")
        for element in driver.find_elements(By.CSS_SELECTOR, "#fx-desk .source-row a")
    ]
    assert any("fx_overlay_contract.md" in href for href in links), links
    assert any("/issues/251" in href for href in links), links
    assert any("/issues/252" in href for href in links), links


def run_viewport(width, height):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size={width},{height}")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(URL)
        assert_fx_view(driver)
        wait_text(driver, "#status", lambda value: "比較完了" in value)
        wait_text(
            driver, "#curve-brief-status", lambda value: "verified snapshots" in value
        )

        metadata = driver.find_element(By.CSS_SELECTOR, "#metadata").text
        assert "2026-07-20 → 2026-07-23" in metadata, metadata
        assert "2026-07-24T20:17:00Z" in metadata, metadata

        source = driver.find_element(By.CSS_SELECTOR, "#source-link").get_attribute(
            "href"
        )
        assert source and "fred.stlouisfed.org" in source, source
        for selector, series in (
            ("#curve-long-source", "DGS10"),
            ("#curve-short-source", "DGS2"),
        ):
            href = driver.find_element(By.CSS_SELECTOR, selector).get_attribute("href")
            assert href and f"/{series}" in href, href

        curve_headline = driver.find_element(
            By.CSS_SELECTOR, "#curve-brief-headline"
        ).text
        curve_detail = driver.find_element(By.CSS_SELECTOR, "#curve-brief-detail").text
        assert "39.0 bp → 34.0 bp" in curve_headline, curve_headline
        assert "フラット化" in curve_headline, curve_headline
        assert "10年は+11.0 bp" in curve_detail, curve_detail
        assert "2年は+16.0 bp" in curve_detail, curve_detail
        assert "REJECT" in curve_detail, curve_detail

        click_chart_date(driver, "2026-07-20")
        wait_text(driver, "#status", lambda value: "次に終了日" in value)
        click_chart_date(driver, "2026-07-23")

        wait_text(driver, "#status", lambda value: "比較完了" in value)
        wait_text(
            driver,
            "#curve-brief-status",
            lambda value: "2026-07-20 → 2026-07-23" in value,
        )
        headline = driver.find_element(By.CSS_SELECTOR, "#headline").text
        story = driver.find_element(By.CSS_SELECTOR, "#story").text
        assert "+11.00 bp" in headline, headline
        assert "4.60%" in story and "4.71%" in story, story
        assert "+0.11 percentage point" in story, story

        start_value = driver.find_element(By.CSS_SELECTOR, "#start").get_attribute(
            "value"
        )
        end_value = driver.find_element(By.CSS_SELECTOR, "#end").get_attribute("value")
        assert start_value == "2026-07-20", start_value
        assert end_value == "2026-07-23", end_value
        assert_period_query(driver, "2026-07-20", "2026-07-23")

        shared_url = f"{URL}?start=2026-07-21&end=2026-07-22"
        driver.get(shared_url)
        assert_fx_view(driver)
        wait_text(driver, "#status", lambda value: "比較完了" in value)
        wait_text(
            driver,
            "#curve-brief-status",
            lambda value: "2026-07-21 → 2026-07-22" in value,
        )
        restored_start = driver.find_element(By.CSS_SELECTOR, "#start").get_attribute(
            "value"
        )
        restored_end = driver.find_element(By.CSS_SELECTOR, "#end").get_attribute(
            "value"
        )
        assert restored_start == "2026-07-21", restored_start
        assert restored_end == "2026-07-22", restored_end
        assert_period_query(driver, "2026-07-21", "2026-07-22")

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
