## 背景

sqlmap作为一个老牌的成熟的SQL漏洞扫描工具，在SQL注入自动化检测领域独占一壁江山。而现在的SQL注入检测往往是通过被动扫描检出，再通过sqlmap或者手工注入的方式进行进一步的漏洞确认和利用。在这种情形下，我们就需要开发一款应用于被动扫描场景下的SQL注入检测工具。而Yakit作为一个综合渗透测试平台，提供了用户友好型的API接口，可以很方便的实现SQL漏洞检测功能，和SQL注入启发式检测所需的核心功能。

## sqlmap中一些概念的介绍

在sqlmap中有一个很重要的概念就是页面相似度，这个页面相似度基于python中自带的`difflib`模块

sqlmap 主要使用其`SequenceMatcher`这个类。以下是关于这个类的简单介绍：

> This is a flexible class for comparing pairs of sequences of any type, so
> long as the sequence elements are hashable. The basic algorithm predates,
> and is a little fancier than, an algorithm published in the late 1980’s by
> Ratcliff and Obershelp under the hyperbolic name “gestalt pattern matching.”
> The idea is to find the longest contiguous matching subsequence that
> contains no “junk” elements (the Ratcliff and Obershelp algorithm doesn’t
> address junk). The same idea is then applied recursively to the pieces of
> the sequences to the left and to the right of the matching subsequence. This
> does not yield minimal edit sequences, but does tend to yield matches that
> “look right” to people.

简单来说这个类使用了 Ratcliff 和 Obershelp
提供的算法，匹配最长相同的字符串，设定无关字符（junk）。在实际使用中，他们应用最多的方法应该就是`ratio()`。

