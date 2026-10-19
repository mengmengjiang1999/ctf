> ### 本文作者：[HAI_](https://bbs.ichunqiu.com/space-uid-249512.html)  
>

# 0x00 前言

  
![图片.png](https://image.3001.net/images/20180308/15204873513026.png!small)  

来看看我们今天的主题。

让你自由自在脱壳的热身运动。

现在很多第厂家都是使用第三方的加固方式来进行加固的。或者使用自己的加固方式进行加固。

那么我们必不可少的就是脱壳这个过程。

想要脱壳？看大佬步骤？

还是要知其然也要知其所以然才能进步。

## 内容

### 1.一个好用的工具简单教程(Insight)

#### 你可以学到什么？

一个超级厉害的分析辅助软件。

### 2.Android 优化过程分析

#### 你可以学到什么？

1.深度了解Android 优化过程  
2.近距离观察Android 源码  
2.可以见到大佬脱壳下段的函数

### 3.Android DEX文件解析分析

#### 你可以学到什么？

1.其他可以下段的函数  
2.dex文件解析的过程  
3.脱壳下断的小知识

### 4\. Android DEX类加载过程分析

#### 你可以学到什么？

1.类加载的完整过程  
2.脱壳加固类的选择

# 0x01 一个好用的工具简单教程（Insight）

这个软件对于分析c/c++还有java源码具有很强的辅助功能，之后要进行使用，所以进行简单的介绍。

工具在附件中找。单独上传下载就可以了。

[SI3US-205035-36448](https://bbs.ichunqiu.com/thread-35286-1-1.html?from=beef)

这里提供一个注册码。

安装，next，next就可以了。

![图片.png](https://image.3001.net/images/20180308/15204873616811.png!small)  

## 新建一个工程

选择new project。  

![图片.png](https://image.3001.net/images/20180308/15204871674005.png!small)

单机OK  
![图片.png](https://image.3001.net/images/20180308/15204873851642.png!small)  

选择第一个

  
![图片.png](https://image.3001.net/images/20180308/15204874079654.png!small)  

选择 Add Tree，意思就是说全部加在。  
![图片.png](https://image.3001.net/images/20180308/15204874147666.png!small)  

加载完成

![图片.png](https://image.3001.net/images/20180308/15204874267044.png!small)  

之后我们会用到这个软件进行分析。

## Android 优化过程分析

我想啰嗦一下，这个时候就知道英语的重要性了，当然我的英语也不好，但是我会查字典呀。

  
![图片.png](https://image.3001.net/images/20180308/15204874397014.png!small)  

### 1.extractAndProcessZip

我们先不说这个内容的事情，先来看看这个函数的名称。extract：提取，and 和，Process 过程
Zip，压缩文件格式，我们都知道apk其实就是一个zip压缩包。  
那么这个函数的意思就是提取 zip的过程。

然后我们来一步一步的分析。

  
![图片.png](https://image.3001.net/images/20180308/15204874468876.png!small)  

这里是extractAndProcessZip的中间变量定义。不是我们研究的重点。

  
![图片.png](https://image.3001.net/images/20180308/15204874535206.png!small)  

    
    
    DexClassVerifyMode verifyMode = VERIFY_MODE_ALL;

这一句定义的是 verifyMode，就是验证模块，这里初始化的数据是VERIFY_MODE_ALL，也就是全部都进行验证。

 **思考**

 **如果我们对这里进行更改是不是就可以跳过这个验证。**

我们来看看其他的值。

  
![图片.png](https://image.3001.net/images/20180308/15204874592627.png!small)  

如果有想法可以自己定义这个值。

    
    
    DexOptimizerMode dexOptMode = OPTIMIZE_MODE_VERIFIED;

  
![图片.png](https://image.3001.net/images/20180308/15204874675951.png!small)  

我们来接着往下看。  
![图片.png](https://image.3001.net/images/20180308/15204875046617.png!small)  

这里有一个函数，dexOptCreateEmptyHeader，看英文，创建一个dex优化的空的头部。

  
![图片.png](https://image.3001.net/images/20180308/15204875229508.png!small)  

dexOffset，record the file position so we can get back here
later，其实就是读取dex文件的起始位置。

接着来看下一个函数。  
![图片.png](https://image.3001.net/images/20180308/15204875472100.png!small)

Open the zip archive, find the DEX entry.  
很明显，这个部分在做的事情就是，从apk中找到dex文件。

接着进行分析。

  

  
![图片.png](https://image.3001.net/images/20180308/1520487555783.png!small)  

提取dex的一些偏移的函数。

![图片.png](https://image.3001.net/images/20180308/15204875885354.png!small)  

Extract the DEX data into the cache file at the current
offset.对dex文件的一些偏移进行记录。

以上就是处理部分。

接下来要说的是dex odex化的过程。

  
![图片.png](https://image.3001.net/images/20180308/15204875988562.png!small)  

这里就是优化验证的地方。

通过这里就可以修改优化的过程，甚至可以去除优化验证。

 **思考**  
 **这里的数据是哪里来的，在什么地方进行对比。·**  
 **这些数据都是在build.prop中进行对比的。**

## 2.继续进行优化

  
  

我们来跟进dvmContinueOptimization这个函数。

 **PS：**  
 **马上就要接触到一个非常重要的和脱壳非常相关的地方了**

打开dvmContinueOptimization函数

![图片.png](https://image.3001.net/images/20180308/15204876175165.png!small)  

首先是一个判断。

  
![图片.png](https://image.3001.net/images/20180308/15204876252096.png!small)  

然后就是对dex文件的一个写入。

接着往下看（重点要到了）

  
![图片.png](https://image.3001.net/images/20180308/15204876325823.png!small)  

[dvmDexFileOpenPartial，](https://bbs.ichunqiu.com/thread-35286-1-1.html?from=beef)如果之前看过别人脱壳的教程，肯定知道这里是经常使用的下端点的时候，以前只知道要下，现在知道，这个函数是存在于源码之中的。

我们来查看下dvmDexFileOpenPartial这个函数的调用

![图片.png](https://image.3001.net/images/20180308/15204876423644.png!small)  

这里调用了两次，还有一次是自己的定义。

先来看一下dvmDexFileOpenPartial的原型

int dvmDexFileOpenPartial(const void* addr, int len, DvmDex** ppDvmDex)  
参数1：加载的DEX文件在内存中的基址.(也就是DEX.035)  
参数2：加载的DEX文件的文件长度，  
参数3：出参, DEX 文件转成DvmDex结构，里面包含Dex文件的类，字段，方法，字符串信息。Dalivk操作Dex文件的对象这是结构结构体

  
![图片.png](https://image.3001.net/images/20180308/15204876508363.png!small)  

最后在这里写入头部的信息。

  
![图片.png](https://image.3001.net/images/20180308/15204876593720.png!small)  

# 0x03 Android DEX文件解析分析

dvmRawDexFileOpen() 这个函数是我们要关键要了解的函数，它在RawDexFile.cpp函数中。

  
![图片.png](https://image.3001.net/images/20180308/15204876677016.png!small)  

先对基本变量进行定义。

  
![图片.png](https://image.3001.net/images/20180308/15204876732693.png!small)

都知道文件格式一个很重要的东西就是魔数，那么这里就是首先判断魔数，verifyMagicAndGetAdler32。这里的magic就是魔数。  

  
![图片.png](https://image.3001.net/images/20180308/15204876818393.png!small)  

这里是对时间，以及文件大小的验证。

  
![图片.png](https://image.3001.net/images/20180308/1520487702101.png!small)  

这个函数是一个重点函数，也是我们要着重分析的一个函数，它的主要功能就是生成dex对应的odex文件，也就是所谓的odex化。我们跟进函数进行查看。  

![图片.png](https://image.3001.net/images/20180308/15204877145814.png!small)

这个就是dexOptGenerateCacheFileName()函数部分。我们主要的是看它输出的位置是什么地方。

![图片.png](https://image.3001.net/images/20180308/15204877374962.png!small)  

在这里可以看到是在data目录下生成， ALOGV("Cache file for '%s' '%s' is '%s'", fileName,
subFileName, nameBuf);  
这个样子的格式。

也就是说这里已经生成我们的odex文件了。

然后要做的事情就是这个函数了dvmDexFileOpenFromFd（），进一步进行优化，完成映射，设为可读文件。打开这个函数。位置是在DvmDex.cpp里。

![图片.png](https://image.3001.net/images/20180308/15204877499616.png!small)  

我们先来看一下调用这个函数的地方。

![图片.png](https://image.3001.net/images/20180308/15204877622808.png!small)  

调用这个函数的地方，就是我们的重点函数dvmRawDexFileOpen，这个函数先调用dexOptGenerateCacheFileName生成odex，然后再调用dvmDexFileOpenFromFd进行再一次优化。

优化中的最后一步就是dexFileParse()，也就是解析DEX。这个位置在DexFile

![图片.png](https://image.3001.net/images/20180308/15204877691080.png!small)  

## 做一个简单的总结。

dvmRawDexFileOpen()主控函数——dexOptGenerateCacheFileName()生成对应的odex——dvmDexFileOpenFromFd（）进一步优化——dexFileParse()解析dex。

## PS：小技巧

dexfileopenpartial在下段的时候，可能会发现没有办法断下来，那么我们就可以选择[dexOptGenerateCacheFileNamePKcS0](https://bbs.ichunqiu.com/thread-35286-1-1.html?from=beef)，dvmdexfileopenfromfd
等函数来进行下段。

一般来说dexfileopenpartial处理有壳的东西会比较好一点。

# 0x04 Android Dex类加载过程

其他源码都是由一个主控函数来进行指引，引导其他关键函数进行运作，dex类加载过程也是这个样子的。

它的主控函数就是[Dalvik_dalvik_system_DexFile_defineClassNative（）](https://bbs.ichunqiu.com/thread-35286-1-1.html?from=beef)

  
![图片.png](https://image.3001.net/images/20180308/15204877931596.png!small)  

还有一个需要注意的函数Dalvik_dalvik_system_DexFile_openDexFileNative

这里需要注意的是有两个可以dump的地方。

  
![图片.png](https://image.3001.net/images/20180308/15204878006773.png!small)  

还是接着来看我们的主控函数。

在主控函数里有这样一个调用。  
![图片.png](https://image.3001.net/images/20180308/15204878083597.png!small)  

这个调用是验证cookie，但是这个cookie很有可能是解密后的dex的cookie，所以也可以在这里把这个cookie dump下来。

接着往下看。

  
![图片.png](https://image.3001.net/images/20180308/15204878279738.png!small)  

dvmDefineClass这个函数，这个函数就是确认类加载的一个函数。

  

![图片.png](https://image.3001.net/images/20180308/1520487835318.png!small)

函数自己进行了一个判断，但是return返回的东西确是一个大头。我们跟进这个函数进行查看。  

  

![图片.png](https://image.3001.net/images/20180308/15204879729036.png!small)  

![图片.png](https://image.3001.net/images/20180308/15204879613555.png!small)  

这里最重要的就是clazz，这个就是动态加载的类。

他的值是由loadClassFromDex这个函数进行返回的，所以我们就进行进一步的查看。

  

![图片.png](https://image.3001.net/images/20180308/15204879469993.png!small)  

这里看到这样的一个结构。  

![图片.png](https://image.3001.net/images/20180308/15204879346590.png!small)  

来看看这个结构的详细内容。  

![图片.png](https://image.3001.net/images/20180308/15204879215933.png!small)  

这个结构是不是和dex的结构一模一样，说明了这里就是我们需要东西。

研究系统源码最主要的目的就是脱壳或者加固的嘛，不然我们看这些痛苦的代码干什么。

## 总结

### 可以脱dex的地方。

[dvmDefineClass()](https://bbs.ichunqiu.com/thread-35286-1-1.html?from=beef)

[loadClassFromDex()](https://bbs.ichunqiu.com/thread-35286-1-1.html?from=beef)  
这两个地方都可以进行一定的尝试来进行脱壳。

# 0x05 结束语

关于系统源码还是有很多事情需要继续深层次的挖掘。而且加固，脱壳都可能会基于源码进行实现。

