![](https://image.3001.net/images/20230517/1684313629_6464961d247850ba78c1e.png!small)

## 关于Striker

Striker是一款功能强大的命令与控制C2工具，该项目目前仍处于积极开发阶段，大多数功能为试验性功能，并且随时会进行功能更新。广大研究人员可以使用Striker来实现各种命令控制功能。

## 功能介绍

### 代理

> 1、针对Linux和Windows主机的本地代理；
>
> 2、自包含的、最小化的Python代理；
>
> 3、HTTP(s)通信；
>
> 4、异步任务执行；
>
> 5、支持多个重定向程序；

### 后端/Teamserver

> 1、支持多个操作者；
>
> 2、大多数功能都是通过REST API向外暴露，因此很容易实现自动化任务执行；
>
> 3、使用Websocket实现更快速的网络通信；

### 用户接口

> 1、得益于Svelte和SocketIO，能够实现流畅的用户界面，且反应非常灵敏；
>
> 2、易于配置和使用，可以编译成静态HTML、JavaScript和CSS文件，即使是最基本的Web服务器也可以托管这些文件；
>
> 3、团队聊天功能，可以通过文本与其他操作者进行通信；

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/4g3nt47/Striker.git
    
    $ cd Striker

代码库被分为了以下四个独立部分：

> 1、C2服务器/后端
>
> 2、前端
>
> 3、C2重定向器
>
> 4、代理（植入物）

关于每一个部分的详细配置信息，请参考该项目的【[ _GitHub主页_](https://github.com/4g3nt47/Striker)】。

## 工具使用

工具的前端/WebUI托管在https://striker.debian.local，这是一个Nginx反向代理，用于将流量转发到托管了Web文件的HTTP服务器上（http://localhost:8000）：

    
    
    server {
    
        listen 443 ssl;
    
        server_name             striker.debian.local;
    
        ssl_certificate         /etc/ssl/certs/wildcard.debian.local.pem;
    
        ssl_certificate_key     /etc/ssl/private/wildcard.debian.local.key;
    
        access_log              /var/log/nginx/striker.debian.local;
    
     
    
        location / {
    
          proxy_pass              http://127.0.0.1:8000;
    
          proxy_redirect          off;
    
          proxy_read_timeout      90;
    
          proxy_set_header        Host $host;
    
          proxy_set_header        X-Real-IP $remote_addr;
    
          proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
    
        }
    
    }

C2服务器运行在https://localhost:3000。

目标主机是一个运行在Debian 10上的Docker容器（172.17.0.2）。

代理则是一个针对Linux构建的C代理，并且禁用了SSL验证功能。

操作者为admin（一个管理员账号）和guest（一个用户账号）。

## 工具使用截图

### 代理菜单1-10

![](https://image.3001.net/images/20230517/1684314300_646498bc26a978d2a183b.png!small)

![](https://image.3001.net/images/20230517/1684314310_646498c60ff8f27e9f202.png!small)![](https://image.3001.net/images/20230517/1684314319_646498cf7409e6eadabdf.png!small)![](https://image.3001.net/images/20230517/1684314328_646498d88b5787a4e80ed.png!small)![](https://image.3001.net/images/20230517/1684314337_646498e155b5ef369a3c8.png!small)![](https://image.3001.net/images/20230517/1684314349_646498ed76c5023094570.png!small)![](https://image.3001.net/images/20230517/1684314357_646498f58106516e15c13.png!small)![](https://image.3001.net/images/20230517/1684314366_646498fe01a1b981510fc.png!small)![](https://image.3001.net/images/20230517/1684314374_64649906d01703b81723e.png!small)![](https://image.3001.net/images/20230517/1684314383_6464990fd26b07094d2ff.png!small)

### 重定向器菜单11

![](https://image.3001.net/images/20230517/1684314391_6464991775be1044f54b8.png!small)

### 认证密钥菜单12-14

![](https://image.3001.net/images/20230517/1684314400_646499204e7f9a81e3a94.png!small)![](https://image.3001.net/images/20230517/1684314408_64649928a9e5b3a7cff31.png!small)

![](https://image.3001.net/images/20230517/1684314422_646499362dee447be0a6b.png!small)

### 团队聊天菜单15

![](https://image.3001.net/images/20230517/1684314431_6464993f9238bf7bc04e7.png!small)

### 用户菜单16-17

![](https://image.3001.net/images/20230517/1684314449_64649951dffbf9793e808.png!small)![](https://image.3001.net/images/20230517/1684314458_6464995a492974fcf8c27.png!small)

### 事件日志菜单18

![](https://image.3001.net/images/20230517/1684314468_646499640b659eeb026e7.png!small)

## 许可证协议

本项目的开发与发布遵循[GNU](https://github.com/4g3nt47/Striker/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Striker** ：【[ _GitHub传送门_](https://github.com/4g3nt47/Striker)】

## 参考资料

> [ _https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-> on-ubuntu-20-04_](https://www.digitalocean.com/community/tutorials/how-to-> install-mongodb-on-ubuntu-20-04)
>
> [ _https://www.freecodecamp.org/news/get-started-with-mongodb-> atlas/_](https://www.freecodecamp.org/news/get-started-with-mongodb-atlas/)

