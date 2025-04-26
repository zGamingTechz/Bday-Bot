import discord
from discord.ext import commands
import TOKEN
import csv
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="%", intents=intents)

months = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.group()
async def bday(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Use `%bday add` to add your birthday.')

@bday.command()
async def add(ctx):
    await ctx.send('Please enter your birthday (e.g., `6 November`):')

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        parts = msg.content.lower().replace(",", "").split()
        if len(parts) != 2:
            await ctx.send('Invalid format. Please use `6 November` or `6 Nov`.')
            return

        day, month = parts
        if not day.isdigit():
            await ctx.send('Invalid day. Please enter a number for the day.')
            return

        month_full = None
        for m in months:
            if m.startswith(month):
                month_full = m
                break

        if not month_full:
            await ctx.send('Invalid month name.')
            return

        if not os.path.exists('bdays.csv'):
            with open('bdays.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['UserID', 'Birthday'])

        with open('bdays.csv', 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if str(ctx.author.id) == row[0]:
                    await ctx.send('You have already added your birthday!')
                    return

        with open('bdays.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([ctx.author.id, f'{int(day)} {month_full.capitalize()}'])
        await ctx.send(f'Birthday added: {int(day)} {month_full.capitalize()}')

    except asyncio.TimeoutError:
        await ctx.send('You took too long to respond.')


@bday.command()
async def show(ctx):
    if not os.path.exists('bdays.csv'):
        await ctx.send('No birthdays saved yet.')
        return

    with open('bdays.csv', 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if str(ctx.author.id) == row[0]:
                await ctx.send(f'Your birthday is: {row[1]}')
                return

    await ctx.send('You have not added your birthday yet. Use `%bday add`.')


@bday.command()
async def edit(ctx):
    if not os.path.exists('bdays.csv'):
        await ctx.send('No birthdays saved yet.')
        return

    with open('bdays.csv', 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if str(ctx.author.id) == row[0]:
                break
        else:
            await ctx.send('You have not added your birthday yet. Use `%bday add` first.')
            return

    await ctx.send('Please enter your new birthday (e.g., `6 November`):')

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        parts = msg.content.lower().replace(",", "").split()
        if len(parts) != 2:
            await ctx.send('Invalid format. Please use `6 November` or `6 Nov`.')
            return

        day, month = parts
        if not day.isdigit():
            await ctx.send('Invalid day. Please enter a number for the day.')
            return

        month_full = None
        for m in months:
            if m.startswith(month):
                month_full = m
                break

        if not month_full:
            await ctx.send('Invalid month name.')
            return

        rows = []
        with open('bdays.csv', 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if str(ctx.author.id) == row[0]:
                    row[1] = f'{int(day)} {month_full.capitalize()}'
                rows.append(row)

        with open('bdays.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

        await ctx.send(f'Your birthday has been updated to: {int(day)} {month_full.capitalize()}')

    except asyncio.TimeoutError:
        await ctx.send('You took too long to respond.')


bot.run(TOKEN.token)
