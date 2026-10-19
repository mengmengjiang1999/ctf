## Golang 和方便的 goroutine

一个 goroutine 是特指的是被 Golang runtime 所管理的用户态线程，用户态线程也称协程。

在 Golang 中使用 goroutine 是极其方便的，goroutine 也是 Go 语言最吸引人的地方之一。

通过 Go 关键字就能够在 runtime 里创建一个新的 Go 协程 (goroutine)。

学会创建一个 goroutine https://go.dev/tour/concurrency/1

    
    
    go say("world")

goroutine 由于其对比操作系统线程非常明显的特点：

> 上下文切换开销更少
>
> 堆栈空间占用通常更少
>
> goroutine 之间的通信模型更方便。
>
> goroutine 调度对写代码的人来说是透明的。

在 Golang 程序中大量存在，可以说，不用它就相当不用 Golang。

也因为这种便宜好用的 **Go协程** 使得大量使用 Golang 编写的应用大行其道，今天我们来讲讲当使用 Golang 的这个特性开发应用时与
Linux namespace 相关的一些副作用。

## GPM 模型

Golang runtime 从开始到演化成如今的 G-P-M 模型定义中，一个特定 G 代表一个特定 goroutine，M 代表操作系统线程
OSthread，P 则代表 Runtime 中的逻辑处理器。

`G`是 Go 中的基本调度单位，是 Go 语言层面实现并发的最小粒度。G 的生命周期由 Go runtime 跟踪。goroutines
切换只需保存三个寄存器： Program Counter, Stack Pointer and BP。G 的 goid 被设置成私有。

`M`是具体执行 G 的工具人，是操作系统层面最小粒度的调度单位，切换 M 的上下文（OSthread) 带来的开销过大，所以实现了更小粒度的
G。把一个个任务分配成 G。

G 和 M 实现了 M:N 的用户态线程模型。

`P`是 Go runtime 里定义的概念上的逻辑处理器，持有一个本地局部队列保存着`待运行的 G`。 P 的加入是在 G 与 M 加入了一层，P 保存着
G 的栈信息，G 可以跨 M 执行。

> M 需要向 P 请求接下来需要执行的 G。
>
> G 是跑在 M 上的。
>
>  _ **没办法控制在什么时候特定 G 被谁调度**_ 。

## Runtime 中的协程

Go 协程是被 runtime 管理的。

这句话的意思是 Golang runtime 负责管理 goroutine 的资源分配以及调度事务。

因为在操作系统的视角下只有资源分配的基本单位——进程和调度的基本单位——线程，没有 goroutine 的存在。所以 goroutine 由 Golang
runtime 定义，产生，也只能由它去调度和回收。

但是在 Linux 中，你不得不支持一些 ABI 且与一些 C lib 交互。使得 Go 程序对一些使用 **C 代码编写的库** 或
**阻塞系统调用的调用** 与 **调用 Golang 的代码** 在同一线程中执行，并且还要把所有的调度交由 Go
运行时调度程序管理。如果目标库还需要用到 ThreadLocalStorage 这一类的特性，那么就不能让 runtime 想怎么来就怎么来。

在 Linux 中，我们正在研发一些增强云原生可观察性能力的产品，不可避免地需要与容器打交道，而与容器打交道，我们就不能避开如何操作 Linux
namespace。

如果当 G1 在 M1 中从命令空间 N1 切换到 N2，这时候切换了命名空间的是 M1，因为它才是操作系统看得到的那个对象，而不是
G1。如果发生了出于开发人员意料之外的调度，使得 M1 拿到的另一个 G2，那么 G2 所做的操作都是在命名空间 N2 中进行的，这个时候 G1
可能还以为自己在命名空间 N2 中。

这个时候就需要 runtime 提供一定的能力`runtime.LockOSThread`，让 G 和 M
绑在一起。还提供了`runtime.UnlockOSThread`解除这种绑定。

好消息是 LockOSThread 怎么绑的， UnlockOSThread 就能怎么解回去，“恢复原状”。

