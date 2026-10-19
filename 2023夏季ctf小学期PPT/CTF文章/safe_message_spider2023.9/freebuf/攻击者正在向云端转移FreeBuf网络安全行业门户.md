**最近研究Legion
Loader恶意软件时，研究人员偶然发现了一个下载装置，从云服务下载执行恶意有效负载。在寻找其他类似的样本发现：8,000个URL，10,000个样本，Nanocore，Lokibot，Remcos，Pony
Stealer等。可以看出云服务是整个黑客产业的新方向，可取代打包程序和加密程序。如果恶意软件网络活动只与云通联，就很有可能逃过系统检测，研究人员也无法快速分辨恶意软件。**

谷歌对这种攻击手段也有防御措施，如果尝试从Google云下载恶意软件，通常会看到以下消息：

##
![](https://image.3001.net/images/20200421/1587429398_5e9e4016dea9c.png!small)调查分析

在查看近期从云中加载恶意软件的攻击事件时，通常可以发现带有附件的垃圾邮件，附件是包含恶意可执行文件的.ISO文件。攻击者诱骗目标点击ISO并运行文件，从Google云等云端下载恶意软件，然后执行，有效载荷会伪装成图片。在云中文件已加密，在目标机器上会使用“XOR”解密，密钥长度在200到1000字节之间。从根本上不同于“打包”或“加密”恶意软件，打包恶意软件会在执行过程中展示其功能和行为，没有解密的恶意软件就会保持混淆状态。

下图为攻击示例图片：

![](https://image.3001.net/images/20200421/1587430019_5e9e42833ec99.png!small)每个有效负载都使用唯一的加密密钥进行加密，植入程序还具有一个内置选项，允许系统重启后下载有效负载。攻击流程图如下：

![](https://image.3001.net/images/20200421/1587430133_5e9e42f50eeac.png!small)

因为Google和安全厂商都在查看恶意文件的签名和哈希，有效载荷仅停留在内存中，不会以任何形式保存到硬盘。

安全人员通常会使用沙盒环境分析恶意有效负载及其恶意行为。但是，如果沙盒无法在互动过程中记录整个互动过程，在攻击活动结束后攻击者会从云中删除加密的恶意样本，会给安全人员追溯恶意软带来很大的难题。通常，受害者的计算机上也不会留下任何痕迹，恶意文件仅停留在内存中，当分析人员查看机器时，恶意代码早已被清除。

![](https://image.3001.net/images/20200421/1587430736_5e9e45506acb8.png!small)在少数情况下，加密的恶意有效载荷会托管在已被攻陷的合法网站上，调查中发现的主要托管方式：

![](https://image.3001.net/images/20200421/1587430851_5e9e45c37000e.png!small)Google
Drive和OneDrive并不是唯一载体。

![](https://image.3001.net/images/20200421/1587430909_5e9e45fd9d3e9.png!small)每周大约可以发现800个新样本。

##  技术分析

###  下载流程

以Legion Loader恶意软件为例，被分析的样本非常小，因此必须要去下载和执行恶意软件。流程如下：

###
![](https://image.3001.net/images/20200421/1587431132_5e9e46dc64218.png!small)混淆与加密

样本中使用了混淆跳转等反调试技术，需要花费大量人力来弄清楚执行流程：

![](https://image.3001.net/images/20200421/1587431253_5e9e475552fdd.png!small)经过分析，它将解密并执行shellcode，该shellcode位于文件的其他位置（通常位于资源或代码部分）：

![](https://image.3001.net/images/20200421/1587431331_5e9e47a3d8fc4.png!small)其秘钥恢复为：

> plaintext_prefix = 0x0200EC81;
>
> key = ((DWORD *)ciphertext)[0] ^ plaintext_prefix;

###  shellcode

Shellcode也被混淆，IDA无法自动分析。

![](https://image.3001.net/images/20200421/1587431526_5e9e48660bc6e.png!small)

![](https://image.3001.net/images/20200421/1587431564_5e9e488ccc8fb.png!small)攻击者非常了解沙箱，shellcode包含许多技术来检查其是否在沙箱中运行。样本检查了窗口的数量，如果小于12，则静默退出。

![](https://image.3001.net/images/20200421/1587431648_5e9e48e008024.png!small)动态地解析API函数地址：

![](https://image.3001.net/images/20200421/1587431702_5e9e4916b06be.png!small)解析API函数地址后，将在挂起状态下启动另一个进程，将解密的Shellcode复制到内存中，然后执行。

###
![](https://image.3001.net/images/20200421/1587431773_5e9e495d6c4ae.png!small)文件下载

Shellcode从硬编码URL下载加密的有效负载。 在72％的样本中，使用drive.google.com下载有效负载：

![](https://image.3001.net/images/20200421/1587431828_5e9e4994868cc.png!small)![](https://image.3001.net/images/20200421/1587431842_5e9e49a20d7b9.png!small)使用硬编码user-agent：

> Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko

程序会检查下载文件的一致性，将其大小与硬编码值进行比较。如果出现文件大小不一样的情况，程序会反复尝试下载有效负载，直到下载的文件大小等于硬编码值为止。常见文件命名规则为：<prefix>_encrypted_<7
hex digits>.bin

![](https://image.3001.net/images/20200421/1587432030_5e9e4a5ecc6f4.png!small)![](https://image.3001.net/images/20200421/1587432053_5e9e4a759939d.png!small)

###  诱骗图像

还观察到了包含两个URL的样本， 第二个URL用于下载图像：

![](https://image.3001.net/images/20200421/1587432149_5e9e4ad579ae6.png!small)

下载的图像以硬编码名称保存到用户配置文件中。 下面是其中的一些示例：

![](https://image.3001.net/images/20200421/1587432199_5e9e4b07a546d.png!small)已发现的图片下载地址：

![](https://image.3001.net/images/20200421/1587432235_5e9e4b2be35a2.png!small)

###  延迟下载

恶意软件可在用户重启后下载有效负载。

![](https://image.3001.net/images/20200421/1587432293_5e9e4b659b43d.png!small)程序将复制到%USERPROFILE%\subfolder1\filename1.exe，并创建VBS脚本(C:\\{USERPROFILEPATH}\subfolder1\filename1.vbs)，其内容如下：

> Set W = CreateObject("WScript.Shell")
>
> Set C = W.Exec ("C:\Users\User\subfolder1\filename1.exe")

操作系统重启后将自动执行下载程序。

##  总结

服务器维护的重担已经转移到云供应商身上，面对云端威胁，许多安全解决方案是不够的。恶意软件运行完毕不会留下任何痕迹，给分析人员带来很大的难题，他们需要面对一系列的反分析措施以及云端安全功能。

##  IOCs

MD5  |  Embedded URLs  
---|---  
d621b39ec6294c998580cc21f33b2f46  |
[https://drive.google.com/uc?export=download&id=1dwHZNcb0hisPkUIRteENUiXp_ATOAm4y](https://drive.google.com/uc?export=download&id=1dwHZNcb0hisPkUIRteENUiXp_ATOAm4y)  
e63232ba23f4da117e208d8c0bf99390  |
[https://drive.google.com/uc?export=download&id=1Q3PyGHmArVGhseocKK5KcQAKPZ9OacQz](https://drive.google.com/uc?export=download&id=1Q3PyGHmArVGhseocKK5KcQAKPZ9OacQz)  
ad9c9e0a192f7620a065b0fa01ff2d81  |
[https://onedrive.live.com/download?cid=FB607A99940C799A&resid=FB607A99940C799A%21124&authkey=AH_rddw8JOJmNAI](https://onedrive.live.com/download?cid=FB607A99940C799A&resid=FB607A99940C799A%21124&authkey=AH_rddw8JOJmNAI)  
ad419a39769253297b92f09e88e97a07  |
<https://cdn.filesend.jp/private/9gBe6zzNRaAJTAAl1A3VRa8_Gs0yw1ViOupoQM8N7njTTXNKTBoZTTlcXmygveWF/igine%20%282%29_encrypted_8D185FF.bin>  
df6e0bc9e9a9871821374d9bb1e12542  |  [https://fmglogistics-my.sharepoint.com/:u:/g/personal/cfs-hph_fmgloballogistics_com/EX30cSO-FxVEvmgm8O7XHL4ByKe15ghVU829DmSIWng6Jg?e=BFRtSN&download=1](https://fmglogistics-my.sharepoint.com/:u:/g/personal/cfs-hph_fmgloballogistics_com/EX30cSO-FxVEvmgm8O7XHL4ByKe15ghVU829DmSIWng6Jg?e=BFRtSN&download=1)  
232da2765bbf79ea4a51726285cb65d1  |
<https://cdn-12.anonfile.com/RdO1lcdaod/77814bdf-1582785178/makave@popeorigin6_encrypted_4407DD0.bin>  
<https://cdn.filesend.jp/private/hcmyj5nD6aJkDXptSilmcc1iHGLaXs0QTpyQDASA5AqNsWXFkzdNappNJ0_8-TEx/makave%40popeorigin6_encrypted_4407DD0.bin>  
cf3e7341f48bcc58822c4aecb4eb6241  
  
|  <https://www.dropbox.com/s/332yti5x6q8zmaj/plo_encrypted_4D16C50.bin?dl=1>  
  
c1730abe51d8eed05234a74118dfdd6a  |
<https://share.dmca.gripe/iQEkn0067f3MvpRm.bin>  
760f167f44be7fc19c7866db89ba76d5  |  <http://raacts.in/a/00.bin>
<http://alaziz.in/a/00.bin>  
9f4e7577922baa06d75a4a8610800661  |  <http://biendaoco.com/wp-content/plugins/revslider/admin/POORDER.bin>  
61cfb93ff1d5d301aeb716509a02e4b6  |  <https://taxagent.gr/wp-includes/ID3/Host_encrypted_135E9B0.bin>  
  
***参考来源：[checkpoint](https://research.checkpoint.com/2020/threat-actors-migrating-to-the-cloud/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  

