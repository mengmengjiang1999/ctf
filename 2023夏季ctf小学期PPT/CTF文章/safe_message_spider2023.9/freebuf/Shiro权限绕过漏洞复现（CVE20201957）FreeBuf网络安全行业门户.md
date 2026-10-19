# **0x00简介**

Apache
Shiro是一个强大且易用的Java安全框架,执行身份验证、授权、密码和会话管理。使用Shiro的易于理解的API,您可以快速、轻松地获得任何应用程序,从最小的移动应用程序到最大的网络和企业应用程序。

#  **0x01漏洞概述**

Shiro框架通过拦截器功能来对用户访问权限进行控制，如anon,
authc等拦截器。anon为匿名拦截器，不需要登录即可访问；authc为登录拦截器，需要登录才可以访问。主要是Spring
web在匹配url的时候没有匹配上/导致绕过

#  **0x02影响范围**

Apache Shiro < 1.5.3

#  **0x03环境搭建**

1.下载实验代码，下载地址：

https://github.com/lenve/javaboy-code-samples/tree/master/shiro/shiro-basic

2.下载完成后将项目导入Java IDEA中，在pom.xml文件可以看到shiro的版本，把版本修改成1.4.2。（不修改也可）

![1611714250_6010cecaed926f61329dd.png!small](https://image.3001.net/images/20210127/1611714250_6010cecaed926f61329dd.png!small)

3.打开maim目录下ShiroConfig.java文件，添加authc拦截器的拦截正则

map.put("/hello/*", "authc");

![1611714254_6010cecec8d572158f464.png!small](https://image.3001.net/images/20210127/1611714254_6010cecec8d572158f464.png!small)

4\. 打开LoginController.java文件，修改路由控制器方法，添加一个方法。

import org.springframework.web.bind.annotation.PathVariable;

@GetMapping("/hello/{currentPage}")

public String hello(@PathVariable Integer currentPage) {

return "hello";

}![1611714259_6010ced3151b985ec401b.png!small](https://image.3001.net/images/20210127/1611714259_6010ced3151b985ec401b.png!small)

![1611714266_6010cedad15a6371f2ea2.png!small](https://image.3001.net/images/20210127/1611714266_6010cedad15a6371f2ea2.png!small)

5.启动应用点击右上角三角形，运行出现以下图片表示启动成功

![1611714275_6010cee3683091106b590.png!small](https://image.3001.net/images/20210127/1611714275_6010cee3683091106b590.png!small)

 **0x04漏洞复现**

1.在浏览器访问http://your-ip:8080/login,可以看到需要登录

![1611714284_6010ceec15942f5cd1170.png!small](https://image.3001.net/images/20210127/1611714284_6010ceec15942f5cd1170.png!small)

2.打开Burp访问首页进行抓包，并将抓到的包送到Reapter模块

![1611714292_6010cef456f9629781e10.png!small](https://image.3001.net/images/20210127/1611714292_6010cef456f9629781e10.png!small)

3.将url修改为/hello/1，发包，可以看到跳转到了登陆界面。

![1611714295_6010cef7e22b645815fe8.png!small](https://image.3001.net/images/20210127/1611714295_6010cef7e22b645815fe8.png!small)

4.在url处/hello/1后面再加上一个反斜杠/hello/1/，访问成功

![1611714298_6010cefaddfb8cdd4e065.png!small](https://image.3001.net/images/20210127/1611714298_6010cefaddfb8cdd4e065.png!small)

#  **0x05修复建议**

建议升级至最新版本

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

