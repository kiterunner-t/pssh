#! /usr/bin/env python
# -*- coding: utf-8 -*-


# For user-defined plugin, please inherit this Class
class Plugin():
    def __init__(self):
        self.index = -1


    def get_index(self):
        return self.index


    def set_index(self, index):
        self.index = index


    def run(self, cmd):
        return True


    def print_help(self):
        pass


class PluginManager():
    def __init__(self):
        self.plugins = {}
        self.next_index = 0


    def register(self, plugin):
        # @TODO maybe should search the plugins automatically
        if isinstance(plugin, Plugin):
            plugin.set_index(self.next_index)
            self.plugins[self.next_index] = plugin
            self.next_index += 1
        else:
            print("be not instance of Plugin Class")


    def unregister(self, plugin):
        plugin_index = plugin.get_index()
        if plugin_index in self.plugins:
            del self.plugins[plugin_index]


    # 在插件中对cmd进行处理，可以是直接执行命令，也可以是权限检查等等
    #
    # return value:
    #     True 需要进行后续的命令处理
    #     False 跳过后续命令处理
    def run_plugins(self, cmdline):
        cmd_list = cmdline.split()
        for plugin in self.plugins.itervalues():
            if not plugin.run(cmd_list):
                return False

        return True # 默认后续命令需要处理


    def print_help(self):
        for plugin in self.plugins.itervalues():
            plugin.print_help()

