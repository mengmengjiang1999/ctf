# Java安全编码之sql注入

阅读量 **295014**

|评论 **3**

发布时间 : 2020-08-06 10:30:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0154166c8cb8f70210.jpg)

作者：maoge@云影实验室

Java安全编码会是一个系列的文章。此文章为该系列的第一篇。

## 1.框架介绍

目前hibernate和mybatis为java项目广泛采用的两个框架。由于hibernate使用方便，以前的项目采用hibernate非常的广泛，但是后面由于hibernate的侵入式特性，后面慢慢被mybatis所取代
。下面我们会以springboot为基础，分别搭建hibernate和mybatis的漏洞环境。

## 2.配置说明

Springboot采用2.3.1.RELEASE，mysql版本为5.7.20。数据库有一张表user_tbl。数据如下：

![](https://p3.ssl.qhimg.com/t0111c84a894aeca295.png)

## 3.Hibernate

Hibernate 是一个开放源代码的对象关系映射框架，它对 JDBC 进行了非常轻量级的对象封装，是一个全自动的 ORM 框架。Hibernate
自动生成 SQL 语句，自动执行。

###  3.1环境搭建

结构如下，ctl为控制层，service为服务层，dao为持久层。为了方便没有按照标准的接口实现，我们只关注漏洞的部分。

![](https://p2.ssl.qhimg.com/t01971a9ae4de933a5c.png)

Beans下User.java对用为user_tbl表结构。

![](https://p3.ssl.qhimg.com/t019eed1dc7a68c6d50.png)

我们使用/inject 接口,p为接受外部的参数，来查询User的列表，使用fastjson来格化式输出。

![](https://p3.ssl.qhimg.com/t012a77e3c3223821a0.png)

我们回到dao层。

####  3.1.1 SQL注入

SQL注入我们使用字符串拼接方式：

![](https://p3.ssl.qhimg.com/t01c2a845bdacf05675.png)

访问<http://localhost:8080/inject?p=m> 直接用sqlmap跑一下：  
  
很容易就注入出数据来了。

#####  3.1.2 Hql注入

HQL（Hibernate Query Language）是hibernate专门用于查询数据的语句，有别于SQL，HQL
更接近于面向对象的思维方式。表名就是对应我们上面的entity配置的。Hql注入利用难度比sql注入利用大，比如一般程序员不会对系统表进行映射，那么通过系统表获取属性的几乎不可能的，同时由于hql对于复杂的语句支持比较差，对攻击者来说需要花费更多时间去构造可用的payload，更多详细的语法可以参考<https://docs.huihoo.com/hibernate/reference-v3_zh-cn/queryhql.html>

![](https://p1.ssl.qhimg.com/t012f8c55e5b6b2d2b6.png)

#####  3.1.3 预编译

我们使用setParameter的方式，也就是我们熟知的预编译的方式。  
Query query = (Query) this.entityManager.createQuery(“from User u where
u.userName like :userName “,User.class);  
query.setParameter(“userName”,”%”+username+”%”);  
访问<http://localhost:8080/inject?p=m> 后得到正常结果

![](https://p0.ssl.qhimg.com/t0195825e2f2fe8a578.png)

执行注入语句  
[http://localhost:8080/inject?p=m’](http://localhost:8080/inject?p=m%E2%80%99)
or ‘1’ like ‘1 返回为空。

![](https://p1.ssl.qhimg.com/t01c0e0d29c711eee5a.png)

我们来看看setParameter的方式到底对我们的sql语句做了什么。我们将断点打至Loader.class的bindPreparedStatement，这样我们可以完整的sql语句。发现通过预编译后，sql变为了select
user0 _.id as id1_0_ , user0 _.password as password2_0_ , user0 _.username as
username3_0_ from user _tbl user0_ where user0_.username like ‘%’’ or ‘’1’’
like ‘’1%’，然后交给hikari处理。发现变成了将我们的单引号变成了两个单引号，也就是说把里面的变为字符串。

![](https://p1.ssl.qhimg.com/t017d2a1c1a73ef3162.png)

将断点断至mysql-connector-java（也就是我们熟知的JDBC驱动包）的ClientPreparedQueryBindings.setString.这里就是参数设置的地方。

![](https://p4.ssl.qhimg.com/t0142c575547698dda7.png)

看一下算法：

    
    
    public void setString(int parameterIndex, String x) {
        if (x == null) {
            setNull(parameterIndex);
        } else {
            int stringLength = x.length();
            if (this.session.getServerSession().isNoBackslashEscapesSet()) {
                // Scan for any nasty chars
    
                boolean needsHexEscape = isEscapeNeededForString(x, stringLength);
    
                if (!needsHexEscape) {
                    StringBuilder quotedString = new StringBuilder(x.length() + 2);
                    quotedString.append('\'');
                    quotedString.append(x);
                    quotedString.append('\'');
    
                    byte[] parameterAsBytes = this.isLoadDataQuery ? StringUtils.getBytes(quotedString.toString())
                            : StringUtils.getBytes(quotedString.toString(), this.charEncoding);
                    setValue(parameterIndex, parameterAsBytes);
    
                } else {
                    byte[] parameterAsBytes = this.isLoadDataQuery ? StringUtils.getBytes(x) : StringUtils.getBytes(x, this.charEncoding);
                    setBytes(parameterIndex, parameterAsBytes);
                }
    
                return;
            }
    
            String parameterAsString = x;
            boolean needsQuoted = true;
    
            if (this.isLoadDataQuery || isEscapeNeededForString(x, stringLength)) {
                needsQuoted = false; // saves an allocation later
    
                StringBuilder buf = new StringBuilder((int) (x.length() * 1.1));
    
                buf.append('\'');
    
                //
                // Note: buf.append(char) is _faster_ than appending in blocks, because the block append requires a System.arraycopy().... go figure...
                //
    
                for (int i = 0; i < stringLength; ++i) {
                    char c = x.charAt(i);
    
                    switch (c) {
                        case 0: /* Must be escaped for 'mysql' */
                            buf.append('\\');
                            buf.append('0');
                            break;
                        case '\n': /* Must be escaped for logs */
                            buf.append('\\');
                            buf.append('n');
                            break;
                        case '\r':
                            buf.append('\\');
                            buf.append('r');
                            break;
                        case '\\':
                            buf.append('\\');
                            buf.append('\\');
                            break;
                        case '\'':
                            buf.append('\\');
                            buf.append('\'');
                            break;
                        case '"': /* Better safe than sorry */
                            if (this.session.getServerSession().useAnsiQuotedIdentifiers()) {
                                buf.append('\\');
                            }
                            buf.append('"');
                            break;
                        case '\032': /* This gives problems on Win32 */
                            buf.append('\\');
                            buf.append('Z');
                            break;
                        case '\u00a5':
                        case '\u20a9':
                            // escape characters interpreted as backslash by mysql
                            if (this.charsetEncoder != null) {
                                CharBuffer cbuf = CharBuffer.allocate(1);
                                ByteBuffer bbuf = ByteBuffer.allocate(1);
                                cbuf.put(c);
                                cbuf.position(0);
                                this.charsetEncoder.encode(cbuf, bbuf, true);
                                if (bbuf.get(0) == '\\') {
                                    buf.append('\\');
                                }
                            }
                            buf.append(c);
                            break;
    
                        default:
                            buf.append(c);
                    }
                }
    
                buf.append('\'');
    
                parameterAsString = buf.toString();
            }
    
            byte[] parameterAsBytes = this.isLoadDataQuery ? StringUtils.getBytes(parameterAsString)
                    : (needsQuoted ? StringUtils.getBytesWrapped(parameterAsString, '\'', '\'', this.charEncoding)
                            : StringUtils.getBytes(parameterAsString, this.charEncoding));
    
            setValue(parameterIndex, parameterAsBytes, MysqlType.VARCHAR);
        }
    }
    

可以看到mysql-connector-java主要是将将我们’转为了’’,对于转义的\会变为\,比如对于这种sql：  
SELECT user0 _.id AS id1_0_ ,user0 _. PASSWORD AS password2_0_ ,user0
_.username AS username3_0_  
FROM user _tbl user0_  
WHERE user0 _.username LIKE ‘%\’ or username = 0x6d #%’  
也会变为：  
SELECT user0_.id AS id1 _0_ ,user0 _. PASSWORD AS password2_0_ ,user0
_.username AS username3_0_ FROM user _tbl user0_  
WHERE user0_.username LIKE ‘%\‘’ or username = 0x6d #%’

有人会说那我们使用select _from user_tbl where id = 1 and user() =
0x726f6f74406c6f63616c686f7374 这种类似的语句，全程没有jdbc里面的危险字符是不是就可以绕过了？mysql-connector-java里面有个非常巧妙的点是，他会根据你传入的类型判断。比如传入的为int类型。就会走setInt。传入的为string就会走setString。所以这段语句还是会被select_
from user_tbl where id = 1 ‘and user() = 0x726f6f74406c6f63616c686f7374’  
我们看到sql预编译的算法也是非常简单。

## 4.Mybatis

MyBatis是一流的持久性框架，支持自定义SQL，存储过程和高级映射。MyBatis可以使用简单的XML或注释进行配置。现在目前国内大部分公司都是采用的MyBatis框架。

###  4.1环境搭建：

下面为我们项目目录结构：

![](https://p3.ssl.qhimg.com/t01d0c598fe1f11dfb9.png)

###  4.2使用#{}的方式

#{}也就是我们熟知的预编译方式。

![](https://p3.ssl.qhimg.com/t016fbfb044d62c8e19.png)

访问<http://localhost:8080/getList?p=m> 后正常的返回：

![](https://p5.ssl.qhimg.com/t01787561c6a6cfc469.png)

使用<http://localhost:8080/getList?p=m>‘ or ‘1’ like ‘1  
结果返回为空。不存在注入。  
我们将断点断在PreparedStatementLogger的invoke方法上面，其实这里就是一个代理方法。这里我们看到完整的sql语句。

![](https://p1.ssl.qhimg.com/t01e3c15cc360fffe9b.png)

同样我们将断点断在：ClientPreparedQueryBindings.setString同样会进去

![](https://p2.ssl.qhimg.com/t0199b762d4e72fe41f.png)

Hibernate和Mybatis的预编译机制是一样的。

###  4.3使用${}的方式

${}的方式也就是mybatis的字符串连接方式。

![](https://p0.ssl.qhimg.com/t011d72b868f8178b62.png)

使用sqlmap很容易就能跑出数据

![](https://p2.ssl.qhimg.com/t01f62ceceaab1ebb43.png)

###  4.4 关于orderBy

之前有听人说order by后面的语句是不会参与预编译？这句话是错误的。Order
by也是会参与预编译的。从我们上面的jdbc的setString算法可以看到，是因为setString会在参数的前后加上’’，变成字符串。导致order
by失去了原本的意义。只能说是预编译方式的order by不适用而已。所以对于这种order by的防御的话建议是直接写死在代码里面。对于order
by方式的注入我们可以通过返回数据的顺序的不同来获取数据。

![](https://p0.ssl.qhimg.com/t0129717d8c15e50f9e.png)

关于useServerPrepStmts其实在只有jdbc在开启了useServerPrepStmts=true的情况下才算是真正的预编译。但是如果是字符串的拼接方式，预编译是没有效果的。从mysql的查询日志就可以开看到。可以看到Prepare的语句。一样是存在sql注入的。

![](https://p2.ssl.qhimg.com/t01d58644c53b4d66eb.png)

我们使用占位符的方式：

![](https://p1.ssl.qhimg.com/t0151c8ab83a200aec4.png)

上面的语句就不存在sql注入了。我想这就是jdbc默认为啥不开启useServerPrepStmts=true的原因吧。

###  4.5 关于慢查询

比如说我们我们有如下语句select _from user_tbl like
‘%’+subsql+’%’,如果前端提交%或者%25(不同控制器处理不同)时候会出现select_ from user_tbl like ‘%%%’
会查询所有字段，导致慢查询。我们可以在上面看到jdbc并不会处理%的情况，在做模糊查询时，在没有必要使用%的情况下，可以建议也屏蔽掉此符号。

## 总结：

在能使用预编译的情况下我们应该要使用预编译。在不能使用预编译的情况下，可以对特定类型做规范，比如传数字的需要规范为Integer,Long等。这样会在进入数据库前会提前抛出异常。或者使用Spring的AOP机制，添加一个前置的fitler，对有害的字符清洗或者过滤。但是这样有点笼统，会对全局参数进行清洗。还有一种比较好的方式是，通过注解的方式，这样会比较方便，可复用性也很好。对不能进行预编译的参数加上过滤有害字符的注解。我们就不在这里做代码的实现，网上有很多可以参考的教程。可以使用Apache
Jakarta Commons提供的很多方便的方法来过滤有害字符。

本文涉及的源码均在<https://github.com/langligelang/dragonfly>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **云影实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/212897](/post/id/212897)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Web安全](/tag/Web安全)
  * [代码审计](/tag/代码审计)

 **+1** __4赞

 __收藏

![](https://p5.ssl.qhimg.com/t012b723966029ed2c4.png) 云影实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

