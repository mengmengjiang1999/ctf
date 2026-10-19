**Malcom这款工具可分析系统内的网络通信流量，并以图形化的形式将流量分析情况提供给用户，分析结果中将包含已知的恶意软件源，而这些信息将有助于安全研究专家对特定的恶意软件进行分析。**

### Malcom能做什么？

Malcom可以帮助我们：

> 1、 检测中央命令&控制服务器；
>
> 2、 识别点对点网络；
>
> 3、 识别DNS基础设施；
>
> 4、 快速判断网络流量“恶意性”；

Malcom的目标是通过图形化的网络流量信息来帮助研究人员更加轻松地分析恶意软件，并提供更加智能化的情报信息。

下面给出的是主机tomchop.me的分析样本图：

![222222222222.png](https://image.3001.net/images/20190214/1550074856_5c6443e847971.png!small)

数据集查看（可过滤IP）

![333333333.png](https://image.3001.net/images/20190214/1550074864_5c6443f09ebf0.png!small)  

## 工具安装

Malcom采用Python开发，并提供了大部分必要的代码库，你可以直接在任何平台上运行Malcom。我强烈建议大家使用Python虚拟环境：virtualenv，这样就不会影响系统库了。

下列命令以在Ubuntu server 14.04 LTS平台上进行了测试：

-安装git、python、libevent库、mongodb、redis以及其他依赖：
    
    
      $ sudo apt-get install build-essential gitpython-dev libevent-dev mongodb libxml2-dev libxslt-dev zlib1g-dev redis-serverlibffi-dev libssl-dev python-virtualenv

-克隆Git库：
    
    
      $ git clone https://github.com/tomchop/malcom.git malcom

创建并激活你的virtualenv：

    
    
      $ cd malcom
    
      $ virtualenv env-malcom
    
      $ source env-malcom/bin/activate

安装scapy：

    
    
      $ cd .. 
    
      $ wget <http://www.secdev.org/projects/scapy/files/scapy-latest.tar.gz>
    
      $ tar xvzf scapy-latest.tar.gz
    
      $ cd scapy-2.1.0
    
      $ python setup.py install

在virtualenv环境下，安装requirements.txt文件中的必要Python包：

    
    
      $ cd ../malcom
    
      $ pip install -r requirements.txt

如果你需要IP地理位置信息，你可以下载Maxmind数据库并把文件提取到malcom/Malcom/auxiliary/geoIP目录下。

Maxmind数据库免费下载地址：【[传送门](http://dev.maxmind.com/geoip/geoip2/geolite2/)】。

你可以使用./malcom.py来启动Web服务器，并使用./malcom.py
–help监听接口和端口。这里需要将malcom.conf.example文件拷贝为malcom.conf并运行下列命令：

    
    
    ./malcom.py -c malcom.conf

## 配置选项

### 数据库

默认配置下，Malcom会尝试连接本地mongodb实例，并创建自己的数据库，名叫malcom。

设置Malcom数据库名称

默认配置下，Malcom的数据库默认名为malcom。你可以通过编辑malcom.conf文件并设置database标签下的name属性：

    
    
        [database]
    
        ...
    
        name = my_malcom_database
    
    ...

### 远程数据库

你可以在主机my.mongo.server上使用单独的数据库：

    
    
        [database]
    
        ...
    
        hosts = my.mongo.server
    
    ...

你还可以指定mongodb端口：

    
    
        [database]
    
        ...
    
        hosts = localhost:27008
    
    ...

### 使用认证

你可以配置mongodb实例来启用认证连接，你可以自由设置用户名和密码：

    
    
        [database]
    
        ...
    
        username = my_user
    
        password = change_me
    
    ...

如果你想连接其他数据库的话，可以设置authentication_database参数：

    
    
        [database]
    
        ...
    
        authentication_database =some_other_database
    
    ...

## Docker实例

你可以直接从公共docker库中获取Docker镜像：

    
    
    $ sudo docker pull tomchop/malcom-automatic
    
    $ sudo docker run -p 8080:8080 -d --namemalcom tomchop/malcom-automatic

接下来，你就可以直接在浏览器中访问[http://<docker_host>:8080/](/)来使用了。

## 项目地址

Malcom：【[GitHub传送门](https://github.com/tomchop/malcom)】

 ***参考来源：[malcom](https://www.kitploit.com/2018/12/malcom-malware-communications-analyzer.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

