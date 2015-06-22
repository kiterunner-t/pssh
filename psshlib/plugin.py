#! /usr/bin/env python
# -*- coding: utf-8 -*-


# 自定义插件，请继承该类
class Plugin():
    def __init__(self):
        self.index = -1


    def getIndex(self):
        return self.index


    def setIndex(self, index):
        self.index = index


    # 实现自定义插件应该覆盖该方法
    def run(self, cmd):
        return True

    
    def printHelp(self):
        pass
        

class PluginManager():
    def __init__(self):
        self.plugins = []
        self.nextIndex = 0


    def register(self, plugin):
        # 自省检查是否为Plugin及其子类
        plugin.setIndex(self.nextIndex)
        self.plugins.append(plugin)
        self.nextIndex += 1


    def unregister(self, plugin):
        pluginIndex = plugin.getIndex()
        if pluginIndex in self.plugins:
            del self.plugins[pluginIndex]


    # 在插件中对cmd进行处理，可以是直接执行命令，也可以是权限检查等等
    # 返回值
    #     True 需要进行后续的命令处理
    #     False 跳过后续命令处理
    def runPlugins(self, cmd):
        cmdList = cmd.split()
        for plugin in self.plugins:
            if plugin.run(cmdList) == False:
                return False

        return True # 默认后续命令需要处理

        
    def printHelp(self):
        for plugin in self.plugins:
            plugin.printHelp()
