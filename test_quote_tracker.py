#!/usr/bin/env python3
"""
================================================================================
TEST QUOTE TRACKER - UTILITY PER TESTING LOCALE
================================================================================

Questo script permette di testare il quote_tracker manualmente senza aspettare
30 minuti tra i cicli. Utile per debugging e verifica prima del deploy.

USO:
    python test_quote_tracker.py [--test-flashscore] [--test-telegram] [--test-csv]

ESEMPI:
    python test_quote_tracker.py --test-flashscore  # Testa connessione Flashscore
    python test_quote_tracker.py --test-telegram    # Testa invio Telegram
    python test_quote_tracker.py --test-csv         # Testa lettura CSV
    python test_quote_tracker.py                    # Esegui ciclo completo UNA VOLTA
================================================================================
"""

import sys
import os
import argparse
from dotenv import load_dotenv
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CSV_FILE = 'matches_to_track.csv'

# ============================================================
# TEST FUNCTIONS
# ============================================================

def test_flashscore():
    """Test connessione Flashscore"""
    print("\n" + "="*80)
    print("🧪 TEST FLASHSCORE CONNECTION")
    print("="*80)

    test_match_id = "1234567"  # Esempio Juventus-AC Milan

    try:
        url = f"https://www.flashscore.com/match/{test_match_id}/"
        print(f"\n📡 Tentando connessione a: {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response Size: {len(response.content)} bytes")

        if response.status_code == 200:
            print("✅ Connessione Flashscore OK!")
        elif response.status_code == 404:
            print("⚠️ Match non trovato (ma connessione OK)")
        else:
            print(f"⚠️ Errore HTTP {response.status_code}")

    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Flashscore non risponde")
    except Exception as e:
        print(f"❌ ERRORE: {str(e)}")

def test_telegram():
    """Test invio Telegram"""
    print("\n" + "="*80)
    print("🧪 TEST TELEGRAM")
    print("="*80)

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_TOKEN o TELEGRAM_CHAT_ID non configurati!")
        print("   Edita .env e aggiungi:")
        print("   TELEGRAM_TOKEN=xxx")
        print("   TELEGRAM_CHAT_ID=yyy")
        return

    print(f"\n📱 Token: {TELEGRAM_TOKEN[:20]}...")
    print(f"📱 Chat ID: {TELEGRAM_CHAT_ID}")

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        message = (
            "🧪 <b>TEST QUOTE TRACKER</b>\n\n"
            "Questo è un messaggio di test.\n"
            "Se hai ricevuto questo, il bot Telegram funziona! ✅"
        )

        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }

        print(f"\n📤 Inviando messaggio test...")
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            print("✅ Messaggio inviato con successo!")
            print("   Controlla Telegram se hai ricevuto il messaggio.")
        else:
            print(f"❌ Errore Telegram: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ ERRORE: {str(e)}")

def test_csv():
    """Test lettura CSV"""
    print("\n" + "="*80)
    print("🧪 TEST CSV")
    print("="*80)

    if not os.path.exists(CSV_FILE):
        print(f"⚠️ {CSV_FILE} non trovato - creando template...")
        try:
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
            print(f"✅ Template creato: {CSV_FILE}")
        except Exception as e:
            print(f"❌ Errore creazione template: {str(e)}")
            return

    try:
        df = pd.read_csv(CSV_FILE)
        print(f"\n✅ CSV caricato con successo!")
        print(f"   Partite da monitorare: {len(df)}")
        print("\n   Contenuto:")
        print(df.to_string(index=False))

    except Exception as e:
        print(f"❌ Errore caricamento CSV: {str(e)}")

def test_full_cycle():
    """Esegui ciclo completo UNA VOLTA"""
    print("\n" + "="*80)
    print("🧪 TEST FULL CYCLE (esecuzione singola)")
    print("="*80)

    # Importa le funzioni da quote_tracker
    try:
        # Se quote_tracker.py è nella stessa cartella
        import importlib.util
        spec = importlib.util.spec_from_file_location("quote_tracker", "quote_tracker.py")
        qt = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(qt)

        print("\n✅ quote_tracker.py caricato")
        print("   Eseguendo ciclo principale UNA VOLTA...\n")

        qt.main()

        print("\n✅ Ciclo completato!")

    except Exception as e:
        print(f"❌ Errore: {str(e)}")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quote Tracker Testing Utility")
    parser.add_argument("--test-flashscore", action="store_true", help="Test Flashscore connection")
    parser.add_argument("--test-telegram", action="store_true", help="Test Telegram notification")
    parser.add_argument("--test-csv", action="store_true", help="Test CSV loading")
    parser.add_argument("--full-cycle", action="store_true", help="Run one complete cycle")

    args = parser.parse_args()

    # Se nessun argomento, esegui full cycle per default
    if not any([args.test_flashscore, args.test_telegram, args.test_csv, args.full_cycle]):
        args.full_cycle = True

    if args.test_flashscore:
        test_flashscore()

    if args.test_telegram:
        test_telegram()

    if args.test_csv:
        test_csv()

    if args.full_cycle:
        test_full_cycle()

    print("\n" + "="*80)
    print("✅ Test completati")
    print("="*80)
