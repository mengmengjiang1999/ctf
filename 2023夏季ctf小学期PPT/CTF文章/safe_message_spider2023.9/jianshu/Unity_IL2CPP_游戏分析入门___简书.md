Unity IL2CPP 游戏分析入门

[ fenfei331](https://www.jianshu.com/u/01dab7278c9f)关注赞赏支持

# Unity IL2CPP 游戏分析入门

## 一、目标

很多时候App加密本身并不难，难得是他用了一套新玩意，天生自带加密光环。例如PC时代的VB，直接ida的话，汇编代码能把你看懵。

但是要是搞明白了他的玩法，VB Decompiler一上，那妥妥的就是源码。

Unity 和 Flutter 也是如此。

最近迷上了一个小游戏 Dream Blast，今天就拿他解剖吧。

com.rovio.dream

## 二、步骤

### 侦测敌情

从apk包里面发现libil2cpp.so，就足以证明是Unity写的游戏了。

在Android下Unity有两种玩法，一种是Mono方式打包，我们可以从包内拿到Assembly-CSharp.dll，如果开发者没有对Assembly-
CSharp.dll进行加密处理，那么我们可以很方便地使用ILSpy.exe对其进行反编译。这样看到的就是妥妥的C#源码了。

由于总所周知的原因，这种玩法肯定会被公司开除的。现在工作这么难找，所以大家都采取第二种玩法了，使用IL2CPP方式打包，就没有Assembly-
CSharp.dll。这样就不会让人轻易攻破了。

这时候就需要召唤出IL2CPP界的Decompiler了。

### Il2CppDumper

[https://github.com/Perfare/Il2CppDumper](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2FPerfare%2FIl2CppDumper)

Il2CppDumper 通过 assets/bin/Data/Managed/Metadata/global-metadata.dat 字符串文件 和
lib/armeabi-v7a/libil2cpp.so 游戏二进制文件来还原C#写的代码逻辑。

目前只有编译好的windows可执行文件，所以目前只能在win下使用。(本例演示的是Arm32)

1、先把global-metadata.dat 和 libil2cpp.so 这两个文件拷贝到同一个目录。

2、运行 Il2CppDumper-x86.exe，在弹出的文件选择框里面，先选择 libil2cpp.so，然后再选择 global-
metadata.dat。

    
    
    Initializing metadata...
    Metadata Version: 27
    Initializing il2cpp file...
    Applying relocations...
    WARNING: find JNI_OnLoad
    ERROR: This file may be protected.
    Il2Cpp Version: 27
    Searching...
    Change il2cpp version to: 27.1
    CodeRegistration : 205f9c8
    MetadataRegistration : 205ff3c
    Dumping...
    Done!
    Generate struct...
    Done!
    Generate dummy dll...
    Done!
    Press any key to exit...
    

这就算反编译成功了。

一共会生成 DummyDll 目录， script.json，stringliteral.json，dump.cs，il2cpp.h 等文件。

script.json和stringliteral.json是辅助ida 和ghidra 分析的，可以用 ida.py 这个脚本导入到ida里面去。

这会我们只关心 dump.cs。

### 存盘文件

为了 _好好_ 玩一个游戏，除了改内存，还一个重要的方案就是改配置文件甚至改存盘文件了。

遥想当年帝国时代非得搞个200的人口上限，直接hook一下，把200改成2000他不香吗？ (电脑拖崩溃了)

_细心_ 分析了一下，这个游戏的存盘文件在

/sdcard/Android/data/com.rovio.dream/files/usesr/XXX-XXX-XXX/prefs.json

改它，改它，可是它加密了

### 分析

这时候显示出 _dump.cs_ 的用处了，这可是活地图呀。

在里面搜一下 "prefs.json"

    
    
    [CreateAssetMenuAttribute] // RVA: 0x3979B8 Offset: 0x3979B8 VA: 0x3979B8
    public class UserPrefs : UserPrefsBase, IInitializable, IInitializableInit // TypeDefIndex: 7278
    {
            // Fields
            private const string EK = "8CSstq6cz1Gp9YSQpr2l";
            private const string PrefsFileName = "prefs.json";
       ....
               // RVA: 0xAAE690 Offset: 0xAAE690 VA: 0xAAE690 Slot: 42
            public void Init() { }
        ....
    

从这里得到两个有用的信息，一个是存盘文件在UserPrefs类里面处理，再一个EK可能就是密钥或者密钥的一部分。

可以上ida了，打开libil2cpp.so细嚼慢咽一下。

首先运行 Il2CppDumper-v6\ida_py3.py (低版本的ida请跑ida.py)

然后 在弹出的文件选择框里面 ，选择刚才反编译出来的script.json，最后再跑一次ida_py3.py 把stringliteral.json
也加进来。

万事俱备了，我们去分析一下 UserPrefs_Init() ,地图告诉我们它在 0xAAE690，

ida里面去到 0xAAE690， 然后Create Function， 再F5以下，代码就出来了。

代码看上去还是有点懵，它似乎 System_Guid__NewGuid(v47, 0); 生成了个guid，然后再加上了EK

    
    
    v43 = System_String__Concat_23810904(*(_DWORD *)(a1 + 28), StringLiteral_1313, 0);
    

StringLiteral_1313就是 EK。

不过好消息是 最后 它要初始化一个 CryptoUtility___ctor

    
    
    int __fastcall CryptoUtility___ctor(int a1)
    {
      int v2; // r6
      _DWORD *UTF8; // r0
    
      if ( !byte_2173DF8 )
      {
        sub_48CE2C(&System_Security_Cryptography_AesManaged_TypeInfo);
        sub_48CE2C(&System_Security_Cryptography_Rfc2898DeriveBytes_TypeInfo);
        sub_48CE2C(&StringLiteral_1149);
        byte_2173DF8 = 1;
      }
      v2 = sub_48CF00(System_Security_Cryptography_AesManaged_TypeInfo);
      System_Security_Cryptography_AesManaged___ctor(v2, 0);
      *(_DWORD *)(a1 + 16) = v2;
      System_Object___ctor(a1, 0);
      UTF8 = (_DWORD *)System_Text_Encoding__get_UTF8(0);
      if ( !UTF8 )
        sub_48CF08();
      return sub_9DB34C(*UTF8, &StringLiteral_1149, *(_DWORD *)(*UTF8 + 344), *(_DWORD *)(*UTF8 + 340));
    }
    

很明显，算法是 AES， 那么key是啥呢？ aes还有cbc和ecb，又应该是哪一个呢？

### Rfc2898DeriveBytes

幸亏咱还是懂点C#的，一个优秀的C#程序员，看到AesManaged和Rfc2898DeriveBytes，就知道套路了。

Rfc2898DeriveBytes的入参是一个password和salt，然后生成一组key和iv，后面就是aes做AES-128-CBC了。

目标很明确了，搞到pwd和salt。

ida双击进到 sub_9DB34C

    
    
    void __fastcall sub_9DB34C(
            int a1,
            _DWORD *a2,
            int a3,
            int (__fastcall *a4)(int, _DWORD),
            int a5,
            int a6,
            int a7,
            int a8,
            int a9,
            int a10)
    {
      int v10; // r4
      int v11; // r5
      int v12; // r6
      int v13; // r7
      int v14; // r6
      int v15; // r0
    
      v13 = a4(v12, *a2);
      v14 = sub_48CF00(System_Security_Cryptography_Rfc2898DeriveBytes_TypeInfo);
      v15 = System_Security_Cryptography_Rfc2898DeriveBytes___ctor(v14, v11, v13, 0);
      if ( !v14 )
        sub_48CF08(v15);
      ...
    

真相只有一个，hook 这个 System_Security_Cryptography_Rfc2898DeriveBytes___ctor 就可以拿到
pwd和salt了。 a2是pwd，a3是 salt。

###### Tip:

[https://github.com/microsoft/referencesource/blob/master/mscorlib/system/security/cryptography/rfc2898derivebytes.cs](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fmicrosoft%2Freferencesource%2Fblob%2Fmaster%2Fmscorlib%2Fsystem%2Fsecurity%2Fcryptography%2Frfc2898derivebytes.cs)

    
    
    int __fastcall System_Security_Cryptography_Rfc2898DeriveBytes___ctor_17396484(int a1, int a2, int a3, int a4)
    {
      int v8; // r6
    
      if ( !byte_2176D99 )
      {
        sub_48CE2C((int)&System_Security_Cryptography_HMACSHA1_TypeInfo);
        byte_2176D99 = 1;
      }
      System_Security_Cryptography_DeriveBytes___ctor(a1, 0);
      System_Security_Cryptography_Rfc2898DeriveBytes__set_Salt(a1, a3);
      System_Security_Cryptography_Rfc2898DeriveBytes__set_IterationCount(a1, a4);
      *(_DWORD *)(a1 + 20) = a2;
      v8 = sub_48CF00(System_Security_Cryptography_HMACSHA1_TypeInfo);
      System_Security_Cryptography_HMACSHA1___ctor_22256684(v8, a2, 0);
      *(_DWORD *)(a1 + 16) = v8;
      return System_Security_Cryptography_Rfc2898DeriveBytes__Initialize(a1);
    }
    

说干就干

    
    
    var libxx = Process.getModuleByName("libil2cpp.so");
    console.log("*****************************************************");
    console.log("name: " +libxx.name);
    console.log("base: " +libxx.base);
    console.log("size: " +ptr(libxx.size));
    
    Interceptor.attach(ptr(libxx.base).add(0x1097304),{
        onEnter: function(args){
            console.log("=== pwd");
            console.log(TAG + hexdump(ptr(this.context.r1), { offset: 0, length: 128, header: true, ansi: true }) );
    
            console.log("=== salt ");
            console.log(TAG + hexdump(ptr(this.context.r2), { offset: 0, length: 64, header: true, ansi: true }) );
    
    
        },
        onLeave:function(retval){
        }
    });
    

这就尴尬了

    
    
    Error: unable to find module 'libil2cpp.so'
    

libil2cpp.so 大概率是动态载入的，所以刚启动app的时候木有libil2cpp.so。

如果我们要hook的函数之后会被多次调用，那么可以延迟几秒钟来载入 setTimeout(main, 1000*3);

不过这里我们要hook的都是init和ctor之类的初始化函数，几秒钟之后可能都初始化完成了。

### hook_constructor

要第一时间hook 动态载入的so，就需要从so的加载开始搞

    
    
    function hook_constructor0() {
        if (Process.pointerSize == 4) {
            var linker = Process.findModuleByName("linker");
        } else {
            var linker = Process.findModuleByName("linker64");
        }
    
        var addr_call_function =null;
        var addr_g_ld_debug_verbosity = null;
        var addr_async_safe_format_log = null;
        if (linker) {
            var symbols = linker.enumerateSymbols();
            for (var i = 0; i < symbols.length; i++) {
                var name = symbols[i].name;
                if (name.indexOf("call_function") >= 0){
                    addr_call_function = symbols[i].address;
                }
                else if(name.indexOf("g_ld_debug_verbosity") >=0){
                    addr_g_ld_debug_verbosity = symbols[i].address;
    
                    ptr(addr_g_ld_debug_verbosity).writeInt(2);
    
                } else if(name.indexOf("async_safe_format_log") >=0 && name.indexOf('va_list') < 0){
    
                    addr_async_safe_format_log = symbols[i].address;
    
                }
    
            }
        }
        if(addr_async_safe_format_log){
            Interceptor.attach(addr_async_safe_format_log,{
                onEnter: function(args){
                    this.log_level  = args[0];
                    this.tag = ptr(args[1]).readCString()
                    this.fmt = ptr(args[2]).readCString()
                    if(this.fmt.indexOf("c-tor") >= 0 && this.fmt.indexOf('Done') < 0){
                        this.function_type = ptr(args[3]).readCString(), // func_type
                        this.so_path = ptr(args[5]).readCString();
                        var strs = new Array(); //定义一数组
                        strs = this.so_path.split("/"); //字符分割
                        this.so_name = strs.pop();
                        this.func_offset  = ptr(args[4]).sub(Module.findBaseAddress(this.so_name))
    
    
                        if(this.so_name == "libil2cpp.so") {
    
                    var targetSo = Module.findBaseAddress(this.so_name);
    
                    console.log(TAG +' so_name:',this.so_name);
                    console.log(TAG +' ptr:',ptr(targetSo));
    
                    hookDbg(targetSo);
                        }
    
                    }
                },
                onLeave: function(retval){
    
                }
            })
        }
    }
    
    function hookDbg(targetSo){
        Interceptor.attach(targetSo.add(0xAAE690),{
            onEnter: function(args){
                console.log(" UserPrefs_ctor *****************************************************");
    
            },
            onLeave:function(retval){
            }
        });
    
    
        Interceptor.attach(ptr(targetSo).add(0x1097304),{
            onEnter: function(args){
                console.log("=== pwd");
                console.log(TAG + hexdump(ptr(this.context.r1), { offset: 0, length: 128, header: true, ansi: true }) );
    
                console.log("=== salt ");
                console.log(TAG + hexdump(ptr(this.context.r2), { offset: 0, length: 64, header: true, ansi: true }) );
            },
            onLeave:function(retval){
            }
        });
    
    }
    

这次的结果就比较完美了

rc.png

Rfc2898DeriveBytes的入参是String，可以看到String在内存中的布局， 0x0C 开始的4个字节是
字符串长度，0x10开始才是真正的字符串。

password 是存档的文件夹名称+EK

salt 是个固定的字符串

带着这个结果我们再回过头去看 UserPrefs__Init的F5的代码，重点关注那几个 System_String_Concat 就更有心得了。

## 三、总结

为了抵抗Il2CppDumper，敌人变狡猾了，所以作者推出了更帅的 _Zygisk-Il2CppDumper_

现在套路这么多，技能得不断更新才能跟的上，又要掉头发了。

变来变去的都是外围，万变不离其宗的还是arm汇编，最后的定位还是需要你的汇编功底。

网络游戏改存盘是没用的，一联服务器就把你覆盖了。

ffshow.png

_富贵故如此，营营何所求_

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [il2cpp Unity手游逆向破解修改](https://www.jianshu.com/p/a34942d01d2e)

之前分享了一款很好玩的海战游戏，上一次分析它，是因为在玩耍过程中遇到了一个可以连续开炮的变态修改版，严重的破坏了公...

[h080294](https://www.jianshu.com/u/22207f3e84de)阅读 29,579评论 8赞 13

  * [ IL2CPP 深入讲解：方法调用介绍](https://www.jianshu.com/p/1999dcbf4e46)

IL2CPP深入讲解：方法调用介绍 IL2CPP INTERNALS: METHOD CALLS 作者：JOSH ...

[IndieACE](https://www.jianshu.com/u/d4bcaa9410ea)阅读 3,049评论 0赞 2

  * [用Unity做游戏，你需要深入了解一下IL2CPP](https://www.jianshu.com/p/dd430c991d0b)

这次我们翻译了一篇Unity官方博客上的文章，原文题目为AN INTRODUCTION TO IL2CPP INT...

[IndieACE](https://www.jianshu.com/u/d4bcaa9410ea)阅读 6,485评论 0赞 30

  * [内存解析Il2cpp函数地址](https://www.jianshu.com/p/6a261e1ba432)

目的 使用函数名拿到U3D非导出函数指针 起因 相对u3d游戏进行hook基本上离不开 Il2CppDumper[...

[约你一起偷西瓜](https://www.jianshu.com/u/d6bd8ae8f6b0)阅读 3,066评论 0赞 3

  * [CTF(一四月)](https://www.jianshu.com/p/637e6b828e4c)

1、xgm(CRYPTO) 似乎是RSA？❌发现n1 n2是相同的，查阅资料https://www.jianshu...

[gufsicsxzf](https://www.jianshu.com/u/5feacda19e87)阅读 706评论 0赞 0

 