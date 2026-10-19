Author：[Hcamael](http://0x48.pw/)

date： 2016-11-28 20:26:26

注：更多 HCTF 题目可以在此找到：https://github.com/hduisa/HCTF2016

今年犯懒了所以只出了3题RSA的密码学题目, 出题思路来源于协会上一届的学长 @Mystery Of Panda 关于RSA后门的毕业设计.

## Crypto So Interesting

题目: <https://github.com/Hcamael/ctf-library/tree/master/RSA1>

payload: <https://github.com/Hcamael/ctf-library/blob/master/RSA1/rsa1_payload.py>

出题时预测的分数在300分左右, 不过看完选手的wp后发现这题出现了重大失误, 现在来看, 这题只值150分左右, 但是实际情况只有23个队解出了该题.

本题思路来源: 基于隐藏指数的RSA-HSDβ算法, 全称为隐藏小私有指数δ的RSA后门密钥生成算法.

该算法依赖于[wiener](https://github.com/pablocelayes/rsa-wiener-attack)小指数攻击方法

后门生成流程:

![hctf_rsa1](http://qn.lazysheep.cc/img/hctf_rsa_1.png)

其中`β`是在`2^(k-1) ± 2^(k/2)`范围内的素数, 转置函数的作用是在`β`非常大的情况下, 返回值可以认为是PRP(Pseudo-Random Permutation). 转置函数可以有好几种形式, 我选取的是一种比较简单的转置函数.

从上面的流程可以看出这题非常的简单, 要逆向也是很容易的, 所以该题为本届HCTF密码学的签到题

逆向思路:

![hctf_rsa1_2](http://qn.lazysheep.cc/img/hctf_rsa1_2.png)

从上图可以看出本题只涉及到了wiener算法, 难度差不多是150左右

* * *

出题时本来是准备考两种算法的, 一种是wiener算法, 一种是[Riemann's hypothesis and tests for
primality](https://www.cs.cmu.edu/~glmiller/Publications/Papers/Mi76.pdf),
payload中的`divide_pq`函数, 已知e, d, n质因数分解p和q(<http://www.di-mgt.com.au/rsa_factorize_n.html>)

原本设计着算出`(ϵ, δ)`后, 根据`(ϵ, δ, n)`分解出`q`和`p`, 但是出题失误, 导致只需要wiener算法就能getflag

PS1: 不过还是出现了非预期, ROIS的dalao利用wiener算法分解出`p`和`q`,
<https://github.com/Hcamael/ctf-library/blob/master/RSA1/rsa_s.py>

PS2: 基于隐藏指数的RSA后门生成算法除了本题涉及的还有`RSA-HSPEβ`和`RSA-HSEβ`

## Crypto So Cool

题目: <https://github.com/Hcamael/ctf-library/tree/master/RSA2> payload:

  * <https://github.com/Hcamael/ctf-library/blob/master/RSA2/rsa2_payload.py>
  * <https://github.com/Hcamael/ctf-library/blob/master/RSA2/rsa2_payload.sage>

出题时预测的分数在400分左右, 实际情况只有7个队解出了该题. 和预测差不多, 最后放了一波hint, 要不然可能会更少.

本题思路来源: 基于隐藏素数因子的RSA-HPβ算法

该后门算法依赖于`Coppersmith partial information attack`算法,
[sage实现该算法](http://inaz2.hatenablog.com/entries/2016/01/20)

后门生成流程: ![hctf_rsa2_1](http://qn.lazysheep.cc/img/hctf_rsa2_1.png)

该算法的核心在于把p的前半部分比特隐写到n中

τ的长度为k/16比特

μ的长度为5k/16比特

λ的长度为5k/8比特

所以n的长度为k比特

`p * (q xor random(k/8比特长度))`的前3k/8比特的值是不变的

所以可以成功把τ, μ隐写到n中

逆向思路:

![hctf_rsa2_2](http://qn.lazysheep.cc/img/hctf_rsa2_2.png)

该题的难点主要在于`Coppersmith partial information attack`算法,
能在放hint前做出的队伍都是在github上找到了该算法的脚本 <https://github.com/Gao-Chuan/RSA-and-LLL-attacks>

## Crypto So Amazing

题目: <https://github.com/Hcamael/ctf-library/tree/master/RSA3>

payload:

  * <https://github.com/Hcamael/ctf-library/blob/master/RSA3/rsa3_payload.py>
  * <https://github.com/Hcamael/ctf-library/blob/master/RSA3/rsa3.sage>

出题时预测的分数在450分左右, 不过却没有能做出来, 我知道的几个队都是被上一题的脚本给坑了

本题思路来源: 基于有限域F(2^m)上椭圆曲线的RSA后门生成算法

流程图懒得画了, 上一题的后门算法看懂了, 这题去看代码也不难, 主要是通过`Diffie–Hellman key
exchange`算法生成私钥作为种子生成伪随机数, 私钥很好求, 本题的难点跟上题一样同样在于`Coppersmith partial
information attack`算法

上一题我故意改简单了, 已知p的前640比特, 所以可以很容易通过<https://github.com/Gao-Chuan/RSA-and-LLL-attacks>这个脚本恢复出完整的p

但是这题已知p的前576bit, github上的那个脚本就跑不出来了

这部分是出题时无意间挖出的坑, 因为我并不知道github上的这个脚本, 在我预想中能做出rsa2的基本都是能做出rsa3的

这题还有一个坑点

![hctf_rsa_keng2](http://qn.lazysheep.cc/img/hctf_rsa_keng2.png)
![hctf_rsa_keng1](http://qn.lazysheep.cc/img/hctf_rsa_keng1.png)

sage和python 用相同的seed生成的随机数不一样, 所以在payload中我使用了python生成随机数

## 总结

本届HCTF的Crypto计划的考点是`Coppersmith partial information attack`算法和`Riemann's
hypothesis and tests for primality`算法, 不过无奈由于出题失误第二个算法没考成

RSA后门相关的论文可参考:

  * Crépeau C, Slakmon A. Simple backdoors for RSA key generation[J]. Topics in Cryptology—CT-RSA 2003, 2003, 2612: 403-416.
  * Young, A., Yung, M. A Space Efficient Backdoor in RSA and its Applications[J]. Preneel, B., Tavares, S. (eds.) SAC 2005, 2005, 3897: 128-143.
  * Tzung-Her Chen, Tsung-Hao Hung. A Comprehensive Study of Backdoors f or RSA Key Generation[R]. Cryptology and Information Security Conference, 2010.

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/128/>

