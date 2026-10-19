# Ruby安全漫谈

随着Ruby越来越流行，Ruby相关的安全问题也逐渐暴露，目前，国内专门介绍Ruby安全的文章较少，本文结合笔者所了解的Ruby安全知识点以及挖掘到的Ruby相关漏洞进行描述，希望能给读者在Ruby代码审计上提供帮助。

## Ruby简介

Ruby是一种面向对象、指令式、函数式、动态的通用编程语言。在20世纪90年代中期由日本电脑科学家松本行弘（Matz）设计并开发。Ruby注重简洁和效率，句法优雅，读起来自然，写起来舒适。

##  **红宝石安全**

说到Ruby安全不得不提RubyonRails安全，本篇着重关注Ruby本身。Ruby涉及到web安全漏洞几乎囊括其他语言存在的漏洞，例如命令注入漏洞、代码注入漏洞、反序列化漏洞、SQL注入漏洞、XSS漏洞、SSRF漏洞等。但是在具体的漏洞触发上，Ruby又不同于其他语言。

####  **命令注入漏洞**

命令注入漏洞一般是指把外部数据传入system类的函数执行，导致命令注入漏洞。触发命令注入漏洞的链接符号有很多，再配合单双引号可以组合成更多不同的注入条件，例如（linux）：

  * ``
  * $
  * ;
  * |
  * &
  * \n

在审计代码的时候一般会直接搜索能够执行命令的函数，例如：

  * 波彭
  * 生成
  * syscall
  * 系统
  * exec
  * 开盘3.*

而对于Ruby，除了支持这些函数执行命令，还有一些独特执行命令的方式：

  * %x//
  * ``
  * 打开
  * IO.read
  * IO.write
  * IO.binread
  * IO.binwrite
  * IO.foreach
  * IO.readlines

%x//和''属于类似system函数，可以把字符串解析为命令：

