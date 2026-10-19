## 0x00前言

微软公布了一个反序列化代码执行漏洞，[CVE-2021-42321](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-42321)，经过身份认证的攻击者可以通过EWS接口将payload写入UserConfiguration中，并通过GetClientAccessToken触发payload从而在目标服务器上执行代码。本篇通过对POC的跟踪分析漏洞的利用过程。

 **漏洞影响：**

Microsoft Exchange Server 2019 CU10/CU11

Microsoft Exchange Server 2016 CU21/CU22

 **分析环境：**

  * Server 2016
  * Exchange 2016 CU21 (由CU15[升级](https://download.microsoft.com/download/7/d/5/7d5c319b-510b-4a2c-a77a-099c6f30ab54/ExchangeServer2016-x64-CU21.ISO)到CU21)

## 0x01补丁查看

<https://www.catalog.update.microsoft.com/Search.aspx?q=exchange%202016%20cu21>

![1638177264_61a499f0c6054c8e26fa5.png!small?1638177280208](https://image.3001.net/images/20211129/1638177264_61a499f0c6054c8e26fa5.png!small?1638177280208)

KB5007012 是在10月份发布的，通过两个补丁的对比查看修改了哪些文件。

使用Telerik
对比[KB5007409](https://www.catalog.update.microsoft.com/ScopedViewInline.aspx?updateid=c65f8a4e-66a7-483a-b156-4a19902797a6)、[KB5007012](https://www.catalog.update.microsoft.com/ScopedViewInline.aspx?updateid=4af0ef18-9baa-4e06-81b6-86ed4f138f5c)的不同，一共有几百个不同的DLL文件，为了快速找到漏洞点，搜索反序列化的关键字

![1638177278_61a499fee079b442c76bc.png!small?1638177294483](https://image.3001.net/images/20211129/1638177278_61a499fee079b442c76bc.png!small?1638177294483)

Microsoft.Exchange.Compliance.dll中发现删除了几个class

![1638177287_61a49a071883cb734ef0b.png!small?1638177302595](https://image.3001.net/images/20211129/1638177287_61a49a071883cb734ef0b.png!small?1638177302595)

可以看到
TypedBinaryFormatter、TypedSerializationFormatter、TypedSoapFormatter这几个class里有反序列化的操作，同时在最新补丁中被删除。

## 0x02漏洞分析

网上已有payload，我们就利用payload分析漏洞的整个利用过程

dnSpy设置断点，附加到进程 w3wp.exe的MSExchangeServicesAppPool
中（如果不知道是哪个进程，可以将所有的w3wp.exe进程全部附加进去）

![1638177297_61a49a114928fbbbcc98a.png!small?1638177312707](https://image.3001.net/images/20211129/1638177297_61a49a114928fbbbcc98a.png!small?1638177312707)

使用ysoserial构造反序列化数据，gadget 使用 TypeConfuseDelegate

![1638177308_61a49a1c98235379296e6.png!small?1638177324155](https://image.3001.net/images/20211129/1638177308_61a49a1c98235379296e6.png!small?1638177324155)

运行payload，断点停住

调用堆栈如下：

![1638177313_61a49a21e4798cfc45988.png!small?1638177329534](https://image.3001.net/images/20211129/1638177313_61a49a21e4798cfc45988.png!small?1638177329534)

 **漏洞调用链：**

进入LoadMasterTable，解析UserConfiguration 的信息（UserConfiguration可以通过EWS接口操作）

![1638177327_61a49a2fb23f78698eb7c.png!small?1638177343282](https://image.3001.net/images/20211129/1638177327_61a49a2fb23f78698eb7c.png!small?1638177343282)

通过 参数 configName，configType，folderId获取对应配置信息

![1638177334_61a49a369d4d428129f60.png!small?1638177350140](https://image.3001.net/images/20211129/1638177334_61a49a369d4d428129f60.png!small?1638177350140)

参数值如下

![1638177339_61a49a3b4b9cd648c7ed3.png!small?1638177354752](https://image.3001.net/images/20211129/1638177339_61a49a3b4b9cd648c7ed3.png!small?1638177354752)

接着进入Microsoft.Exchange.Data.ApplicationLogic.Extension.OrgExtensionSerializer
类中对userConfiguration进行反序列化操作

![1638177346_61a49a427906b8ef3c108.png!small?1638177362183](https://image.3001.net/images/20211129/1638177346_61a49a427906b8ef3c108.png!small?1638177362183)

首先将配置信息实例化成一个 stream对像，

![1638177417_61a49a89958340f8557f8.png!small?1638177433097](https://image.3001.net/images/20211129/1638177417_61a49a89958340f8557f8.png!small?1638177433097)

其中formatter是IClientExtensionCollectionFormatter的实例化对象，

![1638177432_61a49a9831246e7c4bdaa.png!small?1638177447722](https://image.3001.net/images/20211129/1638177432_61a49a9831246e7c4bdaa.png!small?1638177447722)

调用IClientExtensionCollectionFormatter.Deserialize函数

![1638177437_61a49a9dae88f5acf9d8a.png!small?1638177453283](https://image.3001.net/images/20211129/1638177437_61a49a9dae88f5acf9d8a.png!small?1638177453283)

接着将steam内容传入TypeBinaryFormatte.DeserializeObject中，执行反序列化

![1638177453_61a49aada1fca3535b713.png!small?1638177469189](https://image.3001.net/images/20211129/1638177453_61a49aada1fca3535b713.png!small?1638177469189)

调用 TypeBinaryFormatter类的Deserialize 方法，创建一个ChainedSerializationBinder对象

![1638177465_61a49ab99b4929f5538ea.png!small?1638177481102](https://image.3001.net/images/20211129/1638177465_61a49ab99b4929f5538ea.png!small?1638177481102)

传入allowList参数是一个白名单列表，内容如下：

![1638177479_61a49ac7068913dd8a870.png!small?1638177494550](https://image.3001.net/images/20211129/1638177479_61a49ac7068913dd8a870.png!small?1638177494550)

![1638177482_61a49aca62672f45810a4.png!small?1638177497807](https://image.3001.net/images/20211129/1638177482_61a49aca62672f45810a4.png!small?1638177497807)

白名单中允许使用System.DelegateSerializetionHolder

ChainedSerializationBinder实现方法如下

![1638177491_61a49ad3201c83633596d.png!small?1638177506629](https://image.3001.net/images/20211129/1638177491_61a49ad3201c83633596d.png!small?1638177506629)

![1638177498_61a49ada378f0dc854a72.png!small?1638177513737](https://image.3001.net/images/20211129/1638177498_61a49ada378f0dc854a72.png!small?1638177513737)

其中定义了一个gadget黑名单列表，包含了常用的gadget

![1638177514_61a49aeae36423aec7b98.png!small?1638177530494](https://image.3001.net/images/20211129/1638177514_61a49aeae36423aec7b98.png!small?1638177530494)

![1638177518_61a49aeee661a0df70e03.png!small?1638177534447](https://image.3001.net/images/20211129/1638177518_61a49aeee661a0df70e03.png!small?1638177534447)

但由于开发者的失误，导致其中一个gadget黑名单没有生效，正确的写法是System.Security.Claims.ClaimsPrincipal
，所以我们可以利用这个gadget进行反序列化攻击。

objectReader初始化后，调用ObjectReade.Deserialize方法

![1638177527_61a49af75b87a75710ccc.png!small?1638177543002](https://image.3001.net/images/20211129/1638177527_61a49af75b87a75710ccc.png!small?1638177543002)

接着会有一个白名单和黑名单的验证，如果不合法直接抛出异常

![1638177542_61a49b06a558894615d4b.png!small?1638177558214](https://image.3001.net/images/20211129/1638177542_61a49b06a558894615d4b.png!small?1638177558214)

验证通过后，经过一系列操作进入System.Collections.Generic.SortedSet.OnDeserialization中，获取array的值并进行Add操作

![1638177552_61a49b102b6f16364ce19.png!small?1638177567822](https://image.3001.net/images/20211129/1638177552_61a49b102b6f16364ce19.png!small?1638177567822)

在Add函数里，会对array中的两个元素进行Compare（System.Collections.Generic.ComparisonComparer）操作

![1638177561_61a49b19c204fc16a4d7a.png!small?1638177577280](https://image.3001.net/images/20211129/1638177561_61a49b19c204fc16a4d7a.png!small?1638177577280)

Compare的过程中会调用System.Diagnostics.Process创建进程，从而执行命令。

![1638177568_61a49b20b243b513cc21e.png!small?1638177584232](https://image.3001.net/images/20211129/1638177568_61a49b20b243b513cc21e.png!small?1638177584232)

 **payload** **分析：**

利用EWS（Exchange Web
Service微软提供的一个访问Exchange资源的接口）写入用户配置信息，写入的时候将payload写进去；写入前需要先将旧的配置信息删掉，删除的时候需要传入参数folderId的值；
这个值可以通过 GetFolder 获取 ；最后利用GetClientAccessToken 触发反序列化

1）[GetFolder](https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getfolder-operation)

![1638177595_61a49b3b73b71a2d75ae6.png!small?1638177610988](https://image.3001.net/images/20211129/1638177595_61a49b3b73b71a2d75ae6.png!small?1638177610988)

2）DeleteUserConfiguration

![1638177626_61a49b5ace84432ec1b57.png!small?1638177642433](https://image.3001.net/images/20211129/1638177626_61a49b5ace84432ec1b57.png!small?1638177642433)

3）CreateUserConfiguration（写入生成的序列化数据）

从官方文档可知 UserConfigurationType有5种类型，由于反序列化数据是流式的，所以使用BinaryData。

![1638177640_61a49b68d7d9f4f1fe0f3.png!small?1638177656289](https://image.3001.net/images/20211129/1638177640_61a49b68d7d9f4f1fe0f3.png!small?1638177656289)

![1638177644_61a49b6c4f2876445d5cc.png!small?1638177659852](https://image.3001.net/images/20211129/1638177644_61a49b6c4f2876445d5cc.png!small?1638177659852)

4）[GetClientAccessToken](https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/getclientaccesstoken-operation)

![1638177652_61a49b7471ba57bd3141c.png!small?1638177668040](https://image.3001.net/images/20211129/1638177652_61a49b7471ba57bd3141c.png!small?1638177668040)

运行结果如下：

![1638177658_61a49b7a0c6dfe479572f.png!small?1638177673720](https://image.3001.net/images/20211129/1638177658_61a49b7a0c6dfe479572f.png!small?1638177673720)

注：另一个gadget，System.Security.Claims.ClaimsPrincipal经过测试也是可用的。

## 0x03解决方案

微软已经针对该漏洞发布了补丁，补丁链接：https://www.microsoft.com/en-us/download/details.aspx?id=103645

## 0x04参考链接

<https://peterjson.medium.com/some-notes-about-microsoft-exchange-deserialization-rce-cve-2021-42321-110d04e8852>

<https://gist.github.com/testanull/0188c1ae847f37a70fe536123d14f398>

<https://docs.microsoft.com/en-us/previous-versions/office/developer/exchange-server-2010/dd899825(v=exchg.140)>

<https://docs.microsoft.com/zh-cn/exchange/client-developer/web-service-reference/userconfiguration>

作者:雨夜

