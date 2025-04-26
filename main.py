import discord
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime, timedelta
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


@tasks.loop(minutes=60)
async def birthday_checker():
    if not os.path.exists('bdays.csv'):
        return

    guild = discord.utils.get(bot.guilds)
    if guild is None:
        return

    now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    current_day = now.day
    current_month = now.strftime('%B').lower()

    with open('bdays.csv', 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = int(row['UserID'])
            birthday = row['Birthday']
            gender = row.get('Gender', '3')

            bday_day, bday_month = birthday.split()
            if int(bday_day) == current_day and bday_month.lower() == current_month:
                member = guild.get_member(user_id)
                if member:
                    role_name = "Bday Person"
                    if gender == '1':
                        role_name = "Bday Boy"
                    elif gender == '2':
                        role_name = "Bday Girl"

                    role = discord.utils.get(guild.roles, name=role_name)
                    if role and role not in member.roles:
                        await member.add_roles(role)
                        print(f'Gave {role.name} role to {member.name}')
            else:
                member = guild.get_member(user_id)
                if member:
                    roles_to_remove = [
                        discord.utils.get(guild.roles, name="Bday Boy"),
                        discord.utils.get(guild.roles, name="Bday Girl"),
                        discord.utils.get(guild.roles, name="Bday Person")
                    ]
                    for role in roles_to_remove:
                        if role and role in member.roles:
                            await member.remove_roles(role)
                            print(f'Removed {role.name} from {member.name}')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    guild = discord.utils.get(bot.guilds)

    role_names = ['Bday Boy', 'Bday Girl', 'Bday Person']
    pink = discord.Colour.from_rgb(255, 105, 180)

    for role_name in role_names:
        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            await guild.create_role(name=role_name, colour=pink)
            print(f'Created role: {role_name}')

    birthday_checker.start()


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


@bday.command()
async def gender(ctx):
    await ctx.send('Please select your gender:\n1. Boy\n2. Girl\n3. Dont wanna disclose\n(You can reply with the number or the text)')

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', timeout=30.0, check=check)
        gender_input = msg.content.strip().lower()

        gender_map = {
            '1': 'Boy',
            '2': 'Girl',
            '3': 'Dont wanna disclose',
            'boy': 'Boy',
            'girl': 'Girl',
            'dont wanna disclose': 'Dont wanna disclose'
        }

        if gender_input not in gender_map:
            await ctx.send('Invalid option. Please choose 1, 2, 3, or type Boy, Girl, Dont wanna disclose.')
            return

        selected_gender = gender_map[gender_input]

        if not os.path.exists('bdays.csv'):
            await ctx.send('No birthdays saved yet.')
            return

        rows = []
        found = False

        with open('bdays.csv', 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader)
            if 'Gender' not in header:
                header.append('Gender')
            for row in reader:
                if str(ctx.author.id) == row[0]:
                    if len(row) < len(header):
                        row.append(selected_gender)
                    else:
                        row[header.index('Gender')] = selected_gender
                    found = True
                rows.append(row)

        if not found:
            await ctx.send('You need to add your birthday first using `%bday add`.')
            return

        with open('bdays.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

        await ctx.send(f'Your gender has been updated to: {selected_gender}')

    except asyncio.TimeoutError:
        await ctx.send('You took too long to respond.')


bot.run(TOKEN.token)
