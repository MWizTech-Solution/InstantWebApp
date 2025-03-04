import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Scraper_Data").worksheet("Social_Posts")

# Write X posts to Sheets
try:
    with open('x_posts.txt', 'r') as f:
        posts = f.readlines()[:15000]  # Limit to 15K
        for post in posts:
            parts = post.split(':', 1)
            username = parts[0].strip() if len(parts) > 1 else "Unknown"
            text = parts[1].strip() if len(parts) > 1 else post.strip()
            sheet.append_row([text, username])
            time.sleep(0.5)  # Avoid rate limits
    logger.info("Scraped 15K social posts to Sheets")
except Exception as e:
    logger.error(f"Error writing to Sheets: {e}")