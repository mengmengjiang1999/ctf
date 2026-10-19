**作者： wh0am1i@知道创宇404实验室**

## 0x01 GeoServer & GeoTools

GeoServer 是一个用 Java 编写的开源软件服务器，允许用户共享和编辑地理空间数据，GeoServer 基于 Spring 开发，使用到了
GeoTools 库。

GeoTools 是一个开源的 Java 库，提供对地理数据空间工具，GeoServer 许多核心功能使用 GeoTools 实现，如：数据读写转换。

## 0x02 漏洞介绍

GeoServer 和 GeoTools 发布了
[CVE-2023-25157](https://github.com/geoserver/geoserver/security/advisories/GHSA-7g5f-wrx8-5ccf)和
[CVE-2023-25158](https://github.com/geotools/geotools/security/advisories/GHSA-99c3-qc2q-p94m)，OGC
查询存在 SQL 注入漏洞。GeoServer 支持 OGC 过滤器表达式语言和 OGC 通用查询语言 (CQL)，主要影响 Web 要素服务 (WFS)
、Web 地图服务 (WMS) 和 用于 ImageMosaic 覆盖的 Web 覆盖服务 (WCS) 协议，已知：

  * PropertyIsLike 与带有字符串字段的任何数据库一起使用时，或者与启用了编码功能的 PostGIS 数据存储一起使用时
  * strEndsWith 启用了编码功能的 PostGIS DataStore 一起使用时
  * strStartsWith 启用了编码功能的 PostGIS DataStore 一起使用时
  * FeatureId 与具有字符串主键列的任何数据库表一起使用并禁用预编译时
  * jsonArrayContains 字符串或 JSON 字段以及 PostGIS 或 Oracle DataStore 一起使用时（仅 GeoServer 2.22.0 以上版本受影响）
  * DWithin 与 Oracle DataStore 一起使用时

对于 GeoTools 在使用 JDBCDataStore 实现执行 OGC 过滤器时存在 SQL 注入漏洞：

  * PropertyIsLike 启用“编码功能”的 PostGIS DataStore 或者任何带有字符串字段的 JDBCDataStore
  * strEndsWith 启用“编码功能”的 PostGIS DataStore
  * strStartsWith 启用“编码功能”的 PostGIS DataStore
  * FeatureId JDBCDataStore禁用预编译并且有字符串主键（Oracle 不受影响，SQL Server 和 MySQL 没有启用预准备语句的设置，PostGIS 则受影响）
  * jsonArrayContains 带有字符串或 JSON 字段的 PostGIS 和 Oracle DataStore
  * DWithin 仅在 Oracle DataStore 中

## 0x03 影响版本

GeoServer <2.21.4，<2.22.2

GeoTools <28.2、<27.4、<26.7、<25.7、<24.7

官方已发布补丁，请及时更新。

## 0x04 环境搭建

在这里使用 [GeoServer 2.21.3](https://geoserver.org/release/2.21.3)，下载完成后解压：

    
    
    unzip geoserver-2.21.3-bin.zip

进入到 `geoserver-2.21.3-bin/bin`目录下，执行启动程序

    
    
    sh startup.sh﻿

![](https://image.3001.net/images/20230703/1688368685_64a2762dcd0b6988f30ef.png!small)

启动成功后，访问 http[:]//x.x.x.x:8080/geoserver/web/ 即可。

![](https://image.3001.net/images/20230703/1688368713_64a2764946f5902316d11.png!small)

使用 Docker 搭建 PostgreSQL

    
    
    docker run -e POSTGRES_PASSWORD=password -d -p 5433:5432  postgres:latest

进入容器，安装 `postgis`拓展

    
    
    apt search postgis
    
    apt install postgis postgresql-14-postgis-3-scripts

`postgresql-14-postgis-3-scripts`要根据你 PostgreSQL 来安装，本次使用到的 PostgreSQL 为
`PostgreSQL 14.1`

此时数据可参考官方文档：<https://docs.geoserver.org/latest/en/user/gettingstarted/postgis-quickstart/index.html>

编辑 `startup.sh`启动脚本添加远程调试参数：

    
    
    exec "${_RUNJAVA}" ${JAVA_OPTS:--DNoJavaOpts -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005} "${MARLIN_ENABLER:--DMarlinDisabled}" "${RENDERER:--DDefaultrenderer}" "-Djetty.base=${GEOSERVER_HOME}" "-DGEOSERVER_DATA_DIR=${GEOSERVER_DATA_DIR}" -Djava.awt.headless=true -DSTOP.PORT=8079 -DSTOP.KEY=geoserver -jar "${GEOSERVER_HOME}/start.jar"

至此环境搭建结束。

## 0x05 漏洞分析

由于存在多个注入点，在这里以 `strStartsWith`作为案例进行分析，将项目导入 IDEA，开启 DEBUG 调试，下断点定位到
`ogr.geotools.jdbc`下的
`getReaderInternal`函数![](https://image.3001.net/images/20230703/1688368771_64a27683509128f482da2.png!small)

在查询之前 `this.getDataStore().getConnection(this.getState());`会执行 `select
now()`判断是否能正常连接数据库。

继续跟进到
`selectSQL`中![](https://image.3001.net/images/20230703/1688368807_64a276a72c56f91253dda.png!small)

在 `selectSQL`函数中 `selectColumns`会对数据库中的字段进行遍历，并拼接出 SQL
语句![](https://image.3001.net/images/20230703/1688368826_64a276ba1fc1ee92fe57a.png!small)

拼接相关函数如下：![](https://image.3001.net/images/20230703/1688368839_64a276c7211f43dce7fe0.png!small)![](https://image.3001.net/images/20230703/1688368859_64a276db8982b06e70338.png!small)![](https://image.3001.net/images/20230703/1688368871_64a276e7aded9ffc85f1c.png!small)

拼接完成后 SQL 语句如下：

    
    
    SELECT "gid","bin",encode(ST_AsEWKB("the_geom"), 'base64') as "the_geom" FROM "public"."nyc_buildings" WHERE

接下来是对
`filter`的处理![](https://image.3001.net/images/20230703/1688368906_64a2770a99fd7448d76f9.png!small)

在 `filter`中将我们输入的 `CQL_FILTER`转换成 SQL 后语句后拼接到
`WHERE`后面![](https://image.3001.net/images/20230703/1688368922_64a2771a30d8020eac22c.png!small)

因此最后拼接出来的 SQL 语句如下：

    
    
    SELECT "gid","bin",encode(ST_AsEWKB("the_geom"), 'base64') as "the_geom" FROM "public"."nyc_buildings" WHERE ("bin"::text LIKE 'x') = true and 1=(SELECT CAST ((SELECT version()) AS INTEGER)) -- %') = true

在 `JDBCFeatureReader`中由 `executeQuery`执行 SQL
语句![](https://image.3001.net/images/20230703/1688368944_64a2773073cce1317c2c1.png!small)

总结一下：`org.geotools.jdbc`下的 `getReaderInternal()`函数对用户输入的查询进出处理，进一步调用
`selectSQL`生成对应数据库的 SQL 查询语句，生成数据库的查询语句后，会对判断是否存在
`CQL_FILTER`查询条件，如果是存在则开始处理用户输入的 `CQL_FILTER`条件，由 `encodeToString(Filter
filter)`将 `CQL_FILTER`转换为 SQL 语句，再由 `FilterToSQL filter`拼接到 `WHETE`后面，最后
`JDBCFeatureReader`的 `this.runQuery`执行带有注入的 SQL 语句，完成注入。

最终的整个漏洞的调用栈如下：

    
    
    <init>:153, JDBCFeatureReader (org.geotools.jdbc)
    getReaderInternal:607, JDBCFeatureSource (org.geotools.jdbc)
    getReaderInternal:218, JDBCFeatureStore (org.geotools.jdbc)
    getReader:636, ContentFeatureSource (org.geotools.data.store)
    features:173, ContentFeatureCollection (org.geotools.data.store)
    features:52, ContentFeatureCollection (org.geotools.data.store)
    features:40, SecuredFeatureCollection (org.geoserver.security.decorators)
    features:75, SecuredSimpleFeatureCollection (org.geoserver.security.decorators)
    features:93, DecoratingSimpleFeatureCollection (org.geotools.feature.collection)
    encode:572, FeatureTransformer$FeatureTranslator (org.geotools.gml.producer)
    parse:1054, TransformerBase$XMLReaderSupport (org.geotools.xml.transform)
    transform:485, TransformerIdentityImpl (org.apache.xalan.transformer)
    run:287, TransformerBase$Task (org.geotools.xml.transform)
    transform:121, TransformerBase (org.geotools.xml.transform)
    transform:103, TransformerBase (org.geotools.xml.transform)
    encode:247, GML2OutputFormat (org.geoserver.wfs.xml)
    write:261, GML2OutputFormat (org.geoserver.wfs.xml)
    write:199, WFSGetFeatureOutputFormat (org.geoserver.wfs)
    response:1018, Dispatcher (org.geoserver.ows)
    handleRequestInternal:272, Dispatcher (org.geoserver.ows)

## 0x06 修复

目前 GeoServer 和 Geotools 官方均已发布修复版本，查看 GeoServer
官方提交的[补丁](https://github.com/geoserver/geoserver/commit/145a8af798590288d270b240235e89c8f0b62e1d)，在
`src/community/jdbcconfig/src/main/java/org/geoserver/jdbcconfig/internal/ConfigDatabase.java`中添加了模块`org.geoserver.jdbcloader.JDBCLoaderProperties`模块用于配置文件
`jdbcconfig/jdbcconfig.properties`中的 JDBCConfig
模块属性字段并更改了构造函数以包含此属性字段。![](https://image.3001.net/images/20230703/1688368971_64a2774b3acfd14038b32.png!small)

还修改了`src/community/jdbcconfig/src/main/java/org/geoserver/jdbcconfig/internal/OracleDialect.java`中的插入语法![](https://image.3001.net/images/20230703/1688368998_64a277667b4b118bef327.png!small)

而在 GeoTools
提交的[补丁](https://github.com/geotools/geotools/commit/64fb4c47f43ca818c2fe96a94651bff1b3b3ed2b)中，修改
`modules/library/jdbc/src/main/java/org/geotools/data/jdbc/FilterToSQL.java`添加了`EscapeSql`模块和
`escapeBackslash`字段对 SQL
注入进行防御![](https://image.3001.net/images/20230703/1688369024_64a27780ac94edd279884.png!small)![](https://image.3001.net/images/20230703/1688369032_64a27788a60e087b72e8d.png!small)![](https://image.3001.net/images/20230703/1688369039_64a2778f22e5f6f41c27a.png!small)

## 0x07References

<https://github.com/murataydemir/CVE-2023-25157-and-CVE-2023-25158>

<https://docs.geoserver.org/latest/en/user/introduction/overview.html>

