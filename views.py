from flask import request, g
from flask import Flask, jsonify, render_template, request
from flask import redirect, url_for, flash
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, CatalogItem
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine


@app.route('/catalog.json')
def showCatalogJSON():
    # This is the API endpoint.  This will return the catalog in JSON format.
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    data = {}
    # data['Categories'] = []
    output = "{\"Categories\": {"
    # Pull all of the items and categories from the database
    categories = session.query(Category).all()
    # Iterate through the categories, and pull the items for each.
    for c in categories:
        items = session.query(CatalogItem).filter_by(category_id=c.id).all()
        data[c.name] = str(json.dumps({"Items": [i.serialize for i in items]}))
        # Convert the data into a JSON output string
        output += "\"" + c.name + "\":" + data[c.name] + ","
    # Remove the ending comma, then close all of the brackets
    output = output[:-2]
    output += "} } }"
    # Build the JSON response
    apiResponse = make_response(output)
    apiResponse.headers['Content-Type'] = 'application/json'
    return apiResponse


@app.route('/')
@app.route('/catalog')
def showCatalog():
    # This will show the main catalog screen
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # First, pull the ten most recent catalog items.
    # Do a join on the categoy to associate the category name
    # with the ID in the catalog_item table.
    items = session.query(CatalogItem).join(CatalogItem.category).order_by(
        desc(CatalogItem.date_created)).limit(10).all()
    # Pull the category for the list
    categories = session.query(Category).all()
    if 'username' in login_session:
        return render_template('catalog.html', categories=categories,
                               items=items,
                               username=login_session['username'])
    else:
        return render_template('catalog.html', categories=categories,
                               items=items)


@app.route('/login')
def login():
    # Generate the state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', state=state)


@app.route('/logout')
def logout():
    facebook_id = login_session['facebook_id']
    #  The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['facebook_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['id']
    del login_session['provider']
    flash('Logged out successfully.')
    return redirect(url_for('showCatalog'))


