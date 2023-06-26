import configparser


cfg = configparser.ConfigParser()

cfg.read('config.ini')
indi = cfg['INDI']

print(indi['server']['update_interval'])

print(cfg.getint('INDI', 'update_interval'))
