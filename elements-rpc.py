#!/usr/bin/env pyhton3

import argparse
import json
import logging
import os
import sys
from bitcoinrpc.authproxy import AuthServiceProxy
from decimal import Decimal


MIN_SUPPORTED_ELEMENTS_VERSION = 170001  # 0.17.0.1
LISTUNSPENT_MAX = 9999999


class RpcWrapper:
    def __init__(self, url='', config={}):
        if not url:
            elements_dic = config.get('elements', {})
            rpc_user = elements_dic.get('username', '')
            rpc_password = elements_dic.get('password', '')
            host = elements_dic.get('host', '127.0.0.1')
            port = elements_dic.get('port', 7041)
            path = ''
            wallet_name = elements_dic.get('wallet', '')
            if wallet_name:
                path = f'/wallet/{wallet_name}'
            self.rpc_connection = AuthServiceProxy(
                f'http://{rpc_user}:{rpc_password}@{host}:{port}{path}')
            if wallet_name:
                logging.debug(f'connect to {path}')
        else:
            self.rpc_connection = AuthServiceProxy(url)

    def command(self, command, *args):
        return self.rpc_connection.command(args)

    def get_rpc_client(self):
        return self.rpc_connection

    def listunspent(self, address_list=[]):
        return self.rpc_connection.listunspent(
            0, LISTUNSPENT_MAX, address_list)

    def signrawtransactionwithwallet(self, tx):
        return self.rpc_connection.signrawtransactionwithwallet(tx)

    def getnewaddress(self, label, address_type):
        return self.rpc_connection.getnewaddress(label, address_type)

    def getnetworkinfo(self):
        return self.rpc_connection.getnetworkinfo()

    def check_version(self):
        node_version = int(self.getnetworkinfo().get('version', 0))
        if node_version < MIN_SUPPORTED_ELEMENTS_VERSION:
            logging.error(
                'Node version ({node_version:06}) not supported ' +
                f'(min: {MIN_SUPPORTED_ELEMENTS_VERSION:06})')
            sys.exit(1)


def create_command():
    parser = argparse.ArgumentParser(
        description='Liquid Network Transaction Tool.')

    parser.add_argument('-d', '--debug',
                        default=False, type=bool, help='debug option.')
    parser.add_argument('-e', '--elements-url', default='',
                        help='Elements node URL. ' +
                        'eg http://id:pw@HOST:PORT/',
                        required=False)
    parser.add_argument('-c', '--config-file', default='setting.json',
                        help='configuration file.', required=False)

    subparsers = parser.add_subparsers(dest='command', help='sub-command help')
    parser_addr = subparsers.add_parser(
        'getnewaddress', help='getnewaddress help')
    parser_addr.add_argument('-l', '--label', default='JPYS',
                             help='Address label', required=False)
    parser_addr.add_argument('-t', '--address-type', default='bech32',
                             help='Address type', required=False)
    parser_addr.add_argument('-o', '--output-file', default='address.txt',
                             help='output file name', required=False)

    parser_list = subparsers.add_parser('listunspent', help='listunspent help')
    parser_list.add_argument('-o', '--output-file', default='listunspent.json',
                             help='output file name', required=False)

    parser_sign = subparsers.add_parser('sign', help='sign help')
    parser_sign.add_argument('-i', '--input-tx-file', default='sign_tx.txt',
                             help='tx file path', required=False)
    parser_sign.add_argument('-o', '--output-file', default='sign_tx.txt',
                             help='output file name', required=False)

    return parser


def main():
    parser = create_command()

    args = parser.parse_args()
    logging.root.setLevel(logging.DEBUG if args.debug else logging.INFO)

    config = {}
    try:
        if os.path.isfile(args.config_file):
            with open(args.config_file) as f:
                config = json.load(f)
    except Exception:
        pass

    rpc = RpcWrapper(url=args.elements_url, config=config)
    rpc.check_version()

    if args.command == 'getnewaddress':
        address = rpc.getnewaddress(args.label, args.address_type)
        print(f'address: {address}')

        with open(args.output_file, 'w') as f:
            f.write(address)
            print(f'output: {args.output_file}')

    elif args.command == 'listunspent':
        def convert_to_json(obj):
            return float(obj) if isinstance(obj, Decimal) else obj

        unspent_list = rpc.listunspent()
        json_str = json.dumps(unspent_list,
                              default=convert_to_json, indent=2)
        with open(args.output_file, 'w') as f:
            f.write(json_str)
            print(f'output: {args.output_file}')

    elif args.command == 'sign':
        path = args.input_tx_file
        if not os.path.isfile(path):
            logging.error(f' file not found: {path}')
            sys.exit(1)
        with open(path) as f:
            tx = f.read().replace(' ', '')
        logging.info(f'read file: {path}')
        bytes.fromhex(tx)
        signed_tx = rpc.signrawtransactionwithwallet(tx)
        output_path = args.output_file
        with open(output_path, 'w') as f:
            f.write(signed_tx['hex'])
            print(f'output tx file: {output_path}')

    else:
        print('Unknown command: {args.command}')


if __name__ == '__main__':
    main()
