本文章原作者 非虫，文章来源网站[Mottoin](http://www.mottoin.com/89035.html)

#### 目录

**简述（脱壳前学习的知识、壳的历史、脱壳方法）**

  * 第一代壳
  * 第二代壳
  * 第三代壳
  * 第N代壳

**简述**

  * Apk文件结构
  * Dex文件结构
  * 壳史
  * 壳的识别

== Apk文件结构 ==

![](https://images.seebug.org/content/images/2017/02/1-15.png-w331s) ==
Dex文件结构 ==

![](http://img.mottoin.com/wp-content/uploads/2016/09/2-13.png)

### 壳史

**第一代壳 Dex加密**

  1. Dex字符串加密
  2. 资源加密
  3. 对抗反编译
  4. 反调试
  5. 自定义DexClassLoader

**第二代壳 Dex抽取与So加固**

  1. 对抗第一代壳常见的脱壳法
  2. Dex Method代码抽取到外部（通常企业版）
  3. Dex动态加载
  4. So加

**第三代壳 Dex动态解密与So混淆**

  1. Dex Method代码动态解密**
  2. So代码膨胀混淆
  3. 对抗之前出现的所有脱壳法

**第四代壳 arm vmp（未来）**

  1. vmp

### 壳的识别

1.用加固厂商特征：

  * 娜迦： libchaosvmp.so , libddog.solibfdog.so
  * 爱加密：libexec.so, libexecmain.so
  * 梆梆： libsecexe.so, libsecmain.so , libDexHelper.so
  * 360：libprotectClass.so, libjiagu.so
  * 通付盾：libegis.so
  * 网秦：libnqshield.so *百度：libbaiduprotect.so

2.基于特征的识别代码

![](https://images.seebug.org/content/images/2017/02/3-11.png-w331s)

#### 第一代壳

  1. 内存Dump法
  2. 文件监视法
  3. Hook法
  4. 定制系统
  5. 动态调试法

**内存Dump法**

  * 内存中寻找dex.035或者dex.036
  * /proc/xxx/maps中查找后，手动Dump

![](https://images.seebug.org/content/images/2017/02/4-10.png-w331s)

  * android-unpacker https://github.com/strazzere/android-unpacker

![](http://img.mottoin.com/wp-content/uploads/2016/09/5-11.png)

  * drizzleDumper https://github.com/DrizzleRisk/drizzleDumper
  * 升级版的android-unpacker，read和lseek64代替pread，匹配dex代替匹配odex

![](https://images.seebug.org/content/images/2017/02/6-10.png-w331s)

![](http://img.mottoin.com/wp-content/uploads/2016/09/7-9.png)

**文件监视法**

  * Dex优化生成odex
  * inotifywait-for-Android https://github.com/mkttanabe/inotifywait-for-Android
  * 监视文件变化

![](http://img.mottoin.com/wp-content/uploads/2016/09/8-9.png)

  * notifywait-for-Android https://github.com/mkttanabe/inotifywait-for-Android
  * 监视DexOpt输出

![](http://img.mottoin.com/wp-content/uploads/2016/09/9-9.png)

![](http://img.mottoin.com/wp-content/uploads/2016/09/10-9.png)

Hook法

  * Hook dvmDexFileOpenPartial
  * http://androidxref.com/4.4_r1/xref/dalvik/vm/DvmDex.cpp

![](http://img.mottoin.com/wp-content/uploads/2016/09/11-9.png)

![](http://img.mottoin.com/wp-content/uploads/2016/09/12-6.png)

**定制系统**

  * 修改安卓源码并刷机

![](http://img.mottoin.com/wp-content/uploads/2016/09/13-5.png)

  * DumpApk https://github.com/CvvT/DumpApk
  * 只针对部分壳

![](https://images.seebug.org/content/images/2017/02/14-5.png-w331s)

**动态调试法**

  * IDA Pro

![](https://images.seebug.org/content/images/2017/02/15-5.png-w331s)
![](https://images.seebug.org/content/images/2017/02/16-5.png-w331s)

![](https://images.seebug.org/content/images/2017/02/17-5.png-w331s)

  * gdb gcore法

    
    
    .gdbserver :1234 –attach pid 
    .gdb 
    (gdb) target remote :1234 
    (gdb) gcore

coredump文件中搜索“dex.035”

![](https://images.seebug.org/content/images/2017/02/18-3.png-w331s)

#### 第二代壳

  1. 内存重组法
  2. Hook法
  3. 动态调试
  4. 定制系统
  5. 静态脱壳机

**内存重组法**

**Dex篇**

ZjDroid http://bbs.pediy.com/showthread.php?t=190494

对付一切内存中完整的dex，包括壳与动态加载的jar

![](https://images.seebug.org/content/images/2017/02/19-3.png-w331s)

![](https://images.seebug.org/content/images/2017/02/20-2.png-w331s)

**so篇**

elfrebuild

![](http://img.mottoin.com/wp-content/uploads/2016/09/21-2.png)

![](https://images.seebug.org/content/images/2017/02/22-3.png-w331s)

构造soinfo，然后对其进行重建

![](http://img.mottoin.com/wp-content/uploads/2016/09/23-2.png)

![](http://img.mottoin.com/wp-content/uploads/2016/09/24-2.png)

**Hook法**

针对无代码抽取且Hook dvmDexFileOpenPartial失败

Hook dexFileParse

http://androidxref.com/4.4_r1/xref/dalvik/vm/DvmDex.cpp

![](https://images.seebug.org/content/images/2017/02/25.png-w331s)

https://github.com/WooyunDota/DumpDex

![](https://images.seebug.org/content/images/2017/02/26-1.png-w331s)

针对无代码抽取且Hook dexFileParse失败

Hook memcmp

http://androidxref.com/4.4_r1/xref/dalvik/vm/DvmDex.cpp

![](http://img.mottoin.com/wp-content/uploads/2016/09/27.png)

![](http://img.mottoin.com/wp-content/uploads/2016/09/28.png)

**定制系统**

修改安卓源码并刷机－针对无抽取代码

https://github.com/bunnyblue/DexExtractor

![](http://img.mottoin.com/wp-content/uploads/2016/09/29.png)

Hook dexfileParse

![](http://img.mottoin.com/wp-content/uploads/2016/09/30.png)

![](https://images.seebug.org/content/images/2017/02/31.png-w331s)

DexHunter-最强大的二代壳脱壳工具

https://github.com/zyq8709/DexHunter

DexHunter的工作流程：

![](http://img.mottoin.com/wp-content/uploads/2016/09/32.png)

DexHunter的工作原理：

![](https://images.seebug.org/content/images/2017/02/32.png-w331s)

绕过三进程反调试

http://bbs.pediy.com/showthread.php?p=1439627

![](http://img.mottoin.com/wp-content/uploads/2016/09/34.png)

![](https://images.seebug.org/content/images/2017/02/35.png-w331s)

修改系统源码后：

![](https://images.seebug.org/content/images/2017/02/36.png-w331s)

http://www.cnblogs.com/lvcha/p/3903669.html

![](http://img.mottoin.com/wp-content/uploads/2016/09/37.png)

    
    
    ls /proc/345/task

![](http://img.mottoin.com/wp-content/uploads/2016/09/38.png)

    
    
    ./gdbserver :1234 --attach346 
    ... 
    (gdb) gcore

gcore防Dump解决方案：

http://bbs.pediy.com/showthread.php?t=198995

断点mmap调试，针对Hook dexFileParse无效

原理： dexopt优化时， dvmContinueOptimization()->mmap()

![](https://images.seebug.org/content/images/2017/02/39.png-w331s)

**静态脱壳机**

分析壳so逻辑并还原加密算法

http://www.cnblogs.com/2014asm/p/4924342.html

![](http://img.mottoin.com/wp-content/uploads/2016/09/40.png)

自定义linker脱so壳

https://github.com/devilogic/udog

    
    
    main() -> dump_file()

![](https://images.seebug.org/content/images/2017/02/41.png-w331s)

#### 第三代壳

  1. dex2oat法
  2. 定制系统

**dex2oat法**

ART模式下，dex2oat生成oat时，内存中的DEX是完整的

http://bbs.pediy.com/showthread.php?t=210532

![](http://img.mottoin.com/wp-content/uploads/2016/09/43.png)

**定制系统**

Hook Dalvik_dalvik_system_DexFile_defineClassNative

枚举所有DexClassDef，对所有的class，调用dvmDefineClass进行强制加载

![](https://images.seebug.org/content/images/2017/02/44-1.png-w331s)

#### 第N代壳

  1. so + vmp
  2. 动态调试 ＋ 人肉还原

来源链接：http://www.mottoin.com/89035.html

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/44/>

