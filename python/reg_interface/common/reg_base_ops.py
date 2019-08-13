import sys, os, subprocess, socket
from time import sleep
from ctypes import *
from reg_xml_parser import parseInt

hostname = socket.gethostname()
if 'eagle' in hostname:
  lib = CDLL(os.getenv("GEM_PATH")+"/lib/librwreg.so")
  rReg = lib.getReg
  rReg.restype = c_uint
  rReg.argtypes=[c_uint]
  wReg = lib.putReg
  wReg.argtypes=[c_uint,c_uint]
else:
    # In a future refactoring the following try block
    # should be replaced with just teh single line below:
    #lib = CDLL("librwreg.so")
  try:
    lib = CDLL("librpcman.so")
  except OSError:
    lib = CDLL("librwreg.so")
  rReg = lib.getReg
  rReg.restype = c_uint
  rReg.argtypes=[c_uint]
  wReg = lib.putReg
  wReg.argtypes=[c_uint,c_uint]
  rpc_connect = lib.init
  rpc_connect.argtypes = [c_char_p]
  rpc_connect.restype = c_uint

def readAddress(address):
    output = rReg(address) 
    return '{0:#010x}'.format(parseInt(str(output)))

def readRawAddress(raw_address):
    try: 
        address = (parseInt(raw_address) << 2)+0x64000000
        return readAddress(address)
    except:
        return 'Error reading address. (rw_reg)'

def mpeek(address):
    if 'eagle' in hostname:
        try: 
            output = subprocess.check_output('mpeek '+str(address), stderr=subprocess.STDOUT , shell=True)
            value = ''.join(s for s in output if s.isalnum())
        except subprocess.CalledProcessError as e: value = parseError(int(str(e)[-1:]))
        return value
    else:
        print "mpeek is only available at the AMC card!"
        return 0xdeaddead

def mpoke(address,value):
    if 'eagle' in hostname:
        try: output = subprocess.check_output('mpoke '+str(address)+' '+str(value), stderr=subprocess.STDOUT , shell=True)
        except subprocess.CalledProcessError as e: return parseError(int(str(e)[-1:]))
        return 'Done.'
    else:
        print "mpoke is only available at the AMC card!"
        return 'mpoke is not available at the host PC'

def readReg(reg):
    address = reg.real_address
    if 'r' not in reg.permission:
        return 'No read permission!'
    value = rReg(parseInt(address))
    if parseInt(value) == 0xdeaddead:
        #return 'Bus Error'
        return '{0:#010x}'.format(0xdeaddead)
    if reg.mask is not None:
        shift_amount=0
        for bit in reversed('{0:b}'.format(reg.mask)):
            if bit=='0': shift_amount+=1
            else: break
        final_value = (parseInt(str(reg.mask))&parseInt(value)) >> shift_amount
    else: final_value = value
    final_int =  parseInt(str(final_value))
    return '{0:#010x}'.format(final_int)

def displayReg(reg,option=None):
    address = reg.real_address
    if 'r' not in reg.permission:
        return 'No read permission!'
    value = rReg(parseInt(address))
    if parseInt(value) == 0xdeaddead:
        if option=='hexbin': return hex(address).rstrip('L')+' '+reg.permission+'\t'+tabPad(reg.name,7)+'Bus Error'
        else: return hex(address).rstrip('L')+' '+reg.permission+'\t'+tabPad(reg.name,7)+'Bus Error'
    if reg.mask is not None:
        shift_amount=0
        for bit in reversed('{0:b}'.format(reg.mask)):
            if bit=='0': shift_amount+=1
            else: break
        final_value = (parseInt(str(reg.mask))&parseInt(value)) >> shift_amount
    else: final_value = value
    final_int =  parseInt(final_value)
    if option=='hexbin': return hex(address).rstrip('L')+' '+reg.permission+'\t'+tabPad(reg.name,7)+'{0:#010x}'.format(final_int)+' = '+'{0:032b}'.format(final_int)
    else: return hex(address).rstrip('L')+' '+reg.permission+'\t'+tabPad(reg.name,7)+'{0:#010x}'.format(final_int)
        
def writeReg(reg, value):
    address = reg.real_address
    if 'w' not in reg.permission:
        return 'No write permission!'
    # Apply Mask if applicable
    if reg.mask is not None:
        shift_amount=0
        for bit in reversed('{0:b}'.format(reg.mask)):
            if bit=='0': shift_amount+=1
            else: break
        shifted_value = value << shift_amount
        for i in range(10):
            initial_value = readAddress(address)
            try: initial_value = parseInt(initial_value) 
            except ValueError: return 'Error reading initial value: '+str(initial_value)
            if initial_value == 0xdeaddead:
                print "Writing masked reg %s : Error while reading, retry attempt (%s)"%(reg.name,i)
                sleep(0.1)
                continue
            else: break
        if initial_value == 0xdeaddead:
             print "Writing masked reg %s failed. Exiting..." %(reg.name)
        final_value = (shifted_value & reg.mask) | (initial_value & ~reg.mask)
    else: final_value = value
    output = wReg(parseInt(address),parseInt(final_value))
    if output != final_value:
        print "Writing masked reg %s failed. Exiting..." %(reg.name)
        print "wReg output %s" % (output)
    return str('{0:#010x}'.format(final_value)).rstrip('L')+'('+str(value)+')\twritten to '+reg.name
    
def isValid(address):
    try: subprocess.check_output('mpeek '+str(address), stderr=subprocess.STDOUT , shell=True)
    except subprocess.CalledProcessError as e: return False
    return True

def parseError(e):
    if e==1:
        return "Failed to parse address"
    if e==2:
        return "My Bus error"
    else:
        return "Unknown error: "+str(e)

def tabPad(s,maxlen):
    return s+"\t"*((8*maxlen-len(s)-1)/8+1) 
