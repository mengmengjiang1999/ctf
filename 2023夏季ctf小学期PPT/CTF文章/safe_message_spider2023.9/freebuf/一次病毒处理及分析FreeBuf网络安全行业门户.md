在不久前火绒杀毒一直告警我的电脑被攻击，这篇文章分享了病毒处理及分析过程。

## 攻击告警

火绒告警提示电脑进程在访问一个恶意ip，通过微步在线、奇安信威胁情报查询到此ip地址是黑客远程木马服务器地址。

![1602294382_5f81126e62ff93353aa21.png!small](https://image.3001.net/images/20201010/1602294382_5f81126e62ff93353aa21.png!small)

![1602294421_5f8112954bd3f8c0102b9.png!small](https://image.3001.net/images/20201010/1602294421_5f8112954bd3f8c0102b9.png!small)

通过分析xxx进程，发现此进程是虚拟机网络进程。

## 虚拟机溯源

平时做渗透测试会在虚拟机里面进行，可能是下载了一些恶意软件导致电脑感染病毒。

使用netstat -ano查询网络连接，发现pid：1412的进程在访问恶意地址

![1602294139_5f81117b3c38c8b20057e.png!small](https://image.3001.net/images/20201010/1602294139_5f81117b3c38c8b20057e.png!small)

使用tasklist | findstr "1412"查询相关进程信息。

![1602294563_5f81132386fc747d4160e.png!small](https://image.3001.net/images/20201010/1602294563_5f81132386fc747d4160e.png!small)

使用任务管理器可以查询该病毒文件具体的安装目录。

![1602294741_5f8113d5deff48a87a478.png!small](https://image.3001.net/images/20201010/1602294741_5f8113d5deff48a87a478.png!small)

发现该病毒安装在Windows目录下

![1602294773_5f8113f5198b0c4ac2d72.png!small](https://image.3001.net/images/20201010/1602294773_5f8113f5198b0c4ac2d72.png!small)

## 沙箱运行分析

此次使用微步在线云沙箱进行检测，[检测结果点击查看](https://s.threatbook.cn/report/file/30949dafd351e393762424562edf77347e7646097019a22382f8e7bfe09e3968/?sign=history&env=win7_sp1_enx86_office2013)

病毒软件在运行后进行文件拷贝，将木马拷贝到Windows目录下。

![1602295812_5f8118044dca257864757.png!small](https://image.3001.net/images/20201010/1602295812_5f8118044dca257864757.png!small)

连接了远控服务器。

![1602295914_5f81186a4c3bcb7e286ca.png!small](https://image.3001.net/images/20201010/1602295914_5f81186a4c3bcb7e286ca.png!small)

![1602295940_5f8118847cb44500f4893.png!small](https://image.3001.net/images/20201010/1602295940_5f8118847cb44500f4893.png!small)

创建服务使得病毒每次开机自启动。

![1602295766_5f8117d642de496e275cf.png!small](https://image.3001.net/images/20201010/1602295766_5f8117d642de496e275cf.png!small)

## 逆向分析

首先使用PEiD查询病毒是否进行了加壳，经过查询发现没有加壳。

![1602296057_5f8118f914cdfe90b7e1a.png!small](https://image.3001.net/images/20201010/1602296057_5f8118f914cdfe90b7e1a.png!small)

可以使用od直接分析。

![1602296206_5f81198e1ad98f7822bbc.png!small](https://image.3001.net/images/20201010/1602296206_5f81198e1ad98f7822bbc.png!small)

![1602296250_5f8119badfc539ebd013b.png!small](https://image.3001.net/images/20201010/1602296250_5f8119badfc539ebd013b.png!small)

进行反编译后可以看到是灰鸽子远程控制软件。

![1602296320_5f811a00669ec0a97c0ed.png!small](https://image.3001.net/images/20201010/1602296320_5f811a00669ec0a97c0ed.png!small)

## 病毒处置

通过微步在线云沙箱病毒运行行为可以针对把服务删除、病毒删除。

![1602296401_5f811a5142a82455522e7.png!small](https://image.3001.net/images/20201010/1602296401_5f811a5142a82455522e7.png!small)