![](https://image.3001.net/images/20220922/1663831991_632c0fb70e5e06820868c.jpeg!small)

根据文档中的描述，这个方法返回两段文本的相似度，相似度的算法如下：我们假设两段文本分别为`text1`与`text2`，他们相同的部分长度总共为`M`，这两段文本长度之和为`T`，那么这两段文本的相似度定义为`2.0
* M / T`，这个相似度的值在 0 到 1.0 之间。

###  **PageRatio 的小例子**

![](https://image.3001.net/images/20220922/1663832008_632c0fc80dd327ea48a22.jpg!small)

我们通过上面的介绍，知道了对于`abcdefg`和`abce123`我们计算的结果应该是`2.0 * 4 / 14`所以计算结果应该是：

![](https://image.3001.net/images/20220922/1663832033_632c0fe14dcaed7205c85.jpeg!small)

## WAF检测

在sqlmap中存在WAF检测，简单来说就是在请求中携带一些可能被WAF拦截的敏感字符。以下为sqlmap中检测目标主机潜在WAF的payload。

    
    
    " AND 1=1 UNION ALL SELECT 1,NULL,'<script>alert(\"XSS\")</script>',table_name FROM information_schema.tables WHERE 2>1--/**/; EXEC xp_cmdshell('cat ../../../etc/passwd')#"

如果目标主机存在WAF，那返回的HTTP状态码和响应体和正常请求的响应状态码和响应体就会不同，结合PageRatio进行分析就能比较容易的判断目标主机是否存在WAF。这里WAF检测的主要目的是提示渗透测试人员谨慎使用payload。

## 转型分析

在实际的SQL注入测试和web开发中，经常遇到强制转型，在从请求中收到请求参数后往往会对其执行intval()或是类似的函数，也就是说对于开发者来说这个参数是被当成一个int来使用的，当我们尝试对该参数进行SQL注入时，显然输入的会是字符串，因此后端收到请求参数后在尝试对其进行类型转换的过程中就会报错。而这也意味着这个参数我们无法注入。参考sqlmap的注入流程图

![](https://image.3001.net/images/20220922/1663832072_632c10089b8fc5bdd48d7.jpg!small)

通过将参数转型前置放在实际注入漏洞检测前可以省去无用的请求数，因为在检测到参数转型后就没必要继续接下来的检测了。

## 什么是启发式检测

相信用过sqlmap的读者都注意到sqlmap在扫描时会提示`heuristic (basic) test shows that GET parameter
'xxx' might (not) be
injectable`提示启发式检测表明某个参数似乎无法注入。那么这个所谓的启发式检测的原理是什么呢。我们在刚学SQL注入的时候，都会先学习去先去寻找闭合SQL语句的符号，再通过闭合外的内容形成逃逸，从而执行我们输入的SQL语句。而这个启发式检测就是寻找SQL语句闭合方式的过程，它会根据参数类型，例如数字型和字符串型，采取不同的闭合方式尝试，例如对于数字型参数采用无闭合的方式，对于字符串采取常见的单引号闭合去检测。在sqlmap中有一个常量

    
    
    HEURISTIC_CHECK_ALPHABET = [`"`, `'`, `)`, `(`, `,`, `.`]

这个常量存储的就是常见的闭合符号。通过这种办法去猜测SQL语句的闭合边界，配合一定的Bool表达式，构成所谓的positive和negative请求，也就是语句条件为真和假的情况，如果positive请求和原请求的相似度一致，而negative和positive相似度不一致，那么
**很大概率**
这个参数就是存在注入的。这里之所以强调很大概率是因为，尽管对于两种条件的相似度不一致，我们现在还没有足够证据去实锤这个点就是存在SQL注入。表现在sqlmap中就是上文提示中的`might
(not) be injectable`。

## 进一步确认是否存在注入过程中的优化

### 检测顺序优化

进一步确认就是去检测各种常见的SQL注入类型，诸如时间盲注(Time-Based Blind)，有回显的报错注入(In-Band Error
Based)，有回显和无回显的联合注入(Inband/Outband
Union)。在上一步我们通过启发式检测确认了闭合方式，现在在实际检测时我们要考虑检测的先后顺序，在这里可以做一个短路处理，比如我们首先检测报错注入，如果存在报错注入，那么后面的注入就可以通过报错注入的信息获取对应的SQL数据库类型，从而减少总请求数量。![](https://image.3001.net/images/20220922/1663832105_632c10296c0487f9db5b1.png!small)

### 检测方式优化

同时，我们要明确一点就是能不用sleep检测就不要用sleep进行检测，sleep检测在遇到性能较差的单线程服务器时可能会造成意想不到的阻塞和性能问题，同时在一些orm或者SQL框架中会对查询时间进行限制，一旦查询超时就会提前返回，从而导致漏检的问题出现。

所以我们尽可能要采用正则去匹配返回内容中的信息去匹配，这样不仅可以提高效率，也能保证结果精确性，同时在目标无回显的情况下保留sleep检测方法作为备用方案。

## 联合注入类型的检测

联合注入在常见的SQL注入类型中属于比较复杂的类型，在开发插件中借鉴了sqlmap中的做法，首先尝试使用order by进行检测，同时采用二分法进行检测。

在二分法无法检测，或者目标完全无回显的情况下，采用遍历法检测，即从`lowerCount`到`upperCount`这个区间，构造Payload
为`UNION SELECT (NULL,) * [COUNT]`的请求，这些请求的对应
RATIO（与模版页面相似度）会汇总存储在`ratios`中，同时`items`中存储`列数 和
ratio`形成的`tuple`，经过一系列的算法，尽可能寻找出与众不同（正确猜到列数）的页面。

这里插件为了避免过于复杂，采取了`UNION SELECT
sleep(x)`的方法进行最后的辅助检测。也就是说对于UNION注入，我们首先尝试运用`ORDER
BY`进行检测，在其失效的情况下利用ratio去找最与众不同的页面，去判定行数，如果ratio还不起作用，便使用时间盲注的方式进行辅助检测。

## 使用演示

  1. 首先启动MITM劫持

![](https://image.3001.net/images/20220922/1663832136_632c10484b85c70c1e4c0.png!small)

  2. 勾选左侧插件以加载插件

![](https://image.3001.net/images/20220922/1663832154_632c105ad0ad8582019f0.png!small)

  3. 将模式修改为被动日志界面，这样才能看到MITM插件的扫描输出，浏览器刷新，重新访问存在漏洞的靶场页面，可以看到输出信息

![](https://image.3001.net/images/20220922/1663832173_632c106d3298d90da26b4.png!small)

  4. 查看上方的风险与漏洞

![](https://image.3001.net/images/20220922/1663832187_632c107b5fe19f6f457e5.png!small)

可以看到检测到了时间盲注和联合注入

## 插件测试结果

pentesterlab的SQL靶场一共有9关，具体的测试报告如下

靶场案例| 是否检测出漏洞| 漏洞类型| 说明  
---|---|---|---  
example1| ✔️| 字符型单引号边界闭合，时间盲注，联合注入| 无  
example2| ✔️| 字符型单引号边界闭合，时间盲注，联合注入| 无  
exmaple3| ✔️| 字符型单引号边界闭合，时间盲注，联合注入| 无  
example4| ✔️| 数字型无边界闭合，时间盲注，联合注入| 无  
example5| ✔️| 数字型无边界闭合，时间盲注，联合注入| 无  
example6| ✔️| 数字型无边界闭合| WAF规则为必须以数字结尾，此处需要手工进一步测试  
example7| ✔️| 数字型无边界闭合，时间盲注，联合注入| 无  
example8| ❌| 未检出| 使用了` back tick作为闭合符  
example9| ✔️| ORDER BY无边界闭合|  
  
  
  

## 参考

<https://zhuanlan.zhihu.com/p/43242220>

