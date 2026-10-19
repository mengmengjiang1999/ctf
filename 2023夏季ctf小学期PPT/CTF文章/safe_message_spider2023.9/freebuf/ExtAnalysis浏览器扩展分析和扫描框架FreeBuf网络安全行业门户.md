**ExtAnalysis是一个浏览器扩展分析框架，用于分析和扫描Chrome和firefox扩展以查找其可能存在的漏洞。**

## 使用 ExtAnalysis 你可以

从以下位置下载和分析扩展程序：

> [Chrome Web Store](https://chrome.google.com/)
>
> [Firefox Addons](https://addons.mozilla.org/)

分析已安装的扩展程序：

> Google Chrome
>
> Mozilla Firefox
>
> Opera Browser（即将支持）

上传和扫描扩展程序。支持格式如下：

> .crx
>
> .xpi
>
> .zip

## 特性

1\. 查看基本信息：

> 名称，构建者，描述和版本号

2\. Manifest Viewer

3\. 深入许可信息

4\. 从包含以下内容的文件中提取Intels：

> URLs 和 域
>
> IPv6 和 IPv4 地址
>
> 比特币地址
>
> Email 地址
>
> 文件评论
>
> Base64 编码字符串

5\. 查看和修改文件。已支持的格式如下：

> html
>
> json
>
> JavaScript
>
> css

6\. VirusTotal 扫描：

> URLs
>
> 域
>
> 文件

7\. 针对JavaScript文件的RetireJS漏洞扫描

8\. 所有文件和URL的网络图

提取URL的侦察工具包括：

> Whois Scan
>
> HTTP headers viewer
>
> URL Source viewer
>
> GEO-IP location

其他一些有趣的包括：

> Dark Mode
>
> 内置 chiptune player

## 安装

安装ExtAnalysis很简单！它运行在python3上，因此请确保你已安装python3和python3-pip，并按照以下步骤操作：

    
    
    $ git clone https://github.com/Tuhinshubhra/ExtAnalysis
    
    
    $ cd ExtAnalysis
    
    
    $ pip3 install -r requirements.txt

另外，不要忘了添加你的virustotal api。

## 使用

安装完成后，你可以直接跳转并通过命令$python3
extanalysis.py直接运行ExtAnalysis。它应该会在新的浏览器窗口中自动启动ExtAnalysis。

有关其他选项，请查看帮助菜单$python3 extanalysis.py --help

    
    
    usage: extanalysis.py [-h HOST] [-p PORT] [-v] [-u] [-q] [--help]
    
    optional arguments:
      -h HOST, --host HOST  Host to run ExtAnalysis on. Default host is 127.0.0.1
      -p PORT, --port PORT  Port to run ExtAnalysis on. Default port is 13337
      -v, --version         Shows version and quits
      -u, --update          Checks for update
      -q, --quiet           Quiet mode shows only errors on cli!
      --help                Shows this help menu and exits

## Docker 构建

    
    
    $ docker build -t extanalysis .

## Docker 使用

    
    
    $ docker run --rm -it -p 13337:13337 extanalysis -h 0.0.0.0

## 使用的 Python 模块：

> flask用于webserve
>
> python-whois用于Whois查找
>
> maxminddb用于解析Geo-IP数据库
>
> requests用于http headers和source code viewer

## 截图

![68747470733a2f2f692e696d6775722e636f6d2f466347617257472e706e67.png](https://image.3001.net/images/20190617/1560725480_5d06c7e8c8f50.png!small)![68747470733a2f2f692e696d6775722e636f6d2f76494f53444c652e706e67.png](https://image.3001.net/images/20190617/1560725487_5d06c7efecb46.png!small)

## 贡献

你可以通过改进某些代码甚至是报告bug来为ExtAnalysis的开发做出贡献。

如有任何其他疑问，欢迎随时通过Twitter与我联系：[@r3dhax0r](https://twitter.com/r3dhax0r)

***参考来源：[GitHub](https://github.com/Tuhinshubhra/ExtAnalysis)，FB小编secist编译，转载请注明来自FreeBuf.COM**

