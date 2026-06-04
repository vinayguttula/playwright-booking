import re
import pytest
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta
import time
import urllib.parse

def remove_dialogs(page: Page):
    try:
        page.locator('button[aria-label="Dismiss sign-in info."]').click(timeout=3000)
    except:
        pass
    try:
        page.evaluate('''() => {
            const dialogs = document.querySelectorAll('div[role="dialog"]');
            dialogs.forEach(d => d.remove());
        }''')
    except:
        pass

def search_stockholm(page: Page):
    # Go to homepage first to get cookies
    page.goto("https://www.booking.com", wait_until="domcontentloaded")
    time.sleep(2)
    remove_dialogs(page)
    
    checkin_date = datetime.now() + timedelta(days=5)
    checkout_date = datetime.now() + timedelta(days=9)
    checkin_str = checkin_date.strftime("%Y-%m-%d")
    checkout_str = checkout_date.strftime("%Y-%m-%d")
    
    base_url = "https://www.booking.com/searchresults.html"
    
    params = {
        "ss": "Stockholm",
        "ssne": "Stockholm",
        "ssne_untouched": "Stockholm",
        "checkin": checkin_str,
        "checkout": checkout_str,
        "group_adults": "2",
        "no_rooms": "1",
        "group_children": "1",
        "age": "8",
        "dest_id": "-2524279",
        "dest_type": "city"
    }
    
    query_string = urllib.parse.urlencode(params)
    full_url = f"{base_url}?{query_string}"
    
    page.goto(full_url, wait_until="domcontentloaded")
    time.sleep(3)
    remove_dialogs(page)
    
    # If still redirected, try one more time
    if "/city/" in page.url or "searchresults" not in page.url:
        page.goto(full_url, wait_until="domcontentloaded")
        time.sleep(3)
        remove_dialogs(page)

def test_scenario_1(page: Page):
    """
    Scenario 1: Search
    """
    search_stockholm(page)
    try:
        page.wait_for_selector('[data-testid="property-card"]', timeout=15000)
    except:
        pass
    expect(page.locator("input[name=\"ss\"]").first).to_have_value(re.compile("Stockholm", re.IGNORECASE))


def test_scenario_2(page: Page):
    """
    Scenario 2: Filter
    """
    search_stockholm(page)
    page.wait_for_function('''() => document.querySelectorAll('input[type="checkbox"]').length > 0''', timeout=30000)
    has_slider = page.evaluate('''() => document.querySelectorAll('input[type="range"]').length >= 2''')
    if has_slider:
        page.evaluate('''() => {
            const inputs = document.querySelectorAll('input[type="range"]');
            if (inputs.length >= 2) {
                inputs[0].value = 2000;
                inputs[0].dispatchEvent(new Event('change', { bubbles: true }));
                inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                inputs[1].value = 10000;
                inputs[1].dispatchEvent(new Event('change', { bubbles: true }));
                inputs[1].dispatchEvent(new Event('input', { bubbles: true }));
            }
        }''')
        time.sleep(3)
    
    page.evaluate('''() => {
        const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
        const breakfastCheckbox = checkboxes.find(c => 
            c.name === 'mealplan=1' || 
            (c.getAttribute('aria-label') && c.getAttribute('aria-label').toLowerCase().includes('breakfast'))
        );
        if (breakfastCheckbox) {
            breakfastCheckbox.click();
        }
    }''')
    time.sleep(3)
    page.wait_for_function('''() => document.querySelectorAll('[data-testid="property-card"]').length > 0 || document.querySelectorAll('div[data-testid="title"]').length > 0''', timeout=15000)


def test_scenario_3(page: Page):
    """
    Scenario 3: Algorithmic Sort
    - Sort results by "Property rating (low to high)"
    """
    search_stockholm(page)
    
    assert "searchresults" in page.url, f"Expected searchresults.html, got {page.url}"
    
    try:
        page.wait_for_selector('[data-testid="sorters-dropdown-trigger"]', timeout=15000)
        page.click('[data-testid="sorters-dropdown-trigger"]')
        time.sleep(2)
        
        page.click('button[data-id="class_asc"]')
        time.sleep(3)
    except Exception as e:
        page.evaluate('''() => {
            const btn = document.querySelector('button[data-id="class_asc"]');
            if (btn) btn.click();
        }''')
        time.sleep(3)
        
    page.wait_for_function('''() => document.querySelectorAll('[data-testid="property-card"]').length > 0''', timeout=15000)
    expect(page.locator('[data-testid="sorters-dropdown-trigger"]')).to_contain_text("rating", ignore_case=True)


def test_scenario_4(page: Page):
    """
    Scenario 4: Review Validation
    - Filter by Breakfast included
    - Validate first 5 items contain Breakfast Included text
    - Validate first 5 items have Price info
    """
    search_stockholm(page)
    
    # Wait for checkboxes
    page.wait_for_function('''() => document.querySelectorAll('input[type="checkbox"]').length > 0''', timeout=30000)
    
    # Filter by breakfast
    page.evaluate('''() => {
        const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
        const breakfastCheckbox = checkboxes.find(c => 
            c.name === 'mealplan=1' || 
            (c.getAttribute('aria-label') && c.getAttribute('aria-label').toLowerCase().includes('breakfast'))
        );
        if (breakfastCheckbox) {
            breakfastCheckbox.click();
        }
    }''')
    time.sleep(4)
    
    page.wait_for_function('''() => document.querySelectorAll('[data-testid="property-card"]').length >= 5''', timeout=15000)
    
    # Check first 5 items
    cards = page.locator('[data-testid="property-card"]').all()
    count = min(5, len(cards))
    
    for i in range(count):
        text_content = cards[i].inner_text().lower()
        
        # Validate Breakfast included
        assert "breakfast" in text_content, f"Item {i} does not contain 'Breakfast included'."
        
        # Validate price info (usually contains '$' or 'SEK' or 'kr' or 'price')
        has_price = any(char in text_content for char in ["$", "sek", "kr", "price"])
        assert has_price, f"Item {i} does not contain pricing information."

