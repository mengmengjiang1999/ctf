**作者：km1ng@极光无限维阵漏洞团队  
原文链接：<https://mp.weixin.qq.com/s/Ol3B3PFLLXLFF8ThA9nxEg> **

## 一、简介

荷兰网络安全公司Eye
Control的安全研究人员发现，超过10万个合勤科技（Zyxel）公司的防火墙、接入点控制器和VPN网关产品中存在管理员级后门账户。这些在二进制代码中硬编码的管理员级别账户使攻击者可通过Web管理面板或SSH界面获得对设备的root访问权限。合勤科技（Zyxel）是一家位于中国台湾新竹的网络设备制造商。
Zyxel固件中发现的后门漏洞cve编号为cve-2020-29583等分为7.8 CVSS

## 二、影响范围

![image-20210107095208095](https://images.seebug.org/content/images/2021/01/12/1610430015000-image-20210107095208095.png-w331s)

cve官网上表示USG设备4.60，真实影响范围如下：

zyxel:ap_controller_nxc_2500: _zyxel:ap_controller_nxc_5500:_
zyxel:atp_firmware: 4.60 zyxel:usg_firmware: 4.60 zyxel:usg_flex_firmware:
4.60 zyxel:vpn_firmware: 4.60

## 三、固件后门分析

### 3.1、固件下载

下载链接：<https://portal.myzyxel.com/my/firmwares>

需要注册账户登录，选择USG40固件，4.60版本下载。如下图所示
![image-20210107100332506](https://images.seebug.org/content/images/2021/01/12/1610430015000-image-20210107100332506.png-w331s)

下载后固件是一个名为firmware.zip的压缩包，将这个压缩包放入ubuntu虚拟机下。

### 3.2、固件解压

使用unzip firmware.zip解压压缩包，可以看到解压出如下文件。

![image-20210107101153288](https://images.seebug.org/content/images/2021/01/12/1610430015000-image-20210107101153288.png-w331s)

其中的460ABUH1C0.bin就是需要解压的固件。直接使用binwalk -e 解压,会发现解压的全部文件里面内容是空的。

![image-20210107101734976](https://images.seebug.org/content/images/2021/01/12/1610430015000-image-20210107101734976.png-w331s)

使用file命令查看这个bin文件，发现他是一个zip压缩包文件。将这个bin文件移动到windows下使用7-zip查看目录文件结构。

![image-20210107102629584](https://images.seebug.org/content/images/2021/01/12/1610430015000-image-20210107102629584.png-w331s)

我们是可以得到一些固件中的信息的，如文件大小等。解压firmware.zip的不只解压出来bin文件，还有其他的一些conf、pdf文件。使用7z工具打开bin文件在里面寻找.conf、pdf后缀文件，第一个就发现了大小为30181的文件，ubuntu下查看解压出来的460ABUH1C0.conf也是30181的大小，现在猜测这两个文件是相同的。

![image-20210107103159084](https://images.seebug.org/content/images/2021/01/12/1610430015000-image-20210107103159084.png-w331s)

### 3.3、固件解密

使用pkcrack包进行解密，解密方式为明文攻击，这里不对明文攻击进行详细阐述。pkcrack包在附件给出，解压后进入src目录，直接make即可。

将zyxel.sh脚本和460ABUH1C0.bin放在同一级目录，命令：

    
    
    sudo ./zyxel.sh 460ABUH1C0

可以将固件解压出来，解密过程大概会在20秒左右，zyxel.sh也会在附件中给出。

解压完成后，发现当前目录下有cracked.zip压缩包，直接解压即可得到460ABUH1C0.bin中的内容，可以看到里面有compress.img文件这个才是我们最终需要解压的固件，直接使用binwalk
-e指令即可。

![image-20210107105340103](https://images.seebug.org/content/images/2021/01/12/1610430015000-image-20210107105340103.png-w331s)

可以使用file指令查看一下这个文件，会发现Squashfs filesystem。

### 3.4、搜索后门

因为已爆出了后门账户的账号和密码，这里直接使用grep指令搜索，grep -rn "PrOw\\!aN_fX"
搜索的密码时候，其中“！”是需要进行转义并不是密码里有“\”字符。 打开匹配到的usr/local/bin/capwap/capwap_srv二进制文件。
![image-20210107110202438](https://images.seebug.org/content/images/2021/01/12/1610430016000-image-20210107110202438.png-w331s)
将这个文件取出，放入ida中分析。
![image-20210107111040076](https://images.seebug.org/content/images/2021/01/12/1610430016000-image-20210107111040076.png-w331s)

## 四、维阵固件分析

上诉这种情况大概率就是一个后门账户了，现在是已知账号密码可以使用搜索指令确定位置，如何在未知固件中快速发现这种后门账户。

出现上诉类似情况大概率是一个后门账户，据有很高的分析价值。现在是已知账号密码可以使用搜索指令确定其位置。在一个未知固件中找到漏洞、定位漏洞的具体位置是一个费时费力的工程。维阵平台，可以自动化的分析出容易出现问题的位置，将感兴趣的文件列举出来如一些账号密码文件，固件的目录结构、组件、判断程序是否开启保护机制等。

进入compress.img解压出来的_compress.img.extracted目录，使用7z压缩squashfs-root为一个zip包取出，上传到维阵平台。
![image-20210107193544635](https://images.seebug.org/content/images/2021/01/12/1610430016000-image-20210107193544635.png-w331s)

维阵是实时分析上传的，分析完成前就可以先看到部分结果。

![image-20210107193510317](https://images.seebug.org/content/images/2021/01/12/1610430016000-image-20210107193510317.png-w331s)

点击敏感账号，进入敏感信息页面。

![image-20210107193706097](https://images.seebug.org/content/images/2021/01/12/1610430016000-image-20210107193706097.png-w331s)

点击工具选项，可以看到有ftp。

![image-20210107193842727](https://images.seebug.org/content/images/2021/01/12/1610430016000-image-20210107193842727.png-w331s)

去解压后的固件中，查找这个路径。

![image-20210107194218456](https://images.seebug.org/content/images/2021/01/12/1610430016000-image-20210107194218456.png-w331s)

在附近查看，直接就可以发现感兴趣的passwd.basic
和shadow.basic。打开这两个文件可以发现一些账户和配置信息。根据前面的内容下载解密老版本的固件解压，对比文件是否有差异。

![image-20210107194801537](https://images.seebug.org/content/images/2021/01/12/1610430016000-image-20210107194801537.png-w331s)

zyfwp是否真的被更换了吗？全局搜索这个字符串，会发现它在squashfs-root/usr/local/bin/capwap/capwap_srv二进制文件里面，这个时候已经可以打开ida进行分析，这种情况下一般都是会有所收获的。

打开维阵平台的漏洞分析模块，使用AI和系统共同自动化检测哪里可能存在漏洞，可以看到已经自动化分析出来不少有可能产生漏洞的文件和地址，有助于快速定位挖掘漏洞。

![image-20210108103025707](https://images.seebug.org/content/images/2021/01/12/1610430016000-image-20210108103025707.png-w331s)

## 五、验证登录

搜索NXC2500，NXC系列是目前暂未修复的版本。

![image-20210108110720265](https://images.seebug.org/content/images/2021/01/12/1610430016000-image-20210108110720265.png-w331s)

ftp登录
![image-20210108110523218](https://images.seebug.org/content/images/2021/01/12/1610430016000-image-20210108110523218.png-w331s)

发现直接使用zyfwp账号密码就可以匿名登录

## 六、视频演示

相关视频请转至原文观看：<https://mp.weixin.qq.com/s/Ol3B3PFLLXLFF8ThA9nxEg>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1448/>

