原创： k  合天智汇

前言：

标题真不真，继续往下看，为什么要作者选择这个提交平台，一是作者真菜，二是好过吧，只要是存储xss就给过

本篇是作者的xss备忘录阶段小结，所以读者很有福，能得到大量的姿势（小菜姿势，哈哈哈）

现目前容易且主流的漏洞，作者认为有三种，一是框架漏洞，二是逻辑，三是xss

ok，进入我们的主题

1.xss基础知识和分类

2.xss姿势绕过

3.xss工具测试

4.xss防御

5.总结

好像没什么写的。。。

1.dom

2.反射

3.存储

这里推荐一本书《web前端黑客技术揭秘》

作者这里写的常见基础知识，也是里面的笔记，你说实用性就下面作者的操作就行了，因为我们一般都不会关注这么多，你说知识和技术魅力，这个真的不错；杂乱的笔记，大体写出框架和一些作者关注的点；谅解：

a、使用script标签实现的jsonp跨域可以将服务器响应文本以函数参数的形式返回，浏览器解析js代码时直接就执行了

b、常设置httponly，防止打cookie；但是在head的trace方法开启，有httponly的情况下，也可以进行js的cookie操作，称为xst攻击，简单练习链接
http://www.hackdig.com/?01/hack-11.htm

c、常见的外部url链接

    
    
    html:  
    <link href>  
    <img src>  
    <img lowsrc>  
    <img dynsrc>  
    <iframe src>  
    <frame src>  
    <script src>  
    <bgsound src>  
    <embed src>  
    <vedio src>  
    <audio src>  
    <a href>  
    <table backgroup>  
    css:  
    @import “”  
    backgroud:url(“”)

