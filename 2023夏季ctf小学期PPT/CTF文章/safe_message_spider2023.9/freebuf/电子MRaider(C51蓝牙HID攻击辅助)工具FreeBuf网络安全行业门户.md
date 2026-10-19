Github==>https://github.com/MartinxMax/MRaider

# 首页

MRaider (袭击者) 利用51芯片硬件蓝牙通讯近源渗透靶机

最低(不含外壳)纯元件总花费约 62元  
本次博主最高耗资总花费约 189元

# 硬件准备

## 硬件原理图

![请添加图片描述](https://image.3001.net/images/20230501/1682920787_644f55537f7650ef04156.png!small)

## 所需元件

1.STC51单片机芯片  
2.继电器模块  
3.蓝牙模块HC-05  
4.Attiny85(熟悉的小型HID设备)  
5.外壳[可选项]

## CAD图纸

![在这里插入图片描述](https://image.3001.net/images/20230501/1682920788_644f555439b1a4d010e3f.png!small)

## 焊接组装

![请添加图片描述](https://image.3001.net/images/20230501/1682920789_644f5555040980c9101e0.jpeg!small)![请添加图片描述](https://image.3001.net/images/20230501/1682920790_644f555640a40c33fd626.jpeg!small)

## 烧录文件设置PAYLOAD

1.将\C51文件中Main.hex烧录到51芯片中  
2.将\Attiny85文件中badusb.ino烧录到Attiny85芯片中(在文件中你可以自定义PAYLOAD)  
![请添加图片描述](https://image.3001.net/images/20230501/1682920791_644f5557a9cb2229f10d5.png!small)

# MRaider 工具

## 基础使用方法

`python3 MRaider.py -h`  
![请添加图片描述](https://image.3001.net/images/20230501/1682920792_644f555886ee5f9cb12a9.png!small)`-c`:指定COM口  
`-b`:指定波特率(默认9600)

## 执行PAYLOAD

1.攻击者主动连接蓝牙  
![在这里插入图片描述](https://image.3001.net/images/20230501/1682920793_644f5559692f708dd79e1.png!small)2.查看所属COM口,运行工具

`python3 MRaider.py -c COM4`

![请添加图片描述](https://image.3001.net/images/20230501/1682920794_644f555a0ac327e20e123.png!small)

# 安卓利用

你可以修改远程设备的MAC,再生成该应用,在调试蓝牙模块时输入`AT+ADDR?`即可查看该模块MAC地址

![在这里插入图片描述](https://image.3001.net/images/20230501/1682920794_644f555af1a9ae2e9e8d6.png!small)

下载Raider.apk安装

![在这里插入图片描述](https://image.3001.net/images/20230501/1682920796_644f555c012db9494b981.png!small)  
打开应用

![请添加图片描述](https://image.3001.net/images/20230501/1682920797_644f555d2b4a7ce05468e.jpeg!small)

# MRaider Android端演示

[Android端](https://live.csdn.net/v/288784)

# MRaider PC端演示

[PC端](https://live.csdn.net/v/284914?spm=1001.2014.3001.5501)

