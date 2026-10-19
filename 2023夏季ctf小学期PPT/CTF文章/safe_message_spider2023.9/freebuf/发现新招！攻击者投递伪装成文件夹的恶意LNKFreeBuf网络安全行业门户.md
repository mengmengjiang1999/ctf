## **情报背景**

cynet的研究人员收集到有新的攻击者使用托管在合法存储的ISO文件来对目标发起鱼叉式钓鱼攻击。为了使受害者最大程度地放松警惕，攻击者将ISO内的LNK文件伪装成文件夹的形式。

 **组织名称**

|

BumbleBee  
  
---|---  
  
 **关联组织**

|

未知  
  
 **战术标签**

|

网络钓鱼  
  
 **技术标签**

|

VBS Rundll32 LNK WMI ISO  
  
 **情报来源**

|

https://www.cynet.com/orion-threat-alert-flight-of-the-bumblebee/  
  
##  **01** 攻击技术分析

整体攻击流程：

1\. 包含URL的鱼叉式邮件

2\. 诱导用户访问URL下载存储在合法存储服务网络上的ZIP文件

3\. 用户打开并解压该ZIP文件，并挂载ISO

4\. 用户尝试打开伪装成文件夹的LNK文件，查看文件

5\. LNK文件执行隐藏的恶意DLL

![1652237242_627b23bab172d0e631f8d.png!small?1652237243037](https://image.3001.net/images/20220511/1652237242_627b23bab172d0e631f8d.png!small?1652237243037)

 **2.1 伪装成文件夹的恶意LNK**

攻击者为了最大程度地迷惑受害者，选择将LNK伪装成文件夹。效果如下，settings.dll为设置的隐藏文件，配合LNK发起攻击，该文件默认不会显示。

![1652237255_627b23c7dd24cb0d161dd.png!small?1652237256096](https://image.3001.net/images/20220511/1652237255_627b23c7dd24cb0d161dd.png!small?1652237256096)

具有隐藏属性的settings.dll恶意文件。

![1652237271_627b23d757daf6b3736ae.png!small?1652237271513](https://image.3001.net/images/20220511/1652237271_627b23d757daf6b3736ae.png!small?1652237271513)

伪装的LNK文件属性内包含以下命令：

C:\Windows\System32\rundll32.exe settings.dll,IternalJob

通过rundll32加载同目录下隐藏的恶意DLL。

![1652237294_627b23eedb25c4aa9b1c3.png!small?1652237295146](https://image.3001.net/images/20220511/1652237294_627b23eedb25c4aa9b1c3.png!small?1652237295146)

 **2.2 再次运行VBS启动自身**

在完成初始阶段rundll32对恶意DLL的加载运行后，首先会释放新的恶意DLL和一个VBS脚本文件到%programdata%/{RandomDir}
目录，该恶意DLL同样可以被rundll32加载。

cynet的报告显示攻击者多次活动中分别通过wmi和计划任务运行该vbs脚本，这可能是攻击者尝试在第二阶段绕过父进程检测的手段。

如图：settings.dll运行后会释放vbs文件并调用wmi创建wscript.exe加载运行vbs文件。

![1652237338_627b241adc877337d493d.png!small?1652237339142](https://image.3001.net/images/20220511/1652237338_627b241adc877337d493d.png!small?1652237339142)

settings.dll的反汇编结果显示其vbs中通过了Wscript.Shell接口又一次启动了同样释放在%programdata%/{RandomDir}
目录下的恶意DLL文件。

![1652237376_627b24402216415b8fefe.png!small?1652237376347](https://image.3001.net/images/20220511/1652237376_627b24402216415b8fefe.png!small?1652237376347)

在cynet的报告没有更多内容透露的情况下，攻击者可能尝试以这种方式再次启动自身，实现对父进程关系检测的绕过。

##  **02** 总结

利用ISO这种容器文件进行投递，可规避针对外来文件的WEB标记，绕过针对外源文件的安全限制。针对目标人员在识别钓鱼文档的局限，利用lnk伪装文件夹结合隐藏DLL的方式来发起钓鱼攻击，在研判中也较为少见，对普通的受害者迷惑性很强，很容易让人放松警惕双击打开。rundll32.exe作为常用的系统程序，安全软件也无法完全禁止其运行，还是存在被攻击者恶意利用的机会。

