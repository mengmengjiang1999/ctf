face it-iOS-内存管理

[ Arthur澪](https://www.jianshu.com/u/1c014cbde00d)关注赞赏支持

# face it-iOS-内存管理

### 内存

内存分为：代码段、数据段、堆区、栈区、内核区

  

m

  * 代码段：编译之后的代码
  * 数据段  
字符串常量：如`NSString *str = @"123";`  
已初始化数据：已初始化的`全局变量`、`静态变量`等  
未初始化数据：未初始化的`全局变量`、`静态变量`等

  * 栈：函数调用开销，比如局部变量。分配的内存空间地址越来越小
  * 堆：通过`alloc`、`malloc`、`calloc`等动态分配的空间，分配的内存空间地址越来越大

### 内存泄漏

指程序中间动态分配了内存，但在程序结束时 或使用完这块内存后，没有释放这部分内存，从而造成那一部分内存不可用的情况。  
一般的，内存泄漏是指 堆`（heap）`内存的泄漏。  
真正有危害的是内存泄漏的`积累`，这会最终耗尽系统所有的内存。

### iOS内存管理

内存管理的目的：避免“过早释放”和“内存泄漏”。

基本思想就是 引用计数。通过它来控制内存对象的生命周期。

##### 1、引用计数`（Reference Count）`

一个简单有效地管理对象生命周期的方式。在OC内存管理中，每个对象都有自己的计数器，表示对象被引用的次数。

##### 2、引用计数的工作原理

当创建一个新对象时，它的引用计数为 1；  
当有一个新的指针指向这个对象时，我们将其引用计数加 1；  
当某个指针不再指向这个对象是，我们将其引用计数减 1；  
当对象的引用计数变为 0 时，说明这个对象不再被任何指针指向了，这时就可以将对象销毁，回收内存。

    
    
    当创建(alloc)一个新对象A时，它的引用计数从0变为 1；
    当有一个指针指向这个对象A，也就是某对象想通过引用保留(retain)该对象A时，引用计数+1；
    当某个指针/对象不再指向这个对象A，也就是释放(release)该引用后，我们将其引用计数-1；
    

>   * 引用计数的存储  
>  在64bit中，引用计数可以直接存储在优化过的`isa指针`中，也可能存储在`SideTable`类中
>

> 内存管理原则  
>  创建的对象，当不再需要时，释放掉。  
>  需要使用的对象，保留。  
>  如果没必要释放，不要释放没有拥有的对象。

##### 3、ARC与MRC

iOS内存管理主要有两种机制：MRC、ARC。

  * MRC`（手工引用计数）`  
对象的生成、销毁、引用计数的变化都是由开发人员来完成

  * ARC`（自动引用计数）`  
2011年在`MacOS X 10.7`与`iOS
5`中引入的新技术，用于代替之前的MRC。ARC下几乎把所有内存管理事宜，都交给编译器。(ARC下会自动生成`retain、release、autorelease`)

> ARC 的原理是依赖编译器的静态分析能力，通过在编译时找出合理的插入引用计数管理代码，从而彻底解放程序员。  
>  ARC机制由 LLVM编译器 + Runtime系统，相互协作

ARC的作用：  
降低内存泄露等风险 ； 开发者只负责对象的生成，不需要关心其销毁。专注于业务逻辑。

##### 4、ARC的局限

ARC 能够解决 iOS 开发中 90% 的内存管理问题，但另外 10% 内存管理，是需要开发者自己处理的。就是：

  * 过度使用`block`之后，解决循环引用问题。
  * 与底层 `Core Foundation`对象交互的那部分。底层的`Core Foundation` 对象由于不在 ARC 的管理下，所以需要自己维护其引用计数。

### 循环引用问题

  * 例：  
对象 A 和对象 B，相互引用了对方作为自己的成员变量，只有当自己销毁时，才会将成员变量的引用计数减 1。  
因为 A 的销毁依赖于 B 销毁，而 B 的销毁又依赖于 A
的销毁，这样就造成了“循环引用”。这两个对象即使在外界已经没有任何指针能够访问到它们了，它们也无法被释放。  
另外，多个对象依次持有对方，形式一个环状，也可以造成循环引用。

> 解决循环引用问题，主要有2个办法

##### 办法1：主动置nil

明确知道会存在循环引用，在合理的位置和时机，主动断开环中的一个引用，使得对象得以回收。常见于各种与 block
相关的代码逻辑中。如：一般在最后把block置`nil`。

##### 办法2：使用弱引用weak

弱引用虽然持有对象，但并不增加引用计数，也就避免了循环引用。在 iOS 开发中，通常在 delegate 模式中使用。

> 原理：系统对于每一个有弱引用的对象，都维护一个表来记录它所有的弱引用的指针地址。这样，当一个对象的引用计数为 0
> 时，系统就通过这张表，找到所有的弱引用指针，继而把它们都置成 nil。  
>  可见，弱引用的使用是有额外的开销的。虽然开销很小，但如果一个地方肯定它不需要弱引用，就不应该盲目使用弱引用。

### Core Foundation 对象的内存管理

创建对象

    
    
    // 创建一个 CFStringRef 对象
    CFStringRef str= CFStringCreateWithCString(kCFAllocatorDefault, “hello", kCFStringEncodingUTF8);
    
    // 创建一个 CTFontRef 对象
    CTFontRef fontRef = CTFontCreateWithName((CFStringRef)@"ArialMT", fontSize, NULL);
    

对于这些对象的引用计数的修改，使用 `CFRetain` 和 `CFRelease` 方法，手工管理引用计数。

此外，还有另外一个问题。在 ARC 下，有时需要将一个`Core Foundation`
对象转换成`Objective-C`对象，这时需要告诉编译器，转换过程中的引用计数需要做如何的调整。这就引入了`bridge`相关的关键字。

>   * `__bridge`: 只做类型转换，不修改相关对象的引用计数，  
>  原来的 `Core Foundation` 对象在不用时，需调用 `CFRelease`方法。
>   * `__bridge_retained`：类型转换后，将相关对象的引用计数加 1，  
>  原来的`Core Foundation`对象在不用时，需调用`CFRelease`方法。
>   * `__bridge_transfer`：类型转换后，将该对象的引用计数交给 ARC 管理，`Core Foundation`
> 对象在不用时，不再需要调用 `CFRelease`方法。
>

根据具体的业务逻辑，合理使用上面的 3 种转换关键字，就可以解决 `Core Foundation`对象与 `Objective-C`对象相对转换的问题了。

### 定时器的内存管理

定时器使用完毕时需要将其停止，并置`nil`。

### 自动释放池`autorelease`

执行方法`autorelease`不立即释放，而是注册到（自动释放池)中，等到pool结束时释放池，再自动调用`release`进行释放工作。

> 自动释放池的主要底层数据结构是：  
>  `__AtAutoreleasePool`、`AutoreleasePoolPage`

调用了autorelease的对象，最终都是通过`AutoreleasePoolPage`对象来管理

  * AutoreleasePoolPage的结构  
每个`AutoreleasePoolPage`对象占用4096字节内存，除了存放它的成员变量，剩下的空间用来存放`autorelease对象的地址`。所有的`AutoreleasePoolPage`对象通过`双向链表`的形式连接在一起

-

调用push方法会将一个`POOL_BOUNDARY`入栈，并且返回其存放的内存地址；  
调用pop方法时传入一个`POOL_BOUNDARY`的内存地址，会从最后一个入栈的对象开始发送release消息，直到遇到这个`POOL_BOUNDARY`；  
`id *next`指向了下一个能存放`autorelease`对象地址的区域。

  * 关键字`autoReleasePool`

    
    
    for (int i = 0; i < 100000; i++) {
    
        NSString *string = @"Abc";
        string = [string lowercaseString];
        string = [string stringByAppendingString:@"xyz"];
        NSLog(@"%@", string);
    }
    

该for循环内产生大量的临时对象，直至循环结束才释放，可能导致内存泄漏。解决方法是在循环中创建自己的`autoReleasePool`，及时释放占用内存大的临时变量，减少内存占用峰值。

    
    
    for (int i = 0; i < 100000; i++) {
        @autoreleasepool {
            NSString *string = @"Abc";
            ...
            NSLog(@"%@", string);
        }
    }
    

> ARC 下，当使用`alloc/new/copy/mutableCopy`开始的方法 进行初始化时，系统会自动
> 在合适位置release，不需要pool进行管理。

> 主线程默认为我们开启 Runloop，Runloop 会自动创建`Autoreleasepool`，并进行Push、Pop 等操作来进行内存管理。

### 使用内存管理工具

可以用Xcode工具仪器的帮助下，分析内存的使用情况。它包括的工具有活动监视器，分配，泄漏，僵尸等。

菜单栏选择：Product -> Profile

  

m

  

iOS 模拟器会运行起来，模拟器里切换一些界面。稍等几秒钟，就可以看到 Instruments 检测到了我们的这次循环引用。

* * *

