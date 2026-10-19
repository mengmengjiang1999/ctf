# N1CTF 2021 RE(babyrust, hello) Writeup

阅读量 **149849**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-22 16:30:26

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

题目超难！只做出来两道 re ！

Nebula 战队，排名第8，名次还不错，但是看分数和解题数量，前面的大佬真的太强了。

比赛官网：<https://ctf2021.nu1l.com/>  
比赛时间：2021-11-20 08:00:00 到 2021-11-22 08:00:00

## Reverse

###  babyrust

RE 里唯一一道简单（并不简单）题，给了一个 rust 程序，通过多个 check 宏定义增加分析难度，并且编译时提示宏展开嵌套层次过高，编译失败。

但是实际上很简单，就是`Never gonna
...`那一大段，按照前缀依次宏展开，使用脚本做前缀匹配就能将宏展开为代码。初步处理之后，发现得到的代码里有大量连续的`gonna +=
1`，再将这些合并成一句`gonna += value`即可。python脚本：

    
    
    #!/usr/bin/python2
    
    codes = \
    '''
    macro_rules! check {
        (@s n1ctf{$Never:tt}) => {
            check!(stringify!($Never))
        };
    
        ($Never:expr) => {{
            fn check() -> bool {
                let mut never = $Never.as_bytes().to_vec();
                let mut gonna = 0;
                let mut give:usize = 0;
    '''
    
    macros = [
        ['Never gonna give you up', 'give += 1;'],
        ['Never gonna let you down', 'give -= 1;'],
        ['Never gonna run around and desert you', 'gonna += 1;'],
        ['Never gonna make you cry', 'gonna -= 1;'],
        ['Never gonna say goodbye', 'gonna = never[give];'],
        ['Never gonna tell a lie and hurt you', 'never[give] = gonna;'],
        ['Never gonna give never gonna give', 'let you = [148u8, 59, 143, 112, 121, 186, 106, 133, 55, 90, 164, 166, 167, 121, 174, 147, 148, 167, 99, 86, 81, 161, 151, 149, 132, 56, 88, 188, 141, 127, 151, 63];\n\t\t\treturn never == you;']
    ]
    
    statements = # LONG line
    
    while statements:
        for i in macros:
            if statements.startswith(i[0]):
                codes += '\t\t\t%s\n' % i[1]
                statements = statements[len(i[0]): ].strip(' ')
                break
        else:
            print('No macro found for %s' % statements)
            exit(-1)
    
    codes += \
    '''
            }
            check()
        }};
    }
    
    fn main() {
        let result = check!(@s n1ctf{0123456789abcdef});
        if result {
            println!("Yes");
        }
    }
    '''
    
    lines = codes.splitlines()
    codes = ''
    i = 0
    while i < len(lines):
        value = 0
        var = None
        if lines[i] == '\t\t\tgive += 1;' or lines[i] == '\t\t\tgive -= 1;':
            var = 'give'
        elif lines[i] == '\t\t\tgonna += 1;' or lines[i] == '\t\t\tgonna -= 1;':
            var = 'gonna'
        else:
            if len(lines[i]):
                # codes += lines[i] + '\n'
                print(lines[i])
            i = i + 1
            continue
        while i < len(lines) and lines[i].startswith('\t\t\t' + var):
            if lines[i] == '\t\t\t' + var + ' += 1;':
                value += 1
            elif lines[i] == '\t\t\t' + var + ' -= 1;':
                value -= 1
            else:
                break
            i = i + 1
        # codes += '\t\t\t%s += %d;\n' % (var, value)
        print('\t\t\t%s += %d;' % (var, value))
    
    # print(codes)
    

运行结果：

    
    
    macro_rules! check {
            (@s n1ctf{$Never:tt}) => {
                    check!(stringify!($Never))
            };
            ($Never:expr) => {{
                    fn check() -> bool {
                            let mut never = $Never.as_bytes().to_vec();
                            let mut gonna = 0;
                            let mut give:usize = 0;
                            gonna = never[give];
                            gonna += 83;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 5;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 76;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 61;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 70;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 117;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 41;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 83;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 2;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 35;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 115;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 101;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 117;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 56;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 105;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 97;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 94;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 101;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 29;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 21;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 12;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 106;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 85;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 80;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 67;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 6;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 21;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 120;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 85;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 57;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 98;
                            never[give] = gonna;
                            give += 1;
                            gonna = never[give];
                            gonna += 11;
                            never[give] = gonna;
                            give += 1;
                            let you = [148u8, 59, 143, 112, 121, 186, 106, 133, 55, 90, 164, 166, 167, 121, 174, 147, 148, 167, 99, 86, 81, 161, 151, 149, 132, 56, 88, 188, 141, 127, 151, 63];
                            return never == you;
                    }
                    check()
            }};
    }
    fn main() {
        let result = check!(@s n1ctf{0123456789abcdef});
        if result {
            println!("Yes");
        }
    }
    

