#!/bin/sh

pkill -9 envset_proc
sleep 1

sh run_cubetcm.sh exec_def/_CA.def &
sleep 1
sh run_cubetcm.sh exec_def/_crypt_hub.def &

sleep 1
sh run_cubetcm.sh exec_def/_crypt_user.def &

sleep 1
sh run_cube.sh exec_def/_login_server.def &

sleep 1
sh run_cube.sh exec_def/_login_term.def &

sleep 1
sh run_cube.sh exec_def/_login_user.def  login.msg ctrl_exit.msg

#sleep 1
#sh run_cube.sh exec_def/_login_user.def  keyset_send.msg ctrl_exit.msg
