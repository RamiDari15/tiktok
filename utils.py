from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import time
import re
import csv
import os

from dotenv import load_dotenv
from ocacaptcha import oca_solve_captcha

load_dotenv()


############################################
# INIT BROWSER
############################################

def init_browser():

    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")

    # DO NOT RUN HEADLESS (TikTok blocks it often)
    # chrome_options.add_argument("--headless=new")

    browser = webdriver.Chrome(options=chrome_options)

    wait = WebDriverWait(browser, 25)

    return browser, wait


############################################
# LOGIN
############################################

def login_tiktok(browser, wait, username, password):

    browser.get("https://www.tiktok.com/login/phone-or-email/email")

    actions = ActionChains(browser, duration=550)

    try:

        wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(username)

        password_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
        )

        password_field.send_keys(password)

        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        ).click()

        time.sleep(3)

        user_api_key = os.getenv("CAPTCHA_API_KEY")

        number_captcha_attempts = 10
        action_type = "tiktokcircle"

        if user_api_key:
            oca_solve_captcha(
                browser,
                actions,
                user_api_key,
                action_type,
                number_captcha_attempts
            )

    except Exception:
        print("You have logged in")


############################################
# SCRAPE FRIEND LIST
############################################

def get_all_friends(browser, wait):

    browser.get("https://www.tiktok.com/messages")

    time.sleep(5)

    all_users = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '[data-e2e="chat-item"]')
        )
    )

    my_friends = []

    if os.path.exists("friends.csv"):
        with open("friends.csv", mode="r", newline="") as file:
            reader = csv.DictReader(file)
            my_friends = [row["Username"] for row in reader]

    for user in all_users:

        try:

            user.click()
            time.sleep(2)

            profile_link = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'a[href*="/@"]')
                )
            )

            href = profile_link.get_attribute("href")

            username = re.search(r"/@([^/?]+)", href).group(1)

            if username in my_friends:
                continue

            with open("friends.csv", mode="a", newline="") as file:

                writer = csv.writer(file)

                if file.tell() == 0:
                    writer.writerow(["Username"])

                writer.writerow([username])

            print("Saved friend:", username)

        except Exception:
            continue

    browser.quit()


############################################
# AUTO MESSAGE FRIENDS
############################################

def auto_send_message(browser, wait):

    browser.get("https://www.tiktok.com/messages")

    time.sleep(5)

    my_friends = []

    if os.path.exists("friends.csv"):

        with open("friends.csv", mode="r", newline="") as file:
            reader = csv.DictReader(file)
            my_friends = [row["Username"] for row in reader]

    all_users = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '[data-e2e="chat-item"]')
        )
    )

    for user in all_users:

        try:

            user.click()
            time.sleep(2)

            profile_link = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'a[href*="/@"]')
                )
            )

            href = profile_link.get_attribute("href")

            username = re.search(r"/@([^/?]+)", href).group(1)

        except Exception:
            continue

        if username not in my_friends:
            continue

        try:

            print("Sending message to", username)

            message_input = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[contenteditable="true"]')
                )
            )

            message_input.click()

            message_input.send_keys(os.getenv("MESSAGE"))

            message_input.send_keys(Keys.RETURN)

            time.sleep(3)

        except Exception:
            print("Failed to message", username)