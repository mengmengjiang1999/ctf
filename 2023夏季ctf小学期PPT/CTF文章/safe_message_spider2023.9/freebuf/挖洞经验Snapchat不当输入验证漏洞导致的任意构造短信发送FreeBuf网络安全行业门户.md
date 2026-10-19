![snapchat.jpg](https://image.3001.net/images/20200213/1581557948_5e44a8bce3a7e.jpg!small)

**今天分享的这篇Writeup是关于Snapchat网站的不当输入验证漏洞，攻击者可利用该漏洞，向受害者手机以短信方式发送任意构造的文本或URL链接，从而实现进一步的恶意破坏或攻击，漏洞最终获得了$1000的奖励。**

## 漏洞概况

Snapchat存在一个网站<https://whatis.snapchat.com/>，该网站介绍了Snapchat的一些具体功能和使用概况，在网站页面底部还给出了Snapchat应用APP的两种下载方法：通过点击下载以及填入手机号码以短信方式获取APP下载链接。

![Snap-00.png](https://image.3001.net/images/20200213/1581558033_5e44a911baac8.png!small)

于是，我尝试填入自己的手机号码，点击发送链接（Send
Link），想看看发给我的手机短信是什么链接内容。该动作执行之后，会向app.snapchat.com发起一个HTTP POST请求：

>
> [https://app.snapchat.com/stories_everywhere/download_sms?phone_number=2133198570&country_code=US&cid=whatis](https://app.snapchat.com/stories_everywhere/download_sms?phone_number=2133198570&country_code=US&cid=whatis)

其中的参数 ‘cid’和内容值'whatis'引起了我的注意，因为我收到的手机短信中也包含了其参数内容值'whatis'：

![Snap-01.jpg](https://image.3001.net/images/20200213/1581558092_5e44a94c6e375.jpg!small)

观察之后，我打算重新构造HTTP POST请求，变化其中的 ‘cid’参数值为我自己填写的内容，如下：

> cid=TES+HACKED+1337+LOL+HacKerOne.com

![Snap-02.png](https://image.3001.net/images/20200213/1581558139_5e44a97bd1b72.png!small)

重放该HTTP POST请求之后，我手机收到Snapchat发送来的短信内容如下：

![Snap-04.jpg](https://image.3001.net/images/20200213/1581558161_5e44a9912cfe9.jpg!small)其中竟然包含了我任意构造的cid内容值，并且点击其中的链接，可以形成有效跳转：

![Snap-03.jpg](https://image.3001.net/images/20200213/1581558177_5e44a9a11b6fe.jpg!small)

最终，漏洞上报后，Snapchat及时在短信回复机制中删除了cid和其它相关参数信息，修复了漏洞，我也获得了$1,000的奖励。

## 经验总结

> 可以对目标网站的一些公共应用进行测试，在发起请求中变化参数值，观察服务端的具体响应；
>
> 保持激情和动力，说不准下一次你就会发现一个大漏洞

***参考来源：[securitybreached](https://blog.securitybreached.org/2020/01/26/improper-input-validation-add-custom-text-and-urls-in-sms-send-by-snapchat-bug-bounty-poc/)，clouds 编译整理，转载请注明来自 FreeBuf.COM**  

