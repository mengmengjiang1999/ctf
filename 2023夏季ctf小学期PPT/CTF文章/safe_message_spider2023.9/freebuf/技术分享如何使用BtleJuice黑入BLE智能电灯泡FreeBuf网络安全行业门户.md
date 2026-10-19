## 前言

**在这篇文章中，我们将讨论如何使用BtleJuice通过执行中间人（MiTM）攻击来利用一个蓝牙低能耗（BLE）智能灯泡。本文中探讨的技术，也同样适用于其他基于BLE的智能设备。**

 **![页首配图](https://image.3001.net/images/20180813/15341517697891.png!small)**

## 概述

本文的主要内容包括：

> 安装BtleJuice；
>
> 分析在目标设备上运行的所有截获的GATT操作；
>
> 使用GATT操作执行Man-in-the-middle（中间人）攻击；
>
> 将数据导出到文件。

 **以下是一些必须满足的基本硬软件要求：**

###  **硬件**

> 基于BLE的物联网智能灯泡
>
> 两个蓝牙适配器

###  **软件**

> Node.js > 4.3.2
>
> 虚拟机（VMware/Virtual Box）
>
> BtleJuice

## 安装 BtleJuice

BtleJuice是执行蓝牙智能设备的中间人攻击（也被称为蓝牙低能量）的完整框架。BtleJuice由两个组件组成 -拦截代理和核心。这两个组件需要在两个系统上单独运行，每个系统都连接了蓝牙4.0+适配器。我们将使用一台物理机器和另一台运行在同一主机上的虚拟机（VM）。

 **注意：**
不是使用两台独立的物理机器。其中一个适配器将连接到主机，另一个适配器连接到VM。下面，我们按照以下步骤在主机和VM上来安装BtleJuice。

 **Step 1：** Btlejuice需要一个相当新版本的node(>=4.3.2)
和npm。你可以按照[本指南](https://yoember.com/nodejs/the-best-way-to-install-node-js/)使用nvm（Node 版本管理器）来进行安装。

 **Step 2：** 使用包管理器安装BtleJuice的依赖项：

    
    
    sudo apt-get install bluetooth bluez pbbluetooth-dev pbudev-dev

 **Step 3：** 安装 Btlejuice：

    
    
    npm install -g btlejuice

## 设置BtleJuice代理（在VM中）

 **Step 1：** 将蓝牙适配器连接到VM并启动蓝牙：

    
    
    service bluetooth start

**![启动蓝牙](https://image.3001.net/images/20180813/1534117118_5b70c4fe04713.png!small)**

 **Step 2：** 通过hciconfig命令查看适配器是否已按预期工作：

![查看适配器是否已按预期工作](https://image.3001.net/images/20180813/1534117133_5b70c50d197b2.png!small)

 **Step 3：** 在虚拟机中启动btlejuice-proxy：

![启动btlejuice-proxy](https://image.3001.net/images/20180813/1534117148_5b70c51c7a524.png!small)

 **Step 4：** 找到VM的IP地址，以便我们可以从主机连接到它。或在终端中运行ifconfig来获取IP：

![获取IP](https://image.3001.net/images/20180813/1534117162_5b70c52ac7f9b.png!small)

## 设置BtleJuice核心（在主机上）

 **Step 1：** 在主机上打开终端并运行hciconfig：

![运行hciconfig](https://image.3001.net/images/20180813/1534117200_5b70c550d3642.png!small)

 **Step 2：** 运行sudo service bluetooth stop停止蓝牙服务：

![停止蓝牙服务](https://image.3001.net/images/20180813/1534117217_5b70c561f22f3.png!small)

 **Step 3：** 在主机上插入蓝牙适配器：

![插入蓝牙适配器](https://image.3001.net/images/20180813/1534117228_5b70c56c9814c.jpg!small)

 **Step 4：** 通过hciconfig命令查看连接到主机的蓝牙适配器是否已按预期工作：

![查看连接到主机的蓝牙适配器](https://image.3001.net/images/20180813/1534117243_5b70c57b8b463.png!small)

 **Step 5：** 通过运行sudo hciconfig hciX up打开蓝牙适配器，其中的X是上一步中获得的蓝牙适配器号：

![获得的蓝牙适配器号](https://image.3001.net/images/20180813/1534117265_5b70c5917024c.png!small)

 **Step 6：** 现在我们需要运行BtleJuice核心并连接虚拟机：

    
    
    sudo btlejuice -u <VM IP address> -w

其中u是运行btlejuice-proxy的VM的IP地址，w表示启动Web界面：

![Web界面](https://image.3001.net/images/20180813/1534117292_5b70c5ac427b1.png!small)

与此同时，在VM中运行的btlejuice-proxy将会显示客户端连接的消息：

![显示客户端连接的消息](https://image.3001.net/images/20180813/1534117309_5b70c5bd65beb.png!small)

 **Step 7：** 一旦主机上运行的BtleJuice核心成功连接到bltjejuice-proxy，我们打开浏览器并导航至<http://localhost:8080/>：

![打开浏览器](https://image.3001.net/images/20180813/1534117326_5b70c5ce47b54.png!small)

 **Step 8：** 单击蓝牙图标的 "Select Target"按钮。此时将会出现一个对话框，并显示核心检测到的所有可用蓝牙设备：

![所有可用蓝牙设备](https://image.3001.net/images/20180813/1534117344_5b70c5e004353.png!small)

 **Step 9：** 双击目标设备并等待接口准备就绪（蓝牙按钮方面将改变）：

![等待接口准备就绪](https://image.3001.net/images/20180813/1534117362_5b70c5f2200ab.png!small)

 **Step 10：** 将关联的移动应用程序与刚创建的dummy设备连接：

![与刚创建的dummy设备连接](https://image.3001.net/images/20180813/1534117379_5b70c603564d5.png!small)

 **Step 11：** 如果连接成功，则主界面上将显示已连接的事件：

![显示已连接的事件](https://image.3001.net/images/20180813/1534117397_5b70c6158d526.png!small)

## 通过重放GATT操作执行中间人攻击

BtleJuice充当移动应用程序和BLE智能灯泡之间的代理，发送到灯泡的任何命令都将被BtleJuice捕获并被转发给灯泡。

让我们使用移动应用程序与灯泡进行交互，并尝试破译命令的结构方式。

 **Step 1：** 使用Android应用程序将灯泡颜色更改为蓝色，蓝色的RGB值为：2, 0, 255：

![将灯泡颜色更改为蓝色](https://image.3001.net/images/20180813/1534117415_5b70c62714770.png!small)

BtleJuice捕获相应的数据包：

![捕获相应的数据包](https://image.3001.net/images/20180813/1534117438_5b70c63e9f338.png!small)

现在将灯泡颜色更改为红色，RGB值为： 255, 8, 0：

![将灯泡颜色更改为红色](https://image.3001.net/images/20180813/1534117455_5b70c64f833f2.png!small)

BtleJuice捕获与命令相对应的数据包，以将颜色更改为红色：

![捕获与命令相对应的数据包](https://image.3001.net/images/20180813/1534117476_5b70c66475bba.png!small)

检查数据包，我们可以注意到一个模式。应用程序中显示的颜色的RGB值与捕获中的第二个，第三个和第四个字节匹配。

因此，如果我们更改这些字节然后重放数据包，应该能够获得不同的颜色。

 **Step 2：** 从捕获的数据包列表中，右键单击颜色更改命令，然后单击replay：

![捕获的数据包](https://image.3001.net/images/20180813/1534117498_5b70c67a461b5.png!small)

 **Step 3：** 将数据值中的颜色字节从8c 86 ff更改为任何其他值，例如8c 45 ff，这是一种带有紫色调的颜色：

![数据值中的颜色字节](https://image.3001.net/images/20180813/1534117520_5b70c690dffb3.png!small)

**![数据值中的颜色字节](https://image.3001.net/images/20180813/1534117624_5b70c6f811df3.png!small)**

 **Step 4：** 单击“ Write”按钮。 我们会注意到灯泡颜色变为了紫色：

![23Picture27.png](https://image.3001.net/images/20180813/1534117643_5b70c70b80b03.png!small)

## 导出捕获的数据

BtleJuice可以将捕获的数据导出到文件中，以便以后使用或在其他工具中进行分析。

单击export按钮并下载捕获数据的JSON（或文本）版本：

![下载捕获数据的JSON](https://image.3001.net/images/20180813/1534117669_5b70c725aa2ff.png!small)

至此，我们已经演示了BtleJuice作为独立工具的使用。

此外，BtleJuice还提供了NodeJS和Python
bindings，我们可以在我们自己的BLE攻击工具中使用它。有关更多信息，请[参阅此处](https://www.npmjs.com/package/btlejuice-bindings)。

 ***参考来源：[attify](https://blog.attify.com/btlejuice-mitm-attack-smart-bulb/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

