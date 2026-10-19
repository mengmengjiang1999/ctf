![](https://image.3001.net/images/20210922/1632316602_614b2cbacc06b38c1d2d9.png!small)

## 关于SQLancer

SQLancer，全称为Synthesized Query
Lancer，该工具是一款针对数据库管理系统DBMS的自动化安全测试工具。该工具可以帮助广大研究人员轻松识别应用程序实现中的逻辑漏洞。我们这里所指的逻辑漏洞，即能够导致DBMS获取错误结果集的安全漏洞（比如说忽略数据记录等等）。

 **SQLancer能够在下面两个阶段进行操作：**

>
> 1，数据库生成：此阶段的目标是创建一个填充有数据的数据库，并向DBMS输入测试用例以尝试识别和检测不一致数据库状态。随后，该工具将会创建一个随机表，并随机选择SQL语句来生成、修改和删除数据。除此之外，该工具还会使用其他类型的语句（如创建索引和视图以及设置DBMS特定选项的语句）来测试目标DBMS；
>
> 2，测试：此阶段的目标是针对生成的数据库检测逻辑错误。

## 工具要求

> Java 8或以上版本；
>
> Maven（Ubuntu安装：“sudo apt install maven”）；
>
> 需要测试的DBMS（项目中带有SQLite，而SQLite是一款嵌入式DBMS）。

## 工具安装&使用

广大研究人员可以使用下列命令将该项目源码克隆至本地，然后创建一个JAR，并开启SQLancer来测试SQLite，此过程使用的是非优化引用引擎结构（NoREC）：

    
    
    git clone https://github.com/sqlancer/sqlancer
    cd sqlancer
    mvn package -DskipTests
    cd target
    java -jar sqlancer-*.jar --num-threads 4 sqlite3 --oracle NoREC

执行之后，工具每5秒会打印一次处理信息。SQLancer可能会找出SQLite中的漏洞，在报告漏洞信息之前，请确保处理信息仍在打印。我们可以按下CTRL +
C组合键手动停止SQLancer的运行。如果SQLancer没有找出漏洞，那么它将会一直运行下去。我们可以使用“--num-tries”来控制SQLancer在找到多少漏洞之后停止运行。除此之外，我们也可以使用“--timeout-seconds”来指定SQLancer允许执行的最大超时。

如果SQLancer在没有参数的情况下执行，工具则会输出所有可用的选项和命令。

## 支持的DBMS

由于各种DBMS使用的SQL形式差异很大，因此需要针对不同的DBMS采用单独的实现方式：

> SQLite
>
> MySQL
>
> PostgreSQL
>
> Citus
>
> MariaDB
>
> CockroachDB
>
> TiDB
>
> DuckDB
>
> ClickHouse

## 项目地址

 **SQLancer：** 【[ _GitHub传送门_](https://github.com/sqlancer/sqlancer)】

## 参考资料

> [
> _https://github.com/sqlancer/sqlancer/blob/master/CONTRIBUTING.md_](https://github.com/sqlancer/sqlancer/blob/master/CONTRIBUTING.md)
>
> [
> _https://github.com/sqlancer/sqlancer/blob/master/docs/PAPERS.md_](https://github.com/sqlancer/sqlancer/blob/master/docs/PAPERS.md)
>
> [ _https://github.com/chaos-mesh/go-sqlancer_](https://github.com/chaos-> mesh/go-sqlancer)
>
> [ _https://www.manuelrigger.at/dbms-> bugs/_](https://www.manuelrigger.at/dbms-bugs/)

