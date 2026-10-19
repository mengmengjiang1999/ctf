#  

Nmap是学习网络安全必备的一款工具，有着强大的信息收集能力，有本书甚至因此称它为“诸神之眼”
。Nmap不仅仅是一个端口扫描器那么简单，它还有着一个强大的脚本引擎（NSE）可以通过编程来实现定制化。

## 0x01 关于Nmap中NSE的使用姿势

斗哥目前使用的 nmap 7.40这个版本中就内置有500多个官方编写的NSE脚本。下面是window上nmap的安装目录：

![安装目录.png](https://image.3001.net/images/20180307/1520386091483.png!small)  

其中，`scripts`目录存放着NSE脚本，而`nselib`目录存放各种库文件，通常使用`--script`来指定要使用的nmap脚本。

 **比如：** 使用`mysql-brute.nse`这个脚本对目标地址进行mysql的口令爆破。 **命令：**`nmap
--script=mysql-brute <target>`

在Nmap的官方说明文档`https://nmap.org/nsedoc/`中有NSE脚本和库文件的详细使用说明。

![使用说明.png](https://image.3001.net/images/20180307/15203861677015.png!small)  

## 0x02 NSE编写demo文件

 **LUA语言基础**

打开任何一个NSE脚本或者是库文件，里面的代码功能通常由lua语言来实现。因此想要写自己的脚本或者库，前提是有一定的lua语言基础。lua是一个轻量化的脚本语言，有编程基础的同学学lua应该会比较轻松，在菜鸟教程花个把小时学习lua语言的基本使用，已经足够明白本篇的编程内容了。

![编程.png](https://image.3001.net/images/20180307/15203862814388.png!small)  

 **NSE脚本基本格式**

一个完整的NSE脚本通常都有这么几个部分的代码字段：

  * description 字段：本脚本的说明介绍。
  * categories 字段：本脚本的分类。Nmap执行脚本除了指定单个脚本外，还可以指定某一类脚本，比如`default`类，我们没有使用`--script`参数时，默认会加载这一类的脚本。
  * rule 字段：本脚本的执行规则，也即触发脚本执行的条件会在rule字段定义。一般执行规则是一个lua函数，返回值只有true和false两种。
  * action字段：脚本执行的具体内容。rule字段返回true时会执行action字段定义的函数。

    
    
    local shortport = require "shortport"
    description = [[a demo nse file]]
    author = "reborn"
    license = "Same as Nmap--See http://nmap.org/book/man-legal.html"
    categories = {"default"}
    
    portrule = function( host, port )
        return true
    end
    
    action = function(host, port)
    
    end
    

**NSE脚本的规则**
你可以发现上述rule字段是`portrule`，NSE脚本的执行规则是和nmap的扫描相结合的，两者执行的先后顺序目前有如下4种。

  * prerule()：规则早于nmap的扫描，执行的顺序是先执行脚本，后nmap扫描。
  * hostrule()：nmap完成了主机发现之后运行脚本。
  * portrule()：nmap执行了端口扫描后运行脚本。
  * postrule()：nmap完成所有的扫描后才执行脚本。

 **编写简单的NSE脚本**

如：编写一个简单的脚本来探测目标是否开放了80端口，并且这个端口运行的是HTTP服务，如果是nmap输出“This is a
WebServer”。那么在前面脚本demo代码的基础上，我们只需修改portrule函数的代码和让action函数来输出。 **代码逻辑**
先portrule判断条件是否成立：“目标是否开放了80端口，服务是否是HTTP”，是返回true不是返回false，代码实现：

    
    
    portrule = function(host,port)
        return port.protocol == "tcp" and port.number == 80 and port.service =="http" and port.state =="open"
    end
    

如果返回true：执行action，输出“This is a WebServer”：

    
    
    action = function(host, port)
    return "This is a WebServer"
    end
    

完整的代码：

    
    
    local shortport = require "shortport"
    description = [[a http service detect test demo]]
    
    author = "reborn"
    license = "Same as Nmap--See http://nmap.org/book/man-legal.html"
    categories = {"default"}
    
    portrule = function(host,port)
        return port.protocol == "tcp" and port.number == 80 and port.service =="http" and port.state =="open"
    end
    
    action = function(host, port)
    return "This is a WebServer"
    end
    

将上述代码命名为`http-detect-test.nse`保存在`scripts`目录下，然后执行`nmap --script-updatedb`更新nse脚本。

![脚本.png](https://image.3001.net/images/20180307/15203863553878.png!small)  

接着在nmap中执行`http-detect-test.nse`这个脚本：`nmap -p 80 10.10.10.39 --script http-detect-test`

![test.png](https://image.3001.net/images/20180307/15203865815974.png!small)  

另外，如果执行过程，脚本有错误，可以在nmap命令中加入`-d`来获得调试中的数据。

## 0x03 NSE中的API

你可能会对上面脚本中portrule规则判断扫描结果的代码心存疑惑，实际上那个位置调用了nmap扫描结果的API。

Nmap中的API的核心功能就是向脚本提供关于主机和端口的信息，例如名字解析、主机和端口的状态、服务发现等内容。此处介绍一部分常用的的API调用和代码demo供给大家参考使用。

 **两个Lua table 类型的参数**

  * host table
  * port table

### host table

#### 1\. host.os

 **获取nmap扫描到的操作系统信息。**

  * vendor 供应商
  * osfamily 所属系列
  * osgen 具体型号
  * type 设备类型
  * CPE

    
    
    local shortport = require "shortport"
    
    description = [[test api]]
    
    author = "reborn"
    license = "Same as Nmap--See http://nmap.org/book/man-legal.html"
    categories = {"default"}
    
    hostrule = function( host, port )
        return true
    end
    
    action = function(host, port)
        return host.os
    end
    

扫描命令：`nmap -O 10.10.10.39 --script my-api-test`

    
    
    Host script results:
    | my-api-test:
    |
    |     name: Linux 2.6.13 - 2.6.32
    |     classes:
    |
    |         type: general purpose
    |         vendor: Linux
    |         osgen: 2.6.X
    |         osfamily: Linux
    |         cpe:
    |_          cpe:/o:linux:linux_kernel:2.6
    

#### 2\. host.ip

将`host.os`那段脚本的第14行改为`return host.ip`。

扫描命令：`nmap www.baidu.com --script my-api-test`

    
    
    Host script results:
    |_my-api-test: 14.215.177.38
    

#### 3.host.name

将`host.os`那段脚本的第14行改为`return host.name`。

扫描命令：`nmap www.baidu.com --script my-api-test`

    
    
    Host script results:
    |_my-api-test: 14.215.177.38
    

#### 4.host.targetname

目标主机在命令行的名字。

#### 5.host.directly_connected

表示目标计算机是否与我们同在一个子网。

#### 6.host.name

将`host.os`那段脚本的第14行改为`return host.mac_addr`。

扫描命令：`nmap 10.10.10.39 --script my-api-test` 必须是同一子网的设备这个命令才有效。

    
    
    Host script results:
    |_my-api-test: \x00\x0C)f\xF4\xDF
    

#### 7.host.traceroute

将`host.os`那段脚本的第14行改为`return host.traceroute`。

扫描命令：`nmap --traceroute www.baidu.com --script my-api-test`

    
    
    Host script results:
    | my-api-test:
    |
    |     times:
    |       srtt: 0.002
    |     ip: 192.168.1.1
    |
    |     times:
    |       srtt: 0.004
    |     ip: 192.168.12.1
    |
    |     times:
    |       srtt: 0.002
    |     ip: 192.168.200.1
    |
    |     name: 78.228.84.110.broad.fz.fj.dynamic.163data.com.cn
    |     ip: 110.84.228.78
    |     times:
    |       srtt: 0.002
    |
    |     times:
    |       srtt: 0.017
    |     ip: 113.96.4.70
    |
    |     times:
    |       srtt: 0.017
    |_    ip: 14.215.177.39
    

### port table

#### 1\. port.number

    
    
    local shortport = require "shortport"
    
    description = [[test api]]
    
    author = "reborn"
    license = "Same as Nmap--See http://nmap.org/book/man-legal.html"
    categories = {"default"}
    portrule = function( host, port )
        return true
    end
    
    action = function(host, port)
        return port.number
    end
    

扫描命令：`nmap www.baidu.com --script my-api-test`

    
    
    PORT    STATE SERVICE
    80/tcp  open  http
    |_my-api-test: 80
    443/tcp open  https
    |_my-api-test: 443
    

#### 2\. port.protocol

    
    
    PORT    STATE SERVICE
    80/tcp  open  http
    |_my-api-test: tcp
    443/tcp open  https
    |_my-api-test: tcp
    

#### 3\. port.service

    
    
    PORT    STATE SERVICE
    80/tcp  open  http
    |_my-api-test: http
    443/tcp open  https
    |_my-api-test: https
    

#### 4\. port.version

    
    
    PORT    STATE SERVICE
    80/tcp  open  http
    | my-api-test:
    |   name_confidence: 3.0
    |   service_tunnel: none
    |   name: http
    |   service_dtype: table
    |_  cpe:
    443/tcp open  https
    | my-api-test:
    |   name_confidence: 3.0
    |   service_tunnel: none
    |   name: https
    |   service_dtype: table
    |_  cpe:
    

#### 5.port.state

    
    
    PORT    STATE SERVICE
    80/tcp  open  http
    |_my-api-test: open
    443/tcp open  https
    |_my-api-test: open
    

## 0x04 小结

内容太多篇幅限制原因，本篇就介绍到NSE如何调用API这里，我们下期见吧。未来几期将会向大家介绍的文章主题如下：

  * NSE的异常处理
  * Nmap中的库文件和编写方式
  * 利用Nmap自有库文件实现将扫描结果保存在数据库
  * NSE漏洞审计和渗透脚本的demo
  * NSE的并发处理
  *   

  * ![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180307/15203866384517.jpg!small)  

