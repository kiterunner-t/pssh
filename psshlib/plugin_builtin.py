#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import psshutil

from psshlib.plugin import Plugin


# 在本地执行的命令请以l开头
# lset 设置pssh选项
class BuiltInCmd(Plugin):
    def __init__(self, opts):
        Plugin.__init__(self)
        self.options = opts

        self.lsetCmd = dict({
            "timeout": self.lsetTimeout,
            "inline": self.lsetInline,
        })

        self.builtInCmds = dict({
            "lset": self.lsetCmd,
            "lhost": self.lhost,
            "lhostfile": self.lhostfile,
        })


    def printHelp(self):
        print("builtincmd")
        print("    lset timeout <seconds>")
        print("    lset inline <bool>")
        print("")
        
        print("    lhost <host-ip> ...")
        print("    lhostfile <hostfile> ...")
        
        print("\n")
    
    
    def run(self, cmd):
        if cmd[0] in self.builtInCmds:
            cmdValue = self.builtInCmds[cmd[0]]
            
            if type(cmdValue) == type({}):
                if cmd[1] in cmdValue:
                    cmdValue[cmd[1]](cmd)
                else:
                    print("invalid cmd: " + " ".join(cmd))
                    
                return False
            else:
                cmdValue(cmd)
                return False

        return True
        
        
    def lhost(self, cmd):
        if self.checkCmd(cmd, 2, "str") == False:
            return
    
        hosts = []
        for i in range(1, len(cmd)):
            hosts.extend(psshutil.parse_host_string(cmd[i], default_user=self.options.user))
            
        self.options.hosts = hosts
        
    
    def lhostfile(self, cmd):
        if self.checkCmd(cmd, 2, "str") == False:
            return
        
        try:
            hostfiles = cmd[1:]
            hosts = psshutil.read_host_files(hostfiles, default_user=self.options.user)
        except IOError:
            _, e, _ = sys.exc_info()
            sys.stderr.write('Could not open hosts file: %s\n' % e.strerror)
            return
        
        self.options.hosts = hosts
            
        
    def lsetTimeout(self, cmd):
        if self.checkCmd(cmd, 3, "int") == True:
            self.options.timeout = int(cmd[2])

            
    def lsetInline(self, cmd): 
        if self.checkCmd(cmd, 3, "bool") == True:
            self.options.inline = bool(cmd[2])
        

    def checkCmd(self, cmd, minCount, type):
        cmdLen = len(cmd)
        if cmdLen < 2 or cmdLen < minCount:
            print("error parameter number")
            return False
        
        if type == "str":
            return True
                
        for i in range(minCount - 1, cmdLen):
            item = cmd[i]
            
            if type == "bool":
                try:
                    b = int(item)
                except ValueError:
                    print("error parameter, need bool(0 or 1)")
                    return False
                    
                if b == 0 or b == 1:
                    return True
                else:
                    print("error parameter, need bool(0 or 1)")
                    return True
            elif type == "int":
                try:
                    b = int(item)
                except ValueError:
                    print("error parameter, need int")
                    return False
                    
                return True
            else:
                return False

            