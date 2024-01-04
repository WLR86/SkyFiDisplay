#Documentation AutoHotspot

Copy autohotspot.txt to /usr/bin/autohotspot
chmod +x /usr/bin/autohotspot

sudo apt install hostapd dnsmasq

sudo cp autohotspot-service.txt /etc/systemd/system/autohotspot.service
sudo systemctl enable autohotspot.service

cp hostapd.txt /etc/hostapd.conf
You have first to configure it by creating the file /etc/hostapd/hostapd.conf and reference to it in /etc/default/hostapd with option DAEMON_CONF="/etc/hostapd/hostapd.conf"

hostapd is masked by default and its ok as is : our service script will take care of this 


