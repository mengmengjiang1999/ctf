本文来自i春秋作者:
[penguin_wwy](http://bbs.ichunqiu.com/thread-12734-1-1.html?from=paper)

### 零、问题出现

对dex文件进行加密，解密后动态加载是一种常用的加壳方式（一代壳以这种方式为主）。但这种在解密之后往往会产生一个解密后的完整dex。过程一般是这样的
打开文件

`File file = new File("classes.dex");`

读取字节码

`byte[] buffer = new FileInputStream(file).read();`

解密字节码

`decrypt(buffer)`

重写到文件

`File newFile = new File("classes_decrypt.dex"); new
FileOutputStream(newFile).write(buffer);`

加载dex

`DexClassLoader dexClassLoader = new
DexClassLoader("classes_decrypt.dex"...);`

可见在重写到文件这一步，就有可能被截获到解密后的dex，那加密dex的意义就完全不存在了。
当然也有过许多办法，比如加载完后删除文件、或者隐藏文件等等，但都没法从根本上解决问题。而最有实际意义的方法就是今天要说的，不落地加载dex。

### 一、理论基础

不落地的含义就是说在解密后直接由字节码进行加载，不需要变成dex文件。Dalvik中的两种类加载器DexClassLoader和PathClassLoader显然都不具备这个能力。我们需要自己定义一个类加载器。
那如何自己定义呢？我们先分析一下DexClassLoader加载的过程（详细分析请看我的博客）。这里简单说明一下，首先是DexClassLoader的构造函数
源码位置 libcore\dalvik\src\main\java\dalvik\system\DexClassLoader.java

    
    
    public class DexClassLoader extends BaseDexClassLoader {
    /**
    * Creates a {[url=home.php?mod=space&uid=74926]@Code[/url] DexClassLoader} that finds interpreted and native
    * code. Interpreted classes are found in a set of DEX files contained
    * in Jar or APK files.
    *
    * <p>The path lists are separated using the character specified by the
    * {@code path.separator} system property, which defaults to {@code :}.
    *
    * @param dexPath the list of jar/apk files containing classes and
    * resources, delimited by {@code File.pathSeparator}, which
    * defaults to {@code ":"} on Android
    * @param optimizedDirectory directory where optimized dex files
    * should be written; must not be {@code null}
    * @param libraryPath the list of directories containing native
    * libraries, delimited by {@code File.pathSeparator}; may be
    * {@code null}
    * @param parent the parent class loader
    */
    public DexClassLoader(String dexPath, String optimizedDirectory,
    String libraryPath, ClassLoader parent) {
    super(dexPath, new File(optimizedDirectory), libraryPath, parent);
    }
    }

实质上是对它的父类，BaseDexClassLoader的构造 源码位置
libcore\dalvik\src\main\java\dalvik\system\BaseDexClassLoader.java

    
    
    public BaseDexClassLoader(String dexPath, File optimizedDirectory,
    String libraryPath, ClassLoader parent) {
    super(parent);
    this.pathList = new DexPathList(this, dexPath, libraryPath, optimizedDirectory);
    }

libcore\dalvik\src\main\java\dalvik\system\DexPathList.java

    
    
    public DexPathList(ClassLoader definingContext, String dexPath,
    String libraryPath, File optimizedDirectory) {
    if (definingContext == null) {
    throw new NullPointerException("definingContext == null");
    }
     
    if (dexPath == null) {
    throw new NullPointerException("dexPath == null");
    }
     
    if (optimizedDirectory != null) {
    if (!optimizedDirectory.exists()) {
    throw new IllegalArgumentException(
    "optimizedDirectory doesn't exist: "
    + optimizedDirectory);
    }
     
    if (!(optimizedDirectory.canRead()
    && optimizedDirectory.canWrite())) {
    throw new IllegalArgumentException(
    "optimizedDirectory not readable/writable: "
    + optimizedDirectory);
    }
    }
     
    this.definingContext = definingContext;
    this.dexElements = makeDexElements(splitDexPath(dexPath), optimizedDirectory);
    this.nativeLibraryDirectories = splitLibraryPath(libraryPath);
    }

重点在函数makeDexElements

    
    
    private static Element[] makeDexElements(ArrayList<File> files,
    File optimizedDirectory) {
    ArrayList<Element> elements = new ArrayList<Element>();
     
    /*
    * Open all files and load the (direct or contained) dex files
    * up front.
    */
    for (File file : files) {
    File zip = null;
    DexFile dex = null;
    String name = file.getName();
     
    if (name.endsWith(DEX_SUFFIX)) {
    // Raw dex file (not inside a zip/jar).
    try {
    dex = loadDexFile(file, optimizedDirectory);
    } catch (IOException ex) {
    System.logE("Unable to load dex file: " + file, ex);
    }
    } else if (name.endsWith(APK_SUFFIX) || name.endsWith(JAR_SUFFIX)
    || name.endsWith(ZIP_SUFFIX)) {
    zip = file;
     
    try {
    dex = loadDexFile(file, optimizedDirectory);
    } catch (IOException ignored) {
    /*
    * IOException might get thrown "legitimately" by
    * the DexFile constructor if the zip file turns
    * out to be resource-only (that is, no
    * classes.dex file in it). Safe to just ignore
    * the exception here, and let dex == null.
    */
    }
    } else if (file.isDirectory()) {
    // We support directories for looking up resources.
    // This is only useful for running libcore tests.
    elements.add(new Element(file, true, null, null));
    } else {
    System.logW("Unknown file type for: " + file);
    }
     
    if ((zip != null) || (dex != null)) {
    elements.add(new Element(file, false, zip, dex));
    }
    }
     
    return elements.toArray(new Element[elements.size()]);
    }

根据文件后缀名的判断选择分支，然后调用loadDex函数

    
    
    private static DexFile loadDexFile(File file, File optimizedDirectory)
    throws IOException {
    if (optimizedDirectory == null) {
    return new DexFile(file);
    } else {
    String optimizedPath = optimizedPathFor(file, optimizedDirectory);
    return DexFile.loadDex(file.getPath(), optimizedPath, 0);
    }
    }

DexFile.loadDex这个函数的内部也只是构造一个DexFile对象，所以直接看DexFile的构造函数就好

    
    
    private DexFile(String sourceName, String outputName, int flags) throws IOException {
    if (outputName != null) {
    try {
    String parent = new File(outputName).getParent();
    if (Libcore.os.getuid() != Libcore.os.stat(parent).st_uid) {
    throw new IllegalArgumentException("Optimized data directory " + parent
    + " is not owned by the current user. Shared storage cannot protect"
    + " your application from code injection attacks.");
    }
    } catch (ErrnoException ignored) {
    // assume we'll fail with a more contextual error later
    }
    }
     
    mCookie = openDexFile(sourceName, outputName, flags);
    mFileName = sourceName;
    guard.open("close");
    //System.out.println("DEX FILE cookie is " + mCookie);
    }

重点的重点在openDexFile，这个函数负责最终的dex文件加载

运行流程

DexClassLoader ——> BaseDexClassLoader ——> DexPathList ——> makeDexElements ——>
loadDex ——> DexFile

这个openDexFile函数是一个native函数，在libdvm.so中，看对应的函数表

    
    
    const DalvikNativeMethod dvm_dalvik_system_DexFile[] = { 
    { "openDexFile", "(Ljava/lang/String;Ljava/lang/String;I)I", 
    Dalvik_dalvik_system_DexFile_openDexFile }, 
    { "openDexFile", "([B)I", 
    Dalvik_dalvik_system_DexFile_openDexFile_bytearray }, 
    { "closeDexFile", "(I)V", 
    Dalvik_dalvik_system_DexFile_closeDexFile }, 
    { "defineClass", "(Ljava/lang/String;Ljava/lang/ClassLoader;I)Ljava/lang/Class;", 
    Dalvik_dalvik_system_DexFile_defineClass }, 
    { "getClassNameList", "(I)[Ljava/lang/String;", 
    Dalvik_dalvik_system_DexFile_getClassNameList }, 
    { "isDexOptNeeded", "(Ljava/lang/String;)Z", 
    Dalvik_dalvik_system_DexFile_isDexOptNeeded }, 
    { NULL, NULL, NULL }, 
    };

调用表中第一个openDexFile所对应的`Dalvik_dalvik_system_DexFile_openDexFile`
，这个就是实际执行的函数，函数参数 `"(Ljava/lang/String;Ljava/lang/String;I)I"` 两个字符串一个整型。
而意外的发现在它的下一个位置`Dalvik_dalvik_system_DexFile_openDexFile_bytearray`，它的参数
`([B)I`
一个byte数组和一个整型，也就是说如果我们直接调用这个函数的话，就可以将字节码以一个byte数组的形式传入。了解到这里，我们的目标就清晰了。

（1）构造一个我们自己的类加载器

（2）通过`Dalvik_dalvik_system_DexFile_openDexFile_bytearray`，来加载dex文件的字节码

### 二、开工实践

下面我们就来尝试实现一下，首先我们需要一个正常的Apk，越简单越好，最好不需要太多资源文件，加载了dex能直接运行，毕竟只是实验一下。上一篇当中的TestApk就很合适。解压出它的classes.dex，放到手机/data/local/tmp文件夹下

然后新建一个Apk，就叫DexFile, 准备一个java类，负责native函数

    
    
    public class JNITool {
    static {
    System.loadLibrary("JNITool");
    }
     
    public static native int loadDex(byte[] dex,long dexlen);
    }

这个loadDex就负责通过我们前面所述的函数加载dex。在JNITool.so，我们要加载libdvm.so并且找到`Dalvik_dalvik_system_DexFile_openDexFile_bytearray`函数
所以需要定义JNI_OnLoad函数

    
    
    JNIEXPORT jint JNI_OnLoad(JavaVM* vm, void* reserved) {
     
    void *ldvm = (void*) dlopen("libdvm.so", RTLD_LAZY);
    dvm_dalvik_system_DexFile = (JNINativeMethod*) dlsym(ldvm, "dvm_dalvik_system_DexFile");
     
    //openDexFile
    if(0 == lookup(dvm_dalvik_system_DexFile, "openDexFile", "([B)I",&openDexFile)) {
    openDexFile = NULL;
    LOGI("openDexFile method does not found ");
    }else{
    LOGI("openDexFile method found ! HAVE_BIG_ENDIAN");
    }
     
    LOGI("ENDIANNESS is %c" ,ENDIANNESS );
    void *venv;
    LOGI("dufresne----->JNI_OnLoad!");
    if ((*vm)->GetEnv(vm, (void**) &venv, JNI_VERSION_1_4) != JNI_OK) {
    LOGI("dufresne--->ERROR: GetEnv failed");
    return -1;
    }
    return JNI_VERSION_1_4;
    }

dlopen函数链接libdvm.so，dlsym找到并返回dvm_dalvik_system_DexFile。dvm_dalvik_system_DexFile就是我们之前看到的函数表

    
    
    const DalvikNativeMethod dvm_dalvik_system_DexFile[] = { 
    { "openDexFile", "(Ljava/lang/String;Ljava/lang/String;I)I", 
    Dalvik_dalvik_system_DexFile_openDexFile }, 
    { "openDexFile", "([B)I", 
    Dalvik_dalvik_system_DexFile_openDexFile_bytearray }, 
    { "closeDexFile", "(I)V", 
    Dalvik_dalvik_system_DexFile_closeDexFile }, 
    { "defineClass", "(Ljava/lang/String;Ljava/lang/ClassLoader;I)Ljava/lang/Class;", 
    Dalvik_dalvik_system_DexFile_defineClass }, 
    { "getClassNameList", "(I)[Ljava/lang/String;", 
    Dalvik_dalvik_system_DexFile_getClassNameList }, 
    { "isDexOptNeeded", "(Ljava/lang/String;)Z", 
    Dalvik_dalvik_system_DexFile_isDexOptNeeded }, 
    { NULL, NULL, NULL }, 
    };

lookup从函数表中寻找我们要的`Dalvik_dalvik_system_DexFile_openDexFile_bytearray`

    
    
    int lookup(JNINativeMethod *table, const char *name, const char *sig,
    void (**fnPtrout)(u4 const *, union JValue *)) {
    int i = 0;
    while (table.name != NULL)
    {
    LOGI("lookup %d %s" ,i,table.name);
    if ((strcmp(name, table.name) == 0)
    && (strcmp(sig, table.signature) == 0))
    {
    *fnPtrout = table.fnPtr;
    return 1;
    }
    i++;
    }
    return 0;
    }

找到之后就用全局的函数指针

    
    
    void (*openDexFile)(const u4* args, union JValue* pResult);

来保存这个函数

    
    
    JNIEXPORT jint JNICALL Java_cn_wjdiankong_dexfiledynamicload_NativeTool_loadDex(JNIEnv* env, jclass jv, jbyteArray dexArray, jlong dexLen)
    {
    // header+dex content
    u1 * olddata = (u1*)(*env)-> GetByteArrayElements(env,dexArray,NULL);
    char* arr;
    arr = (char*)malloc(16 + dexLen);
    ArrayObject *ao=(ArrayObject*)arr;
    ao->length = dexLen;
    memcpy(arr+16,olddata,dexLen);
    u4 args[] = { (u4) ao };
    union JValue pResult;
    jint result;
    if(openDexFile != NULL) {
    openDexFile(args,&pResult);
    }else{
    result = -1;
    }
     
    result = (jint) pResult.l;
    LOGI("Java_cn_wjdiankong_dexfiledynamicload_NativeTool_loadDex %d" , result);
    return result;
    }

loadDex函数最终会通过这个函数指针来调用`dvm_dalvik_system_DexFile`，最终加载dex

那么回到Java层，我们需要定义一个自己的类加载器

    
    
    public class DynamicDexClassLoder extends DexClassLoader {
     
    private static final String TAG = "dexlog";
    private int cookie;
    private Context mContext;

构造函数

    
    
    public DynamicDexClassLoder(Context context, byte[] dexBytes,
    String libraryPath, ClassLoader parent, String oriPath,
    String fakePath) {
    super(oriPath, fakePath, libraryPath, parent);
    setContext(context);
     
    int cookie = JNITool.loadDex(dexBytes, dexBytes.length);
     
    setCookie(cookie);
     
    }

cookie这个变量代表了加载完成后的dex的句柄 然后实现findClass函数

    
    
    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
    Log.d(TAG, "findClass-" + name);
    Class<?> cls = null;
    String as[] = getClassNameList(cookie);
    Class obj_class = Class.forName(DexFile.class.getName());
    Method method = obj_class.getDeclaredMethod("defineClassNative",
    new Class[]{String.class, ClassLoader.class, int.class});
    method.setAccessible(true);
    for (int z = 0; z < as.length; z++) {
    Log.i(TAG, "classname:"+as[z]);
    if (as[z].equals(name)) {
    cls = (Class) method.invoke(null, 
    new Object[]{as[z].replace('.', '/'), mContext.getClassLoader(), cookie});
    } else {
    //加载其他类
    method.invoke(null, 
    new Object[]{as[z].replace('.', '/'), mContext.getClassLoader(), cookie});
    }
    }
     
    if (null == cls) {
    cls = super.findClass(name);
    }
     
    return cls;
    }

然后在MainActivity中我们就可以通过以下代码，启动TestApk的MainActivity

    
    
    DynamicDexClassLoder dLoader = new DynamicDexClassLoder(
    getApplicationContext(),
    dexContent,
    null,
    clzLoader,
    getPackageResourcePath(),getDir(".dex", MODE_PRIVATE).getAbsolutePath()
    );
    Class clazz = dLoader.findClass("com.example.testapk.MainActivity");
    Intent intent = new Intent(this, clazz);
    startActivity(intent);

### 三、小结

以上的代码在Android5.0以下的Android系统上可以正确执行（少数真机可能会出问题），我测试的时候在原生的Android4.4上成功。至于Android5.0？不好意思，从Android5.0开始，谷歌已经放弃了Dalvik虚拟机，转而支持ART，没有了libdvm，所以。。。。之后我会考虑研究一下怎么在ART虚拟机中实现。

这种不落地的加载方式是现在加壳方式的一部分。现在的加壳方法往往是多种方法捏合在一起的（还有那种丧心病狂的VMP），大家可以试试将上篇的方法和这篇结合起来，对一个加密的dex，解密后不落地加载，之后再修复dex中的错误指令。之后我也会介绍越来越多的加壳、抗反编译方法，都可以尝试结合在一起。

原文地址：http://bbs.ichunqiu.com/thread-12734-1-1.html?from=paper

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/59/>

