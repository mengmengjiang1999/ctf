## 背景介绍

近日，奇安信病毒响应中心在日常的样本运营过程中，通过盘古平台发现了一款仿冒奥地利“Willhaben”软件的钓鱼木马APP。该钓鱼木马通过仿冒成“Willhaben”APP，窃取用户个人信息，并向用户发送含有钓鱼链接的短信。

Willhaben是奥地利最大的用于个人之间买卖的市场应用程序。其中有超过400万辆二手车、房地产、工作和最大的分类市场，Willhaben在Google
Play拥有将近8万的下载量。目前Willhaben已就此次钓鱼木马事件，在其官网发出了相关的预警信息。

Willhaben Google Play下载信息：

![图片.png](https://image.3001.net/images/20191203/1575356741_5de6094518e1a.png!small)

Willhaben 发出的预警信息：

![图片.png](https://image.3001.net/images/20191203/1575356747_5de6094b37f27.png!small)

盘古平台捕获的样本信息：

![图片.png](https://image.3001.net/images/20191203/1575356751_5de6094fb53ba.png!small)

## 样本分析

### 样本信息

文件名称  |  Willhaben  
---|---  
软件名称  |  Willhaben  
软件包名  |  com.resterent  
MD5  |  AC7C59F2AA0D684A7857B3E305CBB714  
安装图标  |
![图片.png](https://image.3001.net/images/20191203/1575356758_5de609564078b.png!small)  
  
### 样本行为描述

此次发现的通过仿冒“Willhaben”的恶意程序，其主要目是进行钓鱼。恶意程序运行后会诱骗用户激活设备管理器，并可通过远控指令隐藏APP图标，从而达到保护自身；其会通过服务端下发远控指令，包括向服务器发送用户手机状态、发送用户手机号码、发送用户手机短信、发送用户已安装的APP信息、实时对用户手机进行监控等。攻击者会根据获取到的信息，向指定用户发送钓鱼短信，诱骗用户打开钓鱼页面并预付款，从而达到诱骗钱财的目的。

钓鱼短信示例：

“NAME,Vorauszahlung bezahlt www-willhaben-org/….”

![图片.png](https://image.3001.net/images/20191203/1575356771_5de60963b5db1.png!small)

预付款钓鱼页面：

![图片.png](https://image.3001.net/images/20191203/1575356777_5de6096998aef.png!small)

目前该钓鱼页面已无法正常显示：

![图片.png](https://image.3001.net/images/20191203/1575356787_5de60973f2688.png!small)

### 详细代码分析

激活设备管理器：

![图片.png](https://image.3001.net/images/20191203/1575356794_5de6097a314ea.png!small)

通过服务端下发远控指令，指令及其含义：

服务端：<http://lkalipso1.com/3lfk3jGj/>

![图片.png](https://image.3001.net/images/20191203/1575356886_5de609d68e8bf.png!small)

主要代码片段：

![图片.png](https://image.3001.net/images/20191203/1575356937_5de60a09680df.png!small)

![图片.png](https://image.3001.net/images/20191203/1575356942_5de60a0e728c5.png!small)![图片.png](https://image.3001.net/images/20191203/1575356946_5de60a12b4fcb.png!small)

So文件中主要功能代码：

![图片.png](https://image.3001.net/images/20191203/1575356968_5de60a28135ee.png!small)![图片.png](https://image.3001.net/images/20191203/1575356972_5de60a2c95834.png!small)

## 仿冒美团钓鱼事件回顾

11月6日，奇安信病毒响应中心收到用户举报，美团、饿了么出现大规模短信钓鱼事件，且收到短信的人群非常集中。攻击者通过短信发送的方式，进行了大规模钓鱼攻击。奇安信病毒响应中心第一时间进行了分析，并将结果交给了警方。

### 事件还原

11月6日当天，有大量用户收到自称是饿了么、美团的短信，要求用户点击短信链接，进行相关进一步操作。

短信内容如下：

![图片.png](https://image.3001.net/images/20191203/1575356982_5de60a3604b9f.png!small)

当用户点击链接后，会弹出输入电话号码、***的链接：

![图片.png](https://image.3001.net/images/20191203/1575356989_5de60a3d38ba9.png!small)

输入后会进一步要求用户填写***相关信息：

![图片.png](https://image.3001.net/images/20191203/1575356994_5de60a429d2f0.png!small)

当用户提交完信息后会停留在此页面：

![图片.png](https://image.3001.net/images/20191203/1575356999_5de60a472aa73.png!small)

当用户手机停留在此页面时，攻击者会通过用户提供的***账号、密码进行转账操作，并诱骗用户填写银行二次确认短信，从而完成转账操作。

攻击者后台操作页面：

![图片.png](https://image.3001.net/images/20191203/1575357007_5de60a4f3f621.png!small)

用户信息上传数据包：

![图片.png](https://image.3001.net/images/20191203/1575357012_5de60a5402c90.png!small)![图片.png](https://image.3001.net/images/20191203/1575357016_5de60a58ef76a.png!small)

被上传的用户数据：

![图片.png](https://image.3001.net/images/20191203/1575357022_5de60a5ece248.png!small)

## 总结

随着移动端APP所涉及领域的不断扩大，在方便大众的同时，也带来了更多的安全隐患。加之近年来各种购物节类似双11、双12、618、黑五的规模不断扩大，购物付款、退款的安全隐患也会随之增加。奇安信病毒响应中心提醒广大用户，预防短信类钓鱼木马的最好方式，就是用户不要随意点击，来自不明号码，短信中的不明链接。如果用户收到了类似的不明短信，请及时与相关公司的客服进行联系，以确保短信信息的真实性。

## IOC

AC7C59F2AA0D684A7857B3E305CBB714

57DF2C8EAC6AAA2D7EBB94F4357A353F

<http://lkalipso1.com/3lfk3jGj/>

<http://karambga3j.net/3lfk3jGj/>

<http://lkrishtifaa.com/3lfk3jGj/>

<http://lkrishtifaa.org/3lfk3jGj/>