只是简单的加，减一下就得到flag：  
`n1ctf{A6C33EA2571A2AE26BFAE7BEA2CD8F54}`

###  hello

Go逆向，用ida7.6可以恢复部分符号信息，转到main_main，结合动调可得前面的简单逻辑，输入32字节16进制数，每两个16进制数得到一个新的字节，总共16字节，再传入main__Cfunc_func1，通过C函数func1做变换，得到新的字节数组，最后用一个方程组判断值。

最后的方程组求解，前面的式子都比较复杂，最后一个判断是一个算式模293，而看汇编，这个结构和前面的式子结构是相同的，ida识别出问题了吧，所以前面也应该是模293。

线性方程组直接扔给z3求解，但是早上9点多开始跑，晚上6点多还没出结果，那就只好自己写脚本求解：

    
    
    #!/usr/bin/python2
    from gmpy2 import *
    
    def add(x, y):
        assert(len(x) == len(y))
        return [(i + j) % 293 for i, j in zip(x, y)]
    
    def sub(x, y):
        assert(len(x) == len(y))
        return [(i - j) % 293 for i, j in zip(x, y)]
    
    def mul(x, n):
        return [i * n % 293 for i in x]
    
    def div(x, n):
        rev = int(invert(n, 293))
        return mul(x, rev)
    
    conds = '''68  == (11448910 * v60[15] + 40743553 * v60[14] + 15249722 * v60[13] + 51420184 * v60[12] + 1272949 * v60[11] + 17564837 * v60[10] + 52185491 * v60[9] + 8881295 * v60[8] + 27627194 * v60[7] + 20133359 * v60[6] + 12649121 * v60[5] + 16687834 * v60[4] + 35629177 * v60[3] + 65149487 * v60[2] + 44718284 * v60[1] + 5377102 * v60[0]) % 293
    73  == (48411728 * v60[15] + 46007731 * v60[14] + 35099188 * v60[13] + 58592730 * v60[12] + 31668013 * v60[11] + 37493724 * v60[10] + 34235932 * v60[9] + 3705469 * v60[8] + 46765687 * v60[7] + 11650930 * v60[6] + 40946083 * v60[5] + 14512921 * v60[4] + 410852 * v60[3] + 8677693 * v60[2] + 48100308 * v60[1] + 15513275 * v60[0]) % 293
    105 == (11388094 * v60[15] + 22952329 * v60[14] + 28320092 * v60[13] + 61937243 * v60[12] + 9778043 * v60[11] + 3328881 * v60[10] + 34002181 * v60[9] + 20900966 * v60[8] + 15752138 * v60[7] + 52093804 * v60[6] + 12201596 * v60[5] + 41219106 * v60[4] + 44419237 * v60[3] + 46626798 * v60[2] + 17611295 * v60[1] + 51342117 * v60[0]) % 293
    26  == (34715169 * v60[15] +  2137413 * v60[14] + 38457326 * v60[13] + 23972020 * v60[12] + 59151919 * v60[11] + 45673314 * v60[10] + 63801756 * v60[9] + 36167240 * v60[8] + 16650010 * v60[7] + 36591851 * v60[6] + 9676221 * v60[5] + 28388843 * v60[4] + 43159917 * v60[3] + 45916134 * v60[2] + 46862881 * v60[1] + 57970260 * v60[0]) % 293
    278 == (65951721 * v60[15] + 49899769 * v60[14] + 20365833 * v60[13] + 50854754 * v60[12] + 66315899 * v60[11] + 24023407 * v60[10] + 10941397 * v60[9] + 56539279 * v60[8] + 21483823 * v60[7] + 23526593 * v60[6] + 56977904 * v60[5] + 40100057 * v60[4] + 40013998 * v60[3] + 28326782 * v60[2] + 11375397 * v60[1] + 32808901 * v60[0]) % 293
    236 == (13044253 * v60[15] +  8291395 * v60[14] + 53262276 * v60[13] + 39192608 * v60[12] + 11857558 * v60[11] + 11073096 * v60[10] + 25927713 * v60[9] + 34514986 * v60[8] + 63871055 * v60[7] + 52604124 * v60[6] + 36309373 * v60[5] + 282427 * v60[4] + 32746957 * v60[3] + 47833723 * v60[2] + 40551307 * v60[1] + 52471216 * v60[0]) % 293
    261 == (37348869 * v60[15] + 48980070 * v60[14] + 1682385 * v60[13] + 30745745 * v60[12] + 6761227 * v60[11] + 52918290 * v60[10] + 17699555 * v60[9] + 28922206 * v60[8] + 32578112 * v60[7] + 38269989 * v60[6] + 62585890 * v60[5] + 61739612 * v60[4] + 66810519 * v60[3] + 47531426 * v60[2] + 37064630 * v60[1] + 24199242 * v60[0]) % 293
    90  == (62202924 * v60[15] + 30396598 * v60[14] + 60438120 * v60[13] + 65789447 * v60[12] + 58876674 * v60[11] + 9672908 * v60[10] + 45032298 * v60[9] + 41831746 * v60[8] + 9801829 * v60[7] + 50757695 * v60[6] + 34021426 * v60[5] + 1903443 * v60[4] + 32345456 * v60[3] + 54221555 * v60[2] + 34693296 * v60[1] + 12966608 * v60[0]) % 293
    173 == (29937890 * v60[15] + 31874820 * v60[14] + 34796144 * v60[13] + 8593554 * v60[12] + 59077744 * v60[11] + 2668953 * v60[10] + 17349024 * v60[9] + 18966262 * v60[8] + 41122881 * v60[7] + 50679759 * v60[6] + 63670216 * v60[5] + 49780363 * v60[4] + 7969099 * v60[3] + 63071621 * v60[2] + 55027617 * v60[1] + 25298698 * v60[0]) % 293
    55  == (17388834 * v60[15] + 57153581 * v60[14] + 16103318 * v60[13] + 39797887 * v60[12] + 62966701 * v60[11] + 37180051 * v60[10] + 54575969 * v60[9] + 1201444 * v60[8] + 53660494 * v60[7] + 18424162 * v60[6] + 26060497 * v60[5] + 61745538 * v60[4] + 32524194 * v60[3] + 34874075 * v60[2] + 11891252 * v60[1] + 599957 * v60[0]) % 293
    229 == (28288668 * v60[15] + 18660303 * v60[14] + 42011531 * v60[13] + 31750158 * v60[12] + 67056908 * v60[11] + 7550306 * v60[10] + 18108987 * v60[9] + 35129803 * v60[8] + 59291588 * v60[7] + 8246048 * v60[6] + 61723044 * v60[5] + 61462529 * v60[4] + 27114985 * v60[3] + 9330086 * v60[2] + 49623029 * v60[1] + 52820893 * v60[0]) % 293
    292 == (21003028 * v60[15] + 43880816 * v60[14] + 51093211 * v60[13] + 58809916 * v60[12] + 41009760 * v60[11] + 37370364 * v60[10] + 1598982 * v60[9] + 36725663 * v60[8] + 32731509 * v60[7] + 32491361 * v60[6] + 8400987 * v60[5] + 32271858 * v60[4] + 20940616 * v60[3] + 64477078 * v60[2] + 63976576 * v60[1] + 3226343 * v60[0]) % 293
    43  == ( 7196185 * v60[15] + 51302172 * v60[14] + 63640408 * v60[13] + 21200580 * v60[12] + 24738818 * v60[11] + 20336759 * v60[10] + 23703928 * v60[9] + 19179549 * v60[8] + 53260842 * v60[7] + 6702116 * v60[6] + 5235806 * v60[5] + 59525552 * v60[4] + 52408555 * v60[3] + 31148317 * v60[2] + 18322594 * v60[1] + 11484407 * v60[0]) % 293
    5   == (34266111 * v60[15] + 32686335 * v60[14] + 8717460 * v60[13] + 12159655 * v60[12] + 57509360 * v60[11] + 34665752 * v60[10] + 11016018 * v60[9] + 50811576 * v60[8] + 28977207 * v60[7] + 54404660 * v60[6] + 49813519 * v60[5] + 42212815 * v60[4] + 44514143 * v60[3] + 11571592 * v60[2] + 14524437 * v60[1] + 28563837 * v60[0]) % 293
    276 == (39608187 * v60[15] + 24282261 * v60[14] + 18997872 * v60[13] + 16783819 * v60[12] + 27865128 * v60[11] + 58513213 * v60[10] + 18911756 * v60[9] + 44480266 * v60[8] + 5700458 * v60[7] + 8630338 * v60[6] + 52860393 * v60[5] + 22833691 * v60[4] + 35672785 * v60[3] + 61382021 * v60[2] + 7979743 * v60[1] + 33392211 * v60[0]) % 293
    165 == (23299004 * v60[15] + 31034972 * v60[14] + 55982584 * v60[13] + 886406 * v60[12] + 4029227 * v60[11] + 15741379 * v60[10] + 50326885 * v60[9] + 13077670 * v60[8] + 9249973 * v60[7] + 17218640 * v60[6] + 31294575 * v60[5] + 40628674 * v60[4] + 11554134 * v60[3] + 23103319 * v60[2] + 61959315 * v60[1] + 28529793 * v60[0]) % 293
    217 == (32579505 * v60[15] +  4371300 * v60[14] + 61149522 * v60[13] + 39840129 * v60[12] + 50452614 * v60[11] + 28645103 * v60[10] + 26341415 * v60[9] + 43235505 * v60[8] + 41390328 * v60[7] + 38289933 * v60[6] + 9418491 * v60[5] + 30588692 * v60[4] + 24338954 * v60[3] + 49647471 * v60[2] + 58384561 * v60[1] + 2075035 * v60[0]) % 293
    207 == (29828862 * v60[15] +  8163681 * v60[14] + 52610483 * v60[13] + 24081438 * v60[12] + 14841955 * v60[11] + 52095831 * v60[10] + 48298737 * v60[9] + 1866553 * v60[8] + 34823251 * v60[7] + 25602134 * v60[6] + 26835402 * v60[5] + 35248885 * v60[4] + 30084536 * v60[3] + 31133287 * v60[2] + 19156834 * v60[1] + 39948186 * v60[0]) % 293
    1   == (60508155 * v60[15] + 36682310 * v60[14] + 33373239 * v60[13] + 16795502 * v60[12] + 20246162 * v60[11] + 53199974 * v60[10] + 31387649 * v60[9] + 31002578 * v60[8] + 9965987 * v60[7] + 39349501 * v60[6] + 52819211 * v60[5] + 44652087 * v60[4] + 26104149 * v60[3] + 41109851 * v60[2] + 1371418 * v60[1] + 620322 * v60[0]) % 293
    21  == (30297807 * v60[15] +  5280747 * v60[14] + 49427355 * v60[13] + 18487297 * v60[12] + 39564284 * v60[11] + 45990969 * v60[10] + 37674240 * v60[9] + 29438609 * v60[8] + 23766078 * v60[7] + 37794867 * v60[6] + 931273 * v60[5] + 63971060 * v60[4] + 31909354 * v60[3] + 27118998 * v60[2] + 66362659 * v60[1] + 30803764 * v60[0]) % 293'''
    
    matrix = []
    for i in conds.splitlines():
        rvalue, lvalue = i.split('==')
        rvalue = int(rvalue)
        lvalues = lvalue.replace('(', '').replace(')', '').split(' + ')[::-1]
        assert(len(lvalues) == 16)
        matrix.append([])
        for j in lvalues:
            j = j.strip(' ')
            matrix[-1].append(int(j[: j.index(' ')]) % 293)
        matrix[-1].append(rvalue % 293)
    
    j = 0
    while j < 16:
        if matrix[j][j] == 0:
            matrix = matrix[: j] + matrix[j + 1: ] + [matrix[j]]
            continue
    
        matrix[j] = div(matrix[j], matrix[j][j])
        for i in range(j + 1, len(matrix)):
            matrix[i] = sub(matrix[i], mul(matrix[j], matrix[i][j]))
        j = j + 1
    
    assert(all (i == 0 for i in matrix[j] for j in range(16, len(matrix))))
    
    matrix = matrix[: 16]
    
    for j in range(15, -1, -1):
        for i in range(j):
            matrix[i] = sub(matrix[i], mul(matrix[j], matrix[i][j]))
    
    for i in range(16):
        for j in range(16):
            if i == j:
                assert(matrix[i][j] == 1)
            else:
                assert(matrix[i][j] == 0)
    
    values = [matrix[i][-1] for i in range(16)]
    
    print(values)
    # [201, 247, 36, 211, 26, 224, 241, 131, 112, 24, 2, 0, 17, 243, 56, 186]
    

