**最近，我发现了一种非常有趣的可用来绕过UAC，并以High Mandatory Level启动进程的方法。下面，让我来重现这个过程。**

1\. 以常规用户身份启动cmd.exe。

2\. 确认完整性级别：

    
    
    C:\test>WHOAMI /Groups | FIND "S-1-16"
    Mandatory Label\Medium Mandatory Level Label S-1-16-8192

3\. 启动：

    
    
    sdclt /configure

**![sdclt1.png](https://image.3001.net/images/20180912/1536715254_5b9869f625534.png!small)**

4\. sdclt.exe程序自动提权。

5\. 备份文件；这里我创建了一个存放有少量文件的虚拟文件夹c:\test，并对它进行了备份。

6\. 等待完成。

![sdclt2.png](https://image.3001.net/images/20180912/1536715270_5b986a06dd4b2.png!small)

7\. 备份完成后，我们转到备份列表恢复这些备份文件。

![sdclt3.png](https://image.3001.net/images/20180912/1536715295_5b986a1f719c8.png!small)

8\. 选择backup，搜索c:\test勾选并执行恢复操作（由于文件并不大，因此很快就能完成）。

![sdclt4.png](https://image.3001.net/images/20180912/1536715311_5b986a2f8288b.png!small)

9\.
文件恢复完成后，会有一个提示面板。通过面板的提示信息可以得知，有一些程序或系统文件被跳过未能恢复。这里有一点非常重要，就是至少要有一些文件是被成功恢复的，否则将不会在面板中看到logs文件。

![sdclt5.png](https://image.3001.net/images/20180912/1536715330_5b986a4203d68.png!small)

10\. 单击View Log file。

11\. 这将会以特权身份为我们打开Notepad.exe。

12\. 在Notepad中，我们依次点选menu File -> Open -> c:\windows\system32。

13\. 在列表中输入cmd*.*找到cmd.exe程序。

14\. 启动cmd.exe。

15\. 可以看到，此时的cmd.exe具有S-1-16-12288/High Mandatory Level/高完整性级别。

    
    
    C:\Windows\System32>WHOAMI /Groups | FIND "S-1-16"
    Mandatory Label\High Mandatory Level Label S-1-16-12288

16\. 现在你可以启动任何程序，并且它们都将以High Mandatory integrity level运行。

最后，如果你有好的思路请与我分享。同时，你也可以关注我的[twitter](https://twitter.com/Hexacorn/status/1038136386426167296)，每当我有新的想法我都会及时的进行更新。谢谢！

 ***参考来源：[hexacorn](http://www.hexacorn.com/blog/2018/09/07/a-bit-of-a-quackery-how-to-elevate-w-o-doing-a-single-thing/)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

