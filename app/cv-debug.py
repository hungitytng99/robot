#!/usr/bin/python
import getopt
import sys

from computer_vision.object_detection import debug
from computer_vision.color_picker import pick_color

source = "" # video source
colors = [] # colors to detect objects

if __name__ == "__main__":
    argv = sys.argv[1:]
    
    try:
        opts, args = getopt.getopt(argv, "p:h")
    except:
        print("error: input arg")
        print("\t python main.py -h : for help")
        exit(1)

    if args:
        source = args[0]
        if source.isnumeric():
            source = int(source)
            
    elif opts and not '-h' in opts[0]:
        print("please give a source to the video stream e.g.")
        print("\t python main.py -p 0 http://ip:port/video : from online source" )
        print("\t python main.py -p 0 : from laptop cam")
        exit(1)

    for opt, arg in opts:
        if opt in ['-h']:
            print("options:")
            print("\t -h   \t: For help")
            print("\t -p X \t: To pick X colors to detect using the color picker \n \t \t: use X=0 to use colors defined in colors.txt")
            exit(1)

        if opt in ['-p']:
            colors = []
            for i in range(int(arg)):
                colors.append(pick_color(source))

            if not colors:
                with open('computer_vision/colors.txt', 'r') as f:
                    for line in f.readlines():
                        color = ''.join(
                            c for c in line if c not in '\n[]').split(',')
                        colors.append(list(map(int, color)))
            else:
                with open('computer_vision/colors.txt', 'w') as f:
                    for color in colors:
                        f.write(str(color) + "\n")

    debug(source, colors)
