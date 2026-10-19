反调试之最朴实的招式最致命

反调试手段检测花样层出不穷，今天来介绍俩种相对简单的手段，但是却能达到出其不意的效果。

在系统编程中我们遍历进程，模块，线程，堆的时候都需要用到一个函数：CreateToolhelp32Snapshot，其函数原型及其解释如下：

HANDLE CreateToolhelp32Snapshot(  
[in] DWORD dwFlags,  
[in] DWORD th32ProcessID  
);  
//获取指定进程的快照，以及这些进程使用的堆、模块和线程。

TH32CS_INHERIT:0x80000000

|

指示快照句柄是可继承的。  
  
---|---  
  
TH32CS_SNAPALL

|

包括系统中的所有进程和线程，以及 th32ProcessID 中指定的进程的堆和模块。 等效于使用 OR 操作 。  
  
TH32CS_SNAPHEAPLIST:0x00000001

|

包括快照中 th32ProcessID 中指定的进程的所有堆。 若要枚举堆，请参阅 Heap32ListFirst。  
  
TH32CS_SNAPMODULE:0x00000008

|

包括快照中 th32ProcessID 中指定的进程的所有模块。 若要枚举模块，请参阅 Module32First。 如果函数失败
**且ERROR_BAD_LENGTH** ，请重试该函数，直到函数成功。  
  
TH32CS_SNAPMODULE32:0x00000010

|

 **64 位 Windows：** 在 32 位进程中使用此标志包括 第 32 个ProcessID 中指定的进程的 32 位模块，而在 64
位进程中使用它包括 64 位模块。若要从 64 位进程包含 在 th32ProcessID 中指定的进程的 32 位模块，请使用
**TH32CS_SNAPMODULE32** 标志。从 64 位进程调用时，在快照中包含 在 th32ProcessID 中指定的进程的所有 32
位模块。此标志可以与 **TH32CS_SNAPMODULE** 或 **TH32CS_SNAPALL** 结合使用。 如果函数失败
**且ERROR_BAD_LENGTH** ，请重试该函数，直到函数成功。  
  
TH32CS_SNAPPROCESS:0x00000002

|

在快照中包含系统中的所有进程。 若要枚举进程，请参阅 Process32First。  
  
TH32CS_SNAPTHREAD:0x00000004

|

在快照中包含系统中的所有线程。 若要枚举线程，请参阅 Thread32First。  
  
接下来通过此函数完成进程遍历：

#include  
#include  
#include  
  
  
int main()  
{  
PROCESSENTRY32 pe32 = { 0 };  
pe32.dwSize = sizeof(PROCESSENTRY32);  
HANDLE hSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);  
BOOL bRet = Process32First(hSnap, &pe32);  
do  
{  
printf("Process Name:%S\n", pe32.szExeFile);  
printf("Process ID:%d\n", pe32.th32ProcessID);  
} while (Process32Next(hSnap, &pe32));  
CloseHandle(hSnap);  
system("pause");  
return 0;  
}

运行效果如下：![](https://image.3001.net/images/20230718/1689661704_64b63108c5fa7a0e7610d.png!small)

那么遍历出进程名，就可以开始对各种调试器进行名称查找，如果找到，说明开启了调试器，这里以x32dbg为例：

#include  
#include  
#include  
  
  
int main()  
{  
PROCESSENTRY32 pe32 = { 0 };  
pe32.dwSize = sizeof(PROCESSENTRY32);  
HANDLE hSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);  
BOOL bRet = Process32First(hSnap, &pe32);  
do  
{  
/*printf("Process Name:%S\n", pe32.szExeFile);  
printf("Process ID:%d\n", pe32.th32ProcessID);*/  
if (wcsstr(pe32.szExeFile,L"x32dbg.exe") != 0)  
{  
printf("被调试");  
system("pause");  
return 0;  
}  
} while (Process32Next(hSnap, &pe32));  
CloseHandle(hSnap);  
printf("一切正常");  
system("pause");  
return 0;  
}

效果如下：![](https://image.3001.net/images/20230718/1689661705_64b631097c9109919440a.png!small)

![](https://image.3001.net/images/20230718/1689661706_64b6310ad88f9fb643572.png!small)

​同样的道理，除了可以通过遍历进程名检检查是否有调试器开启，还可以遍历窗口名称，就像这一块：![](https://image.3001.net/images/20230718/1689661707_64b6310b9f407eb88812f.png!small)

![](https://image.3001.net/images/20230718/1689661708_64b6310c3e57a1470ad1a.png!small)

这里用到函数FindWindow，函数介绍如下：

//检索顶级窗口的句柄，该窗口的类名称和窗口名称与指定的字符串匹配。此函数不搜索子窗口。此函数不执行区分大小写.  
//的搜索。若要搜索子窗口，请从指定的子窗口开始，请使用 FindWindowEx 函数。  
HWND FindWindowA(  
[in, optional] LPCSTR lpClassName,  
[in, optional] LPCSTR lpWindowName  
);  
[in, optional] lpClassName  
类型： LPCTSTR  
类名或上一次对 RegisterClass 或 RegisterClassEx 函数的调用创建的类名或类原子。原子必须位于 lpClassName
的低序单词中;高阶单词必须为零。  
如果 lpClassName 指向字符串，则指定窗口类名。类名可以是向 RegisterClass 或 RegisterClassEx
注册的任何名称，也可以是预定义控件类名称中的任何名称。  
如果 lpClassName 为 NULL，它将查找其标题与 lpWindowName 参数匹配的任何窗口。  
[in, optional] lpWindowName  
类型： LPCTSTR  
窗口名称 (窗口的标题) 。如果此参数为 NULL，则所有窗口名称都匹配。

#include  
#include  
#include  
  
  
int main()  
{  
HWND hWnd = NULL;  
hWnd = FindWindow(NULL, L"x32dbg");  
if (hWnd != NULL)  
{  
printf("被调试");  
}  
else {  
printf("一切正常");  
}  
system("pause");  
return 0;  
}![](https://image.3001.net/images/20230718/1689661709_64b6310d3b43cf2e2bacf.png!small)

![](https://image.3001.net/images/20230718/1689661709_64b6310de011594d19f21.png!small)

注：这里单纯演示手法，在主函数中进行检测

