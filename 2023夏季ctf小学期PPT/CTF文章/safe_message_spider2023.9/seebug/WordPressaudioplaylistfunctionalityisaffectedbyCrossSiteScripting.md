**Author: p0wd3r (知道创宇404安全实验室)**

**Date: 2017-03-10**

## 0x00 漏洞概述

### 漏洞简介

近日 Wordpress 发布了
[4.7.3](https://wordpress.org/news/2017/03/wordpress-4-7-3-security-and-maintenance-release/)，在此次更新中修复了一个[利用恶意 MP3 文件的 XSS
漏洞](https://securify.nl/advisory/SFY20160742/wordpress_audio_playlist_functionality_is_affected_by_cross_site_scripting.html)，该漏洞触发点有两处，一个是在服务端输出数据时，另外一个在前端渲染数据时。触发该漏洞有两个前提条件：攻击者需要具有上传
MP3 文件的权限或者能够诱导管理员进行上传，并且还需具有发表文章并添加播放列表的权限。成功触发该漏洞后攻击者可以利用 XSS 进行获取用户信息等敏感操作。

### 漏洞影响

利用 XSS 进行获取用户信息等敏感操作

触发前提：

  1. 具有上传 MP3 文件的权限或者能够诱导管理员进行上传
  2. 具有发表文章并添加播放列表的权限

影响版本： < 4.7.3

## 0x01 漏洞复现

### 环境搭建

只需下载安装相应版本 Wordpress 即可

### 复现

在看具体的漏洞之前，我们先简单了解一下 [ID3](https://en.wikipedia.org/wiki/ID3)，它是一个元数据容器，用来存储
MP3 文件的一些相关信息，例如名称、作者和专辑等等，我们可以用一个Python 的第三方库
[eyeD3](http://eyed3.nicfit.net/) 来对 MP3 文件进行解析和修改，首先我们来解析一下漏洞作者给出的
[PoC](https://securify.nl/advisory/SFY20160742/xss.mp3)：

![id3_xss.png\)](https://images.seebug.org/content/images/2017/03/id3_xss.png-w331s)

可以看到在 title 中存在着 XSS 代码。

接下来我们执行以下几个步骤来触发漏洞：

  1. 登陆后台上传该 MP3 文件
  2. 创建文章
  3. 创建播放列表，把恶意 MP3 文件加入到播放列表中
  4. 发布文章

然后我们点开新发布的文章，发现会弹窗两次：

![xss1.png\)](https://images.seebug.org/content/images/2017/03/xss1.png-w331s)

![xss2.png\)](https://images.seebug.org/content/images/2017/03/xss2.png-w331s)

我们先看第一次弹框，刷新页面，开启动态调试，我们看`wp-includes/media.php`的`wp_playlist_shortcode`函数，该函数用于创建播放列表，在第2112-2118行中有这样一段代码：

    
    
    <noscript>
        <ol><?php
        foreach ( $attachments as $att_id => $attachment ) {
            printf( '<li>%s</li>', wp_get_attachment_link( $att_id ) );
        }
        ?></ol>
    </noscript>

这里将 `wp_get_attachment_link`的值直接输出到了页面上，跟进这个函数：

    
    
    function wp_get_attachment_link( $id = 0, $size = 'thumbnail', $permalink = false, $icon = false, $text = false, $attr = '' ) {
        $_post = get_post( $id );
    
        if ( empty( $_post ) || ( 'attachment' !== $_post->post_type ) || ! $url = wp_get_attachment_url( $_post->ID ) ) {
            return __( 'Missing Attachment' );
        }
    
        if ( $permalink ) {
            $url = get_attachment_link( $_post->ID );
        }
    
        if ( $text ) {
            $link_text = $text;
        } elseif ( $size && 'none' != $size ) {
            $link_text = wp_get_attachment_image( $_post->ID, $size, $icon, $attr );
        } else {
            $link_text = '';
        }
    
        if ( '' === trim( $link_text ) ) {
            $link_text = $_post->post_title;
        }
    
        if ( '' === trim( $link_text ) ) {
            $link_text = esc_html( pathinfo( get_attached_file( $_post->ID ), PATHINFO_FILENAME ) );
        }
    
        ... 
    
        return apply_filters( 'wp_get_attachment_link', "<a href='" . esc_url( $url ) . "'>$link_text</a>", $id, $size, $permalink, $icon, $text );
    }

最终的返回值与`$link_text`有关，根据调试来看，`$link_text`最终取的是
`$_post->post_title`，`$_post->post_title`的值如下：

![post_title.png\)](https://images.seebug.org/content/images/2017/03/post_title.png-w331s)

可见`$link_text`即为我们构造的 payload （图中由于 payload 过长并没有显示完全），接下来继续跟进`apply_filters(
'wp_get_attachment_link', "<a href='" . esc_url( $url ) . "'>$link_text</a>",
$id, $size, $permalink, $icon, $text );`函数直接返回了`$value`：

![apply_filters.png\)](https://images.seebug.org/content/images/2017/03/apply_filters.png-w331s)

![value.png\)](https://images.seebug.org/content/images/2017/03/value.png-w331s)

所以最终输出到两个`<li>`之间的内容是`<a href='http://127.0.0.1:8081/wp-content/uploads/2017/03/xss.mp3'>Summer of Pwnage
</noscript><script>alert(document.cookie);</script></a>`
，其中`</noscript>`对前面的标签进行了闭合，整个过程中并没有进行过滤，从而使 payload 得以被执行：

![view_source.png\)](https://images.seebug.org/content/images/2017/03/view_source.png-w331s)

接下来我们来看第二个弹框，在`/wp-includes/js/mediaelement/wp-playlist.js`第91-105行：

    
    
    renderTracks : function () {
            var self = this, i = 1, tracklist = $( '<div class="wp-playlist-tracks"></div>' );
            this.tracks.each(function (model) {
                if ( ! self.data.images ) {
                    model.set( 'image', false );
                }
                model.set( 'artists', self.data.artists );
                model.set( 'index', self.data.tracknumbers ? i : false );
                tracklist.append( self.itemTemplate( model.toJSON() ) );
                i += 1;
            });
            this.$el.append( tracklist );
    
            this.$( '.wp-playlist-item' ).eq(0).addClass( this.playingClass );
        },

`renderTrack`函数的作用是对播放列表进行填充，这里使用 jQuery
`this.$el.append`将`tracklist`的内容输出的页面中，
`tracklist`和`self.itemTemplate(model.toJSON())`有关，我们通过`console.log`来看一下`self.itemTemplate(model.toJSON())`的值：

![console_log.png\)](https://images.seebug.org/content/images/2017/03/console_log.png-w331s)

可以看到`wp-playlist-item-title`中有我们的 payload，这个过程也并没有进行过滤或转义，从而导致了 XSS 的产生。

总的来说，这个漏洞在利用上虽然不用担心 payload 的构造问题，但是由于需要特殊权限以及文件上传，笔者觉得还是略显鸡肋的。

## 0x02 补丁分析

其实不难看出漏洞的根源在于上传文件后没有对元数据的合法性进行检测，所以 Wordpress 官方做了如下补丁：

![patch.png\)](https://images.seebug.org/content/images/2017/03/patch.png-w331s)

在读取文件元数据的地方对元数据进行过滤。

## 0x03 参考

  * <https://securify.nl/advisory/SFY20160742/wordpress_audio_playlist_functionality_is_affected_by_cross_site_scripting.html>
  * <https://wordpress.org/news/2017/03/wordpress-4-7-3-security-and-maintenance-release/>
  * <https://en.wikipedia.org/wiki/ID3>
  * <http://eyed3.nicfit.net/>
  * https://www.seebug.org/vuldb/ssvid-92753

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/244/>

