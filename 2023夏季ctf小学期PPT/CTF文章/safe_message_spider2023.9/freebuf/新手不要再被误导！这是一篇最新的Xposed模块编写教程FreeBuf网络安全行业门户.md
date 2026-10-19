***本文作者：张召忠，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 0x00 前言

**在互联网上，关于Xposed模块编写的教程可谓是一抓一大把。但由于时间的推移，很多工具和方法都发生了变化（如Eclipse退出安卓编程舞台，AndroidStudio
不断升级导致其一些设置也随之变化等）也正因此，网上的教程往往有一些时限性，比如现如今 provide
这个关键字已经被舍弃了却仍有人在用，还有些说要把jar包放到lib文件夹而非libs文件夹……种种错误或者落伍的教程对新手产生了很大的误导。
笔者近日收到过朋友初学Xposed模块编写时的求助，看了一些他找的参考教程，觉得多多少少都存在点问题，因此萌生了写一篇关于在最新AndriodStudio
开发环境下实现Xposed模块开发入门的文章。**

![](https://image.3001.net/images/20181111/1541928495_5be7f62fe01b9.png!small)

## 0x01 Xposed 模块编写简介

Xposed
框架的原理就不多说了，它部署在ROOT后的安卓手机上，通过替换/system/bin/app_process程序控制zygote进程，使得app_process在启动过程中会加载XposedBridge.jar这个jar包，从而完成对Zygote进程及其创建的Dalvik虚拟机的劫持。可以让我们在不修改APK源码的情况下，通过自己编写的模块来影响程序运行的框架服务，实现类似于自动抢红包、微信消息自动回复等功能。

其实，从本质上来讲，Xposed 模块也是一个 Android 程序。但与普通程序不同的是，想要让写出的Android程序成为一个Xposed
模块，要额外多完成以下四个硬性任务：

> 1、让手机上的xposed框架知道我们安装的这个程序是个xposed模块。
>
> 2、模块里要包含有xposed的API的jar包，以实现下一步的hook操作。
>
> 3、这个模块里面要有对目标程序进行hook操作的方法。
>
> 4、要让手机上的xposed框架知道，我们编写的xposed模块中，哪一个方法是实现hook操作的。

这就引出我即将要介绍的四大件（与前四步一一对照）：

> 1、AndroidManifest.xml
>
> 2、XposedBridgeApi-xx.jar 与 build.gradle
>
> 3、实现hook操作的具体代码
>
> 4、xposed_Init

牢记以上四大件，按照顺序一个一个实现，就能完成我们的第一个Xposed模块编写。下面我们就开始吧！

## 0x02 迈开第一步，新建项目并编辑AndroidManifest.xml

1、首先打开AndroidStudio（以版本3.1为例，还在用老版本的请升级），建立一个工程，提示我们选择“Activity”，那就选一个Empty
Activity吧。（这个是模块的界面，随意选择即可）。

![新建项目并编辑AndroidManifest.xml](https://image.3001.net/images/20181111/1541924626_5be7e7128a210.png!small)

2、我们可以把项目查看方式设置为Project模式，以方便查看。然后在
“项目名称/app/src/main/”目录下找到AndroidManifest.xml，双击之，并在指定位置插入以下三段代码：

    
    
    <meta-data
    
    android:name="xposedmodule"
    
    android:value="true" />
    
    <meta-data
    
        android:name="xposeddescription"
    
        android:value="这是一个Xposed例程" />
    
    <meta-data
    
        android:name="xposedminversion"
    
        android:value="53" />

插入位置及代码说明如图所示：

![插入位置及代码说明](https://image.3001.net/images/20181111/1541924925_5be7e83d3cf81.png!small)

插入之后，如果你把手机连上AndroidStudio
，点击“编译”或者“运行”的话，手机就会启动刚刚编写的这个程序。而在手机里的Xposed框架中也会显示出这个模块：

![手机里的Xposed框架](https://image.3001.net/images/20181111/1541925052_5be7e8bcdd6de.jpg!small)

说明Xposed框架已经认出了我们写的程序。但先别高兴太早——虽然框架已经觉得他是一个Xposed模块了，但我们自己心里清楚，这个模块还啥都不会干呢。下一步，我们让这个模块长点本事。

## 0x03 走出第二步，搞定XposedBridgeApi-xx.jar 与 build.gradle

我们知道，Xposed模块主要功能是用来Hook其他程序的各种函数。但是，如何让前一步中的那个“一穷二白”的模块长本事呢？那就要引入
XposedBridgeApi.jar
这个包，你可以理解为一把兵器，模块有了这把宝刀才能施展出Hook本领。以前，都需要手动下载诸如XposedBridgeApi-54.jar 、
XposedBridgeApi-82.jar 等jar包，然后手工导入到libs目录里，才能走下一步道路。其实在AndroidStudio
3.1里面，我们完全不用这么麻烦，只需要多写一行代码，就让AndroidStuido自动给我们配置XposedBridgeApi.jar
！下面操作开始（序号接着上一节）：

3、在 “项目名称/app/src/main/”目录下找到build.gradle，在图示位置加上：

    
    
    repositories {
    
        jcenter()
    
    }

以及

    
    
    compileOnly 'de.robv.android.xposed:api:82'
    
    compileOnly 'de.robv.android.xposed:api:82:sources'

这句代码是告诉AndroidStuido使用jcenter作为代码仓库，从这个仓库里远程寻找 de.robv.android.xposed:api:82
这个API。这个网上很少有Xposed教程介绍它的！（我们不用自己找XposedBridgeApi.jar了。注意！此处要用compileOnly这个修饰符！网上有些写的是provide
，现在已经停用了！）如图：

![代码仓库](https://image.3001.net/images/20181111/1541925314_5be7e9c21f13d.png!small)

写完之后， build.gradle会提示文件已经修改，是否同步。点击 “sync now”，同步即可：

![代码仓库](https://image.3001.net/images/20181111/1541925374_5be7e9fe0fe7b.png!small)

【ps:如果网络不通，或者同步不畅，就不要进行第三步的repositories { jcenter()}这个步骤了，改做这个步骤：】

> 手动下载XposedBridgeApi-82.jar
> ，拖放到“项目名称/app/libs/”里面（不是网上说的单独建立lib文件夹，那是很久以前的故事了！），然后右键“Add As Library”
> 自行添加这个jar包。而compileOnly 'de.robv.android.xposed:api:82'和 compileOnly
> 'de.robv.android.xposed:api:82:sources'这两句仍然照常添加。

好了，现在宝刀已经到手。下一步，就要开始“施展刀法”（编写hook代码）了。

## 0x04 迈开第三步，实现hook操作的具体代码

4、在“施展刀法”（编写hook代码）之前，我们先要立一个靶子。在界面上画一个按钮，并在MainAcitiviy里写代码如下：

    
    
    package com.example.root.xposd_hook_new;
    
    import android.support.v7.app.AppCompatActivity;
    
    import android.os.Bundle;
    
    import android.view.View;
    
    import android.widget.Button;
    
    import android.widget.Toast;
    
    public class MainActivity extends AppCompatActivity {
    
        private Button button;
    
        @Override
    
        protected void onCreate(Bundle savedInstanceState) {
    
            super.onCreate(savedInstanceState);
    
            setContentView(R.layout.activity_main);
    
            button = (Button) findViewById(R.id.button);
    
            button.setOnClickListener(new View.OnClickListener() {
    
                public void onClick(View v) {
    
                    Toast.makeText(MainActivity.this, toastMessage(), Toast.LENGTH_SHORT).show();
    
                }
    
            });
    
        }
    
        public String toastMessage() {
    
            return "我未被劫持";
    
        }
    
    }

![实现hook操作的具体代码](https://image.3001.net/images/20181111/1541925608_5be7eae8c43d2.png!small)

![实现hook操作的具体代码](https://image.3001.net/images/20181111/1541925623_5be7eaf7cf013.png!small)

这个靶子很简单：MainActivity界面有个按钮，点击按钮后会弹出一个toast提示，该提示的内容由 toastMessage()
方法提供，而toastMessage()的返回值为“我未被劫持”：

![我未被劫持](https://image.3001.net/images/20181111/1541927640_5be7f2d8e9586.png!small)

下面我们正式开始“施展刀法”（编写hook代码）
来hook我们的MainActivity并修改这个类的toastMessage()方法，让它的返回值为“你已被劫持”：

5、在MainActivity的同级路径下新建一个类“HookTest.java”，代码如下：

    
    
    package com.example.root.xposd_hook_new;  
    
    
    import de.robv.android.xposed.IXposedHookLoadPackage;
    
    import de.robv.android.xposed.XC_MethodHook;
    
    import de.robv.android.xposed.XposedBridge;
    
    import de.robv.android.xposed.XposedHelpers;
    
    import de.robv.android.xposed.callbacks.XC_LoadPackage;
    
    public class HookTest implements IXposedHookLoadPackage {
    
        public void handleLoadPackage(XC_LoadPackage.LoadPackageParam loadPackageParam) throws Throwable {
    
            if (loadPackageParam.packageName.equals("com.example.root.xposd_hook_new")) {
    
                XposedBridge.log(" has Hooked!");
    
                Class clazz = loadPackageParam.classLoader.loadClass(
    
                        "com.example.root.xposd_hook_new.MainActivity");
    
                XposedHelpers.findAndHookMethod(clazz, "toastMessage", new XC_MethodHook() {
    
                    protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
    
                        super.beforeHookedMethod(param);
    
                        //XposedBridge.log(" has Hooked!");
    
                    }
    
                    protected void afterHookedMethod(MethodHookParam param) throws Throwable {
    
                        param.setResult("你已被劫持");
    
                    }
    
                });
    
            }
    
        }
    
    }

![新建一个类“HookTest.java”](https://image.3001.net/images/20181111/1541925724_5be7eb5ce22b1.png!small)

由代码可知，我们是通过IXposedHookLoadPackage接口中的handleLoadPackage方法来实现Hook并篡改程序的输出结果的。代码中“com.example.root.xposd_hook_new
”是目标程序的包名，"com.example.root.xposd_hook_new.MainActivity" 是想要Hook的类，
"toastMessage"是想要Hook的方法。我们在afterHookedMethod方法（用来定义Hook了目标方法之后的操作）中，修改了toastMessage()方法的返回值为“你已被劫持”。

OK，以上用来hook的代码编写完毕，让我们进行下一步操作。

## 0x05 最后一步，添加入口点

右键点击 “main ” 文件夹 ， 选择new --> Folder -->Assets Folder，新建assets 文件夹：

![新建assets
文件夹](https://image.3001.net/images/20181111/1541927167_5be7f0ff4e92d.jpg!small)

然后右键点击 assets文件夹， new-->
file，文件名为xposed_init（文件类型选text），并在其中写上入口类的完整路径（就是自己编写的那一个Hook类），这样，
Xposed框架就能够从这个 xposed_init 读取信息来找到模块的入口，然后进行Hook操作了：

![进行Hook操作](https://image.3001.net/images/20181111/1541927874_5be7f3c2acb84.jpg!small)

![进行Hook操作](https://image.3001.net/images/20181111/1541927281_5be7f1714909a.png!small)

好了，曙光就在前面！最后选择禁用 Instant Run： 单击 File -> Settings -> Build, Execution,
Deployment -> Instant Run，把勾全部去掉。

![禁用 Instant
Run](https://image.3001.net/images/20181111/1541927919_5be7f3efa383e.png!small)

然后点击小三角“运行”！在Xposed框架里找到自己写的模块，打上勾，重启——点开自己的程序看看，是不是toast的提示已经变了？

![toast的提示](https://image.3001.net/images/20181111/1541927328_5be7f1a0ef83e.png!small)

本次教程就到这里，谢谢！

 ***本文作者：张召忠，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

