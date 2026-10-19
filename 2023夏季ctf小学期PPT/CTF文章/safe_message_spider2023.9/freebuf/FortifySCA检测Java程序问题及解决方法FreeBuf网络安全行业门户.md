**本文是本公司软件进行安全评测的结果经验分享，纯属个人经验，如有问题请及时反馈~**

##  **一、输入验证**

###  **1.1 sql注入**

SQL Injection

Abstract

通过不可信来源的输入构建动态 SQL 指令，攻击者就能够修改指令的含义或者执行任意 SQL 命令。

Explanation

SQL injection 错误在以下情况下发生：

> 1\. 数据从一个不可信赖的数据源进入程序。
>
> 2\. 数据用于动态地构造一个 SQL 查询。

例 1：以下代码动态地构造并执行了一个 SQL 查询，该查询可以搜索与指定名称相匹配的项。该查询仅会显

示条目所有者与被授予权限的当前用户一致的条目。

    
    
    ...
    
        String userName = ctx.getAuthenticatedUserName();
    
        String itemName = request.getParameter("itemName");
    
        String query = "SELECT * FROM items WHERE owner = '"
    
        + userName + "' AND itemname = '"
    
        + itemName + "'";
    
        ResultSet rs = stmt.execute(query);
    
        ...

这一代码所执行的查询遵循如下方式：

    
    
    SELECT * FROM items
    
        WHERE owner =
    
        AND itemname = ;

但是，由于这个查询是动态构造的，由一个不变的基查询字符串和一个用户输入字符串连接而成，因此只有在 itemName
不包含单引号字符时，才会正确执行这一查询。如果一个用户名为 wiley 的攻击者为itemName 输入字符串“name' OR
'a'='a”，那么查询就会变成：

    
    
    SELECT * FROM items
    
        WHERE owner = 'wiley'
    
        AND itemname = 'name' OR 'a'='a';

附加条件 OR 'a'='a' 会使 where 从句永远评估为 true，因此该查询在逻辑上将等同于一个更为简化的查询：

    
    
    SELECT * FROM items;

这种查询的简化会使攻击者绕过查询只返回经过验证的用户所拥有的条目的要求；而现在的查询则会直接返回所有储存在 items 表中的条目，不论它们的所有者是谁。

例 2：这个例子指出了将不同的恶意数值传递给在例 1 中构造和执行的查询时所带来的各种影响。如果一个用户名为 wiley 在 itemName
中输入字符串“name'; DELETE FROM items; --”，则该查询将会变为以下两个：

    
    
    SELECT * FROM items
    
        WHERE owner = 'wiley'
    
        AND itemname = 'name';
    
        DELETE FROM items;
    
        --'

众多数据库服务器，其中包括 Microsoft(R) SQL Server 2000，都可以一次性执行多条用分号分隔的 SQL
指令。对于那些不允许运行用分号分隔的批量指令的数据库服务器，比如 Oracle
和其他数据库服务器，攻击者输入的这个字符串只会导致错误；但是在那些支持这种操作的数据库服务器上，攻击者可能会通过执行多条指令而在数据库上执行任意命令。注意成对的连字符
(--)；这在大多数数据库服务器上都表示下面的语句将作为注释使用，而不能加以执行
[4]。在这种情况下，注释字符的作用就是删除修改的查询指令中遗留的最后一个单引号。而在那些不允许这样加注注释的数据库中，通常攻击者可以如例 1
那样来攻击。如果攻击者输入字符串“name'); DELETE

FROM items; SELECT * FROM items WHERE 'a'='a”就会创建如下三个有效指令：

    
    
    SELECT * FROM items
    
        WHERE owner = 'wiley'
    
        AND itemname = 'name';
    
        DELETE FROM items;
    
        SELECT * FROM items WHERE 'a'='a';

