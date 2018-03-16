#!/usr/bin/env python

import sys, os, paramiko
import argparse
import ConfigParser


def main():
    """
    Nginx maintenance mode manager
    """
    global ssh_username, maintenance_page_path, nodes, nodes_arg
    nodes_arg = {}
    config = ConfigParser.ConfigParser()

    if os.path.isfile("/etc/nginx-maintenance-admin.conf"):
        conf_file = "/etc/nginx-maintenance-admin.conf"
    else:
        conf_file = os.getcwd() + "/nginx-maintenance-admin.conf"
        config.readfp(open(conf_file))

    maintenance_page_path = config.get("options", "maintenance_page_path")
    ssh_username = config.get("options", "ssh_username")
    nodes = dict(config.items('nodes'))

    parser = argparse.ArgumentParser(prog='ngmm')
    parser.add_argument("--nodes", nargs="*", help="Choose a node. Default = all")
    parser.add_argument("command", nargs=1, help="Available commands: list, status, enable, disable")
    args = parser.parse_args()


    if args.nodes is not None:
        for node_key in args.nodes:
            if node_key in nodes:
                nodes_arg[node_key] = nodes[node_key]
            else:
                print node_key + " is not in the configuration!"
                sys.exit(1)

    if bool(nodes_arg):
        nodes_actual = nodes_arg
    else:
        nodes_actual = nodes

    if args.command == ["list"]:
        list_nodes()
    elif args.command == ["status"]:
            display_status(nodes_actual)
    elif args.command == ["enable"]:
        change_status(nodes_actual, "enable")
    elif args.command == ["disable"]:
        change_status(nodes_actual,"disable")
    else: parser.print_help()

def get_status(ip):
    """
    Checks maintenance mode status of the hosts
    """
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
            return True
        except IOError:
            return False
    finally:
        sshclient.close()


def display_status(node):
    """
    Displays the maintenance mode status of the nodes
    """
    for hostname, ip in node.iteritems():
        node_status = get_status(ip)
        if node_status == True:
            print "Status of " + hostname + " : \t" + "[\x1B[32;40m Enabled  \x1B[0m]"
        else:
            print "Status of " + hostname + " : \t" + "[\x1B[31;40m Disabled \x1B[0m]"

def list_nodes():
    """
    Lists all nodes from the configuration
    """
    for hostname, ip in nodes.iteritems():
        print hostname + "\t" + ip

def change_status(node, action):
    """
    Checks maintenance mode status of the hosts
    """

    for hostname, ip in node.iteritems():
        node_status = get_status(ip)
        if node_status == True:
            change_cmd = "mv " + maintenance_page_path + " " + maintenance_page_path + ".DISABLED"
        else:
            change_cmd = "mv" + maintenance_page_path + ".DISABLED " + maintenance_page_path
        try:
            sshclient = paramiko.SSHClient()
            sshclient.load_system_host_keys()
            sshclient.set_missing_host_key_policy(paramiko.WarningPolicy())
            sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshclient.connect(
            ip.partition(':')[0],
            port=int(ip.partition(':')[2]),
            username=ssh_username)

            stdin, stdout, stderr = sshclient.exec_command(change_cmd)
            print stdout.read()
        finally:
            sshclient.close()

        print "Status of " + hostname + " ( " + ip.partition(":")[0] + " ):\t Ok"

if __name__ == "__main__":
    main()
