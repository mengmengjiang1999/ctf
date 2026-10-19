iOS单元测试简介和使用

[ 张聪_2048](https://www.jianshu.com/u/06fad66c4cf3)关注赞赏支持

# iOS单元测试简介和使用

### 一、单元测试简介

#### 1.1、简介

**单元测试** （Unit Testing），又称为 **模块测试**
，是指对软件中的最小可测试单元进行检查和验证，通过开发者编写代码去验证被测代码是否正确的一种手段，例如编写一个测试函数去测试某一功能函数是否能正确执行达到预期效果。在实际项目开发中使用单元测试可以提高软件的质量，也可以尽量早的发现代码中存在的问题加以修正。

执行单元测试，是为了证明某段代码的行为确实和开发者所期望的一致。因此，我们所要测试的是规模很小的、非常独立的功能片段。通过对所有单独部分的行为建立起信心。然后，才能开始测试整个系统。

#### 1.2、单测应用

**持续集成** （Continuous
Integration），简称CI，是软件开发周期的一种实践，把代码仓库（Gitlab或者Github）、构建工具（如Jenkins）和测试工具（SonarQube）集成在一起，频繁的将代码合并到主干然后自动进行构建和测试。简单来说持续集成就是一个监控版本控制系统中代码变化的工具，当发生变化是可以自动编译和测试以及执行后续自定义动作。

持续集成流程.png

### 二、单元测试使用

点击下载Demo：[ZJHUnitTestDemo](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2FZhangJingHao%2FZJHUnitTestDemo.git)

#### 2.1、创建测试项目

在创建项目时勾选 Include Tests选项，如下图所示：

创建项目时勾选 Include Tests选项.png

创建项目成功后，项目目录下即可看到对应的单元测试文件夹。先忽略ZJHUnitTestDemoUITests，它属于UI测试，其他文章会有更多介绍，本文主要讲ZJHUnitTestDemoTests文件

创建项目成功后，项目目录下即可看到对应的单元测试文件.png

#### 2.1.2、项目创建后添加

如果之前的项目还没有添加单元测试target，也可以按照下图方式进行新建：

项目创建后添加测试项目.png

#### 2.2、单元测试类介绍

在新建的测试文件代码如下所示，系统自动生成了几个方法：

    
    
    #import <XCTest/XCTest.h>
    
    // 所有的测试类需要继承 XCTestCase
    @interface ZJHUnitTestDemoTests : XCTestCase
    
    @end
    
    @implementation ZJHUnitTestDemoTests
    
    /// 在每一个测试方法调用前，都会被调用；用来初始化 test 用例的一些初始值
    - (void)setUp {
        // Put setup code here. This method is called before the invocation of each test method in the class.
        // 在这里设置代码。在调用类中的每个测试方法之前调用此方法。
    }
    
    /// 在每一个测试方法调用后，都会被调用；用来重置 test 方法的数值
    - (void)tearDown {
        // Put teardown code here. This method is called after the invocation of each test method in the class.
        // 在这里输入删除代码。在调用类中的每个测试方法之后调用此方法。
    }
    
    /// 测试方法命名以 test 开始
    - (void)testExample {
        // This is an example of a functional test case.
        // Use XCTAssert and related functions to verify your tests produce the correct results.
        // 这是一个功能测试用例。
        // 使用XCTAssert和相关函数来验证您的测试产生正确的结果。
    }
    
    /// 性能测试
    - (void)testPerformanceExample {
        // This is an example of a performance test case.
        // 这是一个性能测试用例。
        [self measureBlock:^{
            // Put the code you want to measure the time of here.
            // 把你想要测量时间的代码放在这里。
        }];
    }
    
    @end
    

**setUp方法**
：setUp方法会在XCTestCase的测试方法每次调用之前调用，所以可以把一些测试代码需要用的初始化代码和全局变量写在这个方法里;

**tearDown**
：在每个单元测试方法执行完毕后，XCTest会执行tearDown方法，所以可以把需要测试完成后销毁的内容写在这个里，以便保证下面的测试不受本次测试影响

**测试用例** ：所有测试的方法都需要以test为前缀进行命名，比如- (void)testExample，-
(void)testPerformanceExample

#### 2.3、新建示例

我们在项目里面创建一个`ZJHMathTool`类：

    
    
    @interface ZJHMathTool : NSObject
    - (int)sumA:(int)a andB:(int)b;
    - (int)subA:(int)a andB:(int)b;
    - (int)multiplyA:(int)a andB:(int)b;
    - (int)divideA:(int)a andB:(int)b;
    @end
    
    @implementation ZJHMathTool
    - (int)sumA:(int)a andB:(int)b {
        return a + b;
    }
    
    - (int)subA:(int)a andB:(int)b {
        return a - b;
    }
    
    - (int)multiplyA:(int)a andB:(int)b {
        return a * b;
    }
    
    - (int)divideA:(int)a andB:(int)b {
        return a / b;
    }
    @end
    

同时在新建一个对应的 `ZJHMathToolTests`测试类：

    
    
    #import <XCTest/XCTest.h>
    
    @interface ZJHMathToolTests : XCTestCase
    @end
    
    @implementation ZJHMathToolTests
    
    - (void)setUp {
    }
    
    - (void)tearDown {
    }
    
    - (void)testExample {
    }
    
    - (void)testPerformanceExample {
        [self measureBlock:^{
        }];
    }
    @end
    

#### 2.4、逻辑测试

接下来我们开始编写用例，来测试ZJHMathTool中的方法，如下所示

    
    
    @interface ZJHMathToolTests : XCTestCase
    @property (nonatomic, strong) ZJHMathTool *mathTool;
    @end
    
    @implementation ZJHMathToolTests
    
    // 新建ZJHMathTool对象
    - (void)setUp {
        self.mathTool = [ZJHMathTool new];
    }
    
    // 销毁ZJHMathTool对象
    - (void)tearDown {
        self.mathTool = nil;
    }
    
    // 测试加法
    - (void)testMathAdd {
        int result = [self.mathTool sumA:2 andB:3];
        XCTAssert(result == 5, @"加法计算出错");
    }
    
    // 测试减法
    - (void)testMathSub {
        int result = [self.mathTool subA:5 andB:2];
        XCTAssert(result == 3, @"减法计算出错");
    }
    
    @end
    

**运行测试用例 ：**

代码编辑器边栏菱形按钮，测试单个用例  
Test 导航栏，测试单个用例  
快捷键 command + U测试全部用例  
使用命令行工具 xcodebuild 可以测试单个用例，也可以测试全部用例

运行测试用例.png

#### 2.5、性能测试

性能测试通过度量代码块执行所消耗的时间长短，来衡量是否通过测试。

##### 2.5.1、测试方法准备

新建 ZJHPerson 类，然后添加一个循环打印方法。

    
    
    @interface ZJHPerson : NSObject
    - (void)sayHello;
    @end
    
    @implementation ZJHPerson
    - (void)sayHello {
        for (int i = 0; i < 1000; i++) {
            NSLog(@"hello");
        }
    }
    @end
    
    

然后再新建 ZJHPerson 对象测试类 ZJHPersonTests。

    
    
    #import <XCTest/XCTest.h>
    #import "ZJHPerson.h"
    
    @interface ZJHPersonTests : XCTestCase
    @property (nonatomic, strong) ZJHPerson *person;
    @end
    
    @implementation ZJHPersonTests
    - (void)setUp {
        self.person = [ZJHPerson new];
    }
    - (void)tearDown {
        self.person = nil;
    }
    - (void)testPerformanceExample {
        [self measureBlock:^{
            [self.person sayHello];
        }];
    }
    @end
    

##### 2.5.2、性能测试API

有两个API可以使用

`-
measureBlock`主要是通过block内部代码块的执行时间来测试性能，通过设置baseline（基准）和stddev（标准偏差）来判断方法是否能通过性能测试。

    
    
    - (void)testPerformanceOfMyFunction {
            [self measureBlock:^{
                //做你想测量的东西。
                MyFunction();
            }];
      }
    

`- measureMetrics:automaticallyStartMeasuring:forBlock`测量代码块的性能，可以选择推迟测量的起点。  
`- startMeasuring`在代码块中开始性能度量。  
`- stopMeasuring`结束代码块内的性能度量。  
`defaultPerformanceMetrics`标识在调用measureBlock:时度量的性能指标。  
`XCTPerformanceMetricXCTest`可以测量的性能指标。

    
    
    - (void)testMyFunction2_WallClockTime {
            [self measureMetrics:[self class].defaultPerformanceMetrics automaticallyStartMeasuring:NO forBlock:^{
                // 做设置工作，需要为每个迭代，但你不希望在调用- startmeasurement之前进行测量
                SetupSomething();
                [self startMeasuring];
    
                // 做你想测量的东西。
                MyFunction();
                [self stopMeasuring];
    
                //执行每次迭代都需要执行的分解工作，但你不想在调用- stopmeasurement后进行度量
                TeardownSomething();
            }];
        }
    

##### 2.5.3、设置基准线

所有的性能测试需要设置一个`Baseline`来验证是否通过测试，没有设置的会提示`No baseline average for
Time`。点击左边灰色菱形图标可查看性能测试结果。

设置Baseline基准线.png

在性能测试结果图里可以看到平均时间（总时长/10），还有10个柱状图，这个意思是在这个测试方法运行总时长被分为10份，蓝色柱子表示每份的耗时，中间的横线表示平均时间，点击数字可查看每份中的平均时长。

  * Metric：度量单位，Time为时间
  * Result：度量结果
  * Average：度量时间平均值
  * Baseline：度量的基准线
  * Max STDDEV：最大容错率

点击`Edit`可以进行编辑，我设置的基准时间是`0.15s`，最大容错率是10%，运行结果是`0.147s`,好于基本先`2%`,所有可以通过。设置时基准时间为`0.05s`时就会出错。

性能测试成功和失败.png

#### 2.6、异步测试

什么时候需要使用异步测试：

  * 打开文档
  * 在后台线程中执行的服务和网络活动
  * 执行动画
  * UI 测试时

##### 2.6.1 异步测试XCTestExpectation

异步测试分为3个部分： **新建期望** 、 **等待期望被履行** 和 **履行期望** 。

  * XCTestExpectation：测试期望，可以由测试类持有，也可以自己持有，自己持有测试期望时灵活性更好一些，你可以选择等待哪些期望。

  * waitForExpectations:timeout: ：等待异步的期望代码执行，根据初始化方式不同，等待的方法不同。

  * fulfill ：履行期望，并且适当加入XCTAssertTrue等断言，来验证测试结果。

    
    
    /// 异步测试XCTestExpectation：测试类持有期望
    - (void)testAsyncMethod1 {
        // 新建期望：测试类持有的初始化方法
        XCTestExpectation *expect1 = [self expectationWithDescription:@"asyncTest1"];
    
        // 履行期望：执行异步操作
        [ZJHNetworkTool requestUrl:@"getTestData" param:@{} completion:^(NSDictionary * _Nonnull respondDic) {
            // 异步结束，标注期望达成
            [expect1 fulfill];
        }];
        
        // 等待期望被履行：测试类持有时的等待方法
        [self waitForExpectationsWithTimeout:3.0 handler:^(NSError * _Nullable error) {
            NSLog(@"***ZJH error : %@", error);
        }];
    }
    
    /// 异步测试XCTestExpectation：自己类持有期望
    - (void)testAsyncMethod2 {
        // 新建期望：自己持有的初始化方法
        XCTestExpectation *expect2 = [[XCTestExpectation alloc] initWithDescription:@"asyncTest2"];
        
        
        // 履行期望：执行异步操作
        [ZJHNetworkTool requestUrl:@"getTestData" param:@{} completion:^(NSDictionary * _Nonnull respondDic) {
            XCTAssertTrue([respondDic[@"code"] isEqualToString:@"200"]);
            // 异步结束，标注期望达成
            [expect2 fulfill];
        }];
    
        // 等待期望被履行：自己持有时的等待方法
        [self waitForExpectations:@[expect2] timeout:3];
    }
    

##### 2.6.2 异步测试XCTWaiter

XCTWaiter是 2017 年新增的异步测试方案，可以通过代理方式来处理异常情况。

XCTWaiterDelegate：如果委托是XCTestCase实例，下方代理被调用时会报告为测试失败。

    
    
    /// 异步测试XCTWaiter
    - (void)testAsyncMethod3 {
        // 新建期望
        XCTWaiter *waiter = [[XCTWaiter alloc] initWithDelegate:self];
        XCTestExpectation *expect3 = [[XCTestExpectation alloc] initWithDescription:@"asyncTest3"];
            
        // 履行期望：执行异步操作
        [ZJHNetworkTool requestUrl:@"getTestData" param:@{} completion:^(NSDictionary * respondDic) {
            XCTAssertTrue([respondDic[@"code"] isEqualToString:@"200"]);
            // 异步结束，标注期望达成
            [expect3 fulfill];
        }];
    
        // 等待期望被履行
        XCTWaiterResult result = [waiter waitForExpectations:@[expect3]
                                                     timeout:3
                                                enforceOrder:NO];
    
        XCTAssert(result == XCTWaiterResultCompleted, @"failure: %ld", result);
    }
    
    // 如果有期望超时，则调用。
    - (void)waiter:(XCTWaiter *)waiter didTimeoutWithUnfulfilledExpectations:(NSArray<XCTestExpectation *> *)unfulfilledExpectations {
        NSLog(@"***ZJH 如果有期望超时，则调用。");
    }
    
    // 当履行的期望被强制要求按顺序履行，但期望以错误的顺序被履行，则调用。
    - (void)waiter:(XCTWaiter *)waiter fulfillmentDidViolateOrderingConstraintsForExpectation:(XCTestExpectation *)expectation requiredExpectation:(XCTestExpectation *)requiredExpectation {
        NSLog(@"***ZJH 当履行的期望被强制要求按顺序履行，但期望以错误的顺序被履行，则调用。");
    }
    
    // 当某个期望被标记为被倒置，则调用。
    - (void)waiter:(XCTWaiter *)waiter didFulfillInvertedExpectation:(XCTestExpectation *)expectation {
        NSLog(@"***ZJH 当某个期望被标记为被倒置，则调用。");
    }
    
    // 当 waiter 在 fullfill 和超时之前被打断，则调用。
    - (void)nestedWaiter:(XCTWaiter *)waiter wasInterruptedByTimedOutWaiter:(XCTWaiter *)outerWaiter {
        NSLog(@"***ZJH 当 waiter 在 fullfill 和超时之前被打断，则调用。");
    }
    

### 三、其他补充

#### 3.1、断言记录

在写测试用例的时候，我们可以使用断言，下面是记录一下：

    
    
    XCTFail(format…) 生成一个失败的测试； 
     
    XCTAssertNil(a1, format...)为空判断，a1为空时通过，反之不通过； 
     
    XCTAssertNotNil(a1, format…)不为空判断，a1不为空时通过，反之不通过；
     
    XCTAssert(expression, format...)当expression求值为TRUE时通过； 
     
    XCTAssertTrue(expression, format...)当expression求值为TRUE时通过； 
     
    XCTAssertFalse(expression, format...)当expression求值为False时通过； 
     
    XCTAssertEqualObjects(a1, a2, format...)判断相等，[a1 isEqual:a2]值为TRUE时通过，其中一个不为空时，不通过；
     
    XCTAssertNotEqualObjects(a1, a2, format...)判断不等，[a1 isEqual:a2]值为False时通过；
     
    XCTAssertEqual(a1, a2, format...)判断相等（当a1和a2是 C语言标量、结构体或联合体时使用,实际测试发现NSString也可以）； 
     
    XCTAssertNotEqual(a1, a2, format...)判断不等（当a1和a2是 C语言标量、结构体或联合体时使用）；
     
    XCTAssertEqualWithAccuracy(a1, a2, accuracy, format...)判断相等，（double或float类型）提供一个误差范围，当在误差范围（+/-accuracy）以内相等时通过测试； 
     
    XCTAssertNotEqualWithAccuracy(a1, a2, accuracy, format...) 判断不等，（double或float类型）提供一个误差范围，当在误差范围以内不等时通过测试； 
     
    XCTAssertThrows(expression, format...)异常测试，当expression发生异常时通过；反之不通过；（很变态） XCTAssertThrowsSpecific(expression, specificException, format...) 异常测试，当expression发生specificException异常时通过；反之发生其他异常或不发生异常均不通过； 
     
    XCTAssertThrowsSpecificNamed(expression, specificException, exception_name, format...)异常测试，当expression发生具体异常、具体异常名称的异常时通过测试，反之不通过； 
     
    XCTAssertNoThrow(expression, format…)异常测试，当expression没有发生异常时通过测试；
     
    XCTAssertNoThrowSpecific(expression, specificException, format...)异常测试，当expression没有发生具体异常、具体异常名称的异常时通过测试，反之不通过； 
     
    XCTAssertNoThrowSpecificNamed(expression, specificException, exception_name, format...)异常测试，当expression没有发生具体异常、具体异常名称的异常时通过测试，反之不通过
     
     
    特别注意下XCTAssertEqualObjects和XCTAssertEqual。
     
    XCTAssertEqualObjects(a1, a2, format...)的判断条件是[a1 isEqual:a2]是否返回一个YES。
     
    XCTAssertEqual(a1, a2, format...)的判断条件是a1 == a2是否返回一个YES。
     
    对于后者，如果a1和a2都是基本数据类型变量，那么只有a1 == a2才会返回YES。例如
    

#### 3.2、查看代码覆盖率

##### 3.2.1、Edit Scheme 勾选配置

`Command+shit+,` 调出工程配置 Test->Options->Code Coverage勾选上

Edit Scheme 勾选配置.png

##### 3.2.2、结果查看

运行测试后，`command+9`或 者点击工程左上角最后一个图标查看覆盖报告

查看代码覆盖率.png

##### 3.2.3、代码查看

双击方法名或者点击方法名右侧的箭头可以跳转到该方法中。右侧有数字，0表示没有覆盖掉，1表示覆盖了一次，调用了几次数字就会变成几。

代码查看结果.png

#### 3.3、跳过部分测试

在 Xcode 10 中新增功能，在 Edit Scheme -> Test -> Info -> Tests
中可以通过取消勾选，来选择跳过部分测试用例。在 target 的 Options 选项中，`Automatically includes new
tests`，选项是默认勾选的，新建的测试文件会自动添加进去。

跳过部分测试.png

#### 3.4、测试用例的执行顺序

默认情况下，测试用例执行的顺序是按字母顺序来执行的，按固定顺序执行可能会使一些隐式的依赖关系无法被发现。现在有了随机的执行顺序，就可以挖掘出那些隐式的依赖关系。可以在
Edit Scheme -> Test -> Info -> Tests -> Options 中开启该功能。

执行顺序和并行设置.png

#### 3.5、并行测试

并行测试可以同时进行多个测试，从而节省大量时间。在测试时会启动多个模拟器，模拟器之间的数据都是隔离的，可以在 Edit Scheme -> Test ->
Info -> Tests -> Options 中开启该功能。如上图

对于并行测试的一些建议：

  * 某个测试用例需要消耗大量时间的类，可以拆分成多个类并行测试，从而节省时间。
  * 你需要清楚哪些测试在并行执行时是不安全的，避免并行执行这些测试。
  * 性能测试的可以统一放在一个 Bundle 中，禁用并行执行。

  
  
参考链接：  
iOS单元测试：<https://www.jianshu.com/p/fcd82723f134>  
iOS开发之单元测试：<https://www.jianshu.com/p/6f4f9fe5f1e1>  
iOS 单元测试和 UI
测试快速入门：[https://juejin.cn/post/6844903744170098695](https://links.jianshu.com/go?to=https%3A%2F%2Fjuejin.cn%2Fpost%2F6844903744170098695)  
iOS单元测试：[https://juejin.cn/post/6844904138388537352](https://links.jianshu.com/go?to=https%3A%2F%2Fjuejin.cn%2Fpost%2F6844904138388537352)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [单元测试 Tests 的简介及使用](https://www.jianshu.com/p/1afe285b3331)

![Upload Snip20161222_3.png failed. Please try again.]](h...

[小苗晓雪](https://www.jianshu.com/u/86fe5f74c2ba)阅读 692评论 0赞 0

  * [iOS单元测试的日常使用](https://www.jianshu.com/p/232ef187c957)

做开发的时候经常听到一个词“单元测试”，很多人听到这个词就觉得是个测试，功能开发完了就在模拟器或者真机上跑一次，点...

[栋柠柒](https://www.jianshu.com/u/b99917ead654)阅读 596评论 0赞 0

  * [在项目中使用单元测试](https://www.jianshu.com/p/a67645c58084)

随着项目增加的功能越来越多，渐渐的有一个问题是我们不能不考虑的，就是每次当我们增加了新功能，或者对某些地方做了优化...

[思绪_HY](https://www.jianshu.com/u/c9f1a84e9513)阅读 1,564评论 0赞 2

  * [iOS单元测试-05-单元测试初探](https://www.jianshu.com/p/9bd18fc12da5)

前言前面四篇文章认识了单元测试，了解了单元测试的简单使用方法，后面的文章将会介绍单元测试的更加全面的使用准则以及具...

[修_远](https://www.jianshu.com/u/1f233a6c382c)阅读 551评论 3赞 2

  * [iOS-单元测试汇总](https://www.jianshu.com/p/d7a515dd10de)

原文地址： https://www.jianshu.com/p/4001e06b150e 前言： 对于单元测试来说...

[chrisLL](https://www.jianshu.com/u/e53614fd0a99)阅读 537评论 0赞 0

 