坏消息是 UnlockOSThread 并不能回滚 GPM 带来的所有 **副作用** 。

    
    
    package main
    import (
        "fmt"
        "net"
        "runtime"
        "github.com/vishvananda/netns"
    )
    
    func main() {
        // Lock the OS Thread so we don't accidentally switch namespaces
        runtime.LockOSThread()
        defer runtime.UnlockOSThread()
    
        // Save the current network namespace
        origns, _ := netns.Get()
        defer origns.Close()
    
        // Create a new network namespace
        newns, _ := netns.New()
        defer newns.Close()
        
        // setNs with New and Do somethings
        _ = netns.Set(ns)
        
        // Do something with the network namespace
        ifaces, _ := net.Interfaces()
        fmt.Printf("Interfaces: %v\n", ifaces)
    
        // Switch back to the original namespace
        netns.Set(origns)
    }

vishvananda/netns 很优雅地封装了一系列 Golang 下的 netns 操作，并且正确地给出了如何操作 Linux 下的
namespace 的 demo。

Go 1.10 在几个重要的 issue 里面达成了一些约定，来简化协程 M:N 模型的一些问题。

[#20395](https://github.com/golang/go/issues/20395)解决了一个问题，被`LockOSThread`的 G
会和 M 绑定，在绑定状态下，

>  **1、G 不会被调度走;**
>
>  **2、M 在 G 结束后也不能够回到 M pool 中等待运行其它 G，要直接被回收;**
>
> runtime 保证 **不会出于调度 G 的目的（但 exec
> 会继承**[#23570](https://github.com/golang/go/issues/23570) **）从被锁定的线程 clone
> 出新线程（**[#20676](https://github.com/golang/go/issues/20676) **）** 。

总而言之，`LockOSThread`就是为了让 goroutine 拥有 **可靠地** 修改线程上下文的能力，比如 setns / unshare /
exec / setxid，但是任何对线程上下文的修改都会让它被污染。 如果 G 在结束前调用 UnlockOSThread 解除了锁定状态，那么 Go
runtime 会认为这个 **M** 从良了。但实际上能不能等同于最开始的 M 需要开发人员来保证，或者通过静态分析 (static code
analysis)来提前检出这些问题。

一个线程能不能返回它之前的状态是不能保证的，credit（uid, gid）, namespace, priority, affinity
受到不同操作系统不同平台实现的因素。开发人员觉得这个线程的上述状态不会影响它所有可能会调度到的 goroutine 的话，就可以
UnlockOSThread 不然还是让这个线程死吧。

比如一个执行了 unshare 系统调用之后的线程，它创建并进入了一个新的 ns 之后，是不能保证能回到原来的 ns 里的。

在此之前，如果没有 Go 1.10 修复的这几个 patch， **Go 可能在一个 goroutine 改变了系统线程 M 的状态之后** ，或
**从其变更状态之后的线程 clone 出的新线程 M'** ，M'继承了 M 的状态。Runtime 把另一个 goroutine 调度到该 M或 M'
上。从结果来说就是这个 G 突然变更了所处的 namespace 等等 的情况，导致预料之外的事情发生。

在 Go 1.10 之后，如果显式地从 locked 的 G/M 中显式创建新的 G'，会发生两种情况。

1、M pool 还有空闲的，那 Runtime 从 M pool 里面取一个 M 来执行 G'。

2、如果 M pool 没有空闲的，那么 Runtime 会让 一个 干净的/没有被 LockOSThread 碰过的 Thread 执行 clone。为了
不与 **runtime 保证不会出于调度 G 的目的（但 exec
会继承**[#23570](https://github.com/golang/go/issues/23570) **）从被锁定的线程 clone
出新线程（**[#20676](https://github.com/golang/go/issues/20676) **）相抵触。**

    
    
    package main
    
    import (
            "fmt"
            "runtime"
            "syscall"
    
            "github.com/vishvananda/netns"
    )
    
    func checkErrAndPanic(err error) {
            if err != nil {
                    panic(err)
            }
    }
    
    func goroutineWithNs() {
            originNs, err := netns.Get()
            checkErrAndPanic(err)
    
            tid := syscall.Gettid()
            fmt.Printf("originNS: %s, tid: %d\n", originNs.UniqueId(), tid)
    
            ns, err := netns.New()
            checkErrAndPanic(err)
    
            runtime.LockOSThread()
            defer runtime.UnlockOSThread()
    
            err = netns.Set(ns)
            checkErrAndPanic(err)
    
            targetNetNS, err := netns.Get()
            checkErrAndPanic(err)
            
            // After SetNs() with CLONE_NEWNET
            fmt.Printf("-targeNS: %s, tid: %d\n", targetNetNS.UniqueId(), syscall.Gettid())
    
            wait := make(chan struct{})
    
            // Spwan a new goroutine, with origin net namespace
            go func() {
                    goroutineNetNS, err := netns.Get()
                    checkErrAndPanic(err)
                    // new goroutine dosen't work under the targetNetNS
                    fmt.Printf("goroutineNetNS: %s, tid: %d \n", goroutineNetNS.UniqueId(), syscall.Gettid())
                    wait <- struct{}{}
            }()
    
            <-wait
    
    }
    
    func main() {
            mainNs, err := netns.Get()
            checkErrAndPanic(err)
            fmt.Printf("mainNs: %s, tid: %d\n", mainNs.UniqueId(), syscall.Gettid())
    
            goroutineWithNs()
    
            lastestNs, err := netns.Get()
            checkErrAndPanic(err)
            fmt.Printf("lastestNs: %s, tid: %d\n", lastestNs.UniqueId(), syscall.Gettid())
    
            if !lastestNs.Equal(mainNs) {
                    
                    fmt.Printf("the original prog has be poisoned. \n")
            }
    
    }

````会得到

    
    
    ubuntu$ sudo strace -f -o log ./lockosthread
    
    mainNs: NS(4:4026531992), tid: 2204650
    originNS: NS(4:4026531992), tid: 2204650
    -targeNS: NS(4:4026532235), tid: 2204650
    goroutineNetNS: NS(4:4026531992), tid: 2204652 
    lastestNs: NS(4:4026532235), tid: 2204650
    the original prog has be poisoned. 

  

从保存下来的 strace log 上观察，setns 系统调用有且仅有调用过一次。

![](https://image.3001.net/images/20220719/1658199462_62d61da685eadccb1ff4d.png!small)

``

netns.Get() 操作则是调用 openat 的选手，就是去获取自己的 netns inode 等等相关信息。

![](https://image.3001.net/images/20220719/1658199493_62d61dc5cc6c7ec34000b.png!small)

进程虽然还是那个进程，但是不知道不觉就因为调用的函数把自己的 netns 给换了。

goroutine / 协程 可能想进入某个 ns 并且想啪地一下地产生更多的 goroutine（goroutine
没有父子关系）结果发现并没有继承关系。

## 结论

Go 选手请不要从锁定的 goroutine 生成新的 goroutine。

在 Go 1.10 之后，开发者应该如果在 LockOSThread 的协程上调用了复杂的第三方库函数，这个第三方库函数自己 go func
得很开心，可能导致开发者自己也不清楚是不是踩了这种坑，我觉得应该 propose 一个新的 API 或者让 golang
的编译器通过静态分析之类的技术手段来保证不会从当前 goroutine 上产生新的 goroutine，不然预期的这个第三方库函数并不会在预期 Lock
住的状态下运行。

如果执行的是 os/exec 之类的，那么就不是出于调度 G 的目的的 fork 线程，那么不受 Runtime 限制。 Docker
早期为了避开操作命名空间的这类问题采用了 cgo 的方法。

若在语言层面上提供协程支持的编程语言们应该都对以上的情况对应的解决方案，如果没有，就应该在编码上约法三章。比如以下趣闻。

## 趣闻

有 Go 1.10 修解决这几个问题之前，需要跨 namespace 操作东西的要么是 docker / runc / cni 那几个玩意。CNI
的开发者就提倡了注意几条规则来规避 Go Runtime 的问题。

<https://github.com/containernetworking/cni/issues/262>

> For now, the only suggestion I can make is that CNI plugins should obey the
> following 3 rules:

> be short-lived (as you said)

> be single-threaded, single-goroutine

> never re-enter`NetNS.Do()`

## Reference

https://github.com/vishvananda/netns

[Don't mix goroutines and namespaces: Part
1](https://engineering.pivotal.io/post/goroutines-and-namespaces-part-1/)

[https://www.bookstack.cn/read/qcrao-Go-Questions/goroutine 调度器-GPM
是什么.md](https://www.bookstack.cn/read/qcrao-Go-Questions/goroutine%20%E8%B0%83%E5%BA%A6%E5%99%A8-GPM%20%E6%98%AF%E4%BB%80%E4%B9%88.md)

[rosenhouse/ns-mess](https://github.com/rosenhouse/ns-mess/tree/master/c-demos)

[Linux Namespaces and Go Started to Mix](https://www.weave.works/blog/linux-namespaces-golang-followup)

https://github.com/weaveworks/weave/blob/v2.2.0/net/netns.go#L65

以及本文中直接引用的 Github issue 就不在这里重复了。

