# **一、开篇背景**

“锁”代表安全。在程序中（这里指java）尤其多线程环境下，有了锁的帮助，会给数据安全带来保障，帮助线程更好的运作，避免竞争和互斥。

锁共有15种算法：乐观锁、悲观锁、自旋锁、重入锁、读写锁、公平锁、非公平锁、共享锁、独占锁、重量级锁、轻量级锁、偏向锁、分段锁、互斥锁、同步锁....一口气输出真的累，谁记这个啊。我们要吃现成的。ok，上面的一大堆在咱java里就是：

 **ReentrantLock，Synchronieed，ReentrantReadWriteLock，Atomic
全家桶，Concurrent全家桶**

已上再并发场景中都是被常常用到，想必大家都已炉火纯青般.....巴特！我们还有后浪同学们可能不熟悉，那我在这里聊下锁的用法和使用场景。

###  **ReentrantLock：**

ReentrantLock是一个互斥的可重入锁。互斥的意思就是排他，独占，只能一个线程获取到锁。可重入的意思就是单个线程可以多次重复获取锁。它实现了悲观锁、重入锁、独占锁、非公平锁和互斥锁的算法。

 **常用方法**

方法名| 说明| 异常  
---|---|---  
lock()| 一直阻塞获取锁，直到获取成功| 无  
lockInterruptibly()| 尝试获取锁，直到获取锁或者线程被中断| InterruptedException  
tryLock()| 尝试获取空闲的锁，获取成功返回true，获取失败返回false，不会阻塞，立即返回| 无  
tryLock(long time, TimeUnit unit)| 尝试在time时间内获取空闲的锁，在等待时间内可以被中断|
InterruptedException  
unLock()| 释放锁| 无  
newCondition()| 返回当前锁的一个condition实例，可以唤醒或等待线程 | 无  
  
  

 **场景**

递归嵌套的业务场景中，例如一棵树型的业务逻辑，方法有嵌套和调用，这时候我从外层加锁后，在递归遍历多次，每次都要是同一把锁，并且递归到其他层级时锁还不能失效。这个时候就可以使用重入锁了。江湖上还有个花名，叫递归锁。

###  **Synchronized** ：

Synchronized是悲观锁，默认是偏向锁，解锁失败后会升级为轻量级锁，当竞争继续加剧，进入CAS自旋10次后会升级为重量级锁。它实现了悲观锁、重入锁（用关键字修饰方法或代码段时）、独占锁，非公平锁、轻量级锁、重量级锁、偏向锁和同步锁算法。

 **使用方法**

