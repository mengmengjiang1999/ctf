原创xiaoyuer合天智汇

上次我们对主函数分析完成了，那么这次我们对子函数IsAlreadyRun进行分析。

C语言代码

IsAlreadyRun函数的C语言代码如下图所示:

![v2-b7c44e38d21e1976a82185ec9785d326_r.jp](https://pic2.zhimg.com/v2-b7c44e38d21e1976a82185ec9785d326_r.jpg)

下面对其汇编代码进行分析：

![v2-65d329540595c7a9d27f8563093f476c_r.jp](https://pic3.zhimg.com/v2-65d329540595c7a9d27f8563093f476c_r.jpg)

rep stosd之前，同样是入栈操作，我们无需仔细追究，重点关注call函数。

## CreateMutexA函数  

首先根据call ds:CreateMutexA这一条指令便可得知调用了CreateMutex函数（注：CreateMutexA是在Ascii
环境下的，CreateMutexW是unicode环境下的）。

上次我们提到过，在函数调用之前，如果有参数需要传递，需要使用push先将参数从后往前入栈。那么我们来看下call
ds:CreateMutexA前面的三条push指令分别代表什么意思？如果查呢？这就用到非常常用的一个文档--msdn文档，这个文档是微软写的，介绍了Windows API函数，基本上遇到的函数都可以在这里查到，比如CreateMutex这个函数对应的地址是：

https://docs.microsoft.com/zh-cn/windows/win32/api/synchapi/nf-synchapi-createmutexa

从官网可以看到对应的函数解释，详细介绍了这个函数的作用，参数，返回值等：

![v2-bde8dc9a433ba7a115333d9fbf84820f_r.jp](https://pic4.zhimg.com/v2-bde8dc9a433ba7a115333d9fbf84820f_r.jpg)

三个参数lpMutexAttributes,bInitialOwner,lpName中第三个参数lpName的意思是互斥对象的名称，另外两个在此处不展开介绍了，感兴趣的可以去查看msdn文档。现在我们再回过头来仔细看一下ida
Pro给的反汇编代码：

![v2-9db94cdcbbdfb575d2006bff6b309f3f_r.jp](https://pic4.zhimg.com/v2-9db94cdcbbdfb575d2006bff6b309f3f_r.jpg)

是不是和MSDN上的三个参数反过来就对应上了？第一条push指令对应的是lpName这个参数，所以根据ida
pro右边给出的备注，可以得知这个互斥对象的名称是TEST。

上一次也提到过，函数调用完成后，VC中，会使用eax寄存器来保存函数的返回值。在这里也是一样的，call
ds:CreateMutexA的返回值会存入eax寄存器。

## 跳转分析  

我们继续分析下面的汇编代码：

![v2-2c7fb249c3033f8cc6dcce7f814d5e4d_r.jp](https://pic1.zhimg.com/v2-2c7fb249c3033f8cc6dcce7f814d5e4d_r.jpg)

根据call __chkesp可知是调用了栈平衡错误检测函数，这里我们无需理会。之后，

``

`mov [ebp+var_4], eax`

``

`cmp [ebp+var_4], 0`

``

`jz short loc_40107D`

``

mov指令将调用CreateMutexA函数的返回值eax先移动到ebp+var_4的地址上，之后又与0对比，如果两者相等，则跳转到
loc_40107D位置。即，如果CreateMutexA函数的返回值为0，则跳转 loc_40107D位置。

下面分两种情况进行讨论，一种是CreateMutexA函数的返回值为0，一种是不为0。

## CreateMutexA返回值为0  

首先分析CreateMutexA函数的返回值为0的情况：

跳转到这个位置之后，执行xor eax,eax这条指令，上次也提到过xor eax,eax直接会将eax的值设置为0，这是很常见的一种将eax置为0的方式。

![v2-55750c31d869f8fe95389577fb44253b_r.jp](https://pic1.zhimg.com/v2-55750c31d869f8fe95389577fb44253b_r.jpg)

执行完这条指令后，会到loc_40107F位置，根据pop出栈指令、call
__chkesp、retn等指令可知，这是子函数IsAlreadyRun调用完要返回主函数。

![v2-6365f5fde49c745f7163a9c31c58f28b_r.jp](https://pic1.zhimg.com/v2-6365f5fde49c745f7163a9c31c58f28b_r.jpg)

那么，IsAlreadyRun函数的返回值是多少呢？返回值存在eax中，由前面可知，eax在CreateMutexA函数的返回值为0情况下，eax值为0（xor
eax，eax的作用），所以IsAlreadyRun函数的返回值也是0，即IsAlreadyRun返回值为false。

对应的C语言代码:

![v2-f42424d8a226347f1e9c0f1329d2e5de_r.jp](https://pic4.zhimg.com/v2-f42424d8a226347f1e9c0f1329d2e5de_r.jpg)

即，当hMutex = ::CreateMutex(NULL, FALSE,
"TEST")执行后得到的hMutex为0时的场景，子函数IsAlreadyRun直接执行return FALSE；

## CreateMutexA返回值不为0  

之后，分析CreateMutexA函数的返回值不为0的情况：

![v2-1d2f95264c9d37f85a555400b250a4e9_r.jp](https://pic4.zhimg.com/v2-1d2f95264c9d37f85a555400b250a4e9_r.jpg)

此时，由于eax不为0，所以不会跳转到loc_40107D这个位置，而是执行call
ds:GetLastError执行调用GetLastError函数。后面又执行call __chkesp
调用栈平衡错误检查函数，我们在这里无需理会。之后执行cmp
eax,0B7h指令，由于GetLastError函数的返回值存储在eax中，此处其实是在看GetLastError返回值是否等于16进制的B7，对应10进制的183。

如果eax的值不等于183，那么跳转到loc_40107D，之后和上一种情况一样，将eax置为0，然后返回主函数。

如果eax的值等于183，则执行mov eax,1指令，然后跳转到loc_40107F位置，返回主函数。

那么这个183到底代表什么意义呢？通过查询MSDN文档，我们可以得知，它刚好对应常数ERROR_ALREADY_EXISTS。

对比我们写的C语言代码：

![v2-d5a7be4d857fc560e91e789c6d5a1315_r.jp](https://pic3.zhimg.com/v2-d5a7be4d857fc560e91e789c6d5a1315_r.jpg)

也就是GetLastError函数的返回值等于ERROR_ALREADY_EXISTS时，返回true；否则，返回false。

到此为止，整个代码分析完毕。感谢各位耐心的阅读，如有不当之处，欢迎指出。

参考书籍：

《Windows黑客编程技术详解》甘迪文著--北京：人民邮电出版社，2018年12月。

《C++反汇编与逆向分析技术揭秘》钱松林，赵海旭著--北京：机械工业出版社，2011年9月。

《恶意代码分析实战》 （美）Michael Sikorski / Andrew Honig 著，诸葛建伟，姜辉，张光凯译 --北京：电子工业出版社，2014年4月，原书名： Practical Malware Analysis: The Hands-On Guide to
Dissecting Malicious Software。

《汇编语言》王爽 著--2版，北京：清华大学出版社，2008年4月。

推荐实验：实验：逆向破解-CrackMe系列

[课程:逆向破解-CrackMe系列(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=C172.19.104.182016031814360300001)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

