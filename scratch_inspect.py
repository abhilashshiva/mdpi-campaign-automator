from playwright.sync_api import sync_playwright
import time

p = sync_playwright().start()
browser = p.chromium.launch(headless=False)
# Use a large viewport so desktop layout loads
context = browser.new_context(viewport={"width": 1920, "height": 1080})
page = context.new_page()

# Go directly to the login page
page.goto("https://www.mdpi.com/user/login", wait_until="domcontentloaded")
time.sleep(5)

print("=== CURRENT URL ===")
print(page.url)
print()

# Find all input fields
inputs = page.query_selector_all("input")
for inp in inputs:
    name = inp.get_attribute("name") or ""
    typ = inp.get_attribute("type") or ""
    placeholder = inp.get_attribute("placeholder") or ""
    inp_id = inp.get_attribute("id") or ""
    visible = inp.is_visible()
    print(f"INPUT: name=[{name}] type=[{typ}] id=[{inp_id}] placeholder=[{placeholder}] visible=[{visible}]")

# Find submit buttons
buttons = page.query_selector_all("button, input[type='submit']")
for btn in buttons:
    text = btn.inner_text().strip()[:50] if btn.evaluate("el => el.tagName") == "BUTTON" else ""
    typ = btn.get_attribute("type") or ""
    cls = btn.get_attribute("class") or ""
    visible = btn.is_visible()
    print(f"BUTTON: text=[{text}] type=[{typ}] class=[{cls}] visible=[{visible}]")

browser.close()
p.stop()
