前段时间学习审计时，审计的一个小众cms 梦想cms, 不喜勿喷，谢谢 ^0^  

## 环境  

###  **一、** ** **Lmxcms_v1.4下载:****

[
_http://www.lmxcms.com/file/d/down/xitong/20150113/201501130910222659.rar_](http://www.lmxcms.com/file/d/down/xitong/20150113/201501130910222659.rar)  

###  **二、** ** **Lmxcms_v1.4搭建:****

环境：phpstudy2018 +windows10

  * 第一步：上传程序到服务器网站根目录
  * 第二步：运行install目录进行安装(在地址栏输入[ _http://你的域名/install_](http://xn--6qqv7i2xdt95b/install))
  * 第三步：登陆后台（在地址栏输入[ _http://你的域名/admin_](http://xn--6qqv7i2xdt95b/install) _.php_ ）。

## 代码审计  

  * 漏洞分析

打开文件文件AcquisiAction.class.php，找到update()函数分析。

发现了存在sql注入漏洞。分析图1

![1605443994_5fb1219a880bdfc8e3b20.png!small?1605443995560](https://image.3001.net/images/20201115/1605443994_5fb1219a880bdfc8e3b20.png!small?1605443995560)

####  ** **图1****

标记1：判断是否有POST请求

标记2：将POST请求的内容经过一系列操作赋值给**$data**变量

标记3：sql注入的漏洞点，进入update函数-->updateModel()函数-->updateDB()函数.会发现一处sql语句执行处。见图2

![1605444000_5fb121a0631c56db9e0d1.png!small?1605444001410](https://image.3001.net/images/20201115/1605444000_5fb121a0631c56db9e0d1.png!small?1605444001410)

####  ** **图2****

标记1：sql语句构造并执行。都是数据未做好过滤，直接储存在数据库中。

###  **二、** ** **漏洞验证****

在后台的采集管理-->创建/修改节点处，填写表单。如下图3所示。

![1605444008_5fb121a81f5f336ac00e3.png!small?1605444009121](https://image.3001.net/images/20201115/1605444008_5fb121a81f5f336ac00e3.png!small?1605444009121)

 ** **图3****

标记1于标记2处存在sql注入漏洞，可以提交精心构造的sql测试语句： ** **aa' and
updatexml(0,concat(0x7e,database()),1) and 'ss****

效果：浏览器会返回数据库的名称。见图4

![1605444017_5fb121b1c4beec8cc253b.png!small?1605444018872](https://image.3001.net/images/20201115/1605444017_5fb121b1c4beec8cc253b.png!small?1605444018872)

 ** **图4****

攻击者可以利用此漏洞获取网站的数据库信息。

