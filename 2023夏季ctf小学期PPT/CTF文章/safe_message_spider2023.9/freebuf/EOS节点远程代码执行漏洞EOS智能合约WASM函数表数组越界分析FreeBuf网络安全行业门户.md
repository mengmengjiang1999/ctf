***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **6月2日凌晨，EOS
1.0正式版发布，同一时间，EOS官方就近期出现的一系列高危漏洞做出回应，向发现漏洞的360公司安全团队公开致谢，对其中3个漏洞分别给出1万美元的赏金，同时表示，欢迎安全社区人员共同努力保证EOS1.0软件安全性的持续提高。关于这个漏洞到底是怎么一回事儿，下面我们来做一波详细分析。**

![0.jpg](https://image.3001.net/images/20180604/15280930656709.jpg!small)

## 漏洞描述

近日，360安全专家发现EOS区块链系统在解析WASM文件时，会出现缓冲区溢出的问题，而攻击者将能够利用这个缓冲区溢出漏洞对EOS系统实施攻击。在该漏洞的帮助下，攻击者将能够向EOS节点服务器上传恶意智能合约，当节点服务器完成对智能合约的解析之后，恶意Payload将会在服务器中执行，并完成远程接管。成功接管远程节点服务器之后，攻击者将能够把恶意智能合约封装到新的区块中，并进一步控制整个EOS网络。

### 漏洞时间轴

> 2018-5-11：研究人员发现EOS系统中存在缓冲区溢出漏洞；
>
> 2018-5-28：设计并开发漏洞PoC；
>
> 2018-5-28：将漏洞报告提交给厂商；
>
> 2018-5-29：厂商在Github托管代码库中修复漏洞，并关闭问题跟踪项；
>
> 2018-5-29：提醒厂商漏洞未完全修复。

我们尝试通过Telegram跟Daniel
Larimer取得联系，并将漏洞信息直接报告给他。他给我们的回复是：在漏洞被成功修复之前，他们不会发布新的EOS版本，并希望我们能够通过非公开方式先将漏洞信息提交给他。

![1.jpg](https://image.3001.net/images/20180604/15280930964995.jpg!small)  

他提供了他的邮箱，我们也将漏洞报告发送到他邮箱了。

![2.jpg](https://image.3001.net/images/20180604/15280931067244.jpg!small)![2-1.jpg](https://image.3001.net/images/20180604/15280931838187.jpg!small)  

Daniel表示，这个漏洞成功修复之后会给我们公开致谢。

![3.jpg](https://image.3001.net/images/20180604/15280931949059.jpg!small)  

## 漏洞技术细节

这个缓冲区溢出漏洞存在于libraries/chain/webassembly/binaryen.cpp（第78行）文件中的binaryen_runtime::instantiate_module函数：

    
    
    for (auto& segment : module->table.segments) {
    Address offset = ConstantExpressionRunner<TrivialGlobalManager>(globals).visit(segment.offset).value.geti32();
    assert(offset + segment.data.size() <= module->table.initial);
    for (size_t i = 0; i != segment.data.size(); ++i) {
    table[offset + i] = segment.data[i]; <= OOB write here !
    }
    }  
    

上述代码中的table指的是一个std::vector，其中包含函数表中的名称。在将元素存储到表中时，代码并没有对|offset|域的内容进行检测。需要注意的是，在设置具体的值之前，代码中写了一个断言，按理来说它就应该对偏移量的值进行检测，但不幸的是，|assert|只能在调试版本中正常运行，因此它在正式的发布版本中并不能发挥它的作用。

table首先会在语句执行之前进行初始化：

    
    
    table.resize(module->table.initial);

这里的|module->table.initial|是直接从WASM文件中的函数表声明部分中读取来的，有效值的范围为0-1024。

除此之外，|offset|域的值也是从WASM文件的数据域中读取来的，这个值是一个32位值。

所以基本上说，在这个漏洞的帮助下，我们可以在table向量的内存地址后面越界写入任意内容。

## 漏洞复现过程

1.编译EOS代码最新发布的版本：

    
    
    ./eosio-build.sh

2.启动EOS节点，如有必要用户还需要按照下面给出的教程完成配置：

    
    
    https://github.com/EOSIO/eos/wiki/Tutorial-Getting-Started-With-Contracts

3.设置包含漏洞的合约：

这里我们给大家提供了一个包含漏洞的PoC，在这个PoC中我们让 |offset|
字段直接引用地址0xfffffff，然后成功触发缓冲区溢出漏洞并造成程序崩溃。

测试PoC：

    
    
    cd poc
    cleos set contract eosio ../poc -p eosio  
    

如果一切顺利的话，我们将能够看到nodeos进程报出segment fault错误。崩溃信息如下：

    
    
    (gdb) c
    Continuing.
    Program received signal SIGSEGV, Segmentation fault.
    0x0000000000a32f7c in eosio::chain::webassembly::binaryen::binaryen_runtime::instantiate_module(char const*, unsigned long, std::vector<unsigned char, std::allocator<unsigned char> >) ()
    (gdb) x/i $pc
    => 0xa32f7c <_ZN5eosio5chain11webassembly8binaryen16binaryen_runtime18instantiate_moduleEPKcmSt6vectorIhSaIhEE+2972>:   mov    %rcx,(%rdx,%rax,1)
    (gdb) p $rdx
    $1 = 59699184
    (gdb) p $rax
    $2 = 34359738360
    Here |rdx| points to the start of the |table| vector,
    And |rax| is 0x7FFFFFFF8, which holds the value of |offset| * 8.  
    

## 利用该漏洞实现远程代码执行

在该漏洞的帮助下，攻击者可以在nodeos进程中实现远程代码执行。首先，攻击者需要利用该漏洞将恶意合约上传到目标节点，并让节点对恶意合约进行解析，在真实的攻击场景下，攻击者可以向EOS主网络发布恶意合约。当EOS节点完成对恶意合约的解析并成功触发漏洞之后，攻击者将能够控制目标节点。接下来，攻击者将能够窃取目标节点中的私钥并控制新区块中的内容。更重要的是，攻击者还可以将恶意合约封装成一个新的区块并添加到主网络中，然后实现对整个EOS网络的攻击。

我们所设计的PoC已经在Ubuntu（64位）平台上的nodeos进行了测试，攻击过程如下：

1.将恶意合约上传到nodeos服务器；

2.服务器中的nodeos进程对恶意合约进行解析并触发漏洞；

3.利用漏洞写入恶意代码，并在WASM文件的帮助下实现任意内存读写操作；

4.漏洞利用成功后，攻击者将能够拿到反向shell；

### 攻击演示视频

### 漏洞修复  

Bytemaster在EOS的GitHub托管项目中专门建立了issue以跟进该问题：

![5.png](https://image.3001.net/images/20180604/15280934105479.png!small)  

漏洞修复代码：

![6.png](https://image.3001.net/images/20180604/15280934196214.png!small)  

不过根据漏洞发现者Yuki所提交的信息，该漏洞目前并没有被完全修复，在32位平台的进程运行过程中仍然存在安全问题：

![7.png](https://image.3001.net/images/20180604/15280934293976.png!small)  

***本文由Alpha_h4ck整理编译，参考来源：[360技术博客](http://blogs.360.cn/blog/eos-node-remote-code-execution-vulnerability/?from=timeline&isappinstalled=0)，转载请注明来自FreeBuf.COM**

