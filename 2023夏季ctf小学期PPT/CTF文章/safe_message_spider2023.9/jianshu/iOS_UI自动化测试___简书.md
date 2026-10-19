iOS UI自动化测试

[ loongod](https://www.jianshu.com/u/3209fda51a9a)关注赞赏支持

# iOS UI自动化测试

### UI testing

找到交互的UI控件，检测UI控件的属性和状态

生成测试报告，包括每步的截图

核心技术包括XCTest 和 Accessibility

##### XCTest

Xcode's testing framework

##### Requirements

UI testing depends on new OS features

  * iOS 9
  * OS X 10.11

* * *

### Getting Started

  * Xcode target type
  * APIs
  * UI recording

##### UI Testing Xcode Targets

UI tests have special requirements

  * Execute in aseparate process
  * Permission to use Accessibility

New Xcode target templates

  * Cocoa Touch UI Testing Bundle(iOS)
  * Cocoa UI Testing Bundle (OS X)

##### APIs

Three new classes

  * XCUIApplication
  * XCUIElement
  * XCUIElementQuery

##### UI Recording

Recording generates the code

  * Create new tests
  * Expand existing tests

### 控件和查询

##### Element Uniqueness

Every XCUIElement is backed by a query  
Query must resolve to exactly one match

  * No matches or multiple matches cause test failure
  * Failure raised when element resolves query  
Exception

  * Exists property

##### XCUIElementQuery

API for specifying elements  
Queries resolve to collections of accessible elements

  * Number of matches: count
  * Specify by identifier: subscripting
  * Specify by index: elementAtIndex()

How do queries work?

  * Relationships
  * Filtering

##### Expressing relationships

Descendants  
Children  
Containment

##### Filtering

过滤方式 | 方式类型  
---|---  
Element type | Button,table,menu.etc  
Identifiers | Accessibility identifier,label,title,etc  
Predicates | Value,partial matching,etc  
  
### Combining Relationships and Filtering

##### descandantsMatchingType()

    
    
    let allButtons = app.descendantsMatchingType(.Button)
    
    let allCellsInTable = table.descendantsMatchingType(.Cell)
    
    let allMenuItemsInMenu = menu.descendantsMatchingType(.MenuItem)
    
    
    
    So common, wo provide convenience API for each type
    let allButtons = app.buttons
    let allCellsInTables = table.cells
    let allMenuItemsInMenu = menu.menuItems
    

##### childrenMatchingType()

Differentiates between any descendant and a direct child relationship

    
    
    let allButtons = app.buttons //descendantsMatchingType(.Button)
    
    let childButtons = navBar.childrenMatchingType(.Button)
    

##### containingType()

Find elements by describing their descendants

屏幕快照 2018-02-08 下午1.33.17.png

    
    
    let cellQuery = cells.containingType(.StaticText, identifier:"Groceries")
    
    descendantsMatchingType()
    childrenMatchingType()
    containingType()
    这三个方法也可以同样的方式使用
    

##### Combining Queries

Queries can be "chained" together  
Output of each query is the input of the next query

屏幕快照 2018-02-08 下午1.39.28.png

    
    
    let labelsInTables = app.tables.staticTest
    

##### Getting Elements from Queries

方式 | 示例  
---|---  
Subscripting | `table.staticTests["Groceries"]`  
Index | `table.staticTests.elementAtIndex(0)`  
Unique | `app.navigationBars.element`  
  
* * *

### 生成截图

我运行完之后，发现没有图片生成

  

屏幕快照 2018-02-08 下午2.07.27.png

需要去scheme中的text设置

  

text设置

* * *

### 使用终端测试

    
    
    xcodebuild test -workspace UITerminalDemo.xcworkspace 
    -scheme UITerminalDemoUITests 
    -destination 'platform=iOS Simulator,name=iPhone X,OS=11.2' 
    

下面是destination的可用值：  
（也是可以用真机的，下面的第一条就是我自己的手机，需要连接上）

    
    
    Available destinations for the "UITerminalDemoUITests" scheme:
            { platform:iOS, id:86c38f55392f78e1c14ee5b1e5e547492075df20, name:许龙的 iPhone }
            { platform:iOS Simulator, id:E5186B36-BD50-412D-8AD2-E9A1E1F3AB9C, OS:10.3.1, name:iPad (5th generation) }
            { platform:iOS Simulator, id:9AE98D1F-49F6-4D56-BB17-B5D474941C5D, OS:11.2, name:iPad (5th generation) }
            { platform:iOS Simulator, id:3293AA96-0573-4316-8FC5-7B14559F3E20, OS:10.3.1, name:iPad Air }
            { platform:iOS Simulator, id:44E080B6-B931-42BF-988D-E55345DBF8CB, OS:11.2, name:iPad Air }
            { platform:iOS Simulator, id:288C496A-3AF2-413E-B816-71BE66AE8124, OS:10.3.1, name:iPad Air 2 }
            { platform:iOS Simulator, id:7420C15C-05CC-4C55-AA38-6A5D5E0CCF3B, OS:11.2, name:iPad Air 2 }
            { platform:iOS Simulator, id:21C6851F-2F5E-4F8F-BCEF-51878F70986C, OS:10.3.1, name:iPad Pro (9.7 inch) }
            { platform:iOS Simulator, id:8C328212-6A92-4F42-9DBD-DBB1E040EE08, OS:11.2, name:iPad Pro (9.7-inch) }
            { platform:iOS Simulator, id:2F7428EE-C4AE-4D31-A273-0AE1F88C95E6, OS:10.3.1, name:iPad Pro (10.5-inch) }
            { platform:iOS Simulator, id:D53E887B-2704-4919-9E8E-10E7B0B69DFA, OS:11.2, name:iPad Pro (10.5-inch) }
            { platform:iOS Simulator, id:FC2CCFC2-E298-4334-B66D-9D1E9E3F98E2, OS:10.3.1, name:iPad Pro (12.9 inch) }
            { platform:iOS Simulator, id:B6990DA0-DDA0-4999-AD73-E85D14D1A730, OS:11.2, name:iPad Pro (12.9-inch) }
            { platform:iOS Simulator, id:8AD3E839-1319-4E34-A619-4A1F5C60E202, OS:10.3.1, name:iPad Pro (12.9-inch) (2nd generation) }
            { platform:iOS Simulator, id:82AEFE8B-2DCD-499F-A743-46681C38049A, OS:11.2, name:iPad Pro (12.9-inch) (2nd generation) }
            { platform:iOS Simulator, id:C64ED8D5-F709-4E8F-94FC-B4DB97F906F4, OS:10.3.1, name:iPhone 5 }
            { platform:iOS Simulator, id:8DC1550F-7BD0-443E-8895-9DC074217A60, OS:10.3.1, name:iPhone 5s }
            { platform:iOS Simulator, id:C65A270A-653B-4CC4-AADC-D683D0FEB23A, OS:11.2, name:iPhone 5s }
            { platform:iOS Simulator, id:52DBB418-E842-445A-AB95-398D2D4404CF, OS:10.3.1, name:iPhone 6 }
            { platform:iOS Simulator, id:E3E52BB3-51EA-4E47-A72E-49D281BB8F04, OS:11.2, name:iPhone 6 }
            { platform:iOS Simulator, id:8BEDA513-7394-43BF-8A92-56C47704B5EC, OS:10.3.1, name:iPhone 6 Plus }
            { platform:iOS Simulator, id:45D79B21-EE8D-4C6C-8C68-744D8AB388F5, OS:11.2, name:iPhone 6 Plus }
            { platform:iOS Simulator, id:B1B9D218-C692-4C56-8A6A-E73B81885DB4, OS:10.3.1, name:iPhone 6s }
            { platform:iOS Simulator, id:DBC72166-AC98-4E41-A590-DD76F47EB4BF, OS:11.2, name:iPhone 6s }
            { platform:iOS Simulator, id:21B5972B-5377-431F-8445-0CD00BC66B77, OS:10.3.1, name:iPhone 6s Plus }
            { platform:iOS Simulator, id:FDA53200-DBBD-498A-BB58-2B05B17BD785, OS:11.2, name:iPhone 6s Plus }
            { platform:iOS Simulator, id:33122DBD-44EC-40E1-BE5E-85139F0C5B0F, OS:10.3.1, name:iPhone 7 }
            { platform:iOS Simulator, id:6C2EDE5A-4C66-48C6-844F-9A54873904D4, OS:11.2, name:iPhone 7 }
            { platform:iOS Simulator, id:35112E51-2376-4E21-B49D-34A69FBC8DB7, OS:10.3.1, name:iPhone 7 Plus }
            { platform:iOS Simulator, id:44EB9D0D-9D53-4D34-BEAD-7E8DE3162D2D, OS:11.2, name:iPhone 7 Plus }
            { platform:iOS Simulator, id:09E387B5-C0E6-43D9-9BA8-75E3785280C0, OS:11.2, name:iPhone 8 }
            { platform:iOS Simulator, id:F85B7C01-EB2D-4C9E-98C0-CF466941E6E0, OS:11.2, name:iPhone 8 Plus }
            { platform:iOS Simulator, id:E76E917B-DAFB-4849-BC6E-A2AD8CEDE025, OS:10.3.1, name:iPhone SE }
            { platform:iOS Simulator, id:C3F35392-D7C4-44AF-A9E4-4A79E07B4213, OS:11.2, name:iPhone SE }
            { platform:iOS Simulator, id:2B7D423E-D828-4F13-97F3-A2FE4831BF8D, OS:11.2, name:iPhone X }
    
        Ineligible destinations for the "UITerminalDemoUITests" scheme:
            { platform:iOS, id:dvtdevice-DVTiPhonePlaceholder-iphoneos:placeholder, name:Generic iOS Device }
            { platform:iOS Simulator, id:dvtdevice-DVTiOSDeviceSimulatorPlaceholder-iphonesimulator:placeholder, name:Generic iOS Simulator Device }
    

如果想一次测试多个设备怎么办？  
可以使用链式语法指定多个`-destination`

如果项目使用了Cocoapods的话，也就是打开项目使用的是`.workspace`的话，需要用
`-workspace`，如果不是的话需要用`-project`。

    
    
    xcodebuild test -project MyAppProject.xcodeproj -scheme MyApp
    -destination 'platform=OS X,arch=x86_64'
    -destination 'platform=iOS,name=Development iPod touch'
    -destination 'platform=Simulator,name=iPhone,OS=9.0'
    

如果测试失败，则会返回一个非零的Code码。如果想了解更多的·xcodebuild·命令信息，可以在终端中使用`man xcodebuild`。

##### 生成截图

无需额外的工作，只需添加derivedDataPath选项，记得在scheme配置中不要勾选Delete when each test succeeds

    
    
    xcodebuild test -workspace UITerminalDemo.xcworkspace 
    -scheme UITerminalDemoUITests 
    -destination 'platform=iOS Simulator,name=iPhone X,OS=11.2' 
    -derivedDataPath './test' 
    

截图路径：`./test/Logs/Test/Attachments/`

截图.png

* * *

### 关于查询

##### 导航栏标题的查询

最开始我一直找不到导航栏的标题的Label，最后发现是查询条件的问题，title的类型不是XCUIElementTypeStaticText，而是XCUIElementTypeOther，我是先通过下面的代码找到的

    
    
        XCUIApplication *app = [[XCUIApplication alloc] init];
        NSInteger navigationBarCount = app.navigationBars.count;
        NSLog(@"%ld",navigationBarCount);
        XCUIElement *navigationBar = [app.navigationBars elementBoundByIndex:0];
        XCUIElementQuery *navTitleLabels = [navigationBar descendantsMatchingType:XCUIElementTypeAny];
        NSLog(@"navlabels:%ld",navTitleLabels.count);
        XCUIElement *any = [navTitleLabels elementBoundByIndex:0];
        NSLog(@"description: %@", any.debugDescription);
    
    
    
     description: Attributes: Other, 0x60c0001993d0, traits: 8590000128, {{170.3, 55.7}, {34.7, 20.3}}, label: '首页'
    

可以发现Attributes是Other，下面直接使用XCUIElementTypeOther类型进行查找

    
    
        XCUIApplication *app = [[XCUIApplication alloc] init];
        NSInteger navigationBarCount = app.navigationBars.count;
        NSLog(@"%ld",navigationBarCount);
        XCUIElement *navigationBar = [app.navigationBars elementBoundByIndex:0];
        XCUIElementQuery *navTitleLabels = [navigationBar descendantsMatchingType:XCUIElementTypeOther];
        NSLog(@"navlabels:%ld",navTitleLabels.count);
        XCUIElement *other = [navTitleLabels elementBoundByIndex:0];
        NSLog(@"description: %@", other.debugDescription);
    

打印信息是一样的

    
    
     description: Attributes: Other, 0x60c0001993d0, traits: 8590000128, {{170.3, 55.7}, {34.7, 20.3}}, label: '首页'
    

**所以：** 要找到NavigationBar的标题（系统的）查询类型是XCUIElementTypeOther。

* * *

### 关于检测

##### XCTFail(...)

生成一个无条件的错误，参数...是输出的提示文字（后面类似）。

    
    
    /*!
     * @function XCTFail(...)
     * Generates a failure unconditionally.
     * @param ... An optional supplementary description of the failure. A literal NSString, optionally with string format specifiers. This parameter can be completely omitted.
    */
    #define XCTFail(...) \
        _XCTPrimitiveFail(self, __VA_ARGS__)
    

##### XCTAssert(expression, ...)

当参数expression是false的时候生成一个错误，参数...同上。

    
    
    /*!
     * @define XCTAssert(expression, ...)
     * Generates a failure when ((\a expression) == false).
     * @param expression An expression of boolean type.
     * @param ... An optional supplementary description of the failure. A literal NSString, optionally with string format specifiers. This parameter can be completely omitted.
    */
    #define XCTAssert(expression, ...) \
        _XCTPrimitiveAssertTrue(self, expression, @#expression, __VA_ARGS__)
    
    

通过按住Command+Control，然后点击宏定义，跳进宏定义声明的地方，可查看所有的XCTAssert断言的定义声明。如下

    
    
    /*!
     * @define XCTAssertNil(expression, ...)
     * Generates a failure when ((\a expression) != nil).
     * @param expression An expression of id type.
     * @param ... An optional supplementary description of the failure. A literal NSString, optionally with string format specifiers. This parameter can be completely omitted.
    */
    #define XCTAssertNil(expression, ...) \
        _XCTPrimitiveAssertNil(self, expression, @#expression, __VA_ARGS__)
    
    /*!
     * @define XCTAssertNotNil(expression, ...)
     * Generates a failure when ((\a expression) == nil).
     * @param expression An expression of id type.
     * @param ... An optional supplementary description of the failure. A literal NSString, optionally with string format specifiers. This parameter can be completely omitted.
    */
    #define XCTAssertNotNil(expression, ...) \
        _XCTPrimitiveAssertNotNil(self, expression, @#expression, __VA_ARGS__)
    
    /*!
     * @define XCTAssert(expression, ...)
     * Generates a failure when ((\a expression) == false).
     * @param expression An expression of boolean type.
     * @param ... An optional supplementary description of the failure. A literal NSString, optionally with string format specifiers. This parameter can be completely omitted.
    */
    #define XCTAssert(expression, ...) \
        _XCTPrimitiveAssertTrue(self, expression, @#expression, __VA_ARGS__)
    

##### 使用断言

比如我要判断当前页面，可以通过导航标题来判断

    
    
        NSInteger navigationBarCount = app.navigationBars.count;
        XCUIElement *navigationBar = [app.navigationBars elementBoundByIndex:0];
        XCUIElementQuery *navTitleLabels = [navigationBar descendantsMatchingType:XCUIElementTypeOther];
        XCUIElement *otherNavTitle = [navTitleLabels elementBoundByIndex:0];
        //判断导航标题是不是详情页
        XCTAssert([otherNavTitle.label isEqualToString:@"详情页"]);
    

* * *

### 关于测试用例

在test.m中默认有一个testExample，如果你想新写一个测试方法，注意 **方法名需要用text开头**
。这样才会在方法的左边出现单个方法测试的可点击按钮，如果写完方法没出现，command+U运行下即可。

text.png

点击`@implementation UITests`左边的运行所有测试用例或者command+u。  
发现Xcode运行测试用例是按字母排序的。如果想要按固定顺序执行测试用例，可以在test后追加数字来标记顺序，比如：

    
    
    - (void)test00TabPage {
      //your test0
    }
    
    - (void)test01TabPage {
      //your test1
    }
    
    - (void)test02TabPage {
      //your test2
    }
    
    

参考：

[WWDC15 UI Testing in Xcode PDF
](https://link.jianshu.com?t=http%3A%2F%2Fdevstreaming.apple.com%2Fvideos%2Fwwdc%2F2015%2F406o0doszwo8r15m%2F406%2F406_ui_testing_in_xcode.pdf)

[Testing with
Xcode](https://link.jianshu.com?t=https%3A%2F%2Fdeveloper.apple.com%2Flibrary%2Fcontent%2Fdocumentation%2FDeveloperTools%2FConceptual%2Ftesting_with_xcode%2Fchapters%2F08-automation.html%23%2F%2Fapple_ref%2Fdoc%2Fuid%2FTP40014132-CH7-SW1)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [iOS UI自动化测试](https://www.jianshu.com/p/aae160cb9cc4)

0.小目标 关于UI自动化的定义，我想要的是自动地按照流程去点击页面、输入数据，不需要人去参与，节省人工时间。比如...

[孢子菌](https://www.jianshu.com/u/991b061ba509)阅读 15,212评论 10赞 47

  * [IOS UI自动化测试初探](https://www.jianshu.com/p/1647df9b9ee8)

前言 最近我们的项目赶在圣诞前上线，测试这关一直过不去。我们的项目是一个类似电商项目，因此支付这块一直都是重中之重...

[o翻滚的牛宝宝o](https://www.jianshu.com/u/a27dfbb6d04f)阅读 4,926评论 5赞 7

  * [iOS UI自动化测试初探](https://www.jianshu.com/p/e97d7342d570)

iOS UI Testing Bundle支持Swift和OC Xcode 7之后发布，苹果发布的基于XCTest...

[千枫叶](https://www.jianshu.com/u/db58a2cabb65)阅读 477评论 0赞 1

  * [iOS UI自动化测试框架KIF简单使用](https://www.jianshu.com/p/7918b0e2fdaa)

前言 iOS自动化测试一直不如Android的方便，最近没事看简单看了下，分别基本使用了一下自动化框架Quick和...

[遗忘的黑鹰](https://www.jianshu.com/u/99f4aa72e861)阅读 1,569评论 0赞 2

  * [基于Facebook-WDA的iOS-UI自动化测试](https://www.jianshu.com/p/d21fc1040589)

前面一篇文章讲过，基于Appium-Desktop-WDA的iOSUI自动化测试那么，既然都是基于WDA，区别在于...

[wonderfei](https://www.jianshu.com/u/8e7756036e7e)阅读 10,756评论 2赞 4

 