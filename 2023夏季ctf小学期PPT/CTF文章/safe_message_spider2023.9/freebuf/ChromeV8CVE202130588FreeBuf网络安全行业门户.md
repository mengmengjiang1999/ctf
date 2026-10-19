![](https://image.3001.net/images/20220303/1646285286_622051e64528a17f4e3c6.png!small)issue（https://bugs.chromium.org/p/chromium/issues/detail?id=1195650），这是去年发布的1天，我们来看一下详细情况。

##  **漏洞分析**

调试 Poc 以及观察涡轮增压器，我主要是在不合适的地方发现插件无法到达的节点，导致运行时中断。

![](https://image.3001.net/images/20220303/1646285331_622052136493d35d04ff4.png!small)

而这里（https://docs.google.com/presentation/d/1sOEF4MlF7LeO7uq-uThJSulJlTh--wgLeaVibsbb3tc/edit#slide=id.g549957988_0383）有写作。

![](https://image.3001.net/images/20220303/1646285355_6220522b9ad92de7e5f8d.png!small)这个unreachable是和dead
node相关的，我们把惊人的发现在简化的Lowing阶段，因为通过查看turbolizer以及查看问题界面的返回信息错误在这个阶段。

![](https://image.3001.net/images/20220303/1646285378_622052420a5f59543eba5.png!small)![](https://image.3001.net/images/20220303/1646285390_6220524eabdd896bd9ab3.png!small)所以我先把突突SimplifiedLower中之后在SpeculativeToNumber插入Unreachable的部分。

    
    
    template <Phase T>
      void VisitNode(Node* node, Truncation truncation,
                     SimplifiedLowering* lowering) {
        tick_counter_->TickAndMaybeEnterSafepoint();
    
        // Unconditionally eliminate unused pure nodes (only relevant if there's
        // a pure operation in between two effectful ones, where the last one
        // is unused).
        // Note: We must not do this for constants, as they are cached and we
        // would thus kill the cached {node} during lowering (i.e. replace all
        // uses with Dead), but at that point some node lowering might have
        // already taken the constant {node} from the cache (while it was not
        // yet killed) and we would afterwards replace that use with Dead as well.
        if (node->op()->ValueInputCount() > 0 &&
            node->op()->HasProperty(Operator::kPure) && truncation.IsUnused()) {
          return VisitUnused<T>(node);   //调用的这个函数里面打了patch
        }
    
        if (lower<T>()) InsertUnreachableIfNecessary<T>(node);   //这里打了patch，且InsertUnreachableIfNecessary里也打了patch，从SpeculativeToNumber变为unreachable就是在这个函数内
    
        switch (node->opcode()) {
            [ ... ]
          case IrOpcode::kSpeculativeToNumber: {
            NumberOperationParameters const& p =
                NumberOperationParametersOf(node->op());
            switch (p.hint()) {
              case NumberOperationHint::kSignedSmall:
              case NumberOperationHint::kSignedSmallInputs:
                VisitUnop<T>(node,
                             CheckedUseInfoAsWord32FromHint(
                                 p.hint(), kDistinguishZeros, p.feedback()),
                             MachineRepresentation::kWord32, Type::Signed32());
                break;
              case NumberOperationHint::kNumber:
              case NumberOperationHint::kNumberOrBoolean:
              case NumberOperationHint::kNumberOrOddball:   //这里会将其换为float64
                VisitUnop<T>(
                    node, CheckedUseInfoAsFloat64FromHint(p.hint(), p.feedback()),
                    MachineRepresentation::kFloat64);
                break;
            }
            if (lower<T>()) DeferReplacement(node, node->InputAt(0));
            return;
          }

另通过观察patch发现和DeferReplacement也有关系，有patch。

![](https://image.3001.net/images/20220303/1646285458_622052921c1b565a11a62.png!small)

之所以比较麻烦是因为在运行时直接--trace-representation看不到我想要的过程，所以只能一点点调试。

从调试结果来看，是先插入的unreachable，后经下面转的checkedTaggedToFloat64，从节点顺序来看也是如此，不过这就无法作为插入unreachable的原因了，所以要看patch的其他部分。

经调试发现也不会先进入VisitUnused，此外，在插入unreachable之前，不会到达patch的任何其他段代码处，所以目前锁定问题出现在。

    
    
    diff --git a/src/compiler/simplified-lowering.cc b/src/compiler/simplified-lowering.cc
    index 23e0006..a71e627 100644
    --- a/src/compiler/simplified-lowering.cc
    +++ b/src/compiler/simplified-lowering.cc
    @@ -1960,7 +1975,32 @@
           return VisitUnused<T>(node);
         }
    
    -    if (lower<T>()) InsertUnreachableIfNecessary<T>(node);
    +    if (lower<T>()) {
    +      // Kill non-effectful operations that have a None-type input and are thus
    +      // dead code. Otherwise we might end up lowering the operation in a way,
    +      // e.g. by replacing it with a constant, that cuts the dependency on a
    +      // deopting operation (the producer of the None type), possibly resulting
    +      // in a nonsense schedule.
    +      if (node->op()->EffectOutputCount() == 0 &&
    +          node->op()->ControlOutputCount() == 0 &&
    +          node->opcode() != IrOpcode::kDeadValue &&
    +          node->opcode() != IrOpcode::kStateValues &&
    +          node->opcode() != IrOpcode::kFrameState &&
    +          node->opcode() != IrOpcode::kPhi) {
    +        for (int i = 0; i < node->op()->ValueInputCount(); i++) {
    +          Node* input = node->InputAt(i);
    +          if (TypeOf(input).IsNone()) {
    +            MachineRepresentation rep = GetInfo(node)->representation();
    +            DeferReplacement(
    +                node,
    +                graph()->NewNode(jsgraph_->common()->DeadValue(rep), input));
    +            return;
    +          }
    +        }
    +      } else {
    +        InsertUnreachableIfNecessary<T>(node);
    +      }
    +    }
    

可以看到是多了一个判断条件，也就是说，原本不该进入InsertUnreachableIfNecessary的情况进入了，所以也就是在不该插入的时候插入了，这个特殊的情况，可以用各种技巧构造出来，作为比较，拿InsertUnreachableIfNecessary来看。

    
    
    template <>
    void RepresentationSelector::InsertUnreachableIfNecessary<LOWER>(Node* node) {
      // If the node is effectful and it produces an impossible value, then we
      // insert Unreachable node after it.
      if (node->op()->ValueOutputCount() > 0 &&
          node->op()->EffectOutputCount() > 0 &&
          node->opcode() != IrOpcode::kUnreachable && TypeOf(node).IsNone()) {
        Node* control = (node->op()->ControlOutputCount() == 0)
                            ? NodeProperties::GetControlInput(node, 0)
                            : NodeProperties::FindSuccessfulControlProjection(node);
    
        Node* unreachable =
            graph()->NewNode(common()->Unreachable(), node, control);
    
        // Insert unreachable node and replace all the effect uses of the {node}
        // with the new unreachable node.
        for (Edge edge : node->use_edges()) {
          if (!NodeProperties::IsEffectEdge(edge)) continue;
          // Make sure to not overwrite the unreachable node's input. That would
          // create a cycle.
          if (edge.from() == unreachable) continue;
          // Avoid messing up the exceptional path.
          if (edge.from()->opcode() == IrOpcode::kIfException) {
            DCHECK(!node->op()->HasProperty(Operator::kNoThrow));
            DCHECK_EQ(NodeProperties::GetControlInput(edge.from()), node);
            continue;
          }
    
          edge.UpdateTo(unreachable);
        }
      }
    }

可以看到，曾经能走入InsertUnreachableIfNecessary并成功插入unreach节点的node，不满足diff中新加的判断，也就是，原本能向内完成插入的节点还会往后走，那么再仔细看下patch，可以看到，是对另外的一些节点，主动将其变为DeadValue，所以猜测是有些节点未及时变为deadvalue而导致的问题，是哪些节点呢，是pure
dead operation，除了kDeadValue，kStateValues，kFrameState，kPhi之外的operation。

关于dead code，其实含义很广泛，可以说是不可能执行的代码，或者更恰当的是不可能执行的分支，都是代表这段代码可以被消除的含义，我们可以看下dead-code-elimination.h中如何消除dead value的注释。

    
    
    // Propagates {Dead} control and {DeadValue} values through the graph and
    // thereby removes dead code.
    // We detect dead values based on types, replacing uses of nodes with
    // {Type::None()} with {DeadValue}. A pure node (other than a phi) using
    // {DeadValue} is replaced by {DeadValue}. When {DeadValue} hits the effect
    // chain, a crashing {Unreachable} node is inserted and the rest of the effect
    // chain is collapsed. We wait for the {EffectControlLinearizer} to connect
    // {Unreachable} nodes to the graph end, since this is much easier if there is
    // no floating control.
    // {DeadValue} has an input, which has to have {Type::None()}. This input is
    // important to maintain the dependency on the cause of the unreachable code.
    // {Unreachable} has a value output and {Type::None()} so it can be used by
    // {DeadValue}.
    // {DeadValue} nodes track a {MachineRepresentation} so they can be lowered to a
    // value-producing node. {DeadValue} has the runtime semantics of crashing and
    // behaves like a constant of its representation so it can be used in gap moves.
    // Since phi nodes are the only remaining use of {DeadValue}, this
    // representation is only adjusted for uses by phi nodes.
    // In contrast to {DeadValue}, {Dead} can never remain in the graph.

可以看到，dead value是不该在effect chain中的，因为如此会导致unreachable节点的插入effect
chain中，从而导致crash，effect chain可以理解为对于执行流中的有先后顺序操作的限制顺序。

这个漏洞patch方法是主动将一些节点先行转为dead value，所以可以预料到只要能先把非effect chain上的一些节点转为dead
value，就不会造成运行到unreachable的情况，说到这里，我们先要看为什么在这会插入unreachable。

![](https://image.3001.net/images/20220303/1646285588_62205314c44e0904de3a6.png!small)这是在InsertUnreachableIfNecessary内部，而调用这个函数可以说没什么判断，但是在函数内有许多判断需要满足，直观来说就是。

    
    
    // If the node is effectful and it produces an impossible value, then we
      // insert Unreachable node after it.
      if (node->op()->ValueOutputCount() > 0 &&
          node->op()->EffectOutputCount() > 0 &&
          node->opcode() != IrOpcode::kUnreachable && TypeOf(node).IsNone()) {

![](https://image.3001.net/images/20220303/1646285625_622053399aa86a195adae.png!small)再结合turbolizer图（TFEscapeAnalysis）。

![](https://image.3001.net/images/20220303/1646285666_6220536230bc0aeeef715.png!small)

那么满足判断之后就会走入下面插入unreachable的部分。

再看poc

    
    
    (function() {
      function foo(a) {
        let y = Math.min(Infinity ? [] : Infinity, -0) / 0;
        if (a) y = 1.1;
        return y ? 1 : 0;
      }
      %PrepareFunctionForOptimization(foo);
      print(foo(false));
      %OptimizeFunctionOnNextCall(foo);
      print(foo(false));
    })();

其中[]、''之类的是SpeculativeToNumber节点的必须，#74的heapconstant就是这个。

我们看修复之后的版本：

![](https://image.3001.net/images/20220303/1646285721_622053998410c007470d2.png!small)很明显的是虽然还是会生成unreachable以及checkedTaggedToFloat64，但是也可以看到生成了很多的DeadValue，也就是虽然生成Unreachable的分支判断依然可以运行，但是在此之外多出了一些生成dead
value的过程，patch也正是改动的这一点，在遍历节点时，主动检查是否应转为dead value。

![](https://image.3001.net/images/20220303/1646285738_622053aacd317eb44703d.png!small)我们看一下最终生成代码的差别。

![](https://image.3001.net/images/20220303/1646285753_622053b9c2914ae34c2fd.png!small)![](https://image.3001.net/images/20220303/1646285764_622053c4c11108ca83428.png!small)

右边是patch后的版本。

为了辅助定位触发的int3是哪条代码里的，我修改了一下。

    
    
    (function() {
      function foo(a) {
        let y = Math.min(Infinity ? [] : Infinity, -0) / 0;
        console.log("hi");
        if (a) y = 1.1;
        return y ? 1 : 0;
      }
      %PrepareFunctionForOptimization(foo);
      print(foo(false));
      %OptimizeFunctionOnNextCall(foo);
      print(foo(false));
    })();

![](https://image.3001.net/images/20220303/1646285806_622053ee48c13918d503d.png!small)

显然是在let y = Math.min(Infinity ? [] : Infinity, -0) /
0;中直接break，也就是说确实是插入的那个unreachable起了作用，后发现是其旁边的一个unreachable起了作用。

另外经过一些尝试，我发现patch达到的效果和poc中将除操作删去效果一样，都是在后面加了几个dead value，（min操作没有必要，转为dead
value）然后后面的操作就比较正常了。

最终经过阅读最后形成的代码，我发现对于不成功触发的情况，（因为显然是return全变为throw了），最后的结果要么是走到unreachable，要么是deopt，因为unreachable走不到（正常情况下），所以每次都会deopt，从而走正确的流程，下面是patch后的v8运行poc，加了输出deopt的参数。

![](https://image.3001.net/images/20220303/1646285864_62205428d34942ead9a3d.png!small)而未patch的运行poc。

![](https://image.3001.net/images/20220303/1646285881_622054397563b229e0f07.png!small)

看完未patch版本最终生成的代码后，其整体流程其实也是要么走向unreachbale，要么走向deopt，但是大部分情况都会走向unreachable，且看运行结果也发现是直接走到unreachable了，所以最终导致的结果应该是，本该走向deopt的情况，走向了unreachable。

基本上二者从EffectLinearization开始出现差别。

![](https://image.3001.net/images/20220303/1646285902_6220544e931fc1e4a163e.png!small)

是因为，左侧patch前的是在和##104节点差距离较远的一个dead value生成的##190
unreachable，右侧patch后的是由和##104算是有点关系的几个dead value生成的unreachable。

生成unreachable在这里。

    
    
    Node* EffectControlLinearizer::LowerDeadValue(Node* node) {
      Node* input = NodeProperties::GetValueInput(node, 0);
      if (input->opcode() != IrOpcode::kUnreachable) {
        // There is no fundamental reason not to connect to end here, except it
        // integrates into the way the graph is constructed in a simpler way at
        // this point.
        // TODO(jgruber): Connect to end here as well.
        Node* unreachable = __ UnreachableWithoutConnectToEnd();
        NodeProperties::ReplaceValueInput(node, unreachable, 0);   //dead value上会插入unreachable
      }
      return gasm()->AddNode(node);
    }

造成的结果就是在最后，##104旁的unreachable有无与effectPhi有直接联系。

![](https://image.3001.net/images/20220303/1646285947_6220547bb570f20f0c04d.png!small)

而这个effectPhi又是与一个DeoptimizeUnless节点直接关联的，也就是本来会把unreachable安排在deopt后面的，然而因为那些dead
avlue没有在正确的地方生成，导致代码组织出了错误，使得从dead
value衍生出来的unreachable节点与上面的一个DeoptmizeUnless断了联系，从而越过Deopt直接到达Unreachable，然后crash。

在未patch版中虽然simplifiedLowering阶段也把除0操作变为了dead
value，但是还是保留的float64Min节点（原NumberMin）。

![](https://image.3001.net/images/20220303/1646285971_6220549325c27e3144583.png!small)导致此处dead
value（div0）早一步被消除。

![](https://image.3001.net/images/20220303/1646285993_622054a90f8d8a21ef5e8.png!small)

可以看到左侧（patch前），#107 dead value已经没了，右侧倒是还有div0转的dead value。

对应的numberMin变Float64Min逻辑在。

    
    
    case IrOpcode::kNumberMin: {
            // It is safe to use the feedback types for left and right hand side
            // here, since we can only narrow those types and thus we can only
            // promise a more specific truncation.
            // For NumberMin we generally propagate whether the truncation
            // identifies zeros to the inputs, and we choose to ignore minus
            // zero in those cases.
            Type const lhs_type = TypeOf(node->InputAt(0));
            Type const rhs_type = TypeOf(node->InputAt(1));
    [ ... ]
            } else {
              VisitBinop<T>(node,
                            UseInfo::TruncatingFloat64(truncation.identify_zeros()),
                            MachineRepresentation::kFloat64);
              if (lower<T>()) {
                // If the left hand side is not NaN, and the right hand side
                // is not NaN (or -0 if the difference between the zeros is
                // observed), we can do a simple floating point comparison here.
                if (lhs_type.Is(Type::OrderedNumber()) &&
                    rhs_type.Is(truncation.IdentifiesZeroAndMinusZero()
                                    ? Type::OrderedNumber()
                                    : Type::PlainNumber())) {
                  lowering->DoMin(node,
                                  lowering->machine()->Float64LessThanOrEqual(),
                                  MachineRepresentation::kFloat64);
                } else {
                  ChangeOp(node, Float64Op(node));
                }
              }
            }
            return;
          }

对于这次情况就是NumberMin的左是SpeculativeToNumber，右是-0，所以会变为Float64Min，然而patch后的版本会在走到这里之前，先对其进行判断，转为Dead
Value。

![](https://image.3001.net/images/20220303/1646286035_622054d3d28670b0bcd70.png!small)

    
    
    # 对应这里的判断
    +      if (node->op()->EffectOutputCount() == 0 &&
    +          node->op()->ControlOutputCount() == 0 &&
    +          node->opcode() != IrOpcode::kDeadValue &&
    +          node->opcode() != IrOpcode::kStateValues &&
    +          node->opcode() != IrOpcode::kFrameState &&
    +          node->opcode() != IrOpcode::kPhi) {

从而导致没有在靠近#104 unreachable位置衍生出unreachable（因为这里没有一个dead
value），倒是在上面有一个原本应当放在div0化成的dead value后面的一个#110 dead
value衍生了unreachable，在右侧对应#109，也就是原本。![](https://image.3001.net/images/20220303/1646286065_622054f18d5dbb13f7f8d.png!small)

这里的#109，但是这个节点因为前面的关系原因，没有联系到下面#104 unreachable这里，所以造成了上面说的最终结果。

虽然没有找到合适的利用链但是不排除能成功利用的情况，在这里（https://bugs.chromium.org/p/chromium/issues/detail?id=1195650#c31），有半任意地址读的poc，但是离构造出越界数组，仍有一段路要走，另外还有一个poc能把本该返回false的改成true，稍加改变就能使得本该true的被turbofan优化成了false，但是此版本消除check
bound已经不再能使用（也不一定），并且那个利用参杂着另外一个漏洞点，在作者用的这个版本（https://crrev.com/b2ae9951d4a12b996532022959f44a0cd10184ec）上才能成功。

但是也不是完全没有思路，我们可以看到他是越过DeoptimizeUnless直接走到本该在DeoptimizeUnless后面的unreachable，所以我们如果可以把此处的unreachable换为别的类型混淆利用方式，比如用其他类型对象实现越界读写，那么我们就能造出一个越界数组来，但是这只是理论方面的想法。

