## 一、程序功能

在装好了工具的Windows
XP中打开HookMain.exe，然后打开记事本，这时向键盘中键入任何消息都不会在记事本中出现，因为HookMain.exe已经让KeyHook.dll在记事本打开的时候加载进到记事本的进程当中了。在process
explorer中可以看到  
![1617608811_606ac06bb864e0bc905ce.png](https://image.3001.net/images/20210405/1617608811_606ac06bb864e0bc905ce.png)  
上面是notepad.exe这个进程，下面是加载的一部分动态链接库，可以看到在倒数第三行该库被加载了

### 二、HookMain.exe源代码

    
    
    #include<stdio.h>
    #include<conio.h>
    #include<windows.h>
    
    #define DEF_DLL_NAME "KeyHook.dll"
    #define DEF_HOOKSTART "HookStart"
    #define DEF_HOOKSTOP "HookStop"
    
    typedef void(*PFN_HOOKSTART)();
    typedef void(*PFN_HOOKSTOP)();
    
    void main(){
    HMODULE hDll = NULL;
    PFN_HOOKSTART HookStart = NULL;
    PFN_HOOKSTOP HookStop = NULL;
    char ch=0;
    
    //加载dll
    hDll = LoadLibraryA(Dll_NAME);
    
    //获取导出函数的地址
    HookStart =(PFN_HOOKSTART)GetProcAddress(hDll,HOOK_START);
    HookStop = (PFN_HOOKSTOP)GetProcAddress(hDll,HOOK_STOP);
    
    //开始hook
    HookStart();
    
    //输入Q退出hook
    printf("输入Q退出hook!\n");
    while(1)
    {
        char h = getch();
        putch(h);
        if(h == 'Q');
        break;
    }
    
    //结束hook
    HookStop();
    
    //卸载dll
    FreeLibrary(hDll);
    return 0;
    }
    

## 三、KeyHook.dll的源代码

    
    
    //KeyHook.cpp
    #include<stdio.h>
    #include<windows.h>
    
    #define DEF_PROCESS_NAME "notepad.exe"
    
    HINSTANCE g_hInstance = NULL;
    HHOOK g_hHook = NULL;
    HWND g_hWnd = NULL;
    
    BOOL WINAPI DLLMain(HINSTANCE hinstDLL,DWORD dwReason,LPVOID lpvReserved){
        switch(dwReason){
            case DLL_PROCESS_ATTACH:
                g_hInstance = hinstDLL;
                break;
            case DLL_PROCESS_DETACH:
                break;
        }
        return TRUE;
    }
    
    LRESULT CALLBACK KeyboardProc(int nCode,WPARAM wParam,LPARAM lParam)
    {
        char szPath[MAX_PATH] = {0,};
        char *p = NULL;
    
        if(nCode>=0){
            //bit 31:0 = key press,1 = key release
            if(!(lParam&0x80000000)){
                GetModuleFileNameA(NULL,szPath,MAX_PATH);
                p = strrchr(szPath,'\\');
                //比较当前进程名称，若为notepad.exe,则消息不会传递给应用程序（或下一个“钩子”）
                if( !_stricmp(p+1,DEF_PROCESS_NAME) )
                    return 1;
            }
        }
        //若非notepad.exe，则调用CallNextHookEx()函数，将消息传递给应用程序（或者下个钩子）
        return CallNextHookEx(g_hHook,nCode,wParam,lParam);
    }
    
    #ifdef __cplusplus
    extern "C"{
    #endif
    __declspec(dllexport) void HookStart(){
        g_hHook = SetWindowsHookEx(WH_KEYBOARD,KeyboardProc,g_hInstance,0);
    }
    __declspec(dllexport) void HookStop(){
        if(g_hHook)
        {
            UnhookWindowsHookEx(g_hHook);
            g_hHook = NULL;
        }
    }
    #ifdef __cplusplus
    }
    #endif
    

## 四、从这两段源代码中学到的东西

在用C语言写Dll文件的时候，用__declspec指定导出函数；

CALLBACK称为回调函数，是在某个特定事件发生时被指定调用的函数。在这里松开键盘按键就是这个特定的事件；

大致了解了dll文件的源代码

## 五、用OD调试HookMain.exe

用OD打开这个程序，尝试去调试它  
我是根据经验直接到内存的00401000H处找到了main的位置  
书上使用了关键字符串检索的方法，当然书上的更好，不过殊途同归，都找到了main函数的入口  
![image](https://image.3001.net/images/20210405/1617618664_606ae6e86086e6fafda89.png!small)  
下面对这个主函数的汇编代码进行分析

从00401000H到0040102EH，程序调用LoadLibraryA将KeyHook.dll载入，检测是否载入成功，同时将该模块的句柄交给EAX，这里我猜测00401088H处的函数应该是一个弹窗函数，当载入失败的时候会弹出来并告诉用户载入模块失败

从0040102FH到00401049H将两个导入函数的地址传给两个指针，我暂时找不到这两个指针，只知道HookStart()的地址传给了EBX，因为源程序后面立刻调用了HookStart()，同时在汇编处立刻调用了地址位于EBX处的函数。

从0040104BH到00401068H处，首先先调用了载入的HookStart()函数，之后调用位于00401088H处的printf()函数，之后进入一段循环，71H代表的是q，所以当输入q的时候退出循环

此处就能看出来了，之前的GetProAdress函数将得到的地址传给EAX，然后将EAX的值传给EBX和EDI，所以这里结束循环的时候，直接调用EDI处的HookStop()函数

最后释放dll同时释放所有栈空间  
这就是这个程序汇编的运行原理，我们研究一下HookStart()函数的原理，于是我们在0040104BH处单步进入![image](https://image.3001.net/images/20210405/1617621571_606af243833cce8c74312.png!small)  
根据书上的说法，10001020就是钩子过程的地址

## 六、用OD调试notepad.exe进程中的KeyHook.dll

先打开notepad.exe（用OD）在调试设置当中设置中断于新模块  
![image](https://image.3001.net/images/20210405/1617623743_606afabf45d509b2f05dd.png!small)  
然后打开HookMain.exe，并在notepad.exe中敲击键盘，此时打开OD发现dll已经被注入进去了  
![image](https://image.3001.net/images/20210405/1617624590_606afe0e4609bb5efe833.png!small)  
然后双击找到的KeyHook.dll，进入调试  
找到10001020处的KeyboardProc()函数  
这就调试成功了

## 七、总结

结合C语言源代码和汇编代码一起分析有利于了解反汇编的一些常用的结构和语法，以后遇到这些结构就不怕了

对DLL了解更深了一步

