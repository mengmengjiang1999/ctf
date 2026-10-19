## 旁白

### 本篇章是为初接触内网开始的xdm，前面有一章是搭建环境的，老哥们轻点喷(⊙o⊙)…【文章涉及内容仅供参考；该实验在虚拟机环境下完成】

上篇说道web 03的那个服务器不知道什么原因，搭建的网站出现一些小问题，我这里为了显示效果就直接拿到了shell了。嘿嘿

![](https://image.3001.net/images/20210811/1628659217_61135e11f3fa795333b17.jpg!small)下面我们拿到shell之后用到两种提权突破方式，使用mysql提权和msf提权

## Mysql提权

UDF概况：

> UDF（user defined
> function）用户自定义函数，是mysql的一个拓展接口。用户可以通过自定义函数实现在mysql中无法方便实现的功能，其添加的新函数都可以在sql语句中调用，就像调用本机函数一样

嗯~说白了就是利用mysql的使用者执行系统命令，如果mysql是以system权限运行的，那么执行命令时就是system权限，administrator运行时同理。
当然，利用时是有条件的

 ** **windows下udf提权的条件****

> 如果mysql版本大于5.1，udf.dll文件必须放置在mysql安装目录的\lib\plugin文件夹下
>
> 如果mysql版本小于5.1， udf.dll文件在windows server
> 2003下放置于c:\windows\system32目录，在windows server 2000下放置在c:\winnt\system32目录。
>
> 掌握mysql数据库的账户，从拥有对mysql的insert和delete权限，以创建和抛弃函数。
>
> 拥有可以将udf.dll写入相应目录的权限

我这里mysql是大于5.1：提权方法如下

>
> 必须要把udf.dll文件放到mysql安装目录的lib\plugin文件夹下才能创建自定义函数。该目录默认是不存在的，需要使用webshell找到mysql的安装目录，并在安装目录下创建lib\plugin文件夹，然后将udf.dll文件导出到该目录

![1628659693_61135fed72d0bc713d736.png!small?1628659692522](https://image.3001.net/images/20210811/1628659693_61135fed72d0bc713d736.png!small?1628659692522)

自问自答↓

问：那么现在问题来了，udf文件去哪里整呢？

答：可以使用sqlmap下的udf文件需要使用cloak.py进行异或解码在此之前需要进行信息收集了解目标主机的基本信息 对症下药

我这里是32位的

![1628659783_611360477585e1670f287.png!small?1628659782639](https://image.3001.net/images/20210811/1628659783_611360477585e1670f287.png!small?1628659782639)

注意：这个主机版本及架构一定要确认好，不然没反应，别问我怎么知道的

> show variables like '%compile%'; #查看主机版本及架构
> 如果是win32的使用sqlmap的32位dll文件，64的一样操作
>
> show variables like 'plugin%'; #查看 plugin 目录

这时候我们通过webshell进入数据库操作

![1628660038_6113614650950d2be9923.png!small?1628660037359](https://image.3001.net/images/20210811/1628660038_6113614650950d2be9923.png!small?1628660037359)

> create function sys_eval returns string soname "udf.dll"; --引用共享库文件创建存储过程
>
>  
>
>
> 语句解释：
>
> CREATE [AGGREGATE] FUNCTION function_name RETURNS {STRING|INTEGER|REAL}
> SONAME '文件名'
>
> [AGGREATE]是聚集函数的表示，系统定义的聚集函数比如有COUNT()、AVE()、MN()、MAX()、SUM() 可有可无
>
> SONAME
> 'file'表示这个函数从哪个文件里面引入，而这个文件一般是动态链接库，windows下是dll，linux是so，并且这个文件要在mysql的plugin目录下
>
>  
>
>
> select * from mysql.func where name = 'sys_eval'; #查看创建的sys_eval函数
>
> select sys_eval('whoami'); #使用系统命令

![1628660183_611361d7f2ded3de96838.png!small?1628660183043](https://image.3001.net/images/20210811/1628660183_611361d7f2ded3de96838.png!small?1628660183043)

可以看到mysql通过引用我们上传的dll文件进行创建了函数

执行命令看看

![1628660277_61136235cc13d434c7434.png!small?1628660276896](https://image.3001.net/images/20210811/1628660277_61136235cc13d434c7434.png!small?1628660276896)

因为我这里使用administrator启动的环境，所以是administrator，这里我们就不再继续操作了

嗯~这样就相当于提权成功了，可以向机器添加用户，加入管理组，开启3389，到桌面进行计划任务再进行提权一次，老弟也是刚接触，只有这样的思路！如果有想指教的师傅，我这随时恭候，嘿嘿

## MSF提权【flag1】

回到正题！我们最终是要拿system权限的然后进行那个flag的文件查看的，不用上面的那个方法，我们用nc反弹到msf上面一个session进行操作

这时候要注意，嗯~端口转发的时候要转发到m0n01的外网ip，msf进行本地端口监听，如果直接转发kali本地ip的话，这台03根本找不到的，通过webshell上传nc

![1628660384_611362a0607266ea25f1b.png!small?1628660383454](https://image.3001.net/images/20210811/1628660384_611362a0607266ea25f1b.png!small?1628660383454)

MSF进行监听

![1628660428_611362ccd475241f40101.png!small?1628660428252](https://image.3001.net/images/20210811/1628660428_611362ccd475241f40101.png!small?1628660428252)

![1628660440_611362d8cac4481efabba.png!small?1628660439861](https://image.3001.net/images/20210811/1628660440_611362d8cac4481efabba.png!small?1628660439861)

这时候监听出现了问题，连接一直断掉，小场面，我们使用木马反弹也是行得通的，应该是防火墙的一些问题

![1628660478_611362fe1b41c0b0a1acb.png!small?1628660477612](https://image.3001.net/images/20210811/1628660478_611362fe1b41c0b0a1acb.png!small?1628660477612)

这时候直接getsystem就行 为了演示效果把防火墙什么的都关闭了，当然实战的时候就不是这么容易了。

再次声明：这篇文章只是提供一下思路为初接触的新的xdm

![1628660512_611363202f7aba7b16fbf.png!small?1628660511283](https://image.3001.net/images/20210811/1628660512_611363202f7aba7b16fbf.png!small?1628660511283)

查看flag文件

![1628660528_61136330c9826abe4ab6d.png!small?1628660527957](https://image.3001.net/images/20210811/1628660528_61136330c9826abe4ab6d.png!small?1628660527957)

## sudo滥用提权【flag2】

我们现在已经拿到了一个flag了，现在进行端口扫描看看防火墙上都转发了哪些端口(实战的时候就是目标网站了)，当然，在此之前也可以进行端口扫描，但是我这为了演示流程。

![1628660706_611363e27029cac32f039.png!small?1628660705646](https://image.3001.net/images/20210811/1628660706_611363e27029cac32f039.png!small?1628660705646)

可以看到还有一个1235端口，打开一看是一个durpal站

![1628660740_61136404a3c80600c9b83.png!small?1628660739795](https://image.3001.net/images/20210811/1628660740_61136404a3c80600c9b83.png!small?1628660739795)

这时候我们利用：https://vulhub.org/#/environments/drupal/CVE-2018-7602/；这个脚本进行命令执行，因为这个pco需要知道账号密码才可以利用，为了演示效果我们还是“再次开一次挂”
-c是执行的命令 后面的两个drupal分别是账号密码

![1628660773_6113642571c4e7a4126f2.png!small?1628660772594](https://image.3001.net/images/20210811/1628660773_6113642571c4e7a4126f2.png!small?1628660772594)

现在我们可以执行命令了，也就是说我们可以反弹shell或者写入一句话了，我这直接反弹shell了 然后通过sudo滥用提权查看文件，这里利用的是ed编辑器

> Linux ed命令是文本编辑器，用于文本编辑。  
> ed是Linux中功能最简单的文本编辑程序，一次仅能编辑一行而非全屏幕方式的操作

![1628660789_611364352df3eb0dad5cd.png!small?1628660788359](https://image.3001.net/images/20210811/1628660789_611364352df3eb0dad5cd.png!small?1628660788359)

嗯~到这也是结束了，本人也是刚接触，也就知道一些“三脚猫功夫”随时恭候师傅们来指导，嘿嘿

![](https://image.3001.net/images/20210811/1628661009_61136511dbbd1b3583a2e.jpg!small)

  

