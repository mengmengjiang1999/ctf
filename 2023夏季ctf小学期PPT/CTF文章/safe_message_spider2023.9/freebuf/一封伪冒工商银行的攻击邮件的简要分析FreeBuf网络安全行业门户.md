## 一、大概背景

今天，收到一封邮件，显示为：中国工商银行的“付款转账通知“，如下图所示：

![1652088637_6278df3d0a3e6bddedba1.png!small?1652088637025](https://image.3001.net/images/20220509/1652088637_6278df3d0a3e6bddedba1.png!small?1652088637025)

直接双击打开附件ISO文件，加载后显示内容为一个伪造成PDF文档的EXE可执行文件，如下图所示：

![1652088645_6278df4519030be9dd8dc.png!small?1652088644851](https://image.3001.net/images/20220509/1652088645_6278df4519030be9dd8dc.png!small?1652088644851)

该exe文件除了将图标伪造成PDF外，还伪造了EXE文件属性为：卡巴斯基的应用程序：Jefahsumm.exe，如下图所示：

![1652088652_6278df4c55c7911fca245.png!small?1652088652363](https://image.3001.net/images/20220509/1652088652_6278df4c55c7911fca245.png!small?1652088652363)

对邮件原始头进行分析，发现是一份伪造工行邮箱[info@icbc.com.cn](mailto:info@icbc.com.cn)的欺骗邮件

[smtp.mailfrom=info@icbc.com.cn](mailto:smtp.mailfrom=info@icbc.com.cn)

smtp.helo=webmail.ceblinds.com

实际的邮件服务器是：webmail.ceblinds.com，IP地址是：176.9.9.122

邮件头如下表所示：

X-Barracuda-Envelope-From: info@icbc.com.cn

X-ASG-Whitelist: Sender

X-Barracuda-Effective-Source-IP: UNKNOWN[176.9.9.122]

X-Barracuda-Apparent-Source-IP: 176.9.9.122

User-Agent: Roundcube Webmail/1.4.13

To: undisclosed-recipients:;

Received-SPF: pass (frakton.live: connection is authenticated)

Authentication-Results: frakton.live;

spf=pass (sender IP is ::1) smtp.mailfrom=info@icbc.com.cn
smtp.helo=webmail.ceblinds.com

Received: from webmail.ceblinds.com (localhost.localdomain [IPv6:::1]) by

frakton.live (Postfix) with ESMTPSA id C30DA1405E5; Mon, 9 May 2022 05:06:20

+0200 (CEST

  
  
  
---  
  
## 二、分析情况

Exe文件执行后，首先访问URL：http://
bmn.lpmpbanten.id/fint/Jefahsumm_Leczmpgo.bmp下载文件，该url字符串直接明文显示在EXE里面，如下图所示：

![1652088665_6278df595cf57d6bf73e7.png!small?1652088665388](https://image.3001.net/images/20220509/1652088665_6278df595cf57d6bf73e7.png!small?1652088665388)

发送的HTTP报文抓包如下图所示：

![1652088674_6278df626f3ee87633aca.png!small?1652088675017](https://image.3001.net/images/20220509/1652088674_6278df626f3ee87633aca.png!small?1652088675017)

通过简单分析，下载的BMP文件其实是一个EXE文件，它是EXE倒序的结果。我们看BMP文件结尾内容如下图所示，一看就是一个正常的PE文件的倒序。

![1652088685_6278df6d8e33767a128b8.png!small?1652088685871](https://image.3001.net/images/20220509/1652088685_6278df6d8e33767a128b8.png!small?1652088685871)

直接访问：http:// bmn.lpmpbanten.id/，显示为一个需要登陆的系统，如下图所示：

![1652088695_6278df773d109fb654c90.png!small?1652088695116](https://image.3001.net/images/20220509/1652088695_6278df773d109fb654c90.png!small?1652088695116)

直接访问：http://
bmn.lpmpbanten.id/fint，则会直接列举该目录下的所有文件，显示为4个图片文件，下载后经过分析其实和上面的bmp文件一样，其实都是EXE文件的倒序，恶意文件的生成时间为：5月8日和9日，如下图所示:

![1652088703_6278df7fcb11c05905d11.png!small?1652088703768](https://image.3001.net/images/20220509/1652088703_6278df7fcb11c05905d11.png!small?1652088703768)

接着，exe文件会将主机的信息通过SMTP协议发送，具体如下。

SMTP服务器地址为：mail.elparque.com.uy（correo.netgate.com.uy），二者指向同一个IP地址：200.40.119.50.

SMTP服务器端口：587

![1652088716_6278df8c355b748a8d0cc.png!small?1652088716239](https://image.3001.net/images/20220509/1652088716_6278df8c355b748a8d0cc.png!small?1652088716239)

发送人：[info@elparque.com.uy](mailto:info@elparque.com.uy)

收件人：[contacto@filtrosdys.com](mailto:contacto@filtrosdys.com)

邮件主题：当前受害主机的当前登陆名（admin）+主机名。

邮件内容：当前受害主机的基本信息，如下图所示：

![1652088726_6278df963a3af0fced18c.png!small?1652088725960](https://image.3001.net/images/20220509/1652088726_6278df963a3af0fced18c.png!small?1652088725960)

具体的SMTP访问数据如下图所示：

![1652088744_6278dfa879e79b272a0d9.png!small?1652088744817](https://image.3001.net/images/20220509/1652088744_6278dfa879e79b272a0d9.png!small?1652088744817)

利用内嵌的账户名和密码可以成功登陆[info@elparque.com.uy](mailto:info@elparque.com.uy)的邮箱地址。

## 三、小结

本次邮件欺骗攻击是伪冒邮件头，冒充工商银行邮件欺骗用户点击，攻击文档是一个伪装成PDF图标的可执行文件。

1、Kzjqmrxttmbhvqnew-clientlime.exe：

SHA256 : A9CA4A986D895B1975F8CA9BEF5B1CC1C49091B50E8C4465CC773E21014EEB79

MD5 : 76FEE36576EE5FE8F5BAD1471CF7EF0E

CRC32 : F1DEBF97

2、ICBC China_Payment MT103 Copy_Pdf.exe

SHA256 : 64086858AD183B4F58CDEF24D0F2FEAF86754058B6CE41EED180CE67E8A0BBE2

MD5 : 0B14754A7BE0329640A9851868B74559

CRC32 : 5C656FDD

3、url

bmn.lpmpbanten.id

mail.elparque.com.uy

