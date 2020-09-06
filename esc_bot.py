import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

import random
import asyncio
import json 

load_dotenv()

E_FOUR = 329.63
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
POEM_ENCODED=(f"Jvcs gwb vvf vtum, pfp xma ktlca fiavvp;\n"
f"Gxl mavq, ebvs hccha ijcebdg jtgraw-ppqvv zdgm.\n"
f"Cpcchl gww ngha bw ukyn amzg vttkuwtv,\n"
f"Wdn'tt uzkeeg zgrpgtvog kcw Ymtkech Ywct.\n")
composers = {}
cage_unlocked = False
cage_occupied = False
guessed_composer = False
door_tried = False
lock_attempts = []

client = commands.Bot(command_prefix = '$')
member_count = 0
# client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
        # alternative implementations:

        # guild = discord.utils.get(client.guilds, name=GUILD)

        # for guild in client.guilds:
        #     if guild.name == GUILD:
        #         break
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_member_join(member):
    global member_count
    member_count += 1
    print (f'{member.name} has joined the server.')


def is_jett():
    def predicate(ctx):
        return ctx.message.author.id == 208419935377031168
    return commands.check(predicate)

def in_death_chamber():
    def predicate(ctx):
        return ctx.channel.name == 'death-chamber'
    try:
        return commands.check(predicate)
    except discord.ext.commands.errors.CheckFailure:
        return 

def is_prisoner(member):
    return member.id != 208419935377031168 and member.id != client.user.id

@client.command(name='start',hidden=True)
@is_jett()
async def start(ctx):
    global composers
    global guessed_composer
    global cage_unlocked
    global cage_occupied
    global lock_attempts
    global door_tried
    composers = {}
    guessed_composer = False
    cage_unlocked = False
    cage_occupied = False
    lock_attempts = []
    door_tried = False

    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    for channel in guild.channels:
        if channel.name != "Discussion":
            await channel.delete()
    for role in guild.roles:
        if (not role.managed) and (not role.is_default()):
            await role.delete()

    prisoner = await guild.create_role(name="Imprisoned Cellist")

    waiting_room = await guild.create_text_channel('waiting-room')
    await waiting_room.set_permissions(prisoner, read_messages=True, send_messages=False)
    # await waiting_room.set_permissions(ctx.guild.default_role, view_channel=True)

    death_chamber = await guild.create_text_channel('death-chamber')
    await death_chamber.set_permissions(prisoner, view_channel=False)
    # await death_chamber.set_permissions(ctx.guild.default_role, view_channel=False)
    # await death_chamber.edit(slowmode_delay=4)
    # await ctx.guild.create_voice_channel('Discussion')

    await waiting_room.send(f"__*The Game Master says:*__ ")
    await waiting_room.send(f"```fix\n"
                                f"Welcome to Mozart's Musical Mansion! KIDDING, it's my secret prison, deep in the tunnels beneath building 26.\n"
                                f"You probably don't remember how you got here (you probably don't WANT to), but you want OUT.\n"
                                f"To escape, simply DM me your favorite composer.\n"
                            f"```")

    for member in guild.members:
        if not is_prisoner(member):
            continue
        await member.add_roles(prisoner)
        await member.create_dm()

    await death_chamber.send(f"__*The Game Master says:*__ ")
    await death_chamber.send(f"```fix\n"
                                f"KIDDING! I'd never make it that easy. GET PRRRRANKED!\n"
                                f"No, you'll definitely be stuck in this room, FOREVER.\n"
                                f"Looking forward to it!\n"
                            f"```")
    
    responses = await asyncio.gather(*[collect_composers(ctx, member) for member in guild.members if is_prisoner(member)])
    composers = {x[0]: x[1] for x in responses if x is not None}
    print(composers)
    for member in guild.members:
        if is_prisoner(member):
            await waiting_room.set_permissions(member, view_channel=False)
            await death_chamber.set_permissions(member, read_messages=True, send_messages=True)
    await asyncio.sleep(1)
    
    await death_chamber.send(f"You notice a few things about this room:\n"
                                f"  - There is a beautiful melody playing from speakers overhead.\n"
                                f"  - A laptop is sitting on a bare wooden desk; it's on.\n"
                                f"  - The desk has a singular drawer.\n"
                                f"  - There is a large cage labeled, in comic sans: 'MR. SNUGGLES'.\n"
                                f"  - The door on the opposite wall is labeled 'NOT THE EXIT', in Times New Roman.\n")
    await asyncio.sleep(5)
    await death_chamber.send(f"Type $music, $laptop, $desk, $cage, or $door to investigate further.\n"
                            f"Type $hint if you get stuck.")
    await death_chamber.set_permissions(prisoner, view_channel=True, read_messages=True, send_messages=True)

