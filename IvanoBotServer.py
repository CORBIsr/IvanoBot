import discord
from discord.ext import tasks, commands
from datetime import datetime, timezone
import sys
import threading
from flask import Flask
import os

# --- CONFIGURAZIONE FLASK ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Online!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- CONFIG BOT ---
TOKEN = os.getenv('DISCORD_TOKEN')
ID_CANALE = 1493274617001808043

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
                canale = await self.fetch_channel(ID_CANALE)
                await canale.send("⏰ 🎖️ Test EVENTO MILITARI @everyone 🎖️ ⏰")
                await canale.send("⏰ 🚢 Test EVENTO PORTO @everyone 🚢 ⏰")
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
    
        print(f"Controllo orario UTC: {ora}:{minuto:02d}")

        if 9 <= ora <= 20 and minuto == 45:
            try:
                canale = await self.fetch_channel(ID_CANALE)
                if ora % 2 != 0:
                    await canale.send("⏰ 🎖️ Tra 15 minuti c'è l'EVENTO AI MILITARI @everyone 🎖️ ⏰")
                else:
                    await canale.send("⏰ 🚢 Tra 15 minuti c'è l'EVENTO AL PORTO @everyone 🚢 ⏰")
                print(f"Messaggio inviato alle {ora}:{minuto} UTC")
            except Exception as e:
                print(f"Errore critico durante l'invio: {e}")

# --- AVVIO ---
if __name__ == "__main__":
    if "test" not in sys.argv:
        keep_alive()
        
    intents = discord.Intents.default()
    client = MyBot(intents=intents)
    client.run(TOKEN)
