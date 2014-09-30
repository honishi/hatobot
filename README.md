hatobot
==
hatoroda bot.

![sample](./sample/tweet.png)

setup
--
### package
````
# debian
sudo apt-get install mysql-server

# os x
brew install mysql
````

### python runtime
````
pyenv install 3.4.1
pyenv virtualenv 3.4.1 hatobot-3.4.1
pyenv rehash
pip install -r requirements.txt
````
* requires `pyenv` and `pyenv-virtualenv`.
    * https://github.com/yyuu/pyenv
    * https://github.com/yyuu/pyenv-virtualenv

### database scheme
````
cd database
cp database.env.sample database.env
vi database.env
./create.sh
````

### application
````
cp main.configuration.sample main.configuration
vi main.configuration
````

start & stop
--
````
./hatobot.sh start
./hatobot.sh stop
````

monitoring example using cron
--
see `hatobot.sh` inside for details of monitoring.
````
* * * * * /path/to/hatobot/hatobot.sh monitor >> /path/to/hatobot/log/monitor.log 2>&1
````

test
--
````
py.test
pep8 *.py hato/*.py tests/*.py
````

snippet
--
### launch brewed mysql on os x
````
To have launchd start mysql at login:
    ln -sfv /usr/local/opt/mysql/*.plist ~/Library/LaunchAgents
Then to load mysql now:
    launchctl load ~/Library/LaunchAgents/homebrew.mxcl.mysql.plist
Or, if you don't want/need launchctl, you can just run:
    mysql.server start
````

### pyenv issue on os x
try following command when you get python build error when `pip install`.
````
CFLAGS="-I$(xcrun --show-sdk-path)/usr/include" pyenv install 3.4.1
````
* reference
    * https://github.com/yyuu/pyenv/wiki/Common-build-problems#build-failed
    * http://uragami.hatenablog.jp/entry/2014/01/19/010302

license
--
copyright &copy; 2014- honishi, hiroyuki onishi.

distributed under the [MIT license][mit].
[mit]: http://www.opensource.org/licenses/mit-license.php
