这个病毒很老了，已经有很多前辈分析过该病毒，跟着前辈们的思路深入分析一下，并编写一个清理工具。这是我分析的第一个真实环境下的恶意样本，文中如果有不正确的地方请指正。只需要清理工具的话，直接下滑到
解决方案 一节。

## 病毒行为总览

代码使用Delphi7编写，后续分析汇编代码发现有对XP系统和更高版本windows做了兼容处理，在这些系统上都可以正确感染，年代久远(我还没用过xp..)。被感染机器的
C:\ProgramData\目录下会有Synaptics目录，其下包含原始的恶意样本，但是图标不固定（图标会更新为最近一次运行被感染exe文件的图标），病毒生成的大部分文件都将其设置为
隐藏文件和系统文件（Exlporer设置显示隐藏文件和系统文件或命令行下attrib即可看到）。![1638080641_61a3208137ff8f617250e.png!small?1638080643258](https://image.3001.net/images/20211128/1638080641_61a3208137ff8f617250e.png!small?1638080643258)

被感染机器的Desktop、Documents、Downloads目录下的32位EXE文件和xlsx文件都会被掉包，但是用户并不会有察觉，导致文件分享给他人时，大范围感染。

病毒包含很多模块，下面是一个大体功能图，其中和网络连接有关的模块的IOC都已经失效。![1638090974_61a348dee5a4d03316215.png!small?1638090977033](https://image.3001.net/images/20211128/1638090974_61a348dee5a4d03316215.png!small?1638090977033)

## 蠕虫模块分析

通过 SHGetSpecialFolderLocation和
SHGetPathFromIDListA来获取要感染的目录（清理工具的编写也会通过这种方式）。病毒会获取Desktop、Downloads和Documents的路径并递归感染子文件。

![1638083752_61a32ca87ad4a35d7923c.png!small?1638083754547](https://image.3001.net/images/20211128/1638083752_61a32ca87ad4a35d7923c.png!small?1638083754547)

### EXE文件感染分析

对于EXE文件，通过LoadLibrary加载到当前进程（病毒是32位的,所以只感染32位的EXE），根据其资源节“ **EXEVSNX**
”的情况，来进行对应的操作，这个资源节内的数据代表着版本号。这个病毒是可以进行版本更新的。

![1638084261_61a32ea590775c8b1d146.png!small?1638084263720](https://image.3001.net/images/20211128/1638084261_61a32ea590775c8b1d146.png!small?1638084263720)

具体的感染流程如下，思路很简单。将原文件打包到病毒文件的资源节“ **EXERESX**
”中，病毒文件的图标被替换为原文件的图标，最后用病毒文件替换原文件。

![1638084849_61a330f1cd4aac73457ea.png!small](https://image.3001.net/images/20211128/1638084849_61a330f1cd4aac73457ea.png!small)

![1638084914_61a3313267c8d137c222c.png!small?1638084916640](https://image.3001.net/images/20211128/1638084914_61a3313267c8d137c222c.png!small?1638084916640)

当用户运行被掉包的EXE文件时，会释放出资源节"EXERESX"的原文件并运行，这样就对用户来说无感知。

具体的释放流程如下，原文件会被释放到已 "._cache_"开头的文件中，文件属性被设置为
系统文件和隐藏文件，即使打开“显示隐藏文件的选项”也不会显示，“显示系统文件”的选项一般用户很少会打开。比较有趣的一点是代码中还会判断
"._cache_"开头的文件是否也有资源节"EXERESX"。这是一个重复感染的问题，病毒作者考虑到了这一点。分析整个代码来看，可以发现病毒作者的编程功底很强，很多特殊情况的处理都有考虑到。

![1638085984_61a3356023d9630317c80.png!small?1638085986187](https://image.3001.net/images/20211128/1638085984_61a3356023d9630317c80.png!small?1638085986187)

###
![1638086110_61a335de93dbf39ed013c.png!small?1638086112759](https://image.3001.net/images/20211128/1638086110_61a335de93dbf39ed013c.png!small?1638086112759)

###
![1638086830_61a338ae0c596ca52d5cd.png!small?1638086832108](https://image.3001.net/images/20211128/1638086830_61a338ae0c596ca52d5cd.png!small?1638086832108)

### XLSX文件感染分析

感染xlsx文件是通过COM组件完成的，所以只有安装了Excel的机器才会被正确感染（清理工具也是利用COM组件来进行修复xlsx文件的）。![1638087668_61a33bf47e7575b673c69.png!small?1638087670672](https://image.3001.net/images/20211128/1638087668_61a33bf47e7575b673c69.png!small?1638087670672)

大致的感染流程如下，病毒文件的资源节"XLSM"包含包含了恶意宏代码的xlsm文件。

![1638088057_61a33d79d13de8a116b13.png!small?1638088059903](https://image.3001.net/images/20211128/1638088057_61a33d79d13de8a116b13.png!small?1638088059903)

中间部分大量调用了COM组件中的函数，这里并没有去分析。用动态调试跳过了这些函数，从结果来看就是把原来的xlsx中的数据拷贝到包含宏代码的xlsm文件中。最后替换原了的xlsx文件，并再起目录下生成一个
"~$chac1"文件（这也是一个感染特征，文件夹下有这个文件说明该路径下的xlsx文件都被感染为xlsm文件），这个文件的数据就是病毒文件本身，文件属性也设置了系统文件和隐藏文件。被感染的xlsx文件后缀会变成xlsm，内容和原来一样。

![1638088144_61a33dd06a3b47d3b152b.png!small?1638088146531](https://image.3001.net/images/20211128/1638088144_61a33dd06a3b47d3b152b.png!small?1638088146531)

## 其它模块分析

这些模块有的已经失效了，并没有太深入的分析。

  * 邮件发送： 使用的是Delphi中封装好的库,使用邮件服务器是 smtp.gmail.com，账号密码是xredline2@gmail.com;xredline3@gmail.com/xredline2**x;xredline3**x 我用gmail登录了一下，已经失效了。发送邮件的目的邮箱地址是 xredline1@gmail.com
  * ![1638089412_61a342c4e6fd519eeaa86.png!small?1638089414941](https://image.3001.net/images/20211128/1638089412_61a342c4e6fd519eeaa86.png!small?1638089414941)键盘记录，设置消息钩子，最常用的方式。dll文件在病毒文件资源节"KBHKS"中。（动态调试过程中消息钩子并没有设置，出错原因还有待确认）![1638089918_61a344be235b44f77d7c4.png!small?1638089920137](https://image.3001.net/images/20211128/1638089918_61a344be235b44f77d7c4.png!small?1638089920137)
  * 远控模块，功能很少，反弹shell、屏幕截图、文件上下载...
  * 自启动项，直接操作注册表，用的是Delphi封装好的库（Register）,使用很简单，不赘述。

  

## IOC整理

文件MD5就不贴了，被感染文件一直都是变化的。

Mutex| Synaptics2X  
---|---  
Domain| xred.mooo.com  
Email|

xredline1@gmail.com

xredline2@gmail.com

xredline3@gmail.com  
  
Files|

C:\ProgramData\Synaptics

C:\ProgramData\Synaptics\Syanptics.exe  
  
Urls|

http://xred.site50.net/syn/SUpdate.ini

http://xred.site50.net/syn/SSLLibrary.dll

https://www.dropbox.com/s/fzj752whr3ontsm/SSLLibrary.dll?dl=1

https://docs.google.com/uc?id=0BxsMXGfPIZfSVlVsOGlEVGxuZVk&export=download

https://docs.google.com/uc?id=0BxsMXGfPIZfSVzUyaHFYVkQxeFk&export=download

http://freedns.afraid.org/api/?action=getdyndns&sha=a30fa98efc092684e8d1c5cff797bcc613562978  
  
Registry|

HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run：key->"Synaptics
Pointing Device Driver"  
  
## 解决方案

基于上面的分析，就可以编写修复工具了。工具使用的也是Delphi编写的，为了分析这个病毒，稍微了解了一下Delphi，正好Delphi提供了一个很方便使用图形界面库。[cdj68765
](https://www.52pojie.cn/thread-1066827-1-1.html)前辈也提供了一个命令行版本的修复工具，是用
c#写的。对于把xlsm修复为xlsx，前辈使用了Open_XML_SDK进行修复，这种方式更好。我使用的是和恶意代码一样的方式（COM组件）进行修复，这是一个取巧的方式，但是因为xlsm中的VBProject被加密了，导致通过COM组件的方式无法读取到宏代码进行特征判断后再修复，这里用到了一个折中的方案进行特征判断，下面会说明。

代码和工具下载在这里：<https://github.com/forTheBest12138/RepairerForXredWorm>

清理效果如下，目前只会扫描
Desktop、Downloads、Documents目录及其子目录。如果不在这些目录下的文件可以手动输入进行修复，目录和文件路径都行。

![1638092360_61a34e4841df92427e666.png!small?1638092362338](https://image.3001.net/images/20211128/1638092360_61a34e4841df92427e666.png!small?1638092362338)

代码修复思路说明：

  1. 寻找病毒进程并关闭，这边病毒开机启动后一直后台运行
  2. 清除自启动项，及其对应的文件
  3. 修复EXE文件，判断标准是 EXE文件是否包含EXEVSNX和 EXERESX资源节，原理很简单，不赘述。![1638093868_61a3542cbe90546074df2.png!small?1638093870781](https://image.3001.net/images/20211128/1638093868_61a3542cbe90546074df2.png!small?1638093870781)
  4. 修复XLSX文件，使用COM组件的方式其实就和手动用Excel进行操作是一样的。所以我的思路是将xlsm" **另存为/SaveAs** "为xlsx格式，就会直接剔除掉宏代码，就和手动用Excel将xlsm保存为xlsx的效果是一样的，对应的代码就是图中标号3的地方。有几个坑点，图中标号1处的代码表示打开xlsm文件时是否执行宏代码，默认为1，即执行，所以一定要设置成3！！！这个选项好像不受宏执行策略的影响。标号2处的代码是来判断xlsm的宏代码中是否有特定的字符串，这样就可以先进行特征匹配判断其是否是被感染的xlsm文件，再进行修复，但是因为xlsm文件中的VBProject被加密，无法读取到宏代码。所以这部分代码无法使用，上面提到的折中的方案就是判断VBProject是否被加密再进行修复。所以特殊情况就是一个正常的xlsm文件有被加密的VBProject就会被误认为是被感染的文件！如果用Open_XML_SDK的话是可以绕过加密的问题，这样就可以达到100%的修复准确率。![1638094108_61a3551cbb3fce08b20d7.png!small?1638094110812](https://image.3001.net/images/20211128/1638094108_61a3551cbb3fce08b20d7.png!small?1638094110812)同时还要设置运行访问VBA对象模型的注册表项，否则代码是无权读取xlsm的宏代码的。
  5. ![1638094393_61a35639e2e07dacfa092.png!small?1638094395898](https://image.3001.net/images/20211128/1638094393_61a35639e2e07dacfa092.png!small?1638094395898)感染过程中生成的"._cache_"前缀文件和“~$cache1"文件也会清理掉。

## 参考连接&结语

文章如果有不正确的地方请指正。代码问题可以在github上提交issues。

前辈们分析的文章在这里。

<https://s.tencent.com/research/report/880.html>

<https://www.52pojie.cn/thread-1066827-1-1.html>

[https://www.freebuf.com/articles/terminal/222991.html](../articles/terminal/222991.html)

  

