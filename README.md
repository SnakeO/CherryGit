CherryGit
=========

Github webhooks for shared servers, servers that don't allow exec() or shell_exec(), or when you're having permissions issues with git webhooks

CherryGit is a webhook for git that will SSH into another server and update git via SSH when it's triggered. Usually a PHP script is triggered by a git webhook. But, this package is useful if:

	- Your website is on a shared server and you don't have exec() or exec_shell() pirvileges with php
	- Your PHP user doesn't have permission to update the website's git repo
	
CherryGit has dependencies of:
	- Python 2.7
	- cherrypy (pip install cherrypy)
	- fabric (pip install fabric)
	
Also, you need your own virtual dedicated server, which will listen for the webhook and execute the git pull via ssh. You can grab a dedicated virtual server from https://www.digitalocean.com/ or from http://linode.com/ .. both are great.

So, in summation the auto-update process looks like this:
```flow
git_push=>start: git push
git_pull=>end: git pull
cherrygit=>operation: CherryGit
sharedserver=>operation: SSH to Shared Server

git_push->cherrygit->sharedserver->git_pull
```

Now, time to configure and setup CherryGit.

1. Upload cherrygit directory into your virtual dedicated server. It can live anywhere, just note the path.

2. CherryGit webserver is set to listen on port 2321 on all interfaces. You can test the CherryGit webserver by opening your terminal, navigate to your cherrygit/_webserver directory and typing in 'python cherrygit.py'. You should see output like this:

```
# python cherrygit.py 
ENGINE Listening for SIGHUP.
ENGINE Listening for SIGTERM.
ENGINE Listening for SIGUSR1.
ENGINE Bus STARTING
ENGINE Started monitor thread 'Autoreloader'.
ENGINE Started monitor thread '_TimeoutMonitor'.
ENGINE Serving on http://0.0.0.0:2321
ENGINE Bus STARTED
```

Good, that means it's working. Go ahead and shut it down by pressing ctrl-c. If you want, open up cherrygit.py and modify the LISTEN_HOST or LISTEN_PORT to something else.

3. Now we need to tell CherryGit which git repo to update. first, duplicate the 'testproject' directory and give it the same name as your git repo. Inside that directory, find the fabfiles/githook.py file and open it. You'll see the config like so:
```
git_server = {

	'paths'	: {'web':'/path/to/yourwebsite/public_html/your_git_repo/'}, # paths should have trailing slash
	'ssh'	: {
		'login' : 'sshuser@serverdomain.com',
		'pass'	: 'sshpass'
	}
}
```

put in the full path to the git repo there, along with the ssh user and password.

4. Now we setup the CherryGit daemon, so that the webserver will run always run. Open _webserver/daemon/cherrygit.conf and update this line to point to the path where you uploaded cherrygit to (no trailing slash): env CHERRYGIT=/path/to/cherrygit

5. Now, run 'start cherrygit'. If you succeeded you'll see something like 'cherrygit start/running, process 24566' and if you visit http://your-virtual-dedicated-server:2321/githook?project=YOUR_PROJECT_NAME you will see some output. That output details the git update status for the project that you just created. This is the URL you'll use as your git webhook.

To add more git hooks, simply repeat step 3 above.

If you can't access that url, make sure the port is open in your firewall. Also, check the cherrygit/logs/ directory for more juicy debugging info.