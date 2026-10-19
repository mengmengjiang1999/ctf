# 《Chrome V8源码》28.分析substring源码和隐式约定

阅读量 **343596**

|评论 **2**

发布时间 : 2021-11-26 10:30:45

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t015fb3ab27d5c2aaba.png)

## 1 摘要

本篇文章是Builtin专题的第四篇，主要分析`substring`的源码。`substring`有两种实现方法，一种采用CSA实现，另一种采用Runtime实现。本文讲解CSA实现的`substring`方法以及V8对字符串长度和类型的隐式约定。

## 2 substring的CSA实现

提取字符串中介于两个指定下标之间的子字符串时，V8优先使用CSA实现的substring方法，源码如下：

    
    
    1.  TF_BUILTIN(StringPrototypeSubstring, CodeStubAssembler) {
    2.    if (block0.is_used()) {//省略了很多代码.......................................
    3.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 33);
    4.      tmp5 = FromConstexpr6String18ATconstexpr_string_156(state_, "String.prototype.substring");
    5.      tmp6 = CodeStubAssembler(state_).ToThisString(compiler::TNode<Context>{tmp3}, compiler::TNode<Object>{tmp4}, compiler::TNode<String>{tmp5});
    6.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 34);
    7.      tmp7 = CodeStubAssembler(state_).LoadStringLengthAsSmi(compiler::TNode<String>{tmp6});
    8.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 37);
    9.      tmp8 = FromConstexpr8ATintptr17ATconstexpr_int31_150(state_, 0);
    10.      tmp9 = CodeStubAssembler(state_).GetArgumentValue(TorqueStructArguments{compiler::TNode<RawPtrT>{tmp0}, compiler::TNode<RawPtrT>{tmp1}, compiler::TNode<IntPtrT>{tmp2}}, compiler::TNode<IntPtrT>{tmp8});
    11.      tmp10 = ToSmiBetweenZeroAnd_343(state_, compiler::TNode<Context>{tmp3}, compiler::TNode<Object>{tmp9}, compiler::TNode<Smi>{tmp7});
    12.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 40);
    13.      tmp11 = FromConstexpr8ATintptr17ATconstexpr_int31_150(state_, 1);
    14.      tmp12 = CodeStubAssembler(state_).GetArgumentValue(TorqueStructArguments{compiler::TNode<RawPtrT>{tmp0}, compiler::TNode<RawPtrT>{tmp1}, compiler::TNode<IntPtrT>{tmp2}}, compiler::TNode<IntPtrT>{tmp11});
    15.      tmp13 = Undefined_64(state_);
    16.      tmp14 = CodeStubAssembler(state_).TaggedEqual(compiler::TNode<Object>{tmp12}, compiler::TNode<HeapObject>{tmp13});
    17.      ca_.Branch(tmp14, &block1, &block2, tmp0, tmp1, tmp2, tmp3, tmp4, tmp6, tmp7, tmp10);
    18.    }
    19.    if (block1.is_used()) {
    20.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 41);
    21.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 40);
    22.      ca_.Goto(&block4, tmp15, tmp16, tmp17, tmp18, tmp19, tmp20, tmp21, tmp22, tmp21);
    23.    }
    24.    if (block2.is_used()) {
    25.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 42);
    26.      tmp31 = FromConstexpr8ATintptr17ATconstexpr_int31_150(state_, 1);
    27.      tmp32 = CodeStubAssembler(state_).GetArgumentValue(TorqueStructArguments{compiler::TNode<RawPtrT>{tmp23}, compiler::TNode<RawPtrT>{tmp24}, compiler::TNode<IntPtrT>{tmp25}}, compiler::TNode<IntPtrT>{tmp31});
    28.      tmp33 = ToSmiBetweenZeroAnd_343(state_, compiler::TNode<Context>{tmp26}, compiler::TNode<Object>{tmp32}, compiler::TNode<Smi>{tmp29});
    29.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 40);
    30.      ca_.Goto(&block3, tmp23, tmp24, tmp25, tmp26, tmp27, tmp28, tmp29, tmp30, tmp33);
    31.    }
    32.    if (block4.is_used()) {
    33.      ca_.Goto(&block3, tmp34, tmp35, tmp36, tmp37, tmp38, tmp39, tmp40, tmp41, tmp42);
    34.    }
    35.    if (block3.is_used()) {
    36.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 43);
    37.      tmp52 = CodeStubAssembler(state_).SmiLessThan(compiler::TNode<Smi>{tmp51}, compiler::TNode<Smi>{tmp50});
    38.      ca_.Branch(tmp52, &block5, &block6, tmp43, tmp44, tmp45, tmp46, tmp47, tmp48, tmp49, tmp50, tmp51);
    39.    }
    40.    if (block5.is_used()) {
    41.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 44);
    42.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 45);
    43.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 46);
    44.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 43);
    45.      ca_.Goto(&block6, tmp53, tmp54, tmp55, tmp56, tmp57, tmp58, tmp59, tmp61, tmp60);
    46.    }
    47.    if (block6.is_used()) {
    48.      ca_.SetSourcePosition("../../../src/builtins/string-substring.tq", 48);
    49.      tmp71 = CodeStubAssembler(state_).SmiUntag(compiler::TNode<Smi>{tmp69});
    50.      tmp72 = CodeStubAssembler(state_).SmiUntag(compiler::TNode<Smi>{tmp70});
    51.      tmp73 = CodeStubAssembler(state_).SubString(compiler::TNode<String>{tmp67}, compiler::TNode<IntPtrT>{tmp71}, compiler::TNode<IntPtrT>{tmp72});
    52.      arguments.PopAndReturn(tmp73);
    53.    }
    54.  }
    

