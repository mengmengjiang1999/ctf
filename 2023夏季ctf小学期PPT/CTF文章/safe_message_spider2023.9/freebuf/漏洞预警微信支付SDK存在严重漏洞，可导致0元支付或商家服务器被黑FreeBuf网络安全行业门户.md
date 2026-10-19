![timg.jpg](https://image.3001.net/images/20180703/15306013941168.jpg!small)

  

**XXE (XML External Entity Injection)** 漏洞发生在应用程序解析 XML
输入时，没有禁止外部实体的加载。是一种针对使用XML交互的Web应用程序的攻击方法。

 **受影响版本：**

 **JAVA SDK，WxPayAPI_JAVA_v3**

微信在JAVA版本的SDK中提供callback回调功能，用来帮助商家接收异步付款结果，该接口接受XML格式的数据，攻击者可以构造恶意的回调数据（XML格式）来窃取商家服务器上的任何信息。一旦攻击者获得了关键支付的安全密钥（md5-key和商家信息，将可以直接实现0元支付购买任何商品）。当XML允许引用外部实体时，黑客可以通过构造恶意XML实体文件，实现远程读取任意系统文件、远程执行系统命令等一系列危险操作，严重危害商家服务器的系统安全。

目前，微信官方尚未对SDK进行修复，但漏洞利用信息以及攻击方式已被公开，影响范围巨大（已经披露出的有陌陌、vivo确认存在该漏洞），建议用到微信支付JAVA
SDK的企业立刻开展自查并关注微信官方安全通告。

![WechatIMG88.png](https://image.3001.net/images/20180703/15306015286574.png!small)

2018年7月2号，该漏洞在国外漏洞披露网站首次公布

  

国外漏洞披露网站公布的实际攻击案例：

![640.jpeg](https://image.3001.net/images/20180703/15306015832510.jpeg!small)![640.png](https://image.3001.net/images/20180703/15306016049224.png!small)  

青莲云安全团队会持续跟踪该漏洞进展，请厂家持续关注。

  

[点击该处了解漏洞详情](http://seclists.org/fulldisclosure/2018/Jul/3)

