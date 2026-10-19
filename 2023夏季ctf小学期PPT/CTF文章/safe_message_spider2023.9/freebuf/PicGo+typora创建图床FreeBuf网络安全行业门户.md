这里我采用的是PicGo+typora+gitee创建的图床，目的是为了往后往各个平台发笔记的时候不用再一个个传图片了，爽歪歪，这里记录一下步骤；

要使用的工具：

链接：<https://pan.baidu.com/s/1fgr5bOsz-ROcBtZsAbkoxA>提取码：zcc1

在gitee主页依次点击我的->设置->私人令牌；

![5ecc616394a0858bd0de27954f7a2e4](https://image.3001.net/images/20210619/1624034865_60ccce31521e821998d30.png!small)

![25a721f98d7f6d69d2e46523f0cd646](https://image.3001.net/images/20210619/1624034866_60ccce32238210b36c973.png!small)

![image-20210618230734537](https://image.3001.net/images/20210619/1624034867_60ccce3308dc145df64e5.png!small)

![image-20210618230743950](https://image.3001.net/images/20210619/1624034868_60ccce3412c7db9256fbc.png!small)

这里私人描述可以随意写；

![image-20210618230848429](https://image.3001.net/images/20210619/1624034869_60ccce352b03106a2f1e3.png!small)

输入密码；

![image-20210618230907173](https://image.3001.net/images/20210619/1624034870_60ccce36323b3a409c630.png!small)

把令牌复制下来，后面会用到；

然后再gitee下创建一个开源项目：

![image-20210618224731711](https://image.3001.net/images/20210619/1624034871_60ccce3722ea1a410e47e.png!small)

这里仓库名称可以随意起，但是尽量都是小写字母，因为有师兄弟做这个的时候踩了坑，带的大写字母被自动转换成了-和小写，导致后面的图片一直上传不成功，报错原因是找不到要传的文件名称，所以这里提个醒哈，记住了！！仓库一定要是开源的！

![image-20210618225057399](https://image.3001.net/images/20210619/1624034872_60ccce382f95f791bbbe8.png!small)

这里我创建的是仓库名称是img，所以接下来就按img来展示；

![image-20210618225421703](https://image.3001.net/images/20210619/1624034873_60ccce39433853589faf0.png!small)

打开PicGo，点击插件设置，搜索gitee，出来的有两个插件，必须要先安装`node.js`才能安装插件，node.js安装包上面工具包有！

![image-20210618225651649](https://image.3001.net/images/20210619/1624034874_60ccce3a0f6ec62ce08af.png!small)

我用的是后者那个低版本的，也可以使用前者，使用前者的步骤下面再说哈；安装完之后，点击设置小图标，点击配置uploader-gitee;

![image-20210618231143224](https://image.3001.net/images/20210619/1624034876_60ccce3c881d958661e65.png!small)

进入配置界面，填入刚刚复制的token，path是必填的，path这里随机取个名字，customPath选择年月；

![](https://image.3001.net/images/20210619/1624034880_60ccce401a11521621c51.png!small)

repo这里我遇到了一个坑，我们可以看见repo命名是
gitee的名字/仓库名字，这里gitee的名字我刚开始用的是我个人主页的名字，发现不对，导致图片一直上传不了，后面经一个大佬指点，发现是路径中的名字，这里不确定的可以看这里，划线的地方就是上图中repo的前半部分，后半部分就是你的仓库名：

![d490d80ec1880e59dc87d24ca367f78](https://image.3001.net/images/20210619/1624034881_60ccce4116705fb18a23e.png!small)

![94fc3316ed7b83856177b2887bf605e](https://image.3001.net/images/20210619/1624034882_60ccce421f51b223865ca.png!small)

创建好之后，点击图床设置下拉框中的gitee，点击设为默认图床，不然后面会遇到图片上传不成功的问题，不要问我怎么知道的。

![](https://image.3001.net/images/20210619/1624034883_60ccce4364449d2db9a7b.png!small)

点击PicGo设置中的设置server，看看这里的端口是不是默认的36677，不是的话改一下，这里注意每次重启端口都会重新生成，所以每次重启使用时先检查端口情况；

![image-20210618232512229](https://image.3001.net/images/20210619/1624034884_60ccce449d06cf32f0478.png!small)

![image-20210618232529286](https://image.3001.net/images/20210619/1624034885_60ccce4580e1da19851a8.png!small)

然后打开typora，点击文件->偏好设置->图像，上传服务那里选择PicGo（app）；PicGo路径选择你安装的PicGo.exe路径；

![image-20210618233104553](https://image.3001.net/images/20210619/1624034886_60ccce4676c94dcd6cdd2.png!small)

点击验证图片上传选项

![688d6386874c6ef7f3513706065453c](https://image.3001.net/images/20210619/1624034887_60ccce47731020b8795b0.png!small)

出现下图机表示图床配置成功，从这也可以看见其默认端口是36677，对应了我们上面修改的端口；可以看见gitee下面已经有图片；

![0bf1081ac58bf3ab95573b7ec9954d8](https://image.3001.net/images/20210619/1624034888_60ccce485a279013ba2a1.png!small)

![b7908a4575e949eeb423c7734cbc5d7](https://image.3001.net/images/20210619/1624034889_60ccce492a7eb0c4f6e11.png!small)

上面有提到过我选择的是第二个低版本的插件，那如果选择的是第一个版本的插件的话是怎样的呢？

![image-20210618233545755](https://image.3001.net/images/20210619/1624034889_60ccce49edb4effcd15b1.png!small)

这里我发现他们只有配置gitee的页面不一样，可以看见这个版本的配置页面多了owner选项，这里owner随机设置一个名字，repo还是不变，设置好之后，其他的步骤都是一样的；

![image-20210618233743607](https://image.3001.net/images/20210619/1624034890_60ccce4ac151dc2e4d35c.png!small)

参考链接：<https://www.jianshu.com/p/4740993c5843>

