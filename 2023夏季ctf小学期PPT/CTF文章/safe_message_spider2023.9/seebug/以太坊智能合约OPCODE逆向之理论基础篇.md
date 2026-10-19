作者：Hcamael@知道创宇404区块链安全研究团队

在我们对etherscan等平台上合约进行安全审查时，常常会遇到没有公布Solidity源代码的合约，只能获取到合约的OPCODE，所以一个智能合约的反编译器对审计无源码的智能合约起到了非常重要的作用。

目前在互联网上常见的反编译工具只有[porosity](https://github.com/comaeio/porosity
"porosity")[1]，另外在Github上还找到另外的反编译工具[ethdasm](https://github.com/meyer9/ethdasm
"ethdasm")[2]，经过测试发现这两个编译器都有许多bug，无法满足我的工作需求。因此我开始尝试研究并开发能满足我们自己需求的反编译工具，在我看来如果要写出一个优秀的反汇编工具，首先需要有较强的OPCODE逆向能力，本篇Paper将对以太坊智能合约OPCODE的数据结构进行一次深入分析。

#### 基础

智能合约的OPCODE是在EVM(Ethereum Virtual Machine)中进行解释执行，OPCODE为1字节，从`0x00 -0xff`代表了相对应的指令，但实际有用的指令并没有0xff个，还有一部分未被使用，以便将来的扩展

具体指令可参考[Github](https://github.com/trailofbits/evm-opcodes
"Github")[3]上的OPCODE指令集，每个指令具体含义可以参考[相关文档](http://solidity.readthedocs.io/en/v0.4.21/assembly.html
"相关文档")[4]

#### IO

在EVM中不存在寄存器，也没有网络IO相关的指令，只存在对栈(stack)，内存(mem), 存储(storage)的读写操作

  * stack

使用的push和pop对栈进行存取操作，push后面会带上存入栈数据的长度，最小为1字节，最大为32字节，所以OPCODE从`0x60-0x7f`分别代表的是`push1-push32`

`PUSH1`会将OPCODE后面1字节的数据放入栈中，比如字节码是`0x6060`代表的指令就是`PUSH1 0x60`

除了`PUSH`指令，其他指令获取参数都是从栈中获取，指令返回的结果也是直接存入栈中

  * mem

内存的存取操作是`MSTORE`和`MLOAD`

`MSTORE(arg0, arg1)`从栈中获取两个参数，表示`MEM[arg0:arg0+32] = arg1`

`MLOAD(arg0)`从栈中获取一个参数，表示`PUSH32(MEM[arg0:arg0+32])`

因为`PUSH`指令，最大只能把32字节的数据存入栈中，所以对内存的操作每次只能操作32字节

但是还有一个指令`MSTORE8`，只修改内存的1个字节

`MSTORE(arg0, arg1)`从栈中获取两个参数，表示`MEM[arg0] = arg1`

内存的作用一般是用来存储返回值，或者某些指令有处理大于32字节数据的需求

比如: `SHA3(arg0,
arg1)`从栈中获取两个参数，表示`SHA3(MEM[arg0:arg0+arg1])`，SHA3对内存中的数据进行计算sha3哈希值，参数只是用来指定内存的范围

  * storage

上面的stack和mem都是在EVM执行OPCODE的时候初始化，但是storage是存在于区块链中，我们可以类比为计算机的存储磁盘。

所以，就算不执行智能合约，我们也能获取智能合约storage中的数据:

    
    
    eth.getStorageAt(合约地址, slot)   
    # 该函数还有第三个参数，默认为"latest"，还可以设置为"earliest"或者"pending"，具体作用本文不做分析

storage用来存储智能合约中所有的全局变量

使用`SLOAD`和`SSTORE`进行操作

`SSTORE(arg0, arg1)`从栈中获取两个参数，表示`eth.getStorageAt(合约地址, arg0) = arg1`

`SLOAD(arg0)`从栈中获取一个参数，表示`PUSH32(eth.getStorageAt(合约地址, arg0))`

#### 变量

智能合约的变量从作用域可以分为三种, 全局公有变量(public), 全局私有变量(private), 局部变量

全局变量和局部变量的区别是，全局变量储存在storage中，而局部变量是被编译进OPCODE中，在运行时，被放在stack中，等待后续使用

公有变量和私有变量的区别是，公有变量会被编译成一个constant函数，后面会分析函数之前的区别

因为私有变量也是储存在storage中，而storage是存在于区块链当中，所以相当于私有变量也是公开的，所以不要想着用私有变量来储存啥不能公开的数据。

##### 全局变量的储存模型

不同类型的变量在storage中储存的方式也是有区别的，下面对各种类型的变量的储存模型进行分析

###### 1\. 定长变量

第一种我们归类为定长变量，所谓的定长变量，也就是该变量在定义的时候，其长度就已经被限制住了

比如定长整型(int/uint......), 地址(address), 定长浮点型(fixed/ufixed......),
定长字节数组(bytes1-32)

