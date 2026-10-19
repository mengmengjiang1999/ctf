**Author:[HACHp1@Knownsec 404
Team](https://hachp1.github.io/posts/Web%E5%AE%89%E5%85%A8/20190809-kde45ce.html
"HACHp1@Knownsec 404 Team")**  
**Date: August 09, 2019**  
**Chinese Version:<https://paper.seebug.org/1006/>**

## Introduction

KDE Frameworks is a collection of libraries and software frameworks by KDE
readily available to any Qt-based software stacks or applications on multiple
operating systems.They offer a wide variety of commonly needed functionality
solutions like hardware integration, file format support, additional graphical
control elements, plotting functions, spell checking and more and serve as
technological foundation for KDE Plasma 5 and KDE Applications distributed
under the GNU Lesser General Public License (LGPL). The KDE framework is
currently used by several Linux distributions, including Kubuntu,
OpenMandriva, openSUSE, and OpenMandriva.

On July 28, 2019, Dominik Penner (@zer0pwn) found that there was a command
execution vulnerability when the KDE framework version was <= 5.60.0.

On August 5, 2019, Dominik Penner released this 0-day vulnerability on
Twitter. It is the way class KDesktopFile handles `.desktop` or `.directory`
files that has caused this vulnerability. If the victim downloads a
maliciously constructed `.desktop` or `.directory` file, the bash code
injected into the files will be executed.

On August 8, 2019, the KDE community finally fixed it in their updates, and
there was no official patches till that day.

### Gossip

When Dominik Penner released this vulnerability, he did not tell the KDE
community about it and directly posted it on Twitter. A lot of interesting
things happened between Penner and KDE developers later on, but we will not
discuss about them in this paper.

## Affected Version

Operating system with built-in or installed KDE Frameworks version <=5.60.0 ,
such as Kubuntu.

## Recurrence

### Environment Construction

Mirror of virtual machine : kubuntu-16.04.6-desktop-amd64.iso

KDE Framework 5.18.0

Remember to shut down the network since it takes a lot of time to download the
language pack. Enter the system and turn off the iso effect after the
installation is complete, otherwise you will not be able to enter the system.

![](https://images.seebug.org/content/images/2019/08/09/1565340776000-1.png-w331s)

### Recurrence Result

In this article, I reproduced it in three ways. The first and second are just
proof of concept, and the third is what an attacker will do in the real world.

1.PoC1: Create a file named "payload.desktop":

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-2.png-w331s)

Write the payload into it:

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-3.png-w331s)

Open the file manager after saving, and we will find that the written payload
is executed:

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-4.png-w331s)

The file content shows as follows:

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-5.png-w331s)

2.PoC2:

Create a file named".directory":

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-6.png-w331s)

Open it via vi:

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-7.png-w331s)

Write the payload into it:

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-8.png-w331s)

Open the file manager after saving, the payload is successfully executed:

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-9.png-w331s)

3.PoC3: The attacker starts the netcat and waite for connnection:

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-10.png-w331s)

The attacker zips the payload file and mounts it on a web server to induce the
victim to download:

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-11.png-w331s)

The victim unzips it:

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-12.png-w331s)

After that, the payload will be executed and the attacker receives the
connected shell:

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-13.png-w331s)

Impact of this venerability: Although the victims may become alert when the
file is downloaded directly, an attacker can packs the malicious files and use
social engineering to induce victims to unpack it. Whether the victim opens
the unzipped file or not, the malicious code will always be executed, because
the KDE system will call the desktop parsing function after the file is
unzipped.

## Details

Dominik Penner has already explained the vulnerability clearly. But first
let's take a look at Linux's desktop entries.

### Desktop Entry

The XDG Desktop Entry specification defines a standard for applications to
integrate into application menus of desktop environments implementing the XDG
Desktop Menu specification.

Each desktop entry must have a Type and a Name key and can optionally define
its appearance in the application menu.

In other words, it's a specification for parsing desktop items like icon,
name, type.

Development projects applying this specification should add the parsing
configuration in the `.directory` or `.desktop` files.

Details:
<https://wiki.archlinux.org/index.php/Desktop_entries_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87)>

### Causes

KDE's desktop configuration refers to the XDG, but it includes some functions
from KDE and its implementation is also different from the XDG official. These
are the causes of the vulnerability.

