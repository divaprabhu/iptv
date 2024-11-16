#!/bin/sh

# 0 */3 * * * cd /home/dvp/iptv && sh create_m3u.sh >> /tmp/m3u.log
# python -m http.server --directory /tmp

python create_m3u.py
