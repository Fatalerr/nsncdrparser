"""
NSN CDR(text) Parser

This tool can parse the NSN CDR text file and translate the CDR data
to csv format data. at the same time, it can tell you some basic 
statstics on the CDR file(s).

by Liu Jun, 2014/3/25. Contact:jun1.liu@nsn.com
"""
__progname__    = "nsncdrparser"
__version__     = "1.2"
__description__ = "A tool parse/search/export Nokia Packet Core CDR text file"
__author__      = "Jun Liu, jun1.liu@nsn.com"
__date__        = "2014/5/17"
 
import re,binascii,sys
from climessager import DebugMessager
from configobject import ConfigObject
from collections import defaultdict,Sequence
from pprint import pprint

CDR_OUTPUT_FORMAT = "cid:%(chargingID)s,nodeID:%(nodeID)s,FCI:%(FCI)s, cc:%(chargingChar)s"
DEFAULT_SACDR_FIELDS = ['fci','apn','rat','nodeID']
DEFAULT_SCDR_FIELDS = ['chargingID','apn','sgsnAddr']

CDRINFO = ConfigObject()

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
        
def _make_filters1(kvlist):
    _kvlist=(kvstr.split("=") for kvstr in kvlist)
    return {k:re.compile(v) for k,v in _kvlist}
    
def swap_char(rstr):
    """swap two char in the string"""
    slen=len(rstr)
    s0=(rstr[i] for i in xrange(0,slen,2))
    s1=(rstr[i] for i in xrange(1,slen,2))
    return ''.join((''.join(v) for v in zip(s1,s0)))

def _trans_locationinfo(data):
	return swap_char(binascii.a2b_hex(data))

DATASTR_TRANSLATE_METHODS={
	'locationInfo': binascii.a2b_hex,
	'fci'         : binascii.a2b_hex,
	'imeisv'      : swap_char,
}

def datastr_translate(data,key):
    """translate some data string to hex/readable.
    """
    data = '|'.join(data)  #data is a list. for example: ['2000001','1000003']
    
    if key not in DATASTR_TRANSLATE_METHODS.keys():
    	return data
    else:
        #print "key:%s,data:%s" % (key,data)
    	return DATASTR_TRANSLATE_METHODS[key](data) 
    
class CDR(object):
    """Class store and handle CDR data
    """
    _outputformat = "<ChargingID:%(chargingID)s,MSISDN:%(msisdn)s,IMSI:%(imsi)s,ChargingChar:%(chargingChar)s>"
    default_cdr_fields = None

    def __init__(self):
        self._info = {}
        
    def set_output_format(self,format):
        self._outputformat = format
        
    def set_info(self,key,value):
        if key in self.__dict__:
            self.__dict__[key] = value
            
    def extract(self,cdrlines):
        "extract CDR data from cdr text block "
        text = ''.join(cdrlines)

        for key,pat in CDRINFO.Patterns.items():
            if key in CDRINFO.MultiMatches:
                r = pat.findall(text)
            else:
                r = pat.search(text)
                if r:
                    r=r.groups()
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
    _outputformat = "<ChargingID:%(chargingID)s,APN:%(apn)s,MSISDN:%(msisdn)s,IMSI:%(imsi)s,ChargingChar:%(chargingChar)s>"
    
class SCDR(CDR):
    "class handle the S-CDR"
    default_cdr_fields = DEFAULT_SCDR_FIELDS
    
class CDRList(Sequence):
    "class handle a set of CDRs"
    def __init__(self,*cdrs):
        self._cdrs = list(cdrs)
    def __getitem__(self,index):
        return self._cdrs[index]
    def append(self,cdr,txt=''):
        self._cdrs.append((cdr,txt))
    def sort(self,field=[],reverse=False):
        pass
    def __len__(self):
        return len(self._cdrs)
        
def parse_cdrtext(in_stream,cdrinfo,s_patterns=[]):
    """read and parse the CDR text from input_stream (file or stdin)
    in_stream,  the input stream, can be stdin/file stream
    cdrinfo,    the ConfigObject including pattern of CDR information.
    s_patterns, the search patterns for filtering CDR
    """
    _cdrlines  = []
    #allcdrs    = []
    allcdrs    = CDRList()
    filters    = _make_filters(s_patterns)
    cdrobj     = SaCDR or (SCDR and cdrinfo.CdrType=='SCDR')
    filtered_cdrs = CDRList()
    

    for line in in_stream:
        if line.strip():
            _cdrlines.append(line)
            continue
        #empty line encountered, another cdr block begin
        cdr = cdrobj()
        cdr.extract(_cdrlines)
        allcdrs.append(cdr)
        #if filter specified
        if filters:
            r = cdr.filter(filters)
            if r and (not None in r):
                filtered_cdrs.append(cdr,_cdrlines)
        _cdrlines=[]
           
    return allcdrs,filtered_cdrs 

