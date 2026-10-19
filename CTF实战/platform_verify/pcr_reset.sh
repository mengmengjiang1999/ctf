#!/bin/sh

pkill -9 envset_proc

sh run_cubetcm.sh exec_def/_pcr_set.def pcr_reset.msg ctrl_exit.msg

sleep 1

sh run_cubetcm.sh exec_def/_pcr_set.def policy_write.msg ctrl_exit.msg
sleep 1

sh run_cubetcm.sh exec_def/_pcr_set.def policy_write1.msg ctrl_exit.msg
sleep 1

sh run_cubetcm.sh exec_def/_pcr_set.def policy_write3.msg ctrl_exit.msg
