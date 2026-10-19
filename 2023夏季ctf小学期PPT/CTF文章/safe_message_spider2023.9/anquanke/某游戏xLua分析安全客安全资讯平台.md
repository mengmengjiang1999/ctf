# 某游戏xLua分析

阅读量 **260428**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-02-25 10:00:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t016ce7252b3e77729f.jpg)

以前做过很多同类CTF题，闲得无聊，正好在分析样本的时候遇到了xLua，实战一下功能的分析，总结一下关于Lua的相关知识。

## 静态分析

懒得注入然后dump进行opcode比对，直接静态分析。

![](https://p3.ssl.qhimg.com/t01301170c15d94fccb.png)

差异：Lua变为Mua，😗

![](https://p3.ssl.qhimg.com/t01a065ebce8d750546.png)

版本53格式1，是xLua的差异，打开了LUAC_COMPATIBLE_FORMAT，因此格式是1，并且去掉了size_t的校验

![](https://p5.ssl.qhimg.com/t01106a36d758968f67.png)

![](https://p0.ssl.qhimg.com/t012d2fef3ab66e2ffc.png)

![](https://p1.ssl.qhimg.com/t0144e124cad5db22c8.png)

并且根据是否为Mua，checkHeader有所不同

![](https://p1.ssl.qhimg.com/t013780ab6841ca46a5.png)

![](https://p3.ssl.qhimg.com/t010a191136111fe158.png)

![](https://p0.ssl.qhimg.com/t01215005f9bc1da2d5.png)

LoadState增加Mua的信息

    
    
    struct LoadState
    {
      struct lua_State *L;
      struct ZIO *Z;
      const char *name;
      uint8_t isMua;
      uint32_t mua;
    };
    

LoadFunction也是对isMua进行了判断，如果是Mua的话，会先LoadConstant再LoadCode，调换了顺序。其余似乎没有差别

![](https://p3.ssl.qhimg.com/t016a57298c12ca3337.png)

字节码不出意料被打乱了顺序，下面开始分析分析对应关系，首先可以搜索local解决部分对应关系

![](https://p0.ssl.qhimg.com/t01dae63e8f23c4e993.png)

    
    
    OP_MOVE = 21,
    OP_LOADK = 22,
    OP_GETUPVAL = 26,
    OP_LOADKX = 28,
    OP_SELF = 29,
    OP_GETTABUP = 36,
    OP_GETTABLE = 41,
    

![](https://p4.ssl.qhimg.com/t01a078f77da30f22cc.png)

    
    
    OP_LOADNIL = 38,
    OP_TFORCALL = 39,
    OP_CALL = 44,
    OP_TAILCALL = 32,
    OP_JMP = 17
    

其实也可以通过这个表看出一些端倪，这里是一定按OpCode顺序存放的

![](https://p3.ssl.qhimg.com/t01a32e06138ed1b932.png)

可以猜想有一段（数学运算）是整体平移的，貌似以前CTF也做过这样的

![](https://p1.ssl.qhimg.com/t014c47154e2ef75bf7.png)

继续找对应关系，比如相同的可以缩小范围

![](https://p5.ssl.qhimg.com/t0177c57332f858b0ba.png)

![](https://p1.ssl.qhimg.com/t01a63eadb5a464f17e.png)

以此类推，得出对应关系。之后就可以成功反编译了，不过看结果还套了额外一层东西，继续研究。

![](https://p5.ssl.qhimg.com/t0181017aea9400e024.png)

## 动态分析

最后还是得注入看看sb函数是什么东西，首先分析这个CreateLuaTable，从资源中提取出来

![](https://p3.ssl.qhimg.com/t019cf96beedca33319.png)

提取了半天，也没找到什么有用的东西，决定试试玩玩他的lua，发现他拒绝编译文本，只能运行预编译的，因此需要用替换好OP的程序编译一份出来。

![](https://p2.ssl.qhimg.com/t01b5c4714d9ac36f1d.png)

然后手动调用DoString，这里可以用Base64创建数组。

![](https://p0.ssl.qhimg.com/t0161941a5df8ac35b2.png)

成了，说明可以用，接下来看看那个解密函数是什么东西。

![](https://p3.ssl.qhimg.com/t01d1e4d6d33cc1d936.png)

不给dump，看看是为什么，似乎是因为不是lua函数而是CS端或者是native的？继续看看CustomLoader

![](https://p4.ssl.qhimg.com/t018eb0ab27419fd465.png)

经过测试应该是在这几个Init里赋值的

![](https://p1.ssl.qhimg.com/t01729c730e292982f7.png)

Hook xlua的setglobal，看看是在哪里赋值的

![](https://p4.ssl.qhimg.com/t01200e41e0f6c62476.png)

竟然是在xLua的Init之前，打印堆栈

![](https://p4.ssl.qhimg.com/t01af12ad9de792e690.png)

定位到xlua.dll的这里，有混淆代码

![](https://p5.ssl.qhimg.com/t01ab959c02db5a930b.png)

是在lua_newstate里进行初始化的

![](https://p3.ssl.qhimg.com/t01c262e7741cb937b7.png)

先看看汇编，实在不行解混淆，这儿是能看到把这个函数注册到sb_1184180438

![](https://p5.ssl.qhimg.com/t01f2f0aa5db38c52b5.png)

不行，还是要解混淆，初步思路是检测这个特征，然后用angr符号执行替换完事，写脚本开干

![](https://p2.ssl.qhimg.com/t01f08678a19be6d757.png)

好家伙，一万多个，慢慢爆吧

![](https://p1.ssl.qhimg.com/t019fca99e87941d0e7.png)

修复结束之后，继续看，发现还有一堆这样的，结合上下文似乎应该是条件跳转，用dl的值判断然后跳到两个地址位置

![](https://p2.ssl.qhimg.com/t01ae2972d8bf1b212a.png)

先看一眼，这里应该是解密字符串，解密之后就是sb函数名了应该

![](https://p3.ssl.qhimg.com/t012ee7eec73f0f573b.png)

![](https://p0.ssl.qhimg.com/t01e3af3dc8e3d7e8d8.png)

继续修复，这里要修复条件，稍微复杂了一点点

![](https://p5.ssl.qhimg.com/t01eba9f6eb1d3c1fc7.png)

还有一些零碎的地方，先不修了，先看看sb

![](https://p2.ssl.qhimg.com/t01dfb6ba67463c8a98.png)

很多sub_180024390都是耍人玩的，层层switch_case最后只是简单的功能，我们只看关键代码，似乎是相邻异或，从最后一位开始，最后一位由0xA3开始，那么解密看看。

![](https://p3.ssl.qhimg.com/t0113fb5142f46623a3.png)

再反汇编一下，成功

![](https://p4.ssl.qhimg.com/t01e92d34503d3f9640.png)

## 总结

Lua主要就是OpCode
Swap，可以手动爆也可以用模板脚本编译然后对照，但实际上如本文的样本，把编译功能关了就只能手动爆了。其他的反混淆好像和Lua也没啥关系，但也是这个样本里的东西，就顺便提一下吧，另外这种多层的switch-case函数混淆貌似也没法修复，有没有懂哥欢迎评论。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **k1ee** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231798](/post/id/231798)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [双倍活动](/tag/双倍活动)
  * [xLua](/tag/xLua)

 **+1** __7赞

 __收藏

![](https://p1.ssl.qhimg.com/t017393a3827d79f55a.png) k1ee

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

