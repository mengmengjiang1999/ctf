**Author: LoRexxar'@Knownsec 404 Team**  
**Date: December 7, 2018**  
**Chinese Version:<https://paper.seebug.org/756/>**

On December 3, 2018, @L3mOn disclosed a front-end SSRF in Discuz x3.4. By
using a secondary jump and two parsing problems, the SSRF attack chain can be
cleverly completed.

<https://www.cnblogs.com/iamstudy/articles/discuz_x34_ssrf_1.html>

In the process of recurrence with my partner @dawu, it is found that the
vulnerability itself relies on multiple features, resulting in a variety of
reductions in the exploitative environment and strong dependencies on some of
the conditions, which greatly reduces the harm of the vulnerability. Let's
analyze this vulnerability in detail.

# The Conditions of Vulnerability

  * The version ＜ 41eb5bb0a3a716f84b0ce4e4feb41e6f25a980a3 ([The patch link](https://gitee.com/ComsenzDiscuz/DiscuzX/commit/41eb5bb0a3a716f84b0ce4e4feb41e6f25a980a3 "The patch link"))

  * PHP version ＞ PHP 5.3

  * php-curl <= 7.54

  * DZ runs on port 80

  * The default does not affect Linux (not 100% confirmed, the common testing environment of Linux is unaffected)

# Vulnerability Recurrence

## SSRF

First of all, the location of the vulnerability point is:
`/source/module/misc/misc_imgcropper.php line 55`.

![ ](https://images.seebug.org/content/images/2018/12/8209405c-0154-4142-9bac-ff79e9b64e6f.png-w331s)

Here the the variable of `$prefix` is `/` and the remaining code is
controllable, then we enter the function.

`/source/class/class_image.php line 52 Thumb function`

![
](https://images.seebug.org/content/images/2018/12/3d9f053e-b17c-4e73-97ed-60511fb0c7e9.png-w331s)

Then follow into the init function (line 118)

![
](https://images.seebug.org/content/images/2018/12/d1bba71e-a613-43a2-953c-53385327b394.png-w331s)

Obviously, as long as the `parse_url` parses the host, the request can be sent
via `dfsockopen`.

A common trick: since there will add `/` in the front, the source must begin
with `/`.

    
    
    //baidu.com

Such a link will automatically add the protocol, as for how to add it depends
on how the specific client is written.

Then we follow `dfsockopen` to `/source/function/function_core.php line 199`.

![
](https://images.seebug.org/content/images/2018/12/3c438e7b-feae-4316-acdf-220332b932e8.png-w331s)

Then to `source/function/function_filesock.php line 31`.

![
](https://images.seebug.org/content/images/2018/12/d98a4295-9b64-4d3c-bcd9-f26d8eae1c4b.png-w331s)

The main code is in the red box, and you can see that the address of the
request is the corresponding target under `parse_url`.

As mentioned earlier, the front of the link is `/`, so the `parse_url` here is
limited.

![
](https://images.seebug.org/content/images/2018/12/00579f09-193f-4c4f-ab22-31c13afb0510.png-w331s)

Since there is no `scheme`, the link to the final curl access is:

    
    
    ://google.com/

So adding the protocol automatically in the front is just like follows:

    
    
    http://://google.com/

Here occurs a very serious problem: for curl, where exactly does requesting an
empty host go?

In Windows, the version of libcurl: `7.53.0`.

Here you can see that the ip of my local ipv6 is requested.

In the Linux environment (ubuntu), it is `7.47.0` as in the screenshot.

![
](https://images.seebug.org/content/images/2018/12/245d4ae4-3843-4e61-9156-f7fd48ec9c7d.png-w331s)

Having tested a variety of common systems, there is no curl version that will
not report errors during the process, and we temporarily think that it only
affects the server environment of Windows.

Back to the code conditions, we can review the previous conditions:

(1) Firstly we need to ensure that `/{}` is controllable, and there is host
under the `parse_url` operation.

To satisfy this condition, we must first have a clear understanding of the
results of `parse_url`.

In the absence of a protocol, it seems that the protocol or port (: number)
cannot appear in the parameter, otherwise the first segment will not be parsed
into host (don't know the exact reason).

![
](https://images.seebug.org/content/images/2018/12/cbd0a964-52bf-4ad3-81e9-4cb250db0613.png-w331s)

In this case, we only need to remove the HTTP that may appear later, because
in the absence of a protocol, HTTP will be added by default (in general).

(2) Curl must be able to parse empty host into localhost, so the libcurl
version needs to be under 7.54.0, and so far it only affects Windows servers.
(welcome for further rebuttal

(3) DZ runs on port 80

Having satisfied all the conditions, we actually requested arbitrary local
directory.

    
    
    http://://{可控}
    
    ===>
    
    http://127.0.0.1/{可控}

But this is actually useless, so we still need an arbitrary url to jump,
otherwise it makes little sense if it can only attack the local.

# URL Redirector Abuse

In order to be able to interact with the previous requirements, we need an
arbitrary url jump which is the "get" type and does not require login.

Dz will get the value from the referer parameter (not the header parameter)
when in the logout, and then enter the 301 to jump, and the only requirement
here is to have some verification on the host, let’s look at the code.

`/source/function/function_core.php:1498`

![
](https://images.seebug.org/content/images/2018/12/c7ea9b3f-6482-4ec4-b9f8-c8b611203b6a.png-w331s)

The screenshot above explains the main problem with this code, and the core
code is framed in red.

In order for the referer not to change, we must make the host only have one
character, but obviously, if the host can only have one character, we can't
control arbitrary url jump.

So we need to find a way to get `parse_url` and `curl` to parse at odds with
the target of the same url in order to possibly achieve our goal.

    
    
    http://localhost#@www.baidu.com/

`parse_url` parses the above link as `localhost`, and the curl is explained as
`www.baidu.com`.

Let’s capture a packet to take a view:

![
](https://images.seebug.org/content/images/2018/12/4d8c35de-112d-4a9b-9782-6f336339ed70.png-w331s)

We successfully bypassed various limitations.

# Exploits

Now that we have mastered SSRF and arbitrary url jump, we just need to link up
the attack chain. The attack process is as follows:

    
    
    cutimg ssrf link
    =====>
    The server accesses url redirector abuse at the logout
    ====301====>
    Jump to the malicious server
    =====302=====>
    Arbitrary target, such as gophar, http, etc.

Of course, when you first access the cutimg page, you need to get the forghash
first, and the referer should be modified accordingly, otherwise it will be
intercepted directly.

Exp demo

![
](https://images.seebug.org/content/images/2018/12/756f8a53-db10-4bc3-a94f-508d1b90d636.png-w331s)

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
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/981/>

