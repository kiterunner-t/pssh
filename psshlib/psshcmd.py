#! /usr/bin/env python
# -*- coding: utf-8 -*-


import cmd

from psshlib.manager import Manager, FatalError
from psshlib.plugin import PluginManager
from psshlib.plugin_builtin import BuiltInCmd
from psshlib.task import Task


class PsshCmd(cmd.Cmd):
    def __init__(self, opts):
        cmd.Cmd.__init__(self)
        self.pluginManager = PluginManager()
        self.options = opts
        self.builtInCmd = BuiltInCmd(self.options)
        self.prompt = ">> "    # define command prompt

    
    def registerBuiltin(self):
        self.pluginManager.register(self.builtInCmd)
        
        
    def register(self, plugin):
        # 也许可以去自动查找插件
        self.pluginManager.register(plugin)


    def default(self, cmdline):
        # 先执行插件中的命令
        if self.pluginManager.runPlugins(cmdline) == False:
            # 刷新选项，使其生效（因为这里最有可能更改了选项）
            return

        do_pssh(self.options.hosts, cmdline, self.options)


    def emptyline(self):
        # do nothing
        pass


    def do_quit(self, arg):
        return True


    def do_help(self, arg):
        self.pluginManager.printHelp()


def do_pssh(hosts, cmdline, opts):
    if opts.outdir and not os.path.exists(opts.outdir):
        os.makedirs(opts.outdir)
    if opts.errdir and not os.path.exists(opts.errdir):
        os.makedirs(opts.errdir)
    if opts.send_input:
        stdin = sys.stdin.read()
    else:
        stdin = None
    manager = Manager(opts)
    for host, port, user in hosts:
        cmd = ['ssh', host, '-o', 'NumberOfPasswordPrompts=1',
                '-o', 'SendEnv=PSSH_NODENUM PSSH_HOST']
        if opts.options:
            for opt in opts.options:
                cmd += ['-o', opt]
        if user:
            cmd += ['-l', user]
        if port:
            cmd += ['-p', port]
        if opts.extra:
            cmd.extend(opts.extra)
        if cmdline:
            cmd.append(cmdline)
        t = Task(host, port, user, cmd, opts, stdin)
        manager.add_task(t)
    try:
        statuses = manager.run()
    except FatalError:
        sys.exit(1)

    if opts.interactive == True:
        return

    if min(statuses) < 0:
        # At least one process was killed.
        sys.exit(3)
    # The any builtin was introduced in Python 2.5 (so we can't use it yet):
    #elif any(x==255 for x in statuses):
    for status in statuses:
        if status == 255:
            sys.exit(4)
    for status in statuses:
        if status != 0:
            sys.exit(5)

