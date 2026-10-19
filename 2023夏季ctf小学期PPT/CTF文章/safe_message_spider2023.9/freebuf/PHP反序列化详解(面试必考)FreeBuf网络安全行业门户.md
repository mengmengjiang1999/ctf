  

首先看一张图  
![](https://image.3001.net/images/20210212/1613063037_6025637de5a47815966a8.png!small)![](https://image.3001.net/images/20210212/1613063089_602563b1ea52c65f6530b.png!small)

  

## PHP反序列化
原理：未对用户输入的序列化字符串进行检测，导致攻击者可以控制反序列化过程，从而导致代码执行，SQL注入，目录遍历等不可控后果。在反序列化的过程中自动触发了某些魔术方法。当进行反序列化的时候就有可能会触发对象中的一些魔术方法。

  

serialize() //将一个对象转换成一个字符串  
unserialize() //将字符串还原成一个对象  
反序列化分为有类和无类  
我们先来看序列化数据也就是序列化字符串  
先上图  
![](https://image.3001.net/images/20210212/1613063188_60256414d95ca2e55aa16.png!small)![](https://image.3001.net/images/20210212/1613063198_6025641eb4e354b02b8cd.png!small)

  

我们看看上面那张图  
s:8:"chixigua"s  
s代表字符串，8代表长度“chixigua”代表值  
在无类中他调用了unserialize()将字符串还原为对象没有进行过滤我们可以观察其代码而构造payload进行sql注入，代码执行，getshell，目录遍历等等，主要看他的代码，他的代码有sql语句接收序列化字符串这样会产生反序列化sql注入其他漏洞也是如此，主要看代码来辨别危害  
 **反序列化也是我们面试的必考题，所以还是很重要的**  
在思维导图我们提到有类在有类的情况我们会设计到各种魔术方法  
我们首先来介绍一下各种魔术方法  
__construct()  
具有构造函数的类会在每次创建新对象时先调用此方法，所以非常适合在使用对象之前做一些初始化工作。  
__destruct()  
析构函数会在到某个对象的所有引用都被删除或者当对象被显式销毁时执行。  
也就是说进行反序列化时，完成的就是从字符串创建新对象的过程，刚开始就会调用__construct(),而对象被销毁时，例如程序退出时，就会调用__destruct()  
触发：unserialize函数的变量可控，文件中存在可利用的类，类中有魔术方法：  
参考：[官方文档魔法方法部分](https://www.php.net/manual/zh/language.oop5.magic.php)  
__construct()//创建对象时触发  
__destruct() //对象被销毁时触发  
__call() //在对象上下文中调用不可访问的方法时触发  
__callStatic() //在静态上下文中调用不可访问的方法时触发  
__get() //用于从不可访问的属性读取数据  
__set() //用于将数据写入不可访问的属性  
__isset() //在不可访问的属性上调用isset()或empty()触发  
__unset() //在不可访问的属性上使用unset()时触发  
__invoke() //当脚本尝试将对象调用为函数时触发  
接下来我们先看一段魔术方法php代码  
![](https://image.3001.net/images/20210212/1613063253_6025645569f2a36af6163.png!small)

首先先分析一下代码创建了一个类  
里面写了3个魔术方法  
我们看结果首先输出了‘调用了构造函数’，为什么在魔术方法里的这串代码执行了呢？这是因为触发了他的魔术方法，因为我们将一个类进行了实体化，也就是新建了一个对象，触发了__construct()方法里的代码，接下来又输出了‘调用了苏醒函数’在反序列话函数执行的时候会先检测__wakeup()方法有该方法这会先执行这个方法里的代码

详细参考这张图

![](https://image.3001.net/images/20210212/1613063225_60256439164ef70ac02ec.png!small)

可以玩玩去年网鼎的青龙杯里的反序列化题我把解题思路写下来  
[网鼎杯青龙组php反序列化题](https://www.ctfhub.com/#/challenge)

    
    
    首先ctf命名及代码函数unserialize判断反序列化知识点
    第一：获取flag存储flag.php
    第二：两个魔术方法__destruct __construct
    第三：传输str参数数据后触发destruct，存在is_valid过滤
    第四：__destruct中会调用process,其中op=1写入及op=2读取
    第五：涉及对象FileHandler，变量op及filename,content，进行构造输出

**

    
    
    <?php
    class FileHandler{
        public $op=' 2';//源码告诉我们op为1时候是执行写入为2时执行读
        public $filename="flag.php";//文件开头调用的是flag.php
        public $content="zmc";
    }
    $flag = new FileHandler();
    $flag_1 = serialize($flag);
    echo $flag_1;
    ?>
    涉及：反序列化魔术方法调用，弱类型绕过，ascii绕过
    使用该类对flag进行读取，这里面能利用的只有__destruct函数（析构函数）。__destruct函数对$this->op进行了===判断并内容在2字符串时会赋值为1，process函数中使用==对$this->op进行判断（为2的情况下才能读取内容），因此这里存在弱类型比较，可以使用数字2或字符串' 2'绕过判断。
    is_valid函数还对序列化字符串进行了校验，因为成员被protected修饰，因此序列化字符串中会出现ascii为0的字符。经过测试，在PHP7.2+的环境中，使用public修饰成员并序列化，反序列化后成员也会被public覆盖修饰。﻿ **[个人博客](http://www.zmcbk8.ltd/)**

