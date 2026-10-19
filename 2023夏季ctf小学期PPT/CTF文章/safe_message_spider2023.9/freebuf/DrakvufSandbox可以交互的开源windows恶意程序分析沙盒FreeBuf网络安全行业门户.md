DrakvufSandbox是一个自动化的黑盒恶意软件分析开源项目，该项目提供了一个友好的Web界面，允许您上传可疑文件进行分析。沙盒作业完成后，可以通过web界面浏览分析结果，并深入了解文件是否是恶意程序，下面介绍其安装以及使用。由于个人使用习惯，不想装物理的ubuntu系统，所以选择在VMware下进行虚拟嵌套使用。

## 前提条件

电脑CPU支持IntelEPT功能。

## 准备

> VMware Workstation  
> ubuntu18.04虚拟机 http://releases.ubuntu.com/18.04.6/  
> win7镜像  
> drakvuf sandbox安装包 https://github.com/CERT-Polska/drakvuf-sandbox/releases  
> vncviewer  
> 需要测试的程序

## 示意图

![](https://image.3001.net/images/20220228/1646035252_621c8134ce3420492886d.png!small)

## step1: 安装ubuntu18.04虚拟机

这个没什么好说的，需要注意的是需要至少两核CPU，5G内存以及30G磁盘，开启虚拟化。

![](https://image.3001.net/images/20220228/1646033015_621c7877dfb26d13d7b62.png!small)

## step2: 将需要的文件复制进虚拟机中

安装完drakvuf-bundle重启后，VMtools会不起作用，所以最好这个时候把要的东西都复制进虚拟机。

复制内容包括对应版本的安装包以及win7x64系统的iso镜像文件。

![](https://image.3001.net/images/20220228/1646033082_621c78ba3999d4fd358ed.png!small)

## step3: 安装 drakvuf

> sudo apt-get update  
> sudo apt install ./ubuntu_bionic_drakvuf-> bundle-0.8-git20210921114837+5575888-1-generic.deb  
> reboot  
> 电脑重启后:  
> sudo apt-get install redis-server  
> sudo apt install ./ubuntu_bionic_drakcore_0.18.1_amd64.deb  
> sudo apt install ./ubuntu_bionic_drakrun_0.18.1_amd64.deb

安装完成后可输入 sudo draksetup test 查看是否工作。

![](https://image.3001.net/images/20220228/1646033244_621c795c9eb382c03dbc2.png!small)

## step4: 安装win7测试平台

> sudo draksetup install ./win7.iso --vcpus 2 --memory 2048

这里CPU数量和内存都可按需调节。

![](https://image.3001.net/images/20220228/1646033326_621c79ae9fed7e1789474.png!small)上图所示成功后输入
drak-vncpasswd 查看vnc连接密码，记住它。

用vncviewer输入ubuntu IP连接VNC 开始安装windows，安装部分就不赘述，网上搜索一大堆，安装过程中VNC会断开两次,重新连接即可。

![](https://image.3001.net/images/20220228/1646033427_621c7a13e3f55fe4ac28e.png!small)

>
> 这里也可以使用无人值守安装，就不用连接VNC手动装机了。在https://www.windowsafg.com/win7x86_x64.html中完成相关配置生成autounattend.xml，或者去找别人的配置文件，安装命令如下  
> sudo draksetup install ./win7.iso --vcpus 2 --memory 2048 --unattended-xml
> ./autounattend.xml

## step5:初始化vm0

等待WIN7安装启动进入桌面之后ubuntu中输入

> sudo draksetup postinstall

等待vm0的运行信息提取完成，这里会用较多时间

![](https://image.3001.net/images/20220228/1646033488_621c7a508f77914098aa6.png!small)

## step6: 进行测试

访问http://ubuntuip:6300/即可开始使用。

![](https://image.3001.net/images/20220228/1646033564_621c7a9c3b8a900c01f54.png!small)默认一个测试持续十分钟，可自行调节，在进行测试过程中可连接VNC查看并操作，VNC连接地址ubuntuip:5901，密码就是drak-vncpasswd显示密码(网页自带VNC，我个人在测试过程中无法连上，所以是用物理机的VNC连接的)。

![](https://image.3001.net/images/20220228/1646033692_621c7b1c694e67f0686dc.png!small)

十分钟后将关闭测试系统生产测试报告，生成报告时间大概五分钟左右

![](https://image.3001.net/images/20220228/1646033784_621c7b78cb28967313e1e.png!small)

## (可选): 集成procdot 输出行为图

下载最新版procdot 放入ubuntu中 <https://www.procdot.com/downloadprocdotbinaries.htm>

> unzip -o procdot*_linux.zip lin64/* -d /tmp/procdot  
> mv /tmp/procdot/lin64 /opt/procdot  
> chmod +x /opt/procdot/procmon2dot

后续分析将生产行为图：

![](https://image.3001.net/images/20220228/1646033850_621c7bba74b2c16a2c141.png!small)

  

## 其它

drakvuf也支持64位的win10系统测试，但现在还处于测试阶段，其它更多功能(比如开启联网功能等)可参照项目帮助文档。

最后需要说明的是因为虚拟化嵌套以及我的物理机很渣的原因，测试软件在运行过程中会用较长时间，个人建议还是在ubuntu物理机上进行安装，步骤都差不多。

## 参考

https://github.com/CERT-Polska/drakvuf-sandbox/  
https://drakvuf-sandbox.readthedocs.io/en/latest/usage/getting_started.html

