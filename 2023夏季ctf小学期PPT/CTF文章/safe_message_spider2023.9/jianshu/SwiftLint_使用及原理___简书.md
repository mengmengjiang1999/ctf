SwiftLint 使用及原理

[ who_young](https://www.jianshu.com/u/1a4a34ce9690)关注赞赏支持

# SwiftLint 使用及原理

## 简介

[SwiftLint](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Frealm%2FSwiftLint)
是 realm 公司开发的一个插件，用于强制检查 Swift 代码风格和规则的一个工具。  
SwiftLint 的工作原理是检查 Swift 代码编译过程中的 AST 和 SourceKit 环节，从而可以摆脱不同版本 Swift
语法变化的影响。AST 是编译前端形成的抽象语法树（Abstract Symbolic Tree）， SourceKit 过程用来对 AST
进行代码优化，减少内存开销，提高执行效率。

## 安装

**1\. 使用 Homebrew:**  
`brew install swiftlint`

**2\. 使用 CocoaPods:**  
将如下代码添加到你的 Podfile 即可：  
`pod 'SwiftLint'`

**3\. 使用安装包:**  
通过从 [最新的 GitHub
发布地址](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Frealm%2FSwiftLint%2Freleases%2Ftag%2F0.43.1)
下载 SwiftLint.pkg 然后执行的方式安装 SwiftLint。

## 用法

**1\. Xcode:**  
在 **Xcode-Project-Build Phases-+(New Run Script Phase)** 中添加一个新的 Script Phase
并且包含如下代码即可：

    
    
    if which swiftlint >/dev/null; then
      swiftlint
    else
      echo "warning: SwiftLint not installed, download from https://github.com/realm/SwiftLint"
    fi
    

swiftlintScript.png

**2\. 命令行:**  
在有需要执行代码分析的 Swift 源码文件的目录下执行 swiftlint 命令，会对目录递归查找。

    
    
    $ swiftlint help
       autocorrect  Automatically correct warnings and errors
       help         Display general or command-specific help
       lint         Print lint warnings and errors for the Swift files in the current directory (default command)
       rules        Display the list of rules and their identifiers
       version      Display the current version of SwiftLint
    

## 规则

**1\. 终端执行命令:** `swiftlint rules` 或者 **官方文档:** [rule-
directory](https://links.jianshu.com/go?to=https%3A%2F%2Frealm.github.io%2FSwiftLint%2Frule-
directory.html)

    
    
    opt-in:  为 yes 时，规则默认不生效，需要添加进配置的 opt_in_rules 时生效
    correctable: 为 yes 时，执行 swiftlint autocorrect 命令，会自动修改代码格式为正确的格式
    enabled in your config: 为 yes 时，规则默认生效，不需要额外配置
    kind: 规则类型，仅用于规则的分类 
    analyzer: 为 yes 时，可在 Xcode 的 Analyze 生效
    configuration: 支持配置的属性默认值。例： warning 代表不符合代码规则时，编译器会警告。可在配置文件中改成 error，编译器会报错
    

rules 列表详见文章底部 **附录 1. swiftlint rules**

**2\. 规则开启与关闭**  
可以通过在一个源文件中定义一个如下格式的注释来关闭某个规则：  
`// swiftlint:disable <rule>`  
在该文件结束之前或者在定义如下格式的匹配注释之前，这条规则都会被禁用：  
`// swiftlint:enable <rule>`  
也可以通过添加 :previous, :this 或者 :next 来使关闭或者打开某条规则的命令分别应用于前一行，当前或者后一行代码。

    
    
    // swiftlint:disable:next force_cast
    let noWarning = NSNumber() as! Int
    let hasWarning = NSNumber() as! Int
    let noWarning2 = NSNumber() as! Int // swiftlint:disable:this force_cast
    let noWarning3 = NSNumber() as! Int
    // swiftlint:disable:previous force_cast
    

## 配置

在需要执行 SwiftLint 的目录下添加一个 .swiftlint.yml 文件的方式来配置 SwiftLint。可以被配置的参数有：

  * disabled_rules: 关闭某些默认开启的规则。
  * opt_in_rules: 一些规则是可选的，添加到这里才会生效。
  * only_rules: 不可以和 disabled_rules 或者 opt_in_rules 并列。类似一个白名单，只有在这个列表中的规则才是开启的。

    
    
    disabled_rules: # 执行时排除掉的规则
      - colon
    opt_in_rules: # 一些规则仅仅是可选的
      - empty_count
    included: # 执行 linting 时包含的路径。
      - Source
    excluded: # 执行 linting 时忽略的路径。 优先级比 `included` 更高。
      - Carthage
    force_cast: warning # 隐式
    force_try:
      severity: warning # 显式
    type_body_length: # 可以通过一个数组同时进行隐式设置
      - 300 # warning
      - 400 # error
    file_length: # 或者也可以同时进行显式设置
      warning: 500
      error: 1200
    
    reporter: "xcode" # 报告类型 (xcode, json, csv, checkstyle, codeclimate, junit, html, emoji, sonarqube, markdown, github-actions-logging)
    

## 自定义规则

在配置文件 **.swiftlint.yml** 里定义基于正则表达式的自定义规则：

    
    
    custom_rules:
      pirates_beat_ninjas: # 规则标识符
        name: "Pirates Beat Ninjas" # 规则名称，可选
        regex: "([nN]inja)" # 匹配的模式
        match_kinds: # 需要匹配的语法类型，可选
          - comment
          - identifier
        message: "Pirates are better than ninjas." # 提示信息，可选
        severity: error # 提示的级别，可选
      no_hiding_in_strings:
        regex: "([nN]inja)"
        match_kinds: string
    

输出大概可能是这个样子的：  

custom_rules

  
通过提供一个或者多个 match_kinds 的方式来对匹配进行筛选，它会将含有不包括在列表中的语法类型的匹配排除掉。这里有全部可用的语法类型：  
`argument` `attribute.builtin` `attribute.id` `buildconfig.id`
`buildconfig.keyword` `comment` `comment.mark` `comment.url` `doccomment`
`doccomment.field` `identifier` `keyword` `number` `objectliteral` `parameter`
`placeholder` `string` `string_interpolation_anchor` `typeidentifier`

## 嵌套配置

SwiftLint 支持通过嵌套配置文件的方式来对代码分析过程进行更加细致的控制。

  1. 在你需要的目录引入 .swiftlint.yml。
  2. 在目录结构必要的地方引入额外的 .swiftlint.yml 文件。
  3. 每个文件被检查时会使用在文件所在目录下的或者父目录的更深层目录下的配置文件。否则根配置文件将会生效。
  4. excluded 和 included 在嵌套结构中会被忽略。

## 自动更正

SwiftLint 可以自动修正某些错误，磁盘上的文件会被一个修正后的版本覆盖。  
请确保在对文件执行 **swiftlint autocorrect** 之前有对它们做过备份，否则的话有可能导致重要数据的丢失。  
因为在执行自动更正修改某个文件后很有可能导致之前生成的代码检查信息无效或者不正确，所以当在执行代码更正时标准的检查是无法使用的。

## SwiftLint rules 原理

SwiftLint rules 的源码在 Source/SwiftLintFramework/Rules 目录下，以
OverriddenSuperCallRule(方法需要调用 super method)
为例解读源码，路径为：/Source/SwiftLintFramework/Rules/Lint/OverriddenSuperCallRule.swift。  
`| overridden_super_call | yes | no | no | lint | no | warning, excluded: [],
included: [“*"] |`  
主要看 **validate(file:kind:dictionary:)** 方法，在方法中使用了 **configuration** 、
**SourceKittenDictionary** 。  
**configuration: OverriddenSuperCallConfiguration**

    
    
    public struct OverriddenSuperCallConfiguration: RuleConfiguration, Equatable {
        private let defaultIncluded = [
            "addChildViewController(_:)",
            "didReceiveMemoryWarning()",
            "removeFromParentViewController()",
            "viewDidAppear(_:)",
            "viewDidDisappear(_:)",
            "viewDidLoad()",
            "viewWillAppear(_:)",
            "viewWillDisappear(_:)",
            ...
        ]
        var severityConfiguration = SeverityConfiguration(.warning)
        var excluded: [String] = []
        var included: [String] = ["*"]
        public private(set) var resolvedMethodNames: [String]
        init() {
            resolvedMethodNames = defaultIncluded
        }
        public var consoleDescription: String {
            return severityConfiguration.consoleDescription +
                ", excluded: \(excluded)" +
                ", included: \(included)"
        }
        public mutating func apply(configuration: Any) throws {
            guard let configuration = configuration as? [String: Any] else {
                throw ConfigurationError.unknownConfiguration
            }
            if let severityString = configuration["severity"] as? String {
                try severityConfiguration.apply(configuration: severityString)
            }
            if let excluded = [String].array(of: configuration["excluded"]) {
                self.excluded = excluded
            }
            if let included = [String].array(of: configuration["included"]) {
                self.included = included
            }
            resolvedMethodNames = calculateResolvedMethodNames()
        }
        public var severity: ViolationSeverity {
            return severityConfiguration.severity
        }
        private func calculateResolvedMethodNames() -> [String] {
            var names: [String] = []
            if included.contains("*") && !excluded.contains("*") {
                names += defaultIncluded
            }
            names += included.filter({ $0 != "*" })
            names = names.filter { !excluded.contains($0) }
            return names
        }
    }
    

  * defaultIncluded: 默认的配置，里面有一些方法名。
  * severityConfiguration: 规则冲突提示级别
  * excluded: 需要排除的方法
  * included：需要包含的方法
  * func apply(configuration: Any): 应用自定义的配置
  * calculateResolvedMethodNames(): 综合配置

SourceKittenDictionary 使用 [String: SourceKitRepresentable] 初始化。  
[String: SourceKitRepresentable] 是 sourcekitten structure --file
SourcekittenDemoViewController.swift 命令生成的 json 对象。详看:
sourcekitten_structure.json  
**SourceKittenDictionary**

    
    
    public struct SourceKittenDictionary {
       init(_ value: [String: SourceKitRepresentable]) {…}
    …
    

以 SourcekittenDemoViewController.swift 为例：

    
    
    class SourcekittenDemoViewController: UIViewController {
        private var testVar: String?
        override func viewDidLoad() {
            super.viewDidLoad()
            self.view.backgroundColor = UIColor.lightGray
            testVar = "i am testVar"
        }
    }
    

**sourcekitten_structure.json**

    
    
    {
      "key.diagnostic_stage" : "source.diagnostic.stage.swift.parse",
      "key.length" : 414,
      "key.offset" : 0,
      "key.substructure" : [
        {
          "key.accessibility" : "source.lang.swift.accessibility.internal",
          "key.bodylength" : 189,
          "key.bodyoffset" : 223,
          "key.elements" : [
            {
              "key.kind" : "source.lang.swift.structure.elem.typeref",
              "key.length" : 16,
              "key.offset" : 205
            }
          ],
          "key.inheritedtypes" : [
            {
              "key.name" : "UIViewController"
            }
          ],
          "key.kind" : "source.lang.swift.decl.class",
          "key.length" : 246,
          "key.name" : "SourcekittenDemoViewController",
          "key.namelength" : 30,
          "key.nameoffset" : 173,
          "key.offset" : 167,
          "key.substructure" : [
            {
              "key.accessibility" : "source.lang.swift.accessibility.private",
              "key.attributes" : [
                {
                  "key.attribute" : "source.decl.attribute.private",
                  "key.length" : 7,
                  "key.offset" : 228
                }
              ],
              "key.kind" : "source.lang.swift.decl.var.instance",
              "key.length" : 20,
              "key.name" : "testVar",
              "key.namelength" : 7,
              "key.nameoffset" : 240,
              "key.offset" : 236,
              "key.setter_accessibility" : "source.lang.swift.accessibility.private",
              "key.typename" : "String?"
            },
            {
              "key.accessibility" : "source.lang.swift.accessibility.internal",
              "key.attributes" : [
                {
                  "key.attribute" : "source.decl.attribute.override",
                  "key.length" : 8,
                  "key.offset" : 261
                }
              ],
              "key.bodylength" : 120,
              "key.bodyoffset" : 290,
              "key.kind" : "source.lang.swift.decl.function.method.instance",
              "key.length" : 141,
              "key.name" : "viewDidLoad()",
              "key.namelength" : 13,
              "key.nameoffset" : 275,
              "key.offset" : 270,
              "key.substructure" : [
                {
                  "key.bodylength" : 0,
                  "key.bodyoffset" : 317,
                  "key.kind" : "source.lang.swift.expr.call",
                  "key.length" : 19,
                  "key.name" : "super.viewDidLoad",
                  "key.namelength" : 17,
                  "key.nameoffset" : 299,
                  "key.offset" : 299
                }
              ]
            }
          ]
        }
      ]
    }
    

**validate(file:kind:dictionary:)**

    
    
    func validate(file: SwiftLintFile, kind: SwiftDeclarationKind,
              dictionary: SourceKittenDictionary) -> [StyleViolation] {
                 guard let offset = dictionary.bodyOffset,
                           let name = dictionary.name,
                       kind == .functionMethodInstance,
                           configuration.resolvedMethodNames.contains(name),
                       dictionary.enclosedSwiftAttributes.contains(.override)
           else { return [] }
                  let callsToSuper = dictionary.extractCallsToSuper(methodName: name)
                  if callsToSuper.isEmpty {
                     …
                     "Method '\(name)' should call to super function"
                  } else if callsToSuper.count > 1 {
                     ...
                     "Method '\(name)' should call to super only once"
                  }
                  return []
    }
    
    
    
    public struct SourceKittenDictionary {
    …
    internal func extractCallsToSuper(methodName: String) -> [String] {
        guard let methodNameWithoutArguments = methodName.split(
    separator: "(").first else { return [] }
        let superCall = “super.\(methodNameWithoutArguments)"
        return substructure.flatMap { elems -> [String] in
            guard let type = elems.expressionKind,
            let name = elems.name,
            type == .call && superCall == name else {
                return elems.extractCallsToSuper(
    methodName: methodName)}
            return [name]}}
    }
    

**validate(file:kind:dictionary:) 通过判断：**

    
    
    方法 == 含有 .override 属性的实例方法 && 
    methodName 在配置列表中 &&
    Substructure 中表达式类型是 .call && 
    Substructure 中方法调用名称 == super.{methodName}
    

满足上述条件的方法内若没有调用对应的 super 方法，或者  
调用了多次对应的 super 方法，就会提示规则冲突。

**问：sourcekitten 是什么？**  
答：SourceKitten 是基于 Apple 的 SourceKit 封装的命令行工具，SourceKitten 链接并与
sourcekitd.framework 通信以解析 Swift AST，最终提取 Swift 或 ObjC 文件的类结构和方法等。  
sourcekitten 支持的命令如下：

    
    
    SUBCOMMANDS:
      complete                Generate code completion options
      doc                     Print Swift or Objective-C docs as JSON
      format                  Format Swift file
      index                   Index Swift file and print as JSON
      module-info          Obtain Swift module information and print as json
      request                 Run a raw SourceKit request
      structure               Print Swift structure information as JSON
      syntax                  Print Swift syntax information as JSON
      version                 Display the current version of SourceKitten
    

**问：SourceKit 是什么？**  
答：SourceKit 是一套工具集，使得大多数 Swift
源代码层面的操作特性得以支持，例如源代码解析、语法高亮、排版（typesetting）、自动补全、跨语言头文件生成，等等

**问：Swift AST 是什么？**  
答：AST(Abstract Syntax Tree 抽象语法树) 是源代码的抽象语法结构的树状表示，树上的每个节点都表示源代码中的一种结构，是 Swift
文件编译过程中的产物。

**Swift 文件编译过程** :  

Swift 文件编译过程

image.png

**Swiftc 生成 AST** ：  
Swiftc 是 swift 语言的编译工具，它可以直接把 .swift 文件编译生成可执行文件，也可以产生编译过程中某个中间文件。Swiftc
支持命令如下：

    
    
    MODES:
      -dump-ast              Parse and type-check input file(s) and dump AST(s)
      -dump-parse            Parse input file(s) and dump AST(s)
      -emit-assembly         Emit assembly file(s) (-S)
      -emit-executable       Emit a linked executable
      -emit-ir               Emit LLVM IR file(s)
      -emit-sibgen           Emit serialized AST + raw SIL file(s)
      -emit-sib              Emit serialized AST + canonical SIL file(s)
      -emit-silgen           Emit raw SIL file(s)
      -emit-sil              Emit canonical SIL file(s)
      -parse                 Parse input file(s)
      -print-ast             Parse and type-check input file(s) and pretty print AST(s)
      -typecheck             Parse and type-check input file(s)
    ...
    

`swiftc -dump-parse SourcekittenDemoViewController.swift`

    
    
    (source_file "SourcekittenDemoViewController.swift"
      (import_decl range=[SourcekittenDemoViewController.swift:9:1 - line:9:8] 'UIKit')
      (class_decl range=[SourcekittenDemoViewController.swift:11:1 - line:18:1] "SourcekittenDemoViewController" inherits: <null>
        (pattern_binding_decl range=[SourcekittenDemoViewController.swift:12:13 - line:12:32]
          (pattern_typed
            (pattern_named 'testVar')
            (type_optional
              (type_ident
                (component id='String' bind=none)))))
        (var_decl range=[SourcekittenDemoViewController.swift:12:17 - line:12:17] "testVar" type='<null type>' readImpl=stored writeImpl=stored readWriteImpl=stored)
        (func_decl range=[SourcekittenDemoViewController.swift:13:14 - line:17:5] "viewDidLoad()"
          (parameter "self")
          (parameter_list range=[SourcekittenDemoViewController.swift:13:30 - line:13:31])
          (brace_stmt range=[SourcekittenDemoViewController.swift:13:33 - line:17:5]
            (call_expr type='<null>' arg_labels=
              (unresolved_dot_expr type='<null>' field 'viewDidLoad' function_ref=unapplied
                (super_ref_expr type='<null>'))
              (tuple_expr type='()' location=SourcekittenDemoViewController.swift:14:26 range=[SourcekittenDemoViewController.swift:14:26 - line:14:27]))
            (sequence_expr type='<null>'
              (unresolved_dot_expr type='<null>' field 'backgroundColor' function_ref=unapplied
                (unresolved_dot_expr type='<null>' field 'view' function_ref=unapplied
                  (declref_expr type='<null>' decl=SourcekittenDemoViewController.(file).SourcekittenDemoViewController.viewDidLoad().self@SourcekittenDemoViewController.swift:13:19 function_ref=unapplied)))
              (assign_expr type='<null>'
                (**NULL EXPRESSION**)
                (**NULL EXPRESSION**))
              (unresolved_dot_expr type='<null>' field 'lightGray' function_ref=unapplied
                (unresolved_decl_ref_expr type='<null>' name=UIColor function_ref=unapplied)))
            (sequence_expr type='<null>'
              (unresolved_decl_ref_expr type='<null>' name=testVar function_ref=unapplied)
              (assign_expr type='<null>'
                (**NULL EXPRESSION**)
                (**NULL EXPRESSION**))
              (string_literal_expr type='<null>' encoding=utf8 value="i am testVar" builtin_initializer=**NULL** initializer=**NULL**))))))
    

通过生成的 AST 信息可以看到
import_decl、class_decl、var_decl、func_decl、brace_stmt、call_expr
等及所在的行列数。sourcekit 可以通过这些信息实现语法高亮、排版、自动补全、跨语言头文件生成，等等

**提醒** 执行 `swiftc -print-ast SourcekittenDemoViewController.swift` 命令时，终端会报错
`SourcekittenDemoViewController.swift:9:8: error: no such module 'UIKit'` .  
为解决此报错，需要指定 -sdk 和 -target 参数，如下：  
`swiftc -print-ast SourcekittenDemoViewController.swift -sdk
/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS15.5.sdk
-target arm64-apple-ios15.5`  
"15.5" 需要根据本地支持的版本做修改。

## SwiftLint 规则建议

Swiftlint 规则没有完全符合每个工程期望的统一规则。基于项目应用上面，我得出一些经验教训，在此给出一点建议：

  1. **成熟的项目规则宜松不宜紧** 。规则过多或过严会直接导致产生较多警告，改动太耗时间，产生大量提交。万一修改出了错误，查起来也会非常麻烦。
  2. **可纠正代码 bug 的规则，建议提示级别为 error，而非 warning** 。如此可及时提醒修正错误。  
例如： OverriddenSuperCallRule 规则可用于避免遗漏调用 super 方法，从而避免工程中对此方法的 hook 不生效。  
例如: DiscardedNotificationCenterObserverRule 规则可用于避免因为未持有
observer，不能释放内存，从而导致内存泄露的 bug。

  3. 推荐 swift 写法的规则建议使用。  
例如：使用 CGPoint(x:y:) 代替 CGPointMake(,)

基于上面三条建议，制定的规则示例如下：

    
    
    only_rules:
      - block_based_kvo # Swift 3.2 之后使用新的 KVO API
      - compiler_protocol_init # 不应该直接调用字面量转换的初始化方法
      - control_statement # if while 等判断条件不要用括号括起来
      - custom_rules # 一些自定义规则
      - discarded_notification_center_observer # 当使用 block 注册通知中心 observer 的时候，应该存储函数返回的 observer, 以便之后的删除
      - discouraged_optional_boolean # 不建议使用可选布尔值
      - duplicate_imports # 重复导入
      - duplicate_enum_cases # 枚举不能设置两个或者以上相同的名字
      - empty_count
      - empty_string # 优先使用 isEmpty 判断，而不是将字符串与空字符串文字进行比较
      - empty_parameters # 闭包参数为空时,建议使用 `() -> ` 代替 `Void ->
      - explicit_init # 避免直接调用 init 方法
      - fallthrough # switch 语句中不建议使用 fallthrough
      - fatal_error_message # fatalError 必须拥有一个 message
      - file_name_no_space # 文件名不应包含任何空格
      - force_cast # 不建议直接强解类型
      - force_try # 避免 `try!`
      - force_unwrapping # 避免强制解包
      - identical_operands # 比较两个相同的操作数可能是一个错误
      - legacy_cggeometry_functions # 避免使用 C 风格的 CG 遗留函数，使用 struct extension
      - legacy_constructor # 使用 swift 提供的 struct 构造函数， 避免使用遗留的构造函数比如 CGPointMake(10, 10)
      - legacy_nsgeometry_functions # 避免使用 C 风格的 NS 遗留函数，使用 struct extension
      - literal_expression_end_indentation # 数组和字典文字的结尾应与开始它的行具有相同的缩进
      - lower_acl_than_parent # 确保定义的访问控制级别低于其父级
      - mark # 正确使用 mark 的格式 `// MARK: - message`
      - multiline_parameters # 函数和方法参数应该在同一行上，或者每行一个
      - no_extension_access_modifier # 在 extension 扩展前面,不建议使用 (fileprivate,public) 等修饰符
      - redundant_objc_attribute # Objective-C 属性（@objc）在声明中是多余的
      - redundant_optional_initialization # 不需要写默认值为 nil
      - redundant_string_enum_value # 字符串类型枚举，会有默认 string 值，与名字相同，不要再次设置
      - redundant_void_return # 在不必要的时候， 不需要写 ->() and -> Void
      - return_arrow_whitespace # 函数定义返回的 ->  前后有空格， 不换行
      - switch_case_alignment # Case 语句应与其封闭的 switch 语句垂直对齐，如果没有其他配置，则缩进
      - trailing_semicolon # 行末尾不加分号
      - type_name # 类型名字限制规则（类型名称应仅包含字母数字字符，以大写字符开头，长度在 3 到 40 个字符之间）
      - unneeded_break_in_switch # 在 switch-case 语句中, 有方法调用或操作时,避免使用 break 语句
      - unowned_variable_capture # 最好将引用捕获为弱引用以避免潜在的崩溃
      - void_return # 使用 `-> Void` 代替 `-> ()
      - weak_delegate # delegate 应该被设置为 weak
    
    excluded: # paths to ignore during linting. Takes precedence over `included`.
      - Tests
      - Example
      - Resources
    
    force_cast:
      severity: warning
      
    force_try:
      severity: warning
    
    no_extension_access_modifier:
      severity: warning
      
    empty_count:
      severity: warning
    
    type_name:
      min_length: 1
      max_length: 60
    
    overridden_super_call:
      severity: error
    
    prohibited_super_call:
      severity: error
      
    discarded_notification_center_observer:
      severity: error
    
    weak_delegate:
      severity: error
    
    unowned_variable_capture:
      severity: error
    
    reporter: "xcode" # reporter type (xcode, json, csv, checkstyle, junit, html, emoji, sonarqube, markdown)
    
    custom_rules:
      ab_test_recovery:
        name: "AB Test Recovery"
        regex: '^ *//+[ \S]* ABTestHelper\.+'
        match_kinds:
          - comment
          - doccomment
        message: "AB Test Recovery. 调试期间注释掉的 ab test,上线前记得恢复"
        severity: warning
      url_Check:
        name: "URL Check"
        regex: '(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]+[()（）]'
        match_kinds: string
        message: "URL 中发现有 '(' 或 ')' 或 '（' 或 '）' ，请注意确认正确性"
        severity: warning
    

## 附录

### 1\. swiftlint rules

identifier | opt-in | correctable | enabled in your config | kind | analyzer |
configuration | comment  
---|---|---|---|---|---|---|---  
anyobject_protocol | yes | yes | no | lint | no | warning | 对于纯类协议，建议AnyObject
不推荐 class  
array_init | yes | no | no | lint | no | warning | 推荐使用 Array(seq) 不推荐语法：
seq.map { $0 } 将序列转换为Array  
attributes | yes | no | no | style | no | warning, always_on_same_line:
["@IBAction", "@NSManaged"], alwa... | 属性应该在函数和类型中自己的行上，与变量和 imports 在同一行上  
balanced_xctest_lifecycle | yes | no | no | lint | no | warning | -  
block_based_kvo | no | no | yes | idiomatic | no | warning |
属性和下标中的Getter和setter应该保持一致的顺序  
capture_variable | yes | no | no | lint | yes | warning | -  
class_delegate_protocol | no | no | yes | lint | no | warning | delegate
protocol 应该被设定为 class-only,才能被弱引用  
closing_brace | no | yes | yes | style | no | warning |
小括号内包含函数（大括号）的时候，之间没有空格  
closure_body_length | yes | no | no | metrics | no | warning: 20, error: 100 |
封闭体不应跨越太多行  
closure_end_indentation | yes | yes | no | style | no | warning | 闭包前后缩进应相同  
closure_parameter_position | no | no | yes | style | no | warning | 闭包参数位置，
闭包参数应该 { 左边在同一行  
closure_spacing | yes | yes | no | style | no | warning | 闭包表达式在每个大括号 { }
内前后应有一个空格  
collection_alignment | yes | no | no | style | no | warning, align_colons:
false | 集合文字中的所有元素应垂直对齐  
colon | no | yes | yes | style | no | warning, flexible_right_spacing: false,
apply_to_dictionaries: ... | 冒号左边没有空格， 右边有且只有一个空格  
comma | no | yes | yes | style | no | warning | 逗号左边没有空格， 右边有空格  
comment_spacing | no | yes | yes | lint | no | warning | -  
compiler_protocol_init | no | no | yes | lint | no | warning |
不应该直接调用字面量转换的初始化方法，诸如编译器协议中声明的初始化程序ExpressibleByArrayLiteral不应直接调用  
computed_accessors_order | no | no | yes | style | no | warning, order:
get_set | -  
conditional_returns_on_newline | yes | no | no | style | no | warning,
if_only: false | 条件语句与结果不建议写在一行 ，例如：guard true else { return } ；if true {
return "YES" } else { return "NO" } 会有 warning提示  
contains_over_first_not_nil | yes | no | no | performance | no | warning |
推荐使用 contains，避免使用 first(where:) != nil 与 firstIndex(where:) != nil  
control_statement | no | yes | yes | style | no | warning | if while
等判断条件不要用括号 括起来,另外注意条件出的空格  
convenience_type | yes | no | no | idiomatic | no | warning |
用于检测静态成员的类型应实现为无大小写的枚举，以避免实例化  
custom_rules | no | no | no | style | no | user-defined | 通过提供正则表达式字符串来创建自定义规则  
cyclomatic_complexity | no | no | yes | metrics | no | warning: 10, error: 20,
ignores_case_statements: false |
代码复杂度,默认为10，循环复杂度。函数体的复杂度的限制，这个属性主要约束条件句、循环句中的循环嵌套问题，
当嵌套太多的循环时，则会触发swiftlint中的warning和error，当达到10个循环嵌套时就会报warning，达到20个循环嵌套时就会报error,强烈推荐这个属性。嵌套太多，可读性差  
deployment_target | no | no | yes | lint | no | warning,
iOS_deployment_target: 7.0, macOS_deployment_target: 1... | -  
discarded_notification_center_observer | yes | no | no | lint | no | warning |
当使用 block 注册通知中心 observer 的时候， 应该存储函数返回的 observer, 以便之后的删除  
discouraged_assert | yes | no | no | idiomatic | no | warning | -  
discouraged_direct_init | no | no | yes | lint | no | warning, types:
["Bundle", "Bundle.init", "UIDevice", "UIDevice... | 不鼓励直接初始化并声明的类型
warning：types: ["Bundle", "Bundle.init", "UIDevice", "UIDevice.init"]  
discouraged_object_literal | yes | no | no | idiomatic | no | warning,
image_literal: true, color_literal: true | 避免使用图片和颜色的字面量（Ltiteral），尽量使用初始化的方式  
discouraged_optional_boolean | yes | no | no | idiomatic | no | warning |
推荐使用非可选的bool值  
discouraged_optional_collection | yes | no | no | idiomatic | no | warning |
优先选择空集合而不是可选集合  
duplicate_enum_cases | no | no | yes | lint | no | error | 枚举不能设置两个或者以上相同的名字  
duplicate_imports | no | no | yes | idiomatic | no | warning | 重复导入  
dynamic_inline | no | no | yes | lint | no | error |
避免同时使用'dynamic'和'@inline（__ always）'  
empty_count | yes | no | no | performance | no | error, only_after_dot: false
| 建议使用isEmpty判断,而不是使用count==0判断  
empty_enum_arguments | no | yes | yes | style | no | warning |
如果将枚举与关联的类型匹配（如果不使用），则可以忽略参数  
empty_parameters | no | yes | yes | style | no | warning | 使用 `() ->` 代替 `Void
->  
empty_parentheses_with_trailing_closure | no | yes | yes | style | no |
warning | 尾闭包避免空参数括号  
empty_string | yes | no | no | performance | no | warning |
优先使用isEmpty判断，而不是将字符串与空字符串文字进行比较  
empty_xctest_method | yes | no | no | lint | no | warning | 应避免使用空的XCTest方法  
enum_case_associated_values_count | yes | no | no | metrics | no | warning: 5,
error: 6 | 枚举情况下的关联值数量应少  
expiring_todo | yes | no | no | lint | no | (approaching_expiry_severity)
warning, (reached_or_passed_expir... | TODO和FIXME应该在其到期日之前解决  
explicit_acl | yes | no | no | idiomatic | no | warning | 所有声明都应明确指定访问控制级别关键字  
explicit_enum_raw_value | yes | no | no | idiomatic | no | warning | 枚举应设置默认值  
explicit_init | yes | yes | no | idiomatic | no | warning | 避免直接调用 init 方法  
explicit_self | yes | yes | no | style | yes | warning | 实例变量和函数应使用“self”显式访问  
explicit_top_level_acl | yes | no | no | idiomatic | no | warning |
顶级声明应明确指定访问控制级别关键字  
explicit_type_interface | yes | no | no | idiomatic | no | warning, excluded:
[], allow_redundancy: false | 需要跑明确参数的类型定义  
extension_access_modifier | yes | no | no | idiomatic | no | warning |
优先使用扩展名访问修饰符  
fallthrough | yes | no | no | idiomatic | no | warning | 避免在 case语句中使用
fallthrough  
fatal_error_message | yes | no | no | idiomatic | no | warning | 必须拥有一个
message  
file_header | yes | no | no | style | no | warning, required_string: None,
required_pattern: None, forbidd... | 标头注释应与项目模式一致  
file_length | no | no | yes | metrics | no | warning: 400, error: 1000,
ignore_comment_only_lines: false | 文件长度限制  
file_name | yes | no | no | idiomatic | no | (severity) warning, excluded:
["LinuxMain.swift", "main.swift"]... | 文件名应与文件中声明的类型或扩展名匹配（如果有  
file_types_order | yes | no | no | style | no | warning, order:
[[SwiftLintFramework.FileType.supportingType], ... | 指定如何排序文件中的类型  
first_where | yes | no | no | performance | no | warning | 使用 `.first(where:)`
代替 `.filter { }.first`  
flatmap_over_map_reduce | yes | no | no | performance | no | warning | 推荐使用
flatMap，避免使用 map 的 reduce([], +)  
for_where | no | no | yes | idiomatic | no | warning | 使用 `for where` 代替 简单的
`for { if }`  
force_cast | no | no | yes | idiomatic | no | error | 避免强制的类型转化,这里表示强解类型警告 as!
Int  
force_try | no | no | yes | idiomatic | no | error |
对会抛出异常(throws)的方法,不建议try，强解, 避免 `try!`  
force_unwrapping | yes | no | no | idiomatic | no | warning | 避免强制解包  
function_body_length | no | no | yes | metrics | no | warning: 40, error: 100
| 函数体长度 默认超过40行warning,超过100行直接报错。推荐使用  
function_default_parameter_at_end | yes | no | no | idiomatic | no | warning |
方法中参数列表，应将带有默认值的参数放在最后面  
function_parameter_count | no | no | yes | metrics | no | warning: 5, error:
8ignores_default_parameters: true | 函数参数个数  
generic_type_name | no | no | yes | idiomatic | no | (min_length) w/e: 1/0,
(max_length) w/e: 20/1000, excluded: [],... | 类型命名规则限制,以大写字母开头，且长度在1到20个字符之间  
ibinspectable_in_extension | yes | no | no | lint | no | warning |
扩展不应添加@IBInspectable属性  
identical_operands | yes | no | no | lint | no | warning | 比较两个相同的操作数可能是一个错误  
identifier_name | no | no | yes | style | no | (min_length) w/e: 3/2,
(max_length) w/e: 40/60, excluded: [], a... | 参数变量命名规则  
implicit_getter | no | no | yes | style | no | warning | 参数不应该有 getter 方法  
implicit_return | yes | yes | no | style | no | warning, included: [getter,
closure, function] | 在闭包，函数和getter中更喜欢隐式返回  
implicitly_unwrapped_optional | yes | no | no | idiomatic | no | warning,
mode: allExceptIBOutlets | 避免隐式解析可选类型的使用 / 避免隐式解包（定义 ！ 类型）  
inclusive_language | no | no | yes | style | no | warning, additional_terms:
[], override_terms: [], override_all...  
inert_defer | no | no | yes | lint | no | warning |
如果defer在其父范围的末尾，则无论如何它都会被执行  
is_disjoint | no | no | yes | idiomatic | no | warning |
优先：Set.isDisjoint(with:) 不建议：Set.intersection(_:).isEmpty  
joined_default_parameter | yes | yes | no | idiomatic | no | warning |
不推荐显式使用默认分隔符  
large_tuple | no | no | yes | metrics | no | warning: 2, error: 3 | 元祖成员
元组冲突:元组应该最多有2个成员，多余两个会报错  
last_where | yes | no | no | performance | no | warning |
推荐在集合中使用：.last(where:) 不推荐使用： .filter { }.last  
leading_whitespace | no | yes | yes | style | no | warning | 文件末尾不应该存在空格符  
legacy_cggeometry_functions | no | yes | yes | idiomatic | no | warning | 避免使用
C 风格 的 CG 遗留函数， 使用 struct extension  
legacy_constant | no | yes | yes | idiomatic | no | warning | 避免使用 遗留的全局常量， 使用
struct 内定义的 常量  
legacy_constructor | no | yes | yes | idiomatic | no | warning | 使用 swift 提供的
struct 构造函数， 避免使用 遗留的构造函数 比如 CGPointMake(10, 10)  
legacy_hashing | no | no | yes | idiomatic | no | warning |
hash(into:)优先使用函数而不是覆盖hashValue  
legacy_multiple | yes | no | no | idiomatic | no | warning |
推荐使用isMultiple(of:)函数，不推荐使用余数运算符（%）  
legacy_nsgeometry_functions | no | yes | yes | idiomatic | no | warning | 避免使用
C 风格 的 NS 遗留函数， 使用 struct extension  
legacy_objc_type | yes | no | no | idiomatic | no | warning | -  
legacy_random | yes | no | no | idiomatic | no | warning | 随机函数
优先使用type.random（in :)，不建议使用旧版函数  
let_var_whitespace | yes | no | no | style | no | warning |
let和var应该用空白行与其他语句分开  
line_length | no | no | yes | metrics | no | warning: 120, error: 200, ignores
urls: false, ignores function... | 行的字符长度,官方的规定是超过120字符就给 warning  
literal_expression_end_indentation | yes | yes | no | style | no | warning |
数组和字典文字的结尾应与开始它的行具有相同的缩进  
lower_acl_than_parent | yes | no | no | lint | no | warning | 确保定义的访问控制级别低于其父级  
mark | no | yes | yes | lint | no | warning | 正确使用 mark 的格式 `// MARK: -
message`  
missing_docs | yes | no | no | lint | no | warning: open, public | 声明应记录在案  
modifier_order | yes | yes | no | style | no | warning,
preferred_modifier_order: [override, acl, setterACL, d... | 修饰符顺序应一致  
multiline_arguments | yes | no | no | style | no | warning,
first_argument_location: any_line, only_enforce_after_... | 参数应该在同一行，或者每行一个  
multiline_arguments_brackets | yes | no | no | style | no | warning |
多行参数应在其新行中包含方括号 []  
multiline_function_chains | yes | no | no | style | no | warning |
链接的函数调用应该在同一行上，或者每行一个  
multiline_literal_brackets | yes | no | no | style | no | warning |
多行文字应在其新行中包含方括号 []  
multiline_parameters | yes | no | no | style | no | warning, allowsSingleLine:
true | 函数和方法参数应该在同一行上，或者每行一个  
multiline_parameters_brackets | yes | no | no | style | no | warning |
多行参数应在其新行中包含方括号  
multiple_closures_with_trailing_closure | no | no | yes | style | no | warning
| 传递多个闭包参数时，不应使用结尾的闭包语法  
nesting | no | no | yes | metrics | no | (type_level) w: 1, (function_level)
w: 2, (check_nesting_in_clo... | 类型定义嵌套不要超过1层 ， 声明嵌套不要超过5层  
nimble_operator | yes | yes | no | idiomatic | no | warning | 避免 expect
一个确定的判断  
no_extension_access_modifier | yes | no | no | idiomatic | no | error |
禁止使用扩展访问修饰符  
no_fallthrough_only | no | no | yes | idiomatic | no | warning |
仅当case包含至少一个其他语句时，才能使用穿透  
no_grouping_extension | yes | no | no | idiomatic | no | warning |
扩展名不应用于对同一源文件中的代码进行分组  
no_space_in_method_call | no | yes | yes | style | no | warning |
不要在方法名称和括号之间添加空格  
notification_center_detachment | no | no | yes | lint | no | warning |
`NotificationCenter.default.removeObserver` 只在 `deinit` 中被调用  
nslocalizedstring_key | yes | no | no | lint | no | warning |
应将静态字符串用作NSLocalizedString中的键  
nslocalizedstring_require_bundle | yes | no | no | lint | no | warning |
调用NSLocalizedString应该指定包含字符串文件的捆绑软件  
nsobject_prefer_isequal | no | no | yes | lint | no | warning |
NSObject子类应实现isEqual而不是==  
number_separator | yes | yes | no | style | no | warning, minimum_length: 0 |
使用 _ 分割大数， 让数字更清晰  
object_literal | yes | no | no | idiomatic | no | warning, image_literal:
true, color_literal: true | 避免 image and color 使用字面量初始化， 需要把相关图片名，颜色RGB 等参数定义为
enum struct 或者常量  
opening_brace | no | yes | yes | style | no | warning, allowMultilineFunc:
false | 右括号之前应有一个空格，并与声明在同一行  
operator_usage_whitespace | yes | yes | no | style | no | warning,
lines_look_around: 2, skip_aligned_constants: true | 操作符需要使用一个空格间隔  
operator_whitespace | no | no | yes | style | no | warning |
当定义空格操作符的时候，被定义的名字或类型两边应该各有一个单行空格操作符  
optional_enum_case_matching | yes | yes | no | style | no | warning |
将枚举大小写与不带'？'的可选枚举匹配 在Swift 5.1及更高版本中受支持  
orphaned_doc_comment | no | no | yes | lint | no | warning | 注释要写在声明中  
overridden_super_call | yes | no | no | lint | no | warning, excluded: [],
included: ["*"] | 方法需要调用 super method  
override_in_extension | yes | no | no | lint | no | warning | 扩展不应覆盖声明  
pattern_matching_keywords | yes | no | no | idiomatic | no | warning |
通过将关键字移出元组来组合多个模式匹配绑定  
prefer_nimble | yes | no | no | idiomatic | no | warning  
prefer_self_type_over_type_of_self | yes | yes | no | style | no | warning |
访问属性或调用方法时，最好将“自类型”设置为（of：self)  
prefixed_toplevel_constant | yes | no | no | style | no | warning,
only_private: false | 顶级常量的前缀应为k  
private_action | yes | no | no | lint | no | warning | IBActions应该是私有的  
private_outlet | yes | no | no | lint | no | warning, allow_private_set: false
| IBOutlets 应该设置为 private， 来避免泄露  
private_over_fileprivate | no | yes | yes | idiomatic | no | warning,
validate_extensions: false | 推荐：private 不建议：fileprivate  
private_subject | yes | no | no | lint | no | warning | -  
private_unit_test | no | no | yes | lint | no | warning: XCTestCase | 单元测试方法
不能设置为 private  
prohibited_interface_builder | yes | no | no | lint | no | warning |
禁止用interface Builder 创建视图  
prohibited_super_call | yes | no | no | lint | no | warning, excluded: [[]],
included: [["*"]] | 某些特殊的 override 方法， 禁止调用 super method excluded: [[]],
included: [["*"]]  
protocol_property_accessors_order | no | yes | yes | style | no | warning |
在协议中声明属性 要按顺序先写 get set方法  
quick_discouraged_call | yes | no | no | lint | no | warning |
不鼓励在“describe”和/或“context” 框中进行调用  
quick_discouraged_focused_test | yes | no | no | lint | no | warning |
不鼓励重点测试。专注于此测试时，其他测试将不会运行  
quick_discouraged_pending_test | yes | no | no | lint | no | warning |
不推荐：未开始的测试。标记为待定时，该测试不会运行  
raw_value_for_camel_cased_codable_enum | yes | no | no | lint | no | warning |
设置枚举建议设置默认值  
reduce_boolean | no | no | yes | performance | no | warning |
优先使用.allSatisfy()或.contains() 不建议使用：reduce(true)或reduce(false)  
reduce_into | yes | no | no | performance | no | warning | 对于 copy-on-write
类型，推荐使用 reduce(into: _:) 不建议使用 reduce(_ :_:)  
redundant_discardable_let | no | yes | yes | style | no | warning | 使用 `_ =
foo()` 代替 `let _ = foo()`  
redundant_nil_coalescing | yes | yes | no | idiomatic | no | warning | #避免使用
`object ?? nil` 仅当lhs为nil时才评估nil合并运算符，而n为rhs则合并nil合并运算符  
redundant_objc_attribute | no | yes | yes | idiomatic | no | warning |
Objective-C属性（@objc）在声明中是多余的  
redundant_optional_initialization | no | yes | yes | idiomatic | no | warning
| 用nil初始化可选变量是多余的。 # 默认值赋值为nil 不需要写默认值为 nil  
redundant_set_access_control | no | no | yes | idiomatic | no | warning |
如果属性设置程序访问级别与变量访问级别相同，则不应明确  
redundant_string_enum_value | no | no | yes | idiomatic | no | warning |
在定义字符串枚举的时候, 当字符串枚举值等于枚举名称时，可以不用赋值  
redundant_type_annotation | yes | yes | no | idiomatic | no | warning |
变量不应具有冗余类型注释 建议 var url = URL() 不建议 var url : URL = URL()  
redundant_void_return | no | yes | yes | idiomatic | no | warning |
在函数声明中返回Void是多余的。#在不必要的时候， 不需要写 ->() and -> Void  
required_deinit | yes | no | no | lint | no | warning | 类应具有显式的deinit方法  
required_enum_case | yes | no | no | lint | no | No protocols configured. In
config add 'required_enum_case' to... | 符合指定协议的枚举必须实现特定情况  
return_arrow_whitespace | no | yes | yes | style | no | warning |
前后要有空格，函数定义返回的 -> 前后有空格， 不换行  
shorthand_operator | no | no | yes | style | no | error | 使用+= ， -=， *=， /= 代替
a = a + 1  
single_test_class | yes | no | no | style | no | warning |
测试文件应只包含一个QuickSpec或XCTestCase类  
sorted_first_last | yes | no | no | performance | no | warning |
优先使用min()或max() 不建议使用 sorted().first或sorted().last  
sorted_imports | yes | yes | no | style | no | warning | Imports 应排序  
statement_position | no | yes | yes | style | no | (statement_mode) default,
(severity) warning | 这里主要指的是 else 和 catch 前面要加一个空格， 也不能大于1个空格  
static_operator | yes | no | no | idiomatic | no | warning |
应该将运算符声明为静态函数，而不是自由函数  
strict_fileprivate | yes | no | no | idiomatic | no | warning | fileprivate
应该避免  
strong_iboutlet | yes | yes | no | lint | no | warning | @IBOutlets不应被声明为weak
应该为 strong  
superfluous_disable_command | no | no | yes | lint | no | warning |
当禁用规则不会在禁用区域触发违规时，SwiftLint的“禁用”命令是多余的。如果要记录命令，请使用“-”  
switch_case_alignment | no | no | yes | style | no | warning, indented_cases:
false | Case语句应与其封闭的switch语句垂直对齐，如果没有其他配置，则缩进  
switch_case_on_newline | yes | no | no | style | no | warning | switch 的 case
需要新启一行  
syntactic_sugar | no | yes | yes | idiomatic | no | warning | 语法糖[Int] 代替Array
/ 例：要使用 [] ？ 等数组字典可选项的语法糖  
test_case_accessibility | yes | yes | no | lint | no | warning,
allowed_prefixes: [[]] | -  
todo | no | no | yes | lint | no | warning | 避免 TODOs and FIXMEs 标识  
toggle_bool | yes | yes | no | idiomatic | no | warning | 不让使用 A = !A 建议使用
A.toggle()  
trailing_closure | yes | no | no | style | no | warning,
only_single_muted_parameter: false | 尽可能使用尾随闭包语法  
trailing_comma | no | yes | yes | style | no | warning, mandatory_comma: false
| 数组末尾不要加空格  
trailing_newline | no | yes | yes | style | no | warning | 末尾空行,文件末尾应该有一个空行  
trailing_semicolon | no | yes | yes | idiomatic | no | warning | 行末尾不加分号  
trailing_whitespace | no | yes | yes | style | no | warning,
ignores_empty_lines: false, ignores_comments: true | 每一个空行不能有空格  
type_body_length | no | no | yes | metrics | no | warning: 200, error: 350 |
类型体长度不应该跨越太多行，超过200行给warning，超过350行给error  
type_contents_order | yes | no | no | style | no | warning, order:
[[SwiftLintFramework.TypeContent.case], [SwiftL... | 指定类型内子类型，属性，方法及更多内容的顺序  
type_name | no | no | yes | idiomatic | no | (min_length) w/e: 3/0,
(max_length) w/e: 40/1000, excluded: [],... |
类型名字限制规则,类型名称只能包含字母数字字符，以大写字母开头，并且长度在3到40个字符之间  
unavailable_function | yes | no | no | idiomatic | no | warning |
未实现的功能应标记为不可用  
unneeded_break_in_switch | no | no | yes | idiomatic | no | warning | 在switch-
case语句中, 有方法调用或操作时,避免使用break语句  
unneeded_parentheses_in_closure_argument | yes | yes | no | style | no |
warning | 声明闭包参数时，不需要括号  
unowned_variable_capture | yes | no | no | lint | no | warning |
最好将引用捕获为弱引用以避免潜在的崩溃  
untyped_error_in_catch | yes | yes | no | idiomatic | no | warning |
没有类型转换，catch语句不应声明错误变量  
unused_capture_list | no | no | yes | lint | no | warning | 闭包中没有被使用的参数应该删除  
unused_closure_parameter | no | yes | yes | lint | no | warning | 函数的参数必须被使用  
unused_control_flow_label | no | yes | yes | lint | no | warning |
未使用的控制流标签应被删除  
unused_declaration | yes | no | no | lint | yes | severity: error,
include_public_and_open: false, related_usrs_t... | 在所有被删除的文件中，声明至少应被引用一次  
unused_enumerated | no | no | yes | idiomatic | no | warning | 默认-
当参数没有被全部使用的时候， 不要使用容器的 enumerated 方法  
unused_import | yes | yes | no | lint | yes | severity: warning,
require_explicit_imports: false, allowed_tra... | import 的文件要被使用  
unused_optional_binding | no | no | yes | style | no | warning,
ignore_optional_try: false | 在使用if判断某变量是否为nil的时候, 不建议使用下划线(_) 必须使用定义的 optional
binding  
unused_setter_value | no | no | yes | lint | no | warning | 不使用设定值  
valid_ibinspectable | no | no | yes | lint | no | warning | 默认-IBInspectable
必须是可变参数  
vertical_parameter_alignment | no | no | yes | style | no | warning |
函数参数分为多行书写的时候， 头部（小括号后面一位）必须对齐 函数参数分为多行书写的时候， 头部（小括号后面一位）必须对齐  
vertical_parameter_alignment_on_call | yes | no | no | style | no | warning |
如果函数参数在方法调用中位于多行中，则应垂直对齐  
vertical_whitespace | no | yes | yes | style | no | warning, max_empty_lines:
1 | 垂直方向上的空格行，限制为一行（注释除外） 不能有连续多个空行  
vertical_whitespace_between_cases | yes | yes | no | style | no | warning | 在
switch cases 之间包括一条空行  
vertical_whitespace_closing_braces | yes | yes | no | style | no | N/A |
在关闭大括号之前，请勿包括垂直空格（空行）  
vertical_whitespace_opening_braces | yes | yes | no | style | no | N/A |
打开花括号后，请勿包括垂直空格（空行）  
void_return | no | yes | yes | style | no | warning | -  
weak_delegate | no | yes | yes | lint | no | warning | 代理要设置为弱引用  
xct_specific_matcher | yes | no | no | idiomatic | no | warning |
优先使用特定的XCTest匹配器，XCTAssertEqual而不是XCTAssertNotEqual  
xctfail_message | no | no | yes | idiomatic | no | warning |
XCTFail调用应包括断言的描述，描述不能为空  
yoda_condition | yes | no | no | lint | no | warning | 变量应位于比较运算符的左侧，常数应位于右侧  
  
## 参考文献

  1. [SwiftLint](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Frealm%2FSwiftLint)
  2. [SwiftLint 的理解和使用](https://www.jianshu.com/p/abb4057db849)
  3. [rule-directory](https://links.jianshu.com/go?to=https%3A%2F%2Frealm.github.io%2FSwiftLint%2Frule-directory.html)
  4. [AST](https://links.jianshu.com/go?to=http%3A%2F%2Fclang.llvm.org%2Fdocs%2FIntroductionToTheClangAST.html)
  5. [LLVM优点](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.cnblogs.com%2Fzuopeng%2Fp%2F4141467.html)
  6. [How a Swift file is compiled](https://links.jianshu.com/go?to=https%3A%2F%2Ftrinhngocthuyen.github.io%2Fposts%2Ftech%2Fhow-a-swift-file-is-compiled%2F)
  7. [SwiftSyntax详解](https://www.jianshu.com/p/017caf8ddcaa)
  8. [使用“swiftc”命令编译swift文件时如何导入像“UIKit”这样的模块？](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.jb51.cc%2Fswift%2F820695.html)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [SwiftLint 的理解和使用](https://www.jianshu.com/p/abb4057db849)

目的: iOS APP在下一个版本会用swift开发,在多人开发中,即使有官网的规范模板.但每个人的代码风格和规...

[技术进阶在路上](https://www.jianshu.com/u/7ba33c1f4192)阅读 10,581评论 2赞 13

  * [swiftlint使用](https://www.jianshu.com/p/cd223bcedff9)

网上教程比较多，本文适合小白适用 1、安装 brew install swiftlint 2、根目录添加.swif...

[智能老树皮](https://www.jianshu.com/u/79b88c7fe30b)阅读 267评论 0赞 0

  * [swift代码风格检查利器SwiftLint的使用](https://www.jianshu.com/p/58bfa3dc4256)

如何使用工具检查swift代码风格？可以使用SwiftLint ,见链接https://github.com/re...

[ksnowlv](https://www.jianshu.com/u/6fe5d9875a9e)阅读 359评论 0赞 1

  * [使用Swift提高代码质量！](https://www.jianshu.com/p/d24bb71d3a88)

前言 京喜APP最早在2019年引入了Swift，使用Swift完成了第一个订单模块的开发。之后一年多我们持续在团...

[iOS鑫](https://www.jianshu.com/u/ad9bb9edf44f)阅读 2,749评论 3赞 38

  * [Swiftlint 使用及忽略对照表](https://www.jianshu.com/p/bb2bfcba0aeb)

安装 GitHub上附带了中文的README[https://github.com/realm/SwiftLint...

[大也](https://www.jianshu.com/u/0e0aa351f859)阅读 1,263评论 0赞 0

 