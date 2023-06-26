import time
import configparser
import PyIndi
import LCD

LCD = LCD.LCD()

cfg = configparser.ConfigParser()

cfg.read('config.ini')

server = cfg.get('INDI', 'server')
port = cfg.getint('INDI', 'port')
lcd_width = cfg.getint('LCD', 'width')

indi = cfg['INDI']
lcd = cfg['LCD']


class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()

    def newDevice(self, d):
        global dmonitor
        # We catch the monitored device
        dmonitor = d
        # print("New device ", d.getDeviceName())

    def newProperty(self, p):
        global monitored
        global cmonitor
        # we catch the "CONNECTION" property of the monitored device
        if p.getDeviceName() == monitored and p.isNameMatch("CONNECTION"):
            cmonitor = PyIndi.PropertySwitch(p)
        # print("New property ", p.getName(), " for device ", p.getDeviceName())

    def updateProperty(self, p):
        global newval
        global prop
        nvp = PyIndi.PropertyNumber(p)
        if nvp.isValid():
            # We only monitor Number properties of the monitored device
            prop = nvp
            newval = True


# Initialisation du client INDI
indiclient = IndiClient()

monitored = indi['telescope_driver']
indiclient.setServer(indi['server'], int(indi['port']))


# Connexion au serveur INDI
indiclient.connectServer()

# Initialisation de l'afficheur LCD via I2C (vous devez avoir la
# bibliothèque smbus installée)
# bus = smbus.SMBus(1)  # Numéro du bus I2C (1 pour Raspberry Pi 3+)
#
#
# def lcd_command(cmd):
#     bus.write_byte(0x27, cmd)
#
# def lcd_data(data):
#     bus.write_byte_data(0x27, 0x40, data)
#
#
# def lcd_init():
#     lcd_command(0x33)  # Initialisation
#     lcd_command(0x32)  # Initialisation
#     lcd_command(0x06)  # Curseur vers la droite
#     lcd_command(0x0C)  # Afficher le curseur
#     lcd_command(0x28)  # 2 lignes, affichage 5x8
#
#
# def lcd_clear():
#     lcd_command(0x01)  # Effacer l'affichage
#
#
# def lcd_write_string(line, string):
#     if line == 1:
#         lcd_command(0x80)
#     elif line == 2:
#         lcd_command(0xC0)
#
#     for char in string:
#         lcd_data(ord(char))


def format_coordinates(ra, dec):
    ra_hours = int(ra)
    ra_minutes = int((ra - ra_hours) * 60)
    ra_seconds = int(((ra - ra_hours) * 60 - ra_minutes) * 60)

    dec_degrees = int(dec)
    dec_minutes = int((dec - dec_degrees) * 60)
    dec_seconds = int(((dec - dec_degrees) * 60 - dec_minutes) * 60)

    ra_str = f"{ra_hours:02d}h{ra_minutes:02d}'{ra_seconds:02d}\""
    dec_str = f"{dec_degrees:02d}ß{dec_minutes:02d}'{dec_seconds:02d}\""

    return ra_str, dec_str


def display(line1, line2):
    # LCD.clear()
    LCD.message(line1, 1)
    LCD.message(line2, 2)


try:
    # lcd_init()

    display("SkyFi DSC", "(C) 2023 WLR")
    time.sleep(5)
    str1 = "Waiting for"
    str2 = "Data ..."
    display(str1.center(16), str2.center(16))

    while True:
        # Récupération des coordonnées RA et DEC
        telescope = indiclient.getDevice('Telescope Simulator')
        radec = telescope.getNumber("EQUATORIAL_EOD_COORD")
        #  ra = telescope.getNumber("EQUATORIAL_EOD_COORD", "RA")
        #  dec = telescope.getNumber("EQUATORIAL_EOD_COORD", "DEC"
        #  pprint(getmembers(radec))
        ra = radec[0].value
        dec = radec[1].value

        # Conversion des coordonnées
        ra_str, dec_str = format_coordinates(ra, dec)

        # Affichage des coordonnées sur le LCD
        # lcd_clear()
        LCD.message(f"{ra_str}".rjust(lcd_width), 1)
        LCD.message(f"{dec_str}".rjust(lcd_width), 2)

        # Attente avant la prochaine mise à jour
        time.sleep(1)

except KeyboardInterrupt:
    pass

# Déconnexion du serveur INDI
indiclient.disconnectServer()
display('Shutting down'.ljust(lcd_width), 'monitoring...'.rjust(lcd_width))
time.sleep(3)
LCD.clear()
LCD.backlight('off')
