iOS单元测试及TDD开发

[ 沈枫_SerenF](https://www.jianshu.com/u/02d76422b530)关注赞赏支持

# iOS单元测试及TDD开发

# 单元测试

## 什么是单元测试

本文中Demo：[在这里](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fshcamaker%2FTDDDemo%2Ftree%2Fdevelop)

单元测试（unit testing），是指对软件中的最小可测试单元进行检查和验证。

FIRST 原则

  * Fast：要快。毕竟调试bug时需要频繁运行单元测试验证结果，更快地测试就省去很多时间。

  * Independent / Isolated：隔离性。测试之间相互独立。

  * Repeatable：可重复性。同一个测试，每次测试结果应相同。

  * Self-validating：自我验证。单元测试需要采用Asset函数等进行自验证，即当单元测试执行完毕之后就可得知测试结果(成功 or 失败)，全程无需人工接入。

  * Timely：及时。等代码稳定运行再来补齐单元测试可能是低效的，先编写测试，后编写产品代码才是最有效的方式。

要进行单元测试，前提是要保证代码是“可测试的”。这就要求我们在代码结构设计开始阶段，更好地去思考模块划分是否合理，解耦是否到位，如果能mock掉数据库、网络操作、UI等等，还是可以独立工作的话，那他们之间的耦合程度肯定很低。

那如何松耦合，保证代码可测试性呢？

    
    
    class Dog {
        func eat(foodName: String) {
            print("吃\(foodName)")
        }
    }
    class Person {
        let dog = Dog()
        let foodName = "骨头"
     
        func feed(){
            //其他校验内容
            dog.eat(foodName: foodName)
        }
    }
    

上面的代码就不好测试，主要有以下几个问题：

  * dog，foodName不可控，都是由Person内部自己管理，所以说耦合度很高
  * 没法快速验证dog.eat这个方法是否成功调用

第一个问题通过依赖注入解决：

    
    
    protocol Pet {
        func eat(foodName: String)
    }
    class Dog: Pet {
        func eat(foodName: String) {
            print("吃\(foodName)")
        }
    }
    class Person {
        let pet: Pet
        let foodName: String
     
        init(pet: Pet, foodName: String) {
            self.pet = pet
            self.foodName = foodName
        }
         
        func feed(){
            pet.eat(foodName: foodName)
        }
    

通过依赖注入，外部去创建pet和foodName，无论你是养个狗，还是猫，是喂狗粮还是猫粮，都有外部决定，这样就降低了耦合度。

第二个问题通过Mock解决，所谓Mock就是模拟出我们想要的内容：

    
    
    class MockPet: Pet {
        var wasFeed = false
        func eat(foodName: String) {
            wasFeed = true
        }
    }
     
    func testFeed() {
        let cat = MockPet()
        let james = Person(pet: cat, foodName: "小鱼干")
        james.feed()
        XCTAssertTrue(cat.wasFeed, "james should have feed his cat")
    }
    

就这样，通过一个模拟类，我们就可以很方便地编写asset，标记eat方法已经调用。

## 为什么要做单元测试

我们最开始学习程序编写时，最喜欢干的事情就是编写一段代码，然后run起来，再点击一系列按钮之后到达相关界面去查看结果，如果不对就返回代码检查错误，进行各种调试修改，然后再次运行查看效果是否符合预期。这样一次一次地等待编译部署，启动程序然后操作UI，再一直点到相应的界面去验证结果，难道不是在浪费生命吗？

所以，单元测试必不可少！

通过单元测试，我们至少可以收获以下好处：

  * 在一个复杂的项目中添加某功能模块时，可以快捷的进行针对性测试，而不用将整个项目 Run 起来。

  * 可以放心修改、重构业务代码，而不用担心修改某处代码后带来的副作用。（因为每次修改，都要保证测试用例能通过）

  * 帮助反思模块划分的合理性，解耦是否到位。（如果一个单元测试写得逻辑非常复杂、或者说一个函数复杂到无法写单测，那就说明模块的抽象有问题)

  * 能提高代码可维护性、可读性。新加入团队的成员，可以从单元测试入手，比文档更容易被程序员接受。

  * 保证代码被测试，更容易及早发现问题，降低风险。

总之，一句话，单元测试能提高代码质量和可维护性。

## 测试哪些内容

单元测试侧重的是逻辑测试和接口测试，一般来说，测试应该包括:

  * 公共类中的公开方法

  * 网络数据层

  * 业务逻辑层

  * 修复 Bug 的测试

实际操作过程中，要自下而上进行单元测试。从最基础的 Base 层，往上写测试。确保基础的 Model，Manager 测试通过，才开始为
Controller 编写测试，因为这部分业务是最复杂的，也是最容易改变的。

注意⚠️：编写单元测试需要注意的一点是责任分离。即你的测试只需要针对特定单元内部的逻辑，至于其他模块是否正确，是由该模块的编写者来负责测试的。

测试用例可以按以下三步执行：

  1. Given：配置测试的初始状态
  2. When：对要测试的目标执行代码
  3. Then：对测试结果进行断言（成功 or 失败）

这样我们一眼就能看出这个 case 大体上是在干嘛。

    
    
    func testExample1() throws {
            // Given
            let str = "welcome to the world"
            // When
            let headLine = vc.makeHeadline(string: str)
            // Then
            XCTAssertEqual(headLine, "Welcome To The World")
        }
    

## 基本使用

如下图，可新增相关测试target、class。

运行方式：

  * Product ▸ Test or Command-U，跑所有测试用例
  * 测试导航条右侧箭头
  * 测试用例左侧菱形按钮

## 异步测试

异步测试通常是比较慢的，应该单独出一个target去专门进行测试。

下面我们用XCTestExpectation来测试异步操作：

    
    
    func testValidRequestGetsHTTPStatusCode200() throws {
            // given
            let urlString =
              "https://www.jianshu.com/u/02d76422b530"
            let url = URL(string: urlString)!
            // 1
            let promise = expectation(description: "Status code: 200")
       
            // when
            let dataTask = session.dataTask(with: url) { _, response, error in
              // then
              if let error = error {
                XCTFail("Error: \(error.localizedDescription)")
                return
              } else if let statusCode = (response as? HTTPURLResponse)?.statusCode {
                if statusCode == 200 {
                  // 2
                  promise.fulfill()
                } else {
                  XCTFail("Status code: \(statusCode)")
                }
              }
            }
            dataTask.resume()
            // 3
            wait(for: [promise], timeout: 5)
          }
    

CMD+U运行，测试通过！

上面我们大致做了几件事：

  * 调用expectation()方法创建一个返回状态码为200的实例
  * 运行异步请求，请求成功后调用fulfill()标记这个expectation被完成
  * 最后要调用wait方法，不然这次测试就会过早的结束，它会保证测试的运行直到当所有expectation完成或者过时了才会停止测试。

但是上面的测试其实有一个问题，我们接下来换成一个无效的url：

    
    
     let urlString =
              "https://www.jianshu.com/u/02d76422b530test"
    

再次运行，测试不通过，但是此次测试运行完timeout的时间才结束，原因就是我们在请求成功才调用fulfill()，那现在无效的url的请求就会一直持续到即将超时才被完成。

    
    
      显然，我们想要的结果是：一旦请求有响应返回，无论是sucess还是error，都去fulfill这个expectation，然后我们直接断言判断结果即可。
    
    
    
    func testApiCallCompletes() throws {
            // given
      //      let urlString = "https://www.jianshu.com/u/02d76422b530"
              let urlString = "https://www.jianshu.com/u/02d76422b530test"
            let url = URL(string: urlString)!
            let promise = expectation(description: "Completion handler invoked")
            var statusCode: Int?
            var responseError: Error?
       
            // when
            let dataTask = session.dataTask(with: url) { _, response, error in
              statusCode = (response as? HTTPURLResponse)?.statusCode
              responseError = error
              promise.fulfill()
            }
            dataTask.resume()
            wait(for: [promise], timeout: 5)
       
            // then
            XCTAssertNil(responseError)
            XCTAssertEqual(statusCode, 200)
          }
    

CMD+U运行，请求fail后，断言fail，测试立马结束，不用等timeout才结束。

## Stub

实际工作中你会发现，很多时候有些代码是“无法测试”的，因为代码之间存在较高的耦合程度，类与类之间有复杂的依赖性，而我们肯定不能依赖于一个没有经过测试的类去对另一个需要测试的类进行测试，因为这样测试得到的结果，我们无法验证它的正确性（不能排除测试成功，但是其实是因为未测试的依赖类恰好失败了而恰巧得到的正确结果的可能性）。

    
    
    class Reposity {
          var bodyHelper = BodyHelper()
          func saveResultWith(height: Float, weight: Float) {
              let result = bodyHelper.getResultWith(height: height, weight: weight)
              self.save(result: result)
          }
      }
    

比如上面，Reposity中的saveResultWith方法中依赖了BodyHelper的getResultWith方法的结果，这样如果后续getResultWith中算法实现有所更改，会直接导致我们测试结果失败。而我们更多的是关心save方法的正确性，不关心计算结果方法的细节。

为了解决这种问题，我们需要编写一个桩程序，即Stub，它可以让一个对象对某个方法返回我们预先定好的数据。

    
    
    bodyHelper.stub(selector: #selector(bodyHelper.getResultWith(height:weight:)), andResult: mockResult, withArguments: height, weight)
    

想一下，如何使用XCTests去stub一个网络请求？

创建一个Stub，URLSessionStub去模拟返回我们想要的数据：

    
    
    typealias DataTaskCompletionHandler = (Data?, URLResponse?, Error?) -> Void
    protocol URLSessionProtocol {
      func dataTask(
        with url: URL,
        completionHandler: @escaping DataTaskCompletionHandler
      ) -> URLSessionDataTask
    }
    
    extension URLSession: URLSessionProtocol { }
    
    class URLSessionStub: URLSessionProtocol {
      private let stubbedData: Data?
      private let stubbedResponse: URLResponse?
      private let stubbedError: Error?
    
      public init(data: Data? = nil, response: URLResponse? = nil, error: Error? = nil) {
        self.stubbedData = data
        self.stubbedResponse = response
        self.stubbedError = error
      }
    
      public func dataTask(
        with url: URL,
        completionHandler: @escaping DataTaskCompletionHandler
      ) -> URLSessionDataTask {
        URLSessionDataTaskStub(
          stubbedData: stubbedData,
          stubbedResponse: stubbedResponse,
          stubbedError: stubbedError,
          completionHandler: completionHandler
        )
      }
    }
    
    class URLSessionDataTaskStub: URLSessionDataTask {
      private let stubbedData: Data?
      private let stubbedResponse: URLResponse?
      private let stubbedError: Error?
      private let completionHandler: DataTaskCompletionHandler?
    
      init(
        stubbedData: Data? = nil,
        stubbedResponse: URLResponse? = nil,
        stubbedError: Error? = nil,
        completionHandler: DataTaskCompletionHandler? = nil
      ) {
        self.stubbedData = stubbedData
        self.stubbedResponse = stubbedResponse
        self.stubbedError = stubbedError
        self.completionHandler = completionHandler
      }
    
      override func resume() {
        completionHandler?(stubbedData, stubbedResponse, stubbedError)
      }
    }
    

viewModel中请求方法如下：

    
    
    class ViewModel: NSObject {
        var session: URLSessionProtocol = URLSession.shared
         
        func getData(url: URL, result: @escaping (Int) -> ()) {
            let task = session.myDataTask(with: url) { data, response, error in
     
                guard let data = data else { return }
                guard let value = try? JSONDecoder().decode([Int].self, from: data).first else { return }
                result(value)
            }
            task.resume()
        }
     
    }
    

测试用例如下：

    
    
    func testStubData() {
            // given
            // 1
            let stubbedData = "[1]".data(using: .utf8)
            let str = "https://www.jianshu.com/u/02d76422b530"
            guard let url = URL(string: str) else { return }
            let stubbedResponse = HTTPURLResponse(
              url: url,
              statusCode: 200,
              httpVersion: nil,
              headerFields: nil)
            let urlSessionStub = URLSessionStub(
              data: stubbedData,
              response: stubbedResponse,
              error: nil)
            
            let promise = expectation(description: "Completion handler invoked")
    
            // when
            vm?.session = urlSessionStub
            vm?.getData(url: url) { result in
                XCTAssertEqual(result, 1)
                promise.fulfill()
            }
            
            wait(for: [promise], timeout: 5)
        }
    

## Mock

mock是一种更复杂更智能的stub。更复杂更智能体现在，我们可以为创造的 mock 定义在某种输入和方法调用下的输出，甚至为 mock 设定期望。  
mock 与 stub 最大的区别在于 stub 只是简单的方法替换，一般不会新增对象，而mock
是对现有类的行为一种模拟（或是对现有接口实现的模拟），会新增模拟出一个对象，并遵循类的定义相应某些方法。

# 如何UI测试

我们可以新建UI测试文件：

要想进行UI测试，我们需要一个关键的类XCUIApplication，创建并启动它：

    
    
    let app = XCUIApplication()
     
            app.launch()
    

点击xcode底部红色的记录按钮，开启记录UI操作功能

测试app会被启动，然后你在界面上进行操作，比如点击segment、label，此时xcode会同步生成代码记录你操作的UI控件，再次点击红色的记录按钮去中止UI记录：

可以看到buttons[First]和buttons[Second]右上角有下三角，点击可以展开，选segmentedControls.buttons[First]和segmentedControls.buttons[Second]，同时去掉tap

最终，我们拿到界面上的UI元素, cmd+u运行，测试通过！

## 如何性能测试

举例：求第n个斐波那契数，  
0 1 1 2 3 ..N  
这里举例了两种算法：

    
    
    // o(2^n) 0 1 1 2 3 ..N
     
        func fib1(_ n: Int) -> Int {
     
            if n <= 1 {
     
                return n
     
            }
     
            return fib1(n - 1) + fib1(n - 2)
     
        }
     
         
     
        // o(n)
     
        func fib2(_ n: Int) -> Int {
     
            if (n <= 1) {
     
                return n
     
            }
     
             
     
            var first = 0
     
            var second = 1
     
            for _ in 0..<n - 1 {
     
                let sum = first + second
     
                first = second
     
                second = sum
     
            }
     
            return second
     
        }
    

我们就可以将两种方法放到XCTest的measure方法的闭包中测试时间了，cmd+u运行，发现第二种算法耗时更少，算法更优。  
点击measure方法左侧灰色菱形展开，可以看到运行的一些指标。

  * Metric：时间作为性能的指标
  * Average：表示平均时间
  * Baseline：表示你设置一个基线
  * Result：是指平均时间和你是设置的基线进行比较后得出的结果，百分比表示的
  * max STDDEV ：表示标准偏差 10%。  
点击Edit，我们可以设置Baseline，ax STDDEV ，来设置觉得满意的性能测试条件底部点击1，2…可以看到每次运行的结果。

# TDD-测试驱动开发

## 什么是TDD

TDD是测试驱动开发（Test-Driven
Development）的英文简称，是一种流行的软件编写方式，是敏捷开发中的一项核心实践和技术，也是一种设计方法论。

    
    
        在进行单元测试时，我们一般能想到的是先编写业务代码，然后再编写相应测试代码，去验证产品方法是否符合预期。而TDD的思想正好相反，TDD的思想是先根据需求或者接口情况编写测试，然后再根据测试来编写业务代码。
    

典型的TDD遵循以下流程：

  * 红：先写一个会fail的测试
  * 绿：补上足够的代码以使测试通过
  * Refactor：清理和优化代码  
重复以上步骤直至你对所有用例满意为止

再详细点，测试驱动开发的基本过程如下：

  * 明确当前要完成的功能。记录成一个 TODO 列表。
  * 快速完成针对此功能的测试用例编写。
  * 测试代码编译不通过。
  * 编写对应的功能代码。
  * 测试通过。
  * 对代码进行重构，并保证测试通过。
  * 循环完成所有功能的开发。

简单说来，TDD是一种通过进行许多由测试支持的小更改去完成功能开发的方法，它的基本步骤就是“测试失败→编写代码努力让测试通过→再大胆重构，优化代码”。

## 为什么要TDD

    
    
       上面我们说了，一般我们都是先编写所有代码，然后在写测试，或者干脆不编写任何测试代码，直接运行后，一顿点击，到相关页面去手动测试，查看效果。而TDD却是先写测试代码，再写业务代码。
    

那TDD到底有什么好处呢？

    
    
        打个比如，就像砌砖一样，老师傅会先拉一条垂线，然后沿着线砌砖；而新手往往直接开工，砌完后再进行测量和修补。老师傅的做法就是TDD，总是先测试，再编码，有了测试的准绳，你可以有目的有方向地编码；而且有了测试的保护，你可以放心对原有代码进行重构，而不必担心破坏逻辑。
    

从流程上看，TDD提供了确保测试良好的方法：

  * 在编写新的测试之前，所有其他以前的测试都必须通过。这确保了测试的可重复性：不只是运行正在进行的单个测试，而是不断地运行所有测试。
  * 重构时，同时更新代码和测试代码。这可以确保测试用例能够得到很好的维护。
  * 通过并行迭代编写代码和测试，可以确保代码是可测试的。如果在完成代码后编写测试，那么代码很可能需要相当多的重构才能完成单元测试。

## 如何进行TDD开发

我们来实现一个小需求：一个句子中单词首字母大写转换。

在 ViewController.swift 中，添加一个方法：

    
    
    func makeHeadline(string: String) -> String {
            return ""
        }
    

#### Test1

在测试代码如下：

    
    
    func testExample1() throws {
             
            let str = "welcome to the world"
            let headLine = vc.makeHeadline(string: str)
            XCTAssertEqual(headLine, "Welcome To The World")
        }
    

很显然，测试不通过。

我们改下方法实现：

    
    
    func makeHeadline(string: String) -> String {
            return "Welcome To The World"
        }
    
    

Command + U，Test1测试通过。  
当然，为了确保此次测试用例的结果不是偶然的，我们要多写用例覆盖到所有场景，来保证该功能确实是通过的。

#### Test2

测试用例2代码：

    
    
    func testExample2() throws {
             
            let str = "here is another example"
            let headLine = vc.makeHeadline(string: str)
            XCTAssertEqual(headLine, "Here Is Another Example")
        }
    

很显然，测试又不通过。

我们再改下方法实现：

    
    
    func makeHeadline(string: String) -> String {
             
            let words = string.components(separatedBy: " ")
             
            var headline = ""
            for var word in words {
                let firstCharacter = word.remove(at: word.startIndex)
                headline += "\(firstCharacter.uppercased())\(word) "
            }
             
            headline.removeLast()
            return headline
        }
    

Command + U，Test2测试通过。

#### 重构代码

到这里我们的测试就算通过了，但有以下问题需要优化：

  * 测试用例描述的不太清楚
  * makeHeadline 函数的实现中遍历可以用上 Swift 里的高级功能，会更简洁

可调整如下：

    
    
    func testExample3() throws {
             
            let inputString = "here is another example"
            let expectedHeadline = "Here Is Another Example"
             
            let result = vc.makeHeadline(string: inputString)
            XCTAssertEqual(result, expectedHeadline)
        }
     
     
    func makeHeadline(string: String) -> String {
             
            let words = string.components(separatedBy: " ")
             
            let headline = words.map { word in
                var word = word
                let firstCharacter = word.remove(at: word.startIndex)
                return "\(firstCharacter.uppercased())\(word)"
            }.joined(separator: " ")
             
            return headline
        }
    

到此为止，我们就以TDD的开发方式实现了一个小功能。

## 缺点

#### 代码量增加，时间成本增加

编写测试代码就意味着代码量的增加，所以感觉上花费的时间成本也就变大。

但是，往往开发的成本不仅仅是最开始编写的第一个版本的代码。它还包括随着时间的推移，添加新功能、修改现有代码、修复错误等等。从长远来看，遵循 TDD 比不遵循
TDD 花费的时间要少得多，因为它的代码更易于维护，错误更少。

而且一旦你习惯了，TDD 会变得更快，只是刚刚开始用 TDD 可能需要更多的时间去熟悉。

更重要的是，如果在开发过程中发现了某个问题，那调试起来更容易，也能更快修复。而如果你在几周后才发现该问题，你要浪费更多的时间去回忆相关功能，去定位问题。

而生产中的缺陷被发现的时间越滞后，对客户的影响就越大，从而导致负面评论、失去信任和收入损失。

#### 测试用例过于专业，不便于团队协作

BDD

## 小结

大致总结一下：

原理：是在开发功能代码之前，先编写单元测试用例代码，测试代码确定需要编写什么产品代码。

优点：

  * 可以保证代码的质量。可以对自己的所需要的业务功能的每一步设计进行验证，并得到正确的结果，减少bug的出现的，特别对于复杂业务逻辑的项目，以小步慢走的方式，避免后期繁重的测试和维护工作。
  * 可以放心对原有代码进行重构，而不必担心破坏逻辑，必要时候你还可以痛痛快快的并且满怀信心的对代码做一场大的变革。这样我们的代码变得干净了，代码有了更好的扩展性、可维护性以及易理解性。

缺点：

增加代码量。测试代码是系统代码的两倍或更多，但是同时节省了调试程序及挑错时间。

原则：

  * 独立测试：不同代码的测试应该相互独立，一个类对应一个测试类，一个函数对应一个测试函数。用例也应各自独立，每个用例不能使用其他用例的结果数据，结果也不能依赖于用例执行顺序。 一个角色：开发过程包含多种工作，如：编写测试代码、编写产品代码、代码重构等。做不同的工作时，应专注于当前的角色，不要过多考虑其他方面的细节。
  * 测试列表：代码的功能点可能很多，并且需求可能是陆续出现的，任何阶段想添加功能时，应把相关功能点加到测试列表中，然后才能继续手头工作，避免疏漏。
  * 测试驱动：即利用测试来驱动开发，是TDD的核心。要实现某个功能，要编写某个类或某个函数，应首先编写测试代码，明确这个类、这个函数如何使用，如何测试，然后在对其进行设计、编码。
  * 先写断言：编写测试代码时，应该首先编写判断代码功能的断言语句，然后编写必要的辅助语句。
  * 可测试性：产品代码设计、开发时应尽可能提高可测试性，要符合单一职责。每个代码单元的功能应该比较单纯，“各家自扫门前雪”，每个类、每个函数应该只做它该做的事，不要弄成大杂烩。尤其是增加新功能时，不要为了图一时之便，随便在原有代码中添加功能。
  * 及时重构：对结构不合理，重复的代码，在测试通过后，应及时进行重构。
  * 小步前进：软件开发是复杂性非常高的工作，小步前进是降低复杂性的好办法。

# 如何查看测试报告、覆盖率

cmd+9，查看报告：

点击方法右侧箭头，跳到代码区：

右侧覆盖率注释显示测试命中每个代码段的次数。未调用的部分以红色突出显示。

禁止转载，如需转载请通过简信或评论联系作者。

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [IOS-测试驱动开发（TDD）提高单元测试覆盖率](https://www.jianshu.com/p/70809b05e711)

背景 最近在深挖如何提高单元测试覆盖率相关的东西。因为在实际实践项目单元测试的时候发现，编写完项目产品代码后发现再...

[leonardni](https://www.jianshu.com/u/8dabae51aff6)阅读 1,270评论 0赞 2

  * [深入单元测试系列之二，TDD和单元测试](https://www.jianshu.com/p/1c16d5473098)

测试驱动开发（TDD）的全称是Test-Driven Development。上一篇文章中，介绍了Kent Bec...

[杰哥的集思录](https://www.jianshu.com/u/f1f0cdf1488f)阅读 463评论 1赞 0

  * [iOS单元测试从入门到应用（长文）](https://www.jianshu.com/p/9707ff30e567)

引言：因为之前工作中经历过几次大的项目重构和组件化，所以陆陆续续学习了一些iOS单元测试相关的一些知识，以下内容是...

[RyanYuan](https://www.jianshu.com/u/1f312295ca50)阅读 11,130评论 4赞 67

  * [TDD（单元测试驱动开发）的Frequency Number练习](https://www.jianshu.com/p/ae3338e0edb9)

What is TDD? TDD是测试驱动开发（Test-Driven Development）的英文简称，是敏捷...

[WU_Wendy](https://www.jianshu.com/u/cf94cd93b523)阅读 508评论 3赞 2

  * [单元测试：通过简单例子理解测试驱动开发（TDD）](https://www.jianshu.com/p/041e3f48943b)

通常我们设计一个应用程序，并且快速创建单元测试来验证我们的设计，在我们编写这些测试时，这些测试也可以帮助改善了我最...

[ImWiki](https://www.jianshu.com/u/94ddd05814b3)阅读 544评论 0赞 2

 