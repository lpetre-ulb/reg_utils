import sys
from time import *
from reg_utils.reg_interface.arm.mcs_utils import readMcs

def main():

    filename = ""
    if len(sys.argv) < 2:
        print('Usage: mcs.py <mcs_filename>')
        return
    else:
        filename = sys.argv[1]

    timeStart = clock()
    readMcs(filename, 5464972)
    totalTime = clock() - timeStart
    print('time took = ' + str(totalTime))

if __name__ == '__main__':
    main()
