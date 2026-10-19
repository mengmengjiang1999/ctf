## 前言

**Xposed作为一个著名的Hook框架，早已经在移动安全行业家喻户晓。今天写这篇文章主要也是想下手玩玩这个框架，至于框架的安装，虽然也会碰见很多问题，但是今天暂不附上教程，因为最近精力有限，等有时间我会附上安装教程，以及遇见的问题解决方法！**

## 知识前导

### Hook技术

> Hook英文翻译为“钩子”，而钩子就是在事件传送到终点前截获并监控事件的传输，像个钩子钩上事件一样，并且能够在钩上事件时，处理一些自己特定的事件；
>
> Hook使它能够将自己的代码“融入”被勾住（Hook）的进程中，成为目标进程的一部分；
>
> 在Andorid沙箱机制下，Hook是我们能通过一个程序改变其他程序某些行为得以实现；

### Hook原理

Hook技术本质是函数调用，由于处于Linux用户状态，每个进程有自己独立的进程控件，所以必须先注入所要Hook的进程空间，修改其内存中进程代码，替换过程表的符号地址，通过ptrace函数附加进程，向远程进程注入so库，从而达到监控以及远程进程关键函数挂钩；

### Xposed原理分析

Xposed框架的原理是修改系统文件，替换了`/system/bin/app_process`可执行文件，在启动Zygote时加载额外的jar文件（`/data/data/de.robv.android.xposed.installer/bin/XposedBridge.jar`），并执行一些初始化操作(执行`XposedBridge的main`方法)。然后我们就可以在这个Zygote上下文中进行某些hook操作。

在Android中，zygote是整个系统创建新进程的核心进程。zygote进程在内部会先启动Dalvik虚拟机，继而加载一些必要的系统资源和系统类，最后进入一种监听状态。

在之后的运作中，当其他系统模块（比如AMS）希望创建新进程时，只需向zygote进程发出请求，zygote进程监听到该请求后，会相应地fork出新的进程，于是这个新进程在初生之时，就先天具有了自己的Dalvik虚拟机以及系统资源。

zygote进程是由init进程启动起来，由`init.rc`脚本中关于zygote的描述可知：`zygote`对应的可执行文件就是`/system/bin/app_process`，也就是说系统启动时会执行到这个可执行文件的`main()`函数里。

## 正文

Xposed的技术实现是通过系统进程Hook技术，所以必须要有root权限才行。一般通过刷机来实现，这里我找了个兼容模拟器的Xposed来操作。这里我通过三个简单的Hook插件开发，来介绍下Xposed插件开发的基本方法。当然我会附上完整源码来供大家学习研究。接下来，让我们开启上帝模式！

### Hook装载的apk程序包名

 **新建一个入口类并继承并实现IXposedHookLoadPackage接口**

