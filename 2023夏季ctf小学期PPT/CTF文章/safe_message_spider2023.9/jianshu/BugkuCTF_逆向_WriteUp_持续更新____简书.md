BugkuCTF—逆向—WriteUp(持续更新)

[ syxvip](https://www.jianshu.com/u/380fd93bae2c)关注赞赏支持

# BugkuCTF—逆向—WriteUp(持续更新)

BugkuCTF—逆向—WriteUp(持续更新)

0X01  
第一次做逆向的有关题目，实在是丈二的和尚摸不着头脑，借鉴大牛的思路慢慢那进行练习。

# 入门逆向：

直接上 ida 软件可以自行下载  
在main函数中按下

  

image.png

将exe文件下载下来。

  

exe

上 IDA 神器！

image.png

题目提示了 flag的题目是 flag开头的，然后后面跟着大括号进行包围。

    
    
    flag{_N3t_Rev_1s_E4ay_}
    

* * *

0X02  
用OD也可以找出flag

拖入OD后 右击查找---》所有参考文本字符串----》答案

image.png

BugkuCTF_逆向_逆向入门 WriteUp

image.png

  

先进行查壳 提示不存在PE

  

image.png

放入OD中看下，提示不是有效的32位PE文件

  

提示

怎么办。。。。用winhex打开看下，是个PNG文件，然后提示了base64编码。

image.png

base64 转图片：<http://www.vgot.net/test/image2base64.php>

扫码

然后扫码得出FLAG：

  

image.png

    
    
    bugku{inde_9882ihsd8-0}
    

BugkuCTF_逆向_Easy_Re 60 WriteUp

png

把文件拖入OD中先运行一下，然后右击中文搜索引擎---》智能搜索  
答案就出来了

image.png

    
    
    DUTCTF{We1c0met0DUTCTF}
    

* * *

在运行过程中，寄存器也爆出了flag

# 游戏过关

image.png

上来先试了一下  
有八个选项  
那么来挨个试一下  
他是按照每个选选择来进行输出排序  
当我输到8号时  
flag就自动弹出来了  
不过正确的解法应该不是这样的！

image.png

  

当我输到8号时  
flag就自动弹出来了  
不过正确的解法应该不是这样的！

  

image.png

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [3.9](https://www.jianshu.com/p/3eda2561db5f)

想学习了，觉得不能玩手机了，就大胆的断网。几分钟就拿起手机看消息还得承受没有人找你的无聊。你得想，你怎么肯定会...

[尔羽_74d6](https://www.jianshu.com/u/200f383834ed)阅读 125评论 0赞 0

  * [自制美白大法，不花冤枉钱！一个月真的白了](https://www.jianshu.com/p/a514529ba2b3)

仗着自己腿直天生喜欢露腿的我最喜欢过夏天，我腿直我骄傲然鹅，虽然是捂了一个冬天的大白腿，照镜子就发现，我擦、膝盖那...

[少女委托人](https://www.jianshu.com/u/7b95f1e8fc3d)阅读 946评论 0赞 0

  * [信人，信任。](https://www.jianshu.com/p/b237065461a1)

之前有很要好的朋友提醒过我：“你这人没什么大毛病，唯一的缺点大概就是太容易相信别人，你这样迟早要吃亏的。”我笑着回...

[乔纳夫](https://www.jianshu.com/u/d4d12e949318)阅读 429评论 1赞 5

  * [SpringMVC 消息转换器HttpMessageConverter](https://www.jianshu.com/p/d7355cd8166c)

@RequestBody将HTTP请求正文转换为适合的HttpMessageConverter对象。(请求报文到j...

[火星人想回火星](https://www.jianshu.com/u/40feb045288b)阅读 642评论 0赞 0

  * [第一次和女生约会不要犯的错误 男性关注最多的公众号](https://www.jianshu.com/p/f957806c56e6)

在和女生第一次约会的过程中，不要犯一些错误，不然女生不会理你的。可能你们以后就没有了交集。 不要谈论她的问题和提供...

[砸小车](https://www.jianshu.com/u/5b821ab56c28)阅读 130评论 0赞 0

 