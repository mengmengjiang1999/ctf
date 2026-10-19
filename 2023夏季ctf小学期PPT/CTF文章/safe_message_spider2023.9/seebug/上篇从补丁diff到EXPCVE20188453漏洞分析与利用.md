**作者：ze0r @360A-TEAM  
公众号：[360安全监测与响应中心](https://mp.weixin.qq.com/s/ogKCo-Jp8vc7otXyu6fTig
"360安全监测与响应中心")  
相关阅读：[[下篇]从补丁diff到EXP--CVE-2018-8453漏洞分析与利用](https://paper.seebug.org/798/
"\[下篇\]从补丁diff到EXP--CVE-2018-8453漏洞分析与利用")**

在本篇文章中，我们将对CVE-2018-8453（Windows win32kfull.sys内核提权漏洞）进行深入分析。

因国内外各大安全公司和平台主观和客观上的各种原因，该漏洞的技术分析一直模糊不清，甚至带有故意的错误，为还原真实，我们以漏洞为主，卡巴斯基的分析文章为辅进行分析。现将分析过程和利用对外分享发布，以供学习参考。

### 前言

CVE-2018-8453漏洞是一个Windows内核提权漏洞，由卡巴斯基官方于野外发现用于APT中攻击中东地区国家。在微软发布了更新补丁后，卡巴斯基也于第二天发布了关于这个漏洞的更加详细的分析，但仍然讳莫如深，以及多个故意错误（可能是因为卡巴斯基担心该漏洞可能被作为Nday利用）。此外，国内两大安全平台关于该漏洞的描述文章，也为谷歌直接翻译。故意错误加上翻译错误，让人无法清楚的知道该漏洞的原理和利用。

为了还原真实，我们以直面漏洞为主、卡巴分析文章为辅的方式对该漏洞进行分析和学习。

相关链接：

微软官方的补丁和漏洞简介可以看链接：<https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2018-8453>

卡巴斯基的分析文章链接：<https://securelist.com/cve-2018-8453-used-in-targeted-attacks/88151/>

### 正文内容

下载该漏洞的单独补丁用bindiff与历史补丁进行查看，可发现主要变化如下(新旧变化主要用上一个补丁日的win32k.sys来比较，下同)：

