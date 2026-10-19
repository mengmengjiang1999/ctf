## 前言

**今天给大家介绍的是一款名叫Sandsifter的x86处理器模糊测试工具。该工具可以通过系统生成的机器码来搜索处理器指令集，并通过监控异常数据来审计x86处理器中的隐藏指令和硬件漏洞。Sandsifter目前已经成功识别出了大部分处理器产品中的隐藏处理器指令，反汇编器、编译器和模拟器中普遍存在的软件漏洞，企业管理程序中的安全缺陷，以及x86芯片中关键的硬件安全漏洞。**

![页首配图](https://image.3001.net/images/20181021/1540108904_5bcc326826144.png!small)

由于目前市场上仍存在着大量x86处理器，因此该工具的主要目的就是帮助广大用户检查自己系统中的隐藏指令以及安全漏洞。

大家可以直接运行下列命令来对自己的处理器进行基础审计：

    
    
    sudo./sifter.py --unk --dis --len --sync --tick -- -P1 -t

接下来，计算机会自动扫描异常指令。在上图的上半部分中，大家可以查看Sandsifter已测试的指令信息。图片的下半部分显示的是Sandsifter检测到的异常情况。整个搜索过程大约需要1个小时或1天的时间不等，具体取决于处理器的运算速度以及架构复杂程度。扫描完成之后，Sandsifter会将结果报告给用户：

    
    
    ./summarize.py data/log

![sandsifter_1_sandsifter.gif](https://image.3001.net/images/20181022/15402120402373.gif!small)

一般来说，该工具能够扫描出你处理器中的好几百万条隐藏指令，不过工具会帮你进行自动分类。在对异常数据进行分析和筛选之后，工具会将每一条指令分配到不同的目录中：

> 软件漏洞；
>
> 硬件漏洞；
>
> 隐藏指令；

按下“Q”键退出后，你可以获取到文字版的系统扫描结果：

虽然工具会对扫描结果进行自动化分类，但是具体的分析仍需要大家人工参与。如果你需要专业人员帮助你分析数据的话，你可以将./data/log文件发送至xoreaxeaxeax@gmail.com。

## 代码构建

Sandsifter首先需要安装[Capstone](https://www.kitploit.com/search/label/Capstone)反汇编器：【[传送门](http://www.capstone-engine.org/)】。常用的安装命令如下：

    
    
    sudo apt-get install libcapstone3 libcapstone-dev
    
    sudo pip install capstone

Sandsifter构建命令：

    
    
    make

然后运行：

    
    
    sudo ./sifter.py --unk --dis --len --sync --tick -- -P1 -t

## Flag

大家可以使用--flag来给sifter传递标记值，使用-- -f来给注入器传递数据：

    
    
    sudo ./sifter.py --unk --dis --len --sync --tick -- -P1 -t

### Sifter标记：

    
    
    --len
    
     search for length differences in allinstructions (instructions that
    
     executed differently than the disassemblerexpected, or did not
    
     exist when the disassembler expected them to
    
    --dis
    
     search for length differences in validinstructions (instructions that
    
     executed differently than the disassemblerexpected)
    
    --unk
    
     search for unknown instructions (instructionsthat the disassembler doesn't
    
     know about but successfully execute)
    
    --ill
    
     the inverse of --unk, search for invaliddisassemblies (instructions that do
    
     not successfully execute but that thedisassembler acknowledges)
    
    --tick
    
     periodically write the current instruction todisk
    
    --save
    
     save search progress on exit
    
    --resume
    
     resume search from last saved state
    
    --sync
    
     write search results to disk as they are found
    
    --low-mem
    
     do not store results in memory

### Injector标记：

    
    
    -b
    
    mode: brute force
    
    -r
    
    mode: randomized fuzzing
    
    -t
    
    mode: tunneled fuzzing
    
    -d
    
    mode: externally directed fuzzing
    
    -R
    
    raw output mode
    
    -T
    
    text output mode
    
    -x
    
    write periodic progress to stderr
    
    -0
    
    allow null dereference (requires sudo)
    
    -D
    
    allow duplicate prefixes
    
    -N
    
    no nx bit support
    
    -sseed
    
    in random search, seed value
    
    -Bbrute_depth
    
    in brute search, maximum search depth
    
    -Pmax_prefix
    
    maximum number of prefixes to search
    
    -iinstruction
    
    instruction at which to start search(inclusive)
    
    -einstruction
    
    instruction at which to end search (exclusive)
    
    -ccore
    
    core on which to perform search
    
    -Xblacklist
    
    blacklist the specified instruction
    
    -jjobs
    
    number of simultaneous jobs to run
    
    -lrange_bytes
    
    number of base instruction bytes in each subrange

### 快捷键

> M：模式-修改搜索模式；
>
> Q：退出-退出Sifter；
>
> P：暂停-暂停或继续搜索任务；

## 参考资料

> 1\. <https://www.youtube.com/watch?v=KrksBdWcZgQ>
>
> 2\.
> <https://github.com/xoreaxeaxeax/sandsifter/blob/master/references/domas_breaking_the_x86_isa_wp.pdf>
>
> 3\.
> <https://github.com/xoreaxeaxeax/sandsifter/blob/master/references/domas_breaking_the_x86_isa.pdf>

***参考来源：[kitploit](https://www.kitploit.com/2018/10/sandsifter-x86-processor-fuzzer.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

