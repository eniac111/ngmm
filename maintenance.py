#!/usr/bin/env python

import sys, os, paramiko
import argparse
from argparse_color_formatter import ColorHelpFormatter
import ConfigParser

# ssh_username = ""

def main():
    """
    Nginx maintenance mode manager
    """
    config = ConfigParser.ConfigParser()

    if os.path.isfile("/etc/nginx-maintenance-admin.conf"):
        conf_file = "/etc/nginx-maintenance-admin.conf"
    else:
        conf_file = os.getcwd() + "/nginx-maintenance-admin.conf"
        config.readfp(open(conf_file))

    maintenance_page_path = config.get("options", "maintenance_page_path")
    ssh_username = config.get("options", "ssh_username")
    nodes = dict(config.items('nodes'))

    # print(hosts)

    status(nodes, ssh_username, maintenance_page_path)

def status(nodes, ssh_username, maintenance_page_path):
    """
    Checks maintenance mode status of the hosts
    """

    retr = {}
    for hostname, ip in nodes.iteritems():
        host_status = "N/A"
        try:
            sshclient = paramiko.SSHClient()
            sshclient.load_system_host_keys()
            sshclient.set_missing_host_key_policy(paramiko.WarningPolicy())
            sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshclient.connect(
            ip.partition(':')[0],
            port=int(ip.partition(':')[2]),
            username=ssh_username)
            sftp = sshclient.open_sftp()
            try:
                sftp.stat(maintenance_page_path)
                host_status = "[\x1B[31;40m Enabled  \x1B[0m]"
                retr[hostname] = True
            except IOError:
                host_status = "[\x1B[32;40m Disabled \x1B[0m]"
                retr[hostname] = False
        finally:
            sshclient.close()

        print "Status of " + hostname + " ( " + ip.partition(":")[0] + " ):\t " + host_status
    for i in retr:
        print i, retr[i]


def display_status(nodes_status):
    """
    Displays the maintenance mode status of the nodes
    """

    for hostname, status in nodes_status:
        if status == True:
            print "Status of " + hostname +

def change(nodes, ssh_username):
    """
    Checks maintenance mode status of the hosts
    """

    for hostname, ip in nodes.iteritems():
        try:
            sshclient = paramiko.SSHClient()
            sshclient.load_system_host_keys()
            sshclient.set_missing_host_key_policy(paramiko.WarningPolicy())
            sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshclient.connect(
            ip.partition(':')[0],
            port=int(ip.partition(':')[2]),
            username=ssh_username)

            stdin, stdout, stderr = sshclient.exec_command("touch /tmp/foo")
            print stdout.read()
        finally:
            sshclient.close()

        print "Status of " + hostname + " ( " + ip.partition(":")[0] + " ):\t Ok"

if __name__ == "__main__":
    main()
