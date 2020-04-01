DEBUG=False

class Colors:            
    WHITE   = '\033[97m' 
    CYAN    = '\033[96m' 
    MAGENTA = '\033[95m' 
    BLUE    = '\033[94m' 
    YELLOW  = '\033[93m' 
    GREEN   = '\033[92m' 
    RED     = '\033[91m' 
    ENDC    = '\033[0m'  

def debug(string):
    if DEBUG:
        print('DEBUG: ' + string)

def debugCyan(string):
    if DEBUG:
        printCyan('DEBUG: ' + string)

def heading(string):                                                                    
    print Colors.BLUE                                                             
    print '\n>>>>>>> '+str(string).upper()+' <<<<<<<'
    print Colors.ENDC                   
                                                      
def subheading(string):                         
    print Colors.YELLOW                                        
    print '---- '+str(string)+' ----',Colors.ENDC                    
                                                                     
def printCyan(string):                                                
    print Colors.CYAN                                    
    print string, Colors.ENDC                                                                     

def printRed(string):
    print Colors.RED
    print string, Colors.ENDC                                           

def printMagenta(string):
    print Colors.MAGENTA
    print string, Colors.ENDC                                           
