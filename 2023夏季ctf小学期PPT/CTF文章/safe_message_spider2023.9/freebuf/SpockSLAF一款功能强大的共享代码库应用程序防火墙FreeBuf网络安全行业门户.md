![](https://image.3001.net/images/20220508/1651998518_62777f360b1e280c9f00d.png!small)

## 关于Spock SLAF

Spock SLAF是一款功能强大的共享代码库应用程序防火墙，简称为“SLAF”。该项目的主要目的是为了保护那些使用了[
_OpenSSL库_](https://www.openssl.org/docs/man1.1.1/man3/SSL_read.html)的服务或应用程序免受网络威胁的侵害。SLAF可以通过插入钩子来拦截所有的通信信息，以检测异常行为，并阻止和记录入侵行为，比如说缓冲区溢出、路径遍历、XSS和SQL注入等等。因此，为了检测异常，Spock
SLAF使用具有等级分数的确定性有限自动机来计算风险，并为每个上下文创建警报。

## 功能介绍

> 1、可以对SSL_read()输入缓冲区中的数据进行分析处理，并屏蔽、记录和检测安全可疑行为；
>
> 2、适用于任何使用了OpenSSL库的应用程序或服务；
>
> 3、如果在TLS上下文中检测到了异常行为，Spock
> SLAF将会存储异常行为的来源（IP地址）、日期和Payload，并将信息存储到“spock_agressors.log”日志文件中；

## 工具下载&部署&编译

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/CoolerVoid/spock_slaf

接下来，切换到项目目录中：

    
    
    $ cd CoolerVoid/spock_slaf

然后使用make命令编译项目代码：

    
    
    $ make clean; make

现在，我们将看到“bin”目录中会生成共享代码库“spock_slaf.so.1”。

## 工具使用

工具安装和配置完成之后，接下来就需要将生成的共享库注入到我们使用了OpenSSL的程序代码或服务代码中了，这一步可以通过下列通信上下文（服务器）来实现。

现在，使用[ _LD_ __PRELOAD_](https://catonmat.net/simple-ld-preload-tutorial)方法来将其注入到我们的服务代码中：

    
    
    $ LD_PRELOAD=/home/cooler/spock_slaf/bin/spock_slaf.so.1 bin/rest_server
    
    # note: change /home/cooler/spock_slaf/bin/ to your full path name

上述代码已经在一台Rest服务器中进行过测试。此时，如果任何人想要攻击rest_server的话，我们就会在“spock_agressors.log”日志文件中查看到完整的记录信息了。

## 工具使用提示

> 1、如果将SPOCK_SCORE宏设置为1-10之间的任何数字（值越大越敏感），这可以自定义分数等级以检测异常行为；
>
> 2、支持自定义需要屏蔽的Payload列表；
>
> 3、如果在源代码中将宏SPOCK_ONLY_HTTP设置为“1”，则可以在HTTP上下文中得到性能的提升；
>
> 4、如果在源代码中将宏SPOCK_BUGVIEW设置为“0”，则可以删除调试模式；

## 工具演示视频

 **视频地址：**[ _https://www.you*tube.com/watch?v=Lm3kpA-NZnE_](https://www.youtube.com/watch?v=Lm3kpA-NZnE)

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-3-Clause_](https://github.com/CoolerVoid/spock_slaf/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Spock SLAF：** 【[ _GitHub传送门_](https://github.com/CoolerVoid/spock_slaf)】

## 参考资料

> [
> _https://www.openssl.org/docs/man1.1.1/man3/SSL_read.html_](https://www.openssl.org/docs/man1.1.1/man3/SSL_read.html)
>
> [
> _https://www.linuxjournal.com/article/7795_](https://www.linuxjournal.com/article/7795)
>
> [ _https://www.kernel.org/doc/html/v4.16/userspace-> api/seccomp_filter.html_](https://www.kernel.org/doc/html/v4.16/userspace-> api/seccomp_filter.html)
>
> [ _https://man7.org/linux/man-> pages/man8/ld.so.8.html_](https://man7.org/linux/man-> pages/man8/ld.so.8.html)

