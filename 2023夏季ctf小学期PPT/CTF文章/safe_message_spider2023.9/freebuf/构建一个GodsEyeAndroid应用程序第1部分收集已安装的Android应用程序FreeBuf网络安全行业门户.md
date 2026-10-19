首先问候一下我的黑客伙伴们，在之前的[Introduction to
Amunet](https://www.javaworld.com/article/3095406/android/android-studio-for-beginners-part-1-installation-and-setup.html)
教程中，我们了解到Amunet可能是一个间谍Android应用程序。 我不浪费太多时间因而直入主题。

在本教程中，我们将仅收集已安装的应用程序及其相关信息，但不会将它们发送到外部服务器，因为我们尚未设置我们的服务器和数据库。
我相信这将会在下一个教程中（设置Web服务器和数据库）。

我假设您已经安装了Android Studio并且环境运行顺畅。 如果没有，只需前往谷歌搜索“安装和设置android
studio”或者只是按照这个外部网站 [Android Studio for beginners, Part 1: Installation and
setup](https://www.javaworld.com/article/3095406/android/android-studio-for-beginners-part-1-installation-and-setup.html)（我与他们没有任何关系）。
话虽这么说，我们会继续创建一个Android项目。

创建一个新的安卓项目

启动Android Studio并创建一个新的android项目。

![image.png](https://image.3001.net/images/20180726/15325915837313.png!small)根据你的选择进入应用，我的是Amunet.域名可以是您选择的任何内容。
接下来的一步.

![image.png](https://image.3001.net/images/20180726/1532591602443.png!small)  
现在最小的手机目标API是19（KitKat）.

![image.png](https://image.3001.net/images/20180726/15325916208822.png!small)通过该活动，继续选择基本活动,下一个。

![image.png](https://image.3001.net/images/20180726/15325916323543.png!small)我们将活动保留为“MainActivity”，然后单击Finish。

![image.png](https://image.3001.net/images/20180726/15325916407478.png!small)我们的项目应该成功创建。
我们不会对接口做太多工作，因为大多数代码都将在后台线程，服务和广播接收器中编写。 我们可能会使用UI来获取权限（在23 +上）

![image.png](https://image.3001.net/images/20180726/15325916504236.png!small)  

收集有关已安装应用程序的信息  
前往

    
    
    MainActivity.java

随意删除onCreate方法中FloatingActionButton的代码并添加此代码

    
    
    new Thread(new Runnable() {
                @Override
                public void run() {
                    collect_installed_apps();
                }
    }).start();

您可能已经猜到了，我们在onCreate方法中运行一个线程并调用方法（函数）collect_installed_apps。
您还会发现该函数已用红色下划线表示我们尚未创建该函数。 让我们继续前进并创建功能。

收集INSTALLED_APPS

在此方法中，我们导入ApplicationInfo，PackageManager，Log和List。
转到文件的最顶部但在包行（行1）下面并添加此import语句。

    
    
    import android.content.pm.ApplicationInfo;
    import android.content.pm.PackageManager;
    import java.util.List;
    import android.util.Log;

现在，让我们创建我们的方法collect_installed_apps

    
    
     private void collect_installed_apps() {
        final PackageManager pm = getPackageManager();
        List<ApplicationInfo> packages = pm.getInstalledApplications(PackageManager.GET_META_DATA);
        for (ApplicationInfo packageInfo : packages) {
            if(pm.getLaunchIntentForPackage(packageInfo.packageName) != null)
            {
                String app_name = packageInfo.loadLabel(getPackageManager()).toString();
                String app_package = packageInfo.processName;
    
                Log.i("0x00sec", "App name: " + app_name + " Package Name: " + app_package);
            }
        }
    }

使用打包程序管理器，代码循环安装的应用程序并获取其信息。 我们在这里收集的信息是应用程序名称和包名称。 有很多可用的信息，但我们仅限于这两个。
但是，您可以继续收集其他信息。 由于我们没有设置我们的Web服务器和数据库，我们将使用Log.i将信息记录到控制台。

配置LOGCAT

您可以阅读更多有关Logcat的信息，但简单来说，系统和其他应用程序会将错误，警告和其他信息等消息转储到此流中。 它永远在变化而不是不变。
我们的Android应用程序还使用Log.i调用将信息转储到此流中。 由于推送了大量信息，因此很难找到我们的信息，因此我们将Android
Studio配置为仅显示具有特定标记的消息。 如果您在Log.i代码中注意到，我们分别传递了两个参数：tag和message。 我们告诉Android
Studio只显示带有我们定义的标签0x00sec的消息。 通过这种方式，我们看不到与我们的Android应用程序无关的其他消息。 在Android
Studio的左下角，我们将找到Logcat选项卡。 做你自己的荣誉并点击它。
![image.png](https://image.3001.net/images/20180726/15325904192361.png!small)

按照图像中的步骤操作，将弹出另一个“日志”对话框。 填写正确的信息，否则将不会显示相应的消息。

1.输入您自己的过滤器名称。

2.在日志标记中，使用0x00sec（或您在Log.i代码中用作第一个参数的任何内容）。

3.输入包名称（位于MainActivity.java的第一行）

![image.png](https://image.3001.net/images/20180726/15325916958920.png!small)  

单击确定。 现在我们准备运行我们的Android应用程序。 首先必须确保在测试设备上启用USB调试。 点击此链接 [How to Enable USB
Debugging Mode on Android - KingoRoot](https://www.kingoapp.com/root-tutorials/how-to-enable-usb-debugging-mode-on-android.htm)\-如果您尚未启用它，请使用KingoRoot。

让我们运行我们的安卓应用程序

单击android studio顶部app旁边的绿色播放按钮，或使用Control + R（Mac）和Shift + F10（Windows /
Linux）。 确保已连接设备并启用USB调试。  
当应用程序运行时，控制台应填充我们安装的应用程序及其程序包名称。

![image.png](https://image.3001.net/images/20180726/15325917056882.png!small)  

正如您所注意到的，我们的logcat过滤器运行良好。

让我们在这里结束

在今天的教程中，我们学习了如何填充已安装的Android应用程序。 在下一个教程中，我们将设计我们的数据库并设置我们的Web服务器。
与此同时，欢迎我们的代码更正，建议，应用程序设计等。 感谢在我们下次见面前的分享的机会，我要离开了。

检查github仓库: <https://github.com/sergeantexploiter/Amunet>

作者：sergeantsploit  
翻译：i春秋翻译小组-Neo(李皓伟）  
翻译来源：<https://www.0x00sec.org/t/building-a-god-s-eye-android-app-part-1-collecting-installed-android-apps/7121>

[有问题大家可以留言哦~也欢迎大家到春秋论坛中来玩耍呢！
](http://www.freebuf.com/column/178750.html)[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)  