然后就是逆向C语言写的变换了，比较难。

有几个table变换，注意到table5比较特殊，值很有规律，观察一下发现它是周期的，周期为256，所以func1内table5变换中的`256 *
...`这些项可以直接去掉，还有一些`vxx = 16 * …;`然后`table[16 * vxx + ...]`这样的也可以将`16 *
vxx`项去掉，再删除没有引用的变量，将func1化简：

    
    
    void func1(unsigned __int8 *x, unsigned __int8 *a2) {
        int j_mul_24; // er15
        unsigned __int8 *x_ptr; // rdx
        unsigned int v5; // er12
        unsigned int v6; // eax
        unsigned int v7; // esi
        unsigned __int8 v8; // cl
        unsigned __int8 v9; // di
        unsigned __int8 v10; // cl
        unsigned __int8 v13; // di
        unsigned int v14; // eax
        unsigned int v15; // ecx
        unsigned int v16; // esi
        unsigned int v17; // er12
        __int64 j; // rax
        __int64 k; // rax
        unsigned int v21; // [rsp+4h] [rbp-134h]
        int j_mul_4; // [rsp+8h] [rbp-130h]
        __int64 v25; // [rsp+10h] [rbp-128h]
        __int64 v26; // [rsp+18h] [rbp-120h]
        __int64 v27; // [rsp+20h] [rbp-118h]
        __int64 v28; // [rsp+28h] [rbp-110h]
        int i; // [rsp+ECh] [rbp-4Ch]
    
        for ( i = 0; i != 9; ++i )
        {
            j_mul_24 = 0;
            func2(x);
            x_ptr = x;
            j_mul_4 = 0;
            do
            {
                v25 = (i * 16 + j_mul_4) << 8;
                v5 = table3[*x_ptr + v25];
                v26 = (i * 16 + j_mul_4 + 1) << 8;
                v21 = table3[v26 + x_ptr[1]];
                v27 = (i * 16 + j_mul_4 + 2) << 8;
                v6 = table3[v27 + x_ptr[2]];
                v28 = (i * 16 + j_mul_4 + 3) << 8;
                v7 = table3[v28 + x_ptr[3]];
                v8 = table5[
                    16 * table5[
                        16 * (HIBYTE(v5) & 0xF) +
                        (HIBYTE(v21) & 0xF)
                    ] + table5[
                        16 * (HIBYTE(v6) & 0xF) +
                        (HIBYTE(v7) & 0xF)
                    ]
                ] | (16 * table5[
                    16 * table5[
                        16 * (v5 >> 28) +
                        (v21 >> 28)
                    ] + table5[
                        16 * (v6 >> 28) +
                        (v7 >> 28)
                    ]
                ]);
    
                *x_ptr = v8;
                v9 = table5[
                    16 * table5[
                        16 * (HIWORD(v5) & 0xF) +
                        (HIWORD(v21) & 0xF)
                    ] + table5[
                        16 * (HIWORD(v6) & 0xF) +
                        (BYTE2(v7) & 0xF)
                    ]
                ] | (16 * table5[
                    16 * table5[
                        16 * ((v5 >> 20) & 0xF) +
                        ((v21 >> 20) & 0xF)
                    ] + table5[
                        16 * ((v6 >> 20) & 0xF) +
                        ((v7 >> 20) & 0xF)
                    ]
                ]);
    
    
                x_ptr[1] = v9;
                v10 = table5[
                    16 * table5[
                        16 * ((v5 >> 8) & 0xF) +
                        ((v21 >> 8) & 0xF)
                    ] + table5[
                        16 * (BYTE1(v6) & 0xF) +
                        (BYTE1(v7) & 0xF)
                    ]
                ] | (16 * table5[
                    16 * table5[
                        16 * ((unsigned __int16)v5 >> 12) +
                        ((unsigned __int16)v21 >> 12)
                    ] + table5[
                        16 * ((unsigned __int16)v6 >> 12) +
                        ((unsigned __int16)v7 >> 12)
                    ]
                ]);
    
    
                x_ptr[2] = v10;
                v13 = table5[
                    16 * table5[
                        16 * (v5 & 0xF) +
                        (v21 & 0xF)
                    ] + table5[
                        16 * (v6 & 0xF) +
                        (v7 & 0xF)
                    ]
                ] | (16 * table5[
                    16 * table5[
                        16 * ((unsigned __int8)v5 >> 4) +
                        ((unsigned __int8)v21 >> 4)
                    ] + table5[
                        16 * ((unsigned __int8)v6 >> 4) +
                        ((unsigned __int8)v7 >> 4)
                    ]
                ]);
    
                x_ptr[3] = v13;
                v14 = table4[v25 + v8];
                v15 = table4[v27 + v10];
                v16 = table4[v26 + v9];
                v17 = table4[v28 + v13];
    
                *x_ptr = table5[
                    16 * table5[
                        16 * (HIBYTE(v14) & 0xF) +
                        (HIBYTE(v16) & 0xF)
                    ] + table5[
                        16 * (HIBYTE(v15) & 0xF) +
                        (HIBYTE(v17) & 0xF)
                    ]
                ] | (16 * table5[
                    16 * table5[
                        16 * (v14 >> 28) +
                        (v16 >> 28)
                    ] + table5[
                        16 * (v15 >> 28) +
                        (v17 >> 28)
                    ]
                ]);
    
    
                x_ptr[1] = table5[
                    16 * table5[
                        16 * (HIWORD(v14) & 0xF) +
                        (BYTE2(v16) & 0xF)
                    ] + table5[
                        16 * (HIWORD(v15) & 0xF) +
                        (BYTE2(v17) & 0xF)
                    ]
                ] | (16 * table5[
                    16 * table5[
                        16 * ((v14 >> 20) & 0xF) +
                        ((v16 >> 20) & 0xF)
                    ] + table5[
                        16 * ((v15 >> 20) & 0xF) +
                        ((v17 >> 20) & 0xF)
                    ]
                ]);
    
    
                x_ptr[2] = table5[
                    16 * table5[
                        16 * ((v14 >> 8) & 0xF) +
                        (BYTE1(v16) & 0xF)
                    ] + table5[
                        16 * ((v15 >> 8) & 0xF) +
                        (BYTE1(v17) & 0xF)
                    ]
                ] | (16 * table5[
                    16 * table5[
                        16 * ((unsigned __int16)v14 >> 12) +
                        ((unsigned __int16)v16 >> 12)
                    ] + table5[
                        16 * ((unsigned __int16)v15 >> 12) +
                        ((unsigned __int16)v17 >> 12)
                    ]
                ]);
    
    
                j_mul_24 += 24;
                x_ptr += 4;
                j_mul_4 += 4;
                *(x_ptr - 1) = table5[
                    16 * table5[
                        16 * (v14 & 0xF) +
                        (v16 & 0xF)
                    ] + table5[
                        16 * (v15 & 0xF) +
                        (v17 & 0xF)
                    ]
                ] | (16 * table5[
                    16 * table5[
                        16 * ((unsigned __int8)v14 >> 4) +
                        ((unsigned __int8)v16 >> 4)
                    ] + table5[
                        16 * ((unsigned __int8)v15 >> 4) +
                        ((unsigned __int8)v17 >> 4)
                    ]
                ]);
            }
            while ( j_mul_24 != 96 );
        }
    
        func2(x);
        for ( j = 0LL; j != 16; ++j )
            x[j] = table1[256 * j + 0x9000 + x[j]];
        for ( k = 0LL; k != 16; ++k )
            a2[k] = x[k];
    }
    

