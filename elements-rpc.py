#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
from bitcoinrpc.authproxy import AuthServiceProxy
from decimal import Decimal


MIN_SUPPORTED_ELEMENTS_VERSION = 170001  # 0.17.0.1
LISTUNSPENT_MAX = 9999999
COINBASE = 100000000
ASSET_LBTC = '6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d'


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

    def listlabels(self):
        return self.rpc_connection.listlabels()

    def getaddressesbylabel(self, label):
        addresses = self.rpc_connection.getaddressesbylabel(label)
        addr_list = []
        if addresses:
            for addr in addresses.keys():
                addr_list.append(addr)
        return addr_list

    def getbalance(self, asset):
        if asset:
            balance = self.rpc_connection.getbalance('*', 0, False, asset)
            balance_map = {asset: balance}
        else:
            balance_map = self.rpc_connection.getbalance()
        return balance_map

    def dumpassetlabels(self):
        return self.rpc_connection.dumpassetlabels()

    def sendtoaddress(self, address, amount, asset):
        return self.rpc_connection.sendtoaddress(
            address, amount, '', '', False, False, 1, 'UNSET', asset)

    def walletpassphrase(self, passphrase, timeout):
        return self.rpc_connection.walletpassphrase(passphrase, timeout)

    def walletpassphrasechange(self, passphrase, new_passphrase):
        return self.rpc_connection.walletpassphrasechange(
            passphrase, new_passphrase)

    def encryptwallet(self, passphrase):
        return self.rpc_connection.encryptwallet(passphrase)

    def walletlock(self):
        return self.rpc_connection.walletlock()

    def getnetworkinfo(self):
        return self.rpc_connection.getnetworkinfo()

    def check_version(self):
        node_version = int(self.getnetworkinfo().get('version', 0))
        if node_version < MIN_SUPPORTED_ELEMENTS_VERSION:
            logging.error(
                'Node version ({node_version:06}) not supported ' +
                f'(min: {MIN_SUPPORTED_ELEMENTS_VERSION:06})')
            sys.exit(1)


def convert_btc(amount):
    amount_str = str(amount)
    if len(amount_str) > 8:
        num = len(amount_str) - 8
        amount_str = amount_str[:num] + '.' + amount_str[num:]
    else:
        num = 8 - len(amount_str)
        amount_str = '0.' + ('0' * num) + amount_str
    return float(amount_str)


def get_btc_asset(config):
    return config.get('assets', {}).get('bitcoin', ASSET_LBTC)


def create_asset_label_map(rpc, config, full_get=False):
    label_map = config.get('assets', {})
    if not label_map:
        label_map = rpc.dumpassetlabels()
    elif full_get:
        asset_list = rpc.dumpassetlabels()
        label_map.update(asset_list)
    if 'bitcoin' not in label_map:
        label_map['bitcoin'] = ASSET_LBTC
    return label_map


def create_asset_map(rpc, config, full_get=False):
    label_map = create_asset_label_map(rpc, config, full_get)
    value_map = {}
    for label, asset in label_map.items():
        value_map[asset] = label
    return label_map, value_map


