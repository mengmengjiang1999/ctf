本文原创作者：EEE

原创投稿详情：[重金悬赏 |
合天原创投稿等你](https://link.zhihu.com/?target=http%3A//mp.weixin.qq.com/s%3F__biz%3DMjM5MTYxNjQxOA%3D%3D%26mid%3D2652846451%26idx%3D2%26sn%3D2456db03a3a77d5ff8064449c34ffceb%26chksm%3Dbd5945be8a2ecca808f62ee5726223c16cab235d216c891df2dd114b8539001390dbad37bccd%26scene%3D21%23wechat_redirect)

* * *

## 一、 What Is HID ?

HID 全称为 Human Interface Device
直译为人类接口设备，也被称为人体学输入设备，是指与人类直接交互的计算机设备，而pc端上的”HID”一般指的是USB-HID标准，更多指微软在USB委员会上提议创建的一个人体学输入设备工作组。

说了这么多，其实就是设备管理器里的…这个

![image.png](https://image.3001.net/images/20180605/15281787765465.png!small)![image.png](https://image.3001.net/images/20180605/1528178926692.png!small)  

1.1HID标准的概念之前，设备往往要匹配鼠标和键盘,更换新的设备时候，就需要重载所有协议和设备，极其繁琐

类似于TCP/IP协议族一样，在标准化协议发布之前，设备之间的通讯由开发商单方面的协议主导，不同品牌的设备从而因为协议不同，而无法通信。

1.2而HID标准概念之后，所有HID定义的设备驱动程序提供可包含任意数量数据类型和格式的自我描述包。计算机上的单个HID驱动程序就可以解析数据和实现数据[I/O](https://link.zhihu.com/?target=https%3A//zh.wikipedia.org/wiki/I/O%2522%2520%255Co%2520%2522I/O)与应用程序功能的动态关联。

1.3可以说：HID标准的诞生让接口类型，功能更加丰富，多样化，同时也加快了设备的创新与发展。

## 二、 What Is HID attack?

HID attack 通过插入带有攻击向量的USB设备等方式，恶意代码直接就被加载执行，攻击操作也就瞬时发生。此类方式属于物理层面攻击。

相对来说，攻击者控制了用户的键盘，则就可以说控制了对方主机的权限。

攻击者可以在一个芯片中，写入编程进去的恶意代码，诱导用户,或其他方式插入主机中，即可完成整个攻击操作。

  

 **2.1那么造成HID攻击的原因到底是什么**

HID设备类协议缺陷

在聊HID设备标识符之前，先说说鼠标和键盘。早期的鼠标键盘，如果网龄久一些的话，都知道，是那种PS/2的接口。

![image.png](https://image.3001.net/images/20180605/15281789464683.png!small)  

在今天，大部分的鼠标和键盘都用USB来代替，ps/2的接口已经非常非常少见了。

既然，USB插得有可能是移动储存设备，也有可能是类似键盘鼠标的输入设备，那么计算机是如何分辨的呢？

答案就是 HID协议中的定义的HID设备标识符。

就我们人类而言，键盘之所以是键盘，是因为能打字，

鼠标之所以能是鼠标，是因为能控制光标的移动

U盘之所以是U盘，是因为他能长得像U盘，能传入传输文件。

但是计算机不是人，他只认识0和1，Device Class Definition for Human Interface
Devices是一个公开的国际标准，用于规定HID设备的类型。当任何一个HID设备在接入电脑时，操作系统就首先会读取其设备标识符，

 **你如果具备U盘的标识，那我就给你挂载一个盘符。**

 **你如果具备键盘的标识符，我就接受你给我输入的信息。**

原则上HID 是一出厂，就被设定好了的，出厂了就不能再更改了。

老生常谈的一句话“ **互联网本身是安全的，自从有了安全的人，互联网就变得不安全了** 。”

但是HID规范和协议是公开，通过自定义HID标识，让计算机模拟了键盘的输入。

则达到了我们所说的HID攻击。

## 三、 发动 HID攻击 需要什么?

按理说这种物理攻击，应该是玩物联网的兄弟们鼓捣的东西，那么就自然少不了单片机等硬件的支持。

如黑客想发动一次 HID 攻击的话，有很多种硬件的选择，

以下笔者只是简单的举三个例子

 **3.1digispark单片机：**

![image.png](https://image.3001.net/images/20180605/15281789685019.png!small)

![image.png](https://image.3001.net/images/20180605/15281790004626.png!small)  

自带 8k 的闪存，除去（bootloader占用2K，用户可编程部分6K）

  

 **3.2CJMCU-Beetle**

![image.png](https://image.3001.net/images/20180605/15281790175540.png!small)![image.png](https://image.3001.net/images/20180605/15281790239884.png!small)  

均价 32RMB左右，32KB 闪存（4kb bootloader 占用）

 **  
**

 **3.3.商业版定制BadUSB---小黄鸭**

![image.png](https://image.3001.net/images/20180605/15281790378011.png!small)  

价格不菲，40美刀是我等穷逼消费不起的。 按照汇率野爹小几百块钱呢。

![image.png](https://image.3001.net/images/20180605/15281790454684.png!small)  

可以插入一个12MB的SD卡（相对于 淘宝9.9的内个，就储存部分就扩展了几百倍了。）长得也更像U盘啊。

对比图

![image.png](https://image.3001.net/images/20180605/15281790543994.png!small)

## 四、 如何对单片机写简单的模拟键盘程序。

提醒一下各位，所有的单片机都是可以跨平台攻击的，前提是，你准备的payload是这个平台的payload的 不同平台的命令指示符的指令是不一样的。

你如果去攻击win的程序去插入了linux的服务器上，那也毫无意义。

首先去官网下载编译器

[https://www.arduino.cc/en/Main/Software](https://link.zhihu.com/?target=https%3A//www.arduino.cc/en/Main/Software)

![image.png](https://image.3001.net/images/20180605/15281790668578.png!small)  

打开编译器：

![image.png](https://image.3001.net/images/20180605/15281790757703.png!small)  

初始化界面:

![image.png](https://image.3001.net/images/20180605/15281790838945.png!small)  

初始化代码部分

    
    
    void setup() {
      // put your setup code here, to run once:
    }
    void loop() {
      // put your main code here, to run repeatedly:
    }
    

Arduino 提供了以下键盘函数

#include<Keyboard.h> //包含键盘模块的头文件

Keyboard.begin(); //开启键盘通信

Keyboard.press(); //按下某个键

Keyboard.release(); //释放某个键

Keyboard.println(); /*输入某些内容 和一些网上的解释不同 网上解释是输入内容并且能回车，而我测试的时候并不能回车 可能和版本有关
不要不要担心有办法回车*/

Keyboard.end(); //结束键盘通信

以下是单片机模拟打开 win+R echo helloworld

![image.png](https://image.3001.net/images/20180605/15281790965648.png!small)  

(更高阶的操作，本文不再探究，互联网资源丰富  
还请小伙伴利用自己的搜索引擎去探索吧~)

写完代码之后，进行编译

![image.png](https://image.3001.net/images/20180605/15281791389577.png!small)  

然后上传（如果代码写的没有问题的话）

![image.png](https://image.3001.net/images/20180605/1528179148725.png!small)  

注意：digispark
与其他arduino不太一样。以前[DigisparkArduino](https://link.zhihu.com/?target=http%3A//microchip.eefocus.com/tag/term/DigisparkArduino/m/article%2522%2520%255Ct%2520%2522_blank)在SourceForge上提供了专用版的Arduino
IDE，但是很久没有更新，而且支持的板子较少，不方便。下面会介绍

如果你是DigisparArduino板子，就需要设置一下了。

然后运行Arduino，打开File菜单下的Preferences，在Additional Boards manager中输入下面网址：

  1. [http://digistump.com/package_digistump_index.json](https://link.zhihu.com/?target=http%3A//digistump.com/package_digistump_index.json)

![image.png](https://image.3001.net/images/20180605/15281791568318.png!small)  

去工具里面的 打开开发板管理器,安装一下 等5分钟。

![image.png](https://image.3001.net/images/20180605/15281791657815.png!small)  

最后你选择 工具开发板 digispark (default)

写完程序后。

你就可以去你身边小伙伴的电脑上 插插插了~

## 五、 一种新型的BadUSB（wifi版）

近两年的 badusb社区又有geek鼓捣出新玩意，比如说这样的：

![image.png](https://image.3001.net/images/20180605/15281791748471.png!small)

![image.png](https://image.3001.net/images/20180605/15281791815488.png!small)

  

将wifi模块焊上去

增加了wifi模块的badusb，可以通过wifi连接的形式，将代码烧进内存。

在实际的攻击场景则更容易按照需求对代码进行测试,也为攻击方式增加更多的可能性。

  

所需要的设备

  * ESP8266 Wi-Fi芯片  
我推荐使用ESP-12。它使用广泛，价格便宜，体积小巧，拥有4MB的闪存。  
但是，如果你是初学者，你应该从NodeMCU或者Wemos d1 mini等开发者板开始。

  *   

  * ATmega32u4  
Arduino Micro和Arduino Leonardo使用ATmega32u4作为例子。您也可以购买Arduino Pro
Micro或其他使用ATmega32u4的廉价Arduino克隆。我将使用[ATmega32u4
CJMCU甲虫](https://link.zhihu.com/?target=https%3A//www.google.de/search%3Fq%3DCjmcu-beetle%26tbm%3Disch)。

  *   

  * （一个3.3V稳压器）  
我把它放在括号内，因为如果你的ATMega32u4板不提供3.3V，你只需要这个。ESP8266仅适用于3.3V，因此根据您的电路板，您可能需要一个稳压器，以便从5V获得3.3V电压。

  *   

参考接线图：

![image.png](https://image.3001.net/images/20180605/1528179206259.png!small)  

引脚连接图:

![image.png](https://image.3001.net/images/20180605/15281792152235.png!small)  

具体步骤可以参考github地址:
[https://github.com/spacehuhn/wifi_ducky](https://link.zhihu.com/?target=https%3A//github.com/spacehuhn/wifi_ducky)

![image.png](https://image.3001.net/images/20180605/15281792235096.png!small)  

打开 NodeMCU Flasher 写入软件

刷入bin 固件
[https://github.com/spacehuhn/wifi_ducky/releases](https://link.zhihu.com/?target=https%3A//github.com/spacehuhn/wifi_ducky/releases%2522%2520%255Ct%2520%2522_blank)

中文版固件:

[http://files.cnblogs.com/files/k1two2/esp8266_wifi_duck_4mb_zh.zip](https://link.zhihu.com/?target=http%3A//files.cnblogs.com/files/k1two2/esp8266_wifi_duck_4mb_zh.zip)

将的Wi-Fi Ducky插入并连接到新的Wi-Fi

默认网络WiFi Duck。

密码是quackquack。

输入 [http://192.168.4.1](https://link.zhihu.com/?target=http%3A//192.168.4.1)
进入管理地址

效果图

![image.png](https://image.3001.net/images/20180605/15281792514407.png!small)![image.png](https://image.3001.net/images/20180605/15281792572669.png!small)  

（发挥你的想象力，就可以让板子变得更强大）。

## 六、最危险的U盘—USB killer

USB kill用于测试USB端口防止电源浪涌攻击。最新发布的USB Kill 3.0可以测试，设备是否有抵御这种攻击的能力。

（当然了，抵御不了这种攻击的设备，基本都会冒烟什么的）

根据其最早开发团队做的统计，约95%的设备，根据其发布在YouTube的视频，包括三星GalaxyS9+在内的手机 也均无法抵御USB 的攻击。

![image.png](https://image.3001.net/images/20180605/15281792678725.png!small)  

那么他的攻击方式到底是什么呢?

![image.png](https://image.3001.net/images/20180605/15281792764363.png!small)![image.png](https://image.3001.net/images/20180605/15281792825315.png!small)

  

虽然外观U盘长得差不多，但是其内部并不是真正的U盘结构，而换成了电容。它从其电容连接的元件的USB电源中收集功率，直到其达到高电压，然后再将高电压再反向放电到USB接口。

就好比，这东西就像个电荷储存器，来收集USB接口供给他的能量，等达到足够高压的时候，再反向输出给接口。

据他们团队所说，苹果是唯一一家，可以防御这种攻击方法的设备。

攻击效果图(三张 gif)

![1527228927414.gif](https://image.3001.net/images/20180605/15281794013985.gif!small)![1527228935759.gif](https://image.3001.net/images/20180605/1528179401892.gif!small)![1527228941555.gif](https://image.3001.net/images/20180605/15281794014395.gif!small)  

## 七、 思考

U盘作为人们常见的移动存储设备，简单，方便，便携的特别，使人们经常会拿U盘来拷贝资料等等。
同时也吸引了一批对USB接口做手脚的人，HID安全同样也是信息安全中不可或缺的一部分分支。

如果黑客要对于目标单位进行定向投放。U盘上再写个什么“重要资料”“岛国优秀电影赏析”什么的。肯定会有好奇的人拿过来插一插，学习学习的吧。

正是可以利用人们的猎奇心理，黑客们也就达到了目的。

## 八、声明

本文介绍的关于HID攻击的几种方法,只是用于学习信息安全所使用，涉及到的攻击行为只是希望让大家提高安全意识。若读者因此做出危害信息安全的行为后果自负，与合天智汇以及原作者无关，特此声明

（注：本文属合天智汇原创奖励文章，未经允许，禁止转载！）

