```
├── changelog.md                                 # CHANGE LOG PROJECT :D
├── pyproject.toml
├── README.md
├── requirements.txt
├── requirements.yaml
├── src
│   ├── bowlplate
│   │   ├── .env.example                         # ENV EXAMPLE HERE
│   │   ├── application                          # this HOW application started
│   │   │   ├── controller
│   │   │   │   ├── selector.py                  # CLI model UNIX (but not implemented right now)
│   │   │   │   └── webapp.py                    # webapp run engine
│   │   │   ├── ui
│   │   │   │   ├── handler.py                   # handler path webui
│   │   │   │   └── WebUI
│   │   │   │       ├── frontend
│   │   │   │       └── static
│   │   │   └── __init__.py
│   │   ├── assets
│   │   ├── bootstrap                            # bootstrap make others package easly import without long path
│   │   │   ├── bootstrap.py
│   │   │   ├── config.py
│   │   │   └── sql.py
│   │   ├── contract                             # ABC contract
│   │   │   ├── database
│   │   │   │   └── Storage.py
│   │   │   ├── file
│   │   │   │   ├── base.py
│   │   │   │   ├── response.py
│   │   │   │   └── __init__.py
│   │   │   ├── logger
│   │   │   │   ├── logger.py
│   │   │   │   └── __init__.py
│   │   │   ├── model
│   │   │   │   └── base.py
│   │   │   ├── serverapp
│   │   │   │   ├── base.py
│   │   │   │   └── __init__.py
│   │   │   ├── ui
│   │   │   │   └── local.py
│   │   │   └── __init__.py
│   │   ├── data                                 # full of configuration, must be `*.json` cause automated load by RE (Registry)
│   │   │   ├── config
│   │   │   │   ├── client
│   │   │   │   │   └── config.json
│   │   │   │   ├── registry
│   │   │   │   │   ├── config.json
│   │   │   │   │   ├── metadata.json
│   │   │   │   │   └── package
│   │   │   │   ├── server
│   │   │   │   │   ├── security.json
│   │   │   │   │   ├── server.json
│   │   │   │   │   └── service.json
│   │   │   │   ├── system
│   │   │   │   │   ├── config.py
│   │   │   │   │   └── __init__.py
│   │   │   │   └── __init__.py
│   │   │   ├── database                         # file *.db here :D
│   │   │   ├── temp                             # temp file, (currently not used, maybe in the future)
│   │   │   └── __init__.py
│   │   ├── domain                               # logic here
│   │   │   ├── .your_code_here
│   │   │   ├── config
│   │   │   │   └── reader.py
│   │   │   ├── hooks
│   │   │   │   ├── core
│   │   │   │   │   ├── event.py
│   │   │   │   │   ├── eventbus.py
│   │   │   │   │   ├── model.py
│   │   │   │   │   └── namespace.py
│   │   │   │   ├── hooks.py
│   │   │   │   └── __init__.py
│   │   │   ├── sysmd32
│   │   │   │   └── boot
│   │   │   │       ├── model.py
│   │   │   │       └── service.py
│   │   │   ├── web_core
│   │   │   │   ├── bootstrap.py
│   │   │   │   ├── controller
│   │   │   │   │   ├── health.py
│   │   │   │   │   └── security.py
│   │   │   │   ├── data
│   │   │   │   │   └── configuration
│   │   │   │   │       ├── security
│   │   │   │   │       │   ├── authfactor.py
│   │   │   │   │       │   └── config_obsecurity.py
│   │   │   │   │       └── sys
│   │   │   │   │           └── SecurityConfig.py
│   │   │   │   ├── main_controller.py
│   │   │   │   ├── plugin
│   │   │   │   │   ├── plugin.py
│   │   │   │   │   ├── private
│   │   │   │   │   │   ├── crashguard
│   │   │   │   │   │   │   └── guardian.py
│   │   │   │   │   │   ├── flaskSecurity
│   │   │   │   │   │   │   └── main.py
│   │   │   │   │   │   ├── security
│   │   │   │   │   │   │   ├── loader.py
│   │   │   │   │   │   │   ├── middleware
│   │   │   │   │   │   │   │   ├── ProtectChain.py
│   │   │   │   │   │   │   │   ├── protector.py
│   │   │   │   │   │   │   │   ├── SecurityMiddleware.py
│   │   │   │   │   │   │   │   └── __init__.py
│   │   │   │   │   │   │   ├── utils
│   │   │   │   │   │   │   └── __init__.py
│   │   │   │   │   │   ├── serverHealth
│   │   │   │   │   │   │   └── main.py
│   │   │   │   │   │   └── __init__.py
│   │   │   │   │   └── public
│   │   │   │   │       └── test
│   │   │   │   │           └── main.py
│   │   │   │   ├── protector                       # we currently would remove this one and change to plugin flask, (version 2.1.x will removed)
│   │   │   │   │   ├── auth
│   │   │   │   │   │   ├── factor
│   │   │   │   │   │   │   ├── af_four.py
│   │   │   │   │   │   │   ├── af_one.py
│   │   │   │   │   │   │   ├── af_three.py
│   │   │   │   │   │   │   └── af_two.py
│   │   │   │   │   │   └── loader.py
│   │   │   │   │   ├── csrf
│   │   │   │   │   │   ├── csrf
│   │   │   │   │   │   │   ├── csrfmod.py
│   │   │   │   │   │   │   ├── detector.py
│   │   │   │   │   │   │   ├── generator.py
│   │   │   │   │   │   │   ├── model.py
│   │   │   │   │   │   │   ├── validate.py
│   │   │   │   │   │   │   └── __init__.py
│   │   │   │   │   │   └── CSRF_protection.py
│   │   │   │   │   ├── errorpage
│   │   │   │   │   │   └── ErrorHandler.py
│   │   │   │   │   ├── input
│   │   │   │   │   │   └── InputValidator.py
│   │   │   │   │   ├── obsec
│   │   │   │   │   │   └── Obsecurity.py
│   │   │   │   │   ├── ratelimit
│   │   │   │   │   │   ├── attack_detector.py
│   │   │   │   │   │   ├── fingerprint.py
│   │   │   │   │   │   ├── models.py
│   │   │   │   │   │   ├── pattern_analyzer.py
│   │   │   │   │   │   ├── rate_limiter.py
│   │   │   │   │   │   └── store.py
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── rendering
│   │   │   │   │   └── processor.py
│   │   │   │   ├── utils
│   │   │   │   │   ├── crypto
│   │   │   │   │   │   └── encryption.py
│   │   │   │   │   ├── decorators
│   │   │   │   │   │   └── auth.py
│   │   │   │   │   ├── extractor
│   │   │   │   │   ├── logging
│   │   │   │   │   │   └── log.py
│   │   │   │   │   ├── request
│   │   │   │   │   ├── server
│   │   │   │   │   │   └── secretz.py
│   │   │   │   │   ├── validator
│   │   │   │   │   │   └── header
│   │   │   │   │   │       └── hvalidator.py
│   │   │   │   │   └── __init__.py
│   │   │   │   └── __init__.py
│   │   │   └── web_server                            # we will rebuild server for making flexible
│   │   │       ├── controller
│   │   │       │   ├── blueprint
│   │   │       │   │   ├── blueprint.py
│   │   │       │   │   ├── loader.py
│   │   │       │   │   ├── model.py
│   │   │       │   │   └── registry.py
│   │   │       │   └── route
│   │   │       │       └── routes.py
│   │   │       ├── model.py
│   │   │       └── server.py
│   │   ├── infrastructure
│   │   │   ├── database
│   │   │   │   ├── jsonDB                            # JsonDB (database model json) not recomended (good for development)
│   │   │   │   │   ├── components
│   │   │   │   │   │   ├── crud.py
│   │   │   │   │   │   └── __init__.py
│   │   │   │   │   ├── jsondb.py
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── sqlalchemy                        # currently incomplete
│   │   │   │   │   └── main.py
│   │   │   │   ├── sqlite                            # currently incomplete
│   │   │   │   │   └── main.py
│   │   │   │   └── __init__.py
│   │   │   └── services                              # used for third party api
│   │   │       └── .message
│   │   ├── kernel                                    # it mean `don't change this` cause will gave critical error.
│   │   │   └── foundation
│   │   │       ├── libs
│   │   │       │   ├── component
│   │   │       │   │   └── deferred.py
│   │   │       │   ├── package.py
│   │   │       │   └── package_lib
│   │   │       │       └── test
│   │   │       │           └── main.py
│   │   │       ├── manifest
│   │   │       │   ├── parser.py
│   │   │       │   ├── plugins.py
│   │   │       │   └── reader.py
│   │   │       ├── requester
│   │   │       │   ├── client.py
│   │   │       │   ├── http.py
│   │   │       │   └── parallel.py
│   │   │       └── __init__.py
│   │   ├── main.py
│   │   ├── plugins                                  # here is all of plugins storage
│   │   │   └── web
│   │   │       └── test
│   │   │           ├── main.py
│   │   │           └── manifest.json
│   │   ├── share                                    # shared tools
│   │   │   └── builtns
│   │   │       ├── exceptions
│   │   │       │   ├── child
│   │   │       │   │   └── InApp.py
│   │   │       │   ├── error_logger.py
│   │   │       │   ├── parent.py
│   │   │       │   └── __init__.py
│   │   │       ├── handler
│   │   │       │   ├── decorator.py
│   │   │       │   ├── flask_.py
│   │   │       │   └── __init__.py
│   │   │       ├── hook
│   │   │       │   └── events.py
│   │   │       └── logger
│   │   │           ├── components
│   │   │           │   ├── extraFormatter.py
│   │   │           │   ├── local_config.py
│   │   │           │   └── __init__.py
│   │   │           ├── global_logger.py
│   │   │           ├── print.py
│   │   │           ├── server_logger.py
│   │   │           └── user.py
│   │   ├── support                                  # support handler
│   │   │   ├── file
│   │   │   │   ├── FileHandling.py
│   │   │   │   ├── file_manager.py
│   │   │   │   └── __init__.py
│   │   │   ├── generator
│   │   │   │   └── uuid.py
│   │   │   ├── os
│   │   │   │   ├── system.py
│   │   │   │   ├── termutil.py
│   │   │   │   └── wrapSyntax
│   │   │   │       └── iostream.py
│   │   │   ├── parser
│   │   │   │   ├── url.py
│   │   │   │   └── url_utils.py
│   │   │   ├── style
│   │   │   │   └── color.py
│   │   │   ├── time
│   │   │   │   ├── date.py
│   │   │   │   └── delaymanager.py
│   │   │   ├── utility.py
│   │   │   ├── validator
│   │   │   └── __init__.py
│   │   ├── test
│   │   │   └── test_plugins.py
│   │   └── __init__.py
│   ├── lib                                        # the external lib from others language here (c, c++, rust and cython)
│   ├── sources                                    # sources of others language lib
│   │   ├── c
│   │   ├── cpp
│   │   ├── cython
│   │   └── rust
│   ├── tools
└── STRUCTURE.md
```
