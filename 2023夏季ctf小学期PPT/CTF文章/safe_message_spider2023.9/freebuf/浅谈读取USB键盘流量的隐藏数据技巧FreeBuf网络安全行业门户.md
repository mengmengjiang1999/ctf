## 0×00 预备

**wireshark是一款可以用来抓取流量的工具，可以用它来分析流量，从中发现黑客所做的记录和改动，对我们分析被攻击情况和进行防御有很大的帮助，usbkeyboard可以隐藏一些信息，通常，我们可以使用以上工具和方法从中发现一些隐藏信息。**

## 0×01 数据准备

假设有一段流量，协议是usb，我用wiresharp打开这个包，可以看到里面的字段和内容：

![图片1.png](https://image.3001.net/images/20181212/1544614025_5c10f089e785b.png!small)

可以看出内容主要是Leftover Capture
Data，首先要对usb协议进行分析，右键选项，然后点击应用为列，可以将该域的值在主面板上显示，usbkeyborad的数据包数据长度为8个字节，每两位是一个字节，而按键的数据都在第三个字节处，就是00、01、02、03...11、12、13、14，键位和HEX数值之间的对应关系如下图所示：

![图片2.png](https://image.3001.net/images/20181212/1544614041_5c10f099418a9.png!small)

要提取出来这些数据以进行分析，就需要使用工具和脚本来对这些数据进行处理，以下是实现方法。

## 0×02 实现

首先，我们需要使用到wireshark里的工具tshark，这是wireshark工具的命令行程序，效率更高，如果是linux系统，则需要安装tshark包，安装完之后就执行tshark命令，如果是windows则直接安装wireshark，里面自带了tshark程序，可以直接执行。然后执行：

    
    
    "tshark.exe" -r usb.Pcap -T fields -e usb.capdata > usb.data

这样，就生成了一个usb.data文件，这个文件就是tshark对usb.pcap流量包内数据的截取，其实就是个txt文档，可以直接查看。

当我们用文本文档打开查看的时候：

![图片3.png](https://image.3001.net/images/20181212/1544614052_5c10f0a41237c.png!small)

发现里面的数据就是原来Leftover Capture
Data列的数据，这列数据就是usb键盘键位的代码，可以对这列数据进行处理，过滤掉无用的流量，保留与键位有关的流量，也就是第三个字节的数据，精简一下。

![图片4.png](https://image.3001.net/images/20181212/1544614060_5c10f0ac5bde3.png!small)

将以上python脚本保存为一个文件，然后执行：

![图片5.png](https://image.3001.net/images/20181212/1544614072_5c10f0b8d9400.png!small)

打开这个txt文件，发现里面有一段由数字组成的字段，很长，这就是我们需要的数据：

![图片6.png](https://image.3001.net/images/20181212/1544614083_5c10f0c33cff3.png!small)

将这段字段拷贝出来，然后扔到010editor当中：

![图片7.png](https://image.3001.net/images/20181212/1544614276_5c10f18448d22.png!small)

发现这段字段很像一种文件格式，就是zip压缩包格式，因为它的开头是504B,也就是PK，而PK这个文件头就是压缩包的头，所以我们可以把这段字段保存为zip压缩包格式：

![图片8.png](https://image.3001.net/images/20181212/1544614100_5c10f0d4a00c6.png!small)

保存之后，就直接打开这个压缩包，看到里面有个文件，叫flag.txt：

![图片9.png](https://image.3001.net/images/20181212/1544614109_5c10f0ddc3cb0.png!small)

再点击打开，发现没有密码，直接就打开了，里面是隐藏的数据。

## 0×03 END

有时候不仅仅是在键位编码当中，也可能在usb鼠标坐标里，也是需要先用tshark抽取鼠标坐标数据信息，再运用python强大的作图功能对坐标数据进行绘制，以得到图形化隐藏数据。

 ***本文作者：ohhatmy，转载请注明来自FreeBuf.COM**

