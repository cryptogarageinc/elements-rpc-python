# elements-rpc-python

## install

### for windows bat

1. double click `0_install.bat`

### for pipenv

1. pip install --user pipenv
2. pipenv install

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
      "wallet": "(wallet name)"
    }
  }
  ```

### getnewaddress

#### for windows

1. double click `1_getnewaddress.bat`

#### for pipenv

1. pipenv run getnewaddress

### listunspent

#### for windows

1. double click `2_listunspent.bat`

#### for pipenv

1. pipenv run listunspent

### sign

#### for windows

```
1. drag transaction file
2. drop file to `3_sign_tx.bat`
```

Alternative:
```
1. rename transation file to `sign_tx.txt`
2. double click `3_sign_tx.bat`
```

#### for pipenv

1. pipenv run sign -i `filePath`
