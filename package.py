# -*- coding: utf-8 -*-
############
# Package for a steamroller tool to let us set up the environment that it needs.
# Allows for setting of environment variables, running python commands, executing scripts, etc. for 
# whenever Rez loads the tool package
############
name = 'steamroller.tools.checker'    ## Replace with the name of the tool  ------Needs edit
version = '1.0.04'
description = 'Set of conditions that a task must meet to be published.'
authors = [ 'juan.bovio' ]
requires = [                ## Required packages for tool. The necessary packages and versions will vary based on the tool  ------Likely needs edit
    'maya-2022',
    'steamroller.core',
    # 'steamroller.web',
    # 'Qt.py',
    #'steamroller.qt',
    #'otherLibraries'
]
variants = [
	['platform-windows', 'arch-AMD64', 'os-windows-10.0.19041', 'python-3.7'],
	['platform-windows', 'arch-AMD64', 'os-windows-10.0.22000', 'python-3.7']
]
def commands():                      ## Commands executed when rezzing into this package. Used to setup the environment correctly
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.append("{root}/python")
uuid = 'steamroller.tools.checker'         ## Replace with the name of the client     ------Needs edit
format_version = 2          ## Important Rez versioning info, leave it there