async def collect_composers(ctx, member):
    waiting_room = discord.utils.find(lambda c: c.name == 'waiting-room', ctx.guild.channels)
    death_chamber = discord.utils.find(lambda c: c.name == 'death-chamber', ctx.guild.channels)

    await member.dm_channel.send('What\'s the last name of your favorite composer?')
    try:
        ans = await client.wait_for('message', timeout=60, check = lambda m: m.author.id == member.id and m.channel == member.dm_channel)
    except asyncio.TimeoutError: 
        return None
    else:
        await waiting_room.set_permissions(member, view_channel=False)
        await death_chamber.set_permissions(member, read_messages=True, send_messages=True)
        return member, ans.content.lower()

@client.command(name='music')
@in_death_chamber()
async def music(ctx):
    music_channel = discord.utils.get(ctx.guild.voice_channels, name='Music')
    if music_channel is None:
        music_channel = await ctx.guild.create_voice_channel('Music')
    await ctx.send('Head to the `Music` voice channel to hear the lovely music.')

    try:
        vc = await music_channel.connect()
    except:
        await ctx.send('Already playing music! Make sure to join the `Music` voice channel and turn volume on.')
        return

    src_path = 'C:/Users/jettw/Documents/0 Massachusetts Institute of Technology/Year 1/CelloWorld/esc/pachelbel.mp3'
    src = discord.FFmpegPCMAudio(src_path)

    vc.play(src)
    while vc.is_playing():
        await asyncio.sleep(0.2)
    await vc.disconnect()

@client.command(name='laptop')
@in_death_chamber()
async def laptop(ctx):
    death_chamber = discord.utils.get(ctx.guild.text_channels, name='death-chamber')

    await death_chamber.send(f"The laptop has 2 Chrome tabs open:")
    await death_chamber.send(f"1. 'Vines that cure my depression'")
    await death_chamber.send(f"2. '8.02 Pset'")
    await asyncio.sleep(1)
    await death_chamber.send(f"Type $tab 1 or $tab 2 to investigate further.")

@client.command(name='tab')
@in_death_chamber()
async def tab(ctx, arg: int):
    death_chamber = discord.utils.get(ctx.guild.text_channels, name='death-chamber')
    if arg == 1:
        await death_chamber.send(f"You watch the video: https://www.youtube.com/watch?v=Z2s1qIBr-DU. Then you watch it again.")
        await asyncio.sleep(1) 
        await death_chamber.send(f"Soon, an hour has passed and you __still__ haven't done your pset.")
        await asyncio.sleep(1) 
        await death_chamber.send(f"This is a familiar feeling.")
    elif arg == 2:
        await death_chamber.send(f"Your heart sinks.")
        src_path = 'C:/Users/jettw/Documents/0 Massachusetts Institute of Technology/Year 1/CelloWorld/esc/circuit_problem.png'
        await asyncio.sleep(1) 
        await death_chamber.send(file=discord.File(src_path))
    else:
        await death_chamber.send(f"That's not an open tab.")

@client.command(name='desk')
@in_death_chamber()
async def desk(ctx):
    death_chamber = discord.utils.get(ctx.guild.text_channels, name='death-chamber')
    await death_chamber.send(f"Opening the drawer, you see a massive number of **keys**.\n")
    await death_chamber.send(f"Type `$key k n` to use key k at location n.")
    await death_chamber.send(f"Possible keys: Any float between 220 and 440")
    await death_chamber.send(f"Possible locations: laptop, desk, cage, door")

