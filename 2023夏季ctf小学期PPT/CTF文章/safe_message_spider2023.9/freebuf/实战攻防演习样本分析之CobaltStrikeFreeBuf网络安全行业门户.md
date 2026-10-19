## 一、概述

CobaltStrike是一款由美国Strategic
Cyber公司开发的渗透测试套件。其集成了远程Shell、傻瓜式提权、用户凭据窃取、socks代理、文件操作，伪装钓鱼等选项，几乎涵盖了APT攻击链中的所有技术环节。同时在载荷方面，因为CS的beacon
loader程序是一段体积只有几百字节的ShellCode。因此渗透人员很容易对Loader做代码加密变形，达到规避大部分主流杀软的目的，还可以进一步对Loader进行“变形”，使用PowerShell，Vbscript，JavaScript等动态脚本对Loader进行“包装”，也常被用于实战攻防演练。

![1617160088_6063e7986d825b8f4cb69.png!small?1617160088730](https://image.3001.net/images/20210331/1617160088_6063e7986d825b8f4cb69.png!small?1617160088730)

图1 Cobalt Strike视图

近期，随着实战攻防演练的临近，奇安信威胁情报中心在 **基于红雨滴云沙箱部署的APT攻击狩猎流程** 中，捕获了多例实战攻防演习样本。样本主要以“
**???安全防护** ”、“ **自查工具** ”、“ **Windows激活工具** ”、“ **关于护网攻防演练员工行为监管人员名单**
”等话题为诱饵。而此类样本最终执行的Payload往往均为 **CobaltStrike** 生成的载荷。

## 二、 CobaltStrike样本红雨滴云沙箱报告链接

本次捕获到使用CobaltStrike的实战攻防演习样本部分红雨滴云沙箱分析报告列表：

 **CobaltStrike** **样本名称**

|

 **MD5**

|

 **红雨滴云沙箱报告链接**  
  
---|---|---  
  
???安全防护.exe

|

a2bbfcbc00a5ec166c286d8b007ebc37

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhspjX-xyHYZ1u3thkM)  
  
自查工具.exe

|

0e17bedfc31a542c680319944b01a35f

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhtDugQxyHYZ1u3tiq5)  
  
windows激活工具-请关闭杀软后使用.exe

|

1bda3f9bf1a4d96ff9ddf15201688a59

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhtE4CYxyHYZ1u3tirW)  
  
关于护网攻防演练员工行为监管人员名单.exe

|

5a6efa78cbee89097ce308148e972de1

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhth_N-xyHYZ1u3tjQ5)  
  
七芒星蓝黑色简历模板.doc

|

6e6cc414ce98d5ab74641cbf7da426ca

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhcmtAbYZ08-684UW4T)  
  
## 三、案例：伪装成某安全防护软件的样本分析

### 3.1 样本基本信息

 **红雨滴云沙箱报告链接**

|

 **[https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhspjX-xyHYZ1u3thkM](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhspjX-xyHYZ1u3thkM)**  
  
---|---  
  
 **样本文件名**

|

???安全防护.exe  
  
 **样本MD5**

|

a2bbfcbc00a5ec166c286d8b007ebc37  
  
 **样本类型**

|

PE64 Executable for MS Windows (EXE)  
  
 **样本大小**

|

17920字节  
  
 **RAS** **检测结果**

|

 **CobaltStrike**  
  
 **样本基因特征**

|

检测虚拟机 联网行为 HTTP通信 解压执行 探针 C&C 检测沙箱  
  
 **网络行为**

|

hxxp://111[.]229.107.34/Rh2q

hxxp://111[.]229.107.34/load  
  
### 3.2 使用红雨滴云沙箱分析样本

本次发现的一例针对防守方的钓鱼样本以攻防演习为诱饵投递< **???** **安全防护.exe**
>文件。该文件在用户电脑上运行之后，将异或解密自身数据得到一段shellcode，这段shellcode执行后会从C&C服务器下载后续到内存加载执行，以实现对用户主机的完全控制。

首先，用户使用TI账户登录威胁情报中心威胁分析平台（ **https://ti.qianxin.com/**
）后，选择文件分析选项卡，既可拖拽投递需要分析的样本文件：

