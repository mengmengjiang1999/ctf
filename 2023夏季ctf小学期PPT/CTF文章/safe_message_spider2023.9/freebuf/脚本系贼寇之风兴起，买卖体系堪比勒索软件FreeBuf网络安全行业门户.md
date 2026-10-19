**近日，奇安信病毒响应中心在日常黑产挖掘过程中发现一个基于脚本的木马架构，该脚本木马最早出现于2018年或更早，至今一直处于活跃状态。同时在日常样本分析过程中我们发现基于脚本的木马架构越来越多，有些未知的木马架构可能已经被用于APT攻击，这引起了我们对这类样本的关注。**  

该组织通常会投放带有恶意Lnk的Zip文件，受害者双击Lnk后会释放恶意的JS木马，初次运行时，js木马会读取Lnk中的附加数据，释放诱饵。第二次运行时会实现持久化操作，通过git、reddit等获取远程服务器IP，注册ID号。再次运行时开始执行监控逻辑，从远程服务器接收命令

## 样本分析

样本信息如下：

 **** | **MD5** | **Packer/compiler** | **类型**  
---|---|---|---  
**Patel compliance documents.zip** | 3fab9cd9a1da290bdf99256c1f51a4e9 | None |
Zip文件  
  
压缩包内容如下：

![](https://image.3001.net/images/20200604/1591240910_5ed868ceb0f0e.png!small)

四个Lnk释放的JS Rat相同，奇安信新一代反病毒引擎可对Lnk样本进行精确检测

![](https://image.3001.net/images/20200604/1591240916_5ed868d4dc192.png!small)

诱饵内容整理如下：

![](https://image.3001.net/images/20200604/1591240924_5ed868dc774b8.png!small)

  

 **文件名** | **MD5** | **Packer/compiler** | **类型**  
---|---|---|---  
**reportapi.js** | 3fab9cd9a1da290bdf99256c1f51a4e9 | None | Zip文件  
  
VT查杀效果如下：

![](https://image.3001.net/images/20200604/1591240929_5ed868e116781.png!small)

结合js中出现的字符串，我们将该其命名为tranJS Rat，首先会对变量进行初始化，可以看到最新版的版本号为4.0，这说明该JS木马已经存在很长一段时间。

![](https://image.3001.net/images/20200604/1591240950_5ed868f6c92c6.png!small)

开始运行时会判断路径，并调用FirstTimeRun函数

![](https://image.3001.net/images/20200604/1591240957_5ed868fde37bc.png!small)

设置运行目录，从Lnk文件中读取诱饵文件并打开

![](https://image.3001.net/images/20200604/1591240964_5ed86904ded48.png!small)

拷贝到运行目录并再次运行

![](https://image.3001.net/images/20200604/1591240970_5ed8690ab0e11.png!small)

第二次运行时会从

[www.digitalpoint.com/members/bliblobla.943007/](http://www.digitalpoint.com/members/bliblobla.943007/)

[www.reddit.com/user/deltadelta2222/comments/gepb1w/hey/](http://www.reddit.com/user/deltadelta2222/comments/gepb1w/hey/)

获取远程服务器的IP地址

![](https://image.3001.net/images/20200604/1591240978_5ed869125dba0.png!small)

访问的页面如下

![](https://image.3001.net/images/20200604/1591240983_5ed86917e74cc.png!small)

远程服务器地址：139.28.37.63

之后会执行SecondTimeRun函数

![](https://image.3001.net/images/20200604/1591240990_5ed8691e39b1b.png!small)生成media.lnk,通过注册表实现持久化

![](https://image.3001.net/images/20200604/1591240997_5ed869250901f.png!small)

之后向远程服务器register.php发起中注册请求，生成ID文件，作为受害者标记

![](https://image.3001.net/images/20200604/1591241001_5ed86929f415d.png!small)

第三次运行时会先读取ID文件。

![](https://image.3001.net/images/20200604/1591241006_5ed8692e16845.png!small)

RunSS函数会执行工作目录下的python.exe，该程序可能是后续从远程服务器下载，故暂不清楚其功能

![](https://image.3001.net/images/20200604/1591241012_5ed869343cc39.png!small)

RunLogger函数运行特定目录下的log收集脚本

![](https://image.3001.net/images/20200604/1591241018_5ed8693a338f4.png!small)

之后进入Main123Loop死循环函数

![](https://image.3001.net/images/20200604/1591241025_5ed8694185de7.png!small)

向view.php页面发起Post消息，获取CMD命令并执行，调试时服务器返回为空

![](https://image.3001.net/images/20200604/1591241032_5ed8694825cb7.png!small)

分别访问send.php和upload.php上传filetoupload.txt和878478ddd3.TMP，

TakeCookies函数会执行特定目录下的ccv.exe收集浏览器Cookie信息，收集完成后向cookies.php页面发起Post上传数据。之后进行sleep操作，每个一段时间执行一次上述操作。

## 关联分析

通过特征关联，我们找到了该团伙近两年使用的几十个样本，部分整理如下

![](https://image.3001.net/images/20200604/1591241044_5ed8695478de6.png!small)

这些压缩包会挂在Google云盘或者相关服务器上

 **ITW** | **** | **** | ****  
---|---|---|---  
**drive.google[.]com/uc?id=1xkf8odEsr4G21zgJK2hiA9s4xJwCunCx
&export=download** |  |  |  
**doc-14-bo-docs.googleusercontent[.]com/docs/securesc/ha0ro937gcuc7l7deffksulhg5h7mbp1/6eg54kqrjlam0a6qu92jbril13fn0mlo/1565928000000/08856126706763057825/*/1xkf8odEsr4G21zgJK2hiA9s4xJwCunCx?e=download**
|  |  |  
**185.61.137[.]141/webdav0xx0x00x0/Yussuf.zip** |  |  |  
  
获取远程服务器的网站页面整理入下：

![](https://image.3001.net/images/20200604/1591241098_5ed8698aa4010.png!small)![](https://image.3001.net/images/20200604/1591241102_5ed8698ed8b2b.png!small)

使用的诱饵类型包括PDF、JPG、PNG、doc

JPG诱饵部分整理如下：

![](https://image.3001.net/images/20200604/1591241110_5ed8699687c71.png!small)

![](https://image.3001.net/images/20200604/1591241119_5ed8699f7882e.png!small)

PDF诱饵整理如下：

![](https://image.3001.net/images/20200604/1591241129_5ed869a9647b3.png!small)

  

![](https://image.3001.net/images/20200604/1591241136_5ed869b07b98a.png!small)![](https://image.3001.net/images/20200604/1591241142_5ed869b636b91.png!small)
![](https://image.3001.net/images/20200604/1591241147_5ed869bb158a6.png!small)

  

Doc诱饵整理如下

![](https://image.3001.net/images/20200604/1591241152_5ed869c07f497.png!small)

关联的大部分Lnk样本的创建时间都为2018-02-13 07:29:00，我们认为这些Lnk文件应该为该团伙的ToolKit生成。

![](https://image.3001.net/images/20200604/1591241163_5ed869cb74474.png!small)Lnk元数据如下：

![](https://image.3001.net/images/20200604/1591241169_5ed869d18a27e.png!small)  
可以看到有些Lnk样本是在Vmware虚拟机中生成的。MachineID以及Mac地址整理如下

 **MachineID** | **** | **** | ****  
---|---|---|---  
**admin-pc** |  |  |  
**me-rm-pc** |  |  |  
**user-pc** |  |  |  
**win-11nvmud2d59** |  |  |  
  
**MAC** **地址** | **** | **** | ****  
---|---|---|---  
**ac:7d:eb:e8:49:02** |  |  |  
**00:50:56:c0:00:08** |  |  |  
**00:23:ae:84:a3:9f** |  |  |  
**00:24:54:5e:ff:82** |  |  |  
  
## tranJS rat版本迭代

目前我们只捕获到了tranJS
rat的V2.8、V3.0、V3.4、V3.5、V3.6、V4.0版本的样本，各版本之间只存在细节的改变，如V2.8版本中存在结束其他的脚本功能

![](https://image.3001.net/images/20200604/1591241181_5ed869ddabb8f.png!small)

在获取远程服务器的IP地址时通过启动IE来实现

![](https://image.3001.net/images/20200604/1591241187_5ed869e3206b7.png!small)

后续像远程服务器发送数据也是通过IE实现

![](https://image.3001.net/images/20200604/1591241192_5ed869e8e7f80.png!small)

在V3.0版本中，GetCommand函数返回的值也可能是第二阶段的下载地址，ProcessCmd函数实际上实现了下载者的功能，当没有匹配到时才会执行cmd命令，而下载者的功能在V4.0中删除了

![](https://image.3001.net/images/20200604/1591241205_5ed869f5579e8.png!small)

在V3.4中才加入了StartLogger函数

![](https://image.3001.net/images/20200604/1591241210_5ed869faeed01.png!small)

进一步对ProcessCmd函数进行了扩充，增加了上传的功能

![](https://image.3001.net/images/20200604/1591241216_5ed86a0043de3.png!small)

注册ID时发送的Post数据会带有本机的CPU和用户名信息

![](https://image.3001.net/images/20200604/1591241220_5ed86a04a73e4.png!small)

V3.5并没有明显的变化，到了V3.6时Process123Cmd函数又新增了退出的功能

![](https://image.3001.net/images/20200604/1591241227_5ed86a0bdd6df.png!small)

## MaaS中的一员？

当我们对一个ITW链接（185.61.137[.]141/webdav0xx0x00x0/yussuf.zip）进行关联时发现了一些有趣的样本，同目录下的样本整理如下：

 **ITW** | **** | **MD5** | ****  
---|---|---|---  
**185.61.137[.]141/webdav0xx0x00x0/ccv.exe** |  |
7fee8223d6e4f82d6cd115a28f0b6d58 |  
**185.61.137[.]141/webdav0xx0x00x0/x.js** |  |
fc0f2042e63aebd9b3aeb639501dd827|  
**185.61.137[.]141/webdav0xx0x00x0/ccv_old.exe** |  |
2f62db1a1f616deabcbe1dda5b17a00b |  
**185.61.137[.]141/webdav0xx0x00x0/ncat.exe** |  |
b6e0db27c2b3e62db616b0918a5d8ed8|  
**185.61.137[.]141/webdav0xx0x00x0/load.ocx** |  |
fcce335ad11f4e568e6fe23ae766b187 |  
**185.61.137[.]141/webdav0xx0x00x0/msfsigned.ocx** |  |
d76f443222551edfe07b357c3bb157da|  
**185.61.137[.]141/webdav0xx0x00x0/msf_64.ocx** |  |
b034972a9540b3b00161310f5bf03fc9 |  
  
在之前对tranJS rat进行分析时曾经提到过ccv.exe是用来收集浏览器Cookie的程序，tranJS
rat刚开始执行时并不释放该程序，后续很有可能从远程服务器下载而来。

![](https://image.3001.net/images/20200604/1591241239_5ed86a178d932.png!small)

经分析，从185.61.137[.]141/webdav0xx0x00x0/这个目录下下载的ccv.exe的确是一款Cookie提取工具，支持/scookiestxt命令输出。

![](https://image.3001.net/images/20200604/1591241285_5ed86a457ac88.png!small)

且该目录下的x.js为V3.6版本的tranJS
rat，至此我们认为185.61.137[.]141/webdav0xx0x00x0/目录下的部分样本应该为tranJSrat后续执行的内容，185.61.137.141应该为该团伙的资产。当我们对同目录下的load.ocx分析时发现样本由PureBasic编译，编译时间为2020-03-03

![](https://image.3001.net/images/20200604/1591241295_5ed86a4f10f36.png!small)

load.ocx实际上为臭名昭著的more_eggs（SpicyOmelette）恶意软件

![](https://image.3001.net/images/20200604/1591241301_5ed86a5571be5.png!small)该恶意软件目前由资深MaaS提供商在暗网上售卖，已被Cobalt
Gang、Fin6以及其他威胁组织使用，基于现有数据，我们没有发现该团伙的TTP与上述团伙的TTP相重叠的地方，故我们暂且将其命名为一个新的组织Tran
Group。

该服务器上还存在64位的签名失效的SpicyOmelette，VT报毒情况如下：

![](https://image.3001.net/images/20200604/1591241310_5ed86a5ea34c1.png!small)

失效数字签名如下：

![](https://image.3001.net/images/20200604/1591241322_5ed86a6a13b2b.png!small)从导出表可以判断，上述SpicyOmelette家族的dll很有可能被用于Dll-Sideloading

![](https://image.3001.net/images/20200604/1591241328_5ed86a7009eb8.png!small)

## 脚本木马攻击愈演愈烈

近期，在高价值样本挖掘过程中我们发现越来越多的组织开始使用脚本木马进行间谍活动。

 **文件名** | **MD5** | **Packer/compiler** | **类型**  
---|---|---|---  
**Azerbaijan_special.doc** | ba1618a981f755eb752aa5dc90bd70a4 | None | doc文件  
**Azerbaijan_special.doc** | 3aadbf7e527fc1a050e1c97fea1cba4d| None| doc文件  
  
团伙使用带有宏恶意文档利用疫情作为诱饵针对阿塞拜疆政府发起攻击，启用宏后才能阅读文档内容。

![](https://image.3001.net/images/20200604/1591241336_5ed86a78c24d4.png!small)

宏会释放并执行由python编写的木马

![](https://image.3001.net/images/20200604/1591241343_5ed86a7f192e4.png!small)

释放的相关模块如下

![](https://image.3001.net/images/20200604/1591241350_5ed86a861ae9b.png!small)

连接远程服务器

![](https://image.3001.net/images/20200604/1591241355_5ed86a8b39f59.png!small)

支持的命令如下：

![](https://image.3001.net/images/20200604/1591241360_5ed86a90f081d.png!small)

 **命令** | **功能**  
---|---  
**version** | 返回当前版本为4.0  
**ls** | 获取指定路径目录，若指定则获取计算机所有目录  
 **cd** | 改变工作目录  
**sysinfo** | 获取系统，计算机名，用户名，版本号，处理器信息  
 **download** | 从ftp获取文件  
**upload** | 上传指定文件  
 **shot** | 获取屏幕截图并上传  
**cp** | 复制文件  
 **mv** | 移动文件  
**link** | 为指定文件创建硬链接  
 **register** | 创建指定注册表值  
**hide** | 将指定文件属性设置为隐藏或不隐藏  
 **compress** | 将指定文件打包  
**jobs** | 进程相关  
 **exit** | 结束  
**其他** | 远程shell  
  
无独有偶，在年初捕获的中东选手的诱饵中也发现了新型的Python Rat

 **文件名** | **MD5** | **Packer/compiler** | **类型**  
---|---|---|---  
**mofa.docx** | 7c487d8462567a826da95c799591f5fb | None | doc文件  
  
诱饵疑似针对阿联酋政府

![](https://image.3001.net/images/20200604/1591241427_5ed86ad37644d.png!small)

模板注入从谷歌云盘下载dotm，宏会继续从谷歌云盘下载隐写的图片，解密后执行autoit，下载图片解密释放执行经过pyinstall打包后的Rat

![](https://image.3001.net/images/20200604/1591241457_5ed86af129bd2.png!small)

通过Google表单来上传数据

![](https://image.3001.net/images/20200604/1591241470_5ed86afe8d9b6.png!small)

通过Twitter上的内容获取指令

![](https://image.3001.net/images/20200604/1591241496_5ed86b18ec532.png!small)
总结

脚本木马的低可探测性可能是APT组织和黑产团伙对其青睐的原因之一，同时由于脚本之间存在可复用性，会在一定程度上影响安全研究人员溯源的准确性。可以预见未来会有越来越多基于脚本的木马被用于高级威胁对抗的过程中，安全研究人员务必保持警惕，与此同时，奇安信病毒响应中心提醒用户，疫情在家远程办公，不要点击来源不明的邮件和可执行文件，同时提高个人的安全意识，从而可以防止用户隐私信息被盗取的风险，奇安信病毒响应中心会这一趋势进行监控和预警。

同时基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC
等，都已经支持对该家族的精确检测。

## IOC

文件Hash：

3fab9cd9a1da290bdf99256c1f51a4e9

3fab9cd9a1da290bdf99256c1f51a4e9

7fee8223d6e4f82d6cd115a28f0b6d58

fc0f2042e63aebd9b3aeb639501dd827

2f62db1a1f616deabcbe1dda5b17a00b

b6e0db27c2b3e62db616b0918a5d8ed8

fcce335ad11f4e568e6fe23ae766b187

d76f443222551edfe07b357c3bb157da

b034972a9540b3b00161310f5bf03fc9

ba1618a981f755eb752aa5dc90bd70a4

3aadbf7e527fc1a050e1c97fea1cba4d

Host：

139.28.37.63

185.62.190.89

185.61.137.141

dellgenius.hopto.org

 ***参考来源:奇安信威胁情报中心，转载请注明来自FreeBuf.COM**  

