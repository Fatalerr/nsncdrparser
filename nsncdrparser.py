"""
NSN CDR(text) Parser

This tool can parse the NSN CDR text file and translate the CDR data
to csv format data. at the same time, it can tell you some basic 
statstics on the CDR file(s).

by Liu Jun, 2014/3/25. Contact:jun1.liu@nsn.com
"""
__progname__    = "nsncdrparser"
__version__     = "1.1"
__description__ = "A tool parse/search/export NSN CDR text file"
__author__      = "Jun Liu, jun1.liu@nsn.com"
__date__        = "2014/4/12"
 
import re,binascii,sys
from climessager import DebugMessager
from configobject import ConfigObject

CDR_OUTPUT_FORMAT = "cid:%(chargingID)s,nodeID:%(nodeID)s,FCI:%(FCI)s, cc:%(chargingChar)s"
DEFAULT_SACDR_FIELDS = ['fci','apn','rat','nodeID']
DEFAULT_SCDR_FIELDS = ['chargingID','apn','sgsnAddr']

def _make_filters(kvlist):
    """transformat the 'key=value' string to a dictionary"""
    if not kvlist:
        return {} 
    else:
        filters={}
        for kvstr in kvlist:
            key,patstr = kvstr.split("=")
            filters[key]=re.compile(patstr.strip())
        return filters

def swap_char(rstr):
    """swap two char in the string"""
    slen=len(rstr)
    s0=(rstr[i] for i in xrange(0,slen,2))
    s1=(rstr[i] for i in xrange(1,slen,2))
    return ''.join((''.join(v) for v in zip(s1,s0)))

def _trans_locationinfo(data):
	return swap_char(binascii.a2b_hex(data))

def ascii2hex(data):
	return binascii.a2b_hex(data)

DATASTR_TRANSLATE_METHODS={
	'locationInfo': ascii2hex,
	'fci'         : ascii2hex,
	'imeisv'      : swap_char,
}

def datastr_translate(data,key):
    """translate some data string to hex/readable.
    """
    data = ','.join(data)  #data is a list. example: ['2000001','1000003']
    
    if key not in DATASTR_TRANSLATE_METHODS.keys():
    	return data
    else:
    	return DATASTR_TRANSLATE_METHODS[key](data) 
    
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
            self._info[key] = (r and datastr_translate(r,key)) or ''
            
    def data(self,keys=None):
        _keys = keys or self._info
        return [self._info[k] for k in _keys]

    def field(self,key):
        if key in self._info:
            return self._info[key]
        else:
            return None
    def filter(self,conditions):
        result = []
        for key,pattern in conditions.items():
            #append the re.match result to a list
            #print "key/pat/str",key,pattern,self._info[key]
            result.append(pattern.match(self._info[key]))
        #print result    
        return result
            
    def __repr__(self):
        return self._outputformat % (self._info)
        

class SaCDR(CDR):
    "class handle the SA-CDR"
    default_cdr_fields = DEFAULT_SACDR_FIELDS

class SCDR(CDR):
    "class handle the S-CDR"
    default_cdr_fields = DEFAULT_SCDR_FIELDS
     
def parse_cdrtext(in_stream,cdrinfo,s_patterns=[]):
    """read and parse the CDR text from input_stream (file or stdin)
    
    """
    _cdrlines  = []
    cdrs       = []
    filters    = _make_filters(s_patterns)
    cdrobj     = SaCDR or (SCDR and cdrinfo.CdrType=='SCDR')
    p_patterns = cdrinfo.Patterns
    filtered_cdr_text = []
    
    for line in in_stream:
        if line.strip():
            _cdrlines.append(line)
        else: #empty line encountered, another cdr block begin
            cdr = cdrobj()
            cdr.parse(_cdrlines,p_patterns)
            cdrs.append(cdr)
            if filters:
                r = cdr.filter(filters)
                if r and (not None in r):
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
    stats_cdr_format = "\n---CDR stats---\nTotal CDR:%10d"
    stats_sub_header_format = "\n---'%s' stats---"
    try:
        max_display_items = cdrinfo.MaxDisplayItems
    except:
        max_display_items = 5
    
    stats = {}
    if not fields:
        try:
            fields = cdrinfo.DefaultFields
        except:
            fields = cdrs[0].default_cdr_fields
    for f in fields:
        stats[f] = {}

    for cdr in cdrs:
        for f in fields:
            #print "fields:",f,cdr.info(f),stats[f]
            c = count(cdr.field(f),stats[f])
            stats[f] = c

    print stats_cdr_format % len(cdrs)
    for f in fields:
        print stats_sub_header_format % f
        _stats_sorted = sorted(stats[f].items(),key=lambda d:d[1],reverse=True)
        for k,v in _stats_sorted[:max_display_items]:
            print "%s=%s:%10d" % (f,k,v)
        if len(_stats_sorted) > max_display_items:
            print "Total %s were found, Only %s items were displayed" % \
                    (len(_stats_sorted),max_display_items)

