import time
import socket
import subprocess
import configparser
import PyIndi
import RPLCD
from RPLCD.i2c import CharLCD


cfg = configparser.ConfigParser()

cfg.read('config.ini')

server = cfg.get('INDI', 'server')
port = cfg.getint('INDI', 'port')
lcd_width = cfg.getint('LCD', 'width')

indi = cfg['INDI']
lcd = cfg['LCD']

LCD = CharLCD(lcd['chip'], int(lcd['i2c_addr'],16))

# Create missing characters
degree = (0x06, 0x09, 0x09, 0x06, 0x00, 0x00, 0x00, 0x00)
delta =  (0x00, 0x06, 0x08, 0x0E, 0x11, 0x11, 0x0E, 0x00)
LCD.create_char(0,degree)
LCD.create_char(1,delta)


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
        print("New property ", p.getName(),
              " for device ", p.getDeviceName())

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

# Subscribe to our device
indiclient.watchDevice(monitored)

# Connexion au serveur INDI
indiclient.connectServer()

def deg2HMS(ra="", dec="", round=True):
    RA, DEC, rs, ds = "", "", "", ""
    if dec:
        if int(dec) > 180:
            dec = dec - 360
        if str(dec)[0] == "-":
            ds, dec = "-", abs(dec)
        else:
            ds, dec = "+", abs(dec)
        deg = int(dec)
        decM = abs(int((dec - deg) * 60))
        if round:
            decS = int((abs((dec - deg) * 60) - decM) * 60)
        else:
            decS = (abs((dec - deg) * 60) - decM) * 60
        DEC = "{}{:03d}\x00{:02d}'{:02d}\"".format(ds, deg, decM, decS)
    if ra:
        raH = int(ra)
        raM = int((ra - raH) * 60)
        raS = int(((ra - raH) * 60 - raM) * 60)
        RA = "{}{:02d}h{:02d}'{:02d}\"".format(rs, raH, raM, raS)
    if ra and dec:
        return (RA, DEC)
    else:
        return RA or DEC


def message(string,line):
    LCD.cursor_pos = (line - 1, 0)
    LCD.write_string(string)

def display(line1, line2):
    LCD.clear()
    message(line1, 1)
    message(line2, 2)

try:
    ssid = subprocess.check_output(['/usr/sbin/iwgetid','-r'], text=True).strip()

except:
    ssid = "Not found"
    print('Erreur')

try:
    # lcd_init()

    display("SkyFi DSC", "(C) 2023 WLR")
    time.sleep(2)
    message(cfg.get('INDI', 'telescope_driver'), 2)
    time.sleep(2)
    LCD.clear()
    message("SSID", 1)
    message(ssid.rjust(lcd_width), 2)
    time.sleep(2)
    LCD.clear()
    # Attempt to display what the user needs
    # SSID, hostname, IP
    hostname = socket.getfqdn()
    message("Hostname", 1)
    message(hostname.rjust(lcd_width), 2)
    time.sleep(2)

    str1 = "Waiting for"
    str2 = "Data ..."
    display(str1.center(16), str2.center(16))

    i = 0
    while not(dmonitor.isConnected()):
        str1 = "Waiting for"
        str2 = "telescope " + '.'*i
        display(str1.center(lcd_width), str2.ljust(lcd_width))
        i = i + 1
        if i == 4:
            i = 0	
	
        time.sleep(0.5)
	

    while True:
        ra, dec = 0, 0	
        # Récupération des coordonnées RA et DEC
        telescope = indiclient.getDevice(cfg.get('INDI', 'telescope_driver'))
        radec = telescope.getNumber("EQUATORIAL_EOD_COORD")
        ra, dec = radec[0].value, radec[1].value
        ra_str, dec_str = deg2HMS(ra, dec)

        # Affichage des coordonnées sur le LCD
        message(f"\xE0   {ra_str}".rjust(lcd_width), 1)
        message(f"\x01 {dec_str}".rjust(lcd_width), 2)

        time.sleep(cfg.getfloat('INDI', 'update_interval'))

except IOError:
    display("Err: can't connect", "to INDIserver")
    time.sleep(3)

except KeyboardInterrupt:
    pass

# Déconnexion du serveur INDI
indiclient.disconnectServer()
display('Shutting down'.ljust(lcd_width), 'monitoring...'.rjust(lcd_width))
time.sleep(3)
LCD.clear()
LCD.backlight_enabled = False
