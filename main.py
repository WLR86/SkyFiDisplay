import subprocess
import time

program = subprocess.Popen(['/home/willy/.local/bin/indi-web'])

print('Ok')

while program.poll():
    time.sleep(1)
    continue


