# Licensed to Hortonworks, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Hortonworks, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import curses
import sh
import subprocess

screen = None
HINT_WIDTH = 3

class DHCPMisconfiguration(Exception):
    pass

def make_greet_window():
    H, W = screen.getmaxyx()
    greet_win = screen.subwin(H / 2 - HINT_WIDTH, W, 0, 0)
    greet_win.box()
    greet_win.addstr(1,2,"Hortonworks Sandbox 1.2")
    greet_win.addstr(2,2,"http://hortonworks.com")

def make_ip_window():
    H, W = screen.getmaxyx()
    ip_win = screen.subwin(H / 2, W, H / 2 - HINT_WIDTH, 0)
    ip_win.box()
    try:
        ip = sh.head(
                sh.awk(
                    sh.getent("ahosts", sh.hostname().strip()),
                    "{print $1}"),
                n="1").strip()
        if ip == "127.0.0.1":
            raise DHCPMisconfiguration()
    except sh.ErrorReturnCode:
        ip_win.addstr(1,2,"===================================")
        ip_win.addstr(2,2,"Connectivity issues detected!")
        ip_win.addstr(3,2,"===================================")
        ip_win.addstr(4,2,"Check VM setup instructions")
        ip_win.addstr(6,2,"For details, see VM setup instructions")
    except DHCPMisconfiguration:
        ip_win.addstr(1,2,"===================================")
        ip_win.addstr(2,2,"Connectivity issues detected!")
        ip_win.addstr(3,2,"===================================")
        ip_win.addstr(4,2,"Check connection of Host-only interface")
        ip_win.addstr(5,2,"and check DHCP is enabled for it")
        ip_win.addstr(7,2,"For details, see VM setup instructions")
    else:
        ip_win.addstr(1,2,"To initiate your Hortonworks Sandbox session,")
        ip_win.addstr(2,2,"please open a browser and enter this address ")
        ip_win.addstr(3,2,"in the browser's address field: ")
        ip_win.addstr(4,2,"http://%s/" % ip)

def make_hint_window():
    H, W = screen.getmaxyx()
    hint_win = screen.subwin(HINT_WIDTH, W, H - HINT_WIDTH, 0)
    hint_win.box()
    hint_win.addstr(1,1,"Log in to this virtual machine: Linux/Windows <Alt+F5>, Mac OS X <Cmd+Alt+F5>")

def init_screen():
    curses.noecho()

    make_greet_window()
    make_ip_window()
    make_hint_window()

def show_netinfo():
    commands = [
        "route -n",
        "getent ahosts",
        "ip addr",
        "cat /etc/resolv.conf",
        "cat /etc/hosts",
        ]

    f = file("/tmp/netinfo", "w")
    for cmd in commands:
        f.write("====  %s ==== \n" % cmd)
        f.write(subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0])
        f.write("\n")
    f.close()
    subprocess.call("less /tmp/netinfo", shell=True)


def main():
    global screen
    screen = curses.initscr()
    init_screen()

    screen.refresh()

    curses.curs_set(0)

    import sys
    if len(sys.argv)>1 and sys.argv[1] == "-s":
        screen.getch()
    else:
        while True:
            try:
                c = screen.getch()
                if c == ord('n'):
                    curses.endwin()
                    show_netinfo()
                    screen = curses.initscr()
                    init_screen()
                screen.refresh()
            except KeyboardInterrupt, e:
                pass

    curses.endwin()


if __name__ == '__main__':
    main()
