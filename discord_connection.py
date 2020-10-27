import discord
import asyncio
import json
from pytimeparse.timeparse import timeparse
import time


class DiscordConnection(discord.Client):
    def __init__(self, config):
        super().__init__()
        self.instances = {}
        self.config = config

    async def on_ready(self):
        print('ready')

    async def on_message(self, msg):
        if msg.author.id == self.user.id:
            return
        if msg.content.startswith('!underagepersonidentified'):
            args = msg.content.split(' ')[1:]
            if len(args) < 2:
                await msg.channel.send('Use !underagepersonidentified <userid> 1y2m10d')
            for role in msg.author.roles:
                if role.id in self.config.get_moderator_roles():
                    break
            else:
                await msg.channel.send(f'I\'m sorry, {msg.author.display_name}. I\'m afraid I can\'t do that. ')
                return
            try:
                user = await msg.guild.fetch_member(int(args[0]))
                t = timeparse(' '.join(args[1:]))
                self.add_blocked_user(user.id, t)
                for rid in [721469067680022541, 721469037753794560, 768857774573617153]:
                    await user.remove_roles(discord.utils.get(msg.guild.roles, id=rid))
                await msg.channel.send(f'blocked {user.display_name} from nsfw channels for {t} seconds')
            except (discord.HTTPException, ValueError) as e:
                await msg.channel.send(str(e))
        instance = self.instances.get(msg.channel.id)
        if instance:
            if msg.content.startswith('§'):
                if msg.author.id in instance.ops:
                    instance.send_cmd(msg.content[1:])
                    print(f'executing command for {msg.author.display_name}: {msg.content[1:]}')
            else:
                instance.send_chat(msg.author.display_name, msg.content)
                print(f'Sending message from {msg.author.display_name} to {instance.name}')

    async def on_raw_reaction_add(self, payload):
        print(f'user {payload.user_id} reacted in {payload.channel_id} with {payload.emoji}')
        if payload.channel_id == 721487932606906399:
            ch = self.get_channel(payload.channel_id)
            user = ch.guild.get_member(payload.user_id) or await ch.guild.fetch_member(payload.user_id)
            if payload.emoji.is_custom_emoji():
                if payload.emoji.id == 721206165605974019:  # mc
                    role = discord.utils.get(ch.guild.roles, id=721461067334680626)
                    await user.add_roles(role)
            elif payload.emoji.name == '🤖':  # tech
                role = discord.utils.get(ch.guild.roles, id=769767161258311741)
                await user.add_roles(role)
            elif payload.emoji.name == '☕':  # adult-lounge
                if self.is_user_blocked(user.id):
                    msg = await ch.fetch_message(payload.message_id)
                    await msg.remove_reaction('☕', user)
                else:
                    role = discord.utils.get(ch.guild.roles, id=768857774573617153)
                    await user.add_roles(role)
            elif payload.emoji.name == '🤢':  # wasteland
                if self.is_user_blocked(user.id):
                    msg = await ch.fetch_message(payload.message_id)
                    await msg.remove_reaction('🤢', user)
                else:
                    role = discord.utils.get(ch.guild.roles, id=721469067680022541)
                    await user.add_roles(role)
            elif payload.emoji.name == '🇧🇷':  # pt
                role = discord.utils.get(ch.guild.roles, id=722963391316230194)
                await user.add_roles(role)

    async def on_raw_reaction_remove(self, payload):
        print(f'user {payload.user_id} unreacted in {payload.channel_id} with {payload.emoji}')
        if payload.channel_id == 721487932606906399:
            ch = self.get_channel(payload.channel_id)
            user = ch.guild.get_member(payload.user_id) or await ch.guild.fetch_member(payload.user_id)
            if payload.emoji.is_custom_emoji():
                if payload.emoji.id == 721206165605974019:  # mc
                    role = discord.utils.get(ch.guild.roles, id=721461067334680626)
                    await user.remove_roles(role)
            elif payload.emoji.name == '🤖':  # tech
                role = discord.utils.get(ch.guild.roles, id=769767161258311741)
                await user.remove_roles(role)
            elif payload.emoji.name == '☕':  # adult-lounge
                role = discord.utils.get(ch.guild.roles, id=768857774573617153)
                await user.remove_roles(role)
            elif payload.emoji.name == '🤢':  # nsfw
                role = discord.utils.get(ch.guild.roles, id=721469067680022541)
                await user.remove_roles(role)
                await user.remove_roles(role)
            elif payload.emoji.name == '🇧🇷':  # pt
                role = discord.utils.get(ch.guild.roles, id=722963391316230194)
                await user.remove_roles(role)

    def send_mc_message(self, chid, msg):
        channel = self.get_channel(chid)
        parts = []
        for word in msg.split(' '):
            if word.startswith('@'):
                name = word[1:].lower()
                for member in channel.members:
                    if member.display_name.lower().startswith(name):
                        word = member.mention
                        break
                else:
                    word = discord.utils.escape_markdown(word)
            else:
                word = discord.utils.escape_markdown(word)
            parts.append(word)
        msg = ' '.join(parts)
        asyncio.run_coroutine_threadsafe(self.get_channel(chid).send(msg), self.loop)

    def add_blocked_user(self, uid, t):
        with open('blocked_users.json') as f:
            blocked_users = json.load(f)
        until = time.time() + t
        blocked_users[str(uid)] = until
        with open('blocked_users.json', 'w') as f:
            json.dump(blocked_users, f)

    def is_user_blocked(self, uid):
        with open('blocked_users.json') as f:
            blocked_users = json.load(f)
        until = blocked_users.get(str(uid))
        if until:
            print(f'{uid} blocked until {until} ({until - time.time()} more s)')
            if until > time.time():
                return True
            else:
                del blocked_users[str(uid)]
                with open('blocked_users.json', 'w') as f:
                    json.dump(blocked_users, f)
                return False
        else:
            return False

    def register_instance(self, chid, instance):
        self.instances[chid] = instance
