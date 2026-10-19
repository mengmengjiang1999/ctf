# Chakra OP_NewScObjArray Type Confusion远程代码执行漏洞分析与利用

阅读量 **251043**

|评论 **2**

发布时间 : 2018-09-04 14:30:32

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0113296b189609b298.jpg)

## 1.漏洞描述

漏洞编号：无  
影响版本：Chakra <= 1.10.0

此漏洞是我去年11月份发现的，在今年的七月微软的发布版本中被修掉。该漏洞成因在于：Interpreter在执行OP_NewScObjArray操作码指令时处理不当，在OP_NewScObjArray_Impl函数内有一个结构体之间的强制转换，导致了类型混淆，成功利用该漏洞可导致远程代码执行。

## 2.测试环境

    
    
    Windows 10 x64 + Microsoft Edge 42.17074.1002.0
    

## 3.漏洞分析

###
[](http://blogs.360.cn/post/Microsoft%20Edge%20Chakra%20OP_NewScObjArray%20Type%20Confusion%20%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90%E4%B8%8E%E5%88%A9%E7%94%A8.html#toc-68e)3.1
漏洞基本信息

开启页堆保护后(gflags.exe -I MicrosoftEdgeCP.exe +hpa +ust)，用Microsoft
Edge浏览器加载poc.html时的异常信息如下：

    
    
    0:017> r
    rax=00000033438faf18 rbx=00000000000fefa0 rcx=000001aee1be3020
    rdx=00007ff88f40c698 rsi=000001a6c2bcd960 rdi=000001aee1be3020
    rip=00007ff88ee5d224 rsp=00000033438faea0 rbp=000000000000fefa
     r8=000001aee1ce2050  r9=00007ff88f40c698 r10=000001a6c2b38568
    r11=000001aee33001b0 r12=000001aee1be3020 r13=000001aec87103c0
    r14=000001aee1be3b29 r15=00000000000009e9
    iopl=0         nv up ei pl nz na po nc
    cs=0033  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00010206
    chakra!Js::DynamicProfileInfo::RecordCallSiteInfo+0x54:
    00007ff88ee5d224 450fb74802      movzx   r9d,word ptr [r8+2] ds:000001aee1ce2052=????
    0:017> kb
    RetAddr           : Args to Child                                                           : Call Site
    00 00007ff88ed5ca46 : 000001aee1be3020 000001aee33001b0 000001a6c2b3fefa 00007ff88f40c698 : chakra!Js::DynamicProfileInfo::RecordCallSiteInfo+0x54
    01 00007ff88ed5b061 : 000001aec8708580 00000033438faff0 000001aec87103c0 000001a6c2b3fefa : chakra!Js::ProfilingHelpers::ProfiledNewScObjArray+0xa6
    02 00007ff88efe8518 : 00000033438fb280 000001aee3af7c85 00000033438fb0b0 000001aee3af7c84 : chakra!Js::InterpreterStackFrame::OP_NewScObjArray_Impl<Js::OpLayoutT_CallI<Js::LayoutSizePolicy<1> >,0>+0x81
    03 00007ff88ee25e1b : 00000033438fb280 000001aee3af7c84 00000033438fb0b0 0000000000000000 : chakra!Windows::Data::Text::IUnicodeCharactersStatics::vcall'{144}'+0x1f618
    04 00007ff88ee25c55 : 00000033438fb280 0000000000000000 0000000000000001 00007ff88ed5c496 : chakra!Js::InterpreterStackFrame::ProcessUnprofiled+0x9b
    05 00007ff88ee24704 : 00000033438fb280 00000033438fb280 00000033438fb280 0000000000000001 : chakra!Js::InterpreterStackFrame::Process+0x175
    06 00007ff88ee26cdb : 00000033438fb280 000001aee3af7c68 000001aee3af7c68 0000000000000000 : chakra!Js::InterpreterStackFrame::OP_TryCatch+0x64
    07 00007ff88ee25c55 : 00000033438fb280 0000000000000000 0000000000000000 0000000000000000 : chakra!Js::InterpreterStackFrame::ProcessUnprofiled+0xf5b
    08 00007ff88ee1913d : 00000033438fb280 00000033438fb280 00000033438fbc80 000001a6c2b28760 : chakra!Js::InterpreterStackFrame::Process+0x175
    09 00007ff88ee189de : 000001aec87103c0 00000033438fbe60 000001aee1c70fba 00000033438fbe78 : chakra!Js::InterpreterStackFrame::InterpreterHelper+0x49d
    0a 000001aee1c70fba : 00000033438fbeb0 0000000000000001 00000033438fbea0 00000033438fc288 : chakra!Js::InterpreterStackFrame::InterpreterThunk+0x4e
    ....
    

从上面的栈帧可知是调用RecordCallSiteInfo函数时内部发生了访问异常。

### 3.2 漏洞成因

**3.2.1 pc对应的代码**

源代码如下：

    
    
    void DynamicProfileInfo::RecordCallSiteInfo(FunctionBody* functionBody, ProfileId callSiteId, FunctionInfo* calleeFunctionInfo, JavascriptFunction* calleeFunction, uint actualArgCount, bool isConstructorCall, InlineCacheIndex ldFldInlineCacheId)
    {
    ...
        if (!callSiteInfo[callSiteId].isPolymorphic) //out of bound read 
        {
            Js::SourceId oldSourceId = callSiteInfo[callSiteId].u.functionData.sourceId;
            if (oldSourceId == InvalidSourceId)
            {
                return;
            }
    ...
    

反汇编代码如下：

    
    
    void **__fastcall Js::DynamicProfileInfo::RecordCallSiteInfo(Js::DynamicProfileInfo *this, struct Js::FunctionBody *a2, unsigned __int16 a3, struct Js::FunctionInfo *a4, struct Js::JavascriptFunction *a5, unsigned __int16 a6, bool a7, unsigned int a8)
    {
      ...
      unsigned __int16 v12; // bp@1
      signed __int64 v13; // rbx@3
      signed __int64 v14; // r8@3
      __int16 v15; // r9@3
      ... 
      v9 = a2;
      v10 = this;
      v11 = a4;
      v12 = a3; // a3 <=> callSiteId 
      ...
      v13 =0x10 * a3;
      v14 = v13 + *((_QWORD *)this + 1);//<=>callSiteInfo
      v15 = *(_WORD *)(v14 + 2);//out of bound read 
      if ( v15 >= 0 )
      {
        v16 = *(_DWORD *)(v14 + 8);
        LODWORD(v17) = -4;
        if ( v16 == -4 )
          return result;
      ...
    

根据 3.1 步骤的漏洞异常信息时，rbp=0x000000000000fefa，及其上面的源代码与汇编代码的对比发现，callSiteId = a3 =
v12 = bp = 0xfefa。

    
    
    0:017> dq rcx  + 0x8
    000001aee1be3028  000001aee1be30b0 0000000000000000
    000001aee1be3038  0000000000000000 0000000000000000
    000001aee1be3048  0000000000000000 0000000000000000
    000001aee1be3058  000001aee1be3140 0000000000000000
    000001aee1be3068  000001aee1bf313f 0000000000000000
    000001aee1be3078  0000000000000000 0000000000000000
    000001aee1be3088  0000000000000000 0000000000000009
    000001aee1be3098  0000000000000000 ffffffff00000000
    

此时:

    
    
    callSiteInfo = * ((QWORD * )this + 1) => poi(rcx + 0x8) = 0x000001aee1be30b0
    r8 = (callSiteInfo + callSiteId  *  0x10) = 0x000001aee1be30b0 + 0xfefa  *  0x10 = 0x000001aee1ce2050 
    
    
    
    0:017> dd 000001aee1be30b0
    000001aee1be30b0  00000009 00000000 ffffffff 00000000
    000001aee1be30c0  00000009 00000000 ffffffff 00000000
    000001aee1be30d0  00000009 00000000 ffffffff 00000000
    000001aee1be30e0  00000009 00000000 ffffffff 00000000
    000001aee1be30f0  00000009 00000000 ffffffff 00000000
    000001aee1be3100  00000009 00000000 ffffffff 00000000
    000001aee1be3110  00000009 00000000 ffffffff 00000000
    000001aee1be3120  00000009 00000000 ffffffff 00000000
    

通过dd 0x000001aee1be30b0 命令查看callSiteInfo内容是可以访问的，初步判定崩溃是因callSiteId越界导致的内存越界读。

[](http://blogs.360.cn/post/Microsoft%20Edge%20Chakra%20OP_NewScObjArray%20Type%20Confusion%20%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90%E4%B8%8E%E5%88%A9%E7%94%A8.html#toc-f06)**3.2.2
创建callSiteInfo对象的代码**

源代码如下：

    
    
    DynamicProfileInfo* DynamicProfileInfo::New(Recycler* recycler, FunctionBody* functionBody, bool persistsAcrossScriptContexts)
        {
            size_t totalAlloc = 0;
            Allocation batch[] =
            {
                { (uint)offsetof(DynamicProfileInfo, callSiteInfo), functionBody->GetProfiledCallSiteCount() * sizeof(CallSiteInfo) },// 计算分配callSiteInfo对象的内存大小
     ...
             };
            for (uint i = 0; i < _countof(batch); i++)
            {
               totalAlloc += batch[i].size;//数组元素内存分配之和
            }
            info = RecyclerNewPlusZ(recycler, totalAlloc, DynamicProfileInfo, functionBody);// 总的内存分配长度为：totalAlloc + sizeof(DynamicProfileInfo)
              BYTE* current = (BYTE*)info + sizeof(DynamicProfileInfo);
                      }
            }
            for (uint i = 0; i < _countof(batch); i++)
            {
                if (batch[i].size > 0)
                {
                    Field(BYTE*)* field = (Field(BYTE*)*)(((BYTE*)info + batch[i].offset));
                    *field = current;
                    current += batch[i].size;
                }
            }
            info->Initialize(functionBody);
            return info;
    

反汇编代码如下：

    
    
    char *__fastcall Js::DynamicProfileInfo::New(struct Memory::Recycler *a1, struct Js::FunctionBody *a2)
    {
     ...
      size_t v26; // rdx@16
      char *v27; // rbx@18
    ...
      else
      {
        v26 = v25 + 144;
        if ( v25 + 144 < v25 )
          v26 = -1i64;
       v27 = Memory::Recycler::AllocLeafZero(v12, v26);//v26 = rdx => totalAlloc + sizeof(DynamicProfileInfo) = 内存分配长度
      }
      *((_WORD *)v27 + 56) = ValueType::Uninitialized;
      v27[114] = 0;
      v27[136] = 1;
    LABEL_20:
      v28 = (signed __int64)(v27 + 144);
      v29 = 12i64;
      v30 = &v38;
      do
      {
        v31 = *((_QWORD *)v30 + 1);
        if ( v31 )
        {
          *(_QWORD *)&v27[*v30] = v28;
          v28 += v31;
        }
        v30 += 4;
        --v29;
      }
      while ( v29 );
      Js::DynamicProfileInfo::Initialize((Js::DynamicProfileInfo *)v27, (struct Js::FunctionBody *const )retaddr);
      return v27;
    }
    

用命令 ba chakra!Js::DynamicProfileInfo::New
在DynamicProfileInfo::New函数位置打个断点，动态调试之后，可得如下信息：

    
    
    0:017> r
    rax=00000000000100e7 rbx=0000015bce310348 rcx=00000153adba97b0
    rdx=0000000000010177 rsi=0000000000000000 rdi=0000015bce3101b0
    rip=00007ff88ef9a7c3 rsp=0000004016ffba50 rbp=0000004016ffbb50
     r8=0000000000000004  r9=0000000000000001 r10=00000153adba97b0
    r11=0000004016ffbc70 r12=0000004016ffc0a8 r13=0000000000000001
    r14=0000015bb37203c0 r15=0000000000000001
    iopl=0         nv up ei pl nz na po nc
    cs=0033  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000206
    chakra!Js::DynamicProfileInfo::New+0x213:
    00007ff88ef9a7c3 e8c830f0ff      call    chakra!Memory::Recycler::AllocLeafZero (00007ff8`8ee9d890)
    

此时可知:

    
    
    (v26 = rdx  = totalAlloc + sizeof(DynamicProfileInfo)  = 0x10177) < (0xfefa0 = callSiteId * 0x10  = 0xfefa * 0x10)，
    内存分配长度为 0x10177 远远小于 使用时的 0xfefa0，确定漏洞是因callSiteId越界导致的内存越界读。
    

**3.2.3 追溯callSiteId参数的来源**

根据 3.1 步骤的 kb
栈回溯命令可知，callSiteId是上层调用OP_NewScObjArray_Impl函数进来的，OP_NewScObjArray_Impl的源代码如下：

    
    
    template <class T, bool Profiled>
    void InterpreterStackFrame::OP_NewScObjArray_Impl(const unaligned T* playout, const Js::AuxArray<uint32> *spreadIndices)
    {
        // Always profile this operation when auto-profiling so that array type changes are tracked
        if (!Profiled && !isAutoProfiling)
        Assert(!Profiled);
        {
            OP_NewScObject_Impl<T, Profiled, false>(playout, Js::Constants::NoInlineCacheIndex, spreadIndices);
            return;
        }
        Arguments args(CallInfo(CallFlags_New, playout->ArgCount), m_outParams);
        uint32 spreadSize = 0;
        if (spreadIndices != nullptr){...}
        else
        {
            SetReg(
            (RegSlot)playout->Return,
            ProfilingHelpers::ProfiledNewScObjArray(
                GetReg(playout->Function),
                args,
                function,
                static_cast<const unaligned OpLayoutDynamicProfile2<T> *>(playout)->profileId,//profileId  <==> callSiteId
                static_cast<const unaligned OpLayoutDynamicProfile2<T> *>(playout)->profileId2));
        }
        PopOut(playout->ArgCount);
        }
    

根据上面的红色部分，我们可知，callSiteId来自playout参数的profileId的成员变量。

**3.2.4 追溯playout参数的来源**

根据 3.1 步骤的 kb
栈回溯命令可知，playout是上层调用ProcessUnprofiled函数进来的，ProcessUnprofiled的源代码调用栈追溯路径如下：

    
    
    InterpreterLoop.inl:
    ...
    case INTERPRETER_OPCODE::MediumLayoutPrefix:
            {
                Var yieldValue = nullptr;
                ip = PROCESS_OPCODE_FN_NAME(MediumLayoutPrefix)(ip, yieldValue);==>
                CHECK_YIELD_VALUE();
                CHECK_SWITCH_PROFILE_MODE();
                break;
            }
    ...
    const byte* Js::InterpreterStackFrame::PROCESS_OPCODE_FN_NAME(MediumLayoutPrefix)(const byte* ip, Var& yieldValue)
    {
        INTERPRETER_OPCODE op = READ_OP(ip);
        switch (op)
        {
    #ifndef INTERPRETER_ASMJS
        case INTERPRETER_OPCODE::Yield:
            m_reader.Reg2_Medium(ip);
            yieldValue = GetReg(GetFunctionBody()->GetYieldRegister());
            break;
    #endif
    #define DEF2_WMS(x, op, func) PROCESS_##x##_COMMON(op, func, _Medium)
    #define DEF3_WMS(x, op, func, y) PROCESS_##x##_COMMON(op, func, y, _Medium)==>
    #define DEF4_WMS(x, op, func, y, t) PROCESS_##x##_COMMON(op, func, y, _Medium, t)
    #include "InterpreterHandler.inl"
        default:
            // Help the C++ optimizer by declaring that the cases we
            // have above are sufficient
            AssertMsg(false, "dispatch to bad opcode");
            __assume(false);
        }
        return ip;
    }
    InterpreterHandler.inl:
    ...
    DEF3_WMS(CALL,                    NewScObject,                OP_NewScObject, CallI)
    DEF3_WMS(CUSTOM_L_R0,             NewScObjectNoCtorFull,      OP_NewScObjectNoCtorFull, Reg2)
    EXDEF2_WMS(A1toA1Mem,               LdCustomSpreadIteratorList, JavascriptOperators::OP_LdCustomSpreadIteratorList)
    EXDEF3_WMS(CALL,                    NewScObjectSpread,          OP_NewScObjectSpread, CallIExtended)
    DEF3_WMS(CALL,                    NewScObjArray,              OP_NewScObjArray, CallI)==>
    ...
    InterpreterStackFrame.cpp:
    #define PROCESS_CALL_COMMON(name, func, layout, suffix) \
        case OpCode::name: \
        { \
            PROCESS_READ_LAYOUT(name, layout, suffix); \\==>
            func(playout); \
            break; \
        }
    ...
    #define PROCESS_READ_LAYOUT(name, layout, suffix) \
        CompileAssert(OpCodeInfo<OpCode::name>::Layout == OpLayoutType::layout); \
        const unaligned OpLayout##layout##suffix * playout = m_reader.layout##suffix(ip); \\==>
        Assert((playout != nullptr) == (Js::OpLayoutType::##layout != Js::OpLayoutType::Empty)); // Make sure playout is used
    ...
    LayoutTypes.h:
    ...
    LAYOUT_TYPE                 (StartCall)
    LAYOUT_TYPE_PROFILED2_WMS   (CallI)==>
    LAYOUT_TYPE_PROFILED_WMS    (CallIFlags)
    ...
    OpLayouts.h:
    ...
    #define LAYOUT_TYPE_WMS(layout) \
        typedef OpLayoutT_##layout OpLayout##layout##_Large; \
        typedef OpLayoutT_##layout OpLayout##layout##_Medium; \\==>
        typedef OpLayoutT_##layout OpLayout##layout##_Small;
    ...
    template <typename SizePolicy>
    struct OpLayoutT_CallI                // Return = Function(ArgCount)
    {
        typename SizePolicy::ArgSlotType     ArgCount;
        typename SizePolicy::RegSlotSType    Return;
        typename SizePolicy::RegSlotType     Function;
    };
    ...
    ByteCodeReader.cpp:
    template<typename LayoutType>
    const unaligned LayoutType * ByteCodeReader::GetLayout(const byte*& ip)
    {
        size_t layoutSize = sizeof(LayoutType);//LayoutType=Js::OpLayoutT_CallI<Js::LayoutSizePolicy<MediumLayout>> => layoutSize = 0x5
        AssertMsg((layoutSize > 0) && (layoutSize < 100), "Ensure valid layout size");
        const byte * layoutData = ip;
        ip += layoutSize;
        m_currentLocation = ip;
        Assert(m_currentLocation <= m_endLocation);
        return reinterpret_cast(layoutData);
    }
    

根据上面的源代码追溯和动态调试，可得playout参数的类型为OpLayoutT_CallI结构体，指向的是bytecode的内容，长度为0x5个字节。OpLayoutT_CallI内存结构如下：

    
    
    name:  |ArgSlotType|RegSlotSType|RegSlotType|
    size:  |    1 byte |    2 byte  |    2 byte |
    value: |    c5     |    fe 00   |    fe 00  |
    

此时再看OP_NewScObjArray_Impl函数获取callSiteId参数的代码如下：

    
    
    static_cast<const unaligned OpLayoutDynamicProfile2 *>(playout)->profileId,//profileId  <==> callSiteId
    

发现playout参数被强制转换成OpLayoutDynamicProfile2结构体，并提取其成员变量profileId当成callSiteId向下传递了，OpLayoutDynamicProfile2的结构体代码如下：

    
    
    OpLayouts.h:
    ...
    typedef uint16 ProfileId;
    ...
    // Dynamic profile layout wrapper
    template <typename LayoutType>
    struct OpLayoutDynamicProfile : public LayoutType
    {
        ProfileId profileId;
    };
    template <typename LayoutType>
    struct OpLayoutDynamicProfile2 : public LayoutType
    {
        ProfileId profileId;
        ProfileId profileId2;
    };
    ...
    

该结构体的长度为sizeof(OpLayoutDynamicProfile2) = 0x9个字节, OpLayoutDynamicProfile2
内存结构如下：

    
    
    name:  |ArgSlotType|RegSlotSType|RegSlotType|profileId|profileId2|
    size:  |    1 byte |    2 byte  |    2 byte |  2 byte |   2 byte | 
    value: |    c5     |    fe 00   |    fe 00  |  fa fe  |   e9 09  |
    

此时可知OpLayoutT_Call类型被混淆成OpLayoutDynamicProfile2使用，callSiteId = profileId =
0xfefa参数变量是由于在对象混淆情况下，越界读了后面2个字节的bytecode指令操作码，callSiteId参数被传到RecordCallSiteInfo函数之后，产生了越界读异常现象。

## 4.漏洞利用

1)
首先跳到访问异常点附近看看，RecordCallSiteInfo在函数访问异常点之后，还有些什么样的操作，重点关注程序后续流程中有没有写的操作。RecordCallSiteInfo函数关键点代码如下：

    
    
    if (!callSiteInfo[callSiteId].isPolymorphic) // out of bound read
    {
    ...           
    if (doInline && IsPolymorphicCallSite(functionId, sourceId, oldFunctionId, oldSourceId))
    {
        CreatePolymorphicDynamicProfileCallSiteInfo(functionBody, callSiteId, functionId, oldFunctionId, sourceId, oldSourceId);==>
    }
    ...
    void DynamicProfileInfo::CreatePolymorphicDynamicProfileCallSiteInfo(FunctionBody *funcBody, ProfileId callSiteId, Js::LocalFunctionId functionId, Js::LocalFunctionId oldFunctionId, Js::SourceId sourceId, Js::SourceId oldSourceId)
    {
        PolymorphicCallSiteInfo *localPolyCallSiteInfo = RecyclerNewStructZ(funcBody->GetScriptContext()->GetRecycler(), PolymorphicCallSiteInfo);
        Assert(maxPolymorphicInliningSize >= 2);
        localPolyCallSiteInfo->functionIds[0] = oldFunctionId;
        localPolyCallSiteInfo->functionIds[1] = functionId;
        localPolyCallSiteInfo->sourceIds[0] = oldSourceId;
        localPolyCallSiteInfo->sourceIds[1] = sourceId;
        localPolyCallSiteInfo->next = funcBody->GetPolymorphicCallSiteInfoHead();
        for (int i = 2; i < maxPolymorphicInliningSize; i++)
        {
            localPolyCallSiteInfo->functionIds[i] = CallSiteNoInfo;
        }
        callSiteInfo[callSiteId].isPolymorphic = true;//out of bound write boolean
        callSiteInfo[callSiteId].u.polymorphicCallSiteInfo = localPolyCallSiteInfo;//out of bound write pointer
        funcBody->SetPolymorphicCallSiteInfoHead(localPolyCallSiteInfo);
    }
    ...
    

假设在完全可以控制堆喷数据的情况下，那么上面蓝色部分的判断可以过掉，在随后的红色部分就有写的操作。

2) 漏洞分配的内存长度为0x10177，越界读的内存偏移为0xfefa0 = callSiteId * 0x10 = 0xfefa *
0x10，由于callSiteId = 0xfefa是通过越界读2个字节的bytecode指令操作码得到的，所以这个越界读的偏移不是任意可以控制的。

3) Microsoft Edge 堆隔离，及其内存分配机制。Edge的堆分为：

  * – 小堆 (0 < size <= 0x300)：每隔0x10为一个堆桶（步长为0x10),对齐方式：0x10 实现方式：size => 堆桶的 map 映射。 例如：0x10、0x20、0x30… 一共(0x300 / 0x10 = 0x30个堆桶）
  * – 中堆 (0x300 < size <= 0x2000)：每隔0x100为一个堆桶（步长为0x100),对齐方式：0x100 实现方式：size => 堆桶的 map 映射。例如：0x400、0x500、0x600…一共(0x2000-0x300 / 0x100 = 0x1D个堆桶）
  * – 大堆 (size > 0x2000)：对齐方式：0x10 实现方式：堆桶之间的链表串连。

由于 0x10177 > 0x2000 的内存大小在大堆范畴，所以由大堆来分配内存。

综合
1），2），3），及其深入分析之后，要能够精准控制内存的堆喷，越界写一些内存关键数据（如：长度、数据存储指针等），选用array进行堆喷可以满足要求，本利用中选择越界修改array的长度来实现漏洞利用。堆喷之后的内存结构如下：

    
    
    name: | vulnmem | fill_mem  | pre_trigger_arr | trigger_arr | fill_leak_arr |
    desc: | 0x10180 | spray_mem |  int array      |  int array  |  object array |
    

完整的漏洞利用步骤如下：  
a. 触发漏洞之后，pre_trigger_arr的长度被修改为一个指针，此时pre_trigger_arr可越界写，但不能越界读。  
b. 通过pre_trigger_arr越界写，修改trigger_arr的长度，此时trigger_arr可越界读写。  
c. 通过trigger_arr越界读，可泄露fill_leak_arr中的任意一个元素对象的地址。  
d.
通过pre_trigger_arr越界写，修改trigger_arr的数据存储指针为DataView对象地址偏移，把DataView数据头伪造成trigger_arr的元素数据。  
e. 通过trigger_arr正常的写，修改DataView的arrayBuffer的数据指针。  
f. 通过DataView正常读取，可达到任意地址读写的目的。

## 5.漏洞演示

a. 通过任意地址读写，泄露chakra.dll的基地址。  
b. 通过调用GetProcAddress函数，泄露msvcrt.dll中malloc函数的地址。  
c. 通过调用GetProcAddress函数，泄露kernel32.dll中WinExec函数的地址。  

## 6.漏洞补丁

补丁前：

    
    
    template <class T, bool Profiled>
    void InterpreterStackFrame::OP_NewScObjArray_Impl(const unaligned T* playout, const Js::AuxArray<uint32> *spreadIndices)
    {
        // Always profile this operation when auto-profiling so that array type changes are tracked
        if (!Profiled && !isAutoProfiling) isAutoProfiling 变量出的问题，导致该条件判断为false
        Assert(!Profiled);
        {
            OP_NewScObject_Impl<t, profiled,="" false="" style="box-sizing: border-box;">(playout, Js::Constants::NoInlineCacheIndex, spreadIndices);
            return;
        }
        Arguments args(CallInfo(CallFlags_New, playout->ArgCount), m_outParams);
        uint32 spreadSize = 0;
        if (spreadIndices != nullptr){...}
        else
        {
            SetReg(
            (RegSlot)playout->Return,
            ProfilingHelpers::ProfiledNewScObjArray(
                GetReg(playout->Function),
                args,
                function,
                static_cast<const unaligned OpLayoutDynamicProfile2<T> *>(playout)->profileId,//profileId  <==> callSiteId
                static_cast<const unaligned OpLayoutDynamicProfile2<T> *>(playout)->profileId2));
        }
        PopOut(playout->ArgCount);
        }
    </t,>

补丁后：

    
    
    template <class T, bool Profiled> void OP_NewScObjArray_Impl(const unaligned T* playout, const Js::AuxArray<uint32> *spreadIndices = nullptr) 
    { 
        OP_NewScObject_Impl<T, Profiled, false>(playout, Js::Constants::NoInlineCacheIndex, spreadIndices);==>
    }
    template <class T, bool Profiled, bool ICIndex>
    void InterpreterStackFrame::OP_NewScObject_Impl(const unaligned T* playout, InlineCacheIndex inlineCacheIndex, const Js::AuxArray *spreadIndices)
    {
        if (ICIndex)
        {
            Assert(inlineCacheIndex != Js::Constants::NoInlineCacheIndex);
        }
        Var newVarInstance =
    #if ENABLE_PROFILE_INFO
            Profiled ? 补丁前的isAutoProfiling 条件判断被干掉了
            ProfiledNewScObject_Helper(
                GetReg(playout->Function),
                playout->ArgCount,
                static_cast<const unaligned OpLayoutDynamicProfile<T> *>(playout)->profileId,
                inlineCacheIndex,
                spreadIndices) :
    #endif
            NewScObject_Helper(GetReg(playout->Function), playout->ArgCount, spreadIndices);
        SetReg((RegSlot)playout->Return, newVarInstance);
    }
    

从上面补丁前后的对比可知，补丁后OP_NewScObjArray_Impl函数代码中有问题的代码被优化掉了。

## 7.exp

  * [exp地址](https://github.com/bo13oy/ChakraCore/tree/master/%231)

## 8.参考链接

  * [ChakraCore v1.8.0](https://github.com/Microsoft/ChakraCore/releases/tag/v1.8.0)
  * [pwnjs](https://github.com/theori-io/pwnjs)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360vulcan team** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/158818](/post/id/158818)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [代码执行](/tag/代码执行)
  * [Chakra](/tag/Chakra)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t01cce7f410770758df.png) 360vulcan team

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

