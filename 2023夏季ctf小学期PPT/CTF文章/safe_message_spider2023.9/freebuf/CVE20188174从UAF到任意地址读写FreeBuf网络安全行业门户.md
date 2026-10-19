***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ** ***本文原创作者：elli0tn0phacker，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

##  **0x00** **背景**

 **2018年5月9日，360发表Blog “Analysis of CVE-2018-8174 VBScript 0day and APT actor
related toOffice targeted attack” 揭露了利用“双杀”0day发起的APT攻击，其中使用的漏洞就是IE vbscript
0day：CVE-2018-8174，不久该样本就在互联网被公布。由于360的Blog并没有对漏洞原理和任意地址读写的利用方法详细介绍，且原始样本混淆严重，笔者对样本进行了简化，重点说明该漏洞的原理和如何利用该漏洞实现任意地址读写，希望帮助大家更好的理解这个漏洞利用程序。**

##  **0x01** **漏洞原理**

poc如下：

![](https://image.3001.net/images/20180526/15272664888863.png!small)

poc中首先定义了两个数组array_a和array_b，并声明了一个类Trigger，Trigger中重载了析构函数Class_Terminate，在UAF函数中，创建了一个Trigger的实例赋值给数组array_a
(1)，并通过Erase
array_a清空array_a中的元素，这时候在析构array_a中的元素的时候会触发脚本中Class_Terminate的调用，在Class_Terminate中增加了一个array_b(0)对Trigger实例的引用（Trigger实例引用计数+1），再通过array_a
(1)= 1删除array_a (1)
对Trigger实例的引用（Trigger实例引用计数-1）来平衡引用计数，这时候Trigger实例会被释放，但是array_b(0)仍然保留了这个Trigger实例的引用，从而array_b(0)指向了被释放的Trigger实例的内存，最终在TriggerVuln中通过b(0)
= 0访问未分配内存触发漏洞。开启hpa和ust观察漏洞现场：

![](https://image.3001.net/images/20180526/15272664974812.png!small)

显然eax已经在vbscript!VbsErase的调用栈中被释放了，vbscript!VbsErase即对应了脚本中的Erase，而eax正是被VBScriptClass::Release函数释放的VBScriptClass对象也就是脚本中的Trigger实例。这里看下VBScriptClass::Release的逻辑：

![](https://image.3001.net/images/20180526/15272665159683.png!small)

VBScriptClass::Release中首先对VBScriptClass的引用计数-1（&VBScriptClass+0x4），如果引用计数=0则调用VBScriptClass::TerminateClass，调用VBScriptClass::TerminateClass时因为在脚本中重载了Class_Terminate函数，所以获得了一次脚本执行的机会，这里就可以在释放VBScriptClass的内存前将即将释放的VBScriptClass内存地址保存脚本控制的变量中(Set
array_b(0) =array_a(1))，并通过array_a (1) = 1平衡引用计数，最终释放内存。

1） Set array_a(1) = New Trigger：此时VBScriptClass引用计数=2

![](https://image.3001.net/images/20180526/15272673632165.png!small)

2） Erase array_a返回后：

![](https://image.3001.net/images/20180526/15272666169106.png!small)

此时Trigger指向的内存已经被释放，但是array_b(0)仍然指向这块被释放的内存，形成悬挂指针。

##  0x02 漏洞利用

UAF漏洞利用的关键是如何使用这个悬挂指针操作内存。通过分析漏洞原理知道array_b(0)指向被释放的VBScriptClass的内存（大小为0x30）,这时候可以用一个VBScriptClass占位（这里称为MyClass2），接着利用悬挂指针array_b(0)释放这块内存再用另外一个VBScriptClass占位（这里称为MyClass1），此时MyClass1和MyClass2将同时指向这块内存。此外VBScriptClass在+0x08处是保存了VBScriptClass成员变量和成员函数NameTbl对象（大小为0x88）的指针，NameTbl对象从+0x48开始保存成员变量和成员函数的指针：

![](https://image.3001.net/images/20180526/15272666986870.png!small)可以理解为下图，通过UAF
MyClass1 和MyClass2都指向VBScriptClass的内存，同时MyClass1
MyClass2的变量也都保存在NameTbl中，如果MyClass1
MyClass2的变量在NameTbl内存是错位排列的，那么就有可能通过控制其中一个对象变量的值来修改另一个对象变量的属性，从而实现类型混淆：

![](https://image.3001.net/images/20180526/15272667238295.png!small)简化后的任意地址读写poc：

![](https://image.3001.net/images/20180526/15272667883967.png!small)![](https://image.3001.net/images/20180526/1527266791151.png!small)

首先在UAF函数中创建了一些VBScriptClass对象占据系统堆碎片为后面UAF准备，然通过触发漏洞获得指向已释放的Trigger对象内存的array_b，接着通过“Set
mycls2 = New MyClass2”，用MyClass2占位释放的内存，此时array_b的7个元素和MyClass2都指向这块内存。

在InitObjects函数的“mycls2.SetProp(myconf)”中会触发Confusion类的Public Default Property
Get P函数调用，并将返回值“P=174088534690791e-324”保存在MyClass2的成员变量mem中。在PublicDefault
Property Get
P函数调用中，再次利用悬挂指针array_b(i)释放了MyClass2的内存，然后用MyClass1占位并将字符串FAKESAFEARRAY赋值给MyClass1的成员变量mem，由于MyClass2依然指向这块内存，因此MyClass2.mem
= MyClass1.mem = FAKESAFEARRAY。

注意到之前Public Default Property Get
P函数调用的返回值“P=174088534690791e-324”会保存在MyClass2的成员变量mem中，但是此时MyClass2内存已经被释放，返回值“P=174088534690791e-324”仍然会保存在原来的MyClass2的mem指向的内存地址，poc中的被释放的MyClass2的mem和MyClass1的mem有0xC字节的错位，而“P=174088534690791e-324”对应的VARIANT在内存中的值为“00000005
00000000 00000000
0000200C”，从而利用错位的“0000200c”将BSTR混淆为VARIANT|ARRAY，而FAKESAFEARRAY的内容正好是一个起始地址为0x00000000长度为0x7FFFFFFF每个元素占1Byte的数组，最终实现任意地址读写。

1）Set mycls2 = New MyClass2后MyClass2的内存布局：

![](https://image.3001.net/images/20180526/15272668637128.png!small)2）PublicDefault
Property Get P中MyClass2被释放，MyClass1占位：

![](https://image.3001.net/images/20180526/15272669497278.png!small)

可以看到MyClass1.mem(0x020066C6C)和释放前的MyClass2.mem(0x020066C60)相差0xC Byte

3）PublicDefault Property Get 返回后通过“P=174088534690791e-324”修改释放前的
MyClass2.mem为“00000005 00000000 00000000 0000200c”实现类型混淆：

![](https://image.3001.net/images/20180526/15272669673219.png!small)

最终myClass2.mem获得任意地址读写权限。

同理BSTR也可以被混淆成Long类型用来泄露shellcode的内存地址：

![](https://image.3001.net/images/20180526/15272669843684.png!small)![](https://image.3001.net/images/20180526/1527266986911.png!small)

关于对象地址泄露和shellcode执行，可以参考360那篇Blog，当然DVE也是可行的，不再详述。

 ***本文原创作者：elli0tn0phacker，本文属FreeBuf原创奖励计划，未经许可禁止转载**

