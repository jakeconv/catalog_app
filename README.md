# Catalog Application

## About
This program hosts a web application that displays a catalog when accessed through a front end.  The home screen displays all of the categories of items as well as the 10 most recently added items.  Clicking on a category displays its items, and clicking on an individual item within a category will display its description.  Upon logging in with Facebook, users have the option to add, delete, and edit individual items, and create new categories.

## Prerequisites

This program runs in Python 3.  Python may be downloaded from:

https://www.python.org/downloads/

To install, run the downloaded executable. 

For this project, the program executes within a virtual machine running on VirtualBox.  VirtualBox may be downlaoded from:

https://www.virtualbox.org/wiki/Downloads

To install, downlaod the appropriate package for your platform and run the executable.

This program was tested from within a Vagrant virtual machine environment.  A Vagrant installation package may be downloaded from:

https://www.vagrantup.com/downloads.html

Finally, this program makes use of the sqlalchemy, flask, oauth2client, and httplib2 libraries.  To install, run the following commands (in no particular order):

		sudo pip install sqlalchemy
		sudo pip install flask
		sudo pip install oauth2client
		sudo pip install httplib2

When downloading the project files, place them within a Vagrant shared directory, such as the vagrant folder.

## Installing
To get started, navigate to your vagrant directory.  Run the following command:

		vagrant up

Then, connect to the vagrant VM:
		
		vagrant ssh

Navigate to the directory where the project files were downloaded to.  Before the project can run, locate the fb_client_secrets.json file.  This file will need to be updated with your App ID and App Secret from Facebook.  Likewise, the App ID will need to be inserted into line 25 of templates/index.html.

Before the application can run for the first time, run the following command to initialize the SQLite database:
		
		python models.py

Now, the application is ready to run with a blank database.

## Running
To run the catalog application, use the following command:

		python views.py

The application will not be running at localhost on port 8000.  The catalog will be accessible from your web browser of choice using the following links:

		http://localhost:8000
		http://localhost:8000/catalog
