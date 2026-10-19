# 1.前言

Brute Ratel C4是类似于Cobalt Strike的商业红队框架，每年的License收费为$2500，首个版本Brute Ratel C4
v0.2 (Prometheus)于2021年2月9日发布，截至发稿最新发布版本v1.1(Stoffel's
Escape)与2022年7月20日发布，相比与Cobalt
Strike的知名度BRc4显然要低调的多，但是BRc4使用的技术和功能却丝毫不亚于CS，本次分析的样本使用的最终payload就是BRc4框架。

# 2.样本运行流程图

![image](https://image.3001.net/images/20220808/1659969911_62f12177b78793f29d392.png!small)

# 3.样本IOCs

名称: Roshan_CV.iso  
大小: 4839424 字节 (4726 KiB)  
MD5: a7df3462a6dce565064cfe408557c4df  
SHA1: 6b91bfc761fe958c8ac04dd403db284ccc3a530e  
SHA256: 1fc7b0e1054d54ce8f1de0cc95976081c7a85c7926c03172a3ddaa672690042c

名称: OneDrive.Update  
大小: 277064 字节 (270 KiB)  
MD5: d6eae771c6cb12e17028fa35e4fba295  
SHA1: 70767d3f7ff7736063ee76c0d9c0e90ce895332b  
SHA256: b5d1d3c1aec2f2ef06e7d0b7996bc45df4744934bd66266a6ebb02d70e35236e

名称: OneDriveUpdater.exe  
大小: 4200864 字节 (4102 KiB)  
MD5: 792e95b64b9cf45ac8bc10d4d0f077c2  
SHA1: e50af7ee7e0a323d8aa60b6d9b3d39ab33b004f5  
SHA256: 60e64dd2c6d2ac6fe9b498fadac81bc34a725de5d893e7df8b2728d8dc5b192d

名称: version.dll  
大小: 259584 字节 (253 KiB)  
MD5: 76fa734236daa023444dec26863401dc  
SHA1: a68a1b7ca1d1ddd005fd10382bf6cd0b86e74e86  
SHA256: ea2876e9175410b6f6719f80ee44b9553960758c7d0f7bed73c0fe9a78d8e669

名称: vresion.dll  
大小: 31496 字节 (30 KiB)  
MD5: 17c1e1099b65051bb6dec71fea37315b  
SHA1: 8ed26469afbd53da7749ef9c6ab8c7f010e9bb1e  
SHA256: e549d528fee40208df2dd911c2d96b29d02df7bef9b30c93285f4a2f3e1ad5b0

名称: Roshan-Bandara_CV_Dialog  
大小: 3149 字节 (3.07 KiB)  
MD5: 82eb32d941b6dd63957a37453c9b0333  
SHA1: f27a374044c73a6a5b2d926bb9468daf570b8bfc  
SHA256: 4466017fd40c4b5fa9923928b7be3acf03825b4dd8c5fcf088992aee398b8c2d

# 4.恶意代码分析

恶意样本是个iso文件，双击挂载iso，一共有5个文件，除了`Roshan-Bandara_CV_Dialog`这个快捷方式之外其他的文件都是隐藏文件（我开启了显示隐藏文件所以这里全部显示了）  
![image](https://image.3001.net/images/20220808/1659970028_62f121ec091feceae3d7d.jpg!small)  
我们查看Roshan-Bandara_CV_Dialog快捷方式指向的目标`%windir%/system32/cmd.exe /c start
OneDriveUpdater.exe`，主要就是调用cmd命令执行了隐藏文件OneDriveUpdater.exe，`cmd.exe
/c`命令指定执行完后会自动关闭控制台窗口  
![image](https://image.3001.net/images/20220808/1659970068_62f1221497a2a8d48be59.jpg!small)  
我们接着看这个快捷方式的图标文件，发现其图标文件指向`%ProgramFiles%\Microsoft
Office\root\Office16\WINWORD.EXE`，由于本机没有装Office
2016所以此快捷方式的图标就无法显示，由此可见此次攻击样本十分有针对性  
![image](https://image.3001.net/images/20220808/1659970092_62f1222c12a7c920a4c51.jpg!small)  
其中的vresion.dll和OneDriveUpdater.exe为白文件都有Microsoft的有效数字签名  
![image](https://image.3001.net/images/20220808/1659970119_62f1224726c4fe6c393fa.jpg!small)  
其中的version.dll链接器版本14.29是使用1929 (Visual Studio 2019 Version 16.10 +
16.11)编译的64位DLL，可以看到编译时间戳为`2022-5-17 16:35:50`  
![image](https://image.3001.net/images/20220808/1659970143_62f1225fa755ac43c381e.jpg!small)  
version.dll和vresion.dll的导出函数完全相同  
![image](https://image.3001.net/images/20220808/1659970162_62f12272ad9031cc4f82b.jpg!small)  
OneDrive.Update是一个被加密的二进制文件，猜测可能是shellcode或者pe文件  
![image](https://image.3001.net/images/20220808/1659970181_62f1228538b1d1d95784d.jpg!small)  
使用ida64打开OneDriveUpdater.exe分析，我们可以看到OneDriveUpdater.exe一共调用了version.dll中的3个导出函数  
![image](https://image.3001.net/images/20220808/1659970210_62f122a251e5ac088d3c5.jpg!small)  
接下来我们使用ida64分析version.dll，查看version.dll的导出函数时发现并没有相关的实现，而是使用了导出函数转发技术将函数转发到白文件vresion.dll的实现  
![image](https://image.3001.net/images/20220808/1659970251_62f122cb864d618bdf497.jpg!small)

## 4.1 stage0：version.dll代码分析

接下来我们分析version.dll的DllMain函数，只调用了一个sub_180002090函数  
![image](https://image.3001.net/images/20220808/1659970324_62f12314003c612279c42.jpg!small)  
sub_180002090函数使用了WTSEnumerateProcessesA函数枚举进程  
![image](https://image.3001.net/images/20220808/1659970347_62f1232b61cb837245bf4.jpg!small)  
循环查找`RuntimeBroker.exe`进程  
![image](https://image.3001.net/images/20220808/1659970383_62f1234f6f31c7c18e5bb.jpg!small)  
读取加密文件`OneDrive.Update`到内存  
![image](https://image.3001.net/images/20220808/1659970424_62f12378044d156f616fc.jpg!small)  
控制台窗口打印字符串`"Please wait..."`  
![image](https://image.3001.net/images/20220808/1659970446_62f1238e8cb1bbfdf78b4.jpg!small)  
先调用了`NtDelayExecution`函数休眠了几秒，接着调用`NtOpenProcess`函数以`PROCESS_ALLACCESS`权限打开`RuntimeBroker.exe`进程  
![image](https://image.3001.net/images/20220808/1659970467_62f123a3dede266179092.jpg!small)  
此样本的NtOpenProcess函数实现，这些汇编代码特征让我想到了[SysWhispers3](https://github.com/klezVirus/SysWhispers3)项目  
![image](https://image.3001.net/images/20220808/1659970510_62f123ce463e28040449a.jpg!small)  
这是我使用SysWhispers3项目生成的NtOpenProcesss的syscall调用，发现除了SysWhispers3使用函数Hash方式之外汇编代码特征完全一致，可以判断此样本使用了SysWhispers3项目  
![image](https://image.3001.net/images/20220808/1659970529_62f123e112763de859085.jpg!small)  
接下来我们详细分析下首先`SW3_GetSyscallEGG_180001D20`函数参数为`ntop`  
![image](https://image.3001.net/images/20220808/1659970550_62f123f6dd6d4ca23d6d5.jpg!small)  
主要逻辑是通过`gs:[60]`获取PEB，然后通过偏移找到`PEB->Ldr->InMemoryOrderModuleList`链表，并通过访问`LDR_DATA_TABLE_ENTRY->FullDllName`字段使用_stricmp函数判断找到ntdll.dll  
![image](https://image.3001.net/images/20220808/1659970587_62f1241b05c0f0dbdbb4d.jpg!small)  
接下来通过解析ntdll.dll的PE结构获取导出函数  
![image](https://image.3001.net/images/20220808/1659970611_62f124336ac256d40f675.jpg!small)  
第一个导出函数名称  
![image](https://image.3001.net/images/20220808/1659970636_62f1244c0dc657764ef2c.jpg!small)  
memcmp函数对比直到找到导出函数NtOpenProcess  
![image](https://image.3001.net/images/20220808/1659970653_62f1245db651fc42539de.jpg!small)  
最终获取到导出函数地址  
![image](https://image.3001.net/images/20220808/1659970670_62f1246eda98dd42a2cc8.jpg!small)  
接下来通过搜索函数NtOpenProcess的OPCODE特征找到syscall（0F05）的地址（EGG）  
![image](https://image.3001.net/images/20220808/1659970685_62f1247de9e0374444445.jpg!small)  
接下来分析`SW3_GetSyscallNumber_180002000`函数，主要逻辑还是通过OPCODE特征搜索找到syscall
id，关于syscall
id对应的函数在不同windows版本下不同可以在[j00ru](https://j00ru.vexillium.org/syscalls/nt/64/)的博客查询  
![image](https://image.3001.net/images/20220808/1659970703_62f1248f8e342563d39ec.jpg!small)  
此时RAX为NtOpenProcess函数的syscall id：26，r15为syscall的地址  
![image](https://image.3001.net/images/20220808/1659970722_62f124a2e8d8303bcf9c1.jpg!small)  
通过syscall调用NtOpenProcess函数  
![image](https://image.3001.net/images/20220808/1659970735_62f124afc72ebc8d8df38.jpg!small)  
接下来使用硬编码的xor密钥`jikoewarfkmzsdlhfnuiwaejrpaw`解密`OneDrive.Update`，解密大小为0x493E0  
![image](https://image.3001.net/images/20220808/1659970754_62f124c2b875aefb4811a.jpg!small)  
调用了`NtCreateSection`函数创建`0x493E0`大小的`PAGE_EXECUTE_READWRITE`内存权限，`SECTION_MAP_READ
| SECTION_MAP_WRITE | SECTION_MAP_EXECUTE`访问属性的section  
![image](https://image.3001.net/images/20220808/1659970780_62f124dc51a0852c10423.jpg!small)  
接着调用`NtMapViewOfSection`函数将section映射到本进程虚拟内存  
![image](https://image.3001.net/images/20220808/1659970795_62f124eb27900503f07c8.jpg!small)  
并调用`NtMapViewOfSection`函数将section映射到`RuntimeBroker.exe`进程虚拟内存  
![image](https://image.3001.net/images/20220808/1659970809_62f124f9a65d0cd92aefc.jpg!small)  
使用memmove函数将解密后的shellcode复制到本进程section共享内存空间，此时section内存会同步映射到远程进程`RuntimeBroker.exe`进程虚拟内存  
![image](https://image.3001.net/images/20220808/1659970824_62f1250803f79d29dac10.jpg!small)  
然后调用NtCreateThreadEx函数在RuntimeBroker.exe进程中创建远程线程执行注入的shellcode  
![image](https://image.3001.net/images/20220808/1659970838_62f1251657c6bc8619cd2.jpg!small)  
我们使用processhack工具查看`RuntimeBroker.exe`进程内存可以看到shellcode已经注入成功  
![image](https://image.3001.net/images/20220808/1659970857_62f12529de3a2d92cb711.jpg!small)

## 4.2 stage1：OneDrive.Update代码分析

为了方便调试我将stage0解密后的shellcode从内存中dump下来并使用自写的shellcode
loader加载调试分析，shellcode开头有巨量的`mov`和`push`执行的组合，通过压入栈中的数据可以判断大致是在初始化数据和函数调用要用到的参数等等  
![image](https://image.3001.net/images/20220808/1659970895_62f1254f131f8fd9a8e4f.jpg!small)  
在偏移0x43750处才开始主要逻辑  
![image](https://image.3001.net/images/20220808/1659970910_62f1255e3860f9416246f.jpg!small)  
可以看到刚刚压入栈中的众多数据包含了一个PE文件并且此PE文件的Dos头的MZSignature（0x5A4D）被抹除防止EDR进行内存扫描查杀，通过访问0x3C位置AddressOfNewExeHeader开始解析此PE文件  
![image](https://image.3001.net/images/20220808/1659970928_62f12570b2b249e328786.jpg!small)  
最终获取导出函数的RVA：0x92E0  
![image](https://image.3001.net/images/20220808/1659970946_62f12582a9f61d7204ff1.jpg!small)  
接下来的逻辑还是熟悉的通过`PEB-Ldr->InMemoryOrderModuleList`获取ntdll.dll的基址  
![image](https://image.3001.net/images/20220808/1659970961_62f125918f165c52bd9dd.jpg!small)  
然后调用FindHashFunAddress_5137AE函数通过函数Hash获取对应函数的地址  
![image](https://image.3001.net/images/20220808/1659970974_62f1259e008a21deca0a7.jpg!small)  
通过解析ntdll.dll的PE结构获取导出函数名称表  
![image](https://image.3001.net/images/20220808/1659970986_62f125aa1362d1907962a.jpg!small)  
并对导出函数名进行ror13 Hash然后对比目标函数Hash直到找到需要的函数  
![image](https://image.3001.net/images/20220808/1659970998_62f125b6b5af18ca9ca70.jpg!small)  
获取到需要的导出函数地址后会调用CheckFuninlineHook_51375B函数进行检查  
![image](https://image.3001.net/images/20220808/1659971011_62f125c3e7ecf5e1b34d3.jpg!small)  
首先检查函数头是否被下了int3软件断点（0xCC），然后通过检测OPCODE编码E9（jmp）判断函数是否被EDR给inlineHook，如果函数正常则通过偏移获取函数的syscall
id  
![image](https://image.3001.net/images/20220808/1659971031_62f125d78197c62e67510.jpg!small)  
接着将参数压栈，通过syscall调用`ZwAllocateVirtualMemory`申请`PAGE_READWRITE`权限的内存  
![image](https://image.3001.net/images/20220808/1659971049_62f125e93ff06e9281f33.jpg!small)  
接着又申请了一块内存`PAGE_READWRITE`权限的内存  
![image](https://image.3001.net/images/20220808/1659971083_62f1260b3b9d84133bb55.jpg!small)  
申请完内存后调用了CopyPeToAllocAddress_513815函数  
![image](https://image.3001.net/images/20220808/1659971097_62f126192099646094265.jpg!small)  
此函数将栈中的PE文件（0x3240）大小的内容以每次QWORD大小复制到申请的虚拟内存中  
![image](https://image.3001.net/images/20220808/1659971111_62f12627f1d18aa2ca021.jpg!small)  
PE文件复制完成  
![image](https://image.3001.net/images/20220808/1659971123_62f1263398bdfc6528210.jpg!small)  
接着调用
MemSetPeMemoryFeatures_513805函数将内存中PE文件Dos头除了AddressOfNewExeHeader字段以外的内存置0，防止EDR扫描内存查杀  
![image](https://image.3001.net/images/20220808/1659971136_62f126403f35f7f065ddf.jpg!small)  
又调用了MemSetPeMemoryFeatures_513805函数将内存中PE文件DosStub部分的内存置0  
![image](https://image.3001.net/images/20220808/1659971154_62f12652e70f00f66381b.jpg!small)  
接着调用CopyBase64ToAllocAddress_513820函数  
![image](https://image.3001.net/images/20220808/1659971202_62f1268206271c17dd6f9.jpg!small)  
将0x148字节大小的Base64编码数据复制到申请的第二块虚拟内存中  
![image](https://image.3001.net/images/20220808/1659971216_62f12690ee053b11b40c7.jpg!small)  
复制完内存后还是通过调用FindHashFunAddress_5137AE函数通过函数Hash获取ZwProtectVirtualMemory函数地址  
![image](https://image.3001.net/images/20220808/1659971230_62f1269ed88937feec699.jpg!small)  
调用ZwProtectVirtualMemory将存放PE文件那块内存属性改为`PAGE_EXECUTE_READ`属性  
![image](https://image.3001.net/images/20220808/1659971244_62f126acc0ae83f890063.jpg!small)  
获取了ZwCreateThreadEx的syscall id  
![image](https://image.3001.net/images/20220808/1659971255_62f126b79965c037e74df.jpg!small)  
调用ZwCreateThreadEx执行的函数为函数开头获取的导出函数  
![image](https://image.3001.net/images/20220808/1659971273_62f126c9f1adf52494fe8.jpg!small)  
调用ZwWaitForSingleObject函数等待线程执行完毕  
![image](https://image.3001.net/images/20220808/1659971285_62f126d5b8382074928d7.jpg!small)

## 4.3 stage2：ReflectiveDLLInjection代码分析

stage1创建的线程执行的函数入口，搜索内存找到Nt头的Signature（PE）地址，通过kernel32.dll的hash获取基址  
![image](https://image.3001.net/images/20220808/1659971344_62f12710c3d5eb44b4e9b.jpg!small)  
访问`PEB->Ldr->InMemoryOrderModuleList`链表并对FullDllName进行ror13 Hash  
![image](https://image.3001.net/images/20220808/1659971358_62f1271e66c5e5efff479.jpg!small)  
对比Hash正确  
![image](https://image.3001.net/images/20220808/1659971371_62f1272be11cad8de57a2.jpg!small)  
获得kernel32.dll基址  
![image](https://image.3001.net/images/20220808/1659971386_62f1273ac9c77047f630f.jpg!small)  
函数GetNtdllAddress_66b2c0通过PEB加偏移获取ntdll.dll的基址  
![image](https://image.3001.net/images/20220808/1659971402_62f1274abaddfaf3d4868.jpg!small)  
接下来调用GetFunAddressByHash_668050函数通过Hash获取6个对应函数的地址  
![image](https://image.3001.net/images/20220808/1659971419_62f1275bb7676ae5453c1.jpg!small)  
通过解析kernel32.dll的PE结构导出表，对导出函数进行Hash对比找到对应的函数  
![image](https://image.3001.net/images/20220808/1659971457_62f12781e3081309661cd.jpg!small)  
成功获取LoadLibraryA函数地址  
![image](https://image.3001.net/images/20220808/1659971470_62f1278e35e229be26ca7.jpg!small)  
获取完需要的函数地址之后，对于ntdll的导出函数进行inlineHook检测并动态获取对应的syscall id  
![image](https://image.3001.net/images/20220808/1659971483_62f1279b938eabef441b8.jpg!small)  
检测函数是否被下int3软件断点，并检测函数头前7个字节OPCODE是否和函数固定特征相同，最后通过固定偏移获取syscall id  
![image](https://image.3001.net/images/20220808/1659971494_62f127a60bb88947e9e91.jpg!small)  
通过BRc4官网的功能介绍可知检测EDR的HOOK是BRc4的主要功能之一  
![image](https://image.3001.net/images/20220808/1659971506_62f127b2f28845ed5be98.jpg!small)  
此时rax为动态获取的syscall id  
![image](https://image.3001.net/images/20220808/1659971532_62f127cc17b4bd10f1dbb.jpg!small)  
通过此函数获取了4个ntdll的导出函数syscall id  
![image](https://image.3001.net/images/20220808/1659971544_62f127d8b8bb501183579.jpg!small)  
syscall（间接系统调用）也是BRc4官网介绍的主要功能特征  
![image](https://image.3001.net/images/20220808/1659971558_62f127e644ed38d364537.jpg!small)  
调用NtSetInformationProcess函数并设置参数`PROCESS_INFOMATION_CLASS`为0x28  
![image](https://image.3001.net/images/20220808/1659971575_62f127f7debc3676bc1b7.jpg!small)  
通过syscall id调用NtSetInformationProcess函数  
![image](https://image.3001.net/images/20220808/1659971589_62f128055a32f6163432a.jpg!small)  
调用NtAllocateVirtualMemory函数申请了`PAGE_READWRITE`权限的内存  
![image](https://image.3001.net/images/20220808/1659971602_62f12812839fbb1a6f0b6.jpg!small)  
syacall id调用NtAllocateVirtualMemory函数  
![image](https://image.3001.net/images/20220808/1659971615_62f1281f89b53a08a9e26.jpg!small)  
接下来将PE头0x400字节复制到了新申请的内存，通过前面获取的函数地址和此复制操作有分析过类似样本的应该可以大致推断这是[ReflectiveDLLInjection](https://github.com/stephenfewer/ReflectiveDLLInjection/blob/master/dll/src/ReflectiveLoader.c)（反射式注入），主要逻辑就是模拟系统的PE
Loader将PE文件复制到可执行内存中并修复IAT处理重定位数据然后直接调用内存中的函数执行，虽然这是10年前发布的技术但metasploit和cobalt
strike等等框架还是普遍有使用ReflectiveDLLInjection技术，此方式可以避免文件落地以减少EDR查杀  
![image](https://image.3001.net/images/20220808/1659971633_62f128311eff53453aa80.jpg!small)  
接着将全部section逐个复制到新内存  
![image](https://image.3001.net/images/20220808/1659971644_62f1283c9b1524c7e4363.jpg!small)  
复制下一个section  
![image](https://image.3001.net/images/20220808/1659971655_62f12847552ec503860e8.jpg!small)  
复制完全部secsion后开始获取IAT函数地址填充修复IAT  
![image](https://image.3001.net/images/20220808/1659971666_62f12852e67ee923de390.jpg!small)  
循环直到修复完IAT  
![image](https://image.3001.net/images/20220808/1659971677_62f1285d5619a20c06230.jpg!small)  
修复重定位数据  
![image](https://image.3001.net/images/20220808/1659971688_62f12868df23ce17b98b3.jpg!small)  
调用NtFlushInstructionCache函数刷新缓存  
![image](https://image.3001.net/images/20220808/1659971699_62f12873b19621a5cb86b.jpg!small)  
调用NtProtectVirtualMemory修改各个section的内存权限  
![image](https://image.3001.net/images/20220808/1659971712_62f12880149c51792e0f5.jpg!small)  
所有section被更改的内存权限  
![image](https://image.3001.net/images/20220808/1659971727_62f1288f576962ebcf485.jpg!small)  
我们使用processhack工具查看内存中各个区段的权限  
![image](https://image.3001.net/images/20220808/1659971739_62f1289bdb947ebde9330.jpg!small)  
之后将PE头0x200字节内存置0，防止EDR扫描内存特征查杀  
![image](https://image.3001.net/images/20220808/1659971752_62f128a801e1a1c213523.jpg!small)  
最后调用dllmain  
![image](https://image.3001.net/images/20220808/1659971766_62f128b647fb62f6f706b.jpg!small)

## 4.4 stage3：DllPayload代码分析

我们将内存中的PE文件dump出来，可以看到此PE文件为MinGW-w64编译的x64 DLL  
![image](https://image.3001.net/images/20220808/1659971794_62f128d28c01b5e5b016c.jpg!small)  
编译时间戳为`2022-3-26 4:51:36`，一共有11个sections  
![image](https://image.3001.net/images/20220808/1659971808_62f128e0456fa8a1a051a.jpg!small)  
有一个无名导出函数为ReflectiveDLLInjection  
![image](https://image.3001.net/images/20220808/1659972058_62f129da85af123595c06.jpg!small)  
接下来我们分析dllmain的两个函数sub_7A1500和sub_7A1FB0  
![image](https://image.3001.net/images/20220808/1659972079_62f129ef0242aec63e843.jpg!small)  
sub_7A1500函数通过多个时间戳函数和进程线程ID异或获得12位的唯一ID  
![image](https://image.3001.net/images/20220808/1659972092_62f129fce63713b167984.jpg!small)  
sub_7A1FB0函数主要检测确保内存中PE文件的`MZSignature（MZ）`和`NtHeaderSignature（PE00）`被抹除  
![image](https://image.3001.net/images/20220808/1659972105_62f12a09548e2ff656540.jpg!small)  
接下来分析主要的核心函数，通过Hash获取VirtualFree函数释放了不需要的两处内存  
![image](https://image.3001.net/images/20220808/1659972124_62f12a1cf3ac34c41f15b.jpg!small)  
SendRecvDataC2Server_61F89060函数就是主要的加密解密和收发数据到C2服务器  
![image](https://image.3001.net/images/20220808/1659972137_62f12a298f0bbc20e76fd.jpg!small)  
GetAllNeedFunAddressbyHash_61F83A30获取了全部需要用到的函数地址，首先获取了kernel32.dll中需要的函数（由于篇幅限制只截取了部分获取dll导出函数的截图）  
![image](https://image.3001.net/images/20220808/1659972154_62f12a3a36160b6b5d8a4.jpg!small)  
获取ntdll.dll中需要用到的函数  
![image](https://image.3001.net/images/20220808/1659972164_62f12a44ced03474fdf3e.jpg!small)  
除了获取kelnel32.dll和kernelbase.dll和ntdll.dll基址使用了通过PEB加Hash方式，获取其它DLL都使用RC4密钥`bYXJm/3#M?:XyMBF`解密dll字符串并使用LoadLibraryA加载  
![image](https://image.3001.net/images/20220808/1659972178_62f12a52d165fade70259.jpg!small)  
获取通过syscall方式调用的ntdll.dll的导出函数syscall id  
![image](https://image.3001.net/images/20220808/1659972189_62f12a5dc18fc8fecfb27.jpg!small)  
最后获取了wininet.dll中的导出函数  
![image](https://image.3001.net/images/20220808/1659972207_62f12a6f334ea45804531.jpg!small)  
接下来DecryptBase64ReqHeader_61F88DC0函数主要解密了base64参数  
![image](https://image.3001.net/images/20220808/1659972220_62f12a7c526dfa68f5d90.jpg!small)  
initDecBox9_61F8B100函数初始化了Brute Ratel C4自定义加密算法需要用的9个box[256]，初始化方法将box中每位元素减1  
![image](https://image.3001.net/images/20220808/1659972235_62f12a8b268c2cabc9ffb.jpg!small)  
此为其中一个box  
![image](https://image.3001.net/images/20220808/1659972247_62f12a97559b66b89d17a.jpg!small)  
base64解码  
![image](https://image.3001.net/images/20220808/1659972261_62f12aa56d281672e1623.jpg!small)  
使用了CryptStringToBinaryA函数解码base64，可以看到解码后的数据还是乱码  
![image](https://image.3001.net/images/20220808/1659972278_62f12ab60d67ac092c104.jpg!small)  
之后使用rc4算法和硬编码的密钥`bYXJm/3#M?:XyMBF`解密后的数据可以看到有C2的ip地址User-Agent以及一些配置信息  
![image](https://image.3001.net/images/20220808/1659972289_62f12ac14a470921809b1.jpg!small)  
对于解密的User-Agent`Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36`和Brute Ratel
C4官网的Documentation的Listener Profile配置教程中User-Agent完全一致，可以判断此样本就是Brute Ratel
C4生成的payload  
![image](https://image.3001.net/images/20220808/1659972301_62f12acdd2ce0d19926f1.jpg!small)  
base64解码配置数据头的`eyJjb29raWUiOiI=`  
![image](https://image.3001.net/images/20220808/1659972314_62f12adaa76243df4af8c.jpg!small)  
base64解码`In0=`  
![image](https://image.3001.net/images/20220808/1659972331_62f12aeb664dd8624f540.jpg!small)  
接下来GetSysInfo_61F99FC0函数主要是调用函数获取了用户名进程PID系统版本和位数等等信息  
![image](https://image.3001.net/images/20220808/1659972343_62f12af70d404a1baa695.jpg!small)  
获取的当前进程的绝对路径  
![image](https://image.3001.net/images/20220808/1659972364_62f12b0c216a735b42e99.jpg!small)  
并使用base64编码  
![image](https://image.3001.net/images/20220808/1659972428_62f12b4c0bd175166d754.jpg!small)  
获取完数据初始化winsocket版本为2.2  
![image](https://image.3001.net/images/20220808/1659972439_62f12b5764971f755127c.jpg!small)  
函数EncryptDataAndConnectC2_61F8C760首先将将获取到的的系统信息格式化  
![image](https://image.3001.net/images/20220808/1659972451_62f12b631d448d6e74057.jpg!small)  
格式化后的数据  
![image](https://image.3001.net/images/20220808/1659972463_62f12b6f71227d6b5902d.jpg!small)  
这里使用了Brute Ratel C4自定义的加密算法密钥`2Q73HI7Q0OD5BRN7`加密了数据  
![image](https://image.3001.net/images/20220808/1659972476_62f12b7c6169907a75ab8.jpg!small)  
关于Brute Ratel C4自定义的加密算法官网有进行说明，此加密用于加密和BRc4服务器之间的网络数据，这层加密是在ssl层之下  
![image](https://image.3001.net/images/20220808/1659972490_62f12b8a8b93de2f5fe18.jpg!small)  
对于Brute Ratel
C4的自定义加密算法其实就是一个比较复杂的xor加密，这里使用我逆向还原的c++代码，关于完整的加密解密算法源码感兴趣的可以去我的[github](https://github.com/yauv/brc4encrypt)，首先InitXorKeyBox函数根据key`2Q73HI7Q0OD5BRN7`生成160字节xorkey，函数首先获取key的后4字节传入replaceFourByteKey函数  
![image](https://image.3001.net/images/20220808/1659972782_62f12cae085c13d1584aa.jpg!small)  
replaceFourByteKey函数首先将4字节的key进行ror
8，然后以第1个字节数据当作g_Box1的数组下标取出值异或g_Box2[g_replaceIndex]，g_replaceIndex默认值为1每次调用replaceFourByteKey函数值+1，这是第1个字节的处理方式  
![image](https://image.3001.net/images/20220808/1659972881_62f12d114c51e5b3eb7f5.jpg!small)  
2到4字节处理方式是直接将数据当作g_Box1的数组下标取出值直接进行替换  
![image](https://image.3001.net/images/20220808/1659972956_62f12d5c73cf59317bf72.jpg!small)  
replaceFourByteKey函数处理完的4字节数据会和key的前4字节异或生成第二组xorkey的前4字节  
![image](https://image.3001.net/images/20220808/1659973029_62f12da5433acde00876d.jpg!small)  
第二组xorkey后面每4字节都是通过前4字节的key异或前一组xorkey的后4字节，这里`33 ^
48`生成的就是第二组xorkey的第5个字节，剩下的以此类推  
![image](https://image.3001.net/images/20220808/1659973373_62f12efd887bed3f14123.jpg!small)  
通过以上流程一共176字节11组xorkey生成完毕  
![image](https://image.3001.net/images/20220808/1659973439_62f12f3f0ea69ef80ee64.jpg!small)  
接下来这是EncryptData函数的主要逻辑也就是全部的加密过程，每次加密16字节的明文数据  
![image](https://image.3001.net/images/20220808/1659973480_62f12f685e9ea9836b8b8.jpg!small)  
首先调用MyXor函数使用第一组xorkey逐字节和明文数据进行异或  
![image](https://image.3001.net/images/20220808/1659973567_62f12fbfb18e2ef4deb43.jpg!small)  
接着replaceBoxData函数将数据作为g_Box1的数组下标进行替换  
![image](https://image.3001.net/images/20220808/1659973632_62f13000bb6740a300a0f.jpg!small)  
接着调用ByteOutOfOrder函数将数据乱序  
![image](https://image.3001.net/images/20220808/1659973663_62f1301f16f863e74a58b.jpg!small)  
boxXorData函数一共是处理了16字节，我这里就贴了前4个字节的图，因为加密方式都相同主要就是数据作为g_box3和g_box4数组下标取出的值进行异或  
![image](https://image.3001.net/images/20220808/1659973695_62f1303f67dbf64c8021f.jpg!small)  
再次调用MyXor函数对数据进行异或，本次使用的就是第二组xorkey，这里循环9次前面的3个函数流程相同，MyXor函数一共使用9组xorkey进行异或加密  
![image](https://image.3001.net/images/20220808/1659973781_62f130957fd827bc342e9.jpg!small)  
最后一层加密除了没有调用boxXorData函数其他的调用顺序和9次循环加密里的逻辑相同，至此16字节的明文数据加密完毕，开始加密下16字节的明文数据  
![image](https://image.3001.net/images/20220808/1659973855_62f130df621cbd086c018.jpg!small)  
通过以上加密算法加密后的数据进行base64编码  
![image](https://image.3001.net/images/20220808/1659973928_62f131282dacb9fb1c9a0.jpg!small)  
使用InternetOpenW函数设置User-Agent为`Mozilla/5.0 (Windows NT 10.0; Win64; x64)
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36`  
![image](https://image.3001.net/images/20220808/1659973946_62f1313a6153ce5d4caef.jpg!small)  
InternetConnectW函数设置C2的ip地址`174.129.157.251`和端口`443`  
![image](https://image.3001.net/images/20220808/1659973960_62f13148e868cc0417f01.jpg!small)  
HttpOpenRequestW函数涉资请求类型为POST并且请求路径为`/content.html`  
![image](https://image.3001.net/images/20220808/1659973971_62f13153b53e5ec6061ee.jpg!small)  
InternetSetOptionW设置Internet选项为`INTERNET_OPTION_SECURITY_FLAGS`  
![image](https://image.3001.net/images/20220808/1659973985_62f13161326c6c1203b2a.jpg!small)  
HttpAddRequestHeadersW函数参数`HTTP_ADDREQ_FLAG_ADD`  
![image](https://image.3001.net/images/20220808/1659973996_62f1316c488cfaa164363.jpg!small)  
向C2发送POST请求  
![image](https://image.3001.net/images/20220808/1659974007_62f1317770d3acbf2c9ec.jpg!small)  
COFFLoader（BOFs）功能部分代码  
![image](https://image.3001.net/images/20220808/1659974020_62f1318496431a1350a1f.jpg!small)  
C-Sharp内存加载部分代码  
![image](https://image.3001.net/images/20220808/1659974036_62f13194b8c63c3800513.jpg!small)  
由此分析对比官网介绍的C-Sharp、BOFs内存加载功能  
![image](https://image.3001.net/images/20220808/1659974072_62f131b80865207f0c8cc.jpg!small)  
ETW
patch功能使用的方案是直接将EtwEventWrite函数头改写C3（ret）让函数直接返回，由于没有动态调试我通过自己写的ror13Hash小工具确认函数Hash  
![image](https://image.3001.net/images/20220808/1659974113_62f131e1d98735fa02f8c.jpg!small)  
![image](https://image.3001.net/images/20220808/1659974121_62f131e9af84b625603ee.jpg!small)  
AMSI patch的方案是将AmsiScanBuffer函数头改写为`B8 57 00 07 80 C3`（mov eax,0x80070057;ret）  
![image](https://image.3001.net/images/20220808/1659974141_62f131fda80a7c757e52d.jpg!small)  
![image](https://image.3001.net/images/20220808/1659974149_62f132059d0c5741b56a1.jpg!small)  
我们反汇编amsi.dll可知如果AmsiScanBuffer函数判断传入参数错误的话会跳过扫描分支过程直接将返回值0x80070057存放eax并返回，所以这里的patch方案也是直接将0x80070057存放eax并直接ret返回  
![image](https://image.3001.net/images/20220808/1659974166_62f1321645e64a5b05313.jpg!small)

# 5.总结

Brute Ratel C4是一款非常优秀的商业红队C2框架，使用了众多用于规避和检测EDR的技术，在最新版的BRc4 v1.1（Stoffel's
Escape）的更新日志中作者宣布已经对核心程序进行了重写以隐藏内存的的几处痕迹，并且不再更新试用许可证，新申请试用许可证只会获得 v1.0.x
版本的最新更新。作者称此举是为了防止试用用户将最新的payloads上传到Virus
Total，可见BRc4作者为了对抗EDR厂商获取最新的payloads分析以进行针对性查杀的努力，BRc4作者的总结很到位这是一场EDR和BRc4之间的猫捉老鼠游戏。

