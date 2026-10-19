## 前言

**随着攻防演习行动暂时告一段落，回想起攻防演习中的神操作，如从树莓派+8187L网卡魔改无人机及带着味道的钻下水道操作，再到入职到防守方内网部署后门以及发布的防护文章里搞远控后门工具的种种碟中碟中碟中碟中谍的操作，当然也少不了本次行动中攻击方人员在各个目标附近广撒BadUSB试图使用物理手段拿下目标......**![-w590](https://image.3001.net/images/20190703/1562084447_5d1b845f1191e.jpg!small)

## 0X00 原理及基础知识

### 简介

吾旧友，拾U盘,彼异之，插PC，遂上线。

这个（愚蠢）精彩故事不禁让我萌生学习制作一个BadUSB的想法，为了贴合实际，特地从某宝入手了一个arduino leonardo板，如下图所示。

![image.png](https://image.3001.net/images/20190703/1562084610_5d1b85025a395.png!small)

简单来说，通过硬件直接插入对方电脑，让对方电脑执行代码，达到干扰、控制主机或者窃取信息等目的。

### 基础知识

 **HID攻击**

HID是Human Interface
Device的缩写，由其名称可以了解HID设备是直接与人交互的设备，例如键盘、鼠标与游戏杆等。不过HID设备并不一定要有人机接口，只要符合HID类别规范的设备都是HID设备。一般来讲针对HID的攻击主要集中在键盘鼠标上，因为只要控制了用户键盘，基本上就等于控制了用户的电脑。攻击者会把攻击隐藏在一个正常的鼠标键盘中，当用户将含有攻击向量的鼠标或键盘，插入电脑时，恶意代码会被加载并执行。

 **Teensy**

攻击者在定制攻击设备时，会向USB设备中置入一个攻击芯片，此攻击芯片是一个非常小而且功能完整的单片机开发系统，它的名字叫TEENSY。通过TEENSY你可以模拟出一个键盘和鼠标，当你插入这个定制的USB设备时，电脑会识别为一个键盘，利用设备中的微处理器与存储空间和编程进去的攻击代码，就可以向主机发送控制命令，从而完全控制主机，无论自动播放是否开启，都可以成功。
关于TEENSY，可以参考天融信阿尔法实验室的[《HID攻击之TEENSY实战》](http://blog.topsec.com.cn/ad_lab/hid%E6%94%BB%E5%87%BB%E4%B9%8Bteensy%E5%AE%9E%E6%88%98/)

 **Arduino**

Arduino是一款便捷灵活、方便上手的开源电子原型平台。 它构建于开放原始码simple
I/O介面版，并且具有使用类似Java、C语言的Processing/Wiring开发环境。主要包含两个主要的部分：硬件部分是可以用来做电路连接的Arduino电路板；另外一个则是Arduino
IDE，你的计算机中的程序开发环境。你只要在IDE中编写程序代码，将程序上传到Arduino电路板后，程序便会告诉Arduino电路板要做些什么了。

 **操作流程**

BadUsb插入后，会模拟键盘鼠标对电脑进行操作，通过这些操作打开电脑的命令终端，并执行一条命令，这条命令将从指定网址下载其他代码并于后台静默运行。这些代码功能包括：窃取信息、反弹shell、发送邮件等，从而实现控制目标机或者窃取信息的目的。

## Arduino

### Arduino的特点

 **跨平台**

Arduino 编程平台可以运行在Windows、Mac OS
X、Linux、Android、iOS等各种操作系统上。而其它的大多数控制器一般只能在Windows上进行开发

 **编程灵活性**

经过世界各国创客们的努力，Arduino编程平台已经可以脱离PC机上的传统编程。开发出来了一套更简单实用的图形化编程软件，让Arduino编程学习门槛进一步降低。让技术小白们能更快地创作出自己的智能作品。

 **开放性**

Arduino的硬件原理图、电路图、IDE等软件和核心库都是开源的，开发人员可以在开源协议的范围内任意修改原始设计及相应的代码。

 **发展迅速**

Arduino不仅仅是全球最流行的开源硬件，也是一个优秀的硬件开发平台，更是硬件发展的趋势。Arduino简单的开发方式使得开发者更关注创意与实现，更快的完成自己的项目开发，大大节约了学习的成本，缩短了开发的周期。

### Arduino板子种类

Arduino先后发布了十多个型号的板子，有最基础的型号UNO，有小尺寸的micro，还有引脚数量更多的MEGA板。![image.png](https://image.3001.net/images/20190703/1562084642_5d1b852255cff.png!small)

Arduino
UNO![image.png](https://image.3001.net/images/20190703/1562084661_5d1b85350a43e.png!small)

Arduino
Leonardo![image.png](https://image.3001.net/images/20190703/1562084671_5d1b853f89839.png!small)

Arduino MICRO

![image.png](https://image.3001.net/images/20190703/1562084684_5d1b854c0ac21.png!small)Arduino
MEGA 2560

以上为Arduino板子介绍，下面进入正题。

## 0X01 安装驱动及连接arduino IDE

linux、Mac OS不需要安装驱动，但是Win7需要安装驱动，在win7系统中插入Arduino Leonardo
会显示下图黄色感叹号，安装驱动在arduino IDE 目录下的drivers中。

![image.png](https://image.3001.net/images/20190703/1562084698_5d1b855a12da7.png!small)

arduino IDE官网下载可能会稍慢些，我把IDE放到网盘里，链接如下所示，需要请自取，解压即可使用。

<https://pan.baidu.com/s/1UqLszoiN8OI_vM3QYMlgIA>
密码:8asp![image.png](https://image.3001.net/images/20190703/1562084710_5d1b8566484a0.png!small)

## 0X02 案例操作

将硬件插入电脑后打开arduino
IDE，以下为IDE启动界面![image.png](https://image.3001.net/images/20190703/1562084721_5d1b8571e301d.png!small)

arduino IDE工具栏->开发板->选择“Arduino
Leonardo”![image.png](https://image.3001.net/images/20190703/1562084736_5d1b858027150.png!small)

arduino IDE工具栏->端口->选择“COMX(Arduino
Leonardo)”![image.png](https://image.3001.net/images/20190703/1562084746_5d1b858aba9c7.png!small)

弹计算器案例
从第一个程序来看，不难发现Arduino的程序结构与传统的c程序结构有所不同——Arduino程序中没有main函数。其实并不是Arduino程序中没有main函数，而是main函数的定义隐藏在了Arduino的核心库文件中。在进行Arduino开发中不直接操作main函数，而是使用setup和loop这两个函数。

    
    
    setup（）    Arduino控制器通电或者复位后，就会开始执行Arduino的初始化配置（IO口    串口等）;
    
    loop（）     setup函数执行完毕后，Arduino会接着执行loop（）函数中的程序。而loop函数是一个死循环，其中的程序会不断地重复运行。通常在loop函数中完成程序的主要功能，如驱动各种模块和采集数据等。

![image.png](https://image.3001.net/images/20190703/1562084767_5d1b859f506e0.png!small)

弹计算器代码：

    
    
    #include <Keyboard.h>
    void setup() {
    Keyboard.begin();//开始键盘通讯
    delay(1000);//延时
    Keyboard.press(KEY_LEFT_GUI);//win键
    delay(500);
    Keyboard.press('r');//r键
    delay(500);
    Keyboard.release(KEY_LEFT_GUI);
    Keyboard.release('r');
    Keyboard.press(KEY_CAPS_LOCK);
    Keyboard.release(KEY_CAPS_LOCK);
    delay(500);
    Keyboard.println("CALC");
    Keyboard.press(KEY_RETURN);
    Keyboard.release(KEY_RETURN);
    Keyboard.press(KEY_CAPS_LOCK);
    Keyboard.release(KEY_CAPS_LOCK);
    Keyboard.end();//结束键盘通讯
    }
    
    void loop()//循环
    {
    }
    

注:Upload代码过程中会遇到反复断开问题，原因在Leonardo中被设定为在上传时，软件建立连接让控制器复位，从而免去了我们手动按下复位按钮的操纵。

arduino 弹出计算器：

![image.png](https://image.3001.net/images/20190703/1562084782_5d1b85ae22846.png!small)

再比如说弹个窗：![image.png](https://image.3001.net/images/20190703/1562084791_5d1b85b7a5bd5.png!small)

以及从远程服务端下载恶意文件等等。![image.png](https://image.3001.net/images/20190703/1562084802_5d1b85c2c32bc.png!small)

这篇文章更多的是让自己对Arduino
Leonardo有一个初步的认识，方便以后（还不是因为vps被ban了）更深入的去研究，许多后阶段的利用可以参考各位前辈优秀的文章，例如维克斯大佬的《利用Arduino快速制作Teensy
BadUSB》无论从科普还是实践都给我们详尽的描述了BadUSB制作的相关过程，lpcdma大佬的《使用arduino进行渗透测试》则通过SET与Arduino的结合进行渗透，mrzcpo大佬的
《HID高级攻击姿势：利用PowerShell脚本进行文件窃取》则介绍了获取文件的详细步骤及各种payload免杀，针对内网设备等等~~

## 0X03 BadUsb防御

大家可能发现，我（主要是穷）所使用BadUSB的只适合win10，只有win10能运行。WIN7都是提示安装驱动，针对性的参考国外大牛文章，主要是为了（主要是为了增加文章字数篇幅）学习一下如何针对BadUsb进行防御。[How
to Fix the Critical BadUSB Security Flaw in Less than 10
Minutes](https://heimdalsecurity.com/blog/badusb-exploit-vulnerability-fix/)

### 创建黑名单

1、“ 开始” - > “运行”，然后键入gpedit.msc 以访问“ 本地组策略编辑器”。

2、访问以下内容：计算机配置 > 管理模板 > 系统 > 设备安装 >
设备安装限制![image.png](https://image.3001.net/images/20190703/1562084817_5d1b85d185641.png!small)

3、双击
使用与这些设备设置类匹配的驱动程序阻止设备安装，然后选择启用。![image.png](https://image.3001.net/images/20190703/1562084828_5d1b85dc06d96.png!small)

4、在同一位置，单击“
显示”以通过其GUID创建USB设备的黑名单。![image.png](https://image.3001.net/images/20190703/1562084846_5d1b85ee082ba.png!small)下列表格为常见的几个GUID及对应设备:

4d36e96b-E325-11CE-BFC1-08402BE10318 | 此控制器控制USB键盘的自动安装。  
---|---  
4D36E972-E325-11CE-BFC1-08012BE10318 | 此对应于NIC（网络接口控制器）  
e0cbf06c-cd8b-4647-bb8a-263b45f0f974 | 这个用于蓝牙。  
  
如想查阅GUID号码的更多信息，请参考[GUID号码快速查阅](http://betterexplained.com/articles/the-quick-guide-to-guids/)

### 避免自动USB安装

为保护系统免受BadUSB漏洞影响的另一个方法是禁用自动安装新USB设备，依旧同上面一样的位置。

1、“ 开始” - > “运行”，然后键入gpedit.msc 以访问“ 本地组策略编辑器”。

2、访问以下内容：计算机配置 > 管理模板 > 系统 > 设备安装 >
设备安装限制![image.png](https://image.3001.net/images/20190703/1562084858_5d1b85fabd24c.png!small)

1\. 双击“ 禁止安装可移动设备”并启用它。

![image.png](https://image.3001.net/images/20190703/1562084881_5d1b861128579.png!small)

2\. 双击“ 允许管理员覆盖设备安装限制”策略 并启用它。

![image.png](https://image.3001.net/images/20190703/1562084903_5d1b862795c8c.png!small)

### 禁用非活动USB端口

当然少不了一个比较（骚）硬的策略，那就是禁用那些不活跃的USB端口，从物理上进行隔绝，解决大部分BadUsb问题。

## 0X04 结束语

还是如同之前所示，这篇文章更多的是让自己对Arduino Leonardo有一个初步的认识及为了以后更深入的去学习，初识 Arduino
Leonardo，望各位大佬斧正。

## 0X05 参考及感谢

> <https://www.jianshu.com/p/38cc68ff44ab>
>
> <https://www.cnblogs.com/danpianjicainiao/p/11048576.html#_label1>
>
> <https://heimdalsecurity.com/blog/badusb-exploit-vulnerability-fix/>
>
> <https://blog.csdn.net/cd_xuyue/article/details/50500579>

***本文作者：Parad0x，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

