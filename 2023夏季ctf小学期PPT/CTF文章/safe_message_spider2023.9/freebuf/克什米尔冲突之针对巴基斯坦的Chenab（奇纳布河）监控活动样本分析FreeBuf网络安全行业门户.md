## **背景** ****

印巴冲突历来已久，其归根到底是克什米尔问题，克什米尔争端是指印度和巴基斯坦对查谟和克什米尔地区**纷争而引发的一系列问题，克什米尔争端是英殖民主义在1947年撤出印度时留下的。

2019年10月5日，印控克什米尔地区政府办公室遭到***袭击，目前已造成至少14人受伤，再次加剧当地紧张气氛。6日，数千名巴控克什米尔地区民众开始聚集在印巴实际控制区分界线附近，**印控克什米尔地区被封锁。巴基斯坦总理伊姆兰·汗随后在社交平台上表示，希望民众不要越线，任何对印控克什米尔地区的人道主义援助，都会“被印度利用”。

自8月5日印度政府宣布取消宪法赋予印控克什米尔地区的特殊地位后,印巴局势骤然升级。取消特殊地位意味着印控克什米尔地区曾享有的自治权不复存在,而印度宪法将完全适用于这里。印度还封锁了印控克什米尔大部分地区,切断当地对外通讯,包括手机、互联网和固线电话,并增派军队到边界地区。这一单方面改变克什米尔现状的做法立即招来巴基斯坦强烈反弹,巴方随即决定降低与印度的外交关系级别,并中断双边贸易。

而近日，奇安信病毒响应中心捕捉到了一起极具目的性的安卓APK攻击，经过研判发现其攻击目标疑似为巴基斯坦。此次攻击事件涉及的样本乌尔都翻译为“河边”
，联系到奇纳布河（Chenab
River）流域发生过印巴水资源争议，1960年9月达成《印度河水协定》。根据协定，奇纳河、印度河及杰赫勒姆河划归巴基斯坦。奇纳布河（Chenab
River）上游经过经克什米尔查谟（Jammu）地区，目前是巴基斯坦控制区域。有理由相信在8月5日之后，各方在该地区的监控会加强，这次针对奇纳布河（Chenab
River）上游的监控活动，我们正式命名为Chenab。