@app.route('/login/fb', methods=['POST'])
def handleLogin():
    # Check and see if a state token is provided
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    # Load our Facebook app ID and app secret
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type='
           'fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s' % (app_id, app_secret, access_token))
    # Get a token from Facebook
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    # Use the token to get the user details from Facebook
    token = data['access_token']
    url = ('https://graph.facebook.com/v4.0/me?access_token=%s'
           '&fields=name,id,email' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    # Store the data in the Flask session
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    # Store the access token for processing a logout later on
    login_session['access_token'] = token
    flash('Welcome, %s!' % login_session['username'])
    # Get user picture
    # User picture is not currently used...
    # implement it in a later version of the app
    url = ('https://graph.facebook.com/v4.0/me/picture?'
           'access_token=%s&redirect=0&height=200&width=200' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']
    # Make sure the user is recorded in our users database
    user = processUser(login_session)
    # Add our user ID to the login session
    login_session['id'] = user.id
    output = '<h1>Welcome!</h1>'
    return output


@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    # Verify that a user is logged in.
    # If not, redirect them to the login page.
    if 'username' not in login_session:
        flash('You must login to add items.')
        return redirect(url_for('login'))
    # User is logged in. Process data.
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        # The completed form.  Add the data into the items table
        newItem = CatalogItem(name=request.form['name'],
                              description=request.form['description'],
                              category_id=request.form['cat_id'],
                              user_id=login_session['id'])
        # Before comitting, make sure the item doesn't already exist
        try:
            if (session.query(CatalogItem).filter_by(name=newItem.name).one()):
                flash('Error: An item by the name %s already exists!'
                      % newItem.name)
                return redirect(url_for('showCatalog'))
        except:
            # Item does not exist.  Add it.
            session.add(newItem)
            session.commit()
            flash('%s successfully added.' % newItem.name)
            return redirect(url_for('showCatalog'))
    else:
        # Get request.  Pull the current category list.
        # Then, return the add item form.
        categories = session.query(Category).all()
        return render_template('new_item.html', categories=categories,
                               username=login_session['username'])


@app.route('/catalog/category/add', methods=['GET', 'POST'])
def addCategory():
    # Verify that a user is currently logged in.
    # If no user is logged in, redirect them to the login page.
    if 'username' not in login_session:
        flash('You must login to add categories.')
        return redirect(url_for('login'))
    # User is logged in. Process data.
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        # The completed form.  Add the data into the categories table
        newCat = Category(name=request.form['name'],
                          user_id=login_session['id'])
        # Before committing, make sure the cartegory doesn't exist
        try:
            if (session.query(Category).filter_by(name=newCat.name).one()):
                flash('Error: %s category already exists!' % newCat.name)
                return redirect(url_for('showCatalog'))
        except:
            # Category does not exist.  Add it.
            session.add(newCat)
            session.commit()
            flash('%s category successfully added.' % newCat.name)
            return redirect(url_for('showCatalog'))
    else:
        # Get request.  Pull the current category list.
        # Then, return the add item form.
        categories = session.query(Category).all()
        return render_template('new_category.html',
                               username=login_session['username'])
    return render_template('new_category.html')


@app.route('/catalog/<string:catName>/items')
def showCategoryItems(catName):
    # This will display all of the items available in a particular category
    # First, pull the items in the category
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # Identify the category
    category = session.query(Category).filter_by(name=catName).one()
    # Get the items for this category
    items = session.query(CatalogItem).filter_by(category_id=category.id).all()
    # Get all of the categories for the sidebar
    categories = session.query(Category).all()
    if 'username' in login_session:
        # Render the template as a logged in user
        return render_template('category.html', category=category, items=items,
                               categories=categories, count=len(items),
                               username=login_session['username'])
    else:
        # Render the template for the general public
        return render_template('category.html', category=category, items=items,
                               categories=categories, count=len(items))


@app.route('/catalog/<string:catName>/<string:itemName>')
def showItem(catName, itemName):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # Pull the category to get the ID
    category = session.query(Category).filter_by(name=catName).one()
    # Next, pull the actual item
    item = session.query(CatalogItem).filter_by(name=itemName).filter_by(
        category_id=category.id).one()
    # Check and see if there is a user logged in.
    # If so, display the edit and delete buttons.
    if 'username' in login_session:
        return render_template('item.html', item=item,
                               username=login_session['username'])
    else:
        # No user logged in
        return render_template('item.html', item=item)


@app.route('/catalog/<string:itemName>/edit', methods=['GET', 'POST'])
def editItem(itemName):
    # First, see if the user is logged in.
    # If no user is logged in, redirect them to the login page
    if 'username' not in login_session:
        flash('You must login to edit items.')
        return redirect(url_for('login'))
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # Grab the item
    item = session.query(CatalogItem).filter_by(name=itemName).one()
    # If this is a post request, update the item and send it to the database
    if request.method == 'POST':
        # The completed form process.
        # Before comitting, make sure the item doesn't already exist.
        # If the name is the same, it's OK to commit
        if (request.form['name'] == itemName):
            print("Name's the same!")
            item.name = request.form['name']
            item.description = request.form['description']
            item.category_id = request.form['cat_id']
            session.add(item)
            session.commit()
            flash('%s successfully edited.' % item.name)
            return redirect(url_for('showCatalog'))
        # The name has changed.  Run the check.
        testItems = session.query(CatalogItem).filter_by(
            name=request.form['name']).all()
        if (testItems):
            # Items were returned, so this name already exists in our database.
            flash('Error: An item by the name %s already exists!' %
                  request.form['name'])
            return redirect(url_for('showCatalog'))
        else:
            # Items were not returned.  This name does not exist.
            # Adjust the item and commit it to the database.
            item.name = request.form['name']
            item.description = request.form['description']
            item.category_id = request.form['cat_id']
            session.add(item)
            session.commit()
            flash('%s successfully edited.' % item.name)
            return redirect(url_for('showCatalog'))
    else:
        # Get request.  Grab the available categories for the drop down menu
        categories = session.query(Category).all()
        return render_template('edit_item.html', item=item,
                               categories=categories,
                               username=login_session['username'])


@app.route('/catalog/<string:itemName>/delete', methods=['GET', 'POST'])
def deleteItem(itemName):
    # First, see if the user is logged in.
    # If no user is logged in, redirect them to the login page
    if 'username' not in login_session:
        flash('You must login to delete items.')
        return redirect(url_for('login'))
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # Grab the item to be delete
    item = session.query(CatalogItem).filter_by(name=itemName).one()
    if request.method == 'POST':
        # Post request.  Delete the item.
        session.delete(item)
        session.commit()
        flash('%s successfully deleted.' % item.name)
        return redirect(url_for('showCatalog'))
    else:
        # Get request.  Show the delete item page
        return render_template('delete_item.html', item=item,
                               username=login_session['username'])


# Support Methods
def processUser(login_session):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # First, try getting the user info
    try:
        user = session.query(User).filter_by(
            email=login_session['email']).one()
        return user
    # If no user is found with that info, then create a new one
    except:
        newUser = User(name=login_session['username'],
                       email=login_session['email'],
                       picture=login_session['picture'])
        session.add(newUser)
        session.commit()
        return newUser


def itemsJSON(category):
    # Return JSON data for the items in a category
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    items = session.query(CatalogItem).filter_by(category_id=category.id).all()
    return jsonify(Items=[i.serialize for i in items])

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
