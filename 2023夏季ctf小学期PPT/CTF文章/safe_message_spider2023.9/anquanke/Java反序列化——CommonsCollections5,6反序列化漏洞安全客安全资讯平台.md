# Java反序列化——Commons Collections5,6反序列化漏洞

阅读量 **220202**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-07-10 15:00:03

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t014c6af71886c98ee7.jpg)

最新一直在做java的代码审计

无目的的挖洞让人好疲惫

为了让自己不能闲下来

不挖的时候觉得学习一下java的反序列化也是不错的

那么就从最开始的Commons Collections反序列化来学习

## java的反序列化操作的函数

java有writeObject()函数可以来执行序列化操作

    
    
    public class ser {
        public static void main(String[] args) throws Exception {
            String test = "ckj123";
    
            FileOutputStream fos = new FileOutputStream("ser.txt");
            ObjectOutputStream oos = new ObjectOutputStream(fos);
            oos.writeObject(test);
            oos.close();
    
            FileInputStream fis = new FileInputStream("ser.txt");
            ObjectInputStream ois = new ObjectInputStream(fis);
            Object result = ois.readObject();
            ois.close();
            System.out.println(result);
        }
    }
    

这只是对一个字符串的序列化当然也可以对对象进行序列化

对象需要一个`Serializable`这个接口

    
    
    import java.io.*;
    
    class ckj123 implements Serializable{
        String test = "test";
    }
    
    public class ser {
        public static void main(String[] args) throws Exception {
            ckj123 test = new ckj123();
    
            FileOutputStream fos = new FileOutputStream("ser.txt");
            ObjectOutputStream oos = new ObjectOutputStream(fos);
            oos.writeObject(test);
            oos.close();
    
            FileInputStream fis = new FileInputStream("ser.txt");
            ObjectInputStream ois = new ObjectInputStream(fis);
            ckj123 result = (ckj123)ois.readObject();
            ois.close();
            System.out.println(result.test);
    
        }
    }
    

