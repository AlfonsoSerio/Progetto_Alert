# 🚂 SETUP QUOTE TRACKER SU RAILWAY

**Costo:** €5/mese (macchina sempre accesa)  
**Aggiornamento quote:** Ogni 30 minuti  
**Notifiche:** Telegram  

---

## 📋 STEP 1: PREPARAZIONE FILES

Assicurati di avere questi file nella stessa cartella:

```
.
├── quote_tracker.py          ✅ Script principale
├── matches_to_track.csv      ✅ Lista partite da monitorare
├── requirements.txt          ✅ Dipendenze Python
├── .env.example              ✅ Template variabili ambiente
└── Procfile                  ✅ File di configurazione Railway (crea tu)
```

### Crea Procfile

Crea un file `Procfile` (senza estensione) nella cartella principale:

```
worker: python -u quote_tracker.py
```

Questo dice a Railway di eseguire `quote_tracker.py` come processo worker.

---

## 🎯 STEP 2: SETUP TELEGRAM (se non già fatto)

Se NON hai un Telegram bot:

### 2.1 Crea il bot (@BotFather)
1. Apri Telegram
2. Cerca **@BotFather** (utente ufficiale Telegram)
3. Scrivi `/start` → `/newbot`
4. Segui le istruzioni:
   - Nome del bot: es. `QuoteTrackerBot`
   - Username: es. `quote_tracker_bot`
5. 🔑 Copia il **TOKEN** ricevuto

### 2.2 Ottieni il CHAT_ID (@userinfobot)
1. Cerca **@userinfobot** su Telegram
2. Scrivi `/start`
3. Riceverai il tuo **Chat ID**

### Salva le credenziali
```
TELEGRAM_TOKEN = [il token da @BotFather]
TELEGRAM_CHAT_ID = [il tuo chat id da @userinfobot]
```

---

## 🚀 STEP 3: DEPLOY SU RAILWAY

### 3.1 Crea Account Railway

