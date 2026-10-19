## **Golang简介**

Golang
是当前热门的语言之一，其拥有原生支持并发、对线程操作便捷、自身协程的轻量化、极大程度利用cpu多核等优点，使用其开发端口扫描器不仅开发过程高效，而且程序性能优秀。并且go支持跨平台编译和单平台交叉编译，使用起来极其方便。

Go语言的并发是基于 goroutine 的，goroutine 类似于线程，但并非线程。可以将 goroutine
理解为一种虚拟线程。Go语言运行时会参与调度 goroutine，并将 goroutine 合理地分配到每个 CPU 中，最大限度地使用 CPU 性能。

多个 goroutine 中，Go语言使用通道channel进行通信，通道是一种内置的数据结构，可以让用户在不同的 goroutine
之间同步发送具有类型的消息。这让编程模型更倾向于在 goroutine 之间发送消息，而不是让多个 goroutine 争夺同一个数据的使用权。

这些优点都非常适合用来写扫描器。

##  **多线程**

###  **一、** **理解并发与并行**

纠正一个大多数人对多并发理解上的一个错误，并发并不是并行，就网络连接请求来说，比如当前有1000个网络连接需要处理，并发是一个个去连接，但是在当前这个连接发出去之后，等待回连的时候他会将这个任务挂起去对下一个目标发起连接，等这个任务的连接返回来之后再去继续处理，通过切换多个线程达到减少物理处理器空闲等待的目的，典型的语言就是python，他的多线程就是并发，并不会利用并行。这种并发在处理网络连接和io操作上是可以一定程度上提升速度，但是在纯使用cpu计算的场景中基本没有提升。并行就很好理解，就是利用cpu的多个核心去跑多个任务，原本一个线程10分钟并行用了两个线程就可以5分钟完成（可以这么理解，实际上不是五分钟）

并发最简单的例子就是在一个逻辑处理器上运行多个goroutine，简单来说就是在cpu单个核心上运行多个goroutine，比如一个四核的的Intel一般来说都是有8个线程，并发只会利用其中一个，并行可以利用多个，在go中使用runtime.GOMAXPROCS(2)来指定使用的线程数

 **01** 并发

逻辑处理器：Golang 的运行时会在逻辑处理器上调度 goroutine 来运行。每个逻辑处理器都与一个操作系统线程绑定。在 Golang 1.5
及以后的版本中，运行时默认会为每个可用的物理处理器分配一个逻辑处理器。

本地运行队列：每个逻辑处理器有一个本地运行队列。如果创建一个 goroutine 并准备运行，这个 goroutine
首先会被放到调度器的全局运行队列中。之后，调度器会将全局运行队列中的 goroutine
分配给一个逻辑处理器，并放到这个逻辑处理器的本地运行队列中。本地运行队列中的 goroutine 会一直等待直到被分配的逻辑处理器执行。

