"""
NSN text CDR parse tool

This tool can parse the NSN CDR text file and translate to csv format 
data. at the same time, it can generate basic statstics of the the 
CDR file.

by Liu Jun, 2014/3/25. Contact:jun1.liu@nsn.com
"""
__version__ = "1.0.2"
__description__ = ""
__date__ = "2014/4/6"
 
import re,binascii
import sys

CDR_OUTPUT_FORMAT = "cid:%(chargingID)s,nodeID:%(nodeID)s,FCI:%(FCI)s, cc:%(chargingChar)s"
DEFAULT_SACDR_FIELDS = ['fci','apn','rat','nodeID']
DEFAULT_SCDR_FIELDS = ['chargingID','apn','sgsnAddr']

## common data handling
def load_patterns_from_file(fp):
    """read the CDR fields's patterns from file and compile them to RE object"""
    patterns = {}
    
    for line in fp.readlines():
        if line.startswith('#') or len(line.strip())==0:
            continue
        key,restr = (s.strip() for s in line.split("="))
        patterns[key]=re.compile(restr.replace('"',''),re.DOTALL)
        
    return patterns

def _keyvalue2dict(kvlist):
    "transformat the 'key=value' string to a dictionary"
    if not kvlist:
        return {} 
    else:
        return dict((s.split('=') for s in kvlist))

def swap_char(rstr):
    """swap two char in the string"""
    slen=len(rstr)
    s0=(rstr[i] for i in xrange(0,slen,2))
    s1=(rstr[i] for i in xrange(1,slen,2))
    return ''.join((''.join(v) for v in zip(s1,s0)))

def _trans_locationinfo(data):
	return swap_char(binascii.a2b_hex(data))

def _trans_fci(data):
	return binascii.a2b_hex(data)

TRANSFORM_METHODS={
	'locationInfo':_trans_locationinfo,
	'fci': _trans_fci,
	'imeisv':swap_char,
}

def string_trans_hex(data,key):
    """transformat some hex string to human readable.
    """
    data = ','.join(data)  #data is a list.
    #return data
    
    if key not in TRANSFORM_METHODS.keys():
    	return data
    else:
    	return TRANSFORM_METHODS[key](data)

    # if key in ['locationInfo']:
    #     data = swap_char(binascii.a2b_hex(data[2:]))
    # elif key in ['fci']:
    #     data = binascii.a2b_hex(data[2:])
    # elif data.startswith('0x'):
    #     data = swap_char(data[2:])
    # return data    
    
class CDR(object):
    """Class store and handle CDR data
    """
    _outputformat = "%(chargingID)s,%(msisdn)s,%(imsi)s,%(chargingChar)s"
    default_cdr_fields = None
    def __init__(self):
        self._info = {}
    
    def set_output_format(self,format):
        self._outputformat = format
        
    def parse(self,cdrlines,patterns):
        text = ''.join(cdrlines)

        for key,pat in patterns.items():
            # r = pat.search(text)
            # self._info[key] = (r and self._transformat(r.groups()[0],key)) or ''
            r=pat.findall(text)
            self._info[key] = (r and string_trans_hex(r,key)) or ''
            
    def data(self,keys=None):
        _keys = keys or self._info
        return [self._info[k] for k in _keys]

    def info(self,key):
        if key in self._info:
            return self._info[key]
        else:
            return None
    def filter(self,conditions):
        result = []
        for k,p in conditions.items():
            result.append(p in self._info[k])
        return result
            
    def __repr__(self):
        return self._outputformat % (self._info)
        

class SaCDR(CDR):
    "class handle the SA-CDR"
    default_cdr_fields = DEFAULT_SACDR_FIELDS

class SCDR(CDR):
    "class handle the S-CDR"
    default_cdr_fields = DEFAULT_SCDR_FIELDS
     
def parse_cdrtext(in_stream,p_patterns,s_patterns=[]):
    """read and parse the CDR text from input_stream (file or stdin)
    
    """
    _cdrlines = []
    cdrs = []
    filtered_cdr_text = []
    filters= _keyvalue2dict(s_patterns)
            
    for line in in_stream:
        if line.strip():
            _cdrlines.append(line)
        else: #empty line encountered, another cdr block begin
            cdr = SaCDR()
            cdr.parse(_cdrlines,p_patterns)
            cdrs.append(cdr)
            if filters:
                r = cdr.filter(filters)
                if r and not False in r:
                    filtered_cdr_text.append(_cdrlines)
            _cdrlines=[]
            
    return cdrs,filtered_cdr_text
       
