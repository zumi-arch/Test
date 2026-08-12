import sqlite3
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import TOKEN


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

bot.remove_command("help")

H_MIN = 1

conn = sqlite3.connect("tugas.db")
c = conn.cursor()

c.execute(
    """
    CREATE TABLE IF NOT EXISTS tugas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        judul TEXT NOT NULL,
        deadline TEXT NOT NULL
    )
    """
)

c.execute(
    """
    CREATE TABLE IF NOT EXISTS status_tugas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        tugas_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (tugas_id) REFERENCES tugas(id)
    )
    """
)

conn.commit()


async def tugas_autocomplete(
    interaction: discord.Interaction,
    current: str,
):
    c.execute(
        """
        SELECT id, judul, deadline
        FROM tugas
        ORDER BY deadline ASC
        """
    )

    rows = c.fetchall()
    choices = []

    for tugas_id, judul, deadline in rows:
        text = f"{tugas_id} - {judul} ({deadline})"

        if current.lower() in text.lower():
            choices.append(
                app_commands.Choice(
                    name=text[:100],
                    value=tugas_id,
                )
            )

    return choices[:25]


@bot.hybrid_command(
    name="help",
    description="Tampilkan panduan penggunaan bot.",
)
async def help_command(ctx):
    embed = discord.Embed(
        title="📚 Panduan Bot Tugas",
        description=(
            "Ketik `/` untuk melihat semua command yang tersedia.\n\n"
            "Semua command juga masih dapat digunakan dengan prefix `!`."
        ),
        color=discord.Color.blue(),
    )

    embed.add_field(
        name="➕ /tambah",
        value="Tambahkan tugas baru.",
        inline=False,
    )

    embed.add_field(
        name="📋 /lihat",
        value="Lihat semua tugas aktif.",
        inline=False,
    )

    embed.add_field(
        name="✅ /selesai",
        value="Tandai tugas sebagai selesai.",
        inline=False,
    )

    embed.add_field(
        name="🏆 /leaderboard",
        value="Lihat 5 penyelesai tugas terbanyak.",
        inline=False,
    )

    embed.add_field(
        name="⏰ /set_reminder",
        value="Atur pengingat sebelum deadline.",
        inline=False,
    )

    embed.add_field(
        name="🏓 /ping",
        value="Cek latensi bot.",
        inline=False,
    )

    embed.set_footer(
        text="Tip: ketik / untuk melihat command dan parameter yang tersedia."
    )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="ping",
    description="Cek apakah bot aktif dan lihat latensinya.",
)
async def ping(ctx):
    embed = discord.Embed(
        description=f"Pong! Latensi: {round(bot.latency * 1000)}ms",
        color=discord.Color.blue(),
    )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="tambah",
    description="Tambahkan tugas baru.",
)
@app_commands.describe(
    judul="Nama atau judul tugas",
    deadline="Tanggal deadline, contoh: 2026-08-20",
)
async def tambah(
    ctx,
    judul: str,
    deadline: str,
):
    try:
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d")

        if deadline_date.date() < datetime.now().date():
            embed = discord.Embed(
                title="Deadline Tidak Valid",
                description="Deadline tidak boleh berada di masa lalu.",
                color=discord.Color.red(),
            )

            return await ctx.send(embed=embed)

        c.execute(
            """
            INSERT INTO tugas (judul, deadline)
            VALUES (?, ?)
            """,
            (
                judul,
                deadline,
            ),
        )

        conn.commit()

        tugas_id = c.lastrowid

        embed = discord.Embed(
            title="Tugas Ditambahkan",
            description=(
                f"Tugas **{judul}** berhasil disimpan.\n"
                f"ID: **{tugas_id}**\n"
                f"Deadline: **{deadline}**"
            ),
            color=discord.Color.green(),
        )

        await ctx.send(embed=embed)

    except ValueError:
        embed = discord.Embed(
            title="Format Salah",
            description=(
                "Format tanggal salah.\n"
                "Gunakan format **YYYY-MM-DD**.\n\n"
                "Contoh:\n"
                "`/tambah judul:Matematika deadline:2026-08-20`"
            ),
            color=discord.Color.red(),
        )

        await ctx.send(embed=embed)


