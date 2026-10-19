# **概述** ****

近日，奇安信病毒响应中心在日常样本监控过程中发现Hakbit勒索在国内有扩散趋势，经过分析，奇安信已经将其破解，并公布了解密器和解密思路。

Hakbit勒索于11月4日在野外被发现，加密82种文件后缀，传播方式主要为僵尸网络和垃圾邮件，执行过程中会使用开源项目SharpExec用于横向移动扩大受害面积，目前已经检测到国内外用户有小批量的中招。

如果要解密文件请按照文章末尾的解密操作流程来进行操作。

  

#  **详细分析** ****

 **文件名称** ****| chrome32.exe  
---|---  
 **文件类型** ****| Windows PE  
 **MD5** ****| 791f2cb92301fd5709e0bfee741cf6d1  
  
该勒索由.net语言编写，原始样本加有Smart Assembly壳，执行过程中会根据配置项来决定是否执行某些函数，下面会对每一个功能逐一分析：

![图片.png](https://image.3001.net/images/20191111/1573458893_5dc913cd2b479.png!small)

首先会检查是否具有管理员权限，如果有则通过注册表禁用Windows Defender：

![图片.png](https://image.3001.net/images/20191111/1573458898_5dc913d277b4f.png!small)

并调用Powershell禁用Windows Defender相关功能：

![图片.png](https://image.3001.net/images/20191111/1573458906_5dc913da92e72.png!small)

将自身进程设置为系统严重状态，防止进程被结束：

![图片.png](https://image.3001.net/images/20191111/1573458912_5dc913e08d5b5.png!small)

给自身添加ACL，防止文件被访问：

![图片.png](https://image.3001.net/images/20191111/1573458918_5dc913e66a6d1.png!small)

调用五个方法检测当前环境是否在虚拟机中。

1、 调用WMI查询本机BIOS中是否包含相关字符串：

![图片.png](https://image.3001.net/images/20191111/1573458923_5dc913ebd6810.png!small)

2、 检测调试器：

![图片.png](https://image.3001.net/images/20191111/1573458928_5dc913f0cfe7d.png!small)

3、 检查是否含有SbieDll.dll，来判断当前是否在沙箱中运行：

![图片.png](https://image.3001.net/images/20191111/1573458932_5dc913f4831d8.png!small)

4、 判断磁盘大小：

![图片.png](https://image.3001.net/images/20191111/1573458939_5dc913fb2fd99.png!small)

5、 检测系统名中是否包含“xp”：

![图片.png](https://image.3001.net/images/20191111/1573458944_5dc91400344a2.png!small)

判断当前执行路径是否在启动目录下，如果不是则将自身拷贝到启动目录下，文件名则随机从列表中选择。删除卷影：

![图片.png](https://image.3001.net/images/20191111/1573458949_5dc914053fc62.png!small)

列表如下：

![图片.png](https://image.3001.net/images/20191111/1573458953_5dc9140960f9e.png!small)

并从Github上下载SharpExec：

![图片.png](https://image.3001.net/images/20191111/1573458958_5dc9140ebef5b.png!small)

用于横向移动：

![图片.png](https://image.3001.net/images/20191111/1573458963_5dc91413782ec.png!small)

结束相关进程：

![图片.png](https://image.3001.net/images/20191111/1573458969_5dc9141905fdf.png!small)

通过RNGCryptoServiceProvider类生成强随机数，并进行base64加密：

![图片.png](https://image.3001.net/images/20191111/1573458973_5dc9141d71353.png!small)

通过PBKDF2算法生成AES的key：

![图片.png](https://image.3001.net/images/20191111/1573458977_5dc9142170285.png!small)

PBKDF2算法的key：

![图片.png](https://image.3001.net/images/20191111/1573458982_5dc91426a2999.png!small)

Salt如下：

![图片.png](https://image.3001.net/images/20191111/1573458988_5dc9142c0***6.png!small)

通过AES算法对之前生成的base64值进行加密：

![图片.png](https://image.3001.net/images/20191111/1573458993_5dc91431bea90.png!small)

并生成用户ID，用户ID结构如下：

（加密base64的AES_IV的长度+加密base64的AES_IV+AES加密后的base64的值）

对其计算base64，结果即为用户ID。

之后开始遍历磁盘：

![图片.png](https://image.3001.net/images/20191111/1573458998_5dc91436bf36b.png!small)

加密如下后缀的文件：

![图片.png](https://image.3001.net/images/20191111/1573459003_5dc9143b6e478.png!small)

加密后的文件后缀为.crypted。

将之前生成的base64作为PBKDF2算法的Key。

salt如下：

![图片.png](https://image.3001.net/images/20191111/1573459014_5dc91446a59b3.png!small)

AES的key和IV均是通过PBKDF2算法生成。

对文件进行加密：

![图片.png](https://image.3001.net/images/20191111/1573459018_5dc9144a9ac1d.png!small)

拼接用户ID，生成勒索信：

![图片.png](https://image.3001.net/images/20191111/1573459022_5dc9144e5fbc2.png!small)

并将本机IP、加密时间、加密文件数、用户ID，发送到远程FTP服务器：

![图片.png](https://image.3001.net/images/20191111/1573459027_5dc91453236f8.png!small)

从远程服务器下载JPG文件作为桌面背景：

![图片.png](https://image.3001.net/images/20191111/1573459031_5dc914572d3bf.png!small)

并调用notepad打开勒索信：

![图片.png](https://image.3001.net/images/20191111/1573459035_5dc9145b9c769.png!small)![图片.png](https://image.3001.net/images/20191111/1573459041_5dc914619380e.png!small)

最后自删除：

![图片.png](https://image.3001.net/images/20191111/1573459046_5dc91466e853e.png!small)

# **解密** **思路** ****

 **该勒索可以** **被解密** **，** **目前** **奇** **安信** **已经** **公布解密工具，为了** **给**
**社区做** **更多** **贡献** **，** **我们** **公布** **了相关解密思路** ：

解密文件需要获得AES的key和IV，由于AES的key和IV是通过PBKDF2算法生成的，PBKDF2的salt已知，而PBKDF2得key则是之前通过强随机数生成经过base64编码后的值，该值被另一套AES加密存到用户ID中了，而AES的key还是通过PBKDF2算法生成的，PBKDF2的key是硬编码在程序中的，salt是已知的，所以我们可以得到AES的key，而AES的IV并不是通过PBKDF2生成的，而是RijndaelManaged类默认生成的。但是IV被保存在了用户ID中，所以用户只要能够提供勒索信和加密后的文件就可以解密。

#  **解密操作** **流程** ****

解密器下载地址：<https://github.com/RedDrip7/Hakbit_decryptor>

将被加密的文件放置到同一个目录下，下载我们提供的解密工具：

![图片.png](https://image.3001.net/images/20191111/1573459056_5dc91470adb29.png!small)

打开命令行，输入：

Decode.exe <勒索信的全路径> <要解密的目录>

![图片.png](https://image.3001.net/images/20191111/1573459061_5dc9147503bfa.png!small)

解密前文件数据：

![图片.png](https://image.3001.net/images/20191111/1573459065_5dc9147910ea1.png!small)

解密后文件数据：

![图片.png](https://image.3001.net/images/20191111/1573459070_5dc9147e1ceea.png!small)

**随后奇安信会推出官方整合版解密器，支持解密近百种勒索家族，敬请期待** **。** ****

目前奇安信集团全线产品，包括天擎、天眼、SOC、态势感知、威胁情报平台，支持对涉及该报告相关的攻击活动检测。

  

  

  

#  **IOC** ****

文件MD5：

791f2cb92301fd5709e0bfee741cf6d1

Host：

hakbit.000webhostapp.com

213.190.6.99

hakbit.hostingerapp.com

勒索比特币钱包地址：12grtxACJZkgT2nGAvMesgoM4ADHJ6NTaW

联系邮箱：hakbit@protonmail.com

