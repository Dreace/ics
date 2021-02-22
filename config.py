import yaml


class Bilibili:
    def __init__(self, bilibili_config: dict):
        self.uid = bilibili_config["uid"]
        self.limit = bilibili_config["limit"]


class Config:

    def __init__(self):
        with open('config.yaml') as config_file:
            config_dict = yaml.load(config_file.read(), Loader=yaml.FullLoader)
            self.bilibili = Bilibili(config_dict["bilibili"])


config = Config()