使用场景| 说明  
---|---  
修饰方法| public synchronized void someMethod() { // 方法体 }  
修饰代码块| public void someMethod() { synchronized (lockObject) { // 临界区代码 } }  
修饰静态方法| public static synchronized void someStaticMethod() { // 方法体 }  
修饰类| public class MyClass { public void method1() {
synchronized(MyClass.class) { // 同步代码块 } } public synchronized void method2()
{ // 同步方法 } }  
  
  

 **场景**

多个线程访问共享变量，为了保证期原子性就可以使用 synchronized
。一个典型的业务场景是银行转账操作。假设有多个用户在同时进行转账操作，需要确保转账过程的原子性和数据的一致性，避免出现重复转账或者转账金额错误的情况。在这种情况下，可以使用
synchronized 关键字来实现同步访问。

###  **ReentrantReadWriteLock** ：

ReentrantReadWriteLock是Java提供的读写锁，它支持多个线程同时读取共享数据，但只允许一个线程进行写操作。
他实现了读写锁和共享锁算法。

  

 **常用方法**

方法| 说明  
---|---  
readLock()| 获取读锁  
writeLock()| 获取写锁  
readLock().lock()| 获取读锁并加锁  
writeLock().lock()| 获取写锁并加锁  
readLock().unlock()| 释放读锁  
writeLock().unlock()| 释放写锁  
newCondition()| 创建与锁相关联的Condition实例，可以唤醒或等待线程  
  
  

**场景**

读写锁应用在读多写少的情况下。读取时不涉及数据修改，写入时需要互斥操作。现在基本所有的号称效率高的准实时数据库都有实现读写锁的算法。

  

###  **Atomic 全家桶** ：

Atomic全家桶 我们已 AtomicInteger
为例。他的特点是实现了CAS算法，同时解决了ABA问题保证原子性。还实现了自旋锁的CLHLock算法，用于CAS比较失败后自旋等待。它实现了乐观锁、自旋锁和轻量级锁的算法。

  

 **常用方法**

方法| 说明  
---|---  
get();| 获取当前AtomicInteger对象的值  
set(int newValue);| 将AtomicInteger对象的值设置为指定的新值  
getAndSet(int newValue)| 将AtomicInteger对象的值设置为指定的新值，并返回设置前的旧值  
incrementAndGet()| 将AtomicInteger对象的值递增1，并返回递增后的新值  
decrementAndGet()| 将AtomicInteger对象的值递减1，并返回递减后的新值  
getAndIncrement()| 先获取AtomicInteger对象的当前值，然后将其递增1，并返回获取的旧值  
getAndDecrement()| 先获取AtomicInteger对象的当前值，然后将其递减1，并返回获取的旧值  
addAndGet(int delta)| 将指定的值加到AtomicInteger对象的当前值上，并返回相加后的结果  
getAndAdd(int delta)| 先获取AtomicInteger对象的当前值，然后将指定的值加到当前值上，并返回获取的旧值  
  
  

 **场景**

用来做计数器非常合适，再有就是线程通讯，数据共享。

  

###  **Concurrent全家桶** ：

Concurrent全家桶我们已ConcurrentHashMap为代表。它实现了分段锁算法（Segmented
Locking）的策略，将整个数据结构划分成多个Segments，每个段都拥有独立的锁。

  

 **常用方法**

方法| 说明  
---|---  
clear();| 移除所有关系  
containsKey(object value);| 检查指定对象是都为表中的键  
containsValue(object value);| 如果此映射将一个或多个健映射到指定值，返回true  
elements()| 返回此表值的枚举  
entrySet()| 返回此映射所包含的映射关系Set视图  
get()| 返回指定键映射到的值没如果此映射不包含该键的映射关系，则返回null  
isEmpty()| 此映射不包含键值则返回true  
keys()| 返回此表中键的枚举  
put(K key, V value)| 指定将健映射到此表中的指定值  
putAll(Map<? extends k, ? extends v> m)| 将指定映射中所有的映射关系复制到此映射中  
size()| 返回此映射中的键值映射关系数  
remove(object key)| 将键从此映射中移除  
replace(K key, V value)| 只有目前将键的条目映射到给定值时，才替换该键的条目  
  
  

 **场景**

在java中ConcurrentHashMap，就是将数据分为16段，每一段都有单独的锁，并且处于不同锁段的数据互不干扰，以此来提升锁的性能。

比如在秒杀扣库存的场景中，现在的库存中有2000个商品，用户可以秒杀。为了防止出现超卖的情况，通常情况下，可以对库存加锁。如果有1W的用户竞争同一把锁，显然系统吞吐量会非常低。为了提升系统性能，我们可以将库存分段，比如：分为100段，这样每段就有20个商品可以参与秒杀。在秒杀的过程中，先把用户id获取hash值，然后除以100取模。模为1的用户访问第1段库存，模为2的用户访问第2段库存，模为3的用户访问第3段库存，后面以此类推，到最后模为100的用户访问第100段库存。如此一来，在多线程环境中，可以大大的减少锁的冲突。

  

#  **二、重点分布式场景redisson和zk的锁的介绍**

###  Redisson

我们日常开发中用用的最多的场景还是分布式锁。提到分布式锁就不可回避Redisson。WHY？
他就是权威好用。使用场景最多没有之一。Redisson官方一共提供了8把锁。我们逐一看一下。

 **1 可重入锁（Reentrant Lock）**

基于Redis的Redisson分布式可重入锁` **RLock**`
Java对象实现了`java.util.concurrent.locks.Lock`接口。同时还提供了异步（ **Async** ）、反射式（
**Reactive** ）和 **RxJava2** 标准的接口。

    
    
    publicstaticvoidmain(String[]args)throwsInterruptedException{// connects to 127.0.0.1:6379 by defaultRedissonClientredisson =Redisson.create();RLocklock =redisson.getLock("lock");lock.lock(2,TimeUnit.SECONDS);Threadt =newThread(){publicvoidrun(){RLocklock1 =redisson.getLock("lock");lock1.lock();lock1.unlock();};};t.start();t.join();redisson.shutdown();}

大家都知道，如果负责储存这个分布式锁的Redisson节点宕机以后，而且这个锁正好处于锁住的状态时，这个锁会出现锁死的状态。为了避免这种情况的发生，Redisson内部提供了一个监控锁的看门狗，它的作用是在Redisson实例被关闭前，不断的延长锁的有效期。默认情况下，看门狗的检查锁的超时时间是
**30秒** 钟，也可以通过修改Config.lockWatchdogTimeout来另行指定。

另外Redisson还通过加锁的方法提供了`leaseTime`的参数来指定加锁的时间。超过这个时间后锁便自动解开了。

    
    
    // 加锁以后10秒钟自动解锁// 无需调用unlock方法手动解锁lock.lock(10,TimeUnit.SECONDS);// 尝试加锁，最多等待100秒，上锁以后10秒自动解锁booleanres =lock.tryLock(100,10,TimeUnit.SECONDS);if(res){try{...}finally{lock.unlock();}}

Redisson同时还为分布式锁提供了异步执行的相关方法：

    
    
    RLocklock =redisson.getLock("anyLock");lock.lockAsync();lock.lockAsync(10,TimeUnit.SECONDS);Future<Boolean>res =lock.tryLockAsync(100,10,TimeUnit.SECONDS);

`RLock`对象完全符合Java的Lock规范。也就是说只有拥有锁的进程才能解锁，其他进程解锁则会抛出`IllegalMonitorStateException`错误。但是如果遇到需要其他进程也能解锁的情况，请使用分布式信号量`Semaphore`对象.

 **2\. 公平锁（Fair Lock）**

基于Redis的Redisson分布式可重入公平锁也是实现了`java.util.concurrent.locks.Lock`接口的一种`RLock`对象。同时还提供了异步（Async）、反射式（Reactive）和RxJava2标准的接口。它保证了当多个Redisson客户端线程同时请求加锁时，优先分配给先发出请求的线程。所有请求线程会在一个队列中排队，当某个线程出现宕机时，Redisson会等待5秒后继续下一个线程，也就是说如果前面有5个线程都处于等待状态，那么后面的线程会等待至少25秒。

    
    
    publicstaticvoidmain(String[]args)throwsInterruptedException{// connects to 127.0.0.1:6379 by defaultRedissonClientredisson =Redisson.create();RLocklock =redisson.getFairLock("test");intsize =10;List<Thread>threads =newArrayList<Thread>();for(inti =0;i <size;i++){finalintj =i;Threadt =newThread(){publicvoidrun(){lock.lock();lock.unlock();};};threads.add(t);}for(Threadthread :threads){thread.start();thread.join(5);}for(Threadthread :threads){thread.join();}}

  

同样也有看门狗机制来防止死锁。另外Redisson还通过加锁的方法提供了`leaseTime`的参数来指定加锁的时间。超过这个时间后锁便自动解开了。

    
    
    // 10秒钟以后自动解锁// 无需调用unlock方法手动解锁fairLock.lock(10,TimeUnit.SECONDS);// 尝试加锁，最多等待100秒，上锁以后10秒自动解锁booleanres =fairLock.tryLock(100,10,TimeUnit.SECONDS);...fairLock.unlock();

Redisson同时还为分布式可重入公平锁提供了异步执行的相关方法：

  

    
    
    RLockfairLock =redisson.getFairLock("anyLock");fairLock.lockAsync();fairLock.lockAsync(10,TimeUnit.SECONDS);Future<Boolean>res =fairLock.tryLockAsync(100,10,TimeUnit.SECONDS);

3\. 联锁（MultiLock）

基于Redis的Redisson分布式联锁` **RedissonMultiLock**`
对象可以将多个`RLock`对象关联为一个联锁，每个`RLock`对象实例可以来自于不同的Redisson实例。

    
    
    publicstaticvoidmain(String[]args)throwsInterruptedException{// connects to 127.0.0.1:6379 by defaultRedissonClientclient =Redisson.create();// 同时加锁：lock1 lock2 lock3 所有的锁都上锁成功才算成功。RLocklock1 =client.getLock("lock1");RLocklock2 =client.getLock("lock2");RLocklock3 =client.getLock("lock3");Threadt =newThread(){publicvoidrun(){RedissonMultiLocklock =newRedissonMultiLock(lock1,lock2,lock3);lock.lock();try{Thread.sleep(3000);}catch(InterruptedExceptione){}lock.unlock();};};t.start();t.join(1000);RedissonMultiLocklock =newRedissonMultiLock(lock1,lock2,lock3);lock.lock();lock.unlock();}

同样也有看门狗机制来防止死锁。另外Redisson还通过加锁的方法提供了`leaseTime`的参数来指定加锁的时间。超过这个时间后锁便自动解开了。

  

    
    
    RedissonMultiLocklock =newRedissonMultiLock(lock1,lock2,lock3);// 给lock1，lock2，lock3加锁，如果没有手动解开的话，10秒钟后将会自动解开lock.lock(10,TimeUnit.SECONDS);// 为加锁等待100秒时间，并在加锁成功10秒钟后自动解开booleanres =lock.tryLock(100,10,TimeUnit.SECONDS);...lock.unlock();

4\. 红锁（RedLock）

基于Redis的Redisson红锁`RedissonRedLock`对象实现了 **Redlock**
介绍的加锁算法。该对象也可以用来将多个`RLock`对象关联为一个红锁，每个`RLock`对象实例可以来自于不同的Redisson实例。

    
    
    RLocklock1 =redissonInstance1.getLock("lock1");RLocklock2 =redissonInstance2.getLock("lock2");RLocklock3 =redissonInstance3.getLock("lock3");RedissonRedLocklock =newRedissonRedLock(lock1,lock2,lock3);// 同时加锁：lock1 lock2 lock3// 红锁在大部分节点上加锁成功就算成功。lock.lock();...lock.unlock();。

  

    
    
    publicstaticvoidmain(String[]args)throwsInterruptedException{// connects to 127.0.0.1:6379 by defaultRedissonClientclient1 =Redisson.create();RedissonClientclient2 =Redisson.create();RLocklock1 =client1.getLock("lock1");RLocklock2 =client1.getLock("lock2");RLocklock3 =client2.getLock("lock3");Threadt1 =newThread(){publicvoidrun(){lock3.lock();};};t1.start();t1.join();Threadt =newThread(){publicvoidrun(){RedissonMultiLocklock =newRedissonRedLock(lock1,lock2,lock3);lock.lock();try{Thread.sleep(3000);}catch(InterruptedExceptione){}lock.unlock();};};t.start();t.join(1000);lock3.forceUnlock();RedissonMultiLocklock =newRedissonRedLock(lock1,lock2,lock3);// 给lock1，lock2，lock3加锁，如果没有手动解开的话，10秒钟后将会自动解开lock.lock(10,TimeUnit.SECONDS);lock.unlock();client1.shutdown();client2.shutdown();}

5\. 读写锁（ReadWriteLock）

基于Redis的Redisson分布式可重入读写锁`RReadWriteLock`Java对象实现了`java.util.concurrent.locks.ReadWriteLock`接口。其中读锁和写锁都继承了RLock接口。

分布式可重入读写锁允许同时有多个读锁和一个写锁处于加锁状态。

    
    
    RReadWriteLockrwlock =redisson.getReadWriteLock("anyRWLock");// 最常见的使用方法rwlock.readLock().lock();// 或rwlock.writeLock().lock();

  

    
    
    publicstaticvoidmain(String[]args)throwsInterruptedException{// connects to 127.0.0.1:6379 by defaultRedissonClientredisson =Redisson.create();finalRReadWriteLocklock =redisson.getReadWriteLock("lock");lock.writeLock().tryLock();Threadt =newThread(){publicvoidrun(){RLockr =lock.readLock();// 10秒钟以后自动解锁，无需调用unlock方法手动解锁//lock.readLock().lock(10, TimeUnit.SECONDS);r.lock();try{Thread.sleep(1000);}catch(InterruptedExceptione){e.printStackTrace();}r.unlock();};};t.start();t.join();lock.writeLock().unlock();t.join();redisson.shutdown();}

6\. 信号量（Semaphore）

基于Redis的Redisson的分布式信号量（Semaphore）Java对象`RSemaphore`采用了与`java.util.concurrent.Semaphore`相似的接口和用法。同时还提供了异步（Async）、反射式（Reactive）和RxJava2标准的接口。

    
    
    publicstaticvoidmain(String[]args)throwsInterruptedException{// connects to 127.0.0.1:6379 by defaultRedissonClientredisson =Redisson.create();RSemaphores =redisson.getSemaphore("test");s.trySetPermits(5);s.acquire(3);Threadt =newThread(){@Overridepublicvoidrun(){RSemaphores =redisson.getSemaphore("test");s.release();s.release();}};t.start();//或s.acquire(4);redisson.shutdown();}

7\. 可过期性信号量（PermitExpirableSemaphore）

基于Redis的Redisson可过期性信号量（PermitExpirableSemaphore）是在`RSemaphore`对象的基础上，为每个信号增加了一个过期时间。每个信号可以通过独立的ID来辨识，释放时只能通过提交这个ID才能释放。它提供了异步（Async）、反射式（Reactive）和RxJava2标准的接口。

    
    
    publicstaticvoidmain(String[]args)throwsInterruptedException{// connects to 127.0.0.1:6379 by defaultRedissonClientredisson =Redisson.create();RPermitExpirableSemaphores =redisson.getPermitExpirableSemaphore("test");s.trySetPermits(1);// 获取一个信号，有效期只有2秒钟。StringpermitId =s.tryAcquire(100,2,TimeUnit.SECONDS);Threadt =newThread(){publicvoidrun(){RPermitExpirableSemaphores =redisson.getPermitExpirableSemaphore("test");try{StringpermitId =s.acquire();s.release(permitId);}catch(InterruptedExceptione){e.printStackTrace();}};};t.start();t.join();s.tryRelease(permitId);}

8\. 闭锁（CountDownLatch）

基于Redisson的Redisson分布式闭锁（ **CountDownLatch**
）Java对象`RCountDownLatch`采用了与`java.util.concurrent.CountDownLatch`相似的接口和用法。

  

    
    
    publicstaticvoidmain(String[]args)throwsInterruptedException{// connects to 127.0.0.1:6379 by defaultRedissonClientredisson =Redisson.create();ExecutorServiceexecutor =Executors.newFixedThreadPool(2);finalRCountDownLatchlatch =redisson.getCountDownLatch("latch1");latch.trySetCount(1);// 在其他线程或其他JVM里executor.execute(newRunnable(){@Overridepublicvoidrun(){latch.countDown();}});executor.execute(newRunnable(){@Overridepublicvoidrun(){try{latch.await(550,TimeUnit.MILLISECONDS);}catch(InterruptedExceptione){e.printStackTrace();}}});executor.shutdown();executor.awaitTermination(10,TimeUnit.SECONDS);}

### Zookeeper

接着我们再看zookeeper的锁。zk不是为高可用性设计的，但它使用` **ZAB**`
协议达到了极高的一致性。所以它经常被选作注册中心、配置中心、分布式锁等场景。它的性能是非常有限的，而且API并不是那么好用。xjjdog倾向于使用基于`
**Raft**` 协议的` **Etcd**` 或者` **Consul**` ，它们更加轻量级一些。我们看一下zk的加锁时序图。

![](https://image.3001.net/images/20230821/1692582663_64e2c3071ca6894e33750.png!small)

  

 **Curator**
是netflix公司开源的一套zookeeper客户端，目前是Apache的顶级项目。与Zookeeper提供的原生客户端相比，Curator的抽象层次更高，简化了Zookeeper客户端的开发量。Curator解决了很多zookeeper客户端非常底层的细节开发工作，包括连接重连、反复注册wathcer和NodeExistsException
异常等。Curator由一系列的模块构成，对于一般开发者而言，常用的是curator-framework和curator-recipes，我们跳过他的其他能力，直接看分布式锁。

1\. （可重入锁 Shared Reentrant Lock）

Shared意味着锁是全局可见的， 客户端都可以请求锁。 Reentrant和JDK的ReentrantLock类似，
意味着同一个客户端在拥有锁的同时，可以多次获取，不会被阻塞。 它是由类InterProcessMutex来实现。
通过acquire获得锁，并提供超时机制。通过release()方法释放锁。 InterProcessMutex 实例可以重用。 Revoking
ZooKeeper recipes wiki定义了可协商的撤销机制。 为了撤销mutex, 调用makeRevocable方法。我们来看示例：

    
    
    publicclassExampleClientThatLocks{privatefinalInterProcessMutexlock;privatefinalFakeLimitedResourceresource;privatefinalStringclientName;publicExampleClientThatLocks(CuratorFrameworkclient,StringlockPath,FakeLimitedResourceresource,StringclientName){this.resource =resource;this.clientName =clientName;lock =newInterProcessMutex(client,lockPath);}publicvoiddoWork(longtime,TimeUnitunit)throwsException{if(!lock.acquire(time,unit)){thrownewIllegalStateException(clientName +" could not acquire the lock");}try{System.out.println(clientName +" has the lock");resource.use();}finally{System.out.println(clientName +" releasing the lock");//释放锁lock.release();}}}

 **2.** 不可重入锁（Shared Lock）

使用InterProcessSemaphoreMutex，调用方法类似，区别在于该锁是不可重入的，在同一个线程中不可重入。

3\. 可重入读写锁（Shared Reentrant Read Write Lock）

类似JDK的ReentrantReadWriteLock. 一个读写锁管理一对相关的锁。 一个负责读操作，另外一个负责写操作。
读操作在写锁没被使用时可同时由多个进程使用，而写锁使用时不允许读 (阻塞)。 此锁是可重入的。一个拥有写锁的线程可重入读锁，但是读锁却不能进入写锁。
这也意味着写锁可以降级成读锁， 比如请求写锁 —>读锁 —->释放写锁。 从读锁升级成写锁是不成的。 主要由两个类实现：

    
    
    InterProcessReadWriteLockInterProcessLock

4\. 信号量（Shared Semaphore）

一个计数的信号量类似JDK的Semaphore。
JDK中Semaphore维护的一组许可(permits)，而Cubator中称之为租约(Lease)。注意，所有的实例必须使用相同的numberOfLeases值。
调用acquire会返回一个租约对象。 客户端必须在finally中close这些租约对象，否则这些租约会丢失掉。 但是，
但是，如果客户端session由于某种原因比如crash丢掉， 那么这些客户端持有的租约会自动close， 这样其它客户端可以继续使用这些租约。
租约还可以通过下面的方式返还：

    
    
    publicvoidreturnAll(Collection<Lease>leases)publicvoidreturnLease(Leaselease)

注意一次你可以请求多个租约，如果Semaphore当前的租约不够，则请求线程会被阻塞。 同时还提供了超时的重载方法:

    
    
    publicLeaseacquire()publicCollection<Lease>acquire(intqty)publicLeaseacquire(longtime,TimeUnitunit)publicCollection<Lease>acquire(intqty,longtime,TimeUnitunit)

主要类有:

    
    
    InterProcessSemaphoreV2LeaseSharedCountReader

5\. 多锁对象（Multi Shared Lock）

Multi Shared Lock是一个锁的容器。 当调用acquire， 所有的锁都会被acquire，如果请求失败，所有的锁都会被release。
同样调用release时所有的锁都被release(失败被忽略)。 基本上，它就是组锁的代表，在它上面的请求释放操作都会传递给它包含的所有的锁。
主要涉及两个类：

    
    
    InterProcessMultiLockInterProcessLock

它的构造函数需要包含的锁的集合，或者一组ZooKeeper的path。

    
    
    publicInterProcessMultiLock(List<InterProcessLock>locks)publicInterProcessMultiLock(CuratorFrameworkclient,List<String>paths)

6\. 完整锁示例

我们再看一个官方完整锁示例：

    
    
    publicclassLockingExample{privatestaticfinalintQTY =5;privatestaticfinalintREPETITIONS =QTY *10;privatestaticfinalStringPATH ="/examples/locks";publicstaticvoidmain(String[]args)throwsException{// all of the useful sample code is in ExampleClientThatLocks.java// FakeLimitedResource simulates some external resource that can only be access by one process at a timefinalFakeLimitedResourceresource =newFakeLimitedResource();ExecutorServiceservice =Executors.newFixedThreadPool(QTY);finalTestingServerserver =newTestingServer();try{for(inti =0;i <QTY;++i){finalintindex =i;Callable<Void>task =newCallable<Void>(){@OverridepublicVoidcall()throwsException{CuratorFrameworkclient =CuratorFrameworkFactory.newClient(server.getConnectString(),newExponentialBackoffRetry(1000,3));try{client.start();ExampleClientThatLocksexample =newExampleClientThatLocks(client,PATH,resource,"Client "+index);for(intj =0;j <REPETITIONS;++j){example.doWork(10,TimeUnit.SECONDS);}}catch(InterruptedExceptione){Thread.currentThread().interrupt();}catch(Exceptione){e.printStackTrace();// log or do something}finally{CloseableUtils.closeQuietly(client);}returnnull;}};service.submit(task);}service.shutdown();service.awaitTermination(10,TimeUnit.MINUTES);}finally{CloseableUtils.closeQuietly(server);}}}

#  **三、总结**

分布式环境中，我们始终绕不开CAP理论，这也是Redisson锁和ZK锁的本质区别。CAP指的是在一个分布式系统中：一致性（Consistency）、可用性（Availability）、分区容错性（Partition
tolerance）。

这三个要素最多只能同时实现两点，不可能三者兼顾。如果你的实际业务场景，更需要的是保证数据一致性。那么请使用CP类型的分布式锁，比如：zookeeper，它是基于磁盘的，性能可能没那么好，但数据一般不会丢。

如果你的实际业务场景，更需要的是保证数据高可用性。那么请使用AP类型的分布式锁，比如：Redisson，它是基于内存的，性能比较好，但有丢失数据的风险。

**其实，在我们绝大多数分布式业务场景中，使用Redisson分布式锁就够了，真的别太较真。因为数据不一致问题，可以通过最终一致性方案解决。但如果系统不可用了，对用户来说是暴击一万点伤害。**

  

#  **四、思考思考**

以上就是我对锁的总结和。分布式锁不是完美的，总会有问题；如：在redis中，lockName和已有的key不能重名
！unlock的前提是lock成功！必须要设计自己的兜底方案......

回顾整个锁界，兄弟们都掌握了哪些锁呢？在分布式锁的场景中都遇到哪些疑难杂症？我们 **评论区** 继续

  

#  **五、备注**

redisson：

[官方实例](https://github.com/redisson/redisson/wiki/8.-%E5%88%86%E5%B8%83%E5%BC%8F%E9%94%81%E5%92%8C%E5%90%8C%E6%AD%A5%E5%99%A8)

[官方代码示例](https://github.com/redisson/redisson-examples/tree/master/locks-synchronizers-examples)

curator：

[curator的ZK客户端示例﻿](https://github.com/apache/curator/tree/master/curator-examples)

  

> 作者：京东保险 管顺利  
> 来源：京东云开发者社区 转载请注明来源

