原创： Smity 合天智汇

推特爬虫爬取用户id和所有tweets（免登录，不使用api）所有代码都已经发布在github上：https://github.com/smityliu/spider这次做的一个项目中涉及人物画像，做人物画像中兴趣属性很关键的一点就是要收集足够多的人物数据，基础工作就是进行爬虫的书写，收集数据集。对于一个社交网络来说，这里最大最实用的数据**就是用户发布的帖子，因为里面的东西会关联到个人的兴趣爱好，甚至工作生活，从中做主题提取就可以大致的看出来人物在这个社交网络上所体现出来的一个兴趣属性。经久不衰的话题
----白帽子安全条款：不用爬虫爬取个人隐私！所以我对于社交网络的选择标准：1.国外社交网络-----推特；2.只爬取网站上公开发布的用户信息。由于模拟登录过于频繁还是会被网站封ip和账号，因此就想能不能实现免登录状态下的爬虫，爬取用户数据。

用户id爬取

推特上用来标识用户身份的标志可不是用户名，因为用户名是可以重复的，比如我搜索tolly这个用户，会发现有好多用户名叫tolly的。

![v2-288affbec031e01bbcca3aefa0004b75_hd.j](https://pic3.zhimg.com/80/v2-288affbec031e01bbcca3aefa0004b75_hd.jpg)

但是他们的用户id却是唯一的：

![v2-f795975e74a9dea5da85c055abc70bb9_hd.j](https://pic3.zhimg.com/80/v2-f795975e74a9dea5da85c055abc70bb9_hd.jpg)

红色框中的就是用户id。即使用户名相同，id也不会相同，那么我们来看一下用户主页：这里随便找了一个国外小哥的主页，发现其实域名就是twitter.com +
用户id。

![v2-84c50cef25fe8dd2903135b832f0f26e_hd.j](https://pic3.zhimg.com/80/v2-84c50cef25fe8dd2903135b832f0f26e_hd.jpg)

因此我们首先要通过爬虫获取到用户id，才能进行下一步的数据爬取：查询的api接口为：https://twitter.com/search?f=users&vertical=default&q=smity&src=unkn

q参数输入的就是在你要查询的昵称大致是什么样子，也就是你在搜索框输入的东西。

如果我们直接requests请求这个连接，那么返回的东西就会是一堆带着html标签的文本，很难看。所以我们必须分析用户名在哪种标签里，id在哪种标签里。

![v2-491f2cd86133295e5f8e3c94163cb1a3_hd.j](https://pic4.zhimg.com/80/v2-491f2cd86133295e5f8e3c94163cb1a3_hd.jpg)

![v2-202af39850f6c6e73a1f0128c1716c19_hd.j](https://pic1.zhimg.com/80/v2-202af39850f6c6e73a1f0128c1716c19_hd.jpg)

上图就是爬取出来的带有很多html标签的文本，我们可以看到用户名是在<div>标签中的data-name参数中，然后data-screnn-name和下一段的<span class中都有着MrNastyPantz这个id，影响不大，你选择哪个标签做正则都是可以的。

我选择的是data-name和span，个人观念是最好不在同一个标签中做正则提取，会有很多意想不到的问题。因此这个正则这么写：用户名：

data-name="(.*?) data-protected="false"Id：<span class="username u-dir"
dir="ltr">@<b class="u-linkComplex-target">(.*?)</b></span>

所以加入正则以后的爬虫代码为：

import requestsimport reimport
sys#查询用户名idurl='https://twitter.com/search?f=users&vertical=default&q='+sys.argv[1]+'&src=unkn'proxies={'http':
'http://127.0.0.1:10809', 'https': 'http://127.0.0.1:10809'}search =
requests.get(url,proxies=proxies) search.encoding =
'utf-8'print('查询成功')text=search.textprint(re.findall(r'data-name="(.*?) data-protected="false"',text))print('\n')print(re.findall(r'<span class="username
u-dir" dir="ltr">@<b class="u-linkComplex-target">(.*?)</b></span>',text))

运行命令为：Python twitter_userid_sucess.py + 你要爬取的用户名（在搜索框输入的东西）运行效果为：

![v2-e6d8cdd400f768be7ed6da8a20d0fd79_hd.j](https://pic2.zhimg.com/80/v2-e6d8cdd400f768be7ed6da8a20d0fd79_hd.jpg)

上面为用户名，对应下面的id。因为有输入一个smity会有很多用户与之相似，所以会有不止一个结果。用户tweets爬取做完了id的爬取，我们自然就可以直接通过id定位到你想爬取的用户tweets主页。我选取的是https://twitter.com/BeSmity一个社交网络类似*博，推特，脸书这样的，有没有实现免登录爬取信息的可能性，就要看你在不登录的状态下，能否通过浏览器页面看到你想看的信息，推特页面如下：

![v2-661439eeccb30da16a2342b9448ceb80_hd.j](https://pic1.zhimg.com/80/v2-661439eeccb30da16a2342b9448ceb80_hd.jpg)

可以看到这里我们是在一个没有登录的状态下，看到了该用户的tweets和个人简介还有用户id，然后我们利用鼠标滚轮下滑。不断的往下翻就可以看到这个用户的所有推文，代表着其实我们不用登录推特账户就可以看到这个用户的很多信息。

![v2-81eb2e2ef01352f3915e5ad4fdd5731f_hd.j](https://pic1.zhimg.com/80/v2-81eb2e2ef01352f3915e5ad4fdd5731f_hd.jpg)

但是也有一部分信息看不到，比如我们点击这个用户的粉丝和关注页面，或者点击用户头像，会发现其实还是需要登录以后才可查看。

![v2-76fd7756ecec70566d31511b93ee4ab4_hd.j](https://pic1.zhimg.com/80/v2-76fd7756ecec70566d31511b93ee4ab4_hd.jpg)

有了这个，我们就来看我们当然想到可以用requests直接请求页面，于是这里很多人就会考虑到直接，requests.get(‘https://twitter.com/BeSmity’)，我们看一下返回结果：

![v2-7f7b3b11ac379e9cdcaf1f8310d15bee_hd.j](https://pic3.zhimg.com/80/v2-7f7b3b11ac379e9cdcaf1f8310d15bee_hd.jpg)

确实有抓到这个用户的tweets，但是发现好像这个只是一条在11月25号的tweets，这个帖子之后还有很多帖子我们没有看到，但是我们明明是可以看到所有的推文的啊，这里却显示了一部分，这个是怎么回事呢？

![v2-0f3d8dcf3e6c6ac748ca64bb97bac008_hd.j](https://pic4.zhimg.com/80/v2-0f3d8dcf3e6c6ac748ca64bb97bac008_hd.jpg)

我们尝试着继续滚轮下滑，然后发现每滚过一段距离，就会有一个短暂的卡顿，于是我们截取那个卡顿发送的网络数据包：

![v2-29024b4d64643c32a3fa50617549663b_hd.j](https://pic1.zhimg.com/80/v2-29024b4d64643c32a3fa50617549663b_hd.jpg)

原来这个卡顿是发送了一个ajax请求，来进行进一步的页面获取，俗称异步页面更新，也就是在不刷新页面的情况下，直接更新页面的内容，可以保证用户不用每次都重新打开页面查看新内容。

所以我们只请求https://twitter.com/BeSmity是绝对不够，他只会返回第一次异步更新之前的值，所以我们需要自己手动模拟这个ajax请求。观察数据包，我们可以看到红色箭头指向的地方有一个max_position，为什么关注这个，一个是因为它有position这个标志位，另外一个是因为这个请求的返回包里面有一个min_position。

![v2-ca186a0fff998768c5b9b03048b15e27_hd.j](https://pic1.zhimg.com/80/v2-ca186a0fff998768c5b9b03048b15e27_hd.jpg)

这个min_position恰好就在第一个，所以我们记录一下当前的这两个标志位。max_position=1197617887390900237min_position=1184647192977514496然后我们继续滚动鼠标滚轮翻页看看会有什么内容突然又是一阵卡顿，我们知道这个时候网页又发送了一个异步更新请求了，赶紧截取查看一下流量包：

![v2-8cf50415d5568a143ed2036d7e6753d7_hd.j](https://pic1.zhimg.com/80/v2-8cf50415d5568a143ed2036d7e6753d7_hd.jpg)

复制一下请求的url，我们发现这个时候的max_position变成了上一次ajax请求时返回包中的min_position。

https://twitter.com/i/profiles/show/BeSmity/timeline/tweets?include_available_features=1&include_entities=1&max_position=1184647192977514496&reset_error_state=false

![v2-5368f06cc2c38d8751fc942d1a4d2bc8_hd.j](https://pic2.zhimg.com/80/v2-5368f06cc2c38d8751fc942d1a4d2bc8_hd.jpg)

并且它还继续在返回包里面给我们发送了一个min_position，我们大胆猜测，其实max_posotion记录的就是当前页的位置编码，然后在请求包中会返回一个下一页的请求编码，那么如果用户想查看下一页的内容，网页就会用这个min_position作为下一页的max_position发送请求来更新下一页内容。

那么如果到了最后一页呢，果不其然，最后一页的响应包中min_position的值位null，意味着没有下一页了。

![v2-23a018bbeb135155e5be0e38b1f01747_hd.j](https://pic1.zhimg.com/80/v2-23a018bbeb135155e5be0e38b1f01747_hd.jpg)

现在关键是要获取第一个min_position，我们尝试着去访问一下不带max_position的请求，https://twitter.com/i/profiles/show/BeSmity/timeline/tweets?include_available_features=1&include_entities=1

![v2-ae540270a3deb723194e723163674a38_hd.j](https://pic3.zhimg.com/80/v2-ae540270a3deb723194e723163674a38_hd.jpg)

果然就是最初始的min_position，那么我们的爬虫流程就是先访问初始url，获取到第一个min_position后，循环获取以上一个min_position作为max_position的url的页面内容，并且接受它返回的min_position，再作为下一个页面的max_position。

这下我们的爬虫就很好写了，首先利用json.loads解析返回的响应包，获取min_position。text_json=json.loads(tweets.text)然后根据第一次的json数据我们很容易得知”items_html”就是我们需要的页面内容。

提取步骤一这里有几个做提取的坑给大家填了，一个是items_html里面有些地方有回车符，正则表达式匹配回车符将会变得十分麻烦，所以一定要先去掉html内容中所有回车符，没有去除回车的效果如下：

![v2-a9f5bd3cb69e5e8be8e5a5db74795cb0_hd.j](https://pic2.zhimg.com/80/v2-a9f5bd3cb69e5e8be8e5a5db74795cb0_hd.jpg)

红框处都是回车符，会导致内容截断，所以我们需要如下操作：

text=text_json["items_html"].replace('\n','')

提取步骤二第二个是想要提取帖子内容一定要用取的形式，从标签里面先取，然后再删除多余内容，直接删除所有标签会导致代码没有重用性而且去除很麻烦。帖子的内容位于这个标签内：

<p class="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text" data-aria-label-part="0">*****</p>

但是由于语言的不同，这个标签还会有如下形式：

<p class="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text" data-aria-label-part="0">*****</p><p class="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text" data-aria-label-part="0">*****</p>

因此我们依据标签中都有的data-aria-label-part属性设置取出帖子文本的正则为：

content=re.findall(r'data-aria-label-part="0">(.*?)</p>',text)

这样提取之后，我们的内容就被简化为如下效果：

![v2-48d551ea911147cd9a14555752a523b4_hd.j](https://pic2.zhimg.com/80/v2-48d551ea911147cd9a14555752a523b4_hd.jpg)

会发现还是有很多杂质在里面

提取步骤三因此我们继续做如下处理，首先分析提取的东西结构，里面含有很多<a>标签和unicode编码字符，@其他用户的语句，以及一些固定的url，我们都将其去除或者替换。

![v2-4139bf837f289210692cc142d0b2ea39_hd.j](https://pic2.zhimg.com/80/v2-4139bf837f289210692cc142d0b2ea39_hd.jpg)

pattern =re.compile(r'<[^>]+>|pic.twitter.com/.*|http(.*?)&ampnbsp|',re.S)line
= re.sub(pattern ,'',line)line = re.sub('&#39;' ,'\'',line)line =
re.sub('&amplt','<',line)line = re.sub('&ampgt','>',line)line =
re.sub('&ampamp','&',line)line = re.sub('&ampquot','"',line)line =
re.sub(r'^@(.*?) @(.*?) |^@(.*?) ','',line)

这样的到的就是我们干净的文本，每一行的内容都是一个tweets。

![v2-f16fd7bb4c8b4e19dce283a21b3ef343_hd.j](https://pic4.zhimg.com/80/v2-f16fd7bb4c8b4e19dce283a21b3ef343_hd.jpg)

最后加上我们的新请求构造，取下一个max_position的页面内容

tweets=requests.get(url+'&max_position='+text_json["min_position"]+'&reset_error_state=false',proxies=proxies)

整体代码如下：

import requestsimport jsonimport reimport sys#返回一个json，里面有min-position#这个地方可以用下面这个url获取到最开始的max_position，当前页面用的是max_position，然后响应包json里的min_position就是下一页的max_position，循环获取，直到没有min_position。url="https://twitter.com/i/profiles/show/"+sys.argv[1]+"/timeline/tweets?include_available_features=1&include_entities=1"proxies={'http':'127.0.0.1:10809','https':'127.0.0.1:10809'}tweets=requests.get(url,proxies=proxies)tweets.encoding="utf-8"#这个地方一定要写入一行content作为标题，不然后面的lda.py会报错with
open("./text.txt",'w',encoding='utf-8') as f: f.write("content"+'\n')with
open("./text.txt",'a',encoding='utf-8') as f:
text_json=json.loads(tweets.text) while(text_json["min_position"]):
print(text_json["min_position"]+'\n')
#items_html里面有些地方有回车符，导致正则不能提取帖子文本，一定要先去掉所有回车符
text=text_json["items_html"].replace('\n','')
#这个地方应该要用取得形式，从标签里面先取，然后再删除，版本一是直接删除所有标签这样做代码没有重用性而且去除很麻烦
content=re.findall(r'data-aria-label-part="0">(.*?)</p>',text) for line in
content: #把多余标签，pic.twitter.com和url去掉 pattern =
re.compile(r'<[^>]+>|pic.twitter.com/.*|http(.*?)&ampnbsp|',re.S) line =
re.sub(pattern ,'',line) line = re.sub('&#39;' ,'\'',line) line =
re.sub('&amplt','<',line) line = re.sub('&ampgt','>',line) line =
re.sub('&ampamp','&',line) line = re.sub('&ampquot','"',line) line =
re.sub(r'^@(.*?) @(.*?) |^@(.*?) ','',line) if(len(line)): #continue
f.write(line+'\n')
tweets=requests.get(url+'&max_position='+text_json["min_position"]+'&reset_error_state=false',proxies=proxies)
text_json=json.loads(tweets.text)print("finish work")

代码运行后，每爬取一个页面就会返回下一个页面的max_position，如果没有下一页，就会结束爬取。

![v2-232f7008c15b8d5631a96c1d2e201d77_hd.j](https://pic4.zhimg.com/80/v2-232f7008c15b8d5631a96c1d2e201d77_hd.jpg)

可以提前用ctrl+c结束脚本运行，不论是否爬取完毕，都会在同目录下生成一个text.txt文件用于存放爬取的数据。下一章节我们将继续分析如何利用这些爬取的数据进行主题提取。

相关实验：

Python爬虫-基础：

[实验:Python爬虫-基础(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID80b9-d088-4e0c-8f80-0d57b2a9e89c)

（了解爬虫的基本原理，对爬虫有简单的认识）

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

