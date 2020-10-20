# Playmobil Tele-Presence Car (TPTC)

In today's world, physical presence is increasingly becoming the exception. There are many free and affordable video conferencing tools to mitiage the need for communication. But unfortunately there are little to no affordable solutions for virtual presence in remote locations, that allow the remotee interaction with the physical world. This project trys to solve this dilemma, by providing an easy to install and setup remote tele-presence solution.

## General Idea

The general idea was to take an affordable RC car, apply some remote control ability via web technologies on it and use a phone plus generally available video conferencing tools for audio and video transmission.

A friend of mine gave the hint for using the Playmobil RC cars when he discovered that they have an open bluetooth interface.
The use for webinterface and websockets felt natural due to its easy setup and general 

## Technology

The current software was quickly assembled by smashing together these repositories: (Thanks to their contributors)
 * https://github.com/tmonjalo/playmobil-racer
 * https://github.com/mattmakai/python-websockets-example

## Setup

**Install**
```
sudo pip3 install -r requirements.txt
```

**Run**
```
sudo python3 app.py
```

**Expose local webserver publicly**
```
ssh -R 5000:localhost:5000 <server>
```

## Development

Current status is just a proof-of-concept and not ready for production.
