#! /bin/sh

kill -9 $(ps aux | grep '[p]ython3 main.py' | awk '{print $2}')

echo 'kill over'
