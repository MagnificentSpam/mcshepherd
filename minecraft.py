import subprocess
import re
import threading
import asyncio
import discord.utils


class MinecraftInstance(threading.Thread):
    def __init__(self, name, path, chid, disc, ops=[], mem=1024):
        super().__init__()
        self.name = name
        self.path = path
        self.chid = chid
        self.disc = disc
        self.ops = ops
        self.cmd = ['java', f'-Xmx{mem}M', f'-Xms{mem}M', '-jar', 'server.jar', 'nogui']
        self.process = None

    def run(self):
        self.process = subprocess.Popen(self.cmd, cwd=self.path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        for line in self.process.stdout:
            try:
                line = line.decode('utf-8').rstrip('\n')
                m = re.match(r'\[(?P<time>\d\d:\d\d:\d\d)\] \[Server thread/INFO\]: <(?P<author>\w+)> (?P<text>.*)', line)
                if m:
                    author = m.group('author')
                    text = m.group('text')
                    msg = discord.utils.escape_markdown(f'{author}: {text}')
                    asyncio.run_coroutine_threadsafe(self.disc.get_channel(self.chid).send(msg), self.disc.loop)
                else:
                    print(f'Output on {self.name}: {line}')
            except UnicodeDecodeError:
                print(f'UnicodeDecodeError on instance {self.name}: {line}')

    def send_chat(self, name, text):
        text = text.replace('\n', ' ')
        cmd = f'tellraw @a {{"text":"<{name}> {text}"}}\n'
        self.process.stdin.write(cmd.encode('utf-8'))
        self.process.stdin.flush()

    def send_cmd(self, cmd):
        cmd = f'{cmd}\n'
        self.process.stdin.write(cmd.encode('utf-8'))
        self.process.stdin.flush()
