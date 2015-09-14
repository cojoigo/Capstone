# Nosferatu

Nosferatu is a home automation webapp written in python and coffeescript using Flask, and angular

----

## Quick Start

Append the following to your `.bashrc`, then run `source ~/.bashrc`

    export WORKON_HOME=~/.virtualenvs
    VIRTUALENVWRAPPER_PYTHON='/usr/bin/python3'
    PROJECT_HOME='/home/capstone/Capstone'
    source /usr/local/bin/virtualenvwrapper.sh

To set up all of the prerequisites for running **Nosferatu**, run the following command:

    sudo adduser capstone -q
    sudo adduser capstone sudo -q
    su - capstone
    wget https://raw.githubusercontent.com/cojoigo/Capstone/master/nosferatu/bin/initial_configuration; chmod u+x initial_configuration; ./initial_configuration; rm initial_configuration -f

\***Note**\* This command will prompt you a number of times throughout the process, and will have the side effect of creating a new **capstone** `sudo` user

----
At this point, you should be able to start the webapp by running

    sudo supervisorctl restart nosferatu:redis_server
    sudo supervisorctl restart nosferatu:redis_worker
    sudo supervisorctl restart nosferatu:gunicorn


## Development
In order to develop on **Nosferatu**:

 - Log on to the `capstone` user
 - Run `workon nosferatu`
 - Run `cd ~/Capstone/nosferatu`
 - And start working!