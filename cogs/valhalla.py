import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
from database import DatabaseManager

# liste des questions et des réponses 
QUIZ_NORDIC = [
    {"q": "Qui est le père de Thor ?", "r": ["odin"]},
    {"q": "Quel animal est Fenrir ?", "r": ["loup", "un loup"]},
    {"q": "Comment s'appelle le monde des humains ?", "r": ["midgard"]},
    {"q": "Quel objet permet à Thor de lancer la foudre ?", "r": ["mjollnir", "marteau"]},
    {"q": "Qui est le dieu de la malice ?", "r": ["loki"]},
    {"q": "Combien de pattes a Sleipnir ?", "r": ["8", "huit"]},
    {"q": "Quel est le nom de l'arbre-monde ?", "r": ["yggdrasil"]},
    {"q": "Qui garde les pommes de jouvence ?", "r": ["idunn"]},
    {"q": "Où vont les guerriers morts au combat ?", "r": ["valhalla"]},
    {"q": "Quel dieu a perdu une main ?", "r": ["tyr"]}
]

# liste des récompenses
RECOMPENSES = [
    ("Pièce de Cuivre", "Commun"),
    ("Corne à Boire", "Commun"),
    ("Runes", "Peu Commun"),
    ("Bouclier Rond", "Rare"),
    ("Hache de Bataille", "Rare"),
    ("Casque de Jarl", "Épique"),
    ("Amulette de Freya", "Légendaire"),
    ("Fragment de Mjöllnir", "Mythique")
]

