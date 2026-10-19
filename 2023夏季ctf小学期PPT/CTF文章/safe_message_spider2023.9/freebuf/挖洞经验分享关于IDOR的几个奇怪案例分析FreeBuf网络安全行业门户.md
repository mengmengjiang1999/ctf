![](https://image.3001.net/images/20200302/1583148732_5e5ceebc01e06.png!small)

**果阿这个地方一直是冒险者的天堂，就在前不久，我们几个朋友计划去果阿旅行，于是乎我们便在Skyscanner上搜索廉价机票，然后找到了一个名为“whereIDORsLive.com”的网站。这个网站的优惠幅度非常大，它是一个大型旅游门户网站。在这篇文章中，我将跟大家分享几个我从中发现的IDOR（不安全的直接对象引用）漏洞。**

##  第一个IDOR：下载任意用户的机票

当我在该网站的交易确认页面中继续完成机票订购时，我发现了一个选项，即将机票订单的PDF版通过短信、右键和直接下载的方式提供给用户。

![](https://image.3001.net/images/20200302/1583148744_5e5ceec8c0000.png!small)

于是，我直接下载了机票的PDF文件。PDF文件名是一个加密字符串，我一开始以为它使用的是Base64编码，但解码之后却生成了一堆乱七八糟的东西。这种情况很常见，即字符串经过加密之后再次被编码为Base64格式，这样它们就可以转换为可打印的字符，以便在应用程序之间进行平滑传输和呈现。

![](https://image.3001.net/images/20200302/1583148751_5e5ceecfa6f39.png!small)

![](https://image.3001.net/images/20200302/1583148757_5e5ceed5b5c97.jpg!small)

每当我在网站中看到有数据被加密时，我都忍不住想要去研究一下，因为根据我的经验，大多数网站在使用加密算法时都存在错误实现或者错误的“自定义”实现。

我之所以觉得这个网站有问题，是因为他们没有为他们的API使用SSL证书，并且对PDF文件名进行了加密操作，这里一定有问题。于是乎，我右键点击了网页上的“下载PDF”按钮，然后审查元素。

![](https://image.3001.net/images/20200302/1583148764_5e5ceedc067f8.png!small)

我们发现，代码使用我的“订单ID”作为参数调用了downloadPdf函数。那么我所做的第一件事，就是将我的订单ID+1，比如说“66786694”，然后再次调用该函数。但此时打开的仍然是我这一份订单PDF，无论你提供给downloadPdf函数的订单ID值是多少，它都只会返回当前机票订单的PDF。接下来，我开始分析downloadPdf函数。

![](https://image.3001.net/images/20200302/1583148787_5e5ceef3353a0.gif!small)

函数代码很简单，它接收一个订单ID号作为参数“tid”（这里就是“66786693”），但是却没有将其重新分配给加密字符串“hdnBookingId”。因此，当你单击它时，将会在一个新的选项卡中打开你的PDF：

    
    
    http://api.whereIDORsLive.com/XYZService/EticketPdf/hdnBookingId.pdf

###
downloadPdf.js【[源代码](https://gist.github.com/LuD1161/eb41453e6d85f19c4d681bfadec69c38/raw/43ee2df41e54a276625491838e72caf450f0d3c0/downloadPdf.js)】

    
    
    function downloadPdf(tid) {
    
            if (document.getElementById("hdnBookingId") != null && document.getElementById("hdnBookingId").value != "")
    
                tid = document.getElementById("hdnBookingId").value;
    
            if (tid != null && tid != "" && tid != undefined)
    
                window.open("[http://api.whereIDORsLive.com/XYZService/EticketPdf/](http://api.whereidorslive.com/XYZService/EticketPdf/)" + tid + ".pdf", '_blank');
    
        }

这就很奇怪了，为什么会有人这么做？为什么不直接调用downloadPdf函数？为什么不用它来传递订单编号？我的第一反应，就是遗留代码，此前可能是这个函数直接将“订单ID”转换为URL。因此，我猜测之前的链接形式可能为：

    
    
    http://api.whereIDORsLive.com/XYZService/EticketPdf/bookingId.pdf

为了查看后端是否仍然有效，我访问了下面这个链接：

    
    
    http://api.whereIDORsLive.com/XYZService/EticketPdf/66786693.pdf

没错，这条链接给我们返回了PDF，通过枚举订单ID，我还能够获取到其他人的机票订单。

![](https://image.3001.net/images/20200302/1583148825_5e5cef19121f6.png!small)

![](https://image.3001.net/images/20200302/1583148829_5e5cef1dcf290.png!small)

![](https://image.3001.net/images/20200302/1583148833_5e5cef21bc7a4.jpg!small)

###  漏洞成因

很可能是因为，后端文件仍然是以“bookingId.pdf”的形式存储的，并且有一个中间件来负责将hdnBookingId解密为bookingId，或者说同时存储了一个订单的两种文件名称/格式，即同时存在“hdnBookingId.pdf”和“bookingId.pdf”。

##  第二个IDOR：同一家公司的另一个终端节点

接下来，我对该公司旗下的Android应用程序进行了分析，并且发现流量会被路由至一个终端节点处：

    
    
    http://cloud.whereIDORsLive.in/XYZService/dboperation.svc

![](https://image.3001.net/images/20200302/1583148864_5e5cef40ac5ae.png!small)

这对于黑客来说，绝对是一个宝藏。这是一个记录了所有节点的文档，当点击相应节点的超链接时，还会提供响应的JSON和XML样本Payload，以及节点返回的响应数据格式。检查完这些节点之后，我发现了一个可能会导致某些信息泄露的节点：

    
    
    /GetETicket/{TransactionscreenID}/{UserName}/{Password}/{ProcessType}

这里要求提供TransactionscreenID、UserName和Password这三个参数，但此时的我竟然有些束手无策测。

![](https://image.3001.net/images/20200302/1583148878_5e5cef4e9f752.png!small)

通过Android应用程序获取到订票信息后，便会触发这个节点，然后我们就可以查看到获取订票细节所需的参数值了：

![](https://image.3001.net/images/20200302/1583148883_5e5cef53d55c2.png!small)

节点会以HTML Table的格式返回乘客的信息，而不是之前的PDF格式：

![](https://image.3001.net/images/20200302/1583148890_5e5cef5a8c1d9.png!small)

现在，我们可以再看看之前的文档了。还记得ProcessType参数吗？我们可以直接将URL地址中的最后一个参数改成1或者其他值：

![](https://image.3001.net/images/20200302/1583148900_5e5cef6442a3e.png!small)

![](https://image.3001.net/images/20200302/1583148905_5e5cef6975a34.png!small)

将“3”传递给ProcessType参数，将会触发异常，并允许我们查看到底层代码。

##  第三个IDOR：同一家公司的另一个终端节点

在查看文档时，我还发现了另一个可能会泄露敏感信息的节点：

    
    
    /GetPaxBookingDetails/{TransactionscreenID}/{UserName}/{Password}

向这个节点请求数据，将会返回用户的个人身份识别信息PII。只要你在这家公司的网站上订过票，那你的数据就可以通过这样的方式来获取到。

![](https://image.3001.net/images/20200302/1583148924_5e5cef7c2e793.png!small)

![](https://image.3001.net/images/20200302/1583148930_5e5cef82899d5.png!small)

![](https://image.3001.net/images/20200302/1583148934_5e5cef86d7c64.png!small)

###  漏洞成因

该节点之所以会存在这个漏洞，是因为它没有部署任何的访问控制策略或健壮的身份验证机制。

 *** 参考来源：[medium](https://medium.com/@aseem.shrey/attention-to-details-a-curious-case-of-multiple-idors-5a4417ba8848)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

