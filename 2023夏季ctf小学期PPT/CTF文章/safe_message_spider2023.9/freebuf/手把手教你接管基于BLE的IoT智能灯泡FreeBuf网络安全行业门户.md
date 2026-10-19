**在这篇文章中。我将手把手的教大家如何接管一个基于BLE的IoT智能灯泡。我将利用嗅探工具抓取通信数据包，并对数据包做相应的修改以执行重放攻击 -而所有的这些操作成本将会控制在10美元以下。**

本文将主要包含以下内容：

>   * 安装和配置Gattacker
>   * 分析物联网设备的advertisement和Service数据包
>   * 嗅探和转储在移动设备和设备之间传输的数据
>   * 用转储文件执行重放攻击
>

这里我先做个预告。在不久后，我们将举办IoT开发的公开课，其中涉及BLE嗅探，开发，Zigbee等主题，大家可以随时通过[secure@attify.com](mailto:secure@attify.com)与我们联系，或查看[这里](http://offensiveiotexploitation.com/)。公开课程的安排在这里：<https://www.attify-store.com/collections/real-world-training/products/offensive-iot-exploitation-live-training>。

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226295851678.png!small)  

在正式开始之前，我们必须具备以下条件：

 **硬件**

>   * 笔记本电脑
>   * BLE Dongles
>

 **软件**

>   * Gattacker
>   * NRFConnect
>

##  **安装Gattacker并对其进行配置：**

 **执行步骤**

 **Step 1** ：安装Gattacker，你需要最新版本的node和npm。可以使用以下命令安装：

    
    
    sudo apt-get install bluetooth bluez libbluetooth-dev libudev-dev

安装NodeJS，你可以参照本[指南](https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions)进行操作

 **Step 2** ：接下来，我们需要安装bleno，命令如下：

    
    
    npm install bleno
    npm install noble

如果出现错误，请确保你之前已正确安装了node和npm软件包。

 **Step 3** ：现在使用该命令安装Gattacker

    
    
    npm install gattacker

 **Step 4** ：在另一台虚拟机（或系统）上重复相同的步骤，因为我们需要两台机器 - 一台用于主机，另一台用于从机。

 **Step 5** ：完成后，插入ble适配器并使用sudo hciconfig确保其已插入。

然后导航到gattacker文件夹

    
    
    cd node_modules/gattacker

 **Step 6** ：

接下来，我们需要编辑config.env文件，配置gattacker。

    
    
    sudo nano config.env

**![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226296214614.png!small)  
**

 **Step 7** ：取消 **NOBLE_HCI_DEVICE_ID**
注释，然后将其替换为hciX，其中（X是我们之前通过hciconfig找到的值）并保存文件

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226296479936.png!small)  

从机的配置

让我们来查看下该从机的IP地址。

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226296736340.png!small)  

从机的连接信息

 **Step 8** ：现在在主机中，插入BLE适配器并按照上述步骤操作。对于config.env，请按照以下步骤操作：

>   * 取消 **NOBLE_HCI_DEVICE_ID** 注释
>   * 取消 **BLENO_HCI_DEVICE_ID** 注释
>

将它们分配给hciX值。

完成后，在WS_SLAVE中，将其中的IP地址替换成从机的地址：

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226297118125.png!small)  

主机的配置

完成后，保存配置文件。现在我们准备开始使用Gattacker并利用一些物联网设备。

## 使用Gattacker扫描和存储设备信息：

 **执行步骤**

 **Step 1** ：打开从机VM并启动ws-slave.js，如下所示：

    
    
    sudo node ws-slave.js

**![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226297453798.png!small)  
**

 **Step 2** ：现在在主机分支的gattacker文件夹下并启动扫描，如下所示

    
    
    sudo node scan.js

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226297779558.png!small)  

扫描命令

现在打开灯泡，然后按Enter键以查看如下消息

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226298046888.png!small)  

保存它的advertisement包

sudo node scan f81d7860753A其中f81d7860753A是由gattacker保存的灯泡的peripheral名称。

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226298552874.png!small)  

保存它的service包

现在，如果你再导航到gattacker中的device文件夹，你可以看到如下图所示的两个文件

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226298901004.png!small)  

文件夹包含了灯泡的advertisement和Service数据包

 **Step 3** ：现在打开文件f81d7860753a_LEDBLE-7860753A.adv.json查看设备的advertisement信息

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226299316745.png!small)  

