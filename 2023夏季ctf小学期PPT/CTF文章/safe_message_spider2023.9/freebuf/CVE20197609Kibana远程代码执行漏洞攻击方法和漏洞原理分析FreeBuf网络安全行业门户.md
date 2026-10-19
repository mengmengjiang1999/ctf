***郑重声明：本文展示的攻击过程是在模拟环境中进行的。文中涉及的漏洞原理和攻击方法，只为交流学习之用。如有人用于非法用途，产生的后果笔者不负任何责任。**  

##  **0x00** **前言**

**本漏洞的exp放出来快一星期了，目前网上的分析文章也出了几篇，但是大都集中于通过容器简单复现攻击过程，没有深入的分析产生原因和exp的构造原理。笔者借鉴了大牛Michał
Bentkowski，也就是漏洞发现者的博客上的英文ppt（参考链接3），写了这篇文章。本文详细介绍了在本地搭建了模拟攻击环境的过程（非docker搭建），并完整分析了这个漏洞的攻击原理。现在分享给大家。**

##  **0x01** **漏洞简介**

Kibana存在远程代码执行漏洞，影响版本为5.6.15和6.6.0之前的所有版本。拥有Kibana的Timelion模块访问权限的人可以以Kibana的运行权限执行任意代码，包括反弹shell。

##  **0x02** **环境搭建**

靶机环境：

> Parrot Security OS 4.7 64位 或其他类Linux操作系统（VMWare 14）
>
> Elasticsearch6.5.4
>
> Kibana 6.5.4
>
> IP：10.10.10.128

攻击机环境：

> Windows 10 Home 64位
>
> Netcat 1.12 64位
>
> Chrome浏览器
>
> IP：172.16.2.62

##  **0x03** **漏洞利用**

1）在靶机上部署Kibana 和Elasticsearch，并 **开放访问端口**
(./config/kibana.xml中的server.host改成0.0.0.0)让攻击机可以访问（如图1所示）。

