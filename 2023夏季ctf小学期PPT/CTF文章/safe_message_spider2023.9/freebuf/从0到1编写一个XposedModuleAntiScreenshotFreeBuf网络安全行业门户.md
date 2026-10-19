最近开始接触app测试，发现坑有些多，赤手空拳搞不定，决定开始学习xposed module的相关的操作。

毕竟“ **root==god** ”，要好好利用 root 来对app进行降维打击！

今天先解决某些app不能截图的问题，实测可bypass 某im的闪图功能、某支付软件的付款码界面、还有某银行app。

![1599131155-92175.jpg](https://image.3001.net/images/20200903/1599133372.jpg!small)

代码已开源到GitHub，并且还有现成的Release等你下载！

Github Repo：[https://github.com/runtimed/Anti-Screenshot](https://github.com/lushann/Anti-Screenshot/tree/master)

Release： [https://github.com/runtimed/Anti-Screenshot/releases](https://github.com/lushann/Anti-Screenshot/releases)

 **正文Start**

毕竟是从0到1的一篇文章，基本流程还得走走。

## 一、环境准备

已经配置好xposed环境的测试机一枚

![](https://image.3001.net/images/20200903/1599134351.png!small)

准备好一份XposedBridge API jar：<https://forum.xda-developers.com/xposed/xposed-api-changelog-developer-news-t2714067>

## 二、项目初始化

### 1.Android Studio 新建项目

这里新建一个 Empty Activity的项目

![](https://image.3001.net/images/20200903/1599134398.png!small)

说明：

> 如果选择No Activity
> 的话，在studio里边没办法直接安装到测试机上进行测试，因为没有actvity。模块开发结束后，可以把activity删掉，然后生成签名的apk，这样安装后，模块不会在桌面生成图标，完美。
>
> 我寻思了一下，我会用到的测试机，Android版本最低也是8.1，所以就把Minimum SDK设置成 8.0 了。

### 2.编写xposed module 基本信息

在src/main/res/values/strings.xml中添加如下：

    
    
    <string name="xposed_description">强制截屏 @lushan</string>

在AndroidManifest.xml文件中，<application>标签内部添加以下代码

    
    
    <meta-data android:name="xposedmodule" android:value="true" /> <meta-data android:name="xposeddescription" android:value="@string/xposed_description" /> <meta-data android:name="xposedminversion" android:value="54" />

如图：

![image.png](https://image.3001.net/images/20200903/1599133373.png!small)

### 3.加载 XposedBridge API 包

将XposedBridgeApi包拷贝到libs下，然后右键 Add As Library：

![image.png](https://image.3001.net/images/20200903/1599130800.png!small)

在app文件夹下的build.gradle中检查 dependencies块中的内容

![image.png](https://image.3001.net/images/20200903/1599130801.png!small)

说明：网上的教程大多数写的是用 provided，该关键字已被 compileOnly 取代。

如果本步骤设置不当，xposed框架会打印如下log：

![](https://image.3001.net/images/20200903/1599134443.png!small)

### 4.新建Xposed module 入口函数

![image.png](https://image.3001.net/images/20200903/1599130802.png!small)

函数体：

    
    
    public class HookMain implements IXposedHookLoadPackage {
        @Override
        public void handleLoadPackage(XC_LoadPackage.LoadPackageParam loadPackageParam) throws Throwable {
        
        }
    }

咱们在这一步呢，先写个空的入口函数，内部逻辑以后再写。

### 5.指定 Xposed module 入口函数

在src/main下，新建 assets/xposed_init , 文件内容为包名+入口函数名

![image.png](https://image.3001.net/images/20200903/1599134116.png!small)

  

到这儿，一个xposed module的雏形就差不多完成了，接下来我们需要完善相关的Hook逻辑，不过我们现在可以执行一下，看一下啥效果

![image.png](https://image.3001.net/images/20200903/1599133374.png!small)

xposed 框架能够正确识别到这是个 module，并且能够显示之前设置好的 module 基本信息。

![1599131749.gif!small](https://image.3001.net/images/20200903/1599131749.gif!small)

## 三、分析Android禁止截屏相关函数

总的来说，经过我的细致观察，Android提供的禁止截屏的方法，最终都是给“Display“这个类，增加“FLAG_SECURE”属性

下边是官方文档关于如何设定 “FLAG_SECURE“的方法：

> An application creates a window with a secure surface by specifying the
> **WindowManager.LayoutParams#FLAG_SECURE** window flag. Likewise, an
> application creates a SurfaceView with a secure surface by calling
> **SurfaceView#setSecure** before attaching the secure view to its containing
> window.

文档：<https://developer.android.com/reference/android/view/Display#FLAG_SECURE>

很明显，上边这段文档介绍了两种方法来设定 Display.FLAG_SECURE，一个呢是通过指定 window类的flag：
**WindowManager.LayoutParams#FLAG_SECURE** ， 另一个就是使用 **SurfaceView#setSecure**
方法。

接下来好好看一下相关的函数，以备Hook之用。

### 1\. 指定window flag

可以通过以下两个方法实现：

 **window.setFlag(WindowManager.LayoutParams.FLAG_SECURE)**

![image.png](https://image.3001.net/images/20200903/1599133375.png!small)

文档：<https://developer.android.com/reference/android/view/Window#setFlags(int,%20int)>

 **window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)**

![image.png](https://image.3001.net/images/20200903/1599133376.png!small)

<https://developer.android.com/reference/android/view/Window#addFlags(int)>

### 2.SurfaceView.setSecure

![image.png](https://image.3001.net/images/20200903/1599134117.png!small)

<https://developer.android.com/reference/android/view/SurfaceView#setSecure(boolean)>

综上所述，咱们需要hook三个函数。

## 四、完成 module 编写

其实逻辑还挺简单的，hook函数调用、改参数，一气呵成

    
    
    public class HookMain implements IXposedHookLoadPackage {
        String packageName = new String();
    
        @Override
        public void handleLoadPackage(XC_LoadPackage.LoadPackageParam loadPackageParam) throws Throwable {
    
            packageName = loadPackageParam.packageName;
    
            // Hook "window.setFlag(WindowManager.LayoutParams.FLAG_SECURE)"
            XposedHelpers.findAndHookMethod(Window.class, "setFlags", int.class, int.class,
                    removeSecureFlagHook);
    
            // Hook "window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)"
            XposedHelpers.findAndHookMethod(Window.class, "addFlags", int.class,
                    removeSecureFlagHook);
    
            // Hook "SurfaceView.setSecure"
            XposedHelpers.findAndHookMethod(SurfaceView.class, "setSecure", boolean.class,
                    removeSetSecureHook);
    
    
        }
    
    
        private final XC_MethodHook removeSecureFlagHook = new XC_MethodHook() {
            @Override
            protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                if ((Integer) param.args[0] == WindowManager.LayoutParams.FLAG_SECURE){
                    param.args[0] = 0;
                    XposedBridge.log("Anti Screenshot : 已阻止" + packageName);
                }
            }
        };
    
    
    
        private final XC_MethodHook removeSetSecureHook = new XC_MethodHook() {
            @Override
            protected void beforeHookedMethod(XC_MethodHook.MethodHookParam param) throws Throwable {
                param.args[0] = false;
                XposedBridge.log("Anti Screenshot : 已阻止" + packageName);
            }
        };
    
    }

## 五、测试

保证在Xposed框架中启用这个模块之后，咱们简单测试一下闪图

![image.png](https://image.3001.net/images/20200903/1599130803.png!small)

![image.png](https://image.3001.net/images/20200903/1599130804.png!small)

Yes！成功看到了茄子！

此时，在Xposed的 log 界面我们可以看到：

![1599132661.png!small](https://image.3001.net/images/20200903/1599132661.png!small)

Yes！本文结束，模块相关问题请提issus,告辞

![](https://image.3001.net/images/20200903/1599134049.jpg!small)

## 参考：

> Xposed模块开发指南 <https://yuanfentiank789.github.io/2017/04/01/xposeddev/>
>
> DisableFlagSecure <https://github.com/veeti/DisableFlagSecure>

