## **情报背景**

Proofpoint团队近日发现了一种利用合法开源软件包安装程序Chocolatey来实现后门的独特攻击，后门被命名为Serpent。在本次事件中，攻击者利用合法的Python代码实现通信以绕过检测，并通过独特的计划任务利用方式实现持久化。本文将就事件中出现的相关技术进行分析阐述。

 **组织名称**

|

Serpent  
  
---|---  
  
 **战术标签**

|

载荷执行 命令与控制  
  
 **技术标签**

|

PowerShell执行 Python脚本执行 计划任务  
  
 **情报来源**

|

https://www.proofpoint.com/us/blog/threat-insight/serpent-no-swiping-new-backdoor-targets-french-entities-unique-attack-chain  
  
##  **01** 攻击技术分析

攻击仍旧以宏文档作为入口，通过宏下载隐写图像，并调用其中隐藏的PowerShell脚本。PowerShell脚本在宿主上下载并安装Chocolatey。PowerShell脚本利用Chocolatey安装Python以及PySocks反向代理等依赖项，然后下载以相同技术隐写在图像中的后门Python脚本，并通过bat文件执行。具体流程如下：

![1651132987_626a4a3bc460b9412df49.png!small?1651132988236](https://image.3001.net/images/20220428/1651132987_626a4a3bc460b9412df49.png!small?1651132988236)

 **亮点一：利用Chocolatey建立PySocks反向代理客户端进行流量转发**

Chocolatey是一款用于Windows的软件自动化管理工具，能够将安装程序、可执行文件、ZIP和脚本打包到编译好的包中。Serpent利用Powershell脚本实现Chocolatey的下载和安装，然后利用Chocolatey强大的环境配置能力实现Python的部署。在Chocolatey的官网上，可以看到其支持9000余种常见软件的命令安装，其中不乏各种开发环境的安装配置：

![1651133000_626a4a481d339b52b343c.png!small?1651133000593](https://image.3001.net/images/20220428/1651133000_626a4a481d339b52b343c.png!small?1651133000593)

利用该强大的自动化安装能力，样本能够方便地部署需要的Python环境。这种高度自动化的环境部署能力在带来方便的同时，也为攻击者提供了极大的便利。攻击者或许能够提供更加难以发现的混淆初始载荷代码，利用Chocolatey在宿主环境中部署相应环境，生成攻击载荷，这可能使得很多终端防护措施可以被轻松绕过。

样本利用Python Socket实现后门，接收命令并回传执行结果。基于部署好的Python环境，能够很好地将相关流量伪装在Python背后。

 **亮点二：利用事件触发计划任务实现进程伪装**

与以往通过创建计划任务周期性执行载荷的利用方式不同，在本次事件中，样本执行以下计划任务命令创建一次性任务来调用可执行文件：

  * schtasks.exe /CREATE /SC ONEVENT /EC application /mo *[System/EventID=777] /f /TN run /TR "xxxxx"

  * EVENTCREATE /ID 777 /L APPLICATION /T INFORMATION /SO DummyEvent /D "Initiatescheduled task."

  * schtasks.exe /DELETE /TN run /f

创建的一次性任务的触发条件为是否创建了事件ID为777的Windows事件。接着，命令创建一个ID为777的虚拟事件来触发该任务，随后从任务调度中删除任务，事了拂衣去。利用计划任务的事件触发来执行有效载荷可导致有效载荷作为已签名Windows二进制文件的子进程执行：

![1651133020_626a4a5cc3fc9e6bc9cbf.png!small?1651133020859](https://image.3001.net/images/20220428/1651133020_626a4a5cc3fc9e6bc9cbf.png!small?1651133020859)

此处的执行对象会从直接托管Task Scheduler服务的svchost.exe派生：

![1651133030_626a4a663e10293f902af.png!small?1651133030453](https://image.3001.net/images/20220428/1651133030_626a4a663e10293f902af.png!small?1651133030453)

查看进程号为1420的svchost进程：

![1651133040_626a4a700ad0c8abd28ad.png!small?1651133040206](https://image.3001.net/images/20220428/1651133040_626a4a700ad0c8abd28ad.png!small?1651133040206)

可以看到，目标程序作为Schedule服务所在的1420进程的子进程创建，以此达成进程伪装的目的，提高了执行时的隐蔽性与排查难度，且实现难度很低。

##  **02** 总结

1.利用Chocolatey作为初始有效载荷，因为软件包的合法性，能够有效绕过威胁检测。这一手法利用了本应创造便利的工具部署代码运行环境以执行恶意代码，这对终端防护措施提出了新的挑战；

2.创新性地将计划任务用于载荷执行而非本地持久化，新颖的执行方式使得恶意行为的执行更加隐蔽。

