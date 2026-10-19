**作者：沈沉舟  
原文链接：<https://mp.weixin.qq.com/s/bmdSyZem46aukj_hvLhu0w>**

在HVV期间同事提出ionCube保护PHP源码比较结实，研究了一下。

ionCube
7.x处理过的some_enc.php不含原始some.php，只有混淆过的opcode。逆向工程技术路线必须分两步走，第一步还原zend_op_array，第二步反编译。

有个付费的反编译网站

<https://easytoyou.eu/>

可以只买一个月，10欧元，大约80人民币，PayPal付款。提交some_enc.php，若是反编译成功，返回some.php。easytoyou应该有一个强大的私有PHP反编译器。

ionCube
7.x确实很结实，作者应该与搞逆向工程的搏斗过多年，其实现很变态。但是，再变态，只要持续投入精力，总能搞定，无非是性价比的问题，后来成功获取还原后的zend_op_array。接下来就是将zend_op_array以PHP源码形式展现，也就是反编译。

<https://www.php.net>

Source Insight看PHP引擎源码是必不可少的。

    
    
    PHP 7 Virtual Machine - nikic [2017-04-14]
    https://www.npopov.com/2017/04/14/PHP-7-Virtual-machine.html

这篇简介了PHP 7引擎的内部机制，不必纠缠看不懂的部分，粗略过一遍即可。有兴趣者，等写完PHP 7反汇编器，再回头重看一遍试试。事实上，我都写完PHP
7反编译器了才回头重看了一遍，怎么说呢，有些鸡肋。

PHP基本上算解释型语言，编译后有一种中间语言形式，平时说Opcode，不严格地说，就是PHP的中间语言形式。可以用VLD感性化认识Opcode。

    
    
    VLD (Vulcan Logic Dumper)
    https://github.com/derickr/vld
    
    Understanding Opcodes - Sara Golemon [2008-01-19]
    http://blog.golemon.com/2008/01/understanding-opcodes.html
    (作者是位女性，同时是parsekit的作者)
    
    More source analysis with VLD - [2010-02-19]
    https://derickrethans.nl/more-source-analysis-with-vld.html
    (VLD作者对VLD输出内容的解释，比如*号表示不可达代码，如何转dot文件成png文件)

虽然我要对付PHP 7，但很多东西是一脉相承的，PHP 5的优质文档可以看看。

    
    
    深入理解Zend执行引擎(PHP5) - Gong Yong [2016-02-02]
    http://gywbd.github.io/posts/2016/2/zend-execution-engine.html
    (讲了Opcode、Zend VM、execute_ex()、zend_vm_gen.php，推荐阅读)
    
    使用vld查看OPCode - Gong Yong [2016-02-04]
    https://gywbd.github.io/posts/2016/2/vld-opcode.html
    (介绍VLD最详细，推荐阅读)

在研究Opcode过程中找到几篇OPcache相关的文档。

    
    
    Binary Webshell Through OPcache in PHP 7 - Ian Bouchard [2016-04-27]
    https://www.gosecure.net/blog/2016/04/27/binary-webshell-through-opcache-in-php-7/
    
    Detecting Hidden Backdoors in PHP OPcache - Ian Bouchard [2016-05-26]
    https://www.gosecure.net/blog/2016/05/26/detecting-hidden-backdoors-in-php-opcache/
    
    PHP OPcache Override
    https://github.com/GoSecure/php7-opcache-override
    https://github.com/GoSecure/php7-opcache-override/issues/6
    (有两个010Editor模板，还有opcache_disassembler.py)
    (提到construct 2.8的问题)

Zend VM OPcache生成的some.php.bin其格式是版本强相关的，随PHP版本不同需要不同的解析方式。010
Editor自带有一个.bt，但不适用于我当时看的版本。Ian Bouchard的.bt也不适用于我当时看的版本，起初我在Ian
Bouchard的.bt基础上小修小改对付着用，后来发现需要修改的地方比较多，也不太适应Ian
Bouchard的解析思路，后来就自己重写了一个匹配版本的解析模板。

之前从未完整写过.bt，突然写这么复杂的模板，碰上很多工程实践问题，后来分享过编写经验。

    
    
    《MISC系列(51)--010 Editor模板编写入门》
    http://scz.617.cn:8/misc/202103211820.txt
    https://www.52pojie.cn/thread-1398493-1-1.html
    https://www.52pojie.cn/thread-1402549-1-1.html

Ian Bouchard还提供了基于Python
Construct库的opcache_parser_64.py，对标.bt，用于解析some.php.bin。opcache_parser_64.py同样是PHP版本强相关的，它这个可能对应PHP
7.4。

