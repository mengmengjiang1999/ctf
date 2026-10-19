## 漏洞简介：

MaxSite CMS是俄国MaxSite
CMS开源项目的一款网站内容管理系统。马克斯程序(MaxCMS)以开源、免费、功能强大、安全健壮、性能卓越、超级易用、模板众多、插件齐全等优势，受到众多企业和站长的喜爱。马克斯程序研发团队拥有多年的技术积累和产品开发经验，成立了官方技术支持团队、官方模板团队、官方插件团队。一切立足于站长利益、孜孜不倦的挖掘站长需求、不断提升产品体验，自主创新多项特色技术、提升网站品质!独立开发的管理员管理系统，可以对管理员进行更能人性化的管理网站。
Maxsite CMS存在文件上传漏洞，攻击者可利用该漏洞通过精心制作的PHP文件执行任意代码。账户为弱口令

## 漏洞环境：

春秋云镜中的漏洞靶标，CVE编号为CVE-2022-25411

## 漏洞复现：

访问环境，网站首页的很多东西都访问不到，没有发现可利用的点

![](https://image.3001.net/images/20230630/1688090311_649e36c77e9f57641fe28.png!small)

  

这里就用dirb来扫描一下网站的后台和可用的文件，扫描到了robots.txt文件，去访问一下

![](https://image.3001.net/images/20230630/1688090335_649e36df6873a1582ac23.png!small)![](https://image.3001.net/images/20230630/1688090348_649e36ec279aeaf425459.png!small)

  

看到了类似后台的目录，去打开就到了后台登录界面，尝试常见弱口令发现账户密码为admin/admin888

![](https://image.3001.net/images/20230630/1688090367_649e36ffbb411740cfdc6.png!small)![](https://image.3001.net/images/20230630/1688090378_649e370aa0100564dfcf5.png!small)

  

进到网站后台后根据翻译找到了一个文件上传设置的地方，发现了文件可上传的类型设置，在后面根据格式加上php

![](https://image.3001.net/images/20230630/1688090409_649e37296b5750ead986e.png!small)![](https://image.3001.net/images/20230630/1688090417_649e3731bc02293f86bed.png!small)

  

根据翻译找到文件上传点，写一句话木马并上传文件

![](https://image.3001.net/images/20230630/1688090460_649e375ce416cdcea8ba0.png!small)![](https://image.3001.net/images/20230630/1688090484_649e37746a3af1e14d5be.png!small)![](https://image.3001.net/images/20230630/1688090496_649e37808d0d78398748a.png!small)![](https://image.3001.net/images/20230630/1688090507_649e378b3ee606129a0b0.png!small)

  

点击文件往浏览器标签栏拽就可访问文件

![](https://image.3001.net/images/20230630/1688090527_649e379f1aeb74ee3526a.png!small)

  

传入phpinfo();不知道为什么没有反应，就尝试用蚁剑连接

![](https://image.3001.net/images/20230630/1688090544_649e37b0360d976ccddda.png!small)

  

可以连接成功，文件可用，就可以用蚁剑进行webshell了

![](https://image.3001.net/images/20230630/1688090577_649e37d19336544b32a39.png!small)

  

这里要获取flag就查找flag就行了

![](https://image.3001.net/images/20230630/1688090591_649e37dfd9ab78ddc1acb.png!small)

  

  