如下操作，我们新建了一个Hook的类，并实现`IXposedHookLoadPackage`接口中的`handleLoadPackage`方法，然后对当前装载的apk程序包名进行打印。

    
    
    package com.example.test;​import de.robv.android.xposed.IXposedHookLoadPackage;import de.robv.android.xposed.XposedBridge;import de.robv.android.xposed.callbacks.XC_LoadPackage;/** * Created by Ethan on 2018/11/18\. */public class  Hook implements IXposedHookLoadPackage{    @Override    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam loadPackageParam) throws Throwable {        // 打印装载的apk程序包名        XposedBridge.log("Launch app: " + loadPackageParam.packageName);        XposedBridge.log("Hook已经成功了");    }}
    

这是一个最简单的一个Xposed插件，实现的功能就是对当前安卓虚拟机装载的apk程序的报名进行Hook，并且打印出来。![1560071502_5cfccd4e2cb6b.png!small](https://image.3001.net/images/20190609/1560071502_5cfccd4e2cb6b.png!small)

### 按钮劫持Hook

首先自己写一个粗糙的apk，实现的功能就是点击界面的按钮，就会弹出消息你未被劫持的消息!具体完整代码如下：

MainActivity:

    
    
    package com.example.ceshi;import android.support.v7.app.AppCompatActivity;import android.os.Bundle;import android.view.View;import android.widget.Button;import android.widget.Toast;​public class MainActivity extends AppCompatActivity {    private Button button;​    public void onCreate(Bundle savedInstanceState) {        super.onCreate(savedInstanceState);        setContentView(R.layout.activity_main);​        button = (Button) findViewById(R.id.button);​        button.setOnClickListener(new View.OnClickListener() {            public void onClick(View v) {                Toast.makeText(MainActivity.this, toastMessage(), Toast.LENGTH_SHORT).show();            }        });    }​    public String toastMessage() {        return "我未被劫持";    }}
    

activity_main.xml:

    
    
    <?xml version="1.0" encoding="utf-8"?><android.support.constraint.ConstraintLayout    xmlns:android="http://schemas.android.com/apk/res/android"    xmlns:tools="http://schemas.android.com/tools"    xmlns:app="http://schemas.android.com/apk/res-auto"    android:layout_width="match_parent"    android:layout_height="match_parent"    tools:context="com.example.ceshi.MainActivity">​    <Button        android:id="@+id/button"        android:layout_width="wrap_content"        android:layout_height="wrap_content"        android:text="Button" />​</android.support.constraint.ConstraintLayout>
    

实现功能如图

![1560071514_5cfccd5a85f29.png!small](https://image.3001.net/images/20190609/1560071514_5cfccd5a85f29.png!small)

接下来我们要对这个apk的按钮的方法进行Hook，并且修改方法。

    
    
    package com.example.xposed;import de.robv.android.xposed.IXposedHookLoadPackage;import de.robv.android.xposed.XC_MethodHook;import de.robv.android.xposed.XposedHelpers;import de.robv.android.xposed.callbacks.XC_LoadPackage;​public class HookToast implements IXposedHookLoadPackage {​//Module继承了IXposedHookLoadPackage接口，当系统加载应用包的时候回回调 handleLoadPackage；    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam loadPackageParam) throws Throwable {        //过滤包名，定位要Hook的包名        if (loadPackageParam.packageName.equals("com.example.ceshi")) {​            //定位要Hook的具体的类名            Class clazz = loadPackageParam.classLoader.loadClass("com.example.ceshi.MainActivity");            //Hook的方法为toastMessage，XposedHelpers的静态方法 findAndHookMethod就是hook函数的的方法，其参数对应为   类名+loadPackageParam.classLoader（照写）+方法名+参数类型（根据所hook方法的参数的类型，即有多少个写多少个，加上.class）+XC_MethodHook回调接口；            XposedHelpers.findAndHookMethod(clazz, "toastMessage", new XC_MethodHook() {                protected void beforeHookedMethod(MethodHookParam param) throws Throwable {                    super.beforeHookedMethod(param);                }​                protected void afterHookedMethod(XC_MethodHook.MethodHookParam param) throws Throwable {                    //param.setResult("你已被劫持")将返回的结果设置成了你已被劫持                    param.setResult("你已被劫持");                }            });        }    }}
    

经过以上操作，当apk执行时会调用我们的Hook类，然后执行就会对apk对应的进程方法进行修改，达到Hook的效果。

Hook后效果如图：

![1560071524_5cfccd6416f7e.png!small](https://image.3001.net/images/20190609/1560071524_5cfccd6416f7e.png!small)

### 登陆劫持

上面进行的按钮劫持的效果也许还不够明显或者说是有趣。大家可能跟我一样喜欢登陆劫持密码这样的操作，首先我们还是自己写一个简单的登陆程序。

MainActivity:

    
    
    package com.example.xposedtest;​import android.support.v7.app.AppCompatActivity;import android.os.Bundle;import android.view.View;import android.widget.Button;import android.widget.EditText;import android.widget.Toast;​public class MainActivity extends AppCompatActivity {    EditText Name;   //定义Plain Test控件第一个输入框的名字    EditText Pass;   //定义Plain Test控件第二个输入框的名字​    protected void onCreate(Bundle savedInstanceState) {        super.onCreate(savedInstanceState);        setContentView(R.layout.activity_main);        Name = (EditText) findViewById(R.id.TEXT_NAME); //通过findViewById找到输入框控件对应的id并给它起一个名字        Pass = (EditText) findViewById(R.id.TEST_PASS);//通过findViewById找到输入框控件对应的id并给它起一个名字        Button Login = (Button) findViewById(R.id.BTN_Login);//通过findViewById找到按钮控件对应的id并给它起一个名字        Login.setOnClickListener(new View.OnClickListener() {  //监听有没有点击按钮控件 如果点击了就会执行onClick函数            @Override            public void onClick(View view) {                check(Name.getText().toString().trim(),Pass.getText().toString().trim()); //调用check函数            }        });    }    public void check(String name,String pass)   //自定义函数check 这里用来检查用户名和密码是否是cck和1234    {        if(name.equals("cck")&&pass.equals("1234"))        {            Toast.makeText(MainActivity.this,"登录成功", Toast.LENGTH_SHORT).show();//弹框        }        else            Toast.makeText(MainActivity.this,"登录失败", Toast.LENGTH_SHORT).show();//弹框    }}
    

activity_main.xml:

    
    
    <?xml version="1.0" encoding="utf-8"?><RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"xmlns:tools="http://schemas.android.com/tools"android:layout_width="match_parent"android:layout_height="match_parent"    tools:context="com.example.xposedtest.MainActivity">​    <TextView        android:text="用户名："        android:layout_width="wrap_content"        android:layout_height="wrap_content"        android:layout_alignParentTop="true"        android:layout_alignParentLeft="true"        android:layout_alignParentStart="true"        android:layout_marginLeft="63dp"        android:layout_marginStart="63dp"        android:layout_marginTop="77dp"        android:id="@+id/textView"/>​    <TextView        android:text="密码："        android:layout_width="wrap_content"        android:layout_height="wrap_content"        android:layout_marginTop="77dp"        android:id="@+id/textView2"        android:layout_below="@+id/textView"        android:layout_alignLeft="@+id/textView"        android:layout_alignStart="@+id/textView"/>​    <EditText        android:layout_width="wrap_content"        android:layout_height="wrap_content"        android:inputType="textPersonName"        android:ems="10"        android:layout_alignBottom="@+id/textView"        android:layout_toRightOf="@+id/textView"        android:layout_toEndOf="@+id/textView"        android:id="@+id/TEXT_NAME"/>​    <EditText        android:layout_width="wrap_content"        android:layout_height="wrap_content"        android:inputType="textPassword"        android:ems="10"        android:layout_alignBottom="@+id/textView2"        android:layout_toRightOf="@+id/textView2"        android:layout_toEndOf="@+id/textView2"        android:id="@+id/TEST_PASS"/>​    <Button        android:text="登录"        android:layout_width="wrap_content"        android:layout_height="wrap_content"        android:layout_below="@+id/TEST_PASS"        android:layout_toRightOf="@+id/textView"        android:layout_toEndOf="@+id/textView"        android:layout_marginLeft="13dp"        android:layout_marginStart="13dp"        android:layout_marginTop="130dp"        android:id="@+id/BTN_Login"/>​</RelativeLayout>
    

实现效果如图：

![1560071535_5cfccd6fab716.png!small](https://image.3001.net/images/20190609/1560071535_5cfccd6fab716.png!small)

![1560071543_5cfccd77f0390.png!small](https://image.3001.net/images/20190609/1560071543_5cfccd77f0390.png!small)

只有当我们输入正确的用户名cck和密码1234时才会弹出登陆成功的消息。

这里的我们要Hook的效果为不管输入什么，都会显示登陆成功，实现的手段就是Hook对应的方法，并对相应的参数进行修改，还是使用上面的回调方法来实现

    
    
    package com.example.xposeddeluhook;​import de.robv.android.xposed.IXposedHookLoadPackage;import de.robv.android.xposed.XC_MethodHook;​​import de.robv.android.xposed.XposedBridge;import de.robv.android.xposed.callbacks.XC_LoadPackage;​import static de.robv.android.xposed.XposedHelpers.findAndHookMethod;public class Hookdenglu implements IXposedHookLoadPackage {​    /**     * 包加载时候的回调     */    public void handleLoadPackage(final XC_LoadPackage.LoadPackageParam lpparam) throws Throwable {​        // 将包名不是 com.example.xposedtest 的应用剔除掉,可以减少管理的类        if (!lpparam.packageName.equals("com.example.xposedtest"))            return;        XposedBridge.log("Loaded app: " + lpparam.packageName);​        //第一个参数是className，表示被注入的方法所在的类        //第二个参数是类加载器，照抄就行        //第三个参数是被注入的方法名        //第四五个参数是第三个参数的两个形参的类型        //最后一个参数是匿名内部类        findAndHookMethod("com.example.xposedtest.MainActivity", lpparam.classLoader, "check", String.class,                String.class, new XC_MethodHook() {​            /**             * 该方法在check方法调用之前被调用，我们输出一些日志，并且捕获参数的值。             * 最后两行的目的是改变参数的值。也就是说无论参数是什么值，都会被替换为name为cck,pass为1234             * @param param             * @throws Throwable             */                    protected void beforeHookedMethod(MethodHookParam param) throws Throwable {                        XposedBridge.log("开始劫持了~");                        XposedBridge.log("参数1 = " + param.args[0]);                        XposedBridge.log("参数2 = " + param.args[1]);                        param.args[0] = "cck";                        param.args[1] = "1234";                    }             /**             * 该方法在check方法调用之后被调用             * @param param             * @throws Throwable             */​                    protected void afterHookedMethod(MethodHookParam param) throws Throwable {                        XposedBridge.log("劫持结束了~");                        XposedBridge.log("参数1 = " + param.args[0]);                        XposedBridge.log("参数2 = " + param.args[1]);​                    }                });    }​}
    

上述代码我们通过对方法的参数进行了重赋值，来达到了我们想要的结果！

实现效果如下：

![1560071552_5cfccd8046b44.png!small](https://image.3001.net/images/20190609/1560071552_5cfccd8046b44.png!small)

Xposed日志如下：

![1560071561_5cfccd8905917.png!small](https://image.3001.net/images/20190609/1560071561_5cfccd8905917.png!small)

## Think one Think

Xposed可以在不修改APK源码的情况下，通过自己编写的模块来影响程序运行的框架服务，采用了插件机制，通过替换/system/bin/app_process程序控制zygote进程，使得app_process在启动过程中会加载XposedBridge.jar这个jar包，从而完成对Zygote进程及其创建的Dalvik虚拟机的劫持，从而可以使我们开启上帝模式，从原理上讲，只要你对要操作的方法，参数的个数，类型了如指掌，那你就可以实现任意应用的任意方法的Hook。这也是Xposed插件开发的初衷！

 ***本文作者：cck，转载请注明来自FreeBuf.COM**

