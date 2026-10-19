# windows server 2016 下域环境的搭建

* * *

在搭建之前简单介绍一下基础知识：  
1.工作组：默认模式，人人平等，不方便管理  
2.域：人人不平等，集中管理，统一管理

  * 域中计算机的分类：

域控制器、成员服务器、客户机、独立服务器

  * 域的部署：

  1. 安装域控制器-就生成了域环境 安装了活动目录-就生成了域控制器

  2. 活动目录：Active Directory =AD是指域环境中提供目录服务的组件。目录用于存储有关网络对象的信息。活动目录存储的是网络中所有资源的快捷方式，用户可以通过寻找快捷方式来定位资源。

  * 活动目录:

  1. AD

  2. 特点：集中管理/统一管理

本次搭建过程需要在虚拟机下进行，需要虚拟机软件（例如VMware），windows 2016 Server（作为域控制器），windows 7
，windows server 2008 R2.

这里需要注意以下所有环境都是属于链接克隆的，所以可能会遇到SID相同的错误，可参考http://www.donny.com.cn/tech/201908163.html来进行解决。

一、环境介绍  
二、搭建主域  
1.创建主域  
2.创建域普通用户  
三、搭建子域  
1.创建子域  
2.创建子域用户  
四、搭建辅域  
五、搭建独立域  
1.创建财务部电脑系统  
2.创建财务部电脑核心资料系统  
六、总结

## 一、环境介绍 ：

