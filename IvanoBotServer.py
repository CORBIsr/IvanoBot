import discord
from discord.ext import tasks, commands
from discord.ui import Button, View
from datetime import datetime, timezone, time, timedelta
import sys
import threading
import json
from flask import Flask

# --- CONFIGURAZIONE FLASK (Keep-Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Online!"

def run_flask():
    # Render usa la porta 8080 o 10000 di solito, ma 0.0.0.0 è universale per il cloud
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True # Il thread si chiude se il programma principale si ferma
    t.start()

# --- CONFIG BOT ---
TOKEN = os.getenv('DISCORD_TOKEN')
ID_CANALE_EVENTI = 1493274617001808043
ID_CANALE_SONDAGGI = 1493894792420261949

with open("lotte.json", "r") as file:
    dati_caricati = json.load(file)
    #print(type(dati_caricati))
class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modalita_test = "test" in sys.argv
        

    async def setup_hook(self):
        if not self.modalita_test:
            self.controllo_orario.start()

    async def on_ready(self):
        print(f"Bot loggato come {self.user}")
        if self.modalita_test:
            print("--- MODALITÀ TEST ATTIVATA ---")
            try:
                canale = await self.fetch_channel(ID_CANALE_EVENTI)
                #await canale.send("⏰ 🎖️ Test EVENTO MILITARI @everyone 🎖️ ⏰")
                #await canale.send("⏰ 🚢 Test EVENTO PORTO @everyone 🚢 ⏰")

                canale = await self.fetch_channel(ID_CANALE_SONDAGGI)

                for lotta in dati_caricati:
                    sondaggio = discord.Poll(
                        question=f"Partecipazione lotta {lotta.get('nome', 'Sconosciuta')} {lotta.get('orario', 'Orario sconosciuto')}",
                        duration=timedelta(hours=24) # Quanto dura il sondaggio
                    )
                    sondaggio.add_answer(text="Si", emoji="✅")
                    sondaggio.add_answer(text="No", emoji="❌")
                    await canale.send(poll=sondaggio)

                #print(dati_caricati)
                print("Test completato. Chiudo il bot...")
            except Exception as e:
                print(f"Errore nel test: {e}")
            await self.close() 
        else:
            print("--- MODALITÀ NORMALE (TIMER ATTIVO) ---")

    @tasks.loop(seconds=60)
    async def controllo_orario(self):
        now = datetime.now(timezone.utc)
        ora = now.hour
        minuto = now.minute
        
        # Log per vedere l'orario UTC nel pannello di Render
        print(f"Controllo orario UTC: {ora}:{minuto:02d}")

        if 10 <= ora <= 21 and minuto == 45:
            try:
                canale = await self.fetch_channel(ID_CANALE)
                if ora % 2 == 0:
                    await canale.send("⏰ 🎖️ Tra 15 minuti c'è l'EVENTO AI MILITARI @everyone 🎖️ ⏰")
                else:
                    await canale.send("⏰ 🚢 Tra 15 minuti c'è l'EVENTO AL PORTO @everyone 🚢 ⏰")
                print(f"Messaggio inviato alle {ora}:{minuto} UTC")
            except Exception as e:
                print(f"Errore critico durante l'invio: {e}")

    orario_sondaggio = time(hour=9, minute=0, tzinfo=timezone.utc)
    @tasks.loop(time=orario_sondaggio)
    async def controllo_sondaggio(self):
        try:
            canale = await self.fetch_channel(ID_CANALE_SONDAGGI)
            for lotta in dati_caricati:

                sondaggio = discord.Poll(
                    question=f"Partecipazione lotta {lotta.get('nome', 'Sconosciuta')} {lotta.get('orario', 'Orario sconosciuto')}",
                    duration=timedelta(hours=24) # Quanto dura il sondaggio
                )

                sondaggio.add_answer(text="Si", emoji="✅")
                sondaggio.add_answer(text="No", emoji="❌")

                await canale.send(poll=sondaggio)
                print("Sondaggio nativo inviato!")
            
        except Exception as e:
            print(f"Errore: {e}")
# --- AVVIO ---
if __name__ == "__main__":
    # Avviamo Flask solo se NON siamo in modalità test
    if "test" not in sys.argv:
        keep_alive()
        
    intents = discord.Intents.default()
    client = MyBot(intents=intents)
    client.run(TOKEN)
