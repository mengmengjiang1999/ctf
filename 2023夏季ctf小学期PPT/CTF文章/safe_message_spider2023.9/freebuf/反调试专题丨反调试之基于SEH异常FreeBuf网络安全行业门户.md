在如果程序出现异常，如果有调试器，根据优先级，调试器会优先接管异常，从而就会跳过异常处理，如果没有调试器，那么程序就会接收异常。那么我们就可以注册一个异常，让程序出现异常，看异常被谁接管：

#include  
#include  
#include  
DWORD WINAPI MyIsDebug(  
LPVOID lpThreadParameter  
)  
{  
while (1) {  
__try {  
_asm int 3;  
}  
__except (EXCEPTION_EXECUTE_HANDLER)  
{  
MessageBox(NULL, L"警告", L"一切正常", MB_OK);  
continue;  
}  
MessageBox(NULL, L"警告", L"调试中", MB_OK);  
return 1;  
}  
return 1;  
}  
  
int main()  
{  
  
printf("被调试了");  
CreateThread(NULL, NULL, MyIsDebug, NULL, NULL, NULL);  
system("pause");  
return 0;  
}

这里是注册一个线程，在线程回调函数，设一个循环，循环里面放入一个int
3断点，也就是CC断点，直接在VS中运行，编译器也是一个调试器，也会被检测出来：![](https://image.3001.net/images/20230718/1689661095_64b62ea7555d6c8ca6d2d.png!small)

在文件夹中打开：![](https://image.3001.net/images/20230718/1689661096_64b62ea876283c8c7abbc.png!small)

当然异常注册有很多方法，不仅仅是int 3，但凡可以触发异常都可以，例如释放句柄，当然这个异常在调试状态下才会触发，所以稍作改动：

#include  
#include  
#include  
DWORD WINAPI MyIsDebug(  
LPVOID lpThreadParameter  
)  
{  
while (1) {  
__try {  
CloseHandle(reinterpret_cast < HANDLE>(0x9999999));  
}  
__except (EXCEPTION_EXECUTE_HANDLER)  
{  
MessageBox(NULL, L"警告", L"一切正常", MB_OK);  
return 0;  
}  
if (IsDebuggerPresent())  
{  
MessageBox(NULL, L"警告", L"调试中", MB_OK);  
}  
}  
return 1;  
}  
  
int main()  
{

CreateThread(NULL, NULL, MyIsDebug, NULL, NULL, NULL);  
system("pause");  
return 0;  
}

![](https://image.3001.net/images/20230718/1689661097_64b62ea973bcf29981b04.png!small)

![](https://image.3001.net/images/20230718/1689661098_64b62eaac93060ae5024e.png!small)