这类的变量在storage中都是按顺序储存

    
    
    uint a;       // slot = 0
    address b;    // 1
    ufixed c;     // 2
    bytes32 d;    // 3
    ## 
    a == eth.getStorageAt(contract, 0)
    d == eth.getStorageAt(contract, 3)

上面举的例子，除了`address`的长度是160bits，其他变量的长度都是256bits，而storage是256bits对齐的，所以都是一个变量占着一块storage，但是会存在连续两个变量的长度不足256bits的情况

    
    
    address a;      // slot = 0
    uint8 b;        // 0
    address c;      // 1
    uint16 d;       // 1

在opcode层面，获取a的值得操作是: `SLOAD(0) & 0xffffffffffffffffffffffffffffffffffffffff`

获取b值得操作是: `SLOAD(0) // 0x10000000000000000000000000000000000000000 & 0xff`

获取d值得操作是: `SLOAD(1) // 0x10000000000000000000000000000000000000000 & 0xffff`

因为b的长度+a的长度不足256bits，变量a和b是连续的，所以他们在同一块storage中，然后在编译的过程中进行区分变量a和变量b，但是后续在加上变量c，长度就超过了256bits，因此把变量c放到下一块storage中，然后变量d跟在c之后

从上面我们可以看出，storage的储存策略一个是256bits对齐，一个是顺序储存。(并没有考虑到充分利用每一字节的储存空间，我觉得可以考虑把d变量放到b变量之后)

###### 2\. 映射变量

    
    
    mapping(address => uint) a;

映射变量就没办法想上面的定长变量按顺序储存了，因为这是一个键值对变量，EVM采用的机制是:

`SLOAD(sha3(key.rjust(64, "0")+slot.rjust(64, "0")))`

比如: `a["0xd25ed029c093e56bc8911a07c46545000cbf37c6"]`首先计算sha3哈希值:

    
    
    >>> from sha3 import keccak_256
    >>> data = "d25ed029c093e56bc8911a07c46545000cbf37c6".rjust(64, "0")
    >>> data += "00".rjust(64, "0")
    >>> keccak_256(data.encode()).hexdigest()
    '739cc24910ff41b372fbcb2294933bdc3108bd86ffd915d64d569c68a85121ec'
    # 
    a["0xd25ed029c093e56bc8911a07c46545000cbf37c6"] == SLOAD("739cc24910ff41b372fbcb2294933bdc3108bd86ffd915d64d569c68a85121ec")

我们也可以使用以太坊客户端直接获取:

    
    
    > eth.getStorageAt(合约地址, "739cc24910ff41b372fbcb2294933bdc3108bd86ffd915d64d569c68a85121ec")

还有slot需要注意一下:

    
    
    address public a;                       // slot = 0
    mapping(address => uint) public b;      // slot = 1
    uint public d;                          // slot = 1
    mapping(address => uint) public c;      // slot = 3

根据映射变量的储存模型，或许我们真的可以在智能合约中隐藏私密信息，比如，有一个secret，只有知道key的人才能知道secret的内容，我们可以`b[key]
= secret`, 虽然数据仍然是储存在storage中，但是在不知道key的情况下却无法获取到`secret`。

不过，storage是存在于区块链之中，目前我猜测是通过智能合约可以映射到对应的storage，storage不可能会初始化`256*256bits`的内存空间，那样就太消耗硬盘空间了，所以可以通过解析区块链文件，获取到storage全部的数据。

上面这些仅仅是个人猜想，会作为之后研究以太坊源码的一个研究方向。

###### 3\. 变长变量

变长变量也就是数组，长度不一定，其储存方式有点像上面两种的结合

    
    
    uint a;         // slot = 0
    uint[] b;       // 1
    uint c;         // 2

数组任然会占用对应slot的storage，储存数组的长度(`b.length == SLOAD(1)`)

比如我们想获取`b[1]`的值，会把输入的`index`和`SLOAD(1)`的值进行比较，防止数组越界访问

然后计算slot的sha3哈希值:

    
    
    >>> from sha3 import keccak_256
    >>> slot = "01".rjust(64, "0")
    >>> keccak_256(slot.encode()).hexdigest()
    '20ec45d096f1fa2aeff1e3da8a84697d90109524958ed4be9f6d69e37a9140a4'
    
    #
    b[X] == SLOAD('20ec45d096f1fa2aeff1e3da8a84697d90109524958ed4be9f6d69e37a9140a4' + X)
    
    # 获取b[2]的值
    > eth.getStorageAt(合约地址, "20ec45d096f1fa2aeff1e3da8a84697d90109524958ed4be9f6d69e37a9140a6")

在变长变量中有两个特例: `string`和`bytes`

字符串可以认为是字符数组，bytes是byte数组，当这两种变量的长度在`0-31`时，值储存在对应slot的storage上，最后一字节为`长度*2|flag`,
当flag = 1，表示长度>31，否则长度<=31

