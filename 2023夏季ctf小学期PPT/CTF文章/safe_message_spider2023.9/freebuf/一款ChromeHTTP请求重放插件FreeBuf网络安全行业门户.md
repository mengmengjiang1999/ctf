## 工具介绍

 **一款用于chrome下的HTTP包重放工具HTTP请求记录又2种模式，一种为记录全部标签页的请求，另一种为记录当前devtool所在标签页的请求。**

## 使用流程

> F12打开后，选到pttools标签。
>
> 选择监听方式。
>
> 选择view即可修改HTTP请求。对于POST的HTTP请求，可以添加body的参数。

使用截图：

![](https://image.3001.net/images/20190612/1560306647_5d0063d7051be.png!small)

![](https://image.3001.net/images/20190612/1560327099_5d00b3bb2898d.png!small)

![](https://image.3001.net/images/20190612/1560327317_5d00b495b83d6.png!small)

### 注意事项

在进行POST的时候，将以application/x-www-form-urlencoded的类型添加参数。

如无特殊需求，请自行删除content-length的内容。

重放某些攻击不生效可能原因是请求了缓存，通常对于图片会发生这种情况。可以勾选Network选项卡种的Disable cache。

## 运行流程

![](https://image.3001.net/images/20190612/1560306295_5d00627758a3b.png!small)

对于重放的一套流程，借鉴了HACKBAR的方法。同时发现了HACKBAR的一个bug。HACKBAR的编辑cookie是失效的，因为要onBeforeSendHeaders的监听处少给了一个参数。

![](https://image.3001.net/images/20190612/1560307222_5d0066160e4b2.png!small)

## TO-DO

完善未知bug。[优先]

添加更多的POST的请求type。

修改HTTP请求后，无法保留原始请求。(对vue不熟悉,还没有找到解决办法)

current tab增加response预览功能。

等我学会前端，我就把它做的更酷炫。

## 传送门

插件：<https://github.com/17307/ptTools>

插件具体实现细节：<https://blog.o1hy.com/2019/06/15/ptToolsChromeExtension/>

目前写的第三个插件，而且是个业余爱好者，如有意见或建议，欢迎提出。

 ***本文作者：howintre，转载请注明来自FreeBuf.COM**

