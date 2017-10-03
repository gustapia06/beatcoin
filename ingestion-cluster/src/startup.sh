#!/bin/bash

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install python3-pip
sudo pip3 install kafka-python
sudo pip3 install websocket-client
