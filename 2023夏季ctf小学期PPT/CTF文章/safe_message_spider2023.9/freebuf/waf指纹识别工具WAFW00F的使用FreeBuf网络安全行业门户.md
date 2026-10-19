***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

## 原理

发送正常的 HTTP请求并分析响应；这确定了许多WAF解决方案。  
如果不成功，则发送多个（可能是恶意的）HTTP请求，并使用简单的逻辑来取代它是其中WAF。  
如果还是不成功，则分析先前回复的响应，并使用另一种简单算法来猜测WAF或安全解决方案是否正在积极响应我们的攻击。

其实它的核心就是其中的`main.py`：

    
    
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-    '''
    Copyright (C) 2019, WAFW00F Developers.
    See the LICENSE file for copying permission.
    '''
    import csv
    import io
    import json
    import logging
    import os
    import random
    import re
    import sys
    from collections import defaultdict
    from optparse import OptionParser
    from wafw00f.lib.asciiarts import *
    from wafw00f import __version__, __license__
    from wafw00f.manager import load_plugins
    from wafw00f.wafprio import wafdetectionsprio
    from wafw00f.lib.evillib import urlParser, waftoolsengine, def_headers
    
    class WAFW00F(waftoolsengine):
    
        xsstring = '<script>alert("XSS");</script>'
        sqlistring = "UNION SELECT ALL FROM information_schema AND ' or SLEEP(5) or '"
        lfistring = '../../../../etc/passwd'
        rcestring = '/bin/cat /etc/passwd; ping 127.0.0.1; curl google.com'
        xxestring = '<!ENTITY xxe SYSTEM "file:///etc/shadow">]><pwn>&amphack</pwn>'
    
        def __init__(self, target='www.example.com', debuglevel=0, path='/',
                     followredirect=True, extraheaders={}, proxies=None):
    
            self.log = logging.getLogger('wafw00f')
            self.attackres = None
            waftoolsengine.__init__(self, target, debuglevel, path, proxies, followredirect, extraheaders)
            self.knowledge = dict(generic=dict(found=False, reason=''), wafname=list())
    
        def normalRequest(self):
            return self.Request()
    
        def customRequest(self, headers=None):
            return self.Request(headers=headers)
    
        def nonExistent(self):
            return self.Request(path=self.path + str(random.randrange(100, 999)) + '.html')
    
        def xssAttack(self):
            return self.Request(path=self.path, params= {'s': self.xsstring})
    
        def xxeAttack(self):
            return self.Request(path=self.path, params= {'s': self.xxestring})
    
        def lfiAttack(self):
            return self.Request(path=self.path + self.lfistring)
    
        def centralAttack(self):
            return self.Request(path=self.path, params={'a': self.xsstring, 'b': self.sqlistring, 'c': self.lfistring})
    
        def sqliAttack(self):
            return self.Request(path=self.path, params= {'s': self.sqlistring})
    
        def oscAttack(self):
            return self.Request(path=self.path, params= {'s': self.rcestring})
    
        def performCheck(self, request_method):
            r = request_method()
            if r is None:
                raise RequestBlocked()
            return r
    
        # Most common attacks used to detect WAFs
        attcom = [xssAttack, sqliAttack, lfiAttack]
        attacks = [xssAttack, xxeAttack, lfiAttack, sqliAttack, oscAttack]
    
        def genericdetect(self):
            reason = ''
            reasons = ['Blocking is being done at connection/packet level.',
                       'The server header is different when an attack is detected.',
                       'The server returns a different response code when an attack string is used.',
                       'It closed the connection for a normal request.',
                       'The response was different when the request wasn\'t made from a browser.'
                    ]
            try:
                # Testing for no user-agent response. Detects almost all WAFs out there.
                resp1 = self.performCheck(self.normalRequest)
                if 'User-Agent' in self.headers:
                    del self.headers['User-Agent']  # Deleting the user-agent key from object not dict.
                resp3 = self.customRequest(headers=def_headers)
                if resp1.status_code != resp3.status_code:
                    self.log.info('Server returned a different response when request didn\'t contain the User-Agent header.')
                    reason = reasons[4]
                    reason += '\r\n'
                    reason += 'Normal response code is "%s",' % resp1.status_code
                    reason += ' while the response code to a modified request is "%s"' % resp3.status_code
                    self.knowledge['generic']['reason'] = reason
                    self.knowledge['generic']['found'] = True
                    return True
    
                # Testing the status code upon sending a xss attack
                resp2 = self.performCheck(self.xssAttack)
                if resp1.status_code != resp2.status_code:
                    self.log.info('Server returned a different response when a XSS attack vector was tried.')
                    reason = reasons[2]
                    reason += '\r\n'
                    reason += 'Normal response code is "%s",' % resp1.status_code
                    reason += ' while the response code to cross-site scripting attack is "%s"' % resp2.status_code
                    self.knowledge['generic']['reason'] = reason
                    self.knowledge['generic']['found'] = True
                    return True
    
                # Testing the status code upon sending a lfi attack
                resp2 = self.performCheck(self.lfiAttack)
                if resp1.status_code != resp2.status_code:
                    self.log.info('Server returned a different response when a directory traversal was attempted.')
                    reason = reasons[2]
                    reason += '\r\n'
                    reason += 'Normal response code is "%s",' % resp1.status_code
                    reason += ' while the response code to a file inclusion attack is "%s"' % resp2.status_code
                    self.knowledge['generic']['reason'] = reason
                    self.knowledge['generic']['found'] = True
                    return True
    
                # Testing the status code upon sending a sqli attack
                resp2 = self.performCheck(self.sqliAttack)
                if resp1.status_code != resp2.status_code:
                    self.log.info('Server returned a different response when a SQLi was attempted.')
                    reason = reasons[2]
                    reason += '\r\n'
                    reason += 'Normal response code is "%s",' % resp1.status_code
                    reason += ' while the response code to a SQL injection attack is "%s"' % resp2.status_code
                    self.knowledge['generic']['reason'] = reason
                    self.knowledge['generic']['found'] = True
                    return True
    
                # Checking for the Server header after sending malicious requests
                response = self.attackres
                normalserver = resp1.headers.get('Server')
                attackresponse_server = response.headers.get('Server')
                if attackresponse_server:
                    if attackresponse_server != normalserver:
                        self.log.info('Server header changed, WAF possibly detected')
                        self.log.debug('Attack response: %s' % attackresponse_server)
                        self.log.debug('Normal response: %s' % normalserver)
                        reason = reasons[1]
                        reason += '\r\nThe server header for a normal response is "%s",' % normalserver
                        reason += ' while the server header a response to an attack is "%s",' % attackresponse_server
                        self.knowledge['generic']['reason'] = reason
                        self.knowledge['generic']['found'] = True
                        return True
    
            # If at all request doesn't go, press F
            except RequestBlocked:
                self.knowledge['generic']['reason'] = reasons[0]
                self.knowledge['generic']['found'] = True
                return True
            return False
    
        def matchHeader(self, headermatch, attack=False):
            if attack:
                r = self.attackres
            else: r = rq
            if r is None:
                return
            header, match = headermatch
            headerval = r.headers.get(header)
            if headerval:
                # set-cookie can have multiple headers, python gives it to us
                # concatinated with a comma
                if header == 'Set-Cookie':
                    headervals = headerval.split(', ')
                else:
                    headervals = [headerval]
                for headerval in headervals:
                    if re.search(match, headerval, re.I):
                        return True
            return False
    
        def matchStatus(self, statuscode, attack=True):
            if attack:
                r = self.attackres
            else: r = rq
            if r is None:
                return
            if r.status_code == statuscode:
                return True
            return False
    
        def matchCookie(self, match, attack=False):
            return self.matchHeader(('Set-Cookie', match), attack=attack)
    
        def matchReason(self, reasoncode, attack=True):
            if attack:
                r = self.attackres
            else: r = rq
            if r is None:
                return
            # We may need to match multiline context in response body
            if str(r.reason) == reasoncode:
                return True
            return False
    
        def matchContent(self, regex, attack=True):
            if attack:
                r = self.attackres
            else: r = rq
            if r is None:
                return
            # We may need to match multiline context in response body
            if re.search(regex, r.text, re.I):
                return True
            return False
    
        wafdetections = dict()
    
        plugin_dict = load_plugins()
        result_dict = {}
        for plugin_module in plugin_dict.values():
            wafdetections[plugin_module.NAME] = plugin_module.is_waf
        # Check for prioritized ones first, then check those added externally
        checklist = wafdetectionsprio
        checklist += list(set(wafdetections.keys()) - set(checklist))
    
        def identwaf(self, findall=False):
            detected = list()
            try:
                self.attackres = self.performCheck(self.centralAttack)
            except RequestBlocked:
                return detected
            for wafvendor in self.checklist:
                self.log.info('Checking for %s' % wafvendor)
                if self.wafdetections[wafvendor](self):
                    detected.append(wafvendor)
                    if not findall:
                        break
            self.knowledge['wafname'] = detected
            return detected
    
    def calclogginglevel(verbosity):
        default = 40  # errors are printed out
        level = default - (verbosity * 10)
        if level < 0:
            level = 0
        return level
    
    def buildResultRecord(url, waf):
        result = {}
        result['url'] = url
        if waf:
            result['detected'] = True
            if waf == 'generic':
                result['firewall'] = 'Generic'
                result['manufacturer'] = 'Unknown'
            else:
                result['firewall'] = waf.split('(')[0].strip()
                result['manufacturer'] = waf.split('(')[1].replace(')', '').strip()
        else:
            result['detected'] = False
            result['firewall'] = 'None'
            result['manufacturer'] = 'None'
        return result
    
    def getTextResults(res=None):
        # leaving out some space for future possibilities of newer columns
        # newer columns can be added to this tuple below
        keys = ('detected')
        res = [({key: ba[key] for key in ba if key not in keys}) for ba in res]
        rows = []
        for dk in res:
            p = [str(x) for _, x in dk.items()]
            rows.append(p)
        for m in rows:
            m[1] = f'{m[1]} ({m[2]})'
            m.pop()
        defgen = [
            (max([len(str(row[i])) for row in rows]) + 3)
            for i in range(len(rows[0]))
        ]
        rwfmt = "".join(["{:>"+str(dank)+"}" for dank in defgen])
        textresults = []
        for row in rows:
            textresults.append(rwfmt.format(*row))
        return textresults
    
    def disableStdOut():
        sys.stdout = None
    
    def enableStdOut():
        sys.stdout = sys.__stdout__
    
    def getheaders(fn):
        headers = {}
        if not os.path.exists(fn):
            logging.getLogger('wafw00f').critical('Headers file "%s" does not exist!' % fn)
            return
        with io.open(fn, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                _t = line.split(':', 2)
                if len(_t) == 2:
                    h, v = map(lambda x: x.strip(), _t)
                    headers[h] = v
        return headers
    
    class RequestBlocked(Exception):
        pass
    
    def main():
        parser = OptionParser(usage='%prog url1 [url2 [url3 ... ]]\r\nexample: %prog http://www.victim.org/')
        parser.add_option('-v', '--verbose', action='count', dest='verbose', default=0,
                          help='Enable verbosity, multiple -v options increase verbosity')
        parser.add_option('-a', '--findall', action='store_true', dest='findall', default=False,
                          help='Find all WAFs which match the signatures, do not stop testing on the first one')
        parser.add_option('-r', '--noredirect', action='store_false', dest='followredirect',
                          default=True, help='Do not follow redirections given by 3xx responses')
        parser.add_option('-t', '--test', dest='test', help='Test for one specific WAF')
        parser.add_option('-o', '--output', dest='output', help='Write output to csv, json or text file depending on file extension. For stdout, specify - as filename.',
                          default=None)
        parser.add_option('-i', '--input-file', dest='input', help='Read targets from a file. Input format can be csv, json or text. For csv and json, a `url` column name or element is required.',
                          default=None)
        parser.add_option('-l', '--list', dest='list', action='store_true',
                          default=False, help='List all WAFs that WAFW00F is able to detect')
        parser.add_option('-p', '--proxy', dest='proxy', default=None,
                          help='Use an HTTP proxy to perform requests, examples: http://hostname:8080, socks5://hostname:1080, http://user:pass@hostname:8080')
        parser.add_option('--version', '-V', dest='version', action='store_true',
                          default=False, help='Print out the current version of WafW00f and exit.')
        parser.add_option('--headers', '-H', dest='headers', action='store', default=None,
                          help='Pass custom headers via a text file to overwrite the default header set.')
        options, args = parser.parse_args()
        logging.basicConfig(level=calclogginglevel(options.verbose))
        log = logging.getLogger('wafw00f')
        if options.output == '-':
            disableStdOut()
        print(randomArt())
        if options.list:
            print('[+] Can test for these WAFs:\r\n')
            attacker = WAFW00F(None)
            try:
                m = [i.replace(')', '').split(' (') for i in wafdetectionsprio]
                print(R+'  WAF Name'+' '*24+'Manufacturer\n  '+'-'*8+' '*24+'-'*12+'\n')
                max_len = max(len(str(x)) for k in m for x in k) 
                for inner in m:
                    first = True
                    for elem in inner:
                        if first:
                            text = Y+"  {:<{}} ".format(elem, max_len+2)
                            first = False
                        else:
                            text = W+"{:<{}} ".format(elem, max_len+2)
                        print(text, E, end="")
                    print()
                sys.exit(0)
            except Exception:
                return
        if options.version:
            print('[+] The version of WAFW00F you have is %sv%s%s' % (B, __version__, E))
            print('[+] WAFW00F is provided under the %s%s%s license.' % (C, __license__, E))
            return
        extraheaders = {}
        if options.headers:
            log.info('Getting extra headers from %s' % options.headers)
            extraheaders = getheaders(options.headers)
            if extraheaders is None:
                parser.error('Please provide a headers file with colon delimited header names and values')
        if len(args) == 0 and not options.input:
            parser.error('No test target specified.')
        #check if input file is present
        if options.input:
            log.debug("Loading file '%s'" % options.input)
            try:
                if options.input.endswith('.json'):
                    with open(options.input) as f:
                        try:
                            urls = json.loads(f.read())
                        except json.decoder.JSONDecodeError:
                            log.critical("JSON file %s did not contain well-formed JSON", options.input)
                            sys.exit(1)
                    log.info("Found: %s urls to check." %(len(urls)))
                    targets = [ item['url'] for item in urls ]
                elif options.input.endswith('.csv'):
                    columns = defaultdict(list)
                    with open(options.input) as f:
                        reader = csv.DictReader(f) 
                        for row in reader:
                            for (k,v) in row.items():
                                columns[k].append(v)
                    targets = columns['url']
                else:
                    with open(options.input) as f:
                        targets = [x for x in f.read().splitlines()]
            except FileNotFoundError:
                log.error('File %s could not be read. No targets loaded.', options.input)
                sys.exit(1)
        else:
            targets = args
        results = []
        for target in targets:
            if not target.startswith('http'):
                log.info('The url %s should start with http:// or https:// .. fixing (might make this unusable)' % target)
                target = 'https://' + target
            print('[*] Checking %s' % target)
            pret = urlParser(target)
            if pret is None:
                log.critical('The url %s is not well formed' % target)
                sys.exit(1)
            (hostname, port, path, _, _) = pret
            log.info('starting wafw00f on %s' % target)
            proxies = dict()
            if options.proxy:
                proxies = {
                    "http": options.proxy,
                    "https": options.proxy,
                }
            attacker = WAFW00F(target, debuglevel=options.verbose, path=path,
                        followredirect=options.followredirect, extraheaders=extraheaders,
                            proxies=proxies)
            global rq
            rq = attacker.normalRequest()
            if rq is None:
                log.error('Site %s appears to be down' % hostname)
                continue
            if options.test:
                if options.test in attacker.wafdetections:
                    waf = attacker.wafdetections[options.test](attacker)
                    if waf:
                        print('[+] The site %s%s%s is behind %s%s%s WAF.' % (B, target, E, C, options.test, E))
                    else:
                        print('[-] WAF %s was not detected on %s' % (options.test, target))
                else:
                    print('[-] WAF %s was not found in our list\r\nUse the --list option to see what is available' % options.test)
                return
            waf = attacker.identwaf(options.findall)
            log.info('Identified WAF: %s' % waf)
            if len(waf) > 0:
                for i in waf:
                    results.append(buildResultRecord(target, i))
                print('[+] The site %s%s%s is behind %s%s%s WAF.' % (B, target, E, C, (E+' and/or '+C).join(waf), E))
            if (options.findall) or len(waf) == 0:
                print('[+] Generic Detection results:')
                if attacker.genericdetect():
                    log.info('Generic Detection: %s' % attacker.knowledge['generic']['reason'])
                    print('[*] The site %s seems to be behind a WAF or some sort of security solution' % target)
                    print('[~] Reason: %s' % attacker.knowledge['generic']['reason'])
                    results.append(buildResultRecord(target, 'generic'))
                else:
                    print('[-] No WAF detected by the generic detection')
                    results.append(buildResultRecord(target, None))
            print('[~] Number of requests: %s' % attacker.requestnumber)
        #print table of results
        if len(results) > 0:
            log.info("Found: %s matches." % (len(results)))
        if options.output:
            if options.output == '-':
                enableStdOut()
                print(os.linesep.join(getTextResults(results)))
            elif options.output.endswith('.json'):
                log.debug("Exporting data in json format to file: %s" % (options.output))
                with open(options.output, 'w') as outfile:
                    json.dump(results, outfile, indent=2)
            elif options.output.endswith('.csv'):
                log.debug("Exporting data in csv format to file: %s" % (options.output))
                with open(options.output, 'w') as outfile:
                    csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', 
                        quoting=csv.QUOTE_MINIMAL)
                    count = 0
                    for result in results:
                        if count == 0:
                            header = result.keys()
                            csvwriter.writerow(header)
                            count += 1
                        csvwriter.writerow(result.values())
            else:
                log.debug("Exporting data in text format to file: %s" % (options.output))
                with open(options.output, 'w') as outfile:
                    outfile.write(os.linesep.join(getTextResults(results)))
    
    if __name__ == '__main__':
        if sys.hexversion < 0x2060000:
            sys.stderr.write('Your version of python is way too old... please update to 2.6 or later\r\n')
        main()
    
    

