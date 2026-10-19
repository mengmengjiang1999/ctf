## **情报背景**

时隔两年，一个可能名为Blue Mockingbird的攻击者再次出现。该攻击者一直在利用 Telerik UI Web 应用程序框架中存在三年的漏洞来控制
Web 服务器，并在此过程中安装 Cobalt Strike Beacon和挖矿病毒XMRig Miner。研究员表示此次的攻击者比两年前的Blue
Mockingbird具有更加完善的感染链和相对成熟的C2机制。

 **组织名称**

|

Blue Mockingbird  
  
---|---  
  
 **战术标签**

|

执行，防御规避，持久化  
  
 **技术标签**

|

反序列化，GPO维持权限  
  
 **情报来源**

|

https://news.sophos.com/en-us/2022/06/15/telerik-ui-exploitation-leads-to-cryptominer-cobalt-strike-infections/  
  
  

##  **01** 攻击技术分析

Telerik UI for ASP.NET AJAX 是一组用于构建 Web 应用程序的组件和主题，CVE-2019-18935 是Telerik UI
的一个早已报告过的反序列化漏洞。

利用CVE-2019-18935漏洞有一个前置条件是异步上传文件RadAsyncUpload模块中的任意文件上传漏洞（CVE-2017-11317），RadAsyncUploadAsyncUploadHandler配置了一个硬编码密钥，用于加密文件上传请求中的表单数据，如果此加密密钥的默认值没有被修改过，或者通过其他漏洞被攻击者获得，攻击者可以使用该密钥通过/Telerik.Web.Ui.WebResource.axd?type=rau自定义POST
参数加密rauPostData数据制作文件上传请求，从而实现任意文件上传。

rauPostData参数中包含序列化配置对象和对象的类型，RadAsyncUpload
在处理rauPostData参数的时候存在缺陷，攻击者可以修改对象类型，对.net反序列化漏洞有过了解的开发者都应该明白，当对象类型可控时，就可以尝试构造gadget触发RCE。在这里攻击者通过rauPostData在利用上述任意文件上传漏洞上传恶意DLL
后，通过再次请求强制指定JavaScriptSerializer.Deserialize()的反序列化类型，从而使得恶意DLL被加载执行。

这里还需要一个mixed-mode assembly DLL，它会被注入到w3wp.exe进程中。要注意的是.NET
应用程序只会使用给定名称加载一次程序集，而RadAsyncUpload在上传文件时遇到相同名称的文件是追加内容而不是覆盖，这时如果尝试加载错误的程序集DLL可能会导致web应用崩溃，所以使用唯一的文件名很重要。

通过上面的描述，可以看出这个漏洞利用链有几个先决条件：找到易受攻击的主机，使用默认密钥或利用漏洞来获取加密密钥，编译DLL，上传DLL然后利用反序列化实现命令执行。

这看起来有些复杂，但在 2019 年 12 月中旬已有研究人员发布了公开的POC。尽管Telerik UI 发布了补丁，但由于Telerik UI
通常是作为一次性定制框架嵌入到web应用程序中，所以很难保证所有的服务器管理员及时的更新补丁，这就给了攻击者可乘之机。

攻击者利用CVE-2019-18935将DLL形式的Cobalt Strike
Beacon加载到内存，然后执行编码后的powershell命令下载更多的恶意软件（ XMRig Miner等），并利用GPO和Windows
Management Instrumentation (WMI) ActiveScriptEvent consumer进行权限维持和横向移动。

最终的攻击链如下图：

![1657682369_62ce39c12c070e28f57d2.png!small?1657682370988](https://image.3001.net/images/20220713/1657682369_62ce39c12c070e28f57d2.png!small?1657682370988)

图 攻击链还原

  

 **亮点1：通过组策略对象（GPO）进行持久化和横向**

攻击者通过CVE-2019-18935获得初始访问权限后，从受感染的 Web 服务器转向未受保护的域控制器，通过植入恶意 GPO进行权限维持。

攻击者通过恶意GPO创建计划任务并将编码后的cmd命令和powershell命令写入以下.注册表项：HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows
NT\CurrentVersion\Schedule\TaskCache\Tasks\\{unique_task_name}

解码后的内容如下：

![1657682411_62ce39eb31c542f45ceab.png!small?1657682413091](https://image.3001.net/images/20220713/1657682411_62ce39eb31c542f45ceab.png!small?1657682413091)

图 解码后的powershell命令

此命令使用了常见的反恶意软件脚本接口 (AMSI)
绕过技术，http://212.192.241.155:8000/a是一个远程powershell脚本，使用了gunzip和XOR编码，该脚本会将Cobalt
Strike DLL加载到内存中，随后下载XMrig Miner。

 **亮点2：使用WMI事件进行权限维持躲避检测**

除了计划任务之外，攻击者还创建了一个名为WindowsUpdate的Windows Management Instrumentation (WMI)
ActiveScriptEvent 消费者，用于从http://212.192.241.155/up/setup下载并执行恶意exe。

![1657682437_62ce3a051ec464d7c41ae.png!small?1657682439416](https://image.3001.net/images/20220713/1657682437_62ce3a051ec464d7c41ae.png!small?1657682439416)

图 恶意WMI ActiveScriptEvent 消费者

WMI事件，即特定对象的属性发生改变时发出的通知，其中包括增加、修改、删除三种类型。可以使用wmic来进行操作。通俗的可以说：WMI内部出现什么变化就由WMI事件来进行通知。WMI事件中的事件消费者可以分为临时和永久两类，临时的事件消费者只在其运行期间关心特定事件并进行处理，永久消费者作为类的实例注册在WMI命名空间中，一直有效到它被注销。

攻击者使用WMI事件进行权限维持，除了可以规避常规的检测，还作为使用GPO进行权限维持的一个备选，以确保受害机器不会掉线。

##  **02 总结**

总的来说，攻击者相对于几年前的Blue Mockingbird
具有更加完善的感染链和相对成熟的C2机制。除了技术上的成长，我们更应该注意到攻击者对以往高危漏洞CVE-2019-18935的利用。这也提醒网络安全管理者更应该注重基础设施的安全检查和更新，攻击者不会因为漏洞过时而放弃对其利用，尤其是能够产生重大威胁的漏洞。

另外，本次事件也表明，攻击者的技战法（TTP）也在不断的进化，演变。不管是对旧漏洞的攻击，还是利用GPO，WMI事件消费者进行权限维持和规避检测等手段，攻击者对过往漏洞攻击链的调整和完善，可能比新兴漏洞更让网络安全管理者头疼。

