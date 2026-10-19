# **0x00简介**

abbix是一个基于WEB界面的提供分布式系统监视以及网络监视功能的企业级的开源解决方案。zabbix能监视各种网络参数，保证服务器系统的安全运营；并提供灵活的通知机制以让系统管理员快速定位/解决存在的各种问题。zabbix由2部分构成，zabbix
server与可选组件zabbix agent。zabbix server可以通过SNMP，zabbix
agent，ping，端口监视等方法提供对远程服务器/网络状态的监视，数据收集等功能，它可以运行在Linux，Solaris，HP-UX，AIX，Free
BSD，Open BSD，OS X等平台上。

#  **0x01漏洞概述**

Zabbix Server的trapper命令处理，存在命令注入漏洞，可导致远程代码执行。

#  **0x02影响版本**

Zabbix 3.0.x~3.0.30

#  **0x03环境搭建**

1、本次漏洞环境手动搭建较为复杂，这里使用vulhub环境搭建，下载

git clone https://github.com/vulhub/vulhub.git

2、进入漏洞目录，使用docker-compose启动一个完整的Zabbix环境，包含Web端、Server端、1个Agent和Mysql数据库

cd vulhub-master/zabbix/CVE-2020-11800

docker-compose up -d

![1615185896_6045c7e8db09e452ec0fb.png!small](https://image.3001.net/images/20210308/1615185896_6045c7e8db09e452ec0fb.png!small)

3、使用docker ps 查看是否都启动成功没有就在执行docker-compose up -d

启动成功在浏览器访问http://your-ip:8080

![1615185903_6045c7ef8ec5cf302d6ef.png!small](https://image.3001.net/images/20210308/1615185903_6045c7ef8ec5cf302d6ef.png!small)

#  **0x0** **4** **漏洞复现**

1、利用该漏洞需要服务端开启了自动注册功能，使用账号密码admin/zabbix登录后台

进入Configuration->Actions，将Event source调整为Auto registration，然后点击Create
action，创建一个Action，名字随意

![1615185906_6045c7f2772825aabd2df.png!small](https://image.3001.net/images/20210308/1615185906_6045c7f2772825aabd2df.png!small)

![1615185908_6045c7f4e148422573fae.png!small](https://image.3001.net/images/20210308/1615185908_6045c7f4e148422573fae.png!small)

2、然后点击Operation，创建一个Operation，type为“Add Host”：然后保存

![1615185912_6045c7f809face0f09114.png!small](https://image.3001.net/images/20210308/1615185912_6045c7f809face0f09114.png!small)

3、这样就开启了自动注册功能

![1615185914_6045c7fa4b4988542738b.png!small](https://image.3001.net/images/20210308/1615185914_6045c7fa4b4988542738b.png!small)

4、在下载的vulhub中漏洞目录有漏洞利用脚本，查看poc可以看到执行的是写入文件的操作，使用python3执行poc，进入docker中查看写入成功

python3 exploit.py 172.16.1.147

![1615185916_6045c7fcab8f46f26a0a8.png!small](https://image.3001.net/images/20210308/1615185916_6045c7fcab8f46f26a0a8.png!small)

![1615185918_6045c7feab9f4f3a71ab3.png!small](https://image.3001.net/images/20210308/1615185918_6045c7feab9f4f3a71ab3.png!small)

#  **0x05修复建议**

1、建议升级至最新版本

