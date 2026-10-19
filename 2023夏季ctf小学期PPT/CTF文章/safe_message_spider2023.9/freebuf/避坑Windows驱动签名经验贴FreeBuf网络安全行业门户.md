## 前言

最近公司在进行NAC网卡驱动的研发，而Windows驱动要想跑起来就必须得进行驱动签名。这中间过程坎坷，我们也在驱动签名上也踩过不少坑，特此记录，希望能帮到有需要的友商。

## 代码签名基础

在开始讲驱动签名之前，我们先简单的科普一下什么是代码签名。

### 什么是代码签名

 **代码签名** （Code signing）是利用 **代码签名证书**
对可执行文件或脚本进行数字签名，以确认软件作者及保证软件在签名后未被修改或损坏的措施，此措施使用加密散列来验证真实性和完整性。简单来说就是进行代码签名后，可以增加程序的可信度。

### 代码签名证书分类

代码签名证书主要分为两类：

 **标准代码签名证书**

标准代码签名(OV)只需要验证申请企业的基本信息、税务信息，验证成功后通过邮件等形式通常针对32/64位应用程序进行签名，以防止各类杀毒软件的误报。仅需较短的处理时间及较低的成本，但无法用于
LSA 和 UEFI 文件签名、无法用于内核模式驱动程序。

 **EV扩展型代码签名证书**

EV扩展型代码签名证书除了验证企业的基本信息、税务信息外，还会对企业的经营地址、申请人身份进行审查，区别于标准代码签名的重要特点是支持 **Windows
10内核驱动文件签名** 和 **消除SmartScreen** 筛选器安全提醒，此外EV代码签名针对内核模式的驱动文件需要进行微软的交叉签名。

 **这里需要注意，驱动文件要用EV证书进行签名才可以用。**

## Windows驱动程序

了解了代码签名之后，再来了解一点关于Windows驱动程序的基础知识：

>   1. Windows驱动程序是一种 **位于内核地址空间** 并且 **工作于内核模式** 的一种特殊的程序类型( .sys 文件 )；
>
>   2. 驱动程序是操作系统信任的一个 **内核扩展模块** ；
>
>   3. 由于驱动程序是工作在内核，极其容易导致系统崩溃蓝屏，所以开发流程相对于普通应用程序会复杂一些；
>
>   4. 驱动程序类似于DLL程序，它是一个回调函数(子程序)的集合体，这些函数由OS在适当的时候调用；
>
>   5. 驱动程序也可以通过 **Windows 内核 API** 获得OS的一些服务。
>
>

## 驱动签名踩坑过程

微软提供的驱动签名有两种方式：

>   * 使用证明签名，仅适用于win10
>
>   * 使用HLK进行认证，适用于win7+win10
>
>

### 前置条件