上述代码由`string-substring.tq`指导编译器生成，其位置在`V8\v8\src\out\default\gen\torque-generated\src\builtins`目录下，这意味它在编译V8过程中生成。  
 **（1）** 第3行代码设置源码，源码来自`string-substring.tq`文件的第33行，见图1；  
 **（2）** `codeStubAssembler(state_).ToThisString()`（第5行代码）把this转成字串符；  
第6行代码设置源码，见图1；`CodeStubAssembler(state_).LoadStringLengthAsSmi()`（第7行代码）计算字符串长度，参数tmp6的值是第5行代码的执行结果。由于第6、7行代码与第3、5行的编码风格一样，所以可以通过对`string-substring.tq`的逐行分析看懂CodeStubAssembler。

![](https://p3.ssl.qhimg.com/t0169a628886c988a05.png)

下面说明substring源码中的其它关键功能：  
 **（1）** `ca_.Goto()`跳转到标签位置，它的第一参数是标签，源码如下：

    
    
      template <class... T, class... Args>
      void Goto(CodeAssemblerParameterizedLabel<T...>* label, Args... args) {
        label->AddInputs(args...);
        Goto(label->plain_label());
      }
    

**（2）**`ca_.Bind()`设置标签，源码如下：

    
    
      template <class... T>
      void Bind(CodeAssemblerParameterizedLabel<T...>* label, TNode<T>*... phis) {
        Bind(label->plain_label());
        label->CreatePhis(phis...);
      }
    

**（3）**`ca_.Branch()`分支跳转，源码如下：

    
    
      template <class... T, class... Args>
      void Branch(TNode<BoolT> condition,
                  CodeAssemblerParameterizedLabel<T...>* if_true,
                  CodeAssemblerParameterizedLabel<T...>* if_false, Args... args) {
        if_true->AddInputs(args...);
        if_false->AddInputs(args...);
        Branch(condition, if_true->plain_label(), if_false->plain_label());
      }
    

其中参数`condition`是条件，参数`if_true、if_false`是跳转标签。  
 **（4）** `LoadStringLengthAsSmi()`和`SmiUntag()`是`CodeStubAssembler`的成员方法。  
总结`TF_BUILTIN(StringPrototypeSubstring, CodeStubAssembler)`的功能为如下三点：  
 **（1）** 把this转换为字符串并获取长度length；  
 **（2）** 判断substring的长度（sublen）是否小于length；  
 **（3）** 调用`CodeStubAssembler.SubString`完成substring操作。  
`CodeStubAssembler.SubString`的源码如下：

    
    
    1.  TNode<String> CodeStubAssembler::SubString(TNode<String> string,
    2.                                            TNode<IntPtrT> from,
    3.                                            TNode<IntPtrT> to) {
    4.  //省略很多
    5.    Label external_string(this);
    6.    {
    7.      if (FLAG_string_slices) {
    8.        Label next(this);
    9.        GotoIf(IntPtrLessThan(substr_length,
    10.                              IntPtrConstant(SlicedString::kMinLength)),
    11.               &next);
    12.        Counters* counters = isolate()->counters();
    13.        IncrementCounter(counters->sub_string_native(), 1);
    14.        Label one_byte_slice(this), two_byte_slice(this);
    15.        Branch(IsOneByteStringInstanceType(to_direct.instance_type()),
    16.               &one_byte_slice, &two_byte_slice);
    17.        BIND(&one_byte_slice);
    18.        {
    19.          var_result = AllocateSlicedOneByteString(
    20.              Unsigned(TruncateIntPtrToInt32(substr_length)), direct_string,
    21.              SmiTag(offset));
    22.          Goto(&end);
    23.        }
    24.        BIND(&two_byte_slice);
    25.        {
    26.          var_result = AllocateSlicedTwoByteString(
    27.              Unsigned(TruncateIntPtrToInt32(substr_length)), direct_string,
    28.              SmiTag(offset));
    29.          Goto(&end);
    30.        }
    31.        BIND(&next);
    32.      }
    33.      GotoIf(to_direct.is_external(), &external_string);
    34.      var_result = AllocAndCopyStringCharacters(direct_string, instance_type,
    35.                                                offset, substr_length);
    36.      Counters* counters = isolate()->counters();
    37.      IncrementCounter(counters->sub_string_native(), 1);
    38.      Goto(&end);
    39.    }
    40.    BIND(&external_string);
    41.    {
    42.      TNode<RawPtrT> const fake_sequential_string =
    43.          to_direct.PointerToString(&runtime);
    44.      var_result = AllocAndCopyStringCharacters(
    45.          fake_sequential_string, instance_type, offset, substr_length);
    46.      Counters* counters = isolate()->counters();
    47.      IncrementCounter(counters->sub_string_native(), 1);
    48.      Goto(&end);
    49.    }
    50.    BIND(&empty);
    51.    {
    52.    }
    53.    BIND(&single_char);
    54.    {
    55.      TNode<Int32T> char_code = StringCharCodeAt(string, from);
    56.      var_result = StringFromSingleCharCode(char_code);
    57.      Goto(&end);
    58.    }
    59.    BIND(&original_string_or_invalid_length);
    60.    {
    61.  //省略很多
    62.    }
    63.    BIND(&runtime);
    64.    {
    65.      var_result =
    66.          CAST(CallRuntime(Runtime::kStringSubstring, NoContextConstant(), string,
    67.                           SmiTag(from), SmiTag(to)));
    68.      Goto(&end);
    69.    }
    70.    BIND(&end);
    71.    return var_result.value();
    72.  }
    

FLAG_string_slices（上述第7行代码）是切片的使能标记，它定义在`flag-definitions.h`中，源码如下：

    
    
    // Flags for data representation optimizations
    DEFINE_BOOL_READONLY(string_slices, true, "use string slices")
    

第9行代码`GotoIf()`计算substr_length的值，如果小于13则跳转到标签next。  
第15行代码`Branch()`判断字符串是单字节字符还是双字节字符。  
第17-23行、24-30行分别处理单字节、双字节两种情况，稍后讲解。  
第40-49行代码`BIND(&external_string)`操作外部字符串，外部字符串指的是不在V8
heap中的字符串，如从DOM中引用的字符串就是外部字符串。操作外部字符串时使用Runtime方法。  
第53-58行代码：当sublength=1时，调用`StringCharCodeAt()`完成相应的操作并返回结果。  
第63-70行代码：当字符串为外部字符串时，调用`Runtime_StringSubstring`完成相应的操作并返回结果。  
在V8中，`slice`生成新字符串时，如果新字符串长度大于SlicedString::kMinLength则不申请新内存，而是使用开始指针和结束指针引用原字符串。以单字节字串符为例讲解slice方法，源码如下：

    
    
    1.  TNode<String> CodeStubAssembler::AllocateSlicedOneByteString(
    2.      TNode<Uint32T> length, TNode<String> parent, TNode<Smi> offset) {
    3.    return AllocateSlicedString(RootIndex::kSlicedOneByteStringMap, length,
    4.                                parent, offset);
    5.  }
    6.  //分隔线..............................
    7.  TNode<String> CodeStubAssembler::AllocateSlicedString(RootIndex map_root_index,
    8.                                                        TNode<Uint32T> length,
    9.                                                        TNode<String> parent,
    10.                                                        TNode<Smi> offset) {
    11.    DCHECK(map_root_index == RootIndex::kSlicedOneByteStringMap ||
    12.           map_root_index == RootIndex::kSlicedStringMap);
    13.    TNode<HeapObject> result = Allocate(SlicedString::kSize);
    14.    DCHECK(RootsTable::IsImmortalImmovable(map_root_index));
    15.    StoreMapNoWriteBarrier(result, map_root_index);
    16.    StoreObjectFieldNoWriteBarrier(result, SlicedString::kHashFieldOffset,
    17.                                   Int32Constant(String::kEmptyHashField),
    18.                                   MachineRepresentation::kWord32);
    19.    StoreObjectFieldNoWriteBarrier(result, SlicedString::kLengthOffset, length,
    20.                                   MachineRepresentation::kWord32);
    21.    StoreObjectFieldNoWriteBarrier(result, SlicedString::kParentOffset, parent,
    22.                                   MachineRepresentation::kTagged);
    23.    StoreObjectFieldNoWriteBarrier(result, SlicedString::kOffsetOffset, offset,
    24.                                   MachineRepresentation::kTagged);
    25.    return CAST(result);
    26.  }
    

上述代码中`AllocateSlicedOneByteString()`是入口函数，调用`AllocateSlicedString()`函数。第13行代码创建`SlicedString`对象（result）；第16-24行代码把sublength、父亲字符串基址和偏移量存入result中，slice完毕。  
 **技术总结**  
 **（1）** string-substring.tq是开发者手写的Builtin源码，string-substring-tq-csa.cc和.h是Tq生成的Builtin源码；  
 **（2）**
SlicedString::kMinLength的值是13，news=substring(start,stop)，news的长度小于13时用copy机制，大于13时用引用机制；  
 **（3）** 因为使用了Runtime_substring方法，所以外部字符串的操作效率低。  
好了，今天到这里，下次见。

**个人能力有限，有不足与纰漏，欢迎批评指正**  
 **微信：qq9123013 备注：v8交流 邮箱：[v8blink@outlook.com](mailto:v8blink@outlook.com)**

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **灰豆** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/260386](/post/id/260386)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [浏览器](/tag/浏览器)
  * [Web安全](/tag/Web安全)
  * [Javascript](/tag/Javascript)
  * [Chrome](/tag/Chrome)
  * [v8](/tag/v8)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t011ad06ea77f9a618e.png) 灰豆

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

