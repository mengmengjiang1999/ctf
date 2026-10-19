**随着蓝牙技术的不断普及发展，蓝牙已然成为了许多设备不可或缺的功能。如今的手机和平板电脑几乎都已具备了蓝牙的功能。但在为我们带来极大方便的同时，蓝牙也成正成为一个泄露我们隐私数据的切入口！一旦黑客破解了我们的蓝牙连接，那么我们存储在手机上的大量隐私数据将会被黑客毫无保留的窃取走。**

当然，黑客想要窃取走我们的数据也并非易事。我们都知道蓝牙协议的最小范围为10米，因此黑客必须要在有效范围内才可能对目标发起攻击。但也别高兴的太早，实际上黑客可以通过一些适配器将它的有效距离延长至100米，这个距离足以让他们对例如咖啡厅，办公室甚至是邻居家的蓝牙设备发起攻击。

## 侦察的重要性

像所有的攻击一样，无论是基于计算机还是军事野战，[侦察](https://www.hackers-arise.com/reconnaissance-1)都是至关重要的。没有良好的侦察基础，你的成功几率将大大降低，甚至在某些情况下直接已失败告终。任何情况下，对目标了解越多，你的成功几率则越大。因此，在本教程中我将向你展示几种对潜在目标进行侦察的方法。

如果你对[蓝牙术语，技术和安全](https://www.hackers-arise.com/getting-started-with-bluetooth-hack)并不太了解，那么我强烈建议你在继续阅读下面的内容之前，去做个基本的了解学习。例如MultiBlue
Dongle，一种专门用于黑客入侵蓝牙的工具。此外本文还有一大亮点，在本文中我们将为大家展示Mr. Robot中Elliot是如何入侵监并狱释放囚犯的。

## 使用Bluez进行蓝牙侦察

[BlueZ](http://www.bluez.org/)是几乎所有Linux版本的默认蓝牙协议栈，包括在Debian上构建的[Kali
Linux](https://www.hackers-arise.com/getting-started)。如今，BlueZ也成为了Mac OS
X和Android上的默认蓝牙协议栈。

蓝牙协议的这种实现有许多内置的工具，我们可以将其用于侦察，并且由于它们几乎适用于所有Linux的版本，因此任何人几乎都可以使用它们。（我们也会在Kali中使用一些专门的蓝牙侦察工具。）

### Step 1：启动Kali

首先，让我们启动Kali系统并打开命令终端。此外，你还需要准备一个与Linux兼容的蓝牙适配器。

### Step 2：使用Hciconfig启用你的蓝牙适配器

第一步检查我们的蓝牙适配器是否被识别并启用。我们可以使用名为hciconfig的内置BlueZ工具来完成此操作：

 **kali > hciconfig**

![Kali下的蓝牙设备侦察方法介绍](https://image.3001.net/images/20180601/15278144719367.png!small)

正如你在截图中所看到的那样，我们的蓝牙适配器的MAC地址为10:AE:60:58:F1:37。蓝牙协议栈已将其命名为“hci0”。现在，让我们确定并启动它：

 **kali > hciconfig hci0 up**

![Kali下的蓝牙设备侦察方法介绍](https://image.3001.net/images/20180601/15278146111019.png!small)

一切顺利，hci0成功启动并开始工作！

### Step 3：使用Hcitool扫描蓝牙设备

BlueZ协议栈还具有一些用于扫描蓝牙设备的优秀命令行（cli）工具。这些都位于hcitool中。让我们首先使用这个工具的扫描部分，寻找正在发送他们的发现信标的蓝牙设备（在发现模式中）。

 **kali > hcitool scan**

![Kali下的蓝牙设备侦察方法介绍](https://image.3001.net/images/20180601/15278146308706.png!small)

在以上截图中，你可以看到它发现了两个设备，ANDROID BT和SCH-I535。现在，让我们尝试使用inquiry (inq)
命令，以获取有关这些设备的更多信息：

 **kali > hcitool inq**

![Kali下的蓝牙设备侦察方法介绍](https://image.3001.net/images/20180601/15278146462252.png!small)

请注意，它还显示了clock offset以及class。class指示了它是哪种类型的蓝牙设备，我们可以通过转到Bluetooth
SIG站点上的[服务发现页](https://www.bluetooth.org/en-us/specification/assigned-numbers/service-discovery)来查看代码，以确定它的设备类型。在接下来的内容中，还有更为方便直接的工具可以为我们做到这一点。

Hcitool是一款功能强大的蓝牙调试工具。下面截图展示了它的一些基本使用命令。

![Kali下的蓝牙设备侦察方法介绍](https://image.3001.net/images/20180601/15278146653166.png!small)

### Step 4：使用Sdptool扫描服务

服务发现协议（SDP）是用于搜索服务的蓝牙协议。BlueZ有一个名为sdptool的工具，可以浏览设备提供的所有服务。使用命令如下：

 **kali > sdptool browse <MAC Address>**

**![Kali下的蓝牙设备侦察方法介绍](https://image.3001.net/images/20180601/15278146886647.png!small)**

​可以看到sdptool获取到了设备上所有的服务信息。

### Step 5：使用L2ping测试可达性

现在我们已经获取到了附近所有设备的MAC地址，我们可以ping它们，不管它们是否处在发现模式中，看看它们是否能到达。

 **kali > l2ping <MAC address>**

![Kali下的蓝牙设备侦察方法介绍](https://image.3001.net/images/20180601/15278147099557.png!small)

从测试结果可以看出，MAC地址为76:6F:46:65:72:67的设备在范围内并且可以访问。

### Step 6：使用BTScanner扫描蓝牙设备

如果你不习惯于命令行界面的使用，那么kali也为我们准备了一些基于GUI界面的蓝牙扫描工具（BTScanner）。你只需输入以下命令即可：

 **kali > btscanner**

此时，会为我们打开一个基本的GUI界面。要进行查询扫描，只需在键盘上输入字母“i”。可以看到，BTScanner同样也发现了那两个设备，并额外又为我们发现了一个设备MINIJAMBOX。

![Kali下的蓝牙设备侦察方法介绍](https://image.3001.net/images/20180601/15278147299634.png!small)

要收集有关设备的更多信息，只需将光标放置在相应的设备上，然后按下键盘上的Enter。它就会为我们显示所有关于设备收集的信息，与sdptool类似。

![Kali下的蓝牙设备侦察方法介绍](https://image.3001.net/images/20180601/15278147477553.png!small)

可以看到这是关于SCH-I535设备的信息。类别号为0x5a020c，并被标识为“手机/智能手机”。

### Step 7：使用BlueMaho进行蓝牙嗅探

除此之外，在Kali上还有一款可用于蓝牙扫描的工具BlueMaho。这是一款集成的蓝牙扫描工具。在这里，我们将简单地使用它进行扫描操作。输入以下命令启动BlueMaho
GUI：

 **kali > bluemaho.py**

随后我们会看到如下所示的GUI界面。这里，我勾选了“get SDP
info”并点击左边的play按钮。BlueMaho开始扫描可发现的设备，和其他工具一样，它找到了两个蓝牙设备。

![Kali下的蓝牙设备侦察方法介绍](https://image.3001.net/images/20180601/15278147714737.png!small)

在底部窗口中，BlueMaho为我们显示了来自扫描设备的详细信息。我已将这些信息复制并粘贴至文本文件中，以方便大家的阅读：

![Kali下的蓝牙设备侦察方法介绍](https://image.3001.net/images/20180601/15278147915551.png!small)

从获取的信息可以看到，第一个设备名称为“MINIJAMBOX”，其类型被识别为“音频/视频，耳机配置文件”。第二个设备名称为“SCH-I535”，其类型被识别为手机，智能手机”。

## 总结

通过本文，我们学习了如何在我们的范围内收集周围蓝牙设备信息的方法手段。在后续的教程中我们将进一步的为大家展示，如何利用这些收集的信息，入侵并窃取他们的隐私数据。

 ***参考来源：[hackers-arise](https://www.hackers-arise.com/bluetooth-reconnaissance)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

