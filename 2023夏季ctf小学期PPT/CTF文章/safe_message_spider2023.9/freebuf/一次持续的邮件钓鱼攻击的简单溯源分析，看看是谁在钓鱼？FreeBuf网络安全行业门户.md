## **一、基本情况**

昨天连续收到两封欺骗邮件，分别是凌晨和下午，邮件的主题、内容都是一样的，主要 是发送人的信息不同，两份邮件截图如下所示：

第一封：

![1654072153_62972359c628f2bb88321.png!small](https://image.3001.net/images/20220601/1654072153_62972359c628f2bb88321.png!small)

第二封：

![1654072136_6297234855c34bb7554b0.png!small](https://image.3001.net/images/20220601/1654072136_6297234855c34bb7554b0.png!small)

邮件内容中，欺骗用户连接的URL地址也是一样的，都是：<http://xiangwangshenghuo.cn/page.php>。

因此，可认定为同一个组织/个人实施的邮件欺骗攻击。

唉，怎么一不小心就成为攻击目标了，还一天两封，晕。

今天在outlook直接点击访问，发现360已经会进行拦阻，显示如下：

![1654072311_629723f77ac06b4a3eb45.png!small](https://image.3001.net/images/20220601/1654072311_629723f77ac06b4a3eb45.png!small)

直接复制url：<http://xiangwangshenghuo.cn/page.php>进行浏览器访问，登陆界面如下：

![1654072396_6297244c44371ba62cf4f.png!small](https://image.3001.net/images/20220601/1654072396_6297244c44371ba62cf4f.png!small)

欺骗用户填写邮箱的账户和密码。

如果直接访问主页[http://xiangwangshenghuo.cn](http://xiangwangshenghuo.cn/page.php)，发现显示的也是邮件登陆系统，界面如下：

![1654072488_629724a8de68e3e1a628c.png!small](https://image.3001.net/images/20220601/1654072488_629724a8de68e3e1a628c.png!small)

随便输入虚拟的邮箱账户和密码，显示“密码错误”，如下。

![1654072514_629724c23193931685823.png!small](https://image.3001.net/images/20220601/1654072514_629724c23193931685823.png!small)

网站的结构大概如下：

![1654072543_629724df4148764898e88.png!small](https://image.3001.net/images/20220601/1654072543_629724df4148764898e88.png!small)

很明显，这就是赤裸裸的邮件钓鱼攻击，用于收集被攻击对象的邮箱账户和密码。

通过分析邮件头属性，发现攻击者没有对邮件头进行信息伪造，邮件实际发送者就是outlook邮箱中显示的发送者，分别是<market@jinglun.com.cn>和<wangren@micropoint.com.cn>，这两个域名是国内正常的两家公司，说明攻击者通过其他手段获取了这两个邮箱的控制权限，尤其是micropoint.com.cn这家公司，还是做网络安全业务的。

第1封邮件头如下：

![1654073386_6297282abc0d2fc4d88ac.png!small](https://image.3001.net/images/20220601/1654073386_6297282abc0d2fc4d88ac.png!small)

从上图可知，该邮件是通过主机名为PC293的主机发送的，网关地址为：10.10.10.1。

第2封邮件头如下：

![1654073441_62972861ec1a05ded3174.png!small](https://image.3001.net/images/20220601/1654073441_62972861ec1a05ded3174.png!small)

从上面的邮件头可以看出，攻击者通过名为PC293的主机发送邮件，但是本次外部IP地址却明显显示在邮件头里面，该IP地址为：58.243.143.201，根据IP地址查询为安徽黄山的联通用户，因此我们可以猜测上面的10.10.10.1是否是联通内部的网关地址？

![1654073543_629728c7dc1336fbfa64b.png!small](https://image.3001.net/images/20220601/1654073543_629728c7dc1336fbfa64b.png!small)

再来看看欺骗域名的情况，xiangwangshenghuo.cn应该是汉字“向往生活”的拼音，不知道攻击者是希望过上怎样的生活，呵呵。

通过ping解析，域名指向的IP是156.234.27.228，位置在中国香港。

![1654072660_62972554bf35b9cb3815b.png!small](https://image.3001.net/images/20220601/1654072660_62972554bf35b9cb3815b.png!small)

![1654072671_6297255ff2a4761072fef.png!small](https://image.3001.net/images/20220601/1654072671_6297255ff2a4761072fef.png!small)

  

我们再来查看156.234.27.228上绑定的域名，查询结果如下，一看都是近几天才绑定的域名，汗，没想到邮箱竟直接成为首轮攻击对象。

![1654072754_629725b226a914ed2a9b1.png!small](https://image.3001.net/images/20220601/1654072754_629725b226a914ed2a9b1.png!small)

通过直接访问 ousiman568.com、hwobuswangzhe.cn域名，发现登陆界面和xiangwangshenghuo是一样的，如下图：

![1654072809_629725e9b0429e62eaf29.png!small](https://image.3001.net/images/20220601/1654072809_629725e9b0429e62eaf29.png!small)

因此，说明这三个域名都是攻击者注册并绑定的，可能用于不同的攻击对象。

再分别对三个域名进行注册信息查询，结果分别如下：

![1654072906_6297264a4527f9ae6ad6a.png!small](https://image.3001.net/images/20220601/1654072906_6297264a4527f9ae6ad6a.png!small)

![1654072941_6297266d67fb21322af7b.png!small](https://image.3001.net/images/20220601/1654072941_6297266d67fb21322af7b.png!small)

![1654072981_62972695d403bc954c0f4.png!small](https://image.3001.net/images/20220601/1654072981_62972695d403bc954c0f4.png!small)

从上面可判断，上述三个域名都是通过浙江贰贰网络有限公司进行申请注册的，通过贰贰网络查询域名，结果如下：

![1654073056_629726e07b77e7e7384c3.png!small](https://image.3001.net/images/20220601/1654073056_629726e07b77e7e7384c3.png!small)

综上，我们可以初步判断攻击者的基本信息，包含域名注册的姓名、QQ号和所在的大概地理位置。

##  **二、小结**

该钓鱼攻击正在持续实施中，攻击者还在不停的发送钓鱼邮件，并且其用于钓鱼的网站域名也不停变化，截至7月7日，发现的IP有3个（香港），绑定的域名信息如下：

1、IP1：156.234.27.226

域名绑定历史：  
2022-07-06-----2022-07-06 hbtmfs.cn  
2022-07-06-----2022-07-06 mquest.cn  
2022-07-04-----2022-07-04 thequest.cn  
2022-06-30-----2022-06-30 foreseabank.cn  
2022-06-30-----2022-06-30 graydigital.cn  
2022-06-27-----2022-06-27 qflwpq.cn  
2022-06-22-----2022-06-24 passportoss.cn  
2022-06-15-----2022-06-18 xuyuying.cn  
2022-06-09-----2022-06-13 xuxiaoying.cn  
2022-06-08-----2022-06-09 www.passportoss.cn

2、IP2：156.234.27.228  
域名绑定历史：  
2022-07-05-----2022-07-06 cafine.cn  
2022-06-28-----2022-07-01 ceciliaderafael.cn  
2022-06-29-----2022-06-29 etherrock.cn  
2022-06-22-----2022-06-27 laliceshiji.cn  
2022-06-24-----2022-06-24 opencti.cn  
2022-06-20-----2022-06-21 ihappywind.cn  
2022-06-21-----2022-06-21 uwurl.cn  
2022-06-09-----2022-06-16 minyanxi.cn  
2022-06-01-----2022-06-12 wobuswangzhe.cn  
2022-05-29-----2022-06-11 ousiman568.com  
2022-05-30-----2022-06-11 xiangwangshenghuo.cn  
2022-05-31-----2022-05-31
[www.xiangwangshenghuo.cn](http://www.xiangwangshenghuo.cn)

3、IP3：103.223.122.172  
域名绑定历史：  
2022-04-26-----2022-06-09 mail.uepojlsd.cn  
2022-05-07-----2022-06-09 dashenowqq.cn  
2022-05-31-----2022-05-31 www.passportoss.cn  
2022-05-11-----2022-05-12 mail.kfrihzlaqq.cn  
2022-05-12-----2022-05-12 uepojlsd.cn  
2022-05-06-----2022-05-08 mail.geelyemail.cn  
2022-04-26-----2022-04-26 jingkezhongxin.cn  
2017-12-03-----2017-12-03 www.200301.com  
2017-11-25-----2017-11-25 1399p.cn  
2017-10-06-----2017-10-07 10pk.ws

4、同时，攻击者对最近对部分CN域名已开启隐私保护服务，whois查询无法看到注册者信息，如下：

![1657160799_62c6445f522952f1c66a7.png!small](https://image.3001.net/images/20220707/1657160799_62c6445f522952f1c66a7.png!small)

![1657160911_62c644cfebc3e5ba94aa0.png!small](https://image.3001.net/images/20220707/1657160911_62c644cfebc3e5ba94aa0.png!small)

