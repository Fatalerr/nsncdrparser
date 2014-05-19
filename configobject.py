### Another config file handling. the file name could be arbitrary.
class ConfigObject(object):
    """usage: conf = ConfigObject('alarm.conf')
    conf.oss_trap_ip
    """
    def __init__(self,cfile=''):
        if cfile:
            self.read(cfile)
    
    def read(self,confile):
        try:
            execfile(confile,globals(),self.__dict__)
        except IOError,e:
            print "Config File not found:%s" % e 
            
    def getall(self):
        """return a dict include all configuration"""
        return self.__dict__
    
    def items(self):
        return self.__dict__.items()
        
    def get(self,key,notfound=None):
        """return the value for 'key' or notfound if key not exist"""
        return self.__dict__.get(key,notfound)
    def __repr__(self):
        import pprint
        return pprint.pformat(self.__dict__)
        
#### or 
#conf = {} or class conf:pass
#execfile('file.conf',globals(),conf)
#conf[xxx]  