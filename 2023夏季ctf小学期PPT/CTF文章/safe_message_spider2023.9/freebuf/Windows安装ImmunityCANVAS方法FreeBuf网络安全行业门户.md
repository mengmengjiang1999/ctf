## 一：百度云地址

Immunity Canvas 7.26.zip 链接：https://pan.baidu.com/s/1fo1lRxJ2buVeg_OJeokcSQ
提取码：r6sk

## 二：安装

### windows

下载好之后，打开canvas.bat

![1614847395_60409da3b6eebd34c5f0b.png!small?1614847395461](https://image.3001.net/images/20210304/1614847395_60409da3b6eebd34c5f0b.png!small?1614847395461)

执行后发现，需要图中的一些python模块，我又是一个懒人，就就就重新安装了以下canvas。

![1614847420_60409dbc6134260841c2e.png!small?1614847420095](https://image.3001.net/images/20210304/1614847420_60409dbc6134260841c2e.png!small?1614847420095)

<http://www.immunityinc.com/canvas-dependencies.shtml>

![1614847744_60409f00908a032cc8a3b.png!small?1614847744525](https://image.3001.net/images/20210304/1614847744_60409f00908a032cc8a3b.png!small?1614847744525)

![1614847823_60409f4fd5663652e5ec5.png!small?1614847823328](https://image.3001.net/images/20210304/1614847823_60409f4fd5663652e5ec5.png!small?1614847823328)

![1614848238_6040a0ee68269db11c9de.png!small?1614848237985](https://image.3001.net/images/20210304/1614848238_6040a0ee68269db11c9de.png!small?1614848237985)

  

canvas.bat

![1614848098_6040a0627bf8b3fa46bd6.png!small?1614848098002](https://image.3001.net/images/20210304/1614848098_6040a0627bf8b3fa46bd6.png!small?1614848098002)

    
    
      
    

@echo off  
setlocal enableextensions enabledelayedexpansion  
rem This is a little CANVAS loader.  
rem Copyright Immunity, Inc.

rem YOU CANNOT USE -OO because that strips doc strings, and  
rem we need docstrings to do our MOSDEF compile!

rem This weird command cd's to the current directory of the batch script  
pushd %~dp0

rem Find what version of python is available, we use the highest available.  
IF exist C:\python27\python.exe (  
## C:\python27\python.exe 为python的安装目录的python  
echo "Using Python 2.7 .bat setup...."  
PATH=C:\python27\DLLs;C:\python27\;!PATH!  
## C:\python27\DLLs为python的安装目录的dlls文件  
## C:\python27为python的安装目录  
## 是注释，方便新手观看  
python.exe -W ignore E:\Canvas\runcanvas.py  
## E:\Canvas\runcanvas.py 是e盘下的canvas的runcanvas.py这个文件，你下载好Canvas 7.26.zip
解压后的地址  
##与我的不一样，建议这里认真看  
) ELSE (  
echo "Python 2.7 could not be found and it is required for CANVAS. Please
update to Python 2.7."  
echo "You can find an archive with all Windows dependencies at:
https://www.immunityinc.com/canvas-dependencies.shtml"  
)

![1614848273_6040a11140a672593c937.png!small?1614848273053](https://image.3001.net/images/20210304/1614848273_6040a11140a672593c937.png!small?1614848273053)

如果一直是这样的话，建议ctrl+c。

![1614848308_6040a1344fd63bafe9cd9.png!small?1614848307994](https://image.3001.net/images/20210304/1614848308_6040a1344fd63bafe9cd9.png!small?1614848307994)

### linux

安装方法

    
    
    Pre Requests for installing Canvas: (tested setup) Ubuntu 18.04 (updated but not upgraded)
    Copy Canvas.zip to Linux PC
    Unzip it to working folder.
    
    Run command as root:
    sudo apt-get update
    sudo apt-get -y install python-pip
    sudo apt-get -y install gtk2.0
    sudo apt-get -y install python-glade2
    sudo apt-get -y install python-nacl python-bcrypt
    sudo pip install pycrypto
    sudo pip install pyasn1
    sudo pip install diskcache==4.1.0
    sudo pip install asn1tools
    sudo apt-get install -y python-pycurl
    sudo apt-get install -y libcanberra-gtk-module
    sudo pip install pycurl
    sudo pip install requests
    sudo pip install pygame
    
    Go to CANVAS folder, then run:
    sudo bash CANVAS/installer/linux_installer.sh
    
    Setup is finished
    Executing: 
    sudo python CANVAS/runcanvas.py
    
    You are breathtaking!

## 官方文档

<https://www.immunityinc.com/products/canvas/tutorials.html>

期待师傅们的使用教程~·