1. Vai su [railway.app](https://railway.app)
2. Clicca **Login** → **Create Account** (oppure accedi se già hai account)
3. Usa GitHub/Google o crea account diretto
4. Verifica email

### 3.2 Crea Nuovo Progetto

1. Dashboard Railway → **Create New Project**
2. Scegli **Deploy from GitHub** (oppure **Empty Project** se preferisci upload manuale)

#### Opzione A: Deploy da GitHub (consigliato)

1. Collega il tuo GitHub account
2. Seleziona il repo con i file Quote Tracker
3. Railway clona il repo e fa il deploy automatico
4. **Vantaggi:** Aggiornamenti automatici quando pusti nuovi commit

#### Opzione B: Deploy Manuale

1. Scegli **Empty Project**
2. Aggiungi le variabili di ambiente (vedi STEP 4)
3. Upload i file manualmente via CLI (vedi sotto)

---

## 🔐 STEP 4: CONFIGURA VARIABILI DI AMBIENTE

### Nel Dashboard Railway:

1. Progetto → **Settings** → **Variables**
2. Aggiungi:

| Chiave | Valore |
|--------|--------|
| `TELEGRAM_TOKEN` | Il tuo token da @BotFather |
| `TELEGRAM_CHAT_ID` | Il tuo chat ID da @userinfobot |

**Salva** (Railway applica automaticamente)

---

## ⏰ STEP 5: CONFIGURA ESECUZIONE OGNI 30 MINUTI

Railway non ha scheduler nativo per task ripetitivi. Usiamo 2 approcci:

### Opzione 1: Mantenere il processo attivo + polling interno ⭐ (CONSIGLIATO)

Modifica `quote_tracker.py` per aggiungere un loop infinito:

```python
# Aggiungi questo PRIMA di `if __name__ == "__main__":`

def schedule_loop():
    """Esegue quote_tracker ogni 30 minuti indefinitamente"""
    import time
    from datetime import datetime
    
    while True:
        logging.info(f"\n{'='*80}")
        logging.info(f"⏰ Ciclo avviato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"{'='*80}\n")
        
        main()  # Esegui la funzione principale
        
        logging.info(f"⏳ Prossimo check tra 30 minuti ({datetime.now().strftime('%H:%M:%S')})")
        time.sleep(1800)  # 30 minuti in secondi

if __name__ == "__main__":
    schedule_loop()
```

**Vantaggi:**
- ✅ Gratuito (Railroad non addebita extra per worker persistenti)
- ✅ Affidabile
- ✅ Niente API esterne

**Svantaggio:**
- ⚠️ Se Railway riavvia l'app, il contatore riparte (raro)

### Opzione 2: Cron Job esterno (Alternative)

Se preferisci trigger esterno:

- **GitHub Actions:** Free, ma solo per repo GitHub
- **EasyCron.com:** Gratuitamente fino a 60 cicli/ora
- **AWS Lambda:** ~€1/mese (molto più caro)

**Per questo progetto: OPZIONE 1 è perfetta** ✅

---

## 🛠️ STEP 6: UPLOAD VIA RAILWAY CLI (opzione manuale)

Se scegli deploy manuale, usa il CLI di Railway:

### Installa Railway CLI
```bash
npm install -g @railway/cli
```

### Login e Deploy
```bash
railway login                      # Accedi (apre browser)
railway init                       # Crea nuovo progetto
railway up                         # Upload files
```

Railway rileverà automaticamente `requirements.txt` e `Procfile`.

---

## 📊 STEP 7: MONITORA I LOG

### Nel Dashboard Railway:

1. Progetto → **quote-tracker** → **Logs**
2. Vedrai in tempo reale:
   ```
   🎯 QUOTE TRACKER AVVIATO
   📅 2026-09-20 14:30:45
   🔍 Verificando: Juventus vs AC Milan (2026-09-20) [Match ID: 1234567]
   ⏳ Quote NON aperte per match 1234567
   ⏳ Prossimo check fra 30 minuti
   ```

### Filtra per ricercare:
- ✅ `APERTE` → quote aperte
- ⚠️ `NON aperte` → ancora chiuse
- ❌ `non trovato` → match ID errato

---

## ✏️ STEP 8: AGGIUNGI PARTITE A MONITORARE

### File: `matches_to_track.csv`

**Formato:**
```
match_id,team1,team2,date,status,notified
1234567,Juventus,AC Milan,2026-09-20,checking,FALSE
7654321,Inter,Napoli,2026-09-21,checking,FALSE
```

**Come trovare MATCH_ID su Flashscore:**

1. Vai su [flashscore.com](https://www.flashscore.com)
2. Cerca la partita (es. "Juventus vs AC Milan")
3. Clicca sulla partita
4. L'URL sarà: `https://www.flashscore.com/match/XXXXXXX/`
5. Estrai il numero: quello è il `match_id`

**Esempio:**
- URL: `https://www.flashscore.com/match/1234567/`
- match_id: `1234567` ✅

### Aggiorna il CSV:

#### Se usi GitHub:
1. Modifica `matches_to_track.csv` localmente
2. Commit e push
3. Railway si aggiorna automaticamente

#### Se usi Railway diretto:
1. Dashboard Railway → **Files** → **matches_to_track.csv**
2. Modifica direttamente o ri-upload il file

---

## 🔔 STEP 9: TESTA LA NOTIFICA TELEGRAM

### Test manuale:

1. Modifica una partita con `notified=FALSE`
2. Assicurati che le quote siano aperte su Flashscore (verifica a mano)
3. Attendi il prossimo ciclo di 30 minuti
4. Se le quote sono aperte, riceverai notifica Telegram ✅

### Se non ricevi notifiche:

Controlla i log Railway:
- ✅ `TELEGRAM_TOKEN` e `TELEGRAM_CHAT_ID` configurati?
- ✅ Le quote sono VERAMENTE aperte su Flashscore? (verifica manualmente)
- ✅ Il bot Telegram è stato avviato da @BotFather?

---

## 💰 COSTI

| Servizio | Costo Mensile |
|----------|---------------|
| Railway (server) | €5/mese |
| Flashscore | Gratis |
| Telegram | Gratis |
| **TOTALE** | **€5/mese** |

---

## 📝 NOTE IMPORTANTI

### 1. File `.env`
```
Non commit il file .env su GitHub!
Aggiungi a .gitignore:

echo ".env" >> .gitignore
```

### 2. Cambio Match ID in CSV
Se cambii un `match_id`, resetta `notified=FALSE` così il tracker manderà notifica di nuovo.

### 3. Errori Comuni

#### ❌ "Match ID non trovato"
- Verifica che il numero sia corretto su Flashscore
- La partita potrebbe essere stata rimossa/cancellata

#### ❌ "TELEGRAM_TOKEN o TELEGRAM_CHAT_ID non configurati"
- Vai a Railway → Settings → Variables
- Aggiungi le credenziali Telegram

#### ❌ "Notifica non inviata"
- Verifica il token di Telegram (copiato male?)
- Il bot deve essere stato iniziato prima (@BotFather)

---

## 🔄 AGGIORNAMENTI FUTURI

Se modifichi `quote_tracker.py`:

### Con GitHub:
```bash
git add .
git commit -m "Fix: migliorato parsing quote"
git push origin main
```
Railway si aggiorna automaticamente.

### Con Railway diretto:
1. Ri-upload il file via CLI o dashboard
2. Railway redeploya automaticamente

---

## 🆘 TROUBLESHOOTING

### Railway non avvia il processo?
```
Verifica:
1. Procfile esiste e contiene: worker: python -u quote_tracker.py
2. requirements.txt con tutte le dipendenze
3. Usa Python 3.9+ (di default su Railway ✅)
```

### App va in crash loop?
```
Guarda i log per l'errore:
- Errori import? requirements.txt manca dipendenze?
- CSV manca? matches_to_track.csv creato automaticamente ✅
- Variabili ambiente? TELEGRAM_TOKEN/CHAT_ID assenti?
```

### Notifiche non arrivano ma i log dicono "inviata"?
```
Il bot Telegram deve essere stato avviato PRIMA:
1. Apri Telegram
2. Cerca @tuobot (l'username creato con @BotFather)
3. Clicca /start una volta
4. Ora è attivato ✅
```

---

## 🎉 CONCLUSIONE

Hai deployato il Quote Tracker su Railway! 🚀

**Ricapitolando:**
- ✅ Server acceso 24/7 (€5/mese)
- ✅ Controlla quote ogni 30 minuti (gratis)
- ✅ Notifiche Telegram quando si aprono
- ✅ CSV per aggiungere/rimuovere partite
- ✅ Log in tempo reale nel dashboard Railway

Buon betting! 🎯