开始之前进行驱动签名的准备工作，首先需要购买EV证书(我司在ssl.com进行购买)，然后登录到[managecertificates](https://partner.microsoft.com/zh-cn/dashboard/account/managecertificates)，以开发者身份将提前准备好的EV证书提交到微软开发者进行认证。

具体步骤如下：

在微软开发者账户设置中选择管理证书。

>   1. 添加证书；
>
>   2. 下载SignableFile.bin；
>
>   3. 对SignableFile.bin进行签名，比如是在ssl.com买的EV证书，可以使用yubikey+signtool 本地签名，也可以使用
> eSigner进行远程上签名；
>
>   4. 重新上传签完名的SignableFile.bin到微软上，没问题的话证书管理中会有新增的EV证书。
>
>

![](https://image.3001.net/images/20220209/1644377035_620333cbe4d51342cb8cd.png!small)

提交完即可根据自身需求，自由选择签名方式。

## 使用证明签名(attestation-signing)

PS： 证明签名(attestation-signing) 在Win 7上没法使用，已经尝试的签名组合：

    
    
    - Ev sha1+ Ev sha256(交叉签名) + 微软签名  
    - Ev sha1+ 微软签名  
    - Ev sha256 + 微软签名

根据微软文档 [get-drivers-signed-by-microsoft-for-multiple-windows-versions，](https://docs.microsoft.com/zh-cn/windows-hardware/drivers/dashboard/get-drivers-signed-by-microsoft-for-multiple-windows-versions)需提交Hardware Lab Kit (HLK)
微软硬件测试结果到微软测试上。也就是说如果想在Win7上使用，请用HLK，此处已踩坑。

### 创建CAB文件进行提交

此处不包含驱动开发部分，假设已经编译出驱动release，此时需要的打包文件有：

 **相关驱动文件**

> nacndislwf.cat
>
> NacNdisLwf.inf
>
> NacNdisLwf.sys
>
> 需使用MakeCab对驱动程序进行打包，相关makeCab程序及signtool请下载WindowsSDK包
>
> 创建DDF文件(相当于打CAB包的配置文件) ，下面是一个打包NacNdisLwf驱动的示例：
    
    
    ;*** nacndislwf.ddf example  
    ;  
    .OPTION EXPLICIT     ; Generate errors  
    .Set CabinetFileCountThreshold=0  
    .Set FolderFileCountThreshold=0  
    .Set FolderSizeThreshold=0  
    .Set MaxCabinetSize=0  
    .Set MaxDiskFileCount=0  
    .Set MaxDiskSize=0  
    .Set CompressionType=MSZIP  
    .Set Cabinet=on  
    .Set Compress=on  
    ;Specify file name for new cab file  
    .Set CabinetNameTemplate=NacNdisLwf.cab  
    ; Specify the subdirectory for the files.  
    ; Your cab file should not have files at the root level,  
    ; and each driver package must be in a separate subfolder.  
    .Set DestinationDir=NacNdisLwf  
    ;Specify files to be included in cab file  
    C:\tmp\Driver\none\NacNdisLwf.Inf  
    C:\tmp\Driver\none\NacNdisLwf.Sys  
    C:\tmp\Driver\none\nacndislwf.cat

打包前可以先对.cat .sys进行签名，这样签名下来可以有两个证书：一个我们的EV证书、一个微软的证明签名。

    
    
    signtool sign  /as /fd sha256 /sha1 a32e4ea1143e9748389b2f3eb85e496d481ffbeb  /tr http://ts.ssl.com "C:\tmp\Driver\double\NacNdisLwf.sys"  
    signtool sign  /as /fd sha256 /sha1 a32e4ea1143e9748389b2f3eb85e496d481ffbeb  /tr http://ts.ssl.com "C:\tmp\Driver\double\nacndislwf.cat"

调用MakeCab进行打包 (路径需要自己指定)。

    
    
    MakeCab /f "C:\tmp\Driver\DDF\NacNdisLwfWin10.ddf"

提交微软的全部文件必须进行EV/sha256签名。

    
    
    signtool sign /fd sha256 /sha1 a32e4ea1143e9748389b2f3eb85e496d481ffbeb /tr http://ts.ssl.com "C:\tmp\Driver\DDF\disk1\NacNdisLwf.cab"

提交微软测试 [dashboard/hardware/Search。](https://partner.microsoft.com/zh-cn/dashboard/hardware/Search)

![](https://image.3001.net/images/20220209/1644377114_6203341a8968dfb8d5579.png!small)

选择Submit new hardware 提交签名过后的CAB文件，等待微软验证，相关错误会反馈回来；若签名无问题，即可下载已签名完成的文件。

查看结果，可见已经有了微软给的驱动签名。![](https://image.3001.net/images/20220209/1644377159_62033447c5280e39be4a1.png!small)

具体步骤，请参考官方文档微软签名：[attestation-signing-a-kernel-driver-for-public-release。](https://docs.microsoft.com/zh-cn/windows-hardware/drivers/dashboard/attestation-signing-a-kernel-driver-for-public-release)

## 使用HLK签名认证

### 搭建HLK测试环境

PS：具体请参考微软文档： [windows-hardware](https://docs.microsoft.com/en-us/windows-hardware/test/hlk/)

大致逻辑是，需要搭建HLK server与HLK client，将需要测试的驱动程序部署在HLK client上，在HLK
server进行控制，HLKserver会对Client执行各种自动化操作，并在server上生成测试结果。

在测试服务器上安装 Controller 和 Studio 去微软下载对应系统版本的安装包 [windows-hardware/test/hlk/](https://docs.microsoft.com/en-us/windows-hardware/test/hlk/)，包名为HLKSetUp.exe，先下载所需要的库及相关资料，下载后进行统一安装。

在Client上安装HLK客户端 确保与server处于同一个局域网域下，ControllerName为server端的设备名
**注意此处不要使用Ip，已踩过坑。**

    
    
    \\<ControllerName>\HLKInstall\Client\Setup.cmd

 **另外还有个坑：Client系统语言请使用英语，不然会出现各种奇奇怪怪的报错。**

创建机器池：客户端安装完成后会打开HLK Studio，点击Configuration可以看到刚刚安装客户端的设备机器
需新建一个机器池，并将这个设备从默认的机器池中拖出去，然后右键更改状态为ready。

之后便可以新建项目，选择测试目标Client上已经安装的驱动进行测试了，这块没啥坑，直接看微软文档即可。

选择Client上的驱动 (先在Client上安装自己的驱动，studio这边刷新之后就会显示)。

![](https://image.3001.net/images/20220209/1644377223_62033487c2b3aa522c1a4.png!small)

在Tests上勾选需要运行的自动测试，点击Run selected进行自动测试。

查看测试结果：遇到失败可以查看原因解决。

![](https://image.3001.net/images/20220209/1644377244_6203349c7cf101da54af1.png!small)

创建提交包：驱动通过验证后需创建提交包进行提交。

点击add Driver Folder 选择提交的驱动相关文件。

nacndislwf.cat

NacNdisLwf.inf

NacNdisLwf.sys

 **点击CreatPackage 进行创建包**

签名：微软是推荐使用Use the certificate
store里面的证书，但我们在插入yubikey打算使用usb密钥的证书对他进行签名时，发现可以选择在yubikey中的证书。但签名时会失败，报错为
**Unable to use the selected certificate to sign the package** ，进入到Event
viewer中查看详情为： **Unable to use the selected certificate to sign the package。**

![](https://image.3001.net/images/20220209/1644377461_620335757ca9abfd7cb14.png!small)

研究了很久，在创建HLKX时只能在这里选择签名，因为HLK不支持signtools。

解决方案1：使用C#的CSP对HLkx进行签名 ，<失败：CSP无法识别sha384 签名>，

解决方案2 ：问SSL.com客服询问解决方法，客服联系相关技术人员回复邮件，结果迟迟未回复。

在相关社区找到资料，看起来是HLK studio只支持sha256签名，不支持新的sha384签名。

指路：[for-a-windows-10-submission-the-input-package-and-the-included-files-must-be-signed-with-sha256-sig#latest](https://community.osr.com/discussion/292981/for-a-windows-10-submission-the-input-package-and-the-included-files-must-be-signed-with-sha256-sig#latest)

通过SSL.com签发的OV证书进行签名
由于之前SSl.com的OV代码证书没有人在使用，所以需要重新创建CSR提交到SSL上重新生成证书(SSL.com的验证流程很慢，正常要3-5天)。

 **获取SSL.com带私钥的OV证书**

查看OV证书是不是带sha256
RSA类型，与EV证书采用相同的操作(下载SignableFile.bin本地使用SignTool签名，上传到微软开发者验证)。在Use the
certificate store中选择导入本机OV证书，签名成功。

提交微软认证

 **签名问题小结** ：签名会失败的原因由于EV证书的签名算法为Sha384ECDSA，HLK
Studio不支持认证该算法，只能使用SHA256RSA来解决；只使用HLK认证的签名依然会失败，这是由于Win10以下的驱动使用HCK认证(与HLK一样
HLK是其升级版本)，可以在创建HLK提交后在Package页面选择merge package将HCK数据包合并到HLK中才可以认证Win7。

### HCK 环境搭建

可参考文档： [windows-hardware-certification-kit](https://docs.microsoft.com/en-us/windows/win32/w8cookbook/windows-hardware-certification-kit)大致安装流程与HLK认证基本相同，这里分享一下过程中踩过的坑：

HCKserver版本可以使用server2012及server2008，建议使用2008英文版。

原因：server2012默认开启domin contrller会导致安装失败，且这个domin contrller不是很好关闭，

需要关闭IE ESC配置。

不关闭IE ESC 安装，.net 4.5会失败(点击service manager关闭IE ESC)，

server与client请都使用英文版，避免不必要的问题。

安装后，操作流程与HLK一致，最后package需注意：

不需要签名，直接生成不签名的HCKX文件；

生成后发送hckx文件到HLK server上进行merge package操作。

## 经验教训

建议使用微软的VHLK虚拟机，在本地装hyper-v直接使用虚拟机运行server可以省很多事情。

HLK Client版本请选择对应VHLK虚拟机的版本， [windows-hardware/test/hlk/](https://docs.microsoft.com/en-us/windows-hardware/test/hlk/)上有对应版本的相关说明

当HLKserver环境内没有相关证书时，可以先生成无签名的hlkx，在外部有证书的机器上下载HLK
studio(此时不需要下载contrler)，使用HLK studio打开hlkx重新创建包，并且选择签名重新生成带有签名的hlkx。

使用英文版！使用英文版！使用英文版！重要的事情说三遍。

# 安全拓展

最后再补充一点关于代码签名安全方面的东西，那就是在已签名PE文件里注入shellcode，不会影响签名的有效性，也就是白加黑的手法。虽然这是个老技术，但很多机器都没打这个补丁(KB2893294)。

为了不把本文弄得又臭又长，这里只做个简单的演示。具体原理可见末尾引用：

这里用到的工具(需自行编译)。

    
    
    https://github.com/med0x2e/SigFlip

shellcode国际惯例用的calc。

    
    
    https://github.com/peterferrie/win-exec-calc-shellcode/tree/master/build/bin

白应用，我这边就用火绒，刚好有安装包，从下图可以看到程序的签名：

![](https://image.3001.net/images/20220209/1644377549_620335cda90f6d53c9272.png!small)

开始把shellcode注入到hr.exe，指定加密key为test，需要注意的是文件的hash会变的，但是数字签名仍有效。

![](https://image.3001.net/images/20220209/1644377607_62033607222be4fa46cca.png!small)

再看看注入后(hrxx.exe)的签名，还是有效的。

![](https://image.3001.net/images/20220209/1644377620_62033614ea3937616ac96.png!small)

用loader配合白应用(hrxx.exe)执行shellcode，可以看到calc顺利弹出。

![](https://image.3001.net/images/20220209/1644377632_620336201d8dfe8c7742d.png!small)

更多用法，请大家自行发挥想象。

##  **References**

>   * <https://www.zhihu.com/question/27084785/answer/1587201371>
>
>   * <https://blog.csdn.net/autumn20080101/article/details/7580829>
>
>   * <https://x.hacking8.com/x.hacking8.com/post-427.html>
>
>   * <https://docs.microsoft.com/en-us/windows-hardware/test/hlk/>
>
>

本文作者@云山雾隐研发安全团队，文章若有不妥之处请联系指正，欢迎大家留言参与讨论。

