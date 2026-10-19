***本文原创作者：lant1e，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 引言

**上回我们完成了[微信中对发信息的自动调用](https://www.freebuf.com/sectool/164988.html)，这次我们接着分析微信的联系人信息，完成对联系人、群信息的获取。完整代码会放在github上：<https://github.com/15pb/wechat_tools>。**

## 蓝铁在逆向分析时的三种分析思路

我们在逆向工程中，分析方法一般是多种方法尝试。以分析微信联系人列表为例，我们可以从三方面入手来分析：

>
> 自上而下分析法此方法是从界面开始分析，也就是从窗口回调函数开始分析界面相关的代码，从界面中获取到联系人信息，这种分析方法如果对UI库(微信用的是DuiLib库)比较熟悉的话，分析起来会比较好一些。
>
>
> 自下而上分析法此方法是从API的调用开始，向上栈回溯分析，一般在我们破解一些有注册弹窗的程序会比较好下断点，而分析微信联系人列表没有弹窗信息，所以这块分析起来需要猜测API，再分析。
>
> 字符串分析法此方法可以说在任何时候都可以进行分析，比如分析联系人列表，可以从`Contact`或`ContactList`入手开始分析。

在分析微信联系人信息时，我采用了三种方法相结合的方式，起初使用的是自下而上分析法，从API入手，因为在上一节对微信发信息的函数分析时，是一步一步向上栈回溯分析的，想的也可以采用类似的方式，但在跟踪过程中耗费了大量时间找信息，并没有找到稳定的数据列表。所以最终放弃这种方法，而从UI层分析，需要先对UI库熟悉一下，而现在一心只想获取数据，不想学UI，所以只能用字符串分析法了。而使用字符串分析，发现也是没有结果。回过头来，依然使用API下断的方式，这时由于前面分析和跟踪的过程中，已经对微信的代码熟悉了，发现微信中所有的信息分为两种方式存储，第一种是UI上会有存储，第二种是数据库存储，第一种PASS，选择第二种最终找到了关键函数。下面就是我尝试的两种方式。

## 使用字符串分析法分析无果

首先使用x64dbg附加正在运行的微信，在符号选项卡中选择微信的通信逻辑模块`wechatwin.dll`：

![1.png](https://image.3001.net/images/20190214/1550127256_5c651098c73c1.png!small)![](index_files/962e16fb-d1ba-4ea1-b0c6-4570ab31418f.png)然后搜索当前模块的字符串，在字符串中过滤`Contact`:

![2.png](https://image.3001.net/images/20190214/1550127271_5c6510a7ab481.png!small)![](index_files/26f14607-55b4-4601-af20-c57034286a34.png)会发现`Contact`字符串还是很多的，换另一个`ContactList`过滤，发现少了一些。

![3.png](https://image.3001.net/images/20190214/1550127306_5c6510ca95fdd.png!small)![](index_files/389a81cb-a46c-4929-a961-97157add2f81.png)仔细观察过滤出的字符串，有几个看起来可能有关，我试了两个，最终并没找到相关代码。写出分析的过程主要就是告诉大家逆向本不是一帆风顺，有时在分析时会无功而返，在这个时候需要耐心，总会有出路的！

## 巧用sql语句执行函数找到获取联系人信息函数

在分析发信息的函数时，底层找到了执行sql语句的函数，由于执行这个函数会多次调用，经过下断观察，发现有和联系人相关的sql语句。(蓝铁提示：注意获取联系人信息的代码是在微信扫码之后执行的，所以需要在微信扫码之前使用x64dbg附加程序并下断点)

![4.png](https://image.3001.net/images/20190214/1550127327_5c6510df2a429.png!small)![](index_files/66c42d53-cde0-4708-bf29-bb51c13c8543.png)在动态跟踪的过程中，在上面代码断下后的上两层代码中，又一次调用了Sql执行函数，sql语句和上图基本一致，再继续跟踪的过程中，发现了获取微信ID的函数。![](index_files/80e8703a-9988-4131-9033-c4e91d682363.png)![5.png](https://image.3001.net/images/20190214/1550127363_5c651103505dd.png!small)

继续向下跟踪时，找到了获取微信号信息的函数。

![6.png](https://image.3001.net/images/20190214/1550127379_5c651113cec48.png!small)

![](index_files/7d75407a-40a8-449e-96d9-097816de558c.png)经过跟踪，发现这段代码是一个循环，每次获取到微信号信息不一样，并且还有群信息。如果我们能自己实现这个循环就能完成获取联系人以及群信息。但看上下文函数调用比较多。所以采用hook的方式对上图中调用的函数进行Hook是一种比较好的方法。hook的点在此：

    
    
    0CCBA0C6   | E8 45 0D 00 00       | call <wechatwin.sub_CCBAE10>          | 获取微信号信息，hook点
    

## 巧用inline hook提取联系人以及群名称

我们知道一般 `inline hook`
是在函数的开始处进行Hook,而在这个代码中发现我们要Hook的这个CALL引用的地方是比较多的，也就是说有很多地方都调用了这个函数，所以我们采用的方式是只hook我们调用的这个点。(蓝铁提示：在x64dbg中，选中函数开始处，使用快捷键x，可以查看所有引用这个函数的代码

![hook1.gif](https://image.3001.net/images/20190214/1550127436_5c65114c76af6.gif!small)![](index_files/hook1.gif))我们hook的代码是将`0CCBA0C6`处代码`call
获取微信信息`改成我们自己的函数，然后在我们自己的函数中保存微信信息，之后再跳过来。原理图如下：

![hook1-1.png](https://image.3001.net/images/20190214/1550127449_5c651159a532a.png!small)![](index_files/3c1b04f4-9f3d-4053-a49f-159882437a5e.png)原理有了剩下的就是写代码，不过写代码前需要先分析一下函数调用的参数以及我们保存的参数的结构，即微信联系人信息的结构。经过多次调用观察堆栈信息，得出了以下结果。

    
    
    call参数：
     第一个是传出缓冲区，获取微信联系人信息
     第二个是sql执行返回的对象，即查询对象或结果集对象
     我们关注的是第一个，调用之后会得到联系人信息
    
    传出缓冲区即为传出对象
     +0x8  微信ID
     +0x1C 微信号
     +0x48 标志位，1代表联系人，2代表群，3代表服务号
     +0x4C 0x0 代表个人，0x8代表普通订阅号，0x18 代表订阅、服务号，0x1C 代表系统服务
     +0x50 微信备注
     +0x64 服务名称或微信名称()
     +0xA4 拼音简称(全大写)
     +0xB8 拼音名称(全拼小写)
    

Hook的关键代码：

    
    
        // 1. 计算虚拟地址，模块基地址+RVA地址
        HMODULE hMod = ::GetModuleHandle(L"wechatwin.dll");
        DWORD dwEIPAddr = (DWORD)hMod + 0x3AA0C6;
        DWORD dwCallAddr = (DWORD)hMod + 0x3AAE10;
    
        // 2. 修改代码属性
        DWORD dwOldType = 0;
        ::VirtualProtect((LPVOID)dwEIPAddr, 5, PAGE_EXECUTE_READWRITE, &dwOldType);
    
        // 3. 读取代码
        DWORD dwRead;
        HookData stcReadData;
        ::ReadProcessMemory((HANDLE)-1, (LPVOID)dwEIPAddr, &stcReadData, 5, &dwRead);
    
        // 4. 写入代码
        HookData stcWriteData(0xE9, dwEIPAddr, (DWORD)NakeHookCall);
        ::WriteProcessMemory((HANDLE)-1, (LPVOID)dwEIPAddr, &stcWriteData, 5, &dwRead);
    
        // 5. 恢复属性
        ::VirtualProtect((LPVOID)dwEIPAddr, 5, dwOldType, &dwOldType);
    
        // 6. 记录原函数返回地址
        g_dwRetAddr = dwEIPAddr + 5;
    

从原函数跳转到的Hook代码

    
    
    DWORD g_dwRetAddr; // 用于保存返回到原函数的地址
    void _declspec(naked) NakeHookCall() {
    
        _asm {
            mov g_OutObj, esi      // 保存参数1，从这个值中获取微信信息
            mov eax, g_hMod;       // 
            add eax, 0x3AAE10;     // 计算调用函数
    
            call eax               // 调用获取微信联系人信息函数
            mov eax, SaveInfo
            call eax               // 调用自己的函数保存微信联系人信息
    
            push g_dwRetAddr       // 跳转回原函数
            ret
        }
    }
    

保存联系人的代码：

    
    
    vector<MyWXContactInfo> g_vector; // 保存微信联系人
    void SaveInfo() { // 执行到Hook点，每次都会调用这个函数保存微信联系人
        MyWXContactInfo obj(g_OutObj);
        g_vector.push_back(obj);
    }
    

自己定义的微信联系人类：

    
    
    class MyWXContactInfo {
    public:
        // +0x8  微信ID
        // +0x1C 微信号
        // +0x48 标志位，1代表联系人，2代表群，3代表服务号
        // +0x4C 0x0 代表个人，0x8代表普通订阅号，0x18 代表订阅、服务号，0x1C 代表系统服务
        // +0x50 微信备注
        // +0x64 服务名称或微信名称()
        // +0xA4 拼音简称(全大写)
        // +0xB8 拼音名称(全拼小写)
        MyWXContactInfo(DWORD dwObj) {
            m_wxID = *(wchar_t**)(dwObj + 0x8);
            m_wxNum = *(wchar_t**)(dwObj + 0x1C);
            m_wxFlag1 = *(DWORD*)(dwObj + 0x48);
            m_wxFlag2 = *(DWORD*)(dwObj + 0x4C);
            m_wxBeizhu = *(wchar_t**)(dwObj + 0x50);
            m_wxName = *(wchar_t**)(dwObj + 0x64);
        }
    
        wchar_t* PrintString() {
            CString strObj;
            strObj.Format(L"ID:%s NUM:%s f1:%p f2 %p,Beizhu:", m_wxID, m_wxNum, m_wxFlag1, m_wxFlag2);
            if (m_wxBeizhu) {
                strObj += m_wxBeizhu;
                strObj += " ";
            }
            if (m_wxName) {
                strObj += m_wxName;
                strObj += " ";
            }
            OutputDebugString(strObj.GetBuffer());
            return strObj.GetBuffer();
        }
    
    public:
        wchar_t* m_wxID;  // +0x8  微信ID
        wchar_t* m_wxNum; // +0x1C 微信号
        int      m_wxFlag1;// +0x48 标志位
        int      m_wxFlag2;// +0x4C 0x0
        wchar_t* m_wxBeizhu;// +0x50
        wchar_t* m_wxName;// +0x64
    
    };
    

除此之外，当然获取信息之后，还需要进行过滤，经过人肉分析之后，发现微信联系人结构中`0x48`和`0x47`是两个标志，可以使用这两个标志过滤群列表和联系人列表。

## 测试结果

测试代码还是写在了DLL中，所以测试的顺序是：

> 1.开微信
>
> 2.注入DLL
>
> 3.在测试对话框中点击按钮`Hook获取联系人`
>
> 4.扫码登录微信
>
> 5.打开DebugView
>
> 6.在测试对话框中点击按钮`获取群列表`
>
> 7.在测试对话框中点击按钮`获取联系人列表`

![GIF.gif](https://image.3001.net/images/20190221/15507545556963.gif!small)

## 总结

在分析微信联系人过程中，我们会发现，从一个商业软件中获取一组信息还是比较麻烦的，最终我们使用了Hook这种方式完成了功能，而写代码和分析两者其实做好都比较难，所以合格的逆向工程师，两者能力都应该具备！

 ***本文原创作者：lant1e，本文属FreeBuf原创奖励计划，未经许可禁止转载**

