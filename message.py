from playwright.sync_api import sync_playwright, TimeoutError

USERNAME = "jordana.bryant"

with sync_playwright() as p:

    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = context.pages[0]

    page.goto(f"https://www.tiktok.com/@{USERNAME}", wait_until="networkidle")

    try:
        page.wait_for_selector('[data-e2e="message-button"], button:has-text("Message")')
        page.wait_for_timeout(4000)

        page.locator('[data-e2e="message-button"], button:has-text("Message")').first.click()
        print("Message window opened")

        # wait for messages page to load
        page.wait_for_url("**/messages*", timeout=15000)

        # wait for conversation panel
        page.wait_for_selector('textarea, div[contenteditable="true"]', timeout=15000)

        print("Chat input fully loaded")

    except TimeoutError:
        print("Chat input never appeared")

    page.wait_for_timeout(5000)