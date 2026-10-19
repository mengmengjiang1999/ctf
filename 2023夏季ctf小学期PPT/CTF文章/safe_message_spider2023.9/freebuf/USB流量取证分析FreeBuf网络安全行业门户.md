**USB是 UniversalSerial
Bus（通用串行总线）的缩写，是一个外部总线标准，用于规范电脑与外部设备的连接和通讯，例如键盘、鼠标、打印机、磁盘或网络适配器等等。通过对该接口流量的监听，我们可以得到键盘的击键记录、鼠标的移动轨迹、磁盘的传输内容等一系列信息。  
**

在Linux中，可以使用lsusb命令，如图所示：

![](https://image.3001.net/images/20200328/1585391699_5e7f285373ec1.png!small)

我们这里主要演示USB的鼠标流量和键盘流量。Linux下的分析已经比较多了，下面的环境均在Windows下进行。

## 一、鼠标流量

### 1.1 特点分析

USB鼠标流量的规则如下所示：

![](https://image.3001.net/images/20200328/1585396331_5e7f3a6b93745.png!small)

### 1.2 使用Wireshark捕获和分析

要想使用Wireshark进行捕获，需要在安装时勾选上usbpcap工具选项，这样你的Wireshark中会有一个usb接口的选项，点击就可以进行抓包了。

![](https://image.3001.net/images/20200328/1585395907_5e7f38c338c80.png!small)

下图是我点击鼠标左键在屏幕上画圆圈的流量：

![](https://image.3001.net/images/20200328/1585394882_5e7f34c2673b2.png!small)

有的鼠标可能协议不是很标准，会导致分析不了。

Wireshark中捕获的USB流量集中在Leftover Capture
Data模块，我们可以使用tshark工具来进行提取。在Windows中安装tshark.exe的目录中输入：

tshark.exe -r b.pcap -T fields -e usb.capdata >b.txt
//这里b.pcap是我抓捕的数据包名字，b.txt是把提取的数据输入到b.txt中

![](https://image.3001.net/images/20200328/1585396142_5e7f39ae73ca0.png!small)

查看b.txt的内容会发现，因为有的数据包无用所以出现了很多空行，在进行下一步之前，我们需要把空行去掉。

![](https://image.3001.net/images/20200328/1585396230_5e7f3a0605eb0.png!small)

把空行去掉之后，根据鼠标流量的规则绘制像素坐标，最后通过画图工具（如matlab或者python的matplotlib进行绘制图像即可）

了解原理之后，为了方便，可以直接使用王一航大佬的工具进行提取，输入：

python UsbMiceDataHacker.py b.pcap LEFT //其中b.pcap是我抓捕的数据包的名字

运行之后就可以看到画面：

![](https://image.3001.net/images/20200328/1585395037_5e7f355d97408.png!small)

需要注意的是这个工具必须在python2环境下，同时保证安装了matplotlib和numpy。

## 二、键盘流量

### 2.1 特点分析

键盘数据包的数据长度为8个字节，击键信息集中在第3个字节，每次击键都会产生一个数据包。所以如果看到给出的数据包中的信息都是8个字节，并且只有第3个字节不为0000，那么几乎可以肯定是一个键盘流量了。

在USB协议的 文档中搜索 keyboard。就可以找到击键信息和数据包中16进制数据的对照表：

![](https://image.3001.net/images/20200328/1585396716_5e7f3bec4f900.png!small)

### 2.2 使用Wireshark捕获和分析

捕获的步骤与上面相似。下面以XCTF的高校战疫比赛中的一道例题（ez_mem&usb）来说明。

最后一步我们得到一个压缩包，通过密码进行解压后，得到一个键盘流量的文本文件：

![](https://image.3001.net/images/20200328/1585398256_5e7f41f072c1a.png!small)

根据键盘流量的特点，我们可以很容易判断出。

对照解码表使用代码进行提取即可，这里贴出代码：

    
    
    # coding:utf-8
    import sys
    import os
    
    usb_codes = {
        0x04: "aA", 0x05: "bB", 0x06: "cC", 0x07: "dD", 0x08: "eE", 0x09: "fF",
        0x0A: "gG", 0x0B: "hH", 0x0C: "iI", 0x0D: "jJ", 0x0E: "kK", 0x0F: "lL",
        0x10: "mM", 0x11: "nN", 0x12: "oO", 0x13: "pP", 0x14: "qQ", 0x15: "rR",
        0x16: "sS", 0x17: "tT", 0x18: "uU", 0x19: "vV", 0x1A: "wW", 0x1B: "xX",
        0x1C: "yY", 0x1D: "zZ", 0x1E: "1!", 0x1F: "2@", 0x20: "3#", 0x21: "4$",
        0x22: "5%", 0x23: "6^", 0x24: "7&", 0x25: "8*", 0x26: "9(", 0x27: "0)",
        0x2C: "  ", 0x2D: "-_", 0x2E: "=+", 0x2F: "[{", 0x30: "]}", 0x32: "#~",
        0x33: ";:", 0x34: "'\"", 0x36: ",<", 0x37: ".>", 0x4f: ">", 0x50: "<"
    }
    
    
    def code2chr(filepath):
        lines = []
        pos = 0
        for x in open(filepath, "r").readlines():
            code = int(x[6:8], 16)  # 即第三个字节
            if code == 0:
                continue
            # newline or down arrow - move down
            if code == 0x51 or code == 0x28:
                pos += 1
                continue
            # up arrow - move up
            if code == 0x52:
                pos -= 1
                continue
    
            # select the character based on the Shift key
            while len(lines) <= pos:
                lines.append("")
            if code in range(4, 81):
                if int(x[0:2], 16) == 2:
                    lines[pos] += usb_codes[code][1]
                else:
                    lines[pos] += usb_codes[code][0]
    
        for x in lines:
            print(x)
    
    
    if __name__ == "__main__":
        code2chr('E://CTF练习/杂项/18e4c103d4de4f07b33a42cb1f0eaa1d/00000122/usbdata.txt')  
    

当然也可以直接使用王一航大佬的代码，直接从pcap包提取出文件，省去了中间很多步骤，代码也很通用。

 ***本文作者：polemo，转载请注明来自FreeBuf.COM**

