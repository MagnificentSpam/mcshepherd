import discord
import asyncio


class DiscordConnection(discord.Client):
    def __init__(self):
        super().__init__()
        self.instances = {}

    async def on_ready(self):
        pass

    async def on_message(self, msg):
        if msg.author.id == self.user.id:
            return
        instance = self.instances.get(msg.channel.id)
        if instance:
            if msg.content.startswith('§'):
                if msg.author.id in instance.ops:
                    instance.send_cmd(msg.content[1:])
                    print(f'executing command for {msg.author.display_name}: {msg.content[1:]}')
            else:
                instance.send_chat(msg.author.display_name, msg.content)
                print(f'Sending message from {msg.author.display_name} to {instance.name}')

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

    def register_instance(self, chid, instance):
        self.instances[chid] = instance