但是还是不行，table3与table4是几乎随机的，只有table5很有规律，但是table5的嵌套变换太难逆向。

![](https://p0.ssl.qhimg.com/t01a4a826bccb4d1e06.png)

后来经同学提醒，table5是用来求异或的，也就是`table5[a][b] == a ^ b`，那就可以继续化简func1：

    
    
    void func1(unsigned __int8 *x, unsigned __int8 *a2) {
        unsigned __int8 *x_ptr; // rdx
        unsigned int v5; // er12
        unsigned int v6; // eax
        unsigned int v7; // esi
        unsigned __int8 v8; // cl
        unsigned __int8 v9; // di
        unsigned __int8 v10; // cl
        unsigned __int8 v13; // di
        unsigned int v14; // eax
        unsigned int v15; // ecx
        unsigned int v16; // esi
        unsigned int v17; // er12
        __int64 j; // rax
        __int64 k; // rax
        unsigned int v21; // [rsp+4h] [rbp-134h]
        __int64 v25; // [rsp+10h] [rbp-128h]
        __int64 v26; // [rsp+18h] [rbp-120h]
        __int64 v27; // [rsp+20h] [rbp-118h]
        __int64 v28; // [rsp+28h] [rbp-110h]
        int i; // [rsp+ECh] [rbp-4Ch]
    
        for ( i = 0; i != 9; ++i ) {
            func2(x);
            x_ptr = x;
            for (int j = 0; j < 4; j++) {
    
                v25 = (i * 16 + j * 4) << 8;
                v5 = table3[*x_ptr + v25];
    
                v26 = (i * 16 + j * 4 + 1) << 8;
                v21 = table3[v26 + x_ptr[1]];
    
                v27 = (i * 16 + j * 4 + 2) << 8;
                v6 = table3[v27 + x_ptr[2]];
    
                v28 = (i * 16 + j * 4 + 3) << 8;
                v7 = table3[v28 + x_ptr[3]];
    
                unsigned int value = v5 ^ v21 ^ v6 ^ v7;
    
                v8 = (value >> 24) & 0xff;
                v9 = (value >> 16) & 0xff;
                v10 = (value >> 8) & 0xff;
                v13 = value & 0xff;
    
    
                v14 = table4[v25 + v8];
                v15 = table4[v27 + v10];
                v16 = table4[v26 + v9];
                v17 = table4[v28 + v13];
                value = v14 ^ v16 ^ v15 ^ v17;
    
                *x_ptr = (value >> 24) & 0xff;
                x_ptr[1] = (value >> 16) & 0xff;
                x_ptr[2] = (value >> 8) & 0xff;
                x_ptr[3] =  value & 0xff;
    
                x_ptr += 4;
            }
        }
    
        func2(x);
        for ( j = 0LL; j != 16; ++j )
            x[j] = table1[256 * j + 0x9000 + x[j]];
        for ( k = 0LL; k != 16; ++k )
            a2[k] = x[k];
    }
    

那就很明显了，需要int空间的爆破。最终程序：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <assert.h>
    #include <string.h>
    #include <sys/mman.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/fcntl.h>
    
    #define __int8 char
    #define __int64 long long
    #define __int16 short
    #define _QWORD long long
    
    #define HIBYTE(x) (assert(sizeof(x) == 4), ((x) >> 24) & 0xff)
    #define BYTE2(x) (assert(sizeof(x) == 4), ((x) >> 16) & 0xff)
    #define BYTE1(x) (assert(sizeof(x) == 4), ((x) >> 8) & 0xff)
    #define HIWORD(x) (assert(sizeof(x) == 4), ((x) >> 16) & 0xffff)
    
    void* addr = NULL;
    unsigned char* table1;
    unsigned int* table3;
    unsigned int* table4;
    unsigned char* table5;
    
    void func2(unsigned __int8 *a1) {
      __int64 v1; // rdx
      __int64 v2; // rax
      __int64 v3; // rdx
      int v4[16]; // [rsp+0h] [rbp-68h]
      char v5[16]; // [rsp+40h] [rbp-28h]
      unsigned __int64 v6; // [rsp+58h] [rbp-10h]
    
      v1 = 0LL;
      v2 = 0LL;
      v4[0] = 0;
      v4[1] = 5;
      v4[2] = 10;
      v4[3] = 15;
      v4[4] = 4;
      v4[5] = 9;
      v4[6] = 14;
      v4[7] = 3;
      v4[8] = 8;
      v4[9] = 13;
      v4[10] = 2;
      v4[11] = 7;
      v4[12] = 12;
      v4[13] = 1;
      v4[14] = 6;
      v4[15] = 11;
      while ( 1 )
      {
        v5[v2++] = a1[v1];
        if ( v2 == 16 )
          break;
        v1 = v4[v2];
      }
      memcpy(a1, v5, 16);
    }
    
    void func2_rev(unsigned __int8 *a1) {
      __int64 v1; // rdx
      __int64 v2; // rax
      __int64 v3; // rdx
      int v4[16]; // [rsp+0h] [rbp-68h]
      char v5[16]; // [rsp+40h] [rbp-28h]
      unsigned __int64 v6; // [rsp+58h] [rbp-10h]
    
      v1 = 0LL;
      v2 = 0LL;
      v4[0] = 0;
      v4[1] = 5;
      v4[2] = 10;
      v4[3] = 15;
      v4[4] = 4;
      v4[5] = 9;
      v4[6] = 14;
      v4[7] = 3;
      v4[8] = 8;
      v4[9] = 13;
      v4[10] = 2;
      v4[11] = 7;
      v4[12] = 12;
      v4[13] = 1;
      v4[14] = 6;
      v4[15] = 11;
      while ( 1 )
      {
        // v5[v2++] = a1[v1];
        v5[v1] = a1[v2++];
        if ( v2 == 16 )
          break;
        v1 = v4[v2];
      }
      memcpy(a1, v5, 16);
    }
    
    void func1(unsigned __int8 *x, unsigned __int8 *a2);
    // 化简后的 func1 在上面
    
    void func1_rev(unsigned char* x) {
        unsigned int v5; // er12
        unsigned int v6; // eax
        unsigned int v7; // esi
        unsigned __int8 v8; // cl
        unsigned __int8 v9; // di
        unsigned __int8 v10; // cl
        unsigned __int8 v13; // di
        unsigned int v14; // eax
        unsigned int v15; // ecx
        unsigned int v16; // esi
        unsigned int v17; // er12
        unsigned int v21; // [rsp+4h] [rbp-134h]
    
        __int64 v25; // [rsp+10h] [rbp-128h]
        __int64 v26; // [rsp+18h] [rbp-120h]
        __int64 v27; // [rsp+20h] [rbp-118h]
        __int64 v28; // [rsp+28h] [rbp-110h]
    
        unsigned char* x_ptr;
        for (int j = 0; j < 16; j++) {
            for (int k = 0; k < 256; k++) {
                if (x[j] == table1[256 * j + 0x9000 + k]) {
                    x[j] = k;
                    break;
                }
            }
        }
    
        func2_rev(x);
    
        for (int i = 8; i >= 0; i--) {
            for (int j = 3; j >= 0; j--) {
                v25 = (i * 16 + j * 4) << 8;
                v26 = (i * 16 + j * 4 + 1) << 8;
                v27 = (i * 16 + j * 4 + 2) << 8;
                v28 = (i * 16 + j * 4 + 3) << 8;
    
                x_ptr = x + 4 * j;
                unsigned int value = (x_ptr[0] << 24) |
                    (x_ptr[1] << 16) |
                    (x_ptr[2] << 8) | x_ptr[3];
    
                unsigned int table[256 * 256];
                for (int a = 0; a < 256; a++) {
                    for (int b = 0; b < 256; b++) {
                        table[a * 256 + b] = value ^ table4[v25 + a] ^ table4[v26 + b];
                    }
                }
                value = 0;
                for (int a = 0; a < 256; a++) {
                    for (int b = 0; b < 256; b++) {
                        unsigned int k = table4[v27 + a] ^ table4[v28 + b];
                        for (int c = 0; c < 256 * 256; c++) {
                            if (k == table[c]) {
                                printf("Found: %d\n", 4 * i + j);
                                value = ((c / 256) << 24) |
                                    ((c % 256) << 16) |
                                    (a << 8) | b;
                                goto break_1;
                            }
                        }
                    }
                }
                printf("Not found: %d\n", 4 * i + j);
                exit(-1);
    
            break_1:
                // assert(value);
                for (int a = 0; a < 256; a++) {
                    for (int b = 0; b < 256; b++) {
                        table[a * 256 + b] = value ^ table3[v25 + a] ^ table3[v26 + b];
                    }
                }
                value = 0;
                for (int a = 0; a < 256; a++) {
                    for (int b = 0; b < 256; b++) {
                        unsigned int k = table3[v27 + a] ^ table3[v28 + b];
                        for (int c = 0; c < 256 * 256; c++) {
                            if (k == table[c]) {
                                printf("Found: %d\n", 4 * i + j);
                                value = ((c / 256) << 24) |
                                    ((c % 256) << 16) |
                                    (a << 8) | b;
                                goto break_2;
                            }
                        }
                    }
                }
                printf("Not found: %d\n", 4 * i + j);
                exit(-1);
    
            break_2:
                x_ptr[0] = (value >> 24) & 0xff;
                x_ptr[1] = (value >> 16) & 0xff;
                x_ptr[2] = (value >> 8) & 0xff;
                x_ptr[3] = value & 0xff;
            }
            func2_rev(x);
        }
    }
    
    int main() {
        struct stat sb;
    
        int fd = open("./hello", O_RDONLY);
        if (fd < 0) {
            perror("open");
            exit(-1);
        }
    
        if (fstat(fd, &sb) == -1) {
            perror("fstat");
            exit(-1);
        }
    
        addr = (unsigned char*) mmap(0, sb.st_size, PROT_READ, MAP_SHARED, fd, 0);
        if (addr == (unsigned char*) -1) {
            perror("mmap");
            exit(-1);
        }
    
        table1 = (unsigned char*) (addr + 0x1D9EA0);
        table3 = (unsigned int*) (addr + 0x1B4EA0);
        table4 = (unsigned int*) (addr + 0x18CEA0);
        table5 = (unsigned char*) (addr + 0x156EA0);
    
        // 0123456789abcdeffedcba9876543210
        unsigned char src[] = {
            0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef,
            0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10
        };
        unsigned char buf[16];
        unsigned char dst[] = {
            0xc9, 0xf7, 0x24, 0xd3, 0x1a, 0xe0, 0xf1, 0x83,
            0x70, 0x18, 0x02, 0x00, 0x11, 0xf3, 0x38, 0xba
        };
        /*
        func1(src, buf);
    
        for (int i = 0; i < 16; i++) {
            printf("0x%02x ", buf[i]);
            if ((i + 1) % 8 == 0) putchar('\n');
        }
        /**/
        /*
        0x50 0x6b 0x92 0xeb 0x8e 0xda 0x33 0xdf
        0x70 0xc8 0x48 0x62 0x48 0xec 0x30 0x1d
        /**/
        /*
        if (memcmp(buf, dst, 16) == 0) {
            puts("Right!");
        } else {
            puts("Wrong!");
        }
        /**/
    
        func1_rev(dst);
        for (int i = 0; i < 16; i++) {
            printf("0x%02x ", dst[i]);
            if ((i + 1) % 8 == 0) putchar('\n');
        }
        /*
        0xbc 0x94 0x60 0xb1 0x72 0x31 0xc7 0xe3
        0x74 0xbe 0x58 0x74 0x27 0xcc 0x3f 0x1a
        /**/
    
        //puts(dst);
    
        if (munmap(addr, sb.st_size) == -1) {
            perror("munmap");
            exit(-1);
        }
    
        return 0;
    }
    

跑几分钟就能得到结果了。

flag：`n1ctf{bc9460b17231c7e374be587427cc3f1a}`

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Ichild** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/260181](/post/id/260181)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [RE](/tag/RE)

 **+1** __1赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/LMicarFC5m2cLIeu7Rlg2TgkcvFQrOCchdA1ia1ZlunvFv4Mk1uJHJLibGDJTRZnDBm1nS2cicvKzRVp0AsSib0lUqA/132)
Ichild

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