def get_passphrase(config, passphrase):
    result = config.get('elements', {}).get('passphrase', '')
    return result if result else passphrase


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

    parser_unlock = subparsers.add_parser(
        'unlock_wallet', help='unlock_wallet help')
    parser_unlock.add_argument('-p', '--passphrase', default='',
                               help='passphrase', required=False)

    subparsers.add_parser('lock_wallet', help='lock_wallet help')

    parser_chg_pass = subparsers.add_parser(
        'change_wallet_passphrase', help='change_wallet_passphrase help')
    parser_chg_pass.add_argument('-p', '--passphrase', default='',
                                 help='old passphrase', required=False)
    parser_chg_pass.add_argument('-n', '--new-passphrase',
                                 help='new passphrase', required=True)

    parser_addr = subparsers.add_parser(
        'get_address', help='get_address help')
    parser_addr.add_argument('-l', '--label', default='',
                             help='Address label', required=False)
    parser_addr.add_argument('-t', '--address-type', default='bech32',
                             help='Address type', required=False)
    parser_addr.add_argument('-o', '--output-file', default='',
                             help='output file name', required=False)

    parser_list_addresses = subparsers.add_parser(
        'list_addresses', help='list_addresses help')
    parser_list_addresses.add_argument('-l', '--label', default=None,
                                       help='Address label', required=False)

    parser_get_balance = subparsers.add_parser(
        'get_balance', help='get_balance help')
    parser_get_balance.add_argument('-a', '--asset', default='',
                                    help='target asset', required=False)

    parser_list = subparsers.add_parser('listunspent', help='listunspent help')
    parser_list.add_argument('-a', '--asset', default='',
                             help='target asset', required=False)
    parser_list.add_argument('-o', '--output-file', default='listunspent.json',
                             help='output file name', required=False)

    parser_send = subparsers.add_parser('send', help='send help')
    parser_send.add_argument('-i', '--address',
                             help='send address', required=True)
    parser_send.add_argument('-a', '--asset',
                             help='target asset', required=True)
    parser_send.add_argument('-v', '--value',
                             help='send value (sat)', required=True)
    parser_send.add_argument('-o', '--output-file',
                             default='last_send_txid.txt',
                             help='output txid file name', required=False)

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

    if args.command == 'get_address':
        address = rpc.getnewaddress(args.label, args.address_type)
        print(f'Confidential address: {address}')

        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(address)
                print(f'output: {args.output_file}')

    elif args.command == 'list_addresses':
        if args.label is None:
            labels = rpc.listlabels()
        else:
            labels = [args.label]

        for label in labels:
            addresses = rpc.getaddressesbylabel(label)
            print(f'label: {label}')
            if len(addresses) > 1:
                print('addresses:')
                for address in addresses:
                    print(f'- {address}')
            elif len(addresses) == 1:
                addr = addresses[0]
                print(f'address: {addr}')
            print('\n')

    elif args.command == 'get_balance':
        label_map, asset_map = create_asset_map(rpc, config, True)
        btc_asset = get_btc_asset(config)
        btc_label = label_map.get('bitcoin', 'bitcoin')

        bitcoin_assets = ['bitcoin', btc_asset, btc_label]
        target_assets = []
        asset = args.asset
        if not asset:
            pass
        if asset in bitcoin_assets:
            target_assets.append('bitcoin')
        else:
            target_assets.append(asset)
            if asset in label_map:
                target_assets.append(label_map.get(asset, asset))
            if asset in asset_map:
                target_assets.append(asset_map.get(asset, asset))

        def dump_balance(label, balance):
            if label in bitcoin_assets:
                print(f'{label}: {balance:.8f}')
            else:
                label = asset_map.get(label, label)
                amount = int(balance * COINBASE)
                print(f'{label}: {amount}')

        balance_map = rpc.getbalance('')
        if not asset:
            for label, balance in balance_map.items():
                dump_balance(label, balance)
        else:
            found = False
            for label, balance in balance_map.items():
                if label in target_assets:
                    found = True
                    dump_balance(label, balance)
            if not found:
                balance_map = rpc.getbalance(args.asset)
                for label, balance in balance_map.items():
                    dump_balance(label, balance)

    elif args.command == 'listunspent':
        def convert_to_json(obj):
            return float(obj) if isinstance(obj, Decimal) else obj

        asset_label_map, _ = create_asset_map(rpc, config, True)
        asset = args.asset
        if asset in asset_label_map:
            asset = asset_label_map.get(asset)

        unspent_list = rpc.listunspent()
        if args.asset:
            utxo_list = []
            for utxo in unspent_list:
                if utxo['asset'] == asset:
                    utxo_list.append(utxo)
            unspent_list = utxo_list
        utxo_count = len(unspent_list)
        print(f'listunspent count: {utxo_count}')
        json_str = json.dumps(unspent_list,
                              default=convert_to_json, indent=2)
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(json_str)
                print(f'output: {args.output_file}')
        else:
            print(json_str)

    elif args.command == 'send':
        if not args.address:
            logging.error(' empty address.')
            sys.exit(1)
        if not args.asset:
            logging.error(' empty asset.')
            sys.exit(1)
        label_map, asset_map = create_asset_map(rpc, config)
        btc_asset = get_btc_asset(config)
        is_btc = True if args.asset in ['bitcoin', btc_asset] else False

        asset = args.asset
        if is_btc or (asset in asset_map):
            pass
        elif asset in label_map:
            asset = label_map.get(asset)
        elif not asset:
            print('The asset is empty.')
            sys.exit(1)
        else:
            print(f'The {asset} asset is not defined on the config file.')
            sys.exit(1)

        if is_btc:
            amount = float(args.value)
        else:
            amount = convert_btc(int(args.value))
        if amount <= 0:
            logging.error(' empty send value.')
            sys.exit(1)

        txid = rpc.sendtoaddress(args.address, amount, asset)
        print(f'txid: {txid}')
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(txid)
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

    elif args.command == 'lock_wallet':
        rpc.walletlock()
        print('lock wallet.')

    elif args.command == 'unlock_wallet':
        if args.passphrase:
            passphrase = args.passphrase
        else:
            passphrase = get_passphrase(config, args.passphrase)
            if not passphrase:
                logging.error(' empty passphrase.')
                sys.exit(1)

        rpc.walletpassphrase(passphrase, (24 * 60 * 60))
        print('unlock wallet. (timeout: 1 day)')

    elif args.command == 'change_wallet_passphrase':
        if args.passphrase:
            rpc.walletpassphrasechange(args.passphrase, args.new_passphrase)
            print('change wallet passphrase.')
        else:
            rpc.encryptwallet(args.new_passphrase)
            print('wallet encrypt.')

    else:
        print(f'Unknown command: {args.command}')


if __name__ == '__main__':
    main()
