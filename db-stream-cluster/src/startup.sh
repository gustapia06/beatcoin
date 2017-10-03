#!/bin/bash

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install python3-pip
sudo pip3 install redis
sudo apt-get -y install make gcc

mkdir Downloads
wget http://download.redis.io/redis-stable.tar.gz  -P ~/Downloads
sudo tar zxvf ~/Downloads/redis-* -C /usr/local
sudo mv /usr/local/redis-* /usr/local/redis
echo "export REDIS_HOME=/usr/local/redis" >> ~/.profile
echo "export PATH=$PATH:$REDIS_HOME/src" >> ~/.profile
source ~/.profile

cd $REDIS_HOME
sudo make distclean
sudo make
sudo $REDIS_HOME/src/redis-server $REDIS_HOME/redis.conf &
