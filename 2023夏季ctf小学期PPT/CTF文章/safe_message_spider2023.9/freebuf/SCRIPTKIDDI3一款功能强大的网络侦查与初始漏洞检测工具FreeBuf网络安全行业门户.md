![](https://image.3001.net/images/20230516/1684248912_64639950bdf990881428d.png!small)

## 关于SCRIPTKIDDI3

SCRIPTKIDDI3是一款功能强大的网络侦查与初始漏洞检测工具，该工具可以帮助我们以自动化的形式完成网络渗透测试初始阶段的网络侦查以及漏洞检测任务。SCRIPTKIDDI3专为漏洞奖励计划设计，使用了各种开源工具和Shell脚本，允许我们以快速高效的形式在目标域上运行扫描并识别潜在的漏洞。

SCRIPTKIDDI3首先会在目标系统上执行侦察，收集子域名等信息，并使用Nuclei运行服务。然后，它将使用这些收集到的信息来扫描已知的漏洞和潜在的攻击向量，并提醒广大研究人员可能需要解决的任何高风险问题。

除此之外，SCRIPTKIDDI3还包括用于识别nucles模板的错误配置和不安全默认设置的功能，帮助我们确保系统配置正确且安全。

## 工具运行机制

该工具主要会执行下列三个任务：

> 1、使用各种开源工具和脚本有效执行子域名枚举任务；
>
> 2、使用开放HTTP和HTTPS服务来获取URL地址；
>
> 3、运行一个Nuclei并扫描搜索结果，该过程就是漏洞奖励计划任务的初始网络侦查阶段；

## 工具安装

SCRIPTKIDDI3的运行需要使用到很多其他的工具组件，广大研究人员可以使用下列命令将该项目源码克隆至本地，并安装所需的依赖组件：

    
    
    git clone https://github.com/thecyberneh/scriptkiddi3.git
    
    cd scriptkiddi3
    
    bash installer.sh

## 工具使用

    
    
    scriptkiddi3 -h

上述命令将显示工具的帮助信息，下面给出的是工具支持的所有参数选项：

    
    
    [ABOUT:]
    
       Streamline your recon and vulnerability detection process with SCRIPTKIDDI3,
    
       A recon and initial vulnerability detection tool built using shell script and open source tools.
    
     
    
     
    
    [Usage:]
    
       scriptkiddi3 [MODE] [FLAGS]
    
       scriptkiddi3 -m EXP -d target.com -c /path/to/config.yaml
    
     
    
     
    
    [MODES:]
    
        ['-m'/'--mode']
    
             Available Options for MODE:
    
             SUB | sub | SUBDOMAIN | subdomain           以子域名枚举模式运行
    
             URL | url                                      以URL提取模式运行
    
             EXP | exp | EXPLOIT | exploit                  以完全漏洞利用模式运行
    
     
    
     
    
             Feature of EXPLOI mode :                    子域名枚举、URL枚举、使用Nuclei执行漏洞检测，扫描子域名接管漏洞
    
     
    
    [FLAGS:]
    
        [TARGET:]   -d, --domain    设置待扫描的目标域名
    
     
    
        [CONFIG:]   -c, --config    subfinder配置文件路径
    
     
    
        [HELP:]     -h, --help      获取工具帮助菜单 
    
          
    
        [UPDATE:]   -u, --update    更新工具

## 工具使用样例

以完全漏洞利用模式运行工具：

    
    
    scriptkiddi3 -m EXP -d target.com

为Subfinder使用自定义配置文件：

    
    
    scriptkiddi3 -m EXP -d target.com -c /path/to/config.yaml

以子域名枚举模式运行工具：

    
    
    scriptkiddi3 -m SUB -d target.com

以URL枚举模式运行工具：

    
    
    scriptkiddi3 -m SUB -d target.com

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/thecyberneh/scriptkiddi3/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **SCRIPTKIDDI3** ：【[
_GitHub传送门_](https://github.com/thecyberneh/scriptkiddi3)】