@client.command(name='key')
@in_death_chamber()
async def key(ctx, k: float, loc: str):
    global composers
    global cage_unlocked
    global cage_occupied
    death_chamber = discord.utils.get(ctx.guild.text_channels, name='death-chamber')
    loc = loc.lower().strip()
    if loc == 'cage' and cage_unlocked:
        await death_chamber.send("The cage is already open. Stop wasting time.")
        return 
    if k < 220 or k > 440:
        await death_chamber.send("The key must be between 220 and 440.")
        await death_chamber.send(f"Type `$key k n` to use key k at location n.")
        return
    if abs(k - E_FOUR) < 0.1 and loc == 'cage': 
        cage_unlocked = True

        await death_chamber.send(f"The cage clicks open!")
        await asyncio.sleep(0.5)
        await death_chamber.send(f"There seems to be a piece of paper at the very back.")
        await asyncio.sleep(0.5)
        await death_chamber.send(f"There's room for __one person__ to go inside the cage and grab the paper--")
        await asyncio.sleep(0.5)
        await death_chamber.send(f"Which member of your group will do the job?")
        await asyncio.sleep(0.5)
        await death_chamber.send(f"@mention whomever you decide.")

        def check_mention(m):
            return len(m.mentions) > 0 and m.channel == death_chamber and is_prisoner(m.mentions[0]) and m.mentions[0] in composers
        msg = await client.wait_for('message', check=check_mention)
        chosen_member = msg.mentions[0]
        await death_chamber.set_permissions(chosen_member, send_messages=False)
        await chosen_member.edit(mute=True)


        await death_chamber.send(f"The cage **SNAPS** shut again- {chosen_member.name} is trapped!")
        await death_chamber.send(f"{chosen_member.name} tries to communicate, but the cage is tinted and it somehow distorts anything they try to say!")
        await asyncio.sleep(1)
        await death_chamber.send(f"__*{chosen_member.name} says:*__ ")
        await death_chamber.send(f"```yaml\n"
                                    f"I like big butts and I cannot lie\n"
                                f"```")
        await death_chamber.send(f"It must be some sort of sophisticated code.")
        await asyncio.sleep(5)
        await death_chamber.send(f"__*The Game Master says:*__ ")
        await death_chamber.send(f"```fix\n"
                                    f"If you wish to see {chosen_member.name} again,\n"
                                    f"answer me this one question:\n"
                                f"```")
        await asyncio.sleep(2)
        await death_chamber.send(f"__*The Game Master says:*__ ")
        await death_chamber.send(f"```fix\n"
                                    f"What is {chosen_member.name}'s favorite composer?\n"
                                f"```")
        
        def check_composer(m):
            return m.channel == death_chamber and m.content.lower() == composers[chosen_member]
        async def wait_answer(ctx):
            global guessed_composer
            answer = await client.wait_for('message', check=check_composer)
            guessed_composer = True
            return answer.content
        async def troll_messages(ctx):
            global guessed_composer
            death_chamber = discord.utils.get(ctx.guild.text_channels, name='death-chamber')
            messages = ['booty booty booty booty booty booty booty',
                        'maybe my favorite composer is YOUR MOM',
                        'SEEECRET TUNNELLLLLLLLLLL',
                        'That\'s rough, buddy.',
                        'i hAvE TO CapTUrE thE avAtAR and rEstoRe My hONor',
                        'Guys, i\'m fine, really! You don\'t need to worry about getting me out of here.',
                        'WHOOO HAS RICE KRISPIES???? I CAN SMELL THEM. GIVE THEM TO ME. YOU CANNOT HIDE THEM.']
            while True:
                for _ in range(40):
                    await asyncio.sleep(0.5)
                    if guessed_composer:
                        return None
                await death_chamber.send(f"__*{chosen_member.name} says:*__ ")
                await death_chamber.send(f"```yaml\n"
                                            f"{random.choice(messages)}\n"
                                        f"```")
        await asyncio.gather(wait_answer(ctx), troll_messages(ctx))

        await death_chamber.set_permissions(chosen_member, send_messages=True)
        await chosen_member.edit(mute=False)
        await death_chamber.send(f"Correct! Bravo! The cage opens.\n")
        await asyncio.sleep(2)
        await death_chamber.send(f"{chosen_member.name} crawls out, bearing the paper.\n")
        await death_chamber.send(f"On it is written... a bunch of gibberish.\n")
        await asyncio.sleep(2)
        await death_chamber.send(f"__*The paper says:*__")
        await death_chamber.send(f"```\n{POEM_ENCODED}```")
    elif k == 404:
        await death_chamber.send(f"You can't locate this key for some reason.")
    elif loc == 'cage':
        await death_chamber.send(f"The key doesn't quite fit.")
    elif loc == 'door':
        await death_chamber.send(f"Unfortunately, the door has a combo lock. No key will open it.")
    elif loc == 'laptop':
        await death_chamber.send(f"You insert key {k} into a USB port.\n")
        await death_chamber.send(f"Nothing happens.\n")
        await death_chamber.send(f"You must feel preeetty stupid right now.\n")
    elif loc == 'desk':
        await death_chamber.send(f"You inspect the desk for any keyholes.\n")
        await death_chamber.send(f"There are none.\n")
        await death_chamber.send(f"Good try... I suppose.")
    else:
        await death_chamber.send(f"loc should be one of the possible locations.")
        await death_chamber.send(f"Possible locations: laptop, desk, cage, door")
        await death_chamber.send(f"Type `$key k n` to use key k at location n.")

