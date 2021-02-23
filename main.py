from config import config
from generators import bilibili

if __name__ == '__main__':
    if config.bilibili.enable:
        bilibili.bilibili(config.bilibili)