![](https://image.3001.net/images/20191023/1571840225_5db060e1d15c0.png)

图1 在靶机上部署Elasticsearch和Kibana

2）确认执行权限并启动Elasticsearch和Kibana（如图2，3所示）

![](https://image.3001.net/images/20191023/1571840619_5db0626bf1a82.png)

图2 在靶机上确认Kibana执行权限

![](https://image.3001.net/images/20191023/1571842272_5db068e048222.png!small)![](https://image.3001.net/images/20191023/1571842294_5db068f6ce99d.png!small)

图3 执行 Elasticsearch和Kibana

在攻击机上启动netcat（图4），并通过Chrome浏览器访问Kibana的Timelion页面，并输入payload（图5）。

![](https://image.3001.net/images/20191023/1571842755_5db06ac308ef8.png!small)

图4 在攻击机上启动netcat

![](https://image.3001.net/images/20191023/1571842779_5db06adba1945.png)

图5 登录Timelion并在输入框中输入payload

payload如图6所示（为了避免各类纠纷，本文的攻击代码只放图片版，文字版可以去参考链接里面自取）![](https://image.3001.net/images/20191023/1571840374_5db0617643476.png)

(注意替换payload中的反弹IP为攻击机IP)

点击右边的执行按钮执行，然后点击控制面板左边的Canvas,可以获取反弹shell

![](https://image.3001.net/images/20191023/1571840730_5db062da0d0ad.png)

图6 获得反弹shell

多次操作之后可能会出现反弹不成功的现象，此时可以删除kibana目录并重新部署一次， **记得修改kibana.xml** ！

##  **0x04** **漏洞机理**

“原型污染”是一种针对JS语言开发的攻击方法。JS语言中，每一个对象都是有其原型（__proto__）的，而该原型又有其自己的原型对象，直到某个对象的原型为null。而如果JS对其中定义的对象原型的属性读写缺乏控制，容易让攻击者操纵一些敏感特征，从而实现攻击者的目的。

本漏洞就是是一个由于JS语言的“原型污染”，导致靶机环境量被污染，最终获得shell执行的漏洞。具体调试过程如下

###  1、POC验证

1） 在Timelion的输入框中输入本漏洞的POC：

![](https://image.3001.net/images/20191023/1571841674_5db0668af36ba.png)

2） 点击canvas，可以发现cookie被污染，页面无法访问。

![](https://image.3001.net/images/20191023/1571841734_5db066c634fb8.png)

3)通过node调试工具(具体使用方法见参考链接)连接后台，删除Object.prototype的cookie值，刷新发现页面暂时恢复正常。因此可以判定该处存在JS原型污染漏洞

###
![](https://image.3001.net/images/20191023/1571843206_5db06c864f3c9.png)2、漏洞产生原理和攻击思路

1）点击canvas页面，可以发现后台大量报错，报错原因是9229端口被占用。因此可以判断：在点击canvas页面的过程中，kibana创建了新的node进程。（
**注意此时要连接chrome的node调试工具才会看到报错** ）因此可以考虑通过劫持环境变量来实现shell命令注入。

![](https://image.3001.net/images/20191023/1571843279_5db06ccf94674.png)

2)
在创建新的node进程过程中，必然使用了NODE_OPTIONS环境变量，如果我们可以劫持该变量，那么就能影响node的新进程创建。NODE_OPTIONS不限制
--require选项，该选项可以在执行js文件之前首先加载其他js模块。而在本案例中，实现上传恶意模块的思路难以实现。因此考虑进一步污染环境变量的方法来间接达到这一目的。

###  3、payload构建

在构建payload之前，我们通过调试工具查看Object.protoytpe.env变量。

![](https://image.3001.net/images/20191023/1571844098_5db07002560ac.png)

Timelion中，props方法的官方解释是：
![](https://image.3001.net/images/20191023/1571840809_5db06329c48ba.png)

简单来说,props可以修改任意对象的属性值。

因此可以采用props方法来对JS中object对象的原型进行修改，同时也就修改了靶机的环境变量。据此，我们构建出了如下的代码：

![](https://image.3001.net/images/20191023/1571843500_5db06dac0ff08.png)

其中,label.__proto__.env是靶机的环境变量，我们在该变量中添加了一个键值对

![](https://image.3001.net/images/20191023/1571842064_5db06810a6b3d.png)

最后两个斜杠用于把后面的内容注释掉。因此我们目前的payload是

![](https://image.3001.net/images/20191023/1571845350_5db074e6707ce.png)

点击执行之后，继续在调试工具中查看Object.protoytpe.env变量的污染情况:

![](https://image.3001.net/images/20191023/1571844199_5db070679d4b1.png)可以看到env已经被污染

下一步就是污染NODES_OPTIONS变量，让node命令在运行时执行我们上面构建的反弹shell的命令。

首先考虑使用eval函数，而node的开发者显然意识到了这是个很危险的设计，因此在NODE_OPTIONS变量中禁用了eval函数，然而却没有禁用—require这个选项。因此我们构建这一部分的代码：

![](https://image.3001.net/images/20191023/1571844404_5db07134a109f.png)

最终，我们构建的payload成了如下结构：

![](https://image.3001.net/images/20191023/1571844458_5db0716a67c7f.png)

点击执行之后再次查看env的污染情况

![](https://image.3001.net/images/20191023/1571844323_5db070e381e37.png)

总体来看，我们首先把环境变量修改成了一条js语句，然后又在node执行过程中劫持了执行参数NODE_OPTIONS，这样构成了完整的攻击链。当然还有
**最后一步点击canvas页面** ，让node建立新进程的过程执行起来。从而达到反弹shell的目的。

##  **0x05** **危害分析和处理建议**

危害分析：

> CNVD评级：高(A*V:N/AC:L/Au:N/C:C/I:C/A:C)
>
> CNNVD评级：超危

虽然该漏洞是一个远程命令执行漏洞，但是本人认为该漏洞影响不大。

因为本漏洞是执行在Kibana的宿主机上，而Kibana是一个Elasticsearch的可视化工具，该工具很少有人会把其页面暴露于公网。

能够造成威胁的只有一种情况，就是页面被暴露于公网，而且使用了弱用户名和弱口令。

故本人认为该漏洞威胁不大。

处理建议：

> 1）及时升级Kibana和Elasticsearch到最新版本，同时尽量用低权限执行Kibana和Elasticsearch。
>
> 2）尽量不要让Kibana的Timelion页面暴露于公网，并检查是否存在使用弱口令登录的情况。

##  **0x06** **参考资料**

> 1) <https://nodejs.org/en/docs/inspector>
>
> 2) <https://github.com/mpgn/CVE-2019-7609>
>
> 3) <https://slides.com/securitymb/prototype-pollution-in-kibana/#/>
>
> 4) CNVD 国家信息安全安全漏洞共享平台 <https://www.cnvd.org.cn/flaw/show/CNVD-2019-12163>
>
> 5) CNNVD 国家信息安全漏洞库
> <http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201902-1035>

***本文原创作者： wangtua，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
  