![图片.png](https://image.3001.net/images/20181122/1542876286_5bf66c7e861f0.png!small)  

可使用以下任意办法防御JSON Hijacking攻击

> 首先在请求中添加token（随机字符串）
>
> 再请求referer验证(限制为合法站点，并且不为空) 注意事项 在线json防御被外域恶意调用只限制了referer，但是允许空referer访问：
> 比如本地html，还有某些伪协议远程调用时是没有referer的。从而导致问题持续。所以空referer也是不安全的

e、很有趣的关注点，但是实际过程中，你要先闭合一些东西，才能继续考虑这些，往往作者都没有用到这里来，所以就扩展不深
html和javascript的自解码过程（html环境和js环境）进制编码：16进制 &#xH &#D 十进制
最后的分号可以不要html实体编码&lt;input type=”button” id=”exec_btn” value=”exec”
onclick=”document.write(‘img src@ onerror=alert(1234) / ‘)”/>js自动解码unicode
16进制 纯转义 无意义防御</p><p>f、一些标签内是不会执行js的，如textarea，所以一般都是要闭合它具备html编码的标签title
iframe noscript noframesxmp没有编码功能plaintext
火弧不会，google有ie有解析差异，代码不会执行</p><p>g、浏览器进制常识html&# 10&# 16 多了a-f
a-f大小写不敏感css中16进制还有\6ceval中八进制的\5616进制的\x5c</p><p>h、由于技术和知识原因，下面的这些没有深层次的学习和探讨其实还有csrf
，拖放和点击劫持，flash的xss（书籍作者介绍由于flash沙箱安全，实用性不强，就没有怎样关注了），xss的漏洞利用，劫持技术（重头戏）</p><p>网上有很多姿势</p><p>作者先写一些自己印象深的，再拿出自己常用的那些什么编码，各种事件替换，就不写了，推荐几篇文章，有兴趣可以自己阅读下姿势：</p><p><img
style="margin:15px auto" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876297_5bf66c899837f.png!small"
width="611"
height="104"><br></p><p>我们来挖小商城的xss，因为商城的xss输入点多</p><p>01</p><p>第一步：</p><p>搜索框判断：</p><p>onfocus=alert1
autofocus </p><p>那两个是反引号，实测可用，在不使用 ‘ ” ( )的情况下，但是一般都要闭合value的 "</p><p>“
onfocus=alert('1') autofocus ”</p><p>"onclick="alert(1)</p><p>">&lt;img src=x
onerror=aLert(1)>&lt;!--</p><p>%22>&lt;img src=x onerror=aLert(1)>&lt;!--</p><p>（有趣的现象，url编码能绕过简单的反斜杠）</p><p>见招拆招了，一般都不会费尽心思过滤什么特殊的字符，都是直接函数过滤</p><p>真的过滤了，继续看</p><p>1.输入：</p><p><br><img
style="margin:15px auto" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876310_5bf66c9650b13.png!small"
width="690"
height="251"><br></p><p>事件判断一波，博主两次遇到一个商城cms，漏了两个事件onuoload（页面关闭时触发），onbblclick(双击时触发)</p><p>2.常用的判断一波：</p><p><br><img
style="margin:15px auto" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876317_5bf66c9dbafe9.png!small"
width="680"
height="149"><br></p><p>这都是常用的字符</p><p>3.特殊字符判断一波</p><p>~!@#$%^&*()_+-={}|:"&lt;>?[]\;',./</p><p>一般&lt;
> ' " 都过滤的了，有时也会漏下 ‘
，作者也不是很清楚为什么</p><p>02</p><p>第二步</p><p>如果这简单的搜索框都做的很好，那么自行考虑要不要继续挖掘</p><p>作者遇到一个，注册登陆后，它是一个选择题，都过滤了的，但正确选项那个答案没有过滤</p><p><br><img
style="margin:15px auto" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876328_5bf66ca859454.png!small"
width="577"
height="101"><br></p><p>一般就这两个就够了</p><p>第三步</p><p>说这么多，来两个简单的实战吧（难的，自己也菜的抠脚）</p><p>第一个，反射：</p><p>http://www.xx.com
</p><p> (就不打码了，就一个简单的反射xss)</p><p>输入</p><p>"></p><p>&lt;img src=x
onerror=prompt(1)</p><p>></p><p><br><img style="margin:15px auto" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876699_5bf66e1bc810f.png!small"
width="690" height="227"><br></p><p>输入</p><p><br><img style="margin:15px auto"
alt="图片.png"
src="https://image.3001.net/images/20181122/1542876712_5bf66e2877ab4.png!small"
width="690"
height="251"><br></p><p>第二个，存储xss</p><p>作者找了另一个网站当例子</p><p>1.搜索框反射</p><p>输入</p><p>"></p><p>&lt;img
src=x onerror=aLert(1)></p><p>&lt;!--</p><p><img style="margin:15px auto"
alt="图片.png"
src="https://image.3001.net/images/20181122/1542876741_5bf66e457132d.png!small"
width="690"
height="300"><br></p><p>2.存在存储xss</p><p>12"></p><p>&lt;/textarea></p><p>
&lt;img src=x onerror=eval(atob(''))></p><p>&lt;!--</p><p><img
style="margin:15px auto" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876748_5bf66e4c4c267.png!small"
width="690" height="390"><br></p><p><br><img style="margin:15px auto"
alt="图片.png"
src="https://image.3001.net/images/20181122/1542876754_5bf66e526188b.png!small"
width="519"
height="465"><br></p><p>按着作者的方法，只要你有耐心和时间，rank真的问题不大，有图有真相，</p><p><img
style="margin:15px auto" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876761_5bf66e5993c86.png!small"
width="580"
height="473"><br></p><p>xss工具</p><p>1.github脚本</p><p>来自一位前辈的收集</p><p><img
style="margin:15px auto" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876768_5bf66e604a7d4.png!small"
width="547"
height="255"><br></p><p>简单测试过，把其他的脚本payload转移到了BruteXSS里，其他的作者用起来效果不是很好（可能没有找到使用方法吧）</p><p>就是上文的
prompt （有点小瑕疵就是，误报，误报后就停止了，还在思考解决）</p><p><img style="margin:15px auto"
alt="图片.png"
src="https://image.3001.net/images/20181122/1542876776_5bf66e68cef58.png!small"
width="690"
height="441"><br></p><p>2.xsser，kali自带的一款工具，由于作者没有研究过，就不扩展讨论了<br><br></p><p>xss防御</p><p>作者的浅薄见解</p><p>很粗暴的方法：输入实体化，敏感词过滤</p><p>作者见过一个cms的过滤是这样的，on开头过滤掉（现在想来应该没有过滤完），script，src，img，iframe，ifame等敏感可引入词过滤，再加上输入实体化</p><p>总结</p><p>1.理解xss姿势的来源</p><p>2.了解现如今的xss常用方法</p><p>3.了解现在的xss防御机制</p><p><br><br></p></div></div>
<!----> <div class="other-panel" data-v-06dc4b68><!----> <!----></div> <!---->
<!----></div> <div class="tags-panel" data-v-06dc4b68><p data-v-06dc4b68><span
data-v-06dc4b68>本文作者：，</span> <span data-v-06dc4b68> 转载请注明来自<a
href="https://www.freebuf.com" class="net"
data-v-06dc4b68>FreeBuf.COM</a></span></p> <div data-v-06dc4b68><span
class="tag" data-v-06dc4b68><span class="spot" data-v-06dc4b68><i class="pot"
data-v-06dc4b68></i></span> <span class="txt" data-v-06dc4b68>#
合天智汇</span></span><span class="tag" data-v-06dc4b68><span class="spot"
data-v-06dc4b68><i class="pot" data-v-06dc4b68></i></span> <span class="txt"
data-v-06dc4b68># 合天网安</span></span></div></div></div></div> <!----> <div
class="remix-module" data-v-06dc4b68><div class="module-title"
data-v-06dc4b68><div class="title" data-v-06dc4b68> 被以下专辑收录，发现更多精彩内容
<!----></div></div> <div class="content column-module" data-v-06dc4b68><div
class="add column-tag" style="background:#f1fff9" data-v-06dc4b68> \+ 收入我的专辑
</div> <div class="add column-tag" style="background:#f1fff9" data-v-06dc4b68>
\+ 加入我的收藏 </div> <div class="add column-tag" style="display:none"
data-v-06dc4b68><span data-v-06dc4b68>展开更多</span> <span class="arrow"
data-v-06dc4b68><i aria-label="图标: down" class="anticon anticon-down"
data-v-06dc4b68><svg viewBox="64 64 896 896" focusable="false" data-icon="down" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M884 256h-75c-5.1 0-9.9 2.5-12.9 6.6L512 654.2 227.9
262.6c-3-4.1-7.8-6.6-12.9-6.6h-75c-6.5 0-10.3 7.4-6.5 12.7l352.6 486.1c12.8
17.6 39 17.6 51.7
0l352.6-486.1c3.9-5.3.1-12.7-6.4-12.7z"></path></svg></i></span></div></div></div>
<div class="comment" data-v-06dc4b68><div class="module-title"
data-v-06dc4b68><div class="title" data-v-06dc4b68> 评论<!----> <span
class="sort" data-v-06dc4b68><i aria-label="图标: swap" class="anticon anticon-swap" data-v-06dc4b68><svg viewBox="64 64 896 896" focusable="false" data-icon="swap" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M847.9 592H152c-4.4 0-8 3.6-8 8v60c0 4.4 3.6 8 8
8h605.2L612.9 851c-4.1 5.2-.4 13 6.3 13h72.5c4.9 0 9.5-2.2
12.6-6.1l168.8-214.1c16.5-21 1.6-51.8-25.2-51.8zM872
356H266.8l144.3-183c4.1-5.2.4-13-6.3-13h-72.5c-4.9 0-9.5 2.2-12.6 6.1L150.9
380.2c-16.5 21-1.6 51.8 25.1 51.8h696c4.4 0 8-3.6
8-8v-60c0-4.4-3.6-8-8-8z"></path></svg></i>按热度排序 </span></div></div> <div
class="intro-list" data-v-06dc4b68></div> <!----> <div class="bottom-comment-region" data-v-06dc4b68><div class="input-item" data-v-96500214
data-v-06dc4b68><div class="avatar" data-v-96500214><div class="img"
data-v-96500214><img src="https://image.3001.net/images/index/wp-user-avatar-50x50.png" data-v-96500214></div></div> <div class="content nologin"
data-v-96500214><p data-v-96500214>请<span data-v-96500214>登录</span>/<span
data-v-96500214>注册</span>后在FreeBuf发布内容哦</p></div></div></div></div> <div
class="introduce" data-v-06dc4b68><div class="module-title"
data-v-06dc4b68><div class="title" data-v-06dc4b68> 相关推荐 </div></div> <div
class="intro-list" data-v-06dc4b68></div></div></div> <div class="aside-right"
data-v-06dc4b68><div class="module-top" data-v-06dc4b68><div class="author-panel" data-v-06dc4b68><div class="top-panel" data-v-06dc4b68><div
class="avatar" data-v-06dc4b68><span data-v-06dc4b68><img src=""
data-v-06dc4b68></span></div> <div class="info" data-v-06dc4b68><div
class="name-info" data-v-06dc4b68><span class="name" data-v-06dc4b68></span>
<!----> <!----> <!----></div> <div class="desc text-line-3" data-v-06dc4b68>
</div> <p class="follow-view" data-v-06dc4b68><button type="button"
class="focus ant-btn ant-btn-colorBorder" style="margin-top:20px;width:132px"
data-v-06dc4b68><span>关 注</span></button></p></div></div> <ul class="number-panel" data-v-06dc4b68><li class="item" data-v-06dc4b68><span class="num"
data-v-06dc4b68>0</span> <span data-v-06dc4b68>文章数</span></li> <li
class="item" data-v-06dc4b68><span class="num" data-v-06dc4b68>0</span> <span
data-v-06dc4b68>评论数</span></li> <li class="item" data-v-06dc4b68><span
class="num" data-v-06dc4b68>0</span> <span
data-v-06dc4b68>关注者</span></li></ul></div> <!----> <!----></div> <div
class="module-middle" data-v-06dc4b68></div> <!----></div></div> <div
class="foot" data-v-06dc4b68><div class="foot-wraper" data-v-06dc4b68><div
class="foot-container" data-v-06dc4b68><div class="foot-left"
data-v-06dc4b68><div class="focusInput" data-v-06dc4b68> 请 <a
href="https://www.freebuf.com/oauth" data-v-06dc4b68>登录</a> / <a
href="https://account.tophant.com/register.html"
data-v-06dc4b68>注册</a>后在FreeBuf发布内容哦 </div></div> <div class="foot-right"
data-v-06dc4b68><span class="approve-num" data-v-06dc4b68><svg aria-hidden="true" class="svg-icon" style="font-size:20px;margin-right:3px"
data-v-322983b7 data-v-06dc4b68><use xlink:href="#like-fill"
data-v-322983b7></use></svg> </span> <span class="comment-num" style="margin-left:30px" data-v-06dc4b68><svg aria-hidden="true" class="svg-icon"
style="font-size:20px;margin-right:3px" data-v-322983b7 data-v-06dc4b68><use
xlink:href="#message-fill" data-v-322983b7></use></svg> </span></div></div>
<div class="foot-container" style="display:none" data-v-06dc4b68><div
class="foot-left" data-v-06dc4b68><textarea placeholder="请输入您的评论..."
maxlength="500" class="ant-input" data-v-06dc4b68></textarea></div> <div
class="foot-right" data-v-06dc4b68><label class="ant-checkbox-wrapper"
data-v-06dc4b68><span class="ant-checkbox"><input type="checkbox" class="ant-checkbox-input"><span class="ant-checkbox-inner"></span></span><span> 匿名
</span></label> <button type="button" class="join ant-btn"
data-v-06dc4b68><span>发 表</span></button> <button type="button" class="cancel
ant-btn" data-v-06dc4b68><span>取 消</span></button> <label class="ant-checkbox-wrapper ant-checkbox-wrapper-checked" style="display:none"
data-v-06dc4b68><span class="ant-checkbox ant-checkbox-checked"><input
type="checkbox" checked class="ant-checkbox-input"><span class="ant-checkbox-inner"></span></span><span> 有人回复时邮件通知我 </span></label></div></div></div></div>
<!----> <!----> <!----> <div data-v-2a4dba56 data-v-06dc4b68><!----></div>
<!----> <!----> <!----> <!----></div></main> <footer class="ant-layout-footer"
data-v-55d8de90><div class="footer" data-v-1d178813 data-v-55d8de90><div
class="container" data-v-1d178813><div class="footer-left"
data-v-1d178813><img src="/images/logo_b.png" data-v-1d178813> <p
data-v-1d178813><span data-v-1d178813>本站由</span>阿里云 提供计算与安全服务</p></div> <div
class="footer-center clearfix" data-v-1d178813><div class="footer-list"
data-v-1d178813><h3 data-v-1d178813>用户服务</h3> <ul data-v-1d178813><li
data-v-1d178813><a target="_blank" href="https://www.freebuf.com/write"
data-v-1d178813>有奖投稿</a></li> <li data-v-1d178813><a target="_blank"
href="https://www.vulbox.com/bounties/detail-72" data-v-1d178813>提交漏洞</a></li>
<li data-v-1d178813><a target="_blank"
href="https://www.vulbox.com/projects/list" data-v-1d178813>参与众测</a></li> <li
data-v-1d178813><a target="_blank" href="https://shop.freebuf.com"
data-v-1d178813>商城</a></li></ul></div> <div class="footer-list"
data-v-1d178813><h3 data-v-1d178813>企业服务</h3> <ul data-v-1d178813><li
data-v-1d178813><a target="_blank" href="https://company.freebuf.com"
data-v-1d178813>安全咨询</a></li> <li data-v-1d178813><a target="_blank"
href="https://www.freebuf.com/news/307349.html" data-v-1d178813>产业全景图</a></li>
<li data-v-1d178813><a target="_blank"
href="https://www.vulbox.com/service/src" data-v-1d178813>企业SRC</a></li> <li
data-v-1d178813><a target="_blank" href="https://www.vulbox.com/"
data-v-1d178813>安全众测</a></li></ul></div> <div class="footer-list"
data-v-1d178813><h3 data-v-1d178813>合作信息</h3> <ul data-v-1d178813><li
data-v-1d178813><a target="_blank" href="https://www.tophant.com/"
data-v-1d178813>斗象官网</a></li> <li data-v-1d178813><a target="_blank"
href="https://www.freebuf.com/advertise" data-v-1d178813>广告投放</a></li> <li
data-v-1d178813><a target="_blank" href="mailto:help@freebuf.com"
data-v-1d178813>联系我们</a></li> <li data-v-1d178813><a target="_blank"
href="https://www.freebuf.com/friends"
data-v-1d178813>友情链接</a></li></ul></div> <div class="footer-list"
data-v-1d178813><h3 data-v-1d178813>关于我们</h3> <ul data-v-1d178813><li
data-v-1d178813><a target="_blank"
href="https://www.freebuf.com/news/others/864.html"
data-v-1d178813>关于我们</a></li> <li data-v-1d178813><a target="_blank"
href="https://www.freebuf.com/jobs/40386.html" data-v-1d178813>加入我们</a></li>
<li data-v-1d178813><div class="weixin-pannel weixin" data-v-1d178813
data-v-1d178813><a href="javascript:;" class="g-icon-qr1"
data-v-1d178813>微信公众号</a></div></li> <li data-v-1d178813><a target="_blank"
href="http://weibo.com/freebuf" data-v-1d178813>新浪微博</a></li></ul></div> <div
class="footer-list" data-v-1d178813><h3 data-v-1d178813>战略伙伴</h3> <ul
data-v-1d178813><li style="padding:0 0 10px" data-v-1d178813><a rel="nofollow"
target="_blank" href="http://www.aliyun.com/?freebuf" data-v-1d178813><img
src="https://image.3001.net/images/20191017/1571306518_5da83c1686dd9.png"
data-v-1d178813></a></li> <li style="padding:0 0 10px" data-v-1d178813><a
rel="nofollow" target="_blank" href="http://www.upyun.com/?freebuf"
data-v-1d178813><img
src="https://image.3001.net/images/20191017/1571310907_5da84d3bbdf2c.png"
data-v-1d178813></a></li> <li style="padding:0 0 10px" data-v-1d178813><a
rel="nofollow" target="_blank" href="https://www.trustasia.com/?freebuf"
data-v-1d178813><img
src="https://image.3001.net/images/20191017/1571306606_5da83c6e8de1c.png"
data-v-1d178813></a></li></ul></div></div> <div class="footer-right"
data-v-1d178813><h3 data-v-1d178813>FreeBuf+小程序</h3> <img src="/images/xcx-code.png" alt data-v-1d178813> <p data-v-1d178813>扫码把安全装进口袋</p></div></div>
<div class="copyright" data-v-1d178813><div class="container"
data-v-1d178813><ul class="clearfix" data-v-1d178813><li data-v-1d178813><a
href="https://www.tophant.com/" target="_blank" data-v-1d178813>斗象科技</a></li>
<li data-v-1d178813><a href="https://www.freebuf.com" target="_blank"
data-v-1d178813>FreeBuf</a></li> <li data-v-1d178813><a
href="https://www.vulbox.com/" target="_blank" data-v-1d178813>漏洞盒子</a></li>
<li data-v-1d178813><a href="https://www.tophant.ai/" target="_blank"
data-v-1d178813>斗象智能安全平台</a></li> <li data-v-1d178813><a
href="https://www.freebuf.com/dis" target="_blank"
data-v-1d178813>免责条款</a></li> <li data-v-1d178813><a
href="https://my.freebuf.com/AgreeProtocol/duty" target="_blank"
data-v-1d178813>协议条款</a></li></ul> <p data-v-1d178813> Copyright © 2020
WWW.FREEBUF.COM All Rights Reserved <a rel="nofollow" target="_blank"
href="https://beian.miit.gov.cn/#/Integrated/index" data-v-1d178813>
沪ICP备13033796号 </a> <span style="padding:0 8px" data-v-1d178813>|</span> <a
rel="nofollow" target="_blank"
href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=31011502009321"
data-v-1d178813> 沪公安网备 <img
src="https://image.3001.net/images/20200106/1578291342_5e12d08ec2379.png"
style="display:inline-block;width:14px;height:12px;position:relative;top:1px;left:3px"
data-v-1d178813></a></p></div></div></div></footer></section></div></div></div><script>window.__NUXT__=function(p,t){return{layout:"articles",data:[{articalId:"190194",jobPosition:p,serverData:{post_title:"作者如何利用xss漏洞shua盒子rank的",ip_address:"湖南省",post_author:t,nickname:t,post_date:"2018-11-22
16:53:03",post_picture:"https://image.3001.net/images/20181122/1542876252_5bf66c5c1cc60.png",category:[{name:"网络安全",slug:"network",url:"https://www.freebuf.com/articles/network"}],tag:[{tag_id:"2846",name:"合天智汇",url:"https://www.freebuf.com/tag/%25e5%2590%2588%25e5%25a4%25a9%25e6%2599%25ba%25e6%25b1%2587"},{tag_id:"2913",name:"合天网安",url:"https://www.freebuf.com/tag/%25e5%2590%2588%25e5%25a4%25a9%25e7%25bd%2591%25e5%25ae%2589"}],post_desc:"本篇是作者的xss备忘录阶段小结，所以读者很有福，能得到大量的姿势（小菜姿势，哈哈哈）\n\n现目前容易且主流的漏洞，作者认为有三种，一是框架漏洞，二是逻辑，三是xss",paid_read:p,vip_read:p,paid_read_amount:0,post_content:'<p>
原创： k <a> 合天智汇</a>
</p><p>前言：</p><p>标题真不真，继续往下看，为什么要作者选择这个提交平台，一是作者真菜，二是好过吧，只要是存储xss就给过</p><p>本篇是作者的xss备忘录阶段小结，所以读者很有福，能得到大量的姿势（小菜姿势，哈哈哈）</p><p>现目前容易且主流的漏洞，作者认为有三种，一是框架漏洞，二是逻辑，三是xss</p><p>ok，进入我们的主题</p><p>1.xss基础知识和分类</p><p>2.xss姿势绕过</p><p>3.xss工具测试</p><p>4.xss防御</p><p>5.总结</p><p>好像没什么写的。。。</p><p>1.dom</p><p>2.反射</p><p>3.存储</p><p>这里推荐一本书《web前端黑客技术揭秘》</p><p>作者这里写的常见基础知识，也是里面的笔记，你说实用性就下面作者的操作就行了，因为我们一般都不会关注这么多，你说知识和技术魅力，这个真的不错；杂乱的笔记，大体写出框架和一些作者关注的点；谅解：</p><p>a、使用script标签实现的jsonp跨域可以将服务器响应文本以函数参数的形式返回，浏览器解析js代码时直接就执行了</p><p>b、常设置httponly，防止打cookie；但是在head的trace方法开启，有httponly的情况下，也可以进行js的cookie操作，称为xst攻击，简单练习链接
http://www.hackdig.com/?01/hack-11.htm</p><p>c、常见的外部url链接</p><pre><span
style="font-family:arial, helvetica, sans-serif;font-size:14px;"><span
style="padding-right:.1px;">html:</span><br /><span style="padding-right:.1px;">&lt;link href&gt;</span><br /><span style="padding-right:.1px;">&lt;img src&gt;</span><br /><span style="padding-right:.1px;">&lt;img lowsrc&gt;</span><br /><span style="padding-right:.1px;">&lt;img dynsrc&gt;</span><br /><span style="padding-right:.1px;">&lt;iframe src&gt;</span><br /><span style="padding-right:.1px;">&lt;frame src&gt;</span><br /><span style="padding-right:.1px;">&lt;script src&gt;</span><br /><span style="padding-right:.1px;">&lt;bgsound src&gt;</span><br /><span style="padding-right:.1px;">&lt;embed src&gt;</span><br /><span style="padding-right:.1px;">&lt;vedio src&gt;</span><br /><span style="padding-right:.1px;">&lt;audio src&gt;</span><br /><span style="padding-right:.1px;">&lt;a href&gt;</span><br /><span style="padding-right:.1px;">&lt;table backgroup&gt;</span><br /><span style="padding-right:.1px;">css:</span><br /><span style="padding-right:.1px;">@import
“”</span><br /><span style="padding-right:.1px;">backgroud:url(“”)</span></span></pre><p><img style="margin:15px
auto;" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876286_5bf66c7e861f0.png!small"
width="562" height="22" /><br /></p><p>可使用以下任意办法防御JSON
Hijacking攻击</p><blockquote><p>首先在请求中添加token（随机字符串）</p><p>再请求referer验证(限制为合法站点，并且不为空)
注意事项 在线json防御被外域恶意调用只限制了referer，但是允许空referer访问：
比如本地html，还有某些伪协议远程调用时是没有referer的。从而导致问题持续。所以空referer也是不安全的</p></blockquote><p>e、很有趣的关注点，但是实际过程中，你要先闭合一些东西，才能继续考虑这些，往往作者都没有用到这里来，所以就扩展不深
html和javascript的自解码过程（html环境和js环境）进制编码：16进制 &amp;#xH &amp;#D 十进制
最后的分号可以不要html实体编码&lt;input type=”button” id=”exec_btn” value=”exec”
onclick=”document.write(‘img src@ onerror=alert(1234) / ‘)”/&gt;js自动解码unicode
16进制 纯转义 无意义防御</p><p>f、一些标签内是不会执行js的，如textarea，所以一般都是要闭合它具备html编码的标签title
iframe noscript noframesxmp没有编码功能plaintext
火弧不会，google有ie有解析差异，代码不会执行</p><p>g、浏览器进制常识html&amp;# 10&amp;# 16 多了a-f
a-f大小写不敏感css中16进制还有\\\6ceval中八进制的\\\5616进制的\\\x5c</p><p>h、由于技术和知识原因，下面的这些没有深层次的学习和探讨其实还有csrf
，拖放和点击劫持，flash的xss（书籍作者介绍由于flash沙箱安全，实用性不强，就没有怎样关注了），xss的漏洞利用，劫持技术（重头戏）</p><p>网上有很多姿势</p><p>作者先写一些自己印象深的，再拿出自己常用的那些什么编码，各种事件替换，就不写了，推荐几篇文章，有兴趣可以自己阅读下姿势：</p><p><img
style="margin:15px auto;" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876297_5bf66c899837f.png!small"
width="611" height="104" /><br
/></p><p>我们来挖小商城的xss，因为商城的xss输入点多</p><p>01</p><p>第一步：</p><p>搜索框判断：</p><p>onfocus=alert1
autofocus </p><p>那两个是反引号，实测可用，在不使用 ‘ ” ( )的情况下，但是一般都要闭合value的 "</p><p>“
onfocus=alert(\'1\') autofocus ”</p><p>"onclick="alert(1)</p><p>"&gt;&lt;img
src=x onerror=aLert(1)&gt;&lt;!--</p><p>%22&gt;&lt;img src=x
onerror=aLert(1)&gt;&lt;!--</p><p>（有趣的现象，url编码能绕过简单的反斜杠）</p><p>见招拆招了，一般都不会费尽心思过滤什么特殊的字符，都是直接函数过滤</p><p>真的过滤了，继续看</p><p>1.输入：</p><p><br
/><img style="margin:15px auto;" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876310_5bf66c9650b13.png!small"
width="690" height="251" /><br
/></p><p>事件判断一波，博主两次遇到一个商城cms，漏了两个事件onuoload（页面关闭时触发），onbblclick(双击时触发)</p><p>2.常用的判断一波：</p><p><br
/><img style="margin:15px auto;" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876317_5bf66c9dbafe9.png!small"
width="680" height="149" /><br
/></p><p>这都是常用的字符</p><p>3.特殊字符判断一波</p><p>~!@#$%^&amp;*()_+-={}|:"&lt;&gt;?[]\\\;\',./</p><p>一般&lt;
&gt; \' " 都过滤的了，有时也会漏下 ‘
，作者也不是很清楚为什么</p><p>02</p><p>第二步</p><p>如果这简单的搜索框都做的很好，那么自行考虑要不要继续挖掘</p><p>作者遇到一个，注册登陆后，它是一个选择题，都过滤了的，但正确选项那个答案没有过滤</p><p><br
/><img style="margin:15px auto;" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876328_5bf66ca859454.png!small"
width="577" height="101" /><br
/></p><p>一般就这两个就够了</p><p>第三步</p><p>说这么多，来两个简单的实战吧（难的，自己也菜的抠脚）</p><p>第一个，反射：</p><p>http://www.xx.com
</p><p> (就不打码了，就一个简单的反射xss)</p><p>输入</p><p>"&gt;</p><p>&lt;img src=x
onerror=prompt(1)</p><p>&gt;</p><p><br /><img style="margin:15px auto;"
alt="图片.png"
src="https://image.3001.net/images/20181122/1542876699_5bf66e1bc810f.png!small"
width="690" height="227" /><br /></p><p>输入</p><p><br /><img style="margin:15px
auto;" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876712_5bf66e2877ab4.png!small"
width="690" height="251" /><br
/></p><p>第二个，存储xss</p><p>作者找了另一个网站当例子</p><p>1.搜索框反射</p><p>输入</p><p>"&gt;</p><p>&lt;img
src=x onerror=aLert(1)&gt;</p><p>&lt;!--</p><p><img style="margin:15px auto;"
alt="图片.png"
src="https://image.3001.net/images/20181122/1542876741_5bf66e457132d.png!small"
width="690" height="300" /><br
/></p><p>2.存在存储xss</p><p>12"&gt;</p><p>&lt;/textarea&gt;</p><p> &lt;img src=x
onerror=eval(atob(\'\'))&gt;</p><p>&lt;!--</p><p><img style="margin:15px
auto;" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876748_5bf66e4c4c267.png!small"
width="690" height="390" /><br /></p><p><br /><img style="margin:15px auto;"
alt="图片.png"
src="https://image.3001.net/images/20181122/1542876754_5bf66e526188b.png!small"
width="519" height="465" /><br
/></p><p>按着作者的方法，只要你有耐心和时间，rank真的问题不大，有图有真相，</p><p><img style="margin:15px
auto;" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876761_5bf66e5993c86.png!small"
width="580" height="473" /><br
/></p><p>xss工具</p><p>1.github脚本</p><p>来自一位前辈的收集</p><p><img style="margin:15px
auto;" alt="图片.png"
src="https://image.3001.net/images/20181122/1542876768_5bf66e604a7d4.png!small"
width="547" height="255" /><br
/></p><p>简单测试过，把其他的脚本payload转移到了BruteXSS里，其他的作者用起来效果不是很好（可能没有找到使用方法吧）</p><p>就是上文的
prompt （有点小瑕疵就是，误报，误报后就停止了，还在思考解决）</p><p><img style="margin:15px auto;"
alt="图片.png"
src="https://image.3001.net/images/20181122/1542876776_5bf66e68cef58.png!small"
width="690" height="441" /><br
/></p><p>2.xsser，kali自带的一款工具，由于作者没有研究过，就不扩展讨论了<br /><br
/></p><p>xss防御</p><p>作者的浅薄见解</p><p>很粗暴的方法：输入实体化，敏感词过滤</p><p>作者见过一个cms的过滤是这样的，on开头过滤掉（现在想来应该没有过滤完），script，src，img，iframe，ifame等敏感可引入词过滤，再加上输入实体化</p><p>总结</p><p>1.理解xss姿势的来源</p><p>2.了解现如今的xss常用方法</p><p>3.了解现在的xss防御机制</p><p><br
/><br
/></p>',is_original:p,is_reward:p,is_reproduce:p,post_list:[]},serverMemuRender:p}],fetch:[],error:null,state:{counter:0,userInfo:{userInfo:{},skinData:{skin:"classical",vip:p,vip_time:""},dynamicCount:"",columnNumber:"",keyAuth:"",messageCount:{},isParty:p,guestRemind:p}},serverRendered:!0,routePath:"/articles/network/190194.html"}}(!1,"蚁景科技")</script><script
src="/freebuf/2.1.0.c639fea2d265a6bebb83.js" defer></script><script
src="/freebuf/2.1.0.307941076e631a27c0ef.js" defer></script><script
src="/freebuf/2.1.0.4c8524bdd27f387e498d.js" defer></script><script
src="/freebuf/2.1.0.9dfd7660182887a56850.js" defer></script><script
src="/freebuf/2.1.0.525f27205448b84bae54.js" defer></script><script
src="/freebuf/2.1.0.6c29ecc5e7fa36f53fa4.js" defer></script><script
src="/freebuf/2.1.0.f7cf8ed7dbb1f1e9c5a5.js" defer></script><script
src="/freebuf/2.1.0.dbc4832fb1e9d608e7f4.js" defer></script><script
src="/freebuf/2.1.0.d0f2c05d63238c7ad546.js" defer></script><script
src="/freebuf/2.1.0.f3fe2368b3dc33e537a1.js" defer></script><script
src="/freebuf/2.1.0.a3da96c1d3b72dd98259.js" defer></script> </body>
<script>var
_hmt=_hmt||[];_hmt.push(["_setAccount","cc53db168808048541c6735ce30421f5"]),function(){var
c=document.createElement("script"),e=(c.src="https://hm.baidu.com/hm.js?cc53db168808048541c6735ce30421f5",document.getElementsByTagName("script")[0]);e.parentNode.insertBefore(c,e)}()</script>
</html>

