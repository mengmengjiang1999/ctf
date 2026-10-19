![](https://image.3001.net/images/20221225/1671968765_63a837fd0e2b131621902.png!small)

## 关于Shennina

Shennina是一款功能强大的自动化主机渗透/漏洞利用框架，该项目的主要目的是使用人工智能技术来实现安全扫描、漏洞扫描/分析和漏洞利用开发的完全自动化。Shennina整合了Metasploit和Nmap这两款强大的网络安全工具实现其部分功能，并执行渗透测试。除此之外，该工具还整合了一个命令控制服务器用于从目标主机中自动过滤数据。

该项目的开发理念取自于Isao Takaesu的DeepExploit项目，并由Mazin Ahmed和Khalid Farah在HITB
CyberWeek 2019人工智能挑战赛中首次面世。

## 工具运行机制

Shennina能够扫描一组输入目标以获得相关的可用网络服务，然后使用其人工智能引擎识别可用的渗透测试方案，并自动提供相对应的漏洞利用技术，最后该工具会自动针对目标尝试进行渗透测试。如果渗透测试成功，那么Shennina将会自动进入后渗透工作阶段。

该工具的人工智能引擎最初使用的是实时活动目标进行训练的，以学习和训练出针对远程服务的可靠渗透技术。

值得一提的是，Shennina还支持“启发式”模式来识别目标漏洞并提供相对应的漏洞利用方案。

## 功能介绍

> 1、实现了自动化自我学习方法来查找漏洞利用方案；
>
> 2、使用了托管并发设计实现高性能运行；
>
> 3、智能集群渗透测试/漏洞利用；
>
> 4、后渗透功能；
>
> 5、欺骗攻击检测；
>
> 6、勒索软件模拟功能；
>
> 7、自动数据过滤；
>
> 8、可选的漏洞扫描模式；
>
> 9、启发式模式获取推荐的渗透测试方案；
>
> 10、支持Windows、Linux和macOS代理；
>
> 11、后渗透阶段脚本化的攻击/渗透模式；
>
> 12、提供针对内核的漏洞利用/渗透解决方案建议；
>
> 13、针对漏洞利用方案提供带外技术测试；
>
> 14、自动过滤目标服务器中的重要数据；
>
> 15、报告生成；
>
> 16、覆盖了 MITRE ATT&CK框架中的40+ TTP；
>
> 17、支持多个输入目标；

## 工具下载

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。接下来，我们就可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/mazen160/shennina.git

然后使用pip命令和项目提供的requirements.txt文件来安装该工具所需的依赖组件：

    
    
    cd Shennina
    
    pip install requirements.txt

除此之外，我们也可以直接访问该项目的【[
_Release页面_](https://github.com/mazen160/shennina/releases/tag/v1.0.0)】来下载工具最新的发布版本。

## 工具运行

### 过滤服务器-代理

Linux/macOS

    
    
    ./exfiltration-server/agent.sh

Windows

    
    
    ./exfiltration-server/agent.ps1

### 过滤服务器-运行

    
    
    $ cd ./exfiltration-server/
    
    $ ./run-server.sh

### MSFRPCD服务器

    
    
    ./scripts/run-msfrp.py

### 运行服务扫描

    
    
    $ ./shennina.py --lhost metasploit-ip --target target.local --service-scan-only

### 以训练模式运行Shennina

    
    
    $ ./shennina.py --training-mode --lhost lhost.local --target training-target.local

### 渗透测试模式

    
    
    $ ./shennina.py --lhost lhost.local --target target.local --exploitation-mode

### 渗透测试模式-启发式

    
    
    $ ./shennina.py --lhost lhost.local --target target.local --exploitation-mode --secondary-mode

## 项目地址

 **Shennina** ：【[ _GitHub传送门_](https://github.com/mazen160/shennina)】

## 参考资料

> [
> _https://www.linkedin.com/in/infosecmazinahmed/_](https://www.linkedin.com/in/infosecmazinahmed/)
>
> [
> _https://www.linkedin.com/in/khaledfarah_](https://www.linkedin.com/in/khaledfarah)
>
> [ _https://cyberweek.ae/2019/session/hitb-ai-> challenge/_](https://cyberweek.ae/2019/session/hitb-ai-challenge/)
>
> [ _https://github.com/13o-bbr-> bbq/machine_learning_security/tree/master/DeepExploit_](https://github.com/13o-bbr-> bbq/machine_learning_security/tree/master/DeepExploit)
>
> [ _https://www.linkedin.com/in/isao-> takaesu-47485a77/_](https://www.linkedin.com/in/isao-takaesu-47485a77/)

