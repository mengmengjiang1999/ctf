## 关于hakoriginfinder

hakoriginfinder是一款功能强大的网络安全工具，在该工具的帮助下，广大研究人员可以轻松识别反向代理背后的真实原始主机。一般来说，这种技术适用于红队研究工作中针对Web应用防火墙的绕过和其他反向代理安全方面的任务。

## 工具运行机制

hakoriginfinder首先会向研究人员提供的主机名称发送一个HTTP请求，并存储目标主机返回的响应信息。接下来，该工具将会通过HTTP（80）和HTTPS（443）向广大研究人员提供的每一个IP地址发送请求，其中的每一个请求中Host头都被设置为了原始主机。然后，该工具会使用Levenshtein算法将每个HTTP响应与原始响应进行比较，以确定相似度。如果响应信息相似，则视为匹配。

## 工具下载

该工具基于Go语言开发，因此广大研究人员首先需要在本地设备上安装并配置好Go语言环境。

接下来，我们可以直接使用下列命令下载和安装hakoriginfinder：

    
    
    go install github.com/hakluke/hakoriginfinder@latest

或者说，可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/hakluke/hakoriginfinder.git

## 工具使用

我们可以通过stdin向工具提供一个目标IP地址列表，并通过-h参数来设置原始主机的主机名，参考命令如下：

    
    
    prips 93.184.216.0/24 | hakoriginfinder -h example.com

我们还可以通过-l参数来设置Levenshtein算法的距离阈值。设置的数值越低，则表示要求匹配度越高，该参数默认值为5。

除此之外，我们还可以通过-t参数来设置工具运行所使用的线程数量，默认为32。

使用-h参数则可以直接设置主机名称，这个参数是没有默认值的，为必填选项。

## 输出结果

该工具的输出结果为三列，其中以空格划分。第一列为匹配结果，可能出现的值为“MATCH”或“NOMATCH”，具体取决于分析结果是否达到了Levenshtein算法的阈值。第二列为测试的URL地址，第三列则为Levenshtein算法的评分。

下面给出的是hakoriginfinder工具执行的样例输出结果：

    
    
    hakluke$ prips 1.1.1.0/24 | hakoriginfinder -h one.one.one.one
    
    NOMATCH http://1.1.1.0 54366
    
    NOMATCH http://1.1.1.30 54366
    
    NOMATCH http://1.1.1.20 54366
    
    NOMATCH http://1.1.1.4 54366
    
    NOMATCH http://1.1.1.11 54366
    
    NOMATCH http://1.1.1.5 54366
    
    NOMATCH http://1.1.1.22 54366
    
    NOMATCH http://1.1.1.13 54366
    
    NOMATCH http://1.1.1.10 54366
    
    NOMATCH http://1.1.1.25 54366
    
    NOMATCH http://1.1.1.19 54366
    
    ... snipped for brevity ...
    
    NOMATCH http://1.1.1.251 54366
    
    NOMATCH http://1.1.1.248 54366
    
    MATCH http://1.1.1.1 0
    
    NOMATCH http://1.1.1.3 19567
    
    NOMATCH http://1.1.1.2 19517
    
    MATCH https://1.1.1.1 0
    
    NOMATCH https://1.1.1.3 19534
    
    NOMATCH https://1.1.1.2 19532

## 项目地址

 **hakoriginfinder：** 【[
_GitHub传送门_](https://github.com/hakluke/hakoriginfinder)】

