都2023年了，你还在用老掉牙的class-dump吗？

众所周知，class-dump已经是个废弃的项目，由于原理是利用Objective-C的运行时机制，因此只能获取Objective-C的头文件，无法应对Swift开发的应用，所以新的class-dump方案必须要能针对Swift的APP正常运行。

因此目前需要新的方案，既可以获取Objective-C的头文件，又可以获取Swift类的定义，现在有了新的工具可以实现这些功能。

# resymbol

## 工具地址

<https://github.com/paradiseduo/resymbol>

看名字像是要做一个符号表恢复的工具，但是由于恢复符号表需要类的信息，因此也具有class-dump的功能。

## 使用方法

使用方法很简单，但是需要电脑上安装了Xcode，期待后续作者可以提供直接编译好的二进制文件：

    
    
    ❯ git clone https://github.com/paradiseduo/resymbol.git
    ❯ cd resymbol
    ❯ ./build-macOS_x86.sh
    ❯ ./resymbol
    OVERVIEW: resymbol v1.0.0
    
    Restore symbol
    
    USAGE: resymbol <file-path> [--ipa] [--symbol] [--class]
    
    ARGUMENTS:
      <file-path>             The machO/IPA to restore symbol.
    
    OPTIONS:
      -i, --ipa               If restore symbol ipa, please set this flag. Default false mean is machO file path.
      -s, --symbol            Dump Symbol Table.
      -c, --class             Dump Class.
      --version               Show the version.
      -h, --help              Show help information.
    

## 效果展示

简单写了一个Swift的程序，不算复杂，这是源代码：

    
    
    enum MyEnum {
        case red
        case blue
        case yellow
    }
    
    struct BaseStruct  {
        var bbname: String = "BaseStruct"
    }
    
    struct MyStruct  {
        var sid: Int = 123
        var sname: String = "hello"
    }
    
    class BaseClass {
        var bcname: String = "BaseClass"
    
        func baseMe() {
            print("BaseClass")
        }
    }
    
    final class MyClass : BaseClass  {
        var cid: Int = 456
        var cname: String = "world"
        var st: MyStruct? = nil
        override func baseMe() {
            print("MyClass")
        }
    }
    
    class YourClass : BaseClass  {
        var i1: Int32 = 456
        var i2: Int16 = 456
        var i3: UInt16 = 456
        var i4: UInt32 = 456
        var i5: Int64 = 456
        var i6: UInt64 = 456
        var c1: CGFloat = 0.0
    }
    
    class HeClass : YourClass  {
    
    }
    

看一下dump出来的结果：

    
    
    ❯ ./resymbol -c -s ~/Desktop/asdhj                                                                                                                                                                                                                                             at 10:24:01
    @interface asdhj.HeClass   //0x0000c7c0
    @end
    
    @interface asdhj.BaseClass :Swift._SwiftObject  //0x0000c4a0
    {
      Swift.Type bcname; //0x0000c0e8
    }
    @end
    
    @interface asdhj.MyClass   //0x0000c558
    {
      Swift.Type cid; //0x0000c1a0
      Swift.Type cname; //0x0000c1c0
      Swift.Type st; //0x0000c1e0
    }
    @end
    
    @interface asdhj.YourClass   //0x0000c628
    {
      Swift.Type i1; //0x0000c298
      Swift.Type i2; //0x0000c2b8
      Swift.Type i3; //0x0000c2d8
      Swift.Type i4; //0x0000c2f8
      Swift.Type i5; //0x0000c318
      Swift.Type i6; //0x0000c338
      Swift.Type c1; //0x0000c358
    }
    @end
    
    class BaseClass {
        var bcname: String
    
        func asdhj.BaseClass.bcname.getter : Swift.String(){}
        func asdhj.BaseClass.bcname.setter : Swift.String(){}
        func asdhj.BaseClass.bcname.modify : Swift.String(){}
        func asdhj.BaseClass.baseMe() -> ()(){}
        func asdhj.BaseClass.__allocating_init() -> asdhj.BaseClass(){}
    }
    
    struct BaseStruct {
        var bbname: String
    }
    
    struct MyStruct {
        var sid: Int
        var sname: String
    }
    
    class HeClass: YourClass {
    }
    
    enum MyEnum {
        case red
        case blue
        case yellow
    }
    
    class MyClass: BaseClass {
        var cid: Int
        var cname: String
        var st: MyStruct?
    }
    
    class YourClass: BaseClass {
        var i1: Swift.Int32
        var i2: Swift.Int16
        var i3: Swift.UInt16
        var i4: Swift.UInt32
        var i5: Swift.Int64
        var i6: Swift.UInt64
        var c1: CoreGraphics.CGFloat
    
        func asdhj.YourClass.i1.getter : Swift.Int32(){}
        func asdhj.YourClass.i1.setter : Swift.Int32(){}
        func asdhj.YourClass.i1.modify : Swift.Int32(){}
        func asdhj.YourClass.i2.getter : Swift.Int16(){}
        func asdhj.YourClass.i2.setter : Swift.Int16(){}
        func asdhj.YourClass.i2.modify : Swift.Int16(){}
        func asdhj.YourClass.i3.getter : Swift.UInt16(){}
        func asdhj.YourClass.i3.setter : Swift.UInt16(){}
        func asdhj.YourClass.i3.modify : Swift.UInt16(){}
        func asdhj.YourClass.i4.getter : Swift.UInt32(){}
        func asdhj.YourClass.i4.setter : Swift.UInt32(){}
        func asdhj.YourClass.i4.modify : Swift.UInt32(){}
        func asdhj.YourClass.i5.getter : Swift.Int64(){}
        func asdhj.YourClass.i5.setter : Swift.Int64(){}
        func asdhj.YourClass.i5.modify : Swift.Int64(){}
        func asdhj.YourClass.i6.getter : Swift.UInt64(){}
        func asdhj.YourClass.i6.setter : Swift.UInt64(){}
        func asdhj.YourClass.i6.modify : Swift.UInt64(){}
        func asdhj.YourClass.c1.getter : CoreGraphics.CGFloat(){}
        func asdhj.YourClass.c1.setter : CoreGraphics.CGFloat(){}
        func asdhj.YourClass.c1.modify : CoreGraphics.CGFloat(){}
    }
    

效果看起来不错，甚至一些被Swift隐藏的函数信息都dump出来了。

