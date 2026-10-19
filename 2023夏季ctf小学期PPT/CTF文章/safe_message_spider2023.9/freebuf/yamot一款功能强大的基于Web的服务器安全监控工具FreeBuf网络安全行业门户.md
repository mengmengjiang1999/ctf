![](https://image.3001.net/images/20230828/1693231919_64ecab2f6304519a912e4.jpg!small)

## 关于yamot

yamot是一款功能强大的基于Web的服务器安全监控工具，专为只有少量服务器的小型环境构建。yamot只会占用非常少的资源，并且几乎可以在任何设备上运行。该工具适用于Linux或BSD，当前版本暂不支持Windows平台。

比如说，广大研究人员可以使用yamot来监控在家运行的Raspberry
Pi服务器。它只需要几个配置步骤，然后就可以在浏览器中显示许多相关的服务器测量数据：

> 1、系统负载
>
> 2、内存使用情况
>
> 3、正常运行时间/启动时间
>
> 4、用量（已计算）
>
> 5、电池（例如用于监控移动设备）
>
> 6、WiFi信号强度
>
> 7、温度
>
> 8、处理器（核心、速度、使用量…）
>
> 9、系统（发行版、版本、体系结构等）
>
> 10、网络服务（开放侦听端口）
>
> 11、网络设备和地址
>
> 12、网络接口IO（发送/接收的字节）
>
> 13、磁盘存储使用情况（已用空间和总空间）
>
> 14、磁盘设备IO（读取/写入字节）
>
> 15、已登录的用户（用户名、登录日期…）

需要注意的是，上述所有的信息都将实时显示在一个页面上，以提供一个简单的概述查阅。

## 工具架构

该工具主要由服务器、控制器和客户端这三个组件组成，其运行流程和架构如下图所示：

![](https://image.3001.net/images/20230828/1693231939_64ecab4312d01fd35c221.png!small)

## 工具下载

由于该工具基于Python 3开发，因此我们首先在本地设备上安装并配置好Python 3环境。接下来，广大研究人员需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/knrdl/yamot.git

## 工具安装

### 服务器

1、安装好Python 3之后，执行下列命令安装psutil和ujson：

    
    
    sudo apt-get install python3-psutil python3-ujson

2、将yamot_server.py文件拷贝到你的服务器中（例如/opt/yamot），让后使用sudo -u将其添加到/etc/rc.local：

    
    
    dash -c 'cd /opt/yamot && python3 /opt/yamot/yamot_server.py' &

3、使用下列命令运行服务器，并生成一个配置文件。

4、如果你的服务器运行了防火墙，请设置好端口并允许通过（默认端口为9393）：

    
    
    sudo ufw allow 9393

### 客户端&控制器

5、控制器组件需要在你网络中的服务器上运行，负责运行控制器的服务器同时也需要运行服务器组件，这里可以使用controller/dist目录中的内容。

6、你需要安装好Node.JS以及Express.js。

7、使用下列命令开启控制器：

    
    
    node controller.js

8、控制器启动之后，Shell将会提供登录凭证。

9、现在，你就可以将工具脚本添加到自启菜单中了，如果你使用了防火墙，别忘了打开相应端口。

10、打开浏览器，并访问下列地址即可开始使用yamot：

    
    
    http://ip-of-the-controller-device:8080

## 工具使用截图

![](https://image.3001.net/images/20230828/1693231997_64ecab7d4a9d4b95ecedf.png!small)![](https://image.3001.net/images/20230828/1693232003_64ecab83c97eec67f75c8.png!small)

![](https://image.3001.net/images/20230828/1693232011_64ecab8bc04a87376c7b8.png!small)

![](https://image.3001.net/images/20230828/1693232018_64ecab92867fac53ffb09.png!small)

![](https://image.3001.net/images/20230828/1693232025_64ecab990dce88d06672b.png!small)

![](https://image.3001.net/images/20230828/1693232032_64ecaba06988a4a5c5a71.png!small)

![](https://image.3001.net/images/20230828/1693232039_64ecaba7c772aac0ead9c.png!small)

![](https://image.3001.net/images/20230828/1693232046_64ecabae00ab6353f764d.png!small)

![](https://image.3001.net/images/20230828/1693232053_64ecabb55e2990b10b6f3.png!small)

  

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/knrdl/yamot/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **yamot** ：【[ _GitHub传送门_](https://github.com/knrdl/yamot)】

## 参考资料

> [ _https://www.nagios.org/_](https://www.nagios.org/)

