## 关于Invoke-EDRChecker

Invoke-EDRChecker是一款功能强大的主机安全产品检测工具，该工具能够对正在运行的进程进行详细的安全检查，包括进程进程元数据、加载到当前进程中的DLL以及每个DLL元数据、常见安装目录、已安装服务、注册表和正在运行的驱动器。检测完成之后，该工具将能够基于检测结果以查看目标主机中是否存在已知的安全防御产品，比如说反病毒软件、EDR或日志记录工具等等。

![](https://image.3001.net/images/20220226/1645806245_621902a5b22ccdcc2eb17.png!small)

本质上来说，Invoke-EDRChecker是一个脚本，它可以直接加载到C2服务器中。比如说，我们可以在PoshC2中，将脚本放入模块目录，加载模块，然后运行它。注意：这个脚本现在已经包含在了PoshC2中，所以我们不需要手动添加它。

除此之外，该脚本还能够对远程目标设备执行检查，不过前提是我们有这样做的权限，而这些检查目前仅限于检查进程、常见的安装目录和已安装的服务。

如果时间允许的话，我们还将继续添加和改进脚本支持的检查对象。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/PwnDexter/Invoke-EDRChecker.git

## 工具使用

将脚本加载到我们选择的目标主机或C2之后，就可以运行下列命令了：

    
    
    Invoke-EDRChecker

针对本地主机运行脚本，并基于当前用户完整性执行检查：

    
    
    Invoke-EDRChecker -Force

在远程主机上运行脚本，测试连接，并在运行之前尝试解析主机名：

    
    
    Invoke-EDRChecker -Remote <hostname>

我们还可以使用“-Ignore”选项来绕过远程主机的连接性检查：

    
    
    Invoke-EDRChecker -Remote <hostname> -Ignore

## 工具输出样例

请注意：下面给出的截图是在Windows 10平台上测试的。

 **如果进程和驱动器是隐藏的话，Invoke-EDRChecker仍然可以找到它们：**

![](https://image.3001.net/images/20220226/1645806299_621902db9ae41be36b141.png!small)

![](https://image.3001.net/images/20220226/1645806310_621902e63d8c828442851.png!small)

 **以非管理员权限运行脚本以显示可视化差异：**

![](https://image.3001.net/images/20220226/1645806323_621902f3abf6e14abd62f.png!small)

![](https://image.3001.net/images/20220226/1645806330_621902fa219ee3d98e2f8.png!small)

![](https://image.3001.net/images/20220226/1645806336_6219030016942a0e4c297.png!small)![](https://image.3001.net/images/20220226/1645806342_62190306dd17070bfee84.png!small)

![](https://image.3001.net/images/20220226/1645806350_6219030e0b29ee4aae756.png!small)

![](https://image.3001.net/images/20220226/1645806359_621903177c5b7c06f0174.png!small)

 **结合PoshC2一起使用Invoke-EDRChecker：**

![](https://image.3001.net/images/20220226/1645806386_6219033245c4f12963ed3.png!small)

  

## 项目地址

Invoke-EDRChecker：【[ _GitHub传送门_](https://github.com/PwnDexter/Invoke-EDRChecker)】

