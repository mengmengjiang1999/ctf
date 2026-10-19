面试大佬只给了一个IP加一个端口
![image.png](https://image.3001.net/images/20210107/1610030801_5ff71ed1b37681d63058a.png!small)

打开后什么，都没有通过目录扫描，漏洞扫描也什么也没发现。 然后开始旁站扫描 全端口扫描
![image.png](https://image.3001.net/images/20210107/1610030802_5ff71ed21be570b1983e7.png!small)

发现58080端口上跑的apachetomcat
![image.png](https://image.3001.net/images/20210107/1610030802_5ff71ed2deb65c055fe3a.png!small)

尝试登录manager,默认的tomcat/tomcat,admin/admin都不正确。
![image.png](https://image.3001.net/images/20210107/1610030803_5ff71ed37b9e3997b7079.png!small)

使用burp进行抓包测试
![image.png](https://image.3001.net/images/20210107/1610030804_5ff71ed40c5b0d4b2d2ac.png!small)

对authorization进行base64破解

![image.png](https://image.3001.net/images/20210107/1610030804_5ff71ed480f41b2274a20.png!small)

使用burp进行爆破，选择自定义迭代器 设置账户
![image.png](https://image.3001.net/images/20210107/1610030804_5ff71ed4f0ccf3b5b7c45.png!small)

中间的：
![image.png](https://image.3001.net/images/20210107/1610030805_5ff71ed581da9015c9573.png!small)

密码
![image.png](https://image.3001.net/images/20210107/1610030806_5ff71ed6095cdeac21e2a.png!small)

admin:111111

![image.png](https://image.3001.net/images/20210107/1610030806_5ff71ed693aa1825b9ad9.png!small)

进行base64编码 禁用url编码，默认打对勾，把对勾去掉
![image.png](https://image.3001.net/images/20210107/1610030807_5ff71ed71c963964fa065.png!small)

如果返回都是200那么把cookie等内容去掉进行爆破
![image.png](https://image.3001.net/images/20210107/1610030807_5ff71ed778c388ab4ec93.png!small)

得到账号密码admin:111111和tomcat6:tomcat6 登录后台：
![image.png](https://image.3001.net/images/20210107/1610030808_5ff71ed81b2362be80b92.png!small)

打jar包：

![image.png](https://image.3001.net/images/20210107/1610030808_5ff71ed8992d3806f22e6.png!small)

上传

![image.png](https://image.3001.net/images/20210107/1610030809_5ff71ed91b214571c3d3c.png!small)

![image.png](https://image.3001.net/images/20210107/1610030809_5ff71ed98d853e394d774.png!small)

注：不通过jar打包，是无法true的！

访问上传后的webshell
![image.png](https://image.3001.net/images/20210107/1610030810_5ff71eda0902f9ee58fa6.png!small)

![image.png](https://image.3001.net/images/20210107/1610030810_5ff71edaa1f6ef90a4eb2.png!small)

可以出网直接上cs

![image.png](https://image.3001.net/images/20210107/1610030811_5ff71edb3f273d4378d4c.png!small)

面试大佬说要拿到桌面才行，cs自带截屏直接上图

![image.png](https://image.3001.net/images/20210107/1610030811_5ff71edbb8f0c2cbdbbb2.png!small)

提权：用cs插件：梼杌——权限提升——MS16-032

![image.png](https://image.3001.net/images/20210107/1610030812_5ff71edc3f18953ffcc51.png!small)

读密码：

![image.png](https://image.3001.net/images/20210107/1610030812_5ff71edccab156e32aef6.png!small)

总结：
1.主站并没有漏洞，只是空白页，出题大佬确实有点坑，害我浪费半天时间，这里考点主要是思路上，在我们正常的渗透测试中一旦目标站点无法直接拿下不要死扣，要换思路从旁站来。

2.通过全端口扫描才找到58080，tomcat，第一时间想到的就是tomcat
manager后台弱口令war包上次getshell,这个主要考点是经验，如果没看过类似文章可能就不会想到这里有问题。另外默认口令都修改了，看来管理员有一定安全意识的，要进行破解，这个时候从网上找找资料，考点是要求面试白帽有快速学习能力。

3.最后面试大佬要求，要截屏“拿不到桌面的黑客不是合格的黑客”，这里主要是希望面试者能够了解渗透的整个流程，而不局限于web渗透，包括提权，内网渗透代理，内存提权密码等渗透测试流程都掌握。

结语：安全圈现在太乱，逐渐浮躁起来了，如果不即时打住（给小白上一课）真的会影响深远（以为安全圈很好混）。好多培训机构通过一两个月的渗透测试培训就让学员面试上岗，然而这些人到了公司既不能调试设备，又不能写方案，渗透测试也是二把刀还得有人带，以为会点工具就会渗透测试了，开个goby就万事大吉了（goby很好用，我也用，但对于渗透实战肯定是不够的）！企业不是培训机构，谁有时间天天带你呢，公司掏钱要你是来干活的，不是来学习的。希望没通过面试的同学不要气馁（黑客精神在于不放弃），多多搭环境自己练练，相信会很有钱途的！

注：原创来自狼组：

<https://plat.wgpsec.org/knowledge/view/0c338f82e2f4415584f7964c049d363f>

更多内容，欢迎关注微信公众号“天大天财”

![1610030653_5ff71e3d4f2c6f21dd499.png!small](https://image.3001.net/images/20210107/1610030653_5ff71e3d4f2c6f21dd499.png!small)

