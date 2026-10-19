**如今单身的我，现在有大把的时间来修炼我的技术，就像圈内的小伙伴们说：「要女朋友有什么用？这不是影响我写代码吗？」希望我未来能达到「重剑无锋，大巧不工」的境界。**  

下面就给大家分享一下我关于一款功能非常强大的 LogParse 的理解以及如果被黑客入侵如何进行调查取证。

## 一、调查取证面临的问题

Windows 下每个工作站、Domain Controller 等都有
安全、应用程序和系统日志。最重要的是它们包含了所有有价值的安全信息和系统信息，并且会产生 IIS 日志、Exchange
Server（电邮服务组件)、MSSQL Server Log
等，由于这些日志的格式和结构的参差不齐，那如何对它们进行高效的调查取证分析呢？LogParse
横空出世，解决了这一问题。![](https://image.3001.net/images/20190418/1555555963_5cb7e67b2df67.png!small)

## 二、LogParse 概述

![](https://image.3001.net/images/20190418/1555555343_5cb7e40fe8b35.png!small)

![](https://image.3001.net/images/20190418/1555554980_5cb7e2a406552.png!small)

这点英文我就不翻译了吧？！呃呃

##  三、LogParser 结构

> 组成部分有：输入处理器、数据引擎、输出处理器

> 1>输入处理器: 支持本地的日志格式 eg:IIS 日志和 windows 日志 (.evt) 文件。LogParser 还可以读取逗号分隔
> (.CSV) 文件、ODBC 数据库文件、通过回车划分的文本文件；输入处理器把每个日志类型转换成统一格式，这样 LogParser
> 数据引擎就能够像一个数据库处理表格那样处理日志文件。
>
> 2>数据引擎： 在数据引擎处理输入数据并且产生一个结果以后，输出处理器接受并且格式化该结果，并输入到一个表中  
>
>
> 3>输出处理器: 与输入处理器一样，支持许多文件格式，因此你可以任意格式化输出表--->从纯文本文件到 SQL 数据库，再到 XML 文件，so
> LogParser 就具有了适合各种各样的日志分类输出功能。

我用 XMIND 给大家整理一下吧，大体的架构就是这样的

##
****![](https://image.3001.net/images/20190418/1555574125_5cb82d6d7a53f.jpg!small)四、Windows
登录类型****

##
****![](https://image.3001.net/images/20190418/1555575145_5cb83169f0eac.jpg!small)![](https://image.3001.net/images/20190418/1555575207_5cb831a795bda.jpg!small)****五、LogParse
分析语法

###  **1 >显示方式**

-i:EVT 是指定分析的日志，也可分析 CSV 、IISW3C 等日志格式。

![](https://image.3001.net/images/20190418/1555578359_5cb83df728194.jpg!small)

###  2>筛选语句

LogParse 直接 SQL 语句，关于详细的 SQL 可在 CHM 查看。结合分组、提取语句就可以统计出源
IP，时间，用户名；只需要取出关键列进行判断或者比对，就可以从庞大的 windows 安全日志中提取出安全事件发生后想要关联的信息。

![](https://image.3001.net/images/20190418/1555578512_5cb83e90d694c.jpg!small)Output:

![](https://image.3001.net/images/20190418/1555578572_5cb83ecc02524.jpg!small)分组别名显示:

![](https://image.3001.net/images/20190418/1555578605_5cb83eed2a4a1.jpg!small)Output:

![](https://image.3001.net/images/20190418/1555593740_5cb87a0c8ff5a.png!small)

按年月日筛选

使用 timestamp('年-月-日', 'yyyy-MM-dd') 方法

![](https://image.3001.net/images/20190418/1555578757_5cb83f856a9d3.jpg!small)

按时间筛选

![](https://image.3001.net/images/20190418/1555578790_5cb83fa64d554.jpg!small)按照事件
ID 分析

4624 是登录成功的 ID 信息，指定某个关键列中的事件 ID 显示出结果  

![](https://image.3001.net/images/20190418/1555578838_5cb83fd646c8a.jpg!small)

##  六、Analysis log of Windows

###  1>Security Log

筛选出登录成功的事件（4624）中的登录时间、用户名、登录类型、进程名、源 IP。

 **Focus on:**

核查管理员登陆时间段是否为正常时间

木马运行时间是否和管理员登陆时间对应

Code:

![](https://image.3001.net/images/20190418/1555592212_5cb8741492c2f.png!small)

###  2>System Log

Focus on:时间段

服务名、服务路径查询

Code:

![](https://image.3001.net/images/20190418/1555592353_5cb874a18a1a6.png!small)

###  3> Application Log  

Focus on:程序运行时间

![](https://image.3001.net/images/20190418/1555592337_5cb8749132480.png!small)

###  4>分析 IIS 日志

统计 IIS 日志 404 错误的页面

    
    
    Logparser.exe "SELECT distinct count(*) as Times,cs-host as Host,cs-uri-stem as
    
        PageUrl into 'D:\Loginfo\IISLog\error\20100428.log.txt' FROM
    
        D:\Loginfo\IISLog\100428.log where sc-status=404 Group by Host,PageUrl order by
    
        Times desc" -o:tsv

###  5>分析自定义的日志

    
    
    LogParser.exe "select distinct Host, Uid,SessionId, CASE STRLEN(TRIM(AccountId))
    
        WHEN NULL THEN 0 ELSE 1 END as IsLogin into C:\****.txt from
    
        'D:\Loginfo\LogInfo_1004280930.log' where Host >''" -i:TSV -fixedSep:ON
    
        -iHeaderFile D:\Loginfo\PVLogHeadFile\PVLogHeadFile.txt -o:tsv -fileMode:0

-fileMode:0，为 0 表示追加，为 1 表示覆盖原文件

###  6>用 LogParser 导数据到数据库中

(1) 导入到远程数据库存在的表中

    
    
    LogParser.exe "SELECT * FROM 'D:\LogInfo\LogInfo_1001032230.log' TO dbo.[table]"
    
        -o:SQL -server:[server] -driver:"SQL Server" -database:[database]
    
        -username:[username] -password:[password] -i:tsv

(2) 导入到本机数据库存在的表中

    
    
    LogParser.exe "select * into [database].dbo.[table] from
    
        'D:\LogInfo\LogInfo_1001032230.log'" -o:sql -database:[dtabase] -i:tsv
    
        -iCodepage:65001

(3) 导入并创建表

    
    
    LogParser.exe "SELECT * FROM 'D:\LogInfo\LogInfo_1001032230.log' TO dbo.[table]"
    
        -o:SQL -server:[server] -driver:"SQL Server" -database:[database]
    
        -username:[username] -password:[password] -i:tsv -createtable:ON

Note:

(1) 对于已存在的表，需要在前面预留两个字段，LogParser 导入的时候，会把文件名和行号也导入到表中

(2)
字段类型，对于已存在的表，里面设置的字段类型必须与要导入的日志文件的类型一一匹配，否则会导入失败，对于创建表的情况，如果需要导入的字段中包含长整型，则导入后的数据也是不对的，创建的表为
int 型，因此建议是手动建表。

###  **7 >C# 调用 LogParser COM**

假设某网站有一模块，被调用成功或失败都会记一笔日志到文本文件中，这样做的目的是需要实时监控失败率。

Note:日志是以一定的格式记录的，第一列表示。时间，第二列为 描述，包含调用参数，调用是否成功等信息

    
    
    using System;
    
    using LogQuery = MSUtil.LogQueryClass;
    
    using LogRecordSet = MSUtil.ILogRecordset;
    
    using TsvInputFormat = MSUtil.COMTSVInputContextClass;
    
    using System.Windows.Forms;
    
    class LogParserUtil
    
    {
    /* / <summary> */
    
    /* / 计算失败率 */
    
    /* / </summary> */
    
    	public double GetFailureRate( string headerFile, string logPath )
    
    	{
    		double failureRate = 1;
    
    		LogQuery oLogQuery = new LogQuery();
    
    		TsvInputFormat oTsvInputFormat = new TsvInputFormat();
    
    		oTsvInputFormat.iHeaderFile = headerFile;
    
    		LogRecordSet oRecordSet;
    
    		double totalQty = 0;
    
    		double successQty = 0;
    
    		string query = string.Empty;
    
    		try
    
    		{
    			#region 所有的条数--Log 中包含「reccode=」的行数
    
    			query = @ "select count(*) as qty from '" + logPath + "' where loginfo
    
    like '%reccode=%'";
    
    			oRecordSet = oLogQuery.Execute( query, oTsvInputFormat );
    
    			if ( !oRecordSet.atEnd() )
    
    			{
    				totalQty = (int) oRecordSet.getRecord().getValue( "qty" );
    			}
    
    			oRecordSet.close();
    
    			#endregion
    
    			#region 成功的条数--Log 中包含「reccode=0,」的行数
    
    			query = @ "select count(*) as qty from '" + logPath + "' where loginfo
    
    like '%reccode=0,%'";
    
    			oRecordSet = oLogQuery.Execute( query, oTsvInputFormat );
    
    			if ( !oRecordSet.atEnd() )
    
    			{
    				successQty = (int) oRecordSet.getRecord().getValue( "qty" );
    			}
    
    			oRecordSet.close();
    
    			#endregion
    
    			if ( totalQty > 0 && totalQty >= successQty )
    
    			{
    				failureRate = Math.Round( (1 - successQty / totalQty) * 100, 2 );
    			}
    		}
    
    		catch ( Exception ex )
    
    		{
    			MessageBox.Show( ex.ToString() );
    		}
    
    		return(failureRate);
    	}
    
    
    /* / <summary> */
    
    /* / 计算调用平均时间 */
    
    /* / </summary> */
    
    	public double GetAvgLockSec( string headerFile, string logPath )
    
    	{
    		double avgLockSec = 0;
    
    		LogQuery oLogQuery = new LogQuery();
    
    		TsvInputFormat oTsvInputFormat = new TsvInputFormat();
    
    		oTsvInputFormat.iHeaderFile = headerFile;
    
    		try
    
    		{
    			string query = "select
    
    AVG(TO_REAL(EXTRACT_VALUE(EXTRACT_TOKEN(SUBSTR(loginfo,INDEX_OF(loginfo,'lockse
    
    c=')),0,' '),'locksec'))) as avglocksec from '" + logPath + "' where loginfo like
    
    '%locksec=%'";
    
    			LogRecordSet oRecordSet = oRecordSet = oLogQuery.Execute( query,
    
    										  oTsvInputFormat );
    
    			if ( !oRecordSet.atEnd() )
    
    			{
    				double item = 0;
    
    				if ( !oRecordSet.getRecord().isNull( 0 ) )
    
    				{
    					item =
    
    						double.Parse( oRecordSet.getRecord().getValue( 0 ).ToString() );
    				}
    
    				avgLockSec = Math.Round( item, 2 );
    			}
    
    			oRecordSet.close();
    		}
    
    		catch ( Exception ex )
    
    		{
    			MessageBox.Show( ex.ToString() );
    		}
    
    		return(avgLockSec);
    	}
    }

##  七、被黑分析思路  

###  1 Focus on  

1>入侵事件段

2>IP（外网 IP--->攻击者 IP、监控--->有被远控的内网 IP）

3>查看登录成功类型、尝试登录类型

4>net user 查看是否添加新的用户

5>进程和资源分析

![](https://image.3001.net/images/20190418/1555594423_5cb87cb755d78.png!small)Note:假如资源消耗很大，极有可能被植入挖矿程序。

6>开放端口分析 建议关闭 135、139、445、等端口

###  2 辅助分析

1>当已经发现 Webshell、远控木马的创建时间

2>然后搜索注册表信息，通过注册表信息获取注册表 键值 创建时间和同时创建的文件  

3>结合文件创建的时间、注册表键值创建时间找出的新文件时间。整合分析系统日志，将整个行为关联起来，进行精确取证

![](https://image.3001.net/images/20190418/1555593087_5cb8777f73cae.png!small)

4>利用 Volatility 进行内存取证，分析入侵攻击痕迹，包括网络连接、进程、服务、驱动模块、DLL、handles、检测进程注入、检测
Meterpreter、cmd 历史命令、IE 浏览器历史记录、启动项、用户、shimcache、userassist、部分 rootkit
隐藏文件、cmdliner 等。

5>列出了当前活动的登录会话 (如果指定-p 选项，则列出每个会话中运行的进程)

![](https://image.3001.net/images/20190418/1555595034_5cb87f1a9df86.png!small)

***本文原创作者：星光111，本文属FreeBuf原创奖励计划，未经许可禁止转载**