@bot.hybrid_command(
    name="lihat",
    description="Lihat semua tugas yang masih aktif.",
)
async def lihat(ctx):
    today = datetime.now().strftime("%Y-%m-%d")

    c.execute(
        """
        SELECT id, judul, deadline
        FROM tugas
        WHERE deadline >= ?
        ORDER BY deadline ASC
        """,
        (today,),
    )

    rows = c.fetchall()

    if not rows:
        embed = discord.Embed(
            description="Tidak ada tugas aktif.",
            color=discord.Color.orange(),
        )

        return await ctx.send(embed=embed)

    embed = discord.Embed(
        title="📋 Daftar Tugas",
        color=discord.Color.green(),
    )

    for tugas_id, judul, deadline in rows:
        try:
            deadline_date = datetime.strptime(
                deadline,
                "%Y-%m-%d",
            ).date()

            remaining_days = (
                deadline_date - datetime.now().date()
            ).days

            if remaining_days == 0:
                status_deadline = "Hari ini"
            elif remaining_days == 1:
                status_deadline = "Besok"
            else:
                status_deadline = f"{remaining_days} hari lagi"

        except ValueError:
            status_deadline = "-"

        embed.add_field(
            name=f"{tugas_id}. {judul}",
            value=(
                f"Deadline: **{deadline}**\n"
                f"{status_deadline}"
            ),
            inline=False,
        )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="selesai",
    description="Tandai tugas sebagai selesai.",
)
@app_commands.describe(
    id_tugas="Pilih tugas yang sudah selesai",
)
@app_commands.autocomplete(
    id_tugas=tugas_autocomplete,
)
async def selesai(
    ctx,
    id_tugas: int,
):
    c.execute(
        """
        SELECT id, judul, deadline
        FROM tugas
        WHERE id = ?
        """,
        (id_tugas,),
    )

    tugas = c.fetchone()

    if not tugas:
        embed = discord.Embed(
            title="Tugas Tidak Ditemukan",
            description=f"Tugas ID **{id_tugas}** tidak ditemukan.",
            color=discord.Color.red(),
        )

        return await ctx.send(embed=embed)

    c.execute(
        """
        SELECT id
        FROM status_tugas
        WHERE user_id = ?
        AND tugas_id = ?
        AND status = 'selesai'
        """,
        (
            str(ctx.author.id),
            id_tugas,
        ),
    )

    existing = c.fetchone()

    if existing:
        embed = discord.Embed(
            title="Sudah Selesai",
            description=(
                f"Kamu sudah menandai tugas "
                f"**{tugas[1]}** sebagai selesai."
            ),
            color=discord.Color.orange(),
        )

        return await ctx.send(embed=embed)

    c.execute(
        """
        INSERT INTO status_tugas (
            user_id,
            tugas_id,
            status
        )
        VALUES (?, ?, ?)
        """,
        (
            str(ctx.author.id),
            id_tugas,
            "selesai",
        ),
    )

    conn.commit()

    embed = discord.Embed(
        title="Tugas Selesai ✅",
        description=(
            f"**{ctx.author.display_name}** telah menyelesaikan\n"
            f"**{tugas[1]}**"
        ),
        color=discord.Color.green(),
    )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="leaderboard",
    description="Lihat 5 penyelesai tugas terbanyak.",
)
async def leaderboard(ctx):
    c.execute(
        """
        SELECT user_id, COUNT(DISTINCT tugas_id) AS total
        FROM status_tugas
        WHERE status = 'selesai'
        GROUP BY user_id
        ORDER BY total DESC
        LIMIT 5
        """
    )

    rows = c.fetchall()

    if not rows:
        embed = discord.Embed(
            description="Belum ada yang menyelesaikan tugas.",
            color=discord.Color.orange(),
        )

        return await ctx.send(embed=embed)

    embed = discord.Embed(
        title="🏆 Leaderboard Penyelesai Tugas",
        color=discord.Color.gold(),
    )

    medals = [
        "🥇",
        "🥈",
        "🥉",
        "4️⃣",
        "5️⃣",
    ]

    for i, (user_id, total) in enumerate(rows):
        try:
            member = ctx.guild.get_member(int(user_id))

            if member:
                name = member.display_name
            else:
                user = await bot.fetch_user(int(user_id))
                name = user.name

        except Exception:
            name = f"User {user_id}"

        embed.add_field(
            name=f"{medals[i]} {name}",
            value=f"**{total}** tugas selesai",
            inline=False,
        )

    await ctx.send(embed=embed)