opcache_disassembler.py利用opcache_parser_64.py的解析结果进行Opcode反汇编。

    
    
    $ python2 opcache_disassembler.py -n -a64 -c hello.php.bin
    
    [0] ECHO('Hello World\n', None);
    [1] RETURN(1, None);

我要对付的PHP版本不是7.4，不能直接用Ian
Bouchard的.py。此外，他用Construct2.8，现在Python3上是2.10或更高，2.8和2.10有不少差别，不想四处修修补补，所以跟.bt一样，最终重写了一个匹配版本的.py。

    
    
    Construct
    https://construct.readthedocs.io/en/latest/
    https://construct.readthedocs.io/en/latest/genindex.html
    https://github.com/construct/construct/

这是我第一次接触Python Construct库，这个库充满了神秘主义哲学，文档也很差。总共从头到尾看了两遍官方文档，感觉作者自嗨得不行。

写完.py后，与.bt做了些比较，各有千秋；.bt的好处是GUI展示，在调试开发阶段很有意义；.py更灵活。设若你要解析二进制数据，建议.bt、.py各整一套，磨刀不误砍柴功，这些都是生产力工具。

反汇编zend_op_array，需要对该数据结构有一定了解，重点是opcodes[]、vars[]、literals[]、arg_info[]这几个结构数组，反汇编时无需理会try_catch_array[]。对着PHP源码以及Ian
Bouchard的实现，拿hello.php.bin练手入门，再对付复杂的.bin。

    
    
    <?php
    
    class TestClass
    {
        public function func_0 ( $arg )
        {
    ...
        }
    }
    
    ...
    
    function func_default ( $m, $hint )
    {
        echo '$mode=' . $m . $hint;
        throw new Exception( "\$mode is invalid" );
    }
    
    $tc  = new TestClass();
    $tc->func_0( $argv );
    
    ?>

假设some.php如上，some.php.bin.asm如下(PHP 7):

    
    
    main()
    [0] (95) var_2 = NEW("TestClass",)
    [1] (95) = DO_FCALL(,)
    [2] (95) = ASSIGN($tc,var_2)
    [3] (96) = INIT_METHOD_CALL($tc,"func_0")
    [4] (96) = SEND_VAR_EX($argv,)
    [5] (96) = DO_FCALL(,)
    [6] (98) = RETURN(0x1,)
    ...
    
    func_default($m,$hint)
    [0] (86) $m = RECV(,)
    [1] (86) $hint = RECV(,)
    [2] (88) tmp_3 = CONCAT("\$mode=",$m)
    [3] (88) tmp_2 = CONCAT(tmp_3,$hint)
    [4] (88) = ECHO(tmp_2,)
    [5] (89) var_2 = NEW("Exception",)
    [6] (89) = SEND_VAL_EX("\$mode is invalid",)
    [7] (89) = DO_FCALL(,)
    [8] (89) = THROW(var_2,)

Ian Bouchard的反汇编器本质上能达到同样效果，修改.py自定义输出效果。

    
    
    Inspector
    https://github.com/krakjoe/inspector
    (A disassembler and debug kit for PHP7)

有个Inspector，看说明，反汇编输出类似VLD输出，我没测过。推荐Ian Bouchard的实现。

即使最终目的是PHP反编译器，也应该先实现一版PHP反汇编器，前者的开发、调试过程会高度依赖后者。

写反汇编器的难点主要是对zend_op_array结构成员的理解，没学《编译原理》也无所谓。但是，写反编译器的难度突然抬升，要我从头干这事，就我现在这岁数，早没心气劲陪它玩了。

遇到困难找警察，遇到问题找hume。我就问他，那些流控语句的反编译怎么下手，没时间翻大部头理论指导，就想听他忽悠我。hume当时原话是这么说的：“个人理解，通过控制流图分析识别出if-else、循环等基本的控制结构，再加上一点语言相关的模式匹配还原”。等我完成后回头看他这个回答，一点没有忽悠我。

DY、XYM找了个现有PHP 5反编译器实现。

    
    
    https://github.com/lighttpd/xcache/blob/master/lib/Decompiler.class.php
    
    还原ZendGuard处理后的php代码
    https://github.com/Tools2/Zend-Decoder
    (看这个)
    
    Decompiling and deobfuscating a Zend Guard protected code base - [2020-03-16]
    https://bartbroere.eu/2020/03/16/decompiling-zend-guard-php/
    (作者提供了一个Docker)

原始版本好像是俄罗斯程序员写的。该反编译器本身也是用PHP开发的，不能单独使用，得跟xcache结合着用。我理解xcache是OPcache出现之前的一种非官方Opcode缓存加速机制，可能不对，无所谓，确实没有细究xcache。