## 安装

github地址：https://github.com/EnableSecurity/wafw00f

官方使用文档：https://github.com/enablesecurity/wafw00f/wiki

安装环境：python3环境 --->使用`pip install wafw00f`进行安装

安装成功后目录：python安装目录中的Lib\site-packages\wafw00f--->例如：C:\Python37\Lib\site-packages\wafw00f

验证：cd到C:\Python37\Lib\site-packages\wafw00f目录中，输入python main.py 如下图说明安装成功  
![image.png](https://image.3001.net/images/20210725/1627174615_60fcb6d710bd5d3ab7b55.png!small)

## 具体使用

这里我们直接使用kali，kali中就有自带WAFW00F：  
![image.png](https://image.3001.net/images/20210725/1627174615_60fcb6d7ed1ba259fb155.png!small)  
输入`wafw00f --help`或者`wafw00f -h`，可以看到很多使用参数：

    
    
    -h, --help            show this help message and exit
      
      -v, --verbose         Enable verbosity, multiple -v options increase
                            verbosity
                            
      -a, --findall         Find all WAFs which match the signatures, do not stop
                            testing on the first one
                            
      -r, --noredirect      Do not follow redirections given by 3xx responses
      
      -t TEST, --test=TEST  Test for one specific WAF
      
      -o OUTPUT, --output=OUTPUT
                            Write output to csv, json or text file depending on
                            file extension. For stdout, specify - as filename.
                            
      -i INPUT, --input-file=INPUT
                            Read targets from a file. Input format can be csv,
                            json or text. For csv and json, a `url` column name or
                            element is required.
                            
      -l, --list            List all WAFs that WAFW00F is able to detect
      
      -p PROXY, --proxy=PROXY
                            Use an HTTP proxy to perform requests, examples:
                            http://hostname:8080, socks5://hostname:1080,
                            http://user:pass@hostname:8080
                            
      -V, --version         Print out the current version of WafW00f and exit.
      
      -H HEADERS, --headers=HEADERS
                            Pass custom headers via a text file to overwrite the
                            default header set.
    
    

`wafw00f -l`列出可以识别出的防火墙：

    
    
    WAF Name                        Manufacturer
      --------                        ------------                                                           
                                                                                                             
      ACE XML Gateway                  Cisco                                                                 
      aeSecure                         aeSecure                         
      AireeCDN                         Airee                            
      Airlock                          Phion/Ergon                      
      Alert Logic                      Alert Logic                      
      AliYunDun                        Alibaba Cloud Computing          
      Anquanbao                        Anquanbao                        
      AnYu                             AnYu Technologies                
      Approach                         Approach                         
      AppWall                          Radware                          
      Armor Defense                    Armor                            
      ArvanCloud                       ArvanCloud                       
      ASP.NET Generic                  Microsoft                        
      ASPA Firewall                    ASPA Engineering Co.             
      Astra                            Czar Securities                  
      AWS Elastic Load Balancer        Amazon                           
      AzionCDN                         AzionCDN                         
      Azure Front Door                 Microsoft                        
      Barikode                         Ethic Ninja                      
      Barracuda                        Barracuda Networks               
      Bekchy                           Faydata Technologies Inc.        
      Beluga CDN                       Beluga                           
      BIG-IP Local Traffic Manager     F5 Networks                      
      BinarySec                        BinarySec                        
      BitNinja                         BitNinja                         
      BlockDoS                         BlockDoS                         
      Bluedon                          Bluedon IST                      
      BulletProof Security Pro         AITpro Security                  
      CacheWall                        Varnish                          
      CacheFly CDN                     CacheFly                         
      Comodo cWatch                    Comodo CyberSecurity             
      CdnNS Application Gateway        CdnNs/WdidcNet                   
      ChinaCache Load Balancer         ChinaCache                       
      Chuang Yu Shield                 Yunaq                            
      Cloudbric                        Penta Security                   
      Cloudflare                       Cloudflare Inc.                  
      Cloudfloor                       Cloudfloor DNS                   
      Cloudfront                       Amazon                           
      CrawlProtect                     Jean-Denis Brun                  
      DataPower                        IBM                              
      DenyALL                          Rohde & Schwarz CyberSecurity    
      Distil                           Distil Networks                  
      DOSarrest                        DOSarrest Internet Security      
      DotDefender                      Applicure Technologies           
      DynamicWeb Injection Check       DynamicWeb                       
      Edgecast                         Verizon Digital Media            
      Eisoo Cloud Firewall             Eisoo                            
      Expression Engine                EllisLab                         
      BIG-IP AppSec Manager            F5 Networks                      
      BIG-IP AP Manager                F5 Networks                      
      Fastly                           Fastly CDN                       
      FirePass                         F5 Networks                      
      FortiWeb                         Fortinet                         
      GoDaddy Website Protection       GoDaddy                          
      Greywizard                       Grey Wizard                      
      Huawei Cloud Firewall            Huawei                           
      HyperGuard                       Art of Defense                   
      Imunify360                       CloudLinux                       
      Incapsula                        Imperva Inc.                     
      IndusGuard                       Indusface                        
      Instart DX                       Instart Logic                    
      ISA Server                       Microsoft                        
      Janusec Application Gateway      Janusec                          
      Jiasule                          Jiasule                          
      Kona SiteDefender                Akamai                           
      KS-WAF                           KnownSec                         
      KeyCDN                           KeyCDN                           
      LimeLight CDN                    LimeLight                        
      LiteSpeed                        LiteSpeed Technologies           
      Open-Resty Lua Nginx             FLOSS                            
      Oracle Cloud                     Oracle                           
      Malcare                          Inactiv                          
      MaxCDN                           MaxCDN                           
      Mission Control Shield           Mission Control                  
      ModSecurity                      SpiderLabs                       
      NAXSI                            NBS Systems                      
      Nemesida                         PentestIt                        
      NevisProxy                       AdNovum                          
      NetContinuum                     Barracuda Networks               
      NetScaler AppFirewall            Citrix Systems                   
      Newdefend                        NewDefend                        
      NexusGuard Firewall              NexusGuard                       
      NinjaFirewall                    NinTechNet                       
      NullDDoS Protection              NullDDoS                         
      NSFocus                          NSFocus Global Inc.              
      OnMessage Shield                 BlackBaud                        
      Palo Alto Next Gen Firewall      Palo Alto Networks               
      PerimeterX                       PerimeterX                       
      PentaWAF                         Global Network Services          
      pkSecurity IDS                   pkSec                            
      PT Application Firewall          Positive Technologies            
      PowerCDN                         PowerCDN                         
      Profense                         ArmorLogic                       
      Puhui                            Puhui                            
      Qiniu                            Qiniu CDN                        
      Reblaze                          Reblaze                          
      RSFirewall                       RSJoomla!                        
      RequestValidationMode            Microsoft                        
      Sabre Firewall                   Sabre                            
      Safe3 Web Firewall               Safe3                            
      Safedog                          SafeDog                          
      Safeline                         Chaitin Tech.                    
      SecKing                          SecKing                          
      eEye SecureIIS                   BeyondTrust                      
      SecuPress WP Security            SecuPress                        
      SecureSphere                     Imperva Inc.                     
      Secure Entry                     United Security Providers        
      SEnginx                          Neusoft                          
      ServerDefender VP                Port80 Software                  
      Shield Security                  One Dollar Plugin                
      Shadow Daemon                    Zecure                           
      SiteGround                       SiteGround                       
      SiteGuard                        Sakura Inc.                      
      Sitelock                         TrueShield                       
      SonicWall                        Dell                             
      UTM Web Protection               Sophos                           
      Squarespace                      Squarespace                      
      SquidProxy IDS                   SquidProxy                       
      StackPath                        StackPath                        
      Sucuri CloudProxy                Sucuri Inc.                      
      Tencent Cloud Firewall           Tencent Technologies             
      Teros                            Citrix Systems                   
      Trafficshield                    F5 Networks                      
      TransIP Web Firewall             TransIP                          
      URLMaster SecurityCheck          iFinity/DotNetNuke               
      URLScan                          Microsoft                        
      UEWaf                            UCloud                           
      Varnish                          OWASP                            
      Viettel                          Cloudrity                        
      VirusDie                         VirusDie LLC                     
      Wallarm                          Wallarm Inc.                     
      WatchGuard                       WatchGuard Technologies          
      WebARX                           WebARX Security Solutions        
      WebKnight                        AQTRONIX                         
      WebLand                          WebLand                          
      RayWAF                           WebRay Solutions                 
      WebSEAL                          IBM                              
      WebTotem                         WebTotem                         
      West263 CDN                      West263CDN                       
      Wordfence                        Defiant                          
      WP Cerber Security               Cerber Tech                      
      WTS-WAF                          WTS                              
      360WangZhanBao                   360 Technologies                 
      XLabs Security WAF               XLabs                            
      Xuanwudun                        Xuanwudun                        
      Yundun                           Yundun                           
      Yunsuo                           Yunsuo                           
      Yunjiasu                         Baidu Cloud Computing            
      YXLink                           YxLink Technologies              
      Zenedge                          Zenedge                          
      ZScaler                          Accenture 
    

### 探测web站点是否存在waf和一些细节

例子1：`wafw00f https://www.baidu.com`(百度肯定有waf）  
![image.png](https://image.3001.net/images/20210725/1627174616_60fcb6d8ba52a8a08d530.png!small)  
这里还能看出它用的服务器应该是`BWS/1.1`，但是它的响应包中返回的服务器是`Apache`，这里我们自己用burp抓包也能看出：  
![image.png](https://image.3001.net/images/20210725/1627174617_60fcb6d97f46f21ec505f.png!small)  
应该是修改了响应包头的返回。比如：进入org/apache/catalina/util
编辑配置文件ServerInfo.properties字段来实现来更改我们tomcat的版本信息  
![image.png](https://image.3001.net/images/20210725/1627174618_60fcb6da24d60d212535b.png!small)![image.png](https://image.3001.net/images/20210725/1627174618_60fcb6dacdf271b801753.png!small)修改为:

    
    
    server.info=Apache Tomcat
    server.number=0.0.0.0
    server.built=Apr 2 2017 07:25:00 UTC
    

将修改后的信息压缩回jar包:

    
    
    # cd  /tomcat/lib
    # jar uvf catalina.jar org/apache/catalina/util/ServerInfo.properties
    

![image.png](https://image.3001.net/images/20210725/1627174619_60fcb6db926dc6e7d5b66.png!small)重启tomcat，验证前后截图如下所示：  
![image.png](https://image.3001.net/images/20210725/1627174620_60fcb6dc5d6f1ba5209d2.png!small)

例子2：`wafw00f https://bbs.ichunqiu.com/`  
![image.png](https://image.3001.net/images/20210725/1627174620_60fcb6dcf2aef3d1e0bea.png!small)这里可以看出来是`Jiasule`WAF。百度一下就得出是知道创宇云WAF了。  
![image.png](https://image.3001.net/images/20210725/1627174621_60fcb6ddc149b6274bcdb.png!small)

