# 前言

burpsuite的一些简单基础，有不对的地方欢迎各位大佬留言交流

# 安装

首先先下载burpsuite和keygen  
burpsuite推荐从雾晓安全公众号上下载(不是打广告，我一直用的这个，一直在更新，真的挺好用的)

至于keygan，网上有很多资源，这里就不提供了

这个作者提供了资源，感谢他  
https://blog.csdn.net/z1013507218/article/details/118969553

下载好后双击运行vbs脚本来运行burpsuite，然后运行keygen工具，将其中的license粘贴到里面  
![](https://image.3001.net/images/20220712/1657595617_62cce6e1ea92f6544d47d.jpg!small)

将这些都复制到里面后，点击下一步，然后选择手动激活

将burp的请求复制到keygen，将生成的响应复制到burp就行了

![](https://image.3001.net/images/20220712/1657595619_62cce6e3ce6963e724cbc.jpg!small)

## 配置问题

要将burpsuite中的证书导入到浏览器中才可以使用

  * 注意：若是浏览器显示您的连接不是私密连接的话导入证书就可以了，注意导入的路径不要出错

 **导入的路径如下，一定要是导入到受信任的根证书颁发机构**

![](https://image.3001.net/images/20220712/1657595622_62cce6e687cefd143fdeb.jpg!small)

# 1、基本使用

安装、配置过程如果还不明白请看以下的文章或者自己搜索

    
    
    https://blog.csdn.net/weixin_43543330/article/details/106723117
    

## 一、简介

Burp Intruder是一个强大的工具，用于自动对Web应用程序自定义的攻击，Burp Intruder
是高度可配置的，并被用来在广范围内进行自动化攻击。你可以使用 Burp Intruder
方便地执行许多任务，包括枚举标识符，获取有用数据，漏洞模糊测试。合适的攻击类型取决于应用程序的情况，可能包括：缺陷测试：SQL
注入，跨站点脚本，缓冲区溢出，路径遍历；暴力攻击认证系统；枚举；操纵参数；拖出隐藏的内容和功能；会话令牌测序和会话劫持；数据挖掘；并发攻击；应用层的拒绝服务式攻击。

## 二、Target组件

主要包括地图、目标域、漏洞问题定义三部分

### 目标域设置Target Scope

当我们对某个产品进行渗透测试时，可以通过域名或者主机名去限制拦截内容，这里域名或主机名就是我们说的作用域；如果我们想限制得更为细粒度化，比如，你只想拦截login目录下的所有请求，这时我们也可以在此设置，此时，作用域就是目录。总体来说，Target
Scope主要使用于下面几种场景中：

> 限制站点地图和Proxy 历史中的显示结果
>
> 告诉Burp Proxy 拦截哪些请求
>
> Burp Spider抓取哪些内容
>
> Burp Scanner自动扫描哪些作用域的安全漏洞
>
> 在Burp Intruder和Burp Repeater 中指定URL

通过Target Scope 我们能方便地控制Burp 的拦截范围、操作对象，减少无效的噪音。在Target
Scope的设置中，主要包含两部分功能：允许规则和去除规则。

其中允许规则即表示包含在此规则列表中的，视为操作允许、有效。如果此规则用于拦截，则请求消息匹配包含规则列表中的将会被拦截；反之，请求消息匹配去除列表中的将不会被拦截

 **四、Intruder的4种攻击类型**

模式| 作用  
---|---  
sniper（狙击手模式）| 一个位置使用一组payload集合  
Battering ram（攻城锤模式）| 在多个位置使用相同的payload集合  
Pitchfork（草叉模式）| 就是每个位置的遍历指定的payload  
Cluster bomb（集束乍弹模式）| 适合爆破用户名密码，第一个位置的paylaod匹配第二位置的每个payload  
  
# 2、高级使用

### 过滤

这里的过滤可以分为抓取的时候过滤和在历史记录中过滤

> 使用过滤能避免抓到一些乱七八糟的包，让我们专注于我们的目标，也可以在后面快速的帮我们找到需要查看分析的包

### 抓取过滤

1、定义只抓取指定域名的网站的包  
例如：只抓取csdn的包

![](https://image.3001.net/images/20220712/1657595624_62cce6e850e51aafb8236.png!small)

如上图，打开proxy -> Option -> Intercept Client Requests，然后添加就行了

### 过滤历史包

打开Target -> Site map，然后点击Filter，然后可以选择要显示的项目

![](https://image.3001.net/images/20220712/1657595625_62cce6e93b78de59bb3ac.png!small)

    
    
    注意：
    可以右击选Add to Scope，然后就可以添加到Scope中（也就是选择的范围中，可以在其他模块里用到）
    
    

## 设置上游代理

    
    
    应用场景：
    
    要使用其他的代理，然后用burpsuite抓包的时候
    
    例如：
    	1、使用代理上网
    	2、使用xray联动burp扫描等等
    
    
    
    

详细设置步骤：

1、使用代理上网用burpsuite抓包

首先配置burpsuite的抓包代理：

  * 设置proxy(代理)  
不用变，默认是代理8080端口  
![](https://image.3001.net/images/20220712/1657595626_62cce6ea3bf234a63625b.png!small)

  * 在浏览器中设置代理：  
这里使用谷歌浏览器的SwitchyOmega插件切换代理  
将代理改成127.0.0.1:8080，设置如下：  
![](https://image.3001.net/images/20220712/1657595627_62cce6eb532714d96ce38.png!small)

  * 设置burp中的上游代理：  
打开burpsuite的user options(用户选项)选项卡，然后选择Upstream Proxy Server(上游代理服务)  
然后配置如下  
![](https://image.3001.net/images/20220712/1657595628_62cce6ec4de5ebef92874.png!small)

里面的IP地址和端口就是梯子的IP和端口

然后就可以经过梯子的流量直接抓包了，如下：

![](https://image.3001.net/images/20220712/1657595629_62cce6ed8923249630629.png!small)

## 插件使用

### 导入插件

从GitHub上下载到本地后如下操作即可

![](https://image.3001.net/images/20220712/1657595630_62cce6ee995082df95dae.png!small)

### 常用的插件使用

#### HachBar插件

项目地址：  
<https://github.com/portswigger/hackbar>

我的主要用途是利用它的==万能密码==模块

#### Burp - Turbo Intruder

个人感觉超强的一款Burp插件，反正超快  
Link: [https://github.com/PortSwigger/turbo-intruder/，https://youtu.be/vCpIAsxESFY，https://portswigger.net/research/turbo-intruder-embracing-the-billion-request-attack](https://github.com/PortSwigger/turbo-intruder/%EF%BC%8Chttps://youtu.be/vCpIAsxESFY%EF%BC%8Chttps://portswigger.net/research/turbo-intruder-embracing-the-billion-request-attack)

> 安装  
> Extender -> BApp Store -> Turbo Intruder

![](https://image.3001.net/images/20220712/1657595631_62cce6ef74a0372fdb3f8.png!small)

Or

 **手动下载 - > 导入**  
<https://github.com/PortSwigger/turbo-intruder/>

##### 基础使用

直接抓取数据包右键发送过去就可以

有上下两块

 **就拿爆破目录来举例吧**  
要fuzz的点用%s来顶上  
[![](https://image.3001.net/images/20220712/1657595632_62cce6f02290be2824a5e.png!small)](https://image.3001.net/images/20220712/1657595632_62cce6f02290be2824a5e.png!small)

> 选择爆破点 -> 加载字典 -> Attack  
>
> ![](https://image.3001.net/images/20220712/1657595632_62cce6f0ef78e14f1e321.jpg!small)

###### 提升速度

想要大大提升速度，就把pipeline设置成True

##
爆破user&pass[#](https://www.cnblogs.com/secxue/p/14035477.html#%E7%88%86%E7%A0%B4userpass)

    
    
    from urllib import quote
    
    def password_brute(target,engine):
     for word in open('F:/Tools/Dict/fuzzDicts-master/top10.txt'):
           engine.queue(target.req, quote(word.rstrip()))
    
    def user_brute(target,engine):
     for word in open('F:/Tools/Dict/fuzzDicts-master/top10.txt'):
           engine.queue(target.req, quote(word.rstrip()))
    def user_password_brute(target, engine):
     for password in open('F:/Tools/Dict/fuzzDicts-master/top10.txt'):
       for user in open('F:/Tools/Dict/fuzzDicts-master/top10.txt'):
              engine.queue(target.req, [quote(user.rstrip()),quote(password.rstrip())])
    
    def queueRequests(target, wordlists):
       engine = RequestEngine(endpoint=target.endpoint,
               concurrentConnections=5,
               requestsPerConnection=100,
               pipeline=True
               )
       #user_brute(target,engine)
       #password_brute(target,engine)
       user_password_brute(target,engine)
    
    def handleResponse(req, interesting):
    # currently available attributes are req.status, req.wordcount, req.length and req.response
       if req.status == 200:
          table.add(req)
    

> if条件 可以自己更改  
> 需要用哪个就用哪个，不需要就注释  
>
> ![](https://image.3001.net/images/20220712/1657595634_62cce6f2603857d68009a.jpg!small)

###### 爆破数字验证码

最后的数字假如是4位验证码就传4，6就是6

    
    
    from itertools import product
    
    def brute_veify_code(target, engine, length):
       pattern = '1234567890'
       for i in list(product(pattern, repeat=length)):
            code =  ''.join(i)
            engine.queue(target.req, code)
    
    def queueRequests(target, wordlists):
       engine = RequestEngine(endpoint=target.endpoint,
               concurrentConnections=30,
               requestsPerConnection=100,
               pipeline=True
               )
       brute_veify_code(target, engine, 6)
    
    def handleResponse(req, interesting):
    # currently available attributes are req.status, req.wordcount, req.length and req.response
     if 'error' not in req.response:
          table.add(req)
    

> 不做演示了

###### 并发漏洞

![](https://image.3001.net/images/20220712/1657595635_62cce6f38f5b232267732.jpg!small)

