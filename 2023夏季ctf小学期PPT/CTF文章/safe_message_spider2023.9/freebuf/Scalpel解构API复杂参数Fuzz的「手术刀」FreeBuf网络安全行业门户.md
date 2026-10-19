## **Scalpel 简介**

Scalpel是一款自动化Web/API漏洞Fuzz引擎，该工具采用被动扫描的方式，通过流量中解析Web/API参数结构，对参数编码进行自动识别与解码，并基于树结构灵活控制注入位点，让漏洞Fuzz向量能够应对复杂的编码与数据结构，实现深度漏洞挖掘。

  * 详细技术原理可参考KCon 2022议题：[《自动化API漏洞Fuzz实战》](http://mp.weixin.qq.com/s?__biz=Mzg3NDcwMDk3OA==&mid=2247484068&idx=1&sn=89ea1b1be48a0cb7f93a4750765719d1&chksm=cecd8b79f9ba026f7fbf52771e41272d684fc3af5175587f768082f8dbaee12d6d33bb892ceb&scene=21#wechat_redirect)

  * 目前我们的Fuzz引擎端已打包为一个小工具，内置100+漏洞POC，供大家试用：

<https://github.com/StarCrossPortal/scalpel>

##  **深度参数注入原理**

随着Web应用复杂度的提升与API接口的广泛使用，在HTTP应用漏洞Fuzz过程中，
**传统的「Form表单明文传参的模式」已经逐渐变为「复杂、嵌套编码的参数传递」。** 在此情况下，直接对参数内容进行注入或替换，无法深入底层的漏洞触发点。

漏洞Fuzz过程中需要对这些「结构体、编码」进行抽离，找到真正的注入点位，方可进行自动化漏洞测试。

![](https://image.3001.net/images/20221108/1667876693_6369c7551545165f3bd8c.png!small)

 **Scalpel拥有一个强大的数据解析和变异算法，它可以将常见的数据格式（json, xml,
form等）解析为树结构，然后根据poc中的规则，对树进行变异，包括对叶子节点和树结构的变异。变异完成之后，将树结构还原为原始的数据格式。**

Scalpel主体结构分为被动代理、Fuzz向量生成与验证、结果输出三个阶段：

![](https://image.3001.net/images/20221108/1667877093_6369c8e57e5550f9506d6.png!small)

漏洞检测部分，采用解析算法，深度解析流量请求中的参数，通过POC中设定的注入点和变异方式生成测试请求，发送请求之后，再通过POC中的验证规则进行成功性判断，最终输出Fuzz结果。

以下面这个JSON请求包为例，解析算法会将其转换为右边所示的树结构，无论其嵌套的层次有多深，解析算法会将其中的所有键值对都解析为一个树结构。然后可以对树中的叶子节点进行变异，也可以对树的整体结构上进行变异。在树上进行变异之后，将树按照原始的数据格式再还原回去，填充到请求报文中，形成变异的请求报文之后再发送出去。

![](https://image.3001.net/images/20221108/1667877799_6369cba739137eb82313a.png!small)

在原始参数结构解析之后，我们可以基于树结构来设定我们的测试向量注入方式：

对节点的变异方式有：

1\. 按数据类型注入payload

2\. 注入通用型payload

3\. 畸形数据替换

4\. 类型转换

![](https://image.3001.net/images/20221108/1667877878_6369cbf6760838e391cec.png!small)

对树结构的变异方式有：

1\. 替换object类型结构

2\. 插入节点

3\. 删除节点

![](https://image.3001.net/images/20221108/1667877903_6369cc0f75743d346d198.png!small)

##  **Scapel 功能介绍**

Scalpel扫描器支持以下漏洞检测或者挖掘场景：

1、检测目标已知安全的漏洞，包括CVE漏洞，热门框架、组件、中间件安全漏洞。

2、通用安全漏洞，包括但不限于SQL注入、XSS漏洞、文件上传、命令执行、文件读取等。

3、未知0day漏洞或者安全问题

同时支持多个参数位置的变异，包括：path、query、header、body等部分，具体可以参考Scalpel

漏洞POC编写指南（https://github.com/StarCrossPortal/scalpel/wiki/POC%E7%BC%96%E5%86%99%E6%8C%87%E5%8D%97）

![](https://image.3001.net/images/20221108/1667878142_6369ccfe9699b5d99cb90.png!small)

###  **案例1：CVE-2022-1388F5 BIG-IP** **API** **Unauthenticated RCE漏洞的检测**

简单了解下漏洞，具体可以参考之前[分析文章](https://mp.weixin.qq.com/s?__biz=Mzg3NDcwMDk3OA==&mid=2247483735&idx=1&sn=0b6ffbf45338fdac74d644bd4895c2c7&scene=21#wechat_redirect)（[【技术干货】F5
BIG-IP API Unauthenticated
RCE(CVE-2022-1388)分析](http://mp.weixin.qq.com/s?__biz=Mzg3NDcwMDk3OA==&mid=2247483735&idx=1&sn=0b6ffbf45338fdac74d644bd4895c2c7&chksm=cecd888af9ba019ce1bd8c218d821874e275aa77287966087ad045c99b8ff27419b92836db2b&scene=21#wechat_redirect)），我们要实现RCE，需要构造如下特殊的请求：

1、访问路径为/mgmt/tm/util/bash

2、Host为localhost或者127.0.0.1时，绕过验证赋予用户身份

3、Connection头加上X-F5-Auth-Token

4、body部分添加json形式的执行命令

![](https://image.3001.net/images/20221108/1667878624_6369cee0994381d6c0cc8.png!small)

为了检测到CVE-2022-1388漏洞是否存在，我们需要在发送构造的特殊请求后，识别响应中是否进行了命令执行。了解到整个检测的步骤后，开始编写漏洞POC

一一对应，在URL部分变异，变异方式为替换，变异值为/mgmt/tm/util/bash

![](https://image.3001.net/images/20221108/1667878718_6369cf3e96a9b5dd2cf55.png!small)![](https://image.3001.net/images/20221108/1667878730_6369cf4a5434d2e951056.png!small)在Host部分变异，变异方式为替换，变异值为localhost

![](https://image.3001.net/images/20221108/1667878745_6369cf5921843b7f7502b.png!small)![](https://image.3001.net/images/20221108/1667878756_6369cf64db971de98e8cc.png!small)对Heder部分的变异，变异方式为替换，变异值为Keep-Alive,X-F5-Auth-Token

![](https://image.3001.net/images/20221108/1667878770_6369cf726e29b67efea1d.png!small)![](https://image.3001.net/images/20221108/1667878779_6369cf7bd9475ecd514b1.png!small)对body部分的变异，变异方式为替换，变异值为我们需要执行的命令，这里执行id命令。

![](https://image.3001.net/images/20221108/1667878795_6369cf8b98e19f8c54335.png!small)![](https://image.3001.net/images/20221108/1667878805_6369cf957086577a24d71.png!small)最后对响应的匹配，使用正则识别id命令之后的结果。

![](https://image.3001.net/images/20221108/1667878820_6369cfa4dc59d0058ac33.png!small)在编辑好漏洞POC之后，运行扫描器进行检查。

![](https://image.3001.net/images/20221108/1667878899_6369cff36f7219d5e5202.png!small)在被动扫描的过程，实际获取到的数据包如下：

![](https://image.3001.net/images/20221108/1667878917_6369d00587fa0041d3de0.png!small)

如果存在漏洞，将会以html文件的形式记录存在漏洞的信息，查看此次扫描结果。

成功扫描出CVE-2022-1388F5 BIG-IP API Unauthenticated
RCE漏洞，漏洞的请求也变异无误，最后的响应中也是执行了id命令。

![](https://image.3001.net/images/20221108/1667878950_6369d0268d6dea8e0bdff.png!small)

###  **案例二：利用Scalpel工具挖掘多个0day漏洞**

Scalpel工具使用较为灵活，通过对检测目标变异响应的check，可以发现检测目标中未知的安全问题。

例如为发现某些API接口是否存在账号密码的泄露，可以在check部分利用正则表达式匹配具体的泄露数据。

![](https://image.3001.net/images/20221108/1667878978_6369d0420554aa362073c.png!small)为发现目标是否存在文件读取漏洞，可以在多个变异位置插入或者替换payload

![](https://image.3001.net/images/20221108/1667878991_6369d04fd34c95995fc12.png!small)![](https://image.3001.net/images/20221108/1667879003_6369d05be62f8a54d634d.png!small)为发现SQL注入漏洞，可以在query、Heder、body中的参数插入'
and 1=1类似的payload

![](https://image.3001.net/images/20221108/1667879019_6369d06b65f7382e7b2de.png!small)![](https://image.3001.net/images/20221108/1667879054_6369d08e8fa17e57a0b9f.png!small)星阑实验室成员利用如上的类似通用检测规则，挖掘多个0day漏洞，已提交给CNVD国家信息安全共享平台并被收录。

![](https://image.3001.net/images/20221108/1667879124_6369d0d4059e0c588e819.png!small)![](https://image.3001.net/images/20221108/1667879138_6369d0e224aab6662a5d0.png!small)同时发现某Apache开源项目的CVE漏洞，报告被该团队接受并正在修复，尚未披露。

![](https://image.3001.net/images/20221108/1667879223_6369d137c7de43c183703.png!small)

##  **工具地址**

 **GitHub地址下载地址：** https://github.com/StarCrossPortal/scalpel

目前已支持100+常见漏洞Fuzz向量与POC，持续维护中。

![](https://image.3001.net/images/20221108/1667879249_6369d1517186e21359237.png!small)Scalpel支持多个平台，请根据您的平台或者需求下载相应的版本。

![](https://image.3001.net/images/20221108/1667879266_6369d162c5d7e73841b21.png!small)

  

