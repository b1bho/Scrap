#!/usr/bin/env python3
"""
Example usage of the modular OSINT scraper API.
This demonstrates how to use the components programmatically.
"""

from browser import BrowserManager, check_first_run
from scraper import ContactScraper
from csv_utils import read_companies_csv, write_results_csv, create_result_entry
import config
import logging

def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def example_single_company():
    """Example: Analyze a single company."""
    print("=== Single Company Analysis Example ===")
    
    setup_logging()
    check_first_run()
    
    # Initialize components
    scraper = ContactScraper()
    
    # Analyze one company
    with BrowserManager() as browser:
        if not browser.driver:
            print("Could not initialize browser")
            return
            
        company_name = "Tech Solutions SRL"
        city = "Milano"
        
        print(f"Analyzing: {company_name} in {city}")
        
        site, emails, phones, socials = scraper.analyze_company_contacts(
            browser, company_name, city
        )
        
        print(f"\nResults for {company_name}:")
        print(f"  Main site: {site}")
        print(f"  Emails found: {emails}")
        print(f"  Phones found: {phones}")
        print(f"  Social media: {socials}")

def example_csv_processing():
    """Example: Process companies from CSV file."""
    print("=== CSV Processing Example ===")
    
    setup_logging()
    
    # Read companies from CSV
    companies_df = read_companies_csv('sample_companies.csv')
    if companies_df is None:
        print("Could not load sample companies CSV")
        return
    
    print(f"Loaded {len(companies_df)} companies from CSV")
    
    # Process first company only for demo
    company = companies_df.iloc[0]
    print(f"Processing: {company['Ragione Sociale']}")
    
    # Create mock results (since we don't have full browser environment)
    results = []
    result = create_result_entry(
        company['Ragione Sociale'],
        company['P.IVA'], 
        "https://example.com",
        ["info@example.com", "contact@example.com"],
        ["+390123456789"],
        ["https://linkedin.com/company/example"]
    )
    results.append(result)
    
    # Write results
    success = write_results_csv(results, 'example_output.csv')
    if success:
        print("Results saved to example_output.csv")

def example_custom_configuration():
    """Example: Use custom configuration."""
    print("=== Custom Configuration Example ===")
    
    # Modify configuration at runtime
    original_headless = config.HEADLESS_MODE
    original_max_results = config.MAX_SEARCH_RESULTS
    
    # Enable headless mode and increase search results
    config.HEADLESS_MODE = True
    config.MAX_SEARCH_RESULTS = 5
    
    print(f"Headless mode: {config.HEADLESS_MODE}")
    print(f"Max search results: {config.MAX_SEARCH_RESULTS}")
    print(f"Contact keywords: {config.CONTACT_KEYWORDS}")
    
    # Restore original values
    config.HEADLESS_MODE = original_headless
    config.MAX_SEARCH_RESULTS = original_max_results

def example_url_scraping():
    """Example: Direct URL scraping without Google search."""
    print("=== Direct URL Scraping Example ===")
    
    setup_logging()
    
    # URLs to scrape (example URLs)
    test_urls = [
        "https://httpbin.org/html",  # Simple HTML page for testing
        "https://example.com"
    ]
    
    scraper = ContactScraper()
    
    # Test contact extraction from sample HTML
    sample_html = """
    <html>
        <body>
            <p>Contact us at info@example.com or call +39 02 1234567</p>
            <a href="https://linkedin.com/company/example">LinkedIn</a>
            <a href="mailto:sales@example.com">Email Sales</a>
        </body>
    </html>
    """
    
    emails, phones, socials = scraper.extract_contacts_from_html(sample_html)
    
    print("Extracted from sample HTML:")
    print(f"  Emails: {emails}")
    print(f"  Phones: {phones}")
    print(f"  Socials: {socials}")

def main():
    """Run all examples."""
    print("OSINT Scraper - Usage Examples\n")
    
    examples = [
        example_custom_configuration,
        example_url_scraping,
        example_csv_processing,
        # example_single_company,  # Commented out as it requires browser setup
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. ", end="")
        try:
            example()
        except Exception as e:
            print(f"Example failed: {e}")
        print("-" * 50)

if __name__ == "__main__":
    main()