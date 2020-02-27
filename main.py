import argparse
from config import Config
from minecraft import MinecraftInstance
from discord_connection import DiscordConnection
import atexit


def exit_handler():
    for name, instance in running.items():
        instance.join()


running = {}
atexit.register(exit_handler)


def run_shepherd(config):
    disc = DiscordConnection()
    for name, conf in config.get_instances():
        print(f'Creating instance {name}')
        mem = conf.get('mem') or 1024
        running[name] = MinecraftInstance(name, conf['path'], conf['chid'], disc, ops=conf.get('ops'), mem=mem)
        running[name].start()
        disc.register_instance(conf['chid'], running[name])
    disc.loop.run_until_complete(disc.login(config.get_discord_token()))
    disc.loop.run_until_complete(disc.connect())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str, default='config.json', help='config json')
    args = parser.parse_args()
    run_shepherd(Config(args.config))
