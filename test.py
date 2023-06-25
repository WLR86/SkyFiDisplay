import configparser


cfg = configparser.ConfigParser()

cfg.read('config.ini')
indi = cfg['INDI']

print(indi['server'])
