*****本文原创作者：TopScrew，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

##  **前言**

**Fastjson是一个由阿里巴巴维护的一个json库。它采用一种“假定有序快速匹配”的算法，是号称Java中最快的json库。Fastjson接口简单易用，已经被广泛使用在缓存序列化、协议交互、Web输出、Android客户端等多种应用场景。今天我们就以最详细的姿势，一步步分析一下FastJson的远程命令执行！**

##  **0x01序列化**

先熟悉一下FastJson的用法，毕竟连用法都不会怎么分析漏洞。下面用在最简单的示例快速入门一下FastJson

![image.png](https://image.3001.net/images/20180317/15212993479983.png!small)  

简单创建了一个实体bean,并set了两个属性值。进行简单的序列化，看看序列化后是不是变成了我们想要的东西。至于WriteClassName的作用，序列化时写入类型信息，默认为false。反序列化是需用到。

![image.png](https://image.3001.net/images/20180317/15212993621324.png!small)  

此时，已经非常完美的序列化成了我们常见的json数据。而加了WriteClassName属性的序列化，多了一个@type,也就是我们当时创建的那个实体对象。

##  **0x02反序列化**

反序列化的用法也比较简单，也就是将toJSONString换成parseObject即可。第一个参数是json字符串，第二个参数就是前面说到的@type实体对象。

![image.png](https://image.3001.net/images/20180317/15212993766309.png!small)  

成功的将字符反序列化位了实体对象。  

![image.png](https://image.3001.net/images/20180317/15212993881513.png!small)  

## 0x03静态分析

分析漏洞最好的方式就是看看他到底做了什么防御，从他的补丁入手。

![image.png](https://image.3001.net/images/20180317/15212993999872.png!small)  

![image.png](https://image.3001.net/images/20180317/15212994071744.png!small)  

从更新的补丁来看，官方增加了一个checkAutoType方法，看到check这个词大概就能想到这块估计是是做了一个黑名单。跟进这个方法  

![image.png](https://image.3001.net/images/20180317/1521299415361.png!small)  

发现checkAutoType方法对denyList列表进行了遍历。跟进checkAutoType看一看。  

    
    
    public Class<?> checkAutoType(StringtypeName, Class<?> expectClass) {
    
           if (typeName == null) {
    
               return null;
    
           }
    
     
    
           final String className = typeName.replace('$', '.');
    
     
    
           if (autoTypeSupport || expectClass != null) {
    
               for (int i = 0; i < acceptList.length; ++i) {
    
                    String accept = acceptList[i];
    
                    if (className.startsWith(accept)){
    
                        returnTypeUtils.loadClass(typeName, defaultClassLoader);
    
                    }
    
               }
    
     
    
               for (int i = 0; i < denyList.length; ++i) {
    
                    String deny = denyList[i];
    
                    if (className.startsWith(deny)){
    
                        throw newJSONException("autoType is not support. " + typeName);
    
                    }
    
               }
    
           }
    
     
    
           Class<?> clazz = TypeUtils.getClassFromMapping(typeName);
    
           if (clazz == null) {
    
               clazz = deserializers.findClass(typeName);
    
           }
    
     
    
           if (clazz != null) {
    
               if (expectClass != null && !expectClass.isAssignableFrom(clazz)){
    
                    throw newJSONException("type not match. " + typeName + " -> " +expectClass.getName());
    
               }
    
     
    
               return clazz;
    
           }
    
     
    
           if (!autoTypeSupport) {
    
               for (int i = 0; i < denyList.length; ++i) {
    
                   String deny = denyList[i];
    
                    if (className.startsWith(deny)){
    
                        throw newJSONException("autoType is not support. " + typeName);
    
                    }
    
               }
    
               for (int i = 0; i < acceptList.length; ++i) {
    
                    String accept = acceptList[i];
    
                    if(className.startsWith(accept)) {
    
                        clazz =TypeUtils.loadClass(typeName, defaultClassLoader);
    
     
    
                        if (expectClass != null&& expectClass.isAssignableFrom(clazz)) {
    
                            throw newJSONException("type not match. " + typeName + " -> " +expectClass.getName());
    
                        }
    
                        return clazz;
    
                    }
    
               }
    
           }
    
     
    
           if (autoTypeSupport || expectClass != null) {
    
               clazz = TypeUtils.loadClass(typeName, defaultClassLoader);
    
           }
    
     
    
           if (clazz != null) {
    
     
    
               if (ClassLoader.class.isAssignableFrom(clazz) // classloader is danger
    
                        ||DataSource.class.isAssignableFrom(clazz) // dataSource can load jdbc driver
    
                        ) {
    
                    throw newJSONException("autoType is not support. " + typeName);
    
               }
    
     
    
               if (expectClass != null) {
    
                    if(expectClass.isAssignableFrom(clazz)) {
    
                        return clazz;
    
                    } else {
    
                        throw newJSONException("type not match. " + typeName + " -> " +expectClass.getName());
    
                    }
    
               }
    
           }
    
     
    
           if (!autoTypeSupport) {
    
               throw new JSONException("autoType is not support. " +typeName);
    
           }
    
     
    
           return clazz;
    
        }
    
    }

首先他会先判断expectClass是否为空如果为空的化，就会去检查denyList这个列表。看名字就知道是一个黑名单列表。看看这个列表里都有什么东西。  

![image.png](https://image.3001.net/images/20180317/15212994349008.png!small)  

当我们引入的库是以列表中任何一个字段开头时就报throw newJSONException("autoType is not support. " +
typeName);的异常。再看看网上的poc引入的库com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl。看来当循环到com.sun时就抛出了异常。阻止了对恶意对象反序列化的执行。当然这是知道了网上流传的poc，利用前辈们的poc分析起来就轻松多了。

## 0x05构造poc  

当然引入poc以前，再熟悉json和java的应用。

![image.png](https://image.3001.net/images/20180317/1521299462271.png!small)  

依旧是新建一个实体bean，但是现在要注意两个地方，一个是我设置了两个属性。二是我往无参构造器里写入了一条弹计算器的命令。接下来我们看看会发生什么。  

![image.png](https://image.3001.net/images/20180317/15212994727353.png!small)  

![image.png](https://image.3001.net/images/20180317/15212994812641.png!small)  

神奇的地方发生了，当json反序列化时会自动调用无参构造器里的方法，导致计算器弹出。但是还有一点大家有没有注意到，我上面的json字符串明明有password=123456为什么没有反序列化出来。答案是因为我的PassWord字段设置的是私有属性，所以FastJson无权直接去反序列化私有字段。只是我们构造poc的一点java基础知识。

这已经能执行系统命令了，是不是把我们的实体bean直接传给服务器，服务器就可以让我们为所欲为了呢？当然不是的，因为这个只是我们自己构造的实体bean，只有在自己环境才能认识，除非将实体bean直接上传到服务器。那就有点扯淡了………

言归正传，现在的第一步就是学习java反序列化的思想，想尽办法在jdk和fastjson中，服务器肯定存在的代码中找我们想要的东西。这时就该引出前辈们的poc中的com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl类,那就跟进去看一看

![image.png](https://image.3001.net/images/20180317/15212994917441.png!small)  

getTransletInstance方法生成一个translet类的实例  

![image.png](https://image.3001.net/images/20180317/15212995007099.png!small)  

_bytecodes字节数组又是translet类的实际类定义。这样我们是不是就以其他的方式代替了将恶意类上传到服务器这个不可取的方法了呢。  

    
    
    private void defineTransletClasses()
    
           throws TransformerConfigurationException {
    
     
    
           if (_bytecodes == null) {
    
               ErrorMsg err = new ErrorMsg(ErrorMsg.NO_TRANSLET_CLASS_ERR);
    
               throw new TransformerConfigurationException(err.toString());
    
           }
    
     
    
           TransletClassLoader loader = (TransletClassLoader)
    
               AccessController.doPrivileged(new PrivilegedAction() {
    
                    public Object run() {
    
                        return newTransletClassLoader(ObjectFactory.findClassLoader(),_tfactory.getExternalExtensionsMap());
    
                    }
    
               });
    
           try {
    
               final int classCount = _bytecodes.length;
    
               _class = new Class[classCount];
    
     
    
               if (classCount > 1) {
    
                    _auxClasses = new Hashtable();
    
               }
    
               for (int i = 0; i < classCount; i++) {
    
                    _class[i] =loader.defineClass(_bytecodes[i]);
    
                    final Class superClass =_class[i].getSuperclass();
    
     
    
                    // Check if this is the mainclass
    
                    if(superClass.getName().equals(ABSTRACT_TRANSLET)) {
    
                        _transletIndex = i;
    
                    }
    
                    else {
    
                       _auxClasses.put(_class[i].getName(), _class[i]);
    
                    }
    
               }
    
     
    
               if (_transletIndex < 0) {
    
                    ErrorMsg err= newErrorMsg(ErrorMsg.NO_MAIN_TRANSLET_ERR, _name);
    
                    throw newTransformerConfigurationException(err.toString());
    
               }
    
           }
    
           catch (ClassFormatError e) {
    
               ErrorMsg err = new ErrorMsg(ErrorMsg.TRANSLET_CLASS_ERR, _name);
    
               throw new TransformerConfigurationException(err.toString());
    
           }
    
           catch (LinkageError e) {
    
               ErrorMsg err = new ErrorMsg(ErrorMsg.TRANSLET_OBJECT_ERR, _name);
    
               throw new TransformerConfigurationException(err.toString());
    
           }
    
        }

首先_bytecodes会传入getTransletInstance方法中的defineTransletClasses方法，defineTransletClasses方法会根据_bytecodes字节数组new一个_class，_bytecodes加载到_class中，最后根据_class,用newInstance生成一个java实例。  

![image.png](https://image.3001.net/images/20180317/15212995145243.png!small)  

此时可以看到已经成功生成了我们的恶意代码com.screw.test.Demo.但是还要注意另一个标注点。强制类型转化为AbstractTranslet类，这是就知道为什么构造的恶意代码一定要继承AbstractTranslet类了。

## 0x04障碍解决

现在还有一个问题，怎么去触发getTransletInstance接下来会将大家带入一个好玩的调用链。感觉这个巧妙程度和当时的java反序列化有得一拼。

![image.png](https://image.3001.net/images/20180317/15212995277467.png!small)  

在newTransformer中触发了getTransletInstance方法，那问题又来了怎么触发newTransformer?  

![image.png](https://image.3001.net/images/20180317/15212995383938.png!small)  

getOutputProperties()方法出场了，在return处调用了newTransformer方法。继续寻找getOutputProperties方法。  

![image.png](https://image.3001.net/images/20180317/15212995454759.png!small)  

很快找到了这个_outputProperties属性，只要调用他的get方法是不是就出发了getOutputProperties方法了呢？但是非常遗憾的是_outputPropertie属性前面有一个下划线，调用get方法是触发的是get_
OutputProperties方法，而且这个属性还是一个私有属性，不知道大家还记不记得我前面的实验，FastJson不能直接使用实体bean中的私有方法，没有达到我们的目标怎么办？  

![image.png](https://image.3001.net/images/20180317/15212995556308.png!small)  

JavaBeanDeserializer中的smartMatch方法会将传入的key的_替换为空。  

![image.png](https://image.3001.net/images/20180317/15212995635491.png!small)  

这张是动态调试的结果，很明显key2已经从 **_** OutputProperties变成了OutputProperties。至此所有的阻碍已经去除。  

## 0x05调用链

##
![image.png](https://image.3001.net/images/20180317/15213006274110.png!small)  

## 0x06最终POC

![image.png](https://image.3001.net/images/20180317/1521299611116.png!small)  
恶意类  

![image.png](https://image.3001.net/images/20180317/15212996289561.png!small)  
poc  

这块放出了完整的poc和恶意类可以结合调用链再回顾一下整个的反序列化过程！

##  **总结：**

FastJson虽然被广泛利用但是不知道大家有没有看到,Feature.SupportNonPublicField这个属性就是最后一个坑。他是在1.2.22版本才引入的，在1.2.25版本就被修复了。导致这个漏洞特别的稀少。虽然漏洞没有什么太大的利用价值，但是最重要的是我们学到了大佬的挖洞思路，我想这才是最有价值的东西。

 ***本文原创作者：TopScrew，本文属FreeBuf原创奖励计划，未经许可禁止转载**

