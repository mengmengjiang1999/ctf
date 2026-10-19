本篇文章是在《Gdb调试复现Dirty
Pipe漏洞（CVE-2022-0847）之用户态调试》（参考链接：https://www.freebuf.com/vuls/330722.html）的基础上，继续深入到内核态进行调试。所以，各位看官可以先看看用户态调试的内容再看本篇内核态调试，当然，技术大牛可直接看内核态调试。

##  **第一、准备环节-增加内核调试辅助语句：**

首先，为了更好的查看关键因素的变化：稍微做了两处修改：

第一处:splice前后，增加getchar和puts;

![](https://image.3001.net/images/20220509/1652078320_6278b6f04f5db0bdf9c89.png!small)第二处:prepare
pipe过程中，增加getchar和puts;

![](https://image.3001.net/images/20220509/1652078352_6278b7108b699036eec82.png!small)修改后代码执行结果如下：

![](https://image.3001.net/images/20220509/1652078375_6278b727a43555f266277.png!small)下面内容重点关注程序运行启动之后，该漏洞利用的两个关键要素：prepare_pipe函数、splice函数的内核态分析，此外对只读的suid文件的写入进行分析。

##  **第二、关键因素-prepare_pipe函数的内核调试**

这里的prepare_pipe函数有两个环节：第一个环节是write循环，第二个环节是read循环。

在第一个环节中，当程序执行到prepare_pipe函数中write循环，这里的内核态重点是关注flag信息，此时执行状态如下：![](https://image.3001.net/images/20220509/1652078443_6278b76b3ce1ce0749ef5.png!small)

对应的内核态执行内容：

![](https://image.3001.net/images/20220509/1652078508_6278b7acdfb54a6b17510.png!small)一步一步的调试，查看flags数值变化：

![](https://image.3001.net/images/20220509/1652078540_6278b7cc03ca1f8417ee0.png!small)结合如下的代码

![](https://image.3001.net/images/20220509/1652078556_6278b7dc83708973c2fb3.png!small)可以看到517行将该flags设置为0x10，也就是can
merge，这里以pipe->bufs[1]->flags为例，看内核流程和对应的变量。

![](https://image.3001.net/images/20220509/1652078588_6278b7fc1b522fed91bef.png!small)这里只是显示了一次循环的结果，总计有16次循环，都会将此flags设置为can
merge标记。

第二个环节就是进入到read循环，对应的执行状态和代码如下：

![](https://image.3001.net/images/20220509/1652078709_6278b875628508774cfda.png!small)![](https://image.3001.net/images/20220509/1652078619_6278b81b71c75b7ee572a.png!small)Read完成后，原有的flag没有改变，依旧是0x10，最终prepare_pipe结束之前得到的flags信息如下：

![](https://image.3001.net/images/20220509/1652078817_6278b8e1cb13b7e00c0ca.png!small)

![](https://image.3001.net/images/20220509/1652078874_6278b91a77316343d9cad.png!small)其中，显示3个bufs对应的flags的位置如下：

![](https://image.3001.net/images/20220509/1652078832_6278b8f0150318470356a.png!small)从而可以看出，prepare_pipe已经顺利完成了flags的设置，全部设置为can
merge的flag。

##  **第三、关键因素-splice函数的内核调试**

设置断点

![](https://image.3001.net/images/20220509/1652078983_6278b98722e7d8a80d423.png!small)对应此时的内核代码：

![](https://image.3001.net/images/20220509/1652079092_6278b9f4cefb662c0c2f9.png!small)以及对应的栈帧信息

![](https://image.3001.net/images/20220509/1652079110_6278ba0617e3539440188.png!small)进入该函数之后，可以查看flags，根据我们在用户态的推断，此时应该是0x10，gdb显示确实也是如此：

![](https://image.3001.net/images/20220509/1652079136_6278ba20bff7a5f5d3c42.png!small)此图说明，第一个要素此时已经准备好了。下面就是splice里面的关键的page的赋值

在尚未执行到buf-page=page时，这里的buf->page和page的值如下：

![](https://image.3001.net/images/20220509/1652079193_6278ba593249caeecde97.png!small)完成page赋值之后，pipe的bufs[0]，已经赋值为chsh这个suid文件的page了。

![](https://image.3001.net/images/20220509/1652079210_6278ba6a5522cfa76733a.png!small)

请记下此处的page信息0xffffea00002b3000，这里的page就是后续我们write函数的目的地址。只有能够write到这个page中，才能算是漏洞利用成功。

##  **第四、将elfcode写入到只读suid文件对应的可读写的内存page中**

设置write断点：

![](https://image.3001.net/images/20220509/1652079302_6278bac6a50a400af0c3c.png!small)对应的用户态代码如下

![](https://image.3001.net/images/20220509/1652079317_6278bad5479c172bbbdca.png!small)一步一步调试进入到内核态中if判断的分支中：

![](https://image.3001.net/images/20220509/1652079341_6278baed43724ca3dd4cb.png!small)此时，各个变量对应的数值如下：

![](https://image.3001.net/images/20220509/1652079368_6278bb083a42f377d0f7a.png!small)此时，该page就是/usr/bin/chsh这个suid文件在内存中的page，因为该page的flag为0x10，can
merge，所以，后续的内容只要不超过这个page大小，就会继续在这个page中写入。这里的chars就是elfcode。大小只有0x196，加上1之后，不超过一个page的大小。所以，就直接覆写到该page中了。这里的操作就是本漏洞利用的重点。

该处函数执行流会进入到如下代码段：

![](https://image.3001.net/images/20220509/1652079552_6278bbc0b91667f67d32f.png!small)此时453行的ret为0，接着执行copy_page_from_iter函数，查看此时的汇编代码：

![](https://image.3001.net/images/20220509/1652079592_6278bbe8d3e64ae8c3c30.png!small)

此时，就查看调用时的参数，终于可以确认该pipe_write函数的目的是处于0xffffea00002b3000的page。

此处执行的copy_page_from_iter的C代码如下：

![](https://image.3001.net/images/20220509/1652079756_6278bc8c181b8b8fbd28b.png!small)

![](https://image.3001.net/images/20220509/1652080203_6278be4b4f5a2d6e73a6b.jpg!small)接着进入到copy_page_from_iter_iovec，

![](https://image.3001.net/images/20220509/1652080274_6278be9230cd278abb08d.jpg!small)进入copy_page_from_iter_iovec函数的栈之后：

![](https://image.3001.net/images/20220509/1652080061_6278bdbd23e010c972bd7.png!small)然后查看该函数中关键的变量page和buf信息如下：

![](https://image.3001.net/images/20220509/1652080017_6278bd9129e8d67683226.png!small)此时，由上图可见，最核心的两个参数都已经准备好了，page就是我们前面得到的可以merge的page，而拷贝的内容就是buf，也是我们准备好的elfcode。该流程继续执行下去就完成了将elfcode拷贝到该page中，而该page对应着具有suid权限的/usr/bin/chsh文件。

至此，内核态最核心的两个关键要素以及写入suid文件对应的page这三个部分就差不多了，剩下的就参考用户态调试即可。还是要感谢发现这个漏洞的Max
Kellermann以及国内众多针对这个漏洞的展开详细描述的各位专家。这两篇文章（用户态调试和内核态调试）如有不到之处，还请各位多指教。最后，完结散花。

