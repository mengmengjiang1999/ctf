# Monica's Casino

本文由长亭科技区块链安全负责人于晓航撰写

  

##  ****# 0x00 概况 ****

这题属于中等偏难，是个EVM JOP类型蜜罐合约题目。需要逆向合约opcode，找一些gadgets来准备好栈以及操作控制流，利用后门。

##  ****# 0x01 JOP思路 ****

Constructor里有jump指令，跳到参数a，通过分析合约创建交易的input data可以知道是0x9b。

在remix里调试一下可以看到0x9b指向的是参数b的开头，刚好这里有一个jumpdest字节码所以程序可以合法跳到这里，执行后面的指令。b开头这段指令做的事很简单：将b的后半段字节copy到memory上，然后直接return这些字节。所以这一步其实就是替换掉了合约在链上的runtime
code，所以runtime code其实跟源码看到的不一样。

严格来说现在runtimecode可以是任意内容，这样的话会需要很多比较无聊的逆向工作，但这里可以尝试的一个技巧是，把源码里constructor的jump一行注释掉，然后编译得到原本的runtime
code，然后比较这两个版本。会发现这里我在‘有效字节码部分’只patch了1个字节。

![21.png](https://image.3001.net/images/20191025/1571980994_5db286c26daa5.png!small)  

如上，第一处diff是1字节，第二处是metadata，这个理论上来说对不同源码是应该不一样的（但这里是题目有意设置的不同）。

第一个字节把push32(0x7f)改成了dup3(0x82)，实际上把后面的字节从‘数据段’解放为了‘代码段’。然后其实后续的这些字节就是源码中salt的值。

于是这部分字节可以被解释为这段opcode：

![22.png](https://image.3001.net/images/20191025/1571981011_5db286d3aa668.png!small)

  

这里可以看到有了第一个任意跳转，也就是后门的入口，然后还有挺多事要做。通过msg.sender[msg.sender[-1]]这个字节可以控制地址。

接下来目标是控制合约触发event，即log字节码，也就是需要跳到log前的某个jumpdest。

从这里可能会有人尝试直接一步到位跳到log，但其实会发现那个地方的地址要高于0xff没法通过1字节控制。

因此我们需要跳转到小于0x100的某个位置，总之最后落在salt的后半段，然后再通过inputdata的其他字节控制跳转到下一个gadget。

可能会注意到的另一个事情是在最近的‘jumpdest’和‘log’之间，存在一些修改栈内容的操作，因此我们需要利用其他gadgets大概准备一下stack的内容。

接下来的步骤是需要跳转到metadata段来处理一些stack/memory的存取操作（正常情况下metadata段不会被执行）

Ummm，我觉得写到这里差不多，还是希望把其他乐趣留给大家来探索接下来的解法。后面的解题应该还会有几个trick没有提到。

##  ****# 0x02 未初始化结构体变量 ****

  
在走到后门入口之前有另一个trick需要处理一下。未初始化结构体变量也是一个很典型的蜜罐合约，在旧版编译器下，‘PlayerInfo
pi’这种写法其实定义了一个指向0的指针，刚好也是secret存储的位置，因此pi.addr =
msg.sender其实悄悄把secret修改成了msg.sender。

所以lottery函数的参数应该是攻击者自己的地址。这个设计像是后门的守卫。总之这样我们就可以触发到后门了。

另一个点是，由于我们需要给lottery提供的inputdata要长于uint256来触发JOP部分，可能需要用web3脚本或者部署一个代理合约来构造发送任意payload。然后为了减轻选手的压力，我写了一个docker
image作为完整的独立debug环境，作为题目附件可供下载，启动后里面有一个包含题目环境的私链，与ropsten上的环境几乎一模一样，也提供了几乎所有解题需要用到的库、脚本样例啥的。

##  ****# 0x03 POC ****

![23.png](https://image.3001.net/images/20191025/1571981037_5db286eda39c2.png!small)

如果你有debug环境的话直接run
docker，记得暴露一下rpc/ws接口，然后把remix连到docker里的私链来debug。如果没有的话用ropsten也是一样的。

接下来配置一下ws_provider跑poc就完事儿了，应该会发一条交易触发SendFlag。可以尝试debug poc这条交易来理解一些细节。

关于如何解密flagdata，请参考‘Monica’s Bank Writeups’。

感谢，希望大家喜欢这小破题。

完事儿

FYI: <http://xhyumiracle.com/defcon27-village-talk/>

#  

  

