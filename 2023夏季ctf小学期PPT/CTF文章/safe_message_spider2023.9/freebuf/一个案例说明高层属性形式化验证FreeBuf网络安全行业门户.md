![640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy](https://mmbiz.qpic.cn/mmbiz_jpg/7icia3gpsuCVBKh17tTgmtrMZuQ4SqXpvrP7LgrsibNWSXlC2BZLIq23TuId2fiaTUk7QznoavYhTaDXDEmasRp2QA/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)

**![1.png](https://image.3001.net/images/20200110/1578622397_5e17ddbd7522d.png!small)  
**

**  
**

**验证软件功能介绍**

01

 **Beosin-VaaS** 的业务逻辑验证软件，是一款用来 **检测智能合约上层业务逻辑漏洞** 的软件。

基于合约的白皮书，软件利用形式化方法，首先对单个函数进行属性的描述，在对单个函数进行属性的验证并通过后，基于这些已验证属性，抽取出高层的状态属性，进而对上层属性进行自动推理和验证，若属性不满足，则会返回一条反例路径。

 **案例介绍** （界面：合约）

02

我们可以以下面这个 **案例** 来举例说明。

  

![2.png](https://image.3001.net/images/20200110/1578622412_5e17ddcc17a29.png!small)![3.png](https://image.3001.net/images/20200110/1578622412_5e17ddcc7cddd.png!small)![4.png](https://image.3001.net/images/20200110/1578622412_5e17ddcc5c01c.png!small)  

  

  

![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_png/7icia3gpsuCVBKh17tTgmtrMZuQ4SqXpvrWhdfuWG58icKZE5cCN3B3hkSP6uVQrv3JBeAibQCfLU9ibCXwDjShxt6g/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_png/7icia3gpsuCVBKh17tTgmtrMZuQ4SqXpvrauTpx450Ban7PE6CKpMjiaQSGFXZic8SJKKLHexrYkjcCTmLUjhOyfCA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_png/7icia3gpsuCVBKh17tTgmtrMZuQ4SqXpvrX8MA2EpXVE9vApdlCmxOiaYhEpadJia9qeWNkhia91uvlCXUnEkiab505w/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_png/7icia3gpsuCVBKh17tTgmtrMZuQ4SqXpvrdvZSq1doXL9OWTYcuQtxOquedfrD17x99kPpchKQ2veGkwXxo0qQtQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)

![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_png/7icia3gpsuCVBKh17tTgmtrMZuQ4SqXpvrWhdfuWG58icKZE5cCN3B3hkSP6uVQrv3JBeAibQCfLU9ibCXwDjShxt6g/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)

这里我们考虑进行一次众筹，目标是在部署后deadline时间内，收集fundingGoal个以太币。如果在该期间收集到相应数额个以太币，则表明众筹成功，在这种情况下，受益人可以提取资金。否则，将认为众筹失败，并允许用户要求退款。众筹合约本身继承了token合约，并直接收集众筹期间投入的所有资金。

 **具体合约和函数说明**

03

我们可以进一步得知，该项目包含了一个 **Crowdsale合约** ，继承一个 **token合约** 。

  * 在众筹合约中，构造函数会初始化设置众筹的截止时间deadline，并添加众筹目标额度fundingGoal，并在合约中硬编码受益人的地址beneficiary；

  * 然后会提供回调函数，提供给用户来参与投资，在开放众筹期间，只要未达到目标额度，就允许所有用户进行投资；

  * 提供一个checkGoalReached()函数，如果达到众筹目标，或者达到了截止时间，就可以修改状态标识，关闭众筹；

  * 然后会提供响应的transfer()和issue()函数接口，用于在众筹分配代币，以及能够进行代币的交易

  * 提供一个safeWithdrawal()函数，如果众筹成功，受益人能够取出投资人的钱；

  * 最后还提供一个safeClaimRefund()退款接口，如果众筹失败，用户可以通过该接口完成撤资。

 **结果分析和说明**

（界面：合约，

中间切换到编写的属性）

04

我们这里已经完成了单个函数的属性验证，可以确认单个函数的功能是 **符合其属性规范** 的，在此基础上，编写上层属性进行验证。

以下，我们编写的上层属性有两条，一条是 **p1**
，含义是总是能够满足，一旦调用了safeWithdrawal()或者safeClaimRefund()，另一个函数就不能够被成功调用。

  *  **P1:**

![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_png/7icia3gpsuCVBKh17tTgmtrMZuQ4SqXpvrGDEzWVnNAyCsCPqCI067icicjmzUTv816N34bSerEjKhHR7oHg91PU0A/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)

另一条是 **p2** ，表示无论任何情况，只要成功调用了函数safeWithdrawal()，众筹到的总和amountRaised就不会小于目标值。

  *  **p2:**

![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_png/7icia3gpsuCVBKh17tTgmtrMZuQ4SqXpvrqj4ibO7qSvKFtviaWgpqfh2LgXHyDxLYAZ2ucZNjGOQPdCibkXEGicjibug/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)

好，我们这里进行 **上层属性** 的验证。（进行验证操作）

  

![5.png](https://image.3001.net/images/20200110/1578622422_5e17ddd62a1a8.png!small)  

  

![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_png/7icia3gpsuCVBKh17tTgmtrMZuQ4SqXpvrWhdfuWG58icKZE5cCN3B3hkSP6uVQrv3JBeAibQCfLU9ibCXwDjShxt6g/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_png/7icia3gpsuCVBKh17tTgmtrMZuQ4SqXpvrhmCw3jm45mHxI1pTCiaZs2EpaZNib2rrxcRJCRNjnibmewpBwTm1QLgJg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_png/7icia3gpsuCVBKh17tTgmtrMZuQ4SqXpvrLgmuZ8DCsUkZ2MWdk410iaVdeJRFEjiald95zEgkEJ05bMVd6gh5gNRA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)

![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_png/7icia3gpsuCVBKh17tTgmtrMZuQ4SqXpvrWhdfuWG58icKZE5cCN3B3hkSP6uVQrv3JBeAibQCfLU9ibCXwDjShxt6g/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)

得到输出结果，可以看到属性2是满足的，而属性1并不满足。我们查看一下反例的 **可视化路径**
，可以看到，确实存在一条路径，safeWithdrawal()函数和safeClaimRefund()函数可以先后被执行成功。

回到合约中，根据所提供的 **反例路径**
，可以看到，发生该情况是调用回调函数一段时间后，当前时间超过了众筹的截止时间，众筹的资金总量没有达到目标fundingGoal，在checkGoalReached()关闭众筹之后，此时的合约状态，用户是可以调用
safeClaimRefund选择退款的。

但是我们可以从结果中发现，此时依旧可以调用成功回调函数投资，那么就出现了后面的状态可能，在众筹失败之后，依旧有用户有意或者无意参与了投资，导致投资的总额超过了目标。

此时，能够再次调用checkGoalReached()函数结束众筹，改变 **状态标识**
，最终受益人能够在按原始需求，众筹失败的情况下，且有用户选择退款之后，依旧调用checkGoalReached()取出了所有的投资资金。

最终回到合约，我们发现，其实是由于用于投资的回调函数缺少了检查当前事件是否超过了截止日期，进而导致的合约漏洞。

可以看到，在该例子中，所有的函数其实是满足其自身的属性并实现了相应的功能的，但是由于在合约之间、函数之间的 **调用和关联关系**
，才导致出现了这样一个漏洞。而该属性验证工具的作用也在于此，它能够更加高效地发现 **逻辑属性漏洞。**

  

  

