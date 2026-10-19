![](https://image.3001.net/images/20200414/1586862925_5e959b4d31b45.png!small)

## KimsukyAPT介绍

 **近期，我们注意到了全球范围内国家层次的网络攻击活动频率有着大幅度增加。其中，[
_APT34_](https://blog.yoroi.company/research/karkoff-2020-a-new-apt34-espionage-operation-involves-lebanon-government/)、[
_Gamaredon_](https://blog.yoroi.company/research/cyberwarfare-a-deep-dive-into-the-latest-gamaredon-espionage-campaign/)和[ _Transparent
Tribe_](https://blog.yoroi.company/research/transparent-tribe-four-years-later/)是我们在最新的几个攻击活动中发现的样本。而在这篇文章中，我们将深入分析近期一个活动比较频繁的朝鲜APT组织，该组织名为Kimsuky，我们将对其所使用的攻击技术以及样本进行深入分析。**

![](https://image.3001.net/images/20200414/1586862935_5e959b57e94a9.png!small)

## 技术分析

跟其他的APT组织不同，Kimsuky所使用的攻击链/感染链并不长，而且它在实现低检测率方面效率非常好。

KimsukyAPT的感染开始于一个典型的可执行文件，文件后缀名为“scr”，而这种后缀名是Windows系统用来识别屏幕保护程序组件所使用的。下面给出的是相关样本的一些信息：

![](https://image.3001.net/images/20200414/1586862945_5e959b61171b9.png!small)

执行之后，恶意软件会利用微软实用程序“regsv***.exe”来在目标设备中的“%AppData%\Local\Temp”路径下写入一个名为“<random_name>.tmp.db”的文件。

![](https://image.3001.net/images/20200414/1586862959_5e959b6f80197.png!small)

暂且先不管这个“.db”后缀，恶意软件所写入的这个文件其实是一种特殊构造的DLL文件，它可以作为恶意软件感染的第二阶段Payload。关于该DLL文件的静态信息如下：

![](https://image.3001.net/images/20200414/1586862966_5e959b76aebdf.png!small)

接下来，这个DLL将会被拷贝到“%AppData%\Roaming\Microsoft\Windows\Defender\”目录中，并重命名为“AutoUpdate.dll”。

恶意软件会通过设置“HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce\WindowsDefender”这个注册表键来实现“AutoUpdate.dll”库的持久化感染。在这里，攻击者所使用的文件名称以及路径非常狡猾，因为它们所指向的都是Windows
Defender：

![](https://image.3001.net/images/20200414/1586862986_5e959b8ae5723.png!small)

除此之外，通过分析“%AppData%\Local\Temp”路径下的文件内容，我们还发现了恶意软件所创建的另一个临时文件-“<random_name>.tmp.bat”，这个文件被创建完成之后会立即被删除。通过分析该文件的内容，我们发现它的功能是用来删除初始感染Payload（scr文件）和其自身的。

![](https://image.3001.net/images/20200414/1586862999_5e959b979aa27.png!small)

为了隐藏其恶意操作，并避免引起不必要的怀疑，恶意软件还会在同一目录下创建一个包含“.scr”文件的合法文档，文档名为“이력서
양식.hwp”，翻译过来的话意思大概是“简历表”。关于该文档的相关信息如下：

![](https://image.3001.net/images/20200414/1586863010_5e959ba239e2d.png!small)

打开该文件后，我们会发现它貌似真的是一份简历表（空的）：

![](https://image.3001.net/images/20200414/1586863014_5e959ba60202d.png!small)

## 绕过反病毒检测

有意思的是，为了避免被反病毒产品检测到，“AutoUpdate.dll”还会对“explorer.exe”进程执行注入操作。通过分析其恶意代码，我们识别出了执行该操作的方法代码。首先，恶意软件会设置其正确的权限，如下图所示：

![](https://image.3001.net/images/20200414/1586863024_5e959bb09c4dd.png!small)

一旦获取到了必要的权限，恶意软件就可以继续完成注入了。正如Elastic所发布的分析描述，恶意软件可以通过“VirtualAllocEx”函数将其恶意DLL的路径写入另一进程的虚拟地址空间。在本文所分析的样本中，恶意软件的注入目标为“explorer.exe”进程，它可以通过在其中创建远程线程来确保远程进程成功加载恶意代码。

为了成功执行这些操作，恶意软件首先需要知道目标进程的进程ID，这一步可以通过遍历进程树来实现，即通过CreateToolhelp32Snapshot()、Process32First()和Process32Next()这几种Windows
API来实现。接下来，恶意软件将会调用VirtualAllocEx()函数来分配一个空间并将恶意DLL的路径写入进去，完成后它将会调用WriteProcessMemory()函数来将恶意DLL的路径地址写入到分配的内存中。

最后，恶意软件将调用CreateRemoteThread() API来将新创建的线程链接到主机进程（explorer.exe）。所述逻辑的部分如下图所示：

![](https://image.3001.net/images/20200414/1586863037_5e959bbd17914.png!small)

在注入过程中，恶意软件会向“explorer.exe”进程中植入两个组件，下面显示的是我们从中提取出的两个DLL文件信息：

![](https://image.3001.net/images/20200414/1586863046_5e959bc6454b4.png!small)

![](https://image.3001.net/images/20200414/1586863049_5e959bc9e582f.png!small)

通过对比两个DLL文件的Ssdeep数据，我们会发现这两个库有一些重复的地方，而且它们两个之间存在高度相似的情况。下面显示的是哈希的不同部分：

> 3072:AFSYAyju5JpkC7xfYZo9cPqvTV+ql4yFa+z *
> +K+H/kocFAnRG5R:AFJ0qC7xAZliT004+p * 0fkoe * RG5

没错，在执行了简单的二进制差异分析之后，我们会发现这两个DLL之间仅存在非常细微的差别。

考虑到这两个DLL之间的差异，我们决定继续对其中一个DLL进行分析。深入到DLL中，我们注意到每当恶意软件必须执行某个函数时，它都依赖于一个递归的解密程序，而这个解密程序将负责对包含了实际指令的字符串进行解密，并执行其中包含的命令。下面给出的是解密程序的样本：

![](https://image.3001.net/images/20200414/1586863058_5e959bd2b8fe5.png!small)

![](https://image.3001.net/images/20200414/1586863063_5e959bd7f0bd5.png!small)

我们发现，每隔15分钟，恶意软件都会跟其C2服务器（suzuki.]datastore.]pe.]hu）进行一次通信，并将受感染主机的相关信息发送至服务器端。在这里，恶意软件所发送的三个HTTP请求使用的都是不同的URL路径以及User-Agent。具体如下图所示：

![](https://image.3001.net/images/20200414/1586863069_5e959bdd1aa5a.png!small)

## 入侵威胁指标IoC

### 哈希：

> 757dfeacabf4c2f771147159d26117818354af14050e6ba42cc00f4a3d58e51f
>
> caa24c46089c8953b2a5465457a6c202ecfa83abbce7a9d3299ade52ec8382c2
>
> bbad65136d73cbd5262bc88571677b5434ceb54fc1103f2133757dae2ec4b47b
>
> 817ef0d9d3584977d1114b7e92012b653d339434a90967cbe8016899801f3751

### C2：

    
    
    suzuki.]datastore.]pe.]hu

### 持久化感染：

    
    
    HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce\WindowsDefender

### Yara规则

    
    
    import "pe"
    rule loader {
        meta:
          description = "Yara rule for the initial loader SRC"
          author = "Yoroi - ZLab"
          last_updated = "2020-03-02"
          tlp = "white"
          category = "informational"
        
    strings:
          	$a1 = " goto Repeat1"
    		$a2 = {84 58 43 F4 39 1B 96 32 E4 2D 63}
    		$a3 = {89 04 4D 30 7A 05 10 41 EB E8 8B}
    		$a4 = {80 A1 B2 F7 15 DE F0 7E 35 75}
    		$a5 = {9C 0E 57 4C 77 B1 0E 06 08 5E}
    
    	  
        condition:
          uint16(0) == 0x5A4D and pe.number_of_sections == 5 and 3 of ($a*) 
    }
    
    import "pe"
    rule AutoUpdate_dll {
        meta:
          description = "Yara rule for the AutoUpdate_dll"
          author = "Yoroi - ZLab"
          last_updated = "2020-03-02"
          tlp = "white"
          category = "informational"
        
    strings:
          	$a1 = {48 8B 3F 48 83 78 18 10 72}
    		$a2 = {36 42 35 45 35 41 42 33 42 41 39}
    		$a3 = { DD E7 FE DA C6 F7 F9 8D 7D F9 }
    		$a4 = "1#SNAN"
    		$a5 = "d$4D9L$t"
    		$a6 = "DllRegisterServer"
    		$a7 = "DllUnregisterServer"
    	  
        condition:
          uint16(0) == 0x5A4D and pe.number_of_sections == 6 and (4 of ($a*)) 
    }
    
    import "pe"
    rule injectedDLL {
        meta:
          description = "Yara rule for the injected DLL"
          author = "Yoroi - ZLab"
          last_updated = "2020-03-02"
          tlp = "white"
          category = "informational"
        
    strings:
          	$a1 = {41 80 3E 5E 89 45 A4 75 08 49}
    		$a2 = {60 03 50 02 30 58 68 01 00 70}
    		$a3 = {98 F7 02 00 7B 44 00 00 91 44}
    		$a4 = "/?m=b&p1="
    		$a5 = "&p2=b"
    		$a6 = "/?m=a&p1="
    		$a7 = "AUAVAWH"
    	  
        condition:
          uint16(0) == 0x5A4D and pe.number_of_sections == 6 and (4 of ($a*)) 
    }
    
    rule legit_DOC {
        meta:
          description = "Yara rule for the Legit DOC"
          author = "Yoroi - ZLab"
          last_updated = "2020-03-02"
          tlp = "white"
          category = "informational"
        
    strings:
          	$a1 = "HWP Document File"
    		$a2 = "UPcfZrc"
    		$a3 = {D1 A9 30 1A 5D C1 16 41 15 DA DF 54}
    		$a4 = {B4 D5 31 1B F9 66 7C 56 5A 15}
    		$a5 = {30 30 F8 18 18 F8 00 00 E0 00 00 C8}
    		$a6 = {DC 66 43 0C 53 00 65 00 63 00}
    		$a7 = {05 00 48 00 77 00 70 00 53 00 75 00 6D 00 6D}
    	  
        condition:
          all of them 
    }

 *** 参考来源：[ _yoroi_](https://blog.yoroi.company/research/the-north-korean-kimsuky-apt-keeps-threatening-south-korea-evolving-its-ttps/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