def print_cdr_stats(cdrlist,fields):                       
    """Print the statistic of CDR"""
    #stats_cdr_format = "\n---CDR stats---\nTotal CDR:%10d"
    stats_cdr_format = CDRINFO.get('format_cdr_header',"\nTotal CDR:%10d")
    stats_sub_header_format = CDRINFO.get('format_sub_header',"\n---'%s' stats---")
    
    max_col = 40 
    output_items_number = CDRINFO.get('DisplayItems',5)
 
    sort_order = True
    if output_items_number <0:
        output_items_number = abs(output_items_number)
        sort_order = False

    #not fields were speicified     
    if not fields:
        try:
            #using fields info from CDRINFO
            fields = CDRINFO.DefaultFields 
        except:
            #or using the first record's 
            fields = cdrs[0].default_cdr_fields
            
    stats = {f:defaultdict(int) for f in fields}
    
    for cdr,txt in cdrlist:
        for f in fields:
            #print "fields:%s, cdr.field(f):%s,stats[f]:%s" %(f,cdr.field(f),stats[f])
            stats[f][cdr.field(f)]+=1
    
    print stats_cdr_format % len(cdrlist)
    for f in fields:
        print stats_sub_header_format % f
        _stats_sorted = sorted(stats[f].items(),key=lambda d:d[1],reverse=sort_order)
        if f in ['serviceCode']:
            max_col = 60
        for k,v in _stats_sorted[:output_items_number]:
            kvstr="%s=%s" %(f,k)
            print kvstr,str(v).rjust(max_col-len(kvstr))
        if len(_stats_sorted) > output_items_number:
            print "...\nOnly %s of %s items were displayed" % \
                    (output_items_number,len(_stats_sorted))

def output_cdr(ostream,cdrlist,export_fields):
    header = ','.join(export_fields) + "\n"
    ostream.write(header)
    for cdr,txt in cdrlist:
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
    search_parser.add_argument('search_patterns',nargs="*",help="patterns need to be match, like 'apn=cm*'")
    search_parser.add_argument('-s', '--save_matched',type=argparse.FileType('wt'), 
                                help="output the matched CDR data to a file")
    fields_parser = subparser.add_parser('list',help="list the supported fields of CDR")
    fields_parser.add_argument('list_flag',action="store_true",default=True)
    
    parser.add_argument('-f','--cdr_file',type=file,default=sys.stdin,
                        help='specify the input cdr file,dont use this option when file is huge!')
    parser.add_argument('-o','--output',type=file,default=sys.stdout,
                        help="output cdr to csv format")
    parser.add_argument('-p','--patterns_file',type=file,default="sacdr.patterns",
                        help="specify the CDR field's pattern file for parsing,default is 'sacdr.patterns'")
    parser.add_argument('-l','--output_level',action='store', default='info',
                        help="specify output message level: silent|info|debug|detail'")                            
    parser.add_argument('-n','--output_items_number',action='store',
                        help="set the number of display/output items. '-' prefix means a reverse order")
    # parser.add_argument('--fields',action='store_true', default=True,
                        # help="list the supported fields of CDR")
                        
    return parser.parse_args()

def main(args):
    #global CDRINFO
        
    if hasattr(args,'search_patterns'):
        #start to parse
        allcdrs,filtered_cdrs = parse_cdrtext(cdr_file,CDRINFO,args.search_patterns)
        end_time = time()
        
        print "\nSearch '%s', \nTotal %s CDR was found" % (
                ' and '.join(args.search_patterns),len(filtered_cdrs))
        if args.output_items_number:
            print
        if args.save_matched:
            for cdr,txt in filtered_cdrs:
                args.save_matched.write(''.join(txt)+'\n')
            args.save_matched.close()
            debug.info("and had been saved to %s" % args.save_matched.name)
            
    elif hasattr(args,'stats_fields'):
        _fields = args.stats_fields
        #start to parse
        allcdrs,filtered_cdrs = parse_cdrtext(cdr_file,CDRINFO)
        end_time = time()

        print_cdr_stats(allcdrs,_fields)
        
    elif hasattr(args,'export_fields'):
        _fields  = []
        _filters = []
        for f in args.export_fields:
            try:
                _f,_p = f.split("=")
                _fields.append(_f)
                _filters.append(f)
            except ValueError,e:
                _fields.append(f)
        if not _fields:
            _fields = CDRINFO.Patterns.keys()
        
        debug.debug(_filters)
        #start to parse
        allcdrs,filtered_cdrs = parse_cdrtext(cdr_file,CDRINFO,_filters)
        end_time = time()
        #if filtered_cdrs:
        _cdrs = filtered_cdrs or allcdrs
        
        output_cdr(args.output,_cdrs,_fields)
        
    return end_time

if __name__ == "__main__":  
    import argparse
    from time import time
    from pprint import pprint
    
    args = args_parse()
    # print args
    # exit(1)
    debug=DebugMessager()
    if args.output_level:
        debug.setlevel(args.output_level)

    CDRINFO.read(args.patterns_file.name)
    
    _pat={}
    for field,patternstr in CDRINFO.Patterns.items():
        CDRINFO.Patterns[field]=re.compile(patternstr,re.DOTALL)
    debug.debug(CDRINFO.getall())

    if args.output_items_number:
        CDRINFO.DisplayItems = int(args.output_items_number)
        
    cdr_file = args.cdr_file
    
    if hasattr(args,'silent'):
        OUTPUT_LEVEL = args.silent and 'silent' or 'Info'

        
    if hasattr(args,'list_flag'):
        fields=CDRINFO.__dict__.pop('Patterns')
        print "Definitions of '%s':\n" % args.patterns_file.name
        for k,v in CDRINFO.items():
            print " ","=".join([k,str(v)])
        
        print "\nSupported fields of CDR:"
        for key in fields:
            print " ",key
        exit(0)
        
    debug.info("Start to parse the CDR file using patterns file:<%s>" % args.patterns_file.name)
    start_time = time()

    end_time = main(args)
    
    debug.info("\nparsing/caculating time: %.5f/%.5f" % (end_time-start_time,time()-end_time))