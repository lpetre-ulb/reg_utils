import sys, os, socket
import cPickle as pickle
import gc
from collections import OrderedDict

"""``reg_xml_parser`` module defines XML address table parser"""

ADDRESS_TABLE_TOP = os.getenv("GEM_ADDRESS_TABLE_PATH")+'/amc_address_table_top.xml'
"""Address table location is defined through `$GEM_ADDRESS_TABLE_PATH`. The file name should be `amc_address_table_top.xml`"""
hostname = socket.gethostname()

DEBUG = True
nodes = OrderedDict()

class Node:
    """Class defining XML node 
    """
    name = ''
    """Node full name"""
    description = ''
    """Node description"""
    vhdlname = ''
    """Node VHDL name"""
    address = 0x0
    """Register address in relative address space"""
    real_address = 0x0
    """Register real address"""
    permission = ''  
    """Register permission. Possible values: 'r','w','rw' or None"""
    mask = 0x0
    """Register mask"""
    isModule = False
    """Flag indicating if a given node is a register or a module"""
    parent = None
    """Parent node"""
    level = 0
    warn_min_value = None
    """Min value warning threshold for monitoring"""
    error_min_value = None
    """Min value error threshold for monitoring"""

    def __init__(self):
        self.children = []

    def addChild(self, child):
        """Add child node

        :param Node child: A child node

        """
        self.children.append(child)

    def getVhdlName(self):
        """Convert XML node name to VHDL node name

        :return: VHDL node name

        """
        return self.name.replace(TOP_NODE_NAME + '.', '').replace('.', '_')

    def output(self):
        """Print node's content

        Ouput example:

        >>> Name: GEM_AMC.GEM_SYSTEM.BOARD_ID
        >>> Description: Board ID that gets embedded in the AMC13 header
        >>> Address: 0x00900002
        >>> Permission: rw
        >>> Mask: 0x0000ffff
        >>> Module: False
        >>> Parent: GEM_AMC.GEM_SYSTEM
        >>> None        

        """
        print 'Name:',self.name
        print 'Description:',self.description
        print 'Address:','{0:#010x}'.format(self.address)
        print 'Permission:',self.permission
        if self.mask is not None: 
            print 'Mask:','{0:#010x}'.format(self.mask)
        else:
            print 'Mask: None'
        print 'Module:',self.isModule
        print 'Parent:',self.parent.name

def main():
    parseXML()
    print 'Example:'
    random_node = nodes.values()[74]
    print 'Node:',random_node.name
    print 'Parent:',random_node.parent.name
    kids = []
    getAllChildren(random_node, kids)
    print len(kids), kids[0].name

def parseXML():
    """Parses XML file. A ``cPickle`` module is used to produce a ``*.pickle`` file to speed up the process. 
       
       In case ``*.pickle`` file exists it will be loaded, otherwise an ``xml`` file will be parsed and a new ``pickle`` file created for future operations

    :return: OrederedDict nodes
    """
    print 'Open pickled address table if available ',ADDRESS_TABLE_TOP[:-3]+'pickle...'

    fname =  ADDRESS_TABLE_TOP[:-3] + "pickle"
    try:
        gc.disable()
        f = open(fname, 'r')
        global nodes 
        nodes = pickle.load(f) 
        f.close()
        gc.enable()
    except IOError:
        if 'eagle' in hostname:
            print 'Pickle file not found, please create new pickle file at the host PC and upload it to the CTP7 card'
            sys.exit()
        else:
            print 'Pickle file not found, parsing ',ADDRESS_TABLE_TOP,'...'
            import lxml.etree as xml
            tree = xml.parse(ADDRESS_TABLE_TOP)
            tree.xinclude()
            root = tree.getroot()
            vars = {}
            makeTree(root,'',0x0,nodes,None,vars,False)

            # Save parsed nodes as pickle
            name = ADDRESS_TABLE_TOP[:-3] + "pickle"
            f = open(name, 'w')
            pickle.dump(nodes, f, -1)
            f.close()

    return nodes

