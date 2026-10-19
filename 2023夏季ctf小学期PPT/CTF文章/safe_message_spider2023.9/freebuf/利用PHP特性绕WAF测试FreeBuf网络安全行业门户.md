在测试绕过 WAF 执行远程代码之前，首先构造一个简单的、易受攻击的远程代码执行脚本，内容如图：

![01.png](https://image.3001.net/images/20230614/1686726172_6489661c3e3b8b7beb10a.png!small)

第 6 行是一个比较明显的命令执行代码，第 3 行尝试拦截 system、exec 或 passthru 等函数（PHP
中有许多其他函数可以执行系统命令，这三个是最常见的）。

这个脚本部署在 Cloudflare WAF 和 ModSecurity + OWASP CRS3 之后。对于第一个测试，尝试读取 passwd 的内容；

> /cfwaf.php?code=system("cat /etc/passwd");

![02.png](https://image.3001.net/images/20230614/1686726173_6489661d0ccbddee94aeb.png!small)

可以看到，被 CloudFlare 拦截了，我们可以尝试使用未初始化变量的方式绕过，比如：

> cat /etc$u/passwd

![03.png](https://image.3001.net/images/20230614/1686726174_6489661e2a82b7eecc550.png!small)

Cloudflare WAF 已被绕过，但是由于脚本检查敏感函数，所以被脚本拦截，那么如何绕过脚本的函数检测呢？我们看看关于字符串的 PHP 文档：

> <https://secure.php.net/manual/en/language.types.string.php>

PHP 字符串转义序列:

  * [0–7]{1,3} 八进制表示法的字符序列，它会自动溢出以适应一个字节（例如“\400”===“\000”）

  * \x[0–9A-Fa-f]{1,2} 十六进制字符序列（例如“\x41”）

  * \u{[0–9A-Fa-f]+} Unicode 代码点序列，将作为该代码点的 UTF-8 表示输出到字符串（在 PHP 7.0.0 中添加）

不是每个人都知道 PHP 表示字符串的语法，而“PHP 变量函数”则成为我们绕过过滤器和规则的瑞士军刀。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

### PHP变量函数

PHP 支持变量函数的概念。这意味着如果变量名后面附加了圆括号，PHP
将寻找与变量求值结果同名的函数，并尝试执行它。除其他事项外，这可用于实现回调、函数表等。

这意味着语法如 $var(args); 和 "sting"(args; 等于 func(args);
。如果我可以通过使用变量或字符串来调用函数，则意味着我可以使用转义序列而不是函数名。这里有一个例子：

![04.png](https://image.3001.net/images/20230614/1686726175_6489661f170eb8d0345ca.png!small)

第三种语法是十六进制符号的转义字符序列，PHP 将其转换为字符串“system”，然后使用参数“ls”转换为函数系统。让我们尝试使用易受攻击的脚本：

![05.png](https://image.3001.net/images/20230614/1686726176_648966200d13fc0ebd746.png!small)

此技术不适用于所有 PHP 函数，变量函数不适用于 echo、print、unset()、isset()、empty()、include、require
。利用包装函数将这些构造中的任何一个用作变量函数。

### 改进用户输入检测

如果我从易受攻击脚本的用户输入中排除双引号和单引号等字符，会发生什么情况？即使不使用双引号也可以绕过它吗？让我们试试：

![06.png](https://image.3001.net/images/20230614/1686726176_64896620e3782a5be1357.png!small)

正如您在第三行看到的，现在脚本阻止在 $_GET[code] 查询字符串参数中使用“和”。我以前的有效负载现在应该被阻止：

![07.png](https://image.3001.net/images/20230614/1686726177_64896621d28a5ced00f7e.png!small)

幸运的是，在 PHP 中，我们并不总是需要引号来表示字符串。PHP 使您能够声明元素的类型，例如 $a = (string)foo; 在这种情况下，$a
包含字符串“foo”。此外，圆括号内没有特定类型声明的任何内容都被视为字符串：

![08.png](https://image.3001.net/images/20230614/1686726178_64896622b4c9b69063cb1.png!small)

在这种情况下，我们有两种方法可以绕过新过滤器：第一种是使用类似 (system)(ls)
的方法；但是我们不能在代码参数中使用“system”，所以我们可以像 (sy.(st).em)(ls); 一样连接字符串。第二种是使用 $GET
变量。如果我发送像 ?a=system&b=ls&code=$GETa 这样的请求；结果是：$GET[a] 将替换为字符串“system”，$GET[b]
将替换为字符串“ls”，我将能够绕过所有过滤器！

![09.png](https://image.3001.net/images/20230614/1686726179_648966237c3d730dd05e7.png!small)

让我们尝试使用第一个有效负载 (sy.(st).em)(whoami)；

![10.png](https://image.3001.net/images/20230614/1686726180_648966244dd439a33baf3.png!small)

和第二个有效载荷 ?

?a=system&b=cat+/etc&c=/passwd&code=$\\_GET[a]($\\_GET[b].$\\_GET[c]);

![11.png](https://image.3001.net/images/20230614/1686726181_64896625488954cf47886.png!small)

在这种情况下，没有用，但您甚至可以在函数名称和参数内部插入注释（这可能有助于绕过阻止特定 PHP 函数名称的 WAF 规则集）。以下所有语法均有效：

#### get_defined_functions 函数

此 PHP 函数返回一个多维数组，其中包含所有已定义函数的列表，包括内置（内部）函数和用户定义函数。内部函数可以通过 $arr[“internal”]
访问，用户定义的函数可以使用 $arr[“user”] 访问。例如：

![12.png](https://image.3001.net/images/20230614/1686726182_648966261d0937045a22d.png!small)

这可能是另一种无需使用其名称即可访问系统功能的方法。如果我对“系统”进行 grep，我可以发现它的索引号并将其用作我的代码执行的字符串：

![13.png](https://image.3001.net/images/20230614/1686726182_64896626dc91e850688fd.png!small)

显然，这应该对我们的 Cloudflare WAF 和脚本过滤器有效：

![14.png](https://image.3001.net/images/20230614/1686726183_64896627c0f407ac4311a.png!small)

#### 字符数组

PHP 中的每个字符串都可以用作字符数组（几乎像 Python 那样），您可以使用语法 $string[2] 或 $string[-3]
引用单个字符串字符。这可能是另一种规避阻止 PHP 函数名称的规则的方法。例如，使用这个字符串 $a=”elmsty/ “; 我可以编写语法系统(“ls
/tmp”);

![15.png](https://image.3001.net/images/20230614/1686726184_648966289adade8270cde.png!small)

如果幸运的话，您可以在脚本文件名中找到所需的所有字符。使用相同的技术，您可以使用类似的方法选择所需的所有字符

![16.png](https://image.3001.net/images/20230614/1686726185_64896629681472e63d905.png!small)

![17.png](https://image.3001.net/images/20230614/1686726186_6489662a5cc12e29ae703.png!small)

### OWASP CRS3

有了 OWASP CRS3，一切都变得更难了。首先，使用之前看到的技术，我只能绕过第一个偏执级别，这太神奇了！因为 Paranoia Level 1
只是我们可以在 CRS3 中找到的规则的一小部分，所以这个级别旨在防止任何误报。对于 2 级偏执狂，由于规则 942430“受限 SQL
字符异常检测（args）：超出特殊字符数”，所有事情都变得困难。我能做的只是执行一个不带参数的命令，如“ls”、“whoami”等。但我无法像使用
Cloudflare WAF 那样执行类似 system(“cat /etc/passwd”) 的命令：

![18.png](https://image.3001.net/images/20230614/1686726187_6489662b34761bf14c5b5.png!small)

![19.png](https://image.3001.net/images/20230614/1686726188_6489662c03f66c4ebdac3.png!small)

###  **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**

