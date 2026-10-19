## 前言

Z3是Microsoft
Research开发的高性能定理证明器。Z3拥有者非常广泛的应用场景：软件/硬件验证和测试，约束求解，混合系统分析，安全性研究，生物学研究（计算机分析）以及几何问题。Z3Py是使用Python脚本来解决一些实际问题，Z3Py在windows下的安装可以参考如下链接：[https://github.com/Z3Prover/z3/wiki/Using-Z3Py-on-Windows。](https://github.com/Z3Prover/z3/wiki/Using-Z3Py-on-Windows%E3%80%82)Z3Py的使用教学可以参考如下链接： <https://ericpony.github.io/z3py-tutorial/guide-examples.htm>

## CTF逆向中的应用

现在的CTF逆向中，求解方程式或者求解约束条件是非常常见的一种考察方式，而ctf比赛都是限时的，当我们已经逆向出来flag的约束条件时，可能还需要花一定的时间去求解逆过程。而Z3求解器就给我们提供了一个非常便利求解方式，我们只需要定义未知量（x,y等），然后为这些未知量添加约束方式即可求解。Z3求解器能够求解任意多项式，但是要注意的是，当方程的方式为2**x这种次方运算的时候，方程式已经不是多项式的范畴了，Z3便无法求解。

## 基本使用

现在我们利用官方文档中的一个例子来粗略的看一下Z3Py的使用。

    
    
    x = Int('x')
    y = Int('y')
    solve(x > 2, y < 10, x + 2*y == 7)
    

代码非常简单，首先利用Int()定义两个int型未知数x和y，然后利用三个约束条件进行相应的求解：

  1. x > 2
  2. y < 10
  3. x + 2*y == 7

由上述的代码看得出来Z3Py的使用方式比较简单，

  1. 定义未知量
  2. 添加约束条件
  3. 然后求解

## CTF中的示例

### XXX比赛中的逆向题

首先我们利用IDA去打开该文件，定位到关键点，发现关键函数如下：

    
    
    signed __int64 sub_400766()
    {
      if ( strlen((const char *)&stru_6020A0) != 32 )
        return 0LL;
      v3 = stru_6020A0.y1;
      v4 = stru_6020A0.y2;
      v5 = stru_6020A0.y3;
      v6 = stru_6020A0.y4;
      if ( stru_6020A0.x2 * (signed __int64)stru_6020A0.x1 - stru_6020A0.x4 * (signed __int64)stru_6020A0.x3 != 0x24CDF2E7C953DA56LL )
        goto LABEL_15;
      if ( 3LL * stru_6020A0.x3 + 4LL * stru_6020A0.x4 - stru_6020A0.x2 - 2LL * stru_6020A0.x1 != 0x17B85F06 )
        goto LABEL_15;
      if ( 3 * stru_6020A0.x1 * (signed __int64)stru_6020A0.x4 - stru_6020A0.x3 * (signed __int64)stru_6020A0.x2 != 0x2E6E497E6415CF3ELL )
        goto LABEL_15;
      if ( 27LL * stru_6020A0.x2 + stru_6020A0.x1 - 11LL * stru_6020A0.x4 - stru_6020A0.x3 != 0x95AE13337LL )
        goto LABEL_15;
      srand(stru_6020A0.x3 ^ stru_6020A0.x2 ^ stru_6020A0.x1 ^ stru_6020A0.x4);
      v1 = rand() % 50;
      v2 = rand() % 50;
      v7 = rand() % 50;
      v8 = rand() % 50;
      v9 = rand() % 50;
      v10 = rand() % 50;
      v11 = rand() % 50;
      v12 = rand() % 50;
      if ( v6 * v2 + v3 * v1 - v4 - v5 != 0xE638C96D3LL
        || v6 + v3 + v5 * v8 - v4 * v7 != 0xB59F2D0CBLL
        || v3 * v9 + v4 * v10 - v5 - v6 != 0xDCFE88C6DLL
        || v5 * v12 + v3 - v4 - v6 * v11 != 0xC076D98BBLL )
      {
    LABEL_15:
        result = 0LL;
      }
      else
      {
        result = 1LL;
      }
      return result;
    }
    

可以看得出来这个题目的目的就是找出满足方程的flag。我们可以很方便的把方程式列出来，但是求解对于一些数学不是很好的人来说简直就是噩梦，这时候Z3求解器就可以很方便的给我们帮助。我们按照题目的意思一步一步利用Z3求解器来求解：

    
    
    from z3 import *
    x1 = Int('x1')
    x2 = Int('x2')
    x3 = Int('x3')
    x4 = Int('x4')
    s = Solver()
    s.add( x2*x1-x4*x3 == 0x24CDF2E7C953DA56)
    s.add( 3*x3+4*x4-x2-2*x1 == 0x17B85F06)
    s.add( 3*x1*x4-x3*x2 == 0x2E6E497E6415CF3E)
    s.add( 27*x2+x1-11*x4 - x3 == 0x95AE13337)
    print s.check()
    m = s.model()
    print "traversing model..."
    for d in m.decls():
        print "%s = %s" % (d.name(), m[d])
    

Solver()命令创建一个通用求解器。我们可以通过add函数添加约束条件。我们称之为声明约束条件。check()函数解决声明的约束条件，sat结果表示找到某个合适的解，unsat结果表示没有解。这时候我们称约束系统无解。最后，求解器可能无法解决约束系统并返回未知作为结果。

对于上面的题目我们首先定义x1,x2,x3,x4四个int变量，然后添加逆向中的约束条件，最后进行求解。Z3会在找到合适解的时候返回sat。我们认为Z3能够满足这些约束条件并得到解决方案。该解决方案被看做一组解决约束条件的模型。模型能够使求解器中的每个约束条件都成立。最后我们遍历model中的解。

得到x1,x2,x3,x4的解后，我们将其代入逆向题中，得出v1,v2,v7,v8,v9,v9,v10,v11,v12的值，然后进行下一步的求解：

    
    
    v1 = 0x16
    v2 = 0x27
    v7 = 0x2d
    v8=  0x2d
    v9 = 0x23 
    v10= 0x29 
    v11 = 0xd
    v12 = 0x24
    v3 = Int('v3')
    v4 = Int('v4')
    v5 = Int('v5')
    v6 = Int('v6')
    s = Solver()
    s.add(v6 * v2 + v3 * v1 - v4 - v5 == 0xE638C96D3)
    s.add(v6 + v3 + v5 * v8 - v4 * v7 == 0xB59F2D0CB)
    s.add(v3 * v9 + v4 * v10 - v5 - v6 == 0xDCFE88C6D)
    s.add(v5 * v12 + v3 - v4 - v6 * v11 == 0xC076D98BB) 
    print s.check()
    m = s.model()
    print "traversing model..."
    for d in m.decls():
        print "%s = %s" % (d.name(), m[d])
    

这样的话我们就花了比较少的时间得到我们想要的flag，还是比较方便的。

但是现实中很多的逆向题都是基于位运算的，同样在Z3Py中可以使用Bit_Vectors进行机器运算。它们能够实现无符号和有符号二进制运算。Z3为符号数运算提供了一个特殊的运算符操作版本，其中运算符<，<=，>，>
=，/，％和>>对应于有符号运算。 相应的无符号运算符是ULT，ULE，UGT，UGE，UDiv，URem和LShR。我们看一下如下的代码就能清楚许多：

    
    
    # Create to bit-vectors of size 32
    x, y = BitVecs('x y', 32)
    solve(x + y == 2, x > 0, y > 0)
    # Bit-wise operators
    # & bit-wise and
    # | bit-wise or
    # ~ bit-wise not
    solve(x & y == ~y)
    solve(x < 0)
    # using unsigned version of < 
    solve(ULT(x, 0))
    

Z3Py同样支持了Python中的创建List的方式，我们看如下代码：

    
    
    # Create list [1, ..., 5] 
    print [ x + 1 for x in range(5) ]
    # Create two lists containing 5 integer variables
    X = [ Int('x%s' % i) for i in range(5) ]
    Y = [ Int('y%s' % i) for i in range(5) ]
    print X
    # Create a list containing X[i]+Y[i]
    X_plus_Y = [ X[i] + Y[i] for i in range(5) ]
    print X_plus_Y
    # Create a list containing X[i] > Y[i]
    X_gt_Y = [ X[i] > Y[i] for i in range(5) ]
    print X_gt_Y
    print And(X_gt_Y)
    # Create a 3x3 "matrix" (list of lists) of integer variables
    X = [ [ Int("x_%s_%s" % (i+1, j+1)) for j in range(3) ]
          for i in range(3) ]
    pp(X)
    

在上面的例子中，表达式“x％s”％i返回一个字符串，其中％s被替换为i的值。命令pp与print类似，但是它使用Z3Py格式化程序而不是Python的格式化程序来使用列表和元组。

## 第八届极客大挑战的REConvolution

我们打开文件，也是比较直观的看到约束条件，我试着逆向了这个过程，花费了挺多的时间才得到答案，但是如果我们使用Z3Py来求解的话就会非常的快。

函数关键部分如下：

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      unsigned int ii; // esi
      unsigned int v4; // kr00_4
      char flag_i; // bl
      unsigned int jj; // eax
      char *v7; // edx
      char v8; // cl
      int v9; // eax
      char xor_result[80]; // [esp+8h] [ebp-A4h]
      char flag[80]; // [esp+58h] [ebp-54h]
      sub_DC1020("Please input your flag: ");
      sub_DC1050("%40s", flag);
      memset(xor_result, 0, 0x50u);
      ii = 0;
      v4 = strlen(flag);
      if ( v4 )
      {
        do
        {
          flag_i = flag[ii];
          jj = 0;
          do
          {
            v7 = &xor_result[jj + ii];
            v8 = flag_i ^ data1[jj++];
            *v7 += v8;
          }
          while ( jj < 0x20 );
          ++ii;
        }
        while ( ii < v4 );
      }
      v9 = strcmp(xor_result, (const char *)&data2);
      if ( v9 )
        v9 = -(v9 < 0) | 1;
      if ( v9 )
        puts("No, it isn't.");
      else
        puts("Yes, it is.");
      return 0;
    }
    

