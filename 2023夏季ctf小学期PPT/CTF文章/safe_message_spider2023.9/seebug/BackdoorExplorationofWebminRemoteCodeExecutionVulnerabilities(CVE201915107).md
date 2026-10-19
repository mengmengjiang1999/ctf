**Author：Ethan@Knownsec 404 Team**

**Time: August 21, 2019**

**Chinese Version:<https://paper.seebug.org/1019/>**

### Introduction

Webmin is a web-based interface for system administration for Unix. Using any
modern web browser, you can setup user accounts, Apache, DNS, file sharing and
much more.

On August 10, 2019, the Webmin CVE-2019-15107 remote code execution
vulnerability was released by penest.

Due to a code execution vulnerability in the password resetting function of
`password_change.cgi` file, this vulnerability allows a malicious third party
to execute malicious code without input validation. Knownsec 404 Team found
that this was because of the backdoor implanted in some versions of the
installation package and source code.

### Recurrence

The official version impated by the vulnerability was Webmin <= 1.920. I used
version 1.920 for the test.

In this version, the triggering of the vulnerability requires the password
reset function to be enabled. In "Webmin-> Webmin Configuration->
Authentication"` option, we should check the box allowing users to set a new
password using the old password.

![](https://images.seebug.org/content/images/2019/08/23/1566533152000-p6.png-w331s)

After Webmin restarts, check the webmin configuration file and you can see
that the value of `passwd_mode` has changed from 0 to 2.

![](https://images.seebug.org/content/images/2019/08/23/1566533152000-p8.png-w331s)

Do packet capture at the password modification, and then add `|ifconfig` to
the old parameter.

![](https://images.seebug.org/content/images/2019/08/23/1566533152000-p21.png-w331s)

I found that the command was successfully executed!

I wanted to try another user, but this was what I got.
![](https://images.seebug.org/content/images/2019/08/23/1566533152000-p20.png-w331s)

The root user here is the root user of the Linux system, I do not know why it
did not work.

Then I tried with another user.

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p22.png-w331s)

The user can be empty or webmin, and this is how I create them:

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p19.png-w331s)

The root is a Linux system account, and its authentication method is `Unix
authenticaton`. The account ethan is a webmin account I created, and its
authentication method is not available.

Why is there such a difference? This is about perl scripts and I want to thank
@Longofo for his help.

### Analysis

First, in the 12th line of `password_change.cgi`, we can know we can only
trigger the vulnerability when `passwd_mode=2`, and this means we must enable
password resetting. Otherwise it will show Password changing is not enabled!

    
    
    $miniserv{'passwd_mode'} == 2 || die "Password changing is not enabled!";

Then look at the 12th to 31st line of `password_change.cgi` :

    
    
    # Is this a Webmin user?
    if (&foreign_check("acl")) {
        &foreign_require("acl", "acl-lib.pl");
        ($wuser) = grep { $_->{'name'} eq $in{'user'} } &acl::list_users();
        if ($wuser->{'pass'} eq 'x') {
            # A Webmin user, but using Unix authentication
            $wuser = undef;
            }
        elsif ($wuser->{'pass'} eq '*LK*' ||
               $wuser->{'pass'} =~ /^\!/) {
            &pass_error("Webmin users with locked accounts cannot change ".
                        "their passwords!");
            }
        }

This code mainly determines whether it is webmin user. And it requests an acl-lib.pl, which can known as the functional file by name. The role of 21st~22nd
line is to get the user in the request and determine whether it belongs to
Webmin user! But why it compares the values of `$wuser` and `x`? . So I tried
to print out the value of `acl::list_users()`.

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p23.png-w331s)

Returned data:

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p14.png-w331s)

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p24.png-w331s)

With the returned data, we can know the root user and the default value of
'pass' is `x`. I create a user that does not choose the authentication method.
The value of `pass` is a string of encrypted string. That is to say, if the
`user` we pass in is the system user and the authentication method is `Unix
authenticaton`, the value of `$wuser` will be `undef`.

Let's print the value of `$wuser`.

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p28.png-w331s)

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p27.png-w331s)

Print out the value of `$wuser` in the `if` conditional statement to confirm
the idea.

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p26.png-w331s)

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p25.png-w331s)

In `perl` language, `undef` is the default value when the variable is not
initialized. In general we see it as empty or 0. It is probably for the
distinction between the modification of the system user password and other
users.

