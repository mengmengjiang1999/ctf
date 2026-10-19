## 一、说明

**本文说的是等级保护1.0中SQLServer数据库操作超时的内容，实际在SQLServer中有很多种超时选项，很容易将其混为一谈，本文将尽力将之说清楚。**

## 二、操作超时的意义

操作超时在sqlserver数据库中可能包含好几个意思：

### 2.1. 客户端连接数据库时的连接超时时间

就是指在客户端连接数据库时，如果在限定时间内数据库没有回应，则返回失败的结果，其中的时间。

值得注意的是，此项是由客户端来指定而非数据库，更具体的来说，是在数据库连接字符串中，以C#为例子：

    
    
    server=.;database=myDB;User ID=sa;Password=password;Connect Timeout=500
    

其中的`Connect
Timeout`即为连接超时时间，单位为秒。也就是说，连接超时时间不仅是由客户端指定，而且还具体到某次连接当中，很简单，如果客户端下次发来的连接字符串把`Connect
Timeout`的值改了，自然这一次的连接超时时间也就改了。所以，这里和主机的超时是有些不一样的，主机的超时是在主机中进行设置（无论linux还是windows），由主机决定而不是连接主机的终端决定。

通常我们用SQL Server Management Studio来管理sqlserver数据库，其本质就是一个可以连接数据库的软件而已。

它的原理大概应该是这样：

让用户选择好验证方式（windows验证还是sqlserver验证），输入用户名和口令（如果是sqlserver验证的话），然后你自己通过用户的操作生成相应的`连接字符串`，连接上数据库，并将此`连接字符串`进行保存。

成功后保存用户的输入（如用户名和口令）在代码中，如用户进行其他查询（通过点击或者输入sql语句），再使用先前保存的`连接字符串`，再和数据库连接一次，并执行相应的命令。因为不大可能从头到尾就用一个连接来搞定，所以应该是每执行一次操作就连接一次，只不过除第一次连接（登陆）时需要用户进行输入用户名和口令，其余的连接用户就不需要再次输入了。

这个过程我相信只要是编写过和数据库有交互的软件的人，都能看明白的。

好，那么SQL Server Management Studio有没有地方可以设置连接超时时间呢？

