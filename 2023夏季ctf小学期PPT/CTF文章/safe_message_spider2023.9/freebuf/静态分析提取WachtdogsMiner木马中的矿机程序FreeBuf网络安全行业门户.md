**这周末爆发的新型 Linux 挖矿木马
WatchdogsMiner，有两家厂商分析的挺详细，尤其是腾讯云鼎实验室的分析，全面而深入。看完他们的的分析很有收获，也才发现这个
WatchdogsMiner 比之前想象的复杂一些：**

> 1\. 腾讯云鼎： [Linux watchdogs
> 感染性隐藏挖矿病毒入侵还原录](https://mp.weixin.qq.com/s/3V0HVEREZWU8SkRWLspaxg)
>
> 2\. 深信服： [WatchDogsMiner挖矿蠕虫大量感染Linux服务器](https://mp.weixin.qq.com/s/dwY--> BLzcyeXqPUZlhb__Q)

但是有一个参与此次木马应急响应的朋友指出：里面有个关键的挖矿模块 `/tmp/ksoftirqds`
，目前公开的分析文章中看他们并没有提到捕获的细节(当然，不是说他们没有搞定这一点，只是他们没在文中提及细节)。

说的也是，既然是 **挖矿木马** ，个人认为分析的时候要重点关注 3 个要素：

> 矿机程序(Hash 值、由什么开源矿机编译而来、版本等等）；
>
> 挖矿配置（挖矿账号、矿池地址，有的还有自建挖矿代理服务器）；
>
> 挖矿收益（可选，因为在某些情况下查不到）。

腾讯云鼎实验室的分析文章里给出了挖矿账号、矿池地址和挖矿收益信息，但关于挖矿程序信息并没有多说，文末也并没给出挖矿程序的
MD5。鄙人姑且一试，看能不能就这一点为公开的技术文章做一个小补充。

因为这个矿机程序在运行起来之后就被主样本删除了本地的执行体，并做了进程隐藏。一起探讨这个事件的朋友说，矿机程序可能需要动态分析的时候提取出来，或者做删除文件的还原操作，当然，也可以找到隐藏的挖矿进程把它从内存中
Dump 出来。挖矿账号和矿池地址在运行木马程序后抓包一般也能抓到……

周日白天出去浪，晚上回来大致看了一眼，发现用静态分析的方法，就可以从 Go 语言编写的 ELF
主木马样本中提取矿机程序和挖矿配置的文件。这里简单说一下思路。

以 WatchdogMiner 的 32bit 样本(UPX packed，MD5:
**aee3a19beb22527a1e0feac76344894c** ，下文简称 **主木马** )为例来分析，这是一个 Go 语言编译来的 ELF
程序，其中有一批函数看起来 import 了 `github_con_hippies_LSD` 这个包：

![funclist.png](https://image.3001.net/images/20190225/1551106397_5c74015d70d89.png!small)

但是，我们如果去 Github 上找这一个 `hippies/LSD` 的 Go 语言包，会发现 **Github 上根本没有这个包** 。以前有人讲过
Go 语言二进制的混淆技巧，其中之一就是修改 import 进来的 Go 语言包的名字，用来迷惑分析人员。这里可以猜测主样本用了这个混淆技巧，即：这个所谓的
`hippies/LSD` 包，是一个别的 Go 语言包，可能是木马作者自己开发的，也可能是网上公开的别的开源 Go
语言包(做这种混淆的话，一般都是针对开源 Go 语言包，因为如果被分析人员发现用了什么包，分析人员就可以直接去参考 Go 语言包的 Docs
或者源码，对逆向分析木马程序帮助很大)。

这一点很有意思，这是鄙人第一次见到这种情况的 Go 语言二进制文件，也是促使我稍微深入一探究竟的原因之一。

那么这个包在这个木马程序中有什么用？简单分析就知道，这个包 **在执行`Go build` 命令来编译最终的二进制程序时，可以把程序用到的文件打包到最终的
EFL 文件中**。具体到这个木马上来看，矿机程序 **ksoftirqds** 和矿机配置文件 **config.json**
其实都已经被以二进制数据的形式打包在了 ELF 格式的主木马文件中，并且在木马执行过程中释放出来。

于是我们就可以看看，能不能直接静态逆向，在 IDA 中直接把矿机程序文件和矿机配置文件从主木马中提取出来。

我们不能准确知道这个 Go 语言包是什么，但好在它并不复杂，直接在 IDA 里就能分析出来关键函数的实现逻辑。这个 Go 语言包的主要的作用是
**把要打包的文件用 GZip 格式压缩，然后打包进 ELF 文件中** 。

WatchdogMiner 的主木马中，有一个 `github_com_hippies_LSD_LSDB__ksoftirqds32Bytes`
函数，该函数的核心逻辑如下：![addr_length.png](https://image.3001.net/images/20190225/1551106448_5c74019043a9f.png!small)

上图已经标出： `addr_ptr` (off_851FAC8 )就是 GZip 压缩后的 `ksoftirqds` 文件地址的指针(指针值是
`byte_84A3580` ，即最终的 GZip 文件地址)，下面的参数即为 Gzip 文件 `length` 地址(length: 0x7BCE6)。

然后，在随后调用的函数 `github_com_hippies_LSD_LSDC_Read` 我们可以看到对
`compress/gzip/NewReader` 的调用，这里就确定了我们前面提到的结论：这个 `hippies/LSD` 包的主要作用是：GZip
压缩文件、把压缩后的文件编译打包进 ELF
主木马中：![gzip_decompress.png](https://image.3001.net/images/20190225/1551106548_5c7401f49af30.png!small)

查看 GZip 数据地址 `byte_84A3580` 的内容，就可以看到前两个字节 `1F8Bh` ，即为 GZip
格式的文件头标志：![gzip_flag.png](https://image.3001.net/images/20190225/1551106576_5c7402108ebe8.png!small)

上面是矿机程序的情况，矿机配置文件 `config.json` 的情况也一毛一样。OK，明白了原理，再从主木马程序文件中提取矿机程序和矿机配置文件就很
Easy 了：

> 在 IDA 中先找到他们的 GZip 压缩数据的 addr 和 length；
>
> 在 IDA 中把这一段数据 dump 出来；
>
> 用 GZip 解压 dump 出来的二进制数据，Over。

###  **结论**

我从 WatchdogMiner 的 32bit 样本(MD5: **aee3a19beb22527a1e0feac76344894c** )
中提取出来的矿机程序也加了 UPX 壳，脱壳后发现是由 **XMRig2.8.0 RC** 编译而来；矿机配置文件 `config.json`
没加壳。IDA
中打开矿机程序截图如下：![miner_info.png](https://image.3001.net/images/20190225/1551106599_5c740227b17e8.png!small)

配置文件的内容如下：

    
    
    {
        "algo": "cryptonight",
        "api": {
            "port": 0,
            "access-token": null,
            "id": null,
            "worker-id": null,
            "ipv6": false,
            "restricted": true
        },
        "asm": true,
        "autosave": true,
        "av": 0,
        "background": false,
        "colors": true,
        "cpu-affinity": null,
        "cpu-priority": null,
        "donate-level": 0,
        "huge-pages": true,
        "hw-aes": null,
        "log-file": null,
        "max-cpu-usage": 100,
        "pools": [
            {
                "url": "stratum+tcp://xmr.f2pool.com:13531",
                "user": "46FtfupUcayUCqG7Xs7YHREgp4GW3CGvLN4aHiggaYd75WvHM74Tpg1FVEM8fFHFYDSabM3rPpNApEBY4Q4wcEMd3BM4Ava.teny",
                "pass": "x",
                "rig-id": null,
                "nicehash": false,
                "keepalive": false,
                "variant": -1,
                "tls": false,
                "tls-fingerprint": null
            }
        ],
        "print-time": 60,
        "retries": 5,
        "retry-pause": 5,
        "safe": false,
        "threads": null,
        "user-agent": null,
        "watch": false
    }
    

相关文件的 MD5 如下：

> a5d6916fdfac60e680681f960430c6b5 config.json
>
> 510f8ee9e4195b0d35ed6daaf0bdb3b1 miner_ksoftirqds_32bit
>
> e160cbeb74612cfbf0e1bdcf2d0038f3 miner_ksoftirqds_32bit.gz
>
> a48f529646b8b5e96bab67d6d517a975 miner_ksoftirqds_64bit
>
> a0bbd10da4aa1426ca42801b948372b9 miner_ksoftirqds_64bit.gz
>
> 86e2f5859ca276f307a034b5c7c450f1 miner_ksoftirqds_64bit_unpacked
>
> 877a282eb09d8f88ae29cd6b332ab90c miner_ksoftirqds__32bit_unpacked

 **后记**

跟同行大佬私下聊，说通过 **binwalk** 也可以直接把里面的文件提取出来。我试了下，可行，而且可以提取出总共 4 个 gzip
文件(除了矿机程序和矿机配置文件，还有另外两个文件也被做了同样的处理)。有兴趣的朋友可以自己探索一下：![binwalk_gzipfilelist.png](https://image.3001.net/images/20190225/1551106636_5c74024c9438b.png!small)

但是有一点需要说明，这个 Case 中，恰好是把这些目标文件压缩成 gzip 格式，然后打包进 ELF 木马文件中，而 binwalk
恰好可以识别二进制程序中的 gzip 文件格式。如果别的 Case 中，木马作者把要打包的文件做了 binwalk 无法识别的编码，那么就难以用
binwalk 直接提取了。

所以，本文提供的只是一个通用但算是 Hard Way 的静态分析手法达到提取文件的目标，仅供参考。

另外，综合几家的分析报告，以及同行大佬私下讨论，可以推测 Watchdogs 木马启用了 2 款矿机程序：

> 一个是[默安科技最新的分析报告](https://mp.weixin.qq.com/s/3jdtIRIFFPrVnWSU1K99lg)中提到的，
> XMR-Stak 编译而来，挖矿配置硬编码在矿机程序中，xmr 钱包地址分支是 .tenx；
>
> 另一个是本文中提到的，XMRig 编译来的矿机，挖矿配置是打包在主样本中的 config.json 文件，xmr 钱包地址分支是 .teny。

xmr-stak 和 xmrig 两个矿机程序的配置文件格式和内容有所不同，可以用来辅助分析：

> \- xmr-stak 的默认配置文件： <https://github.com/fireice-uk/xmr-stak-> cpu/blob/master/config.txt>
>
> \- xmrig 的默认配置文件：
> <https://github.com/xmrig/xmrig/blob/master/src/config.json>

***本文作者：甲鱼，转载请注明来自FreeBuf.COM**

