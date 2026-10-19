近期截获一款木马，从它的签名和域名分析特征来看和之前其他安全公司分析的木马同属于“百家集团木马”，只是行为有所改变，变得更加隐蔽，同时也绑定并且通过网络下发的途径在受害者机器上运行相应的危害性的木马，下面就对此木马做简要分析。

**一、 签名与访问域名的作者**

![1.png](https://image.3001.net/images/20180524/15271620817426.png!small)

木马域名的作者：

![2.png](https://image.3001.net/images/20180524/15271620996558.png!small)

![3.png](https://image.3001.net/images/20180524/15271621084545.png!small)

**二、** **运行原理分析**

**1.初始化会释放两个内存dll**

![4.png](https://image.3001.net/images/20180524/15271621218726.png!small)

内存地址:

(1) byte_42B36D

![5.png](https://image.3001.net/images/20180524/15271621429322.png!small)

(2) byte_42C775

![6.png](https://image.3001.net/images/20180524/15271621513929.png!small)

2.分别获取两个内存dll的接口保存起来方便调用

![7.png](https://image.3001.net/images/20180524/15271622439708.png!small)

  

![8.png](https://image.3001.net/images/20180524/15271622569967.png!small)

![9.png](https://image.3001.net/images/20180524/15271622683827.png!small)  
![10.png](https://image.3001.net/images/20180524/15271622757254.png!small)

它的接口都是用接口号方式获取，下面是提取出来的两个dll

![11.png](https://image.3001.net/images/20180524/15271628525283.png!small)

其中一个内存dll有个10个导出接口

![12.png](https://image.3001.net/images/20180524/15271629466702.png!small)

另外一个内存dll，有22个接口

![13.png](https://image.3001.net/images/20180524/15271629606114.png!small)

  
![14.png](https://image.3001.net/images/20180524/15271630386447.png!small)  
  

**2.执行dll 内的函数**

 **看运行的虚函数指针表**

**![15.png](https://image.3001.net/images/20180524/15271631477955.png!small)**

初始化完成后就进入的 **0x401000** ,里面被 **TMD** 虚拟机虚拟代码， **0x44E157** 函数虚拟加壳了。

![16.png](https://image.3001.net/images/20180524/15271631665055.png!small)  
一开始会获取木马当前的版本：  

![17.png](https://image.3001.net/images/20180524/15271632207400.png!small)  

执行完毕后，跳出虚拟机后执行了会执行到地址401131地址函数

![18.png](https://image.3001.net/images/20180524/15271632529313.png!small)

然后继续执行了2号模块的1号接口初始化网络

![19.png](https://image.3001.net/images/20180524/15271633048971.png!small)  

![20.png](https://image.3001.net/images/20180524/15271633197219.png!small)![21.png](https://image.3001.net/images/20180524/1527163353990.png!small)  

然后接着继续执行2号模块的3号接口

![22.png](https://image.3001.net/images/20180524/15271633717923.png!small)

![23.png](https://image.3001.net/images/20180524/15271634107266.png!small)  

下面2号模块的3号导出接口

![25.png](https://image.3001.net/images/20180524/15271634527488.png!small)  

从IDA下看到函数功能如下  

![26.png](https://image.3001.net/images/20180524/15271634694800.png!small)

该线程会从服务器请求证书key

![27.png](https://image.3001.net/images/20180524/15271635121500.png!small)  

然后继续进入虚拟机,对该数据进行操作，操作结束后，再次跳出虚拟机后就会执行2号模块的4号接口

![28.png](https://image.3001.net/images/20180524/15271635955026.png!small)  

注意这时的接口参数中有个木马域名: **[www.xxxxxx.cn](http://www.xxxxxx.cn)**

![29.png](https://image.3001.net/images/20180524/15271636237173.png!small)

4号接口的功能大概如下，会在本地开启一个本地网络服务器

![30.png](https://image.3001.net/images/20180524/15271636541560.png!small)

![31.png](https://image.3001.net/images/20180524/15271636623492.png!small)  

![32.png](https://image.3001.net/images/20180524/15271636744065.png!small)  

![33.png](https://image.3001.net/images/20180524/15271636837584.png!small)

这个函数开始bind(),绑定本地端口0.  

![34.png](https://image.3001.net/images/20180524/15271637159375.png!small)

接着就会链接 **[www.xxxxx.cn](http://www.xxxxx.cn/)** **的** 服务器  

![35.png](https://image.3001.net/images/20180524/1527163729883.png!small)

Connect 服务器的443端口  

![36.png](https://image.3001.net/images/20180524/15271637538461.png!small)

接着执行5号接口，该接口会向服务器发送数据

![37.png](https://image.3001.net/images/20180524/1527163814531.png!small)

发完数据后，然后会执行6号接口，6号接口是个关闭socket  

![38.png](https://image.3001.net/images/20180524/15271638353212.png!small)

注意的是3号接口线程会反复从服务器接口数据，控制木马的行为  

总结下来，该木马大致行为如下：

![39.png](https://image.3001.net/images/20180524/15271638666131.png!small)
至此这个木马的大概运行流程分析完毕，它的隐蔽性比较强，同时又是一个签名证书的木马，它的危害主要在木马制作者通过销售绑定网络带入其他针对性的木马侵害受害者机器，所以要针对这样的危害做针对性的研究与防御。

