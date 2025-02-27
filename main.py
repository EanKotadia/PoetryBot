import discord
import random
import asyncio
import os
from discord.ext import commands
from flask import Flask
from threading import Thread
import random
import asyncio
import os
from discord.ext import commands
from flask import Flask
from threading import Thread

# Bot Setup with Intents
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Themes for duels
THEMES = ["Love and Loss", "Nature's Fury", "A Journey", "War and Peace", "The Unknown", "Midnight Thoughts"]

# Store ongoing duels
ongoing_duels = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def duel(ctx, opponent: discord.Member):
    """Starts a poetry duel between two users"""
    if ctx.author == opponent:
        await ctx.send("You cannot duel yourself.")
        return

    if ctx.author.id in ongoing_duels or opponent.id in ongoing_duels:
        await ctx.send("One of you is already in a duel.")
        return

    theme = random.choice(THEMES)
    await ctx.send(f"{ctx.author.mention} has challenged {opponent.mention} to a poetry duel! \n**Theme:** {theme} \nBoth participants have **5 minutes** to submit their poems using `!submit <poem>`.")

    ongoing_duels[ctx.author.id] = {"opponent": opponent.id, "theme": theme, "poems": {}}
    ongoing_duels[opponent.id] = {"opponent": ctx.author.id, "theme": theme, "poems": {}}

    await asyncio.sleep(300)  # Wait for 5 minutes

    if len(ongoing_duels[ctx.author.id]["poems"]) < 2:
        await ctx.send("Duel time is up, but both poems were not submitted. Duel canceled.")
        del ongoing_duels[ctx.author.id]
        del ongoing_duels[opponent.id]
        return

    await ctx.send("Voting begins! React with 🏆 to vote for the best poem!")

    await asyncio.sleep(3600)

    duel_data = ongoing_duels[ctx.author.id]
    messages = duel_data["poems"]

    winner = None
    max_votes = 0

    for user_id, msg in messages.items():
        message = await ctx.channel.fetch_message(msg)
        votes = sum(react.count for react in message.reactions if react.emoji == "🏆") - 1  # Subtract bot's reaction

        if votes > max_votes:
            max_votes = votes
            winner = bot.get_user(user_id)

    if winner:
        await ctx.send(f"The winner is {winner.mention} with {max_votes} votes!")

        # Assign the "Duel Champion" role to the winner
        role = discord.utils.get(ctx.guild.roles, name="Duel Champion")
        if role:
            await winner.add_roles(role)
        else:
            await ctx.send("The 'Duel Champion' role was not found. Please create it.")

    else:
        await ctx.send("No winner was determined.")

    # Clear duel data
    del ongoing_duels[ctx.author.id]
    del ongoing_duels[opponent.id]

@bot.command()
async def submit(ctx, *, poem: str):
    """Allows users to submit their poems during a duel"""
    if ctx.author.id not in ongoing_duels:
        await ctx.send("You are not currently in a duel.")
        return

    duel_data = ongoing_duels[ctx.author.id]

    # Check if the user has already submitted a poem
    if ctx.author.id in duel_data["poems"]:
        await ctx.send(f"{ctx.author.mention}, you have already submitted your poem!")
        return

    duel_data["poems"][ctx.author.id] = ctx.message.id
    await ctx.message.add_reaction("🏆")
    await ctx.send(f"Poem submitted by {ctx.author.mention}!")

app = Flask(__name__)

@app.route("/")
def home():
    return "I'm alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run).start()


bot.run(os.environ['DISCORD_BOT_TOKEN'])
