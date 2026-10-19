**本文将为大家介绍docker守护进程的相关安全配置项目。**

## 一、测试环境

### 1.1 安装 CentOS 7

CentOS Linux release 7.7.1908 (Core)

升级内核，重启

    
    
    # yum update kernel
    [root@localhost docker]# uname -a
    Linux localhost 3.10.0-1062.12.1.el7.x86_64 #1 SMP Tue Feb 4 23:02:59 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
    [root@localhost docker]# cat /etc/redhat-release
    CentOS Linux release 7.7.1908 (Core)
    

### 1.2 安装 docker ce 19.03  

    
    
    # yum install -y yum-utils device-mapper-persistent-data lvm2
    # yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    
    # yum install -y docker-ce
    
    [root@localhost docker]# docker --version
    Docker version 19.03.8, build afacb8b
    

## 二、 守护进程安全配置

默认没有配置文件，需要单独创建/etc/docker/daemon.json，下面配置都是在该文件上进行配置，本地的测试示例。

    
    
    {
        "icc": false,
        "log-level": "info",
        "log-driver": "json-file",
        "log-opts": {
            "max-size": "10m",
            "max-file":"5",
            "labels": "somelabel",
            "env": "os,customer"
        },
        "iptables": true,
        "userns-remap": "default",
        "userland-proxy": false,
        "experimental": false,
        "selinux-enabled": true,
        "live-restore": true,
        "no-new-privileges": true,
        "cgroup-parent": "/foobar",
        "seccomp-profile": "/etc/docker/seccomp/default-no-chmod.json",
        "tls": true,
        "tlsverify": true,
        "tlscacert": "/etc/docker/CA/ca.pem",
        "tlscert": "/etc/docker/CA/server-cert.pem",
        "tlskey": "/etc/docker/CA/server-key.pem"
    }
    

### 2.1 配置通过 HTTPS 和证书认证访问 Docker 守护进程

服务器证书  
创建 HOST，定义域（IP 也可以），会根据域来生成对应的证书，一般用于注册证书当中的 CN：

创建证书目录：

    
    
    $ mkdir -p /etc/docker/dockerd/CA && cd /etc/docker/dockerd/CA
    

生成 key 证书，并填写两次 key 证书密码：

    
    
    $ openssl genrsa -aes256 -out ca-key.pem 4096
    

生成 ca 证书，需要输入注册证书基础信息：

    
    
    $ openssl req -new -x509 -days 365 -key ca-key.pem -sha256 -out ca.pem
    

创建 server 证书：

    
    
    $ openssl genrsa -out server-key.pem 4096
    
    $ openssl req -subj "/CN=localhsot" -sha256 -new -key server-key.pem -out server.csr
    

设定证书指定的 IP 地址：

    
    
    $ echo subjectAltName = DNS:localhost,IP:127.0.0.1 >> extfile.cnf
    

将 Docker 守护程序密钥的扩展使用属性设置为仅用于服务器身份验证：

    
    
    $ echo extendedKeyUsage = serverAuth >> extfile.cnf
    

生成 server cert 证书：

    
    
    $ openssl x509 -req -days 3650 -sha256 -in server.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -extfile extfile.cnf
    

客户端证书  
创建客户端证书：(还是当前目录)

    
    
    $ openssl genrsa -out key.pem 4096
    $ openssl req -subj '/CN=localhost' -new -key key.pem -out client.csr
    

要使密钥适合客户端身份验证，请创建扩展配置文件：

    
    
    $ echo extendedKeyUsage = clientAuth >> extfile.cnf
    

生成 client cert 证书：

    
    
    $ openssl x509 -req -days 3650 -sha256 -in client.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out cert.pem -extfile extfile.cnf
    

使用  
对证书赋予相应的权限：

    
    
    $ chmod -v 0400 ca-key.pem key.pem server-key.pem
    $ chmod -v 0444 ca.pem server-cert.pem cert.pem
    
    [root@localhost CA]# ls
    ca-key.pem ca.pem ca.srl cert.pem client.csr extfile.cnf key.pem server-cert.pem server.csr server-key.pem
    
    

