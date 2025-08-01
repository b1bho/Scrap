"""
Browser initialization and search functionality using Selenium WebDriver.
"""
import os
import time
import random
import logging
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

from config import (
    USER_AGENT_REALE, get_profile_path, get_chrome_binary_path,
    HEADLESS_MODE, EXCLUDED_DOMAINS, MAX_SEARCH_RESULTS,
    MIN_WAIT, MAX_WAIT, CONTACT_KEYWORDS
)

class BrowserManager:
    """Manages Selenium WebDriver instance and browser operations."""
    
    def __init__(self):
        self.driver = None
        
    def setup_driver(self) -> Optional[webdriver.Chrome]:
        """Configure and return a Selenium WebDriver instance for Chrome."""
        options = ChromeOptions()
        
        if HEADLESS_MODE:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        
        # Set Chrome binary path if exists
        chrome_binary = get_chrome_binary_path()
        if chrome_binary:
            options.binary_location = chrome_binary
            logging.info(f"Using Chrome binary: {chrome_binary}")
        else:
            logging.warning("Chrome binary not found in standard path. Using auto-detection.")
        
        # Use dedicated profile for the script
        profile_path = get_profile_path()
        options.add_argument(f"user-data-dir={profile_path}")
        logging.info(f"Using dedicated profile: {profile_path}")
        
        # Anti-automation detection options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f"user-agent={USER_AGENT_REALE}")
        
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Apply stealth settings
            stealth(driver,
                    languages=["it-IT", "it"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True)
            
            logging.info("Chrome WebDriver configured successfully")
            self.driver = driver
            return driver
            
        except Exception as e:
            logging.error(f"Error setting up Chrome WebDriver: {e}")
            return None
    
    def human_typing(self, element, text: str):
        """Simulate human typing letter by letter."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))
    
    def google_search(self, nome_azienda: str, citta: str) -> List[str]:
        """
        Perform Google search and return list of relevant URLs.
        
        Args:
            nome_azienda: Company name
            citta: City name
            
        Returns:
            List of URLs found in search results
        """
        if not self.driver:
            logging.error("WebDriver not initialized")
            return []
            
        siti_trovati = []
        query = f'"{nome_azienda}" "{citta}" contatti sito ufficiale'
        
        try:
            self.driver.get("https://www.google.com")
            time.sleep(random.uniform(2, 4))
            
            # Handle cookie popup if present
            try:
                wait = WebDriverWait(self.driver, 5)
                accept_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[.//div[contains(text(), 'Accetta tutto')]]")
                ))
                accept_button.click()
                logging.info("Cookie popup handled")
                time.sleep(random.uniform(1, 2))
            except Exception:
                logging.info("No cookie popup found (normal with existing profile)")
            
            # Perform search
            search_bar = self.driver.find_element(By.NAME, "q")
            search_bar.clear()
            self.human_typing(search_bar, query)
            time.sleep(random.uniform(0.5, 1))
            search_bar.send_keys(Keys.RETURN)
            
            # Wait for results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            time.sleep(random.uniform(2, 4))
            
            # Extract search result links
            link_elements = self.driver.find_elements(By.XPATH, '//a[h3]')
            
            for link_element in link_elements:
                href = link_element.get_attribute('href')
                if self._is_valid_url(href):
                    siti_trovati.append(href)
                    if len(siti_trovati) >= MAX_SEARCH_RESULTS:
                        break
                        
        except Exception as e:
            logging.error(f"Error during Google search for '{nome_azienda}': {e}")
            
        return siti_trovati
    
    def get_candidate_urls(self, base_url: str) -> List[str]:
        """
        Get candidate URLs including main site and contact/about pages.
        
        Args:
            base_url: Main website URL
            
        Returns:
            List of candidate URLs to scrape
        """
        candidate_urls = [base_url]  # Always include main URL
        
        if not self.driver:
            return candidate_urls
            
        try:
            self.driver.get(base_url)
            time.sleep(random.uniform(2, 4))
            
            # Look for contact/about page links
            for keyword in CONTACT_KEYWORDS:
                try:
                    link_element = self.driver.find_element(
                        By.XPATH, 
                        f"//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]"
                    )
                    if link_element and link_element.is_displayed() and link_element.is_enabled():
                        contact_url = link_element.get_attribute('href')
                        if contact_url and contact_url not in candidate_urls:
                            candidate_urls.append(contact_url)
                            logging.info(f"Found contact page: {contact_url}")
                            break  # Only add one contact page
                except Exception:
                    continue
                    
        except Exception as e:
            logging.warning(f"Could not get candidate URLs from {base_url}: {e}")
            
        return candidate_urls
    
    def navigate_to_url(self, url: str) -> bool:
        """
        Navigate to a specific URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            return False
            
        try:
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))
            return True
        except Exception as e:
            logging.warning(f"Could not navigate to {url}: {e}")
            return False
    
    def get_page_source(self) -> str:
        """Get current page source."""
        if self.driver:
            return self.driver.page_source
        return ""
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and not in excluded domains."""
        if not url or not url.startswith('http'):
            return False
            
        return not any(domain in url for domain in EXCLUDED_DOMAINS)
    
    def close(self):
        """Close the browser and clean up resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logging.info("Browser closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

def check_first_run():
    """Check if this is the first run and display authentication instructions."""
    profile_dir = get_profile_path()
    if not os.path.exists(profile_dir):
        print("=" * 70)
        print("ATTENZIONE: PRIMA ESECUZIONE DELLO SCRIPT")
        print("1. Si aprirà una finestra di Chrome.")
        print("2. ACCEDI MANUALMENTE al tuo account Google in quella finestra.")
        print("3. Una volta fatto, puoi chiudere la finestra e riavviare lo script.")
        print("   Dovrai fare questa operazione solo una volta.")
        print("=" * 70)
        time.sleep(8)