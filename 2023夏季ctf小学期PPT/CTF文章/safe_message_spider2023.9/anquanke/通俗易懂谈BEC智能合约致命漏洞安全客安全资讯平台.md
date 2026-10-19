# 通俗易懂谈BEC智能合约致命漏洞

阅读量 **156487**

|评论 **6**

发布时间 : 2018-06-05 14:00:23

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0118bb70b1c89ab35b.jpg)

##

## 安全事件

最近，智能合约漏洞很火。  
让我们再来看一下4月22日BeautyChain（BEC）的智能合约中一个毁灭性的漏洞。

**BeautyChain** **团队宣布，BEC代币在4月22日出现异常。攻击者通过智能合约漏洞成功转账了10^58 BEC到两个指定的地址。**

具体交易详情[https://etherscan.io/tx/0xad89ff16fd1ebe3a0a7cf4ed282302c06626c1af33221ebe0d3a470aba4a660f](https://etherscan.io/tx/0xad89ff16fd1ebe3a0a7cf4ed282302c06626c1af33221ebe0d3a470aba4a660f)

攻击者到底是怎么攻击的？为什么能转账这么大的BEC？

* * *

****

## 智能合约代码

**首先我们来看BEC转账的智能合约代码**

**function batchTransfer(address[] _receivers, uint256 _value) public
whenNotPaused returns (bool) {**

**uint cnt = _receivers.length;**

**uint256 amount = uint256(cnt) * _value;**

**require(cnt > 0 && cnt <= 20);**

**require(_value > 0 && balances[msg.sender] >= amount);**

****

**balances[msg.sender] = balances[msg.sender].sub(amount);**

**for (uint i = 0; i < cnt; i++) {**

**balances[_receivers[i]] = balances[_receivers[i]].add(_value);**

**Transfer(msg.sender, _receivers[i], _value);**

**}**

**return true;**

**}**

以上的代码是[Solidity语言](http://solidity-cn.readthedocs.io/zh/develop/index.html)，是一门面向合约的，为实现智能合约而创建的高级编程语言。

****

## 变量类型

在读代码之前我们先来简单了解一下以下几个变量类型( **Solidity** ):

**address**

**160** **位的值，且不允许任何算数操作。**

* * *

**uint 8**

8位无符号整数，范围是0到2^8减1 **(0-255)**

* * *

**uint256**

256位无符号整数，范围是0到2^256减1  
**(0-115792089237316195423570985008687907853269984665640564039457584007913129639935)**

**敲黑板，玩手机的同学注意看这里，这里是考试重点哦**

那么，我们请看如下神奇的化学反应

**定义变量uint a**

a的取值范围是0到255

**_当a=255，我们对a加 1，a会变成 0。  
当a=255，我们对a加 2，a会变成 1。  
当a=0，我们对a减 1，a会变成 255。  
当a=0，我们对a减 2，a会变成 255。_**

**a** **的值超过了它实际的取值范围，然后会得出后面的值，这种情况叫溢出。**

* * *

****

## 代码解读

**知道了这几个变量类型，下面我们一行一行的来读这段代码。**

**第一行**

**function batchTransfer(address[] _receivers, uint256 _value) public
whenNotPaused returns (bool)**

**函数有两个参数:**

  * _receivers —————转账接收人，address类型的变量数组，是一个160位的值。
  * _value ———————-转账数量，uint256的状态变量，256位的无符号整数。

定义函数batchTransfer，功能主要是实现转账，接收两个参数，定义了参数的取值范围。

**第二行**

uint cnt = _receivers.length;

计算接收人地址对应地址数组的长度，即转账给多少人。

**第三行**

uint256 amount = uint256(cnt) * _value;

把unit类型的cnt参数值强制转换为uint256然后乘以转账数量_value 并赋值给uint256类型的amount变量。

**第四行**

require(cnt > 0 && cnt <= 20);

**require** **函数**

require的入参判定为 **false** **，** 则终止函数，恢复所有对状态和以太币账户的变动，并且也不会消耗 gas 。

判断cnt是否大于0且cnt是否小于等于20

**第五行**

require(_value > 0 && balances[msg.sender] >= amount);

**参数解读:**

  * _value—————————————转账数量
  * balances[msg.sender]————-转账人余额
  * amount————————————转账总数量

判断_value是否大于0且转账人的余额balances[msg.sender]大于等于转账总金额amount

**第六行**

balances[msg.sender] = balances[msg.sender].sub(amount);

计算转账人的余额，使用当前余额balances[msg.sender]减去转账总数量

**第七行**

for (uint i = 0; i < cnt; i++) {

这里是一个循环，循环次数为cnt（遍历转账地址）

**第八行**

balances[_receivers[i]] = balances[_receivers[i]].add(_value);

当i有具体的值时，balances[_receivers[i]]表示转账接收人，这里是表示转账人给转账接收人_value数量的币。

**第九行**

Transfer(msg.sender, _receivers[i], _value);

保存转账记录

**第十行**

return true;

函数返回为True

* * *

****

## 代码流程

**OK** **，我们读了完整的代码，接下来请看一个流程图**

函数的流程是这样，那么攻击者到底是怎么攻击的呢？他为什么这么秀？同样都是九年义务教育……

****

## 攻击过程

其实，他只是细心了一点，所使用的攻击方法并不高明啊， **你且听我慢慢道来，注意看，别走神啊。**

****

###  **交易详情**

我们首先看这笔详细的交易：  

**好了，我们从图可以看到**

转账接收人有两个地址，即balances[_receivers]:

000000000000000000000000b4d30cac5124b46c2df0cf3e3e1be05f42119033  
0000000000000000000000000e823ffe018727585eaf5bc769fa80472f76c3d7

转账数量为_value:

8000000000000000000000000000000000000000000000000000000000000000（十六进制）

转10进制为

57896044618658097711785492504343953926634992332820282019728792003956564819968

* * *

****

###  **实战**

OK，接下来我们来走函数流程

**第一行**

function batchTransfer(address[] _receivers, uint256 _value) public
whenNotPaused returns (bool)

正常执行

**第二行**

uint cnt = _receivers.length  
由于这里有两个转账接收人地址，address数组长度为2，所以cnt为2，类型为uint

**第三行**

uint256 amount = uint256(cnt) * _value;

_value=57896044618658097711785492504343953926634992332820282019728792003956564819968  
cnt=2  
 **两者相乘得到amount，类型为uint256**  

即amount=115792089237316195423570985008687907853269984665640564039457584007913129639936

* * *

**考试重点用上了，记不住的同学去前面看看。**

amount的类型为uint256，那么按照理论，它的最大取值是0到2^256减1，即

**115792089237316195423570985008687907853269984665640564039457584007913129639935**

**所以！！！**

**amount**
**瞬间从115792089237316195423570985008687907853269984665640564039457584007913129639936变成了0**  
第三行得到的结果：amount=0

**第四行**

require(cnt > 0 && cnt <= 20);

cnt=2，2肯定大于0，2当然也小于等于20  
 **所以这个条件成立，require函数返回值为True。**

**第五行**

require(_value > 0 && balances[msg.sender] >= amount);

_value=57896044618658097711785492504343953926634992332820282019728792003956564819968

_value肯定是大于0，转账人的余额balances[msg.sender]肯定是大于等于0的。  
 **所以这个条件同样成立，require函数返回值为True。**

**第六行**

balances[msg.sender] = balances[msg.sender].sub(amount);

前面的条件都成立，那么代码会执行到这。

这行代码是求转账人转完账以后剩下的余额，amount为0 ， **那么转账人的余额其实没变！！！**

**第七行**

for (uint i = 0; i < cnt; i++)

cnt=2，该行代码表示执行两次后面的操作

**第八行**

balances[_receivers[i]] = balances[_receivers[i]].add(_value);  
i=0时，转账接收人balances[_receivers[0]]的余额加_value  
i=1时，转账接收人balances[_receivers[1]]的余额加_value

看到这里其实我们就很明白了吧。

攻击者给以下两个转账接收人

**000000000000000000000000b4d30cac5124b46c2df0cf3e3e1be05f42119033**  
 **0000000000000000000000000e823ffe018727585eaf5bc769fa80472f76c3d7**

**转了  
_value=57896044618658097711785492504343953926634992332820282019728792003956564819968个币**

更可恶的是，攻击者执行完这个操作，转账人的余额根本没变，看代码第六行的执行结果。

**第九行**

Transfer(msg.sender, _receivers[i], _value);  
这里只是把上面两个转账记录保存。

**第十行**

return true;

函数返回为True

* * *

****

## 小结

**千里之堤毁于蚁穴！**

就一个溢出漏洞，导致BEC的市值瞬间变0

这么傻的问题，写代码的人是写睡着了吗？？？

不，其实他根本没睡着啊，人家还用了SafeMath里的add函数和sub函数

**我们看看什么是[ SafeMath](https://ethereumdev.io/safemath-protect-overflows/)函数**

**/****

*** @title SafeMath**

*** @dev Math operations with safety checks that throw on error**

***/**

**library SafeMath {**

**function mul(uint256 a, uint256 b) internal constant returns (uint256) {**

**uint256 c = a * b;**

**assert(a == 0 || c / a == b);**

**return c;**

**}**

**function div(uint256 a, uint256 b) internal constant returns (uint256) {**

**// assert(b > 0); // Solidity automatically throws when dividing by 0**

**uint256 c = a / b;**

**// assert(a == b * c + a % b); // There is no case in which this doesn’t
hold**

**return c;**

**}**

****

**function sub(uint256 a, uint256 b) internal constant returns (uint256) {**

**assert(b <= a);**

**return a – b;**

**}**

****

**function add(uint256 a, uint256 b) internal constant returns (uint256) {**

**uint256 c = a + b;**

**assert(c >= a);**

**return c;**

**}**

**}**

注意看这一段

**function mul(uint256 a, uint256 b) internal constant returns (uint256) {**

**uint256 c = a * b;**

**assert(a == 0 || c / a == b);**

**return c;**

**}**

这里是乘法计算，计算出乘法的结果后会用assert函数去验证结果是否正确。

* * *

**回到我们前面的dis第三行代码执行后的结果**

_value=57896044618658097711785492504343953926634992332820282019728792003956564819968  
cnt=2  
 **两者相乘得到amount，类型为uint256**

由于 **溢出** ，amount=0

赋值给mul函数即

c=amount，而amount=0，则c=0  
a=cnt, 而cnt=2，则a=2  
b=_value  
得出  
b=57896044618658097711785492504343953926634992332820282019728792003956564819968

那么c/a==b这个式子不成立，导致assert函数执行会报错，assert报错，那么就不会执行后面的代码，也就不会发生溢出。

**也就是说，写这段代码的人，加减法他用了SafeMath里面的add函数和sub函数，但是却没有用里面的乘法函数mul**

* * *

****

###  如何防止这样的漏洞？

  * 肯定是要用SafeMath函数啊，你加减法用了，乘法不用，你咋这么皮呢
  * 代码上线前要做代码审计啊亲，强调多少遍了！
  * 合理使用变量类型，了解清楚变量的范围
  * 一定要考虑到溢出！一定要考虑到溢出！一定要考虑到溢出！重要的事情说三遍。

* * *

**写这么通俗易懂，你应该看懂了吧？？看懂了就给点个赞呗！**

****

## 参考

[https://medium.com/secbit-media/a-disastrous-vulnerability-found-in-smart-contracts-of-beautychain-bec-dbf24ddbc30e](https://medium.com/secbit-media/a-disastrous-vulnerability-found-in-smart-contracts-of-beautychain-bec-dbf24ddbc30e)  
[https://solidity-cn.readthedocs.io](https://solidity-cn.readthedocs.io/)

##

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **区块链威胁情报** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/146702](/post/id/146702)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [区块链](/tag/区块链)
  * [智能合约](/tag/智能合约)
  * [BEC](/tag/BEC)

 **+1** __5赞

 __收藏

![](https://p2.ssl.qhimg.com/t0179a11df02bf59d82.png) 区块链威胁情报

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

