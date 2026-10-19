*** 本文作者：0zapt4toM，本文属FreeBuf原创奖励计划，未经许可禁止转载**

**闲来无事，分析一个Rootkit(MD5:973fe1392e8145daf907fad7b4fbacdc)病毒驱动，样本来源于52pojie论坛。分析此样本的目的在于增加自己的逆向分析能力和加深对windows内核的认识。（可能有分析的不对的地方，请大家指正）**  

## 病毒整体逻辑

整体的病毒逻辑如下图所示。

![main_mal_logic.png](https://image.3001.net/images/20180414/15237020337116.png!small)  

> 1，创建病毒设备对象\\\Device\\\93218ec2da92e0af。
>
> 2，hook多处系统函数。
>
> 3，下载并执行盗号木马。
>
> 4，初始化锁首所需的html文件。
>
> 5，解密锁首所需的网址。
>
> 6，创建映像加载回调。
>
> 7，执行主要的锁首逻辑。
>
> 8，注册mimifilter。
>
> 9，创建一个线程，检查更新以及以上逻辑是否都正确执行。

下面详细介绍每一个病毒逻辑。

### 创建驱动对象

创建设备名为\\\Device\\\93218ec2da92e0af的设备，并且注册了关机回调。  

![create_drive.png](https://image.3001.net/images/20180414/15236882637491.png!small)  

### HOOK系统函数

![hook_sysapi.png](https://image.3001.net/images/20180414/15236833908216.png!small)  

使用同样的方法hook了ntdll的ZwCreateThreadEx,NtCreateThreadEx,ZwProtectVirtualMemory,NtProtectVirtualMemory,ZwReadVirtualMemory,NtReadVirtualMemory,ZwWriteVirtualMemory,NtWriteVirtualMemory以及kernel32的WinExec和ZwClose多处API。

### 下载执行盗号木马

该病毒会下载执行盗号病毒(MD5:0769a5098f7e95e1d9bd4bd0acce8eae)，该病毒主要用与收集windows登陆凭证的hash，以及各种服务器的账号密码。

a,收集NTLM哈希。

![image.png](https://image.3001.net/images/20180414/15236882893617.png!small)  

b，收集各种账号密码

![image.png](https://image.3001.net/images/20180414/15236843548475.png!small)  

这个样本在vt的检出率为55.2%。

![vt.png](https://image.3001.net/images/20180414/1523702627590.png!small)  

### 解密锁首需要的网址

解密逻辑分为两步，第一步调用decode_funA()解密key,然后使用key解密内存中被加密的url得到明文url,并将全局变量lockpage_flag设置为1。  

![decode_url.png](https://image.3001.net/images/20180414/15236846244195.png!small)  

### 锁定浏览器主页

我们查看解密出的url的交叉引用，可以看到有三处调用逻辑。

![xref.png](https://image.3001.net/images/20180414/15236905429273.png!small)  

lockpage_logic1:

![lock_logic1.png](https://image.3001.net/images/20180414/15236906617796.png!small)  

lock_logic2:

![lock_logic2.png](https://image.3001.net/images/20180414/15236907714394.png!small)  

lock_logic3:

![lock_logic3.png](https://image.3001.net/images/20180414/1523691040339.png!small)  

### 创建映像加载和进程回调

创建映像加载和进程回调，在指定进程运行时，运行相关的病毒逻辑。

![proc_image.png](https://image.3001.net/images/20180414/15236850401627.png!small)  

### 注册minifilter

逻辑如下：

![minifilter.png](https://image.3001.net/images/20180414/1523700734560.png!small)  

### 更新及检测各逻辑是否都正常执行

![@FUWY4TU_U8CCP6{\)\(@OXFC.png](https://image.3001.net/images/20180414/15237014644061.png!small)  

这里有三个全局变量，updata_flag,run_spyware_flag和lockpage_flag,检测这几个flag位是否正常，特别注意的是lockpage_flag，如果此标志位不为1，则表示加密的url位正常解密，则会再次执行锁首逻辑。

额，大部分的功能都分析完了，一部分觉得没必要的就省去了，还有一部分分析的不透，也没写上了，内核这块还是不太熟悉，大佬们勿喷。

 *** 本文作者：0zapt4toM，本文属FreeBuf原创奖励计划，未经许可禁止转载**

