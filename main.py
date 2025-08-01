"""
Main orchestration module for the OSINT scraper.
"""
import logging
from typing import List, Dict

from config import LOG_LEVEL, LOG_FORMAT
from csv_utils import get_user_input_file, read_companies_csv, write_results_csv, create_result_entry
from browser import BrowserManager, check_first_run
from scraper import ContactScraper

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT
    )

def main():
    """Main function to orchestrate the OSINT scraping process."""
    setup_logging()
    
    # Check if this is first run and show authentication instructions
    check_first_run()
    
    logging.info("Starting OSINT scraper (modular version)...")
    
    # Get input file from user
    input_file = get_user_input_file()
    df_input = read_companies_csv(input_file)
    
    if df_input is None:
        logging.error("Could not load input file. Exiting.")
        return
    
    # Initialize scraper
    scraper = ContactScraper()
    results = []
    
    # Use browser manager with context manager for automatic cleanup
    with BrowserManager() as browser:
        if not browser.driver:
            logging.error("Could not initialize browser. Exiting.")
            return
        
        # Process each company
        for index, row in df_input.iterrows():
            nome_azienda = str(row['Ragione Sociale'])
            p_iva = str(row['P.IVA'])
            citta = str(row['Città'])
            
            logging.info(f"--- ({index + 1}/{len(df_input)}) Processing: {nome_azienda} ---")
            
            try:
                # Analyze company for contacts
                sito_usato, emails, telefoni, socials = scraper.analyze_company_contacts(
                    browser, nome_azienda, citta
                )
                
                # Create result entry
                result = create_result_entry(
                    nome_azienda, p_iva, sito_usato, 
                    emails, telefoni, socials
                )
                results.append(result)
                
                # Log summary
                if emails or telefoni or socials:
                    logging.info(f"✓ Found contacts for {nome_azienda}")
                else:
                    logging.warning(f"✗ No contacts found for {nome_azienda}")
                    
            except Exception as e:
                logging.error(f"Error processing {nome_azienda}: {e}")
                # Add empty result for failed processing
                result = create_result_entry(
                    nome_azienda, p_iva, "Errore durante l'analisi", 
                    [], [], []
                )
                results.append(result)
    
    # Save results
    if results:
        success = write_results_csv(results)
        if success:
            logging.info("--- Analysis completed successfully! ---")
        else:
            logging.error("Failed to save results")
    else:
        logging.warning("No results to save")

if __name__ == '__main__':
    main()