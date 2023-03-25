<p align="center">
    <h1 align="center">🎼 Partoche</h1>
    <p align="center">Terminal based pew pew map that feeds on <a href="https://github.com/bonjourmalware/melody">Melody logs</a></p>
</p>
<center>
    <img src="https://raw.githubusercontent.com/bonjourmalware/partoche/master/readme/partoche_demo.gif" height="350px" />
</center>

# Table of Contents
- [Usage](#usage)
- [Quickstart](#quickstart)
- [Requirements](#requirements)
  * [Asciiworld](#asciiworld)
  * [GeoIP](#geoip)
  * [IP Reputation file](#ip-reputation-file)
- [Log type](#log-type)
  * [Melody](#melody)
    + [`enrich.py` example](#-enrichpy--example)
  * [Elasticsearch](#elasticsearch)
- [Limitations](#limitations)
- [Reputation emojis](#reputation-emojis)

# Usage

`usage: partoche.py [-h|--help] (-D|--demo | -d|--data DATA) [-k|--kind {melody,elasticsearch}]`

# Quickstart
1) Check the [Requirements](#Requirements) section to make sure that everything is setup correctly
2) [OPTIONAL] Install virtual environment
   + `virtualenv ./venv --python=$(which python3)`
   + or `make venv`
3) Install requirements
   + `./venv/bin/pip install -r requirements.txt`
   + or `make reqs`
4) Copy the default config file
   + `cp config/config.sample.yml config/config.yml`
5) Run the program using the demo dataset
   + `./venv/bin/python partoche.py --demo`
   + or `make demo`

# Requirements
A few things are needed before starting Partoche for the first time.

## Asciiworld
Partoche uses `asciiworld` to generate the ascii map. It needs to be installed and in path before running the program. Refer to [these instructions](https://www.uninformativ.de/git/asciiworld/file/README.html) to install it. 

## GeoIP
Partoche uses the `GeoLite2-ASN` and `GeoLite2-City` MaxMind databases to gather coordinates for each hit. You need to pull them in the data/geoip folder before starting.

Refer to [MaxMind's documentation](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data?lang=en) to obtain them (it's free).

## IP Reputation file
A local IP reputation dataset can be build locally using multiple sources and used to enrich the logs data. IP reputation data adds emojis next to hit headers. 

# Log type
The `-k|--kind` flag is required to specify the kind of logs you're feeding Partoche with (default: melody). This is needed since the program can work using either an Elasticsearch live feed or flat melody log files.

## Melody
The program should work out of the box with Melody flat log files.

However, using an Elasticsearch live feed expects enriched logs through a Logstash setup that will add IP reputation data using the `listbot` database on the fly. 

The `enrich.py` script available at the project's root can be used to automatically add this data to the flat log files by updating each row based on an IP reputation database. This database should be updated regularly (ideally before each `enrich.py` run) by running the `data/listbost/listbot.sh` script, which will pull and build the database at `data/listbot/live/iprep.yaml`.

That the script must be started in the `data/listbot` directory. We recommend to use `make iprep` to build/update the database. 

Note that the updated version is saved on another file by default; you can use the `-i|--in-place` to update the log file directly.

### `enrich.py` example
+ Create an updated copy of the `melody.ndjson` file to `./parsed.ndjson`:
  + `./venv/bin/python enrich.py --data melody.ndjson`
+ Create an updated copy of the `melody.ndjson` file to `./custom_output.ndjson`:
  + `./venv/bin/python enrich.py --data melody.ndjson --out custom_output.ndjson`
+ Save the updated rows directly to `melody.ndjson`: 
  + `./venv/bin/python enrich.py --in-place --data melody.ndjson`

## Elasticsearch
The program can also feed from an Elasticsearch instance to which live Melody logs are sent. In this scenario, the `interval` specified in the `config/config.yml` file will be used to query the corresponding timerange. The collected data will be automatically refreshed for a continuous display.

Note that to use this mode, you must create an API access with access to the indexes handling Melody data and update the `config/config.yml` file accordingly.

# Limitations
Partoche has been developed and tested with Elasticsearch 7.x.

# Reputation emojis
These can be customized in the `config/config.yml` file.

Default:

```yml
reputation_emoji:
  "👹":
    - known attacker
    - bad reputation
  "🥸":
    - anonymizer
  "🤖":
    - bot
    - crawler
  "🔎":
    - mass scanner
  "₿":
    - bitcoin node
  "📨":
    - spam
    - form spammer
  "🧅":
    - tor exit node
  "🧟":
    - compromised

matches_emoji:
  "⚡":
    - cve

profile_emoji:
  "💣":
    - dropper

action_emoji:
  "🔑":
    - login
```
