**Author: LoRexxar'@Knownsec 404 Team**  
**Chinese Version:<https://paper.seebug.org/949/>**

On June 11th, the RIPS team released the article [MyBB <= 1.8.20: From Stored
XSS to RCE](https://blog.ripstech.com/2019/mybb-stored-xss-to-rce/), which
mainly discussed a Stored XSS and a file upload vulnerability in MyBB <=18.20.

In fact, this vulnerability chain only depends on normal user auth, which
sounds like a good vulnerability, but whether it is triggered by private
messages or inserted into blog, it really needs the admin click. In addition
to the impact of the vulnerability, the vulnerability point is unexpectedly
delicate. Let's talk about it in detail.

  

# Vulnerability Requirements

## Stored XSS

  * the normal user account which can send messages
  * server with video parse open
  * <=18.20

### RCE in Admin panel via File Write

  * the admin auth account
  * <=18.20

  

# Vulnerability Analysis

The original ariticle gives explanations by constructing multiple
vulnerabilities into one exploit chain, but for analysis, we can just talk
about these two separate vulnerabilities: the Stored XSS and Backend Arbitrary
File Upload Vulnerability.

## Stored XSS

In MyBB and most CMS in the forums, whether it is an article or comment or
anything else, the users need to insert images、links、videos、etc. into the
content, and most of them will use a special markup language just like BBCode.

when users insert `[url]`、`[img]` into the content, the backend will convert
them into corresponding `<a>`、`<img>`when saving or parsing articles, and it
will parse and process the content and tags in a pre-defined way, which is
called the whitelist defense, just like BBCode.

As a result, it is very difficult for an attacker to construct Stored XSS,
because except for these tags, the others will not be parsed(when left and
right angle brackets and double quotes will be filtered).

    
    
    function htmlspecialchars_uni($message)
    {
        $message = preg_replace("#&(?!\#[0-9]+;)#si", "&amp;", $message); // Fix & but allow unicode
        $message = str_replace("<", "&lt;", $message);
        $message = str_replace(">", "&gt;", $message);
        $message = str_replace("\"", "&quot;", $message);
        return $message;
    }

No matter how safe the mechanaism itself is, there are always vulnerabilities.

Let's reorganize the processing in Mybb.

in`/inc/class_parse.php` line 435, function `parse_mycode` is mainly
responsible for dealing with this problem.

    
    
        function parse_mycode($message, $options=array())
        {
            global $lang, $mybb;
    
            if(empty($this->options))
            {
                $this->options = $options;
            }
    
            // Cache the MyCode globally if needed.
            if($this->mycode_cache == 0)
            {
                $this->cache_mycode();
            }
    
            // Parse quotes first
            $message = $this->mycode_parse_quotes($message);
    
            // Convert images when allowed.
            if(!empty($this->options['allow_imgcode']))
            {
                $message = preg_replace_callback("#\[img\](\r\n?|\n?)(https?://([^<>\"']+?))\[/img\]#is", array($this, 'mycode_parse_img_callback1'), $message);
                $message = preg_replace_callback("#\[img=([1-9][0-9]*)x([1-9][0-9]*)\](\r\n?|\n?)(https?://([^<>\"']+?))\[/img\]#is", array($this, 'mycode_parse_img_callback2'), $message);
                $message = preg_replace_callback("#\[img align=(left|right)\](\r\n?|\n?)(https?://([^<>\"']+?))\[/img\]#is", array($this, 'mycode_parse_img_callback3'), $message);
                $message = preg_replace_callback("#\[img=([1-9][0-9]*)x([1-9][0-9]*) align=(left|right)\](\r\n?|\n?)(https?://([^<>\"']+?))\[/img\]#is", array($this, 'mycode_parse_img_callback4'), $message);
            }
            else
            {
                $message = preg_replace_callback("#\[img\](\r\n?|\n?)(https?://([^<>\"']+?))\[/img\]#is", array($this, 'mycode_parse_img_disabled_callback1'), $message);
                $message = preg_replace_callback("#\[img=([1-9][0-9]*)x([1-9][0-9]*)\](\r\n?|\n?)(https?://([^<>\"']+?))\[/img\]#is", array($this, 'mycode_parse_img_disabled_callback2'), $message);
                $message = preg_replace_callback("#\[img align=(left|right)\](\r\n?|\n?)(https?://([^<>\"']+?))\[/img\]#is", array($this, 'mycode_parse_img_disabled_callback3'), $message);
                $message = preg_replace_callback("#\[img=([1-9][0-9]*)x([1-9][0-9]*) align=(left|right)\](\r\n?|\n?)(https?://([^<>\"']+?))\[/img\]#is", array($this, 'mycode_parse_img_disabled_callback4'), $message);
            }
    
            // Convert videos when allow.
            if(!empty($this->options['allow_videocode']))
            {
                $message = preg_replace_callback("#\[video=(.*?)\](.*?)\[/video\]#i", array($this, 'mycode_parse_video_callback'), $message);
            }
            else
            {
                $message = preg_replace_callback("#\[video=(.*?)\](.*?)\[/video\]#i", array($this, 'mycode_parse_video_disabled_callback'), $message);
            }
    
            $message = str_replace('$', '&#36;', $message);
    
            // Replace the rest
            if($this->mycode_cache['standard_count'] > 0)
            {
                $message = preg_replace($this->mycode_cache['standard']['find'], $this->mycode_cache['standard']['replacement'], $message);
            }
    
            if($this->mycode_cache['callback_count'] > 0)
            {
                foreach($this->mycode_cache['callback'] as $replace)
                {
                    $message = preg_replace_callback($replace['find'], $replace['replacement'], $message);
                }
            }
    
            // Replace the nestable mycode's
            if($this->mycode_cache['nestable_count'] > 0)
            {
                foreach($this->mycode_cache['nestable'] as $mycode)
                {
                    while(preg_match($mycode['find'], $message))
                    {
                        $message = preg_replace($mycode['find'], $mycode['replacement'], $message);
                    }
                }
            }
    
            // Reset list cache
            if($mybb->settings['allowlistmycode'] == 1)
            {
                $this->list_elements = array();
                $this->list_count = 0;
    
                // Find all lists
                $message = preg_replace_callback("#(\[list(=(a|A|i|I|1))?\]|\[/list\])#si", array($this, 'mycode_prepare_list'), $message);
    
                // Replace all lists
                for($i = $this->list_count; $i > 0; $i--)
                {
                    // Ignores missing end tags
                    $message = preg_replace_callback("#\s?\[list(=(a|A|i|I|1))?&{$i}\](.*?)(\[/list&{$i}\]|$)(\r\n?|\n?)#si", array($this, 'mycode_parse_list_callback'), $message, 1);
                }
            }
    
            $message = $this->mycode_auto_url($message);
    
            return $message;
        }

When the server gets contents which you request, it will firstly parse images
tag syntax like `[img]`, and then if the server sets
`$this->options['allow_videocode']` true(default True), it will parse video
tags like `[video]`, lastly the [list] tags. Starting from line 488, the
server will deal with tags such as `[url]`.

    
    
    if($this->mycode_cache['callback_count'] > 0)
        {
            foreach($this->mycode_cache['callback'] as $replace)
            {
                $message = preg_replace_callback($replace['find'], $replace['replacement'], $message);
            }
        }

Let's simplify the above process. Suppose we request the content as follows:

    
    
    [video=youtube]youtube.com/test[/video][url]test.com[/url]

The backend will firstly convert `[video]`, and then the content becomes:

    
    
    <iframe src="youtube.com/test">[url]test.com[/url]

Then the backend will convert `[url]`，and finally the content is:

    
    
    <iframe src="youtube.com/test"><a href="test.com"></a>

It seems to be no problems, every tag content will be spliced into the
attributes of the tags, and will be processed by `htmlspecialchars_uni`.

But what if we request the content as follows?

    
    
    [video=youtube]http://test/test#[url]onload=alert();//[/url]&amp;1=1[/video]

Firstly we follow into`/inc/class_parse.php line 1385 mycode_parse_video`.

![](https://images.seebug.org/content/images/2019/06/f5b4a609-d965-4697-815c-1b1887165948.png-w331s)

The link will be splited by function `parse_url` as follows:

    
    
    array (size=4)
      'scheme' => string 'http' (length=4)
      'host' => string 'test' (length=4)
      'path' => string '/test' (length=5)
      'fragment' => string '[url]onmousemove=alert();//[/url]&amp;1=1' (length=41)

In line 1420, each parameter will be processed accourdingly. Since we must
keep `=` and `/`, we choose to put the content after `#`.

![](https://images.seebug.org/content/images/2019/06/2c038542-f524-4984-8cd8-930145021f16.png-w331s)

In line 1501 case youtube, the fragment is spliced into id.

    
    
    case "youtube":
        if($fragments[0])
        {
            $id = str_replace('!v=', '', $fragments[0]); // http://www.youtube.com/watch#!v=fds123
        }
        elseif($input['v'])
        {
            $id = $input['v']; // http://www.youtube.com/watch?v=fds123
        }
        else
        {
            $id = $path[1]; // http://www.youtu.be/fds123
        }
        break;

Finally the parameter id will be filtered by function `htmlspecialchars_uni`,
and then generates the template.

    
    
    $id = htmlspecialchars_uni($id);
    
    eval("\$video_code = \"".$templates->get("video_{$video}_embed", 1, 0)."\";");
    return $video_code;

Of course it does not affect our content above, and at present our content is:

    
    
    <iframe width="560" height="315" src="//www.youtube.com/embed/[url]onload=alert();//[/url]" frameborder="0" allowfullscreen></iframe>

After the processing of `[url]`, the above content becomes:

    
    
    <iframe width="560" height="315" src="//www.youtube.com/embed/<a href="http://onload=alert();//" target="_blank" rel="noopener" class="mycode_url">http://onload=alert();//</a>" frameborder="0" allowfullscreen></iframe>

Let's make it simpler, the link

    
    
    [video=youtube]http://test/test#[url]onload=alert();//[/url]&amp;1=1[/video]

becomes:

    
    
    <iframe src="//www.youtube.com/embed/<a href="http://onload=alert();//"..."></iframe>

Because the href attribute we set in iframe tag has been converted into `<a
href="http://onload=alert();//">`, and the double quote for a href attribute
is closed by that in tag a, the content of a href attribute in tag a becomes
the real attribute of iframe tag, and the onload is effective now.

Finally, the browser will do a simple parsing and spliting, and generates the
tag.

![](https://images.seebug.org/content/images/2019/06/6b786acc-d6b6-41be-951d-9525845662de.png-w331s)

### RCE in Admin panel via File Write

In the backend of Mybb, the admin can customize the templates and themes of
CMS. In addition to the normal theme import, the admin can upload a XML file
to upload many other files, and the server will directly create the
corresponding css file. Of course, the server limits such admin's behavior,
and it requires the admin to create only files ending in `.css`.

    
    
    /admin/inc/functions_themes.php line 264
    
    function import_theme_xml($xml, $options=array())
    {
        ...
        foreach($theme['stylesheets']['stylesheet'] as $stylesheet)
        {
            if(substr($stylesheet['attributes']['name'], -4) != ".css")
            {
                continue;
            }
            ...

It seems no problem, but what's special is that the filename is inserted into
DB when server gets request.

![](https://images.seebug.org/content/images/2019/06/bde73a57-c5a2-4cd9-9a68-8d7a0ee6c56d.png-w331s)

Let's firstly take a look at the database structure.

![](https://images.seebug.org/content/images/2019/06/95f6f9f7-1b52-46a0-b071-ddf2958e0658.png-w331s)

We find the type of name is varchar and there is only 30 bits.

When we upload a XML file like `tttttttttttttttttttttttttt.php.css`, the
filename will be inserted into DB, with only the first 30 bits retained--`tttttttttttttttttttttttttt.php`.

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <theme>
        <stylesheets>
            <stylesheet name="tttttttttttttttttttttttttt.php.css">
                test
            </stylesheet>
        </stylesheets>
    
    </theme>

And then we need a feature to get the name from DB and create file.

In `/admin/modules/style/themes.php line 1252`, this parameter is extracted
from DB.

![](https://images.seebug.org/content/images/2019/06/81cd93cc-6bfe-409e-a3f1-249321dca0c8.png-w331s)

The `theme_stylesheet['name']` is as the key of dictionary.

when it is `$mybb->input['do'] == "save_orders"`, the current theme will be
changed.

![](https://images.seebug.org/content/images/2019/06/a08e471d-37c2-47a9-823b-04ee896cb148.png-w331s)

Having saved the orders, the server will check all files' status. If it does
not exist, the server will create a file and rewrite the content.

![](https://images.seebug.org/content/images/2019/06/b056a8ce-a85c-432a-adc9-7a221499dc7a.png-w331s)

  

# Vulnerability Reproduction

## Store XSS

Find an arbitrary feature such as sendind private messages or new blogs.

![](https://images.seebug.org/content/images/2019/06/9a7a9a33-5a8a-4797-9d32-cdd5d8d92907.png-w331s)

Send the following messages:

    
    
    [video=youtube]http://test/test#[url]onload=alert();//[/url]&amp;amp;1=1[/video]

And read it.

![](https://images.seebug.org/content/images/2019/06/db85eba7-65b2-4106-9060-56588bacc20d.png-w331s)

### RCE in Admin panel via File Write

Find where to import the theme in backend.

![](https://images.seebug.org/content/images/2019/06/f694aec4-199d-4ade-b7c8-5cdaefc3afba.png-w331s)

Construct upload files: test.xml.

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <theme>
        <stylesheets>
            <stylesheet name="tttttttttttttttttttttttttt.php.css">
                test
            </stylesheet>
        </stylesheets>
    
    </theme>

We need allow "Ignore Version Compatibility".

Then find the new theme in Theme list.

![](https://images.seebug.org/content/images/2019/06/580dcd02-ca01-4442-88a6-38e489031c38.png-w331s)

Save it and request the filepath with tid.

![](https://images.seebug.org/content/images/2019/06/e523e128-be26-46de-ad0b-034a0c9d6630.png-w331s)

  

# Patch

  * <https://github.com/mybb/mybb/commit/44fc01f723b122be1bc8daaca324e29b690901d6>

## Store XSS

![](https://images.seebug.org/content/images/2019/06/7a3e003c-246b-4acd-837a-d9b44c86a4d3.png-w331s)

The link of iframe tag will be filtered by function `encode_url`, and the
`[url]` will not continue to be parsed.

### RCE in Admin panel via File Write

![](https://images.seebug.org/content/images/2019/06/41f3a378-13b8-49fd-910a-c21e10a5c97b.png-w331s)

Before checking the suffix of the file name, the name willl be split.

  

# Conclusion

Aside from the actual exploits, what's more special of the vulnerability is
just its universality. BBCode is the solution for the current complex forum
environment. In fact, there may be many CMSs that ignores the same problems as
MyBB. When people think that they understand all the mechanisms of the
machines, they will naturally ignore the problems that have not yet been
discovered. In such case, the security problems has arisen.

# About Knownsec & 404 Team

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
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/954/>

