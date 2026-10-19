## 一 、开篇

 **在某次复现"dedecms前台任意用户登录漏洞重现及分析"漏洞过程中, 发现这个漏洞的利用点是需要注册并审核通过一个"0000001"用户,
但在实际操作中,发现很多站点注册用户后需要邮件校验,但实际没有配置SMTP, 也就不可能发出邮件,遂分析了其邮件校验的hash生成算法,
进而发现伪随机问题,本文不会从邮件hash算法入手,而是从cookie算法分析出发, 分析漏洞的原理和利用方法. 全文分析使用dedecms v5.7
sp2, 但就漏洞本身而言是全版本均存在的。**  

## 二 、本篇简介

主要研究和分析一下在PHP5和PHP7下mtrand/mtsrand和rand/srand函数的特性, 从中找到一些结论, 方便后面对算法的分析与评估。

## 三、黑盒测试

针对PHP5场景下编写一些测试脚本,观察得出基本的函数特征

 **3.1 编写脚本:**

    
    
     vi test_1.php
    
    <?php  
    echo "rand:\n";  
    srand(0);  
    ?>
    

**运行结果:**

    
    
     1804289383
    
    vi test_2.php
    
    <?php  
    echo "mt_rand:\n";  
    mt_srand(0);  
    echo mt_rand();  
    echo "\n";  
    echo mt_rand();  
    echo "\n";  
    mt_srand(0);  
    echo mt_rand();  
    echo "\n";  
      
    echo "rand:\n";  
    srand(0);  
    echo rand();  
    echo "\n";  
    echo rand();  
    echo "\n";  
    srand(0);  
    echo rand();  
    echo "\n";  
      
    echo "mt_rand:\n";  
    mt_srand(0);  
    echo mt_rand();  
    ?>

 **运行结果:**

    
    
    963932192  
    1273124119  
    963932192  
      
    1804289383  
    846930886  
    1804289383  
      
    963932192

 **3.2小结**

1.mtrand/mtsrand不影响 rand/srand

2.在mtsrand的作用下,mtrand次数会重置, 在srand的作用下,rand次数会重置

3.rand和mt_rand在同seed,同次数下,值不同

## 四、白盒审计

针对PHP5和PHP7的C代码进行分析,选用的代码仓库如下

    
    
    PHP5: https://github.com/php/php-src/blob/d31e8a9a85efea54db0b647424f6c4485d71db8b/ext/standard/rand.c
    
    PHP7: https://github.com/php/php-src/blob/becda2e0418d4efb55fca40b1170ca67cfbdb4e0/ext/standard/mt_rand.c

TIPS: 如何定位php版本对应到的源码, 可以根据php版本发布时间, 在git仓库找commit, commit时间在发布时间前一段时间的应该就是:)

###  **1\. PHP5:**

1.1 rand/srand 默认使用的是C语言的原生函数:

