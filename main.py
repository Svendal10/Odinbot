import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


#interaction avec la base de données
class VikingBot(commands.Bot):
    # Initialisation du bot avec les intents nécessaires
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True 
        intents.members = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
    
    # Chargement des cogs au démarrage
    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await self.tree.sync()
        print("✅ Tout est prêt !")

    # Événement lorsque le bot est prêt
    async def on_ready(self):
        print(f"🛡️ Connecté en tant que {self.user}")

# Démarrage du bot
if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERREUR : Token introuvable dans .env")
    else:
        bot = VikingBot()
        bot.run(TOKEN)