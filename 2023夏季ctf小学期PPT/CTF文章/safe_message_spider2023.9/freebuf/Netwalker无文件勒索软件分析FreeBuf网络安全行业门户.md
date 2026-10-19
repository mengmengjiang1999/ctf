**攻击者正不断研究更复杂的方式逃避恶意软件检测，近期发现攻击者利用PowerShell编写Netwalker勒索软件，直接在内存中执行，没有将实际的勒索软件二进制文件存储到磁盘中。恶意软件利用了反射动态链接库（DLL）注入的技术，也称reflective
DLL加载，可以从内存注入DLL，不需要实际DLL文件，也不需要任何Windows加载程序即可注入。**

## PowerShell分析  

powershell脚本行为如下图：

![image.png](https://image.3001.net/images/20200526/1590482619_5eccd6bbf32ee.png!small)该脚本使用了多层加密，混淆和编码技术，最顶层为base64编码：  

![image.png](https://image.3001.net/images/20200526/1590482687_5eccd6ff8fbf8.png!small)base64解码将显示下一层代码，该层是十六进制编码XOR加密：  

![image.png](https://image.3001.net/images/20200526/1590482770_5eccd752cfacf.png!small)解码和解密后会显示主要脚本，该脚本仍有混淆，分析人员难以读懂内容：  

![image.png](https://image.3001.net/images/20200526/1590482822_5eccd786a55b3.png!small)该文件以反射方式将勒索软件DLL注入到合法进程explorer.exe中，
勒索软件以十六进制格式嵌入在脚本中。  

![image.png](https://image.3001.net/images/20200526/1590482871_5eccd7b70fb75.png!small)

脚本将其解码产生两个DLL，一个是勒索软件的x86版本（用于32位OS），另一个是x64版本（用于64位OS）。它会对运行环境进行检测，以便可以确定要使用的DLL版本：

![image.png](https://image.3001.net/images/20200526/1590482989_5eccd82d81060.png!small)它首先从kernell32.dll中找到所需功能的API地址：  

![image.png](https://image.3001.net/images/20200526/1590483014_5eccd846173e6.png!small)然后计算内存地址：  

![image.png](https://image.3001.net/images/20200526/1590483063_5eccd877490bc.png!small)![image.png](https://image.3001.net/images/20200526/1590483076_5eccd88468709.png!small)  

脚本本身充当DLL加载程序，可以自行计算并解析定位其所需的内存地址。然后指定要注入的进程，搜索正在运行的Windows资源管理器进程。

![image.png](https://image.3001.net/images/20200526/1590483191_5eccd8f759699.png!small)通过以下代码将勒索软件DLL写入explorer.exe的内存空间并执行：  

![image.png](https://image.3001.net/images/20200526/1590483222_5eccd9165e574.png!small)最后删除副本，防止受害者使用副本恢复文件。  

##
![image.png](https://image.3001.net/images/20200526/1590483268_5eccd94497a59.png!small)无文件勒索软件分析

Netwalker使用6个随机字符作为扩展名重命名加密文件：  

![image.png](https://image.3001.net/images/20200526/1590483325_5eccd97d58b87.png!small)它将勒索信息放在系统各个文件夹中，并在对受害者数据文档加密后打开，其内容为：

![image.png](https://image.3001.net/images/20200526/1590483400_5eccd9c829fe2.png!small)添加以下注册表项：  

    
    
    HKEY_CURRENT_USER\SOFTWARE\{8 random characters}
    
    {8 random characters} = {Hex values}

![image.png](https://image.3001.net/images/20200526/1590483433_5eccd9e95a0db.png!small)

勒索软件会终止某些进程和服务，其中一些与软件数据备份有关。以下是勒索软件终止的一些服务示例（全部服务列表参照此[报告](https://www.trendmicro.com/vinfo/us/threat-encyclopedia/malware/Ransom.PS1.NETWALKER.B?_ga=2.223232476.670453444.1590019020-865987231.1583109059)）：

    
    
       *backup*
    
        *sql*
    
        AcronisAgent
    
        ARSM
    
        server Administrator
    
        ShadowProtectSvc
    
        wbengine
    
        *sql*
    
        excel.exe
    
        ntrtscan.exe
    
        powerpnt.exe
    
        wbengine*
    
        winword.exe
    
        wrsa.exe

勒索软件还会停止与安全软件相关的进程，逃避安全软件对其恶意活动的检测防御。

Netwalker加密文件时主要针对常见用户文件，例如Office文档，PDF，图像，视频，音频和文本文件等。
它通常会避免对关键文件，可执行文件，动态链接库，注册表或其他与系统相关的文件进行加密，防止系统完全失效。

## 总结与建议

攻击者现在正在向勒索软件中添加反射DLL注入，从而使攻击难以被安全分析人员分析追踪。勒索软件本身对组织就具有很大的危害，成为无文件攻击后，其风险再次加大。组织必须使用各种安全技术来保护其端点，例如采用行为监控和基于行为检测的安全方案等。  

以下是避免被勒索软件攻击的一些建议：  

> 定期备份关键数据，减轻勒索软件攻击的影响；
>
> 安装来自操作系统和第三方供应商的最新软件补丁；
>
> 遵守良好的邮件和网站安全规范；
>
> 及时发现警告可疑的电子邮件和文件；
>
> 在端点上实施应用程序白名单，阻止所有未知和不需要的应用程序；
>
> 定期组织员工进行安全培训。

## IOCs

![image.png](https://image.3001.net/images/20200526/1590484104_5eccdc882fafd.png!small)
***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/netwalker-fileless-ransomware-injected-via-reflective-loading/)，由Kriston编译，转载请注明来自FreeBuf.COM**  

