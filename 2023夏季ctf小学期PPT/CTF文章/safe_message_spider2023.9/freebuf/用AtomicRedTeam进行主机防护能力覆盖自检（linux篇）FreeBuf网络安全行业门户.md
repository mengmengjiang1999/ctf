在日常的安全防护运营工作中，蓝队的同学们会有对自己的主机防护能力的检测的需求。从理论上，我们有Mitre's ATT&CK
这个理论，但是落地要怎么做呢，这时候我想推荐一下最近学习到了Atomic Red Team 这个组件了

Atomic Red Team (简称ART) 是一个依据Mitre's
ATT&CK整理的一个测试库。他依据了ATT&CK的每一个techniques，整理了相应的“原子测试”脚本。通过ART我们能够对于主机防护面有很好的认知。并且依据他们提供的原子测试对自身的安全防护能力做一个自测。

# 1 准备阶段 - 基础环境

需要准备的材料有：

  * 虚拟机并安装 (centos7)

  * 通过yum安装需要的实验环境，安装你需要测试的agent ()

  * 确定你需要测试的内容并且制定相关的测试计划  
第一，是虚拟机的安装。
虚拟机的安装需要注意的是linux的内核版本，一定要和自己的agent支持版本匹配。在测试初期我就遇到过这个问题。通过以下命令在安装后确认内核版本。

    
    
    uname -r
    

第二，语言环境的安装

    
    
    # centos 环境
    if [ -f /etc/redhat-release ]; then
      # yum 安装php
      yum install -y epel-release
      yum install -y http://rpms.remirepo.net/enterprise/remi-release-7.rpm
      yum-config-manager --enable remi-php72
      yum install -y php72
    
      # yum 安装perl
      yum install -y perl
    
      # yum 安装lua
      yum install -y lua
    
      # yum 安装Golang
      yum install -y golang
    
      # yum 安装java
      yum install -y java-1.8.0-openjdk-devel
    
    fi
    

通过简单粗暴的几条yum，准备好服务器的环境.

# 2 Atomic Red Team 测试自动化

为了方便测试，社区准备了一套非常方便的执行框架。但是框架仅限于PowerShell的环境下进行使用。对于无法使用PowerShell
的情况，社区也准备了python与golang的自动化执行框架，都是非常便捷的工具。我在使用的过程中主要挑选了官方本身的框架以及golang的框架进行了自动化的测试。

## 2.1 通过PowerShell invoke-atomicredtem 进行自动化测试

### 2.1.1 准备 powerShell

第一步，为linux准备powershell

Microsoft官方为linux以及macOS都准备了相关的安装方法，能够让linux以及macOS都能够使用powerShell

    
    
    # 注册微软repo
    curl https://packages.microsoft.com/config/rhel/7/prod.repo | sudo tee /etc/yum.repos.d/microsoft.repo
    
    # 安装
    sudo yum install -y powershell
    
    # 启动
    pwsh
    

到此，第一步powershell安装完毕。

### 2.1.2 准备 invoke-atomicredteam

第二步，安装invoke-atomicredteam

首先通过`pwsh`进入powershell操作页面

    
    
    IEX (IWR 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing);
    Install-AtomicRedTeam -getAtomics
    

![image](https://image.3001.net/images/20210415/1618456948_6077b17485600c57d674b.png!small)  
在安装完毕之后，可以通过

    
    
    invoke-atomictest All -ShowDetailsBrief
    

来确定是否安装成功。命令输入后回出现反馈  
![image](https://image.3001.net/images/20210415/1618456983_6077b197204c698791828.png!small)  
记得日后要在在powershell导入模块才能用哦

    
    
    Import-Module "/root/AtomicRedTeam/invoke-atomicredteam/Invoke-AtomicRedTeam.psd1" -Force
    

在没有调整过的情况下，centos7 的该文件位置如命令，如果在之前安装时候有自定义位置，需要按照位置导入。

最后，需要我们明确需要测试的测试项。可以通过依靠官方给出的mitre ATT&CK 并依据环境进行选择，确定下最后的测试项。  
![image](https://image.3001.net/images/20210415/1618457003_6077b1abd96d8eaee46a5.png!small)

### 2.1.3 开始测试吧！

可以按照表格准备的Technique一个个测试

    
    
    Invoke-AtomicTest T1053.003 -TestNumbers 1
    

也可以简单粗暴的 (非虚拟机的话，建议别这么搞)

    
    
    Invoke-AtomicTest All
    

## 2.2 使用go-art 吧！

go-atomicredteam是一个Golang应用程序，用于执行ART的Atomics文件夹中定义的测试。

### 2.2.1 安装

在安装好了 git 与 golang环境下

    
    
    git clone https://github.com/activeshadow/go-atomicredteam.git
    cd go-atomicredteam
    make release
    

### 2.2.2 使用

如果需要观察信息的话

    
    
    /root/go-atomicredteam/bin/goart-linux -t T1053.003#{Technique ID}
    

![image](https://image.3001.net/images/20210415/1618457076_6077b1f47e3331c1523ab.png!small)  
对每个测试项有很好的描述

在测试的时候需要指定测试单元

    
    
    /root/go-atomicredteam/bin/goart-linux -t T1053.003 -i 0 #{Test ID}
    

![image](https://image.3001.net/images/20210415/1618457040_6077b1d041028a7f086cc.png!small)  
要强调的是，与invoke-art不同，这里的testNumer是从零开始的。

接下来的步骤与之前相同，略。

# 3 尾声

在使用中，我更觉得ART相较于一个自动化工具，更像一个知识库。他能帮助我们更好的去理解ATTCK，更好的去理解防御以及常用的探测命令，是一个很值得学习的repo。

参考文档：

https://github.com/redcanaryco/atomic-red-team

https://github.com/activeshadow/go-atomicredteam

