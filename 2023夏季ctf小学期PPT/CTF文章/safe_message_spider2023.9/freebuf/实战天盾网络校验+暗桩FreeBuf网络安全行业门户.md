# 0x1

![1.png](https://image.3001.net/images/20220414/1649899158_625776969b9cb4dddb20f.png!small)

#### 刚打开就显示 有新版 然后自动退出了 说明有更新了现在这个不能用了 拉进od开整

![2.png](https://image.3001.net/images/20220414/1649899159_62577697361a13c3d71ab.png!small)

因为有弹窗，通过弹窗下手，MessageBoxA直接下断

![3.png](https://image.3001.net/images/20220414/1649899159_62577697cd4498194c6bf.png!small)

成功断下，观看堆栈，发现传入进来的值就是提示新版

![4.png](https://image.3001.net/images/20220414/1649899160_62577698834efd6b10830.png!small)

一路f8 走出来走到用户层 可以发现这个call就是提示更新的 然后下面这个就是退出call

![5.png](https://image.3001.net/images/20220414/1649899161_6257769912dca85f5b630.png!small)

我们直接nop掉 然后直接运行起来

![6.png](https://image.3001.net/images/20220414/1649899161_62577699887f80edbe685.png!small)

发现成功运行起来，提示更新就被我们干掉了

![7.png](https://image.3001.net/images/20220414/1649899162_6257769a1d6f836f778e4.png!small)

点击登录显示你未充值到期 假的卡号肯定没用 我们直接搜索字符串

![8.png](https://image.3001.net/images/20220414/1649899162_6257769a90e23048ac76e.png!small)

点E 然后进去401000基地址来查询字符串

![31.png](https://image.3001.net/images/20220414/1649899163_6257769b2a1f7b7c9bd6a.png!small)

发现了 原来是用了天盾网络验证 这里就好办了 这里做一个小知识

解决天盾网络验证分为4个步骤

1.判断登录

2.判断合法

3.判断算法

4.判断时间

我们一步一步解决掉他们

![9.png](https://image.3001.net/images/20220414/1649899163_6257769bad5943a63c7b2.png!small)

先是找到登录中跳转过去

![10.png](https://image.3001.net/images/20220414/1649899164_6257769c5c72cb2932ade.png!small)

直接这里的每一个call都用回车进去查看

![11.png](https://image.3001.net/images/20220414/1649899164_6257769ceae24f324b16c.png!small)

像这种 FF25这种就是自带函数 而不是人自定义的

![12.png](https://image.3001.net/images/20220414/1649899165_6257769d84d2ca1ec08a3.png!small)

往下翻找到这个函数 应该就是登录判断函数

![13.png](https://image.3001.net/images/20220414/1649899166_6257769e2c0e1213ad76c.png!small)

直接改变判断 然后跳转出来

![14.png](https://image.3001.net/images/20220414/1649899166_6257769eba428d0244287.png!small)

找到合法

![15.png](https://image.3001.net/images/20220414/1649899167_6257769f449ed41bb24fb.png!small)

直接retn返回不进行判断

![16.png](https://image.3001.net/images/20220414/1649899167_6257769fcc0e29eb7ef59.png!small)

查找时间-1

![17.png](https://image.3001.net/images/20220414/1649899168_625776a0655f248801451.png!small)

进行更改时间 注意不要超出这个00 不然就是改变代码

![18.png](https://image.3001.net/images/20220414/1649899168_625776a0ef3fffce655bb.png!small)

找到算法识别跳转 一直往下翻到红色算法区域结束 第一个jnz判断的位置

![19.png](https://image.3001.net/images/20220414/1649899169_625776a180214a458da47.png!small)

![20.png](https://image.3001.net/images/20220414/1649899170_625776a20267269419577.png!small)

直接改成jmp

![21.png](https://image.3001.net/images/20220414/1649899170_625776a2791f34e28a1a2.png!small)

![22.png](https://image.3001.net/images/20220414/1649899170_625776a2f2923eb0ee7e7.png!small)

往下翻再把jge改成jmp

## 0x2

这时候我以为已经成功了，但是直接闪退退出了。发现可能有暗桩或其他判断

![23.png](https://image.3001.net/images/20220414/1649899171_625776a38067326732830.png!small)

一直单步跟进到这里，发现在这里闪退了

![24.png](https://image.3001.net/images/20220414/1649899172_625776a40c70a1f5b9ba0.png!small)

进去一看发现又进行了一次合法判断，直接改成retn返回

## 0x3

破解成功

![26.png](https://image.3001.net/images/20220414/1649899172_625776a4868234958b8c2.png!small)

## 0x4

破解成功后发现，里面的功能无法运行，感觉没有完全破解完，后又发现往路径里填写了一个key.txt

![27.png](https://image.3001.net/images/20220414/1649899173_625776a512380c14e70e0.png!small)

里面填了一个也不知道什么用的数字，重新回去调试

## 0x5

![25.png](https://image.3001.net/images/20220414/1649899173_625776a58fc26d86c7c9e.png!small)

![28.png](https://image.3001.net/images/20220414/1649899174_625776a61dfb6fa5486d7.png!small)

搜索字符串发现确实有这个key.txt 但是不知道做了什么

![29.png](https://image.3001.net/images/20220414/1649899174_625776a69f8a9960dbc58.png!small)

往上走发现 有一个判断跳过了这个key.txt

![30.png](https://image.3001.net/images/20220414/1649899175_625776a71e4c814491044.png!small)

直接尝试nop掉这个判断，功能最终成功运行。

## 0x6总结

1.天盾校验就是这么一个过程或者大多数的网络校验都是如此，只需要一直调试。

2.发现有暗桩不要害怕，能断下单步调试，有耐心就能找到。

3.发现破解了还是不能运行，不要着急，仔细观察软件还做了什么，大胆尝试，猜测，改变。

