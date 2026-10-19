  * Unidbg补环境实战第一篇：补环境入门

    * 为什么要补环境﻿

    * Unidbg补环境的案例情景复现

    * 模拟执行so

      * 参数获取

      * unidbg 代码初始化

      * 目标函数的调用

      * 补环境说明

      * 实战补环境

    * 本章小节

## Unidbg补环境实战第一篇：补环境入门

`Unidbg`是一个基于`unicorn`的逆向工具，可以黑盒调用安卓和iOS中的so文件。这使得逆向人员可以在无需了解so内部算法原理的情况下，主动调用so中的函数，让其中的算法“为我所用”，只需要传入所需的参数、补全运行所需的环境，即可运行出所需要的结果。及由此衍生的辅助分析、算法还原、`SO`调试与逆向等等功能。

对于Android逆向来说，Unidbg的特点有以下几种：

  1. 模拟JNI调用的API，因此可以调用`JNI_OnLoad`函数。

  2. 支持`JavaVM`和`JNIEnv`。

  3. 支持模拟系统调用指令。

  4. 支持`ARM32`和`ARM64`。

  5. 支持基于`Dobby`的inline hook。

  6. 支持基于`xHook`的GOT hook。

  7. `unicorn`后端支持简单的控制台调试器，gdb stub，指令追踪和内存读写追踪。

  8. 支持`dynarmic`快速的后端。

### 为什么要补环境

使用unidbg最主要的问题就是补环境，补环境对于so的模拟执行太重要了，并且在这块很容易跌跟头。我们知道unidbg的作用是模拟执行so中的函数，也就是使用C/C++编写的函数，它处于Native层。而Native的函数是Java层的函数通过JNI调用起来的，
那么Native也可以通过JNI这座桥梁去调用Java层的函数。

在Native层调用Java层的函数的时候，unidbg中并没有这些函数的实现，那么这些so就无法正常的通过unidbg加载起来。所以我们需要手动的把Java层的函数补充起来，让Native层的函数去调用。

>
> PS：以下所有分析均在`r0env2022`版安卓逆向环境下完成。`r0env2022`版集成了Unidbg，打开终端输入`unidbg`回车，就是一个安装好所有依赖包的可以直接跑项目的完整的`Unidbg`运行环境。

> PS2：案例涉及的代码及附件会放在我的Github中，地址：https://github.com/r0ysue/AndroidSecurityStudy

### Unidbg补环境的案例情景复现

为了给大家讲清本章的内容，笔者开发了一个样本APK构造了一些环境问题。首先我们先熟悉一下这个APP。APP的打开后的界面如图1所示：

![](https://image.3001.net/images/20221214/1671011215_63999b8f3965f81e82763.png!small)  
图1 样本放置的目录

屏幕中央显示了一串字符，感觉像是16进制。然后，我们使用Jadx-gui反编译APK，其中MainActivity.java的代码如下所示：

    
    
    public class MainActivity extends AppCompatActivity {
        private ActivityMainBinding binding;
    
        // 检测文件
        public native void detectFile();
    
        // 检测是否有Hook
        public native void detectHookTool();
    
        // native函数，获取哈希结果
        public native String getHash(String str);
    
        // 加载 so
        static {
            System.loadLibrary("dogpro");
        }
    
        /* JADX INFO: Access modifiers changed from: protected */
        @Override // androidx.fragment.app.FragmentActivity, androidx.activity.ComponentActivity, androidx.core.app.ComponentActivity, android.app.Activity
        public void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            ActivityMainBinding inflate = ActivityMainBinding.inflate(getLayoutInflater());
            this.binding = inflate;
            setContentView(inflate.mo170getRoot());
            TextView tv = this.binding.sampleText;
            detectFile();
            detectHookTool();
            // 获取Hash结果
            String r1 = getHash(getApplicationContext().getPackageCodePath());
            tv.setText(r1);
        }
    }
    

在onCreate中有两个检测，我们先不要理会，他暂时不会对我们本章的内容产生任何的影响。但是可以给大家看看他们做了什么事情：

  * detectFile

    
    
    int __fastcall Java_com_example_dogpro_MainActivity_detectFile(_JNIEnv *a1)
    {
        int v2; // [sp+8h] [bp-30h]
        int v3; // [sp+Ch] [bp-2Ch]
        int v4; // [sp+14h] [bp-24h]
        int MethodID; // [sp+18h] [bp-20h]
        int v6; // [sp+1Ch] [bp-1Ch]
        int v7; // [sp+20h] [bp-18h]
        int Class; // [sp+24h] [bp-14h]
    
        // 反射去Java层找File类
        Class = _JNIEnv::FindClass(a1, "java/io/File");
        v7 = _JNIEnv::AllocObject(a1, Class);
        // 检测的路径
        v6 = _JNIEnv::NewStringUTF(a1, "/sys/class/power_supply/battery/voltage_now");
        MethodID = _JNIEnv::GetMethodID(a1, Class, "<init>", "(Ljava/lang/String;)V");
        _JNIEnv::CallVoidMethod(a1, v7, MethodID, v6);
        v4 = _JNIEnv::GetMethodID(a1, Class, "exists", "()Z");
        if ( (unsigned __int8)_JNIEnv::CallBooleanMethod(a1, v7, v4) )
        _android_log_print(6, "lilac", byte_35D7);
        else
        _android_log_print(6, "lilac", byte_35F0);
        v3 = _JNIEnv::AllocObject(a1, Class);
        v2 = _JNIEnv::NewStringUTF(a1, "/data/local/tmp/nox");
        _JNIEnv::CallVoidMethod(a1, v3, MethodID, v2);
        if ( (unsigned __int8)_JNIEnv::CallBooleanMethod(a1, v3, v4) )
        return _android_log_print(6, "lilac", byte_361D);
        else
        return _android_log_print(6, "lilac", byte_3636);
    }
    

