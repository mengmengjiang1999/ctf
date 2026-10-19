## 前言

**针对汽车的攻击和入侵是当前最前沿的领域和最热门的话题之一。随着自动驾驶汽车技术的发展，在未来这个领域将变得更加重要。作为汽车黑客快速发展的一部分，我最喜欢的黑客工具之一Metasploit也开发了连接汽车的功能和模块。**

![使用Metasploit进行汽车安全性测试](https://image.3001.net/images/20181114/1542153073_5beb6371891f8.png!small)

如果你当前使用的Metasploit版本没有硬件模块，请进行版本更新获取最新添加的模块。不得不说的是，这只是Metasploit迈向该领域的一小步，而且框架在汽车黑客方面的能力也相当有限，但我相信在不久的将来会有更多更好的汽车黑客模块被添加进来。现在我们的任务是“如何将Metasploit框架连接到汽车网络上”？

![使用Metasploit进行汽车安全性测试](https://image.3001.net/images/20181114/1542153089_5beb638131fba.png!small)

如果你之前已阅读过我关于汽车黑客攻击的相关文章，那么你应该知道汽车的汽车中的主导协议是CAN且为串行协议。我们要做的就是通过串行接口连接到汽车的CAN协议。这样，我们就能够通过Metasploit中的几个预建模块在汽车网络上发送恶意流量了。

## 步骤 1：获取 OBD II 连接器硬件

首先，我们一个可以连接到汽车的ODC II连接器的设备。这里我选择的是相对便宜的[ODB II ELM327
蓝牙](https://www.amazon.com/Vgate-Bluetooth-Scanner-Adapter-Diagnostic/dp/B019SURWYO/ref=as_sl_pc_tf_til?tag=hackerarise-20&linkCode=w00&linkId=98ba8956a8999eaa5ee0890847dfd326&creativeASIN=B019SURWYO)迷你接口，亚马逊上的价格为8.49美元，可有效地与汽车的CAN网络通信，并通过蓝牙使用Metasploit连接到你的系统。因此你需要配备内置蓝牙的计算机或购买USB蓝牙适配器。有关蓝牙协议的更多信息，请参阅
["Bluetooth Hacking, Part 2: Bluetooth Reconnaissance" ](https://www.hackers-arise.com/bluetooth-reconnaissance)一文。

## 步骤 2：安装 Serial Port（串口）

CAN协议是一个串行协议，因此我们需要安装 ruby gem "serialport" 。

    
    
    kali > gem install serialport

## ![安装 Serial
Port（串口）](https://image.3001.net/images/20181114/1542153123_5beb63a36efed.png!small)

## 步骤 3：连接蓝牙适配器

接下来，我们需要连接我们的蓝牙适配器与我们汽车中的ELM 327适配器通信。

要连接到ELM 327设备，我们就需要获取到它的MAC地址。我们可以通过使用内置的hcitool工具，扫描蓝牙设备来获取MAC地址。

    
    
    kali > hcitool scan

![连接蓝牙适配器](https://image.3001.net/images/20181114/1542153143_5beb63b771bf3.png!small)

根据扫描结果，这里我的MAC地址为00:19:6D:36:4A:9D。

现在，我们使用该MAC地址将我们的蓝牙适配器连接到ELM 327设备。 注意：这里要用双引号将MAC地址括起来，如下所示。

    
    
    kali > rfcomm connect /dev/rfcomm1 "00:19:6D:36:4A:9D"

##
![连接蓝牙适配器](https://image.3001.net/images/20181114/1542153185_5beb63e1515f4.png!small)

## 步骤 4：运行 ELM 327 继电器

下一步是运行ELM 327继电器，使Metasploit能够与ELM 327芯片组通信。你可以在/usr/share/metasploit-framework/tools/hardware目录下找到它。

    
    
    kali > cd /usr/share/metasploit-framework/tools/hardware
    
    kali > ls -l

![运行 ELM 327
继电器](https://image.3001.net/images/20181114/1542153204_5beb63f4b4a4b.png!small)

在运行它之前，让我们先来查看下它的帮助信息。

    
    
    kali > ruby elm327_relay.rb -h

![运行 ELM 327
继电器](https://image.3001.net/images/20181114/1542153225_5beb640998852.png!small)

可以看到，我们只需设置两个参数；速度（默认值为115200）和串行设备（默认为/dev/ttyUSB0）。这里的串行设备，可以通过dmesg | grep
ttyS*命令进行确定。

现在，使用串行设备运行elm327继电器，并将speed保持为默认值，如下所示。

    
    
    kali >ruby  elm327_relay.rb -s /dev/ttyS0

## 步骤 5：启动 Metasploit

现在，我们已经将Kali Linux配置为与ELM
327设备通信，我们需要创建一个到Metasploit的硬件桥接。Metasploit被构建用于TCP/IP的通信，而我们现在需要它通过串口与汽车原生的CAN协议进行通信

首先，我们启动Metasploit。

    
    
    kali > msfconsole

然后，搜索汽车模块。

    
    
    kali > search automotive

![启动
Metasploit](https://image.3001.net/images/20181114/1542153295_5beb644f11dae.png!small)

可以看到，只有少数几个汽车模块，且功能也非常的有限。

我们选择使用auxiliary/client/hwbridge/connect模块。

    
    
    msf >use auxiliary/client/hwbridge/connect

![启动
Metasploit](https://image.3001.net/images/20181114/1542153316_5beb64644fd4d.png!small)

加载该模块后，我们可以输入info命令来获取有关此模块的详细信息。

    
    
    kali > info

![启动
Metasploit](https://image.3001.net/images/20181114/1542153335_5beb64774c563.png!small)

最后，让我们执行该模块。

    
    
    msf >exploit

## 步骤 6：使用 Metasploit 汽车模块

现在，我们已在车辆中创建了Metasploit和CAN协议之间的硬件桥接。这样我们就可以开始使用Metasploit中的汽车模块了。

![使用 Metasploit
汽车模块](https://image.3001.net/images/20181114/1542153363_5beb649300d14.png!small)

例如，你想要检索车辆信息。

    
    
    msf > use post/hardware/automotive/getvinfo

![使用 Metasploit
汽车模块](https://image.3001.net/images/20181114/1542153386_5beb64aa3ef82.png!small)

该模块将查询并收集所有车辆DTC（诊断故障码）和其他信息，如速度，冷却液温度，VIN甚至清除DTC。

现在，我们可以将我们的Linux系统和Metasploit 框架直接连接到汽车网络，直接与汽车的设备进行通信！

有关更多汽车黑客方面的教程，请关注我即将推出的汽车黑客课程！

 ** *参考来源：[hackers-arise](https://www.hackers-arise.com/single-post/2018/10/25/Metasploit-Basics-Part-17-Automobile-Hacking-with-Metasploit)，FB小编secist编译，转载请注明来自FreeBuf.COMngguo**

