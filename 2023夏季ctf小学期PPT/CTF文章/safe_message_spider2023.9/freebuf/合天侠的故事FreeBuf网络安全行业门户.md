本文原创作者：佛怒

原创投稿详情： _重金悬赏 | 合天原创投稿等你_

遥远的网安大陆，宗门林立，群雄争锋！

在一个偏僻的小山村里，有一位叫做合天侠的少年，正准备离开山村，入世闯荡。但现在他正面临着父亲给自己设置八道关卡，成功就即可外出闯荡，否则只能做一个普通人。

01

 **第一关**

进入之后看到提示内容和输入框

  
![图片.png](https://image.3001.net/images/20180612/15287951695535.png!small)  

常规思路，查看源代码

发现加载了一个JS(js.js)文件，在JS文件中找到密码(Hello World)

  
![640.jpg](https://image.3001.net/images/20180612/15287953366718.jpg!small)  

输入密码，进入下一关。

  
![640.png](https://image.3001.net/images/20180612/15287953449021.png!small)  

02

 **第二关**

  
![640.jpg](https://image.3001.net/images/20180612/15287953624919.jpg!small)  

提示我们用IE6.5访问，修改浏览器UA即可，此处我们直接用浏览器的插件修改(Http Header
Live)将Mozilla/5.0修改为IE/6.5，点击Send

![640.jpg](https://image.3001.net/images/20180612/15287953722039.jpg!small)  

页面变化为

  
![640.jpg](https://image.3001.net/images/20180612/15287953805644.jpg!small)  

更改的方法相同，最终结果

  
![640.jpg](https://image.3001.net/images/20180612/15287953935204.jpg!small)  

03

 **第三关**

考验手速？随便输点什么试试

  
![640.jpg](https://image.3001.net/images/20180612/1528795402983.jpg!small)  

提示时间差，先用计算器算出结果 (也可用Http Header Live 修改数字) 用HackBar查看提交的数据，将后面的时间改为前面的时间减1s，提交

  
![640.jpg](https://image.3001.net/images/20180612/15287954106090.jpg!small)![640.jpg](https://image.3001.net/images/20180612/15287954218748.jpg!small)  

04

 **第四关**

  
![640.jpg](https://image.3001.net/images/20180612/15287954317014.jpg!small)  

下载解压得到Email.txt，打开分析

  
![640.jpg](https://image.3001.net/images/20180612/15287954403087.jpg!small)  

邮件采用base64加密，是为了更好的在网络中传输，下图是图片转的base64，我们解密看看,格式

<img src="data:image/png;base64,此处为base64内容 " />

![640.jpg](https://image.3001.net/images/20180612/15287954521531.jpg!small)  

![640.jpg](https://image.3001.net/images/20180612/15287954581115.jpg!small)

没有我们过关需要的KEY，继续找，最终找到KEY

  
![640.png](https://image.3001.net/images/20180612/15287954682313.png!small)  

05

 **第五关**

  
![640.jpg](https://image.3001.net/images/20180612/15287954773169.jpg!small)  

下载图片，txt方式打开，没有我们需要的KEY，但我们发现文件的后缀是不对的。

  
![640.png](https://image.3001.net/images/20180612/15287954842321.png!small)  

后缀改为BMP后图片还是看不清。我们继续用Winhex打开分析

经过百度，我们知道，BMP文件的信息头，宽(19-22)，高(23-26)

  
![640.jpg](https://image.3001.net/images/20180612/15287954929084.jpg!small)  

所以此文件的文件头不正确，我们把D5改成FF，得到KEY

  
![640.jpg](https://image.3001.net/images/20180612/15287955044354.jpg!small)![640.png](https://image.3001.net/images/20180612/15287955107868.png!small)  

06

 **第六关**

  
![640.jpg](https://image.3001.net/images/20180612/15287955173015.jpg!small)  

提示上传gif图片，随便找一个gif，成功，但没有KEY，查看源码，需要上传php文件

  
![640.jpg](https://image.3001.net/images/20180612/15287955253802.jpg!small)  

但上传php文件提示只能上传gif图片emm

  
![640.jpg](https://image.3001.net/images/20180612/15287955343368.jpg!small)  

一个很简单的上传绕过，这里用Burp演示，配置好代理，打开拦截。

把此处1.gif改为php发出去即可

  
![640.jpg](https://image.3001.net/images/20180612/15287955424007.jpg!small)![640.png](https://image.3001.net/images/20180612/15287955497335.png!small)  

07

第七关

  
![640.jpg](https://image.3001.net/images/20180612/15287955572251.jpg!small)  

解压之后只有一个key.txt，根据提示，搜索得到如下信息

  
![640.jpg](https://image.3001.net/images/20180612/15287955711711.jpg!small)  

但是我们发现找不到这个文件，说明它改名字了

  
![640.jpg](https://image.3001.net/images/20180612/15287955805653.jpg!small)  

查看文件名的方法有很多，这里介绍简单的一种，Winhex查看WinRAR，如图

  
![640.jpg](https://image.3001.net/images/20180612/1528795588922.jpg!small)  

找到文件名，然后就得到KEY了

  
![640.jpg](https://image.3001.net/images/20180612/15287955951727.jpg!small)  

08

 **第八关**

历经千辛万苦终于来到最后一关，入世大门就在眼前

![640.jpg](https://image.3001.net/images/20180612/15287956037217.jpg!small)  

下载解压软件，随便输入，提示

  
![640.jpg](https://image.3001.net/images/20180612/15287956106391.jpg!small)  

看来需要破解软件了，先查壳

  
![640.png](https://image.3001.net/images/20180612/15287956167413.png!small)  

无壳，VC++6.0编写，丢OD里去

根据特征词找判断，跟进去

  
![640.jpg](https://image.3001.net/images/20180612/15287956248208.jpg!small)  

此处有一个判断，但中间只有一个CALL，而且没有大的跳转，不是我们需要的，继续找

  
![640.jpg](https://image.3001.net/images/20180612/15287956333827.jpg!small)  

此处有一个判断，而且中间有很大的跳转，我们把je(等于)改为jne(不等于)试试，运行程序，得到KEY。

  
![640.jpg](https://image.3001.net/images/20180612/15287956434979.jpg!small)  

合天侠通过了关卡，来到父亲身边，父亲对合天侠说：“孩子，外出闯荡，为父送你两本书。天书可以帮你成就事业，家书可以保你性命。孩子，保重！”

合天侠转身，踏上了艰难而又充满乐趣的网安之路！

  
  

（注：本文属于合天原创投稿奖励，未经允许，禁止转载！）  

