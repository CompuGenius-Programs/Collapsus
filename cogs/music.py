import json
from asyncio import sleep

import discord
from discord import Option
from discord.ext import commands

import parsers
from main import guild_id
from utils import create_embed


def setup(bot):
    bot.add_cog(Music(bot))


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stream_channel = 655390551138631704

    async def get_songs(self, ctx: discord.AutocompleteContext):
        return [song for song in parsers.songs if ctx.value.lower() in song.lower()]

    @discord.slash_command(name="song", description="Plays a song.")
    async def _song(self, ctx, song_name: Option(str, "Song Name", autocomplete=get_songs, required=True)):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=self.bot.get_guild(ctx.guild_id))
        if voice_client is None or not voice_client.is_playing():
            voice_state = ctx.author.voice
            if voice_state is None:
                embed = create_embed("You need to be in a voice channel to use this command.")
                return await ctx.respond(embed=embed, ephemeral=True)

            channel = voice_state.channel.id
            if channel == self.stream_channel:
                embed = create_embed("You can't use this command in the stream channel.")
                return await ctx.respond(embed=embed, ephemeral=True)

            await ctx.defer()

            with open("data/songs.json", "r", encoding="utf-8") as fp:
                data = json.load(fp)
            songs = data["songs"]

            index = next(filter(lambda s: s["title"].lower() == song_name.lower(), songs), None)
            song = parsers.Song.from_dict(index)

            if voice_client is None:
                voice_client = await self.bot.get_channel(channel).connect()
            await self.play(ctx, voice_client, song, channel)

            embed = create_embed("Playing `%s` in <#%s>" % (song.title, channel))
            await ctx.followup.send(embed=embed)

            while voice_client.is_playing():
                await sleep(1)
            await voice_client.disconnect()
        else:
            embed = create_embed("I'm already playing a song. Please wait until it's finished.")
            return await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="songs_all", description="Plays all songs.")
    async def _all_songs(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=self.bot.get_guild(ctx.guild_id))
        if voice_client is None or not voice_client.is_playing():
            voice_state = ctx.author.voice
            if voice_state is None:
                embed = create_embed("You need to be in a voice channel to use this command.")
                return await ctx.respond(embed=embed, ephemeral=True)

            channel = voice_state.channel.id
            if channel == self.stream_channel:
                embed = create_embed("You can't use this command in the stream channel.")
                return await ctx.respond(embed=embed, ephemeral=True)

            await ctx.respond("Playing all songs. Please wait...")

            with open("data/songs.json", "r", encoding="utf-8") as fp:
                data = json.load(fp)
            songs = data["songs"]

            if voice_client is None:
                voice_client = await self.bot.get_channel(channel).connect()

            message = None
            for index, s in enumerate(songs):
                if not voice_client.is_connected():
                    break

                song = parsers.Song.from_dict(s)
                await self.play(ctx, voice_client, song, channel)

                embed = create_embed("Playing all songs. Currently playing `%s` in <#%s>" % (song.title, channel))
                try:
                    await message.edit(embed=embed)
                except:
                    message = await ctx.send(embed=embed)

                while voice_client.is_playing():
                    await sleep(1)
            await voice_client.disconnect()
        else:
            embed = create_embed("I'm already playing a song. Please wait until it's finished.")
            return await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="stop", description="Stops playing a song.")
    async def _stop_song(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=self.bot.get_guild(ctx.guild_id))
        if voice_client is None or not voice_client.is_playing():
            embed = create_embed("I'm not playing a song.")
            return await ctx.respond(embed=embed, ephemeral=True)

        await voice_client.disconnect()

        embed = create_embed("Stopped playing.")
        await ctx.respond(embed=embed)

    async def play(self, ctx, voice_client, song: parsers.Song, channel):
        if voice_client.is_connected():
            source = discord.FFmpegPCMAudio(song.url, executable="ffmpeg")
            voice_client.play(source)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=self.bot.get_guild(guild_id))
        if voice_client is None:
            return
        music_voice_channel = voice_client.channel
        if len(music_voice_channel.members) <= 1:
            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()
