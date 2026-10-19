## 前言

 **与Google Nexus系列一样，如果你想要root[Google Pixel](https://forum.xda-developers.com/pixel)智能手机或为其安装自定义ROM，那么首先你必须解锁Bootloader。在今年最新推出的Google Pixel
3和Google Pixel 3 XL同样也不例外。实际上，随着root神器[Magisk](https://forum.xda-developers.com/apps/magisk)的更新，root[ Pixel 3](https://www.xda-developers.com/tag/google-pixel-3/)和[Pixel 3 XL](https://www.xda-developers.com/tag/google-pixel-3/)早已成为可能。目前Magisk的最新版本为17.3，有关更多信息可以[参阅此处更新说明](https://forum.xda-developers.com/showpost.php?p=77933549&postcount=47)。使用Magisk解锁Pixel
3系列的Bootloader只需短短的几秒钟时间，让你的设备启动并运行Magisk也只需要几分钟时间。如果你曾经有过解锁Google
Nexus，Google Pixel或OnePlus设备的经验，那么解锁Pixel
3和安装Magisk应该不会难倒你。如果你并没有尝试过，本文将会一步步的指导你完成整个过程。**

 **
**![pixel-3-colors2-810x298_c.png](https://image.3001.net/images/20181102/1541128551_5bdbc1678c6f0.png!small)****

在此，我要特别感谢Magisk的首席开发工程师[topjohnwu](https://forum.xda-developers.com/member.php?u=4470081)，感谢他的所有工作和付出。大家可以在[Twitter](https://twitter.com/topjohnwu)或[Patreon](https://www.patreon.com/topjohnwu)上关注他。

## 一、解锁 Google Pixel 3 Bootloader

> **注：**
> 解锁bootloader将擦除设备中的所有数据，包括保存在设备内部存储器上的所有媒体，如图片，视频，音乐，文档等。为了避免不必要的麻烦和损失，请务必先将所有重要文件备份到PC或云存储，然后再执行此操作。

1\. 打开手机 设置-关于手机-点击版本号7次，以打开“开发者选项”。

2\. 返回到设置，打开 开发者选项-打开USB 调试，打开“OEM 解锁”。 出于安全考虑，这可能会要求你输入锁屏PIN/密码。

3\. 向下滚动，直到看到“USB调试”选项并启用。

![1 -副本.png](https://image.3001.net/images/20181102/1541128804_5bdbc26497ee3.png!small)

![解锁 Google Pixel 3
Bootloader](https://image.3001.net/images/20181102/1541128842_5bdbc28ac95a5.png!small)

![5.png](https://image.3001.net/images/20181102/1541128910_5bdbc2ceed0e8.png!small)![解锁
Google Pixel 3
Bootloader](https://image.3001.net/images/20181102/1541128911_5bdbc2cf39c79.png!small)

4\. 将Pixel 3插入PC，并按照[这里的步骤](https://www.xda-developers.com/install-adb-windows-macos-linux/)在PC上设置[ADB](https://www.xda-developers.com/install-adb-windows-macos-linux/)和[Fastboot](https://www.xda-developers.com/google-releases-separate-adb-and-fastboot-binary-downloads/)。如果你只能访问Chromebook，请参照
[本指南](https://www.xda-developers.com/adb-fastboot-chromebook-chrome-os/)在[Chrome OS](https://www.xda-developers.com/tag/chrome-os/)上设置ADB和Fastboot。

5\. 通过在保存ADB和Fastboot二进制文件的同一目录中打开命令提示符/Power
Shell/Terminal，并根据你当前的操作系统输入以下命令，确保你的PC可以正常识别你的Pixel 3手机：

 **Windows 命令提示符：**

    
    
    adb devices

 **Windows Power Shell：**

    
    
    .\adb devices

 **macOS/Linux Terminal：**

    
    
    ./adb devices

（注：对于本教程的其余部分，命令的使用同样取决于你的操作系统。）

如果你看到设备的序列号并且显示“authorized（已授权）”，那么你可以继续以下操作。如果这是你第一次为此设备设置ADB，则可能会在手机上看到“为你的PC启用USB调试”的提示。点击授予即可。如果你在使用Windows
PC识别设备时遇到问题，那么请尝试安装最新的[Google USB
Drivers](https://developer.android.com/studio/run/win-usb)。

6\. 现在，重启到bootloader菜单。你可以通过在启动时按住电源和音量调低键或输入以下ADB命令来执行此操作：

    
    
    adb reboot bootloader

7\. 进入bootloader菜单后，现在你必须切换到使用fastboot命令与你的设备进行通信。要解锁Pixel
3的bootloader，请输入以下命令：

    
    
    fastboot flashing unlock

8\.
现在，你应该会在屏幕上看到一个警告文本，告诉你解锁bootloader将会带来的巨大潜在风险。在电源和音量按钮旁的屏幕上，你应该能看到一些提示内容。按音量增大键，直到显示“unlock
the bootloader”，然后再按电源键。’

![按电源键](https://image.3001.net/images/20181102/1541128975_5bdbc30fd6ed4.jpg!small)

9\. 此时，手机将解锁bootloader并重启到bootloader菜单。这次，bootloader将显示一个红色警告图标和“unlocked”字样。

10\. 现在，重启手机回到Android 9 Pie OS。你可以通过发送以下fastboot命令来执行此操作：

    
    
    fastboot reboot

11.到这里，我们就成功解锁了Google Pixel 3或Google Pixel 3
XL的bootloader！你将在每次重启时都看到一条手机bootloader已被解锁的警告信息，但不要担心这不会影响你的日常使用。

## 二、使用 Magisk Root Google Pixel 3

> **注：** 以下说明是在发布自定义recovery（如[TWRP](https://www.xda-developers.com/how-to-> install-twrp/)）之前撰写的。因此，安装Magisk的唯一方法是从bootloader刷入patched boot
> image。因此，当下一个软件版本可用更新的引导映像时，我提供的库存引导映像将过时。一旦TWRP可用，我将会更新这些指令，因此指令与版本号无关。

使用未锁定的bootloader，现在你可以启动已修改的引导映像。要让Magisk工作，你需要patched Pixel 3的boot
image。幸运的是，Magisk Manager app可以为你解决这个问题。我已在我自己的Google Pixel 3
XL以及Dees_Troy的Google Pixel 3上进行了测试，确认Magisk可以在这两种设备上运行。

1\. 由于设备已被擦除，因此你需要返回并重新启用开发人员选项以及USB调试。 请确保你的PC仍能识别你的Pixel 3手机。

2\. 下载Google Pixel 3或Google Pixel 3 XL的stock boot
image。注意：请确保你设备的版本号与引导映像相匹配。你可以通过打开手机 设置-关于手机-点击版本号 进行查看。

> Download Google Pixel 3 (“blueline”) [stock boot
> image](https://www.androidfilehost.com/?fid=11410932744536984606) 版本号
> **PD1A.180720.030**
>
> Download Google Pixel 3 XL (“crosshatch”) [stock boot
> image](https://www.androidfilehost.com/?fid=11410932744536984609) 版本号
> **PD1A.180720.030**

3\. 将stock boot image移动到设备内部存储器的文件夹中。下载文件夹。

4\. 安装最新的Magisk Manager beta APK。如果以下patched boot image无法启动，请尝试通过加入[Magisk
Canary channel](https://forum.xda-developers.com/apps/magisk/dev-magisk-canary-channel-bleeding-edge-t3839337)下载最新的Magisk Manager APK。

5\. 点按“安装”。

6\. 再次点击“安装”，不会安装显示的zip文件。

7\. 点击“Patch Boot Image File”。

8\. 选择之前保存的stock boot image文件。

9\. 此时，你应该会在屏幕上看到“Magisk Manager patching the stock boot
image”的进度。完成后，点击关闭。Magisk Manager应该已将文件保存为“patched_boot.img”到Download目录下。

![点击关闭](https://image.3001.net/images/20181102/1541129058_5bdbc362d055b.png!small)

![点击关闭](https://image.3001.net/images/20181102/1541129101_5bdbc38df293c.png!small)![点击关闭](https://image.3001.net/images/20181102/1541129145_5bdbc3b9bc367.png!small)

10\. 将patched_boot.img文件从你的设备移动到你的PC上。为了避免麻烦，请将文件移动到ADB和Fastboot二进制文件所在的同一目录下。

11\. 再次重新启动到bootloader菜单。

12.（可选）在bootloader中，输入以下fastboot命令临时引导patched Magisk boot image：

    
    
    fastboot boot patched_boot.img

13\. 几秒钟后，你的手机应该会退出bootloader菜单，并重新启动到Android Pie OS。如果成功，你应该能够打开Magisk
Manager并查看安装了哪个版本的Magisk。现在，我们需要实际安装Magisk，这样我们就不必在每次启动之前运行这个fastboot命令了。

14\. 让我们将patched Magisk boot image刷入到启动分区。在bootloader界面输入以下命令：

    
    
    fastboot flash boot patched_boot.img

![输入命令](https://image.3001.net/images/20181102/1541129176_5bdbc3d864a14.png!small)

15.（可选）由于Google Pixel 3和Pixel 3 XL支持A/B分区，因此你还可以将patched boot image刷入到非活动插槽（
inactive slot）。 只需将上述命令中的“boot”替换为“boot_a”或“boot_b”即可。

16\. 重新启动回到Android Pie OS，并通过打开Magisk Manager来检查root的状态。

## 三、Root Pixel 3 或 Pixel 3 XL 后，我们可以做些什么？

以下是我所想到的能干的一些事情：

> 1、安装Active Edge Mod以[完全自定义Pixel 3上的挤压手势](https://www.xda-> developers.com/customize-google-pixel-2-active-edge-sense-> plus/)。（注：这尚未更新支持Pixel 3，但开发人员正在为此努力！）
>
> 2、通过[Substratum主题引擎](https://www.xda-developers.com/custom-themes-android-p-> root-substratum/)为系统应用或第三方应用安装自定义主题。同样，你也可以使用Pluvius等应用根据当前壁纸动态来设置系统主题。
>
> 3、使用Titanium Backup进行完整的应用备份。
>
> 4、重新启用通话录音（[Android Pie通话录音功能非root用户将无法使用](https://www.xda-> developers.com/android-pie-blocks-non-root-call-recording-apps/)）。
>
> 5、想念Android Nougat的blob表情符号吗？现在，你可以使用[Blobmoji](https://forum.xda-> developers.com/apps/magisk/module-notocoloremoji-blob-patch-t3677992/page4)
> Magisk模块重新获取到这些表情符号。
>
> 6、Magisk Module repo中有大量的音频mods，可以让你体验更好的音乐播放！
>
> 7、喜欢stock Gboard keyboard app？看看[这些Gboard主题](https://www.xda-> developers.com/magisk-mod-gboard-themes-poco-f1-ios-razer-windows/)。
>
> 8、你是谷歌应用和服务的忠实粉丝吗？root后，你就可以启用许多还未正式推出的开发中的功能。你可以查看[我们的文章](https://www.xda-> developers.com/category/tutorials/)，我们的教程文章中有大量关于这方面的示例。
>
> 9、不是Google Pixel Launcher的粉丝？
> 那么，你可以选择使用像Lawnchair这样的第三方launcher，你可以将它[集成到最近的应用程序概述](https://www.xda-> developers.com/lawnchair-android-pie-recent-apps-integration-root/)和手势导航中。
>
> 10、自定义默认系统媒体，字体，启动动画等。
>
> 11、获取[YouTube Vanced](https://www.xda-developers.com/youtube-vanced-apk-> root/)-适用于Android YouTube应用增强版。
>
> 12、这是[我们开发的一个app](https://www.xda-developers.com/custom-saturation-level-> google-pixel-2/)，可以让你自定义显示饱和度级别，如果你喜欢更加强烈的颜色。

你可能听说过解锁bootloader和root设备后，将导致你无法玩某些游戏，例如[Pokémon Go 和 Fate/Grand
Order](https://www.xda-developers.com/fate-grand-order-fortnite-mobile-magisk/)甚至无法正常使用一些银行的app程序。但你大可放心，MagiskHide可以帮助你隐藏设备被修改的痕迹，让你像正常用户一样使用应用和玩游戏。此外，解锁bootloader将会影响你获取更新。你需要了解如何
[sideload每月安全补丁更新](https://www.xda-developers.com/flash-monthly-security-update-google-pixel/)，当然这也非常的容易。

最后，如果你想对你的设备进行更多的控制，你可以在Pixel
3上刷入自定义ROM和内核。自定义ROM可以为你提供许多库存软件上没有的选项。自定义内核允许你调整设备的性能，以增加电池寿命或提高你喜爱游戏的帧数。由于Google
Pixel 3和Pixel 3 XL[刚发布不久](https://www.xda-developers.com/google-pixel-3-google-pixel-3-xl-specs-features-pricing-availability/)，因此目前还没有任何可用于该设备的自定义ROM或内核。如果你对此感兴趣，你可以关注这两种设备的XDA论坛。

> [Google Pixel 3 论坛](https://forum.xda-developers.com/pixel-3)
>
> [Google Pixel 3 XL 论坛](https://forum.xda-developers.com/pixel-3-xl)

 ***参考来源：[XDA](https://www.xda-developers.com/google-pixel-3-unlock-bootloader-root-magisk/)，FB小编secist编译，转载请注明来自FreeBuf.COM**