1.这里用拓扑图进行展示：  
![image](https://image.3001.net/images/20210616/1623814057_60c96fa94fbc42ea5547a.jpg!small)

2.所有环境配置如下  
（1）主域：  
计算机全名：AD01  
域：ice.com  
ip:10.10.88.6 255.255.255.0  
默认网关：10.10.88.1  
首选dns服务器：10.10.88.6  
DNS2:10.10.88.8  
计算机名：AD01  
域：ice.com  
用户名：ICE\Administrator

（2）辅域：  
计算机全名：fuyu.ice.com  
域：ice.com  
ip:10.10.88.8 255.255.255.0  
默认网关：10.10.88.1  
首选dns服务器：10.10.88.8  
DNS2:10.10.88.6

（3）域用户：  
计算机名：user1.ice.com  
域：ice.com  
ip:10.10.88.104 255.255.255.0  
默认网关：10.10.88.1  
首选dns服务器：10.10.88.6  
用户名：USER0\ice  
计算机全名：USER0.ice.com

（4）子域：  
计算机全名：ziyu.ziyu.ice.com  
域：ziyu.ice.com  
ip:10.10.88.12 255.255.255.0  
默认网关：10.10.88.1  
首选dns服务器:10.10.88.6  
DNS2:10.10.88.6  
财务部共享：IP 10.10.99.5 255.255.255.0  
默认网关：10.10.99.1  
首选DNS服务器：10.10.99.5  
用户名：ZIYU0\administrator

（5）子域用户：  
ip:10.10.88.22 255.255.255.0  
默认网关：10.10.88.1  
首选dns服务器:10.10.88.6  
外网ip:192.168.1.13

（6）财务部电脑：  
ip:10.10.99.22 255.255.255.0  
默认网关：10.10.99.1  
DNS：10.10.99.5  
ip:172.16.5.2 255.255.255.0  
默认网关：172.16.5.1  
DNS：172.16.5.2

（7）财务部存放核心资料：  
IP：172.16.5.5  
子网掩码：255.255.255.0  
网关：172.16.5.1  
DNS1:172.16.5.2

* * *

## 二、搭建主域：

1.设置ip  
![image](https://image.3001.net/images/20210616/1623814135_60c96ff76024491a50a1d.jpg!small)

2.点击服务器管理器-->添加角色和功能-->下一步-->选择基于角色或基于功能的安装之后点击下一步-->下一步  
![image](https://image.3001.net/images/20210616/1623814159_60c9700f66f894606f1d1.jpg!small)

3.勾选Active Directory 域服务-->点击添加功能-->下一步  
![image](https://image.3001.net/images/20210616/1623814187_60c9702b9e3a5bf978aeb.jpg!small)

4.直到确认这步点击安装等待  
![image](https://image.3001.net/images/20210616/1623814209_60c970416db2bf329c800.jpg!small)

5.成功安装之后点击将此服务器提升为域控制器  
![image](https://image.3001.net/images/20210616/1623814222_60c9704eaaf48a5bfd9e4.jpg!small)  
6.选择添加新林-->并定义根域名-->下一步  
![image](https://image.3001.net/images/20210616/1623814242_60c9706248891367e28f2.jpg!small)  
![image](https://image.3001.net/images/20210616/1623814253_60c9706d3b3dab433ef8d.jpg!small)

7.直接点击下一步  
![image](https://image.3001.net/images/20210616/1623814306_60c970a24b3c768fe3bd9.png!small)  
![image](https://image.3001.net/images/20210616/1623814319_60c970af04e1814283e8f.jpg!small)  
![image](https://image.3001.net/images/20210616/1623814388_60c970f40b4ec8b7c68c6.png!small)

8.检查此计算机是否满足安装AD 域服务器的条件，满足可点击安装  
![image](https://image.3001.net/images/20210616/1623814416_60c971101368f1e24fe05.jpg!small)

最后重启计算机即可！

### 创建域普通用户:

1.配置IP：  
![image](https://image.3001.net/images/20210616/1623825014_60c99a767788965fef2db.jpg!small)

2.点击计算机-->右键属性更改-->加入ice.com主域-->点击确定，输入主域的账户名与密码为：administrator bing....123  
![image](https://image.3001.net/images/20210616/1623825046_60c99a96458c14032f85c.jpg!small)  
![image](https://image.3001.net/images/20210616/1623825059_60c99aa373a30e6b41083.png!small)

* * *

## 三、搭建子域

1.配置IP：  
![image](https://image.3001.net/images/20210616/1623825081_60c99ab9d26159cbb5d6c.jpg!small)  
![image](https://image.3001.net/images/20210616/1623825095_60c99ac7028e66deca7bb.png!small)

2.点击添加角色功能和向导选择ad域服务（与上一步相似）  
![image](https://image.3001.net/images/20210616/1623825121_60c99ae1248530e3adac6.jpg!small)

3.开始配置选择将域添加到现有林  
![image](https://image.3001.net/images/20210616/1623825153_60c99b01c5ae2ec314aa6.jpg!small)  
![image](https://image.3001.net/images/20210616/1623825175_60c99b179dad36482d570.png!small)

4.点默认下一步....直到安装界面点击安装  
![image](https://image.3001.net/images/20210616/1623825198_60c99b2e410ec36d35c79.jpg!small)

5.安装成功之后自动重启计算机  
![image](https://image.3001.net/images/20210616/1623825215_60c99b3fcd11f41894955.jpg!small)

### 创建子域用户：

1.配置IP：  
![image](https://image.3001.net/images/20210616/1623825235_60c99b5314003a8e22e8b.jpg!small)

2.点击我的电脑右键属性-->选择域  
![image](https://image.3001.net/images/20210616/1623825258_60c99b6a731fc1ff34107.jpg!small)

3.加入成功：  
![image](https://image.3001.net/images/20210616/1623825289_60c99b8960c65a89f6da8.jpg!small)

* * *

## 四、搭建辅域

1.安装完子域之后，为避免出现单点故障，需要再部署一台辅域控制器为备用  
配置ip:  
![image](https://image.3001.net/images/20210616/1623825313_60c99ba1c7ef91683a406.jpg!small)

2.先与主域用户配置同样的方法（加入ice.com域）：  
![image](https://image.3001.net/images/20210616/1623825327_60c99baf3e0e4597d664e.jpg!small)

3.点击服务器管理器-->添加角色和功能-->与搭建子域操作类似，添加域服务  
![image](https://image.3001.net/images/20210616/1623825345_60c99bc109ac663e1efca.png!small)

4.点击下一步直到等待安装  
![image](https://image.3001.net/images/20210616/1623825383_60c99be72c1d6f15c6eb9.jpg!small)

5.点击提升为域控制器：  
![image](https://image.3001.net/images/20210616/1623825400_60c99bf830b77ffa75066.jpg!small)

6.这里将域控制器添加到现有的域，凭证为主域的用户名和密码  
![image](https://image.3001.net/images/20210616/1623825416_60c99c08e6c26cd6cd411.jpg!small)

7.这里都为默认，填写完密码进行下一步  
![image](https://image.3001.net/images/20210616/1623825435_60c99c1b812a104c4aa96.png!small)  
8.路径都为默认，直接下一步  
![image](https://image.3001.net/images/20210616/1623825458_60c99c32e8821d91323ac.png!small)

9.先决条件成功之后 直接安装即可  
![image](https://image.3001.net/images/20210616/1623825732_60c99d44a0712981d100d.png!small)

10.最后辅域控服务器重启后检查DNS服务器是否已获取到主域控制器传输过来的DNS服务器配置,检查正常后需要把辅域控制器的DNS服务器_msds.ice.com和ice.com的起始授权机构(S○A)区域传送设置成允许。

点击工具选择DNS  
![image](https://image.3001.net/images/20210616/1623825759_60c99d5f907c48b7d9450.png!small)  
![image](https://image.3001.net/images/20210616/1623825782_60c99d76098a5d213eda8.jpg!small)  
![image](https://image.3001.net/images/20210616/1623825797_60c99d8597f1fe98ad4a0.jpg!small)

与上一步操作相同，选择到所有服务器之后点击确定  
![image](https://image.3001.net/images/20210616/1623825820_60c99d9c76c6f903e925e.jpg!small)  
安装辅域控制器,如果主域控制器DNS和AD集成,辅域控制器会在安装AD后自动同步DNS记录,到此辅域就安装完成!

## 五、搭建独立域

### 1.创建财务部系统

配置ip:  
![image](https://image.3001.net/images/20210616/1623825838_60c99daeedc1ecab9247c.jpg!small)  
![image](https://image.3001.net/images/20210616/1623825854_60c99dbe8179c90688a32.jpg!small)

### 2.创建财务部存放核心资料系统

配置ip:  
![image](https://image.3001.net/images/20210616/1623825878_60c99dd6d5da31634c348.jpg!small)

