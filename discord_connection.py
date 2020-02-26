import discord


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

    def register_instance(self, chid, instance):
        self.instances[chid] = instance