![
](https://images.seebug.org/content/images/2019/01/d4d3aad0-db68-410c-a5a9-864329953b72.png-w331s)

在底部，看到颜色差异比较大的就是一个叫NtUserSetWindowFNID的函数，比较一下：

![
](https://images.seebug.org/content/images/2019/01/bd8f3368-f1d0-4814-aa7b-93cc8d94cbc9.png-w331s)
![
](https://images.seebug.org/content/images/2019/01/dcc1be0e-d0b4-4e63-9c44-3308092579f6.png-w331s)

可见判断流程中，多了一个IsWindowBeingDestroyed函数调用：

![
](https://images.seebug.org/content/images/2019/01/8a399898-3a2c-49d7-9301-d1cff056550b.png-w331s)

也就是说，主要在设置改变窗口的一个成员时，多了一个检查。那么就意味着，本漏洞的原因是设置成员时，没有判断某成员造成，从名字上看，这个成员为FNID。

那么，问题在于，FNID这个成员没有检查又会造成什么影响呢？我们查看一下这个成员的作用，在win2000的部分源代码中，我们可以搜索FNID来探明FNID是什么意义。

![
](https://images.seebug.org/content/images/2019/01/02e615bc-b1bc-44b2-b1e0-97398464fb8f.jpg-w331s)

这个FNID成员是用来标识本窗口是一个什么样的窗口，比如是一个按钮还是一个编辑框，这一点从文章里也可以印证。而从补丁修改后新加的函数名IsWindowBeingDestroyed来看，这里是要判断本窗口是否已经准备删除了。从文章中说的查看ReactOS代码，可知道准备删除标记就是添加上FNID_FREE（0x8000）的标记。关键在于，不检查FREE之后的窗口是如何触发漏洞呢？

通过卡巴的文章，我们整理出来大致利用思路：代码先HOOK KernelCallbackTable->产生一个主窗口->在USER32!
**fnINLPCREATESTRUCT回调中去查找并取消掉sysShadow窗口->以主窗口作为父窗口产生一个滚动条窗口SrollBar->发送WM_LBUTTONDOWN消息->系统处理消息时会发生USER32!**fnDWORD回调，在USER32!
**fnDWORD回调中销毁主窗口->这将导致主窗口销毁从而产生USER32!**fnNCDESTROY回调->USER32!__fnNCDESTROY回调中调用NtUserSetWindowFNID更改掉FNID->至此文章中开始语焉不详，文章中说重用了sysShadow，但我们根本理解不了如何发生得重用。所以需要我们自己来动手实现。

首先我们来实现漏洞函数得调用，仔细观察：

![
](https://images.seebug.org/content/images/2019/01/9b5b067d-eab0-43d4-9b69-1c2ea3fbdb7b.png-w331s)

可以看到，要想成功更改FNID，需要满足几个条件，我们不可能只设置为0x4000（这个只是打个标记，不产生实际作用）。至于新FNID得值，我们可以按照文章中说的直接设置为0x2a1即可。而对于后面的条件，要求我们要设置的窗口原来不能有FNID（除0x4000和0x8000外，但这两个标记我们打了没用）。这里经过多次测试，发现三种情况会时FNID为空：一种是在任意类型窗口刚建立时，这时系统在用户态主动调用NtUserSetWindowFNID来设置FNID（user32.dll中自动实现），而此时，如果没有设置完FNID，则窗口还没有设置消息处理函数，也就没有处理消息的能力。而文章中提到了WM_LBUTTONDOWN消息，则可以肯定是在Scrollbar窗口完全创建之后。故此种情况不行。二种是用户注册的窗口类所产生的窗口，此窗口一直到销毁，都没有设置FNID。第三种就是文章中所说的sysShadow窗口，此窗口的作用只是产生阴影效果，但是确实FNID为空。也正是由于这个特性，本人被文章误导很长时间。后来请教leeqwind才知道，根本不是重用的sysShadow，而是SBTrack结构。另外也可以看文章截图：

![
](https://images.seebug.org/content/images/2019/01/0b80a6e3-6fb0-497f-8c9a-82dc9707b06b.png-w331s)

由于本人注意力全放在了文章触发中，还未关注利用，没注意后面的内容，其实这里已经泄露了真相（深刻检讨反思！）。从截图的红框中可看到，标记是Usst，分配者又是win32k!xxxSBTrackInit。所以很明显可知要被重用的是SBTrack。

文章中说明了需要在FNID设置为0x8000之后，再调用漏洞函数更改FNID。我们知道，一个窗口销毁的用户态接受到的最后消息是WM_NCDESTORY，在win32k中，这是在xxxFreeWindow函数中发送给窗口的：

![
](https://images.seebug.org/content/images/2019/01/21cd7e2a-cb0f-4095-ba4d-cde1fa5d5615.jpg-w331s)

可以看到在106行发送了0x82（WM_NCDESTORY）号消息，所以我们需要在106行之后想办法回到用户态。但同时有另外一个问题，就是注意第134行，这行把FNID打上0x4000的标记，而文章中完全是0x8000直接变成了0x82a1，没有0x4000的标记，所以我们如果再WM_NCDESTORY消息中去更改FNID，那么确实可以马上更改掉FNID，但是这时窗口还并没有打上0x8000的标记（到136行中才被标记），这与文章明显不符。所以文中所说的在USER32!__fnNCDESTROY中去调用NtUserSetWindowFNID更改FNID的做法为故意错误。

![
](https://images.seebug.org/content/images/2019/01/218960d5-c6df-4d07-ad2c-878b21cb54a9.png-w331s)

经过本人用pykd动态测试发现，窗口在426行的调用后，窗口句柄将不存在，NtUserSetWindowFNID函数的ValidateHwnd函数将返回0从而直接跳过FNID设置。也就是我们想要实现文章中直接将0x8000设置成0x82a1的效果，需要我们在134行到426行之间，找到一个回到用户态的调用。

这里插播一点题外话。本人一开始是在WINDOWS7的win32k.sys做分析，结果搜索很长时间未能成功找到，直到某天twitter上有人提到该漏洞在win8.1之后可利用，在看了win10的win32kfull.sys后恍然大悟，教训深刻！

回到正题，之后我们可以看到这里：

![
](https://images.seebug.org/content/images/2019/01/4b10f5c5-118e-47ec-a292-46918bb3614b.png-w331s)

上面这张截图为win10下的win32kfull.sys的IDA分析结果。我们可以看到，在256行改为了0x8000后，在266行有一个xxxClientFreeWindowClassExtraBytes函数调用：

![
](https://images.seebug.org/content/images/2019/01/3e4453ca-c920-4d1c-8c34-879757aff0ce.png-w331s)

该函数中很直接的调用了KeUserModeCallback！毫无条件的直接回到了用户态。所以我们只要符合进入到xxxClientFreeWindowClassExtraBytes函数的条件即可。仔细查看代码，发现258行的判断，主要是判断窗口是否具有扩展字节（正如xxxClientFreeWindowClassExtraBytes函数名字所暗示的那样），有的话则调用xxxClientFreeWindowClassExtraBytes函数释放掉，由于扩展字节是分配在用户空间中的，所以该函数返回到用户态让用户态代码去释放掉（至少要通知）。所以只要我们在注册窗口类的时候，cbWndExtra成员不为0即可。在窗口销毁时，就会在设置了0x8000之后，又回到了用户态。当窗口以0x8000回到用户态后，我们更改FNID为0x82a1，返回到内核态后，xxxFreeWindow继续往后执行。

回到xxxFreeWindow函数：

![
](https://images.seebug.org/content/images/2019/01/0bb62233-cef1-4dc5-b4ec-593b053d4ca5.png-w331s)

其中这里，可以看到代码判断了FNID的值，从而决定要不要调用USER32!
**fnDWORD。我们知道，当一个窗口被多个其他窗口、结构引用时，即时这个窗口已经被用户调用DestoryWindow销毁掉了，窗口对象也要在内存中继续存在，以等待所有引用它的地方不再引用它才真正释放本对象内存。那么，如果我们在销毁了一个窗口后，它的最后一个引用也释放的时候，调用xxxFreeWindow时，我们就可以用FNID来控制流程是否要回到用户态的USER32!**
fnDWORD调用。所以攻击链也就此完整。

结合上面提到的，文章中提到了使用xxxSBTrackInit。该函数主要用来实现滚动条按钮的跟随鼠标滚动，当用户在一个滚动条上按下左键，表示用户想要拖动滚动条，此时需要开始处理鼠标的移动，让滚动条也跟着相应动起来，在系统中，产生SBTrack结构来标记用户鼠标的当前位置，最后当用户放开鼠标左键时，表示用户已经拖动完成，需要释放相应SBTrack结构。

在windows 2000的源代码中，xxxSBTrackInit部分代码如下：

![
](https://images.seebug.org/content/images/2019/01/ae8551c7-ca48-412d-95bf-1898f3000991.png-w331s)
![
](https://images.seebug.org/content/images/2019/01/fb92c92c-df37-4281-b5b0-99db17a1ff7b.png-w331s)

大致流程就是在调用UserAllocPoolWithQuota申请了内存后，初始化SBtrack，会将滚动条窗口以及通知窗口的指针放在本结构中，然后在2425行将当前窗口设置为捕获窗口。之后就调用xxxSBTrackLoop开始循环来处理用户的鼠标消息：

![ ](https://images.seebug.org/content/images/2019/01/60242651-d93d-48ef-bd3c-4c272713c865.png-w331s)

可以看到，xxxSBTrackLoop循环获取消息、判断消息、分发消息。当用户放开鼠标时，应当停止跟踪处理消息，退出xxxSBTrackLoop后回到xxxSBTrackInit之后，释放SBTrack占用的内存：

![
](https://images.seebug.org/content/images/2019/01/a39ddec6-bf00-4ed4-9443-2f8d7331308e.png-w331s)

而往上两行，可以看到在释放SBTrack之前，会解除一次spwndSBNotify窗口的引用。结合上面的分析，我们可以让这次解除引用时，回到用户态。如果在用户态释放掉SBTrack，则流程再次回到内核时，紧接着后面的UserFreePool即造成重复释放的问题。

那么我们在用户态如何释放SBTrack呢？分析发现，导致释放SBTrack一种是用户正常放开了鼠标左键，还有一种就是xxxEndScroll函数：

    
    
    void xxxEndScroll(    PWND pwnd,    BOOL fCancel){    UINT oldcmd;    PSBTRACK pSBTrack;    CheckLock(pwnd);    UserAssert(!IsWinEventNotifyDeferred());
    pSBTrack = PWNDTOPSBTRACK(pwnd);if (pSBTrack && PtiCurrent()->pq->spwndCapture == pwnd && pSBTrack->xxxpfnSB != NULL) {……..省略部分代码…….
            pSBTrack->xxxpfnSB = NULL;
            /*         * Unlock structure members so they are no longer holding down windows.         */        Unlock(&pSBTrack->spwndSB);        Unlock(&pSBTrack->spwndSBNotify);        Unlock(&pSBTrack->spwndTrack);        UserFreePool(pSBTrack);        PWNDTOPSBTRACK(pwnd) = NULL;    }}

xxxEndScroll函数判断了主要根据窗口的线程信息中存放的SBTrack和pq->sqpwndCapture（）。

![
](https://images.seebug.org/content/images/2019/01/9b16cf14-a431-4b11-8222-b3952fcbb15e.png-w331s)

而我们的程序是单线程，由于每个线程信息是属于线程的，所以线程创建的所有窗口也都指向同一线程信息结构。所以，即使SBTrack所属于的Scrollbar窗口已经释放了，只要还是同一线程创建的新窗口，pSBTrack也还是原来的。而qp->spwndCapture==pwnd如何绕过呢？我们如果创建新的窗口，给这个新窗口发送的消息和操作，pwnd则为新窗口，这显然不会等于在xxxSBTrackInit中设置的捕获窗口
----旧窗口。

通过测试发现，这个Capture窗口的设置，只要简单的在用户态调用SetCapture
API即可直接设置。所以我们只要直接调用API即可让xxxEndScroll中的判断完全通过。

在搜索之后，发现可以通过如下路径调用xxxEndScroll函数：

![ ](https://images.seebug.org/content/images/2019/01/b7315ed0-ab8a-4dea-b1db-bcf29add02f6.png-w331s) ![
](https://images.seebug.org/content/images/2019/01/6d8af8dd-0416-43ee-8c20-cc79ca52f17c.png-w331s)

向一个窗口发送WM_CANCELMODE-> xxxDefWindowProc判断消息->调用xxxDWP_DoCancelMode->
xxxDWP_DoCancelMode 判断当前线程信息中pSBTrack->
xxxEndScroll。而上面我们知道，所有的窗口都在同一线程中创建，所以这里的判断也可以通过！

整理一下流程：

HOOK KernelCallbackTable->注册窗口类，WNDCLASSEXW.cbWndExtra设置为4->产生主窗口
->以主窗口作为父窗口产生一个滚动条窗口SrollBar->发送WM_LBUTTONDOWN消息->系统处理消息初始化SBTrack结构并开始循环->发生fnDWORD回调，fnDWORD回调中销毁主窗口->销毁主窗口，释放扩展字节xxxClientFreeWindowClassExtraBytes->xxxClientFreeWindowClassExtraBytes系统调用回调fnClientFreeWindowClassExtraBytesCallBack->fnClientFreeWindowClassExtraBytesCallBack
HOOK中调用NtUserSetWindowFNID更改掉窗口FNID->创建新窗口并调用SetCapture设置新窗口为捕获窗口->xxxSBLoop返回后解除主窗口引用->由于这是主窗口唯一的一个引用，这次解除导致彻底释放主窗口对象，xxxFreeWindow函数执行->由于主窗口对象的FNID已经被更改，xxxFreeWindow函数执行过程中将再一次回到用户态->用户态向新窗口发送WM_CANCELMODE消息->系统处理WM_CANCELMODE消息，释放了SBTrack->流程返回到内核继续执行xxxSBTrackInit函数最后的释放SBTrack->重复释放SBTrack！

值得说明的一点是：在上面这个流程中，完全跟sysShadow窗口没有关系，自然也跟本不需要HOOK __fnINLPCREATESTRUCT回调。

下面看一下具体代码实现：

首先，我们设置一下回调HOOK，这里就直接用fs来获取PEB了：

![
](https://images.seebug.org/content/images/2019/01/d6c48404-450a-47f8-8cb1-ec61c3980ab4.png-w331s)

创建主窗口及ScrollBar:

    
    
        WNDCLASSEXW wcex;    wcex.cbSize = sizeof(WNDCLASSEX);    wcex.style = CS_HREDRAW | CS_VREDRAW;    wcex.lpfnWndProc = DefWindowProc;    wcex.cbClsExtra = 0;    wcex.cbWndExtra = 4;     wcex.hInstance = hInstance;    wcex.hIcon = LoadIcon(hInstance, MAKEINTRESOURCE(IDI_CVE8453));    wcex.hCursor = LoadCursor(nullptr, IDC_ARROW);    wcex.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);    wcex.lpszMenuName = NULL;    wcex.lpszClassName = L"WNDCLASSMAIN";    wcex.hIconSm = LoadIcon(wcex.hInstance, MAKEINTRESOURCE(IDI_SMALL));
        RegisterClassExW(&wcex);    hMainWND = CreateWindowW(L"WNDCLASSMAIN", L"CVE", WS_DISABLED , 2, 2, 4, 3,nullptr, nullptr, hInstance, nullptr);
        hSBWND = CreateWindowEx(0, L"ScrollBar", L"SB", WS_CHILD | WS_VISIBLE | SBS_HORZ, 0, 0, 3, 3, hMainWND, NULL, hInstance, NULL);    之后发送WM_LBUTTONDOWN消息：    bMSGSENT = TRUE;    SendMessage(hSBWND, WM_LBUTTONDOWN, 0, 0x00020002);

这将导致系统初始化SBTrack并开始循环。这导致系统回调fnDWORD:

    
    
    void fnDWORDCallBack(PDWORD msg) {    if (*msg) {        HWND hCurrentDestroyWND = (HWND)*((DWORD*)(*msg));        memset(ClassName, 0, 0x10);        GetClassNameA(hCurrentDestroyWND, ClassName, 0xF);        if (!strcmp(ClassName, "ScrollBar")) {             if (bMSGSENT) {                 bMSGSENT = FALSE;                 DestroyWindow(hMainWND);             }        }    }    fnDWORD(msg);}

由于在运行过程中，DWORD回调会执行很多次，所以我们加一个全局变量bMSGSENT来控制。在系统执行DestroyWindow时，由于已经预留了扩展字节，所以会回调到用户HOOK：

    
    
    void fnClientFreeWindowClassExtraBytesCallBack(PDWORD msg) {
        if ((HWND)*(msg + 3) == hMainWND) {        hSBWNDnew = CreateWindowEx(0, L"ScrollBar", L"SB", SB_HORZ, 0,0, 0, 0, NULL, NULL, NULL, NULL);        SetWindowFNID(hMainWND, 0x2A1);        SetCapture(hSBWNDnew);    }    fnClientFreeWindowClassExtraBytes(msg);}

我们在fnClientFreeWindowClassExtraBytes回调中，直接设置FNID。由于后面还有捕获窗口的检查，所以我们一并创建窗口并且设置为捕获窗口。当流程回到系统后，发现捕获窗口已经改变，退出了xxxSBTrackLoop函数并开始释放SBTrack内存空间，在解除对主窗口的引用时，会导致调用xxxFreeWindow释放主窗口内存对象，由于我们已经改变了FNID，所以再次回到用户态。此时消息为0x70:

![
](https://images.seebug.org/content/images/2019/01/4447f4bd-7400-4214-8f0f-1baa7ab1bce6.jpg-w331s)

所以在fnDWORD中，判断消息：

    
    
    if ((*(msg + 1) == 0x70) && (hCurrentDestroyWND == hMainWND)) {        SendMessage(hSBWNDnew, WM_CANCELMODE, 0, 0);    }}

WM_CANCELMODE将导致SBTrack被释放，从用户态返回后，xxxSBTrack继续释放SBTrack将导致重复释放！

![
](https://images.seebug.org/content/images/2019/01/79fb6ffd-3690-4abf-930d-49eef4176505.png-w331s)

最后：非常感谢leeqwind的帮助！在分析过程中给了很大的帮助！再次感谢！极力推荐他的博客：<https://xiaodaozhi.com/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/784/>

