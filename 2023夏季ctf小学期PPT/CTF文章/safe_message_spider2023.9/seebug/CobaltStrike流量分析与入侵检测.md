**作者：ainrm@薮猫科技安服团队  
公众号：薮猫科技（欢迎关注）<https://mp.weixin.qq.com/s/CjsqWrm70HVEnolZrRD8oA>**

### 一、前言

Cobaltstrike是一款用于团队协作的内网渗透工具，在攻防、测试中扮演着重要角色，其功能强大、使用人数众多，已被各大安全厂商列入重点"照顾"对象。常见的检测方式有基于内存和基于流量两种，本文从流量角度出发，通过抓包、解包来分析c2与beacon间的通信过程，并尝试从中提取流量特征转化为ids检测规则。

### 二、流量分析

#### 2.1 http-staging

![](https://images.seebug.org/content/images/2022/06/17/1655455720000-c1.png-w331s)

##### 01 stage下载

stager可执行文件`artifact.exe`运行后会有一个payload下载过程，使用http协议从指定服务器下载stage。

![](https://images.seebug.org/content/images/2022/06/17/1655455721000-2.png-w331s)

其中http请求路径不唯一，但都符合一个checksum8规则，即：路径的ascii之和与256取余计算值等于92。

  * `/Yle2`、`/cKTZ`、`/wQPD`

![](https://images.seebug.org/content/images/2022/06/17/1655455721000-3.png-w331s)

而下载的文件约211kb，解析后可以看到回连地址、加密字段、公钥等配置信息。

![](https://images.seebug.org/content/images/2022/06/17/1655455721000-4.png-w331s)

##### 02 beacon上线

随后beacon按设置的频率以`get`方法向c2服务器发起心跳请求，通过cookie携带靶机信息。

![](https://images.seebug.org/content/images/2022/06/17/1655455722000-5.png-w331s)

此时client界面可以看见目标机器上线：

![](https://images.seebug.org/content/images/2022/06/17/1655455722000-6.png-w331s)

##### 03 命令下发

c2服务器如果有任务下发，则放入http心跳请求返回包中。

![](https://images.seebug.org/content/images/2022/06/17/1655455722000-7.png-w331s)

当前下发的命令：`whoami`

![](https://images.seebug.org/content/images/2022/06/17/1655455723000-8.png-w331s)

##### 04 结果回传

beacon端处理完成后，通过`post`方法回传数据。

![](https://images.seebug.org/content/images/2022/06/17/1655455723000-9.png-w331s)

备注：`https-beacon`在`http-beacon`的基础上加入了tls层对流量加密，其他过程相似。

![](https://images.seebug.org/content/images/2022/06/17/1655455724000-10.png-w331s)

#### 2.2 dns-stagless

![](https://images.seebug.org/content/images/2022/06/17/1655455724000-c2.png-w331s)

##### 01 beacon上线

与staging阶段不同，stagless不需要额外加载stage，运行`dns-beacon.exe`后，beacon端向发起一个`A`记录查询，查询内容为16进制字符串地址，表示靶机已上线，c2服务器收到请求后回复`0.0.0.0`表示确认消息。

![](https://images.seebug.org/content/images/2022/06/17/1655455724000-12.png-w331s)

此时，客户端可以看见一个不同于http(s)上线的黑框记录。

![](https://images.seebug.org/content/images/2022/06/17/1655455724000-13.png-w331s)

##### 02 beacon激活

客户端控制台输入`checkin`或其他指令激活窗口，dns-beacon服务器支持`A`、`TXT`、`AAAA`三种方式下发payload，激活后默认使用`TXT`记录，流量中表现为`0.0.0.243`，除此之外还可以通过`mode`指令切换为`A`、`AAAA`记录，流量中表现为`0.0.0.241`、`0.0.0.245`，随后beacon端发起以`www`为首的`A`记录请求，向c2服务器传递靶机基础信息。

![](https://images.seebug.org/content/images/2022/06/17/1655455724000-14.png-w331s)

##### 03 命令下发

beacon准备接收c2任务，先发送以`api`开头的`A`记录请求告知c2服务器可以开始下发任务，即图中的`0.0.0.243-TXT`方式，随后发起以`api`开头的`TXT`记录请求等待c2服务器返回数据。

![](https://images.seebug.org/content/images/2022/06/17/1655455724000-15.png-w331s)

##### 04 结果回传

beacon端执行完命令后，再向c2服务器发起以`post`开头的`A`记录查询回传执行结果。

![](https://images.seebug.org/content/images/2022/06/17/1655455725000-16.png-w331s)

### 三、特征提取

上一节对使用默认配置文件的cobaltstrike交互过程进行了分析，流量中存在很多特征，但在实际攻防、测试中红队常使用[Malleable-C2-Profiles](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2_main.htm)来修改c2配置实现应用层流量混淆，从而绕过部分安全设备监控，这里就以profile为界限将特征划分为基础特征和强特征两个方向，即：

  * 基础特征：使用默认配置时存在的特征，可通过修改profile文件或证书将其隐藏；
  * 强特征：需要修改cobaltstrike源码才能较好去除的这部分特征。

#### 3.1 基础特征

##### 01 http请求

http-beacon通信中，默认使用get方法向`/dpixel`、`/__utm.gif`、`/pixel.gif`等地址发起请求，同时请求头存在cookie字段并且值为base64编码后的非对算算法加密数据。

    
    
    # default c2-http profile
    # define indicators for an HTTP GET
    http-get {
        # Beacon will randomly choose from this pool of URIs
        set uri "/ca /dpixel /__utm.gif /pixel.gif /g.pixel /dot.gif /updates.rss /fwlink /cm /cx /pixel /match /visit.js /load /push /ptj /j.ad /ga.js /en_US/all.js /activity /IE9CompatViewList.xml";
    
        client {
            # base64 encode session metadata and store it in the Cookie header.
            metadata {
                base64;
                header "Cookie";
            }
        }
    
        server {
            # server should send output with no changes
            header "Content-Type" "application/octet-stream";
    
            output {
                print;
            }
        }
    }

![
](https://images.seebug.org/content/images/2022/06/17/1655455725000-17.png-w331s)

##### 02 https证书

https-beacon通信中，默认使用空证书建立加密通道，流量中可以看见这一过程。

![
](https://images.seebug.org/content/images/2022/06/17/1655455725000-18.png-w331s)

##### 03 dns异常返回值

dns-beacon通信中，默认使用`cdn.`、`www6.`、`api.`、`www.`、`post.`为开头发起dns请求，并且查询结果伴随`0.0.0.0`、`0.0.0.80`、`0.0.0.241`等非常规ip。

![
](https://images.seebug.org/content/images/2022/06/17/1655455726000-19.png-w331s)

#### 3.2 强特征

##### 01 chechsum8

运行staging模式的pe文件，会向指定服务器的checksum8路径发起请求来下载stage。

![
](https://images.seebug.org/content/images/2022/06/17/1655455726000-20.png-w331s)

即使通过profile文件改变下载地址，但c2服务器依然会对checksum8地址请求作出响应。

    
    
    # https://github.com/threatexpress/malleable-c2/blob/master/jquery-c2.4.6.profile
    http-stager {  
        set uri_x86 "/jquery-3.3.1.slim.min.js";
        set uri_x64 "/jquery-3.3.2.slim.min.js";
        ...
    }

![
](https://images.seebug.org/content/images/2022/06/17/1655455726000-21.png-w331s)

##### 02 ja3/ja3s

ja3和ja3s分别代表tls握手阶段的client-hello、server-hello的数据集合计算出的哈希值（md5），相同版本相同系统下指纹相同，该特征与操作系统、cobaltstrike版本有关，profile文件无法对其修改。

  1. win10-https-beacon-ja3指纹：`72a589da586844d7f0818ce684948eea`

![
](https://images.seebug.org/content/images/2022/06/17/1655455727000-22.png-w331s)

  1. centos-cs4.4-ja3s指纹：`fd4bc6cea4877646ccd62f0792ec0b62`

![
](https://images.seebug.org/content/images/2022/06/17/1655455727000-23.png-w331s)

#### 3.3 小结

![
](https://images.seebug.org/content/images/2022/06/17/1655455728000-24.png-w331s)

### 四、规则编写

> 根据前面提取的特征，共整理出 17 条 ids
> 规则。这一节对其中的5条进行讲解，其余规则和过程文件已上传至[github](https://github.com/ainrm/cobaltstrike-> suricata-rules)

#### 4.1 checksum8检查

同时命中以下三条规则则触发告警：

  1. 由客户端发起并与目标服务器建立连接：`flow: established, to_server;`

  2. 请求路径长度为5：`urilen:4<>6;`

  3. 调用lua计算路径的ascii之和并与256做取余操作，结果为92：`luajit:checksum8_check.lua;`

![
](https://images.seebug.org/content/images/2022/06/17/1655455728000-25.png-w331s)

完整规则：

    
    
    # suricata规则
    # http-beacon-staging，向c2服务器发起get请求，下载大小约210kb的stager，请求地址符合checksum8规则
    # 调用lua检查uri是否符合checksum8规则：计算uri的ascii之和并与256做取余计算，余数为92则符合规则
    alert http any any -> any any (gid:3333; sid:30001; rev:1; \
        msg:"http-beacon-checksum8-path-parse"; \
        classtype: http-beacon; \
        flow: established, to_server; \
        urilen:4<>6; \
        luajit:checksum8_check.lua; \
    )
    
    
    # checksum8_check.lua
    function init (args)
        local needs = {}
        needs["http.uri"] = tostring(true)
        return needs
    end
    
    function match(args)
        local uri_raw = tostring(args["http.uri"])
        local uri = string.sub(uri_raw, 2, -1) -- 去除uri中的"/"
        local sum = 0
    
        for i=1,#uri do
            local x = string.sub(uri,i,i)
            sum = sum + string.byte(x)
        end
    
        if (sum % 256) == 92 then
            return 1 -- 符合checksum8规则，匹配成功
        else 
            return 0 -- 不符合checksum8规则，匹配失败
        end
    end

#### 4.2 ja3/ja3s检查

满足其中之一则命中规则触发告警：

  1. 采用黑名单机制，正则匹配由beacon端发起请求的ja3指纹；
  2. 采用黑名单机制，正则匹配由c2端返回的ja3s指纹。

![
](https://images.seebug.org/content/images/2022/06/17/1655455729000-26.png-w331s)

完整规则：

    
    
    # https-beacon-ja3指纹，client-hello
    alert tls any any -> any any (gid:6666; sid:30005; rev:1; \
        msg:"https-beacon-ja3-hash"; \
        classtype: https-beacon; \
        ja3.hash; pcre:"/652358a663590cfc624787f06b82d9ae|4d93395b1c1b9ad28122fb4d09f28c5e|72a589da586844d7f0818ce684948eea|a0e9f5d64349fb13191bc781f81f42e1/"; \
    )
    
    
    # https-beacon-ja3s指纹，server-hello
    alert tls any any -> any any (gid:6666; sid:30006; rev:1; \
        msg:"https-beacon-ja3s-hash"; \
        classtype: https-beacon; \
        ja3s.hash; pcre:"/fd4bc6cea4877646ccd62f0792ec0b62|15af977ce25de452b96affa2addb1036|b742b407517bac9536a77a7b0fee28e9/"; \
    )

#### 4.3 异常dns检查

##### 01 A记录异常返回

同时命中以下两条规则则触发告警：

  1. dns流量内容包含二进制数`00 01 00 01 00 00 00`：`content:"|00 01 00 01 00 00 00|";`
  2. dns返回包以`0.0.0.241`结尾：`content:"|00 00 00 f1|"; nocase; endswith;`

![
](https://images.seebug.org/content/images/2022/06/17/1655455729000-27.png-w331s)

完整规则：

    
    
    # dns-beacon，匹配dns-beacon发起上线/心跳请求后，c2服务器的返回包，选择后续使用A记录
    # Type: A, Class: IN, 0.0.0.241
    alert dns any any -> any any (gid:9999; sid:30011; rev:1; \
        msg:"dns-beacon-live-response"; \
        classtype: dns-beacon; \
        content:"|00 01 00 01 00 00 00|"; \
        content:"|00 00 00 f1|"; nocase; endswith; \
    )

##### 02 txt记录异常返回

同时命中以下四条规则则触发告警：

  1. 由c2端发起请求：`flow:to_client;`
  2. dns流量内容包含`api`字符：`pcre:"/api/";`
  3. dns流量内容包含二进制数`00 01 00 01 00 00 00`：`content:"|00 01 00 01 00 00 00|";`
  4. dns返回包以`0.0.0.50`结尾：`content:"|00 00 00 50|"; endswith;`

![
](https://images.seebug.org/content/images/2022/06/17/1655455730000-28.png-w331s)

完整规则：

    
    
    # dns-beacon，匹配dns-beacon使用TXT方式向c2服务器发起payload下载请求后，c2服务器的返回包
    # api ==> TXT 
    # Type: A, Class: IN, 0.0.0.80
    alert udp any any -> any any (gid:9999; sid:30015; rev:1; \
        msg:"dns-beacon-getpayload-response"; \
        classtype: dns-beacon; \
        flow:to_client; \
        pcre:"/api/"; \
        content:"|00 01 00 01 00 00 00|"; \
        content:"|00 00 00 50|"; endswith; \
    )

#### 4.4 测试

##### 01 白流量

hexdump抓取访问baidu站点流量，测试结果没有产生误报。

![
](https://images.seebug.org/content/images/2022/06/17/1655455730000-29.png-w331s)

##### 02 http-beacon

识别出stage下载、心跳请求、执行结果回传三种流量。

![
](https://images.seebug.org/content/images/2022/06/17/1655455730000-30.png-w331s)

##### 03 https-beacon

识别出ja3、ja3s、cert三种cs流量。

![
](https://images.seebug.org/content/images/2022/06/17/1655455731000-31.png-w331s)

##### 04 dns-beacon

识别出心跳请求、结果回传、元数据提交、payload下载四种cs流量。

![
](https://images.seebug.org/content/images/2022/06/17/1655455731000-32.png-w331s)

### 五、总结

cobaltstrike默认配置文件具有较为明显的流量特征，容易被监管设备查杀，使用malleable-c2、证书等手法能够在一定程度上混淆流量，但在整个tcp/ip模型中依然存在蛛丝马迹，无法脱离cobaltstrike框架。对攻击方来说想要究极隐藏，笔者认为还得要从源头入手，在魔改cs或自研网络通信模型上想想办法，同时这对防守方来说提出了更高的要求，能否应对来自高级攻击者发起的挑战。

### 六、参考

  * <https://www.52pojie.cn/thread-1426936-1-1.html>
  * <https://www.52pojie.cn/thread-1607839-1-1.html>
  * <https://suricata.readthedocs.io/en/latest/rules/index.html>
  * <https://wbglil.gitbook.io/cobalt-strike/cobalt-strike-yuan-li-jie-shao/cs-mu-biao-shang-xian-guo-cheng>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1922/>

