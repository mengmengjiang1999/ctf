**作者：启明星辰ADLab  
公众号：<https://mp.weixin.qq.com/s/jbZK0w53DTam_FVpLpWYGQ>**

### 1 研究背景

4月1日，以色列安全研究员Gil Dabah在博客上发布了一篇关于win32k漏洞研究文章，描述了如何通过内核对象的Destroy函数和win32k
user-mode callback缓解措施的特性来寻找UAF漏洞的新思路。

为此，启明星辰ADLab对win32k相关内核机制进行研究分析，并对这类漏洞的挖掘思路进行详细解读分析。

### 2 win32k漏洞缓解与对抗

#### 2.1 win32k user-mode callback漏洞

由于设计原因，win32k驱动需要处理很多用户层的回调，这些回调给win32k模块的安全带来了非常大的隐患，并在过去10年时间贡献了大量的漏洞。

为了便于漏洞描述，以如下伪代码进行举例分析。

    
    
    NtUserSysCall()
    ｛
        PWND p = CreateWindowEx(…);
        somecallback();
        xxxSetWindowStyle(p);
    ｝

上述代码执行效果如下图所示，用户层执行的某函数通过syscall传入内核层，当内核层代码执行到somecallback这一句时，用户层可以在用户定义的callback函数中获得代码执行的机会，如果用户在callback函数调用了DestroyWindow函数销毁窗口p，内核层的相应销毁代码将会被执行，p的相应内存被释放，回调执行完毕，NtUserSysCall函数继续执行，当执行到xxxSetWindowStyle(p)一句时，由于p的内存已经被释放从而导致UAF漏洞的产生。

