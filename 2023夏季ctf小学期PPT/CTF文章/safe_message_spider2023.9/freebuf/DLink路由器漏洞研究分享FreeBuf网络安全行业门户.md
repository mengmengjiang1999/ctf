## 0x0 简介

D-Link DIR-816 A2是中国台湾友讯（D-Link）公司的一款无线路由器。攻击者可借助 "datetime"
参数中的shell元字符利用该漏洞在系统上执行任意命令。

## 0x1 准备

固件版本 1.10B05：http://support.dlink.com.cn:9000/ProductInfo.aspx?m=DIR-816

漏洞存在的程序：goahead

![](https://image.3001.net/images/20210302/1614671496_603dee8847520be489e4a.png!small)

## 0x2 工具

1.静态分析工具：IDA

2.系统文件获取：binwalk

3.动态调试工具：qemu、IDA

## 0x3 测试环境

本人使用Ubuntu 16.04虚拟机测试环境，qemu模拟器模拟D-Link DIR-816 A2固件运行真实情景。

## 0x4 goahead程序调试

1.使用binwalk进行固件解包(binwalk -Me DIR-816A2_v1.10CNB03_D77137.img)

![](https://image.3001.net/images/20210302/1614671511_603dee97514c28c8e0170.png!small)

2.通过binwalk可以解包出如下图的文件，squashfs-root就是我们需要的文件系统。

![](https://image.3001.net/images/20210302/1614671525_603deea54495332b41270.png!small)

![](https://image.3001.net/images/20210302/1614671536_603deeb0d19cf96eb95ba.png!small)

3.一般可以通过find -name "*index*" 可以搜索出web的根目录在哪个具体目录下。

![](https://image.3001.net/images/20210302/1614671552_603deec0ce63f030dead1.png!small)

4.通过file ../../bin/goahead
命令(由于本人已经进入到根目录下面，所以是../../bin/goahead)，可以看出该系统是MIPS架构，则qemu模拟器需要使用MIPS方式的模拟器。

![](https://image.3001.net/images/20210302/1614671571_603deed3ba65fc47c0406.png!small)

5.sudo qemu-mipsel -L ../../ -g 1234 ../../bin/goahead

> -g 使用qemu并将程序挂载在1234端口，等待调试。
>
> -L 是根目录的所在的位置。
>
> 可以使用IDA远程调试连接1234端口，进行调试，获取使用gdb也可以调试。

![](https://image.3001.net/images/20210302/1614671584_603deee03df14dd414bc3.png!small)

6.如下图操作，IDA即可开启远程调试。

![](https://image.3001.net/images/20210302/1614671597_603deeede94da20d2a2ba.png!small)

![](https://image.3001.net/images/20210302/1614671616_603def008c5876976435e.png!small)

![](https://image.3001.net/images/20210302/1614671627_603def0b9b2299da77b24.png!small)

7.经过测试，我们需要在0x45C728处下一个断点，因为此处的 bnez 会使程序退出，所以需要将V0寄存器的值修改为1。

![](https://image.3001.net/images/20210302/1614671685_603def4585985144f7bc2.png!small)

8.同理需要在0x45cdbc地址下断点，并将V0寄存器修改为0。

![](https://image.3001.net/images/20210302/1614671696_603def50ee0ed430121e0.png!small)

9.两处地址都通过后，在网址中输入http://192.168.184.133/dir_login.asp，即可访问到登录页面。

![](https://image.3001.net/images/20210302/1614671708_603def5c253b389c6d853.png!small)

10.想进入路由器web操作页面，就必须先登录，在web服务器程序中用户名为空，而web页面有JS校验，必须需要输入用户名才能进行登录校验，那么可以修改登录校验的寄存器，让其成功运行登录。

![](https://image.3001.net/images/20210302/1614671720_603def68b9a5aeddbf904.png!small)

11.在0x4570fc地址处下断点，修改V0寄存器的值为0。因为此处的V0是用户名的值，在登录页面中，我们是随意输入，所以肯定是不会正确的，那么就只有修改为0后才能跳转到正确的登录流程。

![](https://image.3001.net/images/20210302/1614671741_603def7d455bf3bfa4f30.png!small)

12.登录成功后，会出现页面错误。

![](https://image.3001.net/images/20210302/1614671790_603defae77283c411b221.png!small)

13.再在网址中输入http://192.168.184.133/d_wizard_step1_start.asp，即可进入到登录成功后的页面。看到如下图，即可证明已经登录成功。

![](https://image.3001.net/images/20210302/1614671802_603defbae0a52e97a7ac7.png!small)

14.登录认证后，点击维护，再点击时间与日期，最后点击应用，此处便是漏洞触发点。

![](https://image.3001.net/images/20210302/1614671814_603defc63ed469cafde87.png!small)

15.最终可以通过构造datetime的值，执行任意命令。

![](https://image.3001.net/images/20210302/1614671826_603defd22125915aa20a8.png!small)

## 0x5 总结

这个固件可以锻炼qemu模拟器的使用以及IDA简单调试能力，在没有真实路由器的情况下qemu是非常好用的一款模拟工具，模拟很多款路由器。该程序还存在多个命令执行漏洞，非常适合练手。命令执行漏洞相对来说比较简单，但是杀伤力巨大，很适合新手入门。

