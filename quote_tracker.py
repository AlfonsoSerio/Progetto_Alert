#!/usr/bin/env python3
"""
================================================================================
QUOTE TRACKER v1.0 - FLASHSCORE QUOTE MONITORING
================================================================================

Monitora l'apertura delle quote su Flashscore e invia notifiche Telegram.

FLOW:
  1. Legge partite da matches_to_track.csv
  2. Verifica ogni 30 minuti se quote sono aperte
  3. Invia notifica Telegram quando quote SI APRONO
  4. Aggiorna status nel CSV

COSTO: €0 (Flashscore gratis, Telegram gratis, niente API pagate)
FREQUENZA: Ogni 30 minuti
DEPLOYMENT: Railway.app (€5/mese, sempre acceso)

================================================================================
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
from dotenv import load_dotenv
import time
import logging

# ============================================================
# CONFIGURAZIONE
# ============================================================

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CSV_FILE = 'matches_to_track.csv'
LOG_FILE = 'quote_tracker.log'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# ============================================================
# FUNZIONI CORE
# ============================================================

def check_flashscore_quotes(match_id):
    """
    Verifica se le quote sono aperte per una partita su Flashscore.
    
    Ritorna:
        - True se quote APERTE
        - False se quote NON APERTE
        - None se partita NON TROVATA
    """
    try:
        url = f"https://www.flashscore.com/match/{match_id}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            logging.warning(f"❌ Match ID {match_id} non trovato su Flashscore")
            return None
        
        if response.status_code != 200:
            logging.warning(f"⚠️ Errore Flashscore per {match_id}: HTTP {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Cerca sezione quote (indicatore di apertura)
        # Flashscore mostra quote solo se aperte
        quote_section = soup.find('div', {'class': 'odds-table'}) or \
                       soup.find('div', {'class': 'bookmakers'}) or \
                       soup.find('section', {'class': lambda x: x and 'odds' in x.lower()})
        
        if quote_section:
            logging.info(f"✅ Quote APERTE per match {match_id}")
            return True
        else:
            logging.info(f"⏳ Quote NON aperte per match {match_id}")
            return False
    
    except requests.exceptions.Timeout:
        logging.error(f"⏱️ Timeout per match {match_id}")
        return None
    except Exception as e:
        logging.error(f"❌ Errore per match {match_id}: {str(e)}")
        return None

def send_telegram_notification(message):
    """Invia notifica Telegram"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("❌ TELEGRAM_TOKEN o TELEGRAM_CHAT_ID non configurati")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            logging.info("✅ Notifica Telegram inviata")
            return True
        else:
            logging.error(f"❌ Errore Telegram: {response.text}")
            return False
    
    except Exception as e:
        logging.error(f"❌ Errore invio Telegram: {str(e)}")
        return False

def load_matches():
    """Carica partite da CSV"""
    try:
        if not os.path.exists(CSV_FILE):
            logging.warning(f"⚠️ {CSV_FILE} non trovato - creando template...")
            create_csv_template()
            return pd.DataFrame()
        
        df = pd.read_csv(CSV_FILE)
        logging.info(f"✅ Caricate {len(df)} partite da monitorare")
        return df
    
    except Exception as e:
        logging.error(f"❌ Errore caricamento CSV: {str(e)}")
        return pd.DataFrame()

def create_csv_template():
    """Crea template CSV se non esiste"""
    template_data = {
        'match_id': ['1234567', '7654321'],
        'team1': ['Juventus', 'Inter'],
        'team2': ['AC Milan', 'Napoli'],
        'date': ['2026-09-20', '2026-09-21'],
        'status': ['checking', 'checking'],
        'notified': [False, False]
    }
    
    df = pd.DataFrame(template_data)
    df.to_csv(CSV_FILE, index=False)
    logging.info(f"✅ Template creato: {CSV_FILE}")

def save_matches(df):
    """Salva partite su CSV"""
    try:
        df.to_csv(CSV_FILE, index=False)
        logging.info("✅ CSV aggiornato")
    except Exception as e:
        logging.error(f"❌ Errore salvataggio CSV: {str(e)}")

def main():
    """Loop principale di monitoraggio"""
    logging.info("="*80)
    logging.info("🎯 QUOTE TRACKER AVVIATO")
    logging.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("="*80)
    
    df = load_matches()
    
    if df.empty:
        logging.warning("⚠️ Nessuna partita da monitorare. Aggiungi partite a matches_to_track.csv")
        return
    
    # Processa ogni partita
    for idx, row in df.iterrows():
        match_id = row['match_id']
        team1 = row['team1']
        team2 = row['team2']
        date = row.get('date', 'N/A')
        notified = row.get('notified', False)
        
        logging.info(f"\n🔍 Verificando: {team1} vs {team2} ({date}) [Match ID: {match_id}]")
        
        # Se già notificato, skip
        if notified:
            logging.info(f"✅ Già notificato - skip")
            continue
        
        # Verifica quote
        quotes_open = check_flashscore_quotes(match_id)
        
        if quotes_open is None:
            df.at[idx, 'status'] = 'not_found'
            continue
        
        if quotes_open and not notified:
            # Quote aperte! Invia notifica
            message = (
                f"🎯 <b>QUOTE APERTE!</b>\n\n"
                f"📅 {team1} vs {team2}\n"
                f"📆 {date}\n"
                f"🔗 <a href='https://www.flashscore.com/match/{match_id}/'>Vai su Flashscore</a>\n\n"
                f"⏱️ Quote aperte alle {datetime.now().strftime('%H:%M:%S')}"
            )
            
            if send_telegram_notification(message):
                df.at[idx, 'notified'] = True
                df.at[idx, 'status'] = 'notified'
            else:
                df.at[idx, 'status'] = 'notification_failed'
        
        else:
            df.at[idx, 'status'] = 'waiting'
    
    # Salva aggiornamenti
    save_matches(df)
    
    logging.info("\n" + "="*80)
    logging.info(f"✅ Monitoraggio completato")
    logging.info("="*80)

if __name__ == "__main__":
    main()
