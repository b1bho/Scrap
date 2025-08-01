"""
Configuration constants and settings for the OSINT scraper.
"""
import os

# File paths and CSV configuration
FILE_OUTPUT = 'risultati_osint_selenium_chrome.csv'
COLONNA_NOMI_AZIENDE = 'Ragione Sociale'
COLONNA_PIVA = 'P.IVA'
COLONNA_CITTA = 'Città'

# Timing configuration
MIN_WAIT = 7
MAX_WAIT = 15
PAGE_LOAD_WAIT = 4
JS_WAIT = 6

# Browser configuration
USER_AGENT_REALE = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
CHROME_BINARY_PATH = "/usr/bin/google-chrome-stable"
PROFILE_DIR_NAME = "chrome_profile_for_script"

# Browser options
HEADLESS_MODE = False  # Set to True to run in headless mode
MAX_SEARCH_RESULTS = 3

# Search configuration
EXCLUDED_DOMAINS = [
    'facebook.com', 'linkedin.com', 'google.com', 
    'paginegialle.it', 'instagram.com', 'youtube.com'
]

# Contact page keywords
CONTACT_KEYWORDS = [
    "contatti", "contact", "contattaci", "chi siamo", 
    "about us", "lavora con noi", "about", "team"
]

# Regular expressions for contact extraction
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}'
PHONE_REGEX = r'(?:tel:|callto:)?\s*(?:\+?39)?[\s.-]*\(?\d{2,5}\)?[\s.-]*\d{2,4}[\s.-]*\d{2,4}[\s.-]*\d{2,4}'

# Social media domains for filtering
SOCIAL_MEDIA_DOMAINS = [
    'linkedin.com/company', 'facebook.com', 
    'instagram.com', 'twitter.com/'
]

# Image file extensions to exclude from email extraction
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

def get_profile_path():
    """Get the Chrome profile path for the script."""
    return os.path.join(os.getcwd(), PROFILE_DIR_NAME)

def get_chrome_binary_path():
    """Get the Chrome binary path if it exists."""
    if os.path.exists(CHROME_BINARY_PATH):
        return CHROME_BINARY_PATH
    return None