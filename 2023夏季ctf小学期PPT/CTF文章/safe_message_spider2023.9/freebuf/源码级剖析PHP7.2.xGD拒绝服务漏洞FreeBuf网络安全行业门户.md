***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：chilau，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

 **触发条件：**

> php 7.2.x，开启gd库。只需要三行代码即可完成！

 **我在本地调试php的时候发现某个老代码能够直接把php给crash掉，因此成文。**

![1.PNG](https://image.3001.net/images/20180302/15199594375219.png!small)  

php没有报错，直接死掉了，应该是内部逻辑有问题。再传到服务器上试试：

![1-2.PNG](https://image.3001.net/images/20180302/15199595507646.png!small)  

啊哈，一样的结果。触发这个问题的代码如下：

    
    
    $im=imagecreate(100,100);
    imageantialias($im,true);
    imageline($im,0,0,10,10,0xffffff);
    

话不多说，上vs调试。先看调用堆栈吧。

![2.PNG](https://image.3001.net/images/20180302/15199596126503.png!small)

从这里可以看出是在GD库的画像素点的地方出了错，被调试器断在了gdImageSetAAPixelColor这个函数里。

![3.PNG](https://image.3001.net/images/20180302/15199596121204.png!small)

再看对应代码，访问了gdImagePtr结构体中的一个成员，导致访问违例。我们再从即时窗口检查一下：

![4.PNG](https://image.3001.net/images/20180302/15199596122863.png!small)

没错，tpixels是个空指针！

那tpixels是干啥的呢？在gd.h里面有如下说明：

    
    
    /* Truecolor flag and pixels. New 2.0 fields appear here at the
    end to minimize breakage of existing object code. */
    int trueColor;
    int ** tpixels;

看来是和真彩色相关的东西，我们再沿着调用堆栈往前看。

![5.PNG](https://image.3001.net/images/20180302/15199596138205.png!small)

这里是gdImageAALine函数，一个个点地画线，干的是苦力活。从gdImageLine里调用了它：

![6.PNG](https://image.3001.net/images/20180302/15199596135297.png!small)

这里的条件判断是是否开启了 **防锯齿** 功能。如果我们调用 _imageantialias_ 函数打开这个功能，那么就会走这里来。

![7.PNG](https://image.3001.net/images/20180302/15199596136075.png!small)

上面图里就是我们从php调用的imageline函数的实现啦，非常简单。可以看出图片是真彩色的时候它会默认开启防锯齿功能。

这里问题就在于，我们创建（imagecreate）的图片不是真彩色的图，而后我们手动开启了防锯齿（imageantialias），调用进去想当然地把它当作一张真彩色图，从而导致了错误。

最后我们来看看两个函数的不同：

![8.PNG](https://image.3001.net/images/20180302/15199596134567.png!small)

跟进去，可以看到imagecreate函数调用的gdImageCreate里直接把真彩色相关的成员设为了null。

与之对比，imagecreatetruecolor函数调用的gdImageCreateTrueColor函数里为每个像素点都分配了对应内存并初始化为0了：

![10-gdImageCreateTrueColor.PNG](https://image.3001.net/images/20180302/15199628028236.png!small)

总结一下，从上面分析可以看出，触发这个问题的条件有3个：

> 1.php版本为7.2.x且开启了gd库
>
> 2.创建了非真彩色图且开启抗锯齿
>
> 3.在创建的图句柄上进行像素点写入

导致这个问题的原因还是代码修改考虑不周全，引入了新的漏洞；没有对所有可能条件进行测试，所以从php 7.2.0一直到php 7.2.4都还存在问题。

已经向php官方报告，如果正在生产环境使用相关版本请退回旧版本，旧版本里不存在这个问题。

 ***本文原创作者：chilau，本文属FreeBuf原创奖励计划，未经许可禁止转载**