后来应该是一名中国程序员利用了初版反编译引擎，用于对付ZendGuard。作者应该做了版本升级适配，看说明，适用于PHP 5.6。

我不会PHP啊，反编译引擎这么复杂的代码逻辑，又是PHP写的，看得我头大。XYM搭了个环境，让我可以用VSCode动态调试前述反编译引擎，这就好多了。

就前述PHP 5反编译器而言，从此处看起

    
    
    function &dop_array($op_array, $isFunction = false)

这是负责反编译单个zend_op_array。PHP的中间代码是以zend_op_array为单位进行组织的，一个函数对应一个zend_op_array，main()也是一个函数。

    
    
    $this->fixOpCode($op_array['opcodes'], true, $isFunction ? null : 1);

这与反编译引擎本身无关，可能是对付ZendGuard的某些混淆手段？我没细跟。

    
    
    $this->buildJmpInfo($range);

这步主要识别分支跳转类指令，为它们打上特定标记，标记跳转目标。将来会有一个识别、切分block的过程，要依赖此处所打特定标记。所以，此处不打标记不成。

    
    
    $this->recognizeAndDecompileClosedBlocks($range);

这是根据buildJmpInfo()所打标记识别、切分block。若写过其他语言的反编译器，无需再解释。若无类似经验，就得加强理解了。IDA反汇编时，若用图块形式显示，那一个个方块就是识别、切分过的block。

    
    
    class TestClass
    {
        /**
         * func_0 comment
         */
        public function func_0 ( $arg )
        {
            try
            {
                $mode   = func_1( $arg );
                switch ( $mode )
                {
                /**
                 * case 0
                 */
                case 0 :
                    func_case_0( $mode, $arg );
                    break;
                case 1 :
                    func_case_1( $mode );
                    break;
                default :
                    /**
                     * default
                     */
                    func_default( $mode, " (unexpected)\n" );
                    throw new Exception( "\$mode is invalid" );
                }
            }
            catch ( Exception $e )
            {
                print_r( $e );
                die;
            }
            finally
            {
                echo "Finally\n";
            }
        }
    }

func_0()的反汇编结果(PHP 7):

    
    
    TestClass.func_0($arg)
    [0] (11) $arg = RECV(,)
    [1] (15) = INIT_FCALL(,"func_1")
    [2] (15) = SEND_VAR($arg,)
    [3] (15) var_4 = DO_FCALL(,)
    [4] (15) = ASSIGN($mode,var_4)
    [5] (21) tmp_4 = CASE($mode,0x0)
    [6] (21) = JMPNZ(tmp_4,->9)
    [7] (24) tmp_4 = CASE($mode,0x1)
    [8] (24) = JMPZNZ(tmp_4,->18,->14)
    [9] (22) = INIT_FCALL(,"func_case_0")
    [10] (22) = SEND_VAR($mode,)
    [11] (22) = SEND_VAR($arg,)
    [12] (22) = DO_FCALL(,)
    [13] (32) = JMP(->31,)
    [14] (25) = INIT_FCALL(,"func_case_1")
    [15] (25) = SEND_VAR($mode,)
    [16] (25) = DO_FCALL(,)
    [17] (32) = JMP(->31,)
    [18] (31) = INIT_FCALL(,"func_default")
    [19] (31) = SEND_VAR($mode,)
    [20] (31) = SEND_VAL(" (unexpected)\n",)
    [21] (31) = DO_FCALL(,)
    [22] (32) var_4 = NEW("Exception",)
    [23] (32) = SEND_VAL_EX("\$mode is invalid",)
    [24] (32) = DO_FCALL(,)
    [25] (32) = THROW(var_4,)
    [26] (35) = CATCH("Exception",$e)
    [27] (37) = INIT_FCALL(,"print_r")
    [28] (37) = SEND_VAR($e,)
    [29] (37) = DO_ICALL(,)
    [30] (38) = EXIT(,)
    [31] (41) tmp_3 = FAST_CALL(->33,)
    [32] (41) = JMP(->35,)
    [33] (42) = ECHO("Finally\n",)
    [34] (42) = FAST_RET(tmp_3,)
    [35] (44) = RETURN(null,)

为了正确反编译，要设法将下面这一小段汇编指令识别、切分成一个block。

    
    
    [5] (21) tmp_4 = CASE($mode,0x0)
    [6] (21) = JMPNZ(tmp_4,->9)
    [7] (24) tmp_4 = CASE($mode,0x1)
    [8] (24) = JMPZNZ(tmp_4,->18,->14)
    [9] (22) = INIT_FCALL(,"func_case_0")
    [10] (22) = SEND_VAR($mode,)
    [11] (22) = SEND_VAR($arg,)
    [12] (22) = DO_FCALL(,)
    [13] (32) = JMP(->31,)
    [14] (25) = INIT_FCALL(,"func_case_1")
    [15] (25) = SEND_VAR($mode,)
    [16] (25) = DO_FCALL(,)
    [17] (32) = JMP(->31,)
    [18] (31) = INIT_FCALL(,"func_default")
    [19] (31) = SEND_VAR($mode,)
    [20] (31) = SEND_VAL(" (unexpected)\n",)
    [21] (31) = DO_FCALL(,)
    [22] (32) var_4 = NEW("Exception",)
    [23] (32) = SEND_VAL_EX("\$mode is invalid",)
    [24] (32) = DO_FCALL(,)[25] (32) = THROW(var_4,)

如何达此目的？学习buildJmpInfo()、recognizeAndDecompileClosedBlocks()的实现。PHP 5与PHP
7有不少差别，但原理是相通的。

recognizeAndDecompileClosedBlocks()识别、切分block之后，主要调用两个函数:

decompileBasicBlock() decompileComplexBlock()

有两种block，一种是基本block，一种是复杂block。下面是一个基本block:

    
    
    [1] (15) = INIT_FCALL(,"func_1")
    [2] (15) = SEND_VAR($arg,)
    [3] (15) var_4 = DO_FCALL(,)
    [4] (15) = ASSIGN($mode,var_4)

基本block内部没有分支跳转指令，所有Opcode依次执行，直至基本block结束。

decompileBasicBlock()负责基本block的反编译，需要处理当前PHP版本所支持的大量常见Opcode。无需一步到位支持所有Opcode，可以迭代支持。

"5-25"是复杂block，block中有很多分支跳转指令。

decompileComplexBlock()负责复杂block的反编译，对切分好的复杂block进行具体的模式识别。下面这些函数分别对应不同的控制流模式:

decompile_foreach() decompile_while() decompile_for() decompile_if()
decompile_switch() decompile_tryCatch() decompile_doWhile()

"5-25"会被识别成switch/case。模式识别没有太大难度，跟病毒特征识别、流量特征识别本质上无区别，属于经验迭代；没有难度，但很繁琐，需要足够的样本量进行测试。反编译失败时最大可能就是复杂block模式识别失败，或存在BUG。

只靠前面这些操作得不到最终反编译输出结果，还需要关注:

class Decompiler_Output

该类负责格式化输出，比如各个block的缩进、反缩进。

其他的没必要讲太细，有前述大框架的理解，再动态调试跟踪一下，不断迭代理解即可。总的来说，俄罗斯程序员的PHP
5反编译引擎实现得很有想法，大框架出来了，共性部分已经充分展示。要说不爽，就是这特么是用PHP开发的，对于我这种程序员来说，淡淡的忧伤。

若读者需要开发自己的PHP反编译引擎，可以移植俄罗斯程序员的PHP
5反编译引擎，PHP跟Python之间的移植难度不大，基本上可以行对行翻译。框架移植成功后，再针对PHP
7进行下一步开发，工程实践细节很多，要求对各种Opcode理解较深。

大多数人学PHP是正着学，看语法手册，写Hello World，我是反着来的。不断修正反编译器未处理到的Opcode，在此过程中Source
Insight查看PHP引擎源码，或放狗查询Opcode对应的源码语法、语义。我是被迫反着来的，因为我根本不会PHP编程。胡整中。

比如，我不知道"@unlink()"中这个@是干啥的，我也不知道有这种语法。但我在开发测试PHP反编译器时碰上了BEGIN_SILENCE、END_SILENCE，反查后才知道。然后在反编译引擎中增加对这两个Opcode的处理，设法输出@。

    
    
    [120] (69) tmp_16 = BEGIN_SILENCE(,)
    [121] (69) = INIT_FCALL(,"unlink")
    [122] (69) tmp_17 = FETCH_CONSTANT(,"NET_STATUS_FILE")
    [123] (69) = SEND_VAL(tmp_17,)
    [124] (69) = DO_ICALL(,)
    [125] (69) = END_SILENCE(tmp_16,)

实际对应

    
    
    @unlink(NET_STATUS_FILE);

完成一版ionCubeDecompile_x64_7.py，成功反编译经ionCube加密过的some_enc.php。前后花了5个月时间，有些偏长了。已经不是二十年前的精神小伙，各方面都在持续退化中。若注意力够集中，在我智力水平巅峰的时候，应该2个月能搞完，再快就超出我的水平了。那些3天写个OS的，都不是人，他们是神。

若是easytoyou免费给用，我绝对不想折腾这事儿。有时别人卡脖子，被迫自力更生，长远看，未尝不是一件好事。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1687/>

