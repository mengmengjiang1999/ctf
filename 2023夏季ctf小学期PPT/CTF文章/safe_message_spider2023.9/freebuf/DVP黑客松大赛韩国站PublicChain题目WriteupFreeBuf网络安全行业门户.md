# Writeup 1: Remote DoS

本文由 **PeckShield** 漏洞研究总监 **Edward Lo** 撰写  

  

这是公链项目的第一题，参赛者需要找到漏洞并进行攻击造成Remote DoS。服务器上跑的是经过修改的geth结点，而问题点就在EVM中。

首先来看看EVM正常执行流程：

![1.png](https://image.3001.net/images/20191028/1572255774_5db6b81eaaeaf.png!small)

  

EVM在执行合约时，会一步一步提取其中的OPCode，并做相对应的检查：  

  * 1\. OPCode需要的传参是否已放到栈(stack)上，是否有足够空间能放回传值；

  * 2\. EVM目前是否在readonly模式(例如以static_call方式呼叫)，若是则需符合规则，不能对链上状态有任何改动(例如转帐)；

![2.png](https://image.3001.net/images/20191028/1572255813_5db6b84543e2f.png!small)  

3\. 计算OPCode需要的内存大小，并根据目前的内存情况决定如何收取gas费用并扩容内存。

接下来我们以OPCode mstore8为例，来看看到底怎麽计算。  

![3.png](https://image.3001.net/images/20191028/1572255895_5db6b897b95b5.png!small)  

如上所示，p是offset，v是想写入的内容  

![4.png](https://image.3001.net/images/20191028/1572255912_5db6b8a89e437.png!small)  

EVM会调用memoryMStore8计算回传所需要的内存大小，接着调用gasMStore8来计算所需的gas费用  

![5.png](https://image.3001.net/images/20191028/1572255932_5db6b8bc86a2a.png!small)

  

这道题目就是将memoryMStore8注解掉，如此一来会造成两个问题：

  * 1\. EVM不会计算收取gas，因为memorySize永远为0

  * 2\. 内存不会扩容，攻击者可以在任意offset写入一个可控byte内容

如此一来，只需布置会调用mstore8的恶意合约便可以进行攻击

![6.png](https://image.3001.net/images/20191028/1572255979_5db6b8eb2465f.png!small)  

  

# Writeup 2: RCE

基于上一道题目，我们可以在任意offset写一个byte，理论上便能透过它执行RCE。此题的技术难度跟水平要求较高，攻击者必须结合漏洞并布置巧妙构思过的恶意合约，将shellcode写入远端节点来完成RCE  

  

