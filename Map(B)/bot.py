from config import *
from logic import *
import discord
from discord.ext import commands
from config import TOKEN

# Menginisiasi pengelola database
manager = DB_Map("database.db")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot started")

@bot.command()
async def start(ctx: commands.Context):
    await ctx.send(f"Halo, {ctx.author.name}. Masukkan !help_me untuk mengeksplorasi daftar perintah yang tersedia")

@bot.command()
async def help_me(ctx: commands.Context):
    # Implementasi perintah yang akan menampilkan daftar perintah yang tersedia
    daftar_perintah = (
        "**Daftar Perintah yang Tersedia:**\n"
        "`!start` - Memulai interaksi dengan bot\n"
        "`!help_me` - Menampilkan daftar perintah ini\n"
        "`!show_city [nama_kota]` - Menampilkan gambar/peta dari kota yang ditentukan\n"
        "`!remember_city [nama_kota]` - Menyimpan kota pilihan Anda ke database\n"
        "`!show_my_cities` - Menampilkan semua peta dari kota yang telah Anda simpan"
    )
    await ctx.send(daftar_perintah)
@bot.command()
async def show_city(ctx: commands.Context, *, city_name: str = ""):
    # Implementasi perintah yang akan menampilkan peta dengan kota yang ditentukan
    if not city_name:
        await ctx.send("Silakan masukkan nama kota! Contoh: `!show_city Japan`")
        return
    import os
    # Menyesuaikan dengan file gambar di sidebar Anda (seperti Japan.png, India.png, dll.)
    filename = f"{city_name.capitalize()}.png"
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            await ctx.send(f"Berikut adalah peta untuk {city_name.capitalize()}:", file=discord.File(f))
    else:
        await ctx.send(f"Maaf, file peta untuk '{city_name}' tidak ditemukan di server.")
        
@bot.command()
async def show_my_cities(ctx: commands.Context):
    cities = manager.select_cities(ctx.author.id) # Mengambil daftar kota yang diingat oleh pengguna
    
    # Implementasi perintah yang akan menampilkan peta dengan kota pengguna
    if not cities:
        await ctx.send("Anda belum menyimpan kota apa pun! Gunakan perintah `!remember_city` terlebih dahulu.")
        return
        
    # Menampilkan teks daftar kota yang tersimpan
    list_kota = ", ".join([str(city) for city in cities])
    await ctx.send(f"Kota-kota yang Anda simpan: **{list_kota}**")
    
    import os
    # Mengirim file 'plot.png' yang ada di sidebar Anda (hasil plot koordinat kota user)
    if os.path.exists("plot.png"):
        with open("plot.png", 'rb') as f:
            await ctx.send("Berikut adalah plot visualisasi peta kota Anda:", file=discord.File(f))

@bot.command()
async def remember_city(ctx: commands.Context, *, city_name: str = ""):
    if not city_name:
        await ctx.send("Silakan masukkan nama kota yang ingin disimpan!")
        return

    if manager.add_city(ctx.author.id, city_name): # Memeriksa apakah kota ada dalam database; jika ya, menambahkannya ke memori p...
        await ctx.send(f'Kota {city_name} telah berhasil disimpan!')
    else:
        # Tambahan implementasi di bawah blok 'else:' jika kota gagal disimpan/tidak ada di database
        await ctx.send(f'Gagal menyimpan! Kota "{city_name}" tidak ditemukan di dalam `database.db` atau sudah pernah Anda simpan.')

if __name__ == "__main__":
    bot.run(TOKEN)