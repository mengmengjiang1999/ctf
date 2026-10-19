# Monica's Bank

本文由长亭科技区块链安全负责人于晓航撰写

  

# # 0x00 概况

这题是几种Solidity常见经典漏洞的组合，如果对Solidity熟悉的话会相对简单。

# # 0x01 思路

在 _transferBalance_
函数里，由于整数溢出require并没啥用，只需要随意transfer任意小余额到其他地址就可以获得大量balance。

然后可以buy 1个credit，这里的随机数是完全可预测的，只需要把随机数那段代码复制到攻击合约里就好了。

最后一步是重入攻击，跟hint里说的一样，这个类似DAO的加强版攻击。大概意思是只需要重入1次就好，而不是多次重入，这样可以触发 _creditOf[]
-= amount_ 的整数溢出。

在DAO攻击中，目标函数和攻击合约的fallback都被调用了很多次，直到gas耗尽，调用链底层抛出异常，由于 _.call.value_
特点是返回false而非继续向上抛出异常，所以这整个交易不会被revert，然后 _.call.value_ 之后的代码们只会被执行1次。

在‘加强版’攻击里，由于我们主动结束第二次fallback， _.call.value_ 之后的代码会被执行2次，从而触发整数下溢，达成目标。

# # 0x02 解密Flag

触发 _SendFlag_ 后，后台脚本会把加密flag数据放在交易里发送给攻击者的地址，即tx.origin。

数据是用tx.origin的公钥加密的，因此可以用私钥，和提供的解密脚本来解密。

# # 0x03 POC

![1.png](https://image.3001.net/images/20191025/1571977125_5db277a56edaf.png!small)

然后用解密脚本来获得flag。

# # 0x04 彩蛋

``![2.png](https://image.3001.net/images/20191025/1571977135_5db277afd6191.png!small)  

