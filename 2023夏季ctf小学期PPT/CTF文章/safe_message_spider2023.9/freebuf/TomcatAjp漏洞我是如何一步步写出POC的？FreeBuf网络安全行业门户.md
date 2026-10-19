## 前言

 **晚上，朋友圈有人发了篇tomcat-ajp漏洞的通告和一个简要分析的文章，也是当时唯一的参考文章，本着“好好学习、天天向上”的态度，作为小白，就想试着分析下，看看能不能写出poc。所以本文主要讲述一个小白（当然也不能太白，java至少要会吧，网站要知道是啥吧）如何一步步调试分析，编写poc的过程。**

## 一、漏洞介绍

简单来说就是apache tomcat服务器的8009端口上的ajp协议存在漏洞，导致未授权用户可以读网站目录下的任意文件。

漏洞编号：

> CNVD-2020-10487/CVE-2020-1938

受影响版本：

> ApacheTomcat 9.x < 9.0.31
>
> ApacheTomcat 8.x < 8.5.51
>
> ApacheTomcat 7.x < 7.0.100
>
> ApacheTomcat 6.x

## 二、调试环境搭建

为了观察数据流向、编写poc，我们需要搭建调试环境。

tomcat是开源项目，所以我首先想的是下载源码，在源码基础上调试，这里我下载的版本是9.0.2的代码。调试器选择的是Idea。

我先在网上搜索了下idea 调试 tomcat源码的文章。最后参考了

> <https://blog.csdn.net/weixin_30631587/article/details/96528373>

这篇文章，将pom.xml中tomcat的版本由9.0.14修改成9.0.2。，不过这里我觉得不改也不会影响结果。成功运行tomcat服务。

![](https://image.3001.net/images/20200224/1582535781_5e539465196cf.png!small)

## 三、ajp协议学习

到目前为止，我还不知道什么是ajp协议，这个协议是干啥的，但是既然知道此次tomcat漏洞是ajp协议造成的。我们肯定要去了解下这个协议是什么。

Apache官方有说明文档

> <http://tomcat.apache.org/connectors-doc-archive/jk2/common/AJPv13.html>

当然这个文档一眼看上去，是不太容易理解的，于是百度一番

![](https://image.3001.net/images/20200224/1582535801_5e5394794379f.png!small)

我理解的是，我们要访问tomcat网站有两种方式，一种是通过浏览器直接输入url地址。

另外一种就是通过ajp协议访问。

AJP协议是定向包（面向包）协议，采用二进制形式代替文本形式，以提高性能。

所以我们需要写个ajp的客户端程序用来与tomcat服务器的8009端口进行数据交互。当然我们可以自己从头写一个ajp客户端，前提是我们需要很详细了解ajp协议及其各个字段含义。我并不打算如此，毕竟自己从头写起来还是很费劲的。我先到github上用关键词ajp和ajp
client搜了一下，看来白的人运气不会太差，发现已经有别人的ajp-client项目。

![](https://image.3001.net/images/20200224/1582535822_5e53948e06819.png!small)

我把三个ajp-client都下了下来，经过测试和对比(边调试边测试)，最后使用了

> <https://github.com/espenhw/ajp-client>

这个项目，最后poc也是在这个项目上完成的。

这里我们需要说下ajp协议中比较重要的字段。

![](https://image.3001.net/images/20200224/1582535841_5e5394a1bd6ef.png!small)

Forward Request包就是我们要发送给tomcat
8009端口的内容，用来触发漏洞的。该字段中比较重要的字段是attributes，后面调试跟踪的时候，也会发现的，后面再说。

## 四、调试跟踪

通过参考我们知道，tomcat在接收ajp请求的时候调用org.apache.coyote.ajp.AjpProcessor来处理ajp消息，prepareRequest将ajp里面的内容取出来设置成request对象的Attribute属性。

我们现在AjpProcessor中定位到prepareRequest()函数，并在函数开始出下上断点，在request.setAttribute(n, v
)也下上断点。

![](https://image.3001.net/images/20200224/1582535858_5e5394b28a5c0.png!small)

编写测试代码如下（test_servlet是我自己编写的servlet代码，放在了webapps目录下）：

![](https://image.3001.net/images/20200224/1582535880_5e5394c80415a.png!small)

运行程序，程序成功断在了prepareRequest()，继续向下单步执行，期间可以观察一些字段的变化。但是程序并没有进入while循环，自然也不会执行request.setAttribute(n,
v
)函数。（此时我对attributes还不懂，不知道这个字段的意义），再次跟踪时发现while循环的判断条件中在获取attitudes的值时，返回值为-1。然后又回头重新看了下前一节所说的Forward
Request结构，看到了其中的attitudes字段，心想这个字段也许和代码中while循环判断的attitudecode有关。

然后看了看ajp-client中代码对attitudes字段的处理，发现该项目没有处理attitudes字段。就按照自己的理解在AjpClient.java中添加了attitudes处理相关代码。

    
    
    public List<Pair<String,String>> headers = new LinkedList<Pair<String,String>>(); 
    
    public List<Pair<String,String>> attributes = new LinkedList<Pair<String, String>>();

添加函数setHeaders()此函数并不重要，添加函数addAttributes()。

![](https://image.3001.net/images/20200224/1582535911_5e5394e7a11dc.png!small)

在query函数中添加，处理atrribute代码

![](https://image.3001.net/images/20200224/1582535935_5e5394ff2ba31.png!small)

修改测试代码如下

![](https://image.3001.net/images/20200224/1582535959_5e5395177b4c1.png!small)

(test_servlet/xx是一个不存在的地址或映射，只有设置成不存在的地址，代码流程才会进入DefaultServlet)

运行程序，程序成功进入while循环

![](https://image.3001.net/images/20200224/1582535973_5e539525c3f06.png!small)

至于addAttributes参数为什么这样写，我已开始自然也是不知道的，多跟踪调试几次就知道了。

程序执行了request.setAttribute(n, v )函数，接下来就是DefaultServlet的serveResource函数。

![](https://image.3001.net/images/20200224/1582535987_5e53953302fdf.png!small)

跟踪到getRelativePath函数中，

![](https://image.3001.net/images/20200224/1582536024_5e5395588dc59.png!small)

这里就会获取我们设置的attributes值。然后通过resources.getResource(path);判断设置的路径文件是否存在，如果存在则返回文件内容，不存在则报错。

已经成功读到文件。

![](https://image.3001.net/images/20200224/1582536039_5e539567220e4.png!small)

关于org.apache.jasper.servlet.JspServlet类实现文件包含，这里就不分析了，有兴趣的如法炮制即可。

## 五、编写poc

如何编写poc就不在讲了，上面的测试代码稍微修改，就是poc了。

## 六、总结

总的来说，该漏洞的利用并不是很难，即使你不懂ajp协议，有些参考，稍微花点时间，还是能够独立写出poc的，当然我实际调试的时候也没有文章中那么顺的，要有耐心，多调试几次就好。修复的话，如果不需要ajp的，可以把配置文件中的8009配置关闭，或者更新到最新版本。

## 参考：

> <https://blog.csdn.net/u012206617/article/details/104416626/>
>
> <https://blog.csdn.net/kalman2008/article/details/24487703>
>
> <https://blog.csdn.net/jeikerxiao/article/details/82745516>
>
> <http://tomcat.apache.org/connectors-doc-archive/jk2/common/AJPv13.html>

***本文原创作者：MrCoding，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

