#! /usr/bin/env python

from gamelib import main
import sys

sound = True
fps = False

if '--nosound' in sys.argv:
    sound = False

if '--fps' in sys.argv:
    fps = True

main.main(sound, fps)

