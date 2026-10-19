![00000.png](https://image.3001.net/images/20200211/1581430472_5e42b6c884c59.png!small)

**Pytm是一款Python风格的威胁建模框架，它可以帮助我们以Python语言风格的形式并使用pytm框架中的元素和属性来定义你的系统。根据我们的定义参数，pytm可以针对你的系统生成数据流图（DFD）、序列图以及威胁模型。**

## 工具要求

> Linux/MacOS
>
> Python 3.x
>
> Graphviz package
>
> Java (OpenJDK 10 or 11)
>
> [
> _plantuml.jar_](http://sourceforge.net/projects/plantuml/files/plantuml.jar/download)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/izar/pytm.git

## 工具使用

    
    
    tm.py [-h] [--debug] [--dfd] [--report REPORT] [--exclude EXCLUDE] [--seq] [--list] [--describe DESCRIBE]
    
     
    
    optional arguments:
    
      -h, --help           show this help message and exit
    
      --debug              print debug messages
    
      --dfd                output DFD (default)
    
      --report REPORT      output report using the named template file (sample template file is under docs/template.md)
    
      --exclude EXCLUDE    specify threat IDs to be ignored
    
      --seq                output sequential diagram
    
      --list               list all available threats
    
      --describe DESCRIBE  describe the properties available for a given element

当前该工具可用的元素包括：TM、服务器、外部实体、数据存储、Actor、进程、进程集、数据边界和Lambda。

除此之外，我们也可以使用命令“--describe”来查看每一个元素的可用属性：

    
    
    (pytm) ➜  pytm git:(master) ✗ ./tm.py --describe Element
    
    Element
    
    	OS
    
    	check
    
    	definesConnectionTimeout
    
    	description
    
    	dfd
    
    	handlesResources
    
    	implementsAuthenticationScheme
    
    	implementsNonce
    
    	inBoundary
    
    	inScope
    
    	isAdmin
    
    	isHardened
    
    	name
    
    	onAWS

如果你是安全从业人员的话，你也可以向“`threatlib/threats.json`”文件中添加新的威胁属性：

    
    
    {
    
       "SID":"INP01",
    
       "target": ["Lambda","Process"],
    
       "description": "Buffer Overflow via Environment Variables",
    
       "details": "This attack pattern involves causing a buffer overflow through manipulation of environment variables. Once the attacker finds that they can modify an environment variable, they may try to overflow associated buffers. This attack leverages implicit trust often placed in environment variables.",
    
       "Likelihood Of Attack": "High",
    
       "severity": "High",
    
       "condition": "target.usesEnvironmentVariables is True and target.sanitizesInput is False and target.checksInputBounds is False",
    
       "prerequisites": "The application uses environment variables.An environment variable exposed to the user is vulnerable to a buffer overflow.The vulnerable environment variable uses untrusted data.Tainted data used in the environment variables is not properly validated. For instance boundary checking is not done before copying the input data to a buffer.",
    
       "mitigations": "Do not expose environment variable to the user.Do not use untrusted data in your environment variables. Use a language or compiler that performs automatic bounds checking. There are tools such as Sharefuzz [R.10.3] which is an environment variable fuzzer for Unix that support loading a shared library. You can use Sharefuzz to determine if you are exposing an environment variable vulnerable to buffer overflow.",
    
       "example": "Attack Example: Buffer Overflow in $HOME A buffer overflow in sccw allows local users to gain root access via the $HOME environmental variable. Attack Example: Buffer Overflow in TERM A buffer overflow in the rlogin program involves its consumption of the TERM environmental variable.",
    
       "references": "https://capec.mitre.org/data/definitions/10.html, CVE-1999-0906, CVE-1999-0046, http://cwe.mitre.org/data/definitions/120.html, http://cwe.mitre.org/data/definitions/119.html, http://cwe.mitre.org/data/definitions/680.html"
    
     }

## 注意事项

“`threats.json`”文件中包含的字符串可以通过`eval()`函数来运行，它可以确保文件拥有正确的权限并确保代码能够正确执行。

下面的样本是tm.py文件，它描述了一个简单的应用程序，其中一名用户“`User`”登录进了应用程序，然后在App上发布了评论。App服务器将这些评论存储进了数据库，服务器中有一个`AWS
Lambda`会定期清理数据库。

    
    
    #!/usr/bin/env python3
    
     
    
    from pytm.pytm import TM, Server, Datastore, Dataflow, Boundary, Actor, Lambda
    
     
    
    tm = TM("my test tm")
    
    tm.description = "another test tm"
    
     
    
    User_Web = Boundary("User/Web")
    
    Web_DB = Boundary("Web/DB")
    
     
    
    user = Actor("User")
    
    user.inBoundary = User_Web
    
     
    
    web = Server("Web Server")
    
    web.OS = "CloudOS"
    
    web.isHardened = True
    
     
    
    db = Datastore("SQL Database (*)")
    
    db.OS = "CentOS"
    
    db.isHardened = False
    
    db.inBoundary = Web_DB
    
    db.isSql = True
    
    db.inScope = False
    
     
    
    my_lambda = Lambda("cleanDBevery6hours")
    
    my_lambda.hasAccessControl = True
    
    my_lambda.inBoundary = Web_DB
    
     
    
    my_lambda_to_db = Dataflow(my_lambda, db, "(λ)Periodically cleans DB")
    
    my_lambda_to_db.protocol = "SQL"
    
    my_lambda_to_db.dstPort = 3306
    
     
    
    user_to_web = Dataflow(user, web, "User enters comments (*)")
    
    user_to_web.protocol = "HTTP"
    
    user_to_web.dstPort = 80
    
    user_to_web.data = 'Comments in HTML or Markdown'
    
    user_to_web.order = 1
    
     
    
    web_to_user = Dataflow(web, user, "Comments saved (*)")
    
    web_to_user.protocol = "HTTP"
    
    web_to_user.data = 'Ack of saving or error message, in JSON'
    
    web_to_user.order = 2
    
     
    
    web_to_db = Dataflow(web, db, "Insert query with comments")
    
    web_to_db.protocol = "MySQL"
    
    web_to_db.dstPort = 3306
    
    web_to_db.data = 'MySQL insert statement, all literals'
    
    web_to_db.order = 3
    
     
    
    db_to_web = Dataflow(db, web, "Comments contents")
    
    db_to_web.protocol = "MySQL"
    
    db_to_web.data = 'Results of insert op'
    
    db_to_web.order = 4
    
     
    
    tm.process()

图表将以Dot或PlantUML的形式输出。

如果在运行`tm.py`文件时使用了“`--dfd`”参数，那么它将会向stdout生成输出文件：

    
    
    tm.py --dfd | dot -Tpng -o sample.png

生成的图表如下：

![a.png](https://image.3001.net/images/20200211/1581430557_5e42b71d86ebd.png!small)

下列命令可以生成一份序列图：

    
    
    tm.py --seq | java -Djava.awt.headless=true -jar plantuml.jar -tpng -pipe > seq.png

![b.png](https://image.3001.net/images/20200211/1581430566_5e42b726c2d99.png!small)

生成的图表和数据可以引入到模板文件中来创建最终的报告：

    
    
    tm.py --report docs/template.md | pandoc -f markdown -t html > report.html

用于生成报告的模板格式如下：

    
    
    # Threat Model Sample
    
    ***
    
     
    
    ## System Description
    
     
    
    {tm.description}
    
     
    
    ## Dataflow Diagram
    
     
    
    ![Level 0 DFD](dfd.png)
    
     
    
    ## Dataflows
    
     
    
    Name|From|To |Data|Protocol|Port
    
    ----|----|---|----|--------|----    
    {dataflows:repeat:{{item.name}}|{{item.source.name}}|{{item.sink.name}}|{{item.data}}|{{item.protocol}}|{{item.dstPort}}
    
    }
    
     
    
    ## Findings
    
     
    
    {findings:repeat:* {{item.description}} on element "{{item.target}}"
    
    }
    
    ### 

### 当前支持的威胁如下：

    
    
    INP01 - Buffer Overflow via Environment Variables
    
    INP02 - Overflow Buffers
    
    INP03 - Server Side Include (SSI) Injection
    
    CR01 - Session Sidejacking
    
    INP04 - HTTP Request Splitting
    
    CR02 - Cross Site Tracing
    
    INP05 - Command Line Execution through SQL Injection
    
    INP06 - SQL Injection through SOAP Parameter Tampering
    
    SC01 - JSON Hijacking (aka JavaScript Hijacking)
    
    LB01 - API Manipulation
    
    AA01 - Authentication Abuse/ByPass
    
    DS01 - Excavation
    
    DE01 - Interception
    
    DE02 - Double Encoding
    
    API01 - Exploit Test APIs
    
    AC01 - Privilege Abuse
    
    INP07 - Buffer Manipulation
    
    AC02 - Shared Data Manipulation
    
    DO01 - Flooding
    
    HA01 - Path Traversal
    
    AC03 - Subverting Environment Variable Values
    
    DO02 - Excessive Allocation
    
    DS02 - Try All Common Switches
    
    INP08 - Format String Injection
    
    INP09 - LDAP Injection
    
    INP10 - Parameter Injection
    
    INP11 - Relative Path Traversal
    
    INP12 - Client-side Injection-induced Buffer Overflow
    
    AC04 - XML Schema Poisoning
    
    DO03 - XML Ping of the Death
    
    AC05 - Content Spoofing
    
    INP13 - Command Delimiters
    
    INP14 - Input Data Manipulation
    
    DE03 - Sniffing Attacks
    
    CR03 - Dictionary-based Password Attack
    
    API02 - Exploit Script-Based APIs
    
    HA02 - White Box Reverse Engineering
    
    DS03 - Footprinting
    
    AC06 - Using Malicious Files
    
    HA03 - Web Application Fingerprinting
    
    SC02 - XSS Targeting Non-Script Elements
    
    AC07 - Exploiting Incorrectly Configured Access Control Security Levels
    
    INP15 - IMAP/SMTP Command Injection
    
    HA04 - Reverse Engineering
    
    SC03 - Embedding Scripts within Scripts
    
    INP16 - PHP Remote File Inclusion
    
    AA02 - Principal Spoof
    
    CR04 - Session Credential Falsification through Forging
    
    DO04 - XML Entity Expansion
    
    DS04 - XSS Targeting Error Pages
    
    SC04 - XSS Using Alternate Syntax
    
    CR05 - Encryption Brute Forcing
    
    AC08 - Manipulate Registry Information
    
    DS05 - Lifting Sensitive Data Embedded in Cache

## 项目地址

Pytm：【[GitHub传送门](https://github.com/izar/pytm)】

 ***参考来源：[
_izar_](https://github.com/izar/pytm)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