![](https://p4.ssl.qhimg.com/t01a247d05a759995ba.png)

当然也可以重写readObject

![](https://p4.ssl.qhimg.com/t01aaae42b4e8c73c92.png)

defaultReadObject是反序列化要执行的

就可以让他在反序列化的时候弹一个notepad

## java的反射机制

学习Commons Collections得先了解一下java的反序列化

java里面执行命令的对象是Runtime

    
    
    public class cmd {
        public static void main(String[] args) throws Exception {
            Runtime runtime = Runtime.getRuntime();
            runtime.exec("notepad.exe");
        }
    }
    

![](https://p0.ssl.qhimg.com/t0140d0d8a0a83ffc1f.png)

就会跳出来一个记事本

这样也可以通过java的反射机制来执行

    
    
    import java.lang.reflect.Method;
    
    public class cmd {
        public static void main(String[] args) throws Exception {
            Runtime runtime = Runtime.getRuntime();
            Class cls = runtime.getClass();
            Method method = cls.getMethod("exec", String.class);
            method.invoke(runtime,"notepad.exe");
        }
    }
    

![](https://p5.ssl.qhimg.com/t0165de9ea0071842aa.png)

也可以通过两次反射来实现

    
    
    import java.lang.reflect.Method;
    
    public class cmd {
        public static void main(String[] args) throws Exception {
            Object runtime = Class.forName("java.lang.Runtime").getMethod("getRuntime",new Class[]{}).invoke(null);
            Class.forName("java.lang.Runtime").getMethod("exec",String.class).invoke(runtime,"notepad.exe");
        }
    }
    

![](https://p0.ssl.qhimg.com/t01d6bdac475b947073.png)

    
    
    getMethod("方法","方法类型");
    invoke("对象实例"，"参数");
    

这样就可以任意命令执行了

## Commons Collections

Commons Collections中刚好使用了一个反射

不过他把他们封装了一下

成为了一个对象

其中最重要的一个函数

    
    
        public O transform(final Object input) {
            if (input == null) {
                return null;
            }
            try {
                final Class<?> cls = input.getClass();
                final Method method = cls.getMethod(iMethodName, iParamTypes);
                return (O) method.invoke(input, iArgs);
            } catch (final NoSuchMethodException ex) {
                throw new FunctorException("InvokerTransformer: The method '" + iMethodName + "' on '" +
                                           input.getClass() + "' does not exist");
            } catch (final IllegalAccessException ex) {
                throw new FunctorException("InvokerTransformer: The method '" + iMethodName + "' on '" +
                                           input.getClass() + "' cannot be accessed");
            } catch (final InvocationTargetException ex) {
                throw new FunctorException("InvokerTransformer: The method '" + iMethodName + "' on '" +
                                           input.getClass() + "' threw an exception", ex);
            }
        }
    

可以发现`getMethod`和`invoke`两个函数都齐了

只需要`iMethodName`, `iParamTypes`, `iArgs`三个参数就行了

他的另外一个函数

![](https://p5.ssl.qhimg.com/t018f9db5edac3756c8.png)

刚刚好可以给这三个赋值了

那么来试一下

    
    
    public class test {
        public static void main(String[] args) throws Exception {
            InvokerTransformer invokerTransformer = new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{new String("notepad.exe")});
            Object result = invokerTransformer.transform(Runtime.getRuntime()) ;
        }
    }
    

![](https://p5.ssl.qhimg.com/dm/1024_191_/t01b8300de139310006.png)

都在了=。=

## 命令执行

看完上面的感觉和反序列化没什么关系呀

在mac上测试的时候发现只有Commons Collections 5 和 Commons Collections 6可以

可能是jdk1.8的原因

###  Commons Collections 5

![](https://p0.ssl.qhimg.com/t01b8af06dc6dd6dd8f.png)

`ChainedTransformer`的transformer可以调用每一个`transformer`的`transform`函数

然后就可以用`InvokerTransformer`构造一个利用链

![](https://p0.ssl.qhimg.com/dm/1024_331_/t01cd5d581b8809fcfe.png)

Lazymap在每一次调用get的时候都会调用transform函数调用ChainedTransformer的transform

![](https://p3.ssl.qhimg.com/t01075a4790c828c49b.png)

factory通过初始化Lazymap的时候赋值了

![](https://upload-images.jianshu.io/upload_images/9653874-b28f68d438310813.png)

![](https://p4.ssl.qhimg.com/t015794363f6f640f24.png)

TiedMapEntry的getValue函数中使用了get函数就可以调用LazyMap

![](https://p1.ssl.qhimg.com/t01dd1ad0cc786f0fa1.png)

TiedMapEntry的tostring函数又会调用getvalue

![](https://p4.ssl.qhimg.com/t01df11fbf5d79a846a.png)

![](https://p4.ssl.qhimg.com/t0121eeb947920a52dd.png)

BadAttributeValueExpException的readobject会调用valObj的tostring函数

![](https://p2.ssl.qhimg.com/t0160faf89e6acb8af7.png)

于是有了利用链

    
    
    BadAttributeValueExpException -> readobject
      TiedMapEntry -> tostring
        Lazymap -> get
          ChainedTransformer -> transform
            InvokerTransformer -> transform
    

最后成功执行

    
    
    Runtime runtime = Runtime.getRuntime();
            runtime.exec("calc.exe");
    

###  Commons Collections 6

有了Commons Collections 5的经验Commons Collections 6就好分析很多了

这次不用BadAttributeValueExpException了

跟了一下这次调用的还是

Lazymap -> get

ChainedTransformer -> transform

InvokerTransformer -> transform

不过 TiedMapEntry 使用的就不是tostring了

而是

![](https://p5.ssl.qhimg.com/t01c15797c7daca7a75.png)

![](https://p2.ssl.qhimg.com/t01046b802b57ac0bc8.png)

这样就可以调用Lazymap的get函数了

那么是怎么来的呢=。=

![](https://p2.ssl.qhimg.com/t014e0cc2d9631352d7.png)

hashmap的hash函数调用了key的hashcode

只要key可控就可以

可以找到

![](https://p2.ssl.qhimg.com/t01b6ba59d74b29ab5b.png)

hashmap的put函数

key和value都是传进来的然后是public方法还会调用 hash(key)

完满

这下只要找一个readobject带有put函数的就行了

一个完美的函数hashset

    
    
        private void readObject(java.io.ObjectInputStream s)
            throws java.io.IOException, ClassNotFoundException {
            // Read in any hidden serialization magic
            s.defaultReadObject();
    
            .... ....
            // Create backing HashMap
            map = (((HashSet<?>)this) instanceof LinkedHashSet ?
                   new LinkedHashMap<E,Object>(capacity, loadFactor) :
                   new HashMap<E,Object>(capacity, loadFactor));
    
            // Read in all elements in the proper order.
            for (int i=0; i<size; i++) {
                @SuppressWarnings("unchecked")
                    E e = (E) s.readObject();
                map.put(e, PRESENT);
            }
        }
    

可以看到他的map调用了put函数

而且使用了hashmap

不过进行了判断当前的map是否LinkedHashSet 如果不是就new一个hashmap

![](https://p4.ssl.qhimg.com/t015577760441f69a06.png)

hashset的构造函数就是把map初始化hashmap

那么利用链也有了

    
    
     HashSet -> readobject
      HashMap -> put
       HashMap -> hash
        TiedMapEntry -> hashcode
          Lazymap -> get
           ChainedTransformer -> transform
            InvokerTransformer -> transform
    

get it!

## 后记

![](https://p2.ssl.qhimg.com/t01ed43b2b7b831b406.png)

一直在想为啥传进来字符串foo就变成Runtime了

发现

![](https://p4.ssl.qhimg.com/t014f33c9f6ec296282.png)

原来在这里,不管传什么进来都还给你一样的=。=太坏了

![](https://p4.ssl.qhimg.com/t01a9b77b575f64637c.png)

到最后终于跟通了=。=

真不容易。。。

这个debug的时候还会提前跳出来计算机让我懵逼了一个礼拜

![](https://p4.ssl.qhimg.com/t01360b6b89e6089e75.png)

最后把断点下到这里才行=。=

然而跟的时候他一直走的是下面的else那一段让我懵逼好久

得自己下断点不能跟着跑(牢记牢记@!)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ckj123** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/181722](/post/id/181722)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [代码审计](/tag/代码审计)
  * [Java](/tag/Java)

 **+1** __10赞

 __收藏

![](https://q.qlogo.cn/qqapp/101431079/FFADC1C3225A5C0A7A8080FDD4522FAE/40)
ckj123

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

