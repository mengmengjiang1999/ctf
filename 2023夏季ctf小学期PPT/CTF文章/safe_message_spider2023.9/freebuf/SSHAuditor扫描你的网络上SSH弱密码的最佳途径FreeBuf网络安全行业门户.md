**今天给大家介绍的是一款名叫SSH-Auditor的工具，这款工具可以帮助广大研究人员扫描自己网络上存在的SSH弱密码。还等什么，赶紧检查一下自己的网络环境吧！**

![ccccccccc.png](https://image.3001.net/images/20181121/1542814050_5bf57962207a4.png!small)

## 功能介绍

SSH-Auditor可以自动化实现以下功能：

> 1、 网络内的主机添加了新证书新证书会之后，自动重新检测所有主机，但是它只会检测新添加的证书。
>
> 2、 发现了新的主机之后，新建完整的证书扫描队列。
>
> 3、 主机SSH版本或密钥指纹发生变化之后，新建完整的证书扫描队列。
>
> 4、 尝试实现命令执行，尝试建立TCP连接。
>
> 5、 使用证书扫描时间间隔（默认为14天）重新检测网络内主机的所有证书。

大家可以使用下列命令来实现每一个小时自动执行一次常规审计扫描：

    
    
    ssh-auditor discover + ssh-auditor scan

## 工具演示

### 完整功能演示

视频地址：<https://asciinema.org/a/5rb3wv8oyoqzd80jfl03grrcv?autoplay=1>

### 升级版的日志输出

视频地址：<https://asciinema.org/a/F3fQYyJcieCS9Kfna6xWferjK?autoplay=1>

## 工具使用

安装：

    
    
    $brew install go # or however you want to install the go compiler
    
    $ goget github.com/ncsa/ssh-auditor

利用git克隆构建代码：

    
    
    $ gobuild

构建静态[代码](https://www.kitploit.com/search/label/Binary)（包含SQLite）：

    
    
    $make static

确保使用了足够多的文件描述符：

    
    
    $ulimit -n 4096

创建初始数据库，扫描SSH服务器：

    
    
    $./ssh-auditor discover -p 22 -p 2222 192.168.1.0/24 10.0.0.1/24

添加需要检测的证书对：

    
    
    $./ssh-auditor addcredential root root
    
    $./ssh-auditor addcredential admin admin
    
    $./ssh-auditor addcredential guest guest --scan-interval 1 #check this once perday

在已发现的主机上检测证书有效性：

    
    
    $./ssh-auditor scan

输出证书扫描报告：

    
    
    $./ssh-auditor vuln

重新扫描证书有效性：

    
    
    $./ssh-auditor rescan

输出密钥副本的使用情况：

    
    
    $./ssh-auditor dupes

## 报告查询

    
    
    select
    
            hc.hostport, hc.user, hc.password,hc.result, hc.last_tested, h.version
    
     from
    
            host_creds hc, hosts h
    
     where
    
            h.hostport = hc.hostport
    
     and   result!='' order by last_tested asc

SSH-Auditor项目地址：【[GitHub传送门](https://github.com/ncsa/ssh-auditor)】

 ***参考来源：[ssh-auditor](https://github.com/ncsa/ssh-auditor)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