From our analysis above, the value of `$wuser` is `undef` when the user is
root.

    
    
    if ($wuser) {
        # Update Webmin user's password
        $enc = &acl::encrypt_password($in{'old'}, $wuser->{'pass'});
        $enc eq $wuser->{'pass'} || &pass_error($text{'password_eold'},qx/$in{'old'}/);
        $perr = &acl::check_password_restrictions($in{'user'}, $in{'new1'});
        $perr && &pass_error(&text('password_enewpass', $perr));
        $wuser->{'pass'} = &acl::encrypt_password($in{'new1'});
        $wuser->{'temppass'} = 0;
        &acl::modify_user($wuser->{'name'}, $wuser);
        &reload_miniserv();
        }

That is to say, if the system user `user` cannot enter the `if` conditional
statement on line 37, the command execution code of line 40 `qx/...../` cannot
be executed. When the user we pass in is empty or does not exist, the value of
`$wuser` is `{}`, but the `if` conditional statement is entered.

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p29.png-w331s)

Regarding whether the command execution requires `|`, is we look at the
`pass_error` we can know we do not need `|` to perform command execution echo.

    
    
    sub pass_error
    {
    &header(undef, undef, undef, undef, 1, 1);
    print &ui_hr();
    
    print "<center><h3>",$text{'password_err'}," : ",@_,"</h3></center>\n";
    
    print &ui_hr();
    &footer();
    exit;
    }

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p31.png-w331s)

### Interesting Discoveries

I think `qx/..../` is quite strange, because the official patch deletes it
directly:

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p39.png-w331s)

It feels like that this vulnerability is added to it. The version 1.920
downloaded on Github does not have `qx/..../`. No records related to `qx/../`
were found with the `git log -p` command. The source code and installation
package downloaded on sourceforge have vulnerability code. Is this a back
door?

In 2012, the CDN node of SourceForge Korea was suspected to be invaded, and a
backdoor was implanted in the popular download resource phpMyadmin. To know
more about this: https://www.seebug.org/vuldb/ssvid-60402

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p40.png-w331s)

I have also found out some news on Github,
https://github.com/webmin/webmin/issues/947

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p42.png-w331s)

In the 1.890 version, there is also a vulnerability code, and it can't be more
obvious......

I downloaded the 1.890 version from sourceforge. The vulnerabilities are as
follows:

![](https://images.seebug.org/content/images/2019/08/23/1566533153000-p43.png-w331s)

We can know that the trigger of this vulnerability only needs an
'expired`parameter, and the previous`passwd_mode=2` is not necessary.

![](https://images.seebug.org/content/images/2019/08/23/1566533154000-p34.png-w331s)

In other words, the triggering of the vulnerability in the 1.890 version does
not require any dependencies. Is this a mistake or a malicious back door?

### Validating

Here we will verify it in a more intuitive way. Download the source code from
Github and sourceforge.

password_change.cgi file of version 1.920 is as below:

![](https://images.seebug.org/content/images/2019/08/23/1566533154000-p45.png-w331s)

Webmin 1.890 version of the password_change.cgi file

![](https://images.seebug.org/content/images/2019/08/23/1566533154000-p44.png-w331s)

Compare these two files, we will find there is something wrong about the
sourceforge code, and it is very likely that a back door is implanted in it.

After verification, only the sourceforge code and the installation package
have a backdoor vulnerability.

![](https://images.seebug.org/content/images/2019/08/23/1566533154000-p46.png-w331s)

Among them, the dependency of the 1.890 version backdoor vulnerability is the
least, and the most harmful! Guess this should be the initial backdoor, and
later the backdoor was implanted without considering the logic of the code.
This is why the vulnerability trigger is limited!

### Vulnerability Patching

  * Upgrade to version 1.930 directly

  * Temporary patching scheme: you can locate the line where the vulnerability code is, and then cull it. The following figure is version 1.920:

![](https://images.seebug.org/content/images/2019/08/23/1566533154000-p47.png-w331s)

The picture below shows the 1.890 version:

![](https://images.seebug.org/content/images/2019/08/23/1566533154000-p48.png-w331s)

Replace the indicated label with `$miniserv{'passwd_mode'} == 2 || die
"Password changing is not enabled!";`, the replacement code does not have any
backdoor.

### Conclusion

I did not expect an emergency to develop into a study of backdoor documents.
Thanks to @Longofo for helping me to test a lot of files and code. Heige also
published _The stories behind Webmin CVE-2019–15107_ on the medium describing
the process of finding this backdoor discovery:https://medium.com/@80vul/the-stories-behind-cve-2012-5159-198eaad2449d

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
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1020/>

