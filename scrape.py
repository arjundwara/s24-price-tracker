import os
import time
import requests
import pandas as pd
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Email sending function
def send_email(product_details_text):
    sender_email = "pythonlearner.test@gmail.com"
    receiver_email = "mlarasa.007@gmail.com"
    password = "wpof zhlq kqjq xlpt"

    message = EmailMessage()
    message['Subject'] = "📱 New Mobile Offers Scraped from D4D Online"
    message['From'] = sender_email
    message['To'] = receiver_email
    message.set_content(product_details_text)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, password)
            smtp.send_message(message)
        print("📧 Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Scraping logic
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

url = 'https://d4donline.com/en/qatar/doha/products/2/mobiles'
driver.get(url)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "search-input")))
search_box = driver.find_element(By.ID, "search-input")
search_box.clear()
search_box.send_keys("s24 ultra")
search_box.submit()
time.sleep(4)

max_clicks = 10
clicks = 0
while clicks < max_clicks:
    try:
        view_more = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "view-more-products"))
        )
        ActionChains(driver).move_to_element(view_more).click().perform()
        time.sleep(3)
        clicks += 1
    except:
        break

soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

os.makedirs("s24_images", exist_ok=True)

s24_products = []
product_cards = soup.find_all('a', class_='product-card')

for card in product_cards:
    title = card.get('title', '').strip()
    link = f"https://d4donline.com{card.get('href', '')}"
    image_url = card.get('data-image-title') or card.get('data-image-tr')
    price_tag = card.find('p', class_='ptag-rm-sp product-amount')
    store_tag = card.find('h2', class_='product-description')

    price = price_tag.text.strip() if price_tag else 'Not available'
    store = store_tag.text.strip() if store_tag else 'Not available'

    # img_file = 'Not available'
    # Commented: download and save image
    # if image_url:
    #     img_filename = os.path.join("s24_images", image_url.split("/")[-1])
    #     try:
    #         img_response = requests.get(image_url)
    #         with open(img_filename, 'wb') as f:
    #             f.write(img_response.content)
    #         img_file = img_filename
    #     except Exception as e:
    #         print(f"Image download failed: {e}")

    s24_products.append({
        'Title': title,
        'Price': price,
        'Store': store,
        'Link': link
        # 'Image File': img_file
    })

df = pd.DataFrame(s24_products)

# 🧼 Clean and sort price for ascending order
def extract_price(price_str):
    try:
        return float(price_str.replace("QAR", "").replace(",", "").strip())
    except:
        return float('inf')

df["Cleaned Price"] = df["Price"].apply(extract_price)
df = df[df["Cleaned Price"] >= 1000]  # Filter prices >= 1000
df = df.sort_values(by="Cleaned Price")

# Email result
if df.empty:
    print("No S24 Ultra offers >= QAR 1000 found.")
else:
    print(f"📱 Found {len(df)} offers sorted by price (>= QAR 1000).")
    email_body = "📊 Sorted Mobile Offers (QAR 1000 and above):\n\n"
    for i, row in df.iterrows():
        email_body += f"{i+1}. {row['Title']}\n"
        email_body += f"   💰 Price: {row['Price']}\n"
        email_body += f"   🏪 Store: {row['Store']}\n"
        email_body += f"   🔗 Link: {row['Link']}\n\n"
    send_email(email_body)