def makeTree(node,baseName,baseAddress,nodes,parentNode,vars,isGenerated):
    """Build the nodes tree recursively
    
    :param Node node: Current node
    :param str basname: Current node name without parent nodes
    :param uint_32 baseAddress: Relative address
    :param OrderedDict nodes: Already built node tree
    :param Node parentNode: Parent node
    :param list vars: Dictionary of index shift for generated nodes
    :param bool isGenerated: Flag showing whether the node should be generated (make a number of copies of the same node changing an index parameter) from the address table

    """
    
    if (isGenerated == None or isGenerated == False) and node.get('generate') is not None and node.get('generate') == 'true':
        generateSize = parseInt(node.get('generate_size'))
        generateAddressStep = parseInt(node.get('generate_address_step'))
        generateIdxVar = node.get('generate_idx_var')
        for i in range(0, generateSize):
            vars[generateIdxVar] = i
            makeTree(node, baseName, baseAddress + generateAddressStep * i, nodes, parentNode, vars, True)
        return
    newNode = Node()
    name = baseName
    if baseName != '': name += '.'
    if node.get('id') is not None:
        name += node.get('id')
    name = substituteVars(name, vars)
    newNode.name = name
    if node.get('description') is not None:
        newNode.description = node.get('description')
    address = baseAddress
    if node.get('address') is not None:
        address = baseAddress + parseInt(node.get('address'))
    newNode.address = address
    newNode.real_address = (address<<2)+0x64000000
    newNode.permission = node.get('permission')
    newNode.mask = parseInt(node.get('mask'))
    newNode.isModule = node.get('fw_is_module') is not None and node.get('fw_is_module') == 'true'
    if node.get('sw_monitor_warn_min_threshold') is not None:
        newNode.warn_min_value = node.get('sw_monitor_warn_min_threshold') 
    if node.get('sw_monitor_error_min_threshold') is not None:
        newNode.error_min_value = node.get('sw_monitor_error_min_threshold') 
    nodes[name] = newNode
    if parentNode is not None:
        parentNode.addChild(newNode)
        newNode.parent = parentNode
        newNode.level = parentNode.level+1
    for child in node:
        makeTree(child,name,address,nodes,newNode,vars,False)

def getAllChildren(node,kids=[]):
    """Fills children information

    :param Node node: Current node
    :param OrderedDict kids: Children of a given node

    """
    if node.children==[]:
        kids.append(node)
        return kids
    else:
        for child in node.children:
            getAllChildren(child,kids)

def getNode(nodeName):
    """

    :param str nodeName: Node name
    :return: If found returns Node, otherwise returns None

    """
    try: 
        return nodes[nodeName]
    except KeyError:
        print "Node %s not found" %(nodeName)
        return None

def getNodeFromAddress(nodeAddress):
    """
    
    :param uint_32 nodeAddress: Node address
    :return: A node having the nodeAddress

    """
    return next((node for node in nodes.values() if node.real_address == nodeAddress),None)

def getNodesContaining(nodeString):
    """
 
    :param str nodeString: Substring of node(s) name
    :return: List of nodes containing provided substring in their names

    """
    nodelist = [nodes[key] for key in nodes if nodeString in key]
    if len(nodelist): 
        return nodelist
    else: return None

#returns *readable* registers
def getRegsContaining(nodeString):
    """
 
    :param str nodeString: Substring of register(s) name
    :return: List of readable registers containing provided substring in their names

    """
    nodelist = [nodes[key] for key in nodes if nodeString in key and nodes[key].permission is not None]
    if len(nodelist):
        return nodelist
    else: return None

def completeReg(string):
    """

    :param str string: Starting substring of node name
    :return: A list of nodes with names starting with input string

    """
    possibleNodes = [] 
    completions = []
    currentLevel = len([c for c in string if c=='.'])
  
    possibleNodes = [node for node in nodes.values() if node.name.startswith(string) and node.level == currentLevel]
    if len(possibleNodes)==1:
        if possibleNodes[0].children == []: return [possibleNodes[0].name]
        for n in possibleNodes[0].children:
            completions.append(n.name)
    else:
        for n in possibleNodes:
            completions.append(n.name)
    return completions

def parseInt(s):
    """

    :param str s: An integer number in dec, hex or binary format
    :return: Converted integer

    """
    if s is None:
        return None
    string = str(s)
    if string.startswith('0x'):
        return int(string, 16)
    elif string.startswith('0b'):
        return int(string, 2)
    else:
        return int(string)

def substituteVars(string, vars):
    """
    
    :param str string: Initial string
    :param dict vars: A dictionary with substition pairs
    :return: Initial string with substitions key to value from vars dictionary

    """
    if string is None:
        return string
    ret = string
    for varKey in vars.keys():
        ret = ret.replace('${' + varKey + '}', str(vars[varKey]))
    return ret

if __name__ == '__main__':
    main()
