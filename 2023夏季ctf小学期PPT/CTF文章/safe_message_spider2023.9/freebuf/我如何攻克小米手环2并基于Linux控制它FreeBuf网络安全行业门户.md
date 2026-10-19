本文笔者翻译自hacker博客，原文地址：（<https://medium.com/@a.nikishaev/how-i-hacked-xiaomi-miband-2-to-control-it-from-linux-a5bd2f36d3ad>）

![00.png](https://image.3001.net/images/20180327/15221498043783.png!small)  

这个故事源于我在Facebook一个帖子，帖子中讨论了运动健身追踪器都缺乏API接口的问题，还有为啥不用它帮助数据专家为做一个炫酷的东西。

帖子发出之后，我的好基友Volodymyr Shymanskyy就响应来帮助我，并在github上找了Leo
Soares项目，为我的健身追踪器小米手环2找了一些代码。他尝试运行它，但是连接出现了一些链接问题，所以他花了几个小时修复了他。之后，他提交了个commit，并给了我链接。

那满足了我的初步需求，已经相当OK了。那代码可以连接到手环，发布通知，并获取一次拍摄心脏测量。但这对我来说还有点不够，因为我想从传感器获得实时原始数据，以便在我的数据科学实验中使用（想要做一个健身运动预测器）。

## 正文才开始......

在此之前，我没有任何使用蓝牙设备的经验，所以首先我试着了解了所有这些东西是如何组织和工作的。事实证明，也没啥难得。

每个蓝牙设备都会启动几个的服务，每个服务都有特征，并且一些特征具有描述符（如果特征有多个参数或工作类型（阅读|通知））。某些特性只有读/写访问权限，比如当前时间，电池状态或修订信息。其中一些更复杂并且通过请求/通知循环工作，例如实时心率监视器和授权。基本上，你需要知道这一切的，才能开始使用它。

您还需要两个应用程序来帮助调试蓝牙设备：Wireshark和BLE
debugger。你还需要需要访问安卓手机开发者选项（对不起，对于iOS家伙我还不知道如何做到这点）。

首先，您需要从手机应用程序中取消小米手环2的配对。

现在让我们看看手环有什么服务和特征。让我们打开BLE debugger，开始扫描，你会看到类似这样的东西：

  
![01.png](https://image.3001.net/images/20180327/15221498361317.png!small)  

将设备的MAC地址保存下，后续操作会用到它。

现在让我们连接它，看看它跑了什么服务和特征。

![02.png](https://image.3001.net/images/20180327/1522149865938.png!small)  

以上两个简单的操作中，我们已经获得了一些有用的设备信息。

另一种方法是使用控制台工具hcitool和gatttool。

## Scan:

    
    
    sudo hcitool lescan

连接并获取服务和描述符：

    
    
    sudo gatttool -b YOUR_MAC -I -t random
    > connect
    > primary
    > char-desc

在某些情况下，BLE栈可能会出现故障，您可以打开/关闭蓝牙或运行以下命令：

    
    
    sudo hciconfig hci0 reset

## 数据嗅探

为了我们的手机<->基带通信中嗅探数据，我们需要启用蓝牙在开发设置记录日志。要做到这一点，您需要先打开安卓手机上的开发人员设置。

### 以下是操作的详细步骤：

在Android 4.1及更低版本上，开发者选项屏幕默认可用。在Android 4.2及更高版本中，您必须按如下所示启用此屏幕：

1.打开手机 **设置** 。

2.（仅适用于Android 8.0或更高版本）选择 **系统** 。

3.滚动到底部并选择 **关于手机** 。

4.滚动到底部并点击 **Build numbe** r 7次。

5.返回到上一屏幕以查找底部附近的 **开发人员选项** 。

现在打开开发设置并找到“ **启用** **BleutoothHCI snoop log** ”并启用它。这样，所有蓝牙通信都会被被记录。然后你需要找到名为
**btsnoop_hci.log** 的文件（在我手机中（Android 7.0）它位于/mtklog/btlog/btsnoop_hci.log）

## 认证

现在我们还要要执行一下步骤来获取有关认证（配对）如何工作的一些信息。

1.打开蓝牙和HCI日志。

2.将您的设备与小米安卓程序配对。

3.关闭蓝牙。

4\. 下载btsnoop_hci.log到你的电脑。

5.用Wireshark打开它。

6.找到第一个处理 ** _0x0055_** 的ATT协议请求

你会看到如图的界面：

![1.png](https://image.3001.net/images/20180327/15221499447524.png!small)  

这是验证步骤：

 **配对设备** ****

主要服务UUID ****

 ** _0000fee1-0000–1000–8000–00805f9b34fb_**

 **认证特征 (Char) UUID**

 ** _00000009–0000–3512–2118–0009af100700_**

通知描述符 (Des) 处理

 ** _0x2902_** (所有的过程都一样)

1.通过向Des发送2个字节请求 **\x01\x00** 来设置auth通知（以获得响应）。

2.用命令将16字节的加密密钥发送给Char，并附加2字节 **\x01\x00 + KEY** 。

3.通过发送2个字节 **\x02\x00** 到Char来向设备请求带有命令的随机密钥。

4.从设备响应中获取随机密钥（最后的16个字节）。

5.使用我们的16字节密钥，用A **ES/ECB/ NoPadding** （来自Crypto.Cipher import
AES）对此随机数进行加密，并将其发送回Char（ **\x03\x00+编码数据** ）

### 认证

1.通过发送2个字节 **\x02 \x00** 到Char来向设备请求带有命令的随机密钥。

2.从设备响应中获取随机密钥（最后16个字节）。

3.使用我们的16字节密钥和使用AES / ECB / NoPadding（来自Crypto.Cipher import
AES）对此随机数进行加密，并将其发送回Char（\ x03 \ x00 +编码数据）

## 实时数据

这在认证过程中稍微复杂一些，因为我没有看到在这个过程中犯了一个错误:)并且因为这个心率监视器在15秒后关闭。

硬件服务（HRDW）UUID

 ** _0000fee0-0000-1000-8000-00805f9b34fb_**

心脏监护仪服务（HMS）UUID

 ** _0000180d-0000-1000-8000-00805f9b34fb_**

心率测量特征（HRM）UUID

 ** _00002a37-0000-1000-8000-00805f9b34fb_**

心脏监护仪控制特性（HMC）UUID

 ** _00002a39-0000-1000-8000-00805f9b34fb_**

传感器特性（SENS）UUID

 ** _00000001-0000-3512-2118-0009af100700_**

通知描述符（DES）句柄

 ** _0x2902_** （所有过程都一样）

1.关闭当前监听的测量。

2\. 通过向HMC发送请求 **\x15\x02\x00** 进行一次性测量。

3\. 通过向HMC发送请求 **\x15\x01\x00** 进行连续测量。

4.通过向SENS发送命令到 **\x01\x03\x19** 来启用陀螺仪和心脏原始数据

5.通过向HRM写入DES **\x01\ x00** 启用通知

6.通过向HMC发送请求 **\x15\x01\x01** 来启动连续的心脏测量

7.发送命令到SENS \x02（不知道为什么需要这指令）

8.然后，在每12秒收到一次通知时，需要将 **\x16** ping发送到HCM

## 解析数据

这是最枯燥部分，因为基本上你需要找出如何解包来自设备的打包数据。

它的一部分可以从日志中解析出来，有些不能。

![2.png](https://image.3001.net/images/20180327/15221499766301.png!small)  

这是当前时间的设备的响应

找到合适的数据包和编码可能需要一些时间。就我的例子而言，我需要找到相邻的数据包中相似的字节出现次数，有些重复的数据包。

    
    
    Raw heart: 02102d8c348c448c458c3d8c428c488c 16
    Raw heart: 0218468c418c3d8c468c3f8c398c418c 16
    Realtime heart: 93
    Raw heart: 0220408c448c3f8c428c498c3c8c3d8c 16
    Raw heart: 02283d8c398c488c3e8c468c488c328c 16
    Realtime heart: 99
    Raw heart: 0230438c408c378c3a8c318c458c388c 16
    Realtime heart: 102
    Raw heart: 02404f8c408c458c428c4d8c558c4d8c 16
    Raw heart: 02483e8c3b8c3f8c348c398c318c428c 16
    Realtime heart: 98
    Raw heart: 02504c8c428c5e8c4f8c588c498c558c 16
    Raw heart: 0258478c458c3c8c4e8c3f8c468c4d8c 16
    Realtime heart: 100
    Raw heart: 0260518c4d8c4f8c4b8c4f8c528c458c 16
    Raw heart: 0268408c3f8c538c4d8c408c548c598c 16
    Realtime heart: 102
    Raw heart: 0278418c508c4e8c548c588c468c498c 16
    Raw heart: 0280368c328c2e8c3c8c338c308c3f8c 16
    Realtime heart: 101  
    

从中我们可以看到清晰的数据，重复 **368c 328c 2e8c 3c8c 338c 308c 3f8c**
，数据包长度为16字节。因此，如果我们用2个字节的无符号短数据解压缩，那么我们可以得到7个心脏传感器的原始测量结果。我们也看到第二个字节只是迭代，我认为它只是测量之间的时间差异（我指的是响应的时间差）  

    
    
    Raw gyro: 01de49ffd9ff3c004cffd8ff3b004dffdcff4400Raw gyro: 01df4cffd6ff44004dffd8ff40004cffd1ff4700
    Raw gyro: 02e1103231323d3274328e329632af32c732cf32
    Raw gyro: 01e34fffd7ff56004bffc7ff590049ffccff4c00
    Raw gyro: 01e443ffccff43004effcdff40005bffd4ff4c00
    Raw gyro: 01e558ffc9ff5f005effbfff66005fffb0ff5900
    Raw gyro: 01e64cffacff60005cffa7ff410066ffc9ff4600
    Raw gyro: 01e760ffdcff4b0051ffe4ff4f0034ffdeff5300
    Raw gyro: 02e903365c36813663361036543688374139fe3a
    Raw gyro: 01eb4bffc3ff50004fffc1ff430047ffbbff4100
    Raw gyro: 01ec3effb2ff3c0050ffbfff560047ffccff7300
    Raw gyro: 01ed4fffe0ff78005cffebff8e0056fff6ff8300
    Raw gyro: 01ee7efffbffa1008bff0f00bc00b1ff1900b800
    Raw gyro: 01ef9bff0c00d10095fff3ffd600b7ff0800df00
    Raw gyro: 02f12445314600479e473348aa481c499749244a
    Raw gyro: 01f3c3ff1600fe00beff1800f200a6ff0800e700
    Raw gyro: 01f4a9fff8ffd300a7fff3ffd700a9fff1ffdf00
    Raw gyro: 01f5b1fff8ffe800b4fff1fff700acfffcffef00
    Raw gyro: 01f67ffff7ffc0006bfff4ffb00078ffe9ffb600
    Raw gyro: 01f786ffecffc0006ffff0ffbc0060fff1ffc000
    Raw gyro: 02f9ca4cbb4c784c964ca84c784c854c444c1b4c
    Raw gyro: 01fb7cff0f00bb007eff2700ae0083ff30009800
    Raw gyro: 01fc79ff1800b00076ff0f00bc0068ff0900d900
    Raw gyro: 01fd78ff07000c01f6fffbff19011c000b00f600
    Raw gyro: 01fe4b001100d30054000700c3004300efffeb00
    Raw gyro: 01ff1f00d0ff1701fbffe8ff1b01e3ffffff1101
    Raw gyro: 0201214b014bec4ad04aba4acb4abe4aba4abd4a
    Raw gyro: 0103efffecfffc00e3fff3fff300defff3fffc00
    Raw gyro: 0104e3fff0fff400e6ffefff0301dbffe9ff0c01
    Raw gyro: 0105e3fff0ff0301e6ffe6fffc00dcffecfffc00
    Raw gyro: 0106dffff0fff700dbffeefff600d6fff0fff400
    Raw gyro: 0107dfffecffff00e1fff0ff0301defff3fffc00

至于陀螺仪，就有点困难。但是我的想法是它应该与心脏数据类似的方式打包，但在这种情况下，我们对每个应该签名的陀螺仪轴进行3次测量，数据包长度为20个字节。因此，12
x，y，z测量不会覆盖所有包，但3将会保留前2个字节（与之前的包相同）。所以我这样试了，过不然工作是正常的。

## 代码

代码，你可以找到我的github仓库（<https://github.com/creotiv/MiBand2>）下载所有的代码，所有代码使用python实现。老司机们应该都知道怎么做，在此就不多赘述。

原作者可能是个毛子，如果你们觉得他的思路对你有用，可以给他捐点钱，卖酒喝（他自己的话，github里面可捐款）。  

