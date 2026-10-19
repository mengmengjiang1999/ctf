# 1.前言

APT-Q-27也被称为Operation Dragon
Breath或者金狗眼，是一个主要针对东南亚博彩产业相关人员的黑客团伙，本次分析的样本为APT-Q-27针对中文Telegram用户的攻击，样本使用了多重的白加黑侧加载。

# 2.样本运行流程图

![image](https://image.3001.net/images/20230512/1683889518_645e1d6ea64dc081ef721.png!small)

# 3.恶意代码分析

打开目标网站，显示有4个平台的Telegram可以下载  
![image](https://image.3001.net/images/20230506/1683373543_64563de7b4d31d3b1c419.jpg!small)

我们点开Windows平台的下载链接  
![image](https://image.3001.net/images/20230506/1683373394_64563d525c24501a57d9b.jpg!small)

下载链接是根据浏览器的User-Agent进行判断，如果本机是Linux系统点击下载Windows版的Telegram下载链接会定向到Telegram.apk，下载链接地址为hxxps[:]//down[.]telegramxo[.]com/Telegram.apk  
![image](https://image.3001.net/images/20230506/1683373345_64563d2115ed15139420a.jpg!small)

通过修改浏览器的User-Agent信息为Windows系统，成功下载到TG.exe，下载链接地址为hxxps[:]//down[.]telegramxo[.]com/Telegram.apk  
![image](https://image.3001.net/images/20230506/1683373621_64563e35054d9347cb11b.jpg!small)

修改浏览器的User-Agent信息为ios，点击下载发现跳转到了hxxps[:]//apps[.]apple[.]com/app/telegram-messenger/id686449807，此链接为Apple Store的官方下载地址，可以判断攻击者并没有准备针对ios平台的攻击  
![image](https://image.3001.net/images/20230506/1683373691_64563e7bec53434b50c65.jpg!small)

修改浏览器的User-Agent信息为MAC
OS，下载了Telegram.dmg，下载链接地址为hxxps[:]//osx[.]telegram[.]org/updates/Telegram.dmg，此地址为Telegram官方下载链接，由此判断攻击者暂时也没有准备针对MAC
OS平台下的攻击  
![image](https://image.3001.net/images/20230506/1683373887_64563f3f504e81752c007.jpg!small)

## 3.1 TG.exe分析

使用exeinfope查看TG.exe发现是使用advanced installer进行打包的安装包  
![image](https://image.3001.net/images/20230506/1683374315_645640eb8975599541879.jpg!small)

我们双击TG.exe进行安装  
![image](https://image.3001.net/images/20230506/1683374458_6456417a632e76f0f36fa.jpg!small)

安装完毕后在桌面会创建Telegram的快捷方式，我们查看快捷方式发现目标指向了TG.exe的安装目录其中参数为`appU.exe
appU.dll,OpenURL appr.lnk`  
![image](https://image.3001.net/images/20230506/1683374573_645641ed3e97d0b9b2d39.jpg!small)

使用die查看appU.exe发现是使用Visual Studio 2005编译的32位程序  
![image](https://image.3001.net/images/20230506/1683374735_6456428fb03a1b3e4eaba.jpg!small)

查看appU.exe的属性可以看到没有数字签名，通过详细信息查看此文件的原始文件名为RUNDLL.EXE，文件版本号为5.1.2600.5512（Windows
XP SP3），此PE文件可能是Windows XP
SP3系统下自带的rundll.exe，rundll.exe一般用于加载dll并执行指定的命令行参数的导出函数  
![image](https://image.3001.net/images/20230506/1683374892_6456432c45cdfbfd4ad4f.jpg!small)

在VT搜索appU.exe的sha256 hash可以看到此文件确实为Microsoft编写，首次提交VT的时间为2009-02-12  
![image](https://image.3001.net/images/20230506/1683375228_6456447c48c3506918de3.jpg!small)

接着我们使用die查看appU.dll可以看到是使用VS2013编译的32位dll  
![image](https://image.3001.net/images/20230506/1683375387_6456451b13ee1d1c95cbc.jpg!small)

查看appU.dll的属性，可以看到原始文件名为URL.DLL，文件版本号6.0.2900.5512（Windows XP SP3）  
![image](https://image.3001.net/images/20230506/1683375474_645645722762d47e9a783.jpg!small)

在VT搜索appU.dll的sha256 hash可以看到此文件也是Microsoft编写，首次提交VT的时间为2010-03-27  
![image](https://image.3001.net/images/20230506/1683375702_645646563fe9952af22ae.jpg!small)

查看appU.dll的导出函数，一共导出了22个函数，其中可以看到OpenURL函数，这下我们知道Telegram快捷方式参数的作用了`appU.exe
appU.dll,OpenURL
appr.lnk`，appU.exe（rundll.exe）加载appU.dll（url.dll）调用导出函数OpenURL并传入参数appr.lnk  
![image](https://image.3001.net/images/20230506/1683376462_6456494e5c7dc3438c3ab.jpg!small)

使用ida查看OpenURL函数的实现，可以看到OpenURL和OpenURLA导出函数其实相同，OpenURL函数主要就是通过我们传入的参数lpFile之后直接调用ShellExecuteA函数打开，由于OpenURL函数的实现我们不仅可以打开网页URL还可以运行指定路径的可执行程序  
![image](https://image.3001.net/images/20230506/1683377010_64564b72b76245399603f.jpg!small)

我们查看appr.lnk快捷方式指向目标为`appR.exe /s /n /u /i:appR.dat appR.dll`  
![image](https://image.3001.net/images/20230506/1683380699_645659dba6ee8f0b57e81.jpg!small)

查看appR.exe的属性可以看到原始文件名为REGSVR32.EXE，文件版本号为5.1.2600.5512（Windows XP
SP3），regsvr32.exe是Windows操作系统中用来向系统注册/卸载控件的  
![image](https://image.3001.net/images/20230506/1683380723_645659f3ce41ab9b198f1.jpg!small)

通过VT查看appR.exe确实为Microsoft官方编写  
![image](https://image.3001.net/images/20230506/1683380865_64565a8195d6993d4fe00.jpg!small)

appR.dll的原始文件名为scrobj.dll，Windows Script
Components（WSC）允许程序员使用VBScript或JScript这样的脚本语言来创建COM组件，scrobj.dll就是处理COM实现细节的运行时模块  
![image](https://image.3001.net/images/20230506/1683381456_64565cd0e5ec6a67f07d6.jpg!small)

查看appR.dat，发现是一个SCT脚本，此SCT脚本的描述信息为Bandit（强盗），JScript代码使用了jsjiami.com.v6进行了加密混淆  
![image](https://image.3001.net/images/20230506/1683382526_645660fe3930736dfa8d6.jpg!small)

我们查看regsvr32的命令行参数用法，`appR.exe /s /n /u /i:appR.dat appR.dll`，主要的就是通过appR.exe
（regsvr32.exe）注册调用appR.dll（scrobj.dll）中的DllInstall函数并将appR.dat（.SCT）当作参数传入  
![image](https://image.3001.net/images/20230506/1683381138_64565b929df940b8a7261.jpg!small)

可以看到appR.dll（scrobj.dll）有11个导出函数，其中的DllInstall函数将被调用  
![image](https://image.3001.net/images/20230506/1683388305_64567791e79a0f91cb87c.jpg!small)

我们双击运行，确实运行了Telegram  
![image](https://image.3001.net/images/20230508/1683539766_6458c736c2710028d4cb1.jpg!small)

发现一共有3个新增进程，还有另外两个名为autorun.exe的进程  
![image](https://image.3001.net/images/20230508/1683540006_6458c82697a348ed01665.jpg!small)

我们查看Tgec500d3d.exe发现有某数字公司的签名但是签名是无效的  
![image](https://image.3001.net/images/20230512/1683893820_645e2e3ca6b991af6ac1b.jpg!small)

可以看到数字签名不落在PE文件的任何一个区段，可以判断此数字签名证书应该是伪造的  
![image](https://image.3001.net/images/20230512/1683893882_645e2e7a4e3e44e9beb7f.jpg!small)

其中的std_7.0.0.1030是有某数字公司有效数字签名的PE文件，通过ResourceHacker工具查看似乎是数字公司的杀毒软件安装程序，目前暂不清楚此PE文件的作用  
![image](https://image.3001.net/images/20230512/1683894227_645e2fd33d22c65bcc87d.jpg!small)

进程PID为6652的autorun.exe进程权限提升为了管理员权限，这里bypass了UAC实现了提权  
![image](https://image.3001.net/images/20230508/1683540127_6458c89f5d7b4b7d9df74.jpg!small)

通过Procmon查看发现还在`C:\Users\xxxxx\AppData\Roaming\Microsoft\Windows\Start
Menu\Programs\Startup`开机自启目录创建了KB382456.url和KB894565.url快捷链接  
![image](https://image.3001.net/images/20230508/1683540398_6458c9aed0462d71cc735.jpg!small)

我们查看这两个url文件发现他们指向的都是本地文件  
![image](https://image.3001.net/images/20230508/1683540588_6458ca6c8b72ba9f1582d.jpg!small)

我们查看进程创建情况，创建的进程为`C:/Users/Public/reloc/SILan.exe`和`C:/Users/Public/reloc/0/SILan.exe`路径  
![image](https://image.3001.net/images/20230508/1683540715_6458caeb4b304405ecf14.jpg!small)

## 3.2 autorun.exe分析

我们查看`C:/Users/Public/reloc/`路径下的文件  
![image](https://image.3001.net/images/20230508/1683540918_6458cbb61b7a4ec0cd417.jpg!small)

通过die查看SILan.exe是使用VC6.0编译并且无数字签名  
![image](https://image.3001.net/images/20230512/1683894814_645e321ed68704a4147c2.jpg!small)

使用ida查看SILan.exe，通过搜索autorun字符串  
![image](https://image.3001.net/images/20230508/1683541757_6458cefd502ad793edadf.jpg!small)

通过交叉引用发现调用WinExec函数执行了autorun.exe  
![image](https://image.3001.net/images/20230508/1683541743_6458ceef2e05cb641b1b3.jpg!small)

使用die查看autorun.exe发现是使用VS2003编译的32位程序并且有数字签名  
![image](https://image.3001.net/images/20230508/1683541096_6458cc687c2dfc76b21ee.jpg!small)

查看autorun.exe发现确实数字签名确实有效  
![image](https://image.3001.net/images/20230508/1683541198_6458ccce6da9d8344dbce.jpg!small)

查看详情发现原文件名是Language.exe，根据文件说明应该是PowerDVD软件附带的  
![image](https://image.3001.net/images/20230508/1683541252_6458cd045ee5ce16e048a.jpg!small)

通过die查看language.dll发现编译时间戳为2023-4-28使用VS2010编译  
![image](https://image.3001.net/images/20230508/1683541368_6458cd787815b1b7791c7.jpg!small)

language.dll有2个导出函数分别为LangDLLMain、SetRegPath  
![image](https://image.3001.net/images/20230508/1683541434_6458cdba35441c123dfc0.jpg!small)

TemplateG.txt是一个加密文件  
![image](https://image.3001.net/images/20230508/1683541943_6458cfb7ded6fbe7eb943.jpg!small)

使用ida查看autorun.exe通过字符串发现language.dll  
![image](https://image.3001.net/images/20230508/1683542028_6458d00cdc67409b49bc1.jpg!small)

通过交叉引用看到首先通过LoadLibraryW加载了language.dll，然后通过GetProcAddress函数分别获取了SetRegPath、LangDLLMain导出函数地址，之后先调用了SetRegPath函数接着调用了LangDLLMain函数  
![image](https://image.3001.net/images/20230508/1683542090_6458d04a62a2f0055b1bf.jpg!small)

查看`C:/Users/Public/reloc/0/`路径下的文件两个文件路径下只有TemplateG.txt加密文件的内容不同其他的文件都是相同的  
![image](https://image.3001.net/images/20230508/1683540938_6458cbcabc49446882bc1.jpg!small)

## 3.3 C:/Users/Public/reloc/0/分析

我们首先调试的是`C:/Users/Public/reloc/0/`路径下的autorun.exe，通过x32dbg调试此为language.dll的导出函数SetRegPath函数，首先调用CreateFileW函数打开了`C:\Users\Public\reloc\0\templateG.txt`  
![image](https://image.3001.net/images/20230508/1683543046_6458d406b9e96cfe67377.jpg!small)

初始化KERNEL32.dll字符串  
![image](https://image.3001.net/images/20230508/1683543369_6458d549b3959aaca3a92.jpg!small)

初始化VirtualAlloc和CreateThread字符串，并通过LoadLibraryW函数获取kernel32基址  
![image](https://image.3001.net/images/20230508/1683543417_6458d57971395a80b45f7.jpg!small)

调用GetProcAddress获取VirtualAlloc函数地址  
![image](https://image.3001.net/images/20230508/1683543577_6458d619c9d101f04b408.jpg!small)

调用VirtualAlloc函数申请了0x4CB20字节小大的PAGE_EXECUTE_READWRITE权限的虚拟内存  
![image](https://image.3001.net/images/20230508/1683543629_6458d64dec612c595a5bf.jpg!small)

调用ReadFile函数将templateG.txt文件读取到申请的虚拟内存空间地址加偏移0x3800处  
![image](https://image.3001.net/images/20230508/1683543749_6458d6c509ba704f58c8f.jpg!small)

之后对数据进行解密，解密算法主要的逻辑就是将第1个字节取出当作key，将key取反和第2个字节进行按位与得到byte1，之后将第2个字节取反和key进行按位与得到byte2，之后将byte1和byte2进行按位或操作得到明文填入第一个字节，之后从第3个字节开始取出加密字节重复和key进行以上步骤实现解密，解密后的数据为ShellCode  
![image](https://image.3001.net/images/20230508/1683544116_6458d8348fbf1bc978f6c.jpg!small)

以下的python脚可以用于解密templateG.txt

    
    
    #!/usr/bin/python3
    # author: yauv
    # time: 2023-05-12
    # Decrypt APT-Q-27 templateG.txt ShellCode
    
    import os
    import sys
    
    def DecryptShellCode(data, size):
        key = data[0]
        dByte = b''
        for i in range(size-1):
            dByte += bytes([(~key & data[i+1]) | (~data[i+1] & key)])
        dByte += bytes([data[size-1]])
        with open('decryptShellCode','wb') as f:
            f.write(dByte)
        print("Decrypt ShellCode Sucess!")
    
    if __name__ == "__main__":
        if len(sys.argv) == 2:
            argv = sys.argv[1]
            size = os.path.getsize(argv)
            with open(argv,'rb') as f:
                data = f.read()
            DecryptShellCode(data, size)
        else:
            print("Usage: python3 decrypt.py [arg1]")
    

使用GetProcAddress函数获取CreateThread函数地址后执行解密后的ShellCode  
![image](https://image.3001.net/images/20230508/1683544714_6458da8a260822cd60528.jpg!small)

此为ShellCode起始位置有一个跳转  
![image](https://image.3001.net/images/20230508/1683544903_6458db4797304da9777a3.jpg!small)

跳转后首先会通过HASH算法获取函数地址  
![image](https://image.3001.net/images/20230508/1683545047_6458dbd7138dc117347c3.jpg!small)

查看HASH算法判断为BKDRHash  
![image](https://image.3001.net/images/20230508/1683545032_6458dbc8bc259bbc76284.jpg!small)

通过获取的函数HASH和BKDRHash算法判断此ShellCode特征和github的开源项目[DllToShellCode](https://github.com/killeven/DllToShellCode)十分相似  
![image](https://image.3001.net/images/20230508/1683545166_6458dc4eb5a625d9ef6c8.jpg!small)

DllToShellCode开源项目使用的BKDRHash算法  
![image](https://image.3001.net/images/20230508/1683545296_6458dcd0f16717737602f.jpg!small)

可以看到这里加载ntdll和DllToShellCode项目中的源码也相同  
![image](https://image.3001.net/images/20230508/1683545386_6458dd2a2893dc1aa6999.jpg!small)

之后读取压缩大小数据通调用VirtualAlloc申请虚拟内存  
![image](https://image.3001.net/images/20230508/1683546369_6458e10109ebe95a05d8b.jpg!small)

接着通过BKDRHash获取RtlDecompressBuffer函数地址  
![image](https://image.3001.net/images/20230508/1683546470_6458e166382158a3061c3.jpg!small)

调用RtlDecompressBuffer函数设置`COMPRESSION_FORMAT_LZNT1 |
COMPRESSION_ENGINE_MAXIMUM`标志解压缩数据到虚拟内存，可以看到解压后的数据为PE文件  
![image](https://image.3001.net/images/20230508/1683546645_6458e215cea7ef1bebba6.jpg!small)

接着会检查解压缩PE文件的MZ和PE标志是否正确  
![image](https://image.3001.net/images/20230508/1683546704_6458e25017ab847f9b30d.jpg!small)

接着创建了HEAP_CREATE_ENABLE_EXECUTE（0x40000）权限的堆  
![image](https://image.3001.net/images/20230508/1683546866_6458e2f2850731f102ee4.jpg!small)

调用RtlAllocateHeap函数申请堆空间  
![image](https://image.3001.net/images/20230508/1683546941_6458e33deffe7b541fd26.jpg!small)

将解压缩PE文件的头部复制到申请的堆空间  
![image](https://image.3001.net/images/20230508/1683546985_6458e369b796f2f35cca3.jpg!small)

将解压缩PE文件的所有区段逐个复制到申请的堆空间  
![image](https://image.3001.net/images/20230508/1683547072_6458e3c0ee809f882394d.jpg!small)

修复PE文件的重定位数据  
![image](https://image.3001.net/images/20230508/1683547095_6458e3d7c2dff8f3b00fd.jpg!small)

修复PE文件的IAT  
![image](https://image.3001.net/images/20230508/1683547184_6458e430615b4ed7c81ad.jpg!small)

获取PE文件的TLS表，如果存在则逐个调用TLS回调函数，如果不存在TLS表则跳过  
![image](https://image.3001.net/images/20230508/1683547201_6458e441ec1b6c1401d8b.jpg!small)

通过call eax调用dllmain  
![image](https://image.3001.net/images/20230508/1683547450_6458e53a891dc14b8a856.jpg!small)

### 3.3.1 DecompressDll

通过ida查看dump的dll，首先会检测本进程是否为管理员权限  
![image](https://image.3001.net/images/20230508/1683547584_6458e5c0c4631b3edcf10.jpg!small)

如果本进程不是管理员权限，则会使用反射式注入加载另一个PE文件  
![image](https://image.3001.net/images/20230508/1683547907_6458e703c4dc90e9df360.jpg!small)

先将PE文件头复制到堆空间  
![image](https://image.3001.net/images/20230511/1683797011_645cb4131b9e3efaa54b5.jpg!small)

接下来就是复制Section、修复重定位数据、修复IAT、修复对应Section的内存权限  
![image](https://image.3001.net/images/20230511/1683799284_645cbcf43073db593efbe.jpg!small)

解析导出表获取导出函数UACMe函数地址  
![image](https://image.3001.net/images/20230511/1683799714_645cbea2569980206a23f.jpg!small)

调用UACMe函数  
![image](https://image.3001.net/images/20230511/1683799640_645cbe58d733cac608e1a.jpg!small)

在解压缩的dll中除了有附加带有UACMe导出函数的dll之外还有一个PE文件  
![image](https://image.3001.net/images/20230511/1683800480_645cc1a045a812cb4b13a.jpg!small)

将此PE文件提取出来发现是一个有某数字公司有效数字签名的PE文件  
![image](https://image.3001.net/images/20230511/1683800505_645cc1b95a6a994df0562.jpg!small)

查看此PE文件的调试信息，根据PDB文件的路径可知此PE文件原名应该为QuickInstProxy.exe  
![image](https://image.3001.net/images/20230511/1683800551_645cc1e79700e5c508e01.jpg!small)

### 3.3.2 UACMe分析

使用IDA分析UACMe函数，首先拼接了`C:\Windows\explorer.exe`路径  
![image](https://image.3001.net/images/20230511/1683803221_645ccc552dcc7b6a04935.jpg!small)

获取当前进程的PEB，备份当前进程PEB->ProcessParameters的ImagePathName和CommandLine字段，之后将当前进程的PEB->ProcessParameters的ImagePathName和CommandLine字段改为`C:\Windows\explorer.exe`  
![image](https://image.3001.net/images/20230511/1683804065_645ccfa15531b702e4b67.jpg!small)

将当前进程PEB的BaseDllName修改为`explorer.exe`，FullDllName修改为`C:\Windows\explorer.exe`  
![image](https://image.3001.net/images/20230511/1683804107_645ccfcb1dedfc64945ba.jpg!small)

初始化COM环境，使用管理员权限获取CLSID为`Elevation:Administrator!new:{3E5FC7F9-9A51-4367-9063-A120244FBEC7}`的COM组件对象指针  
![image](https://image.3001.net/images/20230511/1683804122_645ccfda6137840029c34.jpg!small)

调用CMLuaUtil->lpVtbl->ShellExec接口实现提权为管理员权限，此bypassUAC的方法可以参考github开源项目[UACME](https://github.com/hfiref0x/UACME/blob/master/Source/Akagi/methods/methods.c#L524)的代码实现，此方式主要逻辑就是将要提权的进程PEB信息修改为白名单特权进程explorer.exe的信息欺骗PSAPI，之后通过调用AutoElevated未记录的CMSTPLUA的ShellExec接口实现提权  
![image](https://image.3001.net/images/20230511/1683804135_645ccfe76d4ea174d53d6.jpg!small)

将进程的PEB的ImagePathName和CommandLine字段修改回去  
![image](https://image.3001.net/images/20230511/1683804210_645cd0320406005e1ae39.jpg!small)

将当前进程PEB的BaseDllName和FullDllName字段修改回去  
![image](https://image.3001.net/images/20230511/1683803747_645cce63bcb6607337990.jpg!small)

提权后以管理员权限运行将会调用函数枚举360tray.exe进程  
![image](https://image.3001.net/images/20230511/1683805552_645cd570186c71f277da7.jpg!small)

遍历进程如果找到目标进程360tray.exe则返回进程PID  
![image](https://image.3001.net/images/20230511/1683805633_645cd5c1d143da3c8ce90.jpg!small)

向目标进程360tray.exe窗口并发送WM_CLOSE关闭目标进程  
![image](https://image.3001.net/images/20230511/1683805693_645cd5fd9c291ae689fa1.jpg!small)

## 3.3 C:/Users/Public/reloc/分析

### 3.3.1 DeCompressDll

查询注册表键值Time，如果不存在则获取当前时间添加到注册表键值Time  
![image](https://image.3001.net/images/20230511/1683814025_645cf689c34fbd4552e25.jpg!small)

查询的注册表为HKEY_CURRENT_USER\SOFTWARE\ComputerName，如果使用GetComputerNameA获取成功则作为ComputerName，如果获取失败则使用UnKnow作为ComputerName  
![image](https://image.3001.net/images/20230511/1683814161_645cf7119f35d9d7b9214.jpg!small)

添加删除注册表键值都是在HKEY_CURRENT_USER\SOFTWARE\ComputerName下  
![image](https://image.3001.net/images/20230511/1683814439_645cf8275efe894e19714.jpg!small)

将Time键值中的时间每位加1用于创建互斥体  
![image](https://image.3001.net/images/20230511/1683814548_645cf894cb8bac7c7e73a.jpg!small)

接下来会获取C&C服务器地址  
![image](https://image.3001.net/images/20230512/1683823294_645d1abe99e0c1b33098a.jpg!small)

如果注册表键值中存在CopyC的话则进行Base64解码并且异或5进行解密获得C&C服务器URL，如不存在CopyC键值则使用默认的v2[.]pic447[.]com  
![image](https://image.3001.net/images/20230512/1683823360_645d1b000310c91265951.jpg!small)

和C&C服务器通信使用的是TCP协议  
![image](https://image.3001.net/images/20230511/1683814794_645cf98a5508b8407ae10.jpg!small)

通过WMI语句查询操作系统版本以及是否存在反病毒软件，通过注册表查询CPU型号  
![image](https://image.3001.net/images/20230511/1683814848_645cf9c07e68ac6c4242d.jpg!small)

获取Chrome浏览器扩展nkbihfbeogaeaoehlefnkodbefgpgknn的文件属性，通过查询可知nkbihfbeogaeaoehlefnkodbefgpgknn为Chrome浏览器的MetaMask以太坊钱包插件  
![image](https://image.3001.net/images/20230511/1683814978_645cfa42291fa58f602ae.jpg!small)

通过C&C服务器下发的命令执行对应的指令  
![image](https://image.3001.net/images/20230512/1683823450_645d1b5a318b59868d465.jpg!small)  
![image](https://image.3001.net/images/20230512/1683823464_645d1b6840a35783cc504.jpg!small)  
![image](https://image.3001.net/images/20230512/1683823475_645d1b73ba5e22fa8be7f.jpg!small)

C&C服务器的命令ID和对应功能如下表

ID| 功能  
---|---  
0| 关机  
1| 设置C&C服务器更新标志位  
2| 添加注册表键值Remark  
3| 添加注册表键值ZU  
4| 清空事件日志  
5| 复制获取的MetaMask扩展插件信息  
6| 创建线程通过CreateProcessA函数执行下载的exe  
8| 显示窗口调用ShellExecuteA执行  
9| 隐藏窗口调用ShellExecuteA执行  
0x70| 窃取剪切板数据  
0x71| 设置剪切板数据  
0x7D| 创建隐藏cmd窗口执行命令  
0x7E| CreateProcessA函数执行写入到本地的exe，或通过反射式加载dll并调用PluginMe导出函数  
0x23-0x25、0x65-0x6F、0x7F|
反射式加载dll并执行以下指定的导出函数PluginMe、isARDll、getDllName、isCSDll  
0x80| 更新C&C Server通过异或5加密并Base64编码写入CopyC注册表键值，或者创建线程执行获取Chrome的MetaMask扩展信息  
  
# 4.yara rule

以下的yara rule可以用于检测运行中的autorun.exe中通过侧加载反射式加载运行的Payload

    
    
    rule APT_Q_27_COM_bypass_UAC {
        meta:
            description = "Apt-Q-27 COM bypassUAC"
            author = "yauv"
            reference = "https://yauv.me"
            data = "2023-5-12"
        strings:
            // CMLuaUtil->lpVtbl->ShellExec
            $hex1 = {FF 75 14 8B 06 6A 00 FF 75 10 FF 75 0C 8B 40 24 FF 75 08 56 FF D0}
            // CMLuaUtil->lpVtbl->Release
            $hex2 = {8B 06 56 8B 40 08 FF D0}
            $ustring1 = "Elevation:Administrator!new:" fullword wide
            $ustring2 = "{3E5FC7F9-9A51-4367-9063-A120244FBEC7}" fullword wide
            $ustring3 = "explorer.exe" fullword wide
            $astring1 = "aaaaa.dll" fullword ascii
            $astring2 = "UACMe" fullword ascii
        condition:
            5 of them
    }
    
    rule APT_Q_27_Command_Control {
        meta:
            description = "Apt-Q-27 Command Control"
            author = "yauv"
            reference = "https://yauv.me"
            data = "2023-5-12"
        strings:
            // xor 5
            $hex1 = {80 34 30 05 40 3D 8C 00 00 00 72 F4}
            $ustring1 = "SELECT * FROM AntiVirusProduct" wide
            $ustring2 = "Root\\SecurityCenter" fullword wide
            $ustring3 = "ROOT\\CIMV2" fullword wide
            $astring1 = "v2.pic447.com" fullword ascii
            $astring2 = "C:\\Users\\%s\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions\\nkbihfbeogaeaoehlefnkodbefgpgknn\\" fullword ascii
            $astring3 = "%d-%d-%d %d:%d" fullword ascii
        condition:
            5 of them
    }
    

使用管理员权限打开PowerShel使用yara扫描全部进程`Get-Process | ForEach-Object {yara64.exe
.\aptq27.yar $_.ID}`  
![image](https://image.3001.net/images/20230512/1683885201_645e0c9101263e5d9f4ed.jpg!small)

# 5.IOCs

名称: TG.exe  
大小: 95360200 字节 (90 MiB)  
SHA1: 7fa7dccf16a24df73b1cbf6f0b9e893bbac3606b  
SHA256: d4cfb90a36244ac86c4a9c8f52308c95f010fb9ea02739b56832cfc1b1126ecb

名称: appR.dat  
大小: 12744 字节 (12 KiB)  
SHA1: 5b0f1e42e01d03b0d542cc48bdf27c75b971e587  
SHA256: f18351208b5e135f5caf2ef16bd01892dd8182e49afdef78cc7b4fc56605dfb8

名称: appR.dat.bak  
大小: 8910 字节 (8 KiB)  
SHA1: 31d2cc79bed3b1e6f241762fb2a7b3a1383db88c  
SHA256: 31f565e98ee026f4777bc0ce765dc4ec38c0b4619b8b68cbbedb966c2a4e8e28

名称: language.dll  
大小: 5120 字节 (5 KiB)  
SHA1: 08339a7110fa42b737a40e8230648586cf8412fb  
SHA256: 574f8684bffdf703bb726b62633b4581824d04c5502bc36c1f52f48269ec1893

名称: templateG.txt  
大小: 93524 字节 (91 KiB)  
SHA1: 1a61411eb60be0875744372dfd3c00ece71f216f  
SHA256: 767907401a5ed0f3aef5003e1f95267d6b7fe6dfaf75b631fc6f1d0d18f035fd

名称: templateG.txt  
大小: 206784 字节 (201 KiB)  
SHA1: 89285625ad35531d3080af1d36a84ddd4e3d5165  
SHA256: cfa225bfedf6df4c16855d053e2706290535fdccf7f2e58ee364f370aaf0ab62

## CC

hxxps://telegramos[.]org  
v2[.]pic447[.]com  
103.116.15.2

# 6.总结

根据本次分析的APT-Q-27样本主要通过多阶段的白加黑进行侧加载，可以推断此次主要攻击的目标为一些母语为中文使用Telegram的黑灰产团伙和数字加密货币投资者。侧重窃取Chrome浏览器的MetaMask以太坊钱包的数据，这和黑灰产团伙越来越多的使用数字加密货币进行交易有关，看来APT-Q-27主要就通过是黑吃黑的方式进行敛财。

# 7.参考

https://github.com/sophoslabs/IoCs/blob/master/double-dragon-breath-iocs.csv  
https://news.sophos.com/en-us/2023/05/03/doubled-dll-sideloading-dragon-breath/  
https://github.com/hfiref0x/UACME

