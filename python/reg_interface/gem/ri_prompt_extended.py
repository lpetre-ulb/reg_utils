import reg_utils.reg_interface.common.ri_prompt as ri_prompt
from reg_utils.reg_interface.common.reg_xml_parser import *
from reg_utils.reg_interface.common.reg_base_ops import readAddress, readReg, mpeek, mpoke, readReg, displayReg, writeReg, isValid, parseError, tabPad
from reg_utils.reg_interface.gem.vfat_config import *

MAX_OH_NUM = 12

def isValidOH(oh):
    if not oh.isdigit(): return False
    if int(oh)<0 or int(oh)>MAX_OH_NUM: return False
    return True
    
def isValidVFAT(vfat):
    if not vfat.isdigit(): return False
    if int(vfat)<0 or int(vfat)>23: return False
    return True

class Prompt(ri_prompt.Prompt):
    # override base mehod here to provide acces to exended functions
    def execute(self, other_function, args):
        other_function = 'do_'+other_function
        call_func = getattr(Prompt,other_function)
        try:
            call_func(self,*args)
        except TypeError:
            print 'Could not recognize command. See usage in tool.'


    def do_sbittranslate(self, args):
        """Decode SBit Cluster data. USAGE: sbittranslate <SBIT CLUSTER>"""
        arglist = args.split()
        if len(arglist)==1:
            try: cluster = parseInt(args)
            except: 
                print 'Invalid cluster.'
                return
            print 'VFAT:',cluster_to_vfat(cluster)
            print 'SBit:',cluster_to_vfat2_sbit(cluster)
            print 'Size:',cluster_to_size(cluster)
        else: print 'Incorrect number of arguments.'
                                          
    def do_test(self, args):
        print 'Test here!'
        print 'args:',args

    def do_broadcastOH(self, args):
        """ Begin command by selecting OHs, followed by command. USAGE broadcastOH <OH numbers> <command> register value
            OH numbers can be separated by comma or include range: 0,2-5 NO SPACES SHOULD BE BETWEEN!!
            command can be either read or write and should follow by OH register name (see example below). If command is write, add the value to write at the end
            EXAMPLE:
            broadcastOH 0,2-5 read CONTROL.CLOCK.REF_CLK
            OR
            broadcastOH 0,2-5 write CONTROL.CLOCK.REF_CLK 0x1
        """
        arglist = args.split()
        if len(arglist)<3: print 'Too few arguments.'
        else: 
            oh_numbers_list = arglist[0].split(',')
            #print "OH numbers list %s" %(oh_numbers_list)
            oh_numbers = []
            for ohn in oh_numbers_list:
                #print "OH N : %s" %(ohn)
                if ('-' in ohn):
                    borders = ohn.split('-')
                    if len(borders)!=2:
                        print "Invalid OH range!"
                        return
                    elif borders[0]=='':
                        print "Invalid OH range!"
                        return
                    else:
                        pass
                    #print type(borders)
                    #print borders
                    #print int(borders[0])
                    #print int(borders[1])
                    for x in range(int(borders[0]),int(borders[1])+1):
                        #print str(x)
                        oh_numbers.append(str(x))
                else:
                    oh_numbers.append(ohn)
            for ohn in oh_numbers:
                if int(ohn) < 0 or int(ohn) > MAX_OH_NUM:
                    print "Invalid OH range!"
                    return
            command = arglist[1]
            register = arglist[2]
            #print oh_numbers
            if command == 'read':
                for ohn in oh_numbers:
                  #print ohn
                  self.do_read('GEM_AMC.OH.OH'+ohn+'.'+register)
            elif command == 'write':
                value = arglist[3]
                for ohn in oh_numbers:
                  self.do_write('GEM_AMC.OH.OH'+ohn+'.'+register+' '+value)
            else:
                print "Only read and write functinos implemented"

    def do_oh(self, args):
        """ Begin command by selecting OH, followed by command. USAGE oh <number> <command> """
        arglist = args.split()
        if len(arglist)<1: print 'Too few arguments.'
        elif len(arglist)==1:
            if not arglist[0].isdigit():
                print 'Invalid OH number:',arglist[0]
                return
            elif int(arglist[0])<0 or int(arglist[0])>MAX_OH_NUM: print 'Invalid OH number:',arglist[0]
            else:
                if getNodesContaining('GEM_AMC.OH.OH'+str(arglist[0])+'.') is not None:
                    for reg in getNodesContaining('GEM_AMC.OH.OH'+str(arglist[0])+'.'):
                        address = reg.real_address
                        if 'r' in str(reg.permission):
                            print hex(address).rstrip('L'),reg.permission,'\t',tabPad(reg.name,7),readReg(reg)
                else: print 'Regs not found!'

        elif not arglist[0].isdigit(): print 'Incorrect usage.'
        elif int(arglist[0])<0 or int(arglist[0])>MAX_OH_NUM: print 'Invalid OH number:',arglist[0]
        else:
            new_args=''
            for i in range(2,len(arglist)):
                new_args += arglist[i]+' '
            if arglist[1]=='v2a': self.do_v2a(arglist[0])
            elif arglist[1]=='test': self.do_test(new_args)
            elif arglist[1]=='mask': self.do_mask(arglist[0]+' '+new_args)
            #elif arglist[1]=='unmask': self.do_unmask(arglist[0]+' '+new_args)
            else: print 'No command found:',arglist[1]


    def do_daq(self, args=''):
        """Read all registers in DAQ module. USAGE: daq <optional OH_NUM>"""
        arglist = args.split()
        if len(arglist)==1: 
            if not arglist[0].isdigit(): 
                print 'Incorrect usage.'
                return
            elif int(arglist[0])<0 or int(arglist[0])>MAX_OH_NUM: print 'Invalid OH number:',arglist[0]
            else:                
                if getNodesContaining('GEM_AMC.DAQ.OH'+str(arglist[0])+'.') is not None:
                    for reg in getNodesContaining('GEM_AMC.DAQ.OH'+str(arglist[0])+'.'):
                        address = reg.real_address
                        if 'r' in str(reg.permission):
                            print hex(address).rstrip('L'),reg.permission,'\t',tabPad(reg.name,7),readReg(reg)
                else: print 'Regs not found!'
        
        elif args=='': 
            if getNodesContaining('GEM_AMC.DAQ') is not None:
                for reg in getNodesContaining('GEM_AMC.DAQ'):
                    address = reg.real_address
                    if 'r' in str(reg.permission):
                        print hex(address).rstrip('L'),reg.permission,'\t',tabPad(reg.name,7),readReg(reg)
            else: print 'Regs not found!'
        
        else: print 'Incorrect usage.'

    def do_gemsystem(self, args=None):
        """Read all registers in GEM_SYSTEM module. USAGE: gemsystem"""
        if args == '':
            if getNodesContaining('GEM_AMC.GEM_SYSTEM') is not None:
                for reg in getNodesContaining('GEM_AMC.GEM_SYSTEM'):
                    address = reg.real_address
                    if 'r' in str(reg.permission):
                        print hex(address).rstrip('L'),reg.permission,'\t',tabPad(reg.name,7),readReg(reg)
            else: print 'Regs not found!'

    def do_ttc(self, args=None):
        """Read all registers in TTC module. USAGE: ttc"""
        if getNodesContaining('GEM_AMC.TTC') is not None:
            for reg in getNodesContaining('GEM_AMC.TTC'):
                address = reg.real_address
                if 'r' in str(reg.permission):
                    print hex(address).rstrip('L'),reg.permission,'\t',tabPad(reg.name,7),readReg(reg)
        else: print 'Regs not found!'

    def do_trigger(self, args=''):
        """Read all registers in TRIGGER module. USAGE: trigger <optional OH_NUM>"""
        arglist = args.split()
        if len(arglist)==1:
            if not arglist[0].isdigit():
                print 'Incorrect usage.'
                return
            elif int(arglist[0])<0 or int(arglist[0])>MAX_OH_NUM: print 'Invalid OH number:',arglist[0]
            else:
                if getNodesContaining('GEM_AMC.TRIGGER.OH'+str(arglist[0])+'.') is not None:
                    for reg in getNodesContaining('GEM_AMC.TRIGGER.OH'+str(arglist[0])+'.'):
                        address = reg.real_address
                        if 'r' in str(reg.permission):
                            print hex(address).rstrip('L'),reg.permission,'\t',tabPad(reg.name,7),readReg(reg)
                else: print 'Regs not found!'
        elif args=='':
            if getNodesContaining('GEM_AMC.TRIGGER') is not None:
                for reg in getNodesContaining('GEM_AMC.TRIGGER'):
                    address = reg.real_address
                    if 'r' in str(reg.permission):
                        print hex(address).rstrip('L'),reg.permission,'\t',tabPad(reg.name,7),readReg(reg)
            else: print 'Regs not found!'

        else: print 'Incorrect usage.'

    def do_v2a(self,args):
        """Configure recovered clock for OHv2a. USAGE v2a <OH_NUM>"""
        arglist = args.split()
        if len(arglist)==1:
            if not args.isdigit() or int(args)<0 or int(args)>2: 
                print 'Invalid OH number.'
                return
            reg = getNode('GEM_AMC.OH.OH'+str(args)+'.CONTROL.CLOCK.REF_CLK')
            if reg is not None:
                try: print writeReg(reg,1)
                except:
                    print 'Write error.'
                    return
            else: print 'Error finding clock control register!'
        else: print "Incorrect number of arguments!"


    def do_mask(self, args):
        """Mask single VFAT to data. If no VFAT provided, will mask all VFATs. USAGE mask <OH_NUM> <optional VFAT_SLOT> """
        arglist = args.split()
        if len(arglist)==1 and isValidOH(arglist[0]):
            print writeReg(getNode('GEM_AMC.OH.OH'+str(arglist[0])+'.CONTROL.VFAT.MASK'),0xffffffff)
        elif len(arglist)==2 and isValidOH(arglist[0]) and isValidVFAT(arglist[1]):
            vfat = int(arglist[1])
            oh = int(arglist[0])
            mask = (0x1 << vfat)
            try: current_mask = parseInt(readReg(getNode('GEM_AMC.OH.OH'+str(oh)+'.CONTROL.VFAT.MASK')))
            except: 
                print 'Error reading current mask.'
                return
            new_mask = mask | current_mask
            print writeReg(getNode('GEM_AMC.OH.OH'+str(oh)+'.CONTROL.VFAT.MASK'),new_mask)
        else:
            print 'Incorrect usage.'
            return
                                       
    def do_unmask(self, args):
        """Unmask single VFAT to data. If no VFAT provided, will unmask all VFATs. USAGE unmask <OH_NUM> <optional VFAT_SLOT> """
        arglist = args.split()
        if len(arglist)==1 and isValidOH(arglist[0]):
            print writeReg(getNode('GEM_AMC.OH.OH'+str(arglist[0])+'.CONTROL.VFAT.MASK'),0x00000000)
        elif len(arglist)==2 and isValidOH(arglist[0]) and isValidVFAT(arglist[1]):
            vfat = int(arglist[1])
            oh = int(arglist[0])
            mask = 0xffffffff ^ (0x1 << vfat)
            try: current_mask = parseInt(readReg(getNode('GEM_AMC.OH.OH'+str(oh)+'.CONTROL.VFAT.MASK')))
            except:
                print 'Error reading current mask.'
                return
            new_mask = mask & current_mask
            print writeReg(getNode('GEM_AMC.OH.OH'+str(oh)+'.CONTROL.VFAT.MASK'),new_mask)
        else:
            print 'Incorrect usage.'
            return

    def do_update_lmdb(self, args):
        """Updates LMDB address table at the CTP7. USAGE: update_lmdb <absolute path name to the AMC xml address table at the CTP7>"""
        if 'eagle' in hostname:
            print 'This function can only be run from a host PC'
        else:
            print 'Function temporarily not supported'
            # eagle=xi.Utils(self.cardname)
            # eagle.update_atdb(args)
            # print 'LMDB address table updated'

    def do_debug(self,args):
        """Quick read of SBit Clusters. USAGE: debug <OH_NUM>"""
        arglist = args.split()
        if len(arglist)==1:
            for reg in getNodesContaining('OH'+str(args)+'.DEBUG_LAST'):
                try: cluster = parseInt(readReg(reg))
                except: cluster = 0
                if cluster == 2047:
                    if 'r' in str(reg.permission): print hex(reg.real_address),reg.permission,'\t',tabPad(reg.name,4),readReg(reg),'(None)'
                else:
                    if 'r' in str(reg.permission): print hex(reg.real_address),reg.permission,'\t',tabPad(reg.name,4),readReg(reg),'(VFAT:',cluster_to_vfat(cluster),'SBit:',cluster_to_vfat2_sbit(cluster),'Size:',cluster_to_size(cluster),')'

        else: print "Incorrect number of arguments!"

    def do_readFW(self, args=None):
        """Quick read of all FW-related registers"""
        for reg in getNodesContaining('RELEASE'):
            if 'r' in str(reg.permission): print hex(reg.real_address),reg.permission,'\t',tabPad(reg.name,4),readReg(reg)

    def do_fw(self, args=None):
        """Quick read of all FW-related registers"""
        for reg in getNodesContaining('RELEASE'):
            if 'r' in str(reg.permission): print hex(reg.real_address),reg.permission,'\t',tabPad(reg.name,4),readReg(reg)
