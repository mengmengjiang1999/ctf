你有没有在输入域名时把字母输错但是出现了你想要看到的网页？像appple.com、taobaoo.com这样的网页如果模仿了原网页，可以成为钓鱼网站。那么如果把脚本代码包起了一样差不多的名字感染进开发者的电脑里呢？想想就不寒而栗。

![decryptiontool.jpg](https://image.3001.net/images/20200610/1591785595_5ee0b87b65e8e.jpg!small)

大约10年前，有种名为Typosquatting的古老攻击手法——国内有将之翻译成“误植域名”的。这个词的前半部分“Typo”意思是排版错误，其实已经表达了这种攻击手法的内涵。

URLCrazy是一款针对域名安全的攻击测试工具，它本质上是一款OSINT公开资源情报工具，可以帮助广大研究人员生成并测试钓鱼域名及其变种，并执行Typo
Squatting、URL劫持、网络钓鱼以及企业间谍活动等等。

## 使用场景

> 1、通过错误输入域名检测Typo Squatting误值域名攻击；
>
> 2、通过注册常见域名Typo来保护企业域名安全；
>
> 3、识别潜在的Typo域名；
>
> 4、在渗透测试过程中执行网络钓鱼攻击；

## 功能介绍

1、生成15种域名变种；

2、已知超过8000种常见拼写错误；

3、支持比特位翻转攻击；

4、多种键盘布局（qwerty、azerty、qwertz、dvorak）;

5、检测域名变种是否有效；

6、测试域名变种是否正在使用中；

7、评估域名变种热门程度；

## 工具安装

### 通过包管理器安装

如果你使用的是Kali Linux、Ubuntu或Debian系统，那么你就可以使用下列命令安装URLCrazy了：

    
    
    $ sudo apt install urlcrazy

### 安装最新Release版本

或者，你也可以直接点击下列链接下载URLCrazy最新的Release版本：【[
_点我获取_](https://github.com/urbanadventurer/urlcrazy/releases)】

### 安装当前开发版本

这里需要注意的是，最新的开发版本可能并不稳定：

    
    
    $ git clone https://github.com/urbanadventurer/urlcrazy.git

### 安装Ruby

URLCrazy目前已在Ruby v2.4和v2.6版本上进行了测试，如果你使用的是Ubuntu或Debian，则可以运行下列命令安装：

    
    
    $ sudo apt install ruby

### 安装Bundler

Bundler可以给Ruby项目提供依赖组件的管理功能：

    
    
    $ gem install bundler

### 安装依赖组件

    
    
    $ bundle install

或者，如果你不想安装bundler，你也可以选择使用下列命令安装gem依赖：

    
    
    $ gem install json colorize async async-dns async-http

### 命令行参数

``Usage: ./urlcrazy [options] domain``

``

````

``

`` ``

``

````

``

``Options``

``

````

``

``-k, --keyboard=LAYOUT Options are: qwerty, azerty, qwertz, dvorak (default:
qwerty)``

``

````

``

``-p, --popularity Check domain popularity with Google``

``

````

``

``-r, --no-resolve Do not resolve DNS``

``

````

``

``-i, --show-invalid Show invalid domain names``

``

````

``

``-f, --format=TYPE Human readable or CSV (default: human readable)``

``

````

``

``-o, --output=FILE Output file``

``

````

``

``-n, --nocolor Disable colour``

``

````

``

``-h, --help This help``

``

````

``

``-v, --version Print version information. This version is 0.7``

``

``

``

## 工具使用``

![1.gif](https://image.3001.net/images/20200610/1591785664_5ee0b8c0c4a01.gif!small)

### 简单使用样例

默认选项下，URLCrazy将会检测目标站点的超过2000个Typo域名变种：

    
    
    $ urlcrazy google.com

![2.gif](https://image.3001.net/images/20200610/1591785686_5ee0b8d6ab7bb.gif!small)

### 评估热门程度

    
    
    $ urlcrazy -p domain.com

## 项目地址

> URLCrazy：【[ _GitHub传送门_](https://github.com/urbanadventurer/urlcrazy/)】

##  参考来源

> urbanadventurer

