#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import psshutil

from psshlib.plugin import Plugin


class Cmd():
    TypeBool = object()
    TypeInt = object()
    TypeStr = object()


    def __init__(self, cmd_name, min_count, type, method):
        self.cmd_name = cmd_name
        self.min_count = min_count
        self.type = type
        self.method = method


# local cmd is always with prefix "l"
class BuiltInCmd(Plugin):
    def __init__(self, opts):
        Plugin.__init__(self)
        self.options = opts

        self.lset_cmd = dict({
            "timeout": Cmd("lset-timeout", 3, Cmd.TypeInt, self.lset_timeout),
            "inline": Cmd("lset-inline", 3, Cmd.TypeBool, self.lset_inline),
        })

        self.builtin_cmds = dict({
            "lset": self.lset_cmd,
            "lhost": Cmd("lhost", 2, Cmd.TypeStr, self.lhost),
            "lhostfile": Cmd("lhostfile", 2, Cmd.TypeStr, self.lhostfile),
        })


    def print_help(self):
        print(
"""builtincmd
    lset timeout <seconds>
    lset inline <bool>

    lhost <host-ip> ...
    lhostfile <hostfile> ...
""")


    def lhost(self, cmd_list):
        hosts = []
        for i in range(1, len(cmd_list)):
            hosts.extend(psshutil.parse_host_string(cmd_list[i], default_user = self.options.user))

        self.options.hosts = hosts


    def lhostfile(self, cmd_list):
        try:
            hostfiles = cmd_list[1:]
            hosts = psshutil.read_host_files(hostfiles, default_user = self.options.user)
            self.options.hosts = hosts
        except IOError:
            _, e, _ = sys.exc_info()
            sys.stderr.write('Could not open hosts file: %s\n' % e.strerror)


    def lset_timeout(self, cmd_list):
        self.options.timeout = int(cmd_list[2])


    def lset_inline(self, cmd_list): 
        self.options.inline = bool(cmd_list[2])


    def run(self, cmd_list):
        if cmd_list[0] not in self.builtin_cmds:
            return True

        tmp = self.builtin_cmds[cmd_list[0]]
        cmd_type = None
        if isinstance(tmp, dict):
            if cmd_list[1] in tmp:
                cmd_type = tmp[cmd_list[1]]
        elif isinstance(tmp, Cmd):
            cmd_type = tmp

        if cmd_type is None:
            print("invalid cmd: " + " ".join(cmd_list))
        else:
            if self.check_cmd(cmd_list, cmd_type.min_count, cmd_type.type):
                cmd_type.method(cmd_list)

        return False


    def check_cmd(self, cmd_list, min_count, cmd_type):
        cmd_len = len(cmd_list)
        if cmd_len < 2 or cmd_len < min_count:
            print("error parameter number")
            return False

        if cmd_type == Cmd.TypeStr:
            return True

        for i in range(min_count - 1, cmd_len):
            item = cmd_list[i]

            if cmd_type == Cmd.TypeBool:
                try:
                    b = int(item)
                    if b == 0 or b == 1:
                        return True
                    else:
                        print("error parameter, need bool(0 or 1)")
                        return False
                except ValueError:
                    print("error parameter, need bool(0 or 1)")
                    return False

            elif cmd_type == Cmd.TypeInt:
                try:
                    b = int(item)
                    return True
                except ValueError:
                    print("error parameter, need int")
                    return False

            else:
                return False

