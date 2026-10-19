**作者：京东健康 张娜**

# 一、并发编程的意义与挑战

并发编程的意义是充分的利用处理器的每一个核，以达到最高的处理性能，可以让程序运行的更快。而处理器也为了提高计算速率，作出了一系列优化，比如：

1、硬件升级：为平衡 CPU
内高速存储器和内存之间数量级的速率差，提升整体性能，引入了多级高速缓存的传统硬件内存架构来解决，带来的问题是，数据同时存在于高速缓存和主内存中，需要解决缓存一致性问题。

2、处理器优化：主要包含，编译器重排序、指令级重排序、内存系统重排序。通过单线程语义、指令级并行重叠执行、缓存区加载存储 3
种级别的重排序，减少执行指令，从而提高整体运行速度。带来的问题是，多线程环境里，编译器和 CPU
指令无法识别多个线程之间存在的数据依赖性，影响程序执行结果。

并发编程的好处是巨大的，然而要编写一个线程安全并且执行高效的代码，需要管理 **可变共享状态**
的操作访问，考虑内存一致性、处理器优化、指令重排序问题。比如我们使用多线程对同一个对象的值进行操作时会出现值被更改、值不同步的情况，得到的结果和理论值可能会天差地别，此时该对象就不是线程安全的。而当多个线程访问某个数据时，不管运行时环境采用何种调度方式或者这些线程如何交替执行，这个计算逻辑始终都表现出正确的行为，那么称这个对象是线程安全的。因此如何在并发编程中保证线程安全是一个容易忽略的问题，也是一个不小的挑战。

所以，为什么会有线程安全的问题，首先要明白两个关键问题：

1、线程之间是如何通信的，即线程之间以何种机制来交换信息。

2、线程之间是如何同步的，即程序如何控制不同线程间的发生顺序。

# 二、Java 并发编程

Java 并发采用了共享内存模型，Java 线程之间的通信总是隐式进行的，整个通信过程对程序员完全透明。

### 2.1 Java 内存模型

为了平衡程序员对内存可见性尽可能高（对编译器和处理的约束就多）和提高计算性能（尽可能少约束编译器处理器）之间的关系，JAVA 定义了 **Java
内存模型（Java Memory Model，JMM）** ，约定只要不改变程序执行结果，编译器和处理器怎么优化都行。所以，JMM
主要解决的问题是，通过制定线程间通信规范，提供内存可见性保证。

 **JMM 结构如下图所示：**

