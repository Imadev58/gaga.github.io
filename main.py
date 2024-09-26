import discord
from discord.ext import commands, tasks
import asyncio
import random
import string
import requests

client = commands.Bot(command_prefix=".", self_bot=True)

# Task that changes the status
@tasks.loop(seconds=10)  # Change every 10 seconds (adjust as needed)
async def rotate_status():
    for status in status_list:
        await client.change_presence(activity=discord.Game(name=status))
        await asyncio.sleep(10)  # Adjust to match the loop interval

# Dictionary to store dynamically created commands
dynamic_commands = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    if not rotate_status.is_running():
        rotate_status.start()

@client.command()
async def ping(ctx):
    latency = round(client.latency * 1000)  
    await ctx.send(f'🏓 Pong! {ctx.author.mention}, latency is {latency}ms')

@client.command()
async def hack(ctx, member: discord.Member = None):
    """Simulates a hacking process"""
    
    message = await ctx.send('🔍 Hacking...')
    
    await asyncio.sleep(2)
    await message.edit(content='💾 Loading...')
    
    await asyncio.sleep(2)
    
    def generate_random_string(length):
        return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))
    
    fake_password = generate_random_string(12)
    
    def generate_fake_discord_token():
        part1 = ''.join(random.choices(string.ascii_letters + string.digits, k=24))
        part2 = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        part3 = ''.join(random.choices(string.ascii_letters + string.digits, k=27))
        return f"{part1}.{part2}.{part3}"
    
    fake_token = generate_fake_discord_token()
    
    email = f"{member.display_name.lower()}@{random.choice(['gmail.com', 'icloud.com', 'hotmail.com', 'outlook.com'])}" if member else "unknown_user@example.com"
    
    final_message = (
        f'📧 Email: {email}\n'
        f'🔑 Password: {fake_password}\n'
        f'🔑  Token: {fake_token}\n'
        '💻 Hacking complete!\n\n'
    )
    
    await message.edit(content=final_message)

@client.command()
async def kick(ctx, user_id: int):
    """Kicks a user by their ID."""
    if not ctx.guild:
        await ctx.send("This command can only be used in a server.")
        return
    
    try:
        user = await ctx.guild.fetch_member(user_id)
        await user.kick(reason="Kicked by bot command")
        await ctx.send(f'Kicked {user.name} ({user.id})')
    except discord.NotFound:
        await ctx.send('User not found.')
    except discord.Forbidden:
        await ctx.send('I do not have permission to kick this user.')
    except discord.HTTPException as e:
        await ctx.send(f'An error occurred: {e}')

@client.command()
async def ban(ctx, user_id: int):
    """Bans a user by their ID."""
    if not ctx.guild:
        await ctx.send("This command can only be used in a server.")
        return
    
    try:
        user = await ctx.guild.fetch_member(user_id)
        await user.ban(reason="Banned by bot command")
        await ctx.send(f'Banned {user.name} ({user.id})')
    except discord.NotFound:
        await ctx.send('User not found.')
    except discord.Forbidden:
        await ctx.send('I do not have permission to ban this user.')
    except discord.HTTPException as e:
        await ctx.send(f'An error occurred: {e}')

@client.command()
@commands.has_permissions(manage_channels=True)
async def nuke(ctx):
    """Deletes the channel and recreates it with the same name and settings."""
    channel = ctx.channel
    category = channel.category
    channel_name = channel.name
    channel_topic = channel.topic
    slowmode_delay = channel.slowmode_delay
    overwrites = channel.overwrites

    try:
        new_channel = await category.create_text_channel(
            name=channel_name,
            topic=channel_topic,
            slowmode_delay=slowmode_delay,
            overwrites=overwrites
        )
        await channel.delete()
        await new_channel.send(f"The channel has been nuked and recreated!")
    except discord.Forbidden:
        await ctx.send('I do not have permission to manage channels.')
    except discord.HTTPException as e:
        await ctx.send(f'An error occurred: {e}')

