![CMSysBot banner](https://i.imgur.com/7Wr1jcj.jpg)

| Build | Coverage | Quality | Docs | License |
|:-------------------------------------------------------------------------------------------------------------------------------------------:|:-----------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------------------:|
| [![Build Status](https://travis-ci.org/oddworldng/cmsysbot-telegram.svg?branch=master)](https://travis-ci.org/oddworldng/cmsysbot-telegram) | [![Coverage Status](https://coveralls.io/repos/github/oddworldng/cmsysbot-telegram/badge.svg?branch=master)](https://coveralls.io/github/oddworldng/cmsysbot-telegram?branch=master) | [![Codacy Badge](https://api.codacy.com/project/badge/Grade/84f263db2a964e39a24a352772e9c8aa)](https://app.codacy.com/app/Dibad/cmsysbot-telegram?utm_source=github.com&utm_medium=referral&utm_content=oddworldng/cmsysbot-telegram&utm_campaign=Badge_Grade_Settings) | [![Documentation Status](https://readthedocs.org/projects/cmsysbot-telegram/badge/?version=latest)](https://cmsysbot-telegram.readthedocs.io/en/latest/?badge=latest) | [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) |

## Table of contents
* [Description](#description)
* [Documentation](#documentation)
* [Contributing](#contributing)
* [Installing](#installing)
  * [Dependencies](#dependencies)
  * [Instalation guide](#installation-guide)
* [Getting started](#getting-started)
  * [Server](#server)
  * [Client](#client)
* [Social media](#social-media)
* [Authors](#authors)

## Description

__Centralized Management for Systems Administration__ (CMSysBot) it is a Telegram bot that allows you to __manage__ computers in a __local network__ from the bot itself, automating tasks like, for example, executing a series of commands on all computers, or performing updates and collecting information. All in a centralized way.

Also, the bot is easily __extensible__ by adding __plugins__ (bash scripts), so any action that could be performed on a single computer can be easily replicated to the whole local network by using the bot.

## Documentation

`cmsysbot-telegram`'s documentation lives at [readthedocs.io](https://cmsysbot-telegram.readthedocs.io)

## Contributing

Contributions to the project are really appreciated! Please, refer to the [contribution guide](https://github.com/oddworldng/cmsysbot-telegram/blob/master/CONTRIBUTING.md) and [code of conduct](https://github.com/oddworldng/cmsysbot-telegram/blob/master/CONTRIBUTING.md) before contributing.

## Installing

### Dependencies

__NOTE:__ This bot only works with __Python 3.6 or greater__

#### Python3 libraries

* [python-telegram-bot](https://pypi.org/project/python-telegram-bot/)
* [paramiko](https://pypi.org/project/paramiko/)

### Installation guide

First of all, you need a __server__ with any _GNU/Linux distribution_, we have tested this bot on a Debian based operating system.

Once you have installed the server operating system, you have to get the bot from __GitHub__, install `python3` libraries and system dependencies:

#### Download the bot

```console
git clone https://github.com/oddworldng/cmsysbot-telegram.git
```

#### Install Python3 libraries

Go into cloned folder `cmsysbot-telegram` and execute:

```console
make install
```

#### Install system dependencies

```console
sudo apt install -y sshpass
```

## Getting started

### Server

#### How to run

To run this bot in your server, go to your git cloned folder `cmsysbot-telegram` (by default) and execute this command:

```console
make run
```

#### How to configure

First of all, you have to create a new Telegram bot using [BotFather](https://telegram.me/BotFather) bot and get the bot `token`.

Once you've got it, copy your bot token into `config/config.json` file, in `token` filed.

Make sure to fill up all fields in the `config/config.json` file.

### Client

#### How to run

That's all! Now you can open your Telegram client and start a chat with your new bot `@YourTelegramBot` to use it.

## Social media

* Blog: [CMSysBot](https://cmsysbot.wordpress.com/)
* Twitter: [@CMSysBot](https://twitter.com/cmsysbot)

## Authors

* **Andrés Nacimiento García**, computer engineer at [University of La Laguna](https://ull.es/).
* **David Afonso Dorta**, computer engineer at [University of La Laguna](https://ull.es/).
