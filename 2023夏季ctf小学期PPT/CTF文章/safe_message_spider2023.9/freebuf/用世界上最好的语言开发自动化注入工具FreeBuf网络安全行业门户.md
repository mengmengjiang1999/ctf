  
  

本文使用世界上最好的语言(PHP)针对某h站系统而开发的自动化注入工具。

首先来明确工具开发中的几个点：

1、正常页面和错误页面的区别

2、该工具自动化判断表名以及表中字段的数据长度

3、使用缓存机制（读取和写入）

4、使用php cli（命令行）模式

这里可能会有人疑问了“为啥使用php？不使用python”，因为这个注入点比较特殊，是一个302页面跳转处的注入，从数据库中查询到某个域名后会输出到页面，然后跳转，否则查询不到某个域名的情况下造成死循环，输出页面的代码如下：

<script language="javascript" type="text/javascript">

document.write('<a id="go" href="http://www.52six.xyz"></a>');

go.click();

</script>

Href参数有值的情况下为正常，否则异常

<script language="javascript" type="text/javascript">

document.write('<a id="go" href=""></a>');

go.click();

</script>

异常之后就会存在死循环，因为href都为空了。

这里因为是302页面，python获取不到页面内容，而php则可以获取到内容，或许是我不擅长使用python，对php情有独钟的原因吧！

  

对于工具开发，必不可少的是http请求函数，php现成的有file_get_contents，相对来说，这个系统函数并不好用，因为请求不到的使用就会产生异常，当然我们不希望程序运行中突然出现异常就被中断了，然而我们要用的curl函数，下面将curl封装了一个函数：

