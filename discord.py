import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration
APPLICATION_CHANNEL_ID = 1358891911053578332  # Replace with your channel ID
APP1_EMOJI = '✅'  # First application emoji
APP2_EMOJI = '📝'  # Second application emoji

# Questions for each application type
APP1_QUESTIONS = [
    "What is your name?",
    "How old are you?",
    "Why do you want to join as a member?"
]
APP2_QUESTIONS = [
    "What is your name?",
    "What skills do you bring?",
    "Why do you want to join as a staff?"
]

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_application(ctx):
    """Sets up the application embed message with two options"""
    embed = discord.Embed(
        title="Application System",
        description="React with:\n✅ for Member Application\n📝 for Staff Application\nYou will receive a DM with questions to answer.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Please keep your DMs open!")
    
    message = await ctx.send(embed=embed)
    await message.add_reaction(APP1_EMOJI)
    await message.add_reaction(APP2_EMOJI)

async def ask_questions(user, question_set, app_type):
    """Handles the DM application process for a specific application type"""
    responses = {}
    
    try:
        dm_channel = await user.create_dm()
        
        # Send initial message
        await dm_channel.send(f"Hello! Let's start your {app_type} application. I'll ask you a few questions. Please respond to each one.")
        
        # Ask each question and wait for response
        for question in question_set:
            embed = discord.Embed(
                title=f"{app_type} Application Question",
                description=question,
                color=discord.Color.green()
            )
            await dm_channel.send(embed=embed)
            
            # Wait for user's response
            def check(m):
                return m.author == user and m.channel == dm_channel
            
            try:
                response = await bot.wait_for('message', check=check, timeout=300.0)  # 5 minute timeout
                responses[question] = response.content
            except asyncio.TimeoutError:
                await dm_channel.send("You took too long to respond. Application cancelled.")
                return
        
        # Send confirmation
        await dm_channel.send(f"Thank you for your {app_type} application! We'll review it soon.")
        
        # Send responses to a staff channel (optional)
        staff_channel = bot.get_channel(123456789012345678)  # Replace with staff channel ID
        if staff_channel:
            embed = discord.Embed(
                title=f"New {app_type} Application from {user.name}",
                color=discord.Color.purple()
            )
            for question, answer in responses.items():
                embed.add_field(name=question, value=answer, inline=False)
            embed.set_footer(text=f"User ID: {user.id}")
            await staff_channel.send(embed=embed)
            
    except discord.Forbidden:
        # If DMs are closed, try to notify user in the original channel
        channel = bot.get_channel(APPLICATION_CHANNEL_ID)
        if channel:
            await channel.send(f"{user.mention}, please enable DMs from server members to complete your {app_type} application!")

@bot.event
async def on_reaction_add(reaction, user):
    """Handles reaction events for both application types"""
    if user.bot:
        return
        
    if reaction.message.channel.id == APPLICATION_CHANNEL_ID:
        emoji = str(reaction.emoji)
        
        # Remove reaction to keep it clean (optional)
        await reaction.remove(user)
        
        # Check if user already has an ongoing application
        if user in bot.active_applications:
            return
                
        bot.active_applications.add(user)
        
        if emoji == APP1_EMOJI:
            await ask_questions(user, APP1_QUESTIONS, "Member")
        elif emoji == APP2_EMOJI:
            await ask_questions(user, APP2_QUESTIONS, "Staff")
            
        bot.active_applications.remove(user)

# Add this to track active applications
bot.active_applications = set()

# Error handling for the setup command
@setup_application.error
async def setup_application_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need administrator permissions to use this command!")
    else:
        await ctx.send(f"An error occurred: {error}")

# Run the bot
bot.run('MTM1ODg5NDExNDc0OTI4NDQxMw.GmkDT9.aodJO-xXq2q0PMuJMNlonQ1l-OKDaw_pTYrBuA')  # Replace with your bot token




