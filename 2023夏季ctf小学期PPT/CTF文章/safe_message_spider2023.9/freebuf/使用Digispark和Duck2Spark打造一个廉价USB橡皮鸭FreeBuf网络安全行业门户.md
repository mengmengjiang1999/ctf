**如今市面上出现了许多优秀的硬件黑客工具，但缺点是这些工具的价格往往非常的高昂。因此，许多黑客更愿意自己动手打造更为廉价的专属版本。本文我将教大家使用[Digispark](https://bit.ly/2N6oAkh)（一款类似于Arduino
Uno基于Attiny85的微控制器[开发板](https://bit.ly/2N6oAkh)，相比之下它更便宜小巧。）和Duck2Spark，花3美元的价格打造一个廉价的USB橡皮鸭。廉价硬件除了价格上的优势外，还体现在它的安全性上。由于大部分这些硬件都是一次性的，因此它们也几乎不可能被追踪到。**

 **![1_Iv7e7RJ9TK8AlJ-oGxouWg.png](https://image.3001.net/images/20180923/1537663827_5ba6e353a07d8.png!small)**

USB橡皮鸭是一款伪装成U盘的击键注入工具。插入电脑的USB接口后计算机就会将其识别为常规键盘，并以每分钟超过1000个字的速度自动接受其预编程的击键有效载荷。只需短短几秒的物理访问，即可在目标计算机上轻松的部署一些先进的渗透测试攻击或IT自动化任务。此外，Rubber
Ducky还有一些恶搞功能，例如快速更改同事工作站壁纸的脚本等。虽说功能强大，但其价格方面并无优势。目前官方的价格为45美金再加上运费，算起来并不便宜。

![1_I9_HZriwF7C3o-BRpjm1mg.jpeg](https://image.3001.net/images/20180923/1537663838_5ba6e35ed44ba.jpeg!small)

## 第1步：设置Digispark开发环境

在开始使用板子之前，我们必须先安装Arduino IDE。之后，我们还需要下载该板的兼容包，操作非常简单：

<https://www.arduino.cc/en/main/software>  

![1_cIvhX1n8AbwuAzILFsqonQ.png](https://image.3001.net/images/20180923/1537664098_5ba6e462a2b0c.png!small)

安装完成后，打开Arduino IDE应用程序，依次选择 **File** -> **Preferences** ，并在字段名为“Additional
Boards Manager URL”的输入框中，输入以下URL。

    
    
    http://digistump.com/package_digistump_index.json

![1_QWdGarEESeDbCD489rAvtg.jpeg](https://image.3001.net/images/20180923/1537664125_5ba6e47db92c4.jpeg!small)

打开 Arduino IDE - — Preferences **Tools** -> **Board** -> **Boards Manager**
，从下拉菜单中选择“Contributed”，选择 **Digistump AVR Boards** 包并安装。

现在，我们需要安装Digispark Bootloader驱动。

<https://github.com/digistump/DigistumpArduino/releases/download/1.6.7/Digistump.Drivers.zip>

通常，驱动程序安装过程会出现一些问题。因此，请确保驱动程序的正确安装。

![1_5W9j8XXghzX0h7Z0CKD5SQ.jpeg](https://image.3001.net/images/20180923/1537664158_5ba6e49e96308.jpeg!small)

最后，打开 **Tools** -> **Board** ，然后选择 **Digispark (Default — 16.5mhz)**
并将其设置为默认值。

## 第2步：克隆Rubber Ducky脚本

Rubber
Ducky使用简单的脚本语言来创建payloads。而对于Digispark来说，就要复杂许多。我们需要使用Digikeyboard.h和Arduino
IDE编写自己的payloads。在网上也能找到[一些可用于Digispark
ATTiny85的脚本](https://github.com/PlatyPew/Digispark-Duckduino)，但并不能满足我们日常的任务需求。

这里，首先我要感谢我的好友MaMe82 ([Marcus Mengs](https://twitter.com/mame82))
，他创建的duck2spark项目，可将Rubber Ducky脚本转化到Digispark上使用：

<https://github.com/mame82/duck2spark>

Duck2spark的一个很非常棒的功能是，支持非美语键盘布局。该功能主要是借助支持多种键盘布局的DuckEncoder实现的。

Duck2spark使用也非常的简单。以下是一个经典的hello world示例：

    
    
    Generate a DuckyScript test.duck you want to use as output:
    echo "STRING Hello World" > test.duck
    Compile the script using DuckEncoder with your keyboard layout (de in example) or use my python port:
    java -jar encoder.jar -i test.duck -o raw.bin -l de
    Use duck2spark.py to convert into Arduino Sketch (options for single run, 2 seconds startup delay):
    duck2spark.py -i raw.bin -l 1 -f 2000 -o sketch.ino
    After setting up the Arduino IDE load the example "DigisparkKeyboard" and replace the Sketch source by the one saved to sketch.ino 

单击Sketch -> Upload或单击左上角的Upload按钮。打开记事本。再次插入Digispark USB，我们将看到屏幕中“Hello
World”自动输入的过程。

你也可以创建其它用途的Rubber Ducky
Payloads，这主要取决于你的目的和意图。例如你可以创建无线网关联，下载和执行payloads，反向shell等。在做渗透测试时，我们甚至还可以使用Meterpreter，Empire，Unicorn等powershell
payloads：

<https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Payloads>

最后提示大家，可以使用一些[热缩管](https://bit.ly/2CQfLpP)来为你的Digispark-Ducky提供电绝缘，机械保护，密封及隐藏。

![1_rLWVOIHX9L2vx3_7N9Ro3w.png](https://image.3001.net/images/20180923/1537664180_5ba6e4b440c6b.png!small)

 ***参考来源：[hackernoon](https://hackernoon.com/low-cost-usb-rubber-ducky-pen-test-tool-for-3-using-digispark-and-duck2spark-5d59afc1910)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