很简洁明了，我们利用Z3Py来进行变量的声明和约束的增加并进行求解

    
    
    from z3 import *
    s = Solver()
    X =  [BitVec(('x%s' % i),8) for i in range(0x22) ]
    data1 =  [0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x29,0x2A,0x2B,0x2C,0x2D,0x2E,0x2F,0x3A,
    0x3B,0x3C,0x3D,0x3E,0x3F,0x40,0x5B,0x5C,0x5D,0x5E,0x5F,0x60,0x7B,0x7C,0x7D,0x7E]
    data2 = [0x72,0xE9,0x4D,0xAC,0xC1,0xD0,0x24,0x6B,0xB2,0xF5,0xFD,0x45,0x49,0x94,0xDC,0x10,
    0x10,0x6B,0xA3,0xFB,0x5C,0x13,0x17,0xE4,0x67,0xFE,0x72,0xA1,0xC7,0x04,0x2B,0xC2,
    0x9D,0x3F,0xA7,0x6C,0xE7,0xD0,0x90,0x71,0x36,0xB3,0xAB,0x67,0xBF,0x60,0x30,0x3E,
    0x78,0xCD,0x6D,0x35,0xC8,0x55,0xFF,0xC0,0x95,0x62,0xE6,0xBB,0x57,0x34,0x29,0x0E,3]
    xor_result = [0]*0x41
    for m in range(0,0x22):
        for n in range(0,0x20):
            xor_result[n+m] += X[m] ^ data1[n]
    for o in range(0,0x41):
        s.add(xor_result[o] == data2[o])
    print s.check()
    m = s.model()
    print "traversing model..."
    for i in range(0,0x22):
        print chr(int("%s" % (m[X[i]]))),
    

很简单的几行代码，声明0x22个8位BitVec的未知数，获取数据，然后增加约束条件，求解，这样就能够帮助我们获取flag。

题目链接：<https://pan.baidu.com/s/1o8QdFIE>

## 总结

虽然CTF逆向比赛中重点考察的是逆向的能力，采用求解器的方式来求解并不能锻炼到自己的逆向逻辑，REConvolution逆向题目有一个非常清晰明了的逆过程，还是很有趣的。

 *** 本文作者：foyjog，转载请注明来自FreeBuf.COM**

