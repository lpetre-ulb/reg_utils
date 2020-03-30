#!/usr/bin/env python
import sys, os, subprocess

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-e", "--execute", type="str", dest="exe",
                      help="Function to execute once", metavar="exe", default=None)
    parser.add_option("-n", "--hostname", type="string", dest="hostname",
                      help="CTP7 hostname, default is the one used at p5", default="")

    (options, args) = parser.parse_args()

    # A possible way of adding user extension module:
    #try:
    #   from gem_reg_interface_extras.ri_prompt_extended import *
    #   print "Extended prompt module found"
    #except ImportError:
    #   print "Extended prompt module not found, importing basic one"
    from reg_utils.reg_interface.common.ri_prompt import *

    if options.exe:
        parseXML()
        if (options.hostname):
            if (rpc_connect(options.hostname)):
                print '[Connection error] RPC connection failed'
                exit
        prompt=Prompt()
        prompt.execute(options.exe,args)
        sys.exit()
    else:
        try:
            parseXML()
            prompt = Prompt()
            prompt.prompt = 'CTP7 > '
            print 'Starting CTP7 Register Command Line Interface. Please connect to CTP7 using connect <hostname> command unless you use it directly at the CTP7'
            prompt.cmdloop_with_keyboard_interrupt()
        except TypeError as te:
            print '[TypeError] Incorrect usage. See help... ', te
        except KeyboardInterrupt:
            print '\n'