灯泡的advertisement信息

 **Step 4** ：同样，打开f81d7860753a.srv.json查看设备的service信息

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226299622956.png!small)  

灯泡的service信息

## 使用gattacker转储和重放信息：

###  **执行步骤**

 **Step 1** ：按照前面的练习存储advertisement和service数据包。 现在我们关闭灯泡并按照以下步骤操作

 **Step 2** ：完成后，在主机上结合advertisement和service数据包启动advertise.js。

    
    
    sudo node advertise.js
    -a devices/f81d7860753a_LEDBLE-7860753A.adv.json
    -s devices/f81d7860753a.srv.json

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226300009015.png!small)  

嗅探设备之间的通信

现在按回车并等待消息

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226300497014.png!small)  

等待灯泡开启

现在给灯泡供电，你会看到如下信息

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226300845567.png!small)  

初始化攻击

 **Step 3** ：现在从手机中打开MAGICBLUE应用程序并扫描设备

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226301098644.jpg!small)  

 **Step 4** ：现在连接到设备，在主机中你可以看到如下内容

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226301407003.png!small)  

主机中客户端成功连接的消息

 **Step 5** ：在移动应用中，更改灯泡的颜色。

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/1522630174172.png!small)  

可以在这里看到更改的Handles和RGB值

现在我们按 **ctrl + c** 退出

 **Step 6** ：现在此值已被保存在了转储（dump）文件夹中，导航到转储文件夹并输入以下命令：

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226302086669.png!small)  

转储转储文件夹中的文件

打开文件：

    
    
    sudo nano f81d7860753a.log

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226302492416.png!small)  

你将看到如下内容

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226302833178.png!small)  

更改保存为转储的值

 **Step 7** ：现在我们来对它进行重放，在此之前我们必须将前7行删除。

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226303113169.png!small)  

要编辑的行

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226303656880.png!small)  

编辑完成后

现在保存文件

 **Step 7** ：现在在移动设备和灯泡断开连接后的主机中，输入以下命令

![Screenshot-from-2017-10-09-13-42-45.png](https://image.3001.net/images/20180402/15226304012664.png!small)  

    
    
    sudo node replay.js -i dump/f81d7860753a.log -p f81d7860753a -s devices/f81d7860753a.srv.json**

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226304405810.png!small)  

重放攻击

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226304806890.png!small)  

重放信息

 **使用gattacker转储和重放NRFConnect应用程序的信息：**

 **执行步骤**

 **Step 1** ：NRFConnect应用程序支持XML文件。因此，我们需要将从转储文件夹获取的日志文件更改为有效的xml文件，如下所示：

    
    
    node gattacker2nrf.js -i dump/f81d7860753a.log > dump/f81d7860753.xml

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226305219076.png!small)  

转换为xml文件的命令

导航到转储文件并查看名称为 **f81d7860753.xml** 的xml文件

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226305612845.png!small)  

包含f81d7860753.log的文件夹和转换后的f81d7860753.xml文件

现在将这个xml文件传送给手机

 **Step 2** ：接下来，从google play store下载NRFConnect应用程序。 安装完成后打开应用程序和灯泡。使用nrf
connect app扫描灯泡。

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/1522630593372.jpg!small)  

 **Step 3** ：连接后，按下位于右下角的橙色图标

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226306249370.jpg!small)  

灯泡的连接状态

 **Step 4** ：你将看到下图所示的内容

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226306514207.jpg!small)  

打开宏以加载xml文件

 **Step 5** ：现在按屏幕上的 **下载** 图标并浏览到从主机传输xml文件的文件夹。

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226306796430.jpg!small)  

加载xml文件

 **Step 6** ：在这里你将能够看到如下所示的播放选项

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226307031109.jpg!small)  

转储文件准备重放

 **Step 7** ：现在点击播放选项来执行对灯泡的重放攻击。

![手把手教你接管基于BLE的IoT智能灯泡](https://image.3001.net/images/20180402/15226307404115.jpg!small)  

执行攻击

如果现在你已经能够控制和操纵灯泡了，那么就证明你已经成功执行了该攻击。

在之后的文章中我们还会研究和讨论更多有关BLE开发，Zigbee开发等主题，欢迎大家的关注！

 ***参考来源：[attify](https://blog.attify.com/hacking-bluetooth-low-energy/)，FB小编
secist 编译，转载请注明来自FreeBuf.COM**

