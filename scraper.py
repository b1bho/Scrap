"""
Contact information scraper for extracting emails, phone numbers, and social media links.
"""
import re
import logging
from typing import List, Tuple, Set
from bs4 import BeautifulSoup

from config import (
    EMAIL_REGEX, PHONE_REGEX, SOCIAL_MEDIA_DOMAINS, 
    IMAGE_EXTENSIONS, MAX_RETRIES, RETRY_BACKOFF_FACTOR
)

class ContactScraper:
    """Scraper for extracting contact information from web pages."""
    
    def __init__(self):
        self.email_pattern = re.compile(EMAIL_REGEX)
        self.phone_pattern = re.compile(PHONE_REGEX)
    
    def extract_contacts_from_html(self, html_content: str) -> Tuple[List[str], List[str], List[str]]:
        """
        Extract emails, phone numbers and social media links from HTML content.
        
        Args:
            html_content: HTML content as string
            
        Returns:
            Tuple of (emails, phones, social_links)
        """
        emails = self._extract_emails(html_content)
        phones = self._extract_phones(html_content)
        socials = self._extract_social_media(html_content)
        
        return list(emails), list(phones), list(socials)
    
    def _extract_emails(self, html_content: str) -> Set[str]:
        """Extract email addresses from HTML content."""
        emails = set()
        
        # Find all email patterns
        found_emails = self.email_pattern.findall(html_content)
        
        for email in found_emails:
            # Filter out image file extensions
            if not any(email.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                emails.add(email.lower())
        
        return emails
    
    def _extract_phones(self, html_content: str) -> Set[str]:
        """Extract phone numbers from HTML content."""
        phones = set()
        
        # Find all phone patterns
        found_phones = self.phone_pattern.findall(html_content)
        
        for phone in found_phones:
            # Clean phone number - remove all non-digit characters except +
            clean_phone = re.sub(r'[^\d+]', '', phone)
            clean_phone = clean_phone.replace("tel:", "").replace("callto:", "")
            
            # Only include if it has reasonable length
            if len(clean_phone) > 8:
                phones.add(clean_phone.strip())
        
        return phones
    
    def _extract_social_media(self, html_content: str) -> Set[str]:
        """Extract social media links from HTML content."""
        socials = set()
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all anchor tags with href
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                
                # Check if it's a social media link
                if any(domain in href for domain in SOCIAL_MEDIA_DOMAINS):
                    socials.add(href)
                    
        except Exception as e:
            logging.warning(f"Error parsing HTML for social media links: {e}")
        
        return socials
    
    def scrape_url_with_browser(self, browser_manager, url: str) -> Tuple[List[str], List[str], List[str]]:
        """
        Scrape a URL using browser manager for JavaScript-rendered content.
        
        Args:
            browser_manager: BrowserManager instance
            url: URL to scrape
            
        Returns:
            Tuple of (emails, phones, social_links)
        """
        try:
            if browser_manager.navigate_to_url(url):
                html_content = browser_manager.get_page_source()
                return self.extract_contacts_from_html(html_content)
            else:
                logging.warning(f"Could not navigate to {url}")
                return [], [], []
                
        except Exception as e:
            logging.error(f"Error scraping {url}: {e}")
            return [], [], []
    
    def scrape_multiple_urls(self, browser_manager, urls: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """
        Scrape multiple URLs and combine results.
        
        Args:
            browser_manager: BrowserManager instance
            urls: List of URLs to scrape
            
        Returns:
            Combined tuple of (emails, phones, social_links)
        """
        all_emails = set()
        all_phones = set()
        all_socials = set()
        
        for url in urls:
            logging.info(f"Scraping: {url}")
            emails, phones, socials = self.scrape_url_with_browser(browser_manager, url)
            
            all_emails.update(emails)
            all_phones.update(phones)
            all_socials.update(socials)
            
            # Log findings
            if emails or phones or socials:
                logging.info(f"Found contacts on {url}: {len(emails)} emails, {len(phones)} phones, {len(socials)} socials")
                
                # If we have good contact info, we might not need to scrape more URLs
                if len(emails) >= 2 or len(phones) >= 1:
                    logging.info("Found sufficient contact information, stopping URL scraping")
                    break
        
        return list(all_emails), list(all_phones), list(all_socials)
    
    def analyze_company_contacts(self, browser_manager, nome_azienda: str, citta: str) -> Tuple[str, List[str], List[str], List[str]]:
        """
        Analyze a company to find contact information.
        
        Args:
            browser_manager: BrowserManager instance
            nome_azienda: Company name
            citta: City name
            
        Returns:
            Tuple of (main_site_used, emails, phones, social_links)
        """
        # Step 1: Google search
        logging.info(f"Searching Google for: {nome_azienda}")
        search_results = browser_manager.google_search(nome_azienda, citta)
        
        if not search_results:
            logging.warning(f"No search results found for {nome_azienda}")
            return "Non trovato", [], [], []
        
        # Step 2: Get the main site (first result)
        main_site = search_results[0]
        logging.info(f"Main site found: {main_site}")
        
        # Step 3: Get candidate URLs (main + contact pages)
        candidate_urls = browser_manager.get_candidate_urls(main_site)
        logging.info(f"Candidate URLs to scrape: {len(candidate_urls)}")
        
        # Step 4: Scrape candidate URLs
        emails, phones, socials = self.scrape_multiple_urls(browser_manager, candidate_urls)
        
        if emails or phones or socials:
            logging.info(f"Successfully found contacts for {nome_azienda}: {len(emails)} emails, {len(phones)} phones, {len(socials)} socials")
            return main_site, emails, phones, socials
        else:
            logging.warning(f"No contacts found for {nome_azienda} after scraping {len(candidate_urls)} URLs")
            return main_site, [], [], []