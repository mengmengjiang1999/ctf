## 1、环境搭建

> 项目地址：<https://gitee.com/project_team/Tmall_demo.git>

项目基于springboot结构非常简单，修改application.properties数据库配置文件，之后运行`TmallSpringBootApplication`

### 1.2 踩坑记录

在使用高版本mysql时，登录会报如下错误

`Error querying database. Cause: java.sql.SQLSyntaxErrorException: Expression
#1 of ORDER BY clause is not in GROUP BY clause and contains nonaggregated
column 'tmalldemodb.category.category_id' which is not functionally dependent
on columns in GROUP BY clause; this is incompatible with
sql_mode=only_full_group_by`

原因是因为在mysql 5.7+中 默认启用了 ONLY_FULL_GROUP_BY ，大概就是一种严谨的SQL模式，类似于Oracel那些Group
by语句，就是你查询那些字段，group by的时候也要写上哪些字段。

运行该sql语句设置，如果未设置成功，需要更改为低版本mysql(5.7版本)

`set @@global.sql_mode
='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';`

之后重启一下sprignboot即可正常登录

## 2、代码审计

### 2.1 权限绕过任意文件上传

先直接看一下fliter，发现是用contains来判断url该不该放行，所以我们只需要构造类似`/admin/login/../../xxx`
这种即可绕过filter

![](./img/4588148500014984907.png)

再去找一处接口验证，发现一处文件上传接口，并未做任何限制，构造请求

![](./img/6814151037855887506.png)

成功上传

![](./img/7468748402973987716.png)

访问也OK

![](./img/1057536287593236293.png)

这里也有一处

![](./img/8668686403647386773.png)

![](./img/4455524693260172462.png)

### 2.2 SQL注入（1）

数据库框架为Mybatis所以我们只需要关注$即可，全局搜索$，之后定位到同名的dao文件

![](./img/8089615149610410365.png)

继续跟进，

![](./img/4952711329876072271.png)

继续跟进

![](./img/5093037644709486647.png)

发现第一处调用，但是不可控，跳过  
![](./img/5277721981542817050.png)

第二处调用，很明显可控参数

![](./img/8203993633115539542.png)

![](./img/769211444792720950.png)

构造一下

![](./img/8507403352568667582.png)

![](./img/4362486708846530652.png)

sqlmap也可以出结果  
![](./img/2574258887186995034.png)

### 2.3 SQL注入（2）

![](./img/6070334731812207030.png)

![](./img/9200553751726775633.png)

和先前流程一样，跟进查看调用

![](./img/3787522732955522175.png)

最终在`admin/order` 处发现调用，并且orderUtil可控

![](./img/1430636853604375866.png)

![](./img/4071981613071538688.png)

![](./img/7077870516088346715.png)

其他地方还有三四处，暂时不跟了。

组件看了一下，咋全是新版本

![](./img/743839866123075631.png)

## 总结

用于练手还是相当不错，如有问题，感谢各位师傅指正。

