**ssh-auditor是一款可帮助你探测所在网络中ssh弱密码的工具。**

## 特性

以下操作ssh-auditor都将自动化的完成：

> 添加新凭据时，重新检查所有已知主机，并且只检查新凭据。
>
> 在任何新发现的主机上，队列一个完整的凭据扫描
>
> 在任何更改了ssh版本和密钥指纹的已知主机上，队列一个完整的凭据扫描
>
> 尝试执行命令以及TCP隧道连接。
>
> 定时重新检查一遍（scan_interval）。默认为14天。

根据其设计，你可以以小时为单位从cron运行ssh-auditor discover + ssh-auditor scan，执行持续的安全审计。

## Demo

早期的功能演示视频：

[**视频原地址**](https://asciinema.org/a/5rb3wv8oyoqzd80jfl03grrcv?autoplay=1)

改进的日志输出演示视频：  

 **[视频原地址](https://asciinema.org/a/F3fQYyJcieCS9Kfna6xWferjK?autoplay=1)**

## 使用

安装

    
    
    $ brew install go # or however you want to install the go compiler
    $ go get github.com/ncsa/ssh-auditor

或

    
    
    $ go build

构建一个包含sqlite的静态二进制文件

    
    
    $ make static

设置足够的打开文件描述符值

    
    
    $ ulimit -n 4096

创建初始数据库并发现ssh服务器

    
    
    $ ./ssh-auditor discover -p 22 -p 2222 192.168.1.0/24 10.0.0.1/24

添加凭据对进行检查

    
    
    $ ./ssh-auditor addcredential root root
    $ ./ssh-auditor addcredential admin admin
    $ ./ssh-auditor addcredential guest guest --scan-interval 1 #check this once per day

尝试对已发现主机的凭据探测

    
    
    $ ./ssh-auditor scan

输出有效凭据报告

    
    
    $ ./ssh-auditor vuln

重新检查有效凭据

    
    
    $ ./ssh-auditor rescan

输出重复密钥使用报告

    
    
    $ ./ssh-auditor dupes

## 报告查询

ssh-auditor vuln的sql查询语句如下：

    
    
    select
            hc.hostport, hc.user, hc.password, hc.result, hc.last_tested, h.version
     from
            host_creds hc, hosts h
     where
            h.hostport = hc.hostport
     and    result!='' order by last_tested asc

 ***参考来源：[GItHub](https://github.com/ncsa/ssh-auditor)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