# liste des runes
RUNES_LISTE = [
    {"nom": "Fehu (Richesse)", "desc": "L'abondance arrive vers toi. C'est le moment d'investir !", "symbole": "ᚠ"},
    {"nom": "Uruz (Force)", "desc": "Une grande énergie t'habite. Fais face aux obstacles !", "symbole": "ᚢ"},
    {"nom": "Thurisaz (Chaos)", "desc": "Attention, des forces imprévisibles sont à l'œuvre...", "symbole": "ᚦ"},
    {"nom": "Ansuz (Sagesse)", "desc": "Écoute les conseils des anciens. Odin te regarde.", "symbole": "ᚨ"},
    {"nom": "Raidho (Voyage)", "desc": "Un déplacement ou un changement de vie est imminent.", "symbole": "ᚱ"},
    {"nom": "Algiz (Protection)", "desc": "Tu es protégé par les dieux. N'aie pas peur.", "symbole": "ᛉ"}
]
class Valhalla(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()

    # le quizz /quete
    @app_commands.command(name="quete", description="Réponds à une question pour gagner de l'XP !")
    async def quete(self, interaction: discord.Interaction):
        question = random.choice(QUIZ_NORDIC)
        embed = discord.Embed(title="📜 Question", description=question['q'], color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            if msg.content.lower() in question['r']:
                xp = 40
                lvl_up, new_lvl = self.db.add_xp(interaction.user.id, xp)
                txt = f"✅ **Bravo !** +{xp} XP."
                
                if lvl_up:
                    item, rarity = random.choice(RECOMPENSES)
                    self.db.add_item(interaction.user.id, item, rarity)
                    txt += f"\n🎉 **Niveau {new_lvl} atteint !** Tu reçois : {item} ({rarity})."
                
                await interaction.followup.send(txt)
            else:
                await interaction.followup.send(f"❌ **Faux.** C'était : {question['r'][0]}")
        except asyncio.TimeoutError:
            await interaction.followup.send("⏳ Trop lent !")

    # l'inventaire /inventaire
    @app_commands.command(name="inventaire", description="Voir mon profil")
    async def inventaire(self, interaction: discord.Interaction):
        data = self.db.get_player_data(interaction.user.id)
        if not data:
            await interaction.response.send_message("Fais `/quete` d'abord !", ephemeral=True)
            return

        xp, level = data
        items = self.db.get_inventory(interaction.user.id)
        
        embed = discord.Embed(title=f"🎒 Profil de {interaction.user.name}", color=discord.Color.gold())
        embed.add_field(name="Niveau", value=str(level), inline=True)
        embed.add_field(name="XP", value=str(xp), inline=True)
        
        liste = "\n".join([f"- {i[0]} ({i[1]})" for i in items]) if items else "Vide"
        embed.add_field(name="Inventaire", value=liste, inline=False)
        await interaction.response.send_message(embed=embed)

    # Le classement /classement
    @app_commands.command(name="classement", description="Top 5 des joueurs")
    async def classement(self, interaction: discord.Interaction):
        await interaction.response.defer()

        top = self.db.get_top_players(5)
        embed = discord.Embed(title="🏆 Panthéon du Valhalla", color=discord.Color.gold())
        
        if not top:
            embed.description = "Aucun guerrier n'a encore fait ses preuves."
        else:
            description = ""
            for i, (uid, lvl, xp) in enumerate(top, 1):
                try:
                    user = await self.bot.fetch_user(uid)
                    name = user.name
                except:
                    name = f"Viking Disparu ({uid})"
                
                medaille = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "⚔️"
                
                
                description += f"{medaille} **{name}** - Niv. {lvl} ({xp} XP)\n"
            
            embed.description = description

        await interaction.followup.send(embed=embed)

    # l'offrande /offrande
    @app_commands.command(name="offrande", description="Sacrifier un objet pour de l'XP")
    async def offrande(self, interaction: discord.Interaction):
        items = self.db.get_inventory(interaction.user.id)
        if not items:
            await interaction.response.send_message("Tu n'as rien à sacrifier.", ephemeral=True)
            return
            
        objet = items[-1][0] 
        if self.db.remove_item(interaction.user.id, objet):
            self.db.add_xp(interaction.user.id, 30)
            await interaction.response.send_message(f"🔥 Tu as sacrifié **{objet}** (+30 XP).")
        else:
            await interaction.response.send_message("Erreur rituelle.", ephemeral=True)

   # Le duel /duel
    @app_commands.command(name="duel", description="Défie un joueur sur une épreuve de rapidité !")
    async def duel(self, interaction: discord.Interaction, adversaire: discord.Member):
        # Sécurités
        if adversaire.bot:
            await interaction.response.send_message("Tu ne peux pas battre une machine...", ephemeral=True)
            return
        if adversaire.id == interaction.user.id:
            await interaction.response.send_message("Tu ne peux pas te battre contre toi-même !", ephemeral=True)
            return

        
        await interaction.response.send_message(
            f"⚔️ **DUEL !** {interaction.user.mention} VS {adversaire.mention}\n"
            f"Préparez-vous... L'épreuve commence dans **3 secondes** !"
        )
        await asyncio.sleep(1)
        await interaction.edit_original_response(content=f"⚔️ **DUEL !** {interaction.user.mention} VS {adversaire.mention}\nPréparez-vous... **2...**")
        await asyncio.sleep(1)
        await interaction.edit_original_response(content=f"⚔️ **DUEL !** {interaction.user.mention} VS {adversaire.mention}\nPréparez-vous... **1...**")
        await asyncio.sleep(1)

    
        question = random.choice(QUIZ_NORDIC)
        
        
        await interaction.followup.send(
            f"📜 **ÉPREUVE DE SAGESSE :**\n"
            f"# {question['q']}\n"
            f"*(Le premier qui écrit la bonne réponse gagne !)*"
        )

        
        def check(m):
            return (
                m.author in [interaction.user, adversaire] 
                and m.channel == interaction.channel 
                and m.content.lower() in question['r']
            )

        try:
            
            msg = await self.bot.wait_for('message', check=check, timeout=20.0)
        
            gagnant = msg.author
            perdant = adversaire if gagnant == interaction.user else interaction.user
            
            
            xp_gain = 30
            self.db.add_xp(gagnant.id, xp_gain)

            embed = discord.Embed(
                title="🏆 DUEL TERMINÉ !",
                description=f"**{gagnant.name}** a été le plus rapide !\nIl remporte la gloire et **+{xp_gain} XP**.",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)

        except asyncio.TimeoutError:
            
            await interaction.followup.send("⏳ **Temps écoulé !** Vous êtes tous les deux indignes du Valhalla. (Personne ne gagne)")
    
    # Le tirage de runes /runes
    @app_commands.command(name="runes", description="Consulte l'oracle pour connaître ton avenir")
    async def runes(self, interaction: discord.Interaction):
        rune = random.choice(RUNES_LISTE)
        
        embed = discord.Embed(title=f"🔮 Tirage de Rune : {rune['nom']}", color=discord.Color.purple())
        embed.add_field(name="Symbole", value=f"# {rune['symbole']}", inline=False) # Le # rend le texte énorme
        embed.add_field(name="Interprétation", value=rune['desc'], inline=False)
        embed.set_footer(text="Le destin est scellé.")
        
        await interaction.response.send_message(embed=embed)

    # Le pillage /pillage
    @app_commands.command(name="pillage", description="Pars en expédition en misant ton XP (Quitte ou Double)")
    @app_commands.describe(mise="Combien d'XP mises-tu sur cette expédition ?")
    async def pillage(self, interaction: discord.Interaction, mise: int):
        
        if mise <= 0:
            await interaction.response.send_message("On ne part pas en expédition les mains vides !", ephemeral=True)
            return

        data = self.db.get_player_data(interaction.user.id)
        if not data:
            await interaction.response.send_message("Tu es trop faible. Fais `/quete` d'abord.", ephemeral=True)
            return
            
        current_xp = data[0]
        if current_xp < mise:
            await interaction.response.send_message(f"Tu n'as que {current_xp} XP. Tu ne peux pas en miser {mise} !", ephemeral=True)
            return

        
        await interaction.response.send_message(f"🛶 **{interaction.user.name}** embarque sur son drakkar avec **{mise} XP** en jeu...")
        await asyncio.sleep(2) 
        
        
        chance = random.randint(1, 100)
        
        if chance > 60: 
            gain = mise 
            self.db.add_xp(interaction.user.id, gain)
            
            embed = discord.Embed(title="Pillage Réussi ! 💰", color=discord.Color.green())
            embed.description = f"Tu as pillé un monastère anglais !\n**Gain : +{gain} XP**"
            embed.set_thumbnail(url="https://img.icons8.com/color/96/viking-ship.png") 
            
        else: 
            perte = -mise
            self.db.add_xp(interaction.user.id, perte)
            
            embed = discord.Embed(title="Échec de l'expédition... 🩸", color=discord.Color.dark_red())
            embed.description = f"Les villageois étaient armés... Tu fuis en laissant ton butin.\n**Perte : -{mise} XP**"
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Valhalla(bot))

  
    