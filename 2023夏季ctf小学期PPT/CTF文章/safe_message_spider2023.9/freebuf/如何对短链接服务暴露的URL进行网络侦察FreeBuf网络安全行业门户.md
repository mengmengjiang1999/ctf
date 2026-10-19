![](https://image.3001.net/images/20210125/1611504931_600d9d238a90a2c55304a.png!small)

## Urlhunter

Urlhunter是一款网络侦察和信息收集工具，该工具基于Go语言开发。在该工具的帮助下，广大研究人员可以轻松搜索通过短链接服务暴露的URL以及相关资源，比如说bit.ly和goo.gl等等。

## 工具安装

### 源码安装

广大研究人员可以点击【[
_这里_](https://github.com/utkusen/urlhunter/releases/latest)】访问该项目的预构建源码并运行。比如说：

    
    
    tar xzvf urlhunter_0.1.0_Linux_amd64.tar.gz
    
    ./urlhunter --help

### Go安装

首先，我们需要在自己的计算机设备上安装并配置好Go环境。

接下来，运行下列命令即可完成工具的安装：

    
    
    go get -u github.com/utkusen/urlhunter

如果你使用的是Windows系统，那你需要注意了。因为Urlhunter所使用的XZ
Utils在Linux和macOS系统上是自带的。那么对于Windows，则需要手动从h[
_ttps://tukaani.org/xz/_](https://tukaani.org/xz/)下载。

## 工具使用

Urlhunter的运行需要使用三个参数，即-keywords、-date和-o。

比如说：

    
    
    urlhunter -keywords keywords.txt -date 2020-11-20 -o out.txt

### -keywords

你需要指定包含了关键词的txt文件，每个关键词单独占一行，我们有三种不同的方式来指定关键词。

单个关键词：Urlhunter将会把给定的关键词以子字符串的形式进行搜索，比如说，关键词acme.com将匹配到https://acme.com/blabla和https://another.com/?referrer=acme.com。

多个关键词：Urlhunter将会把给定的关键词以AND逻辑的形式进行搜索，这也就意味着，URL必须包含所有提供的关键词。关键词必须以“,”分隔，比如说，关键词acme.com,admin将匹配到https://acme.com/secret/adminpanel，但无法匹配到https://acme.com/somethingelse。

正则表达式：Urlhunter将会搜索给定的正则表达式。在关键词文件中，正则表达式必须以“regex”字符串开头，格式为regex
REGEXFORMULA。比如说，regex
1\d{10}将会匹配到https://example.com/index.php?id=12938454312，但无法匹配到https://example.com/index.php?id=abc223。

### -date

Urlhunter可以根据给定的日期参数来下载文件，我们有三种方式来指定日期参数。

最新日期：Urlhunter将会下载最新的文档，比如说：

    
    
    -date latest

单个日期：Urlhunter将会根据给定日期下载文件，日期格式为YYYY-MM-DD。比如说：

    
    
    -date 2020-11-20

日期范围：Urlhunter将会下载给定日期范围内的文件，比如说：

    
    
    -date 2020-11-10:2020-11-20

### -o

我们可以使用-o参数来指定输出文件，比如说：

    
    
    -o out.txt

## 使用样例

Urlhunter可以用于网络侦察、情报收集和漏洞挖掘等安全活动中。比如说：

docs.google.com/a/acme.com和drive.google.com/a/acme.com关键词将会帮助我们查找Acme公司的公共Google
Docs&Drive共享链接。

而acme.com,password_reset_token关键词可以帮助我们查找acme.com的有效密码重置令牌。

trello.com允许我们查找公共Trello地址。

## 工具使用演示

视频地址：[ _https://www.油管.com/watch?v=Ct086YRm7i8_](https://www.xn--uvwy13a.com/watch?v=Ct086YRm7i8)

## 项目地址

Urlhunter：【[ _GitHub传送门_](https://github.com/utkusen/urlhunter)】

