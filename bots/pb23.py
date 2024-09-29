import discord
from discord.ext import commands
import sqlite3
import datetime  # Import datetime for timestamps
import time
# Setting up the bot
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

cooldown_end = None
# Initialize SQLite database
conn = sqlite3.connect('bot.db')
c = conn.cursor()

# Create the blacklist and whitelist tables if they don't exist
c.execute('''
CREATE TABLE IF NOT EXISTS blacklist (
    user_id INTEGER PRIMARY KEY
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS whitelist (
    user_id INTEGER PRIMARY KEY
)
''')
conn.commit()

# Load stock from stock.txt
def load_stock():
    try:
        with open('stock1.txt', 'r') as f:
            stock = int(f.read().strip())
            return stock
    except (FileNotFoundError, ValueError):
        return 0

# Save stock to stock.txt
def save_stock(stock):
    with open('stock1.txt', 'w') as f:
        f.write(str(stock))

# Load money from money.txt
def load_money():
    try:
        with open('money1.txt', 'r') as f:
            money = float(f.read().strip())  # Now treats the balance as float for dollars and cents
            return money
    except (FileNotFoundError, ValueError):
        return 0.00

# Save money to money.txt
def save_money(money):
    with open('money1.txt', 'w') as f:
        f.write(f"{money:.2f}")  # Ensure that the balance is saved with two decimal places

# Logging function with an embedded message
async def log_djoin(ctx, server_id, server_name):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    embed = discord.Embed(
        title="Member Transfer Log",
        color=discord.Color.blue(),  # You can choose a color of your choice
        timestamp=datetime.datetime.now()
    )
    
    embed.add_field(name="Timestamp", value=timestamp, inline=False)
    embed.add_field(name="User", value=f"<@{ctx.author.id}>", inline=True)
    embed.add_field(name="Server ID", value=f"`{server_id}`", inline=True)
    embed.add_field(name="Server Name", value=f"{server_name}", inline=True)
    embed.add_field(name="members sent", value=f"2", inline=True)
    embed.set_footer(text="Logs generated by the bot")
    
    # Get the channel to log in
    log_channel = bot.get_channel(1289636698602340404)  # Replace with your log channel ID
    
    if log_channel:
        await log_channel.send(embed=embed)  # Send log embed to the specified channel

