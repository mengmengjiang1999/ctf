***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **一、漏洞背景**  

2月20日Drupal官方披露了一个Drupal的远程命令执行漏洞：

<https://www.drupal.org/sa-core-2019-003>

**漏洞的触发条件为开启了RESTful Web Services，且允许POST/PATCH请求。**

根据Drupal的配置，此漏洞可能不需要任何权限即可触发，但普适性不高。
**一旦该漏洞被利用，攻击者则可以直接在Web服务器上执行任意PHP代码，造成服务器被入侵、用户信息泄露等后果。**

腾讯云不受该漏洞影响，此漏洞爆发后，腾讯云安全团队第一时间进行跟踪分析，且对云上客户进行预警通知。

## **二、漏洞定位**

漏洞通告指出了Drupal 8在开启了RESTful Web Services模块，同时允许了PATCH/POST方法请求后，可以造成代码执行漏洞。

根据commit log（
<https://github.com/drupal/core/commit/24b3fae89eab2b3951f17f80a02e19d9a24750f5>
）可以定位到漏洞的触发原因在于反序列化的操作：

![01.png](https://image.3001.net/images/20190221/1550752846_5c6e9c4e772a2.png!small)

可以推测应该是在进行REST
API操作的过程中，options参数的内容带入到unserialize函数导致的。通过diff可以发现LinkItem.php和MapItem.php都受到影响，这里从LinkItem来向上挖掘漏洞点。

查看core\modules\link\src\Plugin\Field\FieldType\LinkItem.php ：

![02.png](https://image.3001.net/images/20190221/1550752873_5c6e9c6936604.png!small)
梳理了其整个调用链，从REST请求开始，先通过用户传入的JSON的_links.type获取了其对应的Entity，再获取Entity内的Fields列表，遍历这个列表得到key，从用户传入的JSON内取出key，拼接成为field_item:key的形式（过程略），最终在getDefinition内查找了definitions数组内的字段定义，得到一个对应的Field的实例对象，过程大体如下：  

![03.png](https://image.3001.net/images/20190221/1550752891_5c6e9c7b9ecff.png!small)
接着FieldNormalizer的denormalize方法调用了Field的setValue方法。  

![04.png](https://image.3001.net/images/20190221/1550752919_5c6e9c9708ca0.png!small)

也就是说，我们如果可以将$field_item控制为LinkItem或者MapItem，即可触发反序列化。

## **三、触发点构造**

我们在Drupal后台配置好RESTful Web Service插件，选择一个可以进行POST的操作。

为了尽可能模拟网站管理员的配置，我们这里允许对于/user/register的POST操作。

于情于理，用户注册处必然可以作为匿名用户来进行操作。开启/user/register：

![05.png](https://image.3001.net/images/20190221/1550752957_5c6e9cbdc36a8.png!small)
设置允许匿名用户利用POST来访问/user/register：  

![06.png](https://image.3001.net/images/20190221/1550752979_5c6e9cd332f1b.png!small)
上文中提到，我们需要一个Entity内存在LinkItem
Field。通过对Entity的查找，定位到MenuLinkContent和Shortcut使用了LinkItem，利用Shortcut来进行进一步的测试。  

![07.png](https://image.3001.net/images/20190221/1550752996_5c6e9ce44e924.png!small)

Shortcut的_links.type为：<http://127.0.0.1/rest/type/shortcut/default>。

向/user/register发送POST请求，同时在PHPStorm内将断点下在core\modules\hal\src\Normalizer\FieldItemNormalizer.php的denormalize函数：

![08.png](https://image.3001.net/images/20190221/1550753019_5c6e9cfba4c1f.png!small)
可以发现，在调用setValue方法的现场，$field_item为LinkItem。跟入setValue方法（图
2），根据逻辑，如果$values为一个数组。且$values['options']存在，那么就执行反序列化操作。我们修改payload为即可触发反序列化。  

![09.png](https://image.3001.net/images/20190221/1550753058_5c6e9d229bf1d.png!small)

### **验证视频：**

攻击者利用此反序列化可以在服务器上执行任意代码，利用此漏洞在服务器上弹出计算器的视频如下：

![验证.gif](https://image.3001.net/images/20190221/1550755207_5c6ea5870ea6a.gif!small)

## **四、安全建议**

### **修复方案如下：**

1.Drupal 8.6.x版本升级到8.6.10版本；

2.Drupal 8.5.x或更早期版本版本升级到8.5.11版本；

3.Drupal 7暂无更新。

###  **缓解措施如下：**

1.禁用RESTful Web Services模块；

2.配置服务器不允许POST/PATCH请求。

 ***本文作者：云鼎实验室，转载请注明来自FreeBuf.COM**

