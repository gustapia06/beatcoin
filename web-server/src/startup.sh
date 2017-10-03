#!/bin/bash

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get install python3-pip
sudo pip3 install redis
sudo pip3 install cassandra-driver
sudo pip3 install flask
sudo pip3 install tornado
