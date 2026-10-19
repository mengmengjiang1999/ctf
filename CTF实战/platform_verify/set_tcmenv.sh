#!/bin/bash
export CUBEAPPPATH=$(pwd) 
export CUBE_TCM_PATH=/root/centoscloud/cube-tcm
export CUBE_TCM_PLUGIN=/root/centoscloud/cube_tcmplugin
export CUBE_APP_PLUGIN=$CUBE_TCM_PLUGIN/plugin:$CUBEAPPPATH/plugin/:$CUBE_APP_PLUGIN
export CUBE_DEFINE_PATH=$CUBEAPPPATH/define:$CUBE_DEFINE_PATH:$CUBE_TCM_PATH/define:$CUBE_TCM_PLUGIN/define
export LD_LIBRARY_PATH=$CUBE_PATH/cubelib/lib/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$CUBEAPPPATH/locallib/bin/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$CUBE_TCM_PATH/locallib/bin/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$CUBE_TCM_PLUGIN/locallib/bin/:$LD_LIBRARY_PATH
:
