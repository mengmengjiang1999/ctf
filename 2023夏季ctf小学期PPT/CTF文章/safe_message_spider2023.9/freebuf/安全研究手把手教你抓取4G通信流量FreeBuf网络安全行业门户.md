## **概述**

随着IoT时代的到来，万物互联的场景离我们也唾手可及，随之而来的新技术、新场景也会来带新的挑战。目前国内对4G/5G网络的研究文章较少，并且该领域的研究也有一定的入门门槛。本文介绍了一种实现一个私人LTE网络环境的方法，并以此分析4G网络架构和通信流量。

##  **环境** **准备**

###  **工具介绍**

USIM测试卡： 可烧录自定义IMSI、Ki、OPC、OP等数据的空白USIM卡。淘宝有售

PCSC读卡器： 用来读写USIM卡，GemaltoUSB Smart Card Reader

智能卡转接器： 方便连接各类形状的USIM卡和读卡器

国际版Android手机： 之所以使用国际版，是因为国际版手机对运营商和信号频段限制较小。

BladeRF： 用来作为基站发射和接收4G信号。

![](https://image.3001.net/images/20210616/1623842615_60c9df3737d01951b84b2.png!small)

###  **USIM** **卡烧写**

IMSI作为USIM的身份表示，也指出该USIM卡属于哪个国家的哪个运营商。

 **关键术语**

> IMSI: 国际移动用户识别码，USIM卡的身份标识
>
> MCC: 移动设备国家代码，中国为460
>
> MNC: 移动设备网络代码，每个运营商有对应的MNC，比如中国移动的MNC有02、00、07

![](https://image.3001.net/images/20210616/1623842638_60c9df4ec856837749d90.png!small)

 **IMSI** **和** **MCC、MNC** **的对应关系：** IMSI前五位对应的就是MCC和MNC

> OP: Operator Code : 分配给运营商，用于3G和4G的密钥生成算法。中国运营商通常在每个省公司使用唯一的OP
>
> KI: 鉴权密钥，用于用户身份的鉴权。每个USIM卡有一个唯一的Ki
>
> OPC: 通过使用特定于 SIM 的（“RijndaelEncrypt”）算法从 OP 和 Ki生成的最终密钥。

### 开始烧录

注：这里使用的烧录软件是由USIM测试卡商家提供，如果没有类似的软件，也可使用pysim等开源软件烧录。

准备IMSI、KI、OPC，这里的KI和OPC填入32位任意数值即可，IMSI为90170开头的任意数值。这三个关键信息填写好之后，开始烧录。

![](https://image.3001.net/images/20210616/1623842682_60c9df7ab1e2578b65ad5.png!small)

## 基站搭建

### 4g网络术语

> UE: user equipment (UE) is any device used directly by an end-user to
> communicate. 通常指用户的手机
>
> EPC: Evolved Packet Core (EPC) is a framework for providing converged voice
> and data on a 4G Long-Term Evolution (LTE) network. 可以简单理解为4G网络架构中处理数据的核心组件
>
> ENB: E-UTRAN Node B, also known as Evolved Node B (abbreviated as eNodeB or
> eNB), is the element in E-UTRA of LTE that is the evolution of the element
> Node B in UTRA of UMTS. 可以简单理解为处理通信信号的组件。

![](https://image.3001.net/images/20210616/1623842726_60c9dfa6ee250a07423da.png!small)

注： 图片来自[1]

### srsRAN搭建

介绍：srsRAN is a free and open-source 4G and 5G software radio suite.

搭建教程参考：<https://docs.srsran.com/en/latest/general/source/1_installation.html>

 **关键步骤：**

srsRAN安装完成后，需要编辑以下三个文件

  * conf
  * conf
  * csv

需要将MMC和MCC、APN等信息填入epc.conf和enb.conf。将IMSI和KI、OPC等信息填入user_db.csv。具体的配置信息参考

<https://docs.srsran.com/en/latest/app_notes/source/cots_ue/source/index.html#conf-files>

### 接入Internet

启动srsepc和srsenb程序后，程序会自动建立一张新的网卡srs_spgw_sgi，
手机访问LTE基站的流量都会从这张网卡上流转，为了使手机能够访问Internet，需要帮该网卡进行流量转发，转发到可以访问公网的网卡上。

 **网络转发设置**

srsRAN/srsepc目录下提供了自动设置流量转发的脚本：srsepc_if_masq.sh

如果脚本无效，可以尝试手动设置网络转发

    
    
    > sudo iptables -A FORWARD -i srs_spgw_sgi -o [your_card] -j ACCEPT
    
    > sudo iptables -A FORWARD -i [your_card] -o srs_spgw_sgi -m state --state ESTABLISHED,RELATED -j ACCEPT
    
    > sudo iptables -t nat -A POSTROUTING -o [your_card] -j MASQUERADE

##  **设置基站上行下行频率**

不同的运营商、不同的网络制式使用的通信频率也不一样，为了可以让设备连接到我们的私人基站，需要将基站的通信频率设置为设备支持的通信频率。

###  **核心概念**

载波频点号（EARFCN）

为了唯一标识某个LTE系统所在的频率范围，仅用频带和信道带宽这两个参数是无法限定的，比如中移动的频带40占了50M频率范围，而LTE最大的信道带宽是20M，那么在这个50M范围里是没有办法限定这个20M具体在什么位置，这个时候就要引入新的参数：载波中心频率Fc（简称载波频率）。

![1623842931_60c9e0735f0517ff2f6d2.png!small?1623842931871](https://image.3001.net/images/20210616/1623842931_60c9e0735f0517ff2f6d2.png!small?1623842931871)

通过上图可以看出，通过频带Band、信道带宽Bandwidth和载波频率Fc这三个值，就可以唯一确定LTE系统的具体频率范围了。由于载波频率Fc是一个浮点值，与整形类型相比，不好用于空口的传输，因此在协议制定的时候，使用载波频点号来表示对应的载波频率Fc。

载波频点号，又叫EARFCN，全称是E-UTRA Absolute Radio Frequency Channel
Number，绝对无线频率信道号，使用16bit表示，范围是0-65535。因为要用EARFCN来指代载波频率Fc，因此这两个参数之间必须一一对应，可以互相转换。载波频率Fc和EARFCN之间的关系式如下所示，其中Fdl和Ful分别表示下行和上行具体的中心载波频率，Ndl和Nul则分别表示下行和上行的绝对频点号。

![1623842960_60c9e090096b4027f114d.png!small?1623842960785](https://image.3001.net/images/20210616/1623842960_60c9e090096b4027f114d.png!small?1623842960785)

 **注： 核心概念内容摘自[2]**

### 获取运营商网络EARFCN

利用www.cellmapper.net查询相应运营商的earfcn， 从图中可以看出中国联通的为1650。

![1623843133_60c9e13d1682dc07e7dbc.png!small?1623843135283](https://image.3001.net/images/20210616/1623843133_60c9e13d1682dc07e7dbc.png!small?1623843135283)

### 利用earfcn计算上行下行频率

使用earfcn计算器(https://5g-tools.com/4g-lte-earfcn-calculator/) 可以得出earfcn
1650对应的上行和下行频率为1850、1755

## 将手机接入4G网络

在手机的设置中，选择移动网络-手动选择网络，
在本示例中，自己搭建的网络显示为90170，选择后即可加入该网络。此时的手机信号已经通了。接下来给手机配置APN来让手机可以访问Internet。

![](https://image.3001.net/images/20210616/1623843187_60c9e173a37a550de2e20.png!small)

### 添加APN

在手机网络设置里，添加APN， APN的名称为我们之前在epc.conf中设置的名称，本示例为srsapn。

![](https://image.3001.net/images/20210616/1623843233_60c9e1a118570121dd682.png!small)

### 测试网络连接情况

开启手机调试模式，使用adb shell访问手机命令行。输入ifconfig命令，可以看到rmnet_data1网卡已经获取到IP地址
172.16.0.2， rmnet_data对应的是移动网络，并且可以访问172.16.0.1。

![](https://image.3001.net/images/20210616/1623843268_60c9e1c45da2bf00e7e75.png!small)

## 监听LTE Internet流量

在运行srsepc的主机上使用wireshark监听srs_spgw_sgi网卡，即可监听LTE Internet流量。

# 提升网络传输速率

可通过MIMO技术提升网络传送速率，如果RF设备支持MIMO，可在srsenb中配置使用。

MIMO：使用多个TX/RX通道发送和接收信号，提高传输速率。

![](https://image.3001.net/images/20210616/1623843311_60c9e1ef43c9a66749f78.png!small)

注：图片来自于网络

# 参考

>
> <https://docs.srsran.com/en/latest/app_notes/source/cots_ue/source/index.html#introduction>
>
> <https://blog.csdn.net/m_052148/article/details/51322260>

##  **免责** **声明**

本篇内容仅供学习交流，不得作为非法用途，本文章谨以协助读者对某些技术专题进行研究。

