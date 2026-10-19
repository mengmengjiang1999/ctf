## 一、概述

 **最近，深信服安全团队捕获到SystemdMiner挖矿木马最新变种，该家族在2019年被首次发现，起初因其组件都以systemd-<XXX>命名而得名，但慢慢的，它们开始弃用systemd的命名形式，改为了随机名。**

深信服安全团队通过C&C域名、脚本、定时任务等特征确认该病毒为SystemdMiner最新变种，本次变种的不同点在于更新了C&C域名及连接C&C域名的方式，使用socket5代理的方式访问C&C域名，从而实现绕过安全网关的目的，其余的特征与过往版本类似。

## 二、主机排查

失陷主机卡顿严重，使用top命令定位到挖矿进程为XBpdur，CPU占用率达到597%。

![](https://image.3001.net/images/20200409/1586422916_5e8ee484ce128.jpg!small)

当查看其进程信息时，发现进程对应的文件及符号链接未找到，说明病毒极大可能运行后进行了自删除并删除符号链接。

![](https://image.3001.net/images/20200409/1586422956_5e8ee4acc6883.png!small)

使用netstat命令发现XBpdur进程有两条可疑网络连接，通过威胁情报关联，确认该病毒为SystemdMiner。

![](https://image.3001.net/images/20200409/1586423000_5e8ee4d87b41f.png!small)

主机上也存在SystemdMiner特有的定时任务，定时调用一个随机名sh脚本，该sh脚本是由一串base64加密的字符串组成的。

![](https://image.3001.net/images/20200409/1586423014_5e8ee4e670ad8.png!small)

## 三、样本分析

解密后的脚本代码如下，与之前变种不同的是，本次的C&C域名由tencentxjy5kpccv.*更换为了trumpzwlvlyrvlss.*，且使用了socket5的方式用relay.tor2socks.in代理访问C&C域名，relay.tor2socks.in是一个类似中转网站的域名，这样，C&C域名trumpzwlvlyrvlss.onion就不会直接出现在数据包头。

![](https://image.3001.net/images/20200409/1586423046_5e8ee506a86bb.png!small)

模拟执行脚本中的下载命令，得到病毒文件母体，是一个64位的ELF文件。

![](https://image.3001.net/images/20200409/1586423062_5e8ee516da0a3.png!small)

当使用IDA进行反汇编时，函数列表与导入表都几乎没有显示，极大可能是经过加密了。

![](https://image.3001.net/images/20200409/1586423079_5e8ee5279cc9a.png!small)

由于是黑客自定义的加密算法，只好单步调试，一路单步后，IDA提示在数据段发现了代码结构，此处的代码即为解密出来的核心恶意代码。

![](https://image.3001.net/images/20200409/1586423101_5e8ee53d24da9.png!small)

核心恶意代码在0x400339处，使用IDA的内存快照功能保存下来，这样就可以断开调试本地分析了。

![](https://image.3001.net/images/20200409/1586423135_5e8ee55fbbfe9.png!small)

保存好快照后，查看字符串窗口，样本的敏感字符串都显示出来了，跟过往的变种一样，样本内嵌了base64脚本，在运行时释放。

![](https://image.3001.net/images/20200409/1586423153_5e8ee57111a68.png!small)

第1个脚本的主要功能是卸载安骑士、云镜等安防产品，以及清除其他家族的挖矿病毒进程。

![](https://image.3001.net/images/20200409/1586423168_5e8ee580cd21a.png!small)

第2个脚本用于下载挖矿程序cpu，下载方式及域名跟上述的一样。

![](https://image.3001.net/images/20200409/1586423183_5e8ee58f7286a.png!small)

cpu也是经过加密的，解密方式与病毒母体的类似，解密出来后的样本是XMRig挖矿程序。

![](https://image.3001.net/images/20200409/1586423197_5e8ee59d31705.png!small)

其他两个脚本用于下载cmd和bot模块，目前下载连接已失效，bot大概率是该病毒的传播模块。

![](https://image.3001.net/images/20200409/1586423210_5e8ee5aa48e8b.png!small)

## 四、解决方案

> 1、修改ssh弱密码，防止被爆破。
>
> 2、对重要的数据文件定期进行非本地备份。
>
> 3、建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。

## 五、IOC

> 57374AF602FE4D852AB38EB68F641FB0-- x86_64
>
> 31DF932A2963F830ACB39B28D60B5E96-- cpu
>
> trumpzwlvlyrvlss.onion -- C&C域名
>
> trumpzwlvlyrvlss.tor2web.in -- C&C域名
>
> trumpzwlvlyrvlss.tor2web.io -- C&C域名
>
> trumpzwlvlyrvlss.tor2web.to -- C&C域名
>
> trumpzwlvlyrvlss.tor2web.su -- C&C域名
>
> 222.35.250.117-- 矿池地址

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

