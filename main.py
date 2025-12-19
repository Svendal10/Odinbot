import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class VikingBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True 
        intents.members = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await self.tree.sync()
        print("✅ Tout est prêt !")

    async def on_ready(self):
        print(f"🛡️ Connecté en tant que {self.user}")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERREUR : Token introuvable dans .env")
    else:
        bot = VikingBot()
        bot.run(TOKEN)