比赛过了2个多月，但笔者太菜，第一次做这种大型模板的源码审计，这过程属实艰难，上学的时候太忙了，好不容易寒假有空了好好看看，之前也看过Siebene大佬写的文章，但我实在是太菜了，很多大佬认为我应该知道的东西我不知道，导致看不太明白，所以就以Siebene师傅的文章作为参考，对自己这几天的研究成果做一个总结吧。

来看个简单的例子，

    
    
    <?php  
    //这是demo.php
    require '../vendor/autoload.php';  
    $latte = new Latte\Engine;
    $latte->setTempDirectory('../temp');
    $policy = new Latte\Sandbox\SecurityPolicy;
    $policy->allowMacros(['block', 'if', 'else','=']);
    $policy->allowFilters($policy::ALL);
    $policy->allowFunctions(['trim', 'strlen']);
    $latte->setPolicy($policy);
    $latte->setSandboxMode();
    $latte->setAutoRefresh(true);
    
    
    $latte->render('template.latte', ['message'=>'Hellow My Glzjin!']);
    
    
    
    /*这是template.latte*/
    <ul>
        {="${eval('echo \'k1gga is so cool!\';')}"}
    </ul>

介绍一下Latte模板的机制，latte会通过正则表达式将模板的内容进行分析，和java中将jsp解析成一个java类一样，latte会尝试将上文template.latte解析成一个php类，如下图，然后执行这个类中的main函数，完成render函数对模板进行动态渲染，latte中有许多宏上文中用到的宏是{=xxx}
也就是会将xxx当成字符串进行输出。![1642316842_61e3c42a8f7aef578c9bc.png!small](https://image.3001.net/images/20220116/1642316842_61e3c42a8f7aef578c9bc.png!small)

  

大佬的博客中的payload是用的${}，首先就来分析一下这个payload的结构，刚开始看到这个还以为是latte中的某个特殊的宏（宏就是像Flask中的{%
%}这种模板中有特殊的语法意义的结构），后来才发现这就是一个变量，看下面这个简单的例子：

![1642317352_61e3c628a0f7b0781b729.png!small](https://image.3001.net/images/20220116/1642317352_61e3c628a0f7b0781b729.png!small)

可以看到上述例子当中虽然有警告，但是eval函数确实执行了，下面解释一下原理，php中会解析双引号包裹的字符串中的变量，所以这里双引号中的$以及后面的东西被当成一个变量来解析，$后面大括号中的内容表示被大括号包裹的内容是一个整体，但是在大括号中是可以执行表达式的，所以这里的双引号解析的变量是eval执行的结果也就是相当于echo
$kigga\ki，但是这个变量并没有被定义过，php中有个特性，如果使用一个没定义过的变量，不会报error错误，而是notice警告，然后默认该变量的值就是变量名，所以看到这里echo输出了eval恶意函数的执行结果。

因此如果我们可以控制latte渲染的模板中的内容，那么就可以控制其生成的php类中的内容，只要在php生成的类中包含我们的payload就可以执行一个RCE了，那么问题就是我们要如何去精心构造这个模板的内容呢？看到在render函数的执行过程中latte源码的PhpWrite中会调用preprocess函数，其中对tokens进行了一系列预处理（tokens是latte对模板进行正则匹配后将如htmltext和macrotag等等不同类型的字符分类后的一个数组，其目的是将模板中的不同类别的内容进行分类处理）。

![1642319781_61e3cfa515b6fd8c7b129.png!small](https://image.3001.net/images/20220116/1642319781_61e3cfa515b6fd8c7b129.png!small)

在这一系列预处理中，着重看这个sandboxPass。

    
    
    //PhpWriter.php
    public function sandboxPass(MacroTokens $tokens): MacroTokens{
            ......
            elseif ($tokens->isCurrent('$')) { // $$$var or ${...}
                    throw new CompileException('Forbidden variable variables.');
    
            }
            ......
            else { // $obj->$$$var or $obj::$$$var
                            $member = $tokens->nextAll($tokens::T_VARIABLE, '$');
                            $expr->tokens = $op === '::' && !$tokens->isNext('(')
                                ? array_merge($expr->tokens, array_slice($member, 1))
                                : array_merge($expr->tokens, $member);
             }
            ......
    }

看到这个方法会检测当前token的内容，不允许其值是$，否则就会抛出异常，命令执行失败，但是其正则匹配得到的token内容是"${eval('echo
\'k1gga is so cool1!\';')}"，所以成功绕过了这个sandboxpass检测。

![1642320451_61e3d24338725a9177bbc.png!small](https://image.3001.net/images/20220116/1642320451_61e3d24338725a9177bbc.png!small)

看到最后生成的类是这个

![1642320636_61e3d2fcd174e0caf2960.png!small](https://image.3001.net/images/20220116/1642320636_61e3d2fcd174e0caf2960.png!small)

看到了双引号包裹的恶意代码，说明成功RCE。

现在latte最新版本已经修复了这个漏洞了，这里对token进行检测是否有效

![1642320777_61e3d389b334990bfa659.png!small](https://image.3001.net/images/20220116/1642320777_61e3d389b334990bfa659.png!small)

![1642320847_61e3d3cf09e5d15978be8.png!small](https://image.3001.net/images/20220116/1642320847_61e3d3cf09e5d15978be8.png!small)

直接禁止在{= }这个宏里面写这种复杂的string表达式了。

  

### 总结

这个漏洞的原理简单来说就是latte对字符串的检测有问题，latte认为其只是一个简单的字符串，但是渲染成php以后，php认为其是一个变量，并且是用双引号包裹的变量会去解析它。

  

  

参考链接：

[Siebene大佬的文章](https://mp.weixin.qq.com/s?__biz=MzA5ODA0NDE2MA==&mid=2649760562&idx=2&sn=4bd448ee5be7644804557ba809cdb7a9)

[Latte源码](https://github.com/nette/latte)

