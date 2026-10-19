# 编译器对于加法运算的优化

## 优化常见的几种方式

### 常量传播

 **将编译期间可计算出结果的变量转换为常量，减少变量的使用**

    
    
    #include <iostream>
    int main()
    {
        int nVar = 1;
        printf("nVar = %d \n",nVar);
    }
    

对于上述代码，如果 **没有进行优化** ，那么处理的逻辑为：

![WeChat
Screenshot_20221012100902.png](https://image.3001.net/images/20221012/1665546192_634637d0a437242c9d5fa.png!small)

会先将该值放入栈中，在 `printf`要输出它时，再将其拿到 `esi`中，通过 `rsi`传给 `printf`进行输出

进行 **O1 优化以后**

![WeChat
Screenshot_20221012101047.png](https://image.3001.net/images/20221012/1665546205_634637ddaa824dbfc182b.png!small)

由于变量 `nVar`是一个在编译期间可以计算出结构的变量， **所以将其替换为常量，直接用 1 来替代，`printf`要使用时直接传入 1 即可**

 **O2 优化中在对变量的处理一致**

![WeChat
Screenshot_20221012101142.png](https://image.3001.net/images/20221012/1665546215_634637e7110484b48cc4d.png!small)

### 常量折叠

 **在公式中出现多个常量进行计算的情况中，且编译器可以算出结果的情况下，在编译期间直接用计算结果替代**

    
    
    #include <iostream>
    
    int main()
    {
        int nNum = 1 + 8 * 7 - 10;
        printf("nNum = %d \n",nNum);
    
    }
    

对于上述代码，如果 **没有进行优化** ，那么处理的逻辑为：

![WeChat
Screenshot_20221012102428.png](https://image.3001.net/images/20221012/1665546229_634637f54b7be98060dbe.png!small)

但其实这也进行了一定的优化，没有将常量的计算生成对应的计算指令，而是编译器直接将计算的结果传入栈中，接下来再从栈中拿值

进行 **O1 优化以后**

![WeChat
Screenshot_20221012103012.png](https://image.3001.net/images/20221012/1665546240_634638001237576fbad09.png!small)

此时在上面的基础上， **没有将结果放入栈中，由于后面`printf`要使用该参数，直接传入 `edx`**，后面通过 `rdx`直接传入 `printf`

### 复写传播

    
    
    #include <iostream>
    
    int main(int argc)
    {
        int nNum = argc;
        printf("nNum = %d \n",nNum);
    }
    

此时我们将 `main`函数的参数值赋给了 `main`中的变量 `nNum`

对于上述代码，如果 **没有进行优化** ，那么处理的逻辑为：

![WeChat
Screenshot_20221012111407.png](https://image.3001.net/images/20221012/1665546250_6346380aa833ba48a0ac5.png!small)

可以看到，为了将 `edi`中的的参数 1 （`argc`）放入到栈 `nNum`的位置，进行了很繁琐的操作

进行 **O1 优化以后**

![WeChat
Screenshot_20221012111747.png](https://image.3001.net/images/20221012/1665546258_63463812e6fc279337e71.png!small)

直接删除掉了 `nNum`（因为之后没有对 `nNum`重新赋值） 用存在于 `edi`中刚刚传入的 `argc`值直接代替他就完事了

![WeChat
Screenshot_20221012111131.png](https://image.3001.net/images/20221012/1665546273_634638216057d8fc88874.png!small)  
后面调用 `printf`时，由于其已经被传入了 `edi`，若直接通过 `rdi`传给 `printf`就完事了，非常的简便

## 具体在代码中的优化

    
    
    #include <cstdio>
    #include <iostream>
    
    int main()
    {
        int nVarOne = 0;
        int nVarTwo = 0;
    
        nVarOne = nVarOne + 1;
    
        nVarOne = 1 + 2;
    
        nVarOne = nVarOne + nVarTwo;
    
        printf("nVarOne = %d \n",nVarOne);
    
        return 0;
    }
    

对于上述代码，如果 **没有进行优化** ，那么处理的逻辑为：

![WeChat
Screenshot_20221012093319.png](https://image.3001.net/images/20221012/1665546287_6346382f3679e0611dfde.png!small)

但还是在编译期间提前做了进行了简单的将常量的计算

进行 **O1 优化以后**

![WeChat
Screenshot_20221012104338.png](https://image.3001.net/images/20221012/1665546295_63463837656a7536f611b.png!small)

代码结构发生大变，处理的流程为：

  1. 常量替换变量，所以 `nVarOne``nVarTwo`开始都被直接替换为常量 0

  2. 接下来代码中对 `nVarOne`做了两次赋值操作，由于第二次赋值操作会覆盖第一次赋值的操作，所以直接去掉第一次赋值，第二次赋值为 3

  3. 再次用常量替换变量，由于 `printf`会使用到该参数，直接把 3 传入 `edx`，等待后续通过 `rdx`传入 `printf`即可

所以最终反映到汇编指令中，只有一条 `mov edx,0x3`实属省事啊。。。

