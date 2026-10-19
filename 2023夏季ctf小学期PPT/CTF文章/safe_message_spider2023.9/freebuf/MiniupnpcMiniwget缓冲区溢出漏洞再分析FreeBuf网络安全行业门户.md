***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文作者：j0hnShi，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 0x00 引言

 **由于最近在挖掘一款程序漏洞, 看到此程序调用了 miniupnpc.dll 1.6.xxx 所以下载了个相应版本的miniupnpc 进行了代码审计,
发现存在几处安全漏洞, 查找相关漏洞库, 发现这是已存在并且已在高版本中修复的安全问题, 本篇我们重点分析如何发现和如何验证的一些方法。**

## 0x01 如何发现

在源码审计的过程中，使用关键字查找、输入流跟踪等方式进行初步的审计，当到Miniwget.c 的时候, 发现了此安全问题。

漏洞存在位置: miniwget.cgetHTTPResponse函数memcpy(content_buf + content_buf_used, buf
+ i, bytestocopy);中。

其中 bytestocopy是可以控制的, 而这次的安全问题也是出现在这, bytestocopy < 0 则会产生漏洞。我们县验证下是否会产出fault。

![](https://image.3001.net/images/20190411/1554946004_5cae97d47325e.png!small)

我们把bytestocopy 直接赋值 0x8000000。

运行结果：

![](https://image.3001.net/images/20190411/1554946012_5cae97dc43ef1.png!small)

发生 segmentation fault 。

我们来看下bytestocopy的整个数据流：

    
    
    unsigned int bytestocopy = 0;
    
    ...
    
    bytestocopy = ((int)chunksize < n - i)?chunksize:(n - i);
    
    memcpy(content_buf + content_buf_used, buf + i, bytestocopy);

然而bytestocopy 是 chunksize, 我们看下chunksize的数据流：

    
    
    unsigned int chunksize = 0;
    
    ...
    
    for(j = 0; j < chunksize_buf_index; j++) {
    
    if(chunksize_buf[j] >= '0' && chunksize_buf[j] <= '9')
    
    chunksize = (chunksize << 4) + (chunksize_buf[j] - '0');
    
    else
    
    chunksize = (chunksize << 4) + ((chunksize_buf[j] | 32) - 'a' + 10);
    
    }
    
    ...

从中我们可以看出 chunksize 会通过一些运算来最终得到 chunksize, 而且运算也比较容易得出。

## 0x02 漏洞调试和验证

至此, 我们已经找到那个问题点, 然后这个点也是可以控制的, 那我们如何构造这个数据让原始程序可以走到并且产生问题呢?

从源码中也可以看到chunksize 是从Body中获取的：

![](https://image.3001.net/images/20190411/1554946024_5cae97e8b21d2.png!small)

![](https://image.3001.net/images/20190411/1554946037_5cae97f588d33.png!small)

通过阅读他的源代码, 发现他解析的是http 的 response 响应体, 并且需要有几个必须的字段：

    
    
    Content-Type: text/html
    
    Transfer-Encoding: chunked
    
    Content-Length: 1

然后是Body数据, 而我们需要控制的是 Body中的数据。

那我们如何来构造数据呢？

构造如下response 响应体：

    
    
    HTTP/1.1 200 OK
    
    Transfer-Encoding: chunked
    
    Content-Length: 1
    
    Content-Type: text/html
    
    f
    
    <xml>test</xml>
    
    80000000
    
    Test

即可出发漏洞, 为了验证漏洞, 我吧getHTTPResponse函数进行了单独编译, 并制作成socket服务方便调试。

![](https://image.3001.net/images/20190411/1554946051_5cae980312593.png!small)

编译运行此文件：

![](https://image.3001.net/images/20190411/1554946058_5cae980a79221.png!small)

使用python 编写一个POC：

![](https://image.3001.net/images/20190411/1554946064_5cae9810e725a.png!small)

运行此POC：

![](https://image.3001.net/images/20190411/1554946071_5cae98177fcaf.png!small)

同样出现了 segmentation fault。

## 0x03 结语

最后查询了一些相关文档，发现此漏洞早已存在，并且新版本已经修复，但由于很多应用会使用低版本的miniupnpc,
同样会出现这个漏洞。漏洞的具体利用就不在阐述, 可以查看CVE-2017-8798。

所编写的代码:

> 链接：<https://pan.baidu.com/s/1PcT09Td3BB14rLbHBVb98A> 提取码：q69e

 ***本文作者：j0hnShi，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