有，就是在登录界面中，而且还能直接手写连接字符串：  
![图片.png](https://image.3001.net/images/20190726/1564106000_5d3a5d105a15a.png!small)![图片.png](https://image.3001.net/images/20190726/1564106012_5d3a5d1c0041e.png!small)

### 2.2. 客户端执行某项sql语句的超时时间

连接数据库后，对数据库进行某项操作（查询、修改、删除、插入），如果在限定时间内没有返回结果，则此次操作失败并中断连接，其中的时间。
和连接超时差不多，也是由连接数据库的客户端进行指定，以C#为例子的话，是在代码中对`SqlCommand`对象的`CommandTimeout`属性进行设置。

而在 **SQL Server Management Studio** 中有两个地方可以进行设置：

 **登陆界面中**  
注意，这个是全局设置，估计会用一个全局变量将`执行超时值`存储起来，每次在`SQL Server Management
Studio`中执行sql语句时，会使用该全局变量进行设置。  
![图片.png](https://image.3001.net/images/20190726/1564106023_5d3a5d2740cd6.png!small)

**每次新建查询后的查询选项**

点击`新建查询`后，会新建一个查询，该查询的`执行超时值`会使用全局变量的`执行超时值`进行初始化，当然，你也可以自己再进行改动，改动后仅对这个查询有效。  
![图片.png](https://image.3001.net/images/20190726/1564106036_5d3a5d34750c5.png!small)![图片.png](https://image.3001.net/images/20190726/1564106046_5d3a5d3e3966a.png!small)
![图片.png](https://image.3001.net/images/20190726/1564106054_5d3a5d46e5c10.png!small)

### 2.3. 数据库连接远程数据库的超时时间

这里说的是`remote login timeout`，也就是初级教程中让我们查的值：  
![图片.png](https://image.3001.net/images/20190726/1564106064_5d3a5d50ac90e.png!small)

这个值是什么意思呢？

我们对sqlserver数据库执行sql语句如查询语句，往往是对一个数据源（数据库）进行查询，而当我们涉及到另一个远程数据源（数据库）的时候，就需要对远程数据源进行连接（登陆），而我们可以通过
**链接服务器** 实现这个功能。

> 通过链接服务器，SQL Server 数据库引擎 和 Azure SQL 数据库托管实例可从远程数据源中读取数据，并针对 SQL Server
> 实例之外的 OLE DB 数据源等远程数据库服务器执行命令。

在msdn中，`remote login timeout`的说明如下：

> remote login timeout 选项指定从登录远程服务器失败返回前等待的秒数。 例如，如果您尝试登录到一个远程服务器而该服务器已关闭，
> remote login timeout 帮助确保您在计算机停止登录尝试前不必无限期地等待下去。 此选项的默认值为 10 秒。 如果该值为
> 0，则允许无限期等待。

比如类似语句就会使用链接服务器：

    
    
    SELECT * FROM [WIN-CGQ89NM7L8J,15478].master.sys.objects
    

而`remote login timeout`的意思是指你现在连接的这个数据库，它去连接远程数据源时，相应的连接超时时间。 也就是说，这里并不是对`SQL
Server Management Studio`这个客户端软件进行设置，而是对你现在连接的这个sqlserver数据库本身进行设置。

所以我们要进行区分，同样是在`SQL Server Management
Studio`上进行一些设置，有些是对这个软件本身的一些项进行设置（如连接超时值等），而有些则是对你连接的这个数据库的一些项进行设置（如`remote
login timeout`）。

我们既可以通过sql语句对`remote login timeout`进行设置，也可以在`SQL Server Management
Studio`界面中进行设置：  
![图片.png](https://image.3001.net/images/20190726/1564106144_5d3a5da0b87c0.png!small)

这两者是等价的，或者说，界面中的远程登录超时值本来就是从数据库中查出来的。

到这里我们可以知道，这个值其实并不符合初级教程中的说明，从描述上看，初级教程是希望对`SQL Server Management
Studio`的空闲时间进行限制，就是长时间不操作`SQL Server Management Studio`后，`SQL Server
Management Studio`会让你重新输入用户名和口令或者自动退出的功能。

### 2.4. 数据库的远程执行超时时间

也就是`remote query timeout`，和`remote login timeout`差不多一个意思：

> remote query timeout 选项指定在 SQL Server 超时之前远程操作可以持续的时间（秒）。此选项的默认值是 600，即允许等待
> 10 分钟。

查询方法也有两种（sql语句和图形界面）：

`sp_configure 'remote query timeout'`  

![图片.png](https://image.3001.net/images/20190726/1564106155_5d3a5dab69bdc.png!small)![图片.png](https://image.3001.net/images/20190726/1564106163_5d3a5db3a791a.png!small)

### 2.5. 某连接的空闲超时时间

当某连接的空闲时间超过一定限制时将其断开，但是sqlserver数据库本身没有这种设置项，`SQL Server Management
Studio`对自己的某个连接也没有这种设置项。 要实现这个功能，需要自己写一个定时任务来解决（来源于网上）：

    
    
    DECLARE @sql NVARCHAR(MAX)
    SET @sql=''
    SELECT @sql='kill '+LTRIM(spid)+';' FROM sys.sysprocesses AS s 
        WHERE s.spid>50                                --不是系统进程 
        AND s.spid<>@@SPID                            --不是当前进程
        AND s.last_batch<DATEADD(HOUR,-4,GETDATE())    --最后执行时间是4小时之前
        AND s.program_name='Microsoft SQL Server Management Studio' --从客户端连接
    --输出要执行的SQL
    PRINT @sql
    --执行动态SQL
    EXEC(@sql)
    

不过我感觉还是有点问题，`last_batch`能不能代表最后执行操作的时间，还未能确认。

### 2.6. SQL Server Management Studio的空闲超时时间

这个其实就是初级教程希望达到的一个目的。

每次`SQL Server Management Studio`对数据库执行操作，比如你新建一个查询，其本质就是新连接了数据库一次。当然可能`SQL
Server Management
Studio`会在某些地方连上数据库就不断开了，一直使用这个连接。但更大概率应该是用完就断，用的时候再连（具体我也不清楚，因为我不知道它代码里怎么实现的），所以`连接的空闲超时时间`的意义其实并不很大。

而长时间不操作使得`SQL Server Management
Studio`自动退出或者让你重新输入用户名和口令这种设置，应该是没有的，至少我没找到这种选项。这个设置和数据库其实没有任何关系，就是看`SQL
Server Management Studio`本身有没有提供这种配置项而已。

所以，如果非要实现这个功能的话，其实也可以。

一个方法是通过编写`SQL Server Management Studio`的插件，说不准可以实现相关功能。 另一个就是不用`SQL Server
Management Studio`管理sqlserver，你自己编写一款类似的软件，然后自己加上这个功能。

 ***本文作者：起于凡而非于凡，本文属 FreeBuf 原创奖励计划，未经许可禁止转载**

