## 一、大概背景

早上收到一封邮件，显示为：中国银行的银行转账通知。 (MT-103 雨燕)，如下图所示：

![1654597623_629f27f72febf51f7a506.png!small?1654597622649](https://image.3001.net/images/20220607/1654597623_629f27f72febf51f7a506.png!small?1654597622649)

直接双击打开附件，ISO文件加载后，显示内容为一个伪造成PDF文件的EXE可执行文件，如下图所示：

![1654597641_629f28090cf07cd5e9a2f.png!small?1654597640304](https://image.3001.net/images/20220607/1654597641_629f28090cf07cd5e9a2f.png!small?1654597640304)

该exe文件除了将图标伪造成PDF外，还伪造了EXE文件属性为：Firefox，如下图所示：

![1654597656_629f2818e1bc3307cf920.png!small?1654597656344](https://image.3001.net/images/20220607/1654597656_629f2818e1bc3307cf920.png!small?1654597656344)

更详细信息如下：

![1654597671_629f28273ff65ac0eb64b.png!small?1654597670720](https://image.3001.net/images/20220607/1654597671_629f28273ff65ac0eb64b.png!small?1654597670720)

攻击手法和形式和前几天收到的雷同，具体可参加：[一封伪冒工商银行的攻击邮件的简要分析 -FreeBuf网络安全行业门户](https://www.freebuf.com/articles/network/332573.html)。

邮件伪造中国银行邮箱：info@boc.cn发送。

实际邮件通过huemul.ffyb.uba.ar发出，ffyb.uba.ar是布宜诺斯艾利斯大学药学和生物化学学院的域名。

![1654597716_629f28540dd7384ef2738.png!small?1654597715780](https://image.3001.net/images/20220607/1654597716_629f28540dd7384ef2738.png!small?1654597715780)

## 二、PE分析情况

Bank of China_Payment_Copy_Xerox Scan_Pdf.exe执行后，首先访问：http:// soprocerto.pt
/new/Vyckdayq_Ardozkwt.bmp, 发送的HTTP报文抓包如下图所示：

![1654597894_629f2906cadf888bd6ce7.png!small?1654597894293](https://image.3001.net/images/20220607/1654597894_629f2906cadf888bd6ce7.png!small?1654597894293)

同样的，该url字符串直接可在EXE静态文件中找到：

![1654597908_629f291475b70f1d2e672.png!small?1654597908169](https://image.3001.net/images/20220607/1654597908_629f291475b70f1d2e672.png!small?1654597908169)

反汇编代码：![1654597921_629f2921314b5fd4da6e8.png!small?1654597920425](https://image.3001.net/images/20220607/1654597921_629f2921314b5fd4da6e8.png!small?1654597920425)

通过上一篇内容的分析，我们看到本次下载的BMP还依然是一个EXE文件的倒序，直接查看下载的数据，拉到底部，可以很容易看出是一个PE头的倒序：

![1654597950_629f293e1c2f0e57e1b40.png!small?1654597949451](https://image.3001.net/images/20220607/1654597950_629f293e1c2f0e57e1b40.png!small?1654597949451)

直接访问：http://soprocerto.pt/new/，则会列出该目录下所有文件，显示为3个图片文件，其实都是EXE文件的倒序，恶意文件的生成时间为：6月5日和6日，如下图所示:

![1654598001_629f29711c369e972a3fb.png!small?1654598000558](https://image.3001.net/images/20220607/1654598001_629f29711c369e972a3fb.png!small?1654598000558)

6月8日再次访问该url，发现多了两个文件，说明攻击者持续在更新攻击样本

![1654653510_62a00246a3ff62afa1b0e.png!small?1654653509612](https://image.3001.net/images/20220608/1654653510_62a00246a3ff62afa1b0e.png!small?1654653509612)

我们来看看反汇编代码，验证一下是否为倒序存放：

首先，调用City类的vipd，用于下载http://soprocerto.pt/new/Vyckdayq_Ardozkwt.bmp

![1654598023_629f2987c1cc1ab64fe8b.png!small?1654598023159](https://image.3001.net/images/20220607/1654598023_629f2987c1cc1ab64fe8b.png!small?1654598023159)

接着，qeat函数调用System.Net.WebClient直接下载：

![1654598057_629f29a935012b58753c9.png!small?1654598056580](https://image.3001.net/images/20220607/1654598057_629f29a935012b58753c9.png!small?1654598056580)

然后，调用Country类的hpai函数，将下载的BMP数据进行倒序操作：

![1654598078_629f29bee30b044255d74.png!small?1654598078225](https://image.3001.net/images/20220607/1654598078_629f29bee30b044255d74.png!small?1654598078225)

转化成代码如下：

![1654598091_629f29cbbd52d92f4954d.png!small?1654598091182](https://image.3001.net/images/20220607/1654598091_629f29cbbd52d92f4954d.png!small?1654598091182)

最后，利用Assembly.Load加载倒序后的PE文件：

![1654598111_629f29df5a1c34318a450.png!small?1654598110637](https://image.3001.net/images/20220607/1654598111_629f29df5a1c34318a450.png!small?1654598110637)

执行后，会在%temp%目录下生成：Mnyxtqwntaqzvqbubhuconfast1.exe

Mnyxtqwntaqzvqbubhuconfast1.exe是一个受害主机信息收集、发送的木马程序，会将受害主机的信息通过SMTP协议发送，连接的SMTP服务器是：mail.pharmadent.com.uy，端口是：587，IP为：170.249.205.194。![1654599258_629f2e5a6b47f936b13ad.png!small?1654599257587](https://image.3001.net/images/20220607/1654599258_629f2e5a6b47f936b13ad.png!small?1654599257587)

具体的SMTP访问数据如下图所示：

![1654599496_629f2f482b0699f06654d.png!small?1654599495418](https://image.3001.net/images/20220607/1654599496_629f2f482b0699f06654d.png!small?1654599495418)

SMTP解析如下：

![1654598233_629f2a59b9f6dfc03ba39.png!small?1654598233575](https://image.3001.net/images/20220607/1654598233_629f2a59b9f6dfc03ba39.png!small?1654598233575)

发送的邮件内容是受害主机的信息（测试机器内容很少），比如主机名、OS系统信息、CPU、内容、IP地址等。

和前一篇文章一样，攻击者最终的接收邮箱地址依然是：[contacto@filtrosdys.com](mailto:contacto@filtrosdys.com)。只不过发送邮箱变成：[gustavoaniano@pharmadent.com.uy](mailto:gustavoaniano@pharmadent.com.uy)，通过SMTP报文获取的账户和密码，可以直接登陆访问[gustavoaniano@pharmadent.com.uy](mailto:gustavoaniano@pharmadent.com.uy)邮箱。

## 三、小结

IOCS：

1、文件

文件名称

|

大小

|

MD5 HASH

|

备注  
  
---|---|---|---  
  
Ktyij_Srfqefve.png

|

940,032

|

a8a6798a4c1c3cb824032230eb088429

|

Exe倒序  
  
Vyckdayq_Ardozkwt.bmp

|

895,488

|

17f1ccb5b199866f68aac90656f4a98d

|

Exe倒序  
  
Emqgfdkel_Ugyidrpi.png

|

896,000

|

18a877a85f2cc421602937b3a7498649

|

Exe倒序  
  
Obppbo_Nkyjgkog.png

|

676,352

|

a5007c2c6750a920b476976968f204e8

|

Exe倒序  
  
Uroyyy_Uvxiesxn.bmp

|

751,616

|

13107b7cd07c910910f7b3ba3c254b2f

|

Exe倒序  
  
Bank of China_Payment_Copy_Xerox Scan_Pdf.exe

|

76,288

|

9d24698102c0f74f296f69776f3b8616

|

伪装成PDF的钓鱼EXE  
  
Mnyxtqwntaqzvqbubhuconfast1.exe

|

213,504

|

40c281ed76a0bfe96418fb5dc0e19f15

|

木马程序  
  
2、URL

最终信息汇聚的邮箱（攻击者拥有）：[contacto@filtrosdys.com](mailto:contacto@filtrosdys.com)

受害主机信息发送邮箱：[gustavoaniano@pharmadent.com.uy](mailto:gustavoaniano@pharmadent.com.uy)：mail.pharmadent.com.uy

下载URL：http:// soprocerto.pt /new/Vyckdayq_Ardozkwt.bmp

