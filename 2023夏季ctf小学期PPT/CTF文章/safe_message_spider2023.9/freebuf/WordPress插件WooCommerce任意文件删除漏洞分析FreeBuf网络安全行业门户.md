## 前言

**近期，研究人员在WordPress的权限处理机制中发现了一个安全漏洞，而这个漏洞将允许WordPress插件实现提权。其中一个典型例子就是WooCommerce，该插件是目前最热门的一款电子商务插件，并且拥有400万+的安装量。简而言之，这个漏洞将允许商铺管理员删除目标服务器上的特定文件，并接管管理员帐号。**

![页首配图](https://image.3001.net/images/20181119/1542631035_5bf2ae7bad11b.png!small)

## 漏洞影响

我们检测并上报了WooCommerce中存在的一个文件删除漏洞，这个漏洞已经在WooCommerce的v3.4.6版本中成功修复。任意文件删除漏洞在大多数情况下并不会被认为是一种高危漏洞，因为攻击者能做的只有通过删除网站的index.php文件来实现拒绝服务攻击。这篇文章主要介绍的是如何删除WordPress服务器中的特定文件，并禁用安全检测，最终导致目标网站被完全接管。实际上，导致该漏洞存在的本质原因是WordPress的权限系统设计存在缺陷，并影响到了400万+的WooCommerce商铺。

接下来，攻击者只需要拿到商铺管理员的用户角色即可。商铺管理员，能够管理订单、产品和客户，这种访问权限可以通过XSS漏洞或网络钓鱼攻击来获得。当漏洞成功利用之后，商铺管理员将能够接管任何一个管理员帐号，然后在服务器上执行代码。

### 漏洞演示

视频地址：<https://blog.ripstech.com/videos/wordpress-design-flaw.mp4>

漏洞扫描报告：【[RIPS扫描报告](https://demo.ripstech.com/projects/woocommerce_3.4.5/)】

## 技术细节

WordPress的权限处理机制主要是通过给不同角色提供不同的功能来实现的，当商铺管理员角色被定义之后，它便会给这个角色分配edit_users功能，这样他们就可以直接管理商铺的客户账号了。整个权限分配过程发生在插件插件饿的安装过程当中。woocommerce/includes/class-wc-install.php：

    
    
    //Shop manager role.
    
    add_role(
    
           'shop_manager',      // Internal name of the new role
    
           'Shop manager',      // The label for displaying
    
           array(               // Capabilities
    
                    ⋮
    
                  'read_private_posts'     => true,
    
                  'edit_users'             => true,
    
                  'edit_posts'             => true,
    
                    ⋮
    
           )
    
    );

角色权限信息会以WordPress核心设置存储在数据库中，这也就意味着用户角色现在已经独立于插件了，即使插件不启用，也不会影响到相关的角色权限。

当一名通过身份验证的用户尝试修改其他用户信息时，便会调用current_user_can()函数，然后确保只有特权用户可以执行这种操作。current_user_can()函数调用样例：

    
    
    $target_user_id= $_GET['target_user_id'];
    
    if(current_user_can('edit_user',$target_user_id)) {
    
        edit_user($target_user_id);
    
    }

调用的验证逻辑如下：这个用户想使用$target_user_id这个ID来修改特定的用户，他是否有权限执行？

默认配置下，edit_users功能允许有权限的用户（例如商铺管理员）来编辑其他用户，甚至是管理员用户，然后执行类似密码更新这样的操作。出于安全因素考虑，WooCommerce需要指定商铺管理员是否能够编辑用户，因此，插件需要增加meta权限功能。Meta功能可以被current_user_can()调用。默认行为下函数返回的值为true，但meta权限函数返回的值可以决定当前用户是否可以执行这样的操作。下面给出的是WooCommerce
meta权限过滤器的抽象函数代码：

    
    
    function disallow_editing_of_admins( $capability, $target_user_id ) {
    
        
    
        // If the user is an admin return false anddisallow the action
    
        if($capability == "edit_user"&& user_is_admin($target_user_id)) {
    
            return false;
    
        } else {
    
            return true;
    
        }
    
    }
    
    add_filter('map_meta_cap', 'disallow_editing_of_admins');

比如说，当current_user_can(‘edit_user’, 1)被调用时，过滤器将会判断ID为1
($target_user_id)的用户是否是管理员，并根据结果来决定是否允许用户操作。

## 商铺管理员禁用插件

默认情况下，只有管理员可以禁用插件。但是这个漏洞允许商铺管理员删除服务器上的任意可写文件，所以我们我们额可以通过删除WooCommerce的主文件-woocommerce.php来禁止WordPress加载该插件。

这个文件删除漏洞存在于WooCommerce的日志记录功能中，日志会以.log文件的形式存储在wp-content目录中。当商铺管理员想要删除日志文件时，他需要以GET参数来提交文件名。下面显示的代码段就是存在漏洞的部分：

### woocommerce/includes/admin/class-wc-admin-status.php

    
    
    class WC_Admin_Status
    
    {
    
        public static function remove_log()
    
        {
    
        ⋮
    
            $log_handler = newWC_Log_Handler_File();
    
           $log_handler->remove(wp_unslash($_REQUEST['handle']));
    
    }

### woocommerce/includes/log-handlers/class-wc-log-handler-file.php

    
    
    class WC_Log_Handler_File extends WC_Log_Handler
    
    {
    
        public function remove($handle)
    
        {
    
        ⋮
    
            $file = trailingslashit(WC_LOG_DIR) .$handle;
    
        ⋮
    
    unlink($file);

这里的问题就在于，文件名($handle)会被添加到日志目录(wp-content/wc-logs/)后，然后传递给unlink()函数。在设置“$handle../../plugins/woocommerce-3.4.5/woocommerce.php”时，文件wp-content/wc-logs/../../plugins/woocommerce-3.4.5/woocommerce.php将会被删除，并导致WooCommerce被禁用。

## 总结

在之前的[文章](https://blog.ripstech.com/2018/wordpress-file-delete-to-code-execution/)中，我们介绍过如何去利用WordPress的文件删除漏洞了，并且演示了如何将文件删除提升为远程代码执行。这篇文章主要介绍的是WordPress插件中的文件删除漏洞，而这些漏洞将允许攻击者在使用了meta权限的WordPress站点上实现提权。值得一提的是，这种设计缺陷短时间内是无法修复的，而且文件删除漏洞很常见，甚至是WordPress的内核本身也存在这种漏洞。除此之外，在某些特定环境下文件删除漏洞还可以配合Phar反序列化漏洞一起使用。

 ***参考来源：[ripstech](https://blog.ripstech.com/2018/wordpress-design-flaw-leads-to-woocommerce-rce/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