![图片1.png](https://image.3001.net/images/20200421/1587453959_5e9ea007c9d59.png!small)

1.2 mt_rand使用的是php实现的一套算法:

![图片2.png](https://image.3001.net/images/20200421/1587453972_5e9ea014d8f5a.png!small)

###  **2\. PHP7:**

2.1
mt_rand使用的是php实现的一套算法:![图片3.png](https://image.3001.net/images/20200421/1587453999_5e9ea02fb4a5d.png!small)

2.2 rand和mtrand, srand和mtsrand完全等价:

rand.c

![图片4.png](https://image.3001.net/images/20200421/1587454041_5e9ea0590840f.png!small)

###  **3\. 共性:**

3.1 调用一次mt_srand不仅设置了seed,而且重置了次数:

![图片5.png](https://image.3001.net/images/20200421/1587454071_5e9ea077981f1.png!small)

3.2 每调用一次mt_rand相当于次数+1:

![图片6.png](https://image.3001.net/images/20200421/1587454086_5e9ea086c99e2.png!small)

3.3 调用rand,若之前没有调用srand, 那么会默认调用一次; 调用mtrand,若之前没有调用mtsrand, 那么会默认调用一次:

mt_rand:

![图片7.png](https://image.3001.net/images/20200421/1587454109_5e9ea09d87e13.png!small)

rand:

![图片8.png](https://image.3001.net/images/20200421/1587454132_5e9ea0b46e5c9.png!small)

3.4 同一进程下,在rand和mtrand均未被人工播种时, rand和mtrand使用的种子会是一样:

基于3.1, 我们能知道rand和mt_srand会默认有如下调用:

    
    
    php_srand(GENERATE_SEED())  
    php_mt_srand(GENERATE_SEED());

已知state生成的关键点在于seed( = GENERATESEED()) 这儿主要需要证明, 先后调用GENERATESEED(),获取的值是一样的:

    
    
    # php_rand.h  
      
    #ifdef PHP_WIN32  
    #define GENERATE_SEED() (((zend_long) (time(0) * GetCurrentProcessId())) ^ ((zend_long) (1000000.0 * php_combined_lcg())))  
    #else  
    #define GENERATE_SEED() (((zend_long) (time(0) * getpid())) ^ ((zend_long) (1000000.0 * php_combined_lcg())))  
    #endif

根据源码可以得出:

1.GENERATESEED()的数据类型为zendlong,zendlong的范围为uint32t

2.其生成取决于phpcombinedlcg()和 [GetCurrentProcessId()或getpid()],当在一个进程下,
先后调用[GetCurrentProcessId()或getpid()],的值是一样,那么只需要关注一下phpcombinedlcg:

lcg.c

![图片9.png](https://image.3001.net/images/20200421/1587454220_5e9ea10c180b9.png!small)

根据代码可以很明显的知道, 第一次调用phpcombinedlcg,会播种生成了新的s1和s2,第二次再调用,不再播种,
用的先前的s1和s2,那么phpcombinedlcg是相等的。

所以先后调用GENERATE_SEED, 值是一样的。

3.5 抽象理解:

由于能力有限并没有具体去看state和BG的数据结构,上面分析可能存在问题, 但基于上面的分析, 可以做如下的抽象理解:

mt_srand用seed构造出来一个叫做state的东西, 可以看成是数组结构, 然后BG可以看成一个字典结构,用JSON格式表示一下:

    
    
    BG = {  
    	"next": [a,b,c,d] , # new_state  
    	"left": N , # 记录next里面剩余数量  
    }

那么:

> 函数mt_initialize == 使用seed生成一个新的state
>
> 函数mtrealod == 将state做了一些函数变化得到newstate, 然后一个赋值到 BG["next"]
>
> 函数mtsrand == mtinitialize+mt_realod+标记已经播种
>
> 函数mtrand == BG["next"].pop(0) , 取出newstate里面第一个

### **4\. 结论**

4.1 影响随机数生成的因素为两个: 1. 种子 2. 次数 (3.5)4.2
srand/mtsrand相当于重置了次数,rand/mtrand相当于次数+=1 (3.1, 3.2)4.3
PHP5下rand/srand和mtrand/mtsrand是独立的,种子和次数均不相互干扰, 在同seed,同次数下,值不一样 (1.1, 1.2)4.2
PHP7下rand/srand和mtrand/mtsrand的种子和次数均互相干扰, 在同seed,同次数下,值完全一样(可以看成同一个函数,会舒服一些)
(2.2)4.3
PHP5的rand/srand和PHP5的mtrand/mtsrand和PHP7的rand/srand/mtrand/mtsrand,在同seed,同次数下,值不一样
(1.1, 1.2, 2.1)4.4 种子区间为0到0xffffffff, 且有如下等式 (3.4)

    
    
    mt_srand(4294967297); == mt_srand(1) == mt_srand(-4294967295);    
      
    mt_srand(-4294967297); == mt_srand(-1) == mt_srand(4294967295);  
      
    srand(4294967297); == srand(1) == srand(-4294967295);  

4.6 同一进程下,先后被调用的rand和mt_rand, 在未播种的前提下, 会使用同一个随机种子 (3.3)

## 四、其他

PYTHON和PHP随机函数是否相同?

不相同: <https://stackoverflow.com/questions/19943476/python-and-php-not-returning-the-same-results-for-a-similiarly-seeded-rng/19951713#19951713>

需要根据PHP的代码, 用C去实现,python自带的rand和php的存在区别:)

## 五、参考

>
> <http://wonderkun.cc/index.html/?p=585%EF%BC%8C%E9%9A%8F%E6%9C%BA%E6%95%B0%E4%B9%8B%E5%89%8D%E4%B9%9F%E6%98%AFctf%E7%9A%84%E5%B8%B8%E8%A7%81%E5%A7%BF%E5%8A%BF>
>
> <https://xz.aliyun.com/t/31>
>
> <https://github.com/ONsec-Lab/Rand-attacks/blob/master/rand-brute.php>
>
> <https://bas.bosschert.nl/sha2017-ctf-web400-write-up/>
>
> <https://stackoverflow.com/questions/28760650/difference-between-mt-rand-> and-rand>
>
> <https://vitux.com/how-to-install-php5-and-php7-on-ubuntu-18-04-lts/>

 ** __*本文作者：光通天下无患实验室 Djerryz，转载请注明来自FreeBuf.COM**

