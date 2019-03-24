# CMSysBot (Telegram bot)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/84f263db2a964e39a24a352772e9c8aa)](https://app.codacy.com/app/Dibad/cmsysbot-telegram?utm_source=github.com&utm_medium=referral&utm_content=oddworldng/cmsysbot-telegram&utm_campaign=Badge_Grade_Settings)
[![Documentation Status](https://readthedocs.org/projects/cmsysbot-telegram/badge/?version=latest)](https://cmsysbot-telegram.readthedocs.io/en/latest/?badge=latest)

## Description

Centralized Management for Systems Administration (CMSysBot) it is a Telegram bot that allows you to manage computers in a local network from the bot itself, for example, execute a series of commands on all computers automatically, or perform updates and collect information from computers, all in a centralized way.

## Python3 libraries

* [python-telegram-bot](https://pypi.org/project/python-telegram-bot/)
* [paramiko](https://pypi.org/project/paramiko/)
* [wakeonlan](https://pypi.org/project/wakeonlan/)

## System dependencies

* [sshpass](https://linux.die.net/man/1/sshpass)

## How to install

First of all, you need a server with any GNU/Linux distribution, we have tested this bot on a Debian based operating system.

Once you have installed your server operating system, you have to download the bot from GitHub, install Python3 libraries and system dependencies:


#### Download bot

```
git clone https://github.com/oddworldng/cmsysbot-telegram.git
```

#### Install Python3 libraries

Go into cloned folder `cmsysbot-telegram` and execute: 

```
make install
```

#### Install system dependencies

```
sudo apt install -y sshpass
```

## How to run (server)

To run this bot in your server, go to your git cloned folder `cmsysbot-telegram` (by default) and execute this command:

```
make run
```

## How to configure

First of all, you have to create a new Telegram bot using [BotFather](https://telegram.me/BotFather) bot and get the bot `token`.

Once you've got it, copy your bot token into `config/config.json` file, in `token` filed.

Make sure to fill up all fields in the `config/config.json` file.

## How to run (client)

That's all! now you can open your Telegram client and get into your created bot `@YourTelegramBot` and start to use it.

## Social media

* Blog: [CMSysBot](https://cmsysbot.wordpress.com/) 
* Twitter: [@CMSysBot](https://twitter.com/cmsysbot)

## Authors
* **Andrés Nacimiento García**, computer engineer at [University of La Laguna](https://ull.es/).
* **David Afonso Dorta**, computer engineer at [University of La Laguna](https://ull.es/).