下面进行举例说明

    
    
    uint i;                // slot = 0
    string a = "c"*31;     // 1
    SLOAD(1) == "c*31" + "00" | 31*2 == "636363636363636363636363636363636363636363636363636363636363633e"

当变量的长度大于31时，`SLOAD(slot)`储存`length*2|flag`，把值储存到`sha3(slot)`

    
    
    uint i;                // slot = 0
    string a = "c"*36;     // 1
    SLOAD(1) == 36*2|1 == 0x49
    SLOAD(SHA3("01".rjust(64, "0"))) == "c"*36

###### 4\. 结构体

结构体没有单独特殊的储存模型，结构体相当于变量数组，下面进行举例说明:

    
    
    struct test {
        uint a;
        uint b;
        uint c;
    }
    address g;
    Test e;
    
    # 上面变量在storage的储存方式等同于
    address g;
    uint a;
    uint b;
    uint c;

#### 函数

##### 两种调用函数的方式

下面是针对两种函数调用方式说明的测试代码，发布在测试网络上:
<https://ropsten.etherscan.io/address/0xc9fbe313dc1d6a1c542edca21d1104c338676ffd#code>

    
    
    pragma solidity ^0.4.18;
    
    contract Test {
    
      address public owner;
      uint public prize;
    
      function Test() {
        owner = msg.sender;
      }
    
      function test1() constant public returns (address) {
        return owner;
      }
    
      function test2(uint p) public {
          prize += p;
      }
    }

整个OPCODE都是在EVM中执行，所以第一个调用函数的方式就是使用EVM进行执行OPCODE:

    
    
    # 调用test1
    > eth.call({to: "0xc9fbe313dc1d6a1c542edca21d1104c338676ffd", data: "0x6b59084d"})
    "0x0000000000000000000000000109dea8b64d87a26e7fe9af6400375099c78fdd"
    > eth.getStorageAt("0xc9fbe313dc1d6a1c542edca21d1104c338676ffd", 0)
    "0x0000000000000000000000000109dea8b64d87a26e7fe9af6400375099c78fdd"

第二种方式就是通过发送交易:

    
    
    # 调用test2
    > eth.getStorageAt("0xc9fbe313dc1d6a1c542edca21d1104c338676ffd", 1)
    "0x0000000000000000000000000000000000000000000000000000000000000005"
    > eth.sendTransaction({from: eth.accounts[0], to: "0xc9fbe313dc1d6a1c542edca21d1104c338676ffd", data: "0xcaf446830000000000000000000000000000000000000000000000000000000000000005"})
    > eth.getStorageAt("0xc9fbe313dc1d6a1c542edca21d1104c338676ffd", 1)
    "0x000000000000000000000000000000000000000000000000000000000000000a"

这两种调用方式的区别有两个:

  1. 使用call调用函数是在本地使用EVM执行合约的OPCODE，所以可以获得返回值
  2. 通过交易调用的函数，能修改区块链上的storage

一个调用合约函数的交易(比如
`https://ropsten.etherscan.io/tx/0xab1040ff9b04f8fc13b12057f9c090e0a9348b7d3e7b4bb09523819e575cf651`)的信息中，是不存在返回值的信息，但是却可以修改storage的信息(一个交易是怎么修改对应的storage信息，是之后的一个研究方向)

而通过call调用，是在本地使用EVM执行OPCODE，返回值是存在MEM中return，所以可以获取到返回值，虽然也可以修改storage的数据，不过只是修改你本地数据，不通过发起交易，其他节点将不会接受你的更改，所以是一个无效的修改，同时，本地调用函数也不需要消耗gas，所以上面举例中，在调用信息的字典里，不需要`from`字段，而交易却需要指定(设置`from`)从哪个账号消耗gas。

##### 调用函数

EVM是怎么判断调用哪个函数的呢？下面使用OPCODE来进行说明

每一个智能合约入口代码是有固定模式的，我们可以称为智能合约的主函数，上面测试合约的主函数如下:

PS: [Github](https://github.com/trailofbits/ida-evm
"Github")[5]上面有一个EVM反汇编的IDA插件

    
    
    [     0x0] | PUSH1                | ['0x80']
    [     0x2] | PUSH1                | ['0x40']
    [     0x4] | MSTORE               | None
    [     0x5] | PUSH1                | ['0x4']
    [     0x7] | CALLDATASIZE         | None
    [     0x8] | LT                   | None
    [     0x9] | PUSH2                | ['0x61']
    [     0xc] | JUMPI                | None
    [     0xd] | PUSH4                | ['0xffffffff']
    [    0x12] | PUSH29               | ['0x100000000000000000000000000000000000000000000000000000000']
    [    0x30] | PUSH1                | ['0x0']
    [    0x32] | CALLDATALOAD         | None
    [    0x33] | DIV                  | None
    [    0x34] | AND                  | None
    [    0x35] | PUSH4                | ['0x6b59084d']
    [    0x3a] | DUP2                 | None
    [    0x3b] | EQ                   | None
    [    0x3c] | PUSH2                | ['0x66']
    [    0x3f] | JUMPI                | None
    [    0x40] | DUP1                 | None
    [    0x41] | PUSH4                | ['0x8da5cb5b']
    [    0x46] | EQ                   | None
    [    0x47] | PUSH2                | ['0xa4']
    [    0x4a] | JUMPI                | None
    [    0x4b] | DUP1                 | None
    [    0x4c] | PUSH4                | ['0xcaf44683']
    [    0x51] | EQ                   | None
    [    0x52] | PUSH2                | ['0xb9']
    [    0x55] | JUMPI                | None
    [    0x56] | DUP1                 | None
    [    0x57] | PUSH4                | ['0xe3ac5d26']
    [    0x5c] | EQ                   | None
    [    0x5d] | PUSH2                | ['0xd3']
    [    0x60] | JUMPI                | None
    [    0x61] | JUMPDEST             | None
    [    0x62] | PUSH1                | ['0x0']
    [    0x64] | DUP1                 | None
    [    0x65] | REVERT               | None