It's written in KDE
docs:(<https://userbase.kde.org/KDE_System_Administration/Configuration_Files#Shell_Expansion>):

    
    
    Shell Expansion
    
    So called Shell Expansion can be used to provide more dynamic default values. With shell expansion the value of a configuration key can be constructed from the value of an environment variable.
    
    To enable shell expansion for a configuration entry, the key must be followed by [$e]. Normally the expanded form is written into the users configuration file after first use. To prevent that, it is recommend to lock the configuration entry down by using [$ie].
    Example: Dynamic Entries
    
    The value for the "Email" entry is determined by filling in the values of the $USER and $HOST environment variables. When joe is logged in on joes_host this will result in a value equal to "joe@joes_host". The setting is not locked down.
    
    [Mail Settings]
    Email[$e]=${USER}@${HOST}

To make the setting more flexible , KDE implements and supports dynamic
configuration. It is worth noticing that the `${USER}` is taken from the
environment variable. It's definitely related to command execution.

Every time the KDE desktop system needs to read an icon, the `readEntry`
function is called. We can see the process of code tracking in Penner's
reports. The implementation process of the entire vulnerability is as follows:  
Firstly, create the malicious file as follows:

    
    
    payload.desktop
    
    [Desktop Entry]
    Icon[$e]=$(echo hello>~/POC.txt)

Enter the file manager, and the system will parse the `.desktop` file. Enter
the process of parsing Icon, according to the instructions in the document,
the shell dynamic parsing will be called when the parameter has a `[$e]`:

kdesktopfile.cpp:

    
    
    QString KDesktopFile::readIcon() const
    {
        Q_D(const KDesktopFile);
        return d->desktopGroup.readEntry("Icon", QString()); 
    }

And the`KConfigPrivate::expandString(aValue)` is called:  
kconfiggroup.cpp:

    
    
    QString KConfigGroup::readEntry(const char *key, const QString &aDefault) const
    {
        Q_ASSERT_X(isValid(), "KConfigGroup::readEntry", "accessing an invalid group");
    
        bool expand = false;
    
        // read value from the entry map
        QString aValue = config()->d_func()->lookupData(d->fullName(), key, KEntryMap::SearchLocalized,
                         &expand);
        if (aValue.isNull()) {
            aValue = aDefault;
        }
    
        if (expand) {
            return KConfigPrivate::expandString(aValue);
        }
    
        return aValue;
    }

Then according to the official documentation of KDE, this is the process of
parsing dynamic commands. The program will get the string between the first
`$(` and the first `)` as a command, and then call `popen`:  
kconfig.cpp

    
    
    QString KConfigPrivate::expandString(const QString &value)
    {
        QString aValue = value;
    
        // check for environment variables and make necessary translations
        int nDollarPos = aValue.indexOf(QLatin1Char('$'));
        while (nDollarPos != -1 && nDollarPos + 1 < aValue.length()) {
            // there is at least one $
            if (aValue[nDollarPos + 1] == QLatin1Char('(')) {
                int nEndPos = nDollarPos + 1;
                // the next character is not $
                while ((nEndPos <= aValue.length()) && (aValue[nEndPos] != QLatin1Char(')'))) {
                    nEndPos++;
                }
                nEndPos++;
                QString cmd = aValue.mid(nDollarPos + 2, nEndPos - nDollarPos - 3);
    
                QString result;
    
    // FIXME: wince does not have pipes
    #ifndef _WIN32_WCE
                FILE *fs = popen(QFile::encodeName(cmd).data(), "r");
                if (fs) {
                    QTextStream ts(fs, QIODevice::ReadOnly);
                    result = ts.readAll().trimmed();
                    pclose(fs);
                }
    #endif

This is the code execution process to exploit the vulnerability. You can see
that KDE execute system commands only to get some parameter dynamically such
as `${USER}`. This is not appropriate.

## Official Patches

The official fix it brutally in their latest version: they directly delete the
popen function, and popen cannot parse property `[e]` dynamically anymore.

![](https://images.seebug.org/content/images/2019/08/09/1565340777000-14.png-w331s)

By the way, the official also says:

    
    
    Summary:
    It is very unclear at this point what a valid use case for this feature
    would possibly be. The old documentation only mentions $(hostname) as
    an example, which can be done with $HOSTNAME instead.

## Conclusion

Personally I think this vulnerability represents something out of itself.
Firstly, it's not clear what were the developers thinking when when they were
developing KDE, perhaps to make the framework more flexible. But it is used
only to get the value of the `${USER}` variable according to the document.

I found that flexibility and security are sometimes conflicting to each other.

Dominik Penner directly released the vulnerability without notifying the
official, which is quite controversial. Personally, I think it is better to
send this vulnerability to its developers to get it patched before releasing
it. Many people supported Penner on Twitter and he explained that this was
just because he wanted to submit his 0-day vulnerability before defcon
started.

## Reference

1.<https://gist.github.com/zeropwn/630832df151029cb8f22d5b6b9efaefb>  
2.<https://twitter.com/zer0pwn/status/1158167374799020039>  
3.<https://www.youtube.com/watch?v=l4z7EOQQs84>  
4.<https://mail.kde.org/pipermail/kde-announce/2019-August/000047.html>  
5.<https://cgit.kde.org/kconfig.git/commit/?id=5d3e71b1d2ecd2cb2f910036e614ffdfc895aa22>

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
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1008/>

