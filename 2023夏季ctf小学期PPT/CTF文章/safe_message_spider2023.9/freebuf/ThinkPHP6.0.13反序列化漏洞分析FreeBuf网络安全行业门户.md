# 1\. 前言

最近有点闲下来了，不找点事干比较难受，打算找点漏洞分析一下，于是就打算看看TP的一些漏洞，ThinkPHP6.0.13是TP的最新版，八月份有师傅提交了一个issue指出TP存在反序列化问题，网上也有些师傅分析了一波，不过断点下的比较多，而且部分方法没有阐明其用途，所以我也尝试详细的分析一波。下面先给出POC

![image.png](https://image.3001.net/images/20221009/1665306308_63428ec48a661741c4973.png!small)

# 2\. 分析

首先看看POC的起始点

![image.png](https://image.3001.net/images/20221009/1665306309_63428ec57feef37199ce9.png!small)

![image.png](https://image.3001.net/images/20221009/1665306310_63428ec646d6a90e3d427.png!small)

发现起始点在Psr6Cache这个类，我们进入这个类，不过没有发现__destruct或者__wakeup等常见的反序列化起始魔术方法，推测应该在其父类AbstractCache这个抽象类中。跟入AbstractCache类

![image.png](https://image.3001.net/images/20221009/1665306311_63428ec7046691b02100f.png!small)

如图，成功发现本次反序列化链子的起始类。这里我们可以控制autosave这个属性为false，从而进入save方法。

回到Psr6Cache类查看这个方法

![image.png](https://image.3001.net/images/20221009/1665306311_63428ec7b8fb7b6b48e7a.png!small)

可以发现，pool属性和key属性我们都可控。因此可能存在两种路线，调用不同类的同名方法（getItem）。或者是直接尝试触发__call方法。我们来看看POC作者是怎么让反序列化进行下去的。

![image.png](https://image.3001.net/images/20221009/1665306312_63428ec888d8fe808f8b3.png!small)

作者用构造方法传入了exp，exp其实就是在实例化Channel类。我们进入Channel类查看

![image.png](https://image.3001.net/images/20221009/1665306313_63428ec943b38fb1f0d77.png!small)

Channel类中有一个__call方法，那么作者是选择触发__call来让链子继续下去。这个call方法接受了两个参数，method是写死的(getItem)，parameters是可控的（即前面可控的key属性）

![image.png](https://image.3001.net/images/20221009/1665306314_63428eca051bd3e83f4ae.png!small)

跟入log方法查看，其接受三个传参（但是其实对后续的链子没啥用），传入record方法

![image.png](https://image.3001.net/images/20221009/1665306314_63428ecabead324d67789.png!small)

跟入record方法

![image.png](https://image.3001.net/images/20221009/1665306315_63428ecb7c9e5adb65e85.png!small)

再返回查看作者的POC，发现其控制lazy属性为false，让函数进入最后一个if分支执行save方法

![image.png](https://image.3001.net/images/20221009/1665306316_63428ecc5b884ba7d7f0e.png!small)

那么save方法应该是比较关键的方法了，跟入save方法，这里面有三个可能被利用的点，作者选择了哪一个呢？

![image.png](https://image.3001.net/images/20221009/1665306317_63428ecd1919af3b1f7aa.png!small)

根据POC不难发现作者选择了控制logger属性，利用构造函数对其赋值，令其为Socket类的对象

![image.png](https://image.3001.net/images/20221009/1665306317_63428ecdd3f80869e443f.png!small)

![image.png](https://image.3001.net/images/20221009/1665306318_63428ece89cdc8709c959.png!small)

在这个类中，我们找到了一个复杂的同名方法，其中有大量的操作。

![image.png](https://image.3001.net/images/20221009/1665306319_63428ecf3346cb7c73797.png!small)

我们继续来看作者是怎么构造的，作者控制config属性，给其赋值为数组。数组有如下内容

![image.png](https://image.3001.net/images/20221009/1665306319_63428ecfd9a08fe0758f6.png!small)

关键在于这两个键值，作者控制config，让程序运行到调用invoke方法的分支

![image.png](https://image.3001.net/images/20221009/1665306320_63428ed0a15f04d5bc076.png!small)

同时，app属性可控，作者令app属性为App类的对象，我们进入App类

![image.png](https://image.3001.net/images/20221009/1665306321_63428ed1870a4e07f7af0.png!small)

这里先看看App类的的exists方法的情况，在其父类中找到了这个方法

![image.png](https://image.3001.net/images/20221009/1665306322_63428ed25f424818acd18.png!small)

继续往后，这里对App类进行了唯一一个操作，控制了instances属性的值。这里控制其值是为了进入Request类，并且执行url方法

![image.png](https://image.3001.net/images/20221009/1665306323_63428ed3346eda8d25c9c.png!small)

![image.png](https://image.3001.net/images/20221009/1665306323_63428ed3f295ba8901bdd.png!small)

作者在这里对Request类做出唯一的操纵，就是控制url属性的值。可以看出，如果url属性存在，那么就会进入第一个分支，其值等于本身。

![image.png](https://image.3001.net/images/20221009/1665306324_63428ed4d0452988da39b.png!small)

同时又注意到，complete我们之前传入的是true。因此最终返回的结果就是$this->domain().$url，url我们已经控制了，那么domain方法返回什么呢？

![image.png](https://image.3001.net/images/20221009/1665306325_63428ed597b2dd1414d0f.png!small)

OK，这点我们就不用看了。分析了这么多，我们得到了$currentUri最后的值，就是：

<http://localhost/><?php system(\'calc\'); exit(); ?>

![image.png](https://image.3001.net/images/20221009/1665306326_63428ed661ff671dff97a.png!small)

currentUri作为一个数组被传入invoke了，根据链子的长度，达到invoke，我们的反序列化之旅就快结束了

![image.png](https://image.3001.net/images/20221009/1665306327_63428ed71f9c01a7c2fd8.png!small)

查看invoke，App类找不到这个方法，在他的父类里找到了这个方法

![image.png](https://image.3001.net/images/20221009/1665306327_63428ed7d8a4e2d772f26.png!small)

这里可以看到。这个函数内有三分支走向，那么最终会走向哪里呢？根据我们之前$config[‘format_head’]的传入，
首先我们传入的这个对象不是Closure的实例或者子类，并且也不满足第二个分支的条件

![image.png](https://image.3001.net/images/20221009/1665306328_63428ed8b6942044131b3.png!small)

因此进入到到第三个分支。我们跟进invokeMethod()方法。这里传入的$callabel就是[new
\think\view\driver\Php,'display']、而$vars就是[‘<http://localhost/><?php
system(\'calc\'); exit(); ?>’]

![image.png](https://image.3001.net/images/20221009/1665306329_63428ed967c328a62eeca.png!small)

注意，我们传入的$method是数组，因此进入第一个分支。把new \think\view\driver\Php
（即对象）赋值给$class，’display’（即方法名）赋值给新的$method。

然后下面进行了一个判断，如果$class是对象，那么其值就为它本身，因为我们传入的是对象，所以这里没什么变化。然后进入最关键的代码

可以看到，把对象new \think\view\driver\Php 以及方法 display传入了ReflectionMethod。

![image.png](https://image.3001.net/images/20221009/1665306330_63428eda2a7d695e24262.png!small)

在最后，调用invokeArgs方法，传入了new \think\view\driver\Php对象，同时传入了$args

![image.png](https://image.3001.net/images/20221009/1665306331_63428edb016c04b1750b4.png!small)

那么args是什么呢？

![image.png](https://image.3001.net/images/20221009/1665306331_63428edbb1fdae885d2e6.png!small)

我们跟入之后发现是一个处理函数，因为本人比较懒，而且到这都快分析完了，就不去硬读了，直接给结论，总之我们传入的 $vars ，也即
[‘<http://localhost/><?php system(\'calc\'); exit(); ?>’] 其中的关键部分<?php
system(\'calc\'); exit(); ?>保留了下来，并且进入到了后续的传参中

![image.png](https://image.3001.net/images/20221009/1665306332_63428edc73934e9566d9b.png!small)

继续往后看，对于这个函数(invokeArgs)，可以简单的类比call_user_func()，因此最后的关键代码其实只有这两行

![image.png](https://image.3001.net/images/20221009/1665306333_63428edd71262e6e11824.png!small)

也即

$reflect = new ReflectionMethod(new \think\view\driver\Php,’display’);

return $reflect->invokeArgs(new \think\view\driver\Php,’ <?php
system(\'calc\'); exit(); ?>’)

常看tp反序列化的朋友就知道，已经结束咧！毕竟调用display方法了。但是上述这个调用ReflectionMethod类的操作到底是什么呢？我们可以借助如下实例来演示。所以说这玩意和call_user_func很像

![image.png](https://image.3001.net/images/20221009/1665306334_63428ede4baa87e621d90.png!small)

最后是display方法，没什么好说的了，content传入display方法中，eval执行命令了

![image.png](https://image.3001.net/images/20221009/1665306334_63428edef2e02392f8c22.png!small)

# 3\. 结语

TP的链子一如既往的有意思（以及复杂），特别是最后的ReflectionMethod类的用法上，如果不了解这个类以及类中的方法组合可以实现类似call_user_func函数的作用的话，那么就很容易错过这样一个精彩的漏洞。

