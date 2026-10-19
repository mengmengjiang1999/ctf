在企业的内网安全防御中，通常会将横向移动技术作为指标，进行有针对性的检测。尽管如此，还是有不少攻击者巧妙地避开了层层关卡，在Windows环境中横向移动。针对这些高级攻击者，该如何应对呢？在使用IPC,WMIC等进行横向移动时，如果使用RID非500的管理员用户，有时会拒绝访问，是什么原因？

 **本文由锦行科技的安全研究团队提供，站在攻击者的视角分析windows内的横向移动，帮助大家深入了解横向移动的全过程以应对该种攻击。**

  

##  **Kb2871997**

网传Kb2871997 是限制远程访问的主要原因，测试一下

  

###  **01** 工作组环境下

 **①** 主机B：win7 ，192.168.18.156 ，未打Kb2871997补丁

用户 win7 非500的主机B本地管理员账户

![1604901142_5fa8d916d657481649cf9.png!small?1604901142769](https://image.3001.net/images/20201109/1604901142_5fa8d916d657481649cf9.png!small?1604901142769)

  

 **使用Administrator访问**
，可![1604901153_5fa8d921ac416e5f3a70b.png!small?1604901154598](https://image.3001.net/images/20201109/1604901153_5fa8d921ac416e5f3a70b.png!small?1604901154598)

  

 **用户Win7访问** 。拒绝访问

![1604901515_5fa8da8b70f170e504003.png!small?1604901515724](https://image.3001.net/images/20201109/1604901515_5fa8da8b70f170e504003.png!small?1604901515724)

  

 **②** 主机B安装Kb2871997补丁

![1604901230_5fa8d96e0a8c7b4ef1ab1.png!small?1604901229922](https://image.3001.net/images/20201109/1604901230_5fa8d96e0a8c7b4ef1ab1.png!small?1604901229922)

  

 **Administrator访问**
，可![1604901531_5fa8da9bb32d33e84d62e.png!small?1604901532343](https://image.3001.net/images/20201109/1604901531_5fa8da9bb32d33e84d62e.png!small?1604901532343)

  

 **用户Win 7访问** ，拒绝访问

![1604901266_5fa8d9921b259804ca245.png!small?1604901266471](https://image.3001.net/images/20201109/1604901266_5fa8d9921b259804ca245.png!small?1604901266471)

  

###  **02** 域环境

主机B 192.168.18.156 安装了Kb2871997补丁

用户test\User为主机B本地管理员的普通域用户

  

用户test\User访问，可![1604901581_5fa8dacd8f629406be301.png!small?1604901582346](https://image.3001.net/images/20201109/1604901581_5fa8dacd8f629406be301.png!small?1604901582346)

  

由安装KB2871997前后的对比发现
**kb2871997对于本地Administrator(rid为500，操作系统只认rid不认用户名)和本地管理员组的域用户是没有影响的。**
但是kb2871997补丁会删除除了wdigest ssp以外其他ssp的明文凭据

  

  

##  **remote UAC 远程限制**

  

###  **01** 工作组环境下

主机A win10

主机B win10 192.168.18.132

用户user为Rid非500的主机B本地管理员账户

  

ipc 拒绝访问

![1604901347_5fa8d9e3e6a6998fe9513.png!small?1604901347951](https://image.3001.net/images/20201109/1604901347_5fa8d9e3e6a6998fe9513.png!small?1604901347951)

  

Schtasks
拒绝访问![1604901357_5fa8d9ed51f7bbad6e46d.png!small?1604901357225](https://image.3001.net/images/20201109/1604901357_5fa8d9ed51f7bbad6e46d.png!small?1604901357225)

  

WMIC,PSEXEC,WINRM,等也是拒绝访问

  

 **原因：**

由于remote UAC默认开启的，计算机的任何非 500本地管理员帐户，
用户在远程计算机上没有特权提升能力，并且用户无法执行管理任务。使用非500用户来远程访问皆为：拒绝访问

  

 **解决：**

在注册表HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsCurrentVersionPoliciesSystem中添加一个键值LocalAccountTokenFilterPolicy。LocalAccountTokenFilterPolicy默认不存在，即为0（开启远程限制），添加并设置为1时将关闭远程限制

  

reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\system /v
LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f

![1604901381_5fa8da053e8e6479a5311.png!small?1604901385075](https://image.3001.net/images/20201109/1604901381_5fa8da053e8e6479a5311.png!small?1604901385075)

  

再次访问,可

![1604901400_5fa8da18680f819878ac0.png!small?1604901402194](https://image.3001.net/images/20201109/1604901400_5fa8da18680f819878ac0.png!small?1604901402194)

schtasks ，可

![1604901414_5fa8da26c96d8aaa73348.png!small?1604901414697](https://image.3001.net/images/20201109/1604901414_5fa8da26c96d8aaa73348.png!small?1604901414697)

若要限制500用户administrator的远程登录，那就是直接把FilterAdministratorToken设置为1，路径为：  
HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsCurrentVersionPoliciesSystem

  

reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v
FilterAdministratorToken /t REG_DWORD /d 1 /f

![1604901442_5fa8da428828b5b09fdb1.png!small?1604901445516](https://image.3001.net/images/20201109/1604901442_5fa8da428828b5b09fdb1.png!small?1604901445516)

  

再用Administrator连接就拒绝访问了

![1604901676_5fa8db2cf29717867d28a.png!small?1604901677303](https://image.3001.net/images/20201109/1604901676_5fa8db2cf29717867d28a.png!small?1604901677303)

  

 **在域环境中，本地管理员用户的域账户不受LocalAccountTokenFilterPolicy限制**

  

###  **02** 域环境

主机A winsrv2012  
主机B win10 192.168.18.149  
用户test\admin为非rid500的主机B 本地管理员的普通域用户  
用户test\uuser 为普通域用户

  

test\admin访问，可

![1604901468_5fa8da5c49219dcf8b3a7.png!small?1604901470732](https://image.3001.net/images/20201109/1604901468_5fa8da5c49219dcf8b3a7.png!small?1604901470732)

  

但非本地管理员的普通域用户还是会受LocalAccountTokenFilterPolicy限制

  

普通域用户test\uuser访问，拒绝访问

![1604901477_5fa8da6568f87c4adda8d.png!small?1604901477635](https://image.3001.net/images/20201109/1604901477_5fa8da6568f87c4adda8d.png!small?1604901477635)

域管理员用户则不受限制

 **由此可见remote UAC才是限制远程访问的主要原因**

