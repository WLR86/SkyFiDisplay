import time
import socket
import configparser
import PyIndi
import LCD

LCD = LCD.LCD(2, 0x27, True)

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


def format_coordinates(ra, dec):
    ra_hours = int(ra)
    ra_minutes = int((ra - ra_hours) * 60)
    ra_seconds = int(((ra - ra_hours) * 60 - ra_minutes) * 60)

    dec_degrees = int(dec)
    dec_minutes = int((dec - dec_degrees) * 60)
    dec_seconds = int(((dec - dec_degrees) * 60 - dec_minutes) * 60)

    ra_str = f"{ra_hours:02d}h{ra_minutes:02d}'{ra_seconds:02d}\""
    # dec_str = f"{dec_degrees:02d}ß{dec_minutes:02d}'{dec_seconds:02d}\""
    dec_str = f"{dec_degrees:02d}\xDF{dec_minutes:02d}'{dec_seconds:02d}\""

    return ra_str, dec_str


def display(line1, line2):
    # LCD.clear()
    LCD.message(line1, 1)
    LCD.message(line2, 2)


try:
    # lcd_init()

    display("SkyFi DSC", "(C) 2023 WLR")
    time.sleep(3)
    LCD.message(cfg.get('INDI', 'telescope_driver'),2)
    time.sleep(2)
    hostname = socket.getfqdn()
    # ipaddress = 
    LCD.message(hostname, 1)
    time.sleep(2)    
    
    str1 = "Waiting for"
    str2 = "Data ..."
    display(str1.center(16), str2.center(16))

    while True:
        # Récupération des coordonnées RA et DEC
        telescope = indiclient.getDevice(cfg.get('INDI', 'telescope_driver'))
        radec = telescope.getNumber("EQUATORIAL_EOD_COORD")
        ra = radec[0].value
        dec = radec[1].value
        # info = indiclient.
        # print(info[0].getStateAsString())

        # Conversion des coordonnées
        ra_str, dec_str = format_coordinates(ra, dec)

        # Affichage des coordonnées sur le LCD
        # lcd_clear()
        LCD.message(f"\xE0 {ra_str}".rjust(lcd_width), 1)
        LCD.message(f"\xE5 {dec_str}".rjust(lcd_width), 2)
        status = telescope.getText("TELESCOPE_STATUS")
        status_str = status.getText()
        # print(status_str)
        messages_blob = telescope.getBLOB("TELESCOPE_MESSAGES")
        # if messages_blob:
        messages_str = messages_blob.getBLOB()
        print(f"Messages texte : {messages_str}")

        time.sleep(cfg.getint('INDI', 'update_interval'))


except KeyboardInterrupt:
    pass

# Déconnexion du serveur INDI
indiclient.disconnectServer()
display('Shutting down'.ljust(lcd_width), 'monitoring...'.rjust(lcd_width))
time.sleep(3)
LCD.clear()
LCD.backlight('off')
