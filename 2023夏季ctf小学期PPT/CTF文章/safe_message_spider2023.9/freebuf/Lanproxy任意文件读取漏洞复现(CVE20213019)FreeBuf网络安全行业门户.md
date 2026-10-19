## **0x00简介**

lanproxy是一个将局域网个人电脑、服务器代理到公网的内网穿透工具，支持tcp流量转发，可支持任何tcp上层协议（访问内网网站、本地支付接口调试、ssh访问、远程桌面...）。目前市面上提供类似服务的有花生壳、TeamView、GoToMyCloud等等，但要使用第三方的公网服务器就必须为第三方付费，并且这些服务都有各种各样的限制，此外，由于数据包会流经第三方，因此对数据安全也是一大隐患。

##  **0x01漏洞概述**

Lanproxy1.0通过../绕过读取任意文件。该漏洞允许目录遍历读取/../conf/config.properties来获取到内部网连接的凭据。

##  **0x02影响版本**

Lanproxy1.0

##  **0x03环境搭建**

1.下载Lanproxy安装包，下载地址：

https://file.nioee.com/d/2e81550ebdbd416c933f/

![1612401870_601b4cce96d01b99b0d02.png!small](https://image.3001.net/images/20210204/1612401870_601b4cce96d01b99b0d02.png!small)

2.解压后运动到/usr/local目录下

mv proxy-server-0.1/ /usr/local/

![1612401875_601b4cd36552a64ceab83.png!small](https://image.3001.net/images/20210204/1612401875_601b4cd36552a64ceab83.png!small)

3.进入proxy-server-0.1 bin目录下给startup.sh加上执行权限，然后启动服务

cd proxy-server-0.1/bin

chmod +x startup.sh

./startup.sh

![1612401878_601b4cd6978c4eec22c2d.png!small](https://image.3001.net/images/20210204/1612401878_601b4cd6978c4eec22c2d.png!small)

4.在浏览器访问http://your-ip:8090，出现以下登录界面启动成功

![1612401887_601b4cdff2516504b8ba2.png!small](https://image.3001.net/images/20210204/1612401887_601b4cdff2516504b8ba2.png!small)

##  **0x04漏洞复现**

1.在登录页面，使用Burp抓包，并发送到Repeater（重放模块）

![1612401891_601b4ce364d9523161fcc.png!small](https://image.3001.net/images/20210204/1612401891_601b4ce364d9523161fcc.png!small)

2.在url构造以下链接读取配置文件

/../conf/config.properties

![1612401895_601b4ce79c837fef881fe.png!small](https://image.3001.net/images/20210204/1612401895_601b4ce79c837fef881fe.png!small)

3.修改payload读取敏感文件

../../../../etc/passwd

![1612401904_601b4cf02c14b3eab48df.png!small](https://image.3001.net/images/20210204/1612401904_601b4cf02c14b3eab48df.png!small)

##  **0x05修复建议**

1、目前厂商已发布升级补丁以修复漏洞，补丁获取链接：

https://github.com/ffay/lanproxy/commits/master

在这里，给大家介绍一下“东塔攻防世界靶场”

2020年12月，东塔攻防世界靶场正式对外提供注册，各位小伙伴可通过注册后进行体验。新注册用户可获得一定的积分，对于靶场使用获取正确的Key后，也可以获取一定的经验值，经验值根据排名会不定期给予一定的奖励。

并且，在操作过程中，针对出现的Bug和安全漏洞问题可以和塔塔子提出，审核通过后可以获得相应的奖励积分。

东塔攻防世界网站不定时推出可免费限时使用的靶场，具体可关注东塔网络安全学院推出的一系列活动或添加东塔客服了解详情。

东塔攻防世界靶场主要分为在线靶场和职业体系两大特色板块。且平台内的靶场会定期更新内容，尤其是最新漏洞复现的一些文章和靶场，会优先在靶场中提供环境让大家体验。

东塔攻防世界网站会不定期限时免费推出最新的一些复现的靶场，以供学习交流，给了大家充分体验和使用靶场的机会。

具体可关注东塔网络安全学院推出的一系列活动或添加东塔客服wx（dongtakefu）了解详情。

除了以上介绍的内容，还有更多宝藏区域，更强大的功能，等你来寻宝！

详戳下方“东塔攻防世界靶场”网址，Get一波新世界

https://labs.do-ta.com