@bot.command()
@commands.has_permissions(administrator=True)
async def addstock(ctx, num: int):
    """makes in order for more stock using the API for the panel we use ."""
    if num < 0:
        await ctx.send("❌ You cannot add a negative number.")
        return

    current_stock = load_stock()
    current_money = load_money()

    # Calculate the total cost: 1 cent for every 5 stock units added
    cost = (num // 5) * 0.01
    new_money = current_money - cost

    # Check if there's enough money to add the stock
    if new_money < 0:
        await ctx.send(f"❌ Not enough money to add {num} stock. Current balance: ${current_money:.2f}.")
        return

    # Add stock and subtract money
    new_stock = current_stock + num
    save_stock(new_stock)
    save_money(new_money)

    await ctx.send(f"✅ Added {num} to stock. New stock count: {new_stock}. Current balance: ${new_money:.2f} (Deducted ${cost:.2f}).")

@bot.command()
@commands.has_permissions(administrator=True)
async def bal(ctx):
    """this isn't fake money  this  is how much money we have on the panel to waste on stock."""
    current_money = load_money()
    await ctx.send(f"💰 The current balance is: ${current_money:.2f}.")

# Initialize global cooldown variable
cooldown_end = None

@bot.command()
async def djoin(ctx, server_id: int):
    global cooldown_end
    current_time = time.time()

    # Check if the user is blacklisted
    c.execute('SELECT * FROM blacklist WHERE user_id = ?', (ctx.author.id,))
    if c.fetchone() is not None:
        await ctx.send("❌ You're blacklisted! Stop using me.")
        return

    # Check if the command is being used in the correct channel
    if ctx.channel.id != 1289636698434834483:
        await ctx.send("❌ This command can only be used in the designated channel.")
        return

    # Check if there is an active cooldown
    if cooldown_end is not None and current_time < cooldown_end:
        remaining_time = int(cooldown_end - current_time)
        minutes, seconds = divmod(remaining_time, 60)
        await ctx.send(f"Yo broski, someone else used the command! Please wait {minutes} minute(s) and {seconds} second(s) before using it again. This helps prevent the stock from going down too fast. We are working on fixing this soon!")
        return

    # Load current stock
    current_stock = load_stock()

    # Ensure there is stock available
    if current_stock <= 0:
        await ctx.send("❌ No stock available! Please wait for stock to be added.")
        return

    # Get the server with the provided ID
    guild = discord.utils.get(bot.guilds, id=server_id)

    if guild is None:
        await ctx.send("❌ I'm not in that server. 📩 Invite me and try again later!")
    else:
        # Decrease stock by 10 and save the new stock value
        new_stock = current_stock - 10
        save_stock(new_stock)

        # Create an embed message showing the number of members in the server
        embed = discord.Embed(
            title=f"🚀 Sending 2 members to `{guild.name}` 🌌",
            description=f"🌐 Server ID: `{server_id}`\n📦 Stock remaining: {new_stock}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="🔗 Powered by .gg/night")
        await ctx.send(embed=embed)

        # Set cooldown to 3 minutes and 59 seconds
        cooldown_end = current_time + 239  # 239 seconds = 3 minutes 59 seconds


@bot.command()
@commands.has_permissions(administrator=True)
async def blacklist(ctx, user: discord.User):
    """Adds a user to the blacklist."""
    c.execute('INSERT OR IGNORE INTO blacklist (user_id) VALUES (?)', (user.id,))
    conn.commit()
    await ctx.send(f"✅ {user.name} has been blacklisted.")

@bot.command()
@commands.has_permissions(administrator=True)
async def whitelist(ctx, user: discord.User):
    """Removes a user from the blacklist."""
    c.execute('DELETE FROM blacklist WHERE user_id = ?', (user.id,))
    conn.commit()
    await ctx.send(f"✅ {user.name} has been whitelisted.")


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_server(ctx):
    """Deletes all channels and creates a new server setup with permissions."""
    guild = ctx.guild
    
    # Delete all existing channels
    for channel in guild.channels:
        await channel.delete()
    
    # Get the everyone role
    everyone_role = guild.default_role
    
    # Create Categories with Channels and Custom Permissions
    categories_and_channels = [
        {
            "name": "🌾・Farm",
            "channels": [
                {"name": "🤖・add-bot-member", "permissions": {"view": True, "send": False}},
                {"name": "🌱・farm-plans", "permissions": {"view": True, "send": False}},
                {"name": "🔒・private-bot", "permissions": {"view": True, "send": False}}
            ]
        },
        {
            "name": "🌍・Community",
            "channels": [
                {"name": "💬・general", "permissions": {"view": True, "send": True}},
                {"name": "👋・introductions", "permissions": {"view": True, "send": True}},
                {"name": "🎉・off-topic", "permissions": {"view": True, "send": True}}
            ]
        },
        {
            "name": "📌・Pinned",
            "channels": [
                {"name": "📢・updates", "permissions": {"view": True, "send": False}},
                {"name": "📄・announcements", "permissions": {"view": True, "send": False}},
                {"name": "💰・price-changes", "permissions": {"view": True, "send": False}}
            ]
        },
        {
            "name": "🛠・Staff",
            "channels": [
                {"name": "📋・staff-chat", "permissions": {"view": False, "send": False}},
                {"name": "🔧・staff-announcements", "permissions": {"view": False, "send": False}},
                {"name": "🔒・private-staff", "permissions": {"view": False, "send": False}}
            ]
        }
    ]

    # Step 1: Create Categories and Channels with Custom Permissions
    for category_info in categories_and_channels:
        category_name = category_info["name"]
        
        # Create the category
        category = await guild.create_category(category_name)

        # Create the channels under the newly created category with custom permissions
        for channel_info in category_info["channels"]:
            channel_name = channel_info["name"]
            perms = channel_info["permissions"]

            overwrites = {
                everyone_role: discord.PermissionOverwrite(
                    view_channel=perms.get("view", True),
                    send_messages=perms.get("send", True)
                )
            }
            
            await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
    
    # Step 2: Set Specific Permissions for Staff Channels (hidden to non-staff members)
    staff_role = discord.utils.get(guild.roles, name="Staff")
    if not staff_role:
        staff_role = await guild.create_role(name="Staff", permissions=discord.Permissions(administrator=True))
    
    for category in guild.categories:
        if "Staff" in category.name:
            for channel in category.channels:
                # Only staff can view and send messages
                await channel.set_permissions(everyone_role, view_channel=False)
                await channel.set_permissions(staff_role, view_channel=True, send_messages=True)

    # Step 3: Send confirmation message with an embed
    embed = discord.Embed(
        title="✅ Server Setup Complete",
        description="Your server has been restructured with custom permissions:\n\n"
                    "**🌾 Farm**\n"
                    "- Channels are viewable, but users cannot type.\n\n"
                    "**🌍 Community**\n"
                    "- Open channels where everyone can interact.\n\n"
                    "**📌 Pinned**\n"
                    "- Channels where users can see important updates but cannot type.\n\n"
                    "**🛠 Staff**\n"
                    "- Hidden from non-staff members.\n",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Your server is now safe and organized! ✨")

    await ctx.send(embed=embed)

@bot.command()
async def stock(ctx):
    current_stock = load_stock()
    await ctx.send(f"📦 Current stock is: {current_stock}")

@bot.command()
async def add(ctx):
    embed = discord.Embed(
        title="🔗 **Invite**",
        description="**🌟 URL** [🌐 ADD](https://discord.com/oauth2/authorize?client_id=1240064584023277638&permissions=8&integration_type=0&scope=bot) THEN ADD [🌐 2nd bot ADD](https://discord.com/oauth2/authorize?client_id=1289637830066180096&permissions=0&integration_type=0&scope=bot) you need both Bots for our member bot to work!!!!!",
        color=discord.Color.blue()
    )
    embed.set_footer(text="💫 Powered by 🌕 .gg/night")
    await ctx.send(embed=embed)
bot.run('MTI4OTYzNzgzMDA2NjE4MDA5Ng.GeYTb-.6_8V5oY0LOYXad2SoHkWDlhaDfOgkDDfZOl5ZI')
