#! /usr/bin/env python
# -*- coding: utf-8 -*-


import cmd
import os
import sys

from psshlib.manager import Manager, FatalError
from psshlib.plugin import PluginManager
from psshlib.plugin_builtin import BuiltInCmd
from psshlib.task import Task


class PsshCmd(cmd.Cmd):
    def __init__(self, opts):
        cmd.Cmd.__init__(self)
        self.prompt = ">> "   # define command prompt

        if opts.outdir and not os.path.exists(opts.outdir):
            os.makedirs(opts.outdir)

        if opts.errdir and not os.path.exists(opts.errdir):
            os.makedirs(opts.errdir)

        self.stdin = None
        if opts.send_input:
            self.stdin = sys.stdin.read()

        self.options = opts

        self.cmd_manager = Manager(self.options)
        self.plugin_manager = PluginManager()
        self.builtin_cmd = BuiltInCmd(self.options)


    def register_builtin(self):
        self.plugin_manager.register(self.builtin_cmd)


    def register(self, plugin):
        self.plugin_manager.register(plugin)


    def default(self, cmdline):
        if self.plugin_manager.run_plugins(cmdline):
            self.pssh_run(cmdline)


    def emptyline(self):
        # do nothing
        pass


    def do_quit(self, arg):
        return True


    def do_help(self, arg):
        self.plugin_manager.print_help()


    def pssh_run(self, cmdline):
        for host, port, user in self.options.hosts:
            cmd_ssh = ['ssh', host, '-o', 'NumberOfPasswordPrompts=1',
                    '-o', 'SendEnv=PSSH_NODENUM PSSH_HOST']
            if self.options.options:
                for opt in self.options.options:
                    cmd_ssh += ['-o', opt]
            if user:
                cmd_ssh += ['-l', user]
            if port:
                cmd_ssh += ['-p', port]
            if self.options.extra:
                cmd_ssh.extend(self.options.extra)
            if cmdline:
                cmd_ssh.append(cmdline)

            t = Task(host, port, user, cmd_ssh, self.options, self.stdin)
            self.cmd_manager.add_task(t)

        try:
            statuses = self.cmd_manager.run()
        except FatalError:
            sys.exit(1)


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
        ssh_cmd = ['ssh', host, '-o', 'NumberOfPasswordPrompts=1',
                '-o', 'SendEnv=PSSH_NODENUM PSSH_HOST']
        if opts.options:
            for opt in opts.options:
                ssh_cmd += ['-o', opt]
        if user:
            ssh_cmd += ['-l', user]
        if port:
            ssh_cmd += ['-p', port]
        if opts.extra:
            ssh_cmd.extend(opts.extra)
        if cmdline:
            ssh_cmd.append(cmdline)
        t = Task(host, port, user, ssh_cmd, opts, stdin)
        manager.add_task(t)
    try:
        statuses = manager.run()
    except FatalError:
        sys.exit(1)

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

