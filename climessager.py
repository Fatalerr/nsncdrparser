from pprint import pprint

msg_levels=['silent','info','debug','detail']
    
class DebugMessager(object):
    "a tool control the output messages with different level "

    def __init__(self,default_level=1):
        self.message_level = default_level
        
    def setlevel(self,level):
        "level is a string or int"
        if isinstance(level,str):
            level=msg_levels.index(level)
        self.message_level = level
        
    def getlevel(self):
        return self.message_level
        
    def info(self,msgstr):
        if self.message_level >= 1:
            print msgstr  
    def debug(self,msgstr):
        if self.message_level >= 2:
            pprint(msgstr) 
    def detail(self,msgstr):
        if self.message_level >= 3:
            pprint(msgstr) 
          
        