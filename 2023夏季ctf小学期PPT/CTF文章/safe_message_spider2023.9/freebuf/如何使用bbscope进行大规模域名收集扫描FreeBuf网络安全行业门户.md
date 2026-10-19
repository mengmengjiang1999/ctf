![](https://image.3001.net/images/20210714/1626253638_60eea9463c36969110202.png!small)

## 关于bbscope

bbscope是一款功能强大的大规模信息收集工具，该工具由sw33tLie开发，可以帮助广大研究人员在HackerOne、Bugcrowd和Intigriti上实现大规模信息收集。

在参与平时的漏洞奖励计划过程中，你通常需要搜索漏洞奖励平台所提供的大规模域名，而这款工具正好就是为这项任务所设计的。bbscope不仅可以搜索大规模域名，除此之外它还可以搜索需要测试的Android应用程序列表。

如果你是一名逆向分析人员，别担心，bbscope同样可以帮助你获取到需要分析的代码列表。

## 工具安装

首先，你需要确保在本地系统上安装好了最新版本的Go编译器。接下来，你就可以使用下列命令将该项目安装到本地系统上了：

    
    
    GO111MODULE=on go get -u github.com/sw33tLie/bbscope

## 工具使用

    
    
    bbscope (h1|bc|it) -t <session-token> <other-flags>

 **如何获取会话令牌（session token）：**

  * HackerOne：登录，然后获取名为“__Host-session”的Cookie值；
  * Bugcrowd：登录，然后获取名为“_crowdcontrol_session”的Cookie值；
  * Intigriti：登录，然后拦截发送至intigriti.com的请求，并查询名为“Authentication: Bearer XXX”的Header值，其中的“XXX”就是你的令牌；

关于工具的更多使用方式，可以使用--help参数来查看所有的参数选项描述。

## 使用样例

下面给出的是该工具的部分命令参数使用样例，所有的选项参数同样适用于Bugcrowd和Intigriti的子命令。

打印所有提供奖励的HackerOne项目中的所有范围内目标

    
    
    bbscope h1 -t <YOUR_TOKEN> -b -o t

 **命令输出类似如下：**

    
    
    app.example.com
    
    *.user.example.com
    
    *.demo.com
    
    www.something.com

### 打印所有提供奖励的私人HackerOne项目的范围内目标

    
    
    bbscope h1 -t <YOUR_TOKEN> -b -p -o t

### 从所有HackerOne项目中打印所有范围内的Android APK

    
    
    bbscope h1 -t <YOUR_TOKEN> -o t -c android

### 使用额外数据打印所有HackerOne项目中的所有范围内目标

    
    
    bbscope h1 -t <YOUR_TOKEN> -o tdu -d ", "

这些命令将会打印来自所有HackerOne项目（包括公共程序和VDP）的范围内目标列表，并输出目标描述（如果可用）和项目的URL：

    
    
    something.com, Something's main website, https://hackerone.com/something
    
    *.demo.com, All assets owned by Demo are in scope, https://hackerone.com/demo

### 获取私人HackerOne项目的URL

    
    
    bbscope h1 -t <YOUR_TOKEN> -o u -p | sort -u

 **输出类似如下：**

    
    
    https://hackerone.com/demo
    
    https://hackerone.com/something

## 项目地址

 **bbscope：** 【[ _GiHub传送门_](https://github.com/sw33tLie/bbscope)】

## 参考资料

  * [ _https://hackerone.com/verizonmedia/?type=team_](https://hackerone.com/verizonmedia/?type=team)
  * [ _https://hackerone.com/mailru_](https://hackerone.com/mailru)
  * [ _https://hackerone.com/sp0tify_](https://hackerone.com/spotify)

