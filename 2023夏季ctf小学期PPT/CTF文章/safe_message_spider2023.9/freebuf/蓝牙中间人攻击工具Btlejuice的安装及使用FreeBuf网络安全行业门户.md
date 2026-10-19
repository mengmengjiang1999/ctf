## 前言

最近因为项目测试的原因需要做蓝牙的Man-in-the-Middle（中间人攻击），有人推荐了一款工具[Btlejuice](https://github.com/DigitalSecurity/btlejuice
"btlejuice_github")，但在实际搭建环境的时候发现总会出现问题，所有分享成功搭建的过程顺便也留个记录

## 前期准备

1.两个蓝牙dongle，按需求准备4.0或5.0的dongle（蓝牙适配器），我这边因为项目的原因要用5.0的，但是4.0的在搭建的时候问题不会很多。

2.两台Linux主机，可以使用虚拟机进行搭建，建议新建ubuntu系统，我这边是kali+ubuntu。

## 搭建过程

### 1.node.js安装

如果系统预装node.js要先清除掉，再输入以下命令进行安装node.js的环境：

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh |
bash

再使用nvm安装node.js，目前在我安装过的版本中v8是不就契合btlejuice，所以我们现在安装的版本是8.9.0

nvm install 8.9.0

### 2.安装依赖及btlejuice

安装蓝牙的相关开发环境，有可能系统会自带，不过还是要确认一次

sudo apt install bluetooth bluez libbluetooth-dev libudev-dev build-essential

安装btlejuice

npm install -g btlejuice --unsafe-perm

选项-g是全局安装，由于btlejuice好像很久没有人维护，所以直接安装会报发现漏洞导致无法安装，所以要加选项--unsafe-perm

检查是否正确安装可以尝试本地进行代理并连接代理

开启代理

btlejuice-proxy

![1636536100_618b8f24756318e0296ec.png!small?1636536102056](https://image.3001.net/images/20211110/1636536100_618b8f24756318e0296ec.png!small?1636536102056)

连接代理并开启网页UI，注意默认是8080但是执行命令的时候是显示8000这个应该是命令行回显的时候写错了。

btlejuice -u [ip] -w //ip是指开启代理服务的主机的ip，-w是开启UI，如果是本地的话直接-w就可以了

![1636536222_618b8f9e7a0af9bb1a20b.png!small?1636536224134](https://image.3001.net/images/20211110/1636536222_618b8f9e7a0af9bb1a20b.png!small?1636536224134)

访问http://localhost:8080

![1636536358_618b9026ba811ecd4b64e.png!small?1636536360318](https://image.3001.net/images/20211110/1636536358_618b9026ba811ecd4b64e.png!small?1636536360318)

### 3.搭建整套环境

两个主机都要安装btlejuice

VM1:作为代理的主机

插入蓝牙dongle并确认状态

hciconfig

![1636536567_618b90f7069d5bca0fc75.png!small?1636536568589](https://image.3001.net/images/20211110/1636536567_618b90f7069d5bca0fc75.png!small?1636536568589)

如果显示的是DOWN，使用命令将其运行起来

hciconfig hci0 up

要注意如果BD
Address显示的全是0，那要确认一下你购买的这个dongle是不是支持Linux系统的，如果支持再确认一下有没有安装驱动，建议购买dongle时要进行确认。

然后开启蓝牙服务

service bluetooth start

开启btlejuice代理

btlejuice-proxy

VM2:作为btlejuice的客户端去连接代理VM1

同样的和VM1确认dongle的状态，但不同的是，VM2要关闭蓝牙服务

service bluetooth stop

使用btlejuice客户端并开启网页UI

btlejuice -u [ip] -w //ip是V1代理机的IP

打开浏览器访问http://localhost:8080，点击下图按钮对附近的蓝牙设备进行搜索

![1636537115_618b931b02bf6928628d9.png!small?1636537116616](https://image.3001.net/images/20211110/1636537115_618b931b02bf6928628d9.png!small?1636537116616)

双击选择你想要攻击的设备后，再用其他蓝牙设备进行正常配对，但是目前我还没有成功过。由于Btlejuice这个工具有点老且没有人在继续维护了，而且好像限制也比较大，目前我查到使用这个工具成功的案例好像只有一个智能灯泡的。

参考来源：

技术分享 |
如何使用BtleJuice黑入BLE智能电灯泡：<https://www.freebuf.com/articles/wireless/180716.html>

Btlejuice：https://github.com/DigitalSecurity/btlejuice

