![a.jpg](https://image.3001.net/images/20190614/1560506029_5d036ead4d519.jpg!small)

## 工具介绍

 **Python-Iocextract是一款高级入侵威胁标识符IoC提取工具，它可以从文本语料库提取URL、IP地址、MD5/SHA哈希、电子邮件地址和YARA规则，其中还包括某些已编码或已被“破坏”的入侵威胁标识符。**

因为网络犯罪分子为了防止暴露自己的恶意活动以及攻击内容，通常都会想办法“破坏”类似URL和IP地址这样的入侵威胁标识符。在这种情况下，有效提取和汇总这些IoC对于安全分析人员来说就非常有价值了。但不幸的是，对于现有的IoC提取工具来说，标准的正则表达式往往无法捕捉到这些东西。

比如说，下面这个样本就使用了括号来进行IoC隐藏：

    
    
    127[.]0[.]0[.]1

这种情况下，基于简单正则表达式匹配的工具就无法提取出这种IoC了。

但是对于Python-Iocextract来说，情况就不一样了。通过使用精心设计的正则表达式以及反混淆检测技术，我们既可以检测到“被破坏”的IoC，也可以还原初始的IoC，为分析人员节省了时间和精力。

## 工具安装

在使用Python-Iocextract之前，我们需要安装Python开发环境以及regex依赖。在Ubuntu和Debian等Linux系统中，可以使用下列命令完成安装：

    
    
    sudo apt-get install python-dev

接下来，使用pip命令安装iocextract：

    
    
    pip install iocextract

在Windows平台下，点击【[这里](https://pypi.org/project/regex/#files)】下载regex安装包：

    
    
    pip install regex-2018.06.21-cp27-none-win_amd64.whl

## 工具使用

提取某些已被破坏的URL地址：

    
    
    >>>content = """
    
    ... Ireally love example[.]com!
    
    ...All the bots are on hxxp://example.com/bad/url these days.
    
    ...C2: tcp://example[.]com:8989/bad
    
    ..."""
    
    >>>import iocextract
    
    >>>for url in iocextract.extract_urls(content):
    
    ...     print url
    
    ...
    
    hxxp://example.com/bad/url
    
    tcp://example[.]com:8989/bad
    
    example[.]com
    
    tcp://example[.]com:8989/bad

如果匹配到多个正则表达式的话，可能会有某些URL地址出现两次。

如果有需要的话，你还可以还原IoC并移除某些常见的混淆技术：

    
    
    >>>for url in iocextract.extract_urls(content, refang=True):
    
    ...     print url
    
    ...
    
    <http://example.com/bad/url>
    
    <http://example.com:8989/bad>
    
    <http://example.com>
    
    <http://example.com:8989/bad>

你甚至还可以提取并解码十六进制编码或Base64编码的URL地址：

    
    
    >>>content ='612062756e6368206f6620776f72647320687474703a2f2f6578616d706c652e636f6d2f70617468206d6f726520776f726473'
    
    >>>for url in iocextract.extract_urls(content):
    
    ...     print url
    
    ...
    
    687474703a2f2f6578616d706c652e636f6d2f70617468
    
    >>>for url in iocextract.extract_urls(content, refang=True):
    
    ...     print url
    
    ...
    
    <http://example.com/path>

该工具中所有的extract_*函数返回的都是迭代器，而不是列表。因此，iocextract可以处理大量数据输入。但如果你想要迭代处理多次IoC，你将需要把结果存储为列表：

    
    
    >>>list(iocextract.extract_urls(content))
    
    ['hxxp://example.com/bad/url','tcp://example[.]com:8989/bad', 'example[.]com','tcp://example[.]com:8989/bad']

### 命令行工具还包括：

    
    
    $iocextract -h
    
    usage:iocextract [-h] [--input INPUT] [--output OUTPUT] [--extract-emails]
    
                  [--extract-ips] [--extract-ipv4s][--extract-ipv6s]
    
                  [--extract-urls] [--extract-yara-rules][--extract-hashes]
    
                  [--custom-regex REGEX_FILE][--refang] [--strip-urls]
    
                  [--wide]
    
     
    
    AdvancedIndicator of Compromise (IOC) extractor. If no arguments are
    
    specified,the default behavior is to extract all IOCs.
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      --input INPUT         default: stdin
    
      --output OUTPUT       default: stdout
    
      --extract-emails
    
      --extract-ips
    
      --extract-ipv4s
    
      --extract-ipv6s
    
      --extract-urls
    
      --extract-yara-rules
    
      --extract-hashes
    
      --custom-regex REGEX_FILE
    
                            file with custom regexstrings, one per line, with one
    
                            capture group each
    
      --refang              default: no
    
      --strip-urls          remove possible garbage from the endof urls. default:
    
                            no
    
      --wide                preprocess input to allowwide-encoded character
    
                            matches. default: no

目前，该工具只支持恢复URL、电子邮件以及IPv4地址。

## Python-Iocextract支持的IoC

### IP地址

1、 完全支持IPv4

2、 部分支持IPv6

### URL地址

1、 协议标识符：http, https, tcp,udp, ftp, sftp, ftps

2、 [.]锚点

3、 十六进制编码URL：http, https, ftp

4、 URL编码URL：http, https, ftp, ftps, sftp

5、 Base64编码URL：http, https, ftp

### 电子邮件地址

支持部分@或at锚点

### YARA规则

导入、包含和注释

### 哈希

1、 MD5

2、 SHA1

3、 SHA256

4、 SHA512

针对IPv4地址，支持扫描下列混淆技术：

![b.png](https://image.3001.net/images/20190614/1560506108_5d036efcac51e.png!small)

针对电子邮件地址，支持扫描下列混淆技术：

![c.png](https://image.3001.net/images/20190614/1560506115_5d036f034e043.png!small)

### 针对URL地址，支持扫描下列混淆技术：

![d.png](https://image.3001.net/images/20190614/1560506121_5d036f09b5382.png!small)

## 项目地址

Python-Iocextract：【[GitHub传送门](https://github.com/inquest/python-iocextract)】

 *** 参考来源：[inquest](https://github.com/inquest/python-iocextract)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

