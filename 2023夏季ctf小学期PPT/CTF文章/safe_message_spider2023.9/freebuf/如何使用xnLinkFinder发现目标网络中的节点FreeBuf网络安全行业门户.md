![](https://image.3001.net/images/20221025/1666687935_6357a3bfc37fa9eecf3a0.png!small)

## 关于xnLinkFinder

xnLinkFinder是一款基于Python
3开发的网络节点发现工具，在该工具的帮助下，广大研究人员只需要提供一个目标网络地址，xnLinkFinder就能够发现其中的网络节点。

## 功能介绍

> 1、根据域名/URL爬取目标网络；
>
> 2、根据包含域名/URL的文件爬取多个目标网络；
>
> 3、搜索给定目录（以目录名作为参数）中的文件；
>
> 4、通过Burp项目获取节点（传递Burp XML文件路径）；
>
> 5、通过OWASP ZAP项目获取节点（传递ZAP ASCII消息文件路径）；
>
> 6、处理一个[ _waymore_](https://github.com/xnl-h4ck3r/waymore)结果目录；

Python脚本基于[ _GAP_](https://github.com/xnl-h4ck3r/burp-extensions)（一个Burp扩展）的链接发现功能实现，并引入了[
_LinkFinder_](https://github.com/GerbenJavado/LinkFinder)工具的部分能力，然后使用正则表达式来发现链接。

## 工具安装

xnLinkFinder基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python
3环境。接下来，可以使用下列命令将该项目源码克隆至本地，并运行setup.py脚本完成工具的安装：

    
    
    $ git clone https://github.com/xnl-h4ck3r/xnLinkFinder.git
    
    $ cd xnLinkFinder
    
    $ sudo python setup.py install

## 工具参数命令

 ** **短参数****

|

 ** **长参数****

|

 ** **参数描述****  
  
---|---|---  
  
-i

|

\--input

|

指定一个URL、URL列表txt、目录、Burp XML输出文件或OWASP ZAP输出文件；  
  
-o

|

\--output

|

指定存储输出的文件，默认为output.txt；  
  
-op

|

\--output-params

|

存储潜在参数的文件路径，默认为parameters.txt；  
  
-ow

|

\--output-overwrite

|

如果输出文件存在，将覆盖之前的内容，而不是追加；  
  
-sp

|

\--scope-prefix

|

设置搜索的域名前缀范围，“/”表示原始链接，也可以指定一个其他节点；  
  
-spo

|

\--scope-prefix-original

|

如果指定了-sp，则这将确定以/开头的原始链接是否也包含在输出中（默认值：false）；  
  
-sf

|

\--scope-filter

|

如果链接的域在指定的范围内，将筛选输出链接以仅包含它们。如果传递的值是有效的文件名，则将使用该文件，否则将使用字符串文本；  
  
-c

|

\--cookies †

|

以'name1=value1; name2=value2;'格式添加Cookie并传递给HTTP请求；  
  
-H

|

\--headers †

|

以'Header1: value1; Header2: value2;'格式添加自定义Header并使用HTTP请求传递；  
  
-ra

|

\--regex-after

|

用于在输出数据之前对数据过滤的正则表达式；(例如. /api/v[0-9]\\.[0-9]\\* )  
  
-x

|

\--exclude

|

排除其他链接节点，例如careers,forum；  
  
-orig

|

\--origin

|

是否在输出中包含原始链接；  
  
-t

|

\--timeout †

|

等待服务器发送数据的时间，默认为10秒；  
  
-inc

|

\--include

|

在输出中包含输入（-i）的链接；  
  
-u

|

\--user-agent †

|

使用的User-Agent，例如 -u desktop mobile  
  
-insecure

|

†

|

是否禁用TLS证书检测；  
  
-s429

|

†

|

当请求链接返回429 Too Many Requests超过95%时终止运行，默认关闭；  
  
-s403

|

†

|

当请求链接返回403 Forbidden超过95%时终止运行，默认关闭；  
  
-sTO

|

†

|

当请求链接超时超过95%时终止运行，默认关闭；  
  
-sCE

|

†

|

当请求链接失败超过95%时终止运行，默认关闭；  
  
-m

|

\--memory-threshold

|

设置内存阈值百分比，默认为95；  
  
-mfs

|

\--max-file-size †

|

设置最大文件大小，默认为500MB；  
  
-replay-proxy

|

†

|

通过代理重放请求；  
  
-ascii-only

|

  

|

开启ASCII字符支持；  
  
-v

|

\--verbose

|

开启Verbose模式；  
  
-vv

|

\--vverbose

|

增强Verbose模式；  
  
  

|

\--version

|

显示当前工具版本；  
  
-h

|

\--help

|

显示工具帮助信息；  
  
## 工具使用样例

### 根据指定目标发现链接

    
    
    python3 xnLinkFinder.py -i target.com

### 根据指定目标发现链接（包含详细信息）

    
    
    python3 xnLinkFinder.py -i target.com -sp target_prefix.txt -sf target_scope.txt -spo -inc -vv -H 'Authorization: Bearer XXXXXXXXXXXXXX' -c 'SessionId=MYSESSIONID' -u desktop mobile -d 10

### 根据URL列表发现链接

    
    
    python3 xnLinkFinder.py -i target_js.txt

### 根据目录文件发现链接

    
    
    python3 xnLinkFinder.py -i ~/Tools/waymore/results/target.com

### 从Burp项目发现链接

    
    
    python3 xnLinkFinder.py -i target_burp.xml

### 从Burp项目发现链接（包含详细信息）

    
    
    python3 xnLinkFinder.py -i target_burp.xml -o target_burp.txt -sp https://www.target.com -sf target.* -ow -spo -inc -vv

### 从OWASP ZAP项目发现链接

    
    
    python3 xnLinkFinder.py -i target_zap.txt

### 从Waymore结果目录发现链接

    
    
    python3 xnLinkFinder.py -i ~/Tools/waymore/results/target.com

### 将结果通过管道发送给其他工具

    
    
    python3 xnLinkFinder.py -i redbull.com -sp https://redbull.com -sf rebbull.* -d 3 | unfurl keys | sort -u
    
    cat redbull_subs.txt | python3 xnLinkFinder.py -sp https://redbull.com -sf rebbull.* -d 3

## 工具演示样例

![](https://image.3001.net/images/20221025/1666688056_6357a438ceb07c01edd60.png!small)![](https://image.3001.net/images/20221025/1666688064_6357a440946458dc6f496.png!small)

![](https://image.3001.net/images/20221025/1666688073_6357a449be2e6ca536057.png!small)

  

## 项目地址

 **xnLinkFinder** ：【[
_GitHub传送门_](https://github.com/xnl-h4ck3r/xnLinkFinder)】

## 参考资料

> [
> _https://github.com/xnl-h4ck3r/waymore_](https://github.com/xnl-h4ck3r/waymore)
>
> [
> _https://github.com/GerbenJavado/LinkFinder_](https://github.com/GerbenJavado/LinkFinder)
>
> [ _https://regex101.com/_](https://regex101.com/)

