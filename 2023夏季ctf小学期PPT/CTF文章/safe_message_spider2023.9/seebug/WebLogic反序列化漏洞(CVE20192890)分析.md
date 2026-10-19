**作者：Lemon@平安银河安全实验室  
公众号：[WebLogic
反序列化漏洞(CVE-2019-2890)分析](https://mp.weixin.qq.com/s?__biz=MzIwNTcxNTczMQ==&mid=2247484313&idx=1&sn=e2fb990c404776ae3126c2b31c78acfd&chksm=972de3e5a05a6af3910463e4a51cb814f33e0a7c7bbf4b40240a9da804f6c5fb1a108593ae47&mpshare=1&scene=1&srcid=1101Oy6BoKWAH30I073wxFyL&sharer_sharetime=1572594005245&sharer_shareid=54b578ae6292d46346149e4cb8ba012b&key=2bbffe7bbfb7d31b83c5cbb0673a37dff008c87628e2b0afa361f0d89590fbe9587c592973e5231a1f50f9afd97bf5f7ae340e32be735a3afca12d95ce3e6d782a02dfe29a6c1797ddaff7ab52e30515&ascene=1&uin=MzM5ODEzOTY3MQ%3D%3D&devicetype=Windows+10&version=62060833&lang=zh_CN&pass_ticket=pqMeVE3dJOKEVHbro%2BnYr7GwYEVqCRiP3DBRNPJ6e32rKlDWo3hKaAZK75MuqZ1j
"分析")**

## **漏洞简介**

2019年10月16日，WebLogic官方发布了安全补丁公告，修复了包含CVE-2019-2890等高危漏洞。Weblogic在利用T3协议进行远程资源加载调用时，默认会进行黑名单过滤以保证反序列化安全。漏洞CVE-2019-2890绕过了Weblogic的反序列化黑名单，使攻击者可以通过T3协议对存在漏洞的Weblogic组件实施远程攻击，但该漏洞利用条件较高，官方也归类为需要身份认证。
![](https://images.seebug.org/content/images/2019/11/1471893a-b7d1-4180-983b-0ed12849dda1.jpg-w331s)

## **影响版本**

WebLogic Server 10.3.6.0

WebLogic Server 12.1.3.0

WebLogic Server 12.2.1.3

## **漏洞分析**

漏洞代码位于weblogic.jar中weblogic.wsee.jaxws.persistence.PersistentContext.class文件，它的readObject函数调用了readSubject函数，readSubject函数中使用了ObjectInputStream.readObject来反序列化对象。
![](https://images.seebug.org/content/images/2019/11/93f987bb-5797-4c1b-bb13-7c83b1b7f045.jpg-w331s)

查看对应的writeObject的逻辑，只要我们给对应的localObjectOutputStream.writeObject()序列化一个恶意对象，则PersistentContext对象被反序列化时，它的readObject函数被调用，readSubject函数中对恶意对象进行反序列化。因此通过T3发送精心伪造的PersistentContext对象，则可成功绕过黑名单检查。
![](https://images.seebug.org/content/images/2019/11/cc6072bf-e2d6-42eb-9603-d10e8d385ba8.jpg-w331s)

## **漏洞复现**

为了让writeObject函数中的localObjectOutputStream.writeObject()序列化一个恶意对象，我们直接对PersistentContext类进行修改。

打开idea新建一个项目，引入需要的Jar文件。在项目中新建一个package，名为weblogic.wsee.jaxws.persistence，在这个包下创建PersistentContext.class文件，复制原来的内容进行修改。

我们在PersistentContext.class文件中新增一个getObject()函数，用于获取恶意对象。然后把localObjectOutputStream.writeObject()函数的参数替换。
![](https://images.seebug.org/content/images/2019/11/eaa8848e-077c-4ca9-ba36-7ce797b00cb2.jpg-w331s)

然后在项目中创建一个Poc.class文件，新建PersistentContext对象对其进行序列化操作，序列化后存储到poc文件中。

此时我们使用T3发送payload发现靶机日志提示报错：
![](https://images.seebug.org/content/images/2019/11/ba6afd8e-2808-4db7-8ac2-722034cbbe6a.jpg-w331s)

根据报错提示定位到代码，发现readSubject函数中有个解密过程：
![](https://images.seebug.org/content/images/2019/11/2e015956-a54c-4c52-94c7-2a0cdfdf64e7.jpg-w331s)

此时我们再次检查writeSubject函数，猜测序列化时加密没有成功，导致反序列化时解密报错：
![](https://images.seebug.org/content/images/2019/11/9318fdd7-1f25-4edf-9505-be97f8186cb7.jpg-w331s)

跟进加密函数：
![](https://images.seebug.org/content/images/2019/11/b64ca7fb-96d6-4872-bf87-57f3c074e072.jpg-w331s)

由于我们idea建立的项目中没有SerializedSystemIni.dat文件，直接返回null，因此加密没有成功，导致反序列化失败。
![](https://images.seebug.org/content/images/2019/11/27c84ff7-bec8-4856-a210-f98a0eb25e1e.jpg-w331s)

因此我们需要修改writeSubject()函数，但由于getEncryptionService属性为private，需再新建EncryptionUtil.class文件,把getEncryptionService()函数属性改成public：
![](https://images.seebug.org/content/images/2019/11/63c0352c-ee0e-4496-9658-8345f5d42a00.jpg-w331s)

并且把SerializedSystemIni.dat文件复制到我们idea项目中。由于SerializedSystemIni.dat是密钥文件，各不相同且无法猜解，这里也就是这个漏洞需要身份认证的原因。

此时再测试发送payload，可爱的计算器成功弹出。

![](https://images.seebug.org/content/images/2019/11/3e4eccb9-90fb-40b8-8df1-7e8f2e3a3d69.jpg-w331s)

## **安全建议**

1、禁用 T3 协议：如果您不依赖 T3 协议进行JVM通信，可通过暂时阻断 T3 协议缓解此漏洞带来的影响。

2、排查弱口令

3、升级补丁

## **相关链接**

<https://www.oracle.com/security-alerts/cpuoct2019.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1069/>