![图片.png](https://image.3001.net/images/20200131/1580481075_5e343a3352dd0.png!small)

我们先来测试一下，主要我们还是要测试是否能获取到302页面的内容，代码如下：

![图片.png](https://image.3001.net/images/20200131/1580481079_5e343a37c6aef.png!small)

获取到的内容如下：

![图片.png](https://image.3001.net/images/20200131/1580481101_5e343a4da169b.png!small)

我使用-----------------------------------------------将正确页面和错误页面分割开来,href参数中有值的是正常页面，否则为异常页面

我们接着往下，因为现在大多数自动化工具都是采用接收命令行参数的方式，比如SQLMAP：

Python sqlmap.py -u “” --batch --dbms “”

也就是这样的，我们也采用这样的方式吧！下面我们来具体的实现：

Php cli模式接收命令行参数的超全局数组为$argv

![图片.png](https://image.3001.net/images/20200131/1580481108_5e343a542d086.png!small)

![图片.png](https://image.3001.net/images/20200131/1580481114_5e343a5a996df.png!small)

首先我们要想到如何实现-u啊这些的，所以这里我们还是将获取的东西封装并且命名为GetHostId，在这个函数中我们不需要参数，我们需要获取全局变量可以使用两种形式$GLOBALS和global
$argv

![图片.png](https://image.3001.net/images/20200131/1580481122_5e343a6252dd9.png!small)

![图片.png](https://image.3001.net/images/20200131/1580481127_5e343a67b442a.png!small)

![图片.png](https://image.3001.net/images/20200131/1580481132_5e343a6c5bc92.png!small)

![图片.png](https://image.3001.net/images/20200131/1580481144_5e343a780b4b8.png!small)  

这里我们还是使用$GLOBALS的方式获取，因为我们最后会将这些函数封装在一个类里面，这样更加灵活，好了，我们继续吧！

根据上图我们可以知道，数组下标为0的数值是无用的，所以我们需要删掉$GLOBALS[“argv”][0]

![图片.png](https://image.3001.net/images/20200131/1580481157_5e343a85a76aa.png!small)

这里第一行就将下标为0的值删掉了，因为第1个就是执行的文件名，所以直接删掉，然后进行赋值，我们接着往下来，我们命令行中需要两个参数一个为--host或者-h，另一个为--id，函数已封装完毕

![图片.png](https://image.3001.net/images/20200131/1580481165_5e343a8d01fe1.png!small)

这里我们当前文件接收命令行参数就有了两种形式：

![图片.png](https://image.3001.net/images/20200131/1580481177_5e343a994114c.png!small)

程序这样做了以后就显得不灵活了，因为这里的位置不能随意调换就比较懊恼，那么我们再封装一个函数

![图片.png](https://image.3001.net/images/20200131/1580481185_5e343aa1d8c7b.png!small)

![图片.png](https://image.3001.net/images/20200131/1580481194_5e343aaa88d8f.png!small)

这样获取命令行参数就可以不分先后顺序了！！这里已经获取到了域名以及id，我们继续往下，获取到域名以及id过后，我们还需要另一个参数--batch，如果这个参数存在那么我们默认使用http，否则则在命令行中获取，已将获取这部分封装成了函数：

![图片.png](https://image.3001.net/images/20200131/1580481200_5e343ab0f3048.png!small)

![图片.png](https://image.3001.net/images/20200131/1580481211_5e343abb50429.png!small)  

GetInput函数是获取命令行中的值，而GetHttp是调用GetInput获取用户输入的是https还是http协议

这里获取到http或者https协议拼接到host后，我们将拼接的值进行存活的判断，我们此时封装一个is_survival函数，存活返回true，否则false，判断存活本应判断状态码，但是判断状态码又不是很严格，这里我们使用正则表达式来进行匹配，返回值如下：

![图片.png](https://image.3001.net/images/20200131/1580481231_5e343acf01ecd.png!small)

我们正则所匹配的东西应该是href中的值，那么我们的正则表达式如下：

/href=”(.+)”/i

以上就是判断存活的必要条件，我们继续：

![图片.png](https://image.3001.net/images/20200131/1580481237_5e343ad51f0e1.png!small)

这里存活条件为href中有值的情况下存活，否则是死亡状态，死亡状态有两种情况，一种是无法访问或者输入的id值不正确，我们接着往下走

![图片.png](https://image.3001.net/images/20200131/1580481241_5e343ad90d2bf.png!small)![图片.png](https://image.3001.net/images/20200131/1580481261_5e343aed44f64.png!small)

查询不到内容的时候！

![图片.png](https://image.3001.net/images/20200131/1580481274_5e343afa5a4ce.png!small)

这个函数中同时会自动测试五次，若五次过后依然获取不到那么自动退出，这里我们验证了是否存活，接着我们从字典中获取表名，然后测试取出的表是否存在，那么我们在本地创建一个dictionary目录，并且写入一个名为tables.txt的字典文件：

![图片.png](https://image.3001.net/images/20200131/1580481280_5e343b001f2d3.png!small)

我们接着往下走，这里我们封装两个函数，一个为GetContents，另一个为GetTables

![图片.png](https://image.3001.net/images/20200131/1580481286_5e343b0613313.png!small)

这里我们通过GetTables函数中调用GetContents函数获取字典内容，然后返回，返回到GetTables函数中，将内容以回车分割为数组并且返回数组，那么接下来我们还要再接着封装一个名为TablesSurvival的函数，然后返回值为数组，这里我们将查表的SQL拼接上去

+and+exists(select%20*%20from%20admin)

![图片.png](https://image.3001.net/images/20200131/1580481290_5e343b0ac25d8.png!small)
![图片.png](https://image.3001.net/images/20200131/1580481295_5e343b0f2fd48.png!small)

![图片.png](https://image.3001.net/images/20200131/1580481311_5e343b1f79392.png!small)

这里我们成功测试表名存在之后再封装一个名为GetColumns的函数，此函数获取dictionary目录下的columns.txt文件中的内容，并以回车分割，具体实现：

这里字段名的格式和表名的格式略有不同，格式如下：

![图片.png](https://image.3001.net/images/20200131/1580481319_5e343b27145c6.png!small)

  

![图片.png](https://image.3001.net/images/20200131/1580481323_5e343b2be4d5d.png!small)

![图片.png](https://image.3001.net/images/20200131/1580481335_5e343b37a676e.png!small)![图片.png](https://image.3001.net/images/20200131/1580481351_5e343b476a7a7.png!small)  

到这里为止，我们的程序已经可以自动化测试表名以及字段名，因为前面相同功能的函数有些重复，我们这里来进行合并，比如GetColumns和GetTables，将这两个函数合并后名称改为GetTablesOrColumns：

![图片.png](https://image.3001.net/images/20200131/1580481356_5e343b4c7288d.png!small)![图片.png](https://image.3001.net/images/20200131/1580481360_5e343b507e12e.png!small)![图片.png](https://image.3001.net/images/20200131/1580481388_5e343b6c308ba.png!small)

接着我们再将TablesSurvival和ColumnsSurvival合并为TablesOrColumnsSurvival:

![图片.png](https://image.3001.net/images/20200131/1580481394_5e343b72ade20.png!small)![图片.png](https://image.3001.net/images/20200131/1580481397_5e343b75d005a.png!small)

运行一下

![图片.png](https://image.3001.net/images/20200131/1580481427_5e343b9353116.png!small)

代码精简了以后，还是一样的运行结果，我们接着来，这个时候我们知道了表名以及字段名称，既然是自动化工具，自然少不了测试字段中内容的长度，也将获取字符长度的代码封装成一个名为GetStringLength，返回值为数组:

![图片.png](https://image.3001.net/images/20200131/1580481432_5e343b9848606.png!small)![图片.png](https://image.3001.net/images/20200131/1580481435_5e343b9ba5aa6.png!small)![图片.png](https://image.3001.net/images/20200131/1580481461_5e343bb54750c.png!small)

这里可以看到我们返回的格式为[表名,字段长度=>字段名,字段长度=>字段名]，然后我们已经得知了表名，字段名以及字段内容长度，接着我们定义一个名为SqlInjection，我们这里就不需要返回值了。

![图片.png](https://image.3001.net/images/20200131/1580481466_5e343bba913bf.png!small)![图片.png](https://image.3001.net/images/20200131/1580481470_5e343bbe3811f.png!small)![图片.png](https://image.3001.net/images/20200131/1580481497_5e343bd9bca62.png!small)

到这里呢！基础的已经写完成了，但是我们还需要一个机制，那就是缓存，我们将获取到的内容写入到文件夹下，我们的缓存目录结构如下

Data目录->域名目录->表名目录->字段文本，那么我们现在封装一个名为TextPut函数:

![图片.png](https://image.3001.net/images/20200131/1580481502_5e343bdec0cca.png!small)

随后我们在GetStringLength中调用textput函数，将字段中字符长度以及字段名写入到以域名的名称命名的文本中

![图片.png](https://image.3001.net/images/20200131/1580481507_5e343be3dcbf3.png!small)

写入文本格式如下：

![图片.png](https://image.3001.net/images/20200131/1580481512_5e343be89d59e.png!small)

接着往下走，然后在SqlInjection函数中调用并将注入到的数据写入文件中

![图片.png](https://image.3001.net/images/20200131/1580481517_5e343bed23482.png!small)

这样我们就成功将获取到的数据写入到文件中，但是还要进行一次判断，封装一个名为is_cache函数：

![图片.png](https://image.3001.net/images/20200131/1580481523_5e343bf395fa7.png!small)

并且将SqlInjection函数增加一个cache形参，方便缓存机制

![图片.png](https://image.3001.net/images/20200131/1580481527_5e343bf7db5c8.png!small)![图片.png](https://image.3001.net/images/20200131/1580481531_5e343bfb536ed.png!small)

最终程序调用如上，我们还应该写一个名为DumpContent的函数，将注入到的数据打印出来

![图片.png](https://image.3001.net/images/20200131/1580481536_5e343c003c029.png!small)

程序调用最终如下：

![图片.png](https://image.3001.net/images/20200131/1580481542_5e343c066f5e1.png!small)![图片.png](https://image.3001.net/images/20200131/1580481546_5e343c0a61faf.png!small)

这里我们来测试一下缓存机制

![图片.png](https://image.3001.net/images/20200131/1580481561_5e343c19142b0.png!small)

这里我们的username字段测试到第四个字符，我们退出程序！

![图片.png](https://image.3001.net/images/20200131/1580481581_5e343c2dedd30.png!small)

程序果断退出了，接着我们再来运行一下：

![图片.png](https://image.3001.net/images/20200131/1580481598_5e343c3e3da36.png!small)

这里说一下为什么还是在获取第四个字符呢？因为咱们设置的是，只有读取到了写入文件之后才会跳到第五个字符，然而我们这里还没读取到第四个字符，所以还是从第四个字符开始。。。静静的等待程序执行完毕。。。

![图片.png](https://image.3001.net/images/20200131/1580481622_5e343c5649232.png!small)

本次分享就到这里了，勿嫌弃，其实工具开发旨在思路，用什么语言都是一样的，只要可以实现就行。

自动化测试工具地址：https://github.com/only-wait/tools/tree/master/h%E7%AB%99%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7

