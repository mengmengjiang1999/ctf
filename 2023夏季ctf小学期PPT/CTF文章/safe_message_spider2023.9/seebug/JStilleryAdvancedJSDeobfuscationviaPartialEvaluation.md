作者：Minded Security  
项目地址：<https://github.com/mindedsecurity/JStillery>

#### JStillery

Advanced JS Deobfuscation via Partial Evaluation.

See <http://blog.mindedsecurity.com/2015/10/advanced-js-deobfuscation-via-ast-and.html>

#### REPL

<https://mindedsecurity.github.io/jstillery/>

#### Install

    
    
    npm install

#### Usage

###### Cli

Deobfuscate file:

    
    
     ./jstillery_cli.js filename

Deobfuscate from stdin

    
    
    echo 'a= String.fromCharCode(41);b=a'|  ./jstillery_cli.js

###### Server

If you wish change `server/config_server.json` Then launch the server:

    
    
    npm start

Visit <http://0:3001/>

###### RESTServer

Launch server then:

    
    
    $ curl 'http://localhost:3001/deobfuscate' -d '{"source":"a=1"}' -H 'Content-type: application/json' 
    {"source":"a = 1;"}

###### Web UI

Add obfuscated code to the upper text area and press CTRL-ENTER. image
![](https://images.seebug.org/content/images/2018/02/cbb0b606-befd-4dbf-9b09-7006300cd8e6.png-w331s)

#### LICENSE

GPL 3.0

#### Contribute

Feel free to contribute in any way!

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/524/>

