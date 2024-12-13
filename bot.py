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

ROLE_CHANNELS = [330243328731774977, 1087165689313378324, 920459479567458304, 1298726258255073361]
FORBIDDEN_MEMBER_IDS = [1219205150711877644, 639859535879602188, 552370548391280640, 218021615085158402,
                        453656388778983424]
ADMIN_CHANNEL_IDS = [1298833447334314005]
MEE6_GREETING_GUILD_IDS = [1298724847530283020]
DO_NOT_LET_NIANTIC_IN_SERVERS = [1298724847530283020, 330217404669886465]


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


def get_text_channel_by_name(member, channel_name):
    guild = member.guild
    channel = discord.utils.get(guild.text_channels, name=channel_name)
    return channel
    # get welcome channel id, then post there
    # get role request id as well
    # reference the role request channel in the welcome post


@client.event
async def on_member_join(member):
    if member.guild.id in MEE6_GREETING_GUILD_IDS:
        welcome_channel = get_text_channel_by_name(member, 'welcome')
        role_channel = get_text_channel_by_name(member, 'role-request')
        rules_channel = get_text_channel_by_name(member, 'rules')
        # post a message in welcome channel, direct user to role request
        await welcome_channel.send(
            f"{member.mention}, welcome to **PoGo Marin**! Please take a minute to read our {rules_channel.mention}, then go to {role_channel.mention} to add information about you, specifically your location and team. Type !roles to see what roles are available for you to add. You must assign a team to access the raid channels!")
        if member.id in FORBIDDEN_MEMBER_IDS and member.guild.id in DO_NOT_LET_NIANTIC_IN_SERVERS:
            channel = get_text_channel_by_name(member, 'admins')
            await channel.send('A user that should not receive the local link just joined the server: ' + member.name)


@client.event
async def on_member_remove(member):
    if member.guild.id in MEE6_GREETING_GUILD_IDS:
        welcome_channel = get_text_channel_by_name(member, 'welcome')
        await welcome_channel.send(f"{member.mention} just left the server. Come back soon!")


@client.event
async def on_presence_update(before, after):
    if before.id in [215316565468512256, 414716521504571393]:
        print(str(before.name) + 'changed status to ' + str(after.status) + '.')


@client.event
async def on_message(message):
    # role request
    role_channel = get_text_channel_by_name(message.author, 'role-request')
    if message.content.startswith('!roles'):
        role_message = f"""You can go to {role_channel.mention} to request (using the format, '!r mystic, san rafael, ross valley') any of the following tags and you can use @ before them to call people with those tags: 
Mystic
Valor
Instinct
San Rafael
Novato
Marinwood-TL
Ross Valley (Fairfax, San Anselmo, Ross)
Central Marin (Kentfield, Corte Madera, Larkspur, Greenbrae)
Southern Marin (Mill Valley, Sausalito, Strawberry, Marin City, Tiburon Peninsula)
West Marin (Woodacre through Pt. Reyes and out through Muir Beach)
To remove a role, type '!remove [role]'"""
        await message.channel.send(role_message)
    if message.channel.id in ROLE_CHANNELS:
        valid_roles = ['mystic', 'valor', 'instinct', 'san rafael', 'ross valley', 'non marin',
                       'novato', 'south novato', 'southern marin', 'marinwood-tl', 'central marin', 'ex raids',
                       'lvl50', 'lvl49', 'lvl48', 'lvl47', 'lvl46', 'lvl45', 'lvl44', 'lvl43', 'lvl42', 'lvl41',
                       'lvl40', 'lvl39', 'lvl38', 'lvl37', 'lvl36', 'lvl35', 'lvl34', 'lvl33', 'lvl32', 'lvl31',
                       'lvl30', 'lvl29', 'lvl28', 'lvl27', 'lvl26', 'lvl25', 'lvl24', 'lvl23', 'lvl22',
                       'ttar', 'ditto', 'machamp', 'kecleon', 'chansey', 'axew', 'deino', 'unown', 'lapras',
                       'ditto', 'legendary', 'gigantamax', 'com', 'mega']
        if message.content.startswith('!r ') or message.content.startswith('!remove '):
            first_space_index = message.content.index(' ')
            print('first space index: ' + str(first_space_index))
            split_message = message.content[first_space_index:].strip().split(', ')
            print('split message: ' + str(split_message))
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
                print(str(requested_roles))
                if len(requested_roles):
                    try:
                        member = message.author
                        if message.content.startswith('!r '):
                            await member.add_roles(*requested_roles, reason='Self-add', atomic=True)
                        else:
                            await message.author.remove_roles(*requested_roles, reason='Self-remove', atomic=True)
                        if len(requested_roles) == 1:
                            if message.content.startswith('!r '):
                                await message.channel.send('Successfully added 1 role.')
                            else:
                                await message.channel.send('Successfully removed 1 role.')
                        else:
                            if message.content.startswith('!r '):
                                await message.channel.send('Successfully added {} roles. '.format(
                                    str(len(requested_roles))))
                            else:
                                await message.channel.send('Successfully removed {} roles. '.format(
                                    str(len(requested_roles))))
                    except discord.Forbidden:
                        await message.channel.send('I don\'t have permission.')


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
