import subprocess
import re
import threading
import asyncio
import discord.utils
import json


class MinecraftInstance(threading.Thread):
    def __init__(self, name, path, chid, disc, ops=None, mem=1024):
        super().__init__()
        self.name = name
        self.path = path
        self.chid = chid
        self.disc = disc
        self.ops = ops or []
        self.cmd = ['java', f'-Xmx{mem}M', f'-Xms{mem}M', '-jar', 'server.jar', 'nogui']
        self.process = None
        self._wlock = threading.Lock()

    def run(self):
        self.process = subprocess.Popen(self.cmd, cwd=self.path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        for line in self.process.stdout:
            try:
                line = line.decode('utf-8').rstrip('\n')
                m = re.match(r'\[(?P<time>\d\d:\d\d:\d\d)\] \[Server thread\/INFO\]: <(?P<author>\w+)> (?P<text>.*)', line)
                if m:
                    author = m.group('author')
                    text = m.group('text')
                    self.disc.send_mc_message(self.chid, f'{author}: {text}')
                    continue
                m = re.match(r'\[(?P<time>\d\d:\d\d:\d\d)\] \[Server thread\/INFO\]: There are (?P<amount>\d+) of a max (?P<max>\d+) players online:(?P<users>[\w ]*)', line)
                if m:
                    amount = int(m.group('amount'))
                    users = m.group('users').strip().split(' ')
                    topic = f'{amount} online'
                    if amount:
                        topic += ': ' + ' '.join(users)
                    asyncio.run_coroutine_threadsafe(self.disc.get_channel(self.chid).edit(topic=topic), self.disc.loop)
                    print(f'Setting channel topic for {self.name} to {topic}')
                    continue
                m = re.match(r'\[(?P<time>\d\d:\d\d:\d\d)\] \[Server thread\/INFO\]: (?P<user>\w+) (?P<action>joined|left) the game', line)
                if m:
                    user = m.group('user')
                    action = m.group('action')
                    msg = f'**{user} {action}**'
                    asyncio.run_coroutine_threadsafe(self.disc.get_channel(self.chid).send(msg), self.disc.loop)
                    with self._wlock:
                        self.process.stdin.write(b'list\n')
                        self.process.stdin.flush()
                print(f'Output on {self.name}: {line}')
            except UnicodeDecodeError:
                print(f'UnicodeDecodeError on instance {self.name}: {line}')

    def send_chat(self, name, text):
        text = json.dumps(text)
        cmd = f'tellraw @a {{"text":"<{name}> {text}"}}\n'
        with self._wlock:
            self.process.stdin.write(cmd.encode('utf-8'))
            self.process.stdin.flush()

    def send_cmd(self, cmd):
        cmd = f'{cmd}\n'
        self.process.stdin.write(cmd.encode('utf-8'))
        self.process.stdin.flush()