反编译出来的代码就是:

    
    
    def main():
        if CALLDATASIZE >= 4:
            data = CALLDATA[:4]
            if data == 0x6b59084d:
                test1()
            elif data == 0x8da5cb5b:
                owner()
            elif data == 0xcaf44683:
                test2()
            elif data == 0xe3ac5d26:
                prize()
            else:
                pass
        raise

PS：因为个人习惯问题，反编译最终输出没有选择对应的Solidity代码，而是使用Python。

从上面的代码我们就能看出来，EVM是根据`CALLDATA`的前4字节来确定调用的函数的，这4个字节表示的是函数的sha3哈希值的前4字节:

    
    
    > web3.sha3("test1()")
    "0x6b59084dfb7dcf1c687dd12ad5778be120c9121b21ef90a32ff73565a36c9cd3"
    > web3.sha3("owner()")
    "0x8da5cb5b36e7f68c1d2e56001220cdbdd3ba2616072f718acfda4a06441a807d"
    > web3.sha3("prize()")
    "0xe3ac5d2656091dd8f25e87b604175717f3442b1e2af8ecd1b1f708bab76d9a91"
    # 如果该函数有参数，则需要加上各个参数的类型
    > web3.sha3("test2(uint256)")
    "0xcaf446833eef44593b83316414b79e98fec092b78e4c1287e6968774e0283444"

