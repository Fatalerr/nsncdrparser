"""
NSN text CDR parse tool

by Liu Jun, 2014/3/25. Contact:jun1.liu@nsn.com
"""
__version__ = "1.0"
__date__ = "2014/3/25"
 
import re
import sys,time,binascii

CDR_OUTPUT_FORMAT = "cid:%(chargingID)s,nodeID:%(nodeID)s,FCI:%(FCI)s, cc:%(chargingChar)s"

def load_patterns_from_file(fp):
    """read the CDR fields's patterns from file and compile them to RE object"""
    keys = []
    pats = {}
    
    for line in fp.readlines():
        if line.startswith('#') or len(line.strip())==0:
            continue
        key,restr = (s.strip() for s in line.split("="))
        keys.append(key)
        pats[key]=re.compile(restr.replace('"',''),re.DOTALL)
    return pats,keys

def swap_char(rstr):
    """swap two char in the string"""
    s0=[rstr[i] for i in xrange(0,len(rstr),2)]
    s1=[rstr[i] for i in xrange(1,len(rstr),2)]
    return ''.join([a+b for a,b in zip(s1,s0)])

class CDR(object):
    """Class store and handle CDR data
    """
    _outputformat = "%(chargingID)s,%(nodeID)s,%(fci)s,%(chargingChar)s"
    def __init__(self,keys=None,patterns=None):
        self.patterns = patterns
        if keys:
            self.keys = keys
        else:
            self.keys = patterns.keys()
        self._info = {}
    
    def set_output_format(self,format):
        CDR._outputformat = format
        
    def parse(self,cdrlines,keys=None):
        text = ''.join(cdrlines)
        if not keys:
            keys = self.keys
        for key in keys:
            r = self.patterns[key].search(text)
            if r:
                self.__dict__[key] = self._transformat(r.groups()[0],key)
            else:
                self.__dict__[key] = ''
            
    def data(self,keys=None):
        _keys = keys or self.keys
        return [self.__dict__[k] for k in _keys]

    def get_value(self,key):
        if key in self.keys:
            return self.__dict__[key]
        else:
            return None

    def __repr__(self):
        return CDR._outputformat % (self.__dict__)
        
    def _transformat(self,data,key):
        if key in ['locationInfo']:
            data = swap_char(binascii.a2b_hex(data[2:]))
        elif key in ['fci']:
            data = binascii.a2b_hex(data[2:])
        elif data.startswith('0x'):
            data = swap_char(data[2:])
        return data

class SaCDR(CDR):
    pass

def parse_cdrtext(inputstream,pats):
    """read and parse the CDR text from file or standard stdin.
    
    """
    _cdrlines = []
    cdrs = []
    
    for line in inputstream:
        if line.strip():
            _cdrlines.append(line)
        else:
            cdr = SaCDR(patterns=pats)
            cdr.parse(_cdrlines)
            cdrs.append(cdr)
            _cdrlines=[]
            
    return cdrs

def cdr_filter(rows,**filters):
    selected = rows
    for key,value in filters.items():
        selected = [cdr for cdr in selected if (key in cdr.keys) and cdr.__dict__[key] == value]
    #
    return selected
        
def count(key,result):
    if key in result:
        result[key] +=1
    else:
        result[key] = 1
    return result

def print_cdr_stats(cdrs,fields):                       
    """Print the statistic of CDR"""
    stats = {}
    for f in fields:
        stats[f] = {}

    for cdr in cdrs:
        for f in fields:
            #print "fields:",f,cdr.get_value(f),stats[f]
            c = count(cdr.get_value(f),stats[f])
            stats[f] = c

    print "##### CDR stats #####"
    print "Total CDR:%10d" % len(cdrs)
    for f in fields:
        print "\n### stats of '%s' ###" % f
        for item in stats[f]:
            print "%s=%s:%10d" % (f,item,stats[f][item])
    

def output_cdr(ostream,cdrs,export_fields):
    header = ','.join(export_fields) + "\n"
    ostream.write(header)
    for cdr in cdrs:
        data=[cdr.get_value(f) for f in export_fields]
        ostream.write(','.join(data)+"\n")

if __name__ == "__main__":  
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    subparser = parser.add_subparsers(help='commands')
    
    stats_parser = subparser.add_parser('stats', help='show the statstics of CDR file')
    stats_parser.add_argument('stats_fields',nargs="*",help="statstics fields of CDR")

    export_parser = subparser.add_parser('export', help='export all CDR data to a csv format')
    export_parser.add_argument('export_fields',nargs="*",help="fields of CDR which need to be exported")
    
    filter_parser = subparser.add_parser('filter', help='show the CDR which match the filter condtion')
    filter_parser.add_argument('filter_content',nargs="*",help="content need to be match")
    
    parser.add_argument('-f','--cdr_file',type=file,default=sys.stdin,
                        help='specify the input cdr file,dont use this option when file is huge!')
    #parser.add_argument('command',nargs='?',default='stats',help="command to be executed. expot")
    parser.add_argument('-o','--output',type=file,default=sys.stdout,
                        help="output cdr to csv format")
    parser.add_argument('-p','--patterns_file',type=file,default="cdr.patterns",
                        help="specify the CDR field's pattern file for parsing ")

    args = parser.parse_args()

    print args
    #print stats_parser.stats_fields
    
    
    start_time=time.time()
    pats,keys=load_patterns_from_file(args.patterns_file)
    allcdrs = parse_cdrtext(args.cdr_file,pats)
    end_time = time.time()

    if 'stats_fields' in args:
        _fields = args.stats_fields or ['fci','apn','rat','nodeID',]
        print_cdr_stats(allcdrs,_fields)
        print "\nparse/stats time: %s/%s" % (end_time-start_time,time.time()-end_time)

    if 'export_fields' in args:
        _fields = args.export_fields or keys
        output_cdr(args.output,allcdrs,_fields)

    