![1683611946_6459e12ada2245aa95400.png!small?1683611947520](https://image.3001.net/images/20230509/1683611946_6459e12ada2245aa95400.png!small?1683611947520)

以此看来，线程内创建的局部变量、方法定义参数等只在线程内使用不会有并发问题，对于共享变量，JMM
规定了一个线程如何和何时可以看到由其他线程修改过后的共享变量的值，以及在必须时如何同步的访问共享变量。

 **为控制工作内存和主内存的交互，定义了以下规范：**

・所有的变量都存储在主内存 (Main Memory) 中。

・每个线程都有一个私有的本地内存 (Local Memory)，本地内存中存储了该线程以读 / 写共享变量的拷贝副本。

・线程对变量的所有操作都必须在本地内存中进行，而不能直接读写主内存。

・不同的线程之间无法直接访问对方本地内存中的变量。

 **具体实现上定义了八种操作：**

1.lock：作用于主内存，把变量标识为线程独占状态。

2.unlock：作用于主内存，解除独占状态。

3.read：作用主内存，把一个变量的值从主内存传输到线程的工作内存。

4.load：作用于工作内存，把 read 操作传过来的变量值放入工作内存的变量副本中。

5.use：作用工作内存，把工作内存当中的一个变量值传给执行引擎。

6.assign：作用工作内存，把一个从执行引擎接收到的值赋值给工作内存的变量。

7.store：作用于工作内存的变量，把工作内存的一个变量的值传送到主内存中。

8.write：作用于主内存的变量，把 store 操作传来的变量的值放入主内存的变量中。

这些操作都满足以下原则：

・不允许 read 和 load、store 和 write 操作之一单独出现。

・对一个变量执行 unlock 操作之前，必须先把此变量同步到主内存中（执行 store 和 write 操作）。

### 2.2 Java 中的并发关键字

Java 基于以上规则提供了 volatile、synchronized
等关键字来保证线程安全，基本原理是从限制处理器优化和使用内存屏障两方面解决并发问题。如果是变量级别，使用 volatile
声明任何类型变量，同基本数据类型变量、引用类型变量一样具备原子性；如果应用场景需要一个更大范围的原子性保证，需要使用同步块技术。Java 内存模型提供了
lock 和 unlock 操作来满足这种需求。虚拟机提供了字节码指令 monitorenter 和 monitorexist
来隐式地使用这两个操作，这两个字节码指令反映到 Java 代码中就是同步块 - synchronized 关键字。

这两个字的作用：volatile 仅保证对单个 volatile 变量的读 /
写具有原子性，而锁的互斥执行的特性可以确保整个临界区代码的执行具有原子性。在功能上，锁比 volatile 更强大，在可伸缩性和执行性能上，volatile
更有优势。

### 2.3 Java 中的并发容器与工具类

#### 2.3.1 CopyOnWriteArrayList

CopyOnWriteArrayList
在操作元素时会加可重入锁，一次来保证写操作是线程安全的，但是每次添加删除元素就需要复制一份新数组，对空间有较大的浪费。

    
    
    public E get(int index) {
            return get(getArray(), index);
        }
    
        public boolean add(E e) {
            final ReentrantLock lock = this.lock;
            lock.lock();
            try {
                Object[] elements = getArray();
                int len = elements.length;
                Object[] newElements = Arrays.copyOf(elements, len + 1);
                newElements[len] = e;
                setArray(newElements);
                return true;
            } finally {
                lock.unlock();
            }
        }

#### 2.3.2 Collections.synchronizedList(new ArrayList<>());

这种方式是在 List 的操作外包加了一层 synchronize 同步控制。需要注意的是在遍历 List 是还得再手动做整体的同步控制。

    
    
    public void add(int index, E element) {
            // SynchronizedList 就是在 List的操作外包加了一层synchronize同步控制
            synchronized (mutex) {list.add(index, element);}
        }
        public E remove(int index) {
            synchronized (mutex) {return list.remove(index);}
        }

#### 2.3.3 ConcurrentLinkedQueue

通过循环 CAS 操作非阻塞的给队列添加节点，

    
    
    public boolean offer(E e) {
            checkNotNull(e);
            final Node<E> newNode = new Node<E>(e);
    
            for (Node<E> t = tail, p = t;;) {
                Node<E> q = p.next;
                if (q == null) {
                    // p是尾节点，CAS 将p的next指向newNode.
                    if (p.casNext(null, newNode)) {
                        if (p != t) 
                            //tail指向真正尾节点
                            casTail(t, newNode);
                        return true;
                    }
                }
                else if (p == q)
                    // 说明p节点和p的next节点都等于空，表示这个队列刚初始化，正准备添加节点，所以返回head节点
                    p = (t != (t = tail)) ? t : head;
                else
                    // 向后查找尾节点
                    p = (p != t && t != (t = tail)) ? t : q;
            }
        }

# 三、线上案例

### 3.1 问题发现

在互联网医院医生端，医生打开问诊 IM 聊天页，需要加载几十个功能按钮。在 2022 年 12 月抗疫期间，QPS 全天都很高，高峰时是平日的 12
倍，偶现报警提示按钮显示不全，问题出现概率大概在百万分之一。

### 3.2 排查问题的详细过程

医生问诊 IM
页面的加载属于业务黄金流程，上面的每一个按钮就是一个业务线的入口，所以处在核心逻辑的上的报警均使用自定义报警，该类报警不设置收敛，无论何种异常包括按钮个数异常就会立即报警。

 **1\. 根据报警信息，开始排查，却发现以下问题：**

（1） **没有异常日志** ：顺着异常日志的 logId 排查，过程中竟然没有异常日志，按钮莫名其妙的变少了。

（2） **不能复现** ：在预发环境，使用相同入参，接口正常返回，无法复现。

 **2\. 代码分析，缩小异常范围：**

医生问诊 IM 按钮处理分组进行：

    
    
    // 多个线程结果集合
        List<DoctorDiagImButtonInfoDTO> multiButtonList = new ArrayList<>();
    
    
    // 多线程并行处理
        Future<List<DoctorDiagImButtonInfoDTO>> multiButtonFuture = joyThreadPoolTaskExecutor.submit(() -> {
            List<DoctorDiagImButtonInfoDTO> multiButtonListTemp = new ArrayList<>();
            buttonTypes.forEach(buttonType -> {
                multiButtonListTemp.add(appButtonInfoMap.get(buttonType));
            });
            multiButtonList.addAll(multiButtonListTemp);
            return multiButtonListTemp;
        });

 **3\. 增加日志线上观察**

由于并发场景容易引发子线程失败的情况，对各子线程分支增加必要节点日志上线后观察：

（1）发生异常的请求处理过程中，所有子线程正常处理完成

（2）按钮缺少个数随机等于子线程中处理的按钮个数

（3）初步判断是 ArrayList 并发 addAll 操作异常

 **4\. 模拟复现**

使用 ArrayList 源码模拟复现问题：

（1）ArrayList 源码分析：

    
    
    public boolean addAll(Collection<? extends E> c) {
             Object[] a = c.toArray();
             int numNew = a.length;
             ensureCapacityInternal(size + numNew); // Increments modCount
     
             //以当前size为起点，向数组中追加本次新增对象
             System.arraycopy(a, 0, elementData, size, numNew);
     
             //更新全局变量size的值，和上一步是非原子操作，引发并发问题的根源
             size += numNew;
             return numNew != 0;
         }
     
         private void ensureCapacityInternal(int minCapacity) {
             if (elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {
                 minCapacity = Math.max(DEFAULT_CAPACITY, minCapacity);
             }
     
             ensureExplicitCapacity(minCapacity);
         }
     
         private void ensureExplicitCapacity(int minCapacity) {
             modCount++;
     
             // overflow-conscious code
             if (minCapacity - elementData.length > 0)
                 grow(minCapacity);
         }
     
         private void grow(int minCapacity) {
             // overflow-conscious code
             int oldCapacity = elementData.length;
             int newCapacity = oldCapacity + (oldCapacity >> 1);
             if (newCapacity - minCapacity < 0)
                 newCapacity = minCapacity;
             if (newCapacity - MAX_ARRAY_SIZE > 0)
                 newCapacity = hugeCapacity(minCapacity);
             // minCapacity is usually close to size, so this is a win:
             elementData = Arrays.copyOf(elementData, newCapacity);
         }
     

（2） 理论分析

在 ArrayList 的 add 操作中，变更 size 和增加数据操作，不是原子操作。

![1683611989_6459e155a8632a2442a1b.png!small?1683611990246](https://image.3001.net/images/20230509/1683611989_6459e155a8632a2442a1b.png!small?1683611990246)

（3）问题复现

复制源码创建自定义类，为方便复现并发问题，增加停顿

    
    
    public boolean addAll(Collection<? extends E> c) {
             Object[] a = c.toArray();
             int numNew = a.length;
             //第1次停顿，获取当前size
             try {
                 Thread.sleep(1000*timeout1);
             } catch (InterruptedException e) {
                 e.printStackTrace();
             }
             ensureCapacityInternal(size + numNew); // Increments modCount
     
             //第2次停顿，等待copy
             try {
                 Thread.sleep(1000*timeout2);
             } catch (InterruptedException e) {
                 e.printStackTrace();
             }
             System.arraycopy(a, 0, elementData, size, numNew);
     
             //第3次停顿，等待size+=
             try {
                 Thread.sleep(1000*timeout3);
             } catch (InterruptedException e) {
                 e.printStackTrace();
             }
             size += numNew;
             return numNew != 0;
         }

![1683612003_6459e16310d4d3b97b9bc.png!small?1683612003728](https://image.3001.net/images/20230509/1683612003_6459e16310d4d3b97b9bc.png!small?1683612003728)

### 3.3 解决问题

使用线程安全工具 Collections.synchronizedList 创建 ArrayList ：

    
    
    List<DoctorDiagImButtonInfoDTO> multiButtonList = Collections.synchronizedList(new ArrayList<>()); 

上线观察后正常。

### 3.4 总结反思

使用多线程处理问题已经变得很普遍，但是对于多线程共同操作的对象必须使用线程安全的类。

另外，还要搞清楚几个灵魂问题：

（1）JMM 的灵魂：Happens-before 原则

（2）并发工具类的灵魂：volatile 变量的读 / 写 和 CAS

