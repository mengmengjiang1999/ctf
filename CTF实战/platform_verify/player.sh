#!/bin/sh
pkill -9 envset_proc
sleep 1
cd instance/player
./main_proc start.msg
cd -

