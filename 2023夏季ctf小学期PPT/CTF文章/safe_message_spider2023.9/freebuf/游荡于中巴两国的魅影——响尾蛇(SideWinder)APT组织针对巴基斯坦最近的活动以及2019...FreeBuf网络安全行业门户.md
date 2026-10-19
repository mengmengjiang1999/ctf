![图片.png](https://image.3001.net/images/20200117/1579251058_5e2175720a0bc.png!small)**一．前**
**言：**

Gcow安全团队追影小组于2019年11月份捕获到名为SideWinder(响尾蛇)组织针对巴基斯坦的活动,介于该组织主要针对巴基斯坦和中国以及其他东南亚国家,且其于10月份时候针对中国部分国防重要行业进行类似手法的攻击活动,为了更好了解对手的攻击手段以及加以防范,团队将以最近的样本为契机来总结该组织为期一年的攻击活动.

响尾蛇（又称SideWinder、T-APT-04）是一个背景可能来源于印度的APT组织,该组织此前已对巴基斯坦和东南亚各国发起过多次攻击,
该组织以窃取政府，能源，军事，矿产等领域的机密信息为主要目的。此次的攻击事件以虚假邮件为诱饵，利用Office远程代码执行漏洞（cve-2017-11882）或者通过远程模板注入技术加载远程URL上的漏洞文件.在针对于巴基斯坦的攻击中我们发现了Lnk文件的载荷,其主要驱动是mshta.exe，攻击者通过各种方式以达到伪装的目的

在我们的样本捕获中,我们发现了该组织在这一年之间的变化,其攻击的手段越来越先进,这对我国的军事部门当然是一个不容小觑的威胁,所以我们追影小组将带领各位读者来回顾该组织的攻击手法,以及其技术的更迭。

**二.样本分析:** ****

为了方便于各位读者的理解,笔者画了一张关于该组织攻击的流程图

如下:

![图片.png](https://image.3001.net/images/20200117/1579250473_5e217329e3ac0.png!small)

在2019下半年,该组织经常使用该流程针对巴基斯坦和中国的目标进行攻击

ADVOCATE.docx
利用远程模板注入技术加载含有漏洞的CVE-2017-11882漏洞RTF文档，使用的这样加载方式可以绕过防病毒网关，增加成功率。当成功加载main.file.rtf文件后，释放1.a
到Temp目录下，触发漏洞shellcode执行1.a，1.a是一个混淆后的Jscript脚本文件，再次释放Duser.dll文件
tmp文件，并拷贝rekeywiz.exe到
C:\ProgramData\DnsFiles目录下,并执行rekeywiz.exe文件，带起Duser.dll，Duser.dll加载tmp文件.

 **1.诱饵文档**

1).样本信息:

样本MD5| 9b1d0537d0734f1ddb53c5567f5d7ab5  
---|---  
样本SHA-1| e127a783870701cdd20a7fc750cad4dae775d362  
样本SHA-256| f1cdd47f7a2502902d15adf3ac79c0f86348ba09f4a482ab9108ad98258edb55  
样本类型| Office Open XML 文件  
样本名称| ADVOCATE.docx  
文件大小| 9.02 KB (9232 bytes)  
  
2).分析

 ************

