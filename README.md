# toolscape

[Bashmator](https://github.com/vinzekatze/bashmator) Library for __Kali Linux__.

## Installation

Download and add library:

```
git clone https://github.com/Kraus17th/toolscape
bshm library add toolscape
bshm library use toolscape
```

Add shells, if not added, rescan the library:
```
bshm shell add /usr/bin/bash
bshm shell add /usr/bin/python3
bshm library scan -f
```

Install dependencies
```
bshm use install --item 1-7
```

After installation, it is recommended to re-login

## Update
Pull from github repository
```
bshm use pull
```

Push to github repository
```
bshm use push
```
