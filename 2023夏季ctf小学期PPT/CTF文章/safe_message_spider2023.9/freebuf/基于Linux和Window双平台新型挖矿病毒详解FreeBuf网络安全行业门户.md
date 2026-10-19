这是一款近期非常流行的挖矿病毒，基于Linux和Windows双平台，主体程序都是使用GO语言进行编写的，并通过多个漏洞进行传播，估计国内已经有不少服务器被感染,笔者最近一段时间发现它更新了，并捕获到它的最新的脚本,通过分析，下载服务器URL地址为：

https://us.gsearch.com.de/api/sysupdate

http://209.182.218.161:80/363A3EDC10A2930D/sysupdate

https://us.gsearch.com.de/api/update.sh

http://209.182.218.161:80/363A3EDC10A2930D/update.sh

https://us.gsearch.com.de/api/config.json

http://209.182.218.161:80/363A3EDC10A2930D/config.json

https://us.gsearch.com.de/api/networkservice

http://209.182.218.161:80/363A3EDC10A2930D/networkservice

https://us.gsearch.com.de/api/sysguard

http://209.182.218.161:80/363A3EDC10A2930D/sysguard

相应的配置文件挖矿地址和钱包地址，如下所示：

cryptonightr.usa.nicehash.com:3375

1NYTak57oEYJwzTrG9wwAtM9Q44DwMBFLq.usa

cryptonightr.eu.nicehash.com:3375

1NYTak57oEYJwzTrG9wwAtM9Q44DwMBFLq.eu

cryptonightr.jp.nicehash.com:3375

1NYTak57oEYJwzTrG9wwAtM9Q44DwMBFLq.jp

cryptonightr.hk.nicehash.com:3375

1NYTak57oEYJwzTrG9wwAtM9Q44DwMBFLq.hk

cryptonightr.br.nicehash.com:3375

1NYTak57oEYJwzTrG9wwAtM9Q44DwMBFLq.br

cryptonightr.in.nicehash.com:3375

1NYTak57oEYJwzTrG9wwAtM9Q44DwMBFLq.in

xmr.f2pool.com:13531

43zqYTWj1JG1H1idZFQWwJZLTos3hbJ5iR3tJpEtwEi43UBbzPeaQxCRysdjYTtdc8aHao7csiWa5BTP9PfNYzyfSbbrwoR.nice

脚本的功能主要是结束其它挖矿程序，然后从服务器上下载三个主要的程序:sysupdate、networkservice、sysguard，分别对这三个Linux下64位主程序进行详细分析，

# sysupdate详细分析

sysupdate是门罗币挖矿程序，如下所示：

