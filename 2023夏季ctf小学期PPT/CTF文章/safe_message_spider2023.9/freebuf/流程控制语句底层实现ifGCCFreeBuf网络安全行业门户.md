# if 流程控制语句

if 语句的功能是现对运算条件进行比较，然后根据比较结果选择对应语句进行执行

if 语句只能判断两种情况：

  * 0 假

  * 非0 真

### if 语句

    
    
    #include <stdio.h>  
    ​  
    int main(int argc,char** argv)  
    {  
    if (argc == 0)  
    {  
       printf("argc == 0");  
    }  
    return 0;  
    }

汇编

![1669265781_637ef9751f61c7e8433a9.png!small?1669265777476](https://image.3001.net/images/20221124/1669265781_637ef9751f61c7e8433a9.png!small?1669265777476)

关于`if`判断在汇编中实现的部分：

    
    
    115c:       83 7d fc 00             cmp    DWORD PTR [rbp-0x4],0x0  
    1160:       75 14                 jne    1176 <main+0x2d>

之前已经将`argc`的值放入通过`edi`放入了`rbp-0x4`地址处的栈空间中

  * `cmp DWORD PTR [rbp-0x4],0x0`

使用`CMP`指令，将`rbp-0x4`地址处的`4`字节数据与`0`相减，并影响标志位，由于之后的`jne`关注的是`ZF`标志位，所以此处说明`CMP`对`ZF`标志位的影响：

    *  **结果 = 0 则`ZF = 1`**

  * `jne 1176 <main+0x2d>`

    * 若`ZF = 0`则进行跳转，也就是说若`argc != 0`则跳转到`return 0;`（`mov eax,0x0`）的语句

    * 否则继续向下执行执行`if`中的语句

可以发现处理的逻辑是： **若不满足`if`判断的语句进行跳转，若满足则继续执行，这显然与`C`语言的逻辑是相反的：**

这是由于`C`语言是根据代码行的位置来决定编译后二进制代码的地址高地的，便于使用标号相减得到代码的长度，所以
**`C`语言的编译器不能随意改变代码行在内存中的顺序，所以`if`先进性不满足跳转的判断，若满足直接向下执行即可**

所以依据这个特性，若判断的语句为`argc > 0`则`cmp`后紧跟的跳转语句的条件应该是`argc <= 0`的

![1669265647_637ef8ef38b41e3521319.png!small](https://image.3001.net/images/20221124/1669265647_637ef8ef38b41e3521319.png!small)

关于`if`判断在汇编中实现的部分：

    
    
    115c:       83 7d fc 00             cmp    DWORD PTR [rbp-0x4],0x0  
    1160:       7e 14                 jle    1176 <main+0x2d>

  * `jle 1176 <main+0x2d>`

`ZF = 1 || SF != OF`则进行跳转（`jle`小于或等于跳转（若`leftOp ≤ rightOp`））

### if...else 语句

    
    
    #include <stdio.h>  
    ​  
    int main(int argc,char** argv)  
    {  
    if (argc == 0)  
    {  
       printf("argc == 0");  
    }  
    else  
    {  
       printf("argc != 0");  
    }  
    return 0;  
    }    

汇编

![1669265877_637ef9d558df2edfedc97.png!small?1669265874034](https://image.3001.net/images/20221124/1669265877_637ef9d558df2edfedc97.png!small?1669265874034)

关于`if...else`判断在汇编中实现的部分：

    
    
    115c:       83 7d fc 00             cmp    DWORD PTR [rbp-0x4],0x0  
    1160:       75 16                 jne    1178 <main+0x2f>  
    ......  
    ......  
    1176:       eb 14                 jmp    118c <main+0x43>

`if...else`最初的比较与跳转过程与单`if`是一致的，唯一的区别在于`1176`行的`jmp`语句，由于在执行完`if`中的语句后不能再去执行`else`里的语句，所以要用一个`jmp`跳到`else`后的语句

所以在还原汇编代码时，若出现上述`3`条汇编语句的组合，可初步判断存在`if...else`语句，且`jmp`的位置位于源代码中`if`语句块的末尾与`else`语句块的开头

 **O1优化下的 if...else**

在`O1`的优化下，`if...else`分支语句在汇编层面的优化处理很有意思，还是上述代码，若在编译时加上`-O1`的优化（`O2`也类似），则汇编代码为

![1669265905_637ef9f1c1813936182e6.png!small?1669265902221](https://image.3001.net/images/20221124/1669265905_637ef9f1c1813936182e6.png!small?1669265902221)

关于`if...else`判断在汇编中实现的部分很巧妙，一步一步来看，首先是：

    
    
    1151:       85 ff                 test   edi,edi          
    1153:       75 20                 jne    1175 <main+0x2c>

由于我们代码中是比较`argc == 0`，所以此处省去了将`0`入栈再通过`cmp`与`edi`中`argc`的值相比较

而是直接使用`test`命令，`edi`（`argc`）中的值与自身做与运算：

  * 若`argc == 0`则与运算后依旧为`0`则`ZF = 1`不会通过`jne`跳转，而是继续往下执行`if`语句块中的代码

  * 若`argc == 1`则与运算后依旧为`1`则`ZF = 0`,所以说明`if`的条件不满足，转去`jne`到`else`的代码中执行

此处 最妙
的地方就来了，此处，在`if`的语句块与`else`的语句块中间并没有看见刚刚提到的`jmp`指令，反而看到了用于函数返回的`ret`指令，而却在结尾处发现了一个`jmp`用于跳回到`ret`指令的地址处

 **所以此时的逻辑就变成了：**

  *  **首先判断是否满足`if`的条件**

    *  **满足** ： 接着向下执行，由于本代码中除了`if...else`语句块外，并没有其余的代码，所以执行到`1174`行，直接通过`ret`返回即可

    *  **不满足** ：`jne`跳转到`else`的语句块中

  * 执行完`else`语句块后，通过最后一个`jmp`跳到位于`1174`行的`ret`返回即可

### if...else if...else 多分枝结构

    
    
    #include <stdio.h>  
    ​  
    ​  
    int main(int argc,char** argv)  
    {  
      if (argc > 0 )  
      {  
          printf("argc > 0");  
      }  
      else if (argc == 0)  
      {  
          printf("argc == 0");  
      }  
      else  
      {  
          printf("argc <= 0");  
      }  
    ​  
     return 0;  
    }

汇编

![1669265984_637efa402d981b80bf6e0.png!small?1669265980700](https://image.3001.net/images/20221124/1669265984_637efa402d981b80bf6e0.png!small?1669265980700)

可以看到`if`与`else
if`的逻辑相同，都是通过`cmp/test`判断后后不满足条件的跟跳转语句，虽然他们组合在一起，但每个`if`和`else...if`又是独立的

  * `if (argc > 0 )`
    
        115c:       83 7d fc 00             cmp    DWORD PTR [rbp-0x4],0x0  
    1160:       7e 16                 jle    1178 <main+0x2f>  
    ; <= 则跳转

  * `else if (argc == 0)`
    
        1178:       83 7d fc 00             cmp    DWORD PTR [rbp-0x4],0x0  
    117c:       75 16                 jne    1194 <main+0x4b>  
    ; != 则跳转

  * `jmp`跳转语句
    
        1176:       eb 30                 jmp    11a8 <main+0x5f>  
    ......  
    1192:       eb 14                 jmp    11a8 <main+0x5f>  
    ; 防止执行完 if 或 if...else 后再次执行 else

 **O1优化下的 if...else if...else**

![1669266016_637efa60487922340f9f2.png!small?1669266012780](https://image.3001.net/images/20221124/1669266016_637efa60487922340f9f2.png!small?1669266012780)

在`O1`优化的条件下，

    
    
    1151:       85 ff                 test   edi,edi  
    1153:       7f 1a                 jg     116f <main+0x26>  
    1155:       75 38                 jne    118f <main+0x46>

此处直接看可能不止所云，好像不知道它想干什么，但仔细看我们要输出的字符串的位置已经被改变了，当前汇编代码的结构已经发生了变化

  * `1157 - 1168`行对应的是满足`else if (argc == 0)`要执行的语句

  * `116f - 1180`行对应的是满足`if (argc > 0 )`要执行的语句块

  * `118f - 11a0`行对应的是最后都不满足走`else`要执行的语句块

所以通过`jg 116f <main+0x26>`判断若`> 0`则直接跳到`116f if`处

若不满足，再通过`jne 118f <main+0x46>`判断若`!= 0`，经前面的判断又说明不大于`0`所以跳到`118f else`处

否则`== 0`接着执行`else if (argc == 0)`

 **这样通过对语句顺序的改变仅使用一个判断指令 test 就完成了所有情况跳转的判断**

