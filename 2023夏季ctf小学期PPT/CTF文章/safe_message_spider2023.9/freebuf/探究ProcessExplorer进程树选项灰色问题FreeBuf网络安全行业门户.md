## 前言

Process Explorer是由SysInternals创建的用于Microsoft
Windows的免费任务管理器和系统监视器，SysInternals已被Microsoft收购并重新命名为Windows
Sysinternals。Process
Explorer可以看成是一个加强版的任务管理器。在较早的Windows版本中，任务管理器提供的功能是非常简单的（比如查看CPU、内存的使用情况，强制结束进程等），很难满足我们高级一些的需求。在这种情况下，Process
Exploere就应运而生了，大大的方便了我们工作中监测进程和排除故障的工作。

## 目的

这是一款在恶意软件研究与分析的过程中也算是会用到的工具，所以本文会对其中一个比较特别的问题进行探究（主要是网上都是瞎写，实在看不下去了）。其实研究对于每一个人来说都不是一件很遥远的事情，英文research的解释为研究、考证，通过re前缀可以知道，需要不断的搜索保持好奇，而搜索的目的是能避免重复的工作，希望能站在巨人的肩膀上继续向前。

## 探究

所以如果很自然的一搜索关于这个问题的关键字，就会得到如下结果，但是都是不对的。

![](https://image.3001.net/images/20200801/1596252472.png!small)

既然中文文章信不过，通过搜索英文内容，得到了如下内容，不过通过时间比对，以下是2009年，而上面的中文内容为2011年，估计也是从这里借鉴过去的，不过很不幸，这也是不对的。

![](https://image.3001.net/images/20200801/1596252530.png!small)

在Win10环境下，管理员权限打开这个工具，会发现这个选项是灰色的，但是请注意，此时已经是进程树状态了，那么如何恢复到不是进程树状态且该选项是可选的呢？

![](https://image.3001.net/images/20200801/1596252560.png!small)

Windows上的软件大多对于配置方面都离不开注册表，作为统一管理配置的自带工具，在Win7下通过在该软件的特定注册表项下找到了非常明显的子项名称【ShowProcessTree】，目前值是1，将其改成0试试，如下。

![](https://image.3001.net/images/20200801/1596252586.png!small)

![](https://image.3001.net/images/20200801/1596252605.png!small)

改完之后，再打开软件，会发现此时选项不是灰色了，是可选的，如下。

![](https://image.3001.net/images/20200801/1596252632.png!small)

通过上面的实践，我们大致可以知道如果不想展示进程树，直接设置为0就可以了。

![](https://image.3001.net/images/20200801/1596252663.png!small)

![](https://image.3001.net/images/20200801/1596252672.png!small)

![](https://image.3001.net/images/20200801/1596252684.png!small)

## 结论

所以，并没有这些文章写的这么玄乎，仅仅需要多动手自然就会琢磨出来。当点击Show Process
Tree后就会以进程树形式展示进程，然后变成灰色，接着软件就将对应注册表值设置成1，如果要恢复成原来的配置（选项可选，不是以进程树展示，直接通过修改注册表值变成0，然后重启系统即可）。

## 玄乎文章链接

<https://blog.csdn.net/knityster/article/details/6311388>

<https://carlupq.wordpress.com/2009/08/06/sysinternals-microsoft-httpsysinternals-com-process-explorer-show-process-tree-menu-item-disabled-greyed-out/>

