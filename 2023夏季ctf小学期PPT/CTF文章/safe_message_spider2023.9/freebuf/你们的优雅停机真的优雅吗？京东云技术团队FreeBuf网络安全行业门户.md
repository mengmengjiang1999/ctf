# 1.前言

emm，又又遇到问题啦，现有业务系统应用上线存在 **窗口期**
，不能满足正常任务迭代上线。在非窗口期上线容易导致数据库、mq、jsf等线程中断，进而导致需要手动修单问题。故而通过添加优雅停机功能进行优化，令其在上线前选择优雅停机后，会优先断掉新流量的涌入，并预留一定时间处理现存连接，最后完全下线，可有效扩大上线预留窗口时间并降低上线期间线程中断，进而降低手动修单。可是什么是优雅停机呢？为什么现有的系统技术没有原生的优雅停机机制呢？通过调研整理文章如下。

![1691980302_64d9920e66c1ecb7e04e6.png!small](https://image.3001.net/images/20230814/1691980302_64d9920e66c1ecb7e04e6.png!small)

# 2.何为优雅停机？

  * 优雅停机是指为确保应用关闭时，通知应用进程 **释放** 所占用的资源。
  * 线程池，shutdown（不接受新任务等待处理完）还是shutdownNow（调用Thread.interrupt进行中断）。
  * socket链接，比如：netty、jmq、fmq。（需要着重处理）
  * 告知注册中心快速下线，比如jsf。（需要着重处理）
  * 清理临时文件。
  * 各种堆内堆外内存释放。

总之，进程 **强行终止** 会带来 **数据丢失** 或者终端无法恢复到正常状态，在分布式环境下可能导致数据不一致的情况。

# 3.导致优雅停机不优雅的元凶之-kill命令

  *  **kill指令**

◦ **kill -15** ：kill指令默认就是-15，知识发送一个SIGTERM信号通知进程终止，由进程自行决定怎么做，即 **进程不一定终止**
。一般不直接使用kill -15，不一定能够终止进程。

◦ **kill -9** ：强制终止进程，进程会被立刻终止。kill -9 **过于暴力**
，往往会出现事务执行、业务处理中断的情况，导致数据库中存在脏数据、系统中存在残留文件等情况。如果要使用kill -9，尽量先使用kill
-15给进程一个处理善后的机会。该命令可以模拟一次系统宕机，系统断电等极端情况。

◦ **kill -2** ：类似Ctrl + C退出，会先保存相关数据再终止进程。kill
-2立刻终止正在执行的代码->保存数据->终止进程，只是在进程终止之前会保存相关数据，依然会出现事务执行、业务处理中断的情况，做不到优雅停机。

# 4.引申问题：jvm如何接受处理linux信号量的？

•在jvm启动时就加载了自定义SingalHandler， **关闭** jvm时触发对应的handle。

    
    
    public interface SignalHandler {
        SignalHandler SIG_DFL = new NativeSignalHandler(0L);
        SignalHandler SIG_IGN = new NativeSignalHandler(1L);
     
        void handle(Signal var1);
    }
    class Terminator {
        private static SignalHandler handler = null;
     
        Terminator() {
        }
        //jvm设置SignalHandler，在System.initializeSystemClass中触发
        static void setup() {
            if (handler == null) {
                SignalHandler var0 = new SignalHandler() {
                    public void handle(Signal var1) {
                        Shutdown.exit(var1.getNumber() + 128);//调用Shutdown.exit
                    }
                };
                handler = var0;
     
                try {
                    Signal.handle(new Signal("INT"), var0);//中断时
                } catch (IllegalArgumentException var3) {
                    
                }
     
                try {
                    Signal.handle(new Signal("TERM"), var0);//终止时
                } catch (IllegalArgumentException var2) {
                    
                }
     
            }
        }
    }
    
    

  * **Runtime.addShutdownHook** 。在了解Shutdown.exit之前，先看Runtime.getRuntime().addShutdownHook(shutdownHook)；则是为jvm中增加一个关闭的钩子，当jvm关闭的时候调用。

    
    
    public class Runtime {
        public void addShutdownHook(Thread hook) {
            SecurityManager sm = System.getSecurityManager();
            if (sm != null) {
                sm.checkPermission(new RuntimePermission("shutdownHooks"));
            }
            ApplicationShutdownHooks.add(hook);
        }
    }
    class ApplicationShutdownHooks {
        /* The set of registered hooks */
        private static IdentityHashMap<Thread, Thread> hooks;
        static synchronized void add(Thread hook) {
            if(hooks == null)
                throw new IllegalStateException("Shutdown in progress");
     
            if (hook.isAlive())
                throw new IllegalArgumentException("Hook already running");
     
            if (hooks.containsKey(hook))
                throw new IllegalArgumentException("Hook previously registered");
     
            hooks.put(hook, hook);
        }
    }
    //它含数据结构和逻辑管理虚拟机关闭序列
    class Shutdown {
        /* Shutdown 系列状态*/
        private static final int RUNNING = 0;
        private static final int HOOKS = 1;
        private static final int FINALIZERS = 2;
        private static int state = RUNNING;
        /* 是否应该运行所以finalizers来exit? */
        private static boolean runFinalizersOnExit = false;
        // 系统关闭钩子注册一个预定义的插槽.
        // 关闭钩子的列表如下:
        // (0) Console restore hook
        // (1) Application hooks
        // (2) DeleteOnExit hook
        private static final int MAX_SYSTEM_HOOKS = 10;
        private static final Runnable[] hooks = new Runnable[MAX_SYSTEM_HOOKS];
        // 当前运行关闭钩子的钩子的索引
        private static int currentRunningHook = 0;
        /* 前面的静态字段由这个锁保护 */
        private static class Lock { };
        private static Object lock = new Lock();
     
        /* 为native halt方法提供锁对象 */
        private static Object haltLock = new Lock();
     
        static void add(int slot, boolean registerShutdownInProgress, Runnable hook) {
            synchronized (lock) {
                if (hooks[slot] != null)
                    throw new InternalError("Shutdown hook at slot " + slot + " already registered");
     
                if (!registerShutdownInProgress) {//执行shutdown过程中不添加hook
                    if (state > RUNNING)//如果已经在执行shutdown操作不能添加hook
                        throw new IllegalStateException("Shutdown in progress");
                } else {//如果hooks已经执行完毕不能再添加hook。如果正在执行hooks时，添加的槽点小于当前执行的槽点位置也不能添加
                    if (state > HOOKS || (state == HOOKS && slot <= currentRunningHook))
                        throw new IllegalStateException("Shutdown in progress");
                }
     
                hooks[slot] = hook;
            }
        }
        /* 执行所有注册的hooks
         */
        private static void runHooks() {
            for (int i=0; i < MAX_SYSTEM_HOOKS; i++) {
                try {
                    Runnable hook;
                    synchronized (lock) {
                        // acquire the lock to make sure the hook registered during
                        // shutdown is visible here.
                        currentRunningHook = i;
                        hook = hooks[i];
                    }
                    if (hook != null) hook.run();
                } catch(Throwable t) {
                    if (t instanceof ThreadDeath) {
                        ThreadDeath td = (ThreadDeath)t;
                        throw td;
                    }
                }
            }
        }
        /* 关闭JVM的操作
         */
        static void halt(int status) {
            synchronized (haltLock) {
                halt0(status);
            }
        }
        //JNI方法
        static native void halt0(int status);
        // shutdown的执行顺序：runHooks > runFinalizersOnExit
        private static void sequence() {
            synchronized (lock) {
                /* Guard against the possibility of a daemon thread invoking exit
                 * after DestroyJavaVM initiates the shutdown sequence
                 */
                if (state != HOOKS) return;
            }
            runHooks();
            boolean rfoe;
            synchronized (lock) {
                state = FINALIZERS;
                rfoe = runFinalizersOnExit;
            }
            if (rfoe) runAllFinalizers();
        }
        //Runtime.exit时执行，runHooks > runFinalizersOnExit > halt
        static void exit(int status) {
            boolean runMoreFinalizers = false;
            synchronized (lock) {
                if (status != 0) runFinalizersOnExit = false;
                switch (state) {
                case RUNNING:       /* Initiate shutdown */
                    state = HOOKS;
                    break;
                case HOOKS:         /* Stall and halt */
                    break;
                case FINALIZERS:
                    if (status != 0) {
                        /* Halt immediately on nonzero status */
                        halt(status);
                    } else {
                        /* Compatibility with old behavior:
                         * Run more finalizers and then halt
                         */
                        runMoreFinalizers = runFinalizersOnExit;
                    }
                    break;
                }
            }
            if (runMoreFinalizers) {
                runAllFinalizers();
                halt(status);
            }
            synchronized (Shutdown.class) {
                /* Synchronize on the class object, causing any other thread
                 * that attempts to initiate shutdown to stall indefinitely
                 */
                sequence();
                halt(status);
            }
        }
        //shutdown操作，与exit不同的是不做halt操作(关闭JVM)
        static void shutdown() {
            synchronized (lock) {
                switch (state) {
                case RUNNING:       /* Initiate shutdown */
                    state = HOOKS;
                    break;
                case HOOKS:         /* Stall and then return */
                case FINALIZERS:
                    break;
                }
            }
            synchronized (Shutdown.class) {
                sequence();
            }
        }
    }
    
    

# 5.Spring 中是如何实现优雅停机的？

  * 以 **Spring3.2.12** 在spring中通过ContexClosedEvent事件来触发一些动作，主要通过LifecycleProcessor.onClose来做stopBeans。由此可见spring也基于jvm做了扩展。

    
    
    public abstract class AbstractApplicationContext extends DefaultResourceLoader {
         public void registerShutdownHook() {
              if (this.shutdownHook == null) {
               // No shutdown hook registered yet.
                   this.shutdownHook = new Thread() {
                        @Override
                        public void run() {
                             doClose();
                        }
                   };
               Runtime.getRuntime().addShutdownHook(this.shutdownHook);
              }
     }
         protected void doClose() {
              boolean actuallyClose;
              synchronized (this.activeMonitor) {
              actuallyClose = this.active && !this.closed;
              this.closed = true;
              }
     
              if (actuallyClose) {
                   if (logger.isInfoEnabled()) {
                        logger.info("Closing " + this);
                   }
     
                   LiveBeansView.unregisterApplicationContext(this);
     
                   try {
        //发布应用内的关闭事件
                        publishEvent(new ContextClosedEvent(this));
                   }
                   catch (Throwable ex) {
                        logger.warn("Exception thrown from ApplicationListener handling ContextClosedEvent", ex);
                   }
     
       // 停止所有的Lifecycle beans.
                   try {
                        getLifecycleProcessor().onClose();
                   }
                       catch (Throwable ex) {
                    logger.warn("Exception thrown from LifecycleProcessor on context close", ex);
                   }
     
       // 销毁spring 的 BeanFactory可能会缓存单例的 Bean.
                   destroyBeans();
     
       // 关闭当前应用上下文（BeanFactory）
                   closeBeanFactory();
     
       // 执行子类的关闭逻辑
                   onClose();
     
                   synchronized (this.activeMonitor) {
                        this.active = false;
                   }
              }
         } 
    }
    public interface LifecycleProcessor extends Lifecycle {
     /**
      * Notification of context refresh, e.g. for auto-starting components.
      */
         void onRefresh();
     
     /**
      * Notification of context close phase, e.g. for auto-stopping components.
      */
         void onClose();
    }
    
    

# 6.SpringBoot是如何做到优雅停机的？

  * 优雅停机是springboot的特性之一，在收到终止信号后，不再接受、处理新请求，但会在终止进程之前预留一小段缓冲时间，已完成正在处理的请求。注：优雅停机需要在tomcat的9.0.33及其之后的版本才支持。
  * springboot中有spring-boot-starter-actuator模块提供了一个restful接口，用于优雅停机。执行请求curl -X POST http://127.0.0.1:8088/shutdown。待关闭成功则返回提示。注：线上环境url需要设置权限，可配合spring-security使用火灾nginx限制内网访问。

    
    
    #启用shutdown
    endpoints.shutdown.enabled=true
    #禁用密码验证
    endpoints.shutdown.sensitive=false
    #可统一指定所有endpoints的路径
    management.context-path=/manage
    #指定管理端口和IP
    management.port=8088
    management.address=127.0.0.1
     
    #开启shutdown的安全验证（spring-security）
    endpoints.shutdown.sensitive=true
    #验证用户名
    security.user.name=admin
    #验证密码
    security.user.password=secret
    #角色
    management.security.role=SUPERUSER
    
    

  * springboot的shutdown通过调用AbstractApplicationContext.close实现的。

    
    
    @ConfigurationProperties(
        prefix = "endpoints.shutdown"
    )
    public class ShutdownMvcEndpoint extends EndpointMvcAdapter {
        public ShutdownMvcEndpoint(ShutdownEndpoint delegate) {
            super(delegate);
        }
        //post请求
        @PostMapping(
            produces = {"application/vnd.spring-boot.actuator.v1+json", "application/json"}
        )
        @ResponseBody
        public Object invoke() {
            return !this.getDelegate().isEnabled() ? new ResponseEntity(Collections.singletonMap("message", "This endpoint is disabled"), HttpStatus.NOT_FOUND) : super.invoke();
        }
    }
    @ConfigurationProperties(
        prefix = "endpoints.shutdown"
    )
    public class ShutdownEndpoint extends AbstractEndpoint<Map<String, Object>> implements ApplicationContextAware {
        private static final Map<String, Object> NO_CONTEXT_MESSAGE = Collections.unmodifiableMap(Collections.singletonMap("message", "No context to shutdown."));
        private static final Map<String, Object> SHUTDOWN_MESSAGE = Collections.unmodifiableMap(Collections.singletonMap("message", "Shutting down, bye..."));
        private ConfigurableApplicationContext context;
     
        public ShutdownEndpoint() {
            super("shutdown", true, false);
        }
        //执行关闭
        public Map<String, Object> invoke() {
            if (this.context == null) {
                return NO_CONTEXT_MESSAGE;
            } else {
                boolean var6 = false;
     
                Map var1;
     
                class NamelessClass_1 implements Runnable {
                    NamelessClass_1() {
                    }
     
                    public void run() {
                        try {
                            Thread.sleep(500L);
                        } catch (InterruptedException var2) {
                            Thread.currentThread().interrupt();
                        }
                        //这个调用的就是AbstractApplicationContext.close
                        ShutdownEndpoint.this.context.close();
                    }
                }
     
                try {
                    var6 = true;
                    var1 = SHUTDOWN_MESSAGE;
                    var6 = false;
                } finally {
                    if (var6) {
                        Thread thread = new Thread(new NamelessClass_1());
                        thread.setContextClassLoader(this.getClass().getClassLoader());
                        thread.start();
                    }
                }
     
                Thread thread = new Thread(new NamelessClass_1());
                thread.setContextClassLoader(this.getClass().getClassLoader());
                thread.start();
                return var1;
            }
        }
    }
    
    

# 7.知识拓展之Tomcat和Spring的关系？

通过参与云工厂优雅停机重构发现Tomcat和Spring均存在问题，故而查询探究两者之间。

  * Tomcat和jettey是 **HTTP服务器** 和 **Servlet容器** ，负责给类似Spring这种servlet提供一个运行的环境，其中：Http服务器与Servlet容器的功能界限是：可以把HTTP服务器想象成前台的接待， **负责网络通信和解析请求** ，Servlet容器是业务部门， **负责处理业务请求** 。
  * Tomcat和Servlet作为 **Web服务器** 和 **Servlet容器** 的结合，可以接受 **网络http请求解析** 为Servlet规范的请求对象和响应对象。比如， **HttpServletRequest** 对象是Tomcat提供的，Servlet是规范， **Tomcat** 是实现规范的Servlet容器， **SpringMVC** 是处理Servlet请求的应用，其中DispatcherServlet实现了Servlet接口，Tomcat负责加载和调用DispatcherServlet。同时，DispatcherServlet有自己的容器（SpringMVC）容器，这个容器负责管理SpringMVC相关的bean，比如Controler和ViewResolver等。同时，Spring中还有其他的Bean比如Service和DAO等，这些由全局的Spring IOC容器管理，因此，Spring有两个IOC容器。
  * 如果只是使用spring(不包含springmvc)，那么是tomcat容器解析xml文件，通过反射实例化对应的类，根据这些servlet规范实现类，触发对应的代码处理逻辑，这个时候tomcat负责http报文的解析和servlet调度的工作。
  * 如果使用spring mvc，那么tomcat只是解析http报文，然后将其转发给dispatchsetvlet，然后由springmvc根据其配置，实例对应的类，执行对应的逻辑，然后返回结果给dispatchservlet，最后由它转发给tomcat,由tomcat负责构建http报文数据。

# 8.实战演练

  * mq（jmq、fmq）通过添加hook在停机时调用pause先停止该应用的消费，防止出现上线期间mq中线程池的线程中断的情况发生。

    
    
    /**
     * @ClassName ShutDownHook
     * @Description
     * @Date 2022/10/28 17:47
     **/
    @Component
    @Slf4j
    public class ShutDownHook {
    
        @Value("${shutdown.waitTime:10}")
        private int waitTime;
    
        @Resource
        com.jdjr.fmq.client.consumer.MessageConsumer fmqMessageConsumer;
    
        @Resource
        com.jd.jmq.client.consumer.MessageConsumer jmqMessageConsumer;
    
    
        @PreDestroy
        public void destroyHook() {
            try {
                log.info("ShutDownHook destroy");
    
                jmqMessageConsumer.pause();
                fmqMessageConsumer.pause();
    
                int i = 0;
                while (i < waitTime) {
                    try {
                        Thread.sleep(1000);
                        log.info("距离服务关停还有{}秒", waitTime - i++);
                    } catch (Throwable e) {
                        log.error("异常", e);
                    }
                }
    
            } catch (Throwable e) {
                log.error("异常", e);
            }
    
        }
    }
    
    

  * 在优雅停机时需要先把jsf生产者下线，并预留一定时间消费完毕，行云部署有相关stop.sh脚本，项目中通过在shutdown中编写方法实现。

jsf启停分析：

    
    
    @Component
    @Lazy(value = false)
    public class ShutDown implements ApplicationContextAware {
        private static Logger logger = LoggerFactory.getLogger(ShutDown.class);
    
        @Value("${shutdown.waitTime:60}")
        private int waitTime;
    
        @Resource
        com.jdjr.fmq.client.consumer.MessageConsumer fmqMessageConsumer;
    
        @PostConstruct
        public void init() {
            logger.info("ShutDownHook init");
        }
    
        private ApplicationContext applicationContext = null;
    
        @PreDestroy
        public void destroyHook() {
            try {
                logger.info("ShutDownHook destroy");
                destroyJsfProvider();
                fmqMessageConsumer.pause();
    
                int i = 0;
                while (i < waitTime) {
                    try {
                        Thread.sleep(1000);
                        logger.info("距离服务关停还有{}秒", waitTime - i++);
                    } catch (Throwable e) {
                        logger.error("异常", e);
                    }
                }
    
            } catch (Throwable e) {
                logger.error("异常", e);
            }
    
        }
        private void destroyJsfProvider() {
            logger.info("关闭所有JSF生产者");
            if (null != applicationContext) {
                String[] providerBeanNames = applicationContext.getBeanNamesForType(ProviderBean.class);
                for (String name : providerBeanNames) {
                    try {
                        logger.info("尝试关闭JSF生产者" + name);
                        ProviderBean bean=(ProviderBean)applicationContext.getBean(name);
                        bean.destroy();
                        logger.info("关闭JSF生产者" + name + "成功");
                    } catch (BeanCreationNotAllowedException re){
                        logger.error("JSF生产者" + name + "未初始化，忽略");
                    } catch (Exception e) {
                        logger.error("关闭JSF生产者失败", e);
                    }
                }
            }
            logger.info("所有JSF生产者已关闭");
        }
    
        @Override
        public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
            this.applicationContext = applicationContext;
            ((AbstractApplicationContext)applicationContext).registerShutdownHook();
        }
    
    }
    
    
    

  * absfactory-base-custcenter应用优雅停机出现日志无法打印问题，排查定位发现问题如下：通过本地debug发现优雅停机先销毁logback日志打印线程，导致实际倒计时的日志无法打印。

    
    
    <!--	fix-程序关停时，logback先销毁的问题-->
        <context-param>
            <param-name>logbackDisableServletContainerInitializer</param-name>
            <param-value>true</param-value>
        </context-param>
    
    

# 9.总结

现有的 **springboot**
内置Tomcat能通过配置参数达到优雅停机的效果。但是因为业务系统中的代码中存在多种技术交叉应用，针对Tomcat和springmvc不同的应用确实需要花费时间研究底层原理来编写相关类实现同springboot配置参数托管的效果。

> 作者：京东科技 宋慧超
>
> 来源：京东云开发者社区

