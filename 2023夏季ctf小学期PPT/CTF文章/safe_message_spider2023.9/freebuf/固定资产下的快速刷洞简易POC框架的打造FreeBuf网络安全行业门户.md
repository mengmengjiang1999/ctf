**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

当我们拿到大批资产时，总会想着用脚本快速、批量地去检测目标有无漏洞。像awvs、appscan之类的扫描器过于笨重，不能在短时间内测试完目标。而我们的目的，则是打造一个轻便、简易的poc框架。

## 简介

“工欲善其事，必先利其器”这句话一点错也没有。既然我们的目的是轻便，那么python则是我们的不二选择。

github上也有很多前辈造的轮子，像poc-t、pocsuite之类的优秀之作。也没必要自己去辛辛苦苦写一份，毕竟重复造轮子效率低下，自己写的也没有前辈好。

这次，我们选择的项目是https://paper.seebug.org/913/﻿

我们要在此的原基础上进行改造，打造属于自己的专属poc框架

原Airpoc项目链接：https://images.seebug.org/archive/airpoc.zip

## 动手改造

说是改造倒也不算，只是在源代码基础上进行微改

先从主文件下手

![](https://image.3001.net/images/20210327/1616823140_605ec364790ff141bf20a.png!small)

可以看出，在原来的Airpoc中，目标地址是被存储在一个list数组中，但这样对我们来说并不方便。我们要实现的是能测试单/多目标，能从文件中批量读取目标地址，也能直接在命令行里接收单个目标。

新建一个attack函数，再往入口点写

![](https://image.3001.net/images/20210327/1616823492_605ec4c421317b851d19e.png!small)

相信不解释大家也清楚这是什么意思，能简则简

attack函数具体代码

![](https://image.3001.net/images/20210327/1616823594_605ec52a299b0cd74668a.png!small)这样就实现了对单个目标的检测

PS：Content-Type最好设置为application/x-www-form-urlencoded，因为thinkphp类的poc对此有需求，如果没有此类Content-Type，那么poc会失效

main函数中也稍稍修改一下

![](https://image.3001.net/images/20210327/1616823744_605ec5c0b9994e42ff0be.png!small)

主文件修改完了，接下来就考虑poc方面了

### 有关poc

既然是追求刺（qing）激（bian），那就要贯彻到底

从原作者的设计中，可以看出没有考虑过对漏洞结果的储存。本来鄙人是想使用数据库的，但原因大家也知道（其实就是因为懒），写了个超级敷衍人的漏洞存储模块

新建report目录，新建report.py，源码见下

![](https://image.3001.net/images/20210327/1616834812_605ef0fc5689b64f00d1e.png!small)

> import os  
> import time
>
> def save(url,pocname,exp):  
> with open("report/report.html","at") as f:  
> f.writelines("目标:" + "<a href=" + '"' + url.strip() + '">' + url.strip() +
> "</a>" + " " + "POC名称:" + pocname.strip() + " " + "Exp:" + exp.strip() +
> '<br />')  
>
> f.writelines("------------------------------------------------------------------------------------------------------------"
> + '<br />')

每个poc在使用report模块时，要提供三个参数，url，pocname以及exp

结果自动存储在report/report.html文件下

![](https://image.3001.net/images/20210327/1616835030_605ef1d6a48485791c607.png!small)

最终结果图见上

然后是poc的具体编写，也是很简单的，以ueditor指纹的poc为例

![](https://image.3001.net/images/20210327/1616836185_605ef659a5d09469c18af.png!small)

测试

![](https://image.3001.net/images/20210327/1616836248_605ef6984a73dd6bcfa4a.png!small)在页面中发现了ueditor的指纹信息，证实了poc的有效性

![](https://image.3001.net/images/20210327/1616836331_605ef6eb3f180b558801b.png!small)

## 小试牛刀

这里我们以补天公益厂商为例子，进行测试

补天公益列表存放在target目录下的butian.txt文件中

![](https://image.3001.net/images/20210327/1616837150_605efa1e9510a97b96d5b.png!small)![](https://image.3001.net/images/20210327/1616840187_605f05fb7819d0786496f.png!small)结果见上

## 结尾

为了避免大家嫌麻烦，该魔改项目已经上传github

https://github.com/hackerhackrat/R-poc

还有很多很多的玩法，例如连动fofa、zoomeye资产收集引擎，进行批量测试

最主要还是多收集、多写poc

## 参考

> https://paper.seebug.org/913/﻿

