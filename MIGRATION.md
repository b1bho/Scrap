# Migration Guide: From Monolithic to Modular OSINT Scraper

This guide helps you transition from the original `OSINT_Sel_Chrome.py` script to the new modular structure.

## What Changed

### Old Structure (Single File)
```
OSINT_Sel_Chrome.py  # Everything in one file (~300 lines)
```

### New Structure (Modular)
```
config.py           # Configuration constants
csv_utils.py        # CSV reading/writing functions  
browser.py          # Browser management and search
scraper.py          # Contact extraction logic
main.py             # Main orchestration
requirements.txt    # Dependencies
README.md           # Documentation
demo.py             # Working demo
example_usage.py    # API usage examples
test_modules.py     # Module tests
```

## Quick Migration

### Option 1: Use the New Main Script (Easiest)
The new `main.py` works exactly like the old script:

```bash
# Old way
python OSINT_Sel_Chrome.py

# New way  
python main.py
```

Same input/output format, same CSV columns, same behavior.

### Option 2: Keep Using the Old Script
The original `OSINT_Sel_Chrome.py` still works and has been fixed:
- ✅ Added missing `BeautifulSoup` import
- ✅ All original functionality preserved

## New Features Available

### 1. Configuration Without Code Changes
Edit `config.py` to customize:
```python
# Enable headless mode
HEADLESS_MODE = True

# Get more search results
MAX_SEARCH_RESULTS = 5

# Adjust timeouts
MIN_WAIT = 5
MAX_WAIT = 10
```

### 2. Programmatic API
```python
from browser import BrowserManager
from scraper import ContactScraper

scraper = ContactScraper()
with BrowserManager() as browser:
    site, emails, phones, socials = scraper.analyze_company_contacts(
        browser, "Company Name", "City"
    )
```

### 3. Better Error Handling
- Automatic retries on page load failures
- Graceful handling of anti-bot measures
- Better timeout management
- Detailed logging

### 4. Improved Contact Detection
- Smarter contact page detection
- Multiple URL strategies (main site + contact/about pages)
- Better email/phone validation
- Priority-based scraping (contact pages first)

## Configuration Comparison

### Old Script Configuration
All settings were hardcoded in the script:
```python
# Had to edit the script file
MIN_WAIT = 7
MAX_WAIT = 15
USER_AGENT_REALE = "Mozilla/5.0..."
```

### New Configuration
Settings in separate `config.py`:
```python
# Easy to modify without touching core code
MIN_WAIT = 7
MAX_WAIT = 15
HEADLESS_MODE = False  # New option!
MAX_SEARCH_RESULTS = 3  # Configurable!
```

## Feature Enhancements

| Feature | Old Script | New Modular |
|---------|------------|-------------|
| Contact page detection | Basic | Multi-strategy |
| Error handling | Basic | Retry logic + backoff |
| Email validation | Regex only | Regex + format validation |
| Phone validation | Length check | International format validation |
| Configuration | Hardcoded | External config file |
| Logging | Basic | Structured with levels |
| API usage | Not possible | Full programmatic API |
| Testing | None | Comprehensive test suite |

## Backward Compatibility

✅ **100% Compatible**: All existing CSV files and workflows work unchanged.

✅ **Same Output Format**: Results CSV has identical structure.

✅ **Same Dependencies**: Uses the same Python packages.

✅ **Same Authentication**: Chrome profile and Google login process unchanged.

## When to Migrate

### Use New Modular Version If:
- You want better error handling and reliability
- You need programmatic access to the scraper
- You want to customize behavior without editing code
- You're integrating into larger applications
- You need better logging and monitoring

### Keep Old Script If:
- Current script works perfectly for your needs
- You don't want to change your workflow
- You prefer single-file simplicity

## Migration Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Test New Version
```bash
# Test with same CSV file
python main.py
```

### Step 3: Compare Results
Both versions should produce identical results for the same input.

### Step 4: Update Automation (if any)
```bash
# Old automation
python OSINT_Sel_Chrome.py

# New automation  
python main.py
```

## Advanced Usage After Migration

### Custom Processing Pipeline
```python
from csv_utils import read_companies_csv
from browser import BrowserManager
from scraper import ContactScraper

# Load companies
companies = read_companies_csv('input.csv')

# Custom processing
with BrowserManager() as browser:
    scraper = ContactScraper()
    for _, company in companies.iterrows():
        # Your custom logic here
        results = scraper.analyze_company_contacts(...)
```

### Configuration Overrides
```python
import config

# Temporarily modify settings
config.HEADLESS_MODE = True
config.MAX_SEARCH_RESULTS = 10

# Run with custom settings
from main import main
main()
```

## Troubleshooting Migration

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Different results than old script**
   - Check that input CSV format matches exactly
   - Verify same Chrome profile is being used
   - Compare logs for differences in search behavior

3. **Performance differences**
   - New version may be slightly slower due to better contact page detection
   - Adjust timeouts in `config.py` if needed

4. **Chrome profile issues**
   - Both versions use the same profile directory
   - No need to re-authenticate

## Support

- **Old Script**: Continue using `OSINT_Sel_Chrome.py` 
- **New Version**: Use `main.py` or programmatic API
- **Demo**: Run `python demo.py` to see new features
- **Examples**: Check `example_usage.py` for API usage

The modular version is a drop-in replacement with significant improvements while maintaining full backward compatibility.