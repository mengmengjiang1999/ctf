![](https://image.3001.net/images/20200518/1589780782_5ec2212e9d131.jpg!small)**HiveJack是一款专用于内部渗透测试过程中的Windows凭证导出工具，在该工具的帮助下，广大安全研究人员不仅可以轻松地从一台已成功入侵的设备中获取到SYSTEM、SECURITY和SAM注册表内容，而且还可以在导出这些Windows凭证之后删除目标文件并清理入侵痕迹。**

一般来说，这种操作属于一种重复性的过程，一旦攻击者获取到目标主机的系统级访问权限之后，下一个步骤就是导出关键的注册表键值。在进行内部渗透测试的过程中，时间往往是非常宝贵的。那么在你导出和删除目标文件时，HiveJack将为你节省下来大量的时间，而且HiveJack还将帮助你自动化完成这些操作。

![](https://image.3001.net/images/20200518/1589780788_5ec22134a8cce.png!small)

导出目标主机中`C:\temp\`目录中的文件内容：

![](https://image.3001.net/images/20200518/1589780795_5ec2213b048c3.png!small)
点击“Delete Hives”按钮后，文件将会从受感染主机中成功删除:

![](https://image.3001.net/images/20200518/1589780800_5ec221409ae23.png!small)
一个Hive时注册表中键、子键、和值的逻辑组合，当目标操作系统启动或用户进行登录操作时，便会将相关一系列支持文件加载进内存中。

注册表文件一般拥有以下两种格式：

> １、标准格式：支持从Windows 2000到当前最新版本的Windows系统，并且拥有向下兼容性。
>
> ２、最新格式：支持从Windows XP开始的Windows系统。

除了`HKEY_CURRENT_USER`、`HKEY_LOCAL_MACHINE\SAM`、`HKEY_LOCAL_MACHINE\Security`以及`HKEY_USERS.DEFAULT`之外，其他所有的Hive使用的都是最新格式。

在一次内部渗透测试过程中，攻击者通常需要通过横向渗透活动来从一台主机转移到另一台主机中，此时通常就需要用到账号凭证了。在HiveJack的帮助下，攻击者将能够通过系统Hive来收集并导出凭证信息。

一般来说，当攻击者成功从目标主机中收集到本地管理员或系统权限之后，那么HiveJack就可以发挥作用了，而导出目标系统Hive也就意味着攻击者将能够获取到系统用户的密码哈希。

在使用该工具的同时，你还可以使用类似[secretsdump](https://github.com/SecureAuthCorp/impacket/blob/master/examples/secretsdump.py)之类的工具来进行导出辅助：

![](https://image.3001.net/images/20200518/1589780825_5ec2215935ea8.png!small)
获取到密码哈希之后，攻击者将能够进行各种其他的攻击行为，比如说通过密码破解或密码传递来在目标网络系统中实现横向渗透。

当Hive成功拷贝到攻击者的设备上之后，该工具还能够并帮助我们从temp文件中删除文件以防止敏感文件泄露，并清除攻击痕迹。

### 注意事项

一般来说，我们都会检查`C:\Windows\repair\`路径来获取SAM和SYSTEM文件以避免被EDR解决方案所检测到。但是，这个目录中包含了原始`C:\Windows\System32\config\`文件的已过期副本，因此它可能无法正确映射出当前用户的账号凭证。不过，通过它们来破解密码或已知的密码格式，仍然是非常有用的。

## 源码获取

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Viralmaniar/HiveJack.git  
    

## 工具使用

方法一：从该项目GitHub库的[Release页面](https://github.com/Viralmaniar/HiveJack/releases/download/v1.0/HiveJack.exe)直接下载[HiveJack.exe](https://github.com/Viralmaniar/HiveJack/releases/download/v1.0/HiveJack.exe)，然后在目标主机中直接运行，获取到的Hive内容将存储在目标主机的`c:\temp\`目录下。

方法二：使用Visual Studio打开项目源码，并根据情况构建源码。

注意：在导出注册表Hive之前，请确保目标主机的“`C:`”驱动器下存在`temp`目录。

## 项目地址

HiveJack：【[GitHub传送门](https://github.com/Viralmaniar/HiveJack)】

***参考来源：[Viralmaniar](https://github.com/Viralmaniar/HiveJack)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

