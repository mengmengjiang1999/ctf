***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **PHP知名开发框架Laravel，前几天在官方博客通报了一个高危SQL注入漏洞，这里简单分析下。**  

****![timg.jpg](https://image.3001.net/images/20190326/1553596925_5c9a01fdccae1.jpg!small)****

首先，这个漏洞属于网站coding写法不规范，官方给了提示：  

![Image](http://image.3001.net/2019/03/d9e37373478559f534700dd4cb239a88.jpg)

但官方还是做了修补，升级 **最新版本V5.8.7** 可修复。

我们先定位下这里：

    
    
    Illuminate\Validation\Rule
    

官方推荐的写法是：

    
    
    Rule::unique('users')->ignore($id),
    

如果网站coding没有预先对$id的值做处理时，用户可以直接传递恶意数据给ignore函数，就会导致SQL注入。

我们来跟一下函数：

    
    
    \Illuminate\Validation\Rules\Unique.php
    
    class Unique
    {
    ...
    public function ignore($id, $idColumn = null)
        {
            if ($id instanceof Model) {
                return $this->ignoreModel($id, $idColumn);
            }
    
            $this->ignore = $id;
            $this->idColumn = $idColumn ?? 'id';
    
            return $this;
        }
    
    

这里我们不考虑把$id写成实例的情况，$id是用户可控的话，$idColumn直接写为空即可，最后赋值情况如下：

    
    
    $this->ignore = $id;
    $this->idColumn = 'id';
    

如果网站代码类似这样构造的话，黑客输入的值就属于可控状态：

    
    
    $id = $request->input('id');
    

最后我们会走到这儿：

    
    
    Illuminate\Validation\Rules\Unique.php
    
        public function __toString()
        {
            ...
            ...
        }
    

我们看下关键的代码变更：

    
    
    Illuminate\Validation\Rules\Unique.php
    
    V5.8.7【最新版】
        public function __toString()
        {
                $this->ignore ? '"'.addslashes($this->ignore).'"' : 'NULL',
        }
    
    
    
    Illuminate\Validation\Rules\Unique.php
    
    V5.8.4
        public function __toString()
        {
    
                $this->ignore ? '"'.$this->ignore.'"' : 'NULL',
    
        }
    

这里最新的代码v5.8.7，把$this->ignore直接给addslashes了，以前这里是没有防护的。

有趣的是，笔者对比了下diff，期间官方还试图对其他引用的地方进行过滤。最后还是在__toString处，进行了统一的过滤。

最后提一句，后面的代码会进入DatabaseRule，进行后续SQL规则匹配。

    
    
    Illuminate\Validation\Rules\DatabaseRule.php
    

这之后就没有再进一步处理，接着形成了SQL注入。  

阅读链接如下：  

[**官方通告**](https://blog.laravel.com/unique-rule-sql-injection-warning?fbclid=IwAR26Cs1Ewh983UxSF5fNO8Xr0hUnwSO_Ikbr08Adi20m5h5llP0WhNDmgRg)

 **[说明文档](https://laravel.com/docs/5.8/validation#rule-unique)**

 ***本文作者：dawner，转载请注明来自FreeBuf.COM**

