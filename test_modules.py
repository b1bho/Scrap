#!/usr/bin/env python3
"""
Simple test script to verify the modular structure works.
This tests the core logic without requiring Selenium or external dependencies.
"""

def test_config():
    """Test config module."""
    try:
        import config
        print("✓ config.py imports successfully")
        print(f"  - Output file: {config.FILE_OUTPUT}")
        print(f"  - Profile path: {config.get_profile_path()}")
        print(f"  - Contact keywords: {len(config.CONTACT_KEYWORDS)} defined")
        return True
    except Exception as e:
        print(f"✗ config.py failed: {e}")
        return False

def test_csv_utils():
    """Test CSV utilities."""
    try:
        # Mock pandas for testing
        import sys
        from unittest.mock import MagicMock
        
        sys.modules['pandas'] = MagicMock()
        
        import csv_utils
        print("✓ csv_utils.py imports successfully")
        
        # Test result entry creation
        result = csv_utils.create_result_entry(
            "Test Company", "123456789", "https://test.com",
            ["test@test.com"], ["+39123456789"], ["https://facebook.com/test"]
        )
        assert result['Ragione Sociale'] == "Test Company"
        assert result['Email Trovate'] == "test@test.com"
        print("  - create_result_entry works correctly")
        
        return True
    except Exception as e:
        print(f"✗ csv_utils.py failed: {e}")
        return False

def test_scraper_logic():
    """Test scraper contact extraction logic."""
    try:
        # Mock BeautifulSoup
        import sys
        from unittest.mock import MagicMock
        
        mock_bs4 = MagicMock()
        sys.modules['bs4'] = mock_bs4
        
        from scraper import ContactScraper
        scraper = ContactScraper()
        print("✓ scraper.py imports successfully")
        
        # Test email validation
        valid_emails = [
            "test@example.com",
            "info@company.it", 
            "contact@test-site.org"
        ]
        
        invalid_emails = [
            "notanemail",
            "test@",
            "@example.com",
            "test@example",
            "test@.com"
        ]
        
        for email in valid_emails:
            if not scraper._is_valid_email(email):
                print(f"  ✗ Should be valid: {email}")
                return False
                
        for email in invalid_emails:
            if scraper._is_valid_email(email):
                print(f"  ✗ Should be invalid: {email}")
                return False
                
        print("  - Email validation works correctly")
        
        # Test phone validation
        valid_phones = ["+393123456789", "0123456789", "+15551234567"]
        invalid_phones = ["123", "0000000000", "abcdefghij"]
        
        for phone in valid_phones:
            if not scraper._is_valid_phone(phone):
                print(f"  ✗ Should be valid phone: {phone}")
                return False
                
        for phone in invalid_phones:
            if scraper._is_valid_phone(phone):
                print(f"  ✗ Should be invalid phone: {phone}")
                return False
                
        print("  - Phone validation works correctly")
        
        return True
    except Exception as e:
        print(f"✗ scraper.py failed: {e}")
        return False

def test_browser_logic():
    """Test browser module logic (without actual browser)."""
    try:
        # Mock selenium modules
        import sys
        from unittest.mock import MagicMock
        
        for module in ['selenium', 'selenium.webdriver', 'selenium_stealth', 'webdriver_manager']:
            sys.modules[module] = MagicMock()
            
        # Mock selenium submodules
        sys.modules['selenium.webdriver.common.by'] = MagicMock()
        sys.modules['selenium.webdriver.common.keys'] = MagicMock()
        sys.modules['selenium.webdriver.chrome.service'] = MagicMock()
        sys.modules['selenium.webdriver.chrome.options'] = MagicMock()
        sys.modules['selenium.webdriver.support.ui'] = MagicMock()
        sys.modules['selenium.webdriver.support'] = MagicMock()
        sys.modules['selenium.webdriver.support.expected_conditions'] = MagicMock()
        sys.modules['webdriver_manager.chrome'] = MagicMock()
        
        from browser import BrowserManager
        browser = BrowserManager()
        print("✓ browser.py imports successfully")
        
        # Test URL validation
        valid_urls = [
            "https://example.com",
            "http://test-site.org/contact"
        ]
        
        invalid_urls = [
            "https://facebook.com/page",
            "https://google.com/search",
            "not-a-url",
            ""
        ]
        
        for url in valid_urls:
            if not browser._is_valid_url(url):
                print(f"  ✗ Should be valid URL: {url}")
                return False
                
        for url in invalid_urls:
            if browser._is_valid_url(url):
                print(f"  ✗ Should be invalid URL: {url}")
                return False
                
        print("  - URL validation works correctly")
        return True
    except Exception as e:
        print(f"✗ browser.py failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing modular OSINT scraper structure...\n")
    
    tests = [
        test_config,
        test_csv_utils,
        test_scraper_logic,
        test_browser_logic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The modular structure is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)