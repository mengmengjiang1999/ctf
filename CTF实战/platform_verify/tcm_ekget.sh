#!/bin/sh

pkill -9 envset_proc
sleep 1

sh run_cubetcm.sh exec_def/_CA.def &

sh run_cubetcm.sh exec_def/_ekget.def

sleep 10

pkill envset_proc
