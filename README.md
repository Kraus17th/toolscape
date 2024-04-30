# toolscape

[Bashmator](https://github.com/vinzekatze/bashmator) Library for __Kali Linux__. Fork of [ktz-autokali](https://github.com/vinzekatze/ktz-autokali).

## Установка

Скачать и добавить библиотеку:

```
git clone https://github.com/Kraus17th/toolscape
bshm library add toolscape
bshm library use toolscape
```

Добавить оболочки, если не добавлены, пересканировать библиотеку:
```
bshm shell add /usr/bin/bash
bshm shell add /usr/bin/python3
bshm library scan -f
```

Установить все необходимое:
```
bshm use install --item 1-7
```
После установки рекомендуется перелогиниться из-за docker

## Обновление

Pull from github repository
```
bshm use pull
```
