题目来源于海淀区网络与信息安全管理员大赛，题目中将加密验证算法打包进.so，在程序中动态调用check。

本题目通过System.loadLibrary("native-lib")加载了libnative-lib.so文件，该文件通过jeb可以实现提取

![202211251614776.png](https://image.3001.net/images/20221125/1669368116_638089348a22f1f694f2c.png!small)

图1 题目关键代码

##  **调试环境选择与配置**

  * mumu模拟器 x64位版本，测试后发现sprintf会导致程序崩溃

  * 夜神模拟器x64,x32的版本经过测试后，sprintf均导致程序崩溃

  * 雷电5模拟器测试后,sprintf导致程序崩溃，动态调试libnative-lib.so时，且无法下载libart.so

  * 最终选用 mumu x32位版本可以进行调试

  * 动态调试选用IDA+MUMU x86模拟器对动态库libnative-lib.so调试

###  **调试环境**

###  **adb的基础配置**

  * mumu模拟器使用的adb为adb_server.exe，这里将adb_server.exe为便于使用重新命名为adb.exe,打开一个cmd终端，adb 接入模拟器中

    
    
    adb connect 127.0.0.1:7555

![202211251614778.png](https://image.3001.net/images/20221125/1669368118_63808936be01e6560fd8b.png!small)

图2 adb 服务端连接

  * 通过adb 将apk 包安装进安卓的模拟器

    
    
    adb install test.apk

  

  * 通过cmd再打开一个终端，通过adb shell可以直接进入到模拟器shell中

![202211251614779.png](https://image.3001.net/images/20221125/1669368119_63808937d230d6b2d07ff.png!small)

图3 adb shell连接

###  **应用程序的配置**

  * 在新起的cmd终端，通过动态调试模式来启动app

    
    
    ./adb shell am start -D -n com.example.dynamic/.MainActivity

  * android包实际的packet以及类如下图所示com.example.dynamic/.MainActivity

![202211251614780.png](https://image.3001.net/images/20221125/1669368121_638089394b972fcc1c96b.png!small)

图4 adb 启动程序分析

  * 运行`adb shell am start`命令后，mumu模拟器中如图5所示

![202211251614781.png](https://image.3001.net/images/20221125/1669368122_6380893abf2b9291ed291.png!small)

图5 adb 动态调试程序

###  **IDA 的配置**

  * 上传IDA的动态服务端android_x86_server到模拟器/data/local/tmp中，tmp文件夹是具有可执行权限的

    
    
    ./adb push android_x86_server /data/local/tmp

![202211251614782.png](https://image.3001.net/images/20221125/1669368123_6380893bc61b52732dfe3.png!small)

图6 查看tmp文件夹权限

  * 赋予android_x86_server可执行权限

    
    
    chmod +x android_x86_server

  * 执行android_x86_server，会监听23946端口，但是仍需要通过adb进行端口转发转发到本地监听

    
    
    ./adb.exe forward tcp:23946 tcp:23946

![202211251614783.png](https://image.3001.net/images/20221125/1669368125_6380893d1c9f6916ffa15.png!small)

图7 启动IDA 调试server端

  * 通过以上步骤使启动服务端IDA的监听

  * 配置本地IDA remote linux debug参数，如图8所示

![202211251614784.png](https://image.3001.net/images/20221125/1669368126_6380893e32210929d17fe.png!small)

图8 配置IDA动态调试

  * 通过attach process 打开远程端的进程

![202211251614785.png](https://image.3001.net/images/20221125/1669368127_6380893f1139272a24c3a.png!small)

图9 IDA远程attach

  * 选择对应的进程，这里选用1535进程

![202211251614786.png](https://image.3001.net/images/20221125/1669368128_638089403a427cc857bd4.png!small)‘图10
附加到指定进程

  * 通过以上步骤，将IDA 服务端和.so文件关联到一起，仍需要唤醒被调试的程序，此时mumu模拟器中仍旧如图11所示

![202211251614787.png](https://image.3001.net/images/20221125/1669368129_6380894161d96571cfb29.png!small)

图11 dynamic程序界面

  * 通过jdb来唤醒被调试程序，本机调试的时候jdb使用java sdk自带的jdb，需要两步操作

    * 通过adb将进程进行转发,进程号是图n中所示的1535

    
    
    ./adb forward tcp:8700 jdwp:1535

  

  * 通过jdb唤醒操作

    
    
    jdb -connect com.sun.jdi.SocketAttach:hostname=127.0.0.1,port=8700

  * 再回到IDA中，选择F9继续运行程序，会弹出框选择本地程序与远程是否一样选项框，主要匹配的是动态库libnative-lib.so这个名字

![202211251614788.png](https://image.3001.net/images/20221125/1669368130_638089429e6c7ad22fb0d.png!small)

图12 IDA提示检测到本地.so

  * IDA中断点断在ptrace前，mumu模拟器中界面未完全同步

![202211251614789.png](https://image.3001.net/images/20221125/1669368132_638089440d65d48b9cb30.png!small)

图13 附加到调试进程后，dynamic界面

  * IDA中界面如下

![202211251614790.png](https://image.3001.net/images/20221125/1669368133_638089451e06979bae976.png!small)

图14 IDA中显示断点

##  **.so的调试**

###  **反调试绕过**

  * 该.so使用了ptrace 反调试，在ptrace处设置断点，下断点的时候有两种方案

    1. 一种是设置IDA 的调试调试，设置载入lib的时候suspend

![202211251614791.png](https://image.3001.net/images/20221125/1669368134_63808946aa0e1f872e5b5.png!small)

图15 IDA调试选项配置

  * 当看到IDA中载入libnative-lib.so时，通过快捷键Ctrl-S打开加载的段，查找libnative-lib.so所在内存1

![202211251614792.png](https://image.3001.net/images/20221125/1669368135_63808947cb79a4c51982c.png!small)

图16 查看IDA中的代码段

  * 还可以在模拟器shell中，查看具体的内存信息

![202211251614793.png](https://image.3001.net/images/20221125/1669368136_63808948d640145fcd672.png!small)

图17 adb shell中查看内存中的数据地址分布

  * 在动态调试的过程中,重置ptrace 的返回值，绕过该处反调试

![202211251614794.png](https://image.3001.net/images/20221125/1669368138_6380894a582325619ff2f.png!small)

图18 重置eax的值

可以直接右键或者在eax寄存器上使用快捷键0重置

  * 另外一种方式是直接在ptrace上下断点，在调试的时候当IDA弹窗如图17所示时，程序会直接断在ptrace断点处。如果没有弹出该弹窗，直接在IDA中分析该so时下的断点无效。

![image-20221125160753773](https://image.3001.net/images/20221125/1669368139_6380894b77464f644f2a5.png!small)

图19 重置eax的值

###  **注册native的方法**

  * 在 Native文件中代码如下

    
    
    static JNINativeMethod jniMethods[] = {  
    {"check", "(Ljava/lang/String;)Z", (void *)hello},  
    };  
    boolean xxxx( char* s) {  
    // do something  
    return JNI_TRUE;  
    }  
    #在JNI_OnLoad中调用RegisterNatives方法注册Natives方法到JVM，建立映射关系。  
    int JNI_OnLoad(JavaVM *vm, void *reserved)  
    {  
    JNIEnv *env；  
    if ((*vm)->GetEnv(vm, (void **)&env, JNI_VERSION_1_4) != JNI_OK) {  
    return JNI_ERR;  
    }  
    ​  
    jclass cls = (*env)->FindClass(env, "LHelloJNI");  
    if (cls == NULL)  
    return JNI_ERR;  
    ​  
    int len = sizeof(jniMethods) / sizeof(jnimethods[0]);  
    (*env)->RegisterNatives(env, cls, jniMethods, len);  
    ​  
    return JNI_VERSION_1_4;  
    }

###  **check 函数的定位**

  * 在apk文件中，反编译后可以看到check函数位于libnative-lib.so中，但是libnative-lib.so中并没有check函数

![202211251614795.png](https://image.3001.net/images/20221125/1669368140_6380894c9b5c431ed14b7.png!small)

图20 查找check函数

  * Java调用.so库函数可以通过静态注册和动态注册两种方式，题目通过动态注册的方式来对函数进行调用

  * 在上图中methods一列，是一个JNINativeMethod的数组，JNINativeMethod结构包含三个成员

    
    
    const char \*name: Java中声明的native方法。  
    const char \*signature：方法的签名。  
    void \*fnPtr： 函数指针

  * 在题目的methods中，check字符串，对应的函数指针为Z4xxxxP7_JNIEnvP8_jobjectP8_jstring ; xxxx(JNIEnv *,jobject *,jstring *)也就是xxxx函数。

![202211251614796.png](https://image.3001.net/images/20221125/1669368141_6380894dc15280df173fa.png!small)

图21 定位check函数

###  **MD5的简单调试**

  * MD5_init的过程如下，根据初始值可以大概判定题目通过md5算hash值

    
    
    *(_OWORD *)v63 = xmmword_B2E6FA40;  
    .rodata:B2E6FA40 xmmword_B2E6FA40 xmmword 1032547698BADCFEEFCDAB8967452301h

  * 经过fff函数转换后的md5值放入[esp+0B4]中

    
    
    .text:B2E51040 8D 84 24 B4 00 00 00    lea     eax, [esp+0B4h]  
    .text:B2E51047 89 44 24 04             mov     [esp+4], eax  
    .text:B2E5104B 8D 44 24 58             lea     eax, [esp+58h]  
    .text:B2E5104F 89 04 24                mov     [esp], eax  
    .text:B2E51052 E8 A9 E7 FF FF          call    __Z4ffffP7MD5_CTXPh ; ffff(MD5_CTX *,uchar *)

  * 读取[esp+0xB4]的值

    
    
    Python>esp=get_reg_value('esp')  
    Python>data=get_bytes(esp+0xb4,16)  
    Python>data.hex()  
    'a82e0cb168bfe134f22dbde167cf046c'

  * 通过python计算wojiushidaan0!!!的md5值为

    
    
    >>> import hashlib  
    >>> result=hashlib.md5("wojiushidaan0!!!".encode())  
    >>> result  
    <md5 _hashlib.HASH object @ 0x00000167FF8BDEF0>  
    >>> result.hexdigest()  
    'a82e0cb168bfe134f22dbde167cf046c'

  * 两者可以对应起来，题目计算了wojiushidaan0!!!的md5值

  * 程序最终经过memcmp比较的时候的值为

    
    
    .text:B2F11398 89 54 24 08             mov     [esp+8], edx  
    .text:B2F1139C 8B 44 24 14             mov     eax, [esp+14h]  
    .text:B2F113A0 89 44 24 04             mov     [esp+4], eax    ; s2  
    .text:B2F113A4 89 0C 24                mov     [esp], ecx      ; s1  
    .text:B2F113A7 E8 84 E4 FF FF          call    _memcmp

  * 提取eax的值为

    
    
    b'c640fc761edbd22f431efb861bc0e28a'

  * 提取ecx的值为

    
    
    b'12345678123456781234567812345678'

  * 程序的输入为

![202211251614797.png](https://image.3001.net/images/20221125/1669368142_6380894eedbc7c815a3e9.png!small)

图22 调试flag结果

  * 推导可知题目的正确输入为

flag{c640fc761edbd22f431efb861bc0e28a}

![202211251614798.png](https://image.3001.net/images/20221125/1669368143_6380894ff29232e109d0c.png!small)

图23 验证flag结果

  * 在调试md5的时候，使用了IDA的上色功能，通过单步步过调试，给执行过的代码染色

  * IDAPro 单步步过上色调试脚本

    
    
    def get_new_color(current_color):  
    colors = [0xffe699, 0xffcc33, 0xe6ac00, 0xb38600]  
    if current_color == 0xFFFFFF:  
    return colors[0]  
    if current_color in colors:  
    pos = colors.index(current_color)  
    if pos == len(colors)-1:  
    return colors[pos]  
    else:  
    return colors[pos+1]  
    return 0xFFFFFF  
    ​  
    addr = ida_dbg.get_ip_val()  
    while addr < 0xB2ED241F:  
    event = wait_for_next_event(WFNE_ANY, -1)  
    t = step_over()  
    addr = ida_dbg.get_ip_val()  
    current_color = get_color(addr, CIC_ITEM)  
    new_color = get_new_color(current_color)  
    set_color(addr, CIC_ITEM, new_color)

#<https://www.cnblogs.com/blacksunny/p/7300271.html>参考trace 修改的step over

###  **有待改进的地方**

  * 绕过反调试依赖于动态调试时的修改寄存器实现

##  **本文涉及的命令**

    
    
    adb connect 127.0.0.1:7555  
    adb install test.apk  
    ./adb shell am start -D -n com.example.dynamic/.MainActivity  
    ./adb push android_x86_server /data/local/tmp  
    ./adb.exe forward tcp:23946 tcp:23946  
    ./adb forward tcp:8700 jdwp:1535  
    jdb -connect com.sun.jdi.SocketAttach:hostname=127.0.0.1,port=8700

