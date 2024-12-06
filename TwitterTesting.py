import time
import re
from rapidfuzz import fuzz
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from hashlib import sha256


def fuzzy_match(tweet, slurs):
    for slur in slurs:
        if fuzz.partial_ratio(tweet.lower(), slur.lower()) > 80:  # Adjust threshold
            return True
    return False

def compute_hash(tweet_text):
    if isinstance(tweet_text, str):
        return sha256(tweet_text.encode('utf-8')).hexdigest
    else:
        print(f"Skipping non-string value: {tweet_text}")
        return None

tweets_collected = set()

usernameInput = input("Enter the username to log in with:")
passwordInput = input("Enter the password to log in with:")


driver = webdriver.Firefox()
hateSpeech = ('faggot', 'tranny', 'trannies', 'trans', 'nigger', 'fag', 'troon', 'dyke', 'beaner', 'ching chong', 'chink', 'cotton picker', 'retard')

driver.get("https://x.com/i/flow/login")


wait = WebDriverWait(driver, 10)
username = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete=username]'))
)
username.send_keys(usernameInput)

login_button = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '[role=button].r-13qz1uu'))
)
login_button.click()

password = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '[type=password]'))
)
password.send_keys(passwordInput)

login_button = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid*=Login_Button]'))
)
login_button.click()

time.sleep(5)

elem = driver.find_element(By.TAG_NAME, "body")

scroll_pause_time = 5
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    post_elems = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
    for post in post_elems:
        try:
            tweet_elem = post.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
            tweet_text = tweet_elem.text.strip()

            tweet_hash = compute_hash(tweet_text)
            if tweet_hash not in tweets_collected:
                tweets_collected.add(tweet_hash)
                
                if fuzzy_match(tweet_text, hateSpeech):
                    print("Potential hate speech found!")
                    print("Offending Tweet:")
                    print(tweet_text)
            else:
                print("Duplicate Tweet Skipped.")
        except Exception as e:
            print("No hatespeech detected in this set, loading next set")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)

    # Check if scrolling reached the end
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

driver.quit()