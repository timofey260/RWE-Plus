RWE+ requires python 3.11 or higher

## Setting things up

to use RWE+ on linux we need python3 and virtual environment

most linux systems have python pre-installed or it can be installed with:

`$ sudo apt install python3`

next thing we need is download newest RWE+ [release](https://github.com/timofey260/RWE-Plus/releases/download/latest/RWE+.rar), unzip and open it in terminal

then virtual environment can be installed and created with:

```
$ sudo apt install python3-venv
$ python3 -m venv ./
```

All modules listed in requirements.txt and can be easily installed with:

`$ bin/pip3 install -r requirements.txt`

after that, the main.py can be opened with:

`$ . run.sh`