所以可以去网上找个[哈希表映射](https://github.com/trailofbits/ida-evm/blob/master/known_hashes.py "哈希表映射")[6]，这样有概率可以通过hash值，得到函数名和参数信息，减小逆向的难度

##### 主函数中的函数

上面给出的测试智能合约中只有两个函数，但是反编译出来的主函数中，却有4个函数调用，其中两个是公有函数，另两个是公有变量

智能合约变量/函数类型只有两种，公有和私有，公有和私有的区别很简单，公有的是能别外部调用访问，私有的只能被本身调用访问

对于变量，不管是公有还是私有都能通过`getStorageAt`访问，但是这是属于以太坊层面的，在智能合约层面，把公有变量给编译成了一个公有函数，在这公有函数中返回`SLOAD(slot)`，而私有函数只能在其他函数中特定的地方调用`SLOAD(slot)`来访问

在上面测试的智能合约中, `test1()`函数等同于`owner()`，我们可以来看看各自的OPCODE:

    
    
    ; test1()
    ; 0x66: loc_66
    [    0x66] | JUMPDEST             | None
    [    0x67] | CALLVALUE            | None
    [    0x68] | DUP1                 | None
    [    0x69] | ISZERO               | None
    [    0x6a] | PUSH2                | ['0x72']
    [    0x6d] | JUMPI                | None
    [    0x6e] | PUSH1                | ['0x0']
    [    0x70] | DUP1                 | None
    [    0x71] | REVERT               | None
    ; 0x72: loc_72
    [    0x72] | JUMPDEST             | None
    [    0x73] | POP                  | None
    [    0x74] | PUSH2                | ['0x7b']
    [    0x77] | PUSH2                | ['0xfa']
    [    0x7a] | JUMP                 | None
    ; 0xFA: loc_fa
    [    0xfa] | JUMPDEST             | None
    [    0xfb] | PUSH1                | ['0x0']
    [    0xfd] | SLOAD                | None
    [    0xfe] | PUSH20               | ['0xffffffffffffffffffffffffffffffffffffffff']
    [   0x113] | AND                  | None
    [   0x114] | SWAP1                | None
    [   0x115] | JUMP                 | None
    ; 0x7B: loc_7b
    [    0x7b] | JUMPDEST             | None
    [    0x7c] | PUSH1                | ['0x40']
    [    0x7e] | DUP1                 | None
    [    0x7f] | MLOAD                | None
    [    0x80] | PUSH20               | ['0xffffffffffffffffffffffffffffffffffffffff']
    [    0x95] | SWAP1                | None
    [    0x96] | SWAP3                | None
    [    0x97] | AND                  | None
    [    0x98] | DUP3                 | None
    [    0x99] | MSTORE               | None
    [    0x9a] | MLOAD                | None
    [    0x9b] | SWAP1                | None
    [    0x9c] | DUP2                 | None
    [    0x9d] | SWAP1                | None
    [    0x9e] | SUB                  | None
    [    0x9f] | PUSH1                | ['0x20']
    [    0xa1] | ADD                  | None
    [    0xa2] | SWAP1                | None
    [    0xa3] | RETURN               | None

和`owner()`函数进行对比:

    
    
    ; owner()
    ; 0xA4: loc_a4
    [    0xa4] | JUMPDEST             | None
    [    0xa5] | CALLVALUE            | None
    [    0xa6] | DUP1                 | None
    [    0xa7] | ISZERO               | None
    [    0xa8] | PUSH2                | ['0xb0']
    [    0xab] | JUMPI                | None
    [    0xac] | PUSH1                | ['0x0']
    [    0xae] | DUP1                 | None
    [    0xaf] | REVERT               | None
    ; 0xB0: loc_b0
    [    0xb0] | JUMPDEST             | None
    [    0xb1] | POP                  | None
    [    0xb2] | PUSH2                | ['0x7b']
    [    0xb5] | PUSH2                | ['0x116']
    [    0xb8] | JUMP                 | None
    ; 0x116: loc_116
    [   0x116] | JUMPDEST             | None
    [   0x117] | PUSH1                | ['0x0']
    [   0x119] | SLOAD                | None
    [   0x11a] | PUSH20               | ['0xffffffffffffffffffffffffffffffffffffffff']
    [   0x12f] | AND                  | None
    [   0x130] | DUP2                 | None
    [   0x131] | JUMP                 | None
    ; 0x7B: loc_7b
    [    0x7b] | JUMPDEST             | None
    [    0x7c] | PUSH1                | ['0x40']
    [    0x7e] | DUP1                 | None
    [    0x7f] | MLOAD                | None
    [    0x80] | PUSH20               | ['0xffffffffffffffffffffffffffffffffffffffff']
    [    0x95] | SWAP1                | None
    [    0x96] | SWAP3                | None
    [    0x97] | AND                  | None
    [    0x98] | DUP3                 | None
    [    0x99] | MSTORE               | None
    [    0x9a] | MLOAD                | None
    [    0x9b] | SWAP1                | None
    [    0x9c] | DUP2                 | None
    [    0x9d] | SWAP1                | None
    [    0x9e] | SUB                  | None
    [    0x9f] | PUSH1                | ['0x20']
    [    0xa1] | ADD                  | None
    [    0xa2] | SWAP1                | None
    [    0xa3] | RETURN               | None

所以我们可以得出结论:

    
    
    address public a;
    会被编译成(==)
    function a() public returns (address) {
        return a;
    }
    
    #
    
    address private a;
    function c() public returns (address) {
        return a;
    }
    等同于下面的变量定义(≈)
    address public c;

公有函数和私有函数的区别也很简单，公有函数会被编译进主函数中，能通过`CALLDATA`进行调用，而私有函数则只能在其他公有函数中进行调用，无法直接通过设置`CALLDATA`来调用私有函数

##### 回退函数和payable

在智能合约中，函数都能设置一个`payable`，还有一个特殊的回退函数，下面用实例来介绍回退函数

比如之前的测试合约加上了回退函数:

    
    
    function() {
        prize += 1;
    }

则主函数的反编译代码就变成了:

    
    
    def main():
        if CALLDATASIZE >= 4:
            data = CALLDATA[:4]
            if data == 0x6b59084d:
                return test1()
            elif data == 0x8da5cb5b:
                return owner()
            elif data == 0xcaf44683:
                return test2()
            elif data == 0xe3ac5d26:
                return prize()
        assert msg.value == 0
        prize += 1
        exit()

当`CALLDATA`和该合约中的函数匹配失败时，将会从抛异常，表示执行失败退出，变成调用回退函数

每一个函数，包括回退函数都可以加一个关键字:
`payable`，表示可以给该函数转帐，从OPCODE层面讲，没有`payable`关键字的函数比有`payable`的函数多了一段代码:

    
    
    JUMPDEST             | None
    CALLVALUE            | None
    DUP1                 | None
    ISZERO               | None
    PUSH2                | ['0x8e']
    JUMPI                | None
    PUSH1                | ['0x0']
    DUP1                 | None
    REVERT               | None

反编译成python，就是:

    
    
    assert msg.value == 0

`REVERT`是异常退出指令，当交易的金额大于0时，则异常退出，交易失败

##### 函数参数

函数获取数据的方式只有两种，一个是从storage中获取数据，另一个就是接受用户传参，当函数hash表匹配成功时，我们可以知道该函数的参数个数，和各个参数的类型，但是当hash表匹配失败时，我们仍然可以获取该函数参数的个数，因为获取参数和主函数、`payable`检查一样，在OPCODE层面也有固定模型:

比如上面的测试合约，调动`test2`函数的固定模型就是: `main -> payable check -> get args -> 执行函数代码`

获取参数的OPCODE如下

    
    
    ; 0xAF: loc_af
    [    0xaf] | JUMPDEST             | None
    [    0xb0] | POP                  | None
    [    0xb1] | PUSH2                | ['0xd1']
    [    0xb4] | PUSH20               | ['0xffffffffffffffffffffffffffffffffffffffff']
    [    0xc9] | PUSH1                | ['0x4']
    [    0xcb] | CALLDATALOAD         | None
    [    0xcc] | AND                  | None
    [    0xcd] | PUSH2                | ['0x18f']
    [    0xd0] | JUMP                 | None

函数test2的参数`p = CALLDATA[4:4+0x20]`

如果有第二个参数，则是`arg2 = CALLDATA[4+0x20:4+0x40]`，以此类推

所以智能合约中，调用函数的规则就是`data = sha3(func_name)[:4] + *args`

但是，上面的规则仅限于定长类型的参数，如果参数是`string`这种不定长的变量类型时，固定模型仍然不变，但是在从`calldata`获取数据的方法，变得不同了，定长的变量是通过调用`CALLDATALOAD`，把值存入栈中，而`string`类型的变量，因为长度不定，会超过256bits的原因，使用的是`calldatacopy`把参数存入MEM

可以看看`function test3(string a) public {}`函数获取参数的代码:

    
    
    ; 0xB2: loc_b2
    [    0xb2] | JUMPDEST             | None
    [    0xb3] | POP                  | None
    [    0xb4] | PUSH1                | ['0x40']
    [    0xb6] | DUP1                 | None
    [    0xb7] | MLOAD                | None
    [    0xb8] | PUSH1                | ['0x20']
    [    0xba] | PUSH1                | ['0x4']
    [    0xbc] | DUP1                 | None
    [    0xbd] | CALLDATALOAD         | None
    [    0xbe] | DUP1                 | None
    [    0xbf] | DUP3                 | None
    [    0xc0] | ADD                  | None
    [    0xc1] | CALLDATALOAD         | None
    [    0xc2] | PUSH1                | ['0x1f']
    [    0xc4] | DUP2                 | None
    [    0xc5] | ADD                  | None
    [    0xc6] | DUP5                 | None
    [    0xc7] | SWAP1                | None
    [    0xc8] | DIV                  | None
    [    0xc9] | DUP5                 | None
    [    0xca] | MUL                  | None
    [    0xcb] | DUP6                 | None
    [    0xcc] | ADD                  | None
    [    0xcd] | DUP5                 | None
    [    0xce] | ADD                  | None
    [    0xcf] | SWAP1                | None
    [    0xd0] | SWAP6                | None
    [    0xd1] | MSTORE               | None
    [    0xd2] | DUP5                 | None
    [    0xd3] | DUP5                 | None
    [    0xd4] | MSTORE               | None
    [    0xd5] | PUSH2                | ['0xff']
    [    0xd8] | SWAP5                | None
    [    0xd9] | CALLDATASIZE         | None
    [    0xda] | SWAP5                | None
    [    0xdb] | SWAP3                | None
    [    0xdc] | SWAP4                | None
    [    0xdd] | PUSH1                | ['0x24']
    [    0xdf] | SWAP4                | None
    [    0xe0] | SWAP3                | None
    [    0xe1] | DUP5                 | None
    [    0xe2] | ADD                  | None
    [    0xe3] | SWAP2                | None
    [    0xe4] | SWAP1                | None
    [    0xe5] | DUP2                 | None
    [    0xe6] | SWAP1                | None
    [    0xe7] | DUP5                 | None
    [    0xe8] | ADD                  | None
    [    0xe9] | DUP4                 | None
    [    0xea] | DUP3                 | None
    [    0xeb] | DUP1                 | None
    [    0xec] | DUP3                 | None
    [    0xed] | DUP5                 | None
    [    0xee] | CALLDATACOPY         | None
    [    0xef] | POP                  | None
    [    0xf0] | SWAP5                | None
    [    0xf1] | SWAP8                | None
    [    0xf2] | POP                  | None
    [    0xf3] | PUSH2                | ['0x166']
    [    0xf6] | SWAP7                | None
    [    0xf7] | POP                  | None
    [    0xf8] | POP                  | None
    [    0xf9] | POP                  | None
    [    0xfa] | POP                  | None
    [    0xfb] | POP                  | None
    [    0xfc] | POP                  | None
    [    0xfd] | POP                  | None
    [    0xfe] | JUMP                 | None

传入的变长参数是一个结构体:

    
    
    struct string_arg {
        uint offset;
        uint length;
        string data;
    }

`offset+4`表示的是当前参数的`length`的偏移，length为data的长度，data就是用户输入的字符串数据

当有多个变长参数时: `function test3(string a, string b) public {}`

`calldata`的格式如下: `sha3(func)[:4] + a.offset + b.offset + a.length + a.data +
b.length + b.data`

翻译成py代码如下:

    
    
    def test3():
        offset = data[4:0x24]
        length = data[offset+4:offset+4+0x20]
        a = data[offset+4+0x20:length]
        offset = data[0x24:0x24+0x20]
        length = data[offset+4:offset+4+0x20]
        b = data[offset+4+0x20:length]

因为参数有固定的模型，因此就算没有从hash表中匹配到函数名，也可以判断出函数参数的个数，但是要想知道变量类型，只能区分出定长、变长变量，具体是`uint`还是`address`，则需要从函数代码，变量的使用中进行判断

##### 变量类型的分辨

在智能合约的OPCDOE中，变量也是有特征的

比如一个`address`变量总会 `& 0xffffffffffffffffffffffffffffffffffffffff`:

    
    
    PUSH1                | ['0x0']
    SLOAD                | None
    PUSH20               | ['0xffffffffffffffffffffffffffffffffffffffff']
    AND                  | None

上一篇说的mapping和array的储存模型，可以根据SHA3的计算方式知道是映射变量还是数组变量

再比如，`uint`变量因为等同于`uint256`，所以使用`SLOAD`获取以后不会再进行`AND`计算，但是`uint8`却会计算`& 0xff`

所以我们可以`SLOAD`指令的参数和后面紧跟的计算，来判断出变量类型

#### 智能合约代码结构

##### 部署合约

在区块链上，要同步/发布任何信息，都是通过发送交易来进行的，用之前的测试合约来举例，合约地址为:
`0xc9fbe313dc1d6a1c542edca21d1104c338676ffd`, 创建合约的交易地址为:
`0x6cf9d5fe298c7e1b84f4805adddba43e7ffc8d8ffe658b4c3708f42ed94d90ed`

查看下该交易的相关信息:

    
    
    > eth.getTransaction("0x6cf9d5fe298c7e1b84f4805adddba43e7ffc8d8ffe658b4c3708f42ed94d90ed")
    {
      blockHash: "0x7f684a294f39e16ba1e82a3b6d2fc3a1e82ef023b5fb52261f9a89d831a24ed5",
      blockNumber: 3607048,
      from: "0x0109dea8b64d87a26e7fe9af6400375099c78fdd",
      gas: 171331,
      gasPrice: 1000000000,
      hash: "0x6cf9d5fe298c7e1b84f4805adddba43e7ffc8d8ffe658b4c3708f42ed94d90ed",
      input: "0x608060405234801561001057600080fd5b5060008054600160a060020a0319163317905561016f806100326000396000f3006080604052600436106100615763ffffffff7c01000000000000000000000000000000000000000000000000000000006000350416636b59084d81146100665780638da5cb5b146100a4578063caf44683146100b9578063e3ac5d26146100d3575b600080fd5b34801561007257600080fd5b5061007b6100fa565b6040805173ffffffffffffffffffffffffffffffffffffffff9092168252519081900360200190f35b3480156100b057600080fd5b5061007b610116565b3480156100c557600080fd5b506100d1600435610132565b005b3480156100df57600080fd5b506100e861013d565b60408051918252519081900360200190f35b60005473ffffffffffffffffffffffffffffffffffffffff1690565b60005473ffffffffffffffffffffffffffffffffffffffff1681565b600180549091019055565b600154815600a165627a7a7230582040d052fef9322403cb3c1de27683a42a845e091972de4c264134dd575b14ee4e0029",
      nonce: 228,
      r: "0xa08f0cd907207af4de54f9f63f3c9a959c3e960ef56f7900d205648edbd848c6",
      s: "0x5bb99e4ab9fe76371e4d67a30208aeac558b2989a6c783d08b979239c8221a88",
      to: null,
      transactionIndex: 4,
      v: "0x2a",
      value: 0
    }

我们可以看出来，想一个空目标发送`OPCODE`的交易就是创建合约的交易，但是在交易信息中，却不包含合约地址，那么合约地址是怎么得到的呢?

    
    
    function addressFrom(address _origin, uint _nonce) public pure returns (address) {
            if(_nonce == 0x00)     return address(keccak256(byte(0xd6), byte(0x94), _origin, byte(0x80)));
            if(_nonce <= 0x7f)     return address(keccak256(byte(0xd6), byte(0x94), _origin, byte(_nonce)));
            if(_nonce <= 0xff)     return address(keccak256(byte(0xd7), byte(0x94), _origin, byte(0x81), uint8(_nonce)));
            if(_nonce <= 0xffff)   return address(keccak256(byte(0xd8), byte(0x94), _origin, byte(0x82), uint16(_nonce)));
            if(_nonce <= 0xffffff) return address(keccak256(byte(0xd9), byte(0x94), _origin, byte(0x83), uint24(_nonce)));
            return address(keccak256(byte(0xda), byte(0x94), _origin, byte(0x84), uint32(_nonce))); // more than 2^32 nonces not realistic
        }

智能合约的地址由创建合约的账号和`nonce`决定，`nonce`用来记录用户发送的交易个数，在每个交易中都有该字段，现在根据上面的信息来计算下合约地址:

    
    
    # 创建合约的账号 from: "0x0109dea8b64d87a26e7fe9af6400375099c78fdd",
    # nonce: 228 = 0xe4 => 0x7f < 0xe4 < 0xff
    >>> sha3.keccak_256(binascii.unhexlify("d7" + "94" + "0109dea8b64d87a26e7fe9af6400375099c78fdd" + "81e4")).hexdigest()[-40:]
    'c9fbe313dc1d6a1c542edca21d1104c338676ffd'

##### 创建合约代码

一个智能合约的OPCODE分为两种，一个是编译器编译好后的创建合约代码，还是合约部署好以后runtime代码，之前我们看的，研究的都是runtime代码，现在来看看创建合约代码，创建合约代码可以在创建合约交易的`input`数据总获取，上面已经把数据粘贴出来了，反汇编出指令如下:

    
    
    ; 0x0: main
    [     0x0] | PUSH1                | ['0x80']
    [     0x2] | PUSH1                | ['0x40']
    [     0x4] | MSTORE               | None
    [     0x5] | CALLVALUE            | None
    [     0x6] | DUP1                 | None
    [     0x7] | ISZERO               | None
    [     0x8] | PUSH2                | ['0x10']
    [     0xb] | JUMPI                | None
    [     0xc] | PUSH1                | ['0x0']
    [     0xe] | DUP1                 | None
    [     0xf] | REVERT               | None
    ----------------------------------------------------------------    ; 0x10: loc_10
    [    0x10] | JUMPDEST             | None
    [    0x11] | POP                  | None
    [    0x12] | PUSH1                | ['0x0']
    [    0x14] | DUP1                 | None
    [    0x15] | SLOAD                | None
    [    0x16] | PUSH1                | ['0x1']
    [    0x18] | PUSH1                | ['0xa0']
    [    0x1a] | PUSH1                | ['0x2']
    [    0x1c] | EXP                  | None
    [    0x1d] | SUB                  | None
    [    0x1e] | NOT                  | None
    [    0x1f] | AND                  | None
    [    0x20] | CALLER               | None
    [    0x21] | OR                   | None
    [    0x22] | SWAP1                | None
    [    0x23] | SSTORE               | None
    [    0x24] | PUSH2                | ['0x24f']
    [    0x27] | DUP1                 | None
    [    0x28] | PUSH2                | ['0x32']
    [    0x2b] | PUSH1                | ['0x0']
    [    0x2d] | CODECOPY             | None
    [    0x2e] | PUSH1                | ['0x0']
    [    0x30] | RETURN               | None

代码逻辑很简单，就是执行了合约的构造函数，并且返回了合约的runtime代码，该合约的构造函数为:

    
    
    function Test() {
        owner = msg.sender;
    }

因为没有`payable`关键字，所以开头是一个check代码`assert msg.value == 0`

然后就是对`owner`变量的赋值，当执行完构造函数后，就是把runtime代码复制到内存中:

    
    
    CODECOPY(0, 0x32, 0x24f)  # mem[0:0+0x24f] = CODE[0x32:0x32+0x24f]

最后在把runtime代码返回: `return mem[0:0x24f]`

在完全了解合约是如何部署的之后，也许可以写一个OPCODE混淆的CTF逆向题

#### 总结

通过了解EVM的数据结构模型，不仅可以加快对OPCODE的逆向速度，对于编写反编译脚本也有非常大的帮助，可以对反编译出来的代码进行优化，使得更加接近源码。

在对智能合约的OPCODE有了一定的了解后，后续准备先写一个EVM的调试器，虽然Remix已经有了一个非常优秀的调试器了，但是却需要有`Solidity`源代码，这无法满足我测试无源码的OPCODE的工作需求。所以请期待下篇《以太坊智能合约OPCODE逆向之调试器篇》

* * *

针对目前主流的以太坊应用，知道创宇提供专业权威的智能合约审计服务，规避因合约安全问题导致的财产损失，为各类以太坊应用安全保驾护航。

知道创宇404智能合约安全审计团队： <https://www.scanv.com/lca/index.html>  
联系电话：(086) 136 8133 5016(沈经理，工作日:10:00-18:00)

欢迎扫码咨询：
![](https://images.seebug.org/content/images/2018/06/95677dc3-cb3e-474e-832e-8b79ec73bfa9.png-w331s)

#### 引用

  1. <https://github.com/comaeio/porosity>
  2. <https://github.com/meyer9/ethdasm>
  3. <https://github.com/trailofbits/evm-opcodes>
  4. <http://solidity.readthedocs.io/en/v0.4.21/assembly.html>
  5. <https://github.com/trailofbits/ida-evm>
  6. <https://github.com/trailofbits/ida-evm/blob/master/known_hashes.py>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/640/>

