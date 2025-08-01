import pandas as pd
import time
import random
import re
import logging
from urllib.parse import urljoin, urlparse
import os

# Importazioni per Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from bs4 import BeautifulSoup

# --- CONFIGURAZIONE ---
FILE_OUTPUT = 'risultati_osint_selenium_chrome.csv'
COLONNA_NOMI_AZIENDE = 'Ragione Sociale'
COLONNA_PIVA = 'P.IVA'
COLONNA_CITTA = 'Città'

MIN_WAIT = 7
MAX_WAIT = 15

# --- MODIFICA FONDAMENTALE: INSERISCI QUI IL TUO USER-AGENT ---
# 1. Cerca su Google "what is my user agent"
# 2. Copia la stringa che ti viene mostrata e incollala qui sotto.
USER_AGENT_REALE = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36" # <--- INCOLLA QUI IL TUO USER AGENT


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_selenium_driver():
    """Configura e restituisce un'istanza del WebDriver di Selenium per Chrome."""
    options = ChromeOptions()
    # options.add_argument("--headless") # Manteniamo visibile per massima compatibilità
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    
    # Specifica il percorso dell'eseguibile di Chrome su Linux per maggiore stabilità
    chrome_binary_path = "/usr/bin/google-chrome-stable"
    if os.path.exists(chrome_binary_path):
        options.binary_location = chrome_binary_path
        logging.info(f"Trovato eseguibile di Chrome in: {chrome_binary_path}")
    else:
        logging.warning(f"Eseguibile di Chrome non trovato nel percorso standard '{chrome_binary_path}'. Selenium proverà a trovarlo automaticamente.")

    # Usa un profilo DEDICATO e PERSISTENTE per lo script
    profile_path = os.path.join(os.getcwd(), "chrome_profile_for_script")
    options.add_argument(f"user-data-dir={profile_path}")
    logging.info(f"Uso del profilo dedicato per lo script in: {profile_path}")


    # Opzioni per mascherare l'automazione
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Applica l'User-Agent reale
    options.add_argument(f"user-agent={USER_AGENT_REALE}")

    logging.info("Configurazione del driver di Selenium per Chrome...")
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        stealth(driver,
                languages=["it-IT", "it"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

        logging.info("Driver di Chrome configurato con successo.")
        return driver
    except Exception as e:
        logging.error(f"Errore durante la configurazione di Selenium. Errore: {e}")
        return None

def human_typing(element, text):
    """Simula la digitazione umana lettera per lettera."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

def cerca_con_selenium(driver, nome_azienda, citta):
    """
    Simula una ricerca umana su Google per eludere il reCAPTCHA.
    """
    siti_trovati = []
    query = f'"{nome_azienda}" "{citta}" contatti sito ufficiale'
    
    try:
        driver.get("https://www.google.com")
        time.sleep(random.uniform(2, 4))

        try:
            wait = WebDriverWait(driver, 5)
            accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//div[contains(text(), 'Accetta tutto')]]")))
            accept_button.click()
            logging.info("    Pop-up dei cookie sulla homepage gestito.")
            time.sleep(random.uniform(1, 2))
        except Exception:
            logging.info("    Nessun pop-up dei cookie sulla homepage (normale con profilo esistente).")

        search_bar = driver.find_element(By.NAME, "q")
        search_bar.clear()
        human_typing(search_bar, query)
        time.sleep(random.uniform(0.5, 1))
        search_bar.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "search")))
        time.sleep(random.uniform(2, 4))
        
        # --- MODIFICA CHIAVE: Selettore più robusto per i link di ricerca ---
        link_elements = driver.find_elements(By.XPATH, '//a[h3]')
        
        for link_element in link_elements:
            href = link_element.get_attribute('href')
            if href and href.startswith('http'):
                if not any(domain in href for domain in ['facebook.com', 'linkedin.com', 'google.com', 'paginegialle.it', 'instagram.com', 'youtube.com']):
                    siti_trovati.append(href)
                    if len(siti_trovati) >= 3:
                        break
    except Exception as e:
        logging.error(f"    Errore durante la ricerca con Selenium per '{nome_azienda}': {e}")
    return siti_trovati

def estrai_contatti_da_pagina(page_source):
    """Estrae email, telefoni e social dal codice sorgente di una pagina."""
    emails = set()
    telefoni = set()
    socials = set()

    # Estrazione Email
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}'
    trovate_email = re.findall(email_regex, page_source)
    for email in trovate_email:
        if not email.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
             emails.add(email)

    # Estrazione Telefoni
    telefono_regex = r'(?:tel:|callto:)?\s*(?:\+?39)?[\s.-]*\(?\d{2,5}\)?[\s.-]*\d{2,4}[\s.-]*\d{2,4}[\s.-]*\d{2,4}'
    trovati_telefoni = re.findall(telefono_regex, page_source)
    for tel in trovati_telefoni:
        tel_pulito = re.sub(r'[^\d+]', '', tel).replace("tel:", "").replace("callto:", "")
        if len(tel_pulito) > 8:
            telefoni.add(tel_pulito.strip())

    # Estrazione Social Media
    soup = BeautifulSoup(page_source, 'html.parser')
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if any(social_domain in href for social_domain in ['linkedin.com/company', 'facebook.com', 'instagram.com', 'twitter.com/']):
            socials.add(href)

    return emails, telefoni, socials

def analizza_sito_con_selenium(driver, base_url):
    """
    Analizza un sito usando Selenium, navigando attivamente
    alla ricerca di pagine di contatto.
    """
    all_emails = set()
    all_telefoni = set()
    all_socials = set()
    
    try:
        # 1. Analizza la pagina di atterraggio (homepage)
        logging.info(f"    -> Analizzo pagina principale: {base_url}")
        driver.get(base_url)
        time.sleep(random.uniform(4, 6)) # Attesa più lunga per JS complessi

        page_source = driver.page_source
        emails, telefoni, socials = estrai_contatti_da_pagina(page_source)
        all_emails.update(emails)
        all_telefoni.update(telefoni)
        all_socials.update(socials)

        # 2. MODIFICA CHIAVE: Cerca SEMPRE un link "Contatti" per massimizzare la raccolta dati
        logging.info("    Cerco link interni a pagine 'Contatti' per un'analisi più approfondita...")
        
        possible_link_texts = ["contatti", "contact", "contattaci", "chi siamo", "about us", "lavora con noi"]
        link_trovato = None

        for text in possible_link_texts:
            try:
                # Cerca link che contengono il testo (case-insensitive con XPath)
                link_trovato = driver.find_element(By.XPATH, f"//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
                if link_trovato and link_trovato.is_displayed() and link_trovato.is_enabled():
                    logging.info(f"    Trovato link '{link_trovato.text}'. Navigo alla pagina...")
                    link_trovato.click()
                    time.sleep(random.uniform(4, 6)) # Attendi caricamento nuova pagina
                    
                    # Analizza la nuova pagina
                    logging.info(f"    -> Analizzo pagina contatti: {driver.current_url}")
                    page_source = driver.page_source
                    emails, telefoni, socials = estrai_contatti_da_pagina(page_source)
                    all_emails.update(emails)
                    all_telefoni.update(telefoni)
                    all_socials.update(socials)
                    break # Esci dal loop una volta trovata e analizzata la pagina contatti
            except Exception:
                continue # Se non trova il link con quel testo, prova il successivo

        if not link_trovato:
            logging.warning("    Nessun link 'Contatti' o simile trovato da cliccare.")

    except Exception as e:
        logging.warning(f"      Impossibile analizzare il sito {base_url} con Selenium: {e}")
            
    return list(all_emails), list(all_telefoni), list(all_socials)

def main():
    profile_dir = os.path.join(os.getcwd(), "chrome_profile_for_script")
    if not os.path.exists(profile_dir):
        print("="*70)
        print("ATTENZIONE: PRIMA ESECUZIONE DELLO SCRIPT")
        print("1. Si aprirà una finestra di Chrome.")
        print("2. ACCEDI MANUALMENTE al tuo account Google in quella finestra.")
        print("3. Una volta fatto, puoi chiudere la finestra e riavviare lo script.")
        print("   Dovrai fare questa operazione solo una volta.")
        print("="*70)
        time.sleep(8)
    
    logging.info("Avvio dello script OSINT (versione full Selenium)...")

    driver = setup_selenium_driver()
    if not driver:
        return

    while True:
        file_input_utente = input("Inserisci il nome del file CSV da analizzare (es. aziende.csv): ")
        try:
            df_input = pd.read_csv(file_input_utente)
            if not all(col in df_input.columns for col in [COLONNA_NOMI_AZIENDE, COLONNA_PIVA, COLONNA_CITTA]):
                logging.error(f"ERRORE: Il file deve contenere le colonne '{COLONNA_NOMI_AZIENDE}', '{COLONNA_PIVA}' e '{COLONNA_CITTA}'.")
                continue
            logging.info(f"File '{file_input_utente}' caricato. Trovate {len(df_input)} aziende.")
            break
        except FileNotFoundError:
            logging.error(f"ERRORE: File '{file_input_utente}' non trovato. Riprova.")
        except Exception as e:
            logging.error(f"Si è verificato un errore imprevisto: {e}")

    risultati = []
    
    for index, row in df_input.iterrows():
        nome_azienda = str(row[COLONNA_NOMI_AZIENDE])
        p_iva = str(row[COLONNA_PIVA])
        citta = str(row[COLONNA_CITTA])
        
        logging.info(f"--- ({index + 1}/{len(df_input)}) Inizio analisi per: {nome_azienda} ---")

        # 1. USA SELENIUM PER LA RICERCA GOOGLE
        logging.info("  Uso Selenium per la ricerca su Google...")
        siti_web = cerca_con_selenium(driver, nome_azienda, citta)
        
        sito_usato = "Non trovato"
        emails_finali, telefoni_finali, socials_finali = [], [], []

        if not siti_web:
            logging.warning(f"  Nessun sito web pertinente trovato per {nome_azienda} dalla ricerca Selenium.")
        else:
            # 2. MODIFICA CHIAVE: Analizza solo il primo e più rilevante sito web
            sito_da_analizzare = siti_web[0]
            logging.info(f"  Trovato sito principale: {sito_da_analizzare}. Avvio analisi approfondita...")
            
            emails, telefoni, socials = analizza_sito_con_selenium(driver, sito_da_analizzare)
            
            if emails or telefoni or socials:
                logging.info(f"    >> DATI TROVATI! Email: {len(emails)}, Telefoni: {len(telefoni)}, Social: {len(socials)}")
                sito_usato = sito_da_analizzare
                emails_finali = emails
                telefoni_finali = telefoni
                socials_finali = socials
            else:
                logging.warning(f"    Nessun contatto trovato dopo l'analisi approfondita di {sito_da_analizzare}.")

        risultati.append({
            'Ragione Sociale': nome_azienda,
            'P.IVA': p_iva,
            'Sito Web Analizzato': sito_usato,
            'Email Trovate': ', '.join(emails_finali),
            'Telefoni Trovati': ', '.join(telefoni_finali),
            'Socials Trovati': ', '.join(socials_finali)
        })

    driver.quit() # Chiudi il browser di Selenium

    if risultati:
        df_output = pd.DataFrame(risultati)
        df_output.to_csv(FILE_OUTPUT, index=False, encoding='utf-8-sig')
        logging.info(f"--- Analisi completata! I risultati sono stati salvati in '{FILE_OUTPUT}' ---")
    else:
        logging.warning("Nessun risultato da salvare.")

if __name__ == '__main__':
    main()