![图片1.png](https://image.3001.net/images/20190603/1559533747_5cf498b323ea4.png!small)版本号为：2.15.1-beta，如下所示：  

![图片2.png](https://image.3001.net/images/20190603/1559533761_5cf498c175d3f.png!small)加载config.json配置程序矿池和钱包地址等，如下所示：  

![图片3.png](https://image.3001.net/images/20190603/1559533771_5cf498cb6c9ef.png!small)开始挖矿，如下所示：  

![图片4.png](https://image.3001.net/images/20190603/1559533784_5cf498d87281c.png!small)config.json配置文件信息，如下所示：  

![图片5.png](https://image.3001.net/images/20190603/1559533795_5cf498e35fbd9.png!small)  

矿池地址：xmr.f2pool.com:13531

钱包地址：

84wSxADJuSCEPGu7FyRPa2UAgs2YkTad1izUTLWJNmyvNFLU9PpTnwYUCn66cSK5v6cfRAvDdxMzpPdirw6njjt5AcRwReU.xmrxmr2019

运行截图如下所示：

![图片6.png](https://image.3001.net/images/20190603/1559533806_5cf498eecc264.png!small)捕获到了网络流量包，如下所示：  

![图片7.png](https://image.3001.net/images/20190603/1559533817_5cf498f981b96.png!small)  

# networkservice详细分析

networkservice漏洞扫描传播程序，如下所示：

1.初始化扫描IP地址段，如下所示：

![图片8.png](https://image.3001.net/images/20190603/1559533828_5cf499047b04c.png!small)从远程服务器下载相应的IP段数据，服务器地址：https://23.175.0.142/api/download/I9RRye，下载回来的IP地址段是数字整型，文件名为ips_cn.txt，如下所示：  

![图片9.png](https://image.3001.net/images/20190603/1559533840_5cf4991013ff3.png!small)  

数字转化为IP地址，如下所示：

16909568 16909823 --> 1.2.5.0 1.2.5.255

737878016 737879039 --> 43.251.32.0 43.251.35.255

1733261312 1733262335 --> 103.79.120.0 103.79.123.255

2525131776 2525132799 --> 150.130.116.0 150.130.119.255

3670879488 3670879999 --> 218.205.45.0 218.205.46.255

2.从内存中解密出相应的PowerShell脚本，如下所示：

![图片10.png](https://image.3001.net/images/20190603/1559533854_5cf4991e8a0ec.png!small)解密出来的PowerShell脚本地址http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/init.ps1，如下所示：  

![图片11.png](https://image.3001.net/images/20190603/1559533864_5cf49928abcf2.png!small)可以在windows执行相应的传播、挖矿程序，如下所示：  

![图片12.png](https://image.3001.net/images/20190603/1559533876_5cf4993426446.png!small)3.创建计划任务，进行更新操作，如下所示：  

![图片13.png](https://image.3001.net/images/20190603/1559533888_5cf4994034976.png!small)4.更新执行挖矿程序，如下所示：  

![图片14.png](https://image.3001.net/images/20190603/1559533899_5cf4994b80c71.png!small)5.执行扫描、传播程序，如下所示：  

![图片15.png](https://image.3001.net/images/20190603/1559533910_5cf4995645c9e.png!small)6.同时还可以下载自清除脚本进行自清除操作，如下所示：  

![图片16.png](https://image.3001.net/images/20190603/1559533921_5cf4996123e52.png!small)7.执行各种扫描主机操作，如下所示：  

![图片17.png](https://image.3001.net/images/20190603/1559533931_5cf4996b70da6.png!small)8.redis未授权访问漏洞扫描，如下所示：  

![图片18.png](https://image.3001.net/images/20190603/1559533945_5cf499799b7eb.png!small)9.Drupal框架CVE-2018-7600漏洞扫描，如下所示：  

![图片19.png](https://image.3001.net/images/20190603/1559533957_5cf49985a6599.png!small)10.Hadoop未授权漏洞扫描，如下所示：  

![图片20.png](https://image.3001.net/images/20190603/1559533968_5cf499902362b.png!small)11.Spring框架CVE-2018-1273漏洞扫描，如下所示：  

![图片21.png](https://image.3001.net/images/20190603/1559533979_5cf4999bea867.png!small)12.thinkphp框架TP5高危漏洞扫描，如下所示：  

![图片22.png](https://image.3001.net/images/20190603/1559533990_5cf499a67075b.png!small)13.WebLogic框架CVE-2017-10271漏洞扫描，如下所示：  

![图片23.png](https://image.3001.net/images/20190603/1559534001_5cf499b1247cd.png!small)14.SQLServer框架xcmd_shell、SP_OACreate注入提权漏洞扫描，如下所示：  

![图片24.png](https://image.3001.net/images/20190603/1559534012_5cf499bc8e29c.png!small)15.Elasticsearch框架CVE-2015-1427、CVE-2014-3120远程代码执行漏洞扫描，如下所示：  

![图片25.png](https://image.3001.net/images/20190603/1559534024_5cf499c871a2c.png!small)  

# sysguard详细分析

sysguard根据操作系统的版本下载执行不同的payload代码，如下所示：

1.内存解密出PowerShell脚本，如下所示：

![图片26.png](https://image.3001.net/images/20190603/1559534035_5cf499d396fea.png!small)然后拼接PowerShell脚本，如下所示：  

![图片27.png](https://image.3001.net/images/20190603/1559534045_5cf499ddb025c.png!small)2.将上面的PowerShell脚本进行Base64编码，如下所示：  

![图片28.png](https://image.3001.net/images/20190603/1559534057_5cf499e9a76fb.png!small)判断是否为windows平台，如果为windows平台执行上面的PowerShell脚本，如下所示：  

![图片29.png](https://image.3001.net/images/20190603/1559534069_5cf499f5161d1.png!small)调用执行PowerShell脚本，如下所示：  

![图片30.png](https://image.3001.net/images/20190603/1559534080_5cf49a00d24de.png!small)3.如果为Linux平台，获取主机root权限:  

![图片31.png](https://image.3001.net/images/20190603/1559534096_5cf49a1020749.png!small)4.然后通过判断不同的操作系统版本，与远程服务器CC通信执行下载Payload、扫描、持久化驻留主机、更新等操作，如下所示：  

![图片32.png](https://image.3001.net/images/20190603/1559534108_5cf49a1c107a2.png!small)5.判断不同的操作系统，执行不同的扫描程序，如下所示：  

![图片33.png](https://image.3001.net/images/20190603/1559534118_5cf49a26bde46.png!small)在windows操作系统下，启动扫描程序networkservice，如下所示：  

![图片34.png](https://image.3001.net/images/20190603/1559534129_5cf49a310aa74.png!small)并把相应的payload命令写入到%temp%目录下的随机文件名的BAT脚本中，如下所示：  

![图片35.png](https://image.3001.net/images/20190603/1559534142_5cf49a3e0aac2.png!small)启动扫描程序，如下所示：  

![图片36.png](https://image.3001.net/images/20190603/1559534152_5cf49a484d334.png!small)捕获到相应的流量包，如下所示：  

![图片37.png](https://image.3001.net/images/20190603/1559534163_5cf49a5340c41.png!small)6\.
不同的操作系统执行不同的持久化操作，如下所示：  

![图片38.png](https://image.3001.net/images/20190603/1559534176_5cf49a60c3a6c.png!small)在windows操作系统下，创建相应的计划任务，如下所示：  

![图片39.png](https://image.3001.net/images/20190603/1559534192_5cf49a7062c60.png!small)创建的计划任务，如下所示：  

![图片40.png](https://image.3001.net/images/20190603/1559534204_5cf49a7cf1743.png!small)在Linux操作系统下，创建相应的crontab自启动，如下所示：  

![图片41.png](https://image.3001.net/images/20190603/1559534216_5cf49a8878c9f.png!small)7.检测各个文件，进行更新操作，如下所示：  

![图片42.png](https://image.3001.net/images/20190603/1559534228_5cf49a94055e0.png!small)执行更新Payload，调用任务计划中的PowerShell脚本执行更新，如下所示：  

![图片43.png](https://image.3001.net/images/20190603/1559534242_5cf49aa2da19f.png!small)8.与远程服务器进行通信，如下所示：  

![图片44.png](https://image.3001.net/images/20190603/1559534255_5cf49aaf759b1.png!small)  

获取的CC服务器URL，如下所示：

http:///6HqJB0SPQqbFbHJD/pi?module=account&action=txlist&address=0xb017eFb3339FfE0EB3dBF799Db6cb065376fFEda☆

tblock=0&endblock=99999999&sort=asc&apikey=ADQAMwAuADIANAA1AC4AMgAyADIALgA1ADcAOgA4ADYANgA3AC8ANgBIAHEASgBCADAAUwBQAFEAcQBiAEYAYgBIAEoARAAvAGkAbgBpAHQALgBwAHMAMQAnACkA

执行下载payload对应的PowerShell脚本，并写入到%temp%目录下，相应的PowerShell脚本，如下所示：

![图片45.png](https://image.3001.net/images/20190603/1559534268_5cf49abcd8004.png!small)执行完Payload，如下所示：  

![图片46.png](https://image.3001.net/images/20190603/1559534281_5cf49ac982199.png!small)  

  

 **IOC：**

 **漏洞:**

redis未授权访问漏洞

Drupal框架CVE-2018-7600

Hadoop未授权漏洞

Spring框架CVE-2018-1273

thinkphp框架TP5

WebLogic框架CVE-2017-10271

SQLServer框架xcmd_shell、SP_OACreate注入提权漏洞

Elasticsearch框架CVE-2015-1427、CVE-2014-3120

**URL：**

https://pixeldrain.com/api/file/3myaXqqZ

https://pixeldrain.com/api/file/kSGgh0Tr

https://pixeldrain.com/api/file/0x_WuGkM

http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/checkcc

http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/sysupdate

http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/sysupdate.exe

http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/update.sh

http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/init.ps1

http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/update.ps1

http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/config.json

https://pixeldrain.com/api/file/aQWIprw

http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/networkservice

http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/networkservice.exe

https://pixeldrain.com/api/file/o4m-DmH6

https://pixeldrain.com/api/file/XOFVsqam

http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/sysguard

http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/sysguard.exe

http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/clean.bat

**最新的URL ：**

https://us.gsearch.com.de/api/sysupdate

http://209.182.218.161:80/363A3EDC10A2930D/sysupdate

https://us.gsearch.com.de/api/update.sh

http://209.182.218.161:80/363A3EDC10A2930D/update.sh

https://us.gsearch.com.de/api/config.json

http://209.182.218.161:80/363A3EDC10A2930D/config.json

https://us.gsearch.com.de/api/networkservice

http://209.182.218.161:80/363A3EDC10A2930D/networkservice

https://us.gsearch.com.de/api/sysguard

http://209.182.218.161:80/363A3EDC10A2930D/sysguard

**MD5**

networkservice 64F11B25EBA509B5EF958B0BD70398D3

sysguard C562BE2E56509236AFA25782B690E67C

sysupdate FF879D31ED80841482C27C90E2BFE268

update.sh 7CE3D45CE6D2831677B8951E53390302

config.json AE99D9B5EBDD94065273AC65E04C47D2

networkservice.exe FE34EBFB84EC980D1804B8AAA821A174

init.sh 9A5F77A32D08A86CFA9E8F7EE34E3BB7

init.ps1 CFE95C12730AF42852E65F1FED84C229

sysguard.exe C9241734C152183FDCE72E1F58463220

sysupdate.exe 86705F59924D0160867FB139CD5B5507

clean.bat 44A51CAFE126EC5B2354AC14FD8FF71C

**最新的MD5**

networkservice 12E8EB24964F8938B6B896472DA24A64

sysguard D4E88D8BF676541BBBBC7CAE7523C0B3

sysupdate FF879D31ED80841482C27C90E2BFE268

  

