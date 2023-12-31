import base64
import discord
import json
import logging
from lxml import html
from random import randint
from difflib import get_close_matches

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)


# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_presence_update(before, after):
    if before.id in [215316565468512256]:
        print(before.name + 'changed status to '+after.status+'. It works!')


@client.event
async def on_message(message):
    # role request
    if message.channel.id in [330243328731774977, 1087165689313378324, 920459479567458304]:
        valid_roles = ['mystic', 'valor', 'instinct', 'san rafael', 'ross valley', 'non marin',
                       'novato', 'south novato', 'southern marin', 'marinwood-tl', 'central marin', 'ex raids',
                       'lvl50', 'lvl49', 'lvl48', 'lvl47', 'lvl46', 'lvl45', 'lvl44', 'lvl43', 'lvl42', 'lvl41',
                       'lvl40', 'lvl39', 'lvl38', 'lvl37', 'lvl36', 'lvl35', 'lvl34', 'lvl33', 'lvl32', 'lvl31',
                       'lvl30', 'lvl29', 'lvl28', 'lvl27', 'lvl26', 'lvl25', 'lvl24', 'lvl23', 'lvl22',
                       'ttar', 'ditto', 'machamp', 'kecleon', 'chansey', 'axew', 'deino', 'unown', 'lapras',
                       'ditto', 'legendary', 'com', 'mega']
        if message.content.startswith('!r '):
            split_message = message.content[3:].split(', ')
            requested_roles = []
            if len(split_message):
                for r in split_message:
                    r = r.lower()
                    if is_number(r):
                        r = 'lvl' + r
                        if r in valid_roles:
                            role = discord.utils.get(message.guild.roles, name=r)
                            requested_roles.append(role)
                    elif r in valid_roles:
                        if r.lower() == 'marinwood-tl':
                            r = 'Marinwood-TL'
                        elif r.lower() == 'ex raids':
                            r = 'EX Raids'
                        elif r == 'ttar':
                            r = r.upper()
                        else:
                            r = r.title()
                        role = discord.utils.get(message.guild.roles, name=r)
                        requested_roles.append(role)
                    elif 'level' in r.lower():
                        r = 'lvl' + r.strip('level ')
                        if r in valid_roles:
                            role = discord.utils.get(message.guild.roles, name=r)
                            requested_roles.append(role)
                    elif 'lvl ' in r.lower():
                        r = 'lvl' + r.strip('lvl ')
                        if r in valid_roles:
                            role = discord.utils.get(message.guild.roles, name=r)
                            requested_roles.append(role)
                if len(requested_roles):
                    try:
                        member = message.author
                        await member.add_roles(*requested_roles, reason='Self-add', atomic=True)
                        if len(requested_roles) == 1:
                            await message.channel.send('Successfully added 1 role.')
                        else:
                            await message.channel.send('Successfully added {} roles. '.format(
                                str(len(requested_roles))))
                    except discord.Forbidden:
                        await message.channel.send('I don\'t have permission.')
        if message.content.startswith('!remove '):
            if len(message.content.split()) > 1:
                role_name = message.content[8:].lower()
                for r in valid_roles:
                    if r in role_name:
                        if r.startswith('lvl'):
                            role = discord.utils.get(message.guild.roles, name=r)
                        else:
                            role = discord.utils.get(message.guild.roles, name=r.title())
                for r in role_name.split():
                    if is_number(r):
                        role = discord.utils.get(message.guild.roles, name='lvl' + r)
                try:
                    await message.author.remove_roles(role, reason='Self-remove', atomic=True)
                    await message.channel.send('Successfully removed 1 role.')
                except discord.Forbidden:
                    await message.channel.send('I don\'t have permission.')
            else:
                await message.channel.send('Sorry, I don\'t understand.')


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def fix_indent(rating):
    """Fixes the spacing between the moveset rating and the moves

    Returns three spaces if the rating is one character, two if it is two characters (A-, B-, etc)
    """

    if len(rating) == 1:
        return ' ' * 3
    else:
        return ' ' * 2


f = open('the_file.txt', 'rb')
thing = f.readline()
other_thing = base64.b64decode(thing, altchars=None, validate=False).decode()
f.close()
client.run(other_thing)