![图片.png](https://image.3001.net/images/20191023/1571794171_5dafacfbc***c.png!small)

##  **诱饵分析** ****

这次捕获到的apk样本名为“ندائےحق”(乌尔都语：河边)，大家都知道乌尔都语为巴基斯坦的国语，通过伪装为正常应用(恶意样本加载正常应用)来实现全面监控的作用，能实时捕捉到巴基斯坦国内最新动态。“河边”代号可能是基于历史与地理位置，奇纳布河（Chenab
River）存在争议，奇纳布河（Chenab
River）上游又经过克什米尔地区，使人不得不去联想到印巴克什米尔冲突，近年来在“克什米尔”地区的冲突也是愈演愈烈。

通过关联样本分析发现，此框架下适用任何针对任何app进行伪装，在关联样本中发现疑似针对巴基斯坦来伪装相关应用，具有很强的针对性，疑似印度针对巴基斯坦近期制定了监控计划。

诱饵APP图标： 正常APP图标： ![Clipboard
Image.png](https://image.3001.net/images/20191023/1571794185_5dafad0962585.png!small)

样本运行截图：

![图片.png](https://image.3001.net/images/20191023/1571794224_5dafad30db576.png!small)  

样本申请的权限：

![图片.png](https://image.3001.net/images/20191023/1571794250_5dafad4ac8412.png!small)

##  **样本分析** ****

###  **样本概况** ****

文件名称|  29E94BC62CBFA221A051E07E23588016.apk  
---|---  
软件名称| ندائےحق  
软件名称翻译| 河边  
软件包名| com.gellery.services  
MD5| 29E94BC62CBFA221A051E07E23588016  
安装图标|
![图片.png](https://image.3001.net/images/20191023/1571794303_5dafad7fe645d.png!small)  
  
  
### **样本行为描述** ****

此次捕捉的针对***国家的恶意样本，通过释放加载正常的应用程序，

隐藏自身图标来实现隐藏自身，让用户误以为安装并更新了一个正常的应用程序。此恶意程序在后台运行时，则会通过远程服务器下发指令(总计56个指令)来实现对用户进行全方位的监控。其恶意操作有：上传短信信息、上传联系人信息、上传电话记录、屏蔽短信、监听手机状态、开启GPS、远程拍照等操作。

远控指令列表：

网络指令| 功能  
---|---  
msurc| 设置音频源的值  
udlt| 更新配置信息并关闭远程连接  
nofia| 预留  
setscrn| 开启截屏  
nofid| 结束前台服务时删除通知  
uclntn| 设置用户ID并更新设置  
setnoti| 开启通知服务  
setgpse| 开启GPS  
info| 获取设备基本信息及配置信息  
dirs/fldr| 获取SD卡根目录信息  
fles| 获取指定目录下文件信息  
ffldr| 获取指定目录下的文件及目录信息  
filsz| 获取文件信息  
notify| 获取_HAENTIFI  
file/afile| 获取文件数据  
thumb| 获取图片  
cnls| 设置isCancl的值  
delnotif| 删除_HAENTIFI文件  
unsnotif| 注销通知服务  
setnotif| 注册通知服务  
delt| 删除文件  
dowf| 下载指定文件  
capbcam| 后置摄像头拍照并保存  
capfcam| 前置摄像头拍照并保存  
capscrn| 开启截屏  
capscrns| 开启连续截屏  
scresize| 设置屏幕大小  
scrtops| 发送广播  
supdat| 安装并运行指定的apk  
runf| 启动指定的应用  
listf| 向服务器回传文件数据  
procl| 向服务器回传运行程序列表信息  
endpo| 关闭指定应用的进程  
calsre| 设置电话记录的配置信息  
recpth| 上传_HAATNECS_  
calstp| 设置电话记录的配置为false  
stsre| 开启录音  
stpre| 停止录音  
conta| 获取联系人信息  
clogs| 上传电话记录  
vibr\vibrate| 设置手机震动参数  
stoast| 显示指定的通知信息  
gcall| 拨打指定号码  
sesms| 向指定号码发送短信  
lntwok| 上传本地网络信息  
lgps| 开启GPS并进行上传  
clping| 上传ping  
smslg| 上传短信信息  
delth| 删除_HAETALOG_  
smsmon| 注册屏蔽短信服务  
smsmons| 注销屏蔽短信服务  
camoni| 注册电话状态监听服务  
camonis| 注销电话状态监听服务  
  
### **详细代码分析** ****

1、“黑加白”实现隐藏自身

恶意样本运行后会直接从raw目录下释放myapps并保存为myapps.apk,同时会运行此正常的apk应用。

![图片.png](https://image.3001.net/images/20191023/1571794321_5dafad91db173.png!small)![图片.png](https://image.3001.net/images/20191023/1571794326_5dafad96e2f23.png!small)  

当运行了真实的正常apk后，则会隐藏恶意程序自身图标，在后台进行远控操作，这样呈现给用户的效果是安装了一个正常的应用程序

![图片.png](https://image.3001.net/images/20191023/1571794340_5dafada49c652.png!small)  

2、通过实时更新配置文件，来灵活切换远控服务器

连接远程服务器后，则可通过网络发送指令数据包进行远程控制操作。

远程服务器的IP端口信息:

服务器：173.249.50.34 和 shareboxs.net

端口：12182

![图片.png](https://image.3001.net/images/20191023/1571794353_5dafadb1628c2.png!small)

通过配置信息来决定是否连接ip或者域名：

![图片.png](https://image.3001.net/images/20191023/1571794359_5dafadb75d289.png!small)  

3、网络远控指令

指令msurc：设置音频源的值

![图片.png](https://image.3001.net/images/20191023/1571794368_5dafadc097d77.png!small)  

指令udlt: 更新配置信息并关闭远程连接
![图片.png](https://image.3001.net/images/20191023/1571794380_5dafadcc82848.png!small)

  

指令setscrn：开启截屏

![图片.png](https://image.3001.net/images/20191023/1571794454_5dafae1685f9b.png!small)![图片.png](https://image.3001.net/images/20191023/1571794469_5dafae25772d7.png!small)  

指令nofid：结束前台服务时删除通知

![图片.png](https://image.3001.net/images/20191023/1571794478_5dafae2ef3a54.png!small)

指令uclntn：设置用户ID并更新设置

![图片.png](https://image.3001.net/images/20191023/1571794490_5dafae3ab1e0c.png!small)

指令setnoti: 开启通知服务

![图片.png](https://image.3001.net/images/20191023/1571794496_5dafae4053580.png!small)![图片.png](https://image.3001.net/images/20191023/1571794511_5dafae4f095cf.png!small)  

指令setgpse:开启GPS

![图片.png](https://image.3001.net/images/20191023/1571794518_5dafae56647e1.png!small)![图片.png](https://image.3001.net/images/20191023/1571794522_5dafae5a0bc29.png!small)

指令info：获取设备基本信息及配置信息

![图片.png](https://image.3001.net/images/20191023/1571794529_5dafae61811fe.png!small)![图片.png](https://image.3001.net/images/20191023/1571794533_5dafae655344d.png!small)

指令dirs和指令fldr: 获取SD卡根目录信息

![图片.png](https://image.3001.net/images/20191023/1571794542_5dafae6e27344.png!small)  

指令fles: 获取指定目录下文件信息

![图片.png](https://image.3001.net/images/20191023/1571794549_5dafae75878e7.png!small)

指令ffldr：获取指定目录下的文件及目录信息

![图片.png](https://image.3001.net/images/20191023/1571794555_5dafae7b11451.png!small)

指令filsz: 获取文件信息

![图片.png](https://image.3001.net/images/20191023/1571794562_5dafae82248e9.png!small)

指令notifi: 获取_HAENTIFI信息

![图片.png](https://image.3001.net/images/20191023/1571794568_5dafae884529e.png!small)

指令file和afile：获取文件数据

![图片.png](https://image.3001.net/images/20191023/1571794574_5dafae8e4d850.png!small)

指令thumb:获取图片

![图片.png](https://image.3001.net/images/20191023/1571794579_5dafae93ad804.png!small)

指令cnls: 设置isCancl的值

![图片.png](https://image.3001.net/images/20191023/1571794585_5dafae9988c3e.png!small)

指令delnotif: 删除_HAENTIFI

![图片.png](https://image.3001.net/images/20191023/1571794591_5dafae9f933fe.png!small)

指令unsnotif: 注销通知服务

![图片.png](https://image.3001.net/images/20191023/1571794598_5dafaea635802.png!small)

指令setnotif: 注册通知服务

![图片.png](https://image.3001.net/images/20191023/1571794604_5dafaeac953ca.png!small)

指令delt：删除文件

![图片.png](https://image.3001.net/images/20191023/1571794610_5dafaeb2001c1.png!small)

指令dowf：下载指定文件

![图片.png](https://image.3001.net/images/20191023/1571794615_5dafaeb77a260.png!small)

指令capbcam：后置摄像头拍照并保存

![图片.png](https://image.3001.net/images/20191023/1571794622_5dafaebe0260a.png!small)

指令capfcam：后置摄像头拍照并保存

![图片.png](https://image.3001.net/images/20191023/1571794627_5dafaec335e0f.png!small)

指令capscrn：开启截屏

![图片.png](https://image.3001.net/images/20191023/1571794633_5dafaec9c7945.png!small)

指令capscrn：开启连续截屏

![图片.png](https://image.3001.net/images/20191023/1571794639_5dafaecf63f5c.png!small)

指令scresize:设置屏幕大小

![图片.png](https://image.3001.net/images/20191023/1571794644_5dafaed42f4cf.png!small)

指令scrtops:发送广播

![图片.png](https://image.3001.net/images/20191023/1571794649_5dafaed99156e.png!small)

指令supdat:安装并运行指定的apk

![图片.png](https://image.3001.net/images/20191023/1571794656_5dafaee0879c0.png!small)

指令runf: 启动指定的应用

![图片.png](https://image.3001.net/images/20191023/1571794661_5dafaee5bd49f.png!small)

指令listf: 向服务器回传文件数据

![图片.png](https://image.3001.net/images/20191023/1571794667_5dafaeebcaf05.png!small)

指令procl: 向服务器回传运行程序列表信息

![图片.png](https://image.3001.net/images/20191023/1571794673_5dafaef155f95.png!small)

指令endpo: 关闭指定应用的进程

![图片.png](https://image.3001.net/images/20191023/1571794679_5dafaef761d8d.png!small)

指令calsre: 设置电话记录的配置信息

![图片.png](https://image.3001.net/images/20191023/1571794685_5dafaefd0ee38.png!small)

指令recpth: 上传_HAATNECS_

![图片.png](https://image.3001.net/images/20191023/1571794690_5dafaf02ae958.png!small)

指令calstp: 设置电话记录的配置为false

![图片.png](https://image.3001.net/images/20191023/1571794696_5dafaf08db30f.png!small)

指令stsre：开启录音

![图片.png](https://image.3001.net/images/20191023/1571794703_5dafaf0fdb012.png!small)

指令stpre：停止录音

![图片.png](https://image.3001.net/images/20191023/1571794710_5dafaf1617079.png!small)

指令conta：获取联系人信息

![图片.png](https://image.3001.net/images/20191023/1571794715_5dafaf1bc8507.png!small)

指令clogs:上传电话记录

![图片.png](https://image.3001.net/images/20191023/1571794721_5dafaf2173dda.png!small)

指令vibr\vibrate:设置手机震动参数

![图片.png](https://image.3001.net/images/20191023/1571794727_5dafaf27a7d86.png!small)

指令stoast：显示指定的通知信息

![图片.png](https://image.3001.net/images/20191023/1571794735_5dafaf2f5ad16.png!small)

指令gcall：拨打指定号码

![图片.png](https://image.3001.net/images/20191023/1571794743_5dafaf37e95f7.png!small)

指令sesms：向指定号码发送短信

![图片.png](https://image.3001.net/images/20191023/1571794749_5dafaf3d47b65.png!small)

指令lntwok：上传本地网络信息![图片.png](https://image.3001.net/images/20191023/1571794758_5dafaf461c43d.png!small)  

指令lgps:开启GPS并进行上传

![图片.png](https://image.3001.net/images/20191023/1571794771_5dafaf534eacb.png!small)

指令clping:上传ping

![图片.png](https://image.3001.net/images/20191023/1571794776_5dafaf58678b8.png!small)

指令smslg:上传短信信息

![图片.png](https://image.3001.net/images/20191023/1571794782_5dafaf5e681ce.png!small)

指令delth:删除_HAETALOG_

![图片.png](https://image.3001.net/images/20191023/1571794788_5dafaf642b9d6.png!small)

指令smsmon:注册屏蔽短信服务

![图片.png](https://image.3001.net/images/20191023/1571794794_5dafaf6a64b80.png!small)

指令smsmons:注销屏蔽短信服务![图片.png](https://image.3001.net/images/20191023/1571794803_5dafaf7335e8c.png!small)

指令camoni:注册电话状态监听服务

![图片.png](https://image.3001.net/images/20191023/1571794814_5dafaf7eeb21a.png!small)

指令camonis:注销电话状态监听服务

![图片.png](https://image.3001.net/images/20191023/1571794821_5dafaf856b5f5.png!small)  

##  **同源分析** ****

通过关联样本发现了使用同一框架的恶意程序，其核心功能代码大同小异（或减少功能），其主要的核心架构就是通过从res\raw\目录下释放myapps/myappes/myapp.apk(正常应用)然后安装运行，同时伪装恶意程序以隐藏图标的方式在后台一直运行监控获取用户信息。

![图片.png](https://image.3001.net/images/20191023/1571794831_5dafaf8fb23bb.png!small)

其利用框架为：

![图片.png](https://image.3001.net/images/20191023/1571794838_5dafaf9620e53.png!small)

##  **总结** ****

印巴冲突无疑是近年来比较火热的话题之一，本文中疑似针对巴基斯坦的apk样本监控分析，无疑是印巴交锋中的网络战争，谁能先获取对方的最新动向则能及时作出相对应的策略。如果网络战争失利了，无疑于失去先机。

奇安信病毒响应中心将持续对最新的恶意安卓APK攻击活动进行及时分析与更新，目前奇安信全系产品均可对此攻击活动进行报警。

## **IOC** ****

文件Hash：

29e94bc62cbfa221a051e07e23588016

aefaf256916cb229c42ffeb1bca18c39

3588b1efda1863a3a10e8230005d877d

f68617671f1a830648b93350e670f698

1095580e4bece45ce5aaefca6125e6e4

C2地址：

173.249.50.34:12182

shareboxs.net:12182

