import re
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    page.goto("https://tutorialsninja.com/demo/")
    page.get_by_role("link", name="Laptops & Notebooks", exact=True).click()
    page.get_by_role("link", name="Show AllLaptops & Notebooks").click()
    page.get_by_role("textbox", name="Search").click()
    page.get_by_role("textbox", name="Search").fill("imac")
    page.get_by_role("button", name="").click()
    expect(page.locator("h4")).to_contain_text("iMac")
    page.get_by_text("iMac", exact=True).click()
    expect(page.locator("#content")).to_contain_text("iMac")
    page.get_by_role("button", name="Add to Cart", exact=True).click()
    expect(page.locator("#product-product")).to_contain_text("Success: You have added iMac to your shopping cart!×")
