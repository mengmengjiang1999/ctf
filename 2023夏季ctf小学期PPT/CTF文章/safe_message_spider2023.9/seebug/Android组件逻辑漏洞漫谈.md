**作者：evilpan  
原文链接：<https://mp.weixin.qq.com/s/shbmbR0AizKHJSAJsLSbfA>  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

# 前言

随着社会越来越重视安全性，各种防御性编程或者漏洞缓解措施逐渐被加到了操作系统中，比如代码签名、指针签名、地址随机化、隔离堆等等，许多常见的内存破坏漏洞在这些缓解措施之下往往很难进行稳定的利用。因此，攻击者们的目光也逐渐更多地投入到逻辑漏洞上。逻辑漏洞通常具有很好的稳定性，不用受到风水的影响；但同时也隐藏得较深、混迹在大量业务代码中难以发现。而且由于形式各异，不太具有通用性，从投入产出比的角度来看可能不是一个高优先级的研究方向。但无论如何，这都始终是一个值得关注的攻击面。因此，本文就以
Android 平台为目标介绍一些常见的逻辑漏洞。

# 四大组件

接触过 Android 的人应该都听说过 “四大组件”，开发应用首先需要学习的就是各个组件的生命周期。所谓四大组件，分别是指 **Activity** 、
**Service** 、 **Broadcast Receiver** 和 **Content Provider**
，关于这些组件的实现细节可以参考官方的文档: [Application
Fundamentals](https://developer.android.com/guide/components/fundamentals)。

在安全研究中，四大组件值得我们特别关注，因为这是应用与外界沟通的重要桥梁，甚至在应用内部也是通过这些组件构建起了相互间松耦合的联系。比如应用本身可以不申请相机权限，但可以通过组件间的相互通信让（系统）相机应用打开摄像头并取得拍到的照片，仿佛是自身进行拍照的一样。

而在组件交互的过程中，最为核心的数据结构就是
[Intent](https://developer.android.com/reference/android/content/Intent)，这是大部分组件之间进行通信的载体。

# Intent 101

根据官方的说法，Intent 是 “对某种要执行的操作的抽象描述”，直译过来也可以叫做 “意图”，比如说 **想要**
打开摄像机拍照、想要打开浏览器访问网址，想要打开设置界面，……都可以用 Intent 来描述。

Intent 的主要形式有两种，分别是显式 Intent 和隐式 Intent；二者的差别主要在于前者显式指定了 `Component`，后者没有指定
Component，但是会通过足够的信息去帮助系统去理解意图，比如 `ACTION`、`CATAGORY` 等。

Intent 的最主要功能是用来启动 Activity，因此我们以这个场景为例，从源码中分析一下 Intent 的具体实现。启动 Activity
的常规代码片段如下：

    
    
    Intent intent = new Intent(context, SomeActivity.class);
    startActivity(intent);

这里用的是显式 Intent，但不是重点。一般在某个 Activity 中调用，因此调用的是 `Activity.startActivity`，代码在
_frameworks/base/core/java/android/app/Activity.java_ 中，这里不复制粘贴了，总而言之调用链路如下：

  * Activity.startActivity()
  * Activity.startActivityForResult()
  * Instrumentation.execStartActivity()
  * ActivityTaskManager.getService().startActivity()
  * IActivityTaskManager.startActivity()

最后一条调用是个接口，这是个很常见的 pattern 了，下一步应该去找其实现，不出意外的话这个实现应该在另一个进程中。事实上也正是在
`system_server` 中：

  * ActivityTaskManagerService.startActivity()
  * ActivityTaskManagerService.startActivityAsUser()
  * ActivityStarter.execute()

最后一个方法通过前面传入的信息去准备启动 Activity，包括 caller、userId、flags，callingPackage 以及最重要的
intent 信息，如下：

    
    
    private int startActivityAsUser(...) {
        // ...
        return getActivityStartController()
                .obtainStarter(
                    intent, "startActivityAsUser")
                .setCaller(caller)
                .setCallingPackage(callingPackage)
                .setCallingFeatureId(callingFeatureId)
                .setResolvedType(resolvedType)
                .setResultTo(resultTo)
                .setResultWho(resultWho)
                .setRequestCode(requestCode)
                .setStartFlags(startFlags)
                .setProfilerInfo(profilerInfo)
                .setActivityOptions(bOptions)
                .setUserId(userId)
                .execute();
    }

**ActivityStarter.execute()** 主要的逻辑如下:

    
    
    int execute() {
        // ...
        if (mRequest.activityInfo == null) {
            mRequest.resolveActivity(mSupervisor);
        }
        res = resolveToHeavyWeightSwitcherIfNeeded();
        res = executeRequest(mRequest);
    
    }

其中，`resolveActivity` 用于获取要启动的 Activity
信息，例如在隐式启动的情况下，可能有多个符合要求的目标，也会弹出菜单询问用户选用哪个应用打开。`executeRequest`
中则主要进行相关权限检查，在所有权限满足条件后再调用 `startActivityUnchecked` 去执行真正的调用。

其中大部分流程我在 [Android12 应用启动流程分析](https://evilpan.com/2021/12/05/apk-startup/)
中已经介绍过了，这里更多是关注 Intent 本身的作用。从上面的分析中发现，可以将其看作是多进程通信中的消息载体，而其源码定义也能看出 Intent
本身是可以可以序列化并在进程间传递的结构。

    
    
    public class Intent implements Parcelable, Cloneable { ... }

`Intent`
本身有很多方法和属性，这里暂时先不展开，后面介绍具体漏洞的时候再进行针对性的分析。后文主要以四大组件为着手点，分别介绍一些常见的漏洞模式和设计陷阱。

# Activity

[Activity](https://developer.android.com/reference/android/app/Activity)
也称为活动窗口，是与用户直接交互的图形界面。APP 主要开发工作之一就是设计各个 activity，并规划他们之间的跳转和连结。通常一个 activity
表示一个全屏的活动窗口，但也可以有其他的存在形式，比如浮动窗口、多窗口等。作为 UI 窗口，一般使用 XML 文件进行布局，并继承 Activity
类实现其生命周期函数 `onCreate` 和 `onPause` 等生命周期方法。

如果开发者定义的 Activity 想通过 `Context.startActivity` 启动的话，就必须将其声明到 APP 的 manifest
文件中，即
[AndroidManifest.xml](https://developer.android.com/guide/topics/manifest/manifest-intro)。应用被安装时，`PackageManager` 会解析其 manifest 文件中的相关信息并将其注册到系统中，以便在 `resolve`
时进行搜索。

在 adb shell 中可以通过 `am start-activity` 去打开指定的 Activity，通过指定 Intent 去进行启动：

    
    
    am start-activity [-D] [-N] [-W] [-P <FILE>] [--start-profiler <FILE>]
            [--sampling INTERVAL] [--streaming] [-R COUNT] [-S]
            [--track-allocation] [--user <USER_ID> | current] <INTENT>

作为用户界面的载体，Activity
承载了许多用户输入/处理、以及外部数据接收/展示等工作，因此是应用对外的一个主要攻击面。下面就介绍几种较为常见的攻击场景。

## 生命周期

Activity 经典的生命周期图示如下：

![Activity Lifecycle](https://img-blog.csdnimg.cn/4d4375cd5428408e90a79a8aac43fc86.png)

通常开发者只需要实现 `onCreate` 方法，但是对于一些复杂的业务场景，正确理解其生命周期也是很必要的。以笔者在内测中遇到的某应用为例，其中某个
Activity 中执行了一些敏感的操作，比如开启摄像头推流，或者开启了录音，但只在 `onDestroy` 中进行了推流/录音的关闭。这样会导致在 APP
进入后台时候，这些操作依然在后台运行，攻击者可以构造任务栈使得受害者在面对恶意应用的钓鱼界面时候仍然执行目标应用的后台功能，从而形成特殊的钓鱼场景。正确的做法应该是在
`onPaused` 回调中对敏感操作进行关闭。

攻击者实际可以通过连续发送不同的 Intent 去精确控制目标 Activity
生命周期回调函数的触发时机，如果开发时没有注意也会造成应用功能的状态机异常甚至是安全问题。

## Implicit Exported

前面说过，开发者定义的 Activity 要想使用 `startActivity` 去启动，就必须在 AndroidManifest.xml 中使用
`<activity>` 进行声明，一个声明的示例如下：

    
    
    <activity xmlns:android="http://schemas.android.com/apk/res/android" android:theme="@android:01030055" android:name="com.evilpan.RouterActivity">
      <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data android:scheme="demo" android:host="router"/>
      </intent-filter>
    </activity>

[activity](https://developer.android.com/guide/topics/manifest/activity-element) 中支持许多属性。其中一个重要的属性就是 `android:exported`，表示当前 Activity 是否可以被 **其他应用**
的组件启动。该属性有几个特点：

  1. 属性可以缺省，缺省值默认为 `false`；
  2. 如果 Activity 没有显式设置该属性，且该 Activity 中定义了 `<intent-filter>`，那么缺省值就默认为 `true`；

也就是说，开发者可能没有显式指定 Activity 导出，但由于指定了 `intent-filter`，因此实际上也是导出的，即可以被其他应用唤起对应的
Activity。这种情况在早期很常见，比如 APP
设计了一组更换密码的界面，需要先输入旧密码然后再跳转到输入新密码的界面，如果后者是导出的，攻击者就可以直接唤起输入新密码的界面，从而绕过了旧密码的校验逻辑。

Google 已经深刻意识到了这个问题，因此规定在 Android 12 之后，如果应用的 Activity 中包含 intent-filter，就必须要显式指定 `android:exported` 为 true 或者 false，不允许缺省。在 Android 12 中未显式指定
exported 属性且带有 intent-filter 的 Activity 的应用在安装时候会直接被 PackageManager 拒绝。

## Fragment Injection

Activity 作为 UI 核心组件，同时也支持模块化的开发，比如在同一个界面中展示若干个可复用的子界面。随着这种设计思路诞生的就是
[Fragments](https://developer.android.com/guide/components/fragments) 组件，即
“片段”。使用 `FragmentActivity` 可以在一个 Activity 中组合一个或者多个片段，方便进行代码复用，片段的生命周期受到宿主
Activity 的影响。

Fragment Injection 漏洞最早在 2013 年爆出，这里只介绍其原理，本节末尾附有原始的文章以及论文。漏洞的核心是系统提供的
`PreferenceActivity` 类，开发者可以对其进行继承实现方便的设置功能，该类的 onCreate 函数有下面的功能：

    
    
    protected void onCreate() {
        // ...
        String initialFragment = getIntent().getStringExtra(EXTRA_SHOW_FRAGMENT);
        Bundle initialArguments = getIntent().getBundleExtra(EXTRA_SHOW_FRAGMENT_ARGUMENTS);
        // ...
        if (initialFragment != null) {
            switchToHeader(initialFragment, initialArguments);
        }
    }
    
    private void switchToHeaderInner(String fragmentName, Bundle args) {
        getFragmentManager().popBackStack(BACK_STACK_PREFS,
                FragmentManager.POP_BACK_STACK_INCLUSIVE);
        if (!isValidFragment(fragmentName)) {
            throw new IllegalArgumentException("Invalid fragment for this activity: "
                    + fragmentName);
        }
    
        Fragment f = Fragment.instantiate(this, fragmentName, args);
    }

可以看到从 Intent 中获取了一个字符串和一个 Bundle 参数，并最终传入 `switchToHeaderInner` 中，用于实例化具体的
`Fragment`。实例化的过程如下：

    
    
    public static Fragment instantiate(Context context, String fname, Bundle args) {
        // ...
        Class clazz = sClassMap.get(fname);
        if (clazz == null) {
                // Class not found in the cache, see if it's real, and try to add it
                clazz = context.getClassLoader().loadClass(fname);
                sClassMap.put(fname, clazz);
        }
        Fragment f = (Fragment)clazz.newInstance();
        if (args != null) {
                args.setClassLoader(f.getClass().getClassLoader());
                f.mArguments = args;
        }
        return f;
    }

经典的反射调用，将传入的字符串实例化为 Java
类，并设置其参数。这是什么，这就是反序列化啊！而实际的漏洞也正是出自这里，由于传入的参数攻击者可控，那么攻击者可以将其设置为某个内部类，从而触及开发者预期之外的功能。在原始的报告中，作者使用了
Settings 应用中的某个设置 PIN 密码的 Fragment 作为目标传入，这是个私有片段，从而导致了越权修改 PIN
码的功能。在当时的其他用户应用中，还有许多也使用了
PreferenceActivity，因此漏洞影响广泛，而且造成的利用根据应用本身的功能而异（也就是看有没有好用的 Gadget）。

注意上面的代码摘自最新的 Android 13，其中 `switchToHeaderInner` 方法加入了 `isValidFragment`
的判断，这正是 Android 当初的修复方案之一，即强制要求 PreferenceActivity
的子类实现该方法，不然就在运行时抛出异常。不过即便如此，还是有很多开发者为了图方便直接继承然后返回 `true` 的。

Fragment Injection 看似是 PreferenceActivity
的问题，但其核心还是对于不可信输入的校验不完善，在后文的例子中我们会多次看到类似的漏洞模式。

参考文章：

  * [A New Vulnerability in the Android Framework: Fragment Injection](https://securityintelligence.com/new-vulnerability-android-framework-fragment-injection/)
  * [ANDROID COLLAPSES INTO FRAGMENTS.pdf (wp)](https://securityintelligence.com/wp-content/uploads/2013/12/android-collapses-into-fragments.pdf)
  * [Understanding fragment injection](https://www.synopsys.com/blogs/software-security/fragment-injection/)
  * [How to fix Fragment Injection vulnerability](https://support.google.com/faqs/answer/7188427?hl=en)

## 点击劫持

Activity 既然作为 UI 的主要载体，那么与用户的交互也是其中关键的一项功能。在传统 Web
安全中就已经有过点击劫持的方法，即将目标网站想要让受害者点击的案件放在指定位置（如iframe），并在宿主中使用相关组件对目标进行覆盖和引导，令受害者在不知不觉中执行了敏感操作，比如点赞投币收藏一键离职等。

Android 中也出现过类似的攻击手段，比如在系统的敏感弹窗前面覆盖攻击者自定义的
TextView，引导受害者确认某些有害操作。当然这需要攻击者的应用拥有浮窗权限（`SYSTEM_ALERT_WINDOW`），在较新的 Android
系统中，该权限的申请需要用户多次的确认。

近两年中在 AOSP 中也出现过一些点击劫持漏洞，包括但不限于：

  * CVE-2020-0306：蓝牙发现请求确认框覆盖
  * CVE-2020-0394：蓝牙配对对话框覆盖
  * CVE-2020-0015：证书安装对话框覆盖
  * CVE-2021-0314：卸载确认对话框覆盖
  * CVE-2021-0487：日历调试对话框覆盖
  * ...

对于系统应用而言，防御点击劫持的方法一般是通过使用 android.permission.HIDE_NON_SYSTEM_OVERLAY_WINDOWS
权限并在布局参数中指定 `SYSTEM_FLAG_HIDE_NON_SYSTEM_OVERLAY_WINDOWS` 来防止 UI 被覆盖。

而对于普通应用，没法申请 HIDE_NON_SYSTEM_OVERLAY_WINDOWS 权限，防御措施一般有两种，一是通过将布局的
`filterTouchesWhenObscured` 设置为 `true` 来禁止窗体被覆盖后的输入事件；二是重载
View.onFilterTouchEventForSecurity 方法，并在其中检测其他应用的覆盖情况。在 Android 12 中系统已经默认开启了
filterTouchesWhenObscured 属性，这也是 security by default 的一种经典实现。

> 关于点击劫持的操作细节和缓解方案，可以参考 OPPO 安全实验室的这篇文章：
> [《不可忽视的威胁：Android中的点击劫持攻击》](https://mp.weixin.qq.com/s?__biz=MzUyNzc4Mzk3MQ==&mid=2247487493&idx=1&sn=c5be070f204b919747a0865156d7caf9&chksm=fa7b1149cd0c985ff69bbbfa4901e026c1db38c32219ba9b777f8a0b163b9b6e3ec9b181bd87&scene=178&cur_album_id=1420861949369303041#rd)

另外一个与点击劫持类似的漏洞称为 StrandHogg，细节可以参考下述的原始文章。其关键点是使用了 Activity 的
`allowTaskReparenting` 和 `taskAffinity` 属性，将其任务栈伪装成目标应用，这样在打开目标应用时由于 TaskStack
后进先出的特性会导致用户看到的是攻击者的应用，从而造成应用的钓鱼场景。

后来还是同一个安全团队有提出了 **StrandHogg 2.0** 版本，主要利用了 `ActivityStarter` 中的 AUTOMERGE
特性。假设有 A、B 两个应用，在 A1 中调用 `startActivites(B1, A2, B2)` 之后，任务栈会从 (A1, B1) 以及
(A2, B2) 合并为 (A1, B1, A2, B2)，也就是在同一个任务栈中覆盖了其他应用的
Activity，从而导致钓鱼场景。不过这个漏洞比较特化，因此谷歌很早就已经修复了，详情可以阅读下面的参考文章：

  * [The StrandHogg vulnerability](https://promon.co/security-news/the-strandhogg-vulnerability/)
  * [StrandHogg 2.0 – New serious Android vulnerability](https://promon.co/resources/downloads/strandhogg-2-0-new-serious-android-vulnerability/)
  * [StrandHogg 2.0 (CVE-2020-0096) 修复方案](https://android.googlesource.com/platform/frameworks/base/+/a952197bd161ac0e03abc6acb5f48e4ec2a56e9d)

## Intent Redirection

Intent Redirection，顾名思义就是将用户传入的不可信输入进行了转发，类似于服务端的 SSRF 漏洞。一个典型漏洞例子如下：

    
    
    protected void onCreate (Bundle savedInstanceState) {
       Intent target = (Intent) getIntent().getParcelableExtra("target");
       startActivity(target);
    }

将用户传入的 target `Parcelable` 直接转换成了 `Intent` 对象，并将这个对象作为 `startActivity`
的参数进行调用。就这个例子而言，可能造成的危害就是攻击者可以用任意构造的 Intent 数据去启动目标 APP
中的任意应用，哪怕是未导出的私有应用。而目标未导出的应用中可能进一步解析了攻击者提供的 Intent 中的参数，去造成进一步的危害，比如在内置
Webview 中执行任意 Javascript 代码，或者下载保存文件等。

实际上 Intent Redirection 除了可能用来启动私有 Activity 组件，还可以用于其他的的接口，包括：

  * [startActivity](https://developer.android.com/reference/android/app/Activity#startActivity\(android.content.Intent\))
  * [startService](https://developer.android.com/reference/android/content/Context#startService\(android.content.Intent\))
  * [sendBroadcast](https://developer.android.com/reference/android/content/Context#sendBroadcast\(android.content.Intent\))
  * [setResult](https://developer.android.com/reference/android/app/Activity#setResult\(int,%20android.content.Intent\))

> 注：每种方法可能还有若干衍生方法，比如 startActivityForResult

前面三个可能比较好理解，分别是启动界面、启动服务和发送广播。最后一个 `setResult` 可能会在排查的时候忽略，这主要用来给当前 Activity
的调用者返回额外数据，主要用于 `startActivityForResult` 的场景，这同样也可能将用户的不可信数据污染到调用者处。

从防御的角度上来说，建议不要直接把外部传入的 Intent 作为参数发送到上述四个接口中，如果一定要这么做的话，需要事先进行充分的过滤和安全校验，比如：

  1. 将组件本身的 `android:exported` 设置为 `false`，但这只是防止了用户主动发送的数据，无法拦截通过 `setResult` 返回的数据；
  2. 确保获取到的 `Intent` 来自于可信的应用，比如在组件上下文中调用 `getCallingActivity().getPackageName().equals("trust.app")`，但注意恶意的应用可以通过构造数据令 `getCallingActivity` 返回 `null`；
  3. 确保待转发的 `Intent` 没有有害行为，比如 component 不指向自身的非导出组件，不带有 `FLAG_GRANT_READ_URI_PERMISSION` 等（详见后文 ContentProvider 漏洞）；
  4. ...

但事实证明，即便是 Google 自己，也未必能够确保完善的校验。无恒实验室近期提交的高危漏洞 `CVE-2022-20223` 就是个很典型的例子：

    
    
    private void assertSafeToStartCustomActivity(Intent intent) {
        // Activity can be started if it belongs to the same app
        if (intent.getPackage() != null && intent.getPackage().equals(packageName)) {
            return;
        }
        // Activity can be started if intent resolves to multiple activities
        List<ResolveInfo> resolveInfos = AppRestrictionsFragment.this.mPackageManager
                .queryIntentActivities(intent, 0 /* no flags */);
        if (resolveInfos.size() != 1) {
            return;
        }
        // Prevent potential privilege escalation
        ActivityInfo activityInfo = resolveInfos.get(0).activityInfo;
        if (!packageName.equals(activityInfo.packageName)) {
            throw new SecurityException("Application " + packageName
                    + " is not allowed to start activity " + intent);
        }
    }

其中使用了 `ActivityInfo.packageName` 来判断启动目标的包名是否与当前 caller 的包名一致，可事实上显式 Intent
是通过 componentName 去指定启动目标，优先级高于 `Intent.packageName`
且后者可以被伪造，这就造成了检查的绕过。上述短短几行代码中其实还有另外一个漏洞，感兴趣的可以参考下面的参考链接。

因此，遇到潜在的 Intent 重定向问题时，可以多花点时间仔细审查，说不定就能够找到一个可利用的场景。

  * [Remediation for Intent Redirection Vulnerability](https://support.google.com/faqs/answer/9267555?hl=en)
  * [AOSP Bug Hunting with appshark (1): Intent Redirection](https://mp.weixin.qq.com/s/CY2nLUb2VQaBNxAKd7GeUQ)

# Service

[Service](https://developer.android.com/guide/components/services)
的主要功能有两个，一是给 APP 提供一个后台的长时间运行环境，二是对外提供自身的服务。与 Activity 的定义类似，Service 必须要在
manifest 中进行声明才能使用。注意 Service 中的代码也是和 Activity 一样运行在主线程的，并且默认和应用处于进程。

根据 Service 的两大主要功能区分，启动 Service 也有对应的两种形式：

  1. `Context.startService()`：启动后台服务并让系统进行调度；
  2. `Context.bindService()`：让（外部）应用绑定服务，并使用其提供的接口，可以理解为 RPC 的服务端；

两种方式启动服务的生命周期图示如下：

![Service Lifecycle](https://img-blog.csdnimg.cn/15dcb0cba60e45f1a138f58a50e2e98d.png)

蓝色部分都是在客户端去进行调用，系统收到请求后会启动对应的服务，如果对应的进程没有启动也会通知 zygote
去启动。不管是哪种方法创建服务，系统都会为其调用 `onCreate` 和 `onDestroy` 方法。整体流程和 Activity
的启动流程类似，这里不再赘述。

shell 中同样提供了 `start-activity` 命令来方便启动服务：

    
    
    am start-service [--user <USER_ID> | current] <INTENT>

下面来介绍一些 Service 组件相关的漏洞。

## 生命周期

前面介绍了 Service 启动的生命周期，总体和 Activity 流程差不多，但需要注意有几点不同：

  1. 与 Activity 生命周期回调方法不同， **不需要** 调用 Serivce 回调方法的超类实现，比如 onCreate、onDestory 等；
  2. `Service` 类的直接子类运行在主线程中，同时处理多个阻塞的请求时候一般需要在新建线程中执行；
  3. `IntentService` 是 Service 的子类，被设计用于运行在 Worker 线程中，可以串行处理多个阻塞的 Intent 请求；API-30 以后被标记为废弃接口，建议使用 WorkManager 或者 JobIntentService 去实现；
  4. 客户端通过 `stopSelf` 或者 `stopService` 来停止绑定服务，但服务端并没有对应的 `onStop` 回调，只有在销毁前收到 `onDestory`；
  5. 前台服务必须为状态栏提供通知，让用于意识到服务正在运行；

对于[绑定服务](https://developer.android.com/guide/components/bound-services)而言，Android 系统会根据绑定的客户端引用计数来自动销毁服务，但如果服务实现了 `onStartCommand()`
回调，就必须显式地停止服务，因为系统会将其视为已启动的状态。此外，如果服务允许客户端再次绑定，就需要实现 onUnbind 方法并返回
true，这样客户端在下次绑定时候会接收到同样的 IBinder，示例图如下所示：

![Rebind](https://img-blog.csdnimg.cn/fdff87e1b2f14aa6a34e60fb1c8556ee.png)

服务的声明周期相比于 Activity 更加复杂，因为涉及到进程间的绑定关系，因此也就更可能在不了解的情况下编写出不健壮甚至有问题的代码。

## Implicit Export

和 Activity 一样，Service 也要在 manifest 中使用
[service](https://developer.android.com/guide/topics/manifest/service-element)
去声明，也有 `android:exported` 属性。甚至关于该属性的默认值定义也是一样的，即默认是 `false`，但包含 intent-filter
时，默认就是 `true`。同样，在 Android 12 及以后也强制性要求必须显式指定服务的导出属性。

## 服务劫持

与 Activity 不同的是，Android 不建议使用隐式 Intent 去启动服务。因为服务在后台运行，没有可见的图形界面，因此用户看不到隐式
Intent 启动了哪个服务，且发送者也不知道 Intent 会被谁接收。

服务劫持是一个典型的漏洞，攻击者可以为自己的 Service 声明与目标相同的 intent-filter
并设定更高的优先级，这样可以截获到本应发往目标服务的 Intent，如果带有敏感信息的话还会造成数据泄露。

而在 `bindService` 中这种情况的危害则更加严重，攻击者可以伪装成目标 IPC 服务去返回错误甚至是有害的数据。因此，在 Android 5.0
（API-21）开始，使用隐式 Intent 去调用 bindService 会直接抛出异常。

如果待审计的目标应用在 Service 中提供了 `intent-filter`，那么就需要对其进行重点排查。

## AIDL

绑定服务可以被用来用作 IPC 服务端，如果服务端绑定的时候返回了 AIDL 接口的实例，那么就意味着客户端可以调用该接口的任意方法。一个实际案例是
Tiktok 的 `IndependentProcessDownloadService`，在 `DownloadService` 的 onBind
中返回了上述 AIDL 接口的实例：

_com/ss/android/socialbase/downloader/downloader/DownloadService.java_ :

    
    
    if (this.downloadServiceHandler != null) {
        return this.downloadServiceHandler.onBind(intent);
    }

而其中有个 `tryDownload` 方法可以指定 url 和文件路径将文件下载并保存到本地。虽然攻击者没有 AIDL
文件，但还是可以通过反射去构造出合法的请求去进行调用，PoC 中关键的代码如下：

    
    
    private ServiceConnection mServiceConnection = new ServiceConnection() {
        public void onServiceConnected(ComponentName cName, IBinder service) {
            processBinder(service);
        }
    
        public void onServiceDisconnected(ComponentName cName) { }
    };
    
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    
        Intent intent = new Intent("com.ss.android.socialbase.downloader.remote");
        intent.setClassName(
            "com.zhiliaoapp.musically",
            "com.ss.android.socialbase.downloader.downloader.IndependentProcessDownloadService");
        bindService(intent, mServiceConnection, BIND_AUTO_CREATE);
    }
    
    private void processBinder(IBinder binder) {
        ClassLoader cl = getForeignClassLoader(this, "com.zhiliaoapp.musically");
        Object handler = cl.loadClass("com.ss.android.socialbase.downloader.downloader.i$a")
                .getMethod("asInterface", IBinder.class)
                .invoke(null, binder);
    
        Object payload = getBinder(cl);
    
        cl.loadClass("com.ss.android.socialbase.downloader.downloader.i")
                .getMethod("tryDownload", cl.loadClass("com.ss.android.socialbase.downloader.model.a"))
                .invoke(handler, payload);
    }
    
    private Object getBinder(ClassLoader cl) throws Throwable {
        Class utilsClass = cl.loadClass("com.ss.android.socialbase.downloader.utils.g");
        Class taskClass = cl.loadClass("com.ss.android.socialbase.downloader.model.DownloadTask");
        return utilsClass.getDeclaredMethod("convertDownloadTaskToAidl", taskClass)
                .invoke(null, getDownloadTask(taskClass, cl));
    }

关键在于使用 `Context.getForeignClassLoader` 获取其他应用的 ClassLoader。

> 漏洞细节参考： [vulnerabilities in the TikTok Android
> app](https://blog.oversecured.com/Oversecured-detects-dangerous-> vulnerabilities-in-the-TikTok-Android-app/#vulnerability-via-> independentprocessdownloadservice-aidl-interface)

## Intent Redirect

这个其实和 Activity 中的对应漏洞类似，客户端启动/绑定 Service 的时候也指定了隐式或者显式的
Intent，其中的不可信数据如果被服务端用来作为启动其他组件的参数，就有可能造成一样的 Intent 重定向问题。注意除了 `getIntent()`
之外还有其他数据来源，比如服务中实现的 `onHandleIntent` 的参数。

其实最早提出 Intent 重定向危害的 "LaunchAnywhere" 漏洞就是出自系统服务，准确来说是 `AccountManagerService`
的漏洞。AccountManager 正常的执行流程为：

  1. 普通应用（记为 A）去请求添加某类账户，调用 AccountManager.addAccount；
  2. AccountManager 会去查找提供账号的应用（记为 B）的 Authenticator 类；
  3. AccountManager 调用 B 的 Authenticator.addAccount 方法；
  4. AccountManager 根据 B 返回的 Intent 去调起 B 的账户登录界面（AccountManagerResponse.getParcelable）；

在第 4 步时，系统认为 B 返回的数据是指向 B 的登陆界面的，但实际上 B 可以令其指向其他组件，甚至是系统组件，就造成了一个 Intent
重定向的漏洞。这里 Intent 的来源比较曲折，但本质还是攻击者可控的。

关于该漏洞的细节和利用过程可参考：[launchAnyWhere: Activity组件权限绕过漏洞解析(Google Bug 7699048
)](http://retme.net/index.php/2014/08/20/launchAnyWhere.html)

# Receiver

[Broadcast
Receiver](https://developer.android.com/guide/components/broadcasts)，简称
receiver，即广播接收器。前面介绍的 Activity 和 Service
之间的联动都是一对一的，而很多情况下我们可能想要一对多或者多对多的通信方案，广播就承担了这个功能。比如，Android
系统本身就会在发生各种事件的时候发送广播通知所有感兴趣的应用，比如开启飞行模式、网络状态变化、电量不足等等。这是一种典型的发布/订阅的设计模式，广播数据的载体也同样是
`Intent`。

与前面 Activity 与 Service 不同的是，Receiver 可以在 manifest
中进行声明注册，称为静态注册；也可以在应用运行过程中进行动态注册。但无论如何，定义的广播接收器都要继承自
[BroadcastReceiver](https://developer.android.com/reference/android/content/BroadcastReceiver)
并实现其声明周期方法 `onReceive(context, intent)`。

注意 BroadcastReceiver 的父类是 Object，不像 Activity 与 Service 是 Context，因此 onReceive
还会额外传入一个 context 对象。

shell 中发送广播的命令如下：

    
    
    am broadcast [--user <USER_ID> | all | current] <INTENT>

下面还是按顺序介绍一些常见的问题。

## Implicit Export

使用静态注册的 receiver 倒没什么特殊，示例如下：

    
    
    <receiver android:name=".MyBroadcastReceiver"  android:exported="true">
        <intent-filter>
            <action android:name="android.intent.action.BOOT_COMPLETED"/>
            <action android:name="android.intent.action.INPUT_METHOD_CHANGED" />
        </intent-filter>
    </receiver>

同样存在和之前一样的默认 export 问题，相信大家已经看腻了，就不再啰嗦了。接着看动态注册的情况，比如：

    
    
    BroadcastReceiver br = new MyBroadcastReceiver();
    IntentFilter filter = new IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION);
    filter.addAction(Intent.ACTION_AIRPLANE_MODE_CHANGED);
    this.registerReceiver(br, filter);

与清单中的定义相比，动态注册的方式可能更容易忽略导出权限的问题。上述代码片段动态注册了一个广播，但没有显式声明 exported
属性，因此默认是导出的。事实上使用 registerReceiver 似乎没有简单的方法去设置 `exported=false`，而 Google
官方的建议是对于不需要导出的广播接收器使用 `LocalBroadcastManager.registerReceiver` 进行注册，或者在注册的时候指定
permission 权限。

对于指定 permission 权限的情况，如果是自定义权限，需要在应用清单中声明，比如：

    
    
    <permission android:name="com.evilpan.MY_PERMISSION"
        android:protectionLevel="signature"/>
    <uses-permission android:name="com.evilpan.MY_PERMISSION" />

signature
表示只有在请求授权的应用使用与声明权限的应用相同的证书进行签名时系统才会授予的权限。如果证书匹配，则系统会在不通知用户或征得用户明确许可的情况下自动授予权限。详见
[protectionLevel](https://developer.android.com/reference/android/R.attr#protectionLevel)。

最后在动态注册时指定该权限即可：

    
    
    this.registerReceiver(br, filter, "com.evilpan.MY_PERMISSION", null);

注册未带有权限限制的导出广播接收器会导致接收到攻击者伪造的恶意数据，如果在 onReceive 时校验不当，可能会出现越权或者 Intent
重定向等漏洞，造成进一步的安全危害。

这类安全问题很多，比较典型的就有 Pwn2Own 上用于攻破三星 Galaxy S8 的 [PpmtReceiver
漏洞](https://paper.seebug.org/1050/)。

## 信息泄露

上面主要是从限制广播发送方的角度去设置权限，但其实这个权限也能限制广播的接收方，只不过发送消息的时候要进行额外的指定，比如要想只让拥有上述权限的接收方受到广播，则发送代码如下：

    
    
    Intent it = new Intent(this, ...);
    it.putExtra("secret", "chicken2beautiful")
    sendBroadcast(it, "com.evilpan.MY_PERMISSION");

如果不带第二个参数的话，默认是所有满足条件的接受方都能受到广播信息的。此时若是发送的 Intent 中带有敏感数据，就可能会造成信息泄露问题。

一个实际案例就是
[CVE-2018-9581](https://wwws.nightwatchcybersecurity.com/2018/11/11/cve-2018-9581/)，系统在广播
android.net.wifi.RSSI_CHANGED 时携带了敏感数据 RSSI，此广播能被所有应用接收，从而间接导致物理位置信息泄露。（搞笑？）

可见对于 Broadcast Receiver 而言，permission 标签的作用尤其明显。对于系统广播而言，比如
`BOOT_COMPLETED`，通常只有系统应用才有权限发送。这都是在 [framework 的
AndroidManifest.xml](https://android.googlesource.com/platform/frameworks/base/+/master/core/res/AndroidManifest.xml)
中进行定义的。

而对于应用的自定义广播，通常是使用上述自定义权限，那么也就自然想到一个问题，如果多个应用定义了同一个权限会怎么样？其实这是正是一个历史漏洞，在早期
Android 的策略是优先采用第一个定义的权限，但在 Andorid 5
之后就已经明确定义了两个应用不同定义相同的权限（除非他们的签名相同），否则后安装的应用会出现
`INSTALL_FAILED_DUPLICATE_PERMISSION` 错误警告。感兴趣的考古爱好者可以参考下面的相关文章：

  * [Vulnerabilities with Custom Permissions](https://github.com/commonsguy/cwac-security/blob/master/PERMS.md)
  * [Custom Permission Vulnerability and the 'L' Developer Preview](https://commonsware.com/blog/2014/08/04/custom-permission-vulnerability-l-developer-preview.html)

## Intent Redirection

原理不多说了，直接看案例吧。漏洞出在 Tiktok 的 `NotificationBroadcastReceiver` 中，定义了 intent-filter 导致组件默认被设置为导出，因此可以接收到外部应用的广播，而且又将广播中的不可信数据直接拿来启动 Activity，如下：

![NotificationBroadcastReceiver](https://img-blog.csdnimg.cn/92b6d5df24c84edabf24c182a48aa246.png)

> 漏洞细节可参考：[Oversecured detects dangerous vulnerabilities in the TikTok Android
> app](https://blog.oversecured.com/Oversecured-detects-dangerous-> vulnerabilities-in-the-TikTok-Android-app/)

# ContentProvider

[Content
Provider](https://developer.android.com/guide/topics/providers/content-providers)，即内容提供程序，简称为 Provider。Android 应用通常实现为 MVC 结构（Model-View-Controller），Model 部分即为数据来源，供自身的 View
即图形界面进行展示。但有时候应用会想要将自身的数据提供给其他数据使用，或者从其他应用中获取数据。

定义一个 ContentProvider 的方式，只需要继承自
[ContentProvider](https://developer.android.com/reference/android/content/ContentProvider)
类并实现六个方法： `query`，`insert`， `update`， `delete`， `getType` 以及 `onCreate`。其中除了
onCreate 是系统在主线程调用的，其他方法都由客户端程序进行主动调用。自定义的 provider 必须在程序清单中进行声明，后文会详细介绍。

可以看到 Provider 主要实现了类似数据库的增删改查接口，从客户端来看，查询过程也和查询传统数据库类似，例如，下面是查询系统短信的代码片段：

    
    
    Cursor cursor = getContentResolver().query(
        Telephony.Sms.Inbox.CONTENT_URI,           // 指定要查询的表名
        new String[] { Telephony.Sms.Inbox.BODY }, // projection 指定索要查询的列名
        selectionClause,                           // 查询的过滤条件
        selectionArgs,                             // 查询过滤的参数 
        Telephony.Sms.Inbox.DEFAULT_SORT_ORDER);   // 返回结果的排序
    while (cursor.moveToNext()) {
        Log.i(TAG, "msg: " + cursor.getString(0));
    }

其中 `ContentResolver` 是 `ContentInterface` 子类，后者是 ContentProvider
的客户端远程接口，可以实现其透明的远程代理调用。 `content_uri` 可以看作是查询的表名，`projection` 可以看作是列名，返回的
cursor 是查询结果行的迭代器。

与前面三个组件不同，在 shell 中访问 provider 组件的工具是 `content`。

下面来介绍 Provider 中常见的问题。

## Permissions

鉴于 provider
作为数据载体，那么安全访问与权限控制自然是重中之重。例如上面代码示例中访问短信的接口，如果所有人都能随意访问，那就明显会带来信息泄露问题。前面简单提到过，应用中定义的
Provider 必须要在其程序清单文件中进行声明，使用的是
[provider](https://developer.android.com/guide/topics/manifest/provider-element) 标签。其中有我们常见的 `exported` 属性，表示是否可被外部访问，`permission`
属性则表示访问所需的权限，当然也可以分别对读写使用不同的权限，比如 `readPermission`/`writePermission` 属性。

比如，前文提到的短信数据库声明如下：

    
    
    <provider android:name="SmsProvider"
        android:authorities="sms"
        android:multiprocess="false"
        android:exported="true"
        android:singleUser="true"
        android:readPermission="android.permission.READ_SMS" />

其他应用若想访问，则需在清单文件中声明请求对应权限。

    
    
    <uses-permission android:name="android.permission.READ_SMS" />

这都很好理解，其他组件也有类似的特性。除此之外，Provider 本身还提供了更为细粒度的权限控制，即
[grantUriPermissions](https://developer.android.com/guide/topics/manifest/provider-element#gprmsn)。这是一个布尔值，表示是否允许临时为客户端授予该 provider 的访问权限。临时授予权限的运行流程一般如下：

  1. 客户端给 Provider 所在应用发送一个 Intent，指定想要访问的 Content URI，比如使用 `startActivityForResult` 发送；
  2. 应用收到 Intent 后，判断是否授权，如果确认则准备一个 Intent，并设置好 flags 标志位 `FLAG_GRANT_[READ|WRITE]_URL_PERMISSION`，表示允许读/写对应的 Content URI（可以不和请求的 URI 一致），最后使用 `setResult(code, intent)` 返回给客户端；
  3. 客户端的 onActivityResult 收到返回的 Intent，使用其中的 URI 来临时对目标 Provider 进行访问；

以读为例，`Intent.flags` 中如果包含
[FLAG_GRANT_READ_URI_PERMISSION](https://developer.android.com/reference/android/content/Intent.html#FLAG_GRANT_READ_URI_PERMISSION)，那么该
Intent 的 **接收方** （即客户端）会被授予 `Intent.data` 部分 URI
的临时读取权限，直至接收方的生命周期结束。另外，Provider 应用也可以主动调用 `Context.grantUriPermission`
方法来授予目标应用对应权限：

    
    
    public abstract void grantUriPermission (String toPackage, 
                    Uri uri, 
                    int modeFlags)
    public abstract void revokeUriPermission (String toPackage, 
                    Uri uri, 
                    int modeFlags)

grantUriPermissions 属性可以在 URI 粒度对权限进行读写控制，但有一个需要注意的点：通过 grantUriPermissions
临时授予的权限，会 **无视 readPermission、writePermission、permission 和 exported 属性施加的限制**
。也就是说，即便 `exported=false`，客户端也没有申请对应的 `uses-permission`，可一旦被授予权限，依然可以访问对应的
Content Provider！

另外，`<provider>` 还有一个子标签 [grant-uri-permission](https://developer.android.com/guide/topics/manifest/grant-uri-permission-element)，即便 grantUriPermissions 被设置为 `false`，通过临时获取权限依然可以访问该标签下定义的
URI 子集，该子集可以用前缀或者通配符去指定 URI 的可授权路径范围。

Provider 权限设置不当可能会导致应用数据被预期之外的恶意程序访问，轻则导致信息泄露，重则会使得自身沙盒数据被覆盖而导致
RCE，后文会看到多个这样的案例。

## FileProvider

前面说过自定义 Provider 需要实现六个方法，但 Android 中已经针对某些常用场景的 Provider
编写好了对应的子类，用户可根据需要继承这些子类并实现少部分子类方法即可。其中一个常用场景就是用 ContentProvider 分享应用的文件，系统提供了
`FileProvider` 来方便应用自定义文件分享和访问，但是使用不当的话很可能会出现任意文件读写的问题。

[FileProvider](https://developer.android.com/reference/androidx/core/content/FileProvider)
提供了使用 XML 去指定文件访问控制的功能，一般 Provider 应用只需继承 FileProvider 类：

    
    
    public class MyFileProvider extends FileProvider {
       public MyFileProvider() {
           super(R.xml.file_paths)
       }
    }

`file_paths` 是用户自定义的 XML，也可以在清单文件中使用 `meta-data` 去指定：

    
    
    <provider xmlns:android="http://schemas.android.com/apk/res/android" android:name="com.evilpan.MyFileProvider" android:exported="false" android:authorities="com.evilpan.fileprovider" android:grantUriPermissions="true">
      <meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@7F15000E"/>
    </provider>

`resource` 指向 `res/xml/file_paths.xml`。该文件中定义了可供访问的文件路径，FileProvider
只会对提前指定的文件生成 Content URI。一个文件路径配置示例如下：

    
    
    <paths>
      <root-path name="root" path=""/>
      <files-path name="internal_files" path="."/>
      <cache-path name="cache" path=""/>
      <external-path name="external_files" path="images"/>
    </paths>

`paths` 标签支持多种类型的子标签，分别对应不同目录的子路径：

  * `files-path`: Context.getFilesDir()
  * `cache-path`: Context.getCacheDir()
  * `external-path`: Environment.getExternalStorageDirectory()
  * `external-files-path`: Context.getExternalFilesDir()
  * `external-cache-path`: Context.getExternalCacheDir()
  * `external-media-path`: Context.getExternalMediaDirs()[0]

比较特殊的是 `root-path`，表示 **系统** 的根目录 `/`。FileProvider 生成的 URI 格式一般是
`content://authority/{name}/{path}`，比如对于上述 Provider，可用
`content://com.evilpan.fileprovider/root/proc/self/maps` 来访问 `/proc/self/maps`
文件。

由此可见，FileProvider 指定 `root-path` 是一个危险的标志，一旦攻击者获得了临时权限，就可以读取所有应用的私有数据。

比如，TikTok 历史上就有过这么一个真实的漏洞：

    
    
    <provider android:name="android.support.v4.content.FileProvider" android:exported="false" android:authorities="com.zhiliaoapp.musically.fileprovider" android:grantUriPermissions="true">
            <meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@xml/k86"/>
        </provider>

这里直接使用了 `FileProvider`，甚至都不需要继承。 _xml/k86.xml_ 文件内容如下：

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <paths xmlns:amazon="http://schemas.amazon.com/apk/res/android" xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto">
        <root-path name="name" path=""/>
        <external-path name="share_path0" path="share/"/>
        <external-path name="download_path2" path="Download/"/>
        <cache-path name="gif" path="gif/"/>
        ...
    </paths>

获取临时权限之后就可以实现应用的任意文件读写。

## The Hidden ...

在 ContentProvider 类中，除了前面说过的 6 个必须实现的方法，还有一些其他隐藏的方法，一般使用默认实现，也可以被子类覆盖实现，比如

  * openFile
  * openFileHelper
  * call
  * ...

这些隐藏的方法可能在不经意间造成安全问题，本节会通过一些案例去分析其中的原因。

### openFile

如果 ContentProvider 想要实现共享文件读写的功能，还可以通过覆盖 `openFile` 方法去实现，该方法的默认实现会抛出
`FileNotFoundException` 异常。

虽然开发者实现上不太会直接就返回打开的本地文件，而是有选择地返回某些子目录文件。但是如果代码写得不严谨，就可能会出现路径穿越等问题，一个经典的漏洞实现如下：

    
    
     @Override
    public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        File file = new File(getContext().getFilesDir(), uri.getPath());
        if(file.exists()){
            return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY);
        }
        throw new FileNotFoundException(uri.getPath());
    }

另外一个同族的类似方法是 `openAssetFile`，其默认实现是调用 openFile：

    
    
    public @Nullable AssetFileDescriptor openAssetFile(@NonNull Uri uri, @NonNull String mode)
            throws FileNotFoundException {
        ParcelFileDescriptor fd = openFile(uri, mode);
        return fd != null ? new AssetFileDescriptor(fd, 0, -1) : null;
    }

有时候开发者虽然知道要要防御路径穿越，但防御的姿势不对，也存在被绕过的可能，比如：

    
    
    public ParcelFileDescriptor openFile(Uri uri, String mode) {
        File f = new File(DIR, uri.getLastPathSegment());
        return ParcelFileDescriptor.open(f, ParcelFileDescriptor.MODE_READ_ONLY);
    }

这里想用 `getLastPathSegment` 去只获取最后一级的文件名，但实际上可以被 URL encode 的路径绕过，比如
`%2F..%2F..path%2Fto%2Fsecret.txt` 会返回 `/../../path/to/secret.txt`。

还有一种错误的防御是使用 `UriMatcher.match` 方法去查找 `../`，这也会被 URL 编码绕过。正确的防御和过滤方式如下：

    
    
    public ParcelFileDescriptor openFile (Uri uri, String mode) throws FileNotFoundException {
      File f = new File(DIR, uri.getLastPathSegment());
      if (!f.getCanonicalPath().startsWith(DIR)) {
        throw new IllegalArgumentException();
      }
      return ParcelFileDescriptor.open(f, ParcelFileDescriptor.MODE_READ_ONLY);
    }

> 详见：[Path Traversal
> Vulnerability](https://support.google.com/faqs/answer/7496913?hl=en)

### openFileHelper

ContentProvider 中还有一个鲜为人知的 `openFileHelper` 方法，其默认实现是使用当前 Provider 中的 `_data`
列数据去打开文件，源码如下：

    
    
    protected final @NonNull ParcelFileDescriptor openFileHelper(@NonNull Uri uri,
            @NonNull String mode) throws FileNotFoundException {
        Cursor c = query(uri, new String[]{"_data"}, null, null, null);
        int count = (c != null) ? c.getCount() : 0;
        if (count != 1) {
            // If there is not exactly one result, throw an appropriate
            // exception.
            if (c != null) {
                c.close();
            }
            if (count == 0) {
                throw new FileNotFoundException("No entry for " + uri);
            }
            throw new FileNotFoundException("Multiple items at " + uri);
        }
    
        c.moveToFirst();
        int i = c.getColumnIndex("_data");
        String path = (i >= 0 ? c.getString(i) : null);
        c.close();
        if (path == null) {
            throw new FileNotFoundException("Column _data not found.");
        }
    
        int modeBits = ParcelFileDescriptor.parseMode(mode);
        return ParcelFileDescriptor.open(new File(path), modeBits);
    }

这个方法的主要作用是方便子类用于快速实现 `openFile` 方法，通常不会直接在子类去覆盖。不过由于其中基于 `_data`
列去打开文件的特性可能会攻击者插入恶意数据后间接地实现任意文件读写。

一个经典案例就是三星手机的 `SemClipboardProvider`，在插入时未校验用户数据：

    
    
    public Uri insert(Uri uri, ContentValues values) {
        long row = this.database.insert(TABLE_NAME, "", values);
        if (row > 0) {
            Uri newUri = ContentUris.withAppendedId(CONTENT_URI, row);
            getContext().getContentResolver().notifyChange(newUri, null);
            return newUri;
        }
        throw new SQLException("Fail to add a new record into " + uri);
    }

而该 Provider 又在 `system_server` 进程中，拥有极高的运行权限，攻击者通过利用这个漏洞去就能实现系统层面的任意文件读写，其 PoC
如下：

    
    
    ContentValues vals = new ContentValues();
    vals.put("_data", "/data/system/users/0/newFile.bin");
    URI semclipboard_uri = URI.parse("content://com.sec.android.semclipboardprovider")
    ContentResolver resolver = getContentResolver();
    URI newFile_uri = resolver.insert(semclipboard_uri, vals);
    return resolver.openFileDescriptor(newFile_uri, "w").getFd(); 

该漏洞与其他漏洞一起曾被用于在野攻击中，由 Google TAG 团队捕获，对这一条 Fullchain 的分析可以参考 Project Zero
近期的文章：[A Very Powerful Clipboard: Analysis of a Samsung in-the-wild exploit
chain](https://googleprojectzero.blogspot.com/2022/11/a-very-powerful-clipboard-samsung-in-the-wild-exploit-chain.html)

### call

ContentProvider 中提供了 `call` 方法，用于实现调用服务端定义方法，其函数签名如下：

    
    
    public Bundle call (String authority, 
                    String method, 
                    String arg, 
                    Bundle extras)
    public Bundle call (String method, 
                    String arg, 
                    Bundle extras)

默认的实现是个空函数直接返回 `null`，开发者可以通过覆盖该函数去实现一些动态方法，返回值也会传回到调用者中。

看起来和常规的 RPC 调用类似，但这里有个小陷阱，开发者文档中也特别标注了：Android 系统并没有对 `call` 函数进行权限检查，因为系统不知道在
call 之中对数据进行了读还是写，因此也就无法根据 Manifest 中定义的权限约束进行判断。因此要求开发者自己对 call 中的逻辑进行权限校验。

如果开发者实现了该方法，但是又未进行校验或者校验不充分，就可能出现越权调用的情况。一个案例是 `CVE-2021-23243`， OPPO 某系统应用中
`HostContentProviderBase` 的 call 方法实现中，直接用 DexClassLoader 去加载了传入 dex
文件，直接导致攻击者的代码在特权进程中运行，所有继承该基类的 Provider 都会受到影响 ()。

另外在某些系统 Provider 中，可以通过 call 方法去获取某些远程对象实例，例如在文章 [Android 中的特殊攻击面（三）—— 隐蔽的
call 函数](https://paper.seebug.org/1269/) 中，作者就通过 `SliceProvider` 与
`KeyguardSliceProvider` 获取到了系统应用内部的 PendingIntent 对象，进一步利用实现了伪造任意广播的功能。

# 其他

除了上述和四大组件直接相关的漏洞，Android 系统中还有许多不太好分类的漏洞，本节主要挑选其中几个最为常见的漏洞进行简单介绍。

## PendingIntent

[PendingIntent](https://developer.android.com/reference/android/app/PendingIntent)
是对 Intent 的表示，本身并不是 Intent 对象，但是是一个 Parcelable
对象。将该对象传递给其他应用后，其他应用就可以以发送方的身份去执行所指向的 Intent 指定的操作。 PendingIntent
使用下述静态方法之一进行创建：

  * getActivity(Context, int, Intent, int);
  * getActivities(Context, int, Intent[], int);
  * getBroadcast(Context, int, Intent, int);
  * getService(Context, int, Intent, int);

PendingIntent 本身只是系统对原始数据描述符的一个引用，可以大致将其理解为 `Intent 的指针`。也因为如此，即便创建
PendingIntent 的应用关闭后，其他应用仍然可以使用该数据。如果原始应用后来进行了重启并以同样的参数创建了一个
PendingIntent，那么实际上返回 PendingIntent 与之前创建的会指向同样的 token。注意判断 Intent 是否相同是使用
[filterEquals](https://developer.android.com/reference/android/content/Intent#filterEquals\(android.content.Intent\))
方法，其中会判断 action，data， type，identity，class，categories 是否相同，注意 `extra`
并不在此列，因此仅有 extra 不同的 Intent 也会被认为是相等的。

由于 PendingIntent 可代表其他应用的特性，在某些场景下可能被用于滥用。例如，如果开发者创建了这样一个默认的 PendingIntent
并传递给其他应用：

    
    
    pi = PendingIntent.getActivity(this, 0, new Intent(), 0);
    bundle.putParcelable("pi", pi)
    // send bundle

恶意的应用在收到此 PendingIntent 后，可以获取到原始的 intent，并使用 `Intent.fillin` 去填充空字段，如果原始
Intent 是上述空 Intent，那么攻击者就可以将其修改为特定的
Intent，从而以目标的身份去启动应用，包括未导出的私有应用。一个经典的案例就是早期的
[broadAnywhere](https://android.googlesource.com/platform/packages/apps/Settings/+/f5d3e74ecc2b973941d8adbe40c6b23094b5abb7%5E%21/#F0)
漏洞，Android Settings 应用中的 addAccount 方法内创建了一个 PendingIntent 广播，但 intent
内容为空，这导致收到 intent 的的恶意应用可以 fillin 填充广播的 action，从而实现越权发送系统广播，实现伪造短信、回复出厂设置等功能。

为了缓解这类问题，Andorid 中对 Intent.fillin 的改写做了诸多限制，比如已有的字段不能修改，component 和 selector
字段不能修改（除非额外设置 FILL_IN_COMPONENT/SELECTOR），隐式 Intent 的 action 不能修改等。

不过有研究者提出了针对隐式 Intent 的利用方法，即通过修改 flag 添加 FLAG_GRANT_WRITE_URI_PERMISSION，并修改
data 的 URI 指向受害者私有的 Provider，将 package 改为攻击者；同时攻击者在自身的 Activity 中声明相同的 intent
filter，这样在转发 intent 时会启动攻击者应用，同时也获取了目标私有 Provider
的访问权限，从而实现私有文件窃取或者覆盖。关于该攻击思路详情可以阅读下面的参考文章。

  * [broadAnywhere：Broadcast组件权限绕过漏洞（Bug: 17356824）](http://retme.net/index.php/2014/11/14/broadAnywhere-bug-17356824.html)
  * [PendingIntent重定向：一种针对安卓系统和流行App的通用提权方法——BlackHat EU 2021议题详解（上）](https://blog.csdn.net/weixin_59152315/article/details/123481053)
  * [PendingIntent重定向：一种针对安卓系统和流行App的通用提权方法——BlackHat EU 2021议题详解（下）](https://blog.csdn.net/weixin_59152315/article/details/123503289)

> 在 Android 12+ 之后，PendingIntent 在创建时候要求显式指定 `FLAG_MUTABLE` 或者
> `FLAG_IMMUTABLE`，表示是否可以修改。

## DeepLink

在大部分操作系统中都有 deeplink 的概念，即通过自定义 schema 打开特定的应用。比如通过点击 <https://evilpan.com/>
可以唤起默认浏览器打开目标网页，点击  会唤起拨号界面，点击  会唤起微信，等等。其他系统暂且不论，在 Android 中这主要是通过隐式 Intent
去实现的。

应用要想注册类似的自定义协议，需要在应用清单文件中进行声明：

    
    
    <intent-filter>
      <action android:name="android.intent.action.VIEW"/>
      <category android:name="android.intent.category.DEFAULT"/>
      <category android:name="android.intent.category.BROWSABLE"/>
    <data android:scheme="weixin" android:host="qr"/>
    </intent-filter>

由于这类隐式 Intent 可以直接通过点击链接去触发，因此更受攻击者喜爱。如果处理对应 Intent 的组件没有过滤好用户传入的内容，很可能会造成
1-click 的漏洞。相关案例可以参考文章：[Android
中的特殊攻击面（二）——危险的deeplink](https://mp.weixin.qq.com/s/81Lq-JwASnkSS2wg62HSvA)

## Webview

在 Andorid
系统中，[Webview](https://developer.android.com/reference/android/webkit/WebView)
主要用于应用在自身的 Activty 中展示网页内容，并提供了一些额外的接口来给开发者实现自定义的控制。更高的拓展性也就意味着更多出错的可能，尤其是如今
Android 客户端开发式微，Java 开发也朝着 “大前端” 的方向发展。原本许多使用原生应用实现的逻辑逐渐转移到了 web 页面中，比如
h5、小程序等，这样一来，webview 的攻击面也就扩宽了不少。

常规的 Webview 安全问题主要是在与一些配置的不安全，比如覆盖 `onReceivedSslError` 忽略 SSL
错误导致中间人攻击，`setAllowFileAccessFromFileURLs` 导致本地私有文件泄露等。但现在的漏洞更多出在 JSBridge
上，这是 Java 代码与网页中的 JavaScript 代码沟通的桥梁。

由于 Webview 或者说 JS 引擎的沙箱特性，网页中的 Javascript 代码本身无法执行许多原生应用才能执行的操作，比如无法从
Javascript 中发送广播，无法访问应用文件等。而由于业务的复杂性，很多逻辑又必须在 Java 层甚至是 Native 层才能实现，因此这就需要用到
JSBridage。传统的 JSBridge 通过 `Webview.addJavascriptInterface` 实现，一个简单示例如下：

    
    
    class JsObject {
        @JavascriptInterface
        public String toString() { return "injectedObject"; }
    }
    webview.getSettings().setJavaScriptEnabled(true);
    webView.addJavascriptInterface(new JsObject(), "injectedObject");
    webView.loadData("", "text/html", null);
    webView.loadUrl("javascript:alert(injectedObject.toString())");

Java 层返回数据给 Javascript 一般是通过直接使用 loadUrl 执行 JS 代码实现。当然除了这种方式注册
Bridge，还有很多应用特异的实现，比如使用 `console.log` 传输数据并在 Java 层使用 `onConsoleMessage`
回调去接收。但无论如何，这都导致攻击面的增加，大型应用甚至注册了上百个 jsapi 来供网页调用。

从历史漏洞来看，Webview 漏洞的成因主要是 jsapi 域名校验问题和 Bridge 代码本身的漏洞，由于篇幅原因就不展开了。

# 后记

本文中主要通过 Android
中的四大组件介绍了一系列相关的逻辑问题，尽可能地囊括了笔者所了解的历史漏洞。由于个人认知水平有限，总是难免挂一漏万，但即便如此，文章的篇幅还是比预想中的超出了亿点点。从温故知新的角度看，挖掘这类逻辑漏洞最好的策略还是使用静态分析工具，搜集更多
Sink 模式并编写有效的规则去进行扫描，实在没有条件的话用 (rip)grep 也是可以的。

# 参考资料

  * [Galaxy Leapfrogging 盖乐世蛙跳 Pwning the Galaxy S8](https://paper.seebug.org/1050/)
  * [Chainspotting: Building Exploit Chains with Logic Bugs](https://labs.f-secure.com/archive/chainspotting-building-exploit-chains-with-logic-bugs/) ([如何用11个exp攻破三星S8](https://paper.seebug.org/628/))
  * [Huawei Mate 9 Pro Mobile Pwn2Own 2017](https://labs.withsecure.com/publications/nhuawew-blog-post)
  * [Detect dangerous vulnerabilities in the TikTok Android app - Oversecured](https://blog.oversecured.com/Oversecured-detects-dangerous-vulnerabilities-in-the-TikTok-Android-app/)
  * [魔形女漏洞白皮书 - 京东探索研究院信息安全实验室](https://dawnslab.jd.com/mystique-paper/)
  * [HACKING XIAOMI'S ANDROID APPS - Part1](http://blog.takemyhand.xyz/2021/07/hacking-on-xiaomis-android-apps.html)
  * [Automating Pwn2Own with Jandroid](https://labs.f-secure.com/blog/automating-pwn2own-with-jandroid/)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2018/>

