## 背景

近日，奇安信威胁情报中心红雨滴团队结合红雨滴云沙箱产出的相关IOC情报，并配合内部蜜罐系统，在全球范围内，首个监测到多例组合使用Chrome浏览器高危漏洞及Windows内核权限提升漏洞。这些都用于穿透Chrome浏览器沙盒，以实现远程代码执行的定向攻击。这项监测实现了基于威胁情报和流量分析的在野Chrome浏览器漏洞攻击检测的突破。

## 关于PuzzleMaker

通过分析研判，红雨滴团队捕获到的Chrome浏览器完整漏洞利用攻击链，疑似与今年6月8日，由卡巴斯基披露的PuzzleMaker组织针对多家公司的高度针对性攻击活动中所使用的漏洞攻击链相同。PuzzleMaker在攻击中串联使用了Chrome和Windows10的0day漏洞，其中包含一个Chrome
0day和两个Windows10
0day。而当时的相关研究人员并未还原完整的攻击链，也暂未捕获带有完整漏洞利用的JavaScript代码。故本次是首次捕获到在野的完整漏洞利用攻击。

由于该漏洞已经用于真实的APT攻击，红雨滴团队第一时间复现并确认捕获到的样本可用，并对该漏洞利用的相关技术细节进行了分析，以便安全厂商可以增加相应的防护措施。

![v2-2d0376c5251a45ea5704b64fade7b41f.jpg](https://image.3001.net/images/20211028/1635405123_617a4d43274d5d5b294a4.jpg!small)

<https://twitter.com/RedDrip7/status/1453291780078714880>

## 漏洞利用分析

该在野漏洞利用链通过Chrome漏洞CVE-2021-21224和Windows内核提权漏洞CVE-2021-31956进行组合攻击。整个利用基于4月的泄露EXP，但是部分字段做了相应的混淆。在随后分析该EXP利用代码的时候发现，利用中获取到任意地址读写原子后，写入执行的ShellCode有两段，这里引起了我们的注意，一般来说Chrome漏洞是无法独立执行的，需要一个提权的漏洞用于沙箱绕过。

经过测试发现整个漏洞CVE-2021-21224部分能正常执行，如下所示第一段ShellCode写入到了WASM对象的可读可写可执行内存页面中。![v2-be26a5bdcfefb73a42c65a5c28dc5a6f.jpg](https://image.3001.net/images/20211028/1635405123_617a4d43974b7d416ed00.jpg!small)

两段ShellCode中大量的API调用通过syscall的方式完成。

![v2-d824f7ceda93de41bc1bf9ca12d0e4bc.jpg](https://image.3001.net/images/20211028/1635405124_617a4d44224646ea4420d.jpg!small)

通过调试发现，第一段写入的ShellCode实际上是CVE-2021-31956的利用代码，该0day漏洞于今年六月被卡巴斯基披露在puzzlemaker团伙的攻击中被使用，巧合的是该漏洞在卡巴斯基的报告中基于时间猜测是作为CVE-2021-21224这个Chrome
0day漏洞进行攻击时的提权模块(因为在实际的攻击中并没有捕获到Chrome漏洞的攻击代码)，因此这里有理由怀疑该次攻击可能和puzzlemaker有关，此外尽管4个月过去了，CVE-2021-31956这个漏洞本身的利用代码没有被公开。

该漏洞发生在内核模块ntfs.sys的函数NtfsQueryEaUserEaList中，任何在NTFS分区上有写入权限的文件句柄的进程都可以访问它，这里就包含了Chrome的渲染进程，因此该漏洞非常适用于突破沙箱，当NtfsQueryEaUserEaList处理文件的拓展属性列表，并将值返回到存储的缓存区时，存在一处整数下溢，从而导致之后的溢出。

这里核心的溢出逻辑在ea_block_size <= out_buf_length –
padding，其中ea_block_size值由攻击者可控。![v2-95ba44223df4e7f373a809a65fd38a27.jpg](https://image.3001.net/images/20211028/1635405124_617a4d4485a81ca36697c.jpg!small)

out_buf_length/padding值按如下方式生成，padding的取值为0，1，2，3，因此这里攻击者通过适当的构造，当循环中生成out_buf_length为0时，out_buf_length
– padding将出现下溢。

![v2-15aa70e87d91f44216234b2d4af7fbeb.jpg](https://image.3001.net/images/20211028/1635405124_617a4d44e0e5deb46e642.jpg!small)

这里溢出写入的地址为漏洞函数父函数NtfsCommonQueryEa中分配的内核分页池中。

![v2-78ea5531ffcd39c09384ecd8b9b4d779.jpg](https://image.3001.net/images/20211028/1635405125_617a4d453ef435a1f87ce.jpg!small)

漏洞使用了WNF模块来完成任意地址读写以及越界读写操作，首先NtUpdateWnfStateData/NtDeleteWnfStateData进行对应的内存布局。![v2-3479e7185a0d4749a443dcb328529641.jpg](https://image.3001.net/images/20211028/1635405125_617a4d45e62688d09d18a.jpg!small)

调用函数NtQueryEaFile触发下溢。![v2-e93d32c7903e478c933fd38c3294b273.jpg](https://image.3001.net/images/20211028/1635405126_617a4d4676ac28772c767.jpg!small)

最终通过修改进程token提升权限，这里详细的利用分析不再赘述，nccgroup的文章“CVE-2021-31956 exploiting the
windows kernel ntfs with
wnf”已经分析得很清楚，感兴趣的读者可以从参考链接找到对应文章。![v2-76324045788264c79654cf94bef07f1c.jpg](https://image.3001.net/images/20211028/1635405126_617a4d46d884a4fdaf194.jpg!small)

如下所示，第一段包含CVE-2021-31956利用代码的ShellCode执行完毕后，对应exp
页面的渲染进程已经是system权限，后续执行的第二段ShellCode将以system的权限在受害者机器上运行任何恶意代码。![v2-f3c8d681efbca140b7668013851818be.jpg](https://image.3001.net/images/20211028/1635405127_617a4d474fe116025788b.jpg!small)

通过第一段ShellCode提权穿过沙箱后，执行第二段ShellCode，最终开启一个线程和cc的通信。

![v2-1ea08490e0278fe3a8ecbc57c70b48be.jpg](https://image.3001.net/images/20211028/1635405127_617a4d47bd6cde7fef261.jpg!small)

如下所示获取wininet相关的联网函数后尝试访问后续的攻击代码。

![v2-bc8c3e1bd6eefb74c736d875900834d0.jpg](https://image.3001.net/images/20211028/1635405128_617a4d4839b9fea338778.jpg!small)

## 总结

目前包括天眼高级威胁检测产品在内的天擎终端安全管理系统、NGSOC、TIP威胁情报平台、智慧防火墙等全线奇安信攻击检测类产品都已经支持对此威胁的检测，用户可以升级相关的设备到最新的版本和规则库。

## 参考链接

<https://securelist.com/puzzlemaker-chrome-zero-day-exploit-chain/102771/>

<https://research.nccgroup.com/2021/07/15/cve-2021-31956-exploiting-the-windows-kernel-ntfs-with-wnf-part-1/>

