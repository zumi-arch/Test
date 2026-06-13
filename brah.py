import discord
from discord.ext import commands
import requests
import io

# Initialize the bot with a command prefix
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content for commands
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

@bot.command(name="generate")
async def generate_image(ctx, *, prompt: str):
    """Generates an image based on a user prompt and sends it to Discord."""
    # Let the user know the bot is working
    await ctx.send(f"🎨 Generating image for: `{prompt}`... Please wait.")

    url = f"https://gen.pollinations.ai/image/{prompt}"
    headers = {
        "Authorization": "Bearer sk_IsLYirY1kjGgqBWxOwsjHm28mtRVlJ1w"
    }

    try:
        # Fetch the image from the API
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Save the image into bytes memory instead of writing to local disk
            image_data = io.BytesIO(response.content)
            
            # Send the image file directly to the Discord channel
            await ctx.send(file=discord.File(fp=image_data, filename='generated_image.jpg'))
        else:
            await ctx.send("❌ Failed to generate image. The API returned an error.")
            
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

# Run the bot with your Discord Token
# Replace 'YOUR_DISCORD_BOT_TOKEN' with your actual bot token from the Discord Developer Portal
bot.run('YOUR_DISCORD_BOT_TOKEN')