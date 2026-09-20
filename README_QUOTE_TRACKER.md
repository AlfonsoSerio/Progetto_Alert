# 🎯 QUOTE TRACKER v1.0

**Monitora l'apertura delle quote su Flashscore e invia notifiche via Telegram**

---

## ⚡ QUICK START

### 1. Setup locale (test)

```bash
# Installa dipendenze
pip install -r requirements.txt

# Copia il template delle variabili di ambiente
cp .env.example .env

# Edita .env e aggiungi le tue credenziali Telegram
# TELEGRAM_TOKEN=xxx
# TELEGRAM_CHAT_ID=yyy

# Modifica matches_to_track.csv con le partite da monitorare
# (vedi formato sotto)

# Esegui manualmente
python quote_tracker.py
```

### 2. Deploy su Railway (produzione)

Vedi **SETUP_RAILWAY_QUOTE_TRACKER.md** per guida completa.

```bash
# Breve riassunto:
1. Crea account su railway.app
2. Crea nuovo progetto (Deploy from GitHub o manuale)
3. Aggiungi variabili Telegram in Settings → Variables
4. Railway esegue automaticamente ogni 30 minuti
```

---

## 📊 FILE DESCRIPTION

| File | Descrizione |
|------|-------------|
| `quote_tracker.py` | Script principale - monitora quote |
| `matches_to_track.csv` | CSV con partite da monitorare |
| `requirements.txt` | Dipendenze Python |
| `.env.example` | Template variabili ambiente |
| `Procfile` | Configurazione Railway |
| `SETUP_RAILWAY_QUOTE_TRACKER.md` | Guida completa deployment |

---

## 🎲 COME USARE

### Aggiungi partite a monitorare

**File:** `matches_to_track.csv`

**Formato:**
```csv
match_id,team1,team2,date,status,notified
1234567,Juventus,AC Milan,2026-09-20,checking,FALSE
7654321,Inter,Napoli,2026-09-21,checking,FALSE
```

**Come trovare match_id:**
1. Vai su flashscore.com
2. Cerca la partita
3. L'URL sarà: `https://www.flashscore.com/match/XXXXXXX/`
4. Copia il numero XXXXXXX → quello è il match_id

### Valori colonne CSV

| Colonna | Valori | Descrizione |
|---------|--------|-------------|
| `match_id` | numero | ID da Flashscore (vedi sopra) |
| `team1` | testo | Nome squadra 1 |
| `team2` | testo | Nome squadra 2 |
| `date` | YYYY-MM-DD | Data partita (informativa) |
| `status` | `checking`, `notified`, `not_found`, `waiting`, `notification_failed` | Stato attuale |
| `notified` | `TRUE` / `FALSE` | Se notifica già inviata |

---

## 🔔 NOTIFICHE TELEGRAM

### Ricevi notifiche quando?
✅ **Quando le quote SI APRONO** su Flashscore per la partita in lista

### Che dice la notifica?
```
🎯 QUOTE APERTE!

📅 Juventus vs AC Milan
📆 2026-09-20
🔗 Vai su Flashscore

⏱️ Quote aperte alle 14:30:45
```

### Frequenza check
- ⏰ **Ogni 30 minuti** (gratis, limiti Flashscore pubblici)
- 🚀 Su Railway (€5/mese) → sempre acceso
- 💻 Localmente → solo se computer acceso

---

## 📈 COSTI

| Item | Costo |
|------|-------|
| Server Railway | €5/mese |
| Flashscore API | Gratis |
| Telegram Bot | Gratis |
| **TOTALE** | **€5/mese** |

---

## 🛠️ DEVELOPMENT

### Struttura del codice

```python
quote_tracker.py
├── check_flashscore_quotes(match_id)  # Verifica se quote aperte
├── send_telegram_notification(msg)    # Invia notifica Telegram
├── load_matches()                     # Carica CSV
├── save_matches(df)                   # Salva aggiornamenti CSV
└── main()                             # Loop principale
```

### Log file
- **Local:** `quote_tracker.log` (nella cartella di progetto)
- **Railway:** Logs → visualizza in dashboard

### Modifica frequenza check
In `quote_tracker.py`, cambia `time.sleep(1800)` (1800 secondi = 30 minuti)

```python
time.sleep(300)   # ogni 5 minuti
time.sleep(1800)  # ogni 30 minuti (default)
time.sleep(3600)  # ogni 1 ora
```

⚠️ **Attenzione:** Flashscore potrebbe bloccare frequenze troppo alte (<5 minuti)

---

## 🐛 TROUBLESHOOTING

### ❌ "Match not found"
```
Il match_id è errato.
Verifica su flashscore.com che il numero sia corretto.
```

### ❌ "TELEGRAM_TOKEN non configurato"
```
Aggiungi a .env:
TELEGRAM_TOKEN=123456789:ABCDefGHIjklMnoPqrsTUVwxyz1234567
TELEGRAM_CHAT_ID=123456789
```

### ❌ "Notifica non inviata"
```
1. Il bot è stato iniziato? (@BotFather → Bot username → /start)
2. Token copiato male? (controlla in Railway Settings)
3. Chat ID corretto? (@userinfobot per verificare)
```

### ❌ "Quote aperte ma niente notifica"
```
Controlla:
1. notified=FALSE in CSV per quella partita
2. Le quote sono VERAMENTE aperte su Flashscore (verifica manualmente)
3. Telegram token valido
4. Il bot è stato avviato con /start
```

---

## 📝 NOTES

- **CSV sempre aggiornato:** Il file `matches_to_track.csv` viene salvato dopo ogni ciclo con status aggiornato
- **Niente integrazione alert.py:** Quote tracker è standalone (per ora)
- **Integrazione futura:** Potrai unire alert.py + quote_tracker.py in un unico sistema
- **Scraper-safe:** Usa Flashscore pubblico (gratis), niente API pagate

---

## 📚 PROSSIMI STEP

1. ✅ Setup locale e test `python quote_tracker.py`
2. ✅ Aggiungi 2-3 partite a `matches_to_track.csv`
3. ✅ Deploy su Railway (guida: SETUP_RAILWAY_QUOTE_TRACKER.md)
4. ✅ Monitora i log su railway.app/projects/.../logs
5. ⏳ (futuro) Integra con alert.py per alerting completo

---

**Made with ❤️ for value betting**
