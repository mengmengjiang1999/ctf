![](https://image.3001.net/images/20210722/1626923961_60f8e3b9f11e1e6d8eea6.png!small)

## 关于Cariddi

Cariddi是一款功能强大的信息收集与扫描工具，我们只需给它提供一个域名列表，Cariddi就能够帮助我们爬取URL地址，扫描终端节点，并搜索敏感数据、API密钥、文件后缀和令牌等信息。

## 工具安装

首先，我们需要在本地设备上安装并配置好[ _Go_](https://golang.org/)环境。

### Linux安装

首先，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/edoardottt/cariddi.git
    
    cd cariddi
    
    go get

运行下列命令即可安装Cariddi：

    
    
    make linux

运行下列命令即可卸载Cariddi：

    
    
    make unlinux

或者，我们也可以直接运行下列一行命令：

    
    
    git clone https://github.com/edoardottt/cariddi.git; cd cariddi; go get; make linux

### Windows安装（可执行程序只能在cariddi目录下运行）

首先，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/edoardottt/cariddi.git
    
    cd cariddi
    
    go get

运行下列命令即可安装Cariddi：

    
    
    .\make.bat windows

运行下列命令即可卸载Cariddi：

    
    
    .\make.bat unwindows

## 工具使用

在命令行窗口中运行命令“cariddi -h”，即可查看工具的帮助信息：

    
    
    Usage of cariddi:
    
      -c int
    
         Concurrency level. (default 20)
    
      -cache
    
    Use the .cariddi_cache folder as cache.
    
      -d int
    
         Delay between a page crawled and another.
    
      -e Hunt for juicy endpoints.
    
      -ef string
    
         Use an external file (txt, one per line) to use custom parameters for endpoints hunting.
    
      -examples
    
         Print the examples.
    
      -ext int
    
         Hunt for juicy file extensions. Integer from 1(juicy) to 7(not juicy).
    
      -h Print the help.
    
      -i string
    
         Ignore the URL containing at least one of the elements of this array.
    
      -intensive
    
         Crawl searching for resources matching 2nd level domain.
    
      -it string
    
         Ignore the URL containing at least one of the lines of this file.
    
      -oh string
    
         Write the output into an HTML file.
    
      -ot string
    
         Write the output into a TXT file.
    
      -plain
    
         Print only the results.
    
      -s Hunt for secrets.
    
      -sf string
    
         Use an external file (txt, one per line) to use custom regexes for secrets hunting.
    
      -t int
    
       Set timeout for the requests. (default 10)
    
      -version
    
         Print the version.

## 工具使用样例

### Linux环境

    
    
    cariddi -version (打印工具版本信息)
    
     
    
    cariddi -h (打印工具帮助信息)
    
     
    
    cariddi -examples (输出样例)
    
     
    
    cat urls | cariddi -s (搜索敏感信息)
    
     
    
    cat urls | cariddi -d 2 (设置页面爬取间隔为2秒)
    
     
    
    cat urls | cariddi -c 200 (将并发级别设置为200)
    
     
    
    cat urls | cariddi -e (搜索有价值的终端节点)
    
     
    
    cat urls | cariddi -plain (仅输出有用的信息)
    
     
    
    cat urls | cariddi -ot target_name (将结果存储至txt文件中)
    
     
    
    cat urls | cariddi -oh target_name (将结果存储至html文件中)
    
     
    
    cat urls | cariddi -ext 2 (搜索有价值的文件(等级2-7))
    
     
    
    cat urls | cariddi -e -ef endpoints_file (搜索自定义终端节点)
    
     
    
    cat urls | cariddi -s -sf secrets_file (搜索自定义敏感信息)
    
     
    
    cat urls | cariddi -i forum,blog,community,open (忽略包含这些关键词的URL)
    
     
    
    cat urls | cariddi -it ignore_file (忽略包含输入文件中内容的URL)
    
     
    
    cat urls | cariddi -cache (使用.cariddi_cache作为缓存目录)
    
     
    
    cat urls | cariddi -t 5 (设置请求超时)
    
     
    
    cat urls | cariddi -intensive (爬取搜索与第二级域匹配的资源)

### Windows使用样例

    
    
    powershell.exe -Command "cat urls | .\cariddi.exe"

## 工具演示视频

视频地址：【[ _点我观看_](https://asciinema.org/a/415989)】

## 项目地址

 **Cariddi：** 【[ _GitHub传送门_](https://github.com/edoardottt/cariddi)】

## 许可证协议

本项目的开发与发布遵循[ _GNU
v3.0开源许可证协议_](https://github.com/edoardottt/cariddi/blob/main/LICENSE)。

## 参考资料

[ _https://www.edoardoottavianelli.it/_](https://www.edoardoottavianelli.it/)

[
_https://github.com/zricethezav/gitleaks/blob/master/config/default.go_](https://github.com/zricethezav/gitleaks/blob/master/config/default.go)

[
_https://github.com/edoardottt/cariddi/blob/master/CODE_OF_CONDUCT.md_](https://github.com/edoardottt/cariddi/blob/master/CODE_OF_CONDUCT.md)

[ _https://golang.org/﻿_](https://golang.org/)

