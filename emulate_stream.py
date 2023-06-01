#! /usr/bin/python
# vim: set fileencoding=utf-8 autoindent expandtab tabstop=4 shiftwidth=4 softtabstop=4 : # noqa

import time
import sys


def loopValues():
    for spot in spots:
        sys.stdout.write(spot)
        sys.stdout.flush()
        time.sleep(1)


def main(spots):
    while True:
        loopValues()


if __name__ == "__main__":
    spots = [
        "eFA263700,FE15D100#",
        "eFA263700,3E15D100#",
        "e34AB0500,12CE0500#",
        "e14AB0500,72CE0500#",
    ]
    main(spots)
