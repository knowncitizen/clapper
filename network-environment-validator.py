#!/usr/bin/env python
# curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
# python get-pip.py

import argparse
import ipaddress
import itertools
import logging
import sys
import yaml

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)  # JPEELER: change to INFO later


def argParser():
    parser = argparse.ArgumentParser(description='Clapper')

    parser.add_argument('-n', '--netenv',
                        help='path to network environment file',
                        type=str,
                        default='network-environment.yaml')

    return vars(parser.parse_args())


def main():
    args = argParser()

    cidrinfo = {}
    poolsinfo = {}
    vlaninfo = {}
    routeinfo = {}
    bondinfo = {}

    with open(args['netenv'], 'r') as net_file:
        network_data = yaml.load(net_file)
        LOG.debug('\n' + yaml.dump(network_data))

    for item in network_data['parameter_defaults']:
        data = network_data['parameter_defaults'][item]

        if item.endswith('NetCidr'):
            cidrinfo[item] = data
        elif item.endswith('AllocationPools'):
            poolsinfo[item] = data
        elif item.endswith('NetworkVlanID'):
            vlaninfo[item] = data
        elif item == 'ExternalInterfaceDefaultRoute':
            routeinfo = data
        elif item == 'BondInterfaceOvsOptions':
            bondinfo = data

    check_cidr_overlap(cidrinfo.values())
    check_allocation_pool(poolsinfo.values())


def check_cidr_overlap(networks):
    objs = [ipaddress.ip_network(x.decode('utf-8')) for x in networks]
    LOG.debug(objs)

    for net1, net2 in itertools.combinations(objs, 2):
        if (net1.overlaps(net2)):
            LOG.error('Overlapping networks detected {} {}'.format(net1, net2))


def check_allocation_pool(ranges):
    objs = [[ipaddress.summarize_address_range(y['start'],
            y['end']) for y in x] for x in ranges]
    LOG.debug(objs)
    #TODO: finish this


if __name__ == "__main__":
    sys.exit(main())