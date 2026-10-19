实验吧CTF密码学Writeup-变异凯撒 Writeup

[ syxvip](https://www.jianshu.com/u/380fd93bae2c)关注赞赏支持

# 实验吧CTF密码学Writeup-变异凯撒 Writeup

变异凯撒分值：10  
来源： 实验吧难度：易参与人数：2665人Get Flag：1143人答题人数：1202人解题通过率：95%  
加密密文：afZ_r9VYfScOeO_UL^RWUc  
格式：flag{ }

* * *

上来 一头雾水，丝毫找不到头绪。  
看了下面的题目中的评论，也没有找到思路，然后学弟按照评论中的思路疏导了而一下，自己试了下，就出来了，这一题虽然难易程度为 易，但是并找不到什么思路。  
ps：评论中的求解引导方法为：

首先理解凯撒加密方式主要是变换，对照前四个字符的ASCII码。  
a(97)+5=f(102);  
f(102)+6=l(108);  
Z(90)+7=a(97);  
_(95)+8=g(103)......按照这个规律以此类推

我看了 writeup  
用世界上最好的语言 php 实现

    
    
    <?php
    
         function decode($str){
        $finish='';
        for($_O=5;$_O<strlen($str)+5;$_O++){
            $_c=substr($str,$_O-5,1);
            $__=ord($_c)+$_O;
            $_c=chr($__);
            $finish=$finish.$_c;
        }
        return $finish;
    }
    $p=decode("afZ_r9VYfScOeO_UL^RWUc");
    print $p;
    ?>
    
    

然后转ASCII

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [南邮CTF-WEB-writeup](https://www.jianshu.com/p/19999fa5ca8b)

2018/3/16 17:34:51 WEB题 1.签到题 题目：key在哪里？ writeup:查看源代码即可获...

[Sec小玖](https://www.jianshu.com/u/92820b1051ae)阅读 21,598评论 1赞 11

  * [0ops CTF/0CTF writeup](https://www.jianshu.com/p/edceb531d5b3)

×00 0CTF 『第一届0ops信息安全技术挑战赛，即0ops Capture The Flag，以下简称0CT...

[tmdsb38](https://www.jianshu.com/u/f44cac946f18)阅读 2,565评论 0赞 4

  * [实验吧CTF密码学Writeup-疑惑的汉字Writeup](https://www.jianshu.com/p/3ffd22fd6b72)

疑惑的汉字分值：10 来源： 实验吧 难度：易 参与人数：4948人 Get Flag：3029人 答题人数：31...

[syxvip](https://www.jianshu.com/u/380fd93bae2c)阅读 1,661评论 0赞 0

  * [加密进阶（佩服写这篇文章的人）](https://www.jianshu.com/p/006a8e6e25e7)

CTF中那些脑洞大开的编码和加密 0x00 前言 正文开始之前先闲扯几句吧，玩CTF的小伙伴也许会遇到类似这样的问...

[查无此人asdasd](https://www.jianshu.com/u/6345e3b05eca)阅读 5,408评论 0赞 19

  * [午后大雨得诗名《无题》](https://www.jianshu.com/p/935ee7253180)

窗外流珠點點， 雷鳴蛙聲片片。 由來不知何處， 原是天上人間。 ——辛巳辛卯日

[RHIGHT](https://www.jianshu.com/u/9ce80477bf38)阅读 79评论 0赞 0

 