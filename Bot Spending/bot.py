import sqlite3
from datetime import datetime
import discord
from discord.ext import commands

# ====== MASUKKAN TOKEN BOT DISCORD DI SINI ======
TOKEN = "token_muuuuu"

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Buat / koneksi database SQLite
conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

# Buat tabel jika belum ada
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL, -- 'income' atau 'expense'
    amount REAL NOT NULL,
    description TEXT,
    date TEXT NOT NULL
)
""")
conn.commit()

# Command tambah pemasukan
@bot.command(name="income")
async def add_income(ctx, amount: float, *, description: str = ""):
    try:
        cursor.execute(
            "INSERT INTO transactions (user_id, type, amount, description, date) VALUES (?, ?, ?, ?, ?)",
            (ctx.author.id, "income", amount, description, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        await ctx.send(f"✅ Income wich is **{amount}Rp** successfully added for {ctx.author.display_name}.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

# Command tambah pengeluaran
@bot.command(name="expense")
async def add_expense(ctx, amount: float, *, description: str = ""):
    try:
        cursor.execute(
            "INSERT INTO transactions (user_id, type, amount, description, date) VALUES (?, ?, ?, ?, ?)",
            (ctx.author.id, "expense", amount, description, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        await ctx.send(f"💸 Expense wich is **{amount}Rp** successfully added for {ctx.author.display_name}.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

# Command ringkasan
@bot.command(name="summary")
async def summary(ctx):
    try:
        cursor.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id = ? GROUP BY type", (ctx.author.id,))
        data = cursor.fetchall()

        income = 0
        expense = 0
        for row in data:
            if row[0] == "income":
                income = row[1] or 0
            elif row[0] == "expense":
                expense = row[1] or 0

        balance = income - expense
        await ctx.send(
            f" **Financial Summary for {ctx.author.display_name}**\n"
            f" Total Income: {income}Rp\n"
            f" Total Expenses: {expense}Rp\n"
            f" Balance: {balance}Rp"
        )
    except Exception as e:
        await ctx.send(f" An error occurred: {e}")
    if balance > 10_000_000:
        kaya_message = "\n💎 Aku kayaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa 💎"
        await ctx.send(kaya_message)
# command reset (user sendiri)
@bot.command(name="reset")
async def reset_user_data(ctx):
    try:
        # Hapus semua transaksi milik user yang menjalankan command
        cursor.execute("DELETE FROM transactions WHERE user_id = ?", (ctx.author.id,))
        conn.commit()
        await ctx.send(f" All your transactions have been deleted, {ctx.author.display_name}.")
    except Exception as e:
        await ctx.send(f" An error occurred: {e}")

# reset semua data (admin only)
@bot.command(name="resetall")
@commands.has_permissions(administrator=True)
async def reset_all_data(ctx):
    try:
        # Hapus semua transaksi di database
        cursor.execute("DELETE FROM transactions")
        conn.commit()
        await ctx.send(" All transactions have been deleted for all users!")
    except Exception as e:
        await ctx.send(f" An error occurred: {e}")

# Pesan error kalau bukan admin
@reset_all_data.error
async def reset_all_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(" You don't have permission to execute this command.")

# Event saat bot siap
@bot.event
async def on_ready():
    print(f" Bot {bot.user} sudah online!")

# Jalankan bot
bot.run(TOKEN)