@client.command()
async def proof(ctx):
    """Sends images as proof."""
    image_urls = [
        'https://media.discordapp.net/attachments/1245432691529093240/1266503776060047412/Screenshot_2024-07-26_5.13.30_PM.png',
        'https://media.discordapp.net/attachments/1245432691529093240/1266503881282682960/Screenshot_2024-07-26_5.14.05_PM.png',
        'https://media.discordapp.net/attachments/1255619440976859238/1266505540247359670/image.png'
    ]
    await ctx.send('Proof of Diego caught in 4K :')
    for url in image_urls:
        await ctx.send(url)

@client.command()
async def normal(ctx):
    await ctx.send(f'<@1020638595993833603> is normal.')


@client.command()
async def setstatus(ctx, *, status: str):
    """Sets userr's status."""
    await client.change_presence(activity=discord.Game(name=status))
    await ctx.send(f'Status set to: {status}')

@client.command()
async def setrotate(ctx, *, statuses: str):
    """Sets rotating statuses. First 2 are required, up to 5 more optional."""
    global status_list
    # Split the input by commas and strip any extra spaces
    status_list = [status.strip() for status in statuses.split(',')]
    
    if len(status_list) < 2:
        await ctx.send("Please provide at least two statuses separated by commas.")
        return
    if len(status_list) > 7:
        await ctx.send("You can only provide up to 7 statuses (2 required, 5 optional).")
        return

    await ctx.send(f"Rotating through {len(status_list)} statuses.")
    
    # Start rotating through the statuses
    if not rotate_status.is_running():
        rotate_status.start()

@client.command()
async def create(ctx, cmd_name: str, *, reply: str):
    """Creates a limited-time command.
    
    Usage: .create <cmd_name>, <reply>
    """
    global dynamic_commands

    # Check if the command already exists
    if cmd_name in dynamic_commands:
        await ctx.send(f"A command with the name `{cmd_name}` already exists!")
        return

    # Save the command in the dictionary
    dynamic_commands[cmd_name] = reply
    await ctx.send(f"Command `{cmd_name}` created successfully!")

@client.command()
async def use(ctx, cmd_name: str):
    """Uses a previously created limited-time command."""
    if cmd_name in dynamic_commands:
        reply = dynamic_commands[cmd_name]
        await ctx.send(reply)
    else:
        await ctx.send(f"Command `{cmd_name}` not found.")


@client.command()
async def delete(ctx, cmd_name: str):
    """Deletes a dynamically created command."""
    global dynamic_commands

    # Check if the command exists
    if cmd_name in dynamic_commands:
        del dynamic_commands[cmd_name]
        await ctx.send(f"Command `{cmd_name}` has been deleted.")
    else:
        await ctx.send(f"No command found with the name `{cmd_name}`.")

@client.command()
async def listcmds(ctx):
    """Lists all dynamically created commands."""
    if dynamic_commands:
        cmds = ', '.join(dynamic_commands.keys())
        await ctx.send(f"Dynamically created commands: {cmds}")
    else:
        await ctx.send("No dynamically created commands found.")

@client.command()
async def ip(ctx, ip_address: str):
    """Fetches IP address information."""
    
    # Replace 'YOUR_API_KEY' with your actual API key
    api_key = '0316bba7f5ff5e'  # Your API key
    url = f'http://ipinfo.io/{ip_address}/json?token={api_key}'
    
    try:
        response = requests.get(url)
        data = response.json()

        if "bogon" in data:
            await ctx.send("The IP address provided is not valid.")
            return

        # Extracting relevant details
        ip = data.get('ip', 'N/A')
        city = data.get('city', 'N/A')
        region = data.get('region', 'N/A')
        country = data.get('country', 'N/A')
        org = data.get('org', 'N/A')
        loc = data.get('loc', 'N/A')
        timezone = data.get('timezone', 'N/A')

        # Construct the message
        message = (
            f"**IP Information for {ip}**\n"
            f"🌍 Location: {city}, {region}, {country}\n"
            f"🏢 ISP: {org}\n"
            f"📍 Coordinates: {loc}\n"
            f"🕒 Timezone: {timezone}"
        )
        await ctx.send(message)

    except Exception as e:
        await ctx.send(f"Error fetching IP information: {str(e)}")

client.run('MTI2OTAwNzAwODM3MjIyODExMA.GsKa6S.BUXgHEDwrlke1D_jzjCUJTWvJ_iMKA-dk3wcB0')
