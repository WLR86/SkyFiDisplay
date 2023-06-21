import time
import configParser
from pyindi_client import INDIClient
import smbus2

cfg = configParser.ConfigParser()

cfg.read('config.ini')

indi = cfg['INDI']
lcd = cfg['LCD']


# Initialisation du client INDI
indiclient = INDIClient()
indiclient.set_server(indi['server'], indi['port'])

# Connexion au serveur INDI
indiclient.connect()

# Initialisation de l'afficheur LCD via I2C (vous devez avoir la
# bibliothèque smbus2 installée)
bus = smbus2.SMBus(lcd['bus'])  # Numéro du bus I2C (1 pour Raspberry Pi 3+)


def lcd_command(cmd):
    bus.write_byte(lcd['i2c_addr'], cmd)

def lcd_data(data):
    bus.write_byte_data(lcd['i2c_addr'], 0x40, data)


def lcd_init():
    lcd_command(0x33)  # Initialisation
    lcd_command(0x32)  # Initialisation
    lcd_command(0x06)  # Curseur vers la droite
    lcd_command(0x0C)  # Afficher le curseur
    lcd_command(0x28)  # 2 lignes, affichage 5x8


def lcd_clear():
    lcd_command(0x01)  # Effacer l'affichage


def lcd_write_string(line, string):
    if line == 1:
        lcd_command(0x80)
    elif line == 2:
        lcd_command(0xC0)

    for char in string:
        lcd_data(ord(char))


def format_coordinates(ra, dec):
    ra_hours = int(ra)
    ra_minutes = int((ra - ra_hours) * 60)
    ra_seconds = int(((ra - ra_hours) * 60 - ra_minutes) * 60)

    dec_degrees = int(dec)
    dec_minutes = int((dec - dec_degrees) * 60)
    dec_seconds = int(((dec - dec_degrees) * 60 - dec_minutes) * 60)

    ra_str = f"{ra_hours:02d}h {ra_minutes:02d}m {ra_seconds:02d}s"
    dec_str = f"{dec_degrees:02d}° {dec_minutes:02d}' {dec_seconds:02d}\""

    return ra_str, dec_str


def display(line1, line2):
    lcd_clear()
    lcd_write_string(1, line1)
    lcd_write_string(2, line2)


try:
    lcd_init()

    display("SkyFi DSC", "(C) 2023 WLR")
    time.sleep(5)
    str1 = "Waiting for"
    str2 = "Data ..."
    display(str1.center(lcd['width']), str2.center(lcd['width']))

    while True:
        # Récupération des coordonnées RA et DEC
        telescope = indiclient.get_device(indi['telescope_driver'])
        ra = telescope.get_float("EQUATORIAL_EOD_COORD", "RA")
        dec = telescope.get_float("EQUATORIAL_EOD_COORD", "DEC")

        # Conversion des coordonnées
        ra_str, dec_str = format_coordinates(ra, dec)

        # Affichage des coordonnées sur le LCD
        lcd_clear()
        lcd_write_string(1, f"RA:   {ra_str}")
        lcd_write_string(2, f"DEC: {dec_str}")

        # Attente avant la prochaine mise à jour
        time.sleep(indi['update_interval'])

except KeyboardInterrupt:
    pass

# Déconnexion du serveur INDI
indiclient.disconnect()