有些人认为在移动世界中，典型的 Web 应用程序漏洞（如 SQL injection）是无意义的 --为什么用户要攻击自己？但是，谨记移动平台的本质是从各种来源下载并在相同设备上运行的应用程序。恶意软件在银行应用程序附近运行的可能性很高，它们会强制扩展移动应用程序的攻击面（包括跨进程通信）。

示例 3：以下代码对示例 1 进行调整，使其适用于 Android 平台。

    
    
    ...
    
        PasswordAuthentication pa = authenticator.getPasswordAuthentication();
    
        String userName = pa.getUserName();
    
        String itemName = this.getIntent().getExtras().getString("itemName");
    
        String query = "SELECT * FROM items WHERE owner = '"
    
        + userName + "' AND itemname = '"
    
        + itemName + "'";
    
        SQLiteDatabase db = this.openOrCreateDatabase("DB", MODE_PRIVATE,
    
        null);
    
        Cursor c = db.rawQuery(query, null);

避免 SQL injection
攻击的传统方法之一是，把它作为一个输入合法性检查的问题来处理，只接受列在白名单中的字符，或者识别并避免那些列在黑名单中的恶意数据。白名单方法是一种非常有效方法，它可以强制执行严格的输入检查规则，但是参数化的
SQL 指令所需维护更少，而且能提供更好的安全保障。而对于通常采用的列黑名单方式，由于总是存在一些小漏洞，所以并不能有效地防止 SQL injection
威胁。例如，攻击者可以：

> 把没有被黑名单引用的值作为目标
>
> 寻找方法以绕过对某一转义序列元字符的需要
>
> 使用存储过程来隐藏注入的元字符

手动去除 SQL 查询中的元字符有一定的帮助，但是并不能完全保护您的应用程序免受 SQL injection 攻击。防范 SQL injection
攻击的另外一种常用方式是使用存储过程。虽然存储过程可以阻止某些类型的 SQLinjection 攻击，但是对于绝大多数攻击仍无能为力。存储过程有助于避免
SQL injection
的常用方式是限制可作为参数传入的指令类型。但是，有许多方法都可以绕过这一限制，许多危险的表达式仍可以传入存储过程。所以再次强调，存储过程在某些情况下可以避免这种攻击，但是并不能完全保护您的应用系统抵御
SQLinjection 的攻击。

Recommendation

造成 SQL injection 攻击的根本原因在于攻击者可以改变 SQL 查询的上下文，使程序员原本要作为数据解析的数值，被篡改为命令了。当构造一个
SQL 查询时，程序员应当清楚，哪些输入的数据将会成为命令的一部分，而哪些仅仅是作为数据。参数化 SQL 指令可以防止直接窜改上下文，避免几乎所有的 SQL
injection 攻击。参数化 SQL 指令是用常规的 SQL
字符串构造的，但是当需要加入用户输入的数据时，它们就需要使用捆绑参数，这些捆绑参数是一些占位符，用来存放随后插入的数据。换言之，捆绑参数可以使程序员清楚地分辨数据库中的数据，即其中有哪些输入可以看作命令的一部分，哪些输入可以看作数据。这样，当程序准备执行某个指令时，它可以详细地告知数据库，每一个捆绑参数所使用的运行时的值，而不会被解析成对该命令的修改。

可以将例 1 改写成使用参数化 SQL 指令（替代用户输入连续的字符串），如下所示：

    
    
    ...
    
        String userName = ctx.getAuthenticatedUserName();
    
        String itemName = request.getParameter("itemName");
    
        String query = "SELECT * FROM items WHERE itemname=? AND owner=?";
    
        PreparedStatement stmt = conn.prepareStatement(query);
    
        stmt.setString(1, itemName);
    
        stmt.setString(2, userName);
    
        ResultSet results = stmt.execute();
    
        ...

下面是 Android 的等同内容：

    
    
    ...
    
        PasswordAuthentication pa = authenticator.getPasswordAuthentication();
    
        String userName = pa.getUserName();
    
        String itemName = this.getIntent().getExtras().getString("itemName");
    
        String query = "SELECT * FROM items WHERE itemname=? AND owner=?";
    
        SQLiteDatabase db = this.openOrCreateDatabase("DB", MODE_PRIVATE, null);
    
        Cursor c = db.rawQuery(query, new Object[]{itemName, userName});
    
        ...

