![](https://image.3001.net/images/20191221/1576942413_5dfe3b4de0e60.jpg!small)

**最近，我注意到Instagram增加了大量的[版权说明部分](https://help.instagram.com/126382350847838)，其中声称，当用户上传到Instagram的媒体文件侵犯了其他地方的知识版权后，就会显示一个通知反映媒体文件的版权上诉信息，之后Instagram会自动删除该文件。**

Instagram版权说明中有这样的描述：

> 收到权利所有人投诉 Instagram 上的内容侵犯其知识产权的举报后，我们可能需要立即从Instagram 删除相关内容，而不会事先联系您。
>
> 如果 Instagram
> 根据通过在线表单提交的知识产权举报删除您发布的内容，就会向您发送通知消息，并附上提交举报的权利所有人的姓名和电子邮箱或者举报详情。您如果认为相关内容不应该被删除，则可以直接联系提交举报的用户，尝试解决此问题。

根据以上说明，所以我决定对此功能进行一些测试。我就上传了一个包含某首音乐面临版权问题的视频文件，经测试发现，Instagram会使用一个GET请求来删除该文件。其删除操作路径为：

> <https://www.instagram.com/media/>{MEDIA_ID}/copyright/dismiss_am/

其中的MEDIA_ID代表将要被删除的视频文件或发贴ID，后来我发现，只要获取对受害者所发贴或上传的相关文件ID号，然后把上述链接发送给受害者用户后，都会把对方发贴或相关文件删除掉，造成间接的CSRF场景，实现恶意破坏目的。该Bug在Instagram的手机APP或网页版中都能成功复现。

以下是在安卓版APP中的复现：

![](https://image.3001.net/images/20191221/1576942023_5dfe39c7b9046.gif!small)以下是在网页版中的复现：

![](https://image.3001.net/images/20191221/1576942352_5dfe3b10c5b3b.gif!small)

##  漏洞上报及处理进程

> 2019.1.29 漏洞初报
>
> 2019.1.29 漏洞分类
>
> 2019.1.30 漏洞修复
>
> 2019.2.14 Facebook奖励了$3,000

![](https://image.3001.net/images/20191221/1576942519_5dfe3bb7bc8e0.png!small)***参考来源：[dynamicworld](https://blog.darabi.me/2019/12/instagram-delete-media-csrf.html)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

  

