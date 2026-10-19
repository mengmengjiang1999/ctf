在最近的攻防演练中经常能看到这样的frpc配置文件。

    
    
    [common]
    server_addr = x.x.x.x
    server_port = 7000
    
    [xxx]
    type = tcp
    remote_port = 48944
    plugin = socks5
    

连接服务器的信息中没有凭证信息，这不是妥妥的未授权吗。我寻思着一般安全意识比较好的攻击队怎么会用能未授权访问的东西，不太正常。我去翻阅了frp的官方文档

> https://gofrp.org/docs/examples/ssh/

原来官方例子中的配置就是未授权的，看来是为了图方便。

![image](https://image.3001.net/images/20230501/1682941719_644fa717c03ffa2a11845.png!small)

那既然是未授权，那肯定有办法检测未授权的frp server，从而加以利用(用其他红队的frp
server做代理，是不是就溯源不到咱们头上的IP了呢？#坏笑.jpg)。

不想看分析的师傅们可以直接来弟弟的项目下载成品(开源),可批量检测未授权、弱口令。

> https://github.com/SleepingBag945/frpCracker

![image](https://image.3001.net/images/20230501/1682941746_644fa732d62497f75f5f4.png!small)

为了弄清楚frp的鉴权过程，下载了frp的源码进行阅读。

找到frpc，调试f7单步跟下去。在clint/service.go找到登录相关函数login()

![image](https://image.3001.net/images/20230501/1682941793_644fa7610745396a405ce.png!small)

首先在这发送了进行连接

![image](https://image.3001.net/images/20230501/1682941807_644fa76ff3897a1b0fc7d.png!small)

![image](https://image.3001.net/images/20230501/1682941824_644fa7804f4e2e1611d68.png!small)

    
    
    \x00\x01\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00
    

然后回了个进行确认

![image](https://image.3001.net/images/20230501/1682941838_644fa78e41ee34f323d1c.png!small)

    
    
    \x00\x01\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00
    

通过返回包可以判断一个tcp端口是否开放着frp服务。

接着进入认证阶段。

![image](https://image.3001.net/images/20230501/1682941852_644fa79ced7e121310047.png!small)

将loginMsg序列化成json发送出去

![image](https://image.3001.net/images/20230501/1682941871_644fa7af58852b4625a78.png!small)

其他的很清楚怎么来的，只有这个PrivilegeKey需要弄清楚

进入svr.authSetter.SetLogin(loginMsg)看

![image](https://image.3001.net/images/20230501/1682941884_644fa7bc14da35c4d49b5.png!small)

![image](https://image.3001.net/images/20230501/1682950553_644fc9999df3cb95a58be.png!small)

也就是说这个PrivilegeKey是由auth.token与当前时间戳计算得到,在无配置token的访问中，

![image](https://image.3001.net/images/20230501/1682950569_644fc9a96b09775909fcc.png!small)

这里的token为空。也就是只需要时间戳即可构造。

具体实现方法为 md5(token + timestamp)

![image](https://image.3001.net/images/20230501/1682950602_644fc9ca8536da9518770.png!small)

而未授权时实际上为md5(timestamp)。

是不是有点像是nps未授权访问？nps是默认把auth_key注释了，导致获取时为空字符串。

返回的信息如下

![image](https://image.3001.net/images/20230501/1682950690_644fca2282cd9400d96bc.png!small)

如果Error为空,获取到RunID则是正常的。

到此就可以自己实现一个frps爆破工具了。

核心逻辑在这

先用返回的消息判断是否是frp，如果是frp才开始检测未授权或者爆破

![image](https://image.3001.net/images/20230501/1682950715_644fca3b221d28c201170.png!small)

根据客户端版本、系统、架构、token生成构造出对应的认证消息并发送出去。

![image](https://image.3001.net/images/20230501/1682951822_644fce8e167700740e295.png!small)

![image](https://image.3001.net/images/20230501/1682951883_644fcecbe2797dd17976a.png!small)

如果成功获取到runID之类的信息则成功爆破frp server。

写完爆破出结果

![image](https://image.3001.net/images/20230501/1682951907_644fcee3b57810658fb3e.png!small)

测试下

![image](https://image.3001.net/images/20230501/1682951944_644fcf0872fde9953c370.png!small)

![image](https://image.3001.net/images/20230501/1682951957_644fcf15498322efa0f8c.png!small)

连接成功。

