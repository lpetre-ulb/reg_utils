#!/usr/bin/env python

from gempython.tools.amc_user_functions_xhal import *
from reg_utils.reg_interface.common.reg_xml_parser import parseInt
from ctypes import *
import argparse

def readConfigFile(filename):
    # Read and parse the configuration file
    with open(filename, "r") as f:
        content = [int(line, 16) for line in f.readlines()]

    # GBTX configuration is 366 registers long
    if len(content) < 366:
        raise ValueError("The configuration file you provided is too short.", filename)
    else:
        return content[:366]
        
def configGBT(args):
    amcBoard = HwAMC(args.cardName);

    # We have 3 GBTX
    for i in range(3):
        if args.gbtConfigFiles[i] != "-":
            config = readConfigFile(args.gbtConfigFiles[i])
            configBlob = (c_uint8 * len(config))(*config)

            amcBoard.writeGBTConfig(args.ohN, i, configBlob)

def setPhase(args):
    amcBoard = HwAMC(args.cardName);
    amcBoard.writeGBTPhase(args.ohN, args.vfatN, args.phase)

def printPhaseScanResults(phasesBlob):
    from tabulate import tabulate

    # Create a table with the scan results
    table = []
    for phase in range(16):
        row = []
        row.append(phase)
        for vfatN in range(24):
            row.append(phasesBlob[vfatN*16+phase])

        table.append(row)

    # Create header for the table
    header = ["Phase"]
    for vfatN in range(24):
        header.append("VFAT" + str(vfatN))

    # Print the table
    print tabulate(table, headers=header)

def savePhaseScanResults(filename, ohN, nOfRepetitions, phasesBlob):
    import csv

    # Header for the ROOT file
    header = "ohN/I;"
    header += "vfatN/I:"
    header += "phase/I:"
    header += "nRepetitions/I:"
    header += "nSuccesses/I"

    # Parse the data
    data = []
    for vfatN in range(24):
        for phase in range(16):
            nOfSuccesses = phasesBlob[vfatN*16+phase]
            data.append([ohN, vfatN, phase, nOfRepetitions, nOfSuccesses])

    # Write the file
    with open(filename, 'wb') as f:
        f.write(header)
        writer = csv.writer(f, delimiter = ' ')
        writer.writerows(data)

def scanPhases(args):
    amcBoard = HwAMC(args.cardName)

    # We will retrieve the data in this array
    phasesBlob = (c_uint32 * (24*16))()

    amcBoard.scanGBTPhases(args.ohN, args.nOfRepetitions, 0, 15, 1, phasesBlob)

    # stdout output
    if not args.silent:
        printPhaseScanResults(phasesBlob)

    # File output
    if args.outputFile:
        savePhaseScanResults(args.outputFile, args.ohN, args.nOfRepetitions, phasesBlob)

if __name__ == '__main__':
    # Create the parser
    parser = argparse.ArgumentParser(description='Arguments to supply to gbt.py')

    # Positional arguments
    parser.add_argument("cardName", type=str, help="Hostname of the AMC you are connecting too, e.g. 'eagle64'")
    parser.add_argument("ohN", type=parseInt, help="Index of the OH you want to act on.")
    subparserCmds = parser.add_subparsers(help="gbt.py command help")

    # Create subparser for configGBT
    parser_configGBT = subparserCmds.add_parser("configGBT", help="Configure the GBT's of the selected OH")
    parser_configGBT.add_argument("gbtConfigFiles", action="append", metavar="GBT0", type=str, help="GBT0 configuration file / '-' means do not configure")
    parser_configGBT.add_argument("gbtConfigFiles", action="append", metavar="GBT1", type=str, help="GBT1 configuration file / '-' means do not configure")
    parser_configGBT.add_argument("gbtConfigFiles", action="append", metavar="GBT2", type=str, help="GBT2 configuration file / '-' means do not configure")
    parser_configGBT.set_defaults(func=configGBT)

    # Create subparser for setPhase
    parser_setPhase = subparserCmds.add_parser("setPhase", help="Set the phase of the selected VFAT")
    parser_setPhase.add_argument("vfatN", type=parseInt, help="VFAT to set the phase to.")
    parser_setPhase.add_argument("phase", type=parseInt, help="Value of the phase to set.")
    parser_setPhase.set_defaults(func=setPhase)

    # Create subparser for phaseScan
    parser_scanPhases = subparserCmds.add_parser("scanPhases", help="Scan the phases of the selected OH")
    parser_scanPhases.add_argument("-s", "--silent", action="store_true", help="Do not print the results table.")
    parser_scanPhases.add_argument("-o", "--outputFile", type=str, help="Save the results in this ROOT readable file.")
    parser_scanPhases.add_argument("-n", "--nOfRepetitions", type=int, help="Number of times the scan must be performed.", default=1)
    parser_scanPhases.set_defaults(func=scanPhases)

    # Parser the arguments and call the appropriate function
    args = parser.parse_args()
    args.func(args)