更加复杂的情况常常出现在报表生成代码中，因为这时需要通过用户输入来改变 SQL 指令的命令结构，比如在 WHERE
条件子句中加入动态的约束条件。不要因为这一需求，就无条件地接受连续的用户输入，从而创建查询语句字符串。当必须要根据用户输入来改变命令结构时，可以使用间接的方法来防止
SQL injection 攻击：创建一个合法的字符串**，使其对应于可能要加入到 SQL
指令中的不同元素。在构造一个指令时，可使用来自用户的输入，以便从应用程序控制的值**中进行选择。

扫描到结果截图：

![](https://image.3001.net/images/20190821/1566357325_5d5cb74dbdfe3.png!small)

**注：这些错误把参数以"?"的形式传输即可解决**

###  **1.2 跨站脚本攻击**

这个

> Cross-Site Scripting: External Links、Persistent、Reflected

Abstract

向一个 Web 浏览器发送未经验证的数据会导致该浏览器执行恶意代码。配置中的设置可最大限度降低暴露cross-site scripting 漏洞的可能性。

Explanation

Cross-Site Scripting (XSS) 漏洞在以下情况下发生：

> 1\. 数据通过一个不可信赖的资源进入 Web 应用程序，通常是一个网页请求或者数据库。
>
> 2\. 未检验包含在动态内容中的数据，便将其传送给了 Web 用户。传送到 Web 浏览器的恶意内容通常采用 JavaScript
> 代码片段的形式，但也可能会包含一些 HTML、Flash 或者他任意一种可以被浏览器执行的代码。基于 XSS
> 的攻击手段花样百出，几乎是无穷无尽的，但通常它们都会包含传输给攻击者的私人数据（如 Cookie
> 或者其他会话信息）。在攻击者的控制下，指引受害者进入恶意的网络内容；或者利用易受攻击的站点，对用户的机器进行其他恶意操作。由于针对 XSS
> 漏洞进行的攻击通常涉及到与受攻击者控制的恶意站点进行通信或需要重新定向到该站点，因此注入对其他域内容引用的能力在诸多攻击中必不可少。可对
> AntiSamy 进行配置，使其阻止指向外部域的链接，进而降低攻击者可通过 XSS 攻击造成的破坏。然而，这种保护只能解决部分问题，并不能解决由XSS
> 漏洞带来的整体威胁。

例 1：以下 AntiSamy 配置条目允许链接至在应用程序所运行的域之外的 URL。

    
    
    <attribute name=href onInvalid=filterTag">
    
            <regexp-list>
    
                <regexp name="onsiteURI"/>
    
                <regexp name=offsiteURI"/>
    
            </regexp-list>
    
        </attribute>

Recommendation

无论什么时候，应尽可能阻止引用了外部域的链接。

例 2：以下 AntiSamy 配置条目禁止链接至在应用程序所运行的域之外的 URL。

    
    
    <attribute name=href onInvalid="filterTag">
    
            <regexp-list>
    
                <regexp name="onsiteURL"/>
    
            </regexp-list>
    
        </attribute>

例 3：以下 JSP 代码片段可在数据库中查询具有给定 ID 的雇员，并输出相应雇员姓名。

    
    
    <%...
    
        Statement stmt = conn.createStatement();
    
        ResultSet rs = stmt.executeQuery("select * from emp where id="+eid);
    
        if (rs != null) {
    
        rs.next();
    
        String name = rs.getString("name");
    
        }
    
        %>
    
        Employee Name: <%= name %>

如果对 name 的值处理得当，该代码就能正常地执行各种功能；如若处理不当，就会对代码的盗取行为无能为力。这段代码暴露出的危险较小，因为 name
的值是从数据库中读取的，而且显然这些内容是由应用程序管理的。然而，如果 name
的值是由用户提供的数据产生，数据库就会成为恶意内容沟通的通道。如果不对数据库中存储的所有数据进行恰当的输入验证，那么攻击者就可以在用户的 Web
浏览器中执行恶意命令。这种类型的 Persistent XSS（也称为 Stored
XSS）盗取极其阴险狡猾，因为数据存储导致的间接性使得辨别威胁的难度增大，而且还提高了一个攻击影响多个用户的可能性。XSS 盗取会从访问提供留言簿
(guestbook)的网站开始。攻击者会在这些留言簿的条目中嵌入 JavaScript，接下来所有访问该留言簿的用户都会执行这些恶意代码。

针对 XSS 的解决方法是，确保在适当位置进行验证，并检验其属性是否正确。

由于 XSS 漏洞出现在应用程序的输出中包含恶意数据时，因此，合乎逻辑的做法是在数据流出应用程序的前一刻对其进行验证。然而，由于 Web
应用程序常常会包含复杂而难以理解的代码，用以生成动态内容，因此，这一方法容易产生遗漏错误（遗漏验证）。降低这一风险的有效途径是对 XSS 也执行输入验证。

由于 Web 应用程序必须验证输入信息以避免其他漏洞（如 SQL Injection），因此，一种相对简单的解决方法是，加强一个应用程序现有的入验证机制，将
XSS 检测包括其中。尽管有一定的价值，但 XSS
输入验证并不能取代严格的输出验证。应用程序可能通过共享的数据存储或其他可信赖的数据源接受输入，而该数据存储所接受的输入源可能并未执行适当的输入验证。因此，应用程序不能间接地依赖于该数据或其他任意数据的安全性。这就意味着，避免
XSS 漏洞的最佳方法是验证所有进入应用程序以及由应用程序传送至用户端的数据。

针对 XSS 漏洞进行验证最安全的方式是，创建一份安全字符白名单，允许其中的字符出现在 HTTP
内容中，并且只接受完全由这些经认可的字符组成的输入。例如，有效的用户名可能仅包含字母数字字符，电话号码可能仅包含 0-9 的数字。然而，这种解决方法在
Web 应用程序中通常是行不通的，因为许多字符对浏览器来说都具有特殊的含义，在写入时，这些字符仍应被视为合法的输入，比如一个 Web 设计版就必须接受带有
HTML 代码片段的输入。

更灵活的解决方法称为黑名单方法，但其安全性较差，这种方法在进行输入之前就有选择地拒绝或避免了潜在的危险字符。为了创建这样一个列表，首先需要了解对于 Web
浏览器具有特殊含义的字符集。虽然HTML 标准定义了哪些字符具有特殊含义，但是许多 Web 浏览器会设法更正 HTML
中的常见错误，并可能在特定的上下文中认为其他字符具有特殊含义，这就是我们不鼓励使用黑名单作为阻止 XSS 的方法的原因。卡耐基梅隆大学 (Carnegie
Mellon University) 软件工程学院 (Software Engineering Institute) 下属的CERT(R) (CERT(R)
Coordination Center) 合作中心提供了有关各种上下文中认定的特殊字符的具体信息 [1]

：

在有关块级别元素的内容中（位于一段文本的中间）：

> "<" 是一个特殊字符，因为它可以引入一个标签。
>
> "&" 是一个特殊字符，因为它可以引入一个字符实体。
>
> ">" 是一个特殊字符，之所以某些浏览器将其认定为特殊字符，是基于一种假设，即该页的作者本想在前面添加一个 "<"，却错误地将其遗漏了。

下面的这些原则适用于属性值：

> 对于外加双引号的属性值，双引号是特殊字符，因为它们标记了该属性值的结束。
>
> 对于外加单引号的属性值，单引号是特殊字符，因为它们标记了该属性值的结束。
>
> 对于不带任何引号的属性值，空格字符（如空格符和制表符）是特殊字符。
>
> "&" 与某些特定变量一起使用时是特殊字符，因为它引入了一个字符实体。

例如，在 URL 中，搜索引擎可能会在结果页面内提供一个链接，用户可以点击该链接来重新运行搜索。可以将这一方法运用于编写 URL
中的搜索查询语句，这将引入更多特殊字符：

> 空格符、制表符和换行符是特殊字符，因为它们标记了 URL 的结束。
>
> "&" 是特殊字符，因为它可引入一个字符实体或分隔 CGI 参数。
>
> 非 ASCII 字符（即 ISO-8859-1 编码表中所有高于 128 的字符）不允许出现在 URL 中，因此在此上下文中也被视为特殊字符。
>
> 在服务器端对在 HTTP 转义序列中编码的参数进行解码时，必须过滤掉输入中的 "%" 符号。例如，当输入中出现 "%68%65%6C%6C%6F"
> 时，只有从输入的内容中过滤掉 "%"，上述字符串才能在网页上显示为"hello"。

在 的正文内：

> 如果可以将文本直接插入到已有的脚本标签中，应该过滤掉分号、省略号、中括号和换行符。

服务器端脚本：

> 如果服务器端脚本会将输入中的感叹号 (!) 转换成输出中的双引号 (")，则可能需要对此进行更多过滤。

配置文件可用来缩小攻击者可用来实施攻击的攻击面。

例 1：以下 AntiSamy 配置文件禁止在 href 中设置异地 URL。

    
    
    <attribute name=href" onInvalid=filtertag">
    
            <regexp-list>
    
                < regexp name="onsiteURL"/>
    
            </regexp-list>
    
        </attribute>

扫描到结果截图：

**注：这个直接加上过滤器就行了，不算太难，但是加上之后一定要跟扫描代码的人员说一下，自己代码中存在这个过滤器，反正我扫描的时候总感觉这个工具不能自动检测到过滤器给自己带来很多不是问题的问题**

###  **1.3 路径操作**

###  **1.4 代码注入**

###  **1.5 上传任意文件**

###  **1.6 未验证的重新定向和转发**

###  **1.7 拒绝服务**

###  **1.8 HTTP响应截断**

##  **二、安全特性**

###  **2.1访问控制**

**个人修改方法：附加限制，获取当前登录用户，对任何查询操作均校验该人员是否有权限**

**以下为官方解释及修改方法**

> Access Control: Database

Abstract

如果没有适当的 access control，就会执行一个包含用户控制主键的 SQL 指令，从而允许攻击者访问未经授权的记录。

Explanation

Database access control 错误在以下情况下发生：

> 1\. 数据从一个不可信赖的数据源进入程序。
>
> 2\. 这个数据用来指定 SQL 查询中主键的值。

示例 1：以下代码使用可转义元字符并防止出现 SQL 注入漏洞的参数化语句，以构建和执行用于搜索与指定标识符 [1] 相匹配的清单的 SQL
查询。您可以从与当前被授权用户有关的所有清单中选择这些标识符。

    
    
    ...
    
        id = Integer.decode(request.getParameter("invoiceID"));
    
        String query = "SELECT * FROM invoices WHERE id = ?";
    
        PreparedStatement stmt = conn.prepareStatement(query);
    
        stmt.setInt(1, id);
    
        ResultSet results = stmt.execute();
    
        ...

问题在于开发者没有考虑到所有可能出现的 id
值。虽然接口生成了一个当前用户的标识符清单，但是攻击者可以绕过这个接口，从而获取所需的任何清单。因为此例中的代码没有执行检查，确保用户有权访问需要的清单，所以代码会显示所有清单，即使这些清单并不属于当前用户。有些人认为在移动世界中，典型的
Web 应用程序漏洞（如 Database access control 错误）是无意义的 --为什么用户要攻击自己？但是，谨记移动平台的本质是从各种来源下载并在相同设备上运行的应用程序。恶意软件在银行应用程序附近运行的可能性很高，它们会强制扩展移动应用程序的攻击面（包括跨进程通信）。

示例 2：以下代码对示例 1 进行调整，使其适用于 Android 平台。

    
    
    ...
    
        String id = this.getIntent().getExtras().getString("invoiceID");
    
        String query = "SELECT * FROM invoices WHERE id = ?";
    
        SQLiteDatabase db = this.openOrCreateDatabase("DB", MODE_PRIVATE,
    
        null);
    
        Cursor c = db.rawQuery(query, new Object[]{id});

许多现代 Web 框架都提供对用户输入执行验证的机制。其中包括 Struts 和 Spring MVC。为了突出显示未经验证的输入源，Fortify
安全编码规则包会降低 Fortify Static Code Analyzer（Fortify
静态代码分析器）报告的问题被利用的可能性，并在使用框架验证机制时提供相应的依据，以动态重新调整问题优先级。我们将这种功能称之为上下文敏感排序。为了进一步帮助
Fortify 用户执行审计过程，Fortify 软件安全研究团队提供了数据验证项目模板，该模板会根据应用于输入源的验证机制，将问题分组到多个文件夹中。

Recommendation

与其靠表示层来限制用户输入的值，还不如在应用程序和数据库层上进行 access
control。任何情况下都不允许用户在没有取得相应权限的情况下获取或修改数据库中的记录。每个涉及数据库的查询都必须遵守这个原则，这可以通过把当前被授权的用户名作为查询语句的一部分来实现。

例 3：以下代码实施了与例 1 相同的功能，但是附加了一个限制，即为当前被授权的用户指定某一特定的获

取清单的方式。

    
    
    ...
    
        userName = ctx.getAuthenticatedUserName();
    
        id = Integer.decode(request.getParameter("invoiceID"));
    
        String query =
    
        "SELECT * FROM invoices WHERE id = ? AND user = ?";
    
        PreparedStatement stmt = conn.prepareStatement(query);
    
        stmt.setInt(1, id);
    
        stmt.setString(2, userName);
    
        ResultSet results = stmt.execute();
    
        ...

下面是 Android 的等同内容：

    
    
    ...
    
        PasswordAuthentication pa = authenticator.getPasswordAuthentication();
    
        String userName = pa.getUserName();
    
        String id = this.getIntent().getExtras().getString("invoiceID");
    
        String query = "SELECT * FROM invoices WHERE id = ? AND user = ?";
    
        SQLiteDatabase db = this.openOrCreateDatabase("DB", MODE_PRIVATE,
    
        null);
    
        Cursor c = db.rawQuery(query, new Object[]{id, userName});
    
        ...

扫描到结果截图：

![](https://image.3001.net/images/20190821/1566357426_5d5cb7b2be7c3.png!small)![](https://image.3001.net/images/20190821/1566357431_5d5cb7b7ded13.png!small)![](https://image.3001.net/images/20190821/1566357435_5d5cb7bbd32eb.png!small)
![](https://image.3001.net/images/20190821/1566357440_5d5cb7c0e3a7d.png!small)

**注：在这里面我发现只要你传输的数据中存在"id"那么恭喜你中奖了，工具都会默认想让你增加用户验证。**

###  **2.2不安全的加密存储**

###  **2.3密码管理**

###  **2.4 私有信息侵犯**

###  **2.5 不安全的随机函数**

##  **三、代码质量**

###  **3.1硬编码**

###  **3.2 未释放资源**

###  **3.3 空指针调用**

##  **四、环境**

###  **4.1安全配置错误**

##  **五、代码封装**

###  **5.1 系统信息泄露**

第一次写这种总结，本来想着一上午就能搞定，突然发现这么多，慢慢整理吧，后期会更新，我是一个很懒的程序员ヽ(●-`Д´-)ノ

* **本文原创作者：Mr一凡先生，本文属于FreeBuf原创奖励计划，未经许可禁止转载 ******

