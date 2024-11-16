#!/bin/sh

# 0 */3 * * * cd /home/dvp/iptv && sh create_m3u.sh >> /tmp/m3u.log
#https://t.ly/hnO52

python create_m3u.py
rclone copy /tmp/list.m3u hotmail:
