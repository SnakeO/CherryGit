from fabric.api import *
from fabric.contrib.files import *
from fabric.contrib.console import confirm

import datetime
import sys

import os.path

try:
    import json
except ImportError:
    import simplejson as json

git_server = {

	'paths'	: {'web':'/path/to/yourwebsite/public_html/your_git_repo/'}, # paths should have trailing slash
	'ssh'	: {
		'login' : 'sshuser@serverdomain.com',
		'pass'	: 'sshpass'
	}
}

# set the ENV password
ssh_login = git_server['ssh']['login']
ssh_pass = git_server['ssh']['pass']

env.hosts = [ssh_login]
env.passwords = {ssh_login: ssh_pass}
env.password = ssh_pass

env.roledefs['git_server'] = [git_server['ssh']['login']]

@task
def update():

	execute(gitPull, git_server)
	print("Done!");

@task
def gitPull(server):
	explain("GIT PULL on " + printableEnv(env) + ": " + server['paths']['web'])

	with cd(server['paths']['web']):
		run('pwd')
		run_careful('git pull')

def explain(msg):
	print
	print("************************************************************")
	print(msg)
	print("************************************************************")
	print

def printableEnv(env):
	return "/".join(env.roles).upper()

def run_careful(cmd):
#	if not confirm(cmd):
#		abort('run_careful: Aborting.')

	run(cmd)

