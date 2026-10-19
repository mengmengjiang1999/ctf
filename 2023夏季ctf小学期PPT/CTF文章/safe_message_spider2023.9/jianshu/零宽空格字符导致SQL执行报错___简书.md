零宽空格字符导致SQL执行报错

[ 左轮Lee](https://www.jianshu.com/u/06b7a375a146)关注赞赏支持

# 零宽空格字符导致SQL执行报错

MySQL 5.7.34

研发丢来一个SQL，说一直执行报错（SQL只保留问题部分）：

    
    
    select * from order o WHERE o.created_time < '2021-12-01 00:00:00';
    

看似没毛病的SQL，执行时一直报错，逐个隐藏完整SQL部分内容后定位到上面的条件o.created_time < '2021-12-01 00:00:00'
存在问题

    
    
    mysql> select * from order o WHERE o.created_time < '2021-12-01 00:00:00';
    1064 - You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '' at line 1
    

直觉就是存在特殊字符，于是把各个空格删除后再输入，仍然报错。  
百思不得其解，后面把SQL复制后贴到sublime看看有没有什么发现，果然，在最后的分号前面有个 **0x200b** 的字符，google一下。

image.png

维基百科中称 **0x200b** 代表零宽空格（zero-width space,
ZWSP），是一种不可打印的[Unicode](https://links.jianshu.com/go?to=https%3A%2F%2Fzh.wikipedia.org%2Fwiki%2FUnicode)字符，用于可能需要换行处。涨姿势！

遇到SQL执行不能通过报错直接判断的妖问题时，不妨将SQL贴到sublime，也许有新发现。

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [LCTF的一道sql报错注入+七个字符命令执行](https://www.jianshu.com/p/83d07d5c3af8)

自从很多开发人员禁止回显错误以后，sql报错注入，就很少见了，所以一直没什么机会接触，感谢LCTF给我这个机会，2...

[_阿烨_](https://www.jianshu.com/u/121bf0f6b3d2)阅读 1,451评论 1赞 3

  * [JS中如何去除字符串的空格](https://www.jianshu.com/p/e2be087eef79)

在JS中，我们经常需要处理字符串，也经常需要去除字符串的空格。 通过字符串自带方法 缺陷：通过字符串自带方法，无法...

[深度剖析JavaScript](https://www.jianshu.com/u/851bd01f6233)阅读 3,531评论 0赞 6

  * [如何在Linux中操作文件名有空格和特殊字符](https://www.jianshu.com/p/063fdd05115c)

我们经常遇到文件和文件夹名称。 在大多数情况下，文件/文件夹名称与文件/文件夹的内容相关，并以数字和字符开头。 A...

[gzwawj](https://www.jianshu.com/u/47c8b84ea019)阅读 5,438评论 0赞 0

  * [【变量】python中的字符集和编码](https://www.jianshu.com/p/bcbf7444e814)

字符集和编码简介 在编程中常常可以见到各种字符集和编码，包括ASCII,MBCS,Unicode等字符集。确切的说...

[兰山小亭](https://www.jianshu.com/u/07e818300caa)阅读 7,418评论 0赞 13

  * [去除字符串左右两边的空格](https://www.jianshu.com/p/94d148cda40d)

在日常工作中，过滤表单中一些特殊的字符是很常见的功能。比如文本中要求输入单纯的数字，但用户有时会误输入一些多余的空...

[指尖的宇宙](https://www.jianshu.com/u/8274c6acbb35)阅读 898评论 0赞 1

 