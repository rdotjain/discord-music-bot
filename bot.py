import discord
from discord.ext import commands,tasks
import os
import asyncio
import youtube_dl
from youtubePlaylist import *

token = ""
server_queue = dict()


#Prefix input
prefix = ""
try:
    print(os.environ['PREFIX'])
    prefix = str(os.environ['PREFIX'])
except:
    prefix = '&'
bot = commands.Bot(command_prefix = prefix)


#Youtube stuff. Thanks to stackoverflow
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, play=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream or play))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#Discord stuff

#joining the channel
@bot.command(name="join")
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel!")
        return
    else:
        channel = ctx.message.author.voice.channel
        await ctx.send(f'Connected to ``{channel}``')
    await channel.connect()

#Leaving VC
@bot.command(name="leave")  
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Bot left!")
        server_queue[ctx.guild.id] = []
    else:
        await ctx.send("I am not in the VC")

async def getQueuePopulated(server_id, urls):
    for url in urls:
        if(server_id in server_queue):
            server_queue[server_id].append(await YTDLSource.from_url(url, loop=bot.loop, stream=True))
        else:
            server_queue[server_id] = [await YTDLSource.from_url(url, loop=bot.loop, stream=True)]

#Play command
@bot.command(name="play") 
async def play(ctx, url):
    vc = ctx.voice_client

    if not vc:
        if not ctx.message.author.voice:
            embed = discord.Embed(title="", descritpion="You are not connected the Voice channel", color=discord.Color.red())
            await ctx.send(embed)
            return
        else:
            channel = ctx.message.author.voice.channel
            embed = discord.Embed(title="", descritpion="Connected to ``{channel}``", color=discord.Color.red())
            await ctx.send(embed)
    
    await channel.connect()
    print(type(server_queue))
    voice_client = ctx.voice_client
    try:
        if "playlist" in url:
            urls_in_playlist = getURL(url)
            number_of_songs = await getQueuePopulated(ctx.guild.id, urls_in_playlist)
            await ctx.send("Added {} songs".format(len(urls_in_playlist)))
            start_playing(ctx.guild.id, voice_client)
        else:
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            
                if ctx.guild.id in server_queue:
                    #already using the bot
                    if(len(server_queue[ctx.guild.id]) == 0):
                        server_queue[ctx.guild.id].append(player)
                        await ctx.send("Playing {}".format(player.title))
                        start_playing(ctx.guild.id, voice_client)
                    else:
                        server_queue[ctx.guild.id].append(player)
                        await ctx.send("Added to queue {}".format(player.title))
                else:
                    server_queue[ctx.guild.id] = [player]
                    await ctx.send("Playing {}".format(player.title))
                    start_playing(ctx.guild.id, voice_client)
    except Exception as error:
        print(error)
        await ctx.send("Something went wrong, try again later")
                
#Playing music
def start_playing(server_id, voice_client):
    if(len(server_queue[server_id]) != 0):
        player = server_queue[server_id][0]
        try:
            voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else queuePlayer(server_id, voice_client))
        except:
            print("unkown error!")
        #Removing stuff from the list
    else:
        print("queue over")

#Queue management
def queuePlayer(server_id, voice_client):
    if server_id in server_queue:
        server_queue[server_id].pop(0)
    else:
        print("empty")
    start_playing(server_id, voice_client)

#Pause
@bot.command(name="pause")
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client

    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("I am not playing anything")

#Resume
@bot.command(name="resume")
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await ctx.send("Resuming...")
        await voice_client.resume()
    else:
        await ctx.send("I am not playing anything")

#Skip
@bot.command(name="skip")
async def skip(ctx):
    #skip the track
    print("skip")
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()

#Queue
@bot.command(name="queue")
async def queue(ctx):
    message = ""
    count = 0
    for player in server_queue[ctx.guild.id]:
        if (count < 7):
            message = message + player.title + "\n"
            count = count + 1
        else:
            break
    await ctx.send("{}".format(message))

#Stop music
@bot.command(name="stop")
async def stop(ctx):
    server_queue[ctx.guild.id] = []
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    await ctx.send("Stopped, queue removed")

#Now playing
@bot.command(name="np")
async def np(ctx):
    await ctx.send("Playing {}".format(server_queue[ctx.guild.id][0].title))

#Token input
try:
    print(os.environ['TOKEN'])
    token = str(os.environ['TOKEN'])
    bot.run(token)
except:
    print("Invalid token")
