**介绍：**

官方文档：

https://codeql.github.com/docs/codeql-overview/

官方支持的编程语言和框架：

开发语言：C/C++、C#、Go、Java、JavaScript、Python、TypeScript

开发框架<https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/>

 **安装：**

1.下载 CodeQL包：

https://github.com/github/codeql-cli-binaries/releases

2、将CodeQL CLI的可执行文件添加到path变量，这样后面方便操作。

3、标准库：

https://github.com/github/codeql/releases

说明：CodeQL的标准库是需要我们手动下载。

 **验证安装：**

1、运行codeql resolve languages以显示哪些语言可用于数据库创建。这将列出CodeQL CLI包中默认支持的语言

2、运行codeql resolve qlpacks以显示CLI可以找到哪些QL包。

 **一个简单的小例子：**

创建一个Python文件

创建CodeQL的数据库：

codeql database create <database> \--language=<language-identifier>

参数介绍：

<database>：要创建的新数据库的路径。

\--language:要创建数据库的语言的标识符。CodeQL支持为以下语言创建数据库:

 **Language**

|

 **Identifier**  
  
---|---  
  
C/C++

|

cpp  
  
C#

|

csharp  
  
Go

|

go  
  
Java

|

java  
  
JavaScript/TypeScript

|

javascript  
  
Python

|

python  
  
因为我们使用的是Python语言，则创建数据库时命令如下：

codeql database create --language=python <output-folder>/python-database

成功创建之后会提示：Successfully created database at <output-folder>/python-database.

在这个目录下会有一个python-database的文件夹

使用CodeQL CLI分析数据库：

codeql database analyze <database> \--format=<format> \--output=<output>
<queries>参数介绍：

<database>：要分析的CodeQL数据库的路径。

\--format分析过程中生成的结果文件的格式。支持多种不同的格式，包括CSV、SARIF和图形格式。

\--output:分析过程中生成的结果文件的输出路径。

<queries>：在数据库中运行的查询，一个以ql结尾的文件

我们以CSV格式的为结果来查询一个Python的文件，生成的文件格式如下：

![1634541634_616d204298a5ffc3be6e7.png!small](https://image.3001.net/images/20211018/1634541634_616d204298a5ffc3be6e7.png!small)

各列含义如下：

Name，Description，Severity，Message，Path，Start line，Start column，End line，End
column

以上就是通过CodeQL CLI进行了一个代码的查询分析。

查询的重点在于配置文件和查询规则的脚本文件。QL
Pack的配置文件，名称固定为`qlpack.yml`，查询规则的脚本文件，必须为ql后缀的文件，名称随意。

CodeQL的查询语句规则：

    
    
    /**
     *
     * Query metadata
     *
     */
    
    import /* ... CodeQL libraries or modules ... */
    /* ... Optional, define CodeQL classes and predicates ... */
    from /* ... variable declarations ... */
    where /* ... logical formula ... */
    select /* ... expressions ... */

Query metadata规则：

    
    
    /**
     * @id xxx
     * @name xxx
     * @description xxx
     * @tags xxx
     * @kind xxx
     */

配置文件的文件规则

    
    
    name: XXX
    version: 0.0.0
    extractor: XXX
    libraryPathDependencies: XXX

基于以上我们来看下，刚才例子中具体执行：

1、创建一个Test的文件夹，包含两个文件：pythoncode和codeql

2、Pythoncode中我们写一个Python的代码：animal.py

    
    
    def dog(sound):
        print(sound)
    def cat(sound):
        print(sound)
    def chicken(sound):
        if sound:
            pass
        else:
           print("chicken is not sound")

3、在codeql中，我们创建两个文件：ql和qlpack.yml，其中ql文件中写我们的查询规则，yml中写配置文件

Query.ql

    
    
    /**
     * @id redundant
     * @name statement redundant
     * @description Find redundant statements
     * @tags redundant
     * @kind problem
     */
    import python
    from If ifstmt, Stmt pass
    where pass = ifstmt.getStmt(0) and pass instanceof Pass
    select ifstmt, "This 'if' statement is redundant."

qlpack.yml

    
    
    name: python-query
    version: 0.0.0
    extractor: python
    libraryPathDependencies: codeql-python

4、创建codeql数据库：

codeql database create pythondb --language=python --source-root=/Test/PythonCode

5、分析数据库

codeql database analyze pythondb --format=csv --output=query.csv query.ql

此时我们可以在单签目录下看到生成的csv文件。