服务端配置`/etc/docker/daemon.json`

    
    
    "tls": true,
    "tlsverify": true,
    "tlscacert": "/etc/docker/CA/ca.pem",
    "tlscert": "/etc/docker/CA/server-cert.pem",
    "tlskey": "/etc/docker/CA/server-key.pem"
    

客户端配置  
设置客户端证书到当服务器上，并放置到相应的位置：

    
    
    $ cp -v {ca,cert,key}.pem ~/.docker
    $ export DOCKER_HOST=tcp://$HOST:2376 DOCKER_TLS_VERIFY=1
    

通过如下方式模拟测试：

    
    
    $ curl https://$HOST:2376/images/json \
       --cert ~/.docker/cert.pem \
       --key ~/.docker/key.pem \
       --cacert ~/.docker/ca.pem
     
    [{"Containers":-1,"Created":1540777343,"Id":"sha256:55e7b305dc477345434ce3bd3941940481f982eea31c8f28c0670d59c63d544b","Labels":nu
    

### 2.2 使用namespace隔离技术

namespace是一种隔离技术，docker就是使用隔离技术开启特定的namespace创建出一些特殊的进程，不过使用namespace是有条件的。系统会创建dockremap，通过/etc/subuid和/etc/subuid对应的id值，映射到容器中去；实际情况还是使用的是dockremap普通权限，达到自动隔离的效果。

首先修改`/etc/sysctl.conf`

    
    
    # echo "user.max_user_namespaces=15076" >> /etc/sysctl.conf
    

在`/etc/docker/daemon.json`增加配置项`"userns-remap": "default"`

 **修改此项配置需要慎重，如果是已经部署了一套docker环境，启用此选项后，会切换到隔离环境，以前的docker容器将无法使用！**

    
    
    [root@localhost docker]# cat /etc/subuid
    dockremap:100000:65536
    

### 2.3 设置 docker 的分区

为容器创建单独的分区，默认分区在\var\lib\docker\，包含本地镜像、容器、网络等相关的东西。

    
    
    [root@localhost docker]# ls /var/lib/docker 
    100000.100000  builder  buildkit  containers  image  network  overlay2  plugins  runtimes  swarm  tmp  trust  volumes
    

可以使用`"data-root": ""`配置默认的分区位置。

### 2.4 限制默认网桥容器之间的流量  

当启动 Docker 服务时候，默认会添加一条转发策略到 iptables 的 FORWARD 链上。策略为通过（ ACCEPT ）还是禁止（ DROP
），取决于配置 `--icc=true` （缺省值）还是 `--icc=false` 。如果手动指定 `--iptables=false` 则不会添加
iptables 规则。  
默认情况下，默认网桥上同一主机上的容器之间允许所有网络通信，如果不需要，限制所有容器间的通信。
将需要通信的特定容器链接在一起，或者创建自定义网络，并且仅加入需要与该自定义网络进行通信的容器。

配置限制默认网桥上容器之间的流量`"icc":false`

### 2.5 配置日志  

配置集中的远程日志，设置日志进程`--log-level`级别为`info`，日志记录格式 json，本地日志记录

    
    
    "log-level": "info",
    "log-driver": "json-file",
    "log-opts": {
      "max-size": "10m",
      "max-file":"5",
      "labels": "somelabel",
      "env": "os,customer"
    },
    

配置远程日志

![](https://image.3001.net/images/20200315/1584284702_5e6e441e0c835.png!small)

Docker 日志记录驱动程序接收容器日志并将其转发到远程目标或文件。 默认的日志记录驱动程序是json-file。
它将容器日志以JSON格式存储在本地磁盘上。 Docker具有用于记录日志的插件体系结构，因此有用于开源工具和商业工具的插件：

> Journald–将容器日志存储在系统日志中.
>
> Syslog Driver–支持UDP，TCP，TLS
>
> Fluentd –支持将TCP或Unix套接字连接到fluentd
>
> Splunk – HTTP / HTTPS转发到Splunk服务器
>
> Gelf – UDP日志转发到Graylog2

示例 fluent

    
    
     {
       "log-driver": "fluentd",
       "log-opts": {
         "fluentd-address": "fluentdhost:24224"
       }
     }
    

使用 syslog

    
    
    {
      "log-driver": "syslog",
      "log-opts": {
        "syslog-address": "udp://1.2.3.4:1111"
      }
    }
    

### 2.6 设置 ulimit

    
    
    {
        "default-ulimits": {
            "nofile": {
                "Name": "nofile",
                "Hard": 64000,
                "Soft": 64000
            }
        }
    }
    

### 2.7 设置 cgroup

`--cgroup-parent`选项允许设置用于容器的默认cgroup父级。 如果未设置此选项，则对于fs
cgroup驱动程序，默认为`/docker`；对于systemd cgroup驱动程序，默认为`system.slice`。  
如果cgroup有一个正斜杠（`/`），则cgroup在根cgroup下创建，否则cgroup在守护程序cgroup下创建。  
假设守护程序在cgroup daemoncgroup中运行，则`--cgroup-parent=/foobar`在`/sys/fs/cgroup/memory/foobar`中创建一个cgroup，而使用`--cgroup-parent=foobar`则创建 `/sys/fs/cgroup/memory/daemoncgroup/foobar`中创建 cgroup。  
systemd cgroup驱动程序对--cgroup-parent具有不同的规则。 Systemd按切片表示层次结构，切片的名称对树中的位置进行编码。
因此，systemd cgroup的`--cgroup-parent`应为切片名称。
名称可以包含一系列用短划线分隔的名称，这些名称描述了从根切片到切片的路径。 例如，`--cgroup-parent=user-a-b.slice`表示容器的内存cgroup在`/sys/fs/cgroup/memory/user.slice/user-a.slice/user-a-b.slice/docker-<id>.scope`中创建。  
也可以使用容器运行来设置，使用docker create和docker run上的`--cgroup-parent`选项，会优先于守护程序上的`--cgroup-parent`选项。

### 2.8 配置 seccomp

使用的测试配置文件，禁止在 Docker 里使用`chmod`命令  
<https://github.com/docker/labs/blob/master/security/seccomp/seccomp-profiles/default-no-chmod.json>

    
    
    [root@localhost docker]# docker run --rm -it alpine sh
    / # ls bin  etc  lib  mnt  proc  run  srv  tmp  var
    dev  home  media  opt  root  sbin  sys  usr / # touch foo.sh
    / # chmod +x foo.sh
    chmod: foo.sh: Operation not permitted
    / # exit
    

实际可以完成禁止、允许、告警某些系统相关的调用，参考：<https://github.com/torvalds/linux/blob/master/arch/x86/entry/syscalls/syscall_64.tbl>

### 2.9 配置支持无守护程序的容器

`--live-restore`确保 docker 守护进程关闭时不影响容器。

测试时再关闭 docker 守护进程后，nginx 容器仍能正常提供访问。  
![snipaste20200315_212215](https://image.3001.net/images/20200315/1584284713_5e6e44299f10a.png!small)

### 2.10 禁用 docker 的实验性功能

设置`"experimental": false`

### 2.11 限制容器通过 suid 或 sgid 提权

`no-new-privileges`安全选项可防止容器内的应用程序进程在执行期间获得新的特权。  

举例：有一个在映像中设置了 setuid/setgid
位的程序，例如sudo，容器中的进程也具有执行该程序的（文件）权限，试图通过诸如setuid/setgid之类的设施获取特权的任何操作将被拒绝。

## 三、守护进程配置示例说明（Linux）

    
    
    {
        "authorization-plugins": [],//访问授权插件
        "data-root": "",//docker数据持久化存储的根目录,默认为/var/lib/docker
        "dns": [],//DNS服务器
        "dns-opts": [],//DNS配置选项，如端口等
        "dns-search": [],//DNS搜索域名
        "exec-opts": [],//执行选项
        "exec-root": "",//执行状态的文件的根目录
        "experimental": false,//是否开启试验性特性
        "features": {},//启用或禁用特定功能。如：{"buildkit": true}使buildkit成为默认的docker镜像构建器。
        "storage-driver": "",//存储驱动器类型
        "storage-opts": [],//存储选项
        "labels": [],//键值对式标记docker元数据
        "live-restore": true,//dockerd挂掉是否保活容器（避免了docker服务异常而造成容器退出）
        "log-driver": "json-file",//容器日志的驱动器
        "log-opts": {
            "max-size": "10m",
            "max-file":"5",
            "labels": "somelabel",
            "env": "os,customer"
        },//容器日志的选项
        "mtu": 0,//设置容器网络MTU（最大传输单元）
        "pidfile": "",//daemon PID文件的位置
        "cluster-store": "",//集群存储系统的URL
        "cluster-store-opts": {},//配置集群存储
        "cluster-advertise": "",//对外的地址名称
        "max-concurrent-downloads": 3,//设置每个pull进程的最大并发
        "max-concurrent-uploads": 5,//设置每个push进程的最大并发
        "default-shm-size": "64M",//设置默认共享内存的大小
        "shutdown-timeout": 15,//设置关闭的超时时限
        "debug": true,//开启调试模式
        "hosts": [],//dockerd守护进程的监听地址
        "log-level": "",//日志级别
        "tls": true,//开启传输层安全协议TLS
        "tlsverify": true,//开启输层安全协议并验证远程地址
        "tlscacert": "",//CA签名文件路径
        "tlscert": "",//TLS证书文件路径
        "tlskey": "",//TLS密钥文件路径
        "swarm-default-advertise-addr": "",//swarm对外地址
        "api-cors-header": "",//设置CORS（跨域资源共享-Cross-origin resource sharing）头
        "selinux-enabled": false,//开启selinux(用户、进程、应用、文件的强制访问控制)
        "userns-remap": "",//给用户命名空间设置 用户/组
        "group": "",//docker所在组
        "cgroup-parent": "",//设置所有容器的cgroup的父类
        "default-ulimits": {
            "nofile": {
                "Name": "nofile",
                "Hard": 64000,
                "Soft": 64000
            }
        },//设置所有容器的ulimit
        "init": false,//容器执行初始化，来转发信号或控制(reap)进程
        "init-path": "/usr/libexec/docker-init",//docker-init文件的路径
        "ipv6": false,//支持IPV6网络
        "iptables": false,//开启防火墙规则
        "ip-forward": false,//开启net.ipv4.ip_forward
        "ip-masq": false,//开启ip掩蔽(IP封包通过路由器或防火墙时重写源IP地址或目的IP地址的技术)
        "userland-proxy": false,//用户空间代理
        "userland-proxy-path": "/usr/libexec/docker-proxy",//用户空间代理路径
        "ip": "0.0.0.0",//默认IP
        "bridge": "",//将容器依附(attach)到桥接网络上的桥标识
        "bip": "",//指定桥接IP
        "fixed-cidr": "",//(ipv4)子网划分，即限制ip地址分配范围，用以控制容器所属网段实现容器间(同一主机或不同主机间)的网络访问
        "fixed-cidr-v6": "",//（ipv6）子网划分
        "default-gateway": "",//默认网关
        "default-gateway-v6": "",//默认ipv6网关
        "icc": false,//容器间通信
        "raw-logs": false,//原始日志(无颜色、全时间戳)
        "allow-nondistributable-artifacts": [],//不对外分发的产品提交的registry仓库
        "registry-mirrors": [],//registry仓库镜像加速地址
        "seccomp-profile": "",//seccomp配置文件
        "insecure-registries": [],//配置非https的registry地址
        "no-new-privileges": false,//禁止新优先级
        "default-runtime": "runc",//OCI联盟(The Open Container Initiative)默认运行时环境
        "oom-score-adjust": -500,//内存溢出被杀死的优先级(-1000~1000)
        "node-generic-resources": ["NVIDIA-GPU=UUID1", "NVIDIA-GPU=UUID2"],//对外公布的资源节点
        "runtimes": {
            "cc-runtime": {
                "path": "/usr/bin/cc-runtime"
            },
            "custom": {
                "path": "/usr/local/bin/my-runc-replacement",
                "runtimeArgs": [
                    "--debug"
                ]
            }
        },//运行时
        "default-address-pools":[
            {"base":"172.80.0.0/16","size":24},//默认的dhcp分配地址
            {"base":"172.90.0.0/16","size":24}
        ]
    }

 ***本文原创作者：白河·愁 ，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

