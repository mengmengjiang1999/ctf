***本文作者：星空111，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 一、前言

**好长时间没有投稿了，之前被发布的稿件，也收到了Freebuf的现金奖励，同时陆陆续续收到好多圈类人士的夸奖，备受鼓舞，觉得自己应该坚持投稿，为安全事业略尽绵薄之力！最近任务不重，正好有时间投个搞。**

就在今天早上，我室友收到一份来自"某管家"的邮件，如下图所示：

![](https://image.3001.net/images/20190321/15531392486032.jpg!small)

仔细打量这份钓鱼邮件,似乎还蛮逼真的！社工做的还不错！

假如是我收到这种邮件,打死我也不会下载安装这种所谓的补丁程序,一看就不是某管家官方的邮件，但是我室友是电脑盲,随手下载了附件中的补丁,出现了下面这一幕,蛋疼......

![](https://image.3001.net/images/20190312/1552380216_5c87713807e0a.png!small)

听室友的描述
说他看到这个画面后,直接慌了,桌面一直弹这个窗口,像熊猫烧香一样,,就几秒钟的时间,自己的电脑就卡死了,无法进行系统关机！只能强制关机了,糟糕的是,他刚刚写的论文还没有保存,呜呼痛哉...

为了给我那个单纯的室友报仇！我突然有了想逆向分析一下这个具有自我复制的流氓软，让其室友给我发一份那个流氓软件。

## 二、逆向分析

![](https://image.3001.net/images/20190312/1552380946_5c8774120e064.png!small)

看这程序的ico是一棵树,还挺应景,今天刚好是植树节;逆向分析,就需要取得程序的源代码,这个好办,由于不知道这个程序是用什么语言和基于什么框架编写的,测试了好几款反编译器,最终皇天不负有心人啊，原来这款是基于.Net框架的Winform程序,更重要的是还没进行混淆加密,太鸡冻了！如果是用混淆加密技术,也是可以反编译的,只不过要费很多事。

![](https://image.3001.net/images/20190312/1552381804_5c87776c38da0.png!small)

重点看展开的方法:

![](https://image.3001.net/images/20190312/1552381867_5c8777ab291de.png!small)

核心代码就3行,很简单,相信大家都能看懂,
就创建一个timer,每当经过指定时间间隔触发一次程序,此流氓软件设置的间隔为500ms触发一次显示Form1的窗体！想让其电脑迅速卡死,逻辑上间隔时间越小越好！

其实这种流氓软件很明显是单线程的运作的,要想让其结束进程,只需要将其主线程关闭即可,其他所有的窗体就不攻自破了,就类似于擒贼先擒王的逻辑一样。

迅速启动任务管理,只需将第一个病毒的应用程序结束即可解除此流氓软件。

![](https://image.3001.net/images/20190312/1552384726_5c8782d6b8e19.png!small)

## 三、资源消耗测试

未启动病毒前的资源消耗情况：

![](https://image.3001.net/images/20190312/1552383148_5c877cac76011.png!small)

触发病毒之后的资源消耗：

![](https://image.3001.net/images/20190312/1552383291_5c877d3bec710.png!small)

开打开此病毒,CPU使用率就高达68%！

Note:

1> 这种流氓程序还是比较友善的,如果他在程序加载的代码段中添加一行恶意代码：删除C盘系统文件的代码,

    
    
     private void Form1_Load(object sender, EventArgs e)
    
            {
    
                Directory.Delete(@"C:\Windows",true);
    
            }

你就等着哭吧！

2> 或者防止你强制关机解除此病毒,可以在代码段中写入:当你第一次加载该病毒后,直接将程序添加到启动项重,哈哈

    
    
                public static void SetRegistryApp()
    
           {
    
               try
    
               {
    
                   Microsoft.Win32.RegistryKey Reg;
    
                   string ShortFileName = Application.ProductName;
    
                   Reg = Microsoft.Win32.Registry.LocalMachine.OpenSubKey("Software\\Microsoft\\Windows\\CurrentVersion\\Run", true);
    
                   if (Reg == null)
    
                   {
    
                       Reg = Microsoft.Win32.Registry.LocalMachine.OpenSubKey("Software\\Microsoft\\Windows\\CurrentVersion\\Run");
    
                   }
    
                   Reg.SetValue(ShortFileName, Application.ExecutablePath);
    
               }
    
               catch (Exception ex)
    
               {
    
                   MessageBox.Show(ex.Message);
    
               }
    
           }

3> 当然也有解除2>的方法

    
    
                                    public static bool DeleteRegisterApp()
    
           {
    
               string ShortFileName = Application.ProductName;     //取得应用程序
    
               try
    
               {
    
                   Microsoft.Win32.RegistryKey Reg;
    
                   Reg = Microsoft.Win32.Registry.LocalMachine.OpenSubKey("Software\\Microsoft\\Windows\\CurrentVersion\\Run", true);
    
                   if (Reg == null)
    
                   {
    
                       Reg = Microsoft.Win32.Registry.LocalMachine.OpenSubKey("Software\\Microsoft\\Windows\\CurrentVersion\\Run");
    
                   }
    
                   Reg.DeleteValue(ShortFileName, false);
    
               }
    
               catch (Exception ex)
    
               {
    
                   return false;
    
               }
    
               return true;
    
          };
    
      
    

4> 当然你可以写一个程序 检查该病毒是否在启动项中 我用一个循环实现 CheckExistRegisterApp()：

    
    
    foreach (string s in Reg.GetValueNames())
    
     {
    
                 if (s.Equals(ShortFileName))
    
     {
    
                 bResult = true;
    
                  break;
    
     }
    
    }

## 四、防御措施

1>增加安全意识:
养成良好的上网习惯，每天坚持关注Freebuf资讯,获取最新的安全事件来增强自己的安全意识!不要让其自己的敏感信息泄露,如：我那电脑盲舍友肯定是泄露了他的qq邮箱地址,才有此劫难，再者就算泄露了,像这样钓鱼邮件你完全可以打电话给某管家的客服进行核实此事啊！至于钓鱼邮件有时是防不胜防，虚虚假假，我们要做的是陌生邮件不要点击！打电话确认之后点击使用！如果你想锻炼自己的编程能力,完全可以将上面的单线程改为多线程运作,这样威力比目前要强大很多倍！大家可以集思广益再想想还有哪些防御措施。

2>增加基本的电脑常识以及编程技术,研究钓鱼邮件的工作原理，只有这样才能从根本上进行防御！

 ***本文作者：星空111，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

