## 一、问题描述

在一次上线时，按照正常流程上线后，观察了线上报文、接口可用率十分钟以上，未出现异常情况，结果在上线一小时后突然收到 jsf
线程池耗尽的报警，并且该应用一共有 30 台机器，只有一台机器出现该问题，迅速下线该机器的 jsf 接口，恢复线上。然后开始排查问题。

![1686713117_6489331dcc17d13771d2a.png!small?1686713118620](https://image.3001.net/images/20230614/1686713117_6489331dcc17d13771d2a.png!small?1686713118620)

### 报错日志信息：

[WARN]2023-04-10 18:03:34.847 [ - ][]
|[JSF-23002]Task:java.util.concurrent.FutureTask@502cdfa0 has been reject for
ThreadPool exhausted! pool:200, active:200, queue:0, taskcnt:
2159[BusinessPool#:][JSF-SEV-WORKER-225-T-8]

## 二、问题分析

### 1、出现问题原因：

a）因为只有一台机器出现线程池耗尽，其他机器均正常运行。所以第一时间判断是否为有大量流量负载不均衡导致；

b）业务代码存在并发锁；

c）业务代码处理时间较长；

d）访问数据源（如 DB、redis）变慢；

排查接口流量 UMP 监控，按照机器纬度看，发现每个机器流量是均衡的，排除 a) 项；

排查业务量大的接口 UMP KEY 监控，按照机器纬度看，正常机器和异常机器耗时基本一致，并于往常一致，无较大差异，排除 c）项；

排查数据库监控，无慢 sql，读写均无耗时较长的情况，排除 d）项；

 **综上，只剩下 b）项，确认问题原因是代码存在并发锁，故开始排查日志及业务代码。**

### 2、根据已确认的原因排查思路：

1）down 下 dump 文件，发现极多 JSF 线程处于 RUNNABLE 状态，并且堆栈处于 SerializersHelper 类

    
    
    "JSF-BZ-22000-223-T-200" #1251 daemon prio=5 os_prio=0 tid=0x00007fd15005c000 nid=0xef6 in Object.wait（） [0x00007fce287ac000]
       java.lang.Thread.State: RUNNABLE
    	at com.jd.purchase.utils.serializer.helper.SerializersHelper.ofString(SerializersHelper.java:79)
    	at com.jd.ldop.pipe.proxy.OrderMiddlewareCBDExportServiceProxy.getAddress(OrderMiddlewareCBDExportServiceProxy.java:97)
    	at com.jd.ldop.pipe.proxy.OrderMiddlewareCBDExportServiceProxy.findOrder(OrderMiddlewareCBDExportServiceProxy.java:211)
    

根据堆栈信息排查代码，发现代码会初始化一个自定义的序列化工厂类：SerializerFactory

![1686713302_648933d6bc6c267a96395.png!small?1686713303815](https://image.3001.net/images/20230614/1686713302_648933d6bc6c267a96395.png!small?1686713303815)

并且此时初始化时会打印日志：

    
    
    log.info("register: {} , clazz : {}", serializer.getCode（）, serializer.getClass（）.getName（）);
    

故根据此日志关键字排查初始化加载日志，发现正常机器都加载了两个序列化对象，只有出问题的那个机器只加载了这一个序列化对象。

![1686713319_648933e7a257a09207184.png!small?1686713320266](https://image.3001.net/images/20230614/1686713319_648933e7a257a09207184.png!small?1686713320266)

于是问题初步定位到出问题的机器初始化 ProtoStuffSerializer 这个类时失败。

初始化此类时 static 代码块为：

    
    
    static {
        STRATEGY = new DefaultIdStrategy(IdStrategy.DEFAULT_FLAGS);
    }
    

2）开始排查为什么初始化这个类会失败

由于不同机器存在初始化成功和失败的独立性，首先考虑 jar 包是否冲突

a）于是发现这里存在 jar 冲突，但是将冲突 jar 排除后，多次重启机器后发现依然存在此 ProtoStuffSerializer 初始化失败情况。

b）存在死锁，但是正常逻辑下，存在死锁的话，应该所有机器都会存在此类情况，但是此时大概只有 5% 的几率出现死锁，并且排查 jstack 发现 200
个线程都卡在获取 ProtoStuffSerializer。

> 山重水尽疑无路 柳暗花明又一村

### 3、找到问题

此时排除了所有没可能的选项，剩下一个可能性再低也是正确选项。

如果存在死锁情况的话，那 jstack 的线程堆栈信息肯定会报出来，于是根据 jstack 线程信息逐个排查每一个线程。

最后发现下面这个线程的堆栈：

    
    
    "jcase-jmq-reporter-t-0" #1010 daemon prio=5 os_prio=0 tid=0x00007fd258004800 nid=0x9ba in Object.wait（） [0x00007fd10fffd000]
       java.lang.Thread.State: RUNNABLE
    	at io.protostuff.runtime.RuntimeEnv.<clinit>(RuntimeEnv.java:229)
    	at io.protostuff.runtime.IdStrategy.<clinit>(IdStrategy.java:53)
    	at io.protostuff.runtime.ExplicitIdStrategy$Registry.<init>(ExplicitIdStrategy.java:67)
    	at com.jd.tp.jcase.util.RecordSerializers$ProtostuffIdRegistry.<init>(RecordSerializers.java:108)
    	at com.jd.tp.jcase.util.RecordSerializers.<clinit>(RecordSerializers.java:34)
    	at com.jd.tp.jcase.recording.agent.reporter.impl.JmqReporter$ReportRunner.run(JmqReporter.java:106)
    	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
    	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
    	at java.lang.Thread.run(Thread.java:748)
    

发现此线程（in Object.wait（））也依然处于 **等待状态** ，并且此线程的堆栈信息中包含了 protostuff
这个关键字（由于上面线程都等待在初始化 protostuffprotostuff 导致的！）

于是乎开始分析此线程！

从此行栈信息开始排查

    
    
    at com.jd.tp.jcase.recording.agent.reporter.impl.JmqReporter$ReportRunner.run(JmqReporter.java:106)
    

xml 中存在以下 bean：

    
    
    <bean id="jcaseJmqReporter" class="com.jd.tp.jcase.recording.agent.reporter.impl.JmqReporter" init-method="start" destroy-method="stop">
        <constructor-arg name="name" value="jmq"/>
        <constructor-arg name="recorder" ref="jcaseRecorder"/>
        <constructor-arg name="topic" value="${jmq.topic.ldopjcasereporter}"/>
        <constructor-arg name="producer" ref="jcaseJmqProducer"/>
        <property name="config" ref="jcaseConfig"/>
    </bean>
    

发现以下代码符合堆栈信息：

![1686713334_648933f69cf0fb2785a14.png!small?1686713335496](https://image.3001.net/images/20230614/1686713334_648933f69cf0fb2785a14.png!small?1686713335496)

根据此线程的堆栈信息逐行排查代码，发现该线程执行 JmqReporter.run 方法时，会初始化 RecordSerializers 类；并在
RecordSerializers 中的静态代码块会执行如下代码：

    
    
    RecordSerializers.ProtostuffIdRegistry registry = new RecordSerializers.ProtostuffIdRegistry（）;
    

于是执行这个类的无参构造时会 new 出类变量：

![1686713344_6489340051046f8dd3dd6.png!small?1686713345042](https://image.3001.net/images/20230614/1686713344_6489340051046f8dd3dd6.png!small?1686713345042)

于是线程开始初始化 ExplicitIdStrategy 这个类：

![1686713381_6489342531683ffee0baf.png!small?1686713382357](https://image.3001.net/images/20230614/1686713381_6489342531683ffee0baf.png!small?1686713382357)

开始执行父类的有参构造：

![1686713393_64893431052a3b75083ce.png!small?1686713393976](https://image.3001.net/images/20230614/1686713393_64893431052a3b75083ce.png!small?1686713393976)

于是开始初始化 IdStrategy 类，并且执行 IdStrategy 类的 static 静态代码块：

![1686713402_6489343a52366183eae62.png!small?1686713403151](https://image.3001.net/images/20230614/1686713402_6489343a52366183eae62.png!small?1686713403151)

于是此处开始初始化 RuntimeEnv，并且执行 RuntimeEnv 的静态代码块；线程堆栈信息就显示等待在此类了，

排查 RuntimeEnv 的 static 代码块时发现存在和上一个线程使用了相同的类：

    
    
    new DefaultIdStrategy（）;
    

> 类加载的问题？

首次应该怀疑是类加载的问题，因为除了两百个线程停留在加载 protostuffprotostuff（初始化有 new
DefaultIdStrategy（）的代码）这个类上，此线程也处于等待状态，并且也在加载 DefaultIdStrategy（）的类上。

然后再分析一下这个线程的堆栈信息。

    
    
    "jcase-jmq-reporter-t-0" #1010 daemon prio=5 os_prio=0 tid=0x00007fd258004800 nid=0x9ba in Object.wait（） [0x00007fd10fffd000]
       java.lang.Thread.State: RUNNABLE
    	at io.protostuff.runtime.RuntimeEnv.<clinit>(RuntimeEnv.java:229)
    	at io.protostuff.runtime.IdStrategy.<clinit>(IdStrategy.java:53)
    	at io.protostuff.runtime.ExplicitIdStrategy$Registry.<init>(ExplicitIdStrategy.java:67)
    	at com.jd.tp.jcase.util.RecordSerializers$ProtostuffIdRegistry.<init>(RecordSerializers.java:108)
    	at com.jd.tp.jcase.util.RecordSerializers.<clinit>(RecordSerializers.java:34)
    	at com.jd.tp.jcase.recording.agent.reporter.impl.JmqReporter$ReportRunner.run(JmqReporter.java:106)
    	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
    	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
    	at java.lang.Thread.run(Thread.java:748)
    
       Locked ownable synchronizers:
    	- <0x00000000c81fce28> (a java.util.concurrent.ThreadPoolExecutor$Worker)
    

可以看到在 RuntimeEnv、IdStrategy 后都有 <clinit>；

从名字上来不难猜到是正在做类的初始化，那我们先来了解下类的初始化过程。

#### 类的初始化过程

当我们第一次主动调用某个类的静态方法就会触发这个类的初始化，当然还有其他的触发情况，类的初始化说白了就是在类加载起来之后，在某个合适的时机执行这个类的
clinit 方法。

 **clinit 方法是什么？**

比如我们在类里声明一段 static 代码块，或者有静态属性，javac 会将这些代码都统一放到一个叫做 clinit
的方法里，在类初始化的时候来执行这个方法，但是 JVM
必须要保证这个方法只能被执行一次，如果有其他线程并发调用触发了这个类的多次初始化，那只能让一个线程真正执行 clinit 方法，其他线程都必须等待，当
clinit 方法执行完之后，然后再唤醒其他等待这里的线程继续操作，当然不会再让它们有机会再执行 clinit
方法，因为每个类都有一个状态，这个状态可以保证这一点。

    
    
    public static class ClassState {
        public static final InstanceKlass.ClassState ALLOCATED = new InstanceKlass.ClassState("allocated");
        public static final InstanceKlass.ClassState LOADED = new InstanceKlass.ClassState("loaded");
        public static final InstanceKlass.ClassState LINKED = new InstanceKlass.ClassState("linked");
        public static final InstanceKlass.ClassState BEING_INITIALIZED = new InstanceKlass.ClassState("beingInitialized");
        public static final InstanceKlass.ClassState FULLY_INITIALIZED = new InstanceKlass.ClassState("fullyInitialized");
        public static final InstanceKlass.ClassState INITIALIZATION_ERROR = new InstanceKlass.ClassState("initializationError");
        private String value;
    
        private ClassState(String value) {
            this.value = value;
        }
    
        public String toString（） {
            return this.value;
        }
    }
    

当有个线程正在执行这个类的 clinit 方法的时候，就会设置这个类的状态为 being_initialized，当正常执行完之后就马上设置为
fully_initialized，然后才唤醒其他也在等着对其做初始化的线程继续往下走，在继续走下去之前，会先判断这个类的状态，如果已经是
fully_initialized 了说明有线程已经执行完了 clinit 方法，因此不会再执行 clinit 方法了

#### 类加载的动作

    
    
    void TemplateTable::checkcast（） {
       ...
       call_VM(rax, CAST_FROM_FN_PTR(address, InterpreterRuntime::quicken_io_cc));
       ...
    }
    
    IRT_ENTRY(void, InterpreterRuntime::quicken_io_cc(JavaThread* thread))
     // Force resolving; quicken the bytecode
     int which = get_index_u2(thread, Bytecodes::_checkcast);
     constantPoolOop cpool = method(thread)->constants（）;
     // We'd expect to assert that we're only here to quicken bytecodes, but in a multithreaded
     // program we might have seen an unquick'd bytecode in the interpreter but have another
     // thread quicken the bytecode before we get here.
     // assert( cpool->tag_at(which).is_unresolved_klass（）, "should only come here to quicken bytecodes" );
     klassOop klass = cpool->klass_at(which, CHECK);
     thread->set_vm_result(klass);
    IRT_END
    
    klassOop klass_at(int which, TRAPS) {
       constantPoolHandle h_this(THREAD, this);
       return klass_at_impl(h_this, which, CHECK_NULL);
    }
    
    klassOop constantPoolOopDesc::klass_at_impl(constantPoolHandle this_oop, int which, TRAPS) {
       ...
       klassOop k_oop = SystemDictionary::resolve_or_fail(name, loader, h_prot, true, THREAD);
       ...
    }    
    
    //SystemDictionary::resolve_or_fail最终会调用到下面这个方法
    klassOop SystemDictionary::resolve_instance_class_or_null(Symbol* name, Handle class_loader, Handle protection_domain, TRAPS) {
     ...
     // Class is not in SystemDictionary so we have to do loading.
     // Make sure we are synchronized on the class loader before we proceed
     Handle lockObject = compute_loader_lock_object(class_loader, THREAD);
     check_loader_lock_contention(lockObject, THREAD);
     ObjectLocker ol(lockObject, THREAD, DoObjectLock);
     ...
     //此时会调用ClassLoader.loadClass来加载类了
     ...
    }
    
    Handle SystemDictionary::compute_loader_lock_object(Handle class_loader, TRAPS) {
     // If class_loader is NULL we synchronize on _system_loader_lock_obj
     if (class_loader.is_null（）) {
       return Handle(THREAD, _system_loader_lock_obj);
     } else {
       return class_loader;
     }
    }
    

SystemDictionary::resolve_instance_class_or_null 这个方法非常关键了，在里面我们看到会获取一把锁
ObjectLocker，其相当于我们 java 代码里的 synchronized 关键字，而对象对应的是 lockObject，这个对象是上面的
SystemDictionary::compute_loader_lock_object 方法返回的，从代码可知只要不是
bootstrapClassloader 加载的类就会返回当前 classloader
对象，也就是说当我们在加载一个类的时候其实是会持有当前类加载对象的锁的，在获取了这把锁之后就会调用 ClassLoader.loadClass 来加载类了。

#### 小结

看到这里是否能解释了我们线上为什么会有那么多线程会卡在某一个地方了？因为这个类的状态是 being_initialized，所以只能等了。

这个类加载的锁，不过遗憾的是因为这把锁不是 java 层面来显示加载的，因此我们在 jstack 线程 dump 的输出里居然看不到这把锁的存在。

从 dump 来看确实是死锁了，那这个场景当时是怎么发生的呢？

![1686713419_6489344b0ba49a6c3892b.png!small?1686713419614](https://image.3001.net/images/20230614/1686713419_6489344b0ba49a6c3892b.png!small?1686713419614)

如图所示，最后 A、B 线程均在等待对方初始化完成，然后 C、D、E 等两百个线程需要使用 ProtoStuffSerializer 时，就在等待 A
线程初始化 ProtoStuffSerializer 完成。因此造成了 JSF 线程池爆满。

    
    
    "JSF-BZ-22000-223-T-1" #980 daemon prio=5 os_prio=0 tid=0x00007fd164002000 nid=0x99a in Object.wait（） [0x00007fd1de8b7000]
       java.lang.Thread.State: RUNNABLE
    	at com.jd.purchase.utils.serializer.impl.ProtoStuffSerializer.<clinit>(ProtoStuffSerializer.java:42)
    	at sun.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
    	at sun.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:62)
    	at sun.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
    	at java.lang.reflect.Constructor.newInstance(Constructor.java:423)
    

只有此线程获取到了 ProtoStuffSerializer 的初始化锁也间接证明了这一点。

## 三、解决方案

了解到是由于 A、B 线程互相争夺对方的初始化锁后，那么为了打破这一点，就让其中某一个线程提前初始化这些类就可以了。

这里选择提前加载这个 bean：初始化业务所使用到的类

<bean
class="com.jd.purchase.utils.serializer.starter.CustomSerializerStarter"/>

## 四、Demo 验证

### Demo 代码：

    
    
    public class JVMTest {
        public static void main(String[] args) {
            new Thread（）{
                public void run（）{
                    B.test（）;
                }
            }.start（）;
    
            new Thread（）{
                public void run（）{
                    A.test（）;
                }
            }.start（）;
        }
    
    }
    class A{
        static{
            int a=0;
            System.out.println(a);
            B.test（）;
        }
        static void test（）{
            System.out.println("调用了A的test方法");
        }
    }
    class B{
        static{
            int b=0;
            System.out.println(b);
            A.test（）;
        }
        static void test（）{
            System.out.println("调用了B的test方法");
        }
    }
    

结果：

![1686713432_648934581e1aa9a1301a8.png!small?1686713432957](https://image.3001.net/images/20230614/1686713432_648934581e1aa9a1301a8.png!small?1686713432957)

### Demo 现象解释

我们 Demo 里的那两个线程，从 dump 来看确实是死锁了，那这个场景当时是怎么发生的呢？

线程 1 首先执行 B.test（），于是会对 B 类做初始化，设置 B 的类状态为 being_initialized，接着去执行 B 的 clinit
方法，但是在 clinit 方法里要去调用 A.test 方法，理论上此时会对 A 做初始化并调用其 test 方法，但是就在设置完 B
的类状态之后，执行其 clinit 里的 A.test 方法之前；

线程 2 却执行了 A.test 方法，此时线程 2 会优先负责对 A 的初始化工作，即设置 A 类的状态为
being_initialized，然后再去执行 A 的 clinit 方法，此时线程 1 发现 A 的类状态是 being_initialized
了，那线程 1 就认为有线程对 A 类正在做初始化，于是就等待了，而线程 2 同样发现 B 的类状态也是
being_initialized，于是也开始等待，这样就形成了两个线程都在等待另一个线程完成初始化的情况，造成了类死锁的现象。

## 五、总结

类加载的死锁很隐蔽了，但是类初始化的死锁更隐蔽，所以大家要谨记在类的初始化代码里产生循环依赖，另外对于 jdk8 的 defalut
特性也要谨慎，因为这会直接触发接口的初始化导致更隐蔽的循环依赖。

## 推荐阅读：

JDK 的 sql
设计不合理导致的驱动类初始化死锁问题：[https://blog.csdn.net/xichenguan/article/details/39578401](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fblog.csdn.net%2Fxichenguan%2Farticle%2Fdetails%2F39578401)

java 虚拟机规范 —
初始化：[https://blog.csdn.net/weixin_38233104/article/details/125251345](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fblog.csdn.net%2Fweixin_38233104%2Farticle%2Fdetails%2F125251345)

JVM
常用命令：[https://zhuanlan.zhihu.com/p/401563061](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fzhuanlan.zhihu.com%2Fp%2F401563061)

> 作者：京东物流 李键屿
>
> 来源：京东云开发者社区

