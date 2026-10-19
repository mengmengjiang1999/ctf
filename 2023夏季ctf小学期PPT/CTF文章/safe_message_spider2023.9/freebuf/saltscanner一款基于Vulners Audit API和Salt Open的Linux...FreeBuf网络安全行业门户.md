![](https://image.3001.net/images/20230827/1693100656_64eaaa70830be4fba7016.png!small)  

## 关于salt-scanner

salt-scanner是一款基于Vulners Audit API和Salt
Open的Linux漏洞扫描工具，该工具整合了JIRA，并带有Slack通知功能。在该工具的帮助下，广大研究人员可以轻松实现针对Linux操作系统的安全漏洞扫描任务，并及时获取最新的扫描结果。

## 功能特性

> 1、支持Slack通知；
>
> 2、报告上传；
>
> 3、JIRA集成；
>
> 4、OpsGenie集成；

## 工具要求

> [ _Salt_ __ _Open_](https://saltstack.com/salt-open-source/)2016.11.x（salt-> master、salt-minion）
>
> Python 2.7
>
> salt（你可能还需要安装gcc、gcc-c++和python dev）
>
> slackclient
>
> jira
>
> opsgenie-sdk

 **注意事项** ：Salt Master和Minion版本必须相匹配，Salt-Scanner支持Salt
v2016.11.x，如果你使用的是v2017.7.x或其他版本，请将salt-scanner.py脚本中的"expr_form"修改为"tgt_type"。

## 工具下载

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python
2.7环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/0x4D31/salt-scanner.git

然后，切换到项目目录中，并使用pip工具和项目提供的requirements.txt文件安装该工具所需的依赖组件：

    
    
    cd salt-scanner/
    
    pip install requirements.txt

## 工具使用

    
    
    $ ./salt-scanner.py -h
    
     
    
     ==========================================================
    
      Vulnerability scanner based on Vulners API and Salt Open
    
     _____       _ _     _____                                 
    
    /  ___|     | | |   /  ___|                               
    
    \ `--.  __ _| | |_  \ `--.  ___ __ _ _ __  _ __   ___ _ __
    
     `--. \/ _` | | __|  `--. \/ __/ _` | '_ \| '_ \ / _ \ '__|
    
    /\__/ / (_| | | |_  /\__/ / (_| (_| | | | | | | |  __/ |   
    
    \____/ \__,_|_|\__| \____/ \___\__,_|_| |_|_| |_|\___|_|   
    
     
    
                   Salt-Scanner 0.1 / by 0x4D31               
    
     ==========================================================
    
     
    
    usage: salt-scanner.py [-h] [-t TARGET_HOSTS] [-tF {glob,list,grain}]
    
                           [-oN OS_NAME] [-oV OS_VERSION]
    
     
    
    optional arguments:
    
      -h, --help            显示工具帮助信息和退出
    
      -t TARGET_HOSTS, --target-hosts TARGET_HOSTS 设置目标主机
    
      -tF {glob,list,grain}, --target-form {glob,list,grain}  从文件或数据源获取目标
    
      -oN OS_NAME, --os-name OS_NAME          目标主机操作系统名称
    
      -oV OS_VERSION, --os-version OS_VERSION    目标主机操作系统版本

## 工具使用样例

    
    
    $ sudo SLACK_API_TOKEN="EXAMPLETOKEN" ./salt-scanner.py -t "*"
    
     
    
     ==========================================================
    
      Vulnerability scanner based on Vulners API and Salt Open
    
     _____       _ _     _____                                 
    
    /  ___|     | | |   /  ___|                               
    
    \ `--.  __ _| | |_  \ `--.  ___ __ _ _ __  _ __   ___ _ __
    
     `--. \/ _` | | __|  `--. \/ __/ _` | '_ \| '_ \ / _ \ '__|
    
    /\__/ / (_| | | |_  /\__/ / (_| (_| | | | | | | |  __/ |   
    
    \____/ \__,_|_|\__| \____/ \___\__,_|_| |_|_| |_|\___|_|   
    
     
    
                   Salt-Scanner 0.1 / by 0x4D31               
    
     ==========================================================
    
     
    
    + No default OS is configured. Detecting OS...
    
    + Detected Operating Systems:
    
       - OS Name: centos, OS Version: 7
    
    + Getting the Installed Packages...
    
    + Started Scanning '10.10.10.55'...
    
       - Total Packages: 357
    
       - 6 Vulnerable Packages Found - Severity: Low
    
    + Started Scanning '10.10.10.56'...
    
       - Total Packages: 392
    
       - 6 Vulnerable Packages Found - Severity: Critical
    
     
    
    + Finished scanning 2 host (target hosts: '*').
    
    2 Hosts are vulnerable!
    
     
    
    + Output file created: 20170622-093138_232826a7-983f-499b-ad96-7b8f1a75c1d7.txt
    
    + Full report uploaded to Slack
    
    + JIRA Issue created: VM-16
    
    + OpsGenie alert created

## 工具运行截图

JIRA扫描问题：

![](https://image.3001.net/images/20230827/1693100742_64eaaac6ac752d8a08983.jpg!small)

Opsgenie警报：

![](https://image.3001.net/images/20230827/1693100749_64eaaacdf08d8796d764c.jpg!small)

Slack警报（概览版）：

![](https://image.3001.net/images/20230827/1693100759_64eaaad710c35dd218658.jpg!small)

Slack警报（完整版）：

![](https://image.3001.net/images/20230827/1693100766_64eaaadea1d71866da33f.jpg!small)

Slack完整报告：

![](https://image.3001.net/images/20230827/1693100775_64eaaae774eaa84218594.jpg!small)

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/0x4D31/salt-scanner/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **salt-scanner** ：【[ _GitHub传送门_](https://github.com/0x4D31/salt-scanner)】

## 参考资料

> [ _https://saltstack.com/salt-open-source/_](https://saltstack.com/salt-> open-source/)
>
> [ _https://github.com/saltstack/salt-> contrib/blob/master/grains/ec2_tags.py_](https://github.com/saltstack/salt-> contrib/blob/master/grains/ec2_tags.py)
>
> [
> _https://docs.saltstack.com/en/latest/topics/tutorials/walkthrough.html_](https://docs.saltstack.com/en/latest/topics/tutorials/walkthrough.html)

