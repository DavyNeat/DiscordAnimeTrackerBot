import discord
import os
import Scrape
import json
import asyncio
from dotenv import load_dotenv
from discord.ext import commands, tasks

bot = commands.Bot(command_prefix='*', help_command=None)

@bot.event
async def on_ready():
    print(F"We have logged in as {bot.user}")
    with open('shows.json', 'r+') as f:
        data = json.load(f)
        shows = Scrape.scrape()

        for show in shows:
            data[show] = shows[show]
        
        if "Animes" not in data:
            data["Animes"] = []

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

@bot.command()
async def add(ctx, arg):
    with open('shows.json', 'r+') as f:
        data = json.load(f)
        if arg in Scrape.getCurrentSeason() and arg not in data["Animes"]:
            data['Animes'].append(arg)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            await ctx.send(f"<@&930870897768792114> {arg} added to list")
        elif arg in data["Animes"]:
            await ctx.send(f"{arg} already in list")
        else:
            await ctx.send(f"<@&930870897768792114> {arg} is not a current anime")

@bot.command()
async def remove(ctx, arg):
    with open('shows.json', 'r+') as f:
        data = json.load(f)
        if arg in data['Animes']:
            data['Animes'].remove(arg)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            await ctx.send(f"{arg} removed from list")
        else:
            await ctx.send(f"{arg} is not in list")

@bot.command()
async def trackanime(ctx, enabled = "enable"):
    if enabled.lower() == 'disable':
        check_anime.cancel()
        await ctx.send("Tracking anime disabled, You will no longer receive updates in this channel")
    elif enabled.lower() == 'enable':
        check_anime.start(ctx)
        await ctx.send("Tracking anime enabled, You will now receive updates in this channel")

@bot.command()
async def list(ctx):
    with open('shows.json', 'r+') as f:
        data = json.load(f)
        if data["Animes"] == []:
            await ctx.send("No animes are being tracked")
        else: await ctx.send(f"{data['Animes']}")

@bot.command()
async def help(ctx):
    help = """Help:\n
    *add <anime> - Adds an anime to the list\n
    *remove <anime> - Removes an anime from the list\n
    *list - Lists all animes being tracked\n
    *trackanime <enable/disable> - Enables/Disables the tracking of animes in the current channel\n
    *season - Lists all animes in the current season\n
    *help - Displays this message\n
    """
    await ctx.send(F'>>> {help}')

@bot.command()
async def season(ctx):
    season = Scrape.getCurrentSeason()
    animes = [*season,]
    pages = len(season) // 10

    if len(season) % 10 != 0:
        pages += 1

    contents = []

    for i in range(pages):
        page = ""
        for j in range(10):
            if i*10 + j >= len(season):
                break
            page += (F"{animes[i*10 + j]}\n")
        contents.append(page)
    cur_page = 1
    message = await ctx.send(F"Page {cur_page}/{pages}:\n>>> {contents[cur_page-1]}")
    # getting the message object for editing and reacting

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        # This makes sure nobody except the command sender can interact with the "menu"

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
            # waiting for a reaction to be added - times out after x seconds, 60 in this
            # example

            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page

        except asyncio.TimeoutError:
            await message.delete()
            break
            # ending the loop if user doesn't react after x seconds

@tasks.loop(minutes=5)
async def check_anime(ctx):
    with open('shows.json', 'r+') as f:
        data = json.load(f)
        shows = data['Animes']
        currUpdated = Scrape.scrape()
        for show in shows:
            if show in currUpdated and (show not in data or data[show] < currUpdated[show]):
                await ctx.send(f"<@&930870897768792114> {show} has been updated (Episode {currUpdated[show]})")
                data[show] = currUpdated[show]
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
                

load_dotenv(os.path.join(os.getcwd(), '.env'))
SECRET_KEY = os.getenv("TOKEN")
bot.run(SECRET_KEY)