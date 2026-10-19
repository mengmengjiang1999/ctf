历史文章：

[固件分析技术(1)-简介](../273150.html)

[固件分析技术(2)-工具使用](../273152.html)

文章首发于公众号：焊死车门

##  **一、固件下载地址：**

由于贫穷没有买设备拆解，进行完整的研究。所以硬件部分还是以后学习在进行总结。虽然没有路由器可以拆解，但是设备的固件还是比较容易得到的。我们可以从官网下载不同型号路由器的固件升级包来进行漏洞研究。

D-LINK固件下载地址：ftp://ftp2.dlink.com/PRODUCTS/

其中包括绝大部分型号的固件，如果此地址没有想要下载的型号，也可以百度自行搜索。

![](https://image.3001.net/images/20210529/1622302727_60b26007c8139146a0981.png!small)

路由优化大师：http://www.luyoudashi.com/roms/

网站中有不同品牌不同型号的路由器固件，省去找固件的时间。

![](https://image.3001.net/images/20210529/1622302744_60b26018e6ec0f875f501.png!small)

如果想要研究的固件在这两个网站中没有，也可以去该品牌的官网进行下载。

##  **二、漏洞复现：**

D-Link系列网上公开的漏洞资料比较多，在初学时推荐从D-Link路由器漏洞开始学起。

###  **1** **、D-Link DIR300 信息泄露复现**

固件下载：

>
> <ftp://ftp2.dlink.com/PRODUCTS/DIR-300/REVA/DIR-300_REVA_FIRMWARE_v1.06B05_WW.zip>

 **（1）固件解压**

解压固件：

![](https://image.3001.net/images/20210529/1622302796_60b2604c52f5016027650.png!small)

固件解压出来之后会有一个suashfs-root文件夹。

![](https://image.3001.net/images/20210529/1622302812_60b2605c905685d19225f.jpg!small)

查看文件夹下的内容可以发现其中的文件和Linux系统是基本一致的。在路由器中bin、sbin和usr目录下的bin、sbin是存放路由器应用程序目录的。etc用来存放路由器配置文件。www、htdocs一般用来存放web文件。

![](https://image.3001.net/images/20210529/1622302825_60b26069825f225052d6f.jpg!small)

 **（2）漏洞分析**

进入www目录，信息泄露漏洞出现在/model/__show_info.php文件中。

![](https://image.3001.net/images/20210529/1622302850_60b260820ff28c3b06f07.png!small)

已经禁止了$REQUIRE_FILE的参数为var/etc/httpasswd和var/etc/hnapassw，但是从根路径开始配置httpasswd的路径，就可以绕过这个过滤了。

>  **Payload:**
> Localhost.com/model/__show_info.php?REQUIRE_FILE=/var/etc/httpasswd

设置REQUIRE_FILE=/var/etc/httpasswd 成功绕过上面的 if判断，进行任意文件读取。

FOFA上搜索此型号路由器可以测试：

![](https://image.3001.net/images/20210529/1622302909_60b260bd85f46a1555939.png!small)![](https://image.3001.net/images/20210529/1622302919_60b260c74c93edcb18c8e.png!small)

测试payload成功

![](https://image.3001.net/images/20210529/1622302932_60b260d49b736269c27b2.png!small)

###  **2** **、D-Link DWR932B 硬编码漏洞**

固件地址：

>
> <https://media.dlink.eu/ftp/products/dwr/dwr-932/driver_software/DWR-932_fw_revB_2_02_eu_en_20150709.zip>

 **（1）固件解压**

此固件以zip格式进行压缩打包，并经过加密，无法直接解压。

![](https://image.3001.net/images/20210529/1622302991_60b2610f8d05a6c465736.png!small)

使用binwalk进行解包，生成_DWR-932_B1_FW v.02.02EU.zip.extracted文件夹。文件夹下存在40.zip包。

![](https://image.3001.net/images/20210529/1622303008_60b26120a3763a2ded115.png!small)

继续对40.zip解压，发现需要密码。![](https://image.3001.net/images/20210529/1622303027_60b26133398e191d4a496.png!small)

使用frackzip工具可以破解该zip密码，这里直接给出压缩包的密码：beUT9Z。获得解压后的文件夹与文件。![](https://image.3001.net/images/20210529/1622303047_60b26147e90475a36efd0.png!small)

Yaffs2文件就是它的根文件系统，使用binwalk进行解压时发现无法提取出根文件系统。![](https://image.3001.net/images/20210529/1622303063_60b261574079f95bce10d.png!small)

提取后的文件夹中并非根文件系统，查阅资料后，了解到932b采用了yaffs的原生态压缩算法，需要使用工具unyaffs提取。![](https://image.3001.net/images/20210529/1622303083_60b2616b6eb8a19bd3d86.png!small)

使用unyaffs进行解压。将镜像文件提取到yaffs2-root目录，获得完整的根文件系统。![](https://image.3001.net/images/20210529/1622303097_60b261798dd8d3d7ea821.png!small)

 **（2）漏洞分析**

文件分析方法是通过对根文件系统进行遍历，以此发现存在安全隐患的文件或配置信息，已知漏洞存在于inadyn-mt.conf文件中，通过遍历.conf文件找到位置。![](https://image.3001.net/images/20210529/1622303119_60b2618fd087b6f10541f.png!small)

在inadyn-mt.conf文件（用于dyndns客户端）中存储了路由器no-IP配置信息，其中包含了了用于访问网站<https://www.no-ip.com>的用户名和硬编码口令。![](https://image.3001.net/images/20210529/1622303136_60b261a02da0bd2eb539e.png!small)

 **最后在复现一个工控固件的漏洞：**

###  **3** **、施耐德PLC以太网模块noe77101固件**

最初分析的是根据此漏洞出的一道CTF题：2020工业信息安全技能大赛(ICSC)石家庄站——简单的固件逆向分析（CTFHUB中已收录）。

后来找到此型号的固件进行分析。下载地址：

> <https://pan.baidu.com/s/1sQz-3idl97ZkhVZpANWbAQ>提取码：phyy

（1）固件解压

拿到固件之后，打开zip格式的固件压缩包，得到FLASH0文件夹和commandList.lst文件。

FLASH0文件夹目录如下：![](https://image.3001.net/images/20210529/1622303217_60b261f123ba5cf157855.png!small)

在FLASH0/wwwroot/conf/exec目录下发现NOE77101.bin文件。使用binwalk对此文件进行解压分析。![](https://image.3001.net/images/20210529/1622303242_60b2620aee5389e3ba5e9.png!small)

提取文件后，得到217和217.zlib两个文件。使用binwalk的-A参数分析217，可以看到此固件使用的是PowerPC架构。![](https://image.3001.net/images/20210529/1622303257_60b2621915d2ec3ba3e98.png!small)

（2）修复函数名

将217文件放入IDA中进行分析，处理器手动选择PowerPC big
endian(PPC)，固件地址填写0x10000（固件常见加载地址是0x10000）。![](https://image.3001.net/images/20210529/1622303282_60b262324caef264a4f77.png!small)![](https://image.3001.net/images/20210529/1622303300_60b2624496b48945c105a.png!small)

这时候发现IDA没有识别到函数。![](https://image.3001.net/images/20210529/1622303316_60b262541239c92fa86d6.png!small)

在网上找到修复脚本，生成py文件放入IDA中：File-->Script file…

> from idaapi import *
>
> from idc import *
>
>  
>
>
> loadaddress = 0x10000
>
> eaStart = 0x31eec4 + loadaddress
>
> eaEnd = 0x348114 + loadaddress
>
>  
>
>
> ea = eaStart
>
> eaEnd = eaEnd
>
> while ea < eaEnd:
>
> create_strlit(Dword(ea), BADADDR)
>
> sName = get_strlit_contents(Dword(ea))
>
> print sName
>
> if sName:
>
> eaFunc = Dword(ea + 4)
>
> MakeName(eaFunc, sName)
>
> MakeCode(eaFunc)
>
> MakeFunction(eaFunc, BADADDR)
>
> ea = ea + 16

修复后看到IDA识别了8879个函数，可以进行下一步分析。![](https://image.3001.net/images/20210529/1622303381_60b262952d5600a975c80.png!small)

（3）漏洞分析

寻找和用户相关的函数调用情况，搜索login、user等关键字，发现函数loginUserAdd![](https://image.3001.net/images/20210529/1622303400_60b262a810303c97e2cf1.png!small)

查看调用，发现有多个函数：usrAppInit、userSecurity、FTP_User_Add等。![](https://image.3001.net/images/20210529/1622303417_60b262b9654b1de8e4e09.png!small)

分别查看以上函数，在usrAppInit函数中可以查到后门账户的调用。

在PowerPC中，lis(立即数载入并左移)和addi(立即数加法)的组合是最常见的赋值操作，ida
pro的注释中给出了经过赋值之后的结果。以第一次调用为例，实际上是执行了loginUserAdd(0x22DB7C,0x22DB84)，这两个内存地址在固件中的实际地址应是再减去固件的加载地址。![](https://image.3001.net/images/20210529/1622303439_60b262cf8e9d2938335d8.png!small)

定位固件0x21DB7C(0x22DB7C-0x10000)，发现ftp后门账号。![](https://image.3001.net/images/20210529/1622303452_60b262dc46e72fea1bfec.png!small)

##  **三、修复建议：**

建议定期对路由器升级更新。

修复建议这里其实想了很多，这里主要复现的是家用的路由器，寻常百姓家基本都会用到。而且有很多家庭因为安全意识薄弱，安装好路由器后从未升级过，更别说使用默认口令或弱口令。还有些家庭很久之前买的路由器，一直使用到现在，型号可能都已经停产（我家最开始的路由器就是这样）。这种已经没有办法用升级来进行保护，那最起码还是要修改一下自己路由器的密码，定期检查家用路由器DNS地址是否被恶意篡改，尽可能保护自己的安全。

