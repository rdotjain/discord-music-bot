# discord-music-bot

This is a discord bot that plays music in your server

a) Install everything mentioned in the requirements.txt<br>
b) Also install ffmpeg using: <br>

Debian based OS (Ubuntu, Raspberry Pi OS, Debian 10)<br>
```$sudo apt install ffmpeg```<br>

Using Snap<br>
```$sudo snap install ffmpeg```<br>

c)Create a bot/app in the discord developer platform<br>
d)Create a Youtube V3 API token and note it down
e)Add the youtube API tokeb variable: ```$export API_TOKEN=YOUR_Youtube_API_TOKEN```<br>
d)Note your discord bot TOKEN<br>
e)Add the TOKEN variable: ```$export TOKEN=YOUR_TOKEN```<br>
f)Use the OAuth2 link and add the bot to your desired discord bot<br>
g)You can change the docker bot prefix: ```$export PREFIX=PREFIX_CHARACTER```<br>
Example: ```$export PREFIX=!```<br>
h)For spotify you will have to use the developer platform. Create an app and note the ID and secret<br>
j)Export variables: ```&export SPOTIFY_ID=<YOUR_SPOTIFY_DEV_ID>``` and ```$export SPOTIFY_SECRET=<SPOTIFY_DEV_SECRET>```<br>

Default character is: ```&```

## Execution
```$python3 bot.py```<br>

## Bot commands:

a) ```&join``` => Telling the bot to join the VC (important for playing music)<br>
b) ```&play <Youtube URL>``` => Plays the audio from youtube url<br>
c) ```&pause``` => Pausing the song<br>
d) ```&resume``` => Resume music<br>
e) ```&queue``` => Shows the music queue list<br>
f) ```&skip``` => Skips the music to the next song<br>
g) ```&stop``` => Stops music and clears queue<br>
h)```&shuffle```=> Shuffles the queue of music

## Container Usage
https://hub.docker.com/repository/docker/raghavtinker/discordmusicbot<br>

### Features:
a)Can play playlists from spotify and youtube<br>
b)Can play single tracks from youtube urls and spotify urls<br>
c)Can play spotify albums<br>
d)You can also simply put the song name to play it via youtube<br>
e)Do note: Playlists in Spotify arent streamed from it. Rather they are used to create a youtube playlist which is streamed<br>
