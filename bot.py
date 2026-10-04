import base64
import discord
import logging
import re

# ── Configuration ────────────────────────────────────────────────────────────

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

VALID_ROLES = {
    'mystic', 'valor', 'instinct',
    'san rafael', 'novato', 'south novato', 'marinwood-tl',
    'ross valley', 'central marin', 'southern marin', 'non marin',
    'ex raids',
    'ttar', 'ditto', 'machamp', 'kecleon', 'chansey', 'axew',
    'deino', 'unown', 'lapras', 'legendary', 'gigantamax', 'com', 'mega',
    'under level 50',
    *[f'lvl{n}' for n in range(50, 81)],
}

# Uncomment to enable debug logging:
# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_text_channel_by_name(member, channel_name):
    return discord.utils.get(member.guild.text_channels, name=channel_name)


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def normalize_role_name(key):
    """Converts a lowercased role key to the display name used in Discord."""
    if key == 'marinwood-tl':
        return 'Marinwood-TL'
    if key == 'ex raids':
        return 'EX Raids'
    if key == 'ttar':
        return 'TTAR'
    if key == 'under level 50':
        return 'Under level 50'
    if re.match(r'^lvl\d+$', key):
        return key  # Discord role names are exactly 'lvl50', 'lvl71', etc.
    return key.title()


def _extract_level_number(token):
    """Returns the integer level from inputs like '40', 'lvl40', 'lvl 40', 'level40', 'level 40', or None."""
    if is_number(token):
        return int(token)
    for prefix in ('level', 'lvl'):
        if token.startswith(prefix):
            rest = token[len(prefix):].strip()
            if is_number(rest):
                return int(rest)
    return None


def parse_role_key(token):
    """
    Normalises a single user-input token to a key in VALID_ROLES.
    Level inputs below 50 map to 'under level 50'.
    Returns None if the token does not match any known role.
    """
    token = token.strip().lower()

    level = _extract_level_number(token)
    if level is not None:
        if level < 50:
            return 'under level 50'
        candidate = f'lvl{level}'
        return candidate if candidate in VALID_ROLES else None

    return token if token in VALID_ROLES else None


def resolve_roles(content, guild):
    """Parses role tokens from a !r / !remove command and returns matching Role objects."""
    after_command = content[content.index(' '):].strip()
    roles = []
    for token in after_command.split(', '):
        key = parse_role_key(token)
        if key is None:
            continue
        role = discord.utils.get(guild.roles, name=normalize_role_name(key))
        if role:
            roles.append(role)
    print(roles)
    return roles


def fix_indent(rating):
    """Returns alignment spacing for single- vs multi-digit move ratings."""
    return ' ' * 3 if len(rating) == 1 else ' ' * 2


# ── Event handlers ───────────────────────────────────────────────────────────

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name} ({client.user.id})')
    print('------')


@client.event
async def on_member_join(member):
    if member.guild.id not in MEE6_GREETING_GUILD_IDS:
        return
    welcome_channel = get_text_channel_by_name(member, 'welcome')
    role_channel = get_text_channel_by_name(member, 'role-request')
    rules_channel = get_text_channel_by_name(member, 'rules')
    await welcome_channel.send(
        f"{member.mention}, welcome to **PoGo Marin**! "
        f"Please take a minute to read our {rules_channel.mention}, "
        f"then go to {role_channel.mention} to add information about you, "
        f"specifically your location and team. "
        f"Type !roles to see what roles are available for you to add. "
        f"You must assign a team to access the raid channels!"
    )
    if member.id in FORBIDDEN_MEMBER_IDS and member.guild.id in DO_NOT_LET_NIANTIC_IN_SERVERS:
        admin_channel = get_text_channel_by_name(member, 'admins')
        await admin_channel.send(
            f'A user that should not receive the local link just joined the server: {member.name}'
        )


@client.event
async def on_member_remove(member):
    if member.guild.id not in MEE6_GREETING_GUILD_IDS:
        return
    welcome_channel = get_text_channel_by_name(member, 'welcome')
    await welcome_channel.send(f"{member.mention} just left the server. Come back soon!")


@client.event
async def on_presence_update(before, after):
    if before.id in [215316565468512256, 414716521504571393]:
        print(f'{before.name} changed status to {after.status}.')


@client.event
async def on_message(message):
    role_channel = get_text_channel_by_name(message.author, 'role-request')

    if message.content.startswith('!roles'):
        await handle_roles_info(message, role_channel)

    if message.channel.id in ROLE_CHANNELS and message.content.startswith(('!r ', '!remove ')):
        await handle_role_request(message)


async def handle_roles_info(message, role_channel):
    await message.channel.send(
        f"You can go to {role_channel.mention} to request "
        "(using the format, '!r mystic, san rafael, ross valley') "
        "any of the following tags, and you can use @ before them to call people with those tags:\n"
        "Mystic\n"
        "Valor\n"
        "Instinct\n"
        "San Rafael\n"
        "Novato\n"
        "Marinwood-TL\n"
        "Ross Valley (Fairfax, San Anselmo, Ross)\n"
        "Central Marin (Kentfield, Corte Madera, Larkspur, Greenbrae)\n"
        "Southern Marin (Mill Valley, Sausalito, Strawberry, Marin City, Tiburon Peninsula)\n"
        "West Marin (Woodacre through Pt. Reyes and out through Muir Beach)\n"
        "To remove a role, type '!remove [role]'"
    )


async def handle_role_request(message):
    roles = resolve_roles(message.content, message.guild)
    if not roles:
        return
    adding = message.content.startswith('!r ')
    try:
        if adding:
            await message.author.add_roles(*roles, reason='Self-add', atomic=True)
        else:
            await message.author.remove_roles(*roles, reason='Self-remove', atomic=True)
        verb = 'added' if adding else 'removed'
        noun = '1 role' if len(roles) == 1 else f'{len(roles)} roles'
        await message.channel.send(f'Successfully {verb} {noun}.')
    except discord.Forbidden:
        await message.channel.send("I don't have permission.")


# ── Startup ──────────────────────────────────────────────────────────────────

with open('the_file.txt', 'rb') as f:
    token = base64.b64decode(f.readline()).decode()

client.run(token)