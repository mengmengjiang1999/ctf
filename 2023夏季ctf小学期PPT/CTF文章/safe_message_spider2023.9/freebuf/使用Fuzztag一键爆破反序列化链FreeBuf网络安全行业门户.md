  

# 背景

Yakit 新增的 Yso-Java-Hack 功能可以让我们生成反序列化利用的 payload ，通过图形化的方式简化了生成 payload
的过程，但发包过程由于需要针对不同的目标站点对 payload 进行编码，所以这部分留给了用户，自行通过Yak进行编码和发包。

......还是要写代码。在@rr师傅的建议下，我为 Fuzztag 增加了几个新标签，方便一键爆破利用链。

# 新增标签

新增了几个标签：`yso:exec、yso:urldns、yso:headerecho、yso:bodyexec、headerauth、yso:dnslog`，方便大家进行反序列化漏洞的简单手工测试。如果需要更复杂的漏洞利用，可以使用
Yso-Java Hack 生成 hex 格式 payload ，然后使用 hexdec 标签在Fuzztag中调用。

## 命令执行

`yso:exec`标签用于命令执行测试，参数是需要执行的命令。这里介绍下命令执行链的分类，可以分为代码执行链和命令执行链，命令执行链是通过反射调用RuntimeExec执行的，而代码执行链可以加载任意java代码执行，所以代码执行链可以实现更多操作。

## URLDNS

`yso:urldns`标签用于反序列化漏洞检测。参数是一个url，其原理是通过URL对象反序列化时触发dns查询。

## DNSLOG

`yso:dnslog`标签用于dns出网的利用链爆破。它有两个参数，第一个参数是一个域名，第二个参数是域名前缀。第一个参数是必填参数，第二个参数是可选的，后面会介绍使用方法。原理上是通过`InetAddress.getByName`方法实现，与URLDNS链原理相同。

## Header回显

`yso:headerecho`标签可用于不出网的站点反序列化漏洞检测，它支持tomcat和weblogic的header回显，它需要两个参数，分别是需要回显的header的key和value，例如`{{yso:headerecho(flag|ok)}}`，需要注意的是，使用此标签需要设置header：`Accept-Language: zh-CN,zh;q=1.9`

## Body回显

`yso:headerecho`标签用于不出网情况的命令执行回显，同样支持tomcat和weblogic的回显，它需要一个参数，例如这样`{{yso:headerecho(whoami)}}`，同样的，使用此标签需要设置header：`Accept-Language: zh-CN,zh;q=1.9`

## Header标志

由于header和body回显都需要设置header:`Accept-Language: zh-CN,zh;q=1.9`，每次设置比较麻烦，所以提供了一个新标签：`headerauth`，会自动生成`Accept-Language: zh-CN,zh;q=1.9`，使用时可以这样用`{{headerauth}}`

# 实战演练

## 思路分析

在开始靶场测试前先分析下测试流程。首先要判断出目标站点是否有反序列化漏洞，再爆破反序列化利用链，得到一条可以代码执行或命令执行的链，这个过程需要想办法得知是否命令执行成功了。最后利用这条链完成后续攻击。

总结下流程大概是这样的

  

![](https://image.3001.net/images/20221230/1672372109_63ae5f8d21d44e0a89833.jpg!small)

## 环境搭建

在本地搭建一个测试环境，源码如下

![](https://image.3001.net/images/20221230/1672372094_63ae5f7e8f7c4d261e269.png!small)

这里已经给需要测试的师傅打包好了docker环境，docker运行下就可以:`docker run -p 8080:8080 -itd
--name="deserilize_test" z3r0ne0/deserilize_test`

## 漏洞检测

先使用urldns检测目标是否存在漏洞

![](https://image.3001.net/images/20221230/1672372121_63ae5f99b26a2aa156ee4.png!small)

![](https://image.3001.net/images/20221230/1672372130_63ae5fa278f3dcbcc179d.png!small)

如图，未收到dnslog记录，说明可能目标机器不出网，那再继续测试下不出网回显。

使用`yso:headerecho和yso:bodyecho`时要注意下，需要在header中加入`{{headerauth}}`并设置并发数量为1，随机延迟的最大和最小值要大于1，原因是回显链的原理是遍历所有请求，并在header中有特殊标志的的请求的header中添加元素，这种方式在并发情况下会有问题。

![](https://image.3001.net/images/20221230/1672372139_63ae5fab5eb1727d20b99.png!small)

注意看我设置的回显header的kay和value都很长，目的是可以通过header头相似度找出成功回显的请求

![](https://image.3001.net/images/20221230/1672372148_63ae5fb4487fdafa5691e.png!small)

如图，CommonsBeanutils183NOCC链的相似度明显小了0.1，看下响应，发现成功回显。

![](https://image.3001.net/images/20221230/1672372158_63ae5fbe50c8c4e65c588.png!small)

再测试下命令执行回显，如图

![](https://image.3001.net/images/20221230/1672372166_63ae5fc6a907c91bae42b.png!small)

CommonsBeanutils183NOCC和CommonsCollectionsK1的响应大小明显不正常，在详情中可以看到命令执行成功。

![](https://image.3001.net/images/20221230/1672372176_63ae5fd09689455ecbd8d.png!small)

至此，我们就得到了 CommonsBeanutils183NOCC 和 CommonsCollectionsK1 两条可以代码执行的利用链了。

## 补充案例

如果回显失败，可能是不支持该中间件回显，那就可以使用`yso:dnslog`去爆破可代码执行的链，也有可能代码执行链用不了，那就使用`yso:exec`爆破命令执行链。

先试下`yso:dnslog`爆破，使用时注意，此标签第一个参数是域名，第二个参数是可选参数，如果设置了，那么每条链调用的域名将会是`<参数2><编号>.<域名>`

![](https://image.3001.net/images/20221230/1672372186_63ae5fda2a7da059712d6.png!small)

如图，收到dnslog，可以看到标号9和标号3对应的链触发了dnslog

![](https://image.3001.net/images/20221230/1672372194_63ae5fe2b1164116860e7.png!small)

在 Responses 的 Payloads 中可以看见对应的链为 CommonsBeanutils183NOCC 和
CommonsCollectionsK1。

![](https://image.3001.net/images/20221230/1672372203_63ae5feb25f228d7eeacb.png!small)

如果还是收不到dnslog，那就只能用`yso:exec`试试反弹shell、在web目录写文件、延时等操作了，这里测试下写文件。

![](https://image.3001.net/images/20221230/1672372212_63ae5ff42d18b047d72ca.png!small)

进入docker可以看见写入文件成功

![](https://image.3001.net/images/20221230/1672372220_63ae5ffcd91104d446486.png!small)

## 打内存马

可以看另一篇文章 《Yso-Java Hack 进阶：利用反序列化漏洞打内存马》

# 总结

新增的几个tag几乎可以覆盖大部分反序列化漏洞利用场景了，师傅们使用时需要根据目标出网情况，是否有代码执行链去判断，可以参考前面的流程图。如果有可代码执行的链，可以根据出网情况选择打入内存马、直接上线cs或其它操作，需要打入内存马时可以使用
Yso-Java Hack 直接生成hex格式的payload，然后使用hexdec标签调用就可以了。

