![](https://image.3001.net/images/20200518/1589806445_5ec2856d96564.png!small)**INTERCEPT是一套强大的代码静态分析审计策略，这套策略集简单易用，占用空间小，可以通过快速且强大的多行扫描工具来扫描你的代码库。除此之外，广大研究人员还可以将其作为数据采集器和检查器，或把它当作一款跨平台的武器化ripgrep来使用。**

## 功能介绍

代码即策略；

细粒度正则策略；

多个执行级别；

静态分析，无守护进程；

低占用空间，可自我更新的二进制文件；

易于集成在任何CI/CD管道上；

声明式策略，以降低复杂性；

无自定义策略语言；

## 代码即策略

“代码即策略”的思想来源于策略的管理和自动化实现这方面，通过将策略以YAML文件代码的形式来呈现，是已经过验证的软件开发最佳实践，有助于研究人员实现版本控制、自动测试和自动部署。

## 工作机制

> 1、拦截和分析命令行接口代码；
>
> 2、YAML文件策略实施；

INTERCEPT会整合环境标记、YAML策略和可选参数来生成一个全局配置文件，它可以递归扫描目标路径以查找违反策略的代码，并生成人类可读的详细扫描及分析报告。

### 扫描报告输出样本：

###
![](https://image.3001.net/images/20200518/1589806463_5ec2857f0abf9.png!small)

## 工具构建

    
    
    # Standard package (intercept + ripgrep) for individual platforms
    
    -- core-intercept-rg-*.zip
    
    # Cross Platform Full package (intercept + ripgrep)
    
    -- x-intercept.zip
    
    # Build package to build on all platforms (Development)
    
    -- setup-buildpack.zip
    
    # Package of the latest compatible release of ripgrep (doesn't include intercept)
    
    -- i-ripgrep-*.zip

## 快速开始  

首先，根据自己的平台下载最新版本的INTERCEPT：

    
    
    --- Darwin
    
    curl -fSL https://github.com/xfhg/intercept/releases/latest/download/intercept-darwin_amd64 -o intercept
    
    --- Linux
    
    curl -fSL https://github.com/xfhg/intercept/releases/latest/download/intercept-linux_amd64 -o intercept
    
    --- Windows
    
    curl -fSL https://github.com/xfhg/intercept/releases/latest/download/intercept-windows_amd64 -o intercept.exe

获取样本进行快速扫描：

    
    
    curl -fSLO https://github.com/xfhg/intercept/releases/latest/download/_examples.zip

现在，我们需要分析的代码已经存储在一个examples/文件夹中了，在开始之前，我们需要查看策略文件中的可选策略类型：

    
    
    - scan : where we enforce breaking rules on matched patterns
    
    - collect : where we just collect matched patterns

我们给出的演示样例将会做以下几件事情：

1、扫描目标代码中是否存在私钥：我们需要保证策略的fatal:true，并且不接受任何异常，即enforcement:true。设置环境：保证此策略将在所有环境上强制执行。

2、扫描模块是否来自兼容源而不是本地或git：我们需要保证策略的fatal:true，并且环境必须为PROD，即environment:prod。这个策略可以接受本地异常：enforcement:false。

3、收集模块使用之外的terraform资源实例。

包含上述扫描策略和收集策略的策略文件如下（[examples/policy/simple.yaml](https://github.com/xfhg/intercept/tree/master/examples/policy/simple.yaml)）：

    
    
    # This banner is shown on the start of the scanning report,
    
    # use it to point out important documentation/warnings/contacts
    
    
    Banner:
    
    | Banner text here, drop documentation link or quick instructions on how to react to the report
    
    Rules:
    
    # This is the main policy block, all rules will be part of this array
    
    # This is a rule structure block
    
    # Each rule can have one or more patterns (regex)
    
    # The rule is triggered by any of the patterns listed
    
    #
    
    
    # Essential settings :
    
    # id : ( must be unique )
    
    # type : ( scan | collect )
    
    # fatal : ( true | false )
    
    # enforcement : ( true | false )
    
    # environment : ( all | anystring)
    
    # All other settings are free TEXT to complement your final report
    
    - name: Private key committed in code
    
    id: 1
    
    description: Private key committed to code version control
    
    solution:
    
    error: This violation immediately blocks your code deployment
    
    type: scan
    
    enforcement: true
    
    environment: all
    
    fatal: true
    
    
    patterns:
    
    - \s*(-----BEGIN PRIVATE KEY-----)
    
    - \s*(-----BEGIN RSA PRIVATE KEY-----)
    
    - \s*(-----BEGIN DSA PRIVATE KEY-----)
    
    - \s*(-----BEGIN EC PRIVATE KEY-----)
    
    - \s*(-----BEGIN OPENSSH PRIVATE KEY-----)
    
    - \s*(-----BEGIN PGP PRIVATE KEY BLOCK-----)
    
    
    # Another scan rule
    
    - name: Compliant module source
    
    id: 5
    
    description: Modules should not be sourced locally nor from git
    
    error: This breach blocks your deployment on production environments
    
    type: scan
    
    solution:
    
    environment: prod
    
    fatal: true
    
    enforcement: false
    
    patterns:
    
    - source\s*.*\.git"
    
    - \s+source\s*=\s*"((?!https\:).)
    
    
    # A different type of policy rule that just collects findings matched with the patterns listed
    
    - name: Collect sparse TF resources outside of modules.
    
    description: The following resources were detected outside of compliant module usage
    
    type: collect
    
    patterns:
    
    - (resource)\s*"(.*)"
    
    
    # These are the messages displayed at the end of the report
    
    # Clean for no finds
    
    # Warning for at least one non-fatal find
    
    # Critical for at least one fatal find
    
    ExitCritical: "Critical irregularities found in your code"
    
    ExitWarning: "Irregularities found in your code"
    
    ExitClean: "Clean report"

## 项目地址  

INTERCEPT：【[GitHub传送门](https://github.com/xfhg/intercept)】

## 其他引用项目

> 1、[Ripgrep](https://github.com/BurntSushi/ripgrep)
>
> 2、[Hashicorp Sentinel](https://www.hashicorp.com/sentinel/)
>
> 3、[Open Policy Agent](https://www.openpolicyagent.org/)

***参考来源：[xfhg](https://github.com/xfhg/intercept)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

