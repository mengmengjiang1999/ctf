**Pown
CDB是一个Chrome调试协议实用程序。该工具的主要目标是将一些常见任务自动化的执行，以帮助从命令行调试Web应用，并主动监视和拦截HTTP请求和响应。这在渗透测试和其他类型的安全评估和调查期间非常有用。**

**![01.png](https://image.3001.net/images/20190704/1562201807_5d1d4ecfbe88d.png!small)**

该工具是secapps.com开源计划的一部分。

    
    
     ___ ___ ___   _   ___ ___  ___
    / __| __/ __| /_\ | _ \ _ \/ __|
    \__ \ _| (__ / _ \|  _/  _/\__ \
    |___/___\___/_/ \_\_| |_|  |___/
     https://secapps.com

 **作者**

[@pdp](https://twitter.com/pdp) \- <https://pdparchitect.github.io/www/>

## 快速开始

该工具旨在作为[Pown.js](https://github.com/pownjs/pown)的一部分使用，但你也可以作为独立的工具来单独调用。

让我们首先来安装Pown：

    
    
    $ npm install -g pown@latest

直接从Pown调用：

    
    
    $ pown cdb

 **库的使用**

从项目的根目录本地安装此模块：

    
    
    $ npm install @pown/cdb --save

完成后，调用pown cli：

    
    
    $ POWN_ROOT=. ./node_modules/.bin/pown-cli cdb

你还可以使用全局pown在本地调用该工具：

    
    
    $ POWN_ROOT=. pown cdb

## 使用

 **警告** ：此pown命令当前正处在开发阶段，因此后续将可能出现重大更改的情况。

    
    
    pown cdb <command>
    
    Chrome Debug Protocol Tool
    
    Commands:
      pown cdb launch             Launch server application such as chrome, firefox, opera and edge  [aliases: start]
      pown cdb navigate <url>     Go to the specified url  [aliases: goto, go]
      pown cdb network            Chrome Debug Protocol Network Monitor  [aliases: net, sniff, proxy, mon, monitor]
      pown cdb cookies            Dump current page cookies  [aliases: cookie]
      pown cdb screenshot <file>  Screenshot the current page  [aliases: capture, shoot, shot]
    
    Options:
      --version  Show version number  [boolean]
      --help     Show help  [boolean]

### pown cdb launch

    
    
    pown cdb launch
    
    Launch server application such as chrome, firefox, opera and edge
    
    Options:
      --version                 Show version number  [boolean]
      --help                    Show help  [boolean]
      --port, -p                Remote debugging port  [number] [default: 9222]
      --xss-auditor, -x         Turn on/off XSS auditor  [boolean] [default: true]
      --certificate-errors, -c  Turn on/off certificate errors  [boolean] [default: true]
      --pentest, -t             Start with prefered settings for pentesting  [boolean] [default: false]

### pown cdb navigate

    
    
    pown cdb navigate <url>
    
    Go to the specified url
    
    Options:
      --version     Show version number  [boolean]
      --help        Show help  [boolean]
      --host, -H    Remote debugging host  [string] [default: "localhost"]
      --port, -p    Remote debugging port  [number] [default: 9222]
      --secure, -s  HTTPS/WSS frontend  [boolean] [default: false]

### pown cdb network

    
    
    pown cdb network
    
    Chrome Debug Protocol Network Monitor
    
    Options:
      --version      Show version number  [boolean]
      --help         Show help  [boolean]
      --host, -H     Remote debugging host  [string] [default: "localhost"]
      --port, -p     Remote debugging port  [number] [default: 9222]
      --secure, -s   HTTPS/WSS frontend  [boolean] [default: false]
      --output, -o   Output directory/file  [array] [default: []]
      --blessed, -b  Start with blessed ui  [boolean] [default: false]

### pown cdb cookies

    
    
    pown cdb cookies
    
    Dump current page cookies
    
    Options:
      --version     Show version number  [boolean]
      --help        Show help  [boolean]
      --host, -H    Remote debugging host  [string] [default: "localhost"]
      --port, -p    Remote debugging port  [number] [default: 9222]
      --secure, -s  HTTPS/WSS frontend  [boolean] [default: false]

### pown cdb screenshot

    
    
    pown cdb screenshot <file>
    
    Screenshot the current page
    
    Options:
      --version     Show version number  [boolean]
      --help        Show help  [boolean]
      --host, -H    Remote debugging host  [string] [default: "localhost"]
      --port, -p    Remote debugging port  [number] [default: 9222]
      --secure, -s  HTTPS/WSS frontend  [boolean] [default: false]

##  **教程**

 **Web 应用安全评估**

让我们探讨如何在典型的Web应用中使用Own CBD。

首先，请确保安已装了最新的pown：

    
    
    $ npm install -g pown

如果你已安装了pown，那么请确保你当前的版本为最新版：

    
    
    $ pown update

想要使用Pown CDB，我们需要一个Chrome浏览器实例（也支持其他浏览器），启用了chrome调试远程接口并在localhost上进行侦听：

    
    
    $ pown cdb launch --port 9333

Chrome浏览器实例运行后，将其与pown cdb网络实用程序挂钩：

    
    
    $ pown cdb network --port 9333 -b

-b：使用基于curses的用户界面启动Pown CDB：

![2.png](https://image.3001.net/images/20190704/1562201833_5d1d4ee9b48cd.png!small)

使用key-combo shift + ?获取可用快捷方式列表：

![3.png](https://image.3001.net/images/20190704/1562201845_5d1d4ef59bddd.png!small)

一旦开始使用浏览器，Pown CDB将在用户界面中记录并显示流量。要拦截请求，请使用key-combo ctrl + t。

![4.png](https://image.3001.net/images/20190704/1562201860_5d1d4f042680e.png!small)

在默认的shell编辑器（$EDITOR）中捕获并打开请求。进行所需的更改，然后保存并退出。原始请求将会被替换为你的更改。

 ** *参考来源：[GitHub](https://github.com/pownjs/pown-cdb)，FB小编secist编译，转载请注明来自FreeBuf.COM **  

