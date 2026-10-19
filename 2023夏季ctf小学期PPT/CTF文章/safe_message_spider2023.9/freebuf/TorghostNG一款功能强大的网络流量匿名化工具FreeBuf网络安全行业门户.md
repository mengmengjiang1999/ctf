## TorghostNG  

 **TorghostNG是一款功能强大的网络流量匿名化工具，该工具基于Python3开发，并对[
_TorGhost_](https://github.com/SusmithKrishnan/torghost)工具进行了重构。TorghostNG的匿名化功能通过Tor网络实现，可以帮助广大研究人员让自己所有的网络通信流量匿名化。**

目前，该工具已在Kali Linux和Manjaro等平台上进行过测试。

注意事项

>
> 1、由于该工具基于Tor网络实现，即使你通过其他方法绕过了某种限制，BitTorrent流量仍然可能会被iptable屏蔽。不过，完全屏蔽所有的torrent流量也是不可能的。
>
> 2、出于安全因素考虑，BitTorrent将会禁用IPv6来阻止IPv6流量泄露。

## 工具安装

TorghostNG当前支持下列系统平台：

> 基于Arch Linux的GNU/Linux发行版；
>
> 基于Debian/Ubuntu的GNU/Linux发行版；
>
> 基于Fedora、CentOS, RHEL、openSUSE的GNU/Linux发行版；

-[ _Solus OS_](https://getsol.us/)

-[ _Void Linux_](https://voidlinux.org/)

-[ _Slackware_](http://slackware.com/)

安装TorghostNG，请打开终端窗口，并输入下列命令：

    
    
    git clone <https://github.com/githacktools/TorghostNG>
    
    cd TorghostNG
    
    sudo python3 install.py
    
    sudo torghostng

但如果使用的是Slackware，那你则需要使用下列命令来运行TorghostNG：

    
    
    sudo python3 torghostng.py

## 工具帮助信息

    
    
    OPTIONS:
    
      -h, --help      Show this help message and exit
    
      -s, --start     Start connecting to Tor
    
      -x, --stop      Stop connecting to Tor
    
      -r, --renew     Renew the current Tor circuit
    
      -id COUNTRY ID  Connect to Tor exit node of a specific country. Go to CountryCode.org to search country ID
    
      -mac INTERFACE  Randomly change MAC address. Use 'ifconfig' to show interface devices
    
      -c, --checkip   Check your current IPv4 address
    
      --dns           Use this to fix DNS when website address can't be resolved
    
      -l, --language  Change the display language. English is the default
    
      --list          Show the available languages list
    
      -u, --update    Check for update
    
      --nodelay       Disable delay time
    
    在运行工具的同时，你还可以结合下列选项一起使用：
    
    torghostng -s -m INTERFACE: 在建立连接之前修改MAC地址；
    
    torghostng -c -m INTERFACE: 检查IP地址并修改MAC地址；
    
    torghostng -s -x: 连接至Tor；

## 工具更新

广大用户可以使用下列命令更新TorghostNG：

    
    
    torghostng -u

## 工具运行截图

1、修改MAC地址：`torghostng -m INTERFACE`

![2.png](https://image.3001.net/images/20200508/1588929180_5eb5229c1f9f5.png!small)

2、检查IP地址：`torghostng -c`

![3.png](https://image.3001.net/images/20200508/1588929187_5eb522a31d957.png!small)

3、与Tor断开连接：`torghostng -x`

![4.png](https://image.3001.net/images/20200508/1588929196_5eb522ac78cd1.png!small)

4、连接至特定国家Tor节点：`torghostng -id COUNTRY ID`

![5.png](https://image.3001.net/images/20200508/1588929205_5eb522b579b27.png!small)

5、卸载TorghostNG：`python3 install.py`

![](https://image.3001.net/images/20200508/1588929213_5eb522bda849c.png!small)

## 项目地址

> TorghostNG：【[ _GitHub传送门_](https://github.com/GitHackTools/TorghostNG)】

 *** 参考来源：[
_GitHackTools_](https://github.com/GitHackTools/TorghostNG)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

