#!/bin/sh
rm -f instance/CA/lib/* 
cd instance/CA/
cd ekpub
ls | grep -v README | xargs rm
cd ../../..
