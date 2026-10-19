***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **QRLJacker，又名Quick Response Code
LoginJacking，这是一种简单但功能强大的攻击向量，大部分拥有二维码扫码登录功能的Web应用程序都会受到这种攻击向量的影响，这种功能本身是为了提升用户账号安全性来设计的，但攻击者可以通过劫持用户会话来破坏这种安全功能。**

![a.jpg](https://image.3001.net/images/20190428/1556418557_5cc50ffd3b3c8.jpg!small)

实际上，QRLJacking就是一种新型的社会工程学攻击向量，而我们设计的QRLJacking是一款高度定制化的漏洞利用框架，该框架可以用来演示或执行“QRLJacking攻击向量”。

## 工具演示视频

### 工具运行截图

![b.png](https://image.3001.net/images/20190428/1556418572_5cc5100c62b88.png!small)

## 工具依赖

> 1.Linux或macOS（暂不支持Windows）
>
> 2.Python 3.7+

## 工具安装

1.将Firefox浏览器升级至最新版本；

2.从【[这里](https://github.com/mozilla/geckodriver/releases)】获取最新版本的geckodriver，并提取文件：

    
    
    chmod +x geckodriver
    
    sudo mv -f geckodriver /usr/local/share/geckodriver
    
    sudo ln -s /usr/local/share/geckodriver /usr/local/bin/geckodriver
    
    sudo ln -s /usr/local/share/geckodriver /usr/bin/geckodriver

3.使用下列命令克隆代码库：

    
    
    git clone <https://github.com/OWASP/QRLJacking>
    
    cd QRLJacking/QRLJacker

4.安装依赖组件：

    
    
    pip install -r requirements.txt

5.工具运行：

    
    
    python3 QrlJacker.py --help

## 工具使用

### 命令行参数：

    
    
    usage:QrlJacker.py [-h] [-r ] [-x ] [--debug] [--dev] [--verbose] [-q]
    
    optional arguments:
    
      -h, --help show this help message and exit
    
      -r         Execute a resource file (history file).
    
      -x         Execute a specific command (use ; for multiples).
    
      --debug    Enables debug mode (Identifying problems easier).
    
      --dev      Enables development mode (Reloading modules every use).
    
      --verbose  Enables verbose mode (Display more details).
    
      -q         Quit mode (no banner).

### 主菜单：

    
    
    General commands
    
    =================
    
           Command               Description
    
           ---------             -------------    
           help/?                Show this help menu.
    
           os     <command>     Execute asystem command without closing the framework
    
           banner                Display banner.
    
           exit/quit             Exit the framework.
    
    Core commands
    
    =============
    
           Command               Description
    
           ---------             -------------    
           database              Prints the core version, check ifframework is up-to-date and update if you are not up-to-date.
    
           debug                 Drop into debug mode ordisable it. (Making identifying problems easier)
    
           dev                   Drop into development modeor disable it. (Reload modules every use)
    
           verbose               Drop into verbose mode or disable it. (Makeframework displays more details)
    
           reload/refresh        Reload the modules database.
    
    Resources commands
    
    ==================
    
           Command               Description
    
           ---------             -------------    
           history               Display commandline most importanthistory from the beginning.
    
           makerc                Save the most importantcommands entered since start to a file.
    
           resource <file>      Run the commandsstored in a file.
    
    Sessions management commands
    
    ============================
    
           Command               Description
    
           ---------             -------------    
           sessions (-h)         Dump session listings and displayinformation about sessions.
    
           jobs    (-h)         Displays and managesjobs.
    
    Module commands
    
    ===============
    
           Command               Description
    
           ---------             -------------    
           list/show             List modules you can use.
    
           use     <module>     Use anavailable module.
    
           info    <module>     Get informationabout an available module.
    
           previous              Runs the previously loadedmodule.
    
           search  <text>       Search for amodule by a specific text in its name or in its description.

### 模块菜单：

    
    
    General commands
    
    =================
    
           Command               Description
    
           ---------             -------------    
           help/?                Show this help menu.
    
           os     <command>     Execute asystem command without closing the framework
    
           banner                Display banner.
    
           exit/quit             Exit the framework.
    
    Core commands
    
    =============
    
           Command               Description
    
           ---------             -------------    
           database              Prints the core version and thencheck if it's up-to-date.
    
           debug                 Drop into debug mode ordisable it. (Making identifying problems easier)
    
           dev                   Drop into development modeor disable it. (Reload modules every use)
    
           verbose               Drop into verbose mode ordisable it. (Make framework displays more details)
    
           reload/refresh        Reload the modules database.
    
    Resources commands
    
    ==================
    
           Command               Description
    
           ---------             -------------    
           history               Display commandline mostimportant history from the beginning.
    
           makerc               Save the mostimportant commands entered since start to a file.
    
           resource <file>      Run the commandsstored in a file.
    
    Sessions management commands
    
    ============================
    
           Command               Description
    
           ---------             -------------    
           sessions (-h)         Dump session listings and displayinformation about sessions.
    
           jobs    (-h)         Displays and managesjobs.
    
    Module commands
    
    ===============
    
           Command               Description
    
           ----------            --------------    
           list/show             List modules you can use.
    
           options               Displays options for the currentmodule.
    
           set                   Sets a context-specificvariable to a value.
    
           run                   Launch the current module.
    
           use    <module>      Use anavailable module.
    
           info   <module>      Getinformation about an available module.
    
           search <text>        Search for amodule by a specific text in its name or in its description.
    
           previous              Sets the previously loaded moduleas the current module.
    
           back                  Move back from the currentcontext.

### 会话命令菜单：

    
    
    usage:sessions [-h] [-l] [-K] [-s] [-k] [-i] 
    
    optional arguments:
    
      -h  Show this help message.
    
      -l  List all captured sessions.
    
      -K  Remove all captured sessions.
    
      -s  Search for sessions with a specifed type.
    
      -k  Remove a specifed captured session by ID
    
      -i  Interact with a captured session by ID.

### 任务命令菜单：

    
    
    usage:jobs [-h] [-l] [-K] [-k] 
    
    optional arguments:
    
      -h  Show this help message.
    
      -l  List all running jobs.
    
      -K  Terminate all running jobs.
    
      -k  Terminate jobs by job ID or module name

## 参考资料

攻击向量文档：【[传送门](https://github.com/OWASP/QRLJacking/wiki)】

QRLJacking漏洞利用框架文档：【[传送门](https://github.com/OWASP/QRLJacking/tree/master/QRLJacker)】

## 存在漏洞的Web应用程序和服务

目前，有很多知名的Web应用以及服务都会受到这种攻击向量的影响，下面给出的是部分受影响的应用：

聊天应用：WhatsApp、微信、Line、微博、QQ；

邮件服务：QQ邮箱（个人和企业）、Yandex Mail；

电子商务：阿里巴巴、Aliexpress、淘宝、天猫、1688.com、阿里妈妈、淘宝旅行；

网络支付：支付宝、Yandex Money、财付通；

Yandex服务：YandexPassport（YandexMail、Yandex Money、Yandex Maps、Yandex Videos等等）；

移动管理软件：AirDroid；

其他服务：MyDigiPass、Zapper & ZapperWordPress Login by QR Code插件、Trustly
App、Yelophone、Alibaba Yunos。

## 项目地址

QRLJacker：【[GitHub传送门](https://github.com/OWASP/QRLJacking)】

***参考来源：[QRLJacking](https://github.com/OWASP/QRLJacking)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

