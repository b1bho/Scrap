"""
CSV utilities for reading input and writing output data.
"""
import pandas as pd
import logging
from typing import List, Dict, Optional
from config import COLONNA_NOMI_AZIENDE, COLONNA_PIVA, COLONNA_CITTA, FILE_OUTPUT

def read_companies_csv(file_path: str) -> Optional[pd.DataFrame]:
    """
    Read companies data from CSV file.
    
    Args:
        file_path: Path to the input CSV file
        
    Returns:
        DataFrame with company data or None if error occurred
    """
    try:
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_columns = [COLONNA_NOMI_AZIENDE, COLONNA_PIVA, COLONNA_CITTA]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logging.error(f"Missing required columns: {missing_columns}")
            return None
            
        logging.info(f"Successfully loaded {len(df)} companies from {file_path}")
        return df
        
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found")
        return None
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return None

def get_user_input_file() -> str:
    """
    Get input file path from user with validation.
    
    Returns:
        Valid file path as string
    """
    while True:
        file_path = input("Inserisci il nome del file CSV da analizzare (es. aziende.csv): ")
        df = read_companies_csv(file_path)
        if df is not None:
            return file_path
        print("File non valido o non trovato. Riprova.")

def write_results_csv(results: List[Dict], output_file: str = None) -> bool:
    """
    Write results to CSV file.
    
    Args:
        results: List of dictionaries with company contact data
        output_file: Output file path (defaults to config FILE_OUTPUT)
        
    Returns:
        True if successful, False otherwise
    """
    if not results:
        logging.warning("No results to save")
        return False
        
    output_path = output_file or FILE_OUTPUT
    
    try:
        df_output = pd.DataFrame(results)
        df_output.to_csv(output_path, index=False, encoding='utf-8-sig')
        logging.info(f"Results saved to '{output_path}'")
        return True
    except Exception as e:
        logging.error(f"Error writing results to CSV: {e}")
        return False

def create_result_entry(nome_azienda: str, p_iva: str, sito_usato: str,
                       emails: List[str], telefoni: List[str], 
                       socials: List[str]) -> Dict:
    """
    Create a standardized result entry dictionary.
    
    Args:
        nome_azienda: Company name
        p_iva: VAT number
        sito_usato: Website analyzed
        emails: List of email addresses found
        telefoni: List of phone numbers found
        socials: List of social media links found
        
    Returns:
        Dictionary with standardized result format
    """
    return {
        'Ragione Sociale': nome_azienda,
        'P.IVA': p_iva,
        'Sito Web Analizzato': sito_usato,
        'Email Trovate': ', '.join(emails) if emails else '',
        'Telefoni Trovati': ', '.join(telefoni) if telefoni else '',
        'Socials Trovati': ', '.join(socials) if socials else ''
    }