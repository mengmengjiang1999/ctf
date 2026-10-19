## 前言

近日，笔者参加了浙江护网，在攻击队停止攻击的那一天凌晨，Windows服务器被攻破大量失分，早晨溯源时拿到了这一份名为chrome.exe的木马样本。

木马HASH

    
    
    SHA256:7fbe93d7c29b4ea4ce918f3d16a74d2930120f44d00862bdc0a1f8289954e010
    MD5:a5f06c8e88e200a860e83a6bdd197752
    SHA1:7e5675f8c84b800a1290dd7422be1f10c2302c4d
    

## 正文

![image](https://image.3001.net/images/20220602/1654163754_6298892a98005b2b2802b.png!small)

这份木马被火绒报毒，从报毒界面可以得到关于此样本的两条信息，

  1. 64位Windows程序。

  2. 大概率是CobaltStrike后门。

既然很可能是CobaltStrike后门，那直接上传哈勃、微步一把梭看一看木马行为。可奇怪的是沙箱均未检测出网络连接行为，且被鉴定为安全，这激起了我的好奇心。

![image](https://image.3001.net/images/20220602/1654163762_629889321da741cac7231.png!small)

![image](https://image.3001.net/images/20220602/1654163770_6298893a6015633b50cda.png!small)

拖入IDA，在主函数头部发现了exit(0)，则五行伪C代码很有可能是反沙箱的代码，若是沙箱直接exit，非沙箱执行下边的解密、执行操作。

为验证这五行代码是否起到我预料的效果，我用c实现了一份类似功能的exe准备传入微步沙箱，若微步沙箱的程序运行截图中存在"sandbox!!!"则代表检测到沙箱。

    
    
    #define HIDWORD(x)  (*((DWORD*)&(x)+1)) //IDA
    int main()
    {
    	int v3; // ebx
    	__int64 v4; // kr00_8
    	v3 = GetTickCount64();                        // 反沙箱
    	Sleep(300u);
    	v4 = (int)(-300 - v3 + GetTickCount64());
    	printf_s("v4:%d\n",v4);
    	if ((int)((HIDWORD(v4) ^ v4) - HIDWORD(v4)) > 100)
    		printf_s("sandbox!!!\n");
    	else
    		printf_s("none!!\n");
    	system("pause");
    	return 0;
    }
    

![image](https://image.3001.net/images/20220602/1654163780_6298894421d667b14e640.png!small)

![image](https://image.3001.net/images/20220602/1654163792_629889500e669030ddcea.png!small)

在微步沙箱中v4为负数，检测到沙箱，而在自家Windows虚拟机内则返回正常，可见代码有效。

猜测这段代码的原理是沙箱为了节省运行时间，处理了Sleep或SleepEx类的API，导致此类API无法正常延迟，通过记录时间检测是否跳过延时即可判断是否存在沙箱。

![image](https://image.3001.net/images/20220602/1654163801_62988959750ada18a6008.png!small)

![image](https://image.3001.net/images/20220602/1654163813_629889654ad89446e6d5a.png!small)

将jg条件跳转噶了，避免其转入exit，保存后传入沙箱。

![image](https://image.3001.net/images/20220602/1654163821_6298896dccb3a18f691b9.png!small)

可见能正常分析出网络行为。

![image](https://image.3001.net/images/20220602/1654163831_62988977e0a76563e6e57.png!small)

运行完反沙箱部分便是解密shellcode，这里是带key的xor解密。

![image](https://image.3001.net/images/20220602/1654163842_6298898274933605549b3.png!small)

解密完毕后修改内存为PAGE_EXECUTE_READWRITE属性用于后续执行shellcode。

此样本另外有趣的一点是他没有使用CreateThread的方式执行shellcode，而是使用Crypt32.dll中的CertEnumSystemStore，降低杀软查杀样本的可能性。

![image](https://image.3001.net/images/20220602/1654163850_6298898abef854d453eea.png!small)

通过查询微软官方文档可知，此API会为每个找到的系统存储调用参数四提供的回调函数，这给shellcode提供了执行的机会。

为进一步分析加载器，需得到解密后的shellcode。

![image](https://image.3001.net/images/20220602/1654163859_62988993409e9ecbecc05.png!small)

直接对CertEnumSystemStore下断点，在执行前一刻dump下解密后的pfnEnum开头的0x40255大小的内存，拖入IDA.

![image](https://image.3001.net/images/20220602/1654163868_6298899c453e3940950eb.png!small)

shellcode开头，调用sub_4022F，进入函数。

![image](https://image.3001.net/images/20220602/1654163876_629889a4e41a5bfcc7682.png!small)

开头pop
rdx将返回地址取到rdx，对返回地址后续进行一系列解密操作。在sub_4022f处下断，重新dump整个shellcode(这里注意断下后取消断点再dump，否则会将软件断点int3
也dump下来)，拖入IDA。

![image](https://image.3001.net/images/20220602/1654163886_629889ae9e189bdcab56c.png!small)

又是解密。依法炮制。

![image](https://image.3001.net/images/20220602/1654163894_629889b6984b6c9b0d43b.png!small)

这一次下方0X7D位置可见经典的PE程序特征了，未见MZ头部，但可根据PE结构推测出文件头位于0x2F位置,0x2F位置刚好又是MZ头部，将DOS头复用作为代码执行空间，节省空间。

继续看上方的loc_2F,MZ头部的0x4D5A对应的pop r10后做了一次逆向操作，随后调用了sub_16023.

![image](https://image.3001.net/images/20220602/1654163903_629889bfe0e92c597405b.png!small)

进入25行的sub_16383。

![image](https://image.3001.net/images/20220602/1654163914_629889cab22e3ef308920.png!small)

根据读gs:[60h]以及ROR4可以推测sub_16383主要功能是根据HASH获取API地址。

在shellcode+0x160DF(sub_16383返回地址)打下断点，将木马运行起来，分析sub_16023的v13可知，

v13结构如下。

    
    
    typedef struct _API
    {
    	PVOID GetModuleHandleA;
    	PVOID GetProcAddress;
    	PVOID LoadLibraryA;
    	PVOID LoadLibraryExA;
    	PVOID VirtualAlloc;
    	PVOID VirtualProtect;
    }API, * PAPI;
    

![image](https://image.3001.net/images/20220602/1654163926_629889d61e721aae2211d.png!small)

再下边就是在内存展开、修复导入表...最后找到入口点并执行，所以sub_16383功能为内存加载Dll。

将Dll Dump出来，拖入IDA。

![image](https://image.3001.net/images/20220602/1654163938_629889e2dec5bc5856680.png!small)

EAT中发现ReflectiveLoader,而原生CobaltStrike木马所Map的Dll也同样导出了ReflectiveLoader，且IAT也极为相似，基本可以判断这个就是最后的功能DLL。

加载器部分分析完毕。

## 总结

1.计算Sleep类函数延时时间与实际流逝时间是否匹配可判断环境是否为正常。对沙箱来说，跳过Sleep节约时间成本是有必要的不可省去，但可适当处理GetTickCount类函数，使其与延时时间匹配。

2.对于动态解密，打好断点动态分析比静态分析省时间，至少对我这种刚上路的菜狗来说是这样。

3.CertEnumSystemStore可作为CertEnumSystemStore替代品用于执行Shellcode。

