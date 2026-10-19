![](https://image.3001.net/images/20190920/1568945470_5d84353e8d5ae.png!small)

## 前言

**一个公司的安全建设需要大量的物力、人力，由于网络安全在企业没有实际利益产出，常常在企业网络安全建设中，没有足够的投入（废话，投入没有经济效益回报，为什么要投入），但是企业网络安全建设不只是针对经济效益，它更像是一种保险（等出了事情，数据丢失，被网安抓典型处理），它更是一种对主业务的辅助（信息化辅助生产，甚至代替生产），但巧妇难为无米之炊，要对企业内网形成一套完整的纵深防御体系需要许多的商业化解决方案，无奈呼信息安全部门在一些企业中就是一个背锅的角色，为了能把锅抗好。。嗯，还是最好没锅吧！毕竟真的扛不动**

闲话少说，纵深防护体系的第一道就是下一代防火墙，下面是下一代防火墙的简单配置介绍：

## 一、说明

### 1.1 pfSense是什么

pfSense是基于FreeBSD的、开源中最为可靠（World's Most Trusted Open Source
Firewall）的、可与商业级防火墙一战（It has successfully replaced every big name commercial
firewall youcan imagine in numerous installations around the world）的防火墙。

简单点说pfSense就是一个操作系统形式的防火墙。更多介绍见：<https://www.pfsense.org/getting-started/>

## 二、pfSense安装

整个安装过程也不是很复杂，官方安装文档见：<https://www.netgate.com/docs/pfsense/install/installing-pfsense.html>

在虚拟机中安装使用（操作系统）freedbs 11 进行安装

### 2.1下载

下载地址：<https://www.pfsense.org/download/>

下载镜像iso即可

![](https://image.3001.net/images/20190919/1568893523_5d836a535d4a9.png!small)

### 2.2安装

首选创建一个虚拟机，其他的都无所谓但是系统一定要FreeBSD。

![](https://image.3001.net/images/20190919/1568895085_5d83706d58c88.png!small)

![](https://image.3001.net/images/20190919/1568893767_5d836b47760b1.png!small)

![](https://image.3001.net/images/20190919/1568895161_5d8370b947cc1.png!small)

![](https://image.3001.net/images/20190919/1568895203_5d8370e3d2467.png!small)

![](https://image.3001.net/images/20190919/1568895245_5d83710de7426.png!small)

到这步后所有的选项都是直接点击下一步，虚拟机创建完成后点击编辑虚拟机配置，添加网卡

![](https://image.3001.net/images/20190919/1568895713_5d8372e18caa6.png!small)

因为防火墙至少需要两块网卡，所以需要创建至少2块网卡，一个网卡作为lan口，一个网卡作为wan口（也可以多个网卡），我们留一个网卡作为wan口（NAT模式），一个作为lan口（主机模式或者自定义），登录界面配置在lan口上，网卡只要启动两块就好了。

![](https://image.3001.net/images/20190919/1568895825_5d8373514bccc.png!small)

![](https://image.3001.net/images/20190919/1568896358_5d8375662dba0.png!small)

![](https://image.3001.net/images/20190919/1568896222_5d8374de156db.png!small)

将ISO文件配置到虚拟光驱中，开启电源

![](https://image.3001.net/images/20190919/1568896424_5d8375a857f39.png!small)

回车接受版权声明

![](https://image.3001.net/images/20190919/1568896541_5d83761dc4ec5.png!small)

回车确认安装

![](https://image.3001.net/images/20190919/1568896634_5d83767a8301f.png!small)

选择键盘格式，默认是美国标准键盘，直接回车

![](https://image.3001.net/images/20190919/1568896685_5d8376adb5b7e.png!small)

选择文件系统，回车选择UFS，此步之后正式安装操作系统

![](https://image.3001.net/images/20190919/1568896746_5d8376ea2c38d.png!small)

![](https://image.3001.net/images/20190919/1568896789_5d8377156fa9e.png!small)

直接回车选择重启完成安装

![](https://image.3001.net/images/20190919/1568896827_5d83773b74793.png!small)

![](https://image.3001.net/images/20190919/1568896917_5d83779548648.png!small)

## 三、pfSense配置

### 3.1 设置pfsense接口

重启完成后会进入以下界面

![](https://image.3001.net/images/20190920/1568943403_5d842d2ba3b94.png!small)

不设置vlan（透明传输使用），设置wan口网卡，设置lan口网卡，最后输入Y进入系统

![](https://image.3001.net/images/20190920/1568943499_5d842d8b0a2cb.png!small)

查看自己设置的网卡的网段le0 口因为使用dhcp直接通过即可，le1口作为lan口，必须使用le1口网卡的网段地址（主机模式下的DHCP分配期间地址）

![](https://image.3001.net/images/20190920/1568943720_5d842e68d181d.png!small)

设置接口地址，设置wan和lan的地址（只需要设置一个就可以，设置完成后需要将web界面到底是使用哪一个地址进行登录），在控制界面按 2
进入地址设置界面，设置一个lan口地址（设置为192.168.192.0/24
网段的地址），关闭dhcp（避免IP地址冲突），设置lan口为web管理口地址

![](https://image.3001.net/images/20190920/1568943906_5d842f22edd7d.png!small)

设置完成后就可以登录了，通过上边14启动sshd后使用admin/pfsense也可以ssh登录操作系统

SSH账户名密码：admin/pfsense

### 3.2 web管理界面

访问设置为web登录的网卡地址，进行登录，默认用户名密码admin/pfsense

![](https://image.3001.net/images/20190920/1568943970_5d842f6279c3c.png!small)

第一次登录后有有几步主机名、dns、时区等相关初始化向导，看着填不会就直接next

![](https://image.3001.net/images/20190919/1568894624_5d836ea02098e.png!small)

最后finish

![](https://image.3001.net/images/20190919/1568894638_5d836eae453f7.png!small)

点击finish大约30秒后进入该界面

![](https://image.3001.net/images/20190920/1568944506_5d84317a1b722.png!small)

设置完成后设置中文显示，依次点击SystemGeneral>Setup>Language，在下拉框中找到Simplified,china，选择之后点击该页面最下方的save

![](https://image.3001.net/images/20190920/1568944623_5d8431efb5c10.png!small)

接下来就可以按照正常防火墙进行配置了

最后：在非常苛刻的条件下，可以使用三层路由的方式，使用各种开源的系统级防护系统，通过多个不同的主机网络将所有的设备串联起来，放置于网络的出口，以便进行内网安全防护，嗯，就是这样（说多了都是泪，都是被逼的。）

最后送上一些基础软件

 **vmware 15**

> 链接：<https://pan.baidu.com/s/1q0janMOCtIFbiApRfEgrfA>
>
> 提取码：hqou

 **pfsense**

> 链接：<https://pan.baidu.com/s/10Va4z6f69FkCjpY29X0JNA>
>
> 提取码：7o1w

 ***本文作者：寂静尘埃，转载请注明来自FreeBuf.COM**

