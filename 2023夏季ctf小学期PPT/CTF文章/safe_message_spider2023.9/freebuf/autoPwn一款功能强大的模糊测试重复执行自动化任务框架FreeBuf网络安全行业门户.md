**今天给大家介绍的是一款名叫autoPwn的强大工具，广大研究人员可以利用这款工具来自动化完成一些需要重复执行的模糊测试任务。**

![a.png](https://image.3001.net/images/20190703/1562158878_5d1ca71e08ccd.png!small)

## 工具概述

autoPwn其实是一个帮助我们重复执行模糊测试任务的脚本工具，我在之前的模糊测试过程中，发现有的时候需要重复性地去做相同的事情。因此，我创建这个工具的目的有以下几个方面：

> 1、 自动化和简化模糊测试任务的开始进程；
>
> 2、 通过配置文件自动化和简化模糊测试任务的重复执行；
>
> 3、 完全自动化afl任务处理队列；
>
> 4、 完全自动化提取和简化所有可能的漏洞利用路径；
>
> 5、 完全/部分自动化实现初始路径值的生成；

## 注意事项

本工具经过了彻底重构，目前主要针对的是只能从stdin接受输入数据的交互式Linux应用程序。目前版本的autoPwn只能以受限模式运行，运行下列命令，并选择“开始”(Start)选项即可：

    
    
    autoPwn ./binary

## 工具安装

安装和运行autoPwn最简单的方法就是使用Docker构建项目代码。需要注意的是，你可以删除--security-opt和--cap-add这两个选项，但是某些模糊测试用例可能会失效。

    
    
    $sudo docker pull bannsec/autoPwn
    
    $sudo docker run -it -v $PWD:/mount--security-opt="apparmor=unconfined" --cap-add=SYS_PTRACEbannsec/autoPwn

运行完上述命令之后，Docker中应该一切准备就绪了。你可以直接使用下列命令启用工具：

    
    
    $autoPwn ./file

## 编译源码进行模糊测试

Autopwn为了简化项目的模糊测试过程，会先对项目源码进行编译。工具首先会创建autoPwnCompile，然后将其指向我们的源代码，并提供相应的命令参数，最终工具会生成一个待进行模糊测试的可执行文件。

    
    
    usage:autoPwnCompile [-h] [--file FILE] [--ASAN | --MSAN] [--UBSAN]
    
                          [--fuzzer FUZZER]
    
    Compilesource to binaries for use in autoPwn.
    
    optionalarguments:
    
      -h, --help       show this help message and exit
    
      --file FILE      Single file to compile.
    
      --ASAN           Enable ASAN (default off)
    
      --MSAN           Enable MSAN (default off)
    
      --UBSAN          Enable UBSAN (default off)
    
      --fuzzer FUZZER  (optional) What fuzzer to compile for.Options are:
    
                       ['AFL']. Default is AFL.

## 工具使用

我们先来看一看TUCFT挑战中这个名为“WoO2”的题目，这里不需要找到可利用的漏洞或漏洞利用方式，我们只是为了演示如何使用autoPwn来简化漏洞利用路径的发现流程。下面给出的是程序的基础运行样例：

    
    
    $ ./e67eb287f23011a40ef5bd5c2ad2f48ca97834cf
    
    Welcome!I don't think we're in Kansas anymore.
    
    We're about to head off on an adventure!
    
    Select some animals you want to bring along.
    
    Menu Options:
    
    1:Bring a lion
    
    2:Bring a tiger
    
    3:Bring a bear
    
    4:Delete Animal
    
    5:Exit
    
    Enter your choice:
    
    1
    
    Choose the type of lion you want:
    
    1:Congo Lion
    
    2:Barbary Lion
    
    1
    
    Enter name of lion:
    
    Test
    
    Menu Options:
    
    1:Bring a lion
    
    2:Bring a tiger
    
    3:Bring a bear
    
    4:Delete Animal
    
    5:Exit
    
    Enter your choice:
    
    5

接下来，我们创建一个简单的输入测试用例：

    
    
    $ catin/1 
    
    1
    
    1
    
    Test
    
    5

现在，我们就可以直接开启模糊测试功能了：

    
    
    $autoPwn 
    
    Setting up fuzz configuration
    
    Target Binary (full or relative path): e67eb287f23011a40ef5bd5c2ad2f48ca97834cf
    
    Command line args: 
    
    Number of cores (default: 8): 
    
    TestCase Dir (default: 'in/'): 
    
    TestCase Dir (default: 'out/'): 
    
    Maxmemory (default: 200): 4096
    
    Starting fuzz
    
    autoPwn>s
    
    statuscheck tool for afl-fuzz by <lcamtuf@google.com>
    
    Individual fuzzers
    
    ==================
    
    >>>SESSION007 (0 days, 0 hrs) <<<
    
      cycle 1, lifetime speed 1 execs/sec, path 0/1(0%)
    
      pending 1/1, coverage 0.15%, no crashes yet
    
    >>>SESSION000 (0 days, 0 hrs) <<<
    
      cycle 1, lifetime speed 1 execs/sec, path 0/1(0%)
    
      pending 1/1, coverage 0.15%, no crashes yet
    
    >>>SESSION002 (0 days, 0 hrs) <<<
    
      cycle 1, lifetime speed 1 execs/sec, path 0/1(0%)
    
      pending 1/1, coverage 0.15%, no crashes yet
    
    >>>SESSION006 (0 days, 0 hrs) <<<
    
      cycle 1, lifetime speed 1 execs/sec, path 0/1(0%)
    
      pending 1/1, coverage 0.15%, no crashes yet
    
    >>>SESSION004 (0 days, 0 hrs) <<<
    
      cycle 1, lifetime speed 1 execs/sec, path 0/1(0%)
    
      pending 1/1, coverage 0.15%, no crashes yet
    
    >>>SESSION001 (0 days, 0 hrs) <<<
    
      cycle 1, lifetime speed 1 execs/sec, path 0/1(0%)
    
      pending 1/1, coverage 0.15%, no crashes yet
    
    >>>SESSION005 (0 days, 0 hrs) <<<
    
      cycle 1, lifetime speed 1 execs/sec, path 0/1(0%)
    
      pending 1/1, coverage 0.15%, no crashes yet
    
    >>>SESSION003 (0 days, 0 hrs) <<<
    
      cycle 1, lifetime speed 1 execs/sec, path 0/1(0%)
    
      pending 1/1, coverage 0.15%, no crashes yet
    
    Summary stats
    
    =============
    
           Fuzzers alive : 8
    
          Total run time : 0 days, 0 hours
    
             Total execs : 0 million
    
        Cumulative speed : 8 execs/sec
    
           Pending paths : 8 faves, 8 total
    
      Pending per fuzzer : 1 faves, 1 total (onaverage)
    
           Crashes found : 0 locally unique
    
    autoPwn>h
    
    autoPwn
    
         s == fuzzer (s)tatus
    
         e == collect (e)xploits
    
         a == collect (a)ll paths
    
         m == (m)inimize corpus
    
         q == (q)uit

在这个过程中，工具会创建某些默认的测试用例值。如果想要在QEMU中运行的话，我们还需要修改默认值以提供更多的运行内存。autoPwn会创建一个配置文件，并提供给afl-utils（[点我获取](https://github.com/rc0r/afl-utils)）。在配置文件中，它还会设置CPU关联性，以实现最佳的模糊测试效果。

## 项目地址

autoPwn：【[GitHub传送门](https://github.com/bannsec/autoPwn)】

 ***
参考来源：[bannsec](https://github.com/bannsec/autoPwn)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

