**Author：LoRexxar'@Knownsec 404 Team  
Chinese Version：<https://paper.seebug.org/822/>**

On February 20th, the RIPS team released the article [WordPress 5.0.0 Remote
Code Execution](https://blog.ripstech.com/2019/wordpress-image-remote-code-execution/ "WordPress 5.0.0 Remote Code Execution")(CVE-2019-6977), which
mainly discussed that under the account with author permission, RCE
vulnerability could be formed by means of Post Meta variable overwriting,
directory traversal, and local file inclusion.

However, the principle of vulnerability is only roughly described in the
paper, in which a large number of details of vulnerability are omitted, and
even part of the utilization has corresponding relationship with the back-end
server, thus causing problems in the process of reproduction. Having analyzed
the code, we managed to reproduce the vulnerability completely. Some of the
key utilization points are slightly different form the original text, which
will be illustrated further in this article.

## Vulnerability requirements

The requirements of the vulnerability is constrained as follows:

  * [WordPress commit <= 43bdb0e193955145a5ab1137890bb798bce5f0d2 （WordPress 5.1-alpha-44280）](https://github.com/WordPress/WordPress/commit/43bdb0e193955145a5ab1137890bb798bce5f0d2)
  * An account with author permission

This vulnerability affects servers including Windows, Linux and Mac, and the
back-end image processing library "gd" and "imagick" are also get affected.
The original article mentioned that it only affected release 5.0.0, but now
5.0.0 available on the official website has been fixed. However, after the
update of WordPress 5.1-alpha-44280, the not-updated WordPress 4.9.9-5.0.0 is
still affected by this vulnerability.

## Vulnerability reproduction

The following reproduction process includes some exclusive uses and ways which
does not match the original text, and the reasons will be clarified further.

Upload the image. ![
](https://images.seebug.org/content/images/2019/02/847f50f1-61bb-42e7-9308-792e4b782ca2.png-w331s)

Modify the information. ![
](https://images.seebug.org/content/images/2019/02/2a7b4c30-c2eb-4111-8647-8d50c44dd227.png-w331s)

Keep the datagram and add POST.

    
    
    &meta_input[_wp_attached_file]=2019/02/2-4.jpg#/../../../../themes/twentynineteen/32.jpg

![
](https://images.seebug.org/content/images/2019/02/1866d200-fdb6-40fd-a588-ff9070826e83.png-w331s)

Crop the image. ![
](https://images.seebug.org/content/images/2019/02/9a729cc3-882d-46be-9530-75f4e3db4126.png-w331s)

Keep the datagram and change POST to the following operation, where nonce and
id keep unchanged.

    
    
    action=crop-image&_ajax_nonce=8c2f0c9e6b&id=74&cropDetails[x1]=10&cropDetails[y1]=10&cropDetails[width]=10&cropDetails[height]=10&cropDetails[dst_width]=100&cropDetails[dst_height]=100

Trigger the required cropping. ![
](https://images.seebug.org/content/images/2019/02/93110974-7ae2-42a0-98c2-1855d598780d.png-w331s)

The picture has been sent. ![
](https://images.seebug.org/content/images/2019/02/f2d4cb9a-0514-4b80-b80b-19d7eb2d36ec.png-w331s)

Included, we choose to upload one "test.txt", and then modify the information
again like before.

    
    
    &meta_input[_wp_page_template]=cropped-32.jpg

![
](https://images.seebug.org/content/images/2019/02/fc779278-0572-449d-a540-a7001fb59261.png-w331s)

Click to view the attachment page. If the sensitive code is retained after the
image is cropped, the command is executed successfully.

![
](https://images.seebug.org/content/images/2019/02/b9b8ed60-9736-4d81-a9a3-3a14d7aaabaf.png-w331s)

## The detailed analysis

We can divide the vulnerability utilization chain into 4 major parts:

(1) Modify the `_wp_attached_file` variable of the image in the media library
via Post Meta variable overwriting.

This vulnerability is the core point of the entire utilization chain, and
WordPress chose to fix this vulnerability firstly. The original text mentioned
that the entire utilization chain was affected by another security patch of
4.9.9 and 5.0.1, so only 5.0.0 was affected. During the process of analyzing
and reproducing the updated commit of WordPress, we got the latest version
affected by this vulnerability: [WordPress commit <=
43bdb0e193955145a5ab1137890bb798bce5f0d2 （WordPress
5.1-alpha-44280）](https://github.com/WordPress/WordPress/commit/43bdb0e193955145a5ab1137890bb798bce5f0d2)

(2) Through the cropping function of the image, write the cropped image to
arbitrary directory (directory traversal).

**In WordPress settings, the image path may be affected by a plugin. If the
target image is not in the desired path, WordPress will stitch the file path
into a URL link like`http://127.0.0.1/wp-content/uploads/2019/02/2.jpg`, and
then download the original image from the URL.**

If we construct a file name which includes “?” or “#” and is followed by a
path, it can cause inconsistency in positions of obtaining and writing the
image.

The biggest problem with this part is that the cropping function of the front
end doesn’t exist vulnerability. We can only do this by manually constructing
crop request.

    
    
    action=crop-image&_ajax_nonce=8c2f0c9e6b&id=74&cropDetails[x1]=10&cropDetails[y1]=10&cropDetails[width]=10&cropDetails[height]=10&cropDetails[dst_width]=100&cropDetails[dst_height]=100

PS: When the back-end image library is "Imagick", its Readimage function
cannot read the image of remote http protocol, which requires "https".

(3) Set `_wp_page_template` variable via Post Meta variables overwriting.

This part is briefly introduced in the original text, and it is also the
biggest problem in the whole process of analysis and reproduction. At present
all the released WordPress RCE analyses bypass this section, among which there
are two most important points:

  * How to set this variable? 
  * How to trigger this template reference?

(4) How to make the image contain the sensitive PHP code after being cropped.

This part involves the back-end image library. There are two back-end image
processing libraries used by WordPress, "gd" and "imagick", and the default
priority is to use "imagick" for processing.

  * imagick  
It doesn't handle the "exif" part of the image. Adding sensitive code to
"exif" section will not change it.

  * gd  
The use of "gd" is more difficult. Not only will "gd" process the "exif" part
of the image, but also delete the "PHP" code that appears in the image. Unless
the attacker gets a well-constructed image through "fuzz", the required "PHP"
code can appear just after it has been cropped.

Finally, by combining the above four processes, we can fully exploit this
vulnerability.

### Post Meta variable overwriting

When you edit the image you uploaded, you will trigger `action=edit_post`.

    
    
    wp-admin/includes/post.php line 208

![
](https://images.seebug.org/content/images/2019/02/0d446179-8930-406e-ad05-bbafa8498b14.png-w331s)

`post data` comes from `POST`.

If it has been fixed, there is a repair patch on line 275.

    
    
    $translated = _wp_get_allowed_postdata( $post_data );

<https://github.com/WordPress/WordPress/commit/43bdb0e193955145a5ab1137890bb798bce5f0d2>

This patch directly prohibits the passing of this variable.

    
    
    function _wp_get_allowed_postdata( $post_data = null ) {
        if ( empty( $post_data ) ) {
            $post_data = $_POST;
        }
        // Pass through errors
        if ( is_wp_error( $post_data ) ) {
            return $post_data;
        }
        return array_diff_key( $post_data, array_flip( array( 'meta_input', 'file', 'guid' ) ) );
    }

This function can be followed all the way to `wp-includes/post.php line 3770`.

![
](https://images.seebug.org/content/images/2019/02/82b2b17d-6b02-478e-a317-0e0fb186219c.png-w331s)

`update_post_meta` will traverse and update all the fields.

![
](https://images.seebug.org/content/images/2019/02/aa1b35f5-0912-44f4-a541-73e538380e52.png-w331s)

### Match the variable overwriting to the directory traversal

The corresponding cropping function is as follows:

    
    
    /wp-admin/includes/image.php line 25 

![
](https://images.seebug.org/content/images/2019/02/ce209b1a-31a6-486b-acd1-1968e6e310a2.png-w331s)

The variable src passed here is from the modified `_wp_attached_file`.

In the code, the problem is easily verified. **In WordPress settings, the
image path may be affected by a plugin. If the target image is not in the
desired path, WordPress will stitch the file path into a URL link
like`http://127.0.0.1/wp-content/uploads/2019/02/2.jpg`, and then download the
original image from the URL.**

Here, `_load_image_to_edit_path` is used to complete this operation.

It is just for such reason that, assuming the image we upload is named as
`2.jpg`, the original `_wp_attached_file` becomes `2019/02/2.jpg`.

Then we modify `_wp_attached_file` to `2019/02/1.jpg?/../../../evil.jpg` via
Post Meta variable overwriting, and the original image path here will be
stitched to `{wordpress_path}/wp-content/uploads/2019/02/1.jpg?/../../../evil.jpg`, which obviously does not
exist, so the stitching link will be `http://127.0.0.1/wp-content/uploads/2019/02/2.jpg?/../../../evil.jpg`. The latter part is treated
as GET request and the original picture will be successfully obtained.

The new image path that immediately enters the save function will be stitched
to `{wordpress_path}/wp-content/uploads/2019/02/1.jpg?/../../../cropped-evil.jpg` and we will write a new file successfully.

Later on, save function will call the cropping function of your current image
library to generate the image result(the default is imagick).

    
    
    /wp-includes/class-wp-image-editor.php line 394

![
](https://images.seebug.org/content/images/2019/02/5b0141da-32df-4b58-b856-c448c9c7feb9.png-w331s)

It seems to be no limit here, but in the written target directory, there is a
fake directory, which is `1.jpg?`.

  * Linux and Mac support this fake directory, you can use “?”.
  * But Windows can't have “?” in path, so I changed it to “#”.

    
    
    &meta_input[_wp_attached_file]=2019/02/2-1.jpg#/../../../evil.jpg

Write the file successfully.

    
    
    cropped-evil.jpg

### Control template parameters to cause arbitrary file inclusion

In the original text, this part was simply mentioned, and we encountered many
problems in the process of practice. Even different versions of WordPress will
have different performances. Among them, a variety of utilization methods have
been put forward. Here I mainly talk about one stable way of utilization.

#### Set `_wp_page_template`

Let's firstly analyze under what circumstances we can set `_wp_page_template`.

To be sure, this variable is part of Post Meta, just like `_wp_attached_file`,
which can be assigned to this variable by the previous operation.

![
](https://images.seebug.org/content/images/2019/02/158f6bb3-077a-467c-9c6c-a216d02ea294.png-w331s)

But during the actual testing process, we found that we counldn’t modify and
set this value in any way.

    
    
    /wp-includes/post.php line 3828

![ ](https://images.seebug.org/content/images/2019/02/71a5e22d-bada-49ff-ac7e-9ae1e5b5aa66.png-w331s)

  * If you set this value, but this file does not exist, it will be defined as default.
  * If this value is set, you cannot modify it in this way.

So we may need to upload a new media file and then set this value via variable
overwriting.

#### Load the template

When we successfully set the variable, we find that not all pages will load
the template. We return to the code and the place where the template is
finally loaded is as follows:

    
    
    wp-includes/template.php line 634

![
](https://images.seebug.org/content/images/2019/02/95e922c3-839e-4b00-9db7-0a26a8c37216.png-w331s)

As long as the file name in `$template_names` needs to be loaded, it will be
traversed and loaded in the current theme directory.

Backtracking

    
    
    wp-includes/template.php line 23

![
](https://images.seebug.org/content/images/2019/02/29697c7a-84d4-4cfd-a573-d93a0498754b.png-w331s)

Continuing backtracking, we find that when you visit the page, the page will
call different template load functions through the page properties you access.

    
    
    wp-includes/template-loader.php line 48

![
](https://images.seebug.org/content/images/2019/02/82c029a1-d222-442e-8191-c70cb4c5511b.png-w331s)

Among so many template calling functions, only `get_page_template` and
`get_single_template` call the `get_page_template_slug` function.

    
    
    wp-includes/template.php line 486

![
](https://images.seebug.org/content/images/2019/02/c40734d0-e4e7-47b1-a2d1-d73e486c0793.png-w331s)

The `get_page_template_slug` function gets the `_wp_page_template` value from
the database.

    
    
    /wp-includes/post-template.php line 1755

![
](https://images.seebug.org/content/images/2019/02/c0cc746f-85fc-4878-be3e-ecf32a9049a6.png-w331s)

As long as we can get the template to enter `get_page_template` or
`get_single_template` when it is being loaded, it can be successfully
included.

Due to the difference between the code and the front end, we have not
completely found out what the trigger condition is. We choose the easiest one
to upload a txt file in the repository, and then edit the information and
preview it.

![
](https://images.seebug.org/content/images/2019/02/57cc6235-3c7a-4dd1-8662-d2f05ec180ae.png-w331s)

### Generate an image hidden with malicious code

This part involves the problem of the back-end image library. There are two
back-end image processing libraries used by WordPress, "gd" and "imagick", and
the default priority is to use "imagick" for processing.

  * imagick  
It doesn't handle the "exif" part of the image. Adding sensitive code to exif
section will not change it.

  * gd  
The use of "gd" is more difficult. Not only will "gd" process the "exif" part
of the image, but also delete the PHP code that appears in the image. Unless
the attacker gets a well-constructed image through "fuzz", the required PHP
code can appear just after it has been cropped.

This is not the core part of the vulnerability, so no more details here.

## Repair

(1) Because the vulnerability is mainly through the picture trojan to complete
RCE, and while the back-end image library is "gd", the "exif" part of the
picture information will be removed, as well as the sensitive PHP code.
However, if an attacker carefully designs a picture that is cropped and just
generates sensitive code, it can result in RCE vulnerability. If the back-end
image library is "imagick", adding the sensitive code to the "exif" part of
the image information can cause RCE vulnerability.

This vulnerability has been fixed in all release versions available for
downloading. You can just update to the latest version or overwrite the
current version by yourself.

(2) The general defense method  
Use a third-party firewall for protection such as Knownsec Cloud Waf(Cloud Web
Application Firewall) (https://www.yunaq.com/cyd/)

(3) Technical service consulting  
The consulting hotline of Knownsec: 400-060-9587、028-68360638

## Conclusion

The entire RCE utilization chain consists of four parts. Deep into the
underlying Core logic of WordPress, these four parts are hard to cause
trouble, but they are cleverly connected, and the whole part is unexpectedly
the default configuration, greatly increasing the scope of impact. This kind
of attack utilization chain is quite rare in WordPress, which is extremely
secure. It deserves to be studied.

## About Knownsec & 404 Team

Beijing Knownsec Information Technology Co., Ltd. was established by a group
of high-profile international security experts. It has over a hundred frontier
security talents nationwide as the core security research team to provide
long-term internationally advanced network security solutions for the
government and enterprises.

Knownsec's specialties include network attack and defense integrated
technologies and product R&D under new situations. It provides visualization
solutions that meet the world-class security technology standards and enhances
the security monitoring, alarm and defense abilities of customer networks with
its industry-leading capabilities in cloud computing and big data processing.
The company's technical strength is strongly recognized by the State Ministry
of Public Security, the Central Government Procurement Center, the Ministry of
Industry and Information Technology (MIIT), China National Vulnerability
Database of Information Security (CNNVD), the Central Bank, the Hong Kong
Jockey Club, Microsoft, Zhejiang Satellite TV and other well-known clients.

404 Team, the core security team of Knownsec, is dedicated to the research of
security vulnerability and offensive and defensive technology in the fields of
Web, IoT, industrial control, blockchain, etc. 404 team has submitted
vulnerability research to many well-known vendors such as Microsoft, Apple,
Adobe, Tencent, Alibaba, Baidu, etc. And has received a high reputation in the
industry.

The most well-known sharing of Knownsec 404 Team includes: [KCon Hacking
Conference](http://kcon.knownsec.com/#/ "KCon Hacking Conference"), [Seebug
Vulnerability Database](https://www.seebug.org/ "Seebug Vulnerability
Database") and [ZoomEye Cyberspace Search Engine](https://www.zoomeye.org/
"ZoomEye Cyberspace Search Engine").

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/926/>

