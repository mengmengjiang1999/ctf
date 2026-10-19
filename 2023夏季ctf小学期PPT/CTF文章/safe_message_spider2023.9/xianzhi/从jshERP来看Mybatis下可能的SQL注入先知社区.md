## 前言

这里选择使用[jshERP](https://github.com/jishenghua/jshERP/releases)这个CMS来进行Mybatis下可能存在的SQL注入点进行学习

jshERP：

  * 框架为：springboot
  * 持久化框架：Mybatis-plus
  * 项目管理框架：Maven

## 前置

### Mybatis概述

  * Mybatis是一款优秀的持久层框架。
  * 它支持定制化SQL、存储过程以及高级映射。
  * Mybatis避免了几乎所有的JDBC代码和手动设置参数以及获取结果集。
  * Mybatis可以使用简单的XML或注解来配置和映射原生类型、接口和Java的POJO(Plain Old Java Object，普通老式Java对象)为数据库中的记录。

如何对持久化进行概括？

持久化是将程序数据在持久状态和瞬时状态间转换的机制。

  * 即把数据（如内存中的对象）保存到可永久保存的存储设备中（如磁盘）。持久化的主要应用是将内存中的对象存储在数据库中，或者存储在磁盘文件中、XML数据文件中等等。
  * JDBC就是一种持久化机制。文件IO也是一种持久化机制。

那么为什么需要Mybatis?不能在需要进行JDBC连接的时候，直接进行单独的数据库操作吗？

  * Mybatis就是帮助程序猿将数据存入数据库中 , 和从数据库中取数据 .
  * 传统的jdbc操作 , 有很多重复代码块 .比如 : 数据取出时的封装 , 数据库的建立连接等等… , 通过框架可以减少重复代码,提高开发效率 
  * MyBatis 是一个半自动化的ORM框架 (Object Relationship Mapping) —>对象关系映射
  * MyBatis的优点
  *     * 简单易学：本身就很小且简单。没有任何第三方依赖，最简单安装只要两个jar文件+配置几个sql映射文件就可以了，易于学习，易于使用，通过文档和源代码，可以比较完全的掌握它的设计思路和实现。
    * 灵活：mybatis不会对应用程序或者数据库的现有设计强加任何影响。sql写在xml里，便于统一管理和优化。通过sql语句可以满足操作数据库的所有需求。
    * 解除sql与程序代码的耦合：通过提供DAO层，将业务逻辑和数据访问逻辑分离，使系统的设计更清晰，更易维护，更易单元测试。sql和代码的分离，提高了可维护性。
    * 提供xml标签，支持编写动态sql。

功能架构的解释：

我们把Mybatis的功能架构分为三层：

(1)API接口层：提供给外部使用的接口API，开发人员通过这些本地API来操纵数据库。接口层一接收到调用请求就会调用数据处理层来完成具体的数据处理。

(2)数据处理层：负责具体的SQL查找、SQL解析、SQL执行和执行结果映射处理等。它主要的目的是根据调用的请求完成一次数据库操作。

(3)基础支撑层：负责最基础的功能支撑，包括连接管理、事务管理、配置加载和缓存处理，这些都是共用的东西，将他们抽取出来作为最基础的组件。为上层的数据处理层提供最基础的支撑。

### 示例

简略的分析一下在这个CMS中的Mybatis的一些关键性配置

  1. 在springboot的配置文件`application.properties`中指定了sql语句的一些映射
    
        mybatis-plus.mapper-locations=classpath:./mapper_xml/*.xml
    

这里是使用通配符进行在classpath下的所有sql语句的映射文件的加载

  2. 在mapper_xml文件夹下存在所以的映射文件

![](./img/7028802856577690795.png)

我们关注一下较为简单的`UserMapper.xml`这个有关用户的sql语句调用的映射

![](./img/8423126536037750171.png)

其对应的`namespace`为`com.jsh.erp.datasource.mappers.UserMapper`，也可以将其视为Dao层，Mybatis中主要是通过动态代理对象的方式，在`UserMapper`接口中定义了一些可以调用的接口

![](./img/3888150326976722480.png)

这些方法的的sql语句的实现就是在`xml`文件的映射中

![](./img/3674765090998158495.png)

对于如何执行这个sql语句，从这个CMS举例来说，可以关注他的`controller`层

存在有`UserController#getUserList`方法，能够获取所有用户信息

![](./img/4643328867942346919.png)

这里通过调用`service`层的`UserService#getUser`方法进行sql查询

## SQL注入

### 可能的漏洞点

在mybatis中，只有在`${}`包裹的参数可控才会造成SQL注入

如果使用`#{}`包裹，将会在执行sql语句的时候进行预编译，能够有效的防止sql注入的产生

但是在下面几点情况下，如果使用`#{}`进行参数的包裹，将会出现 **编译出错**
，某些开发者，在出错之后，将会将其改为`${}`包裹避免错误，但是这样造成了sql注入漏洞的产生

在实际开发中，在Mybatis中容易存在sql注入的点在

  1. 模糊查询
    
        select id from users where name like '%#{name}%'
    

如果使用上面的sql语句，将会出现编译出错

我们可以验证一下是否会出现报错：(还是使用CMS)

这里我们可以将`UserMapperEx.xml`中countsByUser方法的sql语句实现中对应的`${}`修改为`#{}`之后运行项目

![](./img/7292004012000967812.png)

![](./img/6764869745446574088.png)

对于这个方法的调用，是通过访问`/user/list`路由，通过`search`get传参

![](./img/3027167887951234408.png)

这里的`userName / loginName`都是为空，所以并不会执行到`like`语句中

如果我们这里传入的是不为空的数据，将会出错

![](./img/2176856399303452852.png)

也可以在控制台中看到日志输出

    
    
    2023/04/11-19:18:55 DEBUG [http-nio-8080-exec-4] com.jsh.erp.datasource.mappers.UserMapperEx.countsByUser - ==>  Preparing: SELECT count(user.id) FROM jsh_user user LEFT JOIN jsh_user_business ub ON user.id = ub.key_id LEFT JOIN jsh_orga_user_rel rel ON rel.tenant_id = 63 AND user.id = rel.user_id AND ifnull(rel.delete_flag, '0') != '1' LEFT JOIN jsh_organization org ON org.tenant_id = 63 AND rel.orga_id = org.id AND ifnull(org.org_stcd, '0') != '5' WHERE user.tenant_id = 63 AND 1 = 1 AND ifnull(user.status, '0') NOT IN ('1', '2') AND user.username LIKE '%?%' AND user.login_name LIKE '%?%' 
       2023/04/11-19:18:55 ERROR [http-nio-8080-exec-4] com.jsh.erp.service.user.UserService - 异常码[300],异常提示[数据查询异常],异常[{}]
       org.mybatis.spring.MyBatisSystemException: nested exception is org.apache.ibatis.type.TypeException: Could not set parameters for mapping: ParameterMapping{property='userName', mode=IN, javaType=class java.lang.Object, jdbcType=null, numericScale=null, resultMapId='null', jdbcTypeName='null', expression='null'}. Cause: org.apache.ibatis.type.TypeException: Error setting non null for parameter #1 with JdbcType null . Try setting a different JdbcType for this parameter or a different configuration property. Cause: org.apache.ibatis.type.TypeException: Error setting non null for parameter #1 with JdbcType null . Try setting a different JdbcType for this parameter or a different configuration property. Cause: java.sql.SQLException: No parameters defined during prepareCall()
        at org.mybatis.spring.MyBatisExceptionTranslator.translateExceptionIfPossible(MyBatisExceptionTranslator.java:77)
        at org.mybatis.spring.SqlSessionTemplate$SqlSessionInterceptor.invoke(SqlSessionTemplate.java:446)
        at com.sun.proxy.$Proxy83.selectOne(Unknown Source)
        at org.mybatis.spring.SqlSessionTemplate.selectOne(SqlSessionTemplate.java:166)
        at com.baomidou.mybatisplus.core.override.PageMapperMethod.execute(PageMapperMethod.java:101)
        at com.baomidou.mybatisplus.core.override.PageMapperProxy.invoke(PageMapperProxy.java:64)
        at com.sun.proxy.$Proxy97.countsByUser(Unknown Source)
        at com.jsh.erp.service.user.UserService.countUser(UserService.java:128)
    

开发者，此时可能会将预编译的写法改为`${}`这样就不会出现错误，而造成了sql注入

  1. 类似的还有`in`关键词之后的传参
    
        select id from users where name in (#{names})
    

  2. `order by`

### 示例

根据上面有关Mybatis可能存在SQL注入的点，我们可以在本CMS中全局搜索这些关键词

![](./img/2183510390813974967.png)

![](./img/8716818349007862444.png)

存在有很多在这些关键词后使用了`${}`的点，当然我们需要保证这些参数是可控的

直接验证SQL注入漏洞

![](./img/2073241092604312735.png)

在控制台中可以看到具体的sql语句

![](./img/1790515076660933921.png)

进行延时注入

### 修复方式

  1. 模糊匹配
    
        select id from users where name like concat('%', #{name}, '%')
    

  2. `in`之后的参数
    
        select id from users where name in
    <foreach collection="names" item="item" open="("separatosr="," close=")">
    #{names}
    </foreach>
    

## 总结

这里通过使用一个CMS来举例说明了在Mybatis持久化框架中SQL注入的寻找思路

