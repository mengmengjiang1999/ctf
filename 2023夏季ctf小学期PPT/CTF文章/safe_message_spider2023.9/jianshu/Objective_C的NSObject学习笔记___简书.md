Objective-C的NSObject学习笔记

[ 寻心_0a46](https://www.jianshu.com/u/46546c30f8db)关注赞赏支持

# Objective-C的NSObject学习笔记

#### NSObject

    
    
    @interface NSObject <NSObject> {
    #pragma clang diagnostic push
    #pragma clang diagnostic ignored "-Wobjc-interface-ivars"
        Class isa  OBJC_ISA_AVAILABILITY;
    #pragma clang diagnostic pop
    }
    

**大多数Objective-C类层次结构的根类，子类从NSObject中继承并得到访问运行时系统的基本接口能力以及作为Objective-
C对象的行为能力** 。

#### NSObject协议

**协议提供的方法是所有Objective-C对象的基础** 。一个符合这个协议的对象可以被认为是一个一级对象。可以这样询问一个对象：

  * 类及其类在继承层次结构中的位置。

  * 是否符合协议。

  * 响应特定消息的能力

Cocoa根类NSObject采用此协议，因此从NSObject继承的所有对象都具有此协议描述的特性。

#### NSObject协议提供的函数

    
    
    - (BOOL)isEqual:(id)object;
    

**函数描述** ： **返回一个布尔值，该值指示调用方和给定对象是否相等**
。此方法定义实例相等的含义，如果两个对象相等，则它们必须具有相同的哈希值。如果在子类中定义isEqual:并打算将该子类的实例放入集合中，确保在子类中也定义了散列。

参数 ：

anObject ： 要与调用方进行比较的对象。可能为nil，在这种情况下，此方法返回NO。

返回值 ： 如果调用方和对象相等，则为“YES”，否则为“NO”。

    
    
    - (id)performSelector:(SEL)aSelector;
    

**函数描述** ： **将指定的消息发送到调用方并返回消息的结果**
。performSelector:方法相当于直接向调用方发送一个aSelector消息。例如，以下消息都执行相同的操作：

id aClone = [anObject copy];  
id aClone = [anObject performSelector:@selector(copy)];  
id aClone = [anObject performSelector:sel_getUid("copy")];

**performSelector:方法允许发送直到运行时才确定的消息。这意味着可以将消息选择器(SEL) 变量作为一个参数传递** :

SEL aSelector = findTheAppropriateSelectorForTheCurrentSituation();  
id returnedObject = [anObject performSelector:aSelector];

注 ： **如果选择器不是创建方法之一（如copy），则通常调用方不负责返回对象的内存**
，因为不同的消息对于它们返回的对象需要不同的内存管理策略，使用哪种策略可能并不明显。由于这种不确定性，如果在使用ARC管理内存时提供变量选择器，因为它不能在编译时确定返回对象的所有权，所以ARC假设调用者不需要取得所有权，这时编译器将生成警告告知潜在的内存泄漏。为了避免警告，如果知道aSelector没有返回值，可以使用performSelectorOnMainThread:withObject:waitUntilDone:或NSObject中提供的相关方法。

参数 ：

aSelector ：
标识要发送的消息的选择器。消息不应包含任何参数。如果aSelector为空，则引发NSInvalidArgumentException。

返回值 ： 作为消息结果的对象。

    
    
    - (id)performSelector:(SEL)aSelector withObject:(id)object;
    

**函数描述** ： **以对象作为参数向调用方发送消息**
。此方法与performSelector相同：不同之处在于可以为aSelector提供参数。aSelector应标识接受类型id的单个参数的方法。对于具有其他参数类型和返回值的方法，请使用NSInvocation。

参数 ：

aSelector ： 标识要发送的消息的选择器。如果aSelector为空，则引发NSInvalidArgumentException。

anObject ： 作为消息唯一参数的对象。

返回值 ： 作为消息结果的对象。

    
    
    - (id)performSelector:(SEL)aSelector withObject:(id)object1 withObject:(id)object2;
    

**函数描述** ： **用两个对象作为参数向调用方发送消息**
。此方法与performSelector相同：不同之处在于可以为一个selector提供两个参数。aSelector应该标识一个可以接受两个id类型参数的方法。对于具有其他参数类型和返回值的方法，请使用NSInvocation。

参数 ：

aSelector ： 标识要发送的消息的选择器。如果aSelector为空，则引发NSInvalidArgumentException。

anObject ： 作为消息第一个参数的对象。

anotherObject ： 作为消息第二个参数的对象。

返回值 ： 作为消息结果的对象。

    
    
    - (BOOL)isProxy;
    

**函数描述** ： **返回一个布尔值，该值指示调用方是否从NSObject派生**
。这个方法是必要的，因为发送isKindOfClass:或isMemberOfClass:到NSProxy对象将测试代理所代表的对象，而不是代理本身。使用此方法测试调用方是否为代理(或其他根类的成员)。

返回值 ： 如果调用方确实从NSObject派生，则为NO，否则为YES。

    
    
    - (BOOL)isKindOfClass:(Class)aClass;
    

**函数描述** ： 返回一个布尔值，该值 **指示调用方是给定类的实例还是从该类继承的任何类的实例** 。

参数 ：

aClass ： 表示要测试的Objective-C类的类对象。

返回值 ： 如果调用方是aClass的实例或从aClass继承的任何类的实例，则为YES，否则为NO。

注 ：
在类簇表示的对象上使用此方法时要小心。由于类簇的性质，返回的对象可能并不总是所期望的类型，如果调用一个返回类簇的方法，那么这个返回类簇的方法返回的确切类型才是可以对该对象做什么操作的最佳指示，而不是依靠isKindOfClass:判断。
例如，如果一个方法返回一个指向NSString对象的指针，不应该使用这个方法来查看字符串是否可变，如下面的代码所示:

截屏2022-06-29 14.40.19.png

如果在代码中使用这样的结构，可能会认为修改一个实际上不应该修改的对象是可以的。这样做可能会给期望对象保持不变的其他代码带来问题。

    
    
    - (BOOL)isMemberOfClass:(Class)aClass;
    

**函数描述** ：返回一个布尔值，该值 **指示调用方是否为给定类的实例**
。类对象可以是编译器创建的对象(例如元类)，但它们仍然支持成员的概念，因此也可以使用此方法验证调用方是否是特定的类对象。

参数 ：

aClass ： 表示要测试的Objective-C类的类对象。

返回值 ： 如果调用方是aClass的实例，则为“YES”，否则为“NO”。

    
    
    - (BOOL)conformsToProtocol:(Protocol *)aProtocol;
    

**函数描述** ： 返回一个布尔值， **指示调用方是否符合给定的协议**
。此方法的工作方式与NSObject中声明的conformsToProtocol:class方法相同。它是为了方便起见而提供的，这样就不需要获取类对象来确定实例是否能够响应给定的消息集。

参数 ：

aProtocol ： 表示特定协议的协议对象。

返回值 ： 如果调用方符合协议，则为“YES”，否则为“NO”。

    
    
    - (BOOL)respondsToSelector:(SEL)aSelector;
    

**函数描述** ： 返回一个布尔值，该值 **指示调用方是否实现或继承可以响应指定消息的方法** 。

应用程序负责确定不响应是否应视为错误。无法通过使用super关键字向对象发送responssToSelector：来测试对象是否从其超类继承了方法。这个方法仍然将测试对象作为一个整体，而不仅仅是超类的实现。因此，发送respondsToSelector:
到
super相当于发送给self。必须直接在对象的超类上调用NSObject类的instancesRespondToSelector:方法，如下面的代码片段所示：

    
    
    if([MySuperclass instancesRespondToSelector:@selector(aMethod)]) {
    //调用继承的方法
     [super aMethod];
    }
    

不能简单地使用[[self
superclass]instancesRespondToSelector:@selector(aMethod)]，因为如果方法被子类调用，这可能会导致方法失败。

需要注意的是如果调用方能够将一个选择器消息转发到另一个对象，那么它将也是能够响应消息，尽管设置是间接的响应，即使这个方法返回NO。

参数 ：

aSelector ： 标识消息的选择器。

返回值 ：如果调用方实现或继承一个可以响应aSelector的方法，则为YES，否则为NO。

注：一个关于respondsToSelector:函数返回NO的记录，代理类明明遵循了协议，并且也实现了代理方法，但是respondsToSelector:函数还是返回了NO，导致代理的函数没有被调用，通过对比另外一个注册代理并成功调取代理函数的类发现了问题：

respondsToSelector:函数返回YES的：

截屏2020-07-07上午11.18.56.png

respondsToSelector:函数返回NO的：

截屏2020-07-07上午11.20.00.png

虽然通过self.delegate判断代理对象是存在的，但是代理对象并没有初始化，导致respondsToSelector:函数返回NO。

    
    
    - (instancetype)retain OBJC_ARC_UNAVAILABLE;
    

**函数描述** ： **增加调用方的引用计数**
。如果要防止对象在使用完之前被释放，请向该对象发送retain消息。当对象的引用计数达到0时，将自动释放该对象。保留消息增加引用计数，释放消息减少引用计数。

为方便起见，retain返回self，因为它可以在嵌套表达式中使用。  
只有在定义自己的引用计数方案时，才能实现此方法。这样的实现必须返回self，并且不应该通过向super发送retain消息来调用继承的方法。

返回值 ： self。

    
    
    - (oneway void)release OBJC_ARC_UNAVAILABLE;
    

**函数描述** ： **减少调用方的引用计数**
。当调用方的引用计数达到0时，会向其发送dealloc消息。只需要实现此方法来定义自己的引用计数方案。这样的实现不应该调用继承的方法，也就是说它们不应该包含发送给super的发布消息。

    
    
    - (instancetype)autorelease OBJC_ARC_UNAVAILABLE;
    

**函数描述** ：减少调用方在当前自动释放池块结束时的保留计数。

返回值 ： self。

    
    
    - (NSUInteger)retainCount OBJC_ARC_UNAVAILABLE;
    

**函数描述** ：
不要使用这种方法。此方法在调试内存管理问题时没有任何价值。由于任意数量的框架对象可能保留了一个对象以保存对它的引用，而同时autorelease池可能保留了对象上任何数量的延迟释放，因此很难从该方法中获得有用的信息。

返回值 ： 调用方的引用计数。

#### NSObject协议提供的属性

    
    
    @property (readonly, copy) NSString *description;
    

**属性描述** ： 包含实类名和调用方id的十六进制数的字符串。

    
    
    @property (readonly, copy) NSString *debugDescription;
    

**属性描述** ： **返回一个字符串，该字符串描述要在调试器中显示的调用方的内容** 。调试器的print
object命令调用此方法以生成对象的文本描述。NSObject通过调用description方法来实现此方法。因此，默认情况下，对象的调试描述与其描述相同。但是，如果要解除它们的耦合，可以重写debugDescription。

返回值 ： 描述在调试器中显示的调用方内容的字符串。

#### NSObject的常用函数

    
    
    + (void)load;
    

**函数描述** ： **每当向Objective-C运行时添加类或分类时调用**
。实现此方法以在加载时执行特定于类的行为。加载消息将发送到动态加载和静态链接的类和分类，但前提是新加载的类或分类实现了可以响应的方法。

初始化顺序如下：

  * 链接到的任何框架中的所有初始值设定项。
  * 图像中的所有+load方法。
  * 映像中的所有C++静态初始化器和C/C++ +属性（构造函数）函数
  * 框架中所有链接到的初始化器。

此外：

  * 类的+load方法在其所有超类的+load方法之后调用。
  * 在类自身的+load方法之后调用category(分类)的+load方法。  
因此，在自定义的load实现中，可以从同一个映像中安全地向其他不相关的类发送消息，但是这些类实现的任何load方法可能尚未运行。

    
    
    + (void)initialize;
    

**函数描述** ： **在类接收到第一个消息之前初始化该类**
。运行时在类或从类继承的任何类从程序内部发送其第一个消息之前向程序中的每个类发送initialize。超类在子类之前接收此消息。

运行时以线程安全的方式向类发送初始化消息。也就是说，initialize由第一个线程运行，以向类发送消息，任何试图向该类发送消息的其他线程都将阻塞，直到初始化完成。

如果子类没有实现initialize(运行时将调用继承的实现)，或者子类显式地调用[super
initialize]，超类实现可能会被调用多次。如果想保护类不被多次运行，可以按照以下思路构建实现：

    
    
    + (void)initialize {
      if (self == [ClassName self]) {
        // ……执行初始化…
      }
    }
    

**因为initialize是以阻塞的方式调用的，所以将方法实现限制在尽可能少的工作量是很重要的**
。特别是任何在初始化方法中接受其他类可能需要的锁的代码都可能导致死锁。因此，对于复杂的初始化不应依赖initialize，而应将其限制为直接的类本地初始化。

    
    
    - (instancetype)init
    #if NS_ENFORCE_NSOBJECT_DESIGNATED_INITIALIZER
        NS_DESIGNATED_INITIALIZER
    #endif
        ;
    

**函数描述** ： 由子类实现，以便 **在分配新对象(调用方)的内存后立即对其进行初始化**
。init消息与alloc(或allocWithZone:)消息耦合在同一行代码中，例如：

SomeClass *object = [[SomeClass alloc] init];

**对象在初始化之前还不能使用。在此方法的自定义实现中，必须调用super的初始化，然后初始化并返回新对象。如果新对象不能初始化，该方法应该返回nil。例如**
，一个假设的BuiltInCamera类如果在没有摄像头的设备上运行，可能会从init方法返回nil。

初始化实例：

    
    
    - (instancetype)init {
        if (self = [super init]) {
            // 初始化自身
        }
        return self;
    }
    

在某些情况下，init方法的自定义实现可能会返回一个替代对象。因此，在后续代码中，必须始终使用init返回的对象，而不是alloc或allocWithZone:返回的对象。

在NSObject类中定义的init方法不进行初始化，它只是返回self。在可空性方面，调用者可以假设init的NSObject实现不返回nil。

返回值 ： 初始化的对象，如果由于某种原因无法创建对象而不会导致异常，则为nil。

    
    
    + (instancetype)alloc OBJC_SWIFT_UNAVAILABLE("use object initializers instead");
    

**函数描述** ： **返回调用类的新实例**
。这是初始化为描述类的数据结构的新实例的实例变量，所有其他实例变量的内存都设置为0。必须使用init…方法来完成初始化过程。例如:

    
    
    TheClass *newObject = [[TheClass alloc] init];
    

不要覆盖alloc以包含初始化代码。相反，实现init的类特定版本…方法。  
由于历史原因，alloc调用allocWithZone:。

返回值 ： 调用类的新实例。

    
    
    + (instancetype)allocWithZone:(struct _NSZone *)zone OBJC_SWIFT_UNAVAILABLE("use object initializers instead");
    

**函数描述** ： **返回调用类的新实例**
。这是初始化为描述类的数据结构的新实例的实例变量，所有其他实例变量的内存设置为0。必须使用init…方法来完成初始化过程。例如:

    
    
    TheClass *newObject = [[TheClass alloc] init];
    

不要重写allocWithZone:以包含任何初始化代码。相反，实现init的类特定版本…方法。这种方法是由于历史原因而存在的；Objective-
C不再使用内存区域。

参数 ：

zone ： 忽略此参数。

返回值 ： 调用类的新实例。

    
    
    - (void)dealloc OBJC_SWIFT_UNAVAILABLE("use 'deinit' to define a de-initializer");
    

**函数描述** ： **释放接收方占用的内存**
。随后发送到调用方的消息可能会生成一个错误，指示已将消息发送到已解除分配的对象（前提是尚未重用已解除分配的内存）。

重写此方法以释放对象实例变量以外的资源，例如：

    
    
    - (void)dealloc {
        free(myBigBlockOfMemory);
    }
    

**在dealloc的实现中，不要调用超类的实现。应该尽量避免使用dealloc管理有限资源(如文件描述符)的生存期。永远不要直接发送dealloc消息。对象的dealloc方法由运行时调用**
。

    
    
    + (Class)class OBJC_SWIFT_UNAVAILABLE("use 'aClass.self' instead");
    

**函数描述** ： **返回类对象**
。当一个类是消息的接收者时，只引用它的名称。在所有其他情况下，类对象必须通过此方法或类似方法获得。例如：这里SomeClass作为参数传递给isKindOfClass:方法(在NSObject协议中声明)：

    
    
    BOOL test = [self isKindOfClass:[SomeClass class]];
    

返回值：类对象。

    
    
    NS_INLINE id _Nullable CFBridgingRelease(CFTypeRef CF_CONSUMED _Nullable X) {
        return (__bridge_transfer id)X;
    }
    

**函数描述** ： **将非Objective-C指针移动到Objective-C，并将所有权转移到ARC**
。使用此函数可以将核心基础样式对象转换为Objective-C对象，并将对象的所有权转移到ARC，这样就不必释放对象。

例如：将CFStringRef转为Objective-C的NSString：

    
    
    NSString *fontName = (NSString *)CFBridgingRelease(CTFontCopyName((__bridge CTFontRef)font, kCTFontPostScriptNameKey));
    

#### NSObject(NSKeyValueCoding) -- KVC键值编码

**KVC全称Key Value
Coding(键值编码)，是一个基于NSKeyValueCoding非正式协议实现的机制，它可以直接通过key值对对象的属性进行存取操作，而不需通过调用明确的存取方法。这样就可以在运行时动态的访问和修改对象的属性，而不是在编译时确定**
。如果.h文件在interface中提供了对类属性的访问，则使用点语法与KVC的差别不大，但如果.h文件在interface中没有实现对属性的访问，则点语法无法访问，但通过KVC可以进行访问。NSObject、NSArray、NSDictionary、NSMutableDictionary、NSOrderedSedzt和NSSet都有自己的NSKeyValueCoding非正式协议扩展。

##### KVC常用函数

    
    
    - (void)setValue:(nullable id)value forKey:(NSString *)key;
    

**函数描述** ： **将给定Key指定的调用方的属性设置为给定值(通过Key来设置值)**
。如果Key标识一对一的关系，则将value指定的对象与调用方关联，如果存在，则取消对先前相关对象的关联。给定一个集合对象和一个标识多对多关系的键，将集合中包含的对象与调用方关联起来，如果存在先前相关的对象，则取消对它们的关联。

参数 ：

value ： 由Key标识的属性的值。

key ： 调用方属性之一的名称。

    
    
    - (nullable id)valueForKey:(NSString *)key;
    

**函数描述** ：返回由给定Key标识的属性的值。

参数 ：

key ： 调用方属性之一的名称。

返回值 ： 由Key标识的属性的值。

![\\color{red}{简单的存储示例：}](https://math.jianshu.com/math?formula=%5Ccolor%7Bred%7D%7B%E7%AE%80%E5%8D%95%E7%9A%84%E5%AD%98%E5%82%A8%E7%A4%BA%E4%BE%8B%EF%BC%9A%7D)

    
    
    TestKVCModel.h文件
    
    #import <Foundation/Foundation.h>
    
    @interface TestKVCModel : NSObject
    
    @end
    
    TestKVCModel.m文件
    
    #import "TestKVCModel.h"
    
    @interface TestKVCModel()
    
    @property (nonatomic, copy) NSString *name;
    @property (nonatomic, copy) NSString *age;
    
    @end
    
    @implementation TestKVCModel
    
    @end
    
    TestCodeController.h文件
    
    #import <UIKit/UIKit.h>
    
    @interface TestCodeController : UIViewController
    
    @end
    
    TextCodeController.m文件
    
    #import "TestCodeController.h"
    #import "TestKVCModel.h"
    
    @interface TestCodeController ()
    
    @end
    
    @implementation TestCodeController
    
    - (void)viewDidLoad {
    
        [super viewDidLoad];
        TestKVCModel *testMoodel = [[TestKVCModel alloc]init];
        [testMoodel setValue:@"小明" forKey:@"name"];
        [testMoodel setValue:@"25" forKey:@"age"];
        
        NSLog(@"%@",[testMoodel valueForKey:@"name"]);
        NSLog(@"%@",[testMoodel valueForKey:@"age"]);
       
    }
    
    @end
    
    

打印结果 ：

截屏2020-09-10下午10.22.17.png

    
    
    - (void)setValue:(nullable id)value forKeyPath:(NSString *)keyPath;
    

**函数描述** ： **将给定keyPath标识的属性的值设置为给定值**
。该方法的默认实现使用valueForKey:获取每个关系的目标对象，并向最终对象发送一个setValue:forKey:消息。

参数 ：

value ： 由keyPath标识的属性的值。

keyPath ：
类关系的键路径。属性(具有一个或多个关系):例如“department.name”或“department.manager.lastName”。

    
    
    - (nullable id)valueForKeyPath:(NSString *)keyPath;
    

**函数描述** ： **返回由给定keyPath标识的派生属性的值**
。默认实现使用valueForKey:获取每个关系的目标对象，并将valueForKey:消息的结果返回到最终对象。

参数 ：

keyPath ：
类关系的关键路径。属性(有一个或多个关系);例如“department.name”或“department.manager.lastName”。

返回值 ： 由keyPath标识的派生属性的值。

![\\color{red}{对于有层次的模型简单的存储示例：}](https://math.jianshu.com/math?formula=%5Ccolor%7Bred%7D%7B%E5%AF%B9%E4%BA%8E%E6%9C%89%E5%B1%82%E6%AC%A1%E7%9A%84%E6%A8%A1%E5%9E%8B%E7%AE%80%E5%8D%95%E7%9A%84%E5%AD%98%E5%82%A8%E7%A4%BA%E4%BE%8B%EF%BC%9A%7D)

    
    
    TestKVCModel.h文件
    
    #import <Foundation/Foundation.h>
    
    @interface TestKVCModel : NSObject
    
    - (instancetype)initWithPersonalHobbiesModel;
    
    @end
    
    TestKVCModel.m文件
    
    #import "TestKVCModel.h"
    
    @interface PersonalHobbiesModel : NSObject
    
    @property (nonatomic, copy) NSString *playGame;
    @property (nonatomic, copy) NSString *read;
    
    @end
    
    @implementation PersonalHobbiesModel
    
    
    @end
    
    @interface TestKVCModel()
    
    @property (nonatomic, copy) NSString *name;
    @property (nonatomic, copy) NSString *age;
    @property (nonatomic, strong) PersonalHobbiesModel *hobbiesModel;
    
    @end
    
    @implementation TestKVCModel
    
    - (instancetype)initWithPersonalHobbiesModel{
        self = [super init];
        if(self){
            self.hobbiesModel = [[PersonalHobbiesModel alloc]init];
        }
        return self;
    }
    
    @end
    
    TestCodeController.h文件
    
    #import <UIKit/UIKit.h>
    
    @interface TestCodeController : UIViewController
    
    @end
    
    TextCodeController.m文件
    
    #import "TestCodeController.h"
    #import "TestKVCModel.h"
    
    
    @interface TestCodeController ()
    
    @end
    
    @implementation TestCodeController
    
    - (void)viewDidLoad {
    
        [super viewDidLoad];
        TestKVCModel *testMoodel = [[TestKVCModel alloc]initWithPersonalHobbiesModel];
        [testMoodel setValue:@"小明" forKey:@"name"];
        [testMoodel setValue:@"25" forKey:@"age"];
        [testMoodel setValue:@"英雄联盟" forKeyPath:@"hobbiesModel.playGame"];
        [testMoodel setValue:@"中国通史" forKeyPath:@"hobbiesModel.read"];
        
        NSLog(@"%@",[testMoodel valueForKey:@"name"]);
        NSLog(@"%@",[testMoodel valueForKey:@"age"]);
        NSLog(@"%@",[testMoodel valueForKeyPath:@"hobbiesModel.playGame"]);
        NSLog(@"%@",[testMoodel valueForKeyPath:@"hobbiesModel.read"]);
       
    }
    
    @end
    
    

输出结果 ：

截屏2020-09-11下午10.00.53.png

注：
**setValue:forKey:函数是无法直接通过类似hobbiesModel.playGame的Key进行层次赋值的，程序会调用setValue:value
forUndefinedKey:key函数，这个函数会默认抛出NSUnknownKeyException异常** 。

    
    
    - (void)setValue:(nullable id)value forUndefinedKey:(NSString *)key;
    

**函数描述** ： **由setValue:forKey:调用，当它没有找到给定Key的属性时。子类可以重写此方法以以其他方式处理请求**
。默认实现会引发NSUndefinedKeyException异常。

参数 ：

value ： 由Key标识的属性的值。

key ： 不等于调用方任何属性名称的字符串。

    
    
    - (nullable id)valueForUndefinedKey:(NSString *)key;
    

**函数描述** ： **由valueForKey:调用，当它没有找到与给定Key相对应的属性时。子类可以重写此方法以返回未定义Key的替代值**
。默认实现会引发NSUndefinedKeyException异常。

参数 ：

key ： 不等于调用方任何属性名称的字符串。

![\\color{red}{简单的处理异常示例 ：
}](https://math.jianshu.com/math?formula=%5Ccolor%7Bred%7D%7B%E7%AE%80%E5%8D%95%E7%9A%84%E5%A4%84%E7%90%86%E5%BC%82%E5%B8%B8%E7%A4%BA%E4%BE%8B%20%EF%BC%9A%20%7D)

    
    
    TestKVCModel.h文件
    
    #import <Foundation/Foundation.h>
    
    
    @interface TestKVCModel : NSObject
    
    - (instancetype)initWithPersonalHobbiesModel;
    
    @end
    
    TestKVCModel.m文件
    
    #import "TestKVCModel.h"
    
    @interface PersonalHobbiesModel : NSObject
    
    @property (nonatomic, copy) NSString *playGame;
    @property (nonatomic, copy) NSString *read;
    
    @end
    
    @implementation PersonalHobbiesModel
    
    
    @end
    
    @interface TestKVCModel()
    
    @property (nonatomic, copy) NSString *name;
    @property (nonatomic, copy) NSString *age;
    @property (nonatomic, strong) PersonalHobbiesModel *hobbiesModel;
    
    @end
    
    @implementation TestKVCModel
    
    - (instancetype)initWithPersonalHobbiesModel{
        self = [super init];
        if(self){
            self.hobbiesModel = [[PersonalHobbiesModel alloc]init];
        }
        return self;
    }
    
    - (void)setValue:(nullable id)value forUndefinedKey:(NSString *)key{
        NSLog(@"设置%@发生异常了，但我重写了函数后不会崩溃",key);
    }
    
    - (nullable id)valueForUndefinedKey:(NSString *)key{
        NSLog(@"把这个错误的Key-%@抛给你",key);
        return key;
    }
    
    @end
    
    TestCodeController.h文件
    
    #import <UIKit/UIKit.h>
    
    @interface TestCodeController : UIViewController
    
    @end
    
    TextCodeController.m文件
    
    #import "TestCodeController.h"
    #import "TestKVCModel.h"
    
    @interface TestCodeController ()
    
    @end
    
    @implementation TestCodeController
    
    - (void)viewDidLoad {
    
        [super viewDidLoad];
        TestKVCModel *testMoodel = [[TestKVCModel alloc]initWithPersonalHobbiesModel];
        [testMoodel setValue:@"小明" forKey:@"name"];
        [testMoodel setValue:@"25" forKey:@"age"];
        [testMoodel setValue:@"英雄联盟" forKeyPath:@"hobbiesModel.playGame"];
        [testMoodel setValue:@"中国通史" forKeyPath:@"hobbiesModel.read"];
        [testMoodel setValue:@"这个key不存在的" forKey:@"unknownKey"];
        
        NSLog(@"%@",[testMoodel valueForKey:@"name"]);
        NSLog(@"%@",[testMoodel valueForKey:@"age"]);
        NSLog(@"%@",[testMoodel valueForKeyPath:@"hobbiesModel.playGame"]);
        NSLog(@"%@",[testMoodel valueForKeyPath:@"hobbiesModel.read"]);
        NSLog(@"%@",[testMoodel valueForUndefinedKey:@"unknownKey"]);
       
    }
    
    @end
    
    

输出结果 ：

截屏2020-09-11下午11.24.59.png

##### KVC常用属性

    
    
    @property (class, readonly) BOOL accessInstanceVariablesDirectly;
    

**属性描述** ： **返回一个布尔值，该值指示键值编码方法在找不到属性的访问器方法时是否应直接访问相应的实例变量**
。默认值返回YES。子类可以重写它返回NO，在这种情况下，键值编码方法不会访问实例变量。

返回值 ： 如果键值编码方法在查找不到属性的访问器方法时应直接访问相应的实例变量，则为“YES”，否则为“NO”。

![\\color{red}{例如：}](https://math.jianshu.com/math?formula=%5Ccolor%7Bred%7D%7B%E4%BE%8B%E5%A6%82%EF%BC%9A%7D)在下面简单的例子中，如果accessInstanceVariablesDirectly函数返回NO，但没有@property
(nonatomic, copy) NSString *nickName属性，程序会直接调用
setValue:forUndefinedKey：函数抛出异常。单如果accessInstanceVariablesDirectly函数返回YES，则键值编码方法会依次寻找_nickName、_isNickName、nickName、isNickName进行设置值的操作，如果这四个实例变量都未找到，则调用setValue:forUndefinedKey：函数抛出异常。

    
    
    TestKVCModel.h文件
    
    #import <Foundation/Foundation.h>
    
    @interface TestKVCModel : NSObject
    
    - (instancetype)initWithPersonalHobbiesModel;
    - (void)logMemberVariable;
    
    @end
    
    TestKVCModel.m文件
    
    #import "TestKVCModel.h"
    
    @interface PersonalHobbiesModel : NSObject
    
    @property (nonatomic, copy) NSString *playGame;
    @property (nonatomic, copy) NSString *read;
    
    @end
    
    @implementation PersonalHobbiesModel
    
    
    @end
    
    @interface TestKVCModel(){
        @public NSString *_nickName;
        @public NSString *_isNickName;
        @public NSString *nickName;
        @public NSString *isNickName;
        
    }
    
    @property (nonatomic, copy) NSString *name;
    @property (nonatomic, copy) NSString *age;
    @property (nonatomic, strong) PersonalHobbiesModel *hobbiesModel;
    
    @end
    
    @implementation TestKVCModel
    
    - (instancetype)initWithPersonalHobbiesModel{
        self = [super init];
        if(self){
            self.hobbiesModel = [[PersonalHobbiesModel alloc]init];
        }
        return self;
    }
    
    - (void)setValue:(nullable id)value forUndefinedKey:(NSString *)key{
        NSLog(@"设置%@发生异常了，但我重写了函数后不会崩溃",key);
    }
    
    - (nullable id)valueForUndefinedKey:(NSString *)key{
        NSLog(@"把这个错误的Key-%@抛给你",key);
        return key;
    }
    
    + (BOOL)accessInstanceVariablesDirectly{
        return NO;
    }
    
    - (void)logMemberVariable{
        NSLog(@"%@",self->_nickName);
        NSLog(@"%@",self->_isNickName);
        NSLog(@"%@",self->nickName);
        NSLog(@"%@",self->isNickName);
    }
    
    @end
    
    TestCodeController.h文件
    
    #import <UIKit/UIKit.h>
    
    @interface TestCodeController : UIViewController
    
    
    @end
    
    TextCodeController.m文件
    
    #import "TestCodeController.h"
    #import "TestKVCModel.h"
    
    @interface TestCodeController ()
    
    @end
    
    @implementation TestCodeController
    
    - (void)viewDidLoad {
    
        [super viewDidLoad];
        TestKVCModel *testMoodel = [[TestKVCModel alloc]initWithPersonalHobbiesModel];
        [testMoodel setValue:@"小明" forKey:@"name"];
        [testMoodel setValue:@"25" forKey:@"age"];
        [testMoodel setValue:@"英雄联盟" forKeyPath:@"hobbiesModel.playGame"];
        [testMoodel setValue:@"中国通史" forKeyPath:@"hobbiesModel.read"];
        [testMoodel setValue:@"这个key不存在的" forKey:@"unknownKey"];
        [testMoodel setValue:@"明" forKey:@"nickName"];
        
        NSLog(@"%@",[testMoodel valueForKey:@"name"]);
        NSLog(@"%@",[testMoodel valueForKey:@"age"]);
        NSLog(@"%@",[testMoodel valueForKeyPath:@"hobbiesModel.playGame"]);
        NSLog(@"%@",[testMoodel valueForKeyPath:@"hobbiesModel.read"]);
        NSLog(@"%@",[testMoodel valueForUndefinedKey:@"unknownKey"]);
        [testMoodel logMemberVariable];
    
    }
    
    @end
    
    

使用KVC就可以任意修改属性的值么？当然不是，例如在IOS13以后，在UITextField中修改textColor属性，便会抛出Access to
UITextField's _placeholderLabel ivar is prohibited. This is an application
bug异常。代码如下：

    
    
    [textField setValue:[UIColor whiteColor] forKeyPath:@"_placeholderLabel.textColor"];
    

