# elements-rpc-python

## install

 - for windows bat
   1. double click `0_install.bat`

 - for python
   ```
    1. pip install --user python-bitcoinrpc
   ```

 - for pipenv
   ```
    1. pip install --user pipenv
    2. pipenv install
   ```

## usage

### create configuration file

create configuration file on first.

- configuration file (setting.json)
  ```
  {
    "elements": {
      "host": "(server address)",
      "port": "(server port)",
      "username": "(server user id)",
      "password": "(server password)",
      "wallet": "(wallet name)",
      "passphrase": "(wallet passphrase)"
    },
    "assets": {
      "JPY": "(JPY asset id)"
    }
  }
  ```

- configuration
  - elements: Settings for connecting to elements RPC server.
    - host: host name or ip address.
    - port: RPC port
    - username: authentication username
    - password: authentication password
    - wallet: (If you are using multiple wallet) wallet name.
    - passphrase: wallet passphrase. (for unlock_wallet)
  - assets: default asset id. (and label mapping)
    - JPY: JPY asset id.

### support command


  - usage of python
    ```
    (lock wallet)
    python3 elements-rpc.py lock_wallet

    (lock wallet)
    python3 elements-rpc.py lock_wallet

    (unlock wallet)
    python3 elements-rpc.py unlock_wallet [-p (passphrase)]

    (change wallet passphrase)
    python3 elements-rpc.py change_wallet_passphrase -p (current passphrase) -n (new passphrase)

    (get address)
    python3 elements-rpc.py get_address -l (label name)

    (list addresses)
    python3 elements-rpc.py list_addresses -l (label name)

    (get balance)
    python3 elements-rpc.py get_balance [-a (asset name)]

    (listunspent)
    python3 elements-rpc.py listunspent -a (asset name) -o (output file name)

    (sign)
    python3 elements-rpc.py sign -i (input tx file) -o (output signed tx file name)

    (send transaction)
    python3 elements-rpc.py send --address (send address) -a (asset) -v (amount(sat))
    ```

  - usage of pipenv
    ```
    (lock wallet)
    pipenv run lock_wallet

    (unlock wallet)
    pipenv run unlock_wallet [-p (passphrase)]

    (change wallet passphrase)
    pipenv run change_wallet_passphrase -p (current passphrase) -n (new passphrase)

    (get address)
    pipenv run get_address -l (label name)

    (list addresses)
    pipenv run list_addresses -l (label name)

    (get balance)
    pipenv run get_balance [-a (asset name)]

    (listunspent)
    pipenv run listunspent -a (asset name) [-o (output file name)]

    (sign)
    pipenv run sign -i (input tx file) [-o (output signed tx file name)]

    (send transaction)
    pipenv run send --address (send address) -a (asset) -v (amount(sat))
    ```


### usage of windows bat file

Parameter is set to default value.

  - lock wallet
    1. double click `99_lock_wallet.bat`

  - unlock wallet
    1. double click `98_unlock_wallet.bat`

  - get address
    1. double click `1_get_address_jpy.bat`

  - list addresses
    1. double click `2_list_addresses_jpy.bat`

  - get balance
    1. double click `3_get_balance.bat`

  - listunspent (JPY asset)
    1. double click `4_listunspent_jpy.bat`
    2. view `listunspent-jpy.json`

  - sign
    1. drag transaction file
    2. drop file to `3_sign_tx.bat`
    3. view `sign_tx.txt`

    Alternative:
    1. rename transaction file to `sign_tx.txt`
    2. double click `3_sign_tx.bat`
    3. view `sign_tx.txt`
