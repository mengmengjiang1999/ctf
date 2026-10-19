**Imaginary C2是一款python工具，可帮助安全研究人员分析恶意软件（网络）行为。Imaginary
C2上托管了一个HTTP服务器，用于捕获选定域/IP的HTTP请求。此外，该工具还可用于重放捕获的C
&C响应/payloads，使这个过程变得更加方便快捷。**

通过使用该工具，分析师可以向恶意软件提供一致的网络响应（例如，恶意软件要执行的C＆C指令），以及捕获并检查对分析时离线域/IP的HTTP请求。

![imaginary_c2.png](https://image.3001.net/images/20180830/1535587996_5b87369c8d82f.png!small)

## 重放数据包捕获

Imaginary C2提供了两个脚本，用于将数据包捕获（PCAP）或Fiddler会话存档转换为可由Imaginary
C2解析的请求定义。通过这些脚本，用户可以提取HTTP请求URL和域，以及HTTP响应。这样，便可以快速的重放给定HTTP请求的HTTP响应了。

## 技术细节

 **安装环境：** Python 2.7 和 Windows。

 **模块：** 当前，Imaginary C2包含三个模块以及两个配置文件：

文件名 | 功能  
---|---  
1\. imaginary_c2.py | 托管python的简单HTTP服务器。主要模块。  
2\. redirect_to_imaginary_c2.py | 更改Windows的主机文件和Windows（IP）路由表。  
3\. unpack_fiddler_archive.py & unpack_pcap.py |
从数据包捕获中提取HTTP响应。将相应的HTTP请求域和URL添加到配置文件中。  
4\. redirect_config.txt | 包含需要重定向到localhost（到python HTTP服务器）的域和IP。  
5\. requests_config.txt | 包含具有相应数据源的URL路径定义。  
  
**请求定义** ：在请求配置中的各个（HTTP）请求定义包含两个参数：

参数1：HTTP请求URL路径（a.k.a. urlType）

值 | 含义  
---|---  
fixed | 定义URL路径作为一个literal字符串  
regex | 定义一个URL路径匹配正则表达式  
  
参数2：HTTP响应源（a.k.a. sourceType）

值 | 含义  
---|---  
data | Imaginary C2 将响应磁盘上文件的内容  
python | Imaginary C2 将运行python脚本。python脚本输出定义HTTP响应。  
  
## 演示用例：模拟TrickBot服务器

虚构C2可用于模拟TrickBot服务器（包括其组件和配置文件）。此外，它还可用于模拟TrickBot的Web注入服务器。

## 它是如何工作的？

执行时，TrickBot
downloader会连接到一组硬编码的IP获取一些配置文件。其中一个配置文件包含了TrickBot插件服务器的位置（IP地址）。TrickBot
downloader会从这些服务器下载插件（模块）并进行解密。然后将解密的模块注入到svchost.exe实例。

![trickbot_webinject_configuration.png](https://image.3001.net/images/20180830/1535588026_5b8736ba3fe4e.png!small)

TrickBot其中有一个injectdll的插件，该插件主要负责TrickBot
webinjects。injectdll插件会定期获取一组更新的webinject配置，并对配置中的各个目标（银行）网站，定义webfake服务器地址。当受害者浏览TrickBot所针对的（银行）网站时，他的浏览器会被神不知鬼不觉地重定向到webfake服务器。而webfake服务器上则会托管该目标站点的克隆版本。攻击者通常会结合社工的手段来欺骗受害者，以达到最终的目的。

## 视频演示

在视频中你可以看到，在svchost.exe中运行的TrickBot downloader，连接到了imaginary C2并下载了两个模块。

显示了在svchost.exe中运行的TrickBot下载器并连接到想象C2以下载两个模块。每个下载的模块都会注入一个新生成的svchost.exe实例。webinject模块试图窃取浏览器中保存的密码，并将窃取的密码泄露给TrickBot服务器。在访问目标银行网站时，TrickBot将浏览器重定向到了webfake服务器。完整视频可以在这里观看。

![20180830081047.png](https://image.3001.net/images/20180830/1535588054_5b8736d670ba5.png!small)![20180830081109.png](https://image.3001.net/images/20180830/1535588055_5b8736d75226b.png!small)

***参考来源：[github](https://github.com/felixweyne/imaginaryC2)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