首先检测了电池的相关信息，我们尝试去`/sys/class/power_supply/battery/voltage_now`下查看，如图2所示：

![](https://image.3001.net/images/20221214/1671011215_63999b8fcc42b59910948.png!small)  
图21-2 电池属性

其它文件表示的含义如下所示：

    
    
    //电池充电状态
    cat /sys/class/power_supply/battery/status
    
    //电池电量
    cat /sys/class/power_supply/battery/capacity
    
    //电池运行状况
    cat /sys/class/power_supply/battery/health
    
    //显示电池温度
    cat /sys/class/power_supply/battery/temp
    
    //电池电压 mV
    cat /sys/class/power_supply/battery/voltage_now
    

第二处检测的是`/data/local/tmp/nox`，nox是夜神模拟器，模拟器创建的时候会在此路径有文件的创建。幸运的是，当检测到的时候，并不会有任何的操作，所以我们不予理会，这里只带领大家看看它是如何做检测的。

  * detectHookTool

    
    
    int __fastcall Java_com_example_dogpro_MainActivity_detectHookTool(_JNIEnv *a1)
    {
        int v1; // r0
        int v2; // r0
        const char *StringUTFChars; // [sp+28h] [bp-A0h]
        int ObjectClass; // [sp+34h] [bp-94h]
        int ObjectArrayElement; // [sp+38h] [bp-90h]
        int i; // [sp+3Ch] [bp-8Ch]
        int ArrayLength; // [sp+40h] [bp-88h]
        int v9; // [sp+44h] [bp-84h]
        int v10; // [sp+48h] [bp-80h]
        int v11; // [sp+4Ch] [bp-7Ch]
        int MethodID; // [sp+50h] [bp-78h]
        int Class; // [sp+54h] [bp-74h]
        size_t n; // [sp+6Ch] [bp-5Ch]
        size_t v16; // [sp+7Ch] [bp-4Ch]
        char v17[24]; // [sp+80h] [bp-48h] BYREF
        char v18[36]; // [sp+98h] [bp-30h] BYREF
    
        // 反射找到 Throwable => 异常处理
        Class = _JNIEnv::FindClass(a1, "java/lang/Throwable");
        MethodID = _JNIEnv::GetMethodID(a1, Class, "<init>", "()V");
        v11 = _JNIEnv::NewObject(a1, Class, MethodID);
        // 获取异常堆栈
        v10 = _JNIEnv::GetMethodID(a1, Class, "getStackTrace", "()[Ljava/lang/StackTraceElement;");
        // 调用方法
        v9 = _JNIEnv::CallObjectMethod(a1, v11, v10);
        ArrayLength = _JNIEnv::GetArrayLength(a1, v9);
        // 复制值，检测 Xposed 框架
        strcpy(v18, "de.robv.android.xposed.XposedBridge");
        // 复制值，检测 substrate 框架
        strcpy(v17, "com.saurik.substrate");
        for ( i = 0; i < ArrayLength; ++i )
        {
        ObjectArrayElement = _JNIEnv::GetObjectArrayElement(a1, v9, i);
        ObjectClass = _JNIEnv::GetObjectClass(a1, ObjectArrayElement);
        // 每个堆栈中的信息反射获取类名
        v1 = _JNIEnv::GetMethodID(a1, ObjectClass, "getClassName", "()Ljava/lang/String;");
        v2 = _JNIEnv::CallObjectMethod(a1, ObjectArrayElement, v1);
        StringUTFChars = (const char *)_JNIEnv::GetStringUTFChars(a1, v2, 0);
        n = _strlen_chk(v18, 0x24u);
        // 比对
        if ( !strncmp(StringUTFChars, v18, n) )
        {
            _android_log_print(6, "lilac", "%s", StringUTFChars);
            _android_log_print(6, "lilac", byte_389E);
        }
        v16 = _strlen_chk(v17, 0x15u);
        if ( !strncmp(StringUTFChars, v17, v16) )
        {
            _android_log_print(6, "lilac", "%s", StringUTFChars);
            _android_log_print(6, "lilac", byte_38AE);
        }
        }
        return _stack_chk_guard;
    }
    

上述代码也很简单，获取当前的调用堆栈，并利用反射把每条堆栈信息的类找到，比对类名，是否使用Xposed框架和substrate框架，这里也没有任何的操作。接下来，我们直接去用unidbg去调用起来这个so。

### 模拟执行so

#### 参数获取

首先，我们来看下入参的构造：

    
    
    String r1 = getHash(getApplicationContext().getPackageCodePath());
    

很明显是应用的一些信息，对于这种的系统级别的API，可以去官网查看，也可以通过Hook快速去获取值，这里我们使用Frida去Hook应用程序快速拿到值，毕竟这个不是重要的环节。

Frida的Hook代码如下所示：

    
    
    function main(){
        Java.perform(function(){
            var MainActivity = Java.use("com.example.dogpro.MainActivity");
            MainActivity.onCreate.overload("android.os.Bundle").implementation = function(var_0){
    
                console.log("info:",this.getApplicationContext().getPackageCodePath())
    
                var ret = this.onCreate.overload("android.os.Bundle").call(this,var_0);
        }
    
    
        })
    }
    
    
    setImmediate(main)
    

Hook后的结果如图3所示：

![](https://image.3001.net/images/20221214/1671011216_63999b90a444a6d53e54b.png!small)  
图21-3 Hook的结果

getPackageCodePath()返回此上下文的主要 Android 包的完整路径。 Android 包是一个 ZIP
文件，其中包含应用程序的主要代码和资产。也就是我们看到的base.apk文件。

拿到入参后就可以开始构造unidbg的模拟执行代码了。在很多场景下，为了快速获取结果，甚至都不需要打开IDA去分析又臭又长的伪代码，直接把so放到unidbg中去跑，减少对IDA的依赖。

如果单纯的做算法的分析，毋庸置疑我们一定会使用到IDA。如果我们只是去获取一个执行的结果，我们使用unidbg去模拟就可以了。

#### unidbg 代码初始化

unidbg的代码初始化是把对应的模拟器、内存以及module等接口都配置好，这部分经过网上案例大量的练习，相信大家已经可以熟能生巧了，这里再次给大家展示一下，代码如下所示：

    
    
    public class MainActivity extends AbstractJni{
        private final AndroidEmulator emulator;
        private final VM vm;
        private final Memory memory;
        private final Module module;
    
        public MainActivity(){
            emulator = AndroidEmulatorBuilder
                    // 创建32位的模拟器
                    .for32Bit()
                    // 建立模拟器
                    .build();
    
            // 实现内存接口
            memory = emulator.getMemory();
            // 设置解析的库的SDK
            memory.setLibraryResolver(new AndroidResolver(23));
    
            // 创建虚拟机
            vm = emulator.createDalvikVM();
            // 日志开关
            vm.setVerbose(true);
            // 实现 JNI
            vm.setJni(this);
            // 加载so
            DalvikModule dalvikModule = vm.loadLibrary(
                    new File("unidbg-android/src/test/java/com/r0ysue/Chap22/apkfile/lib/armeabi-v7a/libdogpro.so"), false);
            module = dalvikModule.getModule();
            vm.callJNI_OnLoad(emulator,module);
        }
    
        public static void main(String[] args) {
            MainActivity mainActivity = new MainActivity();
            mainActivity.getHash();
        }
    }
    

#### 目标函数的调用

我们调用的就是so中的getHash函数，它是一个non-static方法，需要一个实例来调用，让我们先看看代码是怎么写的：

    
    
    private void getHash() {
        // 找到调用它的类，和哪个类绑定就使用哪个类
        DvmObject<?> dvmObject = vm.resolveClass("com/example/dogpro/MainActivity").newObject(null);
        // 上面找到的入参
        String input = "/data/app/com.example.dogpro-pnF2J3-qBi8ei74vXTNXmQ==/base.apk";
        // 
        DvmObject<?> ret = dvmObject.callJniMethodObject(emulator, "getHash(Ljava/lang/String;)Ljava/lang/String;", input);
        System.out.println("result ==> "+ret.getValue());
    }
    

#### 补环境说明

首先需要找到调用这个方法的类是哪个，和哪个类绑定就使用哪个类。因为方法是一个实例方法，我们通过newObject来实例化这个类。调用是通过dvmObject来操作，对于JNI方法有如下几种类型，如图4所示：

![](https://image.3001.net/images/20221214/1671011217_63999b914db5ce9392ef8.png!small)  
图4 callJnixxx的几种类型

具体的选择需要看函数的返回值，样本中的getHash函数返回的类型是String，而String的本质就是一个Object，所以使用callJniMethodObject来操纵。

callJniMethodObject中需要传递三个参数，第一个是emulator；第二个是方法及签名，这个可以通过Jadx-gui反编译的结果查看，如图5所示：

![](https://image.3001.net/images/20221214/1671011217_63999b91effcdf880658b.png!small)  
图5 callJniMethodObject中的方法签名

最后就是方法中参数的传递，它是一个可变长度的参数列表。

至此，getHash的调用就构造完成了，然后我们去运行代码，看看是否可以正常的运行。第一次运行后，运行结果主要报错信息如下所示：

    
    
    java.lang.UnsupportedOperationException: java/util/zip/ZipFile-><init>(Ljava/lang/String;)V
    	at com.github.unidbg.linux.android.dvm.AbstractJni.newObjectV(AbstractJni.java:791)
    	at com.github.unidbg.linux.android.dvm.AbstractJni.newObjectV(AbstractJni.java:746)
        ...
    

额外说明一点，如果我们没有去继承AbstractJNI，会出现setJNI的错误，这里已经补全了，就不会出现了。这段报错具体是什么含义呢？大致就是要找java/util/zip/ZipFile这个类的构造方法，但是找不到，所以报了上述的错误。找不到类之后，后续就不知道改怎么往下执行，最终抛出了异常。这种就是Java的一个环境问题。

#### 实战补环境

那我们怎么去补充这个环境呢？其实它已经很智能了，框架都填好了，只需要我们稍作改动即可。补环境，即它要什么，我们就给他什么，根据这个提示来就好。给我们抛出的异常就是一种提示。找到下述异常的所在位置：

    
    
    // com.github.unidbg.linux.android.dvm.AbstractJni.newObjectV(AbstractJni.java:791)
    
    @Override
    public DvmObject<?> newObjectV(BaseVM vm, DvmClass dvmClass, String signature, VaList vaList) {
        switch (signature) {
            case "java/io/ByteArrayInputStream-><init>([B)V": {
                ByteArray array = vaList.getObjectArg(0);
                assert array != null;
                return vm.resolveClass("java/io/ByteArrayInputStream").newObject(new ByteArrayInputStream(array.value));
            }
            ...
        }
    }
    

这里仅仅展示了一个case，在这个方法中，有很多case，这是unidbg作者在设计的时候帮我们做好的，补好的这些具有很强的通用性。而没补齐的是比较特殊的：可能是引用了三方的SDK中的函数，也有可能是厂商自己的函数，这就需要使用者自己去补充。补环境就是在这个方法中接着case继续去写分支。但是这个是在unidbg的项目中，为了代码的可移植性，建议大家写到自己的代码中，因为已经继承了AbstraceJNI，只需要重写就可以了。对于上面的报错，补的代码如下所示：

    
    
    @Override
    public DvmObject<?> newObjectV(BaseVM vm, DvmClass dvmClass, String signature, VaList vaList) {
        if (signature.equals("java/util/zip/ZipFile-><init>(Ljava/lang/String;)V")){
            return vm.resolveClass("java/util/zip/ZipFile").newObject(null);
        }
        return super.newObjectV(vm, dvmClass, signature, vaList);
    }
    

但是大家思考一个问题，这是一个构造方法，并且报错异常中也提供了方法的签名，它的入参是一个String类型的，没有返回值，那我们只是简单的给他传一个null对象肯定是不行的。先把他的入参打印出来看看：

    
    
    @Override
    public DvmObject<?> newObjectV(BaseVM vm, DvmClass dvmClass, String signature, VaList vaList) {
        if (signature.equals("java/util/zip/ZipFile-><init>(Ljava/lang/String;)V")){
            String name = (String) vaList.getObjectArg(0).getValue();
            System.out.println("name => " + name);
            return vm.resolveClass("java/util/zip/ZipFile").newObject(null);
        }
        return super.newObjectV(vm, dvmClass, signature, vaList);
    }
    

打印的结果如下所示：

    
    
    name => /data/app/com.example.dogpro-pnF2J3-qBi8ei74vXTNXmQ==/base.apk
    

很明显这里传了一个APK文件，其主要作用就是解析获取APK内部的资源。那我们同样去构造一个这样的数据，把它作为对象让unidbg去解析,补完后的结果如下所示：

    
    
    @Override
    public DvmObject<?> newObjectV(BaseVM vm, DvmClass dvmClass, String signature, VaList vaList) {
        if (signature.equals("java/util/zip/ZipFile-><init>(Ljava/lang/String;)V")){
            String name = (String) vaList.getObjectArg(0).getValue();
            // System.out.println("name => " + name);
            // return vm.resolveClass("java/util/zip/ZipFile").newObject(null);
            try {
                ZipFile zipFile = new ZipFile(name);
                return vm.resolveClass("java/util/zip/ZipFile").newObject(zipFile);
            } catch (IOException e) {
                e.printStackTrace();
                return null;
            }
        }
        return super.newObjectV(vm, dvmClass, signature, vaList);
    }
    

再次运行代码，又有了新的异常报错，如下所示：

    
    
    [16:39:44 871]  WARN [com.github.unidbg.linux.ARM32SyscallHandler] (ARM32SyscallHandler:532) - handleInterrupt intno=2, NR=-1073744324, svcNumber=0x11f, PC=unidbg@0xfffe0284, LR=RX@0x400016e3[libdogpro.so]0x16e3, syscall=null
    java.lang.NullPointerException
    	at com.github.unidbg.linux.android.dvm.DalvikVM$32.handle(DalvikVM.java:540)
    	at com.github.unidbg.linux.ARM32SyscallHandler.hook(ARM32SyscallHandler.java:131)
    	at com.github.unidbg.arm.backend.UnicornBackend$11.hook(UnicornBackend.java:345)
    	at unicorn.Unicorn$NewHook.onInterrupt(Unicorn.java:128)
    	at unicorn.Unicorn.emu_start(Native Method)
    	at com.github.unidbg.arm.backend.UnicornBackend.emu_start(UnicornBackend.java:376)
    	at com.github.unidbg.AbstractEmulator.emulate(AbstractEmulator.java:380)
        ...
    [16:39:44 873]  WARN [com.github.unidbg.AbstractEmulator] (AbstractEmulator:420) - emulate RX@0x40001281[libdogpro.so]0x1281 exception sp=unidbg@0xbffff610, msg=java.lang.NullPointerException, offset=7ms
    java.nio.file.NoSuchFileException: /data/app/com.example.dogpro-pnF2J3-qBi8ei74vXTNXmQ==/base.apk
    	at java.base/sun.nio.fs.UnixException.translateToIOException(UnixException.java:92)
    	at java.base/sun.nio.fs.UnixException.rethrowAsIOException(UnixException.java:111)
    	at java.base/sun.nio.fs.UnixException.rethrowAsIOException(UnixException.java:116)
    

我们来看最下面的模拟器抛出的异常，即NoSuchFileException，是java中最常见的异常，没有找到这个文件的异常。大家注意：我们当前使用的是unidbg，而不是一个手机的真实环境，所以打印出来的name，即文件的路径我们根本没有，那怎么办呢？传一个本地的APK到模拟器中，最终的代码如下所示：

    
    
    @Override
    public DvmObject<?> newObjectV(BaseVM vm, DvmClass dvmClass, String signature, VaList vaList) {
        if (signature.equals("java/util/zip/ZipFile-><init>(Ljava/lang/String;)V")){
            String name = (String) vaList.getObjectArg(0).getValue();
            // System.out.println("name => " + name);
            // return vm.resolveClass("java/util/zip/ZipFile").newObject(null);
            try {
                if(name.equals("/data/app/com.example.dogpro-pnF2J3-qBi8ei74vXTNXmQ==/base.apk")){
                    ZipFile zipFile = new ZipFile("unidbg-android/src/test/java/com/r0ysue/unidbgBook/Chap22/dogpro.apk");
                    // ZipFile zipFile = new ZipFile(name);
                    return vm.resolveClass("java/util/zip/ZipFile").newObject(zipFile);
                }
            } catch (IOException e) {
                e.printStackTrace();
                return null;
            }
        }
        return super.newObjectV(vm, dvmClass, signature, vaList);
    }
    

这里直接根据签名信息返回了一个ZipFile的对象，然后我们把unidbg中补好的方法return回去，即执行unidbg中补好的环境。别的问题暂时没有出现，我们先不做处理。补充完后再次运行代码,报错如下所示：

    
    
    java.lang.UnsupportedOperationException: java/util/zip/ZipFile->entries()Ljava/util/Enumeration;
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callObjectMethodV(AbstractJni.java:416)
    	at com.r0ysue.unidbgBook.Chap22.MainActivity.callObjectMethodV(MainActivity.java:124)
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callObjectMethodV(AbstractJni.java:262)
        ...
    

报错的异常显示，缺少了ZipFie的entries方法，这个方法是空参，返回值类型是Enumeration对象。我们继续使用上面的方法去补环境，补完后的代码如下所示：

    
    
    @Override
    public DvmObject<?> callObjectMethodV(BaseVM vm, DvmObject<?> dvmObject, String signature, VaList vaList) {
        if (signature.equals("java/util/zip/ZipFile->entries()Ljava/util/Enumeration;")){
            // 拿到操作的对象
            ZipFile zipFile = (ZipFile) dvmObject.getValue();
            // 通过对象来调用方法
            Enumeration<? extends ZipEntry> entries = zipFile.entries();
            return vm.resolveClass("java/util/Enumeration").newOnject(entries);
        }
        return super.callObjectMethodV(vm, dvmObject, signature, vaList);
    }
    

注意这里要补的环境是在callObjectMethodV方法中，根据名称我们也能知道，它是在调用对象中的方法，参数dvmObject就是对象，而这里是调用ZipFile形成的对象中的entries方法，ZipFile对象是在上一个方法中做的实例化，并传入了待解析的APK文件。我们要正真的获取这个对象就需要通过getValue()方法来获取。然后通过这个对象来调用entries方法。根据签名可以知道要返回的类型是Enumeration，直接通过前面的方法返回回去。继续运行代码，看看用这种方式能不能起作用：

    
    
    [17:09:25 902]  WARN [com.github.unidbg.linux.ARM32SyscallHandler] (ARM32SyscallHandler:532) - handleInterrupt intno=2, NR=-1073744324, svcNumber=0x122, PC=unidbg@0xfffe02b4, LR=RX@0x40001253[libdogpro.so]0x1253, syscall=null
    java.lang.ClassCastException: class com.github.unidbg.linux.android.dvm.DvmObject cannot be cast to class com.github.unidbg.linux.android.dvm.Enumeration (com.github.unidbg.linux.android.dvm.DvmObject and com.github.unidbg.linux.android.dvm.Enumeration are in unnamed module of loader 'app')
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callBooleanMethodV(AbstractJni.java:609)
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callBooleanMethodV(AbstractJni.java:602)
    

最开始显示了报错的主要信息，即xxx.DvmObject cannot be cast to
xxx.Enumeration,它们的关系不能通过强转来实现。一般出现这种疑难杂症，我们的首要手段是到unidbg的框架中搜索，看看它有没有相关的处逻辑，在AbstractJNI中，我们果真找到了它的实现逻辑：

    
    
    @Override
    public boolean callBooleanMethodV(BaseVM vm, DvmObject<?> dvmObject, String signature, VaList vaList) {
        switch (signature) {
            case "java/util/Enumeration->hasMoreElements()Z":
                return ((Enumeration) dvmObject).hasMoreElements();
        }
    }
    

在AbstractJNI的同级目录下，可以发现unidbg对它的实现

    
    
    package com.github.unidbg.linux.android.dvm;
    
    import java.util.Iterator;
    import java.util.List;
    
    public class Enumeration extends DvmObject<List<?>> {
    
        private final Iterator<? extends DvmObject<?>> iterator;
    
        public Enumeration(VM vm, List<? extends DvmObject<?>> value) {
            super(vm.resolveClass("java/util/Enumeration"), value);
    
            this.iterator = value == null ? null : value.iterator();
        }
    
        public boolean hasMoreElements() {
            return iterator != null && iterator.hasNext();
        }
    
        public DvmObject<?> nextElement() {
            return iterator.next();
        }
    
    }
    

在Java的中同样有Enumeration类的实现，为什么会这样呢？这是因为unidbg对简单的数据类型都做了封装，并优先使用。比如，我们要返回一个String的对象，一般是这样来写的：

    
    
    return new StringObject(vm,"");
    

而不是使用resolveClass的方式：

    
    
    return vm.resolveClass("java/lang/String"),newOnject(");
    

这是为了后续的处理，unidbg是一个完善的系统，每个环节都有相应的承接，如果使用后者，那么后续的操作需要去做强转就无法识别，从而强转失败。我们既然知道了unidbg中基本的数据类型，就要使用它。

到了这步，就该往里面传入参数了，看下unidbg的Enumeration构造方法：

    
    
    public Enumeration(VM vm, List<? extends DvmObject<?>> value) {
        super(vm.resolveClass("java/util/Enumeration"), value);
        this.iterator = value == null ? null : value.iterator();
    }
    

需要传入的是一个List类型的对象，所以我们去补环境的时候同样也需要给他一个List对象，最终的代码如下所示：

    
    
    @Override
    public DvmObject<?> callObjectMethodV(BaseVM vm, DvmObject<?> dvmObject, String signature, VaList vaList) {
        if (signature.equals("java/util/zip/ZipFile->entries()Ljava/util/Enumeration;")){
            ZipFile zipFile = (ZipFile) dvmObject.getValue();
            Enumeration<? extends ZipEntry> entries = zipFile.entries();
            // return vm.resolveClass("java/util/Enumeration").newObject(entries);
            DvmClass ZipEntryClass = vm.resolveClass("java/util/zip/ZipEntry");
            List<DvmObject<?>> objs = new ArrayList<>();
            while (entries.hasMoreElements()){
                ZipEntry zipEntry = entries.nextElement();
                objs.add(ZipEntryClass.newObject(zipEntry));
            }
            return new com.github.unidbg.linux.android.dvm.Enumeration(vm,objs);
        }
    

同理，我们继续往下补，先运行上述的代码，抛出的异常如下所示：

    
    
    java.lang.UnsupportedOperationException: java/util/zip/ZipEntry->getName()Ljava/lang/String;
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callObjectMethodV(AbstractJni.java:416)
    	at com.r0ysue.unidbgBook.Chap22.MainActivity.callObjectMethodV(MainActivity.java:128)
    

同样是在调用对象的方法，我们需要先获取对象，然后再用对象调用对应的方法，它需要的返回值是一个Sting类型，即通过StrongObject返回，代码如下所示：

    
    
    @Override
    public DvmObject<?> callObjectMethodV(BaseVM vm, DvmObject<?> dvmObject, String signature, VaList vaList) {
        if (signature.equals("java/util/zip/ZipEntry->getName()Ljava/lang/String;")){
            ZipEntry zipEntry = (ZipEntry) dvmObject.getValue();
            String name = zipEntry.getName();
            return new  StringObject(vm,name);
        }
        return super.callObjectMethodV(vm, dvmObject, signature, vaList);
    }
    

继续运行代码，报错如下所示：

    
    
    java.lang.UnsupportedOperationException: java/lang/String->endsWith(Ljava/lang/String;)Z
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callBooleanMethodV(AbstractJni.java:624)
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callBooleanMethodV(AbstractJni.java:602)
    

这个报错出现在callBooleanMethodV方法中，代码如下所示：

    
    
    @Override
    public boolean callBooleanMethodV(BaseVM vm, DvmObject<?> dvmObject, String signature, VaList vaList) {
        if (signature.equals("java/lang/String->endsWith(Ljava/lang/String;)Z")){
            String value = (String) dvmObject.getValue();
            String suffix = (String) vaList.getObjectArg(0).getValue();
            return value.endsWith(suffix);
        }
        return super.callBooleanMethodV(vm, dvmObject, signature, vaList);
    }
    

同样，我们需要先拿到对象，而且endsWith函数中有参数的传递，我们需要把参数也构造出来，vaList是一个可变的参数列表，拿第一个参数即可。继续运行代码，报错异常如下所示：

    
    
    java.lang.UnsupportedOperationException: java/util/zip/ZipFile->getInputStream(Ljava/util/zip/ZipEntry;)Ljava/io/InputStream;
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callObjectMethodV(AbstractJni.java:416)
    	at com.r0ysue.unidbgBook.Chap22.MainActivity.callObjectMethodV(MainActivity.java:128)
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callObjectMethodV(AbstractJni.java:262)
    

这个也是在callObjectMethodV方法中，代码如下所示：

    
    
    @Override
    public DvmObject<?> callObjectMethodV(BaseVM vm, DvmObject<?> dvmObject, String signature, VaList vaList) {
        if (signature.equals("java/util/zip/ZipFile->getInputStream(Ljava/util/zip/ZipEntry;)Ljava/io/InputStream;")){
            ZipFile zipFile = (ZipFile) dvmObject.getValue();
            ZipEntry zipEntry = (ZipEntry) vaList.getObjectArg(0).getValue();
            try {
                InputStream inputStream = zipFile.getInputStream(zipEntry);
                return vm.resolveClass("java/io/InputStream").newObject(inputStream);
            } catch (IOException e) {
                e.printStackTrace();
                return null;
            }
        }
        return super.callObjectMethodV(vm, dvmObject, signature, vaList);
    }
    

由于涉及到了IO的操作，需要包裹到try...catch...中，继续运行代码，报错如下所示：

    
    
    java.lang.UnsupportedOperationException: java/io/InputStream->read([B)I
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callIntMethodV(AbstractJni.java:562)
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callIntMethodV(AbstractJni.java:528)
    	at com.github.unidbg.linux.android.dvm.DvmMethod.callIntMethodV(DvmMethod.java:109)
    	at com.github.unidbg.linux.android.dvm.DalvikVM$47.handle(DalvikVM.java:821)
    

报错发生在callIntMethodV中，需要补的是InputStream中的read方法，根据参数和返回值，补充的代码如下所示：

    
    
    @Override
    public int callIntMethodV(BaseVM vm, DvmObject<?> dvmObject, String signature, VaList vaList) {
        if (signature.equals("java/io/InputStream->read([B)I")){
            InputStream inputStream = (InputStream) dvmObject.getValue();
            byte[] bytes = (byte[]) vaList.getObjectArg(0).getValue();
            try {
                int read = inputStream.read(bytes);
                return read;
            } catch (IOException e) {
                e.printStackTrace();
                return -1;
            }
        }
        return super.callIntMethodV(vm, dvmObject, signature, vaList);
    }
    

继续运行代码，报错信息如下所示：

    
    
    java.lang.UnsupportedOperationException: java/security/MessageDigest->update([B)V
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callVoidMethodV(AbstractJni.java:995)
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callVoidMethodV(AbstractJni.java:978)
    	at com.github.unidbg.linux.android.dvm.DvmMethod.callVoidMethodV(DvmMethod.java:228)
    	at com.github.unidbg.linux.android.dvm.DalvikVM$59.handle(DalvikVM.java:1045)
    

调用了Java SDK中的MessageDigest类，我们继续补，代码如下所示：

    
    
    @Override
    public void callVoidMethodV(BaseVM vm, DvmObject<?> dvmObject, String signature, VaList vaList) {
        if (signature.equals("java/security/MessageDigest->update([B)V")){
            MessageDigest md = (MessageDigest) dvmObject.getValue();
            byte[] bytes = (byte[]) vaList.getObjectArg(0).getValue();
            md.update(bytes);
            return;
        }
        super.callVoidMethodV(vm, dvmObject, signature, vaList);
    }
    

继续运行代码，报错如下所示：

    
    
    java.lang.UnsupportedOperationException: java/security/MessageDigest->digest()[B
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callObjectMethodV(AbstractJni.java:416)
    	at com.r0ysue.unidbgBook.Chap22.MainActivity.callObjectMethodV(MainActivity.java:128)
    	at com.github.unidbg.linux.android.dvm.AbstractJni.callObjectMethodV(AbstractJni.java:262)
    

还缺少了digest方法，我们继续来补齐，代码如下所示：

    
    
    @Override
    public DvmObject<?> callObjectMethodV(BaseVM vm, DvmObject<?> dvmObject, String signature, VaList vaList) {
        if (signature.equals("java/security/MessageDigest->digest()[B")){
            MessageDigest md = (MessageDigest) dvmObject.getValue();
            byte[] digest = md.digest();
            return new ByteArray(vm, digest);
        }
        return super.callObjectMethodV(vm, dvmObject, signature, vaList);
    }
    

再次运行代码，返回的结果就出来了，于此同时，给大家打开了setVarbose开关，把JNI的执行流也输出了，结果如下所示：

    
    
    JNIEnv->CallObjectMethodV(java.util.Enumeration@c730b35, nextElement() => java.util.zip.ZipEntry@3f6f6701) was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->CallObjectMethodV(java.util.zip.ZipEntry@3f6f6701, getName() => "res/drawable/design_ic_visibility.xml") was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->CallObjectMethodV("res/drawable/design_ic_visibility.xml", toLowerCase() => "res/drawable/design_ic_visibility.xml") was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->GetStringUtfChars("res/drawable/design_ic_visibility.xml") was called from RX@0x40001749[libdogpro.so]0x1749
    JNIEnv->CallBooleanMethodV("res/drawable/design_ic_visibility.xml", endsWith("dog.png") => false) was called from RX@0x40001253[libdogpro.so]0x1253
    JNIEnv->CallBooleanMethodV(java.util.Enumeration@c730b35, hasMoreElements() => true) was called from RX@0x40001253[libdogpro.so]0x1253
    JNIEnv->CallObjectMethodV(java.util.Enumeration@c730b35, nextElement() => java.util.zip.ZipEntry@1ed6388a) was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->CallObjectMethodV(java.util.zip.ZipEntry@1ed6388a, getName() => "res/drawable/design_ic_visibility_off.xml") was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->CallObjectMethodV("res/drawable/design_ic_visibility_off.xml", toLowerCase() => "res/drawable/design_ic_visibility_off.xml") was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->GetStringUtfChars("res/drawable/design_ic_visibility_off.xml") was called from RX@0x40001749[libdogpro.so]0x1749
    JNIEnv->CallBooleanMethodV("res/drawable/design_ic_visibility_off.xml", endsWith("dog.png") => false) was called from RX@0x40001253[libdogpro.so]0x1253
    JNIEnv->CallBooleanMethodV(java.util.Enumeration@c730b35, hasMoreElements() => true) was called from RX@0x40001253[libdogpro.so]0x1253
    JNIEnv->CallObjectMethodV(java.util.Enumeration@c730b35, nextElement() => java.util.zip.ZipEntry@4f80542f) was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->CallObjectMethodV(java.util.zip.ZipEntry@4f80542f, getName() => "res/drawable/design_password_eye.xml") was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->CallObjectMethodV("res/drawable/design_password_eye.xml", toLowerCase() => "res/drawable/design_password_eye.xml") was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->GetStringUtfChars("res/drawable/design_password_eye.xml") was called from RX@0x40001749[libdogpro.so]0x1749
    JNIEnv->CallBooleanMethodV("res/drawable/design_password_eye.xml", endsWith("dog.png") => false) was called from RX@0x40001253[libdogpro.so]0x1253
    JNIEnv->CallBooleanMethodV(java.util.Enumeration@c730b35, hasMoreElements() => true) was called from RX@0x40001253[libdogpro.so]0x1253
    JNIEnv->CallObjectMethodV(java.util.Enumeration@c730b35, nextElement() => java.util.zip.ZipEntry@130c12b7) was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->CallObjectMethodV(java.util.zip.ZipEntry@130c12b7, getName() => "res/drawable/design_snackbar_background.xml") was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->CallObjectMethodV("res/drawable/design_snackbar_background.xml", toLowerCase() => "res/drawable/design_snackbar_background.xml") was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->GetStringUtfChars("res/drawable/design_snackbar_background.xml") was called from RX@0x40001749[libdogpro.so]0x1749
    JNIEnv->CallBooleanMethodV("res/drawable/design_snackbar_background.xml", endsWith("dog.png") => false) was called from RX@0x40001253[libdogpro.so]0x1253
    JNIEnv->CallBooleanMethodV(java.util.Enumeration@c730b35, hasMoreElements() => true) was called from RX@0x40001253[libdogpro.so]0x1253
    JNIEnv->CallObjectMethodV(java.util.Enumeration@c730b35, nextElement() => java.util.zip.ZipEntry@5d534f5d) was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->CallObjectMethodV(java.util.zip.ZipEntry@5d534f5d, getName() => "res/drawable/dog.png") was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->CallObjectMethodV("res/drawable/dog.png", toLowerCase() => "res/drawable/dog.png") was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->GetStringUtfChars("res/drawable/dog.png") was called from RX@0x40001749[libdogpro.so]0x1749
    JNIEnv->CallBooleanMethodV("res/drawable/dog.png", endsWith("dog.png") => true) was called from RX@0x40001253[libdogpro.so]0x1253
    JNIEnv->GetMethodID(java/util/zip/ZipFile.getInputStream(Ljava/util/zip/ZipEntry;)Ljava/io/InputStream;) => 0xb225c4d4 was called from RX@0x40001195[libdogpro.so]0x1195
    JNIEnv->CallObjectMethodV(java.util.zip.ZipFile@557caf28, getInputStream(java.util.zip.ZipEntry@5d534f5d) => java.io.InputStream@a38c7fe) was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->GetMethodID(java/io/InputStream.read([B)I) => 0x7b2c3fda was called from RX@0x40001195[libdogpro.so]0x1195
    JNIEnv->NewByteArray(256) was called from RX@0x40001769[libdogpro.so]0x1769
    JNIEnv->FindClass(java/security/MessageDigest) was called from RX@0x40001127[libdogpro.so]0x1127
    JNIEnv->GetStaticMethodID(java/security/MessageDigest.getInstance(Ljava/lang/String;)Ljava/security/MessageDigest;) => 0x5c20796 was called from RX@0x40001799[libdogpro.so]0x1799
    JNIEnv->NewStringUTF("MD5") was called from RX@0x40001165[libdogpro.so]0x1165
    JNIEnv->CallStaticObjectMethodV(class java/security/MessageDigest, getInstance("MD5") => java.security.MessageDigest@25641d39) was called from RX@0x400017eb[libdogpro.so]0x17eb
    JNIEnv->CallIntMethodV(java.io.InputStream@a38c7fe, read([B@7b36aa0c) => 0x100) was called from RX@0x4000185f[libdogpro.so]0x185f
    JNIEnv->GetMethodID(java/security/MessageDigest.update([B)V) => 0x7d1a6599 was called from RX@0x40001195[libdogpro.so]0x1195
    JNIEnv->CallVoidMethodV(java.security.MessageDigest@25641d39, update([B@7b36aa0c)) was called from RX@0x400011e7[libdogpro.so]0x11e7
    JNIEnv->GetMethodID(java/security/MessageDigest.digest()[B) => 0x6ccd1d46 was called from RX@0x40001195[libdogpro.so]0x1195
    JNIEnv->CallObjectMethodV(java.security.MessageDigest@25641d39, digest() => [B@5824a83d) was called from RX@0x400016e3[libdogpro.so]0x16e3
    JNIEnv->GetArrayLength([B@5824a83d => 16) was called from RX@0x400018c7[libdogpro.so]0x18c7
    JNIEnv->NewStringUTF("D3E550889725A6A7C5E834ECCDB4B73E") was called from RX@0x40001165[libdogpro.so]0x1165
    result ==> D3E550889725A6A7C5E834ECCDB4B73E
    

明显的可以看到，JNI的执行流就是我们刚才补充环境的顺序，当然有一些是unidbg帮我们补好的。

跟着笔者的思路一路下来终于把结果运行了出来，过程中不知补了多少函数。但是获取最终结果的那一刹那，前面做的所有的努力都是值得的。有意思的是，我们并不知道这其中会有多少函数，也不知道我们会在哪一个节点放弃，这可能就是unidbg的魅力吧。就像人生一样，我们并不知道是否会有一个结果，在每一个时间节点都在努力，但是不知道这样的坚持是否会有结果，期待每一个读者都会有一个完美的结局。

### 本章小节

本章中，笔者带领正式的学习了如何去补环境。其实跟着笔者走下来，你可能会发现，补环境毫无规律可言，需要的是不断实操的经验。接下来我们还会继续探索补环境的技巧，请系好安全带！

