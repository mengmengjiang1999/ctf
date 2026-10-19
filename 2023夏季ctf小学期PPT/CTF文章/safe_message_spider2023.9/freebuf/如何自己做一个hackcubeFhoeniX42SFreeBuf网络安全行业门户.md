hi，大家好，我是fhoenix42s。一次偶然在freebuf上面看到了人家diy的hackcube无线电安全测试设备（这是360独角兽团队曾经做的），只不过现在解散了。我瞬间就来了兴趣。先来介绍一下，HackCube-Special是一个用于无线电安全研究的便携式硬件平台。它适用于多个射频，可以接收和发送RF信号。而且功能有很多。包括nfc，rf，wifi，模拟键盘（badusb）

不过我知道各位都是研究网安的，可能对硬件了解的不多，没关系，这次我手把手教各位做hackcube

![](https://image.3001.net/images/20220211/1644551726_6205de2e6ec9a278ccfdc.png!small)

电路板：ATmega32u4（用于模拟键盘），esp8266（通过wifi收发信号），CC1101（无线电），e01-ml01sp2(其实这个板子的源码被注释了，但我还是安装了)，nfc，线圈，细网线（因为焊接孔太小了）

Atm和esp8266我选的是5.5负加3.3负降压模块。因为到时候我准备直接usb供电，但是我们正常手机是5.5负，可是hackcube是3.3负，所以说我加了一个3.3的降压模块。我看到网上有人用AMS1117
3.3稳压器，（ESP8266模块上面搭载了一块AMS1117
3.3的稳压设备，这恰好给CC1101供电。直接使用数据线给ESP8266供电，之后上面的稳压管提供3.3V给CC1101，同时还可以给ARDUINO供电。这样ARDUINO的USB口就空了出来，方便使用HID攻击。）而我买的esp8266上面自带了3.3降压，哈哈

![](https://image.3001.net/images/20220211/1644551830_6205de963cc960d12c30b.jpg!small)

这是电路图，我相信各位可能看不太懂

![](https://image.3001.net/images/20220211/1644558674_6205f952b57f0999b73ac.jpg!small)

![](https://image.3001.net/images/20220211/1644558701_6205f96d56626bc327e62.jpg!small)

这个看的懂了吧

烧入教程:https://github.com/UnicornTeam/HackCube-Special/wiki/program，烧录过程没啥好说的，我会把这些全部放到网盘里面，文章最后面

由于自己对于无线电方面的信息安全的热爱。在暑假自己按照DIY了一个hack cube。这个hack
cube我只使用了其中的一部分，很多部分我都没有DIY。主要还是不是很感兴趣。包括里面的NFC，2.Gh我都没有，我只为了研究1Ghz以下的频段。
已经nfc模块，就是那个绿色的，价格实在太贵，我没有买。

HackCUBE是一个开放式的平台，可以集成很多附加功能，现在集成的315MHz/433MHz射频模块，能对车钥匙的无线信号进行分析研究，而自带的WIFI功能也能对能够使用WIFI热点连接的汽车做一些研究工作；内置的HID功能，可以对车载电脑进行攻击，之前blackhat上就有安全研究人员展示过类似的攻击方法。另外还有自带的RFID模块，研究人员能用它分析研究下汽车无钥匙进入和无钥匙启动系统。最后，HackCUBE的接口很多，使用者能用它外接比如USRP、usb转can、逻辑分析仪等设备，用这些设备对汽车进行更多的安全研究工作。这就是我做
HackCube-Special 的初衷。HackCube-Special 是一款低成本，便携式，可工作在多个无线射频频段的无线电安全审计平台。我们会给
HackCube-Special 提供丰富的案例，方便初学者能够更好的了解无线电安全领域。

![](https://image.3001.net/images/20220211/1644558863_6205fa0f18cd522121c05.jpg!small)

![](https://image.3001.net/images/20220211/1644558901_6205fa3533f259034dc1f.jpg!small)![](https://image.3001.net/images/20220211/1644558931_6205fa535169a02356865.jpg!small)![](https://image.3001.net/images/20220211/1644558960_6205fa70d86e15024b129.jpg!small)![](https://image.3001.net/images/20220211/1644558989_6205fa8d0e5d92c223098.jpg!small)![](https://image.3001.net/images/20220211/1644559015_6205faa7d8d508342096a.jpg!small)![](https://image.3001.net/images/20220211/1644559052_6205facce18a49b5bcbcc.jpg!small)一开始我还用家里的可调电源看了一下，（最好用网线焊接。孔特别小）

![](https://image.3001.net/images/20220211/1644559142_6205fb26aeda7b78a90bd.jpg!small)nice！！！！！！，搞一辆车玩玩（滑稽）

然后那些测试啥的就不多说了，我懒得上图

![](https://image.3001.net/images/20220211/1644559270_6205fba6f22fb62fcd754.png!small)![](https://image.3001.net/images/20220211/1644559290_6205fbbae22d246632137.png!small)链接hackcube的wifi，密码hackcube

![](https://image.3001.net/images/20220211/1644559353_6205fbf9476962a780555.png!small)![](https://image.3001.net/images/20220211/1644559362_6205fc029e06249aadfa9.png!small)![](https://image.3001.net/images/20220211/1644559370_6205fc0a6a393c8e4e4ad.png!small)灯的话我忘记挤上去了。。。。。。。。。。。。。。。。。。

![](https://image.3001.net/images/20220211/1644559408_6205fc30028b502067085.png!small)![](https://image.3001.net/images/20220211/1644559416_6205fc38cbd157ac83fe8.png!small)![](https://image.3001.net/images/20220211/1644559453_6205fc5d80d2c8228087b.jpg!small)好了，今天就到这里，我是fhoenix。要是有什么问题可以私信我~~~~再见

hackcube链接：https://pan.baidu.com/s/16_UKDXgClViqyxkT2CCLUg

提取码：fx42