**![图片.png](https://image.3001.net/images/20200117/1579250483_5e217333ee181.png!small)**

打开ADVOCATE.docx样本后，利用远程模板注入技术远程加载远程模板:
https://www.sd1-bin.net/images/2B717E98/-1/12571/4C7947EC/main.file.rtf

![图片.png](https://image.3001.net/images/20200117/1579250491_5e21733befa67.png!small)

成功打开后显示,用掩饰目的文档，如下图：

![图片.png](https://image.3001.net/images/20200117/1579250504_5e217348e0836.png!small)

**2.漏洞文档:** ****

 ****

****

1)样本信息:

样本MD5| 3ee30a5cac2bef034767e159865683df  
---|---  
样本SHA-1| c29a1fd54f9f961211e9cd987f90bd8eb0932e45  
样本SHA-256| f08ccc040c8d8db60f30a6d1026aa6523e97c6cf52b1b30f083a830a0a65a3a9  
样本类型| 富文本文件  
样本名称| main.file.rtf  
文件大小| 1.72 MB (1804038 bytes)  
  
2).分析:

当main.file.rtf加载成功后，会将1.A文件释放到当前用户temp文件夹下面

1.a是嵌入到rtf文档中的OLE Object,如下图:

![图片.png](https://image.3001.net/images/20200117/1579250516_5e21735446e36.png!small)

通过分析rtf也可以看到

![图片.png](https://image.3001.net/images/20200117/1579250526_5e21735ee66e4.png!small)

默认释放到 temp文件夹中,如下图:

![图片.png](https://image.3001.net/images/20200117/1579250541_5e21736d5335d.png!small)

1.a文件通过Shellcode加载起来

 **(1).Shellcode分析** ****

shellcode 代码 如下图:

直接在00411874 处下断点 此处为 ret处，也就是将通过覆盖ret返回地址，达到任意代码执行目的,如下图:

![图片.png](https://image.3001.net/images/20200117/1579250550_5e2173768aa22.png!small)

可以看到esp 值已经被覆盖为0x18f354，这个就是shellcode入口地址，如下图:

![图片.png](https://image.3001.net/images/20200117/1579250558_5e21737e1f6e3.png!small)

也可以在rtf 文件中找到shellcode，如下图:

![图片.png](https://image.3001.net/images/20200117/1579250566_5e217386eb6ed.png!small)

Shellcode通过获取RunHTMLApplication来加载恶意js

![图片.png](https://image.3001.net/images/20200117/1579250576_5e217390e8321.png!small)

对异或后的js代码进行解密,秘钥是12

![图片.png](https://image.3001.net/images/20200117/1579250585_5e217399287cd.png!small)

将执行js的命令行替换其原来的命令行

![图片.png](https://image.3001.net/images/20200117/1579250593_5e2173a10d311.png!small)

恶意js如下:（读取1.a文件的所有内容并且用eval执行）

![图片.png](https://image.3001.net/images/20200117/1579250605_5e2173ad1e4e8.png!small)

**(2).1.a分析** ****

 **i.样本信息** ****

样本MD5|  4513f65bdf6976e93aa31b7a37dbb8b6  
---|---  
样本SHA-1| 73ae6cd3913bcfb11d9e84770f532f2490ddef6c  
样本SHA-256| 054a029b378b8bbf5ea3f814a737e9c3b43e124995d05d7dac45a87502bf2f62  
样本类型| Js脚本文件  
样本名称| 1.a  
文件大小| 878.91 KB (900000 bytes)  
  
 **ii.分析** ****

 ****

通过分析，1.a是一个通过DotNetToJScript成生的Jscript文件，并且经过混淆过，但是还原后还可以看出来如下图：

![图片.png](https://image.3001.net/images/20200117/1579250615_5e2173b7880d5.png!small)

![图片.png](https://image.3001.net/images/20200117/1579250624_5e2173c0e6c6f.png!small)

其主要逻辑即为将内置的c# dll解密后内存加载其Work函数传入三个参数

第一个参数是黑dll的数据,第二个参数是同目录下的tmp文件数据,第二个参数是混淆的C2地址

通过调试解密出内置dll文件的base64编码

![图片.png](https://image.3001.net/images/20200117/1579250640_5e2173d053b1f.png!small)

Base64解密后

![图片.png](https://image.3001.net/images/20200117/1579250649_5e2173d9a1456.png!small)

删除前面加载部分然后保存为dll文件

![图片.png](https://image.3001.net/images/20200117/1579250658_5e2173e2b09ce.png!small)

StInstaller.dll

其Work函数是其核心

![图片.png](https://image.3001.net/images/20200117/1579250670_5e2173ee158c7.png!small)

1) .检测白名单文件是否存在,若存在则拷贝到其工作目录下

![图片.png](https://image.3001.net/images/20200117/1579250679_5e2173f7bc4f9.png!small)

2) 修改注册表添加启动项以开机启动,注册表的值为拷贝后的白名单文件路径

![图片.png](https://image.3001.net/images/20200117/1579250688_5e2174003840e.png!small)

3) 释放对应的恶意dll和tmp文件以及配置的config文件

![图片.png](https://image.3001.net/images/20200117/1579250703_5e21740f1c801.png!small)

4) .启动白名单程序

![图片.png](https://image.3001.net/images/20200117/1579250726_5e2174260f99c.png!small)

通过API Monitor可以直观看到释放流程，如下图:

![图片.png](https://image.3001.net/images/20200117/1579250763_5e21744bac744.png!small)

1．拷贝c:\windows\syswow64\rekeywiz.exe到c:\ProgramData\DnsFiles\rekeywiz.exe下面.

2\. 释放 Duser.dll文件到C:\ProgramData\DnsFiles\Duser.dll

3\. 释放 xxx.tmp 文件到 C:\ C:\ProgramData\DnsFiles\xxx.tmp

4\. 使用CreatePocess 拉起 rekeywiz.exe

 ******(3).Duser.dll分析** ****

**i.样本信息** ****

样本MD5|  ff9d14b83f358a7a5be77af45a10d5a2  
---|---  
样本SHA-1| 612b239ce0ebaf6de6ee8eff1fb2fa2f3831ebd2  
样本SHA-256| 920197f502875461186a9d9fbf5a108f7c13677bbdeae129fbc3f535ace27a6f  
样本类型| Dll(动态链接库)文件  
样本名称| Duser.dll  
文件大小| 5.50 KB (5632 bytes)  
  
**ii.分析** ****

Rekeywiz.exe 是一个白名单文件，存在dll劫持特性，俗称白加黑如下图：

![图片.png](https://image.3001.net/images/20200117/1579250776_5e2174587ce2a.png!small)

利用rekeywiz.exe 带起Duser.dll，Duser.dll再将
***.tmp文件,此处用***表示随机文件名，解密后，内存加载.net，使其逃避防护软件查杀.关键代码如下图所示:

![图片.png](https://image.3001.net/images/20200117/1579250787_5e21746331277.png!small)

选取.tmp文件的前32字节当做秘钥,对后续的字节进行异或解密后，使用Assembly.Load 加载到内存执行。

解密后，发现是一个.net后门程序，如下图所示:

![图片.png](https://image.3001.net/images/20200117/1579250798_5e21746e3555f.png!small)

(4). **SystemApp.dll分析** ****

**i.样本信息** ****

样本MD5|  6162005b9ae5d4a8070bfe5f560b0912  
---|---  
样本SHA-1| b4928e4c3a8787e0461e2e78138091134c7f719a  
样本SHA-256| d8aa512b03a5fc451f9b7bc181d842936798d5facf1b20a2d91d8fdd82aa28b7  
样本类型| Dll(动态链接库)文件  
样本名称| SystemApp.dll  
文件大小| 576.00 KB (589824 bytes)  
  
 **ii.分析** ****

![图片.png](https://image.3001.net/images/20200117/1579250828_5e21748cbecba.png!small)start函数

首先加载基础设置信息，设置两个时间回调函数GET函数，POST函数，通过基础配置Settings类的属性来判断是否需要获取系统信息，写入选择文件，最后执行两个时间回调函数GET，POST,执行时间是5000秒。

![图片.png](https://image.3001.net/images/20200117/1579250842_5e21749a12147.png!small)

LoadSettings函数

通过Settings的settingsFilePath来获取配置文件路径，然后通过Decode函数来加载到内存，在返回一个用配置文件信息初始化的Settings类，否则返回默认配置

![图片.png](https://image.3001.net/images/20200117/1579250851_5e2174a3a786c.png!small)

基础配置信息

其中可以看见默认C2地址:

https://reawk.net/202/OaZbRGT9AZ6rhLMSEWSoFykWnI7FeEbXdgvNvwZP/-1/12571/10255afc

![图片.png](https://image.3001.net/images/20200117/1579250861_5e2174ad142b4.png!small)

DecodeData函数

Decode函数主要复制加解密数据文件，就是将文件的前32位当作key,循环异或后面的数据，来解码出源文件数据。

![图片.png](https://image.3001.net/images/20200117/1579250872_5e2174b876021.png!small)

EnCode函数，也就是加密函数，和Decode函数同理

![图片.png](https://image.3001.net/images/20200117/1579250881_5e2174c18df0e.png!small)

Get函数

从配置信息里面的c2地址下载数据，通过DecodeData函数解码后传入Process执行，

![图片.png](https://image.3001.net/images/20200117/1579250891_5e2174cb71858.png!small)

Process函数上半部分

Process函数主要将传入的数据文件解析执行，先申请出一个Loader类型，加载传入的data,然后将data解base64后，根据解码出来的数据的第一个byte来选择需要执行的功能

![图片.png](https://image.3001.net/images/20200117/1579250901_5e2174d51dbb7.png!small)

Process函数中间部分

函数可执行的主要功能:

1\. 获取系统信息 写入.sif文件

![图片.png](https://image.3001.net/images/20200117/1579250911_5e2174dfcc454.png!small)

2\. 获取文件列表 写入.flc文件

![图片.png](https://image.3001.net/images/20200117/1579250918_5e2174e6b061a.png!small)

3\. 获取指定文件，先复制移动到.fls

![图片.png](https://image.3001.net/images/20200117/1579250926_5e2174ee566ec.png!small)

4\. 修改setting

![图片.png](https://image.3001.net/images/20200117/1579250935_5e2174f700acd.png!small)

5\. 更新c2地址

![图片.png](https://image.3001.net/images/20200117/1579250945_5e2175013a4c9.png!small)

6\. 准备上传文件

![图片.png](https://image.3001.net/images/20200117/1579250953_5e217509482b2.png!small)

7\. 加载文件执行

![图片.png](https://image.3001.net/images/20200117/1579250959_5e21750f6ad35.png!small)

8\. 设置文件最大尺寸

![图片.png](https://image.3001.net/images/20200117/1579250967_5e21751738069.png!small)

9\. 下载文件

![图片.png](https://image.3001.net/images/20200117/1579250976_5e2175205d207.png!small)

Case功能列举表格：

Case值| 功能  
---|---  
1| 获取系统信息 写入.sif文件  
2| 获取文件列表 写入.flc文件  
3| 获取指定文件，先复制移动到.fls  
4| 修改setting  
5| 更新c2地址  
6| 准备上传文件  
7| 加载文件执行  
8| 设置文件最大尺寸  
9| 下载文件  
  
![图片.png](https://image.3001.net/images/20200117/1579250984_5e217528881bd.png!small)

Process函数下半部分

Process函数执行出现异常就写入随机命名.err文件

![图片.png](https://image.3001.net/images/20200117/1579250992_5e2175308ffaa.png!small)

POST函数上半部分

![图片.png](https://image.3001.net/images/20200117/1579251002_5e21753a7196d.png!small)

POST函数中间部分

![图片.png](https://image.3001.net/images/20200117/1579251012_5e2175449f44e.png!small)

POST下半部分

![图片.png](https://image.3001.net/images/20200117/1579251021_5e21754da738e.png!small)

POST函数结束部分

把执行写入的文件，也就是GET获取请求执行后的信息或者程序异常的的信息写入的文件，准备上传同时删除写入的文件，如果执行报错依然写入.err文件

![图片.png](https://image.3001.net/images/20200117/1579251030_5e217556a6b51.png!small)

UploadFile函数

通过之前post函数更具文件的后缀入.sif、.fls、.err等来设置type类型，构造包体，然后发包，也就是我们说的回显。改后面基本分析结束

后门获取的信息表：

盘符信息：| 磁盘大小  
---|---  
磁盘名字  
可用空间  
总空间  
磁盘格式  
目录信息：| 目录大小  
目录名字  
目录创建时间  
目录写入时间  
目录读写属性  
文件信息：| 文件大小  
文件名字  
文件创建时间  
文件写入时间  
文件读写属性  
  
**三.活动总结:** ****

 **1).针对中国的攻击:** ****

部分诱饵文档如下(介于一些因素这些样本将不会给出相应的样本hash)

 ****

![图片.png](https://image.3001.net/images/20200117/1579251041_5e217561db226.png!small)![图片.png](https://image.3001.net/images/20200117/1579251050_5e21756ac826c.png!small)

****

**![图片.png](https://image.3001.net/images/20200117/1579251072_5e217580116de.png!small)![图片.png](https://image.3001.net/images/20200117/1579251078_5e217586a7ad9.png!small)**

****

****

**![图片.png](https://image.3001.net/images/20200117/1579251089_5e2175918ad31.png!small)**

**![图片.png](https://image.3001.net/images/20200117/1579251099_5e21759bc0a46.png!small)  
**

![图片.png](https://image.3001.net/images/20200117/1579251110_5e2175a6ac332.png!small)  
****

1.a文件与其攻击巴基斯坦的样本有着一定的相似性

![图片.png](https://image.3001.net/images/20200117/1579251119_5e2175afd09d8.png!small)

但是有略微的不同

攻击中国的样本直接调用ActiveX控件对象进行解密

![图片.png](https://image.3001.net/images/20200117/1579251126_5e2175b6dfce8.png!small)

而攻击巴基斯坦的样本则是通过自实现的解密算法进行

![图片.png](https://image.3001.net/images/20200117/1579251139_5e2175c3c209a.png!small)

样本所使用的都是Write.exe与PROPSYS.dll的白加黑组合

其中PROPSYS.dll依旧与上文流程类似

读取其同目录下的tmp文件并且区其前32个字节作为异或解密的秘钥

然后将tmp文件32个字节后的数据解密后内存加载

![图片.png](https://image.3001.net/images/20200117/1579251153_5e2175d1d9b9b.png!small)

同样其解密后的后门与上文针对巴基斯坦的后门类似

![图片.png](https://image.3001.net/images/20200117/1579251163_5e2175dbbb1db.png!small)

****

****

**2).对巴基斯坦的活动** ****

SideWinder除了针对中国的目标之外,其还热衷于针对巴基斯坦的相关在目标,

与针对中国的目标有相同的特点就是Sidewinder组织对巴基斯坦的军事相关的目标也饶有兴趣,并且也会去攻击政府组织

部分诱饵如下

![图片.png](https://image.3001.net/images/20200117/1579251171_5e2175e350c95.png!small)

![图片.png](https://image.3001.net/images/20200117/1579251184_5e2175f0dbd9c.png!small)![图片.png](https://image.3001.net/images/20200117/1579251192_5e2175f806fb1.png!small)![图片.png](https://image.3001.net/images/20200117/1579251200_5e217600bc4e9.png!small)  

该组织在对巴基斯坦的攻击活动中使用了压缩包中带有lnk的攻击手法,该手法在针对中国的活动中并没有很多次的出现

Lnk载荷

针对于Lnk文件的载荷,该组织通过使用mshta.exe远程加载目标hta文件的手法

![图片.png](https://image.3001.net/images/20200117/1579251209_5e2176092a47c.png!small)

Hta文件貌似也有NotNetToScript的工具,并且其采用了不同的加载payload的方式

采用wmi的方式收集本地杀毒软件信息

![图片.png](https://image.3001.net/images/20200117/1579251218_5e217612d1cd2.png!small)

替换掉内置的混淆字符串,将文件解密加载到内存中

![图片.png](https://image.3001.net/images/20200117/1579251228_5e21761cdfe5d.png!small)

调用pink函数

![图片.png](https://image.3001.net/images/20200117/1579251240_5e2176281b870.png!small)参数一为下一阶段的hta文件

参数二是收集到的杀毒软件信息

参数三是被base64加密的doc文件信息

![图片.png](https://image.3001.net/images/20200117/1579251247_5e21762fb5aad.png!small)

参数四是doc诱饵文件名称

内存加载的dll名称为:LinkZip.dll

释放诱饵文档并打开,做到伪装的目的

![图片.png](https://image.3001.net/images/20200117/1579251258_5e21763a89b8c.png!small)

![图片.png](https://image.3001.net/images/20200117/1579251276_5e21764ccaa08.png!small)

下载下一阶段的hta文件并用mshta.exe执行

![图片.png](https://image.3001.net/images/20200117/1579251283_5e217653bba20.png!small)

下一阶段hta的代码与前文的差不多,利用js加载内存执行payload

![图片.png](https://image.3001.net/images/20200117/1579251293_5e21765db600b.png!small)

该一类样本的流程图如下:

![图片.png](https://image.3001.net/images/20200117/1579251301_5e217665a1f39.png!small)

在另一个样本中,我们发现了相同的释放doc的代码

![图片.png](https://image.3001.net/images/20200117/1579251310_5e21766e93a8f.png!small)

Mydoc.docx如下

![图片.png](https://image.3001.net/images/20200117/1579251319_5e21767708190.png!small)

以及类似的函数pink

![图片.png](https://image.3001.net/images/20200117/1579251328_5e217680ced42.png!small)

但是经过分析

这个的第一个参数为exe文件的数据

第二个参数为dll文件的数据

第三个参数是wmic命令收集的杀毒软件信息

  

其C#内存加载的dll为prebothta.dll

其根据不同的杀毒软件信息执行不同的策略

![图片.png](https://image.3001.net/images/20200117/1579251351_5e21769749c18.png!small)

释放lnk到启动文件夹以持久化

![图片.png](https://image.3001.net/images/20200117/1579251359_5e21769f73844.png!small)

释放bat并执行

![图片.png](https://image.3001.net/images/20200117/1579251369_5e2176a9595ad.png!small)

由于该样本的回连下载的服务器已经失效,故不能分析

该一类样本的流程图如下:

![图片.png](https://image.3001.net/images/20200117/1579251376_5e2176b0bb2f2.png!small)

六. **技术特点以及演进** **:** ****

 **注意:该特点不具有普** **适** **性,同时里面给出的时间节点只是在那个时间段内该组织针对目标使用** **最多的**
**手法,不是代表在那个时间段该组织使用的** **全部** **手法,该组织会针对目标的不同进行调整** ****

1) .白加黑的使用

Exe名称| Dll名称| 属性信息  
---|---|---  
Cmdl32.exe| Cmpbk32.dll| Microsoft连接管理器自动下载  
Credwiz.exe| Duser.dll| 系统凭据备份和还原向导  
Write.exe| Propsys.dll| 写字板程序  
Rekeywiz.exe| Duser.dll| EFS REKEY向导  
  
该组织在白加黑的寻找上偏向于寻找系统文件的白加黑利用,在2018年的活动中主要使用cmdl32.exe+cmpbk32.dll与credwiz.exe+duser.dll的两种组合,在2019年的活动中新增加了wrte.exe+propsys.dll与rekeywiz.exe与duser.dll的组合

未来估计会有别的新的白加黑组合的出现

![图片.png](https://image.3001.net/images/20200117/1579251385_5e2176b9f1d2d.png!small)

2）载荷的明文字符的处理方式

该组织在对js脚本内存加载C# dll文件的时候,采用了字符串拼接等手段.其在2019的1月份到10月份通常采用的是base64解密其c#
dll的shellcode然后内存加载,并且其中调用的activexobject都可见,极其方便于分析以及安全软件的查杀,在11月份到12月份针对巴基斯坦的攻击活动中,该组织大幅度的对其明文字符串进行了混淆,主要采用自编的异或算法和base64进行解密操作

![图片.png](https://image.3001.net/images/20200117/1579251395_5e2176c37e7ef.png!small)

3).漏洞文件加载js loader的方式

在2019年1月到3月的活动中,该组织主要采用的是通过漏洞加载远程地址上托管的hta文件,但在2019年3月到12月的活动中,则采用使用在本地释放1.a文件,再加载1.a文件的js代码.其中该组织都会采用命令行替换的方式去加载恶意js

![图片.png](https://image.3001.net/images/20200117/1579251405_5e2176cd166ec.png!small)

4).lnk攻击载荷加载js loader的方式

该组织对于构造lnk文件的载荷也是变化多样,不过其主要是通过使用mshta.exe执行托管于服务器的远程hta文件,不过该组织总是通过不同的手段来掩盖其执行的策略,比如下图中的执行start来拉起mshta以及利用lnk的性质来伪装成ctfmon以欺骗受害者的执行(具体手段请看参考链接中瑞星的报告,这里就不再赘述)

![图片.png](https://image.3001.net/images/20200117/1579251413_5e2176d529b53.png!small)

**六.总结** ****

sidewinder(响尾蛇)组织作为一个迅速进步,以及拥有c++,c#,delphi等后门以及大规模使用js以及开源的工具对其后门进行装载,使用lnk以及文档载荷。并且其诱饵样本的大部分文件都是诱惑力很高的文件，这种高的诱饵文档会加大人员的受害几率.并且使用系统文件的白加黑技术和内存加载技术与杀毒软件进行对抗。

 ****

**七** **.** **IOCs:** ****

 **md5:** ****

D2522E45C0B0D83DDDD3FCC51862D48C

1FE3D9722DB28C2F3291FF176B989**6

444438F4CE76156CEC17883***887DA6

3CD725172384297732222EF9C8F74ADC

C0F15436912D8A63DBB7150D95E6A4EE

C986635**0764F10BCEBE280B05EFE8C

D1C3FA000154DBCCD6E5485A10550A29

B956496C28306C906FDDF08DED1CDF65

A1CA53EFDA160B31EBF07D8553586264

204860CE22C81C6D9DE763C09E989A20

DE7F526D4F60B59BB1626770F329F984

2CB633375A5965F86360E761363D9F2F

5CD406E886BD9444ADEE4E8B62AA56CC

358450E19D38DB77C236F45881DCEBEF

29325CDBDE5E0CF60D277AA2D9BA4537

836419A7A4675D51D006D4CB9102AF9C

A1CA53EFDA160B31EBF07D8553586264

16E561159EE145008635C52A931B26C8

21CC890116ADCF092D5A112716B6A55F

62606C6CFF3867A582F9B31B018DFEA5

52FA30A**ED**C973A0A84F2E93F2432

CE53ED2A093BBD788D49491851BABFFD

737F3AD2C727C7B42268BCACD00F8C66

2D9655C659970145AB3F2D74BB411C5D

032D584F6C01CC184BF07CDEC713E74D

FB362FE18C3A0A150754A7A1AB068F1E

423194B0243870E8C82B35E5298AD7D7

81F9EB617A2176FF0E561E34EF9FF503

7E23C62A81D2BFB90EF73047E170DEA8

58B5A823C2D3812A66BBF4A1EB**97D3

5E98EA66670FA34BF67054FB8A41979C

8DA5206BACACD5C8B316C910E214257F

65F66BC372EA1F372A8735E9862095DA

361DFD8F299DD80546BCE71D156BC78E

1B11A5DD12BB6EC1A0655836D97F9DD7

9B1D0537D0734F1DDB53C5567F5D7AB5

3EE30A5CAC2BEF034767E159865683DF

4513F65BDF6976E93AA31B7A37DBB8B6

FF9D14B83F358A7A5BE77AF45A10D5A2 ****

**C2:** ****

[cdn-in](http://cdn-in)[.]net

urls:

<http://cdn-in>[.]net/includes/b7199e61/-1/7384/35955a61/final

[http://cdn-in[.]net/plugins/-1/7384/true/true/](http://cdn-in.net/plugins/-1/7384/true/true/)

<http://cdn-in>[.]net/includes/b7199e61/-1/7384/35955a61/final

<http://cdn-in>[.]net/plugins/-1/7384/true/true/

msftupdate[.]srv-cdn[.]com

urls:

hxxps://msftupdate[.]srv-cdn[.]com/cdne/plds/zoxr4yr5KV[.]hta

hxxps://msftupdate[.]srv-cdn[.]com/fin[.]hta

[www[.]google[.]com[.]d-dns[.]co](http://www.google.com.d-dns.co/includes/686a0ea5/-1/1223/da897db0/final.hta)

urls:

hxxp://[www[.]google[.]com[.]d-dns[.]co/includes/686a0ea5/-1/1223/da897db0/final[.]hta](http://www.google.com.d-dns.co/includes/686a0ea5/-1/1223/da897db0/final.hta)

webserv-redir[.]net

urls:

hxxp://webserv-redir[.]net/includes/b7199e61/-1/5272/fdbfcfc1/final

pmo[.]cdn-load[.]net

urls:

hxxp://pmo[.]cdn-load[.]net/cgi/5ed0655734/-1/1078/d70cc726/file[.]hta

fb-dn[.]net

urls:

hxxp://fb-dn[.]net/disrt/fin[.]hta

cdn-edge[.]net

urls:

hxxp://cdn-edge[.]net/checkout[.]php

hxxp://cdn-edge[.]net/cart[.]php

hxxp://cdn-edge[.]net/amount[.]php

ap12[.]ms-update-server[.]net

urls:

hxxp://ap12[.]ms-update-server[.]net/checkout[.]php

hxxp://ap12[.]ms-update-server[.]net/cart[.]php

hxxp://ap12[.]ms-update-server[.]net/amount[.]php

s2[.]cdn-edge[.]net

urls:

hxxp://s2[.]cdn-edge[.]net/checkout[.]php

hxxp://s2[.]cdn-edge[.]net/cart[.]phpB

hxxp://s2[.]cdn-edge[.]net/amount[.]php

webserv-redir[.]net

urls:

hxxp://webserv-redir[.]net/plugins/-1/5272/true/true/

hxxp://webserv-redir[.]net/plugins/-1/5272/true/true/done

s12[.]cdn-apn[.]net

urls:

hxxp://s12[.]cdn-apn[.]net/checkout[.]php

hxxp://s12[.]cdn-apn[.]net/cart[.]php

hxxp://s12[.]cdn-apn[.]net/amount[.]php

cdn-do[.]net

urls:

hxxp://cdn-do[.]net/plugins/-1/7340/true/true/

cdn-list[.]net

urls:

hxxp://cdn-list[.]net/KOmJg2XSthl3PRhXnB6xT6Wo967B1n5uGf7SfiBC/-1/7340/b729d30c/css

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/1

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/2

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/3

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/v4[.]0[.]30319

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/4

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/5

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/6

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/7

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/8

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/9

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/10

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css

<http://cdn-in>[.]net/includes/b7199e61/-1/7384/35955a61/final

<http://cdn-in>[.]net/plugins/-1/7384/true/true/

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/1

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/2

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/3

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/v4[.]0[.]30319

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/4

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/5

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/6

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/7

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/8

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/9

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css/10

<http://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/134/7e711ada/res/css

<https://cdn-list>[.]net/1SdYMUrbdAfpgSt3Gv13U8Jca6qOvI4I2Fa1zSCT/-1/7384/43e2a8fa/css

sd1-bin[.]net

urls:

[https://www.sd1-bin[.]net/images/2B717E98/-1/12571/4C7947EC/main.file.rtf](https://www.sd1-bin.net/images/2B717E98/-1/12571/4C7947EC/main.file.rtf)

reawk[.]net

ap1-acl[.]net

 **八．参考链接** ****

http://it.rising.com.cn/dongtai/19639.html

https://www.antiy.cn/research/notice&report/research_report/20190508.html

https://www.freebuf.com/articles/network/196788.html

http://it.rising.com.cn/dongtai/19658.html

http://it.rising.com.cn/dongtai/19655.html

