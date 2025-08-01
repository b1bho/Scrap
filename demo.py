#!/usr/bin/env python3
"""
Simple demo of the modular structure without external dependencies.
Shows how the contact extraction logic works.
"""

import sys
from unittest.mock import MagicMock

# Mock external dependencies
sys.modules['pandas'] = MagicMock()
sys.modules['bs4'] = MagicMock()

# Mock BeautifulSoup response
mock_soup = MagicMock()
mock_soup.find_all.return_value = [
    MagicMock(href="https://linkedin.com/company/test"),
    MagicMock(href="https://facebook.com/testcompany")
]
sys.modules['bs4'].BeautifulSoup.return_value = mock_soup

from scraper import ContactScraper
from csv_utils import create_result_entry
import config

def demo_contact_extraction():
    """Demonstrate contact extraction from HTML."""
    print("=== Contact Extraction Demo ===")
    
    scraper = ContactScraper()
    
    # Sample HTML content with various contact information
    sample_html = """
    <html>
    <head><title>Test Company</title></head>
    <body>
        <h1>Welcome to Test Company</h1>
        <div class="contact-info">
            <p>Email us at info@testcompany.com or sales@testcompany.it</p>
            <p>Call us: +39 02 1234567 or 011-987-6543</p>
            <p>Phone: tel:+393331234567</p>
            <p>WhatsApp: +39 333 123 4567</p>
        </div>
        <footer>
            <a href="https://linkedin.com/company/testcompany">LinkedIn</a>
            <a href="https://facebook.com/testcompany">Facebook</a>
            <a href="mailto:contact@testcompany.com">Contact Us</a>
        </footer>
        <!-- Some noise -->
        <img src="logo@2x.png" alt="Logo">
        <script>
            var email = "noscript@example.com";
        </script>
    </body>
    </html>
    """
    
    print("Extracting contacts from sample HTML...")
    emails, phones, socials = scraper.extract_contacts_from_html(sample_html)
    
    print(f"\n📧 Emails found ({len(emails)}):")
    for email in emails:
        print(f"  - {email}")
    
    print(f"\n📞 Phone numbers found ({len(phones)}):")
    for phone in phones:
        print(f"  - {phone}")
    
    print(f"\n🌐 Social media links found ({len(socials)}):")
    for social in socials:
        print(f"  - {social}")

def demo_result_creation():
    """Demonstrate result entry creation."""
    print("\n=== Result Creation Demo ===")
    
    # Create a sample result entry
    result = create_result_entry(
        nome_azienda="Test Company SRL",
        p_iva="12345678901",
        sito_usato="https://testcompany.com",
        emails=["info@testcompany.com", "sales@testcompany.com"],
        telefoni=["+390212345678", "+393331234567"],
        socials=["https://linkedin.com/company/testcompany"]
    )
    
    print("Sample result entry:")
    for key, value in result.items():
        print(f"  {key}: {value}")

def demo_configuration():
    """Demonstrate configuration options."""
    print("\n=== Configuration Demo ===")
    
    print("Current configuration:")
    print(f"  Output file: {config.FILE_OUTPUT}")
    print(f"  Headless mode: {config.HEADLESS_MODE}")
    print(f"  Max search results: {config.MAX_SEARCH_RESULTS}")
    print(f"  Contact keywords: {', '.join(config.CONTACT_KEYWORDS)}")
    print(f"  Email regex pattern: {config.EMAIL_REGEX}")
    print(f"  Phone regex pattern: {config.PHONE_REGEX}")
    
    print(f"\nProfile path: {config.get_profile_path()}")
    chrome_path = config.get_chrome_binary_path()
    if chrome_path:
        print(f"Chrome binary: {chrome_path}")
    else:
        print("Chrome binary: Will use auto-detection")

def demo_validation():
    """Demonstrate validation functions."""
    print("\n=== Validation Demo ===")
    
    scraper = ContactScraper()
    
    test_emails = [
        ("valid@example.com", True),
        ("info@test-site.org", True),
        ("notanemail", False),
        ("test@", False),
        ("@example.com", False),
        ("test@.com", False),
    ]
    
    print("Email validation:")
    for email, expected in test_emails:
        result = scraper._is_valid_email(email)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {email:<20} -> {result} (expected {expected})")
    
    test_phones = [
        ("+393123456789", True),
        ("0123456789", True),
        ("+15551234567", True),
        ("123", False),
        ("0000000000", False),
        ("abcdefghij", False),
    ]
    
    print("\nPhone validation:")
    for phone, expected in test_phones:
        result = scraper._is_valid_phone(phone)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {phone:<15} -> {result} (expected {expected})")

def main():
    """Run all demos."""
    print("🔍 OSINT Scraper - Modular Structure Demo")
    print("=" * 50)
    
    try:
        demo_contact_extraction()
        demo_result_creation()
        demo_configuration()
        demo_validation()
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("\nTo run the full scraper:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run: python main.py")
        print("3. Or use individual modules as shown in example_usage.py")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()