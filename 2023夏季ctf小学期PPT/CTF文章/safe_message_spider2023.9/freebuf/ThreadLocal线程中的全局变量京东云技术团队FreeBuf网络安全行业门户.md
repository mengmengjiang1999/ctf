最近接了一个新需求，业务场景上需要在原有基础上新增2个字段，接口新增参数意味着很多类和方法的逻辑都需要改变，需要先判断是否属于该业务场景，再做对应的逻辑。原本的打算是在入口处新增变量，在操作数据的时候进行逻辑判断将变量进行存储或查询。

如果全链路都变更入参和结构，很明显代码上很不优雅，后续如果还要增加业务场景，又需要再改一遍。如果有一个方法可以传递全局变量，而且仅限于当前线程就好了。

到此，会想到有两种解决方案：之前用的比较少的ThreadLocal或者使用redis缓存。考虑到新增字段都是些增删改查的操作，没有必要存到redis中，故使用ThreadLocal。

##  **一、ThreadLocal定义**

以微服务架构为例，服务提供方在收到调用方的请求后，会把这个请求分配给一个线程进行处理。一般来说，一个请求会一直由同一个线程处理，中间不会切换线程，所以如果有一个线程中共享的变量，可以当全局变量使用。

ThreadLocal实现的就是一个线程中的全局变量，与真正的全局变量的区别在于ThreadLocal的变量是每个线程中的全局变量，也就是说不同线程访问到的值是不一样的。其填充的变量属于当前线程，该变量对于其他线程是隔离的。

由定义可以发现，ThreadLocal有两个特性：每个Thread的变量只能由当前Thread使用；由于其他线程不可访问，则不存在多线程间共享的问题。

##  **二、修饰**

ThreadLocal提供了线程本地的实例，它与普通变量的区别在于，每个使用该变量的线程都会初始化一个完全独立的实例副本。

ThreadLocal变量通常被private
static修饰，这样的好处是当一个线程结束时，它所使用的ThreadLocal实例副本都可被回收，避免重复创建。坏处就是这样做可能正好导致内存泄漏。

##  **三、底层实现**

ThreadLocal最朴素的内部实现是Map<threadlocal,
Object>，这是一个HashMap，又称为ThreadLocalMap。但Java源码并不是Map<threadlocal,
Object>的实现。这是因为如果多个线程访问同一个map，这个map需要是线程安全的，构造比较麻烦。Java采用了更简单粗暴的做法：每个线程都有自己的ThreadLocal专属map，里面可以存放多个ThreadLocal变量，这样就解决了多线程同时操作一个map带来的多线程并发问题。

因为要把ThreadLocal的变量当做全局变量使用，需要把变量与初始化函数写在通用的类中，如DDD领域模型中写在Common模块。

具体的实现如下：

    
    
    public class ThreadLocalUtil {
     
       private static ThreadLocal<Integer> THREAD_LOCAL = new ThreadLocal<>();
    
    
       public static Integer getScene() {
           return THREAD_LOCAL.get();
       }
    
       public static void initScene(Integer scene) {
           if (THREAD_LOCAL == null) {
               THREAD_LOCAL = new ThreadLocal<>();
           }
           THREAD_LOCAL.set(scene);
       }
    
       public static void remove() {
           THREAD_LOCAL.remove();
       }
    }
    

## 四、致命点

上面提到了的ThreadLocal会带来内存泄露的问题，深入分析下：

一个ThreadLocal实例对应当前线程的一个对象实例，如果把ThreadLocal声明为某个类的实例变量不是静态变量，那么每次创建一个该类的实例就会导致一个新的对象实例被创建。而这些被创建的实例是同一个类的实例，于是同一个线程可能会访问到同一个类的不同实例，这即使不会导致错误，也会导致重复创建同样的对象。如果使用static修饰后，只要相应的类没有被垃圾回收掉，那么这个类就会持有相对应的ThreadLocal实例引用。

![2022-05-04-11-52wvVrXL0yDIwRSKg.png](https://image.3001.net/images/20230904/1693791674_64f535ba81275a02a2eec.png!small)

ThreadLocal自身并不存储值，而是作为一个key来让线程从ThreadLocal中获取value。ThreadLocalMap中的key是弱引用，所以jvm在垃圾回收时如果外部没有强引用来引用它，ThreadLocal必然会被回收。但是，作为ThreadLocalMap中的key，ThreadLocal被回收后，ThreadLocalMap就会存在null，但value却不为null。如果当前线程一直不结束或者线程结束后不被你销毁，这会产生内存泄露（已分配空间的堆内存由于某种原因未释放或无法释放导致系统内存浪费或程序运行变慢甚至系统奔溃）。

因此， **key弱引用并不是导致内存泄露的原因，而是因为ThreadLocalMap的生命周期与当前线程一样长，并且没有手动删除对应的value** 。

解决的方法也很简单，只需要打破引用路径中的ThreadLocalMap对对象实例的引用即可。也就是在使用完ThreadLocal之后，必须调用ThreadLocal.remove()。

##  **延伸：**

为什么要将Map中的key设置为弱引用呢？

实际上，设置key为弱引用能预防大多数内存泄露的情况。如果key使用强引用，引用的ThreadLocal对象被回收，但是ThreadLocalMap还持有ThreadLocal的强引用，如果没有手动删除，ThreadLocal不会被回收，也会导致内存泄露。设置为弱引用后，引用的ThreadLocal对象被回收，由于ThreadLocalMap持有ThreadLocal的弱引用，即使没有手动删除，ThreadLocal也会被java
GC回收。value在下一次ThreadLocalMap调用set、get、remove的时候会被清除。

## 参考文章：

https://www.cnblogs.com/tiancai/p/13141234.html?ivk_sa=1024320u

https://last2win.com/2020/09/05/java-threadlocal/

<https://blog.csdn.net/u010445301/article/details/111322569>

> 作者：京东零售 李泽阳
>
> 来源：京东云开发者社区 转载请注明来源

