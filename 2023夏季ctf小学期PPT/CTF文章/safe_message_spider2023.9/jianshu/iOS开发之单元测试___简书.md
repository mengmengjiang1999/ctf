iOS开发之单元测试

[ 夜凉听风雨](https://www.jianshu.com/u/713d200930fb)关注赞赏支持

# iOS开发之单元测试

教学视频：  
[https://www.bilibili.com/video/BV1y4411X7Qt?p=1](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.bilibili.com%2Fvideo%2FBV1y4411X7Qt%3Fp%3D1)  
参考博客：  
[https://blog.csdn.net/cwhzm/article/details/72598803](https://links.jianshu.com/go?to=https%3A%2F%2Fblog.csdn.net%2Fcwhzm%2Farticle%2Fdetails%2F72598803)  
<https://www.jianshu.com/p/c54f0cc08c20>

## 什么是单元测试？

>
> 单元测试是开发者编写的一小段代码，用于检验被测代码中的一个很明确的功能是否正确。通常而言，一个单元测试是用于判断某个特定条件（或者场景）下某个特定函数的行为。  
>
> 执行单元测试，是为了证明某段代码的行为确实和开发者所期望的一致。因此，我们所要测试的是规模很小的、非常独立的功能片段。通过对所有单独部分的行为建立起信心。然后，才能开始测试整个系统

## 单元测试好处

对比图.png

  * **好处：**  
1、单元测试使工作完成的更轻松  
2、经过单元测试的代码，质量能够得到保证  
3、单元测试发现的问题很容易定位。  
4、修改代码犯的错，经过单元测试易发现  
5、单元测试可以在早期就发现性能问题  
6、单元测试使你的设计更好  
7、大大减少花在调试上的时间

## 创建项目

新建项目时要勾选Include Tests选项

新建项目.png

新建一对Person类文件

Person.h文件代码

    
    
    #import <Foundation/Foundation.h>
    
    NS_ASSUME_NONNULL_BEGIN
    
    @interface Person : NSObject
    
    @property (nonatomic, strong) NSString *name;
    @property (nonatomic, assign) NSInteger age;
    
    - (instancetype)initWithInfo:(NSDictionary *)info;
    
    @end
    
    NS_ASSUME_NONNULL_END
    

Person.m文件内代码

    
    
    #import "Person.h"
    
    @implementation Person
    
    - (instancetype)initWithInfo:(NSDictionary *)info {
        self = [super init];
        if (self) {
            self.name = info[@"name"];
            self.age = [info[@"age"] integerValue];
        }
        return self;
    }
    
    @end
    

## 逻辑测试

为Person文件新建单元测试类文件

新建步骤.png

取名一般是需要测试的类名+Tests，这里我新建了一个PersonTests文件。

生成文件.png

新建的PersonTests文件代码如下图所示，系统自动生成了几个方法

  * **setUp**  
每个类中 测试方法调用前 先调用这个方法 以方便 开发者 做些 测试前的准备

  * **tearDown**  
当这个 类中的 所有的 测试 方法 测试完后 会调用这个方法

PersonTests文件代码.png

PersonTests文件内新增一个测试方法，用来测试Person类的`- (instancetype)initWithInfo:(NSDictionary
*)info`方法

先引入Person类`#import "Person.h"`

    
    
    - (void)testInitPerson {
        NSDictionary *dic = @{@"name" : @"Jonas", @"age" : @25};
        Person *p = [[Person alloc] initWithInfo:dic];
        NSAssert([p.name isEqualToString:dic[@"name"]], @"姓名不一致");
        NSAssert(p.age == [dic[@"age"] integerValue], @"年龄不一致");
    }
    

点击测试方法左侧的菱形按钮开始单独测试这一个方法。

image.png

或者按组合键Command+U运行所有测试文件，经过一段时间后，看到方法左边有个绿色的勾则表示通过测试，有一个红色的叉表示未通过。

测试通过.png

下面我故意将年龄写错，制造错误

测试未通过.png

控制台也会打印错误信息

错误信息.png

下面是一些常用的断言

    
    
    XCTFail(@"this is a fail test");  // 生成一个失败的测试
    
    XCTAssertNil(@"not a nil string",@"string must be nil"); // XCTAssertNil(a1, format...) 为空判断， a1 为空时通过，反之不通过；
    
    XCTAssertNil(@"",@"string must be nil");  // 注意@"" 一样无法通过
    
    XCTAssertNil(nil,@"object must be nil");
    
    XCTAssertNotNil(a1, format…) 不为nil 判断，a1不为  nil 时通过，反之不通过；
    
    // 注意空  和 nil 还是有区别的
    XCTAssertNotNil(@"not nil string", @"string can not be nil");
    
    XCTAssert(expression, format...) // 当expression求值为TRUE时通过； expression 为一个表达式
    
    XCTAssert((2 > 2), @"expression must be true");
    
    XCTAssert((3>2),@"expression is true");
    
    XCTAssertTrue(expression, format...) // 当expression求值为TRUE时通过；>0 的都视为 true
    
    XCTAssertTrue(1, @"Can not be zero");
    
    XCTAssertFalse(expression, format...) 当expression求值为False时通过；
    
    XCTAssertFalse((2 < 2), @"expression must be false");
    
    XCTAssertEqualObjects(a1, a2, format...) // 判断相等， [a1 isEqual:a2] 值为TRUE时通过，其中一个不为空时，不通过；
    
    XCTAssertEqualObjects(@"1", @"1", @"[a1 isEqual:a2] should return YES");
    
    XCTAssertEqualObjects(@"1", @"2", @"[a1 isEqual:a2] should return YES");
    
    XCTAssertNotEqualObjects(a1, a2, format...) 判断不等， [a1 isEqual:a2] 值为False时通过，
    
    XCTAssertNotEqualObjects(@"1", @"1", @"[a1 isEqual:a2] should return NO");
    
    XCTAssertNotEqualObjects(@"1", @"2", @"[a1 isEqual:a2] should return NO");
    
    XCTAssertEqual(a1, a2, format...) // 判断相等（当a1和a2是 C语言标量、结构体或联合体时使用,实际测试发现NSString也可以）；
    
    // 1.比较基本数据类型变量
    XCTAssertEqual(1, 2, @"a1 = a2 shoud be true"); // 无法通过测试
    
    XCTAssertEqual(1, 1, @"a1 = a2 shoud be true"); // 通过测试
    
    // 2.比较NSString对象
    NSString *str1 = @"1";
    NSString *str2 = @"1";
    //    NSString *str3 = str1;
    XCTAssertEqual(str1, str2, @"a1 and a2 should point to the same object"); // 通过测试
    XCTAssertEqual(str1, str3, @"a1 and a2 should point to the same object"); // 通过测试
    
    // 3.比较NSArray对象
     NSArray *array1 = @[@1];
     NSArray *array2 = @[@1];
     NSArray *array3 = array1;
    
    XCTAssertEqual(array1, array2, @"a1 and a2 should point to the same object"); // 无法通过测试
    
    XCTAssertEqual(array1, array3, @"a1 and a2 should point to the same object"); // 通过测试
    
    XCTAssertNotEqual(a1, a2, format...) // 判断不等（当a1和a2是 C语言标量、结构体或联合体时使用）；
    
    XCTAssertEqualWithAccuracy(a1, a2, accuracy, format...) // 判断相等，（double或float类型）提供一个误差范围，当在误差范围（+/- accuracy ）以内相等时通过测试；
    
    XCTAssertEqualWithAccuracy(1.0f, 1.5f, 0.25f, @"a1 = a2 in accuracy should return NO");  // 测试没法通过
    
     XCTAssertNotEqualWithAccuracy(a1, a2, accuracy, format...) // 判断不等，（double或float类型）提供一个误差范围，当在误差范围以内不等时通过测试；
    
    XCTAssertNotEqualWithAccuracy(1.0f, 1.5f, 0.25f, @"a1 = a2 in accuracy should return NO");  // 测试通过 
    
    XCTAssertThrows(expression, format...) // 异常测试，当expression发生异常时通过；反之不通过；（很变态）
    
     XCTAssertThrowsSpecific(expression, specificException, format...) // 异常测试，当expression发生 specificException 异常时通过；反之发生其他异常或不发生异常均不通过；
    
    XCTAssertThrowsSpecificNamed(expression, specificException, exception_name, format...) // 异常测试，当expression发生具体异常、具体异常名称的异常时通过测试，反之不通过；
    
    XCTAssertNoThrow(expression, format…) // 异常测试，当expression没有发生异常时通过测试；
    
    XCTAssertNoThrowSpecific(expression, specificException, format...) // 异常测试，当expression没有发生具体异常、具体异常名称的异常时通过测试，反之不通过；
    
    XCTAssertNoThrowSpecificNamed(expression, specificException, exception_name, format...) // 异常测试，当expression没有发生具体异常、具体异常名称的异常时通过测试，反之不通过
    
    

## 性能测试

先为Person类添加一个循环打印方法。

    
    
    - (void)sayHello {
        for (int i = 0; i < 1000; i++) {
            NSLog(@"hello");
        }
    }
    

PersonTests.m文件代码如下：

性能测试代码.png

第一次运行测试代码后如下所示，点击左边灰色菱形图标可查看性能测试结果

第一次运行测试.png

在性能测试结果图里可以看到平均时间（总时长/10），还有10个柱状图，这个意思是在这个测试方法运行总时长被分为10份，蓝色柱子表示每份的耗时，中间的横线表示平均时间，点击数字可查看每份中的平均时长。

性能测试结果图.png

点击Set Baseline可以为该性能测试增加基准线，再点击Edit按钮可设置基准线和最大容错率。现在我设置的基准线是0.1
s最大容错率是10%。所以如果平均时间超过0.11 s就报错。

测试结果图.png

可以看到重新运行后，超过了130%，所以会报错。

测试未通过.png

## 异步测试

Person类定义一个异步耗时方法

    
    
    + (void)asyncMethodWithCompletion:(void (^)(void))completion {
        dispatch_async(dispatch_get_global_queue(0, 0), ^{
            for (int i = 0; i < 10000; i++) {
                NSLog(@"hello");
            }
            dispatch_async(dispatch_get_main_queue(), ^{
                if(completion) {
                    completion();
                }
            });
        });
    }
    

测试文件定义一个测试异步方法

    
    
    - (void)testAsyncMethod {
        // 定义一个预期
        XCTestExpectation *exp = [self expectationWithDescription:@"Person异步方法的期望"];
        [Person asyncMethodWithCompletion:^{
            // 异步结束，标注期望达成
            [exp fulfill];
        }];
        // 等待期望异步执行完，若在2秒内完成，则通过，否则不通过
        [self waitForExpectationsWithTimeout:2 handler:^(NSError * _Nullable error) {
            // 期望回调，根据error是否为空可知是否通过
        }];
    }
    

运行测试方法，在期望时间内通过则出现绿勾，否则出现红叉。

## UI测试

新建UI测试文件

image.png

image.png

将UI测试文件从Tests文件夹挪到UITests文件夹

文件挪动.png

首先Command+R运行项目，运行完成后将光标置于UI测试方法内，然后点击左下角红色录制按钮，项目又会运行一次，在界面上做一系列操作会在UI测试方法内自动生成代码，操作完成后点击左下角停止录制按钮。

录制过程.gif

录制中自动生成的代码如下所示，但是发现会有点问题，每次按键点击都写了2次，所以我们手动删掉一次。

**注意：这里有一个坑，如果直接运行这段代码，会报错，因为第一个A键点击后模拟器的键盘上A按键会变成小写的a按键，此时点击第二次A键时就会报错键盘上找不到这个A按键。**

    
    
    - (void)testViewControllerInputUI {
        
        
        XCUIApplication *app = [[XCUIApplication alloc] init];
        [[[[[[app.windows childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeTextField] elementBoundByIndex:0] tap];
        
        XCUIElement *aKey = app.keys[@"A"];
        [aKey tap];
        [aKey tap];
        
        XCUIElement *sKey = app.keys[@"s"];
        [sKey tap];
        [sKey tap];
        
        XCUIElement *dKey = app.keys[@"d"];
        [dKey tap];
        [dKey tap];
        
        XCUIElement *fKey = app.keys[@"f"];
        [fKey tap];
        [fKey tap];
        
        XCUIElement *element = [[[[[app childrenMatchingType:XCUIElementTypeWindow] elementBoundByIndex:0] childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element;
        [[[element childrenMatchingType:XCUIElementTypeTextField] elementBoundByIndex:1] tap];
        
        XCUIElement *zKey = app.keys[@"Z"];
        [zKey tap];
        [zKey tap];
        
        XCUIElement *xKey = app.keys[@"x"];
        [xKey tap];
        [xKey tap];
        
        XCUIElement *cKey = app.keys[@"c"];
        [cKey tap];
        [cKey tap];
        [[element childrenMatchingType:XCUIElementTypeButton].element tap];
            
    }
    

修改后代码

    
    
    - (void)testViewControllerInputUI {
        
        
        XCUIApplication *app = [[XCUIApplication alloc] init];
        [[[[[[app.windows childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeTextField] elementBoundByIndex:0] tap];
        
        XCUIElement *aKey = app.keys[@"A"];
        [aKey tap];
        
        XCUIElement *sKey = app.keys[@"s"];
        [sKey tap];
        
        XCUIElement *dKey = app.keys[@"d"];
        [dKey tap];
        
        XCUIElement *fKey = app.keys[@"f"];
        [fKey tap];
        
        XCUIElement *element = [[[[[app childrenMatchingType:XCUIElementTypeWindow] elementBoundByIndex:0] childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element;
        [[[element childrenMatchingType:XCUIElementTypeTextField] elementBoundByIndex:1] tap];
        
        XCUIElement *zKey = app.keys[@"Z"];
        [zKey tap];
        
        XCUIElement *xKey = app.keys[@"x"];
        [xKey tap];
        
        XCUIElement *cKey = app.keys[@"c"];
        [cKey tap];
        [[element childrenMatchingType:XCUIElementTypeButton].element tap];
            
    }
    

当然我们也可以自己写UI测试的代码，想执行什么操作就写什么代码。下面的代码就是我自己写了段点击tf1输入abcdefg然后点击tf2输入12345，然后点击2次删除键后点击按钮。可以发现自己写的代码逻辑要更清晰一些，代码也要更美观。

    
    
    - (void)testViewControllerInputUI {
        
        
        XCUIApplication *app = [[XCUIApplication alloc] init];
        
        XCUIElement *tf1 = [[[[[app.windows childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeTextField] elementBoundByIndex:0];
        [tf1 tap];
        [tf1 typeText:@"abcdefg"];
        
        XCUIElement *tf2 = [[[[[app.windows childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeTextField] elementBoundByIndex:1];
        [tf2 tap];
        [tf2 typeText:@"12345"];
        
        XCUIElement *deleteKey = app.keys[@"delete"];
        [deleteKey tap];
        [deleteKey tap];
        
        XCUIElement *button = [[[[app.windows childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeOther].element childrenMatchingType:XCUIElementTypeButton].element;
        [button tap];
    }
    

点击测试方法左边的灰色菱形按钮，开始测试UI，可以看到手机会自动的执行代码描述的行为。运行测试方法前需要先运行项目，不想每次都自己运行，可以在`-
(void)setUp`方法里加上运行app代码`[[[XCUIApplication alloc] init]
launch];`这样运行测试代码就会自动运行项目了。

测试过程.gif

## 查看测试覆盖率

Command+shit+, 调出工程配置 Test->Options->Code Coverage勾选上

工程配置.png

运行测试后，command+9或者点击工程左上角最后一个图标查看覆盖报告

覆盖日志.png

双击方法名或者点击方法名右侧的箭头可以跳转到该方法中。

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [iOS开发之单元测试](https://www.jianshu.com/p/ed5e7bcd55b4)

本文侧重讲述如何在iOS程序的开发过程中使用单元测试。使用Xcode自带的OCUnit作为测试框架。 一、单元测试...

[Cooci_和谐学习_不急不躁](https://www.jianshu.com/u/5981a4f71db5)阅读 1,022评论 0赞 2

  * [iOS 单元测试--逻辑测试](https://www.jianshu.com/p/15f347eb207c)

单元测试分为3种： 逻辑测试：测试逻辑方法 异步测试：测试耗时方法（用来测试包含多线程的方法） 性能测试：测试某一...

[爱自由鹏](https://www.jianshu.com/u/89ece537c953)阅读 3,423评论 7赞 26

  * [iOS 单元测试规范](https://www.jianshu.com/p/b2ec82bd466a)

一、简介[https://www.jianshu.com/writer#%E4%B8%80%E7%AE%80%E4...

[豆宝的老公](https://www.jianshu.com/u/f6264206fc47)阅读 773评论 0赞 1

  * [iOS开发之进阶篇（6）—— 单元测试（Unit Tests 和 UI Tests）](https://www.jianshu.com/p/0b2b10ce376e)

版本 Xcode 11.5 目录 概念 准备工作 Unit Tests UI Tests 1. 概念 1.1 单元...

[看影成痴](https://www.jianshu.com/u/83ecdf2d05e0)阅读 473评论 0赞 3

  * [在iOS程序开发过程中，如何完成单元测试？](https://www.jianshu.com/p/9938c650cdcc)

一、单元测试概述 单元测试作为敏捷开发实践的组成之一，其目的是提高软件开发的效率，维持代码的健康性。其目标是证明软...

[博为峰2004](https://www.jianshu.com/u/8acfa1e11f95)阅读 461评论 0赞 3

 