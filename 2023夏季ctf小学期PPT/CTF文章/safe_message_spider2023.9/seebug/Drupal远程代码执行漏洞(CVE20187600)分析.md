作者：绿盟科技  
来源：[http://blog.nsfocus.net/cve-2018-7600-analysis/?from=timeline&isappinstalled=0](http://blog.nsfocus.net/cve-2018-7600-analysis/?from=timeline&isappinstalled=0)

近日，流行的开源内容管理框架Drupal曝出一个远程代码执行漏洞，漏洞威胁等级为高危，攻击者可以利用该漏洞执行恶意代码，导致网站完全被控制。漏洞对应的CVE编号为CVE-2018-7600。

本篇文章对Drupal 8 –
CVE-2017-7600漏洞进行了详细分析。这个漏洞看起来是一个漏洞，其实我认为，它是由两个小的鸡肋问题组成的。具体是什么呢？

#### 漏洞分析

这个漏洞的根本原因出在drupal对表单的渲染上：

![](https://images.seebug.org/content/images/2018/04/ff236de5-79cb-459e-a399-0091c34eb9cb.png-w331s)

可见，在drupal中，我们不需要直接写html表单，而是先创建一个数组，表单呈现引擎通过位于`\drupal\core\lib\Drupal\Core\Form\FormBuilder.php`文件中的buildForm方法构造出一个名为$form表单，然后成对应的html表单进行呈现。

通过下图buildform的定义，可以看出它是用来构造一个表单的

![](https://images.seebug.org/content/images/2018/04/6b62d7dd-26ee-46ee-a033-b85c08b24cb3.png-w331s)

最终的$form是如下图这个样子：

![](https://images.seebug.org/content/images/2018/04/4e9e1f43-6e71-406c-bf0d-24dec9a4deb9.png-w331s)

这个漏洞，恰恰就出在了这里。

但是对于一个drupal框架的应用程序来说，后台表单数组都是开发者写好的，像这个样子

    
    
    public function form(array $form, FormStateInterface $form_state) {
    $user = $this->currentUser();
    /** @var \Drupal\user\UserInterface $account */
    $account = $this->entity;
    $admin = $user->hasPermission('administer users');
    // Pass access information to the submit handler. Running an access check
    // inside the submit function interferes with form processing and breaks
    // hook_form_alter().
    $form['administer_users'] = [
    '#type' => 'value',
    '#value' => $admin,
    ];
    
    $form['#attached']['library'][] = 'core/drupal.form';
    
    // For non-admin users, populate the form fields using data from the
    // browser.
    if (!$admin) {
    $form['#attributes']['data-user-info-from-browser'] = TRUE;
    }
    
    // Because the user status has security implications, users are blocked by
    // default when created programmatically and need to be actively activated
    // if needed. When administrators create users from the user interface,
    // however, we assume that they should be created as activated by default.
    if ($admin) {
    $account->activate();
    }
    
    // Start with the default user account fields.
    $form = parent::form($form, $form_state, $account);
    
    return $form;
    }

攻击者是无法改变表单数组元素的key值的。

很多应用都提供了如下的一个便利的方法：

比如要注册一个用户，用户名、密码、邮箱、电话，这些东西都填好了。当点击提交的时候，网站告诉你，用户名已存在。

这时候，你会发现，密码、邮箱、电话这些元素不需要你再次填写了，页面已经将保存下来了。

drupal系统同样有这样的功能，具体如何实现的呢？下面我们做个试验：

我们先提交个正常的表单

先在buildform函数返回处下断后

![](https://images.seebug.org/content/images/2018/04/842dce03-d16d-48e5-b61e-ac0919072a34.png-w331s)

填写表单并提交

![](https://images.seebug.org/content/images/2018/04/8e37c457-dab6-4d6f-93f1-42639dd0f7a5.png-w331s)

页面跳转到注册成功页面，

![](https://images.seebug.org/content/images/2018/04/fe4aa275-35c5-4aaa-ad55-af36dde22551.png-w331s)

我们在buildform函数返回处下的断点根本没有断下来。

接着我们再按着上面的表单一模一样的注册一个看看：

![](https://images.seebug.org/content/images/2018/04/63ee0b4a-5617-458d-8c30-b6d2e41ba3e3.png-w331s)

但这次呢，在断点处成功断下了：

![](https://images.seebug.org/content/images/2018/04/7b2e2f10-d3e2-4fdc-8d8c-d1fed8a98e02.png-w331s)

在这处断点，我们把name的值改为“kingsguard_test_1”试试

![](https://images.seebug.org/content/images/2018/04/436bf296-9e48-4457-9681-2754331bd7a2.png-w331s)

这次的返回页面如下：

![](https://images.seebug.org/content/images/2018/04/9b30c588-442b-4784-8a90-af5326d07c8c.png-w331s)

整个流程是：

  1. 用户填写表单->表单没有问题->返回注册成功页面
  2. 用户填写表单->表单内容有问题（例如用户名已被注册）->调用buildform方法，把用户传入的内容一同构造为表单数组->渲染表单数组为html页面返回

这就是刚刚在buildform断点处把name值由kingsguard改为`kingsguard_test_1`，返回的页面里username值也变成`kingsguard_test_1`的原因。

到这里，攻击链已经很明确了，攻击者传入的值，可以通过buildform（方法构造表单数组，并且这个表单数组接下来还会被drupal表单呈现引擎解析为html页面。

当我们在这个注册表单页面里，如果想上传一张图片

![](https://images.seebug.org/content/images/2018/04/3268e85c-b020-4292-96a3-6a048c98bcbd.png-w331s)

这时候发送的请求如下

![](https://images.seebug.org/content/images/2018/04/d3394a06-0cac-4200-ba9f-92ad74cb7632.png-w331s)

当上传成功后，往往有一个缩略图显示在那，如下图菊花处：

![](https://images.seebug.org/content/images/2018/04/5c21389e-b852-4809-a46d-5d7c2756b1fe.png-w331s)

这个缩略图，是通过`drupal\core\modules\file\src\Element\ManagedFile.php`文件中的uploadAjaxCallback方法来解析。

注意，还记的上文buildform方法吗？buildform生成form数组传递给uploadAjaxCallback方法来解析，目的是在返回页面上显示那个缩率的菊花。

既然流程已经捋顺了，我们通过构造poc来动态调试下，发送如下图post包：

![](https://images.seebug.org/content/images/2018/04/7212b3d2-9afc-4792-921c-5870f825f64a.png-w331s)

首先会进入buildform函数来构造表单数组，接下来这个表单数组($form)会进入uploadAjaxCallback方法。

看下这个uploadAjaxCallback方法：

![](https://images.seebug.org/content/images/2018/04/81331ae3-6c2b-4565-af6f-89eee1e25b72.png-w331s)

传入uploadAjaxCallback方法中的$form变量，就是buildform方法生成的表单数组：

![](https://images.seebug.org/content/images/2018/04/9a5ee998-ac27-4e51-9625-3f1db9be1e21.png-w331s)

$form数组传入uploadAjaxCallback方法中后,可以看到有这么一行（下图红框处）：

![](https://images.seebug.org/content/images/2018/04/ccc7cc3e-2651-43fd-bc4a-3f442eddbdff.png-w331s)

`$form_parents`变量竟然可以从get中传入，意味着这个变量可控,其实就是我们poc中的`element_parents=account/mail/%23value`。

通过poc，此处的`$form_parents`变量如下图

![](https://images.seebug.org/content/images/2018/04/a4f79331-acc5-4008-ba29-c495397d67bc.png-w331s)

`$form_parents`变量和form

新的form变量如下：

![](https://images.seebug.org/content/images/2018/04/1bb80b17-e572-4473-a658-2e21c3630f05.png-w331s)

接下来看这里的renderRoot方法：

![](https://images.seebug.org/content/images/2018/04/8102d0d5-5298-4817-9636-32bb22e4686d.png-w331s)

此处传入的$form变量为：

![](https://images.seebug.org/content/images/2018/04/b75f1439-86ea-475e-a988-6436b169495a.png-w331s)

继续看renderRoot方法：

    
    
    public function renderRoot(&$elements) {
    // Disallow calling ::renderRoot() from within another ::renderRoot() call.
    if ($this->isRenderingRoot) {
    $this->isRenderingRoot = FALSE;
    throw new \LogicException('A stray renderRoot() invocation is causing bubbling of attached assets to break.');
    }
    
    // Render in its own render context.
    $this->isRenderingRoot = TRUE;
    $output = $this->executeInRenderContext(new RenderContext(), function () use (&$elements) {
    return $this->render($elements, TRUE);
    });
    $this->isRenderingRoot = FALSE;
    
    return $output;
    }

里面调用了render方法

继续看render方法：

    
    
    public function render(&$elements, $is_root_call = FALSE) {
    // Since #pre_render, #post_render, #lazy_builder callbacks and theme
    // functions or templates may be used for generating a render array's
    // content, and we might be rendering the main content for the page, it is
    // possible that any of them throw an exception that will cause a different
    // page to be rendered (e.g. throwing
    // \Symfony\Component\HttpKernel\Exception\NotFoundHttpException will cause
    // the 404 page to be rendered). That page might also use
    // Renderer::renderRoot() but if exceptions aren't caught here, it will be
    // impossible to call Renderer::renderRoot() again.
    // Hence, catch all exceptions, reset the isRenderingRoot property and
    // re-throw exceptions.
    try {
    return $this->doRender($elements, $is_root_call);
    }
    catch (\Exception $e) {
    // Mark the ::rootRender() call finished due to this exception & re-throw.
    $this->isRenderingRoot = FALSE;
    throw $e;
    }
    }

里面调用了doRender方法

继续看doRender方法：

在这个方法的505行

![](https://images.seebug.org/content/images/2018/04/0ec9ee09-3f21-4ca0-8848-5ac059735970.png-w331s)

调用call_user_func方法

此处的参数如下：

![](https://images.seebug.org/content/images/2018/04/ba2d2e9c-55ed-4555-b083-49378d40dac5.png-w331s)

可见，这里的

`$callable=”exec”`

`$elements[‘#children’]=”kingsguard_text”`(这里我们传入的恶意代码，这里我就不演示了)

#### 总结:

这个漏洞看起来是一个漏洞，其实我认为，它是由两个小的鸡肋的问题组成的，第一次就是在buildform处，用户传入的变量没有受到限制，导致可以传入mail[#post_render]、mail[#type]这样的变量，但是单单这个问题，还不严重，因为对于最终渲染的html页面来说，传入的数组仍然是数组，不能被当成元素来解析。但是偏偏uploadAjaxCallback方法中的`$form_parents`变量是直接通过get(‘element_parents’)得来的，这下两个一结合，`$form_parents`把之前传入的数值当成元素了，这下就造成了一个大洞。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/571/>

