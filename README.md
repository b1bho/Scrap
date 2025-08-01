# OSINT Contact Scraper

A modular Python tool for scraping contact information (emails, phone numbers, social media) from company websites using automated Google searches and Selenium WebDriver.

## 🆕 New Modular Version vs Original

| Feature | Original Script | New Modular Version |
|---------|----------------|-------------------|
| **Structure** | Single 300-line file | 5 focused modules |
| **Configuration** | Hardcoded in script | External config file |
| **Contact Detection** | Basic single page | Multi-page + contact pages |
| **Error Handling** | Basic | Retry logic + backoff |
| **Validation** | Regex only | Format + content validation |
| **API Usage** | Not possible | Full programmatic API |
| **Testing** | None | Comprehensive test suite |
| **Customization** | Edit source code | Configuration file |

**✅ 100% Backward Compatible** - Same input/output format, same results.

## Quick Start

### Option 1: Use New Modular Version (Recommended)
```bash
pip install -r requirements.txt
python main.py
```

### Option 2: Keep Using Original Script
```bash
pip install -r requirements.txt  
python OSINT_Sel_Chrome.py
```

### Option 3: Try the Demo (No Dependencies)
```bash
python demo.py
```

## Features

- **Modular Architecture**: Separated concerns into focused modules
- **Google Search Integration**: Automated Google searches to find company websites
- **Smart Contact Detection**: Finds contact pages, about pages, and main sites
- **Multi-source Scraping**: Extracts contacts from multiple pages per company
- **Anti-bot Protection**: Uses stealth mode and human-like interactions
- **Configurable**: Easy configuration through `config.py`
- **Robust Error Handling**: Continues processing even if individual sites fail
- **CSV Integration**: Reads input from CSV, outputs structured results

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Scrap
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure Chrome browser is installed on your system.

## Usage

### Basic Usage

1. Prepare your input CSV file with the following columns:
   - `Ragione Sociale` (Company Name)
   - `P.IVA` (VAT Number)
   - `Città` (City)

2. Run the script:
```bash
python main.py
```

3. When prompted, enter the path to your CSV file:
```
Inserisci il nome del file CSV da analizzare (es. aziende.csv): companies.csv
```

### First Run Setup

On the first run, the script will:
1. Open a Chrome window
2. Ask you to manually log into your Google account
3. Save the session for future runs

This is required to avoid Google's anti-bot measures.

### Example Input CSV

```csv
Ragione Sociale,P.IVA,Città
Tech Solutions SRL,12345678901,Milano
Green Energy SpA,98765432109,Roma
Digital Marketing SNC,11223344556,Napoli
```

### Example Output

The script generates `risultati_osint_selenium_chrome.csv` with:

```csv
Ragione Sociale,P.IVA,Sito Web Analizzato,Email Trovate,Telefoni Trovati,Socials Trovati
Tech Solutions SRL,12345678901,https://techsolutions.it,info@techsolutions.it,+390123456789,https://linkedin.com/company/techsolutions
Green Energy SpA,98765432109,https://greenenergy.com,"contact@greenenergy.com, sales@greenenergy.com",+390987654321,https://facebook.com/greenenergy
```

## Configuration

Edit `config.py` to customize:

- **File paths**: Input/output CSV locations
- **Browser settings**: Headless mode, timeouts, user agent
- **Search parameters**: Number of results, excluded domains
- **Contact patterns**: Email/phone regex patterns
- **Retry logic**: Max retries, backoff factors

### Key Configuration Options

```python
# Run in headless mode (no visible browser)
HEADLESS_MODE = True

# Maximum search results to analyze per company
MAX_SEARCH_RESULTS = 5

# Timeout settings
MIN_WAIT = 7
MAX_WAIT = 15

# Contact page keywords to look for
CONTACT_KEYWORDS = ["contatti", "contact", "about", "chi siamo"]
```

## Module Structure

- **`main.py`**: Main orchestration script
- **`config.py`**: Configuration constants and settings
- **`csv_utils.py`**: CSV reading and writing utilities
- **`browser.py`**: Selenium WebDriver management and Google search
- **`scraper.py`**: Contact information extraction logic

## Advanced Usage

### Programmatic Usage

```python
from browser import BrowserManager
from scraper import ContactScraper
from csv_utils import read_companies_csv, write_results_csv

# Initialize components
scraper = ContactScraper()
companies_df = read_companies_csv('input.csv')

# Process companies
with BrowserManager() as browser:
    for _, company in companies_df.iterrows():
        site, emails, phones, socials = scraper.analyze_company_contacts(
            browser, company['Ragione Sociale'], company['Città']
        )
        print(f"Found {len(emails)} emails for {company['Ragione Sociale']}")
```

### Custom Configuration

```python
# Override configuration
import config
config.HEADLESS_MODE = True
config.MAX_SEARCH_RESULTS = 10

# Then run normally
from main import main
main()
```

## Troubleshooting

### Common Issues

1. **Chrome not found**: Install Google Chrome browser
2. **Selenium errors**: Update Chrome and webdriver-manager
3. **Google blocking**: Use a different IP or wait before retrying
4. **Missing contacts**: Some sites may use JavaScript - the scraper handles this

### Logging

The script provides detailed logging. Check the console output for:
- Search results found
- Pages being scraped
- Contacts extracted
- Errors encountered

### Performance Tips

- Run during off-peak hours to avoid rate limiting
- Use headless mode for better performance
- Adjust wait times in `config.py` based on your internet speed
- Consider using a VPN if you encounter blocking

## Legal Notice

This tool is for educational and legitimate business research purposes only. Always respect:
- Website terms of service
- Robots.txt files
- Rate limiting
- Privacy laws and regulations
- Data protection requirements

Users are responsible for ensuring their usage complies with applicable laws and website policies.

## License

[Add your license information here]