##  ExtAnalysis

![1.png](https://image.3001.net/images/20190517/1558062707_5cde2673f2362.png!small)

ExtAnalysis是一款功能较为强大的浏览器插件安全分析框架，在它的帮助下，我们可以干这些事情：

1、 从以下两个地方下载&分析浏览器扩展：

a) [Chrome Web商店](https://chrome.google.com/)

b) [Firefox Addon](https://addons.mozilla.org/)

2、 分析已安装的扩展插件：

a) GoogleChrome

b) MozillaFirefox

c) Opera浏览器（即将上线）

3、 上传和扫描已支持格式的浏览器扩展文件：

a) .crx

b) .xpi

c) .zip

##  功能介绍

1、 查看基本信息：

a) 扩展名称、开发者、功能描述和版本信息

2、 Manifest文件查看；

3、 详细权限信息；

4、 从文件中提取详细信息：

a) URL和域名

b) IPv6和IPv4地址

c) 比特币地址

d) 电子邮箱地址

e) 文件注释

f) Base64编码字符串

5、 查看和编辑支持类型的文件：

a) Html

b) Json

c) JavaScript

d) Css

6、 VirusTotal扫描支持：

a) URL地址

b) 域名

c) 文件

7、 针对JavaScript文件进行RetireJS漏洞扫描；

8、 所有文件及URL的网络图；

9、 针对已提取URL的网络侦查工具：

a) Whois扫描

b) HTTPHeader查看器

c) URL源查看器

d) 基于IP的地理定位信息

##  工具安装

安装ExtAnalysis其实非常简单，该工具基于Python
开发，在确保了python3和python3-pip已经安装并配置完毕之后，运行下列命令即可完成工具安装：

    
    
    $ gitclone https://github.com/Tuhinshubhra/ExtAnalysis
    $ cd ExtAnalysis
    $ pip3 install -r requirements.txt  
    

如果你想获取更加完整的分析结果，别忘了添加你的VirusTotal API噢！

##  工具使用

工具安装完成之后，你就可以直接运行下列命令来启动ExtAnalysis了：

    
    
    $ python3 extanalysis.py

运行命令之后，会自动在新窗口开启ExtAnalysis。

如需了解更多参数选项，可以运行下列命令查看工具的帮助页面：

    
    
    $python3 extanalysis.py --help
    usage:extanalysis.py [-h HOST] [-p PORT] [-v] [-u] [-q] [--help]
    optional arguments:
      -h HOST, --host HOST  Host to run ExtAnalysis on. Default host is127.0.0.1
      -p PORT, --port PORT  Port to run ExtAnalysis on. Default port is13337
      -v, --version         Shows version and quits
      -u, --update          Checks for update
      -q, --quiet           Quiet mode shows only errors on cli!
      --help                Shows this help menu and exits  
    

###  Docker构建

    
    
    $ docker build -t extanalysis

###  Docker使用

    
    
    $ docker run --rm -it -p 13337:13337 extanalysis -h 0.0.0.0

##  使用的Python模块

1、 Web服务器使用了Flask框架；

2、 Whois查询使用了python-whois模块；

3、 使用了maxminddb来解析地理位置-IP数据库；

4、 HTTP Header和源代码查看工具引入了requests模块；

##  工具运行截图

![2.png](https://image.3001.net/images/20190517/1558062774_5cde26b615b26.png!small)![3.png](https://image.3001.net/images/20190517/1558062774_5cde26b6c5192.png!small)

##  许可证协议

本项目遵顼[GNU GeneralPublic License
v3.0](https://github.com/Tuhinshubhra/ExtAnalysis/blob/master/LICENSE)开源许可证协议。

##  项目地址

ExtAnalysis：【[GitHub传送门](https://github.com/Tuhinshubhra/ExtAnalysis)】

***参考来源：[Tuhinshubhra](https://github.com/Tuhinshubhra/ExtAnalysis)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

