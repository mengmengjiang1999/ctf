  

> 本次投稿至华盟网，转自公众号 **黑白之道**
>
> 出处：https://www.77169.net/html/272981.html

## 0x00 适用场景

本文所采用技术，仅用来实现自定义功能，适用场景仅为自己两台电脑使用聊天软件互发消息学习研究使用。

* **本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担** 。

## 0x01 需求产生

某聊天软件有已读回执功能，可以通过查看标记，判断对方是否读了你的消息：

![image-20201121090009756](https://image.3001.net/images/20201221/1608516068_5fe001e4b67eeaa9d242b.png!small)

经常出现这样一种情况，联系人发来几条消息，啊T.T，我好想看看他说了什么：

![image-20201121090624586](https://image.3001.net/images/20201221/1608516099_5fe002034f387209963be.png!small)

然后点开看了一下，完蛋，又是借钱的：

![image-20201121090717819](https://image.3001.net/images/20201221/1608516111_5fe0020faf86b869153bf.png!small)

这个辩解苍白无力~

![image-20201121090822922](https://image.3001.net/images/20201221/1608516125_5fe0021d13df5e0efbd38.png!small)

那么伟大的需求就此诞生:如何偷偷看他消息，而不让他知道我已读了？

## 0x02 探究原理

盲猜原理一定是这样：

钉钉客户端查看了消息->客户端发送已读回执到服务器->服务器向消息发送者发送已读状态

那也就是说，只要我们使用的PC客户端不发送已读回执，服务器就永远不知道我们读了该条消息，对放也就不会知道我们看过了。

一开始想看有没有人造过轮子，于是github上翻了翻，但没什么收获。不过在翻的过程中发现了一个有意思的项目：dingtalk-interceptor，但该项目删除了，于是就去网上翻了翻，果然找到了相关的文章，针对的是老版的客户端（3.x），该版本就是Electron包装的一层网页，项目实现原理是通过拦截所有包含updateToRead的请求，从而实现永远未读消息的。

![image-20201121093300682](https://image.3001.net/images/20201221/1608516142_5fe0022eea60d2c7bdbf5.png!small)

因此我们要寻找的突破口就在这个关键字上： **updateToRead**

## 0x03 环境准备

调试环境：

win10 2004 x64

![image-20201121093829881](https://image.3001.net/images/20201221/1608516157_5fe0023d18481f27c3c59.png!small)

x96dbg

![image-20201121093931977](https://image.3001.net/images/20201221/1608516166_5fe002464e569968ce7c8.png!small)

ida7.0

![image-20201121094049593](https://image.3001.net/images/20201221/1608516176_5fe0025088c20eac9e945.png!small)

顺便推荐个工具，可以让ida和od/xdbg/lldb等同步调试：

<https://github.com/bootleg/ret-sync>

聊天软件版本：

![image-20201121123219303](https://image.3001.net/images/20201221/1608516188_5fe0025c55dd1c51ff219.png!small)

## 0x04 开始动手

首先用x64dbg启动主程序，主程序目录在.\main\current\路径下

![image-20201121094818508](https://image.3001.net/images/20201221/1608516202_5fe0026a48f8ce7129fb7.png!small)

通过不断尝试，发现该聊天软件的核心逻辑都在MainFrame.dll中，因此只针对MainFrame.dll进行搜索，关键字：updateToRead。

先定位到模块中:

![image-20201121095242297](https://image.3001.net/images/20201221/1608516213_5fe0027536fe99a10aa91.png!small)

![image-20201121095325721](https://image.3001.net/images/20201221/1608516222_5fe0027ecf1b82a99677f.png!small)

然后在该模块中搜索updateToRead,并全部设置断点

发送两条消息并阅读测试，命中断点如下：

![image-20201121095955354](https://image.3001.net/images/20201221/1608516233_5fe00289a9f11a15f9d6c.png!small)

关闭其他断点，并用另一个号给调试的账号发送消息，并查看：

在第一个断点处，消息依然是未读状态

在第二个断点处，消息依然是未读状态

在第三个断点处，消息依然也是未读状态

在断到第四个断点处，消息依然是未读状态，但放过断点，消息就变成了已读：

![image-20201121100722886](https://image.3001.net/images/20201221/1608516244_5fe00294c53e46bf78dea.png!small)

![image-20201121100744441](https://image.3001.net/images/20201221/1608516254_5fe0029e95d582cd1bac1.png!small)

解决方案有几个：

  1. 破坏原有数据包,使其服务器无法正确更新状态

  2. 在发送前拦截该数据包，使其不发送

  3. 不进入检测消息是否未读状态

此处通过调用该接口“/r/IDLMessageStatus/updateToReadV2”向该接口发送请求，来告诉服务器，消息已经被读了。此处可以直接暴力将接口修改，修改成错误的地址，也可以实现看了消息不显示已读。但直接通过该种方式修改，有两个弊端，

  1. 会向服务器发送一条数据，虽然服务器没能正确处理，但会返回一个异常。

  2. 客户端收到该错误响应后会认为自己与服务器断开连接，会经常认为自己掉线了从而发不出去消息

路线1走不通，因此继续寻找突破点，使用ida反编译该模块，查找该接口：

![image-20201121111055225](https://image.3001.net/images/20201221/1608516265_5fe002a929f3827212b88.png!small)

![image-20201121111135466](https://image.3001.net/images/20201221/1608516275_5fe002b3b3c6431b7b6a3.png!small)

发现该接口是出自sub_1127B210函数：

![image-20201121111154640](https://image.3001.net/images/20201221/1608516284_5fe002bcb1610f8314907.png!small)

进入sub_1127B210内容：

![image-20201121112502977](https://image.3001.net/images/20201221/1608516293_5fe002c5a262224f2dbc8.png!small)

往上跟踪，发现sub_110BA580调用了sub_1127B210

![image-20201121111211634](https://image.3001.net/images/20201221/1608516302_5fe002ce761029c7e8b1a.png!small)

往上跟踪，发现sub_107269E0调用了sub_110BA580

![image-20201121111242018](https://image.3001.net/images/20201221/1608516311_5fe002d752c10c7bafa6e.png!small)sub_107269E0函数内容：

![image-20201121112736580](https://image.3001.net/images/20201221/1608516320_5fe002e0a6c1a7989fae1.png!small)

其中包含多个接口，作用是向服务器发送一个包含消息id的请求包，从而实现消息已读。

此时已经基本了解大概情况，继续用x64dbg调试，在调试过程中发现在执行完sub_107269E0消息并未直接变成已读，而是继续向上层函数继续返回，直到返回了这样一个函数：

![image-20201121114115409](https://image.3001.net/images/20201221/1608516334_5fe002ee87827e314482b.png!small)

伪代码：

    
    
    char __thiscall sub_10C77E70(_BYTE *this)  
    {  
    char *i; // esi  
    char result; // al  
    char v3; // [esp+8h] [ebp-10h]  
    char v4; // [esp+10h] [ebp-8h]  
    ​  
    for ( i = this; ; sub_10C77EC0(i) )  
    {  
    result = i[20];  
    if ( result )  
    break;  
    sub_10C77060(i, (int)&v3);  
    if ( v3 )  
    sub_10C785D0(i, &v4);  
    else  
    sub_10C77210(i);  
    }  
    return result;  
    }

该函数sub_10C77E70在if ( v3 )处存在两个分支，一个分支调用sub_10C785D0(i,
&v4)，另一个分支即已读分支sub_10C77210(i)，也就是我们的call所调用的函数。因此，v3是一个关键判断点

v3所对应汇编代码为：jz short loc_10C77EAC

偏移为：C77298

![image-20201121114606117](https://image.3001.net/images/20201221/1608516347_5fe002fbc94c09cf7a3e0.png!small)

在C77298上下断点，通过修改寄存器zf标志位，使其进入sub_10C785D0(i, &v4)

![image-20201121115711537](https://image.3001.net/images/20201221/1608516358_5fe003062e83aaa675215.png!small)

![image-20201121115715873](https://image.3001.net/images/20201221/1608516370_5fe00312381b9db4224fc.png!small)

修改后发现，后续发送的消息均不显示已读，且不会再进入该判断，因此只要让v3永远=True,即可永不进入sub_10C77210(i)分支，即修改该处条件跳转为jmp

![image-20201121115920990](https://image.3001.net/images/20201221/1608516378_5fe0031af385529ccfa80.png!small)

![image-20201121115928781](https://image.3001.net/images/20201221/1608516388_5fe003247b208ff3084ce.png!small)

修改后Patch到dll上即可。

特征码：C0 75 33 8D 45 F0 8B CE 50 E8 CE F1 FF FF 80 7D F0 00 8B CE

修改后：C0 **EB** 33 8D 45 F0 8B CE 50 E8 CE F1 FF FF 80 7D F0 00 8B CE

## 0x05 已读不回

![image-20201121122535054](https://image.3001.net/images/20201221/1608516406_5fe003361b76292d6b4c5.png!small)

  

## 0x07 免责申明

本文是作者闲暇之余，方便自己搞的一个小功能。如果对其他人/公司造成不好的影响请联系我们处理。

  

