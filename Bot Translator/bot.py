import discord
from discord.ext import commands
from config import token
from logic import *

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class PersistentView(discord.ui.View):
    def __init__(self, owner):
        super().__init__(timeout=None)
        self.owner = owner

    @discord.ui.button(label="Terima Balasan", style=discord.ButtonStyle.primary, custom_id="text_ans")
    async def text_ans_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        obj = TextAnalysis.memory[self.owner][-1]
        await interaction.response.send_message(obj.response, ephemeral=True)

    @discord.ui.button(label="Terjemahkan Pesan", style=discord.ButtonStyle.secondary, custom_id="text_translate")
    async def text_translate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        obj = TextAnalysis.memory[self.owner][-1]
        await interaction.response.send_message(obj.translation, ephemeral=True)

@bot.event
async def on_ready():
    print(f'Berhasil log in sebagai {bot.user}')

@bot.command(name="start")
async def start(ctx, *, text: str):
    TextAnalysis(text, ctx.author.name)
    view = PersistentView(ctx.author.name)
    await ctx.send("Pesanmu diterima! Apa yang kamu ingin aku lakukan?", view=view)

bot.run(token)