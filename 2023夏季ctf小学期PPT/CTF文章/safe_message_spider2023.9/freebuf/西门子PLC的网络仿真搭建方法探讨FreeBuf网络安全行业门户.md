## 一、前言

**在手上没有真实的西门子PLC设备情况的情况下，PLC本地仿真器可以为我们进行开关量和简单模拟量的程序仿真。但工控安全人员想在没有真实PLC的条件下获取S7通讯数据报文的时候，或者想测试第三方上位软件与西门子PLC通讯的时候，这种本地的PLC仿真器就无法胜任了，本文分享一种西门子PLC的网络仿真器搭建方法。**

## 二、搭建方法

这里我们准备两个虚拟机，操作系统都为win7 64位专业版：1、操作机（准备Snap7 Client
Demo工具及组态王软件，采用192.168.11.2IP地址）2、靶机（安装了step7 v5.5及plcsim v5.4
sp5，采用192.168.11.1IP地址）。

在靶机中打开SIMATIC Manager软件，新建项目test2，如下图：

![](https://image.3001.net/images/20200511/1589160809_5eb8ab691ce6b.png!small)

在新建项目test2点击插入新对象，并选择SIMATIC 300站点，如下图：

![](https://image.3001.net/images/20200511/1589160826_5eb8ab7ad530d.png!small)

分别点击SIMATIC300（1）>硬件，进入硬件配置界面，如下图：

![](https://image.3001.net/images/20200511/1589160850_5eb8ab928f202.png!small)

在HW Config界面下选择SIMATIC 300,并选择RACK-300下的Rail，如下图：

![](https://image.3001.net/images/20200511/1589160861_5eb8ab9d4c551.png!small)

在UR(0)对话框中的序号槽1中点击右键分别插入对象PS 307 2A，如下图：

![](https://image.3001.net/images/20200511/1589160880_5eb8abb0f0065.png!small)

在UR(0)对话框中的序号槽2中点击右键分别插入对象CPU 314C-2PN/DP V3.3，,并新建子网设置ip地址为本PC及的IP地址，如下图：

![](https://image.3001.net/images/20200511/1589160891_5eb8abbb5994a.png!small)

启动虚拟PLC,点击开始>所有程序>Siemens Automation>SIMATIC>STEP 7>S7-PLCSIM，如下图：

![](https://image.3001.net/images/20200511/1589160905_5eb8abc9f36e1.png!small)

进入S7-PLCSIM界面，选择PLCSIM(TCP/IP)，如下图：

![](https://image.3001.net/images/20200511/1589160915_5eb8abd3b61cb.png!small)

回到HW Config对话框，选择下载到模块，如下图：

![](https://image.3001.net/images/20200511/1589160929_5eb8abe1da8df.png!small)

![](https://image.3001.net/images/20200511/1589160939_5eb8abeb5cfa9.png!small)

待下载完成，PLCSIM会显示PLC的地址为之前设置的IP地址，如下图：

![](https://image.3001.net/images/20200511/1589160949_5eb8abf569b3b.png!small)

启动NetToPLCSIM，点击bin>NetToPLCSim.exe，进入如下图：

![](https://image.3001.net/images/20200511/1589160960_5eb8ac00b139a.png!small)

点击add,弹出station对话框，在Network IP Address及Plcsim IP
Address中选择IP地址为之前设置的ip地址，进入如下图：

![](https://image.3001.net/images/20200511/1589160979_5eb8ac137e020.png!small)

点击Start Server，PLC#001进入运行状态，表示PLC网络仿真器搭建成功进入如下图：

![](https://image.3001.net/images/20200511/1589160987_5eb8ac1baa6e2.png!small)

## 三、攻击测试

在操作机中打开Snap7 Client Demo工具，填写仿真PLC的IP地址如：192.168.11.1，点击Connect，如下图：

![](https://image.3001.net/images/20200511/1589160998_5eb8ac2618b92.png!small)

再在control下点击stop按钮即停止PLC的命令，如下图：

![](https://image.3001.net/images/20200511/1589161006_5eb8ac2e2349f.png!small)

查看靶机中仿真PLC的状态从run变为stop，同时可以用wireshark抓取其数据流量如下图：

![](https://image.3001.net/images/20200511/1589161028_5eb8ac44eaafd.png!small)

![](https://image.3001.net/images/20200511/1589161066_5eb8ac6ac6bd0.png!small)

![](https://image.3001.net/images/20200511/1589161086_5eb8ac7e8f37b.png!small)

也可以在python中构建STOP包进行测试，如下图：

![](https://image.3001.net/images/20200511/1589161093_5eb8ac85e242a.png!small)

## 四、第三方上位软件通讯测试

在靶机（192.168.11.1）的仿真PLC建立了这样一段简单图形图代码，一个简单的设备启停控制逻辑程序，%M0.0、%M0.1是指PLC的M类型的寄存器，0.0、0.1是M寄存器的某两个偏移地址，对应中间变量。%Q0.0是PLC的Q类型的寄存器，0.0是Q寄存器的某个偏移地址。在这个控制程序中，%M0.0（变量名为start）对应是监控画面上的启动按钮，进行对设备的启动操作，%M0.1（变量名为stop）对应是监控画面上的停止按钮，进行对设备的停止操作。%Q0.0（变量名为out），对应PLC的输出，即将控制信号输出给设备。如下图：

![](https://image.3001.net/images/20200511/1589161104_5eb8ac90745f7.png!small)

程序下载到仿真PLC后，对梯形图代码进行在线监控，这时输出为0，如下

![](https://image.3001.net/images/20200511/1589161112_5eb8ac981d99c.png!small)

在操作机（192.168.11.2）中定义仿真PLC的IP地址及寄存器的地址，如下图：

![](https://image.3001.net/images/20200511/1589161123_5eb8aca3009a1.png!small)

![](https://image.3001.net/images/20200511/1589161130_5eb8acaa4ac4d.png!small)

定义监控画面如下：

![](https://image.3001.net/images/20200511/1589161139_5eb8acb371c61.png!small)

按下start按钮，圆形显示变为绿色，证明我们按钮发出的指令，仿真PLC收到启动信号，将输出置为1，并将仿真PLC输出的结果反馈到监控画面，同时我们监控靶机中仿真PLC的程序，我们发现仿真PLC输出也是为1，证明操作机中组态王上位机与靶机中的虚拟机通讯成功，如下图

![](https://image.3001.net/images/20200511/1589161151_5eb8acbf7f9dc.png!small)

![](https://image.3001.net/images/20200511/1589161161_5eb8acc94f1a0.png!small)

同时我们可以获取操作机的组态王（192。168.11.2）与靶机PLC仿真器（192168.11.1）的通讯报文，各类功能码的数据报文，根据具体的操作。

![](https://image.3001.net/images/20200511/1589161173_5eb8acd5b0d60.png!small)

## 五、总结

本文通过研究西门子PLC的网络仿真搭建方法，为工控安全人员研究西门子s7协议提供一个便捷、实惠的渠道，无需花费大量的资金采购真实的PLC设备，同时也可为PLC工程师提供一种测试第三方上位软件与西门子通讯的方法，更为重要的是，这种西门子PLC的网络仿真搭建方法，可以胜任多人在局域网络中对西门子PLC的安全研究工作（例如实训平台），只需启动更多的靶机和操作机即可。

 ***本文作者：thx0405，转载请注明来自FreeBuf.COM**

