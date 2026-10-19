## **简介**

对，你没有看错，本期我们要研究的目标是哥斯拉。

![image.png](https://image.3001.net/images/20210709/1625812505_60e7ee19253ce63efdfc1.png!small)

不过，此哥斯拉非彼哥斯拉，他是继菜刀、蚁剑、冰蝎之后具有更多优点的Webshell管理工具，由java语言开发，如名称一样，他的“凶猛”之处主要体现在：

  * 全部类型的shell能绕过市面大部分的静态查杀

  * 流量加密能绕过过市面绝大部分的流量Waf

  * Godzilla自带的插件是冰蝎、蚁剑不能比拟的

![image.png](https://image.3001.net/images/20210709/1625812507_60e7ee1bea86235636abe.png!small)

图1 哥斯拉运行界面

（如此简单的操作界面，实际效果和功能可绝不简单。）

它能实现的功能除了传统的命令执行、文件管理、数据库管理之外，根据shell类型的不同还包括了：

  * MSF联动

  * 绕过OpenBasedir

  * ZIP压缩 ZIP解压

  * 代码执行

  * 绕过 DisableFunctions

  * Mimikatz

  * 读取服务器 FileZilla Navicat Sqlyog Winscp XMangager 的配置信息以及密码

  * 虚拟终端 可以用netcat连接

  * Windows权限提升 （2012-2019烂土豆）

  * 读取服务器 谷歌 IE 火狐 浏览器保存的账号密码

  * Windows权限提升烂土豆的C#版本 甜土豆

  * 支持 哥斯拉 冰蝎 菜刀 ReGeorg 的内存shell 并且支持卸载

  * 屏幕截图

  * Servlet管理 Servlet卸载

  * 内存加载Jar 将Jar加载到 SystemClassLoader

![image.png](https://image.3001.net/images/20210709/1625812508_60e7ee1c5d2aae1c4484c.png!small)

图2 功能界面

介绍的也差不多了，我们来分析看看他到底强在哪。

##  **加密模块分析**

  * 分析脚本类型：PHP_XOR_base64

  * 工具版本：3.03

 **1.先进行反编译** ，加密代码的位置位于：”shells” packet->”cryptions” packet->”phpxor”
packet->phpxor class

![image.png](https://image.3001.net/images/20210709/1625812508_60e7ee1cda7bb6232ed9a.png!small)

图3 加密函数位置

从代码中可以分析出，发送的payload内容先经过XOR加密后，再将密文进行base64编码，最后进行URL编码，再发给客户端。

![image.png](https://image.3001.net/images/20210709/1625812509_60e7ee1da810305cfd547.png!small)

图4 加密函数

XOR加密的密钥来自用户提供的密钥经过MD5的32位摘要后，取前16位的值。

![image.png](https://image.3001.net/images/20210709/1625812510_60e7ee1e263c3c3c45e40.png!small)

图5 密钥生成

![image.png](https://image.3001.net/images/20210709/1625812511_60e7ee1f4d5645729a5a3.png!small)

图6 数据主要处理流程

 **2\. 生成shell脚本**

接下来查看手动生成的脚本内容，可以看到shell对数据的处理方式基本和工具源码中的分析一致，变量key的值也确实为进行MD5摘要后的前16位的值。

![image.png](https://image.3001.net/images/20210709/1625812511_60e7ee1f9caaaf577d05e.png!small)

图7 shell脚本内容

![image.png](https://image.3001.net/images/20210709/1625812512_60e7ee20cd50d016aaa79.png!small)

图8 密钥的值为'key'

其中，encode()函数主要是进行XOR操作。

主要的数据处理代码为：

$data=encode(base64_decode($_POST[$pass]),$key)

（代码先记下来，一会可以利用到。）

 **3\. 尝试对数据进行解密**

利用wireshark抓取攻击的流量包。

![image.png](https://image.3001.net/images/20210709/1625812513_60e7ee2140f31a975a89a.png!small)

图9 流量包

抓取数据中等号之后的内容，即被加密编码后的数据内容，然后先将内容进行URL解码。

![image.png](https://image.3001.net/images/20210709/1625812516_60e7ee2441f623dcf8905.png!small)

图10 URL解码

再利用第二点提到的代码，写一个简单的解密脚本，将”$POST”的内容替换为URL解码后的数据。

![image.png](https://image.3001.net/images/20210709/1625812517_60e7ee255c378bc673ecd.png!small)

图11 解密脚本

再执行脚本，瞬间感觉豁然开朗了有没有，明文出现，说明分析的思路是正确的。简单分析了一下payload的内容，包含run、bypass_open_basedir、formatParameter、evalFunc等二十多个功能函数，具备代码执行、文件操作、数据库操作等诸多功能。

![image.png](https://image.3001.net/images/20210709/1625812518_60e7ee26442549ddebfc2.png!small)

图12 payload明文

##  **总结**

不得不佩服开发哥斯拉作者的思路很有创造性，虽然其实现的原理并不是很难，但却有效地避开了同类工具在网络流量中出现的常见特征，加上工具配置了自定义http_header,使得一些利用UA等其他http_header数据的检测效果也大打折扣。

