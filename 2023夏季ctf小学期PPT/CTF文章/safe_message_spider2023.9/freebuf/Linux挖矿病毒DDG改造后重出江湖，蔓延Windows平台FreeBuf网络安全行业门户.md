## 0x0 背景概述

**近日，深信服安全团队捕获一枚Linux、windows双平台的挖矿病毒样本，通过安全人员分析确认，该木马是通过redis漏洞传播的挖矿木马DDG的最新变种，使用当前最新的go语言1.10编译使用了大量的基础库文件，该木马会大量消耗服务器资源，难以清除并具有内网扩散功能。**

DDG挖矿病毒是一款在Linux系统下运行的恶意挖矿病毒，该病毒从去年一直活跃在现在，已经挖取了价值一千多万人民币的虚拟币货币，此病毒样本在一年左右的时间，已开发出了DDG.3012/DDG3013/DDG3020多个变种版本。

主要功能如下：

**文件名** | **作用**  
---|---  
networkservice | 横向移动模块，包含mssql redis thinkphp weblogic等漏洞探测模块  
sysguard | 根据获取到的系统版本下载针对性Payload执行、CC通信模块  
sysupdate | Xmrige开源挖矿程序主体  
Update.sh | 下载其他病毒模块、清除其他挖矿进程、定时任务存活  
Config.json | 挖矿配置文件，包含钱包地址与挖矿参数  
  
## 0x1 现象描述

根据安全感知SIP报警提示，某主机会每隔3个小时从互联网去下载一个update.sh的恶意脚本连接地址为：

43.245.222.57:8667/6Hxxxxxx/update.sh

![](https://image.3001.net/images/20190411/1554954429_5caeb8bdeae38.png!small)

同时对外网发起redis的扫描：

![](https://image.3001.net/images/20190411/1554954435_5caeb8c3358bd.png!small)

通过威胁情报关联发现，当前还未收录该URL的相关情报，查询提示非恶意：

![](https://image.3001.net/images/20190411/1554954439_5caeb8c75b133.png!small)

最新的日期为4月8日：

![](https://image.3001.net/images/20190411/1554954449_5caeb8d133d1d.png!small)

## 0x2 主机排查

安全人员通过对主机进行排查发现，当前的挖矿进程当前的CPU已经达到了399%左右，并且该进程名与PID都会间隔一定的时间变换：

![](https://image.3001.net/images/20190411/1554954457_5caeb8d990ae7.png!small)

程序的主要目录在tmp下面：

![](https://image.3001.net/images/20190411/1554954467_5caeb8e360e08.png!small)

在tmp目录下发现病毒主体的样本创建用户为nobody：

![](https://image.3001.net/images/20190411/1554954476_5caeb8eca93be.png!small)

同时使用定时任务做长期的存活，每间隔30分钟执行一次：

![](https://image.3001.net/images/20190411/1554954483_5caeb8f3e6a43.png!small)

Update.sh脚本主要实现的功能比较多，足足有15KB那么大，主要包含的功能如下：

> 1\. 病毒主体的恶意文件下载
>
> 2\. Kill其他的其他挖矿进程
>
> 3\. 写入authorized_keys实现root的免密码登录
>
> 4\. 创建定时任务
>
> 5\. 添加iptables策略、清除系统日志等操作

![](https://image.3001.net/images/20190411/1554954493_5caeb8fd492ee.png!small)

写入authorized_keys实现root的免密码登录截图如下：

![](https://image.3001.net/images/20190411/1554954497_5caeb9014af02.png!small)

## 0x3 病毒样本分析

### Sysupdate模块

该程序由go语言编写，由于没有符号文件，所以函数全都是匿名的。Go语言的编译器不同版本有很大区别，因此在分析过程中需要先识别一下版本信息，该木马的编译器版本为1.10：

![](https://image.3001.net/images/20190411/1554954504_5caeb90844961.png!small)

从函数的名字可以看出，该组件主要作用是用来内网扫描，横向移动。继续跟进相关函数，寻找具体功能；该程序导入了多个模块，对内网中不同服务进行攻击包含mssql
redis thinkphp weblogic等漏洞：

![](https://image.3001.net/images/20190411/1554954507_5caeb90b1d1c8.png!small)

![](https://image.3001.net/images/20190411/1554954513_5caeb91162232.png!small)

### Sysguard模块

这个组件主要工作是开启dog的一些方法，继续跟踪发现内部会有一些不同平台的识别，配合组件二的扫描结果，下载攻击载荷payload，执行相应的os系统命令完成攻击任务。所以判断该挖矿程序是可以在win和linux下均可运行的：

![](https://image.3001.net/images/20190411/1554954518_5caeb91609981.png!small)

通过cc服务器实现的一系列方法，选中的函数的功能是获取windows的powershell：

![](https://image.3001.net/images/20190411/1554954521_5caeb9199c2fc.png!small)

### Sysupdate模块

该组件正是挖矿组件的挖矿部分使用开源的xmrig：

![](https://image.3001.net/images/20190411/1554954526_5caeb91e2f38b.png!small)

## 0x4 加固建议

1\. 清理系统内全部用户的相关的恶意定时任务；

2\. 删除tmp目录下的恶意病毒文件；

3\. 修复相关的漏洞、使用强密码、对redismssql等系统设置访问控制权限；

4\. 建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。

## IOC

### URL：

[](https://pixeldrain.com/api/file/3myaXqqZ)

    
    
    <https://pixeldrain.com/api/file/3myaXqqZ>
    
    <http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/sysupdate>
    
    <http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/update.sh>
    
    <http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/config.json>
    
    <https://pixeldrain.com/api/file/aQWIprw>
    
    <http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/networkservice>
    
    <https://pixeldrain.com/api/file/o4m-DmH6>
    
    <http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/sysguard>

[](http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/sysguard)

### MD5：

    
    
    networkservice 64F11B25EBA509B5EF958B0BD70398D3
    
    sysguard C562BE2E56509236AFA25782B690E67C
    
    sysupdate FF879D31ED80841482C27C90E2BFE268
    
    Update.sh 7CE3D45CE6D2831677B8951E53390302

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

