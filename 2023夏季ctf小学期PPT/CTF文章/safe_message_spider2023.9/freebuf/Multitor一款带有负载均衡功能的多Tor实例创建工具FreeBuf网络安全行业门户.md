![](https://image.3001.net/images/20230829/1693318658_64edfe02e51b2d21b3494.jpg!small)

## 关于Multitor

Multitor是一款带有负载均衡功能的多Tor实例创建工具，Multitor的主要目的是以最快的速度完成大量Tor进程的初始化，并将大量实例应用到我们日常使用的程序中，例如Web浏览器和聊天工具等等。除此之外，在该工具的帮助下，我们还可以在进行渗透测试和对基础设施安全性进行审计时提高隐蔽性和匿名性。

## 工具要求

Multitor需要使用到下列外部实用工具或代码库，请提前安装：

> [ _tor_](https://www.torproject.org/)
>
> [ _netcat_](http://netcat.sourceforge.net/)
>
> [ _haproxy_](https://www.haproxy.org/)
>
> [ _polipo_](https://www.irif.fr/~jch/software/polipo/)
>
> [ _privoxy_](https://www.privoxy.org/)
>
> [ _http-proxy-to-socks_](https://github.com/oyyd/http-proxy-to-socks)

## 支持的环境

> GNU/Linux（已在Debian和CentOS上进行过测试）
>
> [ _Bash_](https://www.gnu.org/software/bash/)（v4.4.19）

## 工具下载&安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/trimstray/multitor

然后切换到项目目录中，运行安装脚本即可：

    
    
    cd multitor
    
    ./setup.sh install

## 工具执行参数

    
    
    Usage:
    
        multitor <option|long-option>
    
     
    
     
    
     
    
      Options:
    
            --help                      显示工具帮助信息和退出
    
            --debug                   在屏幕上打印调试信息
    
            --verbose                  显示与Tor进程相关的更多信息
    
        -i, --init <num>                 初始化新的Tor进程
    
        -k, --kill                        终止所有Multitor进程
    
        -s, --show-id                   显示指定的Tor进程ID
    
        -n, --new-id                    重新生成Tor实例进程
    
        -u, --user <string>              设置用户
    
            --socks-port <port_num|all>   设置Socks端口号
    
            --control-port <port_num>     设置控制端口号
    
            --proxy <proxy_type>        设置Socks或HTTP代理服务器（polipo, privoxy, hpts）
    
            --haproxy                 将HAProxy设置为HTTP代理前端

## 工具运行样例

    
    
    multitor --init 2 --user debian-tor --socks-port 9000 --control-port 9900 --proxy privoxy --haproxy
    
    multitor --init 2 --user debian-tor --socks-port 9000 --control-port 9900
    
    multitor --init 10 --user debian-tor --socks-port 9000 --control-port 9900 --proxy socks
    
    multitor --show-id --socks-port 9000

## 工具输出样例

    
    
    multitor --init 5 -u debian-tor --socks-port 9000 --control-port 9900 --proxy privoxy
    
     
    
         Set processes: 5
    
               Created: 5
    
           Not created: 0
    
      Control password: TI24tO2k0E8f8jqoIr
    
     
    
           Proxy state: running (privoxy » haproxy » socks)

## 工具运行演示截图

![](https://image.3001.net/images/20230829/1693318724_64edfe44784909d19eb64.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/trimstray/multitor/blob/master/LICENSE.md)开源许可证协议。

## 项目地址

 **Multitor** ：【[ _GitHub传送门_](https://github.com/trimstray/multitor)】

## 参考资料

> [ _http://www.haproxy.org/_](http://www.haproxy.org/)
>
> [
> _https://www.irif.fr/~jch/software/polipo/_](https://www.irif.fr/~jch/software/polipo/)
>
> [ _https://www.privoxy.org/_](https://www.privoxy.org/)
>
> [ _https://github.com/oyyd/http-proxy-to-> socks_](https://github.com/oyyd/http-proxy-to-socks)
>
> [ _https://github.com/jseidl/Multi-TOR_](https://github.com/jseidl/Multi-> TOR)
>
> [ _http://blog.databigbang.com/distributed-scraping-with-multiple-tor-> circuits/_](http://blog.databigbang.com/distributed-scraping-with-multiple-> tor-circuits/)
>
> [ _https://www.gnu.org/software/bash/_](https://www.gnu.org/software/bash/)

