## 一、单元测试

### 1.1 单元测试的必要性

测试驱动开发并不是一个很新鲜的概念了。在日常开发中，很多时候需要测试，但是这种输出是必须在点击一系列按钮之后才能在屏幕上显示出来的东西。测试的时候，往往是用模拟器一次一次的从头开始启动
app，然后定位到自己所在模块的程序，做一系列的点击操作，然后查看结果是否符合自己预期。

这种行为无疑是对时间的巨大浪费。于是有很多资深工程师们发现，我们是可以在代码中构造一个类似的场景，然后在代码中调用我们之前想要检查的代码，并将运行结果和设想结果在程序中进行比较，如果一致，则说明我们的代码没有问题，由此就产生了单元测试。

### 1.2 单元测试的目的

单元测试的主要目的是发现模块内部逻辑、语法、算法和功能错误。

单元测试主要是基于白盒测试验证以下问题：

  * 验证代码与设计相符度。
  * 发现设计和需求中存在错误。
  * 发现在编码过程中引入的错误。

单元测试关注的重点有以下部分：

![1686885069_648bd2cdbb058d55764e0.png!small?1686885070414](https://image.3001.net/images/20230616/1686885069_648bd2cdbb058d55764e0.png!small?1686885070414)

独立路径 - 对于基本执行路径和循环进行测试，可能的错误有：

  * 不同数据类型的比较。
  * “差 1 错”，即可能多循环或少循环一次。
  * 错误或不可能的终止条件。
  * 不适当的修改了循环变量。

局部数据结构 -单元的局部数据结构是最常见的错误来源，应设计测试用例以检查可能的错误：

  * 不一致的数据类型。
  * 检查不正确或不一致的数据类型。

错误处理 -比较完善的单元设计要能预见出错的条件，并设置适当的错误处理，以便在程序出错时，能对错误重新做安排，保证期逻辑上的正确性：

  * 出错的描述难以理解。
  * 显示的错误与实际的错误不符。
  * 对错误条件的处理不正确。

边界条件 -边界上出现错误是最常见的错误现象：

  * 取最大最小值发生错误。
  * 控制流中的大于、小于这些比较值常出现错误。

单元接口
-接口实际上就是输入和输出对应关系的集合，要对单元进行动态测试无非就是给这个单元一个输入，然后检查输出是否和预期一致。如果数据不能正常输入和输出，单元测试就无从谈起，因此需要对单元接口进行如下的测试：

  * 被测单元的输入、输出在个数、属性、顺序是否和详细设计中的描述一致。
  * 是否修改了只做输入用的形式参数。
  * 约束条件是否通过形式参数来传送。  

### 1.3 单元测试依赖的两个主要框架

OCUnit（即用 XCTest 进行测试）其实就是苹果自带的测试框架，主要是断言使用，由于使用简单本次文章不过多介绍。

OCMock
主要功能是模拟某个方法或者属性的返回值，你可能会疑惑为什么要这样做？使用模型生成的模型对象，再传进去不就可以了？答案是可以的，但是有特殊的情况，比如一些不容易构造或不容易获取的对象，此时你可以创建一个虚拟的对象来完成测试。实现思想是根据要
mock 的对象的 class
来创建一个对应的对象，并且设置好该对象的属性和调用预定方法后的动作（例如返回一个值，调用代码块，发送消息等等），然后将其记录到一个数组中，接下来开发者主动调用该方法，最后做一个
verify（验证），从而判断该方法是否被调用，或者调用过程中是否抛出异常等。在单元测试开发中使用更多难点的也是对 OCMock
的使用方式不明确，本次文章主要讲的就是这个 OCMock 的集成和使用方法。

## 二、OCMock 的集成与使用

### 2.1 OCMock 的集成方式

项目集成 OCMock 第三方库，这个使用 pod 工具直接安装 OCMock 框架即可。若使用 iBiu 工具安装 OCMock 库需在 podfile
文件同级创建 Podfile.custom。

![1686885116_648bd2fc2a475d3113ddf.png!small?1686885117693](https://image.3001.net/images/20230616/1686885116_648bd2fc2a475d3113ddf.png!small?1686885117693)

使用普通的 pod 文件相同格式添加 OCmock 如下：

    
    
    source 'https://github.com/CocoaPods/Specs.git'
    pod 'OCMock'
    

### 2.2 OCMock 的使用方法

 **（一）置换方法 (存根)：告诉 mock 对象，当 someMethod 被调用，返回什么值**

调用方式：

    
    
    d jalopy = [OCMock mockForClass[Car class]];
    OCMStub([jalopy goFaster:[OCMArg any] units:@"kph"]).andReturn(@"75kph");
    

使用场景：

1． 验证 A 方法时，A 方法内部使用 B 方法的返回值但是 B 方法内部逻辑比较复杂，这时需要使用 stub 方法去存根 B
方法的返回值。代码实现类似下面代码实现固定 funcB 的返回值，做到在不影响源代码的条件下，获取满足测试需要的参数。

方法进行存根前

    
    
    - (NSString *)getOtherTimeStrWithString:(NSString *)formatTime{
        NSDateFormatter *formatter = [[NSDateFormatter alloc] init];
        [formatter setDateStyle:NSDateFormatterMediumStyle];
        [formatter setTimeStyle:NSDateFormatterShortStyle];
        [formatter setDateFormat:@"YYYY-MM-dd HH:mm:ss"]; //(@"YYYY-MM-dd hh:mm:ss") ----------设置你想要的格式,hh与HH的区别:分别表示12小时制,24小时制
        //设置时区选择北京时间
        NSTimeZone* timeZone = [NSTimeZone timeZoneWithName:@"Asia/Beijing"];
        [formatter setTimeZone:timeZone];
        NSDate* date = [formatter dateFromString:formatTime]; //------------将字符串按formatter转成nsdate
        //时间转时间戳的方法:
        NSInteger timeSp = [[NSNumber numberWithDouble:[date timeIntervalSince1970]] integerValue] * 1000;
        return [NSString stringWithFormat:@"%ld",(long)timeSp];
    }
    

使用 stub (mockObject getOtherTimeStrWithString).andReturn (@"1000") 存根后类似于以下效果

    
    
    - (NSString *)getOtherTimeStrWithString:(NSString *)formatTime{
        
        return @"1000";
        
        NSDateFormatter *formatter = [[NSDateFormatter alloc] init];
        [formatter setDateStyle:NSDateFormatterMediumStyle];
        [formatter setTimeStyle:NSDateFormatterShortStyle];
        [formatter setDateFormat:@"YYYY-MM-dd HH:mm:ss"]; //(@"YYYY-MM-dd hh:mm:ss") ----------设置你想要的格式,hh与HH的区别:分别表示12小时制,24小时制
        //设置时区选择北京时间
        NSTimeZone* timeZone = [NSTimeZone timeZoneWithName:@"Asia/Beijing"];
        [formatter setTimeZone:timeZone];
        NSDate* date = [formatter dateFromString:formatTime]; //------------将字符串按formatter转成nsdate
        //时间转时间戳的方法:
        NSInteger timeSp = [[NSNumber numberWithDouble:[date timeIntervalSince1970]] integerValue] * 1000;
        return [NSString stringWithFormat:@"%ld",(long)timeSp];
    }
    

2．
代码正常流程经过测试已经很健壮了，但是一些错误的流程并不容易发现但是是可能存在的，例如边缘值数据，单元测试中可以使用存根对数据进行模拟，测试代码在特殊数据情况下的运行情况。

注：stub () 也可以不设置返回值，验证可行，猜测可能是返回的 nil 或者 void，所以不带返回值的方法也可以进行方法存根。

 **（二）生成 Mock 对象，目前有三种方式。**

通过对 Person 类的 talk 方法进行测试举例，其中也涉及 Men 类以及 Animaiton 类，以下是三个类的相关源码。

Person 类

    
    
    @interface Person()
    @property(nonatomic,strong)Men *men;
    @end
    
    
    @implementation Person
    -(void)talk:(NSString *)str
    {
        [self.men logstr:str];
        [Animaiton logstr:str];
        
    }
    @end
    

Men 类

    
    
    @implementation Men
    -(NSString *)logstr:(NSString *)str
    {
        NSLog(@"%@",str);
        return str;
    }
    @end
    

Animaiton 类

    
    
    @implementation Animaiton
    +(NSString *)logstr:(NSString *)str
    {
        NSLog(@"%@",str);
        return str;
    }
    -(NSString *)logstr:(NSString *)str
    {
        NSLog(@"%@",str);
        return str;
    }
    @end
    

对 talk 方法进行单测时需要对 person 类进行 mock，以下是通过三种不同的方式生成 mock
对象，对三种方式的调用方法，使用场景都做了介绍，最后对每种方式的优缺点也做了一个表格方便区别。

 **Nice Mock**

NiceMock 创建的 mock 对象在进行方法测试时会优先调用实例方法，若未找到实例方法，会继续调用同名的类方法。因此该方法可以用来生成 mock
对象去测试类方法也可以测试对象方法。

使用方式：

    
    
    - (void)testTalkNiceMock {
        id mockA = OCMClassMock([Men class]);
        Person *person1 = [Person new];
        person1.men = mockA;
        [person1 talk:@"123"];
        OCMVerify([mockA logstr:[OCMArg any]]);
    }
    

使用场景：

Nice mock 是比较友好的，当一个没有存根的方法被调用时他不会引起一个异常会验证通过。如果你不想自己对很多的方法进行存根，那么使用 nice
mock。在上方的举例中 mockA 调用 testTalkNiceMock 时，Men 类中的 +(NSString *)
logstr:(NSString *) str 不会执行打印操作。在调用过程中因为同时存在同名的 logstr：类方法和实例方法，会优先调用实例方法。

 **Strict Mock**

使用方式：

测试 case 如下，mockA 是 Strict Mock 生成要调用 testTalkStrictMock 方法，则 Mock 生成要调用
testTalkStrictMock 方法则该方法要使用 stub 进行存根，否则最后的 OCMVerifyAll（mockA）就会抛出异常。

    
    
    - (void)testTalkStrictMock {
        id mockA = OCMStrictClassMock([Person class]);
        OCMStub([mockA talk:@"123"]);
        [mockA talk:@"123"];
        OCMVerifyAll(mockA);
    }
    

使用场景：

这种方式创建的 mock 对象，如果调用未 stub（stub 代表存根）的方法，会抛出一个异常。这需要保证在 mock
的生命周期中每一个独立调用的方法都是被存根的，这种方法使用比较严格，很少使用。

 **Partial Mock**

这样创建的对象在调用方法时：如果方法被 stub, 调用 stub 后的方法，如果方法没有被 stub, 调用原来的对象的方法，该方法有限制只能 mock
实例对象。

使用方式：

    
    
    - (void)testTalkPartialMock {
        id mockA = OCMPartialMock([Men new]);
        Person *person1 = [Person new];
        person1.men = mockA;
        [person1 talk:@"123"];
        OCMVerify([mockA logstr:[OCMArg any]]);
    }
    

使用场景：

当调用一个没有被存根的方法时，会调用实际对象的该方法。当不能很好的存根一个类的方法时，该技术是非常有用的。调用 testTalkPartialMock 时
Men 类中的 +(NSString *) logstr:(NSString *) str 会执行打印操作。

三种方式的差异表格：

![1686885125_648bd3054310d9a36d511.png!small?1686885125889](https://image.3001.net/images/20230616/1686885125_648bd3054310d9a36d511.png!small?1686885125889)

 **（三）验证方法的调用**

调用方式：

    
    
    OCMVerify([mock someMethod]);
    OCMVerify(never(),    [mock doStuff]); //从没被调用
    OCMVerify(times(n),   [mock doStuff]);   //调用了N次
    OCMVerify(atLeast(n), [mock doStuff]);  //最少被调用了N次
    OCMVerify(atMost(n),  [mock doStuff]);
    

使用场景：

在单元测试中可以验证某个方法是否执行，以及执行了几次。

延时验证调用：

    
    
    OCMVerifyAllWithDelay(mock, aDelay);
    

使用场景：该功能用于等待异步操作会比较多，其中 aDelay 为预期最长等待时间。

 **（四）添加预期**

调用方式：

准备数据：

    
    
    NSDictionary *info = @{@"name": @"momo"};
    id mock = OCMClassMock([MOOCMockDemo class]);
    

添加预期：

    
    
    OCMExpect([mock handleLoadSuccessWithPerson:[OCMArg any]]);
    

可以预期不执行：

    
    
    OCMReject([mock handleLoadFailWithPerson:[OCMArg any]]);
    

可以验证参数：

    
    
    // 预期 + 参数验证
    OCMExpect([mock handleLoadSuccessWithPerson:[OCMArg checkWithBlock:^BOOL(id obj) {
        MOPerson *person = (MOPerson *)obj;
        return [person.name isEqualToString:@"momo"];
    }]]);
    

可以预期执行顺序：

    
    
    // 预期下列方法顺序执行
    [mock setExpectationOrderMatters:YES];
    OCMExpect([mock handleLoadSuccessWithPerson:[OCMArg any]]);
    OCMExpect([mock showError:NO]);
    

可以忽略参数 (预期方法执行时)：

    
    
    OCMExpect([mock showError:YES]).ignoringNonObjectArgs; // 忽视参数
    

执行：

    
    
    [MOOCMockDemo handleLoadFinished:info];
    

断言：

    
    
    OCMVerifyAll(mock);
    

可以延迟断言：

    
    
    OCMVerifyAllWithDelay(mock, 1); // 支持延迟验证
    

最后的 OCMVerifyAll 会验证前面的期望是否有效，只要有一个没调用，就会出错。

 **（五）参数约束**

调用方式：

    
    
    OCMStub([mock someMethodWithAnArgument:[OCMArg any]])
    OCMStub([mock someMethodWithPointerArgument:[OCMArg anyPointer]])
    OCMStub([mock someMethodWithSelectorArgument:[OCMArg anySelector]])
    

使用场景：在使用
OCMVerify（）方法验证某个方法是否调用是使用，单元测试会验证方法参数是否一致，如果不一致就是提示验证失败，此时如果只关注方法调用，并不关注参数即可使用
[OCMArg any] 传参。

 **（六）网络接口的模拟**

顾名思义可以 mock 网络接口的数据返回，测试不同数据下代码的走向以及准确性。

调用方式：

    
    
    id mockManager = OCMClassMock([JDStoreNetwork class]);
    [orderListVc setComponentsNet:mockManager];
    [OCMStub([mockManager startWithSetup:[OCMArg any] didFinish:[OCMArg any] didCancel:[OCMArg any]]) andDo:^(NSInvocation *invocation) {   
    
    
        void (^successBlock)(id components,NSError *error) = nil;   
        
        [invocation getArgument:&successBlock atIndex:3];  
        
        successBlock(@{@"code":@"1",@"resultCode":@"1",@"value":@{@"showOrderSearch":@"NO"}},nil);
        }];
    

以上就是在调用 setComponentsNet 方法内部调用了接口，该方法就可以在调用接口后模拟需要的返回数据，successBlock
中的就是返回的测试数据。本方式是通过获取接口调用的方法签名，获取 successBlock
成功回调传参并手动调用。同样可以模拟接口失败的情况，只需获取到签名中的对应的失败回调就可以实现了。

使用场景：书写单元测试方法时涉及网络接口的模拟，通过该方式 mock 接口返回结果。

 **（七）恢复类**

置换类方法后，可以将类恢复到原来的状态，通过调用 stopMocking 来完成。

调用方式：

    
    
    id classMock = OCMClassMock([SomeClass class]);
    /* do stuff */
    [classMock stopMocking];
    

使用场景：

正常对实例对象置换后，mock 对象释放后会自动调用 stopMocking，但是添加到类方法上的 mock 对象会跨越了多个测试，mock
的类对象在置换后不会 deallocated, 需要手动来取消这个 mock 关系。

 **（八）观察者模拟 - 创建一个接受通知的实例**

调用方式：

    
    
    - (void)testPostNotification {   
    Person *person1 = [[Person alloc] init];   
    id observerMock = OCMObserverMock();   
    //给通知中心设置观察者    
    [[NSNotificationCenter defaultCenter] addMockObserver: observerMock name:@"name" object:nil];    
    //设置观察期望    
    [[observerMock expect] notificationWithName:@"name" object:[OCMArg any]];    //调用要验证的方法    
    [person1 methodWithPostNotification];    
    [[NSNotificationCenter defaultCenter] removeObserver:observerMock];    
    // 调用验证   
    OCMVerifyAll(observerMock);}
    

使用场景：

创建一个 mock 对象，可以用来观察通知。mock 必须注册以接收通知。

 **（九）mock 协议**

调用方式：

    
    
    id protocolMock = OCMProtocolMock(@protocol(SomeProtocol));
    /*严格的协议*/
    id classMock = OCMStrictClassMock([SomeClass class]);
    id protocolMock = OCMStrictProtocolMock(@protocol(SomeProtocol));
    id protocolMock = OCMProtocolMock(@protocol(SomeProtocol));
    /*严格的协议*/
    id classMock = OCMStrictClassMock([SomeClass class]);
    id protocolMock = OCMStrictProtocolMock(@protocol(SomeProtocol));
    

调用场景：当需要创建一个实例，让其具有协议的所定义的功能时使用。

### 2.3 mock 使用限制

对于同个方法，先 stub 后 expect 是不行的：因为先 stub 的话，所有的调用都会变成 stub，这样子即使过程调用该方法，最后
OCMVerifyAll 验证也会失败；解决的办法是，在 OCMExpect 上顺便 stub，比如：OCMExpect ([mock
someMethod]).andReturn (@"a string")，或者将 stub 置于 expect 之后。

部分模拟不适用于某些类：如 NSString 和 NSDate，这些”toll-free bridged” 的类，否则会抛出异常。

某些方法不能 stub：如：init、class、methodSignatureForSelector、forwardInvocation 这些。

NSString 与 NSArray 的类方法不能 stub，否则无效。

NSObject 的方法调用不能验证，除非在子类中重写。

苹果核心类的私有方法调用不能被验证，如以_开头的方法。

延时验证方法调用不支持，暂时只支持期望 - 运行 - 验证模式的延时验证。

OCMock 不支持多线程。

## 三、最后

希望这篇文章和例子已经陈述清楚了一些 OCMock 最通用的用法。OCMock
站点：[http://ocmock.org/features/](https://www.oschina.net/action/GoToLink?url=http%3A%2F%2Focmock.org%2Ffeatures%2F)是一个最好的学习
OCMock 的地方。mock 是单调的但是对于一个应用程序却是必须的。如果一个方法很难用 mock 来测试，这个迹象表明你的设计需要重新考虑了。

#### 参考链接：

OCMock
官网：[https://ocmock.org/features/](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Focmock.org%2Ffeatures%2F)

OCMock3
参考：[https://www.cnblogs.com/xilifeng/p/4690280.html#header-c18](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fwww.cnblogs.com%2Fxilifeng%2Fp%2F4690280.html%23header-c18)

iOS 测试系列：[http://blog.oneinbest.com/2017/07/27/iOS 测试系列 - 三 - OCMock 的使用
/](https://www.oschina.net/action/GoToLink?url=http%3A%2F%2Fblog.oneinbest.com%2F2017%2F07%2F27%2FiOS%25E6%25B5%258B%25E8%25AF%2595%25E7%25B3%25BB%25E5%2588%2597-%25E4%25B8%2589-OCMock%25E7%259A%2584%25E4%25BD%25BF%25E7%2594%25A8%2F)

> 作者：京东零售 王中文
>
> 来源：京东云开发者社区

