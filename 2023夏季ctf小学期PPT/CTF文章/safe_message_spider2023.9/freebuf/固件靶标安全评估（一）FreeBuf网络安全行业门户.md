> 本文首发于公众号：  
>
> [​固件安全评估（一）](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/gT3BDhV6G5ail3_-mjp8PQ)

### 一、概述

近年来，随着科技的飞速发展，物联网技术逐渐走向成熟，并在安防、医疗、零售、教育、办公、家居、能源等多个领域得到应用。特别是随着5G
时代的到来，也极大推动了物联网技术的进一步发展和应用，其安全性也越来越受到人们的关注。本篇以物联网的固件入手，进行固件的安全评估。

### 二、环境版本与工具

### 环境版本与工具

系统/工具| 用途| 来源  
---|---|---  
kali| 攻击机| 官网  
IoTGoat| 靶标|
[https://github.com/OWASP/IoTGoat/releases](https://link.zhihu.com/?target=https%3A//github.com/OWASP/IoTGoat/releases)  
binwalk| 分析工具| kali自带  
firmwalk| 分析工具|
[https://github.com/craigz28/firmwalker.git](https://link.zhihu.com/?target=https%3A//github.com/craigz28/firmwalker.git)  
nmap| 端口、服务扫描| kali自带  
nc| 远程链接| kali自带  
hydra| 暴破| kali自带  
RSAS| 漏扫| 绿盟  
  
### 三、安全评估

评估固件的靶标选择：IOTGoat

项目github链接：

>
> [https://github.com/OWASP/IoTGoat](https://link.zhihu.com/?target=https%3A//github.com/OWASP/IoTGoat)

###  **3.1.介绍**

IoTGoat 项目是一个基于OpenWrt的故意不安全的固件由OWASP维护（就是说OWASP提供测试靶标），现在进行测试发掘其中存在的安全问题。

###  **3.2.固件** 准备

首先进行固件下载，我选择下载了IoTGoat-raspberry-pi2.img的这个，

下载链接：

>
> [https://github.com/OWASP/IoTGoat/releases](https://link.zhihu.com/?target=https%3A//github.com/OWASP/IoTGoat/releases)

![v2-db232b0c3898910614aaae82bde51387_b.jpg](https://image.3001.net/images/20220712/1657590964_62ccd4b412658cd42aa64.jpg!small)

使用binwalk-Me命令，解压使用上面链接下载的固件文件。

> binwalk -Me IoTGoat-raspberry-pi2.img

  

![v2-9907e569184a6f06e8c079def87adaa0_b.jpg](https://image.3001.net/images/20220712/1657590964_62ccd4b4adaeeae7d1338.jpg!small)![v2-15e2b2314c6375b9cc4b5b0d2f592f03_b.jpg](https://image.3001.net/images/20220712/1657590965_62ccd4b577f31ff37d4d1.jpg!small)

运行后会在固件同级目录创建_IoTGoat-raspberry-pi2.img.extracted目录。

![v2-e53d63845b8fa39d79bb4d6097a57d04_b.png](https://image.3001.net/images/20220712/1657590966_62ccd4b60f6a845ff8c61.png!small)

进入_IoTGoat-raspberry-pi2.img.extracted目录可以看到squashfs-root文件系统，这就是固件的文件系统了。

###  **3.3.固件测试** 环境

在刚才固件下载的链接下面下载固件vmdk虚拟磁盘文件。

这里选择的是vmware安装虚拟机的方式模拟运行固件，这一步主要是为了验证漏洞，也可以使用一些固件模拟软件或者真实设备进行漏洞验证。

首先vmware点击文件新建虚拟机，选择自定义高级。

默认下一步。

选择稍后安装操作系统，然后点击下一步。

![v2-9bc35b245dd019d9a4eb46619357ade6_b.jpg](https://image.3001.net/images/20220712/1657590966_62ccd4b69d3da11733dff.jpg!small)

这里客户机操作系统选择linux版本选择ubuntu64,然后点击下一步。

![v2-6b699e834bf61f862f360a5c61a01858_b.jpg](https://image.3001.net/images/20220712/1657590967_62ccd4b72c643e3540b04.jpg!small)

填写虚拟机名称与安装路径，点击下一步。

![v2-c8ef5ebf51b3a920d4b169ded06a2761_b.jpg](https://image.3001.net/images/20220712/1657590967_62ccd4b7bd6270e469a3b.jpg!small)

设置处理器，这里设置为两处理器。

设置内存为4096Mb。

设置网络连接为网络地址转换(NAT)模式。

连续使用使用默认设置。

选择使用现有虚拟磁盘。

选择磁盘文件，为上面下载的vmdk文件。

![v2-587b9c0c8087a7a8441e758a29fa913a_b.jpg](https://image.3001.net/images/20220712/1657590968_62ccd4b8553a5d63d834e.jpg!small)

这里选择保存现有格式。

![v2-030f78159ddb17db79b0a46f195a7df3_b.jpg](https://image.3001.net/images/20220712/1657590968_62ccd4b8f34a417d48dfc.jpg!small)

点击完成。

如下图第二张所示虚拟机正常运行。（记得在界面回车下，要不然不到这个界面）

![v2-64b6ca3105cf1b509f12e3d2476639f6_b.jpg](https://image.3001.net/images/20220712/1657590969_62ccd4b9bf29a7feee3d6.jpg!small)![v2-73caff565a2e46caa9b5eb41f4798fab_b.jpg](https://image.3001.net/images/20220712/1657590970_62ccd4ba8f574501a775b.jpg!small)

使用ifconfig查看ip，出现问题。

![v2-370399f7398ab9b38fdd9a539167f8e8_b.jpg](https://image.3001.net/images/20220712/1657590971_62ccd4bb2fdf4be6dd28f.jpg!small)

打开虚拟机设置发现没有添加网卡，于是添加网卡

![v2-11493f22dd8a4b598b826cf0cb1868c7_b.jpg](https://image.3001.net/images/20220712/1657590971_62ccd4bbcc7f4089a2ca5.jpg!small)![v2-919f1c770d04fed4ee2e242fcf0f9d6f_b.jpg](https://image.3001.net/images/20220712/1657590972_62ccd4bc864d4abb7f6d4.jpg!small)![v2-e99f75b875cf68b8194b258d415cf0e1_b.jpg](https://image.3001.net/images/20220712/1657590973_62ccd4bd4a34124358016.jpg!small)

重新获取IP成功获取了IP地址。

![v2-4a8dea65e2d8d68300de61b4712418ac_b.jpg](https://image.3001.net/images/20220712/1657590973_62ccd4bddc85c9f905dcd.jpg!small)

在kali系统浏览器中输入：

> [https://192.168.239.135/cgi-> bin/luci](https://link.zhihu.com/?target=https%3A//192.168.239.135/cgi-> bin/luci)

  

![v2-e1da221138d1684d98c097f2f3d46477_b.jpg](https://image.3001.net/images/20220712/1657590974_62ccd4be9296ff86c9b48.jpg!small)

输入密码root登录成功。

> SSH登录：ssh [root@192.168.239.135](mailto:root@192.168.239.135)

![v2-a9436988a31d41a3b62b8df33fdb5124_b.jpg](https://image.3001.net/images/20220712/1657590975_62ccd4bf2848713a039e2.jpg!small)

到此为止固件仿真环境搭建成功。

### 3.4 信息收集

### 3.4.1 系统信息

系统信息：

直接在IoTGoat系统输入

> uname -a

![v2-815f3993a611d746ad70391786fcdcde_b.png](https://image.3001.net/images/20220712/1657590975_62ccd4bfc51d63fdd5cca.png!small)

可以看到系统的信息

> 端口和web服务信息：nmap -sS -Pn -A -p- 182.168.239.135

![v2-a6ae40099b03fc08a9adc07cf9f2abd9_b.jpg](https://image.3001.net/images/20220712/1657590976_62ccd4c060bfe002bb092.jpg!small)

可以看到开启了22、80、443和5000四个端口。分别是 SSH、DNS、http、https、upnp等服务

### 3.4.2 自动化分析分析

使用 工具firmwalker分析这是一个简单的 bash 脚本，用于搜索提取或挂载的固件文件系统。

它将在提取或挂载的固件文件系统中搜索感兴趣的内容，例如：

> etc/shadow and etc/passwd  
> 列出 etc/ssl 目录  
> 搜索 SSL 相关文件，如 .pem、.crt 等。  
> 搜索配置文件  
> 查找脚本文件  
> 搜索其他.bin文件  
> 查找关键字，例如管理员，密码，远程等。  
> 搜索 IoT 设备上使用的常见 Web 服务器  
> 搜索常见的二进制文件，如 ssh、tftp、dropbear 等。  
> 搜索网址、电子邮件地址和 IP 地址  
> 使用 Shodan CLI 调用 Shodan API 的实验性支持  
> git clone
> [https://github.com/craigz28/firmwalker.git](https://link.zhihu.com/?target=https%3A//github.com/craigz28/firmwalker.git)

![v2-cd8769c5791398f069f9358b9963f8d2_b.jpg](https://image.3001.net/images/20220712/1657590977_62ccd4c13fb80b463632f.jpg!small)

> cd firmwalker  
> ./firmwalker.sh /root/LOT/_IoTGoat-raspberry-pi2.img.extracted/squashfs-root

![v2-8252c57aca2990fcbc1a5b7ef344ed29_b.jpg](https://image.3001.net/images/20220712/1657590978_62ccd4c23aa8aa681eb25.jpg!small)![v2-2c9375490fd4a32a581dde3213467f1d_b.jpg](https://image.3001.net/images/20220712/1657590979_62ccd4c30e1807bd77eff.jpg!small)

### 3.5 漏洞扫描

漏洞扫描：

因为没有LOT的漏扫工具，于是拿绿盟RSAS扫描了一把。

发现了30个漏洞，

### 3.5.1按服务分类：

![v2-45e19a92dfb10db90e7872dbca962260_b.jpg](https://image.3001.net/images/20220712/1657590979_62ccd4c3c8b263f798433.jpg!small)

### 3.5.2按应用分类：

![v2-3d76752fa4bdba8ee746d54b2b53c8ce_b.jpg](https://image.3001.net/images/20220712/1657590980_62ccd4c4534688d2098ca.jpg!small)

### 3.5.3漏洞信息：

![v2-e86aa29172a24b5cd44155efe59c4021_b.jpg](https://image.3001.net/images/20220712/1657590980_62ccd4c4e79faa246f063.jpg!small)![v2-7a249dcded8f256a9a414837181b2f45_b.jpg](https://image.3001.net/images/20220712/1657590981_62ccd4c5a9335292c7482.jpg!small)

可以看到大部分是DNSmasq服务的漏洞

###  **3.6漏洞挖掘**

挖掘思路：根据项目的提示

![v2-a08a6fb8cd5d73a3f5a4a6da395795d1_b.jpg](https://image.3001.net/images/20220712/1657590982_62ccd4c6709b74d5f1e1f.jpg!small)

###  **3.6.1.弱口令**

在信息收集firmwalk分析中可以看到/etc目录存在shadow文件。  
  

![v2-43b43577b900f1a403a4bd49ccbb90dc_b.png](https://image.3001.net/images/20220712/1657590983_62ccd4c73b19d0bdaee7d.png!small)

查看固件中/etc/shadow文件保存的信息。

![v2-9487f29e65a36ce503e1daab46a9349a_b.jpg](https://image.3001.net/images/20220712/1657590983_62ccd4c7f2d534764fe4d.jpg!small)

加密密码格式： **$id$salt$encrypted**
，id为1时表示采用md5进行加密，id为5时，表示采用SHA256进行加密，id为6时，表示SHA512进行加密，该固件使用的加密方式为md5加密。

使用以下命令创建password.txt（用于破解的文件）。

> git clone
> git://[http://github.com/danielmiessler/SecLists.git](https://link.zhihu.com/?target=http%3A//github.com/danielmiessler/SecLists.git)  
> 结果失败了，于是直接安装：  
> apt -y install seclists  
> cd Malware #看图找到seclists 如果找不到使用如下命令：  
> which seclists  
> awk '{print $2}' mirai-botnet.txt > password.txt

  

![v2-00fce100e079bfae8603db1fcdc1881f_b.jpg](https://image.3001.net/images/20220712/1657590984_62ccd4c8d39bbdfba4f86.jpg!small)![v2-81a1f8dca798094d627e4f556fde4c1b_b.png](https://image.3001.net/images/20220712/1657590985_62ccd4c9900dfeb5c97b8.png!small)![v2-c3c82c8f9352997a0ba944858e49891c_b.jpg](https://image.3001.net/images/20220712/1657590986_62ccd4ca1cf800e9a7600.jpg!small)

使用hydra九头蛇进行如下命令爆破：成功活动密码：7ujMko0vizxv

> hydra -l iotgoatuser -P password.txt ssh://192.168.239.135

  

![v2-07f783754c1d328065c4b928443664a3_b.jpg](https://image.3001.net/images/20220712/1657590986_62ccd4caac72c5ad79a81.jpg!small)

进行SSH成功登录固件系统：

> ssh iotgoatuser@192.168.239.135

  

![v2-97a78e8bba92e4df4644ea907265eef5_b.jpg](https://image.3001.net/images/20220712/1657590987_62ccd4cb7aae9d0241158.jpg!small)

###  **3.6.2.web命令注入**

搜寻lua脚本所在目录，在其中找到了iotgoat.lua文件，发现在其中可以执行系统命令。和SSH命令一样可以获取系统信息。

> [https://192.168.239.135/cgi-> bin/luci//admin/iotgoat/webcmd?cmd=uname](https://link.zhihu.com/?target=https%3A//192.168.239.135/cgi-> bin/luci//admin/iotgoat/webcmd%3Fcmd%3Duname)-a

  

![v2-5e632937c16d59d07aa881a579271ebd_b.jpg](https://image.3001.net/images/20220712/1657590988_62ccd4cc449ba9aedacf4.jpg!small)

执行pwd和ls命令，命令注入无疑了。还可以看端口链接。

![v2-212f4b1e90cc8aa8f50b3e194b5a3bb2_b.png](https://image.3001.net/images/20220712/1657590988_62ccd4ccdd52dc1e114aa.png!small)![v2-0798c46c4f70e54de9e017949c7748e8_b.jpg](https://image.3001.net/images/20220712/1657590989_62ccd4cd6d1a9b97264b0.jpg!small)![v2-170951994e9adf347d5caaadd6896934_b.png](https://image.3001.net/images/20220712/1657590989_62ccd4cde7d0524f3dd1d.png!small)![v2-fc01f8a180734f99cf0ab7df5cc5941b_b.jpg](https://image.3001.net/images/20220712/1657590990_62ccd4ce7770771fc4591.jpg!small)

###  **3.6.3.程序后门**

在SSH界面查看端口情况，发现一个可疑程序

![v2-1499d46595d95c9509eed2d5c515c950_b.jpg](https://image.3001.net/images/20220712/1657590991_62ccd4cf0c2075d737e91.jpg!small)

直接尝试nc链接成功，执行了ls命令

![v2-46ea05bbf245fbbda9ce8d2f4097a8f6_b.jpg](https://image.3001.net/images/20220712/1657590991_62ccd4cf9d05e8b3e026b.jpg!small)

###  **3.6.4.任意备份更新** 漏洞

![v2-1b80a28bcbcb19a98ab01a768d6adab6_b.jpg](https://image.3001.net/images/20220712/1657590992_62ccd4d053aba6f08613e.jpg!small)

在后台登陆页面的system存在backup选项，页面中有备份、恢复、刷新固件的操作选项。翻译一下：

![v2-559a020497337f0fe8eb995b740e85ad_b.jpg](https://image.3001.net/images/20220712/1657590993_62ccd4d104e71866deb37.jpg!small)

说明存在可能被恶意刷新固件的风险。（由于本人收到没有合适的其他固件并未进行实际操作，如果需要操作记得先进行快照）

### 3.6.5 含有已知漏洞的组件

 **3.6.5.1** **busybox**

在SSH登录命令行中输入：

> busybox ls -fssdfdsf

可以看到BusyBox v1.28.4 () multi-call binary.也就是BusyBox 的版本信息

![v2-bb1102b60aabc320488a2875ca9f78ab_b.jpg](https://image.3001.net/images/20220712/1657590993_62ccd4d1970a91f9c0bc3.jpg!small)

在CVE中搜索

> [https://cve.mitre.org/cgi-> bin/cvekey.cgi?keyword=BusyBox+v1.28.4](https://link.zhihu.com/?target=https%3A//cve.mitre.org/cgi-> bin/cvekey.cgi%3Fkeyword%3DBusyBox%2Bv1.28.4)

  

![v2-f7868be0b8aa37a9de8d3bde5f76fab9_b.jpg](https://image.3001.net/images/20220712/1657590994_62ccd4d287ee8869a4e33.jpg!small)

可以看到比较多的漏洞。

 **3.6.5.2 dnsmasq**

查看组件dnsmasq版本信息：

> dnsmasq -v

![v2-10afdfb1c34521009b965b9c10a0787b_b.jpg](https://image.3001.net/images/20220712/1657590995_62ccd4d3a048c876b97b6.jpg!small)

发现版本为2.73，在CVE搜寻下。同样看到大量漏洞

> [https://cve.mitre.org/cgi-> bin/cvekey.cgi?keyword=dnsmasq+2.73](https://link.zhihu.com/?target=https%3A//cve.mitre.org/cgi-> bin/cvekey.cgi%3Fkeyword%3Ddnsmasq%2B2.73)

  

![v2-18304023d106c03407bfad8fd1d00e95_b.jpg](https://image.3001.net/images/20220712/1657590996_62ccd4d47cccfd7296132.jpg!small)

### 四、参考

[OWASP固件安全性测试指南 - Firmware Security Testing Methodology
(gitbook.io)](https://link.zhihu.com/?target=https%3A//m2ayill.gitbook.io/firmware-security-testing-methodology/v/zhong-wen-fstm/)

>
> [https://m2ayill.gitbook.io/firm](https://link.zhihu.com/?target=https%3A//m2ayill.gitbook.io/firmware-> security-testing-methodology/v/zhong-wen-fstm/)