def count(key,result):
    try:
        result[key] +=1
    except KeyError:
        result[key] = 1
    
    return result
    

def print_cdr_stats(cdrs,fields):                       
    """Print the statistic of CDR"""
    stats = {}
    if not fields:
        fields = cdrs[0].default_cdr_fields
    for f in fields:
        stats[f] = {}

    for cdr in cdrs:
        for f in fields:
            #print "fields:",f,cdr.info(f),stats[f]
            c = count(cdr.info(f),stats[f])
            stats[f] = c

    print "\n##### CDR stats #####"
    print "Total CDR:%10d" % len(cdrs)
    for f in fields:
        print "\n### '%s' stats ###" % f
        for item in stats[f]:
            print "%s=%s:%10d" % (f,item,stats[f][item])
    

def output_cdr(ostream,cdrs,export_fields):
    header = ','.join(export_fields) + "\n"
    ostream.write(header)
    for cdr in cdrs:
        data=[cdr.info(f) for f in export_fields]
        ostream.write(','.join(data)+"\n")

def args_parse():
    parser = argparse.ArgumentParser(description=__doc__)
    subparser = parser.add_subparsers(help='commands')
    
    stats_parser = subparser.add_parser('stats', help='show the statstics of CDR file')
    stats_parser.add_argument('stats_fields',nargs="*",help="statstics fields of CDR")

    export_parser = subparser.add_parser('export', help='export ALL CDR data to a csv format')
    export_parser.add_argument('export_fields',nargs="*",help="fields of CDR which need to be exported")
    
    search_parser = subparser.add_parser('search', help='search the CDRs which match the patterns')
    search_parser.add_argument('search_patterns',nargs="*",help="patterns need to be match")
    search_parser.add_argument('-w', '--found_output',type=argparse.FileType('wt'), 
                                help="output the filtered CDR info to a file")
    
    parser.add_argument('-f','--cdr_file',type=file,default=sys.stdin,
                        help='specify the input cdr file,dont use this option when file is huge!')
    parser.add_argument('-o','--output',type=file,default=sys.stdout,
                        help="output cdr to csv format")
    parser.add_argument('-p','--patterns_file',type=file,default="sacdr.patterns",
                        help="specify the CDR field's pattern file for parsing ")
                        
    return parser.parse_args()

def main(args):
    if hasattr(args,'search_patterns'):
        #_fields = DEFAULT_CDR_FIELDS
        #start to parse
        allcdrs,cdrs_text = parse_cdrtext(cdr_file,parse_patterns,args.search_patterns)
        end_time = time()
        
        print "\nSearch '%s', \nTotal %s CDR was found" % (
                ' and '.join(args.search_patterns),len(cdrs_text))
        if args.found_output:
            for cdr in cdrs_text:
                args.found_output.write(''.join(cdr)+'\n')
            args.found_output.close()
            
    elif hasattr(args,'stats_fields'):
        _fields = args.stats_fields
        #start to parse
        allcdrs,cdrs_text = parse_cdrtext(cdr_file,parse_patterns)
        end_time = time()
        print_cdr_stats(allcdrs,_fields)
        
    elif hasattr(args,'export_fields'):
        _fields = args.export_fields or parse_patterns.keys()
        #start to parse
        allcdrs,cdrs_text = parse_cdrtext(cdr_file,parse_patterns)
        end_time = time()        
        output_cdr(args.output,allcdrs,_fields)

    return end_time

if __name__ == "__main__":  
    import argparse
    from time import time
    
    args = args_parse()
    
    parse_patterns = load_patterns_from_file(args.patterns_file)
    cdr_file = args.cdr_file
    
    print "Start to parse the CDR file using patterns file:<%s>" % args.patterns_file.name
    start_time = time()

    end_time = main(args)
    
    print "\nparsing/caculating time: %.5f/%.5f" % (end_time-start_time,time()-end_time)