@bot.hybrid_command(
    name="set_reminder",
    description="Atur berapa hari sebelum deadline reminder dikirim.",
)
@app_commands.describe(
    hari="Jumlah hari sebelum deadline",
)
async def set_reminder(
    ctx,
    hari: int,
):
    global H_MIN

    if hari < 0:
        embed = discord.Embed(
            description="Jumlah hari pengingat tidak boleh negatif.",
            color=discord.Color.red(),
        )

        return await ctx.send(embed=embed)

    if hari > 365:
        embed = discord.Embed(
            description="Jumlah hari pengingat maksimal 365 hari.",
            color=discord.Color.red(),
        )

        return await ctx.send(embed=embed)

    H_MIN = hari

    if H_MIN == 0:
        reminder_text = "pada hari deadline"
    else:
        reminder_text = f"H-{H_MIN} sebelum deadline"

    embed = discord.Embed(
        title="Pengingat Diatur",
        description=(
            f"Pengingat tugas berhasil diatur menjadi "
            f"**{reminder_text}**."
        ),
        color=discord.Color.blue(),
    )

    await ctx.send(embed=embed)


@tasks.loop(hours=1)
async def reminder():
    now = datetime.now()

    if now.hour != 8:
        return

    target_date = (
        now + timedelta(days=H_MIN)
    ).strftime("%Y-%m-%d")

    c.execute(
        """
        SELECT id, judul
        FROM tugas
        WHERE deadline = ?
        """,
        (target_date,),
    )

    tugas_target = c.fetchall()

    if not tugas_target:
        return

    for guild in bot.guilds:
        channel = discord.utils.get(
            guild.text_channels,
            name="pengumuman",
        )

        if not channel:
            continue

        for tugas_id, judul in tugas_target:
            if H_MIN == 0:
                title = "⚠️ Deadline Hari Ini"
            else:
                title = f"⏰ Reminder H-{H_MIN}"

            embed = discord.Embed(
                title=title,
                description=(
                    f"Tugas **{judul}**\n"
                    f"ID: **{tugas_id}**\n"
                    f"Deadline: **{target_date}**"
                ),
                color=discord.Color.gold(),
            )

            await channel.send(embed=embed)


@reminder.before_loop
async def before_reminder():
    await bot.wait_until_ready()


@tasks.loop(hours=24)
async def arsip_otomatis():
    today = datetime.now().strftime("%Y-%m-%d")

    c.execute(
        """
        DELETE FROM tugas
        WHERE deadline < ?
        """,
        (today,),
    )

    conn.commit()


@arsip_otomatis.before_loop
async def before_arsip():
    await bot.wait_until_ready()


@bot.event
async def setup_hook():
    await bot.tree.sync()


@bot.event
async def on_ready():
    if not reminder.is_running():
        reminder.start()

    if not arsip_otomatis.is_running():
        arsip_otomatis.start()

    print(f"Bot aktif sebagai {bot.user}")


bot.run(TOKEN)