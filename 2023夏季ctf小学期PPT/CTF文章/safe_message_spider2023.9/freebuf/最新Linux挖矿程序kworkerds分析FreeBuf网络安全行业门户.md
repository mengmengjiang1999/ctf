## 0×00 背景概述

 **近日，同伴的一台Linux服务器中了kworkerds挖矿程序，随即对挖矿程序进行了处理与分析。**

##  0×01服务器现状

进入服务器之后通过top命令，没有发现有占用CPU资源过高的进程，随后使用busybox
top命令查看发现一个kworkerds的程序占用CPU资源达到了99%，计划任务中被写入恶意下载命令；

系统top命令界面；

![最新Linux挖矿程序kworkerds分析](https://image.3001.net/images/20190418/1555589890_5cb86b0244ebd.png!small)

使用busybox top命令界面；

![busybox.png](https://image.3001.net/images/20190418/1555589938_5cb86b3262f24.png!small)

写入的计划任务；

![计划任务.png](https://image.3001.net/images/20190418/1555589965_5cb86b4d60ddb.png!small)

## 0×02脚本分析：

###  **1)** **mr.sh脚本：**

清理文件或其他挖矿程序；

![mr1.png](https://image.3001.net/images/20190418/1555590007_5cb86b7733899.png!small)

值得一提的是，脚本首部已经把防火墙关闭了，为什么又要在防火墙中加入规则，禁止了一个IP地址，并通过string匹配域名来过滤了pastebin，这个很像是在防近期爆发的
khugepageds、watchdogs…

往下是一顿清理-----
![mr2.png](https://image.3001.net/images/20190418/1555590031_5cb86b8f9313d.png!small)

再经过一番清理之后，开始把下载脚本的命令写入计划任务中；

![mr3.png](https://image.3001.net/images/20190418/1555590056_5cb86ba843bda.png!small)

写入的文件列表如下；

![mr4.png](https://image.3001.net/images/20190418/1555590078_5cb86bbe0fb9d.png!small)

随后又开始了一番清理，把除自己之外的进程且占用CPU资源大于30%的给杀掉，并且查看netstat中是否与自己的服务器建立连接成功；

![mr5.png](https://image.3001.net/images/20190418/1555590106_5cb86bdaad9f8.png!small)

在脚本的最后开始下载一个名为2mr.sh的云端脚本，并且检查计划任务中是否有自己写入的下载命令，如果没有继续写入；

![mr6.png](https://image.3001.net/images/20190418/1555590128_5cb86bf0cdf72.png!small)

###  **2)** **2mr.sh脚本：**

2mr脚本是关于挖矿程序的下载与调整，在脚本的首部判断下载的/var/tmp/sustse文件是否存在，如果存在则通过MD5值对比/var/tmp/sustse是否相符，如果不相符则删除并且杀掉自己的相关进程，否则创建/var/tmp；

![2mr1.png](https://image.3001.net/images/20190418/1555590151_5cb86c0717d2b.png!small)

随后通过downloadIfNeed()、download()、download2()三个函数进行判断/下载挖矿相关文件，这里下载了一个名为1.so的文件，并且把1.so替换掉/usr/local/lib/libkk.so，把路径写入/etc/ld.so.preload，最后把/var/tmp/sustse复制一份并命名为kworkerds；

![2mr2.png](https://image.3001.net/images/20190418/1555590188_5cb86c2cdd8ba.png!small)

![2mr3.png](https://image.3001.net/images/20190418/1555590227_5cb86c53c2b63.png!small)![2mr4.png](https://image.3001.net/images/20190418/1555590239_5cb86c5f1f91f.png!small)

最后通过judge()、judge2()函数根据网络连接情况进行判断被攻陷的主机是否与矿池建立连接成功，如果没有则清理占用资源大于30%的其他程序，随后下载相关挖矿程序进行挖矿操作；

![2mr5.png](https://image.3001.net/images/20190418/1555590261_5cb86c75a017f.png!small)

## 0×03处理建议：

> 1) 清除相关的恶意计划任务；
>
> 2) 删除/var/tmp目录下的相关恶意文件；
>
> 3) 删除被替换的动态链接库；

 **相关信息：**

 **矿池信息：**

![pools.jpg](https://image.3001.net/images/20190419/1555652188_5cb95e5c651f3.jpg!small)

 **URL:**

> <http://107.174.47.156/mr.sh>
>
> <http://107.174.47.156/wc.conf>
>
> <http://107.174.47.156/xmrig>
>
> <http://107.174.47.156/11>

 **MD5:**

> be9469ea238d53993f70ed09b8347f3e kworkerds
>
> b4f6d69c8777fea8b169898bea9fb040 sustse
>
> 2fdb64bf08f09ce0cdc650b443590d7b 1.so libkk.so
>
> 83d502512326554037516626dd8ef972 /root/kworkerdss/xmrig

 ** _PS：1.so~~~_**

 **
_![最新Linux挖矿程序kworkerds分析](https://image.3001.net/images/20190418/1555590823_5cb86ea75bc14.jpg!small)_**

 ***本文作者：runmoke，本文属FreeBuf原创奖励计划，未经许可禁止转载。**

