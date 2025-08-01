"""
Contact information scraper for extracting emails, phone numbers, and social media links.
"""
import re
import time
import random
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
        """Extract email addresses from HTML content with better filtering."""
        emails = set()
        
        # Find all email patterns
        found_emails = self.email_pattern.findall(html_content)
        
        # Common spam/invalid email patterns to exclude
        spam_patterns = [
            'example.com', 'test.com', 'domain.com', 'yoursite.com',
            'sampleemail', 'noreply', 'no-reply', 'donotreply'
        ]
        
        for email in found_emails:
            email_lower = email.lower()
            
            # Filter out image file extensions
            if any(email_lower.endswith(ext) for ext in IMAGE_EXTENSIONS):
                continue
                
            # Filter out common spam patterns
            if any(pattern in email_lower for pattern in spam_patterns):
                continue
                
            # Basic email validation
            if self._is_valid_email(email):
                emails.add(email_lower)
        
        return emails
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format and quality."""
        if not email or len(email) < 5:
            return False
            
        # Must have exactly one @
        if email.count('@') != 1:
            return False
            
        local, domain = email.split('@')
        
        # Basic local part validation
        if len(local) < 1 or len(domain) < 3:
            return False
            
        # Domain should have at least one dot and not start/end with dot
        if '.' not in domain or domain.startswith('.') or domain.endswith('.'):
            return False
            
        # Domain extension should be reasonable
        domain_parts = domain.split('.')
        if len(domain_parts[-1]) < 2 or any(not part for part in domain_parts):
            return False
            
        return True
    
    def _extract_phones(self, html_content: str) -> Set[str]:
        """Extract phone numbers from HTML content with better validation."""
        phones = set()
        
        # Find all phone patterns
        found_phones = self.phone_pattern.findall(html_content)
        
        for phone in found_phones:
            # Clean phone number - remove all non-digit characters except +
            clean_phone = re.sub(r'[^\d+]', '', phone)
            clean_phone = clean_phone.replace("tel:", "").replace("callto:", "")
            
            # Validate phone number
            if self._is_valid_phone(clean_phone):
                phones.add(clean_phone.strip())
        
        return phones
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number format and length."""
        if not phone:
            return False
            
        # Remove + for length checking
        digits_only = phone.replace('+', '')
        
        # Should be between 8 and 15 digits (international standard)
        if not digits_only.isdigit() or len(digits_only) < 8 or len(digits_only) > 15:
            return False
            
        # Avoid obvious invalid numbers (but allow reasonable length patterns)
        if len(digits_only) >= 10:  # Only check patterns for longer numbers
            invalid_patterns = ['0000000000', '1111111111', '1234567890']
            if any(pattern in digits_only for pattern in invalid_patterns):
                return False
        
        return True
    
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
    
    def scrape_url_with_browser(self, browser_manager, url: str, max_retries: int = None) -> Tuple[List[str], List[str], List[str]]:
        """
        Scrape a URL using browser manager for JavaScript-rendered content with retry logic.
        
        Args:
            browser_manager: BrowserManager instance
            url: URL to scrape
            max_retries: Maximum number of retry attempts
            
        Returns:
            Tuple of (emails, phones, social_links)
        """
        max_retries = max_retries or MAX_RETRIES
        
        for attempt in range(max_retries + 1):
            try:
                if browser_manager.navigate_to_url(url):
                    # Wait a bit more for dynamic content to load
                    time.sleep(random.uniform(2, 4))
                    html_content = browser_manager.get_page_source()
                    
                    if html_content and len(html_content) > 1000:  # Basic content validation
                        return self.extract_contacts_from_html(html_content)
                    else:
                        logging.warning(f"Page content seems incomplete for {url}")
                        
                else:
                    logging.warning(f"Could not navigate to {url}")
                
                # If we reach here, there was an issue - retry if attempts remaining
                if attempt < max_retries:
                    wait_time = RETRY_BACKOFF_FACTOR ** attempt
                    logging.info(f"Retrying {url} in {wait_time} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    
            except Exception as e:
                logging.error(f"Error scraping {url} (attempt {attempt + 1}): {e}")
                if attempt < max_retries:
                    wait_time = RETRY_BACKOFF_FACTOR ** attempt
                    time.sleep(wait_time)
                else:
                    logging.error(f"Failed to scrape {url} after {max_retries + 1} attempts")
        
        return [], [], []
    
    def scrape_multiple_urls(self, browser_manager, urls: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """
        Scrape multiple URLs and combine results with smart prioritization.
        
        Args:
            browser_manager: BrowserManager instance
            urls: List of URLs to scrape
            
        Returns:
            Combined tuple of (emails, phones, social_links)
        """
        all_emails = set()
        all_phones = set()
        all_socials = set()
        
        # Prioritize URLs - contact pages first, then main site
        prioritized_urls = self._prioritize_urls(urls)
        
        for i, url in enumerate(prioritized_urls):
            logging.info(f"Scraping ({i+1}/{len(prioritized_urls)}): {url}")
            emails, phones, socials = self.scrape_url_with_browser(browser_manager, url)
            
            all_emails.update(emails)
            all_phones.update(phones)
            all_socials.update(socials)
            
            # Log findings
            if emails or phones or socials:
                logging.info(f"✓ Found contacts on {url}: {len(emails)} emails, {len(phones)} phones, {len(socials)} socials")
                
                # Smart stopping criteria - if we have good contact info from a contact page, stop early
                if self._is_contact_page(url) and (len(emails) >= 1 or len(phones) >= 1):
                    logging.info("Found sufficient contact information from contact page, stopping early")
                    break
                elif len(emails) >= 3 or len(phones) >= 2:
                    logging.info("Found substantial contact information, stopping URL scraping")
                    break
            else:
                logging.info(f"✗ No contacts found on {url}")
        
        return list(all_emails), list(all_phones), list(all_socials)
    
    def _prioritize_urls(self, urls: List[str]) -> List[str]:
        """Prioritize URLs to scrape contact pages first."""
        contact_urls = []
        other_urls = []
        
        for url in urls:
            if self._is_contact_page(url):
                contact_urls.append(url)
            else:
                other_urls.append(url)
        
        # Contact pages first, then others
        return contact_urls + other_urls
    
    def _is_contact_page(self, url: str) -> bool:
        """Check if URL appears to be a contact page."""
        url_lower = url.lower()
        contact_indicators = ['contact', 'contatt', 'about', 'chi-siamo', 'team', 'lavora-con-noi']
        return any(indicator in url_lower for indicator in contact_indicators)
    
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