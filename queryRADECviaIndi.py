import time
from pyindi_client import INDIClient
import smbus2

# Adresse IP et port du serveur INDI
INDI_SERVER_IP = "localhost"
INDI_SERVER_PORT = 7624
LCD_WIDTH = 16

# Initialisation du client INDI
indiclient = INDIClient()
indiclient.set_server(INDI_SERVER_IP, INDI_SERVER_PORT)

# Connexion au serveur INDI
indiclient.connect()

# Nom du driver du télescope
telescope_driver = "Telescope Simulator"

# Intervalles de mise à jour des coordonnées (en secondes)
update_interval = 5

# Initialisation de l'afficheur LCD via I2C (vous devez avoir la
# bibliothèque smbus2 installée)
lcd_address = 0x27  # Adresse I2C de l'afficheur LCD
bus = smbus2.SMBus(1)  # Numéro du bus I2C (1 pour Raspberry Pi 3+)


def lcd_command(cmd):
    bus.write_byte(lcd_address, cmd)


def lcd_data(data):
    bus.write_byte_data(lcd_address, 0x40, data)


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
    display(str1.center(LCD_WIDTH), str2.center(LCD_WIDTH))

    while True:
        # Récupération des coordonnées RA et DEC
        telescope = indiclient.get_device(telescope_driver)
        ra = telescope.get_float("EQUATORIAL_EOD_COORD", "RA")
        dec = telescope.get_float("EQUATORIAL_EOD_COORD", "DEC")

        # Conversion des coordonnées
        ra_str, dec_str = format_coordinates(ra, dec)

        # Affichage des coordonnées sur le LCD
        lcd_clear()
        lcd_write_string(1, f"RA:   {ra_str}")
        lcd_write_string(2, f"DEC: {dec_str}")

        # Attente avant la prochaine mise à jour
        time.sleep(update_interval)

except KeyboardInterrupt:
    pass

# Déconnexion du serveur INDI
indiclient.disconnect()
