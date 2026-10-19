# 某DEX_VMP安全分析与还原

阅读量 **224865**

发布时间 : 2021-12-15 14:30:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01fc711a3431f0e46d.jpg)

## 目录:

> 一.思路整理  
>  二.某VMP入口特征  
>  三.定位VMP字节码  
>  四.分割VMP字节码  
>  五.还原为SMALI  
>  六.某VMP攻击面总结 && 启示  
>  七.深入VMP还原的一些问题  
>  八.调试与工具总结

## 一.思路整理

###  还原VMP需要哪些铺垫?

> (1)定位VMP字节码  
>  (2)分割VMP字节码  
>  (3)还原成SMALI

**(1)为什么要找VMP字节码的位置?**

> 因为如果目标方法的字节码地址,都找不到,还原也就没法展开了.

![](https://p2.ssl.qhimg.com/t01d54c17de98df4082.png)

**(2)为什么要分割VMP字节码?**

> 如果要反汇编成smali,  
>  起码要知道这条smali对应的字节码一共几个字节.
>
> 在确定一条指令占几个字节后,  
>  还要知道这几个字节中,  
>  谁是操作码,谁是操作数.

![](https://p4.ssl.qhimg.com/t018da0057fa3a227df.png)

**(3)还原为SMALI**

> 有了前两步铺垫,最终我们可以解读一条完整的smali的含义.

![](https://p4.ssl.qhimg.com/t018676e985055bb954.png)

## 二.某安卓VMP入口特征(2021.8月样本)

> 跳板方法

![](https://p5.ssl.qhimg.com/t0197f8574a18a7a1db.png)

> 进入native后的参数处理逻辑

![](https://p2.ssl.qhimg.com/t0158d91c15664cceb6.png)

> 为了处理不同类型的返回值, 定义了多个jni方法

![](https://p1.ssl.qhimg.com/t01afa39bf34f44bd5e.png)

> 对应jni函数入口指令情况

![](https://p5.ssl.qhimg.com/t013527a90498db7307.png)

## 三.定位VMP字节码

###  逻辑

![](https://p5.ssl.qhimg.com/t01c49a9ce57118745f.png)

> 根据上述逻辑,则一定存在函数F,向F输入index可得到对应codeitem_addr  
>  F(index) == codeitem_addr
>
> 我们看一下这个函数,从index到codeitem_addr的过程  
>  (0x2dce->0xcac85880)

![](https://p5.ssl.qhimg.com/t01324c6eb0cdbbba29.png)

![](https://p5.ssl.qhimg.com/t01e047183152ed9eaf.png)

###  如何在十几万数量级的汇编中定位到这段代码的?

> 通过Trace记录REG信息,  
>  用到了两个关键数值,0x2dce(index)与0xcac85880(codeitems),  
>  标记两个数值出现的中间区间即可.

![](https://p4.ssl.qhimg.com/t01957070c6763d8afe.png)

![](https://p2.ssl.qhimg.com/t011ea03bc08954efa1.png)

###  展开上面的定位方式的两个前提条件:

> 我们已经有了关键数据0x2dce,但还需要知道另一个提前条件,  
>  即codeitem是0xcac85880,所以这个信息是从哪得知的?  
>  这里是本章的关键.

###  如何分析出codeitem的地址是0xcac85880?

> (1) 已知明文  
>  (2) 沙箱日志获取切入点  
>  (3) JNI参数回溯  
>  (4) 内存访问统计

**(1)已知明文**

> 目标APP内很多的onCreate()方法,其内部普遍调用了,  
>  NBSTraceEngine.startTracing();以及super.onCreate()

![](https://p5.ssl.qhimg.com/t01c04dc08b2adede1b.png)

> 我们选一个被vmp保护了的onCreate()作为分析目标, ZxWebViewActivity.onCreate()  
>

**(2) 沙箱日志获取切入点**

> ①
> ZxWebViewActivity.onCreate内必定存在NBSTraceEngine.startTracing();以及super.onCreate()  
>  ② startTracing为静态方法,会被编译器编译为invoke-static  
>  ③ super.onCreate()为超类调用,会被编译器编译为invoke-super  
>  ④我们猜测vmp对invoke-static模拟实现借助了JNI函数,  
>  所以我们触发ZxWebViewActivity.onCreate()执行,截取其调用序列,效果如下:

![](https://p3.ssl.qhimg.com/t01237c28dc561357a3.png)

> 大致逻辑为

![](https://p4.ssl.qhimg.com/t01e59852558eba525f.png)

![](https://p4.ssl.qhimg.com/t01a8ad1ce81367906a.png)

**(3) JNI参数startTracing来源回溯**

> 我们在trace中找到这条GetStaticMethodID()的出现位置,  
>  然后作为起点向上展开回溯,希望找到其参数”startTracing”的最早出处,  
>  如果有自动化的脚本和条件可进行污点分析,由于逻辑不是很复杂,这里人工回溯完成.

![](https://p4.ssl.qhimg.com/t011b91cfc4429511e8.png)

> 具体过程省略……  
>  在trace中对参数”startTracing”来源进行一番回溯,  
>  最终发现了一个起到决定性作用的偏移值0x000081de.  
>  可以简单理解成,它以base+0x000081de的形式确立的参数”startTracing”.
>
> 结论:  
>  如果0x000081de是那个起到决定性意义的数值,  
>  那么毫无疑问0x000081de来自codeitem.
>
> 在trace中找到0x81de的出现位置,  
>  发现它来自于内存位置0xcac858a8.

![](https://p3.ssl.qhimg.com/t01b994657e0660febb.png)

**(4) 内存访问统计**

> 0x81de来自0xcac858a8,  
>  由于这个地址可能是codeitem,  
>  因此我们检索一下,trace中对这片内存区域的访问情况  
>  0xcac858a8取前5个高位,忽略后3个地位,即检索对0xcac85???的访问

![](https://p5.ssl.qhimg.com/t01a3a3ca0f8b6dff9e.png)

> 找到19条指令, 而对0xcac85???的访问,最早的第一条指令,出现在编号5691的位置,  
>  对应的内存地址为0xcac85890,说明这里是ZxWebViewActivity.onCreate()第一条字节码.
>
> 由于codeitem第一条字节码之前0x10个字节还存在一些固定内容,  
>  所以0xcac85890-0x10取得codeitem地址0xcac85880,  
>  即codeitem的地址是0xcac85880

![](https://p2.ssl.qhimg.com/t01e01095fb78966ca5.png)

![](https://p5.ssl.qhimg.com/t014578881e6eabd13f.png)

## 四.分割VMP字节码

![](https://p2.ssl.qhimg.com/t0135ea25099af11987.png)

> 现在已经有了某厂vmp codeitems全部内容,  
>  但是还没法反汇编成smali,
>
> 因为还不知道,  
>  第一条指令一共占几个字节,  
>  第二条指令一共占几个字节,  
>  依次……
>
> dalvik指令是不等长,  
>  反汇编成smali的话,  
>  起码要知道这条smali对应的字节码一共几个字节  
>  在知道了每条指令占几个字节后,  
>  还要知道这几个字节中,  
>  谁是操作码,谁是操作数.

###  通过观察codeitem的内存段的读取情况,可以达到这个目的

![](https://p5.ssl.qhimg.com/t010a76420d8a33b569.png)

![](https://p3.ssl.qhimg.com/t011eab621265748e0f.png)

###  如何快速区分出操作码和操作数?

> 一般opcode后面会有一个EOR解密指令,  
>  以及一串类似定位handle的CMP指令操作,  
>  而operand没有,这就为区分opcode和operand提供了特征依据.  
>

![](https://p3.ssl.qhimg.com/t018ca3d60d7a82deab.png)

###  opcode解密逻辑?

> 由eor指令向上回key出现的位置,  
>  即可确定key的来源,  
>  以及解密逻辑.
>
> 大致逻辑:  
>  off1 = sub( codeitem当前指令地址, codeitem基址 )  
>  off2 = lsl( off1, 1)  
>  key = load( base + off2 )  
>  de_opcode = xor(en_opcode, key)

## 五.VMP字节码还原为SMALI

> 1 标准dalvik指令反汇编过程  
>  2 VMP指令反汇编过程  
>  3 还原VMP所有指令需要什么?  
>  4 没有opcode对照表时,如何展开还原?

###  1 标准dalvik指令反汇编过程

![](https://p4.ssl.qhimg.com/t01275f0ec42fbfc6f6.png)

![](https://p3.ssl.qhimg.com/t01907ec8f14061fc4e.png)

###  2 VMP指令反汇编过程

> 由于使用了已知明文条件作为切入点,  
>  已知分析目标ZxWebViewActivity.onCreate()中,  
>  必定会调用startTracing()方法,  
>  即必定存在invoke-static {v0}, method[@00da6f](https://github.com/00da6f
> "@00da6f") // …startTracing
>
> 又通过上面的分析得知关键值81de出现在这条invoke-static中,  
>  且充当操作数的角色,那么按照我们按照标准invoke-static反汇编规则进行解析,  
>  就可以得到结论.

![](https://p4.ssl.qhimg.com/t0116a53404b9b9bb24.png)

![](https://p2.ssl.qhimg.com/t01e2ecf04333b6d9e2.png)

![](https://p0.ssl.qhimg.com/t01a6b224830fee198b.png)

> VMP指令由标准指令基础上修改而来,有哪些异同?

![](https://p0.ssl.qhimg.com/t015a0e146bfc48afc3.png)

###  3 还原VMP所有指令需要什么?

![](https://p3.ssl.qhimg.com/t012001681e5321c48e.png)

###  4 没有opcode对照表时如何展开还原?

> (1)接口猜测法  
>  (2)参数推导法  
>  (3)标准dalvik指令格式的信息利用  
>  (4)人肉逆向法(略)

**(1)接口猜测法**

> method相关的invoke系列指令,可以通过JNI执行情况猜测.  
>  Field相关的get set系列指令,也可以通过JNI执行情况猜测.

![](https://p5.ssl.qhimg.com/t010a9108825a7b9ab7.png)

**(2)参数推导法**

> 方法调用前,会先准备参数,  
>  通常是声明类型的指令,  
>  可以很大程度缩小猜测的候选指令范围.

![](https://p3.ssl.qhimg.com/t0175d34eb0896a6b83.png)

**(3)标准dalvik指令格式的信息利用**

> 由于vmp指令是由dalvik标准指令略微修改/变异而来,  
>  只做了较小的改动,仍然保留了BIT位分布特征这样信息.  
>  在做还原时,可以利用这些信息,一定程度缩小候选范围.  
> <https://source.android.com/devices/tech/dalvik/instruction-formats>  
> <https://source.android.com/devices/tech/dalvik/dalvik-> bytecode#instructions>  
>

## 六.某VMP攻击面总结 && 启示

> 1 分析路径  
>  2 攻击面总结 && 启示

###  1 分析路径

![](https://p1.ssl.qhimg.com/t01beb1b7edc5511057.png)

###  2 攻击面总结 && 启示

> (1) 被VMP的方法内部存在已知明文指令.  
>  (2) VMP的实现高度依赖JNI函数,通过HOOK拿到其调用信息,是非常有效的切入点与突破口.  
>  (3) codeitems的连续性,集中存储的特性,通过内存访问统计最终被发现.  
>  (4) vmp指令由标准dalvik指令基础上略改而来,整体仍然保留了很多可用信息,  
>  对于一些内部逻辑比较简单的方法,可以以较小成本还原.

**(1) 被VMP的方法内部存在已知明文指令.**

![](https://p3.ssl.qhimg.com/t0126fb03e0071e2d9c.png)

**(2) VMP的实现高度依赖JNI函数,通过HOOK拿到其调用信息,是非常有效的切入点与突破口.**

![](https://p3.ssl.qhimg.com/t0190824bdd1706c246.png)

**(3) codeitems的连续性,集中存储的特性,通过内存访问统计最终被发现.**

![](https://p0.ssl.qhimg.com/t011c574051cf97351e.png)

**(4)某vmp指令由标准dalvik指令基础上略改而来,整体仍然保留了很多可用信息**

![](https://p4.ssl.qhimg.com/t017f0158396c633443.png)

## 七.深入VMP还原的一些问题

> 略

## 八.调试与工具总结

###  核心问题:

> 获取程序完整的执行&&数据信息 (trace).

###  目前公开的主流的获取trace的方案:

> 1 GDB调试  
>  2 FridaStalker编译执行  
>  3 脱机unicorn模拟执行

###  公开的主流的获取trace的方案的弊端和缺陷:

> 1 IDA / GDB:  
>  速度极慢,且会遭遇反调试
>
> 2 FridaStalker  
>  不支持arm指令的thumb模式,且BUG多,  
>  遭遇vmp.so中的花指令时,基本无法正常使用.
>
> 3 PC上脱机unicorn模拟执行  
>  vmp.so中存在大量jni call和system
> call,需要手动实现它们,unicorn才能完成运行,过程繁琐,并且可能遭遇脱机unicorn检测.

###  基于以上问题的解决方案尝试:

> 实现原始APP进程环境 && 原始context中,  
>  通过unicorn构造虚拟化CPU,  
>  执行目标function,获得trace,  
>  方案无已知检测和对抗手段,无脑过一切反调试.  
>

###  基于trace进行离线分析:

> 1 trace形态可视化  
>  文本 / json / 数据库 / EXCEL可视化表格 / 动态CFG图
>
> 2 基本的分析  
>  地址含义解析 调用符号识别
>
> 3 程序分析  
>  污点分析 相似性分析等..

![](https://p2.ssl.qhimg.com/t01ffa9dbf94a4552fe.png)

![](https://p5.ssl.qhimg.com/t012701f8a6ed809cfb.png)

![](https://p0.ssl.qhimg.com/t012fe36d1074c236fe.png)

![](https://p2.ssl.qhimg.com/t0161b2615808cb40bf.png)

## 团队信息

###  Vulpecker Team

隶属于360公司信息安全部，致力于手机 APP
及IOT安全，同时专注于移动安全研究，团队定制了公司内部产品安全开发规范，在提高工作效率的同时也为开发者提供了便捷的安全测试平台。

同时团队高度活跃在谷歌、三星、华为等各大手机厂商的致谢名单中，挖掘的漏洞屡次获得CVE编号及致谢，在保证360产品安全的前提下，团队不断对外输出安全技术，为移动互联网安全贡献一份力量。

![](https://p4.ssl.qhimg.com/t017a2efbfa3e3b7344.png)

###  作者

<https://github.com/acbocai>

![](https://p4.ssl.qhimg.com/t013c9759bc8b110dfe.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360 Vulpecker Team** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/263197](/post/id/263197)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhimg.com/t01cc916865a9b71b8f.png) 360 Vulpecker Team

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

