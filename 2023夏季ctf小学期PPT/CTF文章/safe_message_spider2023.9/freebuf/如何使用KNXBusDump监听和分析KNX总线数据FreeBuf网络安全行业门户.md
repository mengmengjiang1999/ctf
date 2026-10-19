![](https://image.3001.net/images/20220511/1652262279_627b85872397e7dec7797.jpeg!small)  

## 关于KNX-Bus-Dump

KNX是一种热门的自动化构建协议，专门用于将传感器、执行器和其他组件互联在一起。而KNX-Bus-Dump这是一款功能强大的KNX总线数据监听和分析工具，该工具使用了Calimero Java库来记录和监控所有通过KNX总线发送的数据。

KNX-Bus-Dump能够通过一个TPUART连接来访问KNX总线，不过也可以更改为使用其他的连接介质。数据将会转储至一个与Wireshark兼容的十六进制转储文件中。数据将带有时间戳，并以并以纳秒精度标准化为UTC时间，以执行数据分析并提供通信数据的时间线。生成的十六进制转储文件可以导入Wireshark，该文件可以配置为使用Wireshark的cEMI解析器解析KNX数据。

KNX-Bus-Dump可以用于KNX传感器、执行器和其他KNX设备的协议分析。除此之外，我们还可以利用该工具来对KNX设备进行安全分析。

Tcpdump和Wireshark不能用于转储通过KNX总线发送的数据，因为我们处理的是原生KNX数据，而非TCP/IP数据包。Tcpdump和Wireshark可以转储KNXnet/IP数据包，也就是TCP/IP数据包，而KNXnet/IP是通过TCP/IP网络向KNX总线发送命令和数据的协议。

## 工具要求

该工具需要使用到Calimero Java库，能够兼容树莓派3和4，而且还需要树莓派HAT用于TPUART连接。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ChrisM09/KNX-Bus-Dump.git

## 工具使用

### 创建十六进制转储

1、将“KNXBusDump.java”文件拷贝到Calimero项目中的“introduction/src/main/java/ ”路径下。

2、在终端中切换到“introduction”目录中。

3、下列命令即可直接运行KNX-Bus-Dump：

    
    
    ./gradlew run -Pcalimero.serial.tpuart.maxInterByteDelay=60000 -DmainClass=KNXBusDump

4、现在，我们可以等待总线传输数据，转储的数据会存储在“KNXBusDump-Telegrams.txt”文件中。

5、使用Ctrl+C快捷键取消工具运行，然后将生成的文件导入至Wireshark进行后续分析即可。

### 分析十六进制转储

在Wireshark中，我们可以导入十六进制转储数据包，并制定一个解析器来分析数据包。

1、在Wireshark中，等待导入完成，然后点击“File -> Import From Hex Dump”：

![](https://image.3001.net/images/20220511/1652262307_627b85a3f40f90bbbdf6e.png!small)

2、为了正确解析数据并输出结果，我们需要提供一个正则表达式：

    
    
    ^\s*(?<time>\d{4}-\d\d\-\d\dT(\d\d\:){2}\d\d.(\d){6}[Z])\s(?<seqno>\d{6})\s+(?<data>[0-9a-fA-F]*)$

3、选择十六进制转储文件作为输入源。

4、在新的对话窗口中，切换到“Regular Expression”标签，将上述正则表达式复制进去。

5、确保数据编码采用的是“Plain hex 200*16”。

6、在“Timestatmp format”部分，我们需要指定工具的生成模式：

    
    
    %Y-%m-%dT%H:%M:%S.%fZ

7、在“Encapsulation”部分，将“Encapsulation Type”修改为“Wireshark Upper PDU Export”。

8、现在我们就可以导入文件并进行数据包分析了：

![](https://image.3001.net/images/20220511/1652262334_627b85be8cdcc72f635dc.png!small)

## 工具输出样例

 **Wireshark时间戳：**

![](https://image.3001.net/images/20220511/1652262347_627b85cbcfb10a00a58d5.png!small)

 **对应的十六进制转储文件：**

![](https://image.3001.net/images/20220511/1652262358_627b85d6c4398696fc3e5.png!small)

注意：途中高亮显示的时间为“NORMALIZED UTC TIME”，无论标记的是哪个时区，最终显示的都是UTC时间。

![](https://image.3001.net/images/20220511/1652262365_627b85dda5f692a823f6c.png!small)

## 测试场景

![](https://image.3001.net/images/20220511/1652262388_627b85f4ef84bd2f763d5.jpeg!small)

## 项目地址

 **KNX-Bus-Dump：** 【[ _GitHub传送门_](https://github.com/ChrisM09/KNX-Bus-Dump)】

## 参考资料

> [ _https://github.com/ChrisM09/KNX-Bus-Dump/blob/main/KNX-Raspberry-Pi-Hat-> Usage/README.md_](https://github.com/ChrisM09/KNX-Bus-Dump/blob/main/KNX-> Raspberry-Pi-Hat-Usage/README.md)
>
> [ _https://github.com/ChrisM09/KNX-Bus-Dump/blob/main/Raspberry-Pi-Calimero-> Setup/README.md_](https://github.com/ChrisM09/KNX-Bus-> Dump/blob/main/Raspberry-Pi-Calimero-Setup/README.md)