def output_cdr(ostream,cdrs,export_fields):
    header = ','.join(export_fields) + "\n"
    ostream.write(header)
    for cdr in cdrs:
        data=[cdr.field(f) for f in export_fields]
        ostream.write(','.join(data)+"\n")

def args_parse():
    parser = argparse.ArgumentParser(description=__doc__,
                                     version=" v".join([__progname__,__version__]))
    subparser = parser.add_subparsers(help='commands')
    
    stats_parser = subparser.add_parser('stats', help='show the statstics of CDR file')
    stats_parser.add_argument('stats_fields',nargs="*",help="statstics fields of CDR")

    export_parser = subparser.add_parser('export', help='export ALL CDR data to a csv format')
    export_parser.add_argument('export_fields',nargs="*",help="fields of CDR which need to be exported")
    
    search_parser = subparser.add_parser('search', help='search the CDRs which match the patterns')
    search_parser.add_argument('search_patterns',nargs="*",help="patterns need to be match")
    search_parser.add_argument('-s', '--save_found',type=argparse.FileType('wt'), 
                                help="output the filtered CDR data to a file")
    
    parser.add_argument('-f','--cdr_file',type=file,default=sys.stdin,
                        help='specify the input cdr file,dont use this option when file is huge!')
    parser.add_argument('-o','--output',type=file,default=sys.stdout,
                        help="output cdr to csv format")
    parser.add_argument('-p','--patterns_file',type=file,default="sacdr.patterns",
                        help="specify the CDR field's pattern file for parsing ")
    parser.add_argument('-l','--output_level',action='store', default='info',
                        help="specify output message level")                            
    parser.add_argument('-m','--max_disp_items',action='store',default=5,
                        help="set the maxinum display/output items")
                        
    return parser.parse_args()

def main(args):
    global cdrinfo
    
    if hasattr(args,'search_patterns'):
        #start to parse
        allcdrs,cdrs_text = parse_cdrtext(cdr_file,cdrinfo,args.search_patterns)
        end_time = time()
        
        print "\nSearch '%s', \nTotal %s CDR was found" % (
                ' and '.join(args.search_patterns),len(cdrs_text))
        if args.save_found:
            for cdr in cdrs_text:
                args.save_found.write(''.join(cdr)+'\n')
            args.save_found.close()
            debug.info("and had been saved to %s" % args.save_found.name)
            
    elif hasattr(args,'stats_fields'):
        _fields = args.stats_fields
        #start to parse
        allcdrs,cdrs_text = parse_cdrtext(cdr_file,cdrinfo)
        end_time = time()
        print_cdr_stats(allcdrs,_fields)
        
    elif hasattr(args,'export_fields'):
        if args.export_fields:
            _fields = [f for f in args.export_fields if f in cdrinfo.Patterns]
        else:
            _fields = cdrinfo.Patterns.keys()

        #start to parse
        allcdrs,cdrs_text = parse_cdrtext(cdr_file,cdrinfo)
        end_time = time()        
        output_cdr(args.output,allcdrs,_fields)

    return end_time

if __name__ == "__main__":  
    import argparse
    from time import time
    from pprint import pprint
    
    args = args_parse()
    
    debug=DebugMessager()
    if args.output_level:
        debug.setlevel(args.output_level)

    cdrinfo=ConfigObject(args.patterns_file.name)
    _pat={}
    for field,patternstr in cdrinfo.Patterns.items():
        cdrinfo.Patterns[field]=re.compile(patternstr,re.DOTALL)
    debug.debug(cdrinfo.getall())

    if args.max_disp_items:
        cdrinfo.MaxDisplayItems = int(args.max_disp_items)
        
    cdr_file = args.cdr_file
    
    if hasattr(args,'silent'):
        OUTPUT_LEVEL = args.silent and 'silent' or 'Info'
    
    debug.info("Start to parse the CDR file using patterns file:<%s>" % args.patterns_file.name)
    start_time = time()

    end_time = main(args)
    
    debug.info("\nparsing/caculating time: %.5f/%.5f" % (end_time-start_time,time()-end_time))