![1648623513_6243ff9912bcf0fdb4f65.png!small?1648623514489](https://image.3001.net/images/20220330/1648623513_6243ff9912bcf0fdb4f65.png!small?1648623514489)

这就是并发，只有一个逻辑处理器，同时只能执行一个任务。

![1648623574_6243ffd696f6751444489.png!small?1648623576065](https://image.3001.net/images/20220330/1648623574_6243ffd696f6751444489.png!small?1648623576065)

这两个任务是轮换着执行的，他会尽量去降低cpu的空闲时间以此来提升速度。

 **02** 并行

并行可以显著的提升速度，但是相应的cpu资源消耗也会变高。

![1648623712_62440060ba6f79318f294.png!small?1648623714206](https://image.3001.net/images/20220330/1648623712_62440060ba6f79318f294.png!small?1648623714206)

非常有灵性的一张图来说明这两者的区别。

![1648623761_624400915edae756b070a.png!small?1648623762966](https://image.3001.net/images/20220330/1648623761_624400915edae756b070a.png!small?1648623762966)

可以自行体验一下并发

    
    
    func main() {import ("fmt""runtime""sync""time")func main() {// wg用来等待程序完成stime:=time.Now()defer func() {fmt.Println(time.Since(stime))}()var wg sync.WaitGroup// 分配一个逻辑处理器给调度器使用runtime.GOMAXPROCS(2)  //限制使用处理器的个数a:=runtime.NumCPU()println(a)// 计数加2，表示要等待两个goroutinewg.Add(2)// 创建两个goroutinefmt.Println("Create Goroutines")go printPrime("A", &wg)go printPrime("B", &wg)// 等待goroutine结束fmt.Println("Waiting To Finish")wg.Wait()fmt.Println("Terminating Program")}// printPrime 显示5000以内的素数值func printPrime(prefix string, wg *sync.WaitGroup){// 在函数退出时调用Done来通知main函数工作已经完成defer wg.Done()next:for outer := 2; outer < 100000; outer++ {for inner := 2; inner < outer; inner++ {if outer % inner == 0 {continue next}}fmt.Printf("%s:%d\n", prefix, outer)}fmt.Println("Completed", prefix)}

## 协程与线程

 **01** 协程

独立的栈空间，共享堆空间，调度由用户自己控制，本质上有点类似于用户级线程，这些用户级线程的调度也是自己实现的。

 **02** 线程

一个线程上可以跑多个协程，协程是轻量级的线程。

goroutine

Goroutine是 Go语言中的轻量级线程实现，由 Go 运行时（runtime）管理。Go 程序会智能地将 goroutine 中的任务合理地分配给每个
CPU。goroutine详细介绍

Go 程序从 main 包的 main() 函数开始，在程序启动时，Go 程序就会为 main() 函数创建一个默认的 goroutine。

使用非常方便

    
    
    func main() {go say("word")say("hello")}func say(s string)  {for i:=0;i<5;i++{time.Sleep(time.Second)fmt.Println(s)}}

唯一需要注意的是上面例子是可以正常输出我们想要的结果。

word

hello  
hello  
word  
word  
hello  
hello  
word  
hello

但是如果去掉say("hello")就不行了，输出会变为空，因为goroutine会随着主线程的退出而退出，所以需要使用一些手段合理的控制goroutine的结束时间，并在必要的时候阻塞主线程（大部分情况都需要）防止主线程退出而导致子线程意外中断。

### 举例三个方式

###  **第一个使用sleep函数：**

    
    
    func main() {go say("word")time.Sleep(time.Second*6)}func say(s string)  {for i:=0;i<5;i++{time.Sleep(time.Second)fmt.Println(s)}}

可以是可以但是有没有感觉到很蠢。

 **第二种方式使用信道阻塞：**

    
    
    func main() {c:=make(chan bool)go say("word",c)<-c}func say(s string,c chan bool)  {for i:=0;i<5;i++{time.Sleep(time.Second)fmt.Println(s)}c<-true}

利用信道自身的特性讲主线程阻塞，只有当goroutine执行完成像c中写入数据，主线程读取到了c中的数据程序才会继续向下运行。

 **第三种也是最常用的使用sync包中的WaitGroup来解决**

    
    
    func main() {var wg sync.WaitGroupwg.Add(1)go say("word",&wg)wg.Wait()}func say(s string,wg *sync.WaitGroup)  {defer wg.Done()for i:=0;i<5;i++{time.Sleep(time.Second)fmt.Println(s)}}

需要注意的是add一定要和wait在同一个线程中，不然可能还没有将goroutine添加到wg中主线程就运行结束。

##  **Channel（信道）**

 **声明**

    
    
    var ch chan intvar ch map[string] chan boolch := make(chan int)

一个 channel是一个通信机制，它可以让一个 goroutine 通过它给另一个 goroutine 发送值信息。每个 channel
都有一个特殊的类型，也就是 channels 可发送数据的类型。

Go语言提倡使用通信的方法代替共享内存，当一个资源需要在 goroutine 之间共享时，通道在 goroutine
之间架起了一个管道，并提供了确保同步交换数据的机制。声明通道时，需要指定将要被共享的数据的类型。可以通过通道共享内置类型、命名类型、结构类型和引用类型的值或者指针。

在任何时候，同时只能有一个 goroutine 访问通道进行发送和获取数据。goroutine
间通过通道就可以通信，通道像一个传送带或者队列，总是遵循先入先出（队列）的规则，保证收发数据的顺序。

    
    
    func main() {s:=[]int{7,5,3,7,4,3}c:=make(chan int)go sum(s[:len(s)/2],c)go sum(s[len(s)/2:],c)x:=<-cy:=<-cfmt.Println(x,y,x+y)}func sum(s []int,c chan int)  {sum:=0for _,v:=range s{sum+=v}c<-sum}

单说（无缓冲）信道，它仅仅是一个通道，并不会存东西，它只是一个连接两个goroutine并且传输指定的类型的管道，只有双方同时准备好，也就是同时连接上这个管道，数据才会传输，只有一方连接上管道并不会将数据放入管道就去干其他事请了，而是在这等着管道的另一头接上，这期间在等待的这一段时间这个goroutine会一直处于阻塞状体，这也就是上面为什么会使用信道控制主线程

总结一下来说就是

 **01** 向信道内写入数据通常会导致程序堵塞，直到有其他go程从这个channel中读取数据。

 **02** 如果信道内没有数据，那么从channel中读取数据也会导致程序阻塞，直到chnnel中被写入数据

如果只有这样的一个只能传输数据的管道显然是不能胜任大部分情况，有需求就会有解决办法，缓冲信道他来了

带缓冲的channel是一种在被接收之前能存储一个或者多个值的通道。这种类型不强制要起go程之间必须同时完成发送和接收。阻塞的条件也发生了改变（只有在缓冲区满了的时候发生阻塞，缓冲区没有东西，但存在接收动作的时候发生阻塞，无缓冲信道时时刻刻都在发生阻塞）

上图对比一下二者

![1648624247_624402770e1c673ee74df.png!small?1648624249198](https://image.3001.net/images/20220330/1648624247_624402770e1c673ee74df.png!small?1648624249198)

![1648624252_6244027c6da62fc664629.png!small?1648624254070](https://image.3001.net/images/20220330/1648624252_6244027c6da62fc664629.png!small?1648624254070)

看到缓冲信道之后，是不是生产者消费者模型立马就在脑海里面浮现出来了，扫描器会充分利用缓冲信道的优势来节省大量内存空间

  

声明的方式也很简单

    
    
    ch := make(chan int,10)

但是有了缓冲信道就会涉及到关闭的事，为了防止发生问题（向一个以关闭的信道中写入数据）需要严格按照规定，只有发送者能关闭信道，接受者不要关闭信道。

总结

结合goroutine的轻便切换方便、可以在用户态完成线程切换、创建和销毁开销小、天生就能最大化利用多核再加上信道痛心的优势，都非常适合开发网络扫描

## 网络通信

 **1** **tcp连接**

go的标准库很成熟，通过标准库就可以实现很多东西，网络通信基本上都在net库中。

这里介绍最常用的网络连接函数。

 **Dial**

    
    
    func Dial(network, address string) (Conn, error)

只需要两个参数，返回一个网络连接和一个error

    
    
    tcp连接：conn, err := net.Dial("tcp", "192.168.10.10:80")udp连接：conn, err := net.Dial("udp", "192.168.10.10:8888")ICMP连接：conn, err := net.Dial("ip4:icmp", "c.biancheng.net")ICMP连接：conn, err := net.Dial("ip4:1", "10.0.0.3")

可以用来探测端口是否开放

    
    
    func main() {conn,err:=net.Dial("tcp","127.0.0.1:80")if err!=nil{fmt.Println(err)return}conn.Close()fmt.Println("端口开放")}

如果tcp能连接上就证明端口开放的

 **DialTimeout**

    
    
    func DialTimeout(network, address string, timeout time.Duration) (Conn, error)

和Dial的使用方法相同，只不过多了一个超时，这个比较常用，因为在扫描的过程中防止阻塞都要设置超时。

 **DialTCP**

    
    
    func DialTCP(network string, laddr, raddr *TCPAddr) (*TCPConn, error)

和Dial使用方法也类似，多了一个laddr，可以指定连接使用的地址，如果为空就随机选择，raddr是我们要连接的目标地址，是一个TCPAddr类型，可以使用ResolveTCPAddr获得

func ResolveTCPAddr(network, address string) (*TCPAddr, error)

 **Dialer结构体**

    
    
    type Dialer struct {Timeout time.DurationDeadline time.TimeLocalAddr AddrDualStack boolFallbackDelay time.DurationKeepAlive time.DurationResolver *ResolverCancel <-chan struct{}Control func(network, address string, c syscall.RawConn) error}

可以创建一个可定制化的连接

    
    
    func (d *Dialer) Dial(network, address string) (Conn, error)

还可以创建一个带有上下文控制的连接

func (d *Dialer) DialContext(ctx context.Context, network, address string)
(Conn, error)

 **2** **ICMP**

使用golang.org/x/net/icmp库

 **ListenPacket**

使用ListenPacket建立一个监听器，这个监听器可以接收其他主机发送过来的icmp数据包

使用WriteTo方法发送icmp数据包，需要指定目标的地址

    
    
    func (c *PacketConn) WriteTo(b [ ]byte, dst net.Addr) (int, error)
    
    
    dst, _ := net.ResolveIPAddr("ip", 目标地址)IcmpByte := makemsg(host.String())   //构造数据包conn.WriteTo(IcmpByte, dst)    //将数据包发送到目标

使用Readfrom判断谁给发了返回包

    
    
    func (c *PacketConn) ReadFrom(b []byte) (int, net.Addr, error)
    
    
    msg := make([]byte, 100)_, sourceIP, _ := conn.ReadFrom(msg)

获取到哪个ip就说明哪个ip主机是存活的

##  **I/O操作**

网络连接建立上我们就可以知道目标存活，接下来如果我们需要判断这个端口是干什么的，就需要io操作了，或者是我们将扫描结果存到本地也需要io操作

在io标准库中定义了两个重要的接口，Reader和Writer，基本上所有的io操作都围绕着这两个接口展开

并且在go的很多标准库中都实现了这两个接口，比如io库，ioutil库，bufio库，bytes库，strings库等等。

比如当我们建立一个tcp连接之后，得到了一个net.tcpconn对象，他就实现了Writer和Reader接口，可以让我们往连接里面写入东西也可以读取![1648624577_624403c1a9fe875ff8da0.png!small?1648624579761](https://image.3001.net/images/20220330/1648624577_624403c1a9fe875ff8da0.png!small?1648624579761)

简单的整理了一下，不全。使用和转换方式很多可自行探索

##  **总结**

有了上面这三个重要的基础了之后，扫描器写起来就很简单了。

![1648624801_624404a1d850972998e32.gif!small?1648624805352](https://image.3001.net/images/20220330/1648624801_624404a1d850972998e32.gif!small?1648624805352)

