#### **作者：马跃**

### 1 背景

这是一个安静祥和没有 bug 的下午。  
作为一只菜鸡，时刻巩固一下基础还是很有必要的，如此的大好时机，就让我来学习学习 mybatis 如何使用。

![](https://image.3001.net/images/20221122/1669084294_637c3486382ea0267d283.png!small)

这可和我看到的不一样啊，让我来看看项目里怎么写的。

![](https://image.3001.net/images/20221122/1669084295_637c3487019facc805c3e.png!small)

我们项目中的 Dao 都继承于 BaseDao，而 BaseDao 继承于 SqlSessionDaoSupport，每次执行 sql 的时候都是直接将这个
sqlSession 返回，然后执行 sql，这难道不是一个实例变量嘛？这和你说的可不一样诶。于是带着这样的疑问，我开始了探索。

### 2 探索之旅

1）我们都知道，在使用 mybatis 时，sqlSession 都来自于 sqlSessionFactory，而 sqlSessionFactory
可以通过 sqlSessionFactoryBuilder 创建，也可以通过 spring 初始化，而项目中很显然采取了后一种方式。

![](https://image.3001.net/images/20221122/1669084295_637c34879a835739105a9.png!small)

2）那么我们已经得到了 sqlSessionFactory，应该如何去进一步探索 sqlSession 的来源呢，我想到可以通过项目中已经实现的 dao
进行探索。我们随便选取一个 dao 为例。

![](https://image.3001.net/images/20221122/1669084296_637c34881c45176d25fa5.png!small)

它继承了 BaseDao。

![](https://image.3001.net/images/20221122/1669084296_637c3488809bbe1eb29eb.png!small)

而 BaseDao 又继承了 SqlSessionDaoSupport，在 BaseDao 中调用了 getSqlSession 方法，实际上也就是
SqlSessionDaoSupport 的 getSqlSession 方法。

![](https://image.3001.net/images/20221122/1669084297_637c34892033781e9aaa0.png!small)

而 SqlSessionDaoSupport 的 getSqlSession
方法是直接将自己的成员变量返回去的，截至目前为止，和我的怀疑点是相符合的，即目前的写法和 mybatis 官网的说明是冲突的。

3）反复阅读 SqlSessionDaoSupport
这个类后，终于被我发现了线索，细心的小伙伴应该也早已发现了，就在上图之中的注释中，“用户应该使用这个方法来获得一个 SqlSession 来执行 sql
语句，这个 SqlSession 被 spring 管理，用户不应该提交、回滚或关闭它。因为这些已经被自动执行了。”

同时，这个方法会返回一个线程安全的 SqlSession。

![](https://image.3001.net/images/20221122/1669084297_637c3489a375b5e8f075b.png!small)

那么这个 SqlSession 是从何而来的呢，从上图可以看出，它有两种赋值方式，一种是给他传一个 SqlSessionFactory，生成
SqlSessionTemplate，SqlSessionTemplate 即为 sqlSession。另一种是直接给他传一个
SqlSessionTemplate 作为 SqlSession。根据本类的注释，如果 SqlSessionFactory 和
SqlSessionTemplate 都被定义了，那么 SqlSessionFactory 的方式会失效。至此，我的上述疑问已经解决了，也就是说这个
SqlSession 并不是一个 mybatis 初始的 SqlSession，而是 spring 实现的 SqlSessionTemplate。

4）但是，我又诞生了新的疑问，SqlSessionTemplate 是怎么完成线程安全的呢？

![](https://image.3001.net/images/20221122/1669084298_637c348a4a785ec2e7f8d.png!small)

于是我进入了 SqlSessionTemplate 的方法执行，发现实际执行语句的都是这个代理类 sqlSessionProxy。

![](https://image.3001.net/images/20221122/1669084298_637c348ac2576ad2052f0.png!small)

而代理工作内容就在 SqlSessionInterceptor 这个 handler 里。

![](https://image.3001.net/images/20221122/1669084299_637c348b71dc38447b348.png!small)

进入其中，我们终于发现了它的获取和关闭操作。

![](https://image.3001.net/images/20221122/1669084300_637c348c1dab31415a431.png!small)

![](https://image.3001.net/images/20221122/1669084300_637c348cadc01e9070678.png!small)

也就是说，每次执行，代理都会调用 sessionFactory 的 openSession 方法获得一个新的 session。

### 3 总结

终于的终于，mybatis，spring，项目以及我的疑问得到了统一，真是一个宁静祥和而又没有 bug 的下午呀。

