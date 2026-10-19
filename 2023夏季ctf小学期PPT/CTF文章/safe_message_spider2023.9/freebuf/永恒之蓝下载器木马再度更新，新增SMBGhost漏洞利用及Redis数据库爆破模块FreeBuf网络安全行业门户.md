2020年6月10日，奇安信威胁情报中心中心监测到永恒之蓝下载器木马再度更新，木马在原有SMBGhost漏洞监测模块的基础上，新增漏洞利用模块。此外还新增Redis数据库爆破模块。SMBGhost
(CVE-2020-0796)是SMB服务远程代码执行漏洞，攻击者可能利用此漏洞远程无需用户验证通过发送构造特殊的恶意数据导致在目标系统上执行恶意代码，从而获取机器的完全控制。2020年6月2日已有国外有安全人员发布可以导致利用此漏洞进行远程代码执行的POC，详情参考：  

[更新 |
远程命令执行POC被公开发布：微软SMBv3服务远程代码执行漏洞（CVE-2020-0796）通告](http://mp.weixin.qq.com/s?__biz=MzI2MDc2MDA4OA==&mid=2247491180&idx=1&sn=2c3d8429b3cbd863d292acde09fb5447&chksm=ea65e91bdd12600d27b7e352ee0402a92eaf701cea64b871b1e4e92e1cd0c7c462d8b9fe063f&scene=21#wechat_redirect)

更新的脚本从新URL
<http://t.amynx.com/smgh.jsp>下载，经过多层下载及解密后获得永恒之蓝下载器木马爆破及漏洞利用模块，新增的模块函数为smbghost_exec：

![图片.png](https://image.3001.net/images/20200612/1591926957_5ee2e0adb9fb8.png!small)![图片.png](https://image.3001.net/images/20200612/1591926963_5ee2e0b334b39.png!small)  

smgh.bin是漏洞利用代码，是python3编译的exe文件，解包后得到python脚本编写的漏洞利用程序,参考<https://www.exploit-db.com/exploits/48537>。

Redis爆破模块（redisexec）的功能为，扫描内外网中开启6379端口的IP并在其中没有密码的Linux计算机中写入计划任务执行挖矿命令。

![图片.png](https://image.3001.net/images/20200612/1591926978_5ee2e0c229afb.png!small)  

目前永恒之蓝下载器木马已集成多种漏洞利用及弱口令爆破模块并仍在持续更新：

 **漏洞扫描及利用**|  **弱口令爆破**  
---|---  
MS17-010漏洞利用| RDP爆破  
Lnk漏洞（CVE-2017-8464）利用| SMB爆破  
SMBGhost漏洞（CVE-2020-0796）利用| MSSQL爆破  
  
| SSH爆破  
  
| Redis爆破  
  
奇安信威胁情报中心在此提醒各位用户，对于重点服务器和主机，做好网络安全域划分并及时打漏洞补丁，防止利用此漏洞的横向攻击。开启Windows防火墙，尽量关闭3389、445、139、135等不用的高危端口。每台服务器设置唯一口令，且复杂度要求采用大小写字母、数字、特殊符号混合的组合结构，口令位数足够长（15位、两种组合以上）。

**IOC：**

99ecca08236f6cf766d7d8e2cc34eff6

5b3c44***3c7e592e416f68d3924620f

t.amynx.com

t.zer9g.com

t.zz3r0.com

d.ackng.com

<http://t.amynx.com/smgh.jsp>

<http://t.amynx.com/a.jsp>

<http://d.ackng.com/if.bin>

<http://d.ackng.com/smgh.bin>

**参考链接** ：

永恒之蓝木马下载器发起“黑球”行动，新增SMBGhost漏洞检测能力

<https://mp.weixin.qq.com/s/QEE95HTKzuT4-NykfvHfGQ>