![1617160154_6063e7da4163cb6ea92e8.png!small?1617160154673](https://image.3001.net/images/20210331/1617160154_6063e7da4163cb6ea92e8.png!small?1617160154673)

图2 Alpha分析平台红雨滴云沙箱入口

也可以通过访问红雨滴云沙箱入口（ **https://sandbox.ti.qianxin.com/sandbox/page**
）上传待分析文件。红雨滴文件深度分析平台提供三大功能：

>
> 1.上传可疑文件进行样本检测，支持exe、dll、doc、docx、docm、rtf、xls、xlsx、xlsm、ppt、pptx、pptm、mht、pub、mdb、7z、zip、tar、gz、arj、rar、cab、ace、eml、msg、swf、jar、msi、pfm、pdf、chm、equation、lnk、hwp、elf、apk、py、ps1、bat、js、vbs、html、hta、wsf、eps、jse、vbe、bash、url、iqy、slk等
> **51种文件格式** 解析。
>
> 2.根据关键信息进行样本检索，普通检索输入文件HASH值（MD5或SHA1）。 **高级检索**
> 则可以通过文件类型、文件大小、释放文件名称、释放文件HASH、动态行为domain、动态行为IP、动态行为URL等 **多条件组合检索** 。
>
> 3.扫描可疑URL。

![1617160164_6063e7e44be59cef48fc9.png!small?1617160164528](https://image.3001.net/images/20210331/1617160164_6063e7e44be59cef48fc9.png!small?1617160164528)

图3 红雨滴高对抗沙箱分析入口

在上传待分析文件后，可以手动设置沙箱分析参数：分析环境（操作系统）、分析时长等。由于
**红雨滴高对抗沙箱针对各类样本已经进行了智能化判定，所以基本上以默认方式提交检测即可** 。点击“ **开始分析**
”按钮后，会自动跳转到对应样本的分析检测结果页面。稍等数分钟则可以看到整个样本的详细分析报告。

3.2.1 **强大的IOC信息关联查询**

红雨滴云沙箱提供有强大的IOC信息关联查询功能（红雨滴云沙箱 **高级搜索** 也提供了相同的功能入口）。在云沙箱报告的多个元素中都提供了TI及
**关联查询** 的功能。比如，在沙箱报告会话信息给出的IP地址的右侧，便有 **TI查询** 和 **关联查询** 两种查询功能按钮。

其中 **关联查询** 可以为用户 **查询红雨滴云沙箱海量样本里拥有相同元素的样本集** 。我们这里先以另外一个实战攻防演习样本为例：

 **红雨滴云沙箱报告链接**

|

**[https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhcmtAbYZ08-684UW4T](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhcmtAbYZ08-684UW4T)**  
  
---|---  
  
 **样本文件名**

|

七芒星蓝黑色简历模板.doc  
  
 **样本MD5**

|

6e6cc414ce98d5ab74641cbf7da426ca  
  
 **样本类型**

|

Word Microsoft Office Open XML Format Document  
  
 **样本大小**

|

732874字节  
  
 **RAS** **检测结果**

|

 **CobaltStrike CobaltVBA Macros_Exec Macros_Inject Macros_File
Macros_AutoExec**  
  
 **样本基因特征**

|

检测虚拟机 注入 shellcode 解压执行 探针 检测沙箱 联网行为  
  
 **网络行为**

|

http://167.160.188.28:58586/WSiI

http://167.160.188.28:58586/match  
  
点击报告右侧 **导航栏** 中的 **网络行为** 后，再点击 **会话信息**
中IP地址后的对角圈图标，便可以查询并列出红雨滴云沙箱内所有访问过该IP地址的样本沙箱报告列表。

![1617160208_6063e81003dc592fd08c1.png!small?1617160208255](https://image.3001.net/images/20210331/1617160208_6063e81003dc592fd08c1.png!small?1617160208255)

图4 IP地址167.160.188.28 **关联查询** 链接：

<https://sandbox.ti.qianxin.com/sandbox/page/result?search=ip%3D167.160.188.28>

可以看到，关联到的样本中除了有使用同样的C2地址的PE样本外，还有使用 **Office模板注入** 攻击的HW样本，以及使用 **Opcode恶意宏**
的HW攻击样本。这样， **使用该功能我们可以非常快速的关联使用了相同C2的同类样本** ，这在HW期间的样本分析和关联中有非常大的实战作用。

![1617160216_6063e8183ecf57dd5b5fe.png!small?1617160216494](https://image.3001.net/images/20210331/1617160216_6063e8183ecf57dd5b5fe.png!small?1617160216494)

图5 红雨滴云沙箱关联查询

和167.160.188.28关联的样本列表如下：

 **和167.160.188.28关联的样本MD5**

|

 **红雨滴云沙箱报告链接**  
  
---|---  
  
affcf1121304f3286fa5e93181964963

|

[https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhdQb9mYZ08-684UYcl](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhdQb9mYZ08-684UYcl)  
  
1037ad809ba659c18d33a1fbca44d2d0

|

[https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhdMS1rYZ08-684UYag](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhdMS1rYZ08-684UYag)  
  
而点击 **TI查询** 将跳转到红雨滴另一自研产品<威胁研判分析平台>。

![1617160379_6063e8bb55c9bec4ad286.png!small?1617160379605](https://image.3001.net/images/20210331/1617160379_6063e8bb55c9bec4ad286.png!small?1617160379605)

图6 红雨滴云沙箱网络行为

 **TI** **查询** 跳转至<威胁研判分析平台>后，可以帮助我们快速判别该IP地址的使用性质、在攻击活动中所使用过的端口号、地理位置、及用户类型等。

![1617160407_6063e8d730a366e4222e3.png!small?1617160407472](https://image.3001.net/images/20210331/1617160407_6063e8d730a366e4222e3.png!small?1617160407472)

图7 红雨滴威胁研判分析平台IP查询页面

红雨滴云沙箱不但可以提供该IP的域名反查信息、主机信息及近期活动记录。而且还可以根据域名解析记录获取到一段时间内的其他IOC信息。

![1617160414_6063e8de672a1ce8dc2f7.png!small?1617160414746](https://image.3001.net/images/20210331/1617160414_6063e8de672a1ce8dc2f7.png!small?1617160414746)

图8 红雨滴威胁研判分析平台IP查询信息

同时，<威胁研判分析平台>还提供社区情报模块，方便用户记录与分享捕获到的情报信息。这无疑是红雨滴云沙箱的又一强大之处。

![1617160460_6063e90c1c45f72c02946.png!small?1617160460347](https://image.3001.net/images/20210331/1617160460_6063e90c1c45f72c02946.png!small?1617160460347)

![1617160467_6063e9139fbea4d9ab65a.png!small?1617160467970](https://image.3001.net/images/20210331/1617160467_6063e9139fbea4d9ab65a.png!small?1617160467970)

图9 红雨滴威胁研判分析平台社区情报

3.2.2 **样本概要信息和威胁情报关联**

继续使用文章开头的样本进行分析，红雨滴云沙箱报告顶端是对该样本检测的概要信息和威胁情报关联信息。其中概要信息包括文件的MD5、SHA1、SHA256等
**HASH信息** ， **文件类型** 、 **文件大小** 、本次沙箱检测的 **操作系统环境** 信息、 **文件信誉** 、 **RAS**
检测、 **基因特征** 等信息。

此外，恶意评分位于概要信息右侧，是红雨滴云沙箱基于样本分析的所有维度针对该样本的 **智能判断**
，分别有4类不同的判定结果：恶意、可疑、未发现风险、安全。很显然，该样本被明确标记为了 **恶意** 样本。

![1617160481_6063e9216c759f8eb6a90.png!small?1617160482019](https://image.3001.net/images/20210331/1617160481_6063e9216c759f8eb6a90.png!small?1617160482019)

图10 红雨滴云沙箱恶意评分

 **文件信誉** 一栏则表明了该样本已经被云端标记为恶意样本，ExploitKit标签也说明了该样本利用了攻击套件进行开发。

![1617160486_6063e926ebb4c00b843da.png!small?1617160487350](https://image.3001.net/images/20210331/1617160486_6063e926ebb4c00b843da.png!small?1617160487350)

图11红雨滴云沙箱文件信誉判断

 **RAS** **检测结果** 则是红雨滴团队自研的APT样本检测引擎对该样本深度扫描的结果，可以看到该样本被RAS引擎检测为
**CobaltStrike** ，也就表示样本 **由CobaltStrike框架生成** 。

![1617160493_6063e92d2839983e953c7.png!small?1617160493523](https://image.3001.net/images/20210331/1617160493_6063e92d2839983e953c7.png!small?1617160493523)

图12 红雨滴云沙箱RAS检测结果

 **基因特征** 则是红雨滴云沙箱基于动静态行为识别的样本动静态相关的标签，可疑看到该样本具有：虚拟环境监测和C2回连的功能。

![1617160498_6063e932935ae278150ff.png!small?1617160498911](https://image.3001.net/images/20210331/1617160498_6063e932935ae278150ff.png!small?1617160498911)

图13 红雨滴云沙箱基因特征检测结果

 **威胁情报** 一栏则会基于红雨滴云沙箱检测及触发的相关IOC对象进行关联匹配，这里可以看到该样本执行后将访问一个境内已经被标记为
**CobaltStrike** 木马曾经回连过的IP地址。

![1617160505_6063e9393d318a31c48d8.png!small?1617160505505](https://image.3001.net/images/20210331/1617160505_6063e9393d318a31c48d8.png!small?1617160505505)

图14 威胁情报关联信息

3.2.3 **行为异常**

红雨滴高对抗沙箱针对分析的样本智能的输出了丰富的行为异常分析结果，分别会以红色、黄色和绿色顺序排列样本执行过程中的异常行为，红色代表高危，粉色代表中危，绿色代表一般的低危行为。

通过云沙箱对该样本的行为异常分析结果可知，样本的HTTP流量中包含了可疑特征，疑似在通讯过程中传输有恶意流量。除此之外，该样本还具有延迟分析的进程以及流量劫持等。

![1617160513_6063e94152441fee28444.png!small?1617160513813](https://image.3001.net/images/20210331/1617160513_6063e94152441fee28444.png!small?1617160513813)

图15 红雨滴云沙箱行为异常结果

3.2.4 主机行为及网络行为

红雨滴云沙箱提供的主机行为分析图也是非常的简洁明了，通过该样本的主机行为分析图，我们能够快速地得到恶意样本的执行流程：该样本启动后会为自身分配内存空间并更改执行权限。在一系列操作后最终连接IP地址：
**111[.]229.107.34** 。

![1617160519_6063e947583b2dd6a79c4.png!small?1617160519698](https://image.3001.net/images/20210331/1617160519_6063e947583b2dd6a79c4.png!small?1617160519698)

图16 红雨滴云沙箱主机行为信息

## 四、样本分析总结

至此，通过红雨滴高对抗沙箱的辅助分析，我们很容易借助沙箱的帮助出具一份较为详细的分析报告，还是以该样本为例：

> 1.样本运行后先创建进程解密自身
>
> 2.加载执行解密后的shellcode
>
> 3.shellcode访问C2下载后续payload执行远控功能

![1617160526_6063e94e401f7c5594cae.png!small?1617160526578](https://image.3001.net/images/20210331/1617160526_6063e94e401f7c5594cae.png!small?1617160526578)

图17 CobaltStrike框架生成的Beacon木马

![1617160533_6063e9552436e39274912.png!small?1617160533599](https://image.3001.net/images/20210331/1617160533_6063e9552436e39274912.png!small?1617160533599)

图18 C2下载后续payload执行

## 五、相关疑似实战攻防演习样本列表

 **MD5**

|

 **红雨滴云沙箱报告链接**  
  
---|---  
  
affcf1121304f3286fa5e93181964963

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhdQb9mYZ08-684UYcl)  
  
1037ad809ba659c18d33a1fbca44d2d0

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhdMS1rYZ08-684UYag)  
  
a2bbfcbc00a5ec166c286d8b007ebc37

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhspjX-xyHYZ1u3thkM)  
  
0e17bedfc31a542c680319944b01a35f

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhtDugQxyHYZ1u3tiq5)  
  
1bda3f9bf1a4d96ff9ddf15201688a59

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhtE4CYxyHYZ1u3tirW)  
  
5a6efa78cbee89097ce308148e972de1

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhth_N-xyHYZ1u3tjQ5)  
  
6e6cc414ce98d5ab74641cbf7da426ca

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhcmtAbYZ08-684UW4T)  
  
dda792b4888ca30847c282f10159934a

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhaihSFYZ08-684T6Jo)  
  
b13d0ad03be1cf2039bbb76f5134bcc6

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhc57KFYZ08-684UX9_)  
  
532cf5859c8efe4ede6c0e30b5567b4c

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhaSN5PYZ08-684TxMt)  
  
a67b0ea7cfeac2fde28532c91f2bad4a

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhd-ppFYZ08-684UaZ0)  
  
1718f6fa742e78ca55e13e547f743088

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhAieO9YZ08-684P36Y)  
  
a8788d42b22099df32bd698b8bd97aa5

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhXtY7OxyHYZ1u3qTPK)  
  
ff65906a4f30c72ff7210a67f446ec5f

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXhoOCwUxyHYZ1u3stlP)  
  
a62fdc271222de7369cd8049d5a616f7

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXg-B4OnYZ08-684PX8h)  
  
a906eea4771429bf6761779ed4f64b75

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=AXggL75cYZ08-684L73q)  
  
ed7d133831a01e00f592856b6ad6da49

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=9e7df029dd4e9e268ce265dc976f57ef0fedeb45)  
  
cc7c023c6e89333f1c3c83dfbb35ef25

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=9d1dbfb27b109c933abf1ca0304cbffc79a8fa68)  
  
124c0de1068e7934b6bef167f8e1ed3d

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=68a9626f1fb1142c1a3ec537b4dfd7e9793b4dad)  
  
859f0a38a3d5a5d1ab0d382eea7a14c7

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=64c601fd741ed1d60b0237f4d8045ba32f082a82)  
  
541b10ea2c93471cc635b9483d66258b

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=9cae7a9968efb81aec571455129330c674ff8885)  
  
cd4d1a91ce591463069b7d14cb34b6a8

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=9e8b15e4c641deb5c1052ae7c3265db4ce2eabd6)  
  
34b59de4c4ac298a983bdf0982e0cfc7

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=1572bc5a2e1d3aa1252064448b9ba6258571e173)  
  
7645a45ef8578f0bffd6f205e02385fd

|

[点击查看红雨滴云沙箱报告](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=bbfd90edfb1bdc2bf27e7314aad9591ab09810eb)  
  
  

