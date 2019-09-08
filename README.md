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

This project makes use of Facebook's login service to handle user authentication.  More information for this service may be found at:
https://developers.facebook.com/docs/facebook-login/

To register for a Facebook developer account, please visit:
https://developers.facebook.com
Once you are registered, you will need to hit the 'My Apps' dropdown, and create a new app.  Then, select the new application from that dropdown to access the application dashboard.  Under 'products', hit the plus to add Facebook Login.  Underneath the settings dropdown, hit the 'Basic' option, and note down the App ID and App Secret provided.  This information will be required later on.


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

## API Endpoints
This application contains 3 API endpoints.  These endpoints provide JSON-formatted data for the entire catalog, a category and all of its items, or a singular item in the catalog.

### Entire Catalog
The entire catalog may be accessed at:

		http://localhost:8000/catalog.json

This endpoint will return a JSON for the entire catalog, and it will be formatted with an object for each category.  Within each category container, there will be an Items array containing the items for each category.  Each item will contain the name, description, and database ID for each item.
A sample output:

```json
{
  "Fruits": {
    "Items": [
      {
        "description": "Sweet, and great for making pie", 
        "id": 1, 
        "name": "Apples"
      }, 
      {
        "description": "Perfect for making your favorite desserts", 
        "id": 2, 
        "name": "Blueberries"
      }
    ]
  }, 
  "Vegetables": {
    "Items": [
      {
        "description": "The perfect snack", 
        "id": 3, 
        "name": "Carrots"
      }, 
      {
        "description": "High in fiber and goes great in stir fry", 
        "id": 4, 
        "name": "Broccoli"
      }
    ]
  }
}	
```

### A category and its items
A singular category and its items may be accessed at:

		http://localhost:8000/catalog/categories/category-name-here.json

where category-name-here is the category to be formatted as a JSON.  This will return a list of items, where the name, description, and database ID are provided.  The category name is case sensitive.
For my sample database, accessing http://localhost:8000/catalog/categories/Fruits.json provides the following output:

```json
{
  "Items": [
    {
      "description": "Sweet, and great for making pie", 
      "id": 1, 
      "name": "Apples"
    }, 
    {
      "description": "Perfect for making your favorite desserts", 
      "id": 2, 
      "name": "Blueberries"
    }
  ]
}
```

### A singular item
A single item may be accessed at:

		http://localhost:8000/catalog/items/item-name-here.json

where item-name-here is the item to be formatted as a JSON.  This will return the name, description, and database ID for the item.  The item name is case sensitive.
For my sample database, accessing http://localhost:8000/catalog/items/Broccoli.json provides the following output:

```json
{
  "Item": {
    "description": "High in fiber and goes great in stir fry", 
    "id": 4, 
    "name": "Broccoli"
  }
}
```