![
](https://images.seebug.org/content/images/2020/05/111a0766-2239-49bd-b985-270ae656bf9d.png-w331s)

#### 2.2 user-mode callback漏洞缓解机制

为了防止上述问题的产生，微软在对象中引入了一个引用计数（对象+0x8处），对象分配时引用计数为1，当执行对象的Destroy函数时引用计数减1，当引用计数为0时对象会被真正释放。微软通过锁的概念为对象添加和减少引用计数，在win32k中为对象管理引用计数的锁有两种分别是临时锁（相应函数为ThreadLock/
ThreadUnlock）和永久锁（相应函数为HMAssignmentLock/ HMAssignmentUnlock）。经过加固之后代码表现为如下形式：

    
    
    NtUserSysCall()
    ｛
        PWND p = CreateWindowEx(…);
        ThreadLock(p);
        Somecallback();
        xxxSetWindowStyle(p);
        ThreadUnlock();
    ｝

通过上述代码，可以保证即使callback被执行，p在xxxSetWindowStyle函数执行的时候也不会被释放。

#### 2.3 缓解机制的对抗技术

上一节提到了对象的引用计数，如果对象的引用计数为正，即使执行对象的destroy函数，对象没有真正被释放，仍旧存留在内存中，这种对象被微软开发者称为僵尸（Zombie）对象。一旦僵尸对象的引用计数减少到0它将会消失，但是在此之前它仍旧存在内存中，只是用户层无法访问该对象。

同时为了防止僵尸对象继续存留在内存中，锁的释放函数（ThreadUnlock/ HMAssignmentUnlock）一般会包含对象的释放环节。

对象的Destroy函数还有一个特性就是在释放对象的同时，Destroy函数也会释放对象的子资源，其过程可以简要描述如下。

    
    
    void xxxDestroyWindow(PWND pwnd)
    ｛
        xxxFW_DestroyAllChildren(); // Destroy child windows, if exist!
        if (NULL != pwnd->spmenu)  // If there’s a menu, remove and destroy it.
        ｛
            PMENU tmp = pwnd->spmenu;
            if (HMAssignmentUnlock(&pwnd->spmenu)) // If it’s still locked
            ｛
                DestroyMenu(tmp); // Try destroying it (it can remain a zombie).
    ｝
    ｝
    DereferenceClass(pwnd);
    if (HMMarkObjectDestroy(pwnd)) // Check for zero refs!
        HmFreeObject(pwnd); // Only now free the object and handle pair.
    ｝

DestroyWindow在第一次调用时释放子资源，一旦窗口不再被引用，句柄管理器就会再次完全销毁它，一般情况下，第二次销毁Destroy函数不会在去处理子资源，因为第一次已经释放了所有的子资源。

但是事情往往不是这么简单，事实上即使是一个已经调用过相应Destroy函数释放的僵尸对象，仍然有机会对其本身进行一些更改（回调之后内核代码仍会对对象进行一些操作），我们把这种情况叫做Zombie
Reload，当该僵尸对象由于引用计数为0而被真正释放时，之前的更改操作将会给内核带来一些隐患。

对于如下代码片段：

    
    
    ThreadLock(pwnd);
    xxxSomeCallback(); // Here we can destroy pwnd from user-mode.
    InternalSetTimer(pwnd, ...);  // reuse pwnd without check wether it is destroyed
    ThreadUnlock();
    SomefunctionUseTimer();   //UAF of Timer

我们在用户层回调中对pwnd执行了Destroy函数，然后通过InternalSetTimer为之设置了一个计时器，当ThreadUnlock将pwnd真正释放的时候，计时器也将被释放，那么接下来对计时器的操作将会导致UAF漏洞的产生。

### 3 案例分析

上一节我们讨论了对象的引用计数和锁给对象带来的新的安全隐患，但是真正的挑战在于我们如何确定一段代码中存在漏洞，关键点是确保在unlock函数中释放的对象在运行到有问题的代码时其引用计数应该为1，只有这样我们才能在用户层回调调用其Destroy函数，并通过unlock函数将这个对象真正释放掉（上锁的时候会做+1处理），这也是我们接下来需要讨论的。下面我们通过一个案例来分析漏洞挖掘思路。

#### 3.1 漏洞成因

下图是xxxMnOpenHierarchy函数的代码片段。

![
](https://images.seebug.org/content/images/2020/05/31e6d62d-b88f-48e0-b607-38e42c5bf039.png-w331s)

图中通过xxxCreateWindowEx可以获得一个返回用户层执行callback函数的机会，xxxCreateWindowEx创建的窗口将作为父窗口`*(struct
tagWND **)(**v3 +
8)`（上图红框）的子窗口，如果我们可以通过ThreadUnlock释放父窗口，那么子窗口v32也会被释放，所以当后续的`safe_cast_fnid_to_PMENUWND`函数将v32作为参数执行时就会产生问题，值得注意的是通过回调释放v32是行不通的，如果这样xxxCreateWindowEx将会返回0，无法通过if判断。

这里的问题就在于如何保证父窗口在ThreadUnlock函数执行的时候引用计数为1，因为要执行xxxMnOpenHierarchy函数需要将父窗口关联到一个menu窗口上，此时父窗口和menu窗口将会被一个永久锁锁住，下面我们介绍如何绕过永久锁。

#### 3.2 漏洞挖掘思路

首先我们创建了g_hMenuOwner和g_hNewOwner两个窗口，其中g_hMenuOwner的菜单句柄为hMenu，它也是g_hNewOwner的所有者。

![
](https://images.seebug.org/content/images/2020/05/5c6a3bb2-0dee-434d-905a-50f17509ea6d.png-w331s)

在上述创建过程中内核通过LockPopuMenu函数分别为hMenu和g_hMenuOwner添加 了永久锁，为了达成释放目的，这个永久锁需要被绕过。

![
](https://images.seebug.org/content/images/2020/05/20aa11ad-b9ff-42fe-8e72-b2172fe48bec.png-w331s)
![
](https://images.seebug.org/content/images/2020/05/1f32b100-cec6-4e7f-8870-594bb257efe9.png-w331s)

此时锁和所有者的关系是这样的：

![
](https://images.seebug.org/content/images/2020/05/a8d7470e-28a7-4d92-966a-b26d9a4fa7ce.png-w331s)

接下来我们通过SetWindowsHookEx给窗口添加了WH_CBT钩子，并让窗口进入消息循环中。

![
](https://images.seebug.org/content/images/2020/05/1f316fbf-0fea-40c2-aa8d-042866c69d36.png-w331s)

SendMessage操作为g_hMenuOwner添加一个临时锁，由于后续的所有攻击都是在message的回调中进行，所以对于g_hMenuOwner来说这个临时锁是无法释放的，如果想要构造一个漏洞利用环境首先需要用一些方法来绕过它。

![
](https://images.seebug.org/content/images/2020/05/d24565f4-5c0d-4d1c-9c2c-3559a7459e4d.png-w331s)

现在的情况变成了下图所示：

![
](https://images.seebug.org/content/images/2020/05/d1d6cad8-d16f-4e06-b283-bba85443d6ff.png-w331s)

当消息为HCBT_CREATEWND时，我们第一次到达xxxMNOpenHierarchy函数内部的xxxCreateWindowEx。

![
](https://images.seebug.org/content/images/2020/05/e3d1b0d7-a3fe-4c87-8eca-a0fe9375fb65.png-w331s)

这里可以通过定义关于HCBT_CREATEWND消息的处理得到执行用户层回调代码的机会，这一步的主要目的是为了获取Menu的Wnd。

![ ](https://images.seebug.org/content/images/2020/05/a6a55aaa-fb34-4115-ac1d-05bb3a5930bc.png-w331s)

当接收到的消息为WM_ENTERIDLE时，我们在窗口的消息回调中通过PostMessage下发消息。

![
](https://images.seebug.org/content/images/2020/05/6ac8d4ef-5fb3-4d30-8400-a9eedc91ef6b.png-w331s)

发送消息后，驱动程序来到了xxxMNKeyDown函数内部调用xxxSendMessage处。

![
](https://images.seebug.org/content/images/2020/05/7caac08c-ce2d-46d7-802c-fbda0680f968.png-w331s)

通过WM_NEXTMENU消息的回调函数开始为LPARAM赋值，赋值操作是为了修改hMenu的Owner，这样就可以将Owner的临时锁绕过。

![
](https://images.seebug.org/content/images/2020/05/c4423eaf-1d24-439f-af4c-d1ee4bb48ec2.png-w331s)

此时内核会接到销毁menu的消息，通过用户层的回调函数返回1阻止menu的销毁。

![
](https://images.seebug.org/content/images/2020/05/9e88173a-2687-4e51-b978-df23edaecb9f.png-w331s)

xxxMNKeyDown函数通过UnlockPopupMenu将g_hMenuOwner身上的永久锁被去掉。

![
](https://images.seebug.org/content/images/2020/05/e2ffe654-8312-4925-a537-ad4a3c5ceee9.png-w331s)

取而代之的是g_hNewOwner加上了一个锁，hMenu的Owner也从g_hMenuOwner变 成了g_hNewOwner。

![
](https://images.seebug.org/content/images/2020/05/42912d5e-0708-43be-b432-04535804bf52.png-w331s)

这时，锁的关系变成了：

![
](https://images.seebug.org/content/images/2020/05/353c3ae4-ac2c-4624-a69e-d0aceff0712e.png-w331s)

接下来程序第二次进入到xxxMNOpenHierarchy函数并通过xxxSendMessage发送了消息。

![
](https://images.seebug.org/content/images/2020/05/d9af677a-f189-4800-b6a9-b9dfbd95901c.png-w331s)

此时通过设置WM_INITMENUPOPUP回调来获得用户层执行的机会，WM_INITMENUPOPUP回调函数通过SetWindowsHookEx函数设置了一个新的hook，目的是为了在xxxMnOpenHierarchy函数创建子窗口的时候获得用户层执行权限。

![
](https://images.seebug.org/content/images/2020/05/7e36ee3c-6a61-4947-8f9e-cd2a50ed5c81.png-w331s)

xxxMnOpenHierarchy函数继续向下执行，再次来到xxxCreateWindowEx处。

![ ](https://images.seebug.org/content/images/2020/05/633bfece-165c-43fc-bdc2-85c852f78cf4.png-w331s)

xxxCreateWindowEx调用了刚刚设置的回调函数childMenuHookProc。

![
](https://images.seebug.org/content/images/2020/05/632990d7-4b2d-4150-8cd1-2fb8c9ceb09b.png-w331s)

在回调函数childMenuHookProc中，SendMessage发送了WM_NEXTMENU消息，通过该定义该消息的回调函数再次修改参数LPARAM，这是为了去掉g_hNewOwner身上的永久锁。

![
](https://images.seebug.org/content/images/2020/05/003addfd-15f2-4859-a4d6-45af0c549718.png-w331s)

Menu的Owner关系再次被改变，xxxMNKeyDown通过函数UnlockPopMenu去掉g_hNewOwner身上的永久锁。并将这个锁重新加在了g_hMenuOwner上。

![
](https://images.seebug.org/content/images/2020/05/e52f5a37-6572-447c-b108-559b9dfafd65.png-w331s)

![
](https://images.seebug.org/content/images/2020/05/7f10819a-34c8-4b78-a079-c16d15d43fec.png-w331s)

这个时候，所有的锁都已经转移到了g_hMenuOwner身上，而由于WH_CBT钩子已经被移除，menu将被弃用，g_hNewOwner将把新创建的窗口link到自己身上。这个时候情况变成了下面的样子，g_hNewOwner身上已经没有需要绕过的锁了。

![
](https://images.seebug.org/content/images/2020/05/a1716585-5a15-4da1-80fb-b76e96ef3e18.png-w331s)

接着childMenuHookProc通过SetWindowsHookEx函数又一次设置了回调函数并通过SetWindowLongPtr函数来调用它，回调函数销毁了g_hNewOwner和xxxCreateWindowEx生成的新窗口。

![
](https://images.seebug.org/content/images/2020/05/c2fc34e3-a738-4a51-a2c3-62f4a80d534b.png-w331s)

xxxCreateWindowEx返回的值为ffff871b80239130，这就是xxxCreateWindowEx创建的子窗口。

![
](https://images.seebug.org/content/images/2020/05/dda8ef22-e3d3-4517-bd11-b27d7fbb8020.png-w331s)

接下来就可以通过ThreadUnlock来销毁g_hNewOwner和其新创建的子窗口来得到一个UAF漏洞。

![
](https://images.seebug.org/content/images/2020/05/76a42a24-ac66-4dea-8e9a-58960b489322.png-w331s)

### 4 总结

本文对win32k漏洞挖掘新思路进行了详细解读，其中包括将unlock函数和对象的Destroy函数的特性关联在一起，并把对象的子资源作为攻击目标寻找新的攻击面的漏洞挖掘思路。另外，如何通过对象内部的特性去绕过锁对对象的锁定的思路和技巧，也非常具有借鉴意义。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1198/>

