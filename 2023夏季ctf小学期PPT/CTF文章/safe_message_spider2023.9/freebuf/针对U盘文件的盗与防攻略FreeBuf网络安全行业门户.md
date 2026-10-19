近年来，使用U盘作为介质完成的网络攻击屡见不鲜。

> 2010年的震网病毒事件，使用了基于U盘来触发的windows 快捷方式漏洞;
>
> 2014年安全研究员在BlackHat上公布了基于U盘的BadUsb攻击，该攻击也基于U盘这个介质;
>
> 2021年，在BlackHat Europe上，安全研究员利用USB协议栈的Double Free漏洞控制了linux
> 系统，这个攻击同样也基于U盘触发。

以上几种方法都是通过USB设备获得了主机控制权限，本文介绍一种在不获取主机控制权限条件下对U盘文件进行读取的方法。该方法需要一个特制的U盘，在使用这个U盘进行文件的存储、拷贝过程中，可在用户不知情的情况下将U盘里的文件发送给远端的接收者。

## 原理

一个U盘主要由主控板（USB控制器）、FLASH存储等组成。FLASH分为2部分，一部分是用户可见的存储区，另一部分是用户不可见的固件区域。

![](https://image.3001.net/images/20220923/1663930148_632d8f24ecbd0dd6eb31c.png!small)图1.1

  

当U盘插入电脑后，固件区域的代码便开始运行，固件区域的代码主要为USB协议栈代码，这些代码用来响应主机端（HOST端）发起的各种请求，请求包括查看设备信息、设备容量、读写文件等。如下图1.2所示，U盘接入电脑后，电脑主机会向U盘发起一些请求，U盘的固件代码会对这些请求做出响应。

![](https://image.3001.net/images/20220923/1663930151_632d8f2744d19dfe0141b.png!small)图1.2

当主机端向设备端发起请求时，一个"诚实"的U盘（设备端固件）会如实地回答自己的设备信息及其状态，例如，设备名字、设备类型（存储设备，键盘鼠标设备）、设备容量等，而一个"不诚实"的U盘会伪造这些内容来欺骗主机端。用于HID攻击，BADUSB攻击的U盘便属于“不诚实”的U盘，它们在响应主机的请求时，都欺骗了主机设备，把自己伪造成了键鼠设备，在获取主机的信任后，通过执行任意键鼠操作来完成一些恶意操作。

为了达到将U盘的内容发送到远程接收端的目的，需要修改U盘控制器的固件代码，在固件代码中添加文件传输的功能。除此之外，还需要一个支持无线通信功能的U盘控制器，该控制器同时支持WIFI功能和USB功能，通过控制器的WIFI功能，U盘能够连接周围的热点，并且将存储在FLASH中的文件内容发送到文件接收端。

为了实现这个功能，笔者选取了同时支持WIFI和USB功能的芯片作为控制器芯片，芯片同时支持向芯片刷入自定义固件。基于该芯片的开发板更便于开发U盘相关的应用，例如开发制作USB
HID设备、USB存储设备等。

![](https://image.3001.net/images/20220923/1663930151_632d8f27f40c5f398effb.png!small)图1.3

该开发板中需要关注的有USB_DEV，USB-to-UART，Micro SD 卡，ESP-S3-MINI-1。USB_DEV
interface是一个TYPEA公口，可以连接其它USB主机，ESP-S3-MINI-1模组是通用型Wi-Fi
MCU模组，具有丰富的外设接口，内部包含了ESP32S3芯片。Micro SD卡 Slot可以插入TF卡，ESP32S3芯片通过4-线
SDIO和SPI接口读写TF卡里的内容。USB-to-UART接口是Micro-USB接口，可用作开发板的供电接口，可烧录固件至芯片，也可作为通信接口，通过板载USB转UART桥接器与芯片通信。

## 实现细节

本章节介绍如何基于开发板制作一个具有WIFI联网功能的U盘，该U盘具有普通U盘的存储等功能，同时支持将U盘里文件发送给其它接收者。

 **1.下载安装基于ESP-IDF的交叉编译环境**

参考链接如下：https://docs.espressif.com/projects/esp-idf/zh_CN/latest/esp32/get-started/windows-setup.html#get-started-windows-first-steps

安装成功之后，会在桌面生成ESP-IDF X.X CMD快捷方式，双击快捷方式如果显示如下命令行窗口，代表交叉编译环境安装成功了。

![](https://image.3001.net/images/20220923/1663930152_632d8f28ba295c954c0f4.png!small)

 **2.** **下载esp-iot-solution**

esp-iot-solution是专门针对物联网应用的示例程序。

git 克隆 --递归 https://github.com/espressif/esp-iot-solution

详细的环境配置步骤参考：

https://github.com/espressif/esp-iot-solution

esp-iot-solution中包含一个usb_msc_wireless_disk示例，该实例会生成一个具有WIFI的 U盘。

 **3.对无线U盘进行一些配置工作**

切换到C：\Espressif\frameworks\esp-idf-v4.4\esp-iot-solution\examples\usb\device\usb_msc_wireless_disk>目录;

usb_msc_wireless_disk项目是一个无线U盘的示例程序，需要在编译之前进行一些基本的配置。

idf.py set-target esp32s3 //设计芯片的类型是esp32s3;

idf.py menuconfig// 配置一些选项，例如，使用内部flash还是外部sdcard，wifi的类型，AP/STA。

![](https://image.3001.net/images/20220923/1663930153_632d8f295e2340909574d.png!small)

选择使用External SDCcard存储，U盘的存储空间比更大（接近TF卡的容量），如果使用Internal
Flash，存储空间只有1.4MB，空间比较小。另外，还需要配置U盘的联网方式，STA模式代表U盘会主动连接一个周围的热点，在此模式下，需要设置WIFI的名字和密码，
U盘启动会自动连接该WIFI。AP模式代表U盘会生成一个WIFI热点，可以让电脑、手机等其它设备接入。

![](https://image.3001.net/images/20220923/1663930153_632d8f29c74dbea63c572.png!small)

 **4.编程将U盘文件发送到服务端**

在完成上面配置之后，还需要修改源程序的代码。在U盘初始化完成之后，遍历U盘文件，将U盘里的文件发送给接收端。usb_msc_wireless_disk源程序代码通过运行一个file
server来实现文件共享的功能，其它电脑可以经由这file server 可以查看U盘的文件内容。可以通过修改源程序逻辑，使其主动向远端接收者发送文件。

 **5.编译程序并将固件刷入开发板**

完成源程序的编码后，接下来就是执行 idf.py build 编译固件。

![](https://image.3001.net/images/20220923/1663930154_632d8f2a439b41ef00c13.png!small)

Idf.py –p COMx
flash便可以把编译好的固件刷到开发板，开发板再插入电脑之后就会被识别成一个USB存储设备，当把文件拷贝到这个U盘，该文件就会被发送出去，造成文件内容泄露。

想要制作一个具有联网功能并且外观像普通U盘的USB设备，只需通过PCB画板进行硬件设计，把芯片设计到U盘里，一个“不诚实”的U盘便诞生了。

## 防护手法

对于普通用户来说，想要防范此类攻击需要提高个人安全意识。不要随便使用不明来源的U盘，也不要轻易接受并使用他人赠送的U盘。尽量从正规渠道购买，切忌从不可信的第三方渠道/二手市场购买U盘。

除此之外，我们在插入使用新U盘时，可以留意下周围是否有新增可疑WIFI热点，如果没有新增可疑WIFI热点，那么基本上可以确定我们并没有受到此类型攻击。