@client.command(name='cage')
@in_death_chamber()
async def cage(ctx):
    global cage_unlocked
    global cage_occupied
    global guessed_composer

    if guessed_composer:
        await ctx.send('The cage sits menacingly. No one dares go near it again.')
    elif cage_occupied:
        await ctx.send('The cage sits menacingly, mocking its lonesome occupant.')
    elif cage_unlocked:
        await ctx.send('The cage sits menacingly. Who will enter?')
    else:
        await ctx.send('The menacing cage is locked. A key would do the trick!')

@client.command(name='door')
@in_death_chamber()
async def door(ctx):
    global door_tried
    if not door_tried:
        door_tried = True
        await ctx.send(f"The door is locked with a 4-digit combo lock.")
        await asyncio.sleep(1)
        await ctx.send(f"__*The Game Master says:*__ ")
        await ctx.send(f"```fix\n"
                            f"I wouldn't try opening that.\n"
                            f"It's clearly not the exit.\n"
                            f"Look, it even says so on top!\n"
                        f"```")
        await asyncio.sleep(1)
        await ctx.send(f"Indeed, it says 'NOT THE EXIT' over top in large Times New Roman.\n")
        await ctx.send(f"You're inclined to believe him... you can *feel* the academic integrity in that Times New Roman.\n")
    await ctx.send(f"To try a combo, type $lock ####.")

@client.command(name='lock')
@in_death_chamber()
async def lock(ctx, combo: str):
    global lock_attempts 
    def is_int(s):
        try: 
            int(s)
            return True
        except ValueError:
            return False
    if len(combo) != 4 or not is_int(combo):
        await ctx.send(f"The lock takes 4 numeric digits.")
        await ctx.send(f"__*The Game Master says:*__ ")
        await ctx.send(f"```fix\n"
                            f"And I thought you kids were smart...\n"
                        f"```")
        return 
    if combo == '0278':
        await ctx.send(f"The lock clicks.\n")
        await ctx.send(f"You're out.\n")
        await asyncio.sleep(1)
        await ctx.send(f"__*The Game Master says:*__ ")
        await ctx.send(f"```fix\n"
                            f":'(\n"
                        f"```")
        await asyncio.sleep(2)
        await ctx.send(f"You wake up in your bed, realizing you're not in the MIT tunnels.\n")
        await ctx.send(f"You're exactly where you were yesterday, in the middle of a global pandemic.\n")
        await ctx.send(f"Everything sucks.")
        await asyncio.sleep(1)
        await ctx.send(f"---END---")

        discussion = discord.utils.get(ctx.guild.voice_channels, name='Discussion')
        try:
            vc = await discussion.connect()
        except:
            return

        src_path = 'C:/Users/jettw/Documents/0 Massachusetts Institute of Technology/Year 1/CelloWorld/esc/pachelbel.mp3'
        src = discord.FFmpegPCMAudio(src_path)

        vc.play(src)
        while vc.is_playing():
            await asyncio.sleep(0.2)
        await vc.disconnect()
    else:
        if combo not in lock_attempts:
            lock_attempts.append(combo)
        await ctx.send(f"The lock doesn't budge. Only {10000 - len(lock_attempts)} combinations to go.")
@client.command(name='ping',hidden=True)
@is_jett()
async def ping(ctx):
    await ctx.send('pong!')

@client.command(name='debug',hidden=True)
@is_jett()
async def debug(ctx):
    for member in ctx.guild.members:
        await ctx.send(f'{member.name} Permissions in this channel: {ctx.channel.permissions_for(member)}')
        await ctx.send(f'{member.name} is a Prisoner: {is_prisoner(member)}')

@client.command(name='b',hidden=True) 
@is_jett() 
async def broadcast(ctx):
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    for channel in guild.text_channels:
        await channel.send(ctx.message.content[2:])

# on errors
    # @client.event
    # async def on_command_error(ctx, error):
    #     if isinstance(error, commands.errors.CheckFailure):
    #         await ctx.send('You do not have the correct role for this command.')
    #     else:
    #         raise

    # @client.event
    # async def on_error(event, *args, **kwargs):
    #     with open('err.log', 'a') as f:
    #         if event == 'on_message':
    #             f.write(f'Unhandled message: {args[0]}\n')
    #         else:
    #             raise

client.run(TOKEN)

#TODO Slow mode
#TODO manually mute chosen_member