![](https://image.3001.net/images/20220831/1661940330_630f326ad5b586a1360d0.png!small)  

open是Ruby用来操作文件的函数，但是他也支持执行命令，执行传入一个以中划线开头的字符，后面跟着要执行的命令即可：

![](https://image.3001.net/images/20220831/1661940350_630f327e78af0b52031b3.png!small)  

除了open函数，IO.read/IO.write/IO.binread/IO.binwrite/IO.foreach/IO.readlines函数也可以以相同的方式执行命令。

open函数引发的Ruby安全问题：

File.read函数引发的Ruby安全问题：

IO.readlines函数引发的潜在Ruby安全问题，笔者发现，已被忽略：

####  **代码注入漏洞**

代码注入漏洞一般是由于把外部数据传入eval类函数中执行，导致程序可以执行任意代码。Ruby除了支持eval，还支持class_eval、instance_eval函数执行代码，区别在于执行代码的上下文环境不同。eval函数导致的代码注入问题与其他语言类似，不再赘述。

Ruby除了eval、class_eval、instance_eval函数，还存在其他可以执行代码的函数：

> 发送
>
> __send__
>
> public_send
>
> const_get
>
> constantize

#####  **send函数**

send函数是Ruby用来调用符号方法的函数，可以将任何指定的参数传递给它，类似JAVA中的invoke函数，不过它更为灵活，可以接收外部变量，举例：

![](https://image.3001.net/images/20220831/1661940390_630f32a61ee3db8d602cc.jpg!small)

上述代码中，实例k通过send动态调用了hello办法，假如hello字符串来自外部，便可以传入eval，注入恶意代码，举例：

![](https://image.3001.net/images/20220831/1661940404_630f32b435fb70310edaf.jpg!small)

#####  **__send__函数**

__send__函数和send函数一样，区别在于当代码有send同名函数时，可以调用__send__。

#####  **public_send函数**

public_send和send函数的区别在于send可以调用私有方法。

send函数引发的Ruby安全问题：

搜索一些不安全的用法：

![](https://image.3001.net/images/20220831/1661940416_630f32c04d9bfa810e166.png!small)

#####  **const_get函数**

const_get函数是Ruby用来在模块中获取常量值的函数，它存在一个inherit参数，当设置为true时（默认也为true），会递归向祖先模块查找。它还有另外一个用法，就是当字符串是已载入的类名时，会返回这个类（Ruby中，类名也是常量），类似JAVA的forName函数，常用写法是这样：

![](https://image.3001.net/images/20220831/1661940429_630f32cd4fd231486ba41.png!small)

代码中，使用const_get动态实例化了类，使Ruby更为灵活。但是这样的用法如果使用不当，也会出现安全问题，例如这里（rack-proxy模块）：

![](https://image.3001.net/images/20220831/1661940439_630f32d7ba288888dc941.png!small)

如图，perform_request函数在Net：：HTTP模块中搜索HTTP方法类，然后实例化，并传递full_path请求路径参数给new函数，HTTP方法和请求路径都是外部可控的，而且const_get函数没有限制inherit，默认可以递归查找，在整个空间内实例化任意已载入类，并传递一个可控参数。如果找到合适的利用链，完全可以到达任意代码执行。目前，该问题已在GitHub上被发现并修复。

![](https://image.3001.net/images/20220831/1661940450_630f32e2be9715971cd92.png!small)

实战中已经有人使用此方法实现了代码执行，那就是gitlab的一个漏洞

https://hackerone.com/reports/1125425，
kramdown模块使用const_get函数来动态实例化格式化类，但是没有限制inherit，导致vakzz通过使用一个Redis类的利用链达到了任意代码执行的目的，漏洞报告已经写的非常详细，不再赘述。

#####  **constantize**

constantize同样可以将字符串转化为类，属于RubyonRails中的用法，底层调用的const_get函数：

![](https://image.3001.net/images/20220831/1661940748_630f340ccd8c997de601e.jpg!small)

下图中constantize要转化的类和类实例化的参数都可控，如果我们能找到合适的利用链，便可以到达任意代码执行：

####  **反序列化漏洞**

反序列化漏洞是指在把外部传入的不可信字节序列恢复为对象的过程中，未做合适校验，导致攻击者可以利用特定方法，配合利用链，达到任意代码执行的目的。Ruby也有反序列化的函数，同样也存在反序列化漏洞。

#####  **元帅反序列化**

Marshal是Ruby用来序列反序列化的模块，Marshal.dump可以把一个对象序列化为字节序，Marshal.load可以把一个字节序反序列化为对象。

Marshal反序列化的利用已有很多篇分析文章，不再赘述。

  * lhttps://github.com/httpvoid/writeups/blob/main/Ruby-deserialization-gadget-on-rails.md

使用已经公开的POC测试：

![](https://image.3001.net/images/20220831/1661940821_630f34552be50d231bc6f.jpg!small)

执行POC（ruby-3.0.0）：

![](https://image.3001.net/images/20220831/1661940835_630f34634bb567d29406b.png!small)

搜索一些不安全的用法：

![](https://image.3001.net/images/20220831/1661940845_630f346dc10bbd04d8be8.png!small)

#####  **JSON反序列化**

Ruby
处理JSON时可能存在反序列化漏洞，但是不是Ruby内置的JSON解析器，而是第三方开发的解析器oj（https://github.com/ohler55/oj）。oj在解析JSON时支持多种数据类型，包括会导致代码执行的Object类型。

使用已经公开的POC测试：

![](https://image.3001.net/images/20220831/1661940906_630f34aa5ce6ab9976c67.jpg!small)

执行POC（ruby-3.0.0）：

![image.php?url=YD_cnt_38_01EP10d8ODcL](https://image.3001.net/images/20200701/1593550745.png!small)

oj可以通过设置模式，避免反序列化对象：

![](https://image.3001.net/images/20220831/1661940920_630f34b8b2b08d5d6e8df.jpg!small)

#####  **YAML反序列化**

Ruby YAML也支持反序列化对象，pysch 4.0之前版本调用YAML.load函数即可反序列化对象，psych
4.0以后需要调用YAML.unsafe_load才能反序列化对象。使用已经公开的POC测试：

![](https://image.3001.net/images/20220831/1661940940_630f34ccec522e385e3b4.jpg!small)

执行POC（ruby-3.0.0）：

![](https://image.3001.net/images/20220831/1661940958_630f34de69cef28bcd506.png!small)  

Ruby YAML解析，psych4.0之前可以通过调用save_load函数，避免反序列化对象，psych
4.0之后默认load函数就是安全的（https://github.com/ruby/psych/pull/487）。

搜索unsafe_load的使用，不一定存在漏洞，需要yaml内容可控才有风险：

![](https://image.3001.net/images/20220831/1661941095_630f3567d7c3fc569c634.png!small)  

####  **正则错用**

Ruby正则大体与其他语言一样，只是在个别语法上存在差别，如果没有特别了解研究，按照其他的语言用法套用，就很有可能出现安全问题，例如Ruby在用正则匹配开头和结尾时支持^$的用法，但是支持多行匹配则需要改为\A\Z避免换行绕过。

![](https://image.3001.net/images/20220831/1661941136_630f35906031a83d90240.png!small)  

正则错用引发的安全问题：

搜索相关代码，还是有不少错用的：

![](https://image.3001.net/images/20220831/1661941153_630f35a1bcddebe548b4e.png!small)  

####  **FUZZ Ruby解析器**

在学习Ruby反序列化时，想要通过Ruby用C语言实现Marshal，对处理不同数据类型做处理，那么可以对他进行一下FUZZ。

FUZZ使用了AFLplusplus，配置编译Ruby：

> ./configure CC=/opt/AFLplusplus/afl-clang-fast CXX=/opt/AFLplusplus/afl-> clang-fast++ --disable-install-doc --disable-install-rdoc
> --prefix=/usr/local/ruby --enable-debug-env
>
>
> 导出ASAN_OPTIONS=“detect_leaks=0：abort_on_error=1：allow_user_segv_handler=0：handle_abort=1：符号=0”
>
> AFL_USE_ASAN=1

使用AFLplusplus的deferred instrumentation模式，对Ruby源码main.c文件稍作修改：

![](https://image.3001.net/images/20220831/1661941231_630f35ef9702579b167ef.png!small)

样本生成上，可以选取Ruby自带的测试用例，这样可以快速得到比较全面合法的样本，正好在学习Ruby
hook的方案，写了一个简单的hook函数，在rubygems.rb文件中加载，劫持Marshal模块，执行自测的同时即可保存下样本。

![](https://image.3001.net/images/20220831/1661941215_630f35dfdfd63ea8301a8.jpg!small)  

想要FUZZ其他模块也可以用同样办法来获取样本。

经过一段时间的FUZZ，陆陆续续发现了一些漏洞：

1\. CVE-2022-28738 在onig_reg_resize中双自由

![](https://image.3001.net/images/20220831/1661941250_630f3602a476e3837ab11.png!small)  

2\. CVE-2022-28739 strtod 中的堆缓冲区溢出

![](https://image.3001.net/images/20220831/1661941264_630f36109e33ddeef1c21.png!small)  

3\. 全局缓冲区溢出calc_tm_yday

![](https://image.3001.net/images/20220831/1661941279_630f361fa134c9a209afd.png!small)  

4\. renumber_by_map中的动态堆栈缓冲区溢出

![](https://image.3001.net/images/20220831/1661941297_630f36312d8fd0810246e.png!small)  

5\. JSON.parse 拒绝服务

![](https://image.3001.net/images/20220831/1661941308_630f363c5c3755eb6479d.png!small)  

虽然FUZZ出了一些问题，但是依旧存在很多未解决的问题，比如FUZZ速度、效率、自动化等，未来将继续深入探索研究。

以上是笔者在ruby中的一些学习研究汇总，如有不恰当之处，敬请斧正，一起交流学习。

###

###  **参考链接**

> https://hackerone.com/ruby/hacktivity
>
> https://bishopfox.com/blog/ruby-vulnerabilities-exploits
>
> https://zenn.dev/ooooooo_q/books/rails_deserialize
>
> http://gavinmiller.io/2016/the-safesty-way-to-constantize/
>
> https://github.com/haileys/old-> website/blob/master/posts/rails-3.2.10-remote-code-execution.md
>
> https://www.elttam.com/blog/ruby-deserialization/
>
> https://devcraft.io/2021/01/07/universal-deserialisation-gadget-for-> ruby-2-x-3-x.html
>
> https://bsidessf2018.sched.com/event/E6jC/fuzzing-ruby-and-c-extensions

