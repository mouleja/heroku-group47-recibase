#! usr/bin/python3
#########################################################################
# CS340-400-U19 Project Group 47 - Jason Moule - Tommy Armstrong
# 
# Recipe Sharing Database Web Backend Server
#   Python Flask App with various routes for CRUD implementation
#   using mariaDB database running on remote server
#
# Code adapted from course tutorial at: 
# https://github.com/knightsamar/CS340_starter_flask_app/ and
# https://www.roytuts.com/python-web-application-crud-example-using-flask-and-mysql/
# https://pynative.com/python-mysql-tutorial/
#########################################################################

import pymysql, datetime
from app import app
from db_connection import mysql
from flask import flash, render_template, request, redirect
from werkzeug import generate_password_hash, check_password_hash

##########  Helpers ####################
def get_recipe_details(cursor, recipeId):
    cursor.execute(
        '''SELECT r.recipeId, r.name rname, r.date, u.name uname, s.name sname FROM Recipe r
        INNER JOIN User u ON u.userId = r.userId
        LEFT JOIN Source s ON s.sourceId = r.sourceId
        WHERE r.recipeId = %s''', (recipeId,)
    )
    recipe = cursor.fetchone()
    return recipe

def get_recipe_ingredients(cursor, recipeId):
    cursor.execute(
        '''SELECT i.ingredientId, i.name, ri.amount, ri.unit, ri.preperation
        FROM Recipe_Ingredient ri
        INNER JOIN Ingredient i ON i.ingredientId = ri.ingredientId
        WHERE ri.recipeId = %s ORDER BY i.name ASC''', (recipeId,)
    )
    ingredients = cursor.fetchall()
    return ingredients

def get_recipe_steps(cursor, recipeId):
    cursor.execute('SELECT step, instruction FROM Step WHERE recipeId = %s', (recipeId,))
    steps = cursor.fetchall()
    return steps

def get_source_list(cursor):
    cursor.execute('SELECT sourceId, name FROM Source ORDER BY name ASC')
    sourceList = cursor.fetchall()
    return sourceList

def get_users_recipes(cursor, userId):
    cursor.execute('SELECT * FROM Recipe WHERE userId = %s', (userId,))
    recipes = cursor.fetchall()
    return recipes

def get_ingredient_list(cursor):
    cursor.execute('SELECT ingredientId, name FROM Ingredient ORDER BY name')
    ingredientList = cursor.fetchall()
    return ingredientList

def get_basic_recipe(cursor, recipeId):
    cursor.execute('SELECT * FROM Recipe WHERE recipeId = %s', (recipeId,))
    recipe = cursor.fetchone()
    return recipe

def get_userlist(cursor):
    cursor.execute(
        'SELECT u.*, COUNT(recipeId) num, MAX(r.date) last'
        ' FROM Recipe r RIGHT JOIN User u ON u.userId = r.userId'
        ' GROUP BY u.name ORDER BY u.name')
    userList = cursor.fetchall()
    return userList

def get_admin_sources(cursor):
    cursor.execute(
        'SELECT s.sourceId, s.name, s.url, COUNT(r.recipeId) num FROM Recipe r '
        'RIGHT JOIN Source s on s.sourceId = r.sourceId '
        'GROUP BY s.name ORDER BY s.name')
    s_list = cursor.fetchall()
    return s_list

def get_admin_ingr(cursor):
    cursor.execute(
        'SELECT i.*, COUNT(ri.ingredientId) num FROM Recipe_Ingredient ri '
        'RIGHT JOIN Ingredient i on i.ingredientId = ri.ingredientId '
        'GROUP BY i.ingredientId ORDER BY i.name')
    ingrList = cursor.fetchall()
    return ingrList

##########  Routes #########################
@app.route('/get_recipes')
def get_recipes():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''SELECT r.recipeId, r.name recipeName, r.date, u.name username, s.name sourceName 
            FROM Recipe r 
            INNER JOIN User u on u.userId = r.userId
            LEFT JOIN Source s on s.sourceId = r.sourceId ORDER BY recipeName ASC'''
        )
        result = cursor.fetchall()
        print("Getting all recipes.")
        return render_template('recipeList.html', recipes=result)
    except Exception as e:
        print("Error getting recipes", e)
    finally:
        cursor.close() 
        conn.close()

    #return redirect('/')
    return 'Something went wrong in get_recipes!'

@app.route('/show_recipe/<int:id>')
def show_recipe(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        recipeInfo = get_recipe_details(cursor, id)

        ingredients = get_recipe_ingredients(cursor, id)

        steps = get_recipe_steps(cursor, id)

        print("Getting recipe details:", recipeInfo, ingredients, steps)
        return render_template('recipeDetails.html', recipeInfo=recipeInfo,
                               ingredients=ingredients, steps=steps)
    except Exception as e:
        print("Error getting recipe",id, e)
    finally:
        cursor.close() 
        conn.close()

    #return redirect('/')
    return 'Something went wrong in show_recipe!'
        
@app.route('/delete_recipe', methods=['POST'])
def delete_recipe():
    username = request.form.get("username")
    recipeId = request.form.get("recipeId")
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT recipeId, name FROM Recipe WHERE recipeId = %s', (recipeId,))
        recipe = cursor.fetchone()

        print("Delete recipe?", recipe)
        return render_template(
            'confirm_delete.html', recipe=recipe, username = username, deleteType='recipe')
    except Exception as e:
        print("Error deleting recipe", recipeId, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in delete_recipe!'

@app.route('/delete', methods=['POST'])
def delete():
    password = request.form.get('password')
    deleteType = request.form.get('deleteType')
    recipe = {'name': request.form.get("recipeName"), 'recipeId': request.form.get('recipeId')}
    username = request.form.get('username')
    toDelete = request.form.get("toDelete")
    print("Deleting:", deleteType, recipe, username)
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM User WHERE name = %s and password = %s', (username, password))
        checkpw = cursor.fetchone() # True if password wrong
        if not checkpw:
            return render_template(
                'confirm_delete.html',
                username=toDelete or username, recipe=recipe, 
                admin=username if toDelete else None, deleteType=deleteType, pwError = True)

        if deleteType == 'recipe':
            print("Delete processed for recipe id #", recipe['recipeId'])
            cursor.execute('DELETE FROM Recipe WHERE recipeId = %s', (recipe['recipeId'],))
            conn.commit()
            cursor.execute('SELECT * FROM User WHERE name = %s', (username,))
            user = cursor.fetchone()
            recipes = get_users_recipes(cursor, user['userId'])
            return render_template('user_page.html', user=user, recipes=recipes)

        if deleteType == 'user':
            cursor.execute('DELETE FROM User WHERE name = %s', (username,))
            conn.commit()
            print("Deleted user", username, "from the database.")
            return redirect('/get_recipes')

        if deleteType == 'admin_user':
            if (toDelete == 'Jason' or toDelete == 'Tommy'):
                return "How dare you!"
            cursor.execute(
                'DELETE FROM User WHERE name = %s', 
                (toDelete,))
            conn.commit()
            print("Deleted user", request.form.get("toDelete"), "from the database.")
            userList = get_userlist(cursor)
            return render_template('admin_users.html', userList = userList, admin = username)

    except Exception as e:
        print("Error deleting", username, recipe, toDelete, deleteType, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in delete!'

@app.route('/user_entry')
def user_entry():
    print("Going to user entry page.")
    return render_template('user_entry.html')

@app.route('/new_user')
def new_user():
    print("Going to new user page.")
    return render_template('new_user.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    print('Adding new user', username)

    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT userId FROM User WHERE name = %s', (username,))
        nameUsed = cursor.fetchone()
        if nameUsed:
            return render_template('new_user.html', error=True)

        cursor.execute(
            '''INSERT INTO `User` (`name`, `password`) VALUES (%s, %s)''', 
            (username, password)
        )
        conn.commit()
        print("User added")

        cursor.execute('SELECT userId, name from User WHERE name = %s', (username,))
        user = cursor.fetchone()

        return render_template('user_page.html', user=user, recipes={})
    
    except Exception as e:
        print("Error adding user", username, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in add_user!'

@app.route('/user_page', methods=['POST'])
def user_page():
    username = request.form['username']
    password = request.form['password']
    print('Request for user page from', username)

    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            'SELECT userId, name FROM User WHERE name = %s and password = %s', 
            (username, password))
        user = cursor.fetchone()

        if not user:
            return render_template('user_entry.html', error=True)

        recipes = get_users_recipes(cursor, user['userId'])

        print("Going to user page for", username)

        return render_template('user_page.html', user=user, recipes=recipes)
    
    except Exception as e:
        print("Error getting user", username, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in user_page!'

@app.route('/change_username', methods=['POST'])
def change_username():
    userId = request.form['userId']
    newName = request.form['newName']
    user = {'userId': userId, 'name': newName}
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE name = %s', (newName,))
        nameUsed = cursor.fetchone()
        nameFree = not nameUsed # python trick: nameFree = True if nameUsed is empty else False
        if nameFree:
            cursor.execute('UPDATE User SET name = %s WHERE userId = %s', (newName, userId))
            conn.commit()
            print("Successfully updated username for", userId, "to", newName)
        else:
            user['name'] = request.form['username']
            print("Failed update username for", userId, "to", newName)

        recipes = get_users_recipes(cursor, userId)
        return render_template('user_page.html', user=user, recipes=recipes, usedError=not nameFree)
    
    except Exception as e:
        print("Error changing username", userId, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in change_username!'

@app.route('/change_password', methods=['POST'])
def change_password():
    userId = request.form['userId']
    newPass = request.form['newPass']
    user = {'userId': userId, 'name': request.form['username'], 'password': newPass}
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('UPDATE User SET password = %s WHERE userId = %s', (newPass, userId))
        conn.commit()
        print("Successfully updated password for", userId)

        recipes = get_users_recipes(cursor, userId)
        return render_template('user_page.html', user=user, recipes=recipes)
    
    except Exception as e:
        print("Error changing password", userId, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in change_password!'

@app.route('/delete_user', methods=['POST'])
def delete_user():
    userId = request.form['userId']
    username = request.form['username']
    return render_template('confirm_delete.html', username=username, deleteType='user')

@app.route('/update_recipe', methods=['POST'])
def update_recipe():
    userId = request.form.get("userId")
    recipeId = request.form.get("recipeId")
    print("Updating recipe details:", recipeId )

    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        recipe = get_recipe_details(cursor, recipeId)
        ingredients = get_recipe_ingredients(cursor, recipeId)
        steps = get_recipe_steps(cursor, recipeId)

        sourceList = get_source_list(cursor)

        ingredientList = get_ingredient_list(cursor)

        return render_template('update_recipe.html', recipe=recipe, ingredients=ingredients, 
                steps=steps, sourceList=sourceList, ingredientList=ingredientList, changeError = '')

    except Exception as e:
        print("Error getting recipe",id, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in update_recipe!'

@app.route("/add_recipe_initial", methods=["POST"])
def add_recipe_initial():
    userId = request.form.get("userId")
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT sourceId, name FROM Source')
        sourceList = cursor.fetchall()

        return render_template('add_recipe_initial.html', userId=userId, sourceList=sourceList)
    
    except Exception as e:
        print("Error adding recipe -", e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in add_recipe_initial!'

@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    print(request.form)
    userId = request.form.get("userId")
    recipeName = request.form.get("recipeName")
    source = None
    sourceUrl = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        if request.form.getlist('source-check'):
            source = request.form['source']
            sourceUrl = request.form['source-url']
            if source == 'new_source':
                source = request.form['new-source-name']
                cursor.execute('SELECT name from Source WHERE name = %s', (source))
                if cursor.fetchone():
                    sourceList = get_source_list(cursor)
                    return render_template('add_recipe_initial.html',
                        userId=userId, sourceList=sourceList, dupSource=True)
                cursor.execute('INSERT INTO Source (name, url) VALUES (%s, %s)', (source, sourceUrl))
                conn.commit()
                cursor.execute('SELECT sourceId FROM Source WHERE name = %s', (source))
                source = cursor.fetchone()['sourceId']
                conn.commit()

        cursor.execute(
            'SELECT name FROM Recipe WHERE name = %s and userId = %s', (recipeName, userId))
        if cursor.fetchone():           # Check for duplicate
            sourceList = get_source_list(cursor)
            return render_template(
                '/add_recipe_initial.html', userId=userId, sourceList=sourceList, dupName=recipeName)

        cursor.execute('INSERT INTO Recipe (name, userId, sourceId) VALUES (%s, %s, %s)',
                               (recipeName, userId, source))
        conn.commit()   # New recipe created

        cursor.execute('SELECT * FROM Recipe WHERE name = %s and userId = %s', (recipeName, userId))
        recipe = cursor.fetchone()

        ingredientList = get_ingredient_list(cursor)

        return render_template('add_recipe_details.html', recipe=recipe, ingredients = [], 
                               steps = [], ingredientList = ingredientList)
    
    except Exception as e:
        print("Error adding recipe -", recipeName, e)
        print(request.form)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in add_recipe!'

@app.route('/add_recipe_ingredient', methods=['POST'])
def add_recipe_ingredient():
    recipeId = request.form.get("recipeId")
    ingredientName = request.form.get('newIngredientName')
    ingredientId = request.form.get('ingredient')
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        #if an ingredient not in the ingredient list is added, add the ingredient to the list and recipe
        if ingredientId == 'new_ingredient':
            print(
            "Adding new ingredient to", recipeId, ingredientName, request.form.get('amount'), 
            request.form.get('unit'), request.form.get('preperation'))

            cursor.execute(
            'SELECT name from Ingredient WHERE name = %s', (ingredientName,))

            #checking if the ingredient is already in the ingredient list
            if cursor.fetchone():
                recipe = get_basic_recipe(cursor, recipeId)
                ingredientList = get_ingredient_list(cursor)
                ingredients = get_recipe_ingredients(cursor, recipeId)
                steps = get_recipe_steps(cursor, recipeId)

                return render_template(
                    'add_recipe_details.html', recipe=recipe, ingredients = ingredients, 
                    steps = steps, ingredientList = ingredientList, dupError = True)
            #end duplicate ingredient check
            print(request.form)
            #insert the ingredient into the database table
            cursor.execute(
                '''INSERT INTO Ingredient (name, defaultAmount, defaultUnit, calories)
                VALUES (%s, %s, %s, %s)''',
                    (ingredientName, request.form.get("defaultAmount"), request.form.get("defaultUnit"), 
                     request.form.get("calories")))
            conn.commit()
            cursor.execute('SELECT ingredientId FROM Ingredient WHERE name=%s', (ingredientName))
            ingredientId = cursor.fetchone()['ingredientId']
            conn.commit()
        
        print("Adding ingredient to", recipeId, ingredientId, request.form.get('amount'), request.form.get('unit'), request.form.get('preperation'))

        #add the ingredient into the recipe
        cursor.execute(
            '''INSERT INTO Recipe_Ingredient (recipeId, ingredientId, amount, unit, preperation)
            VALUES (%s, %s, %s, %s, %s)''',
                (recipeId, ingredientId, request.form.get('amount'), 
                 request.form.get("unit"), request.form.get("preperation")))
        conn.commit()

        recipe = get_basic_recipe(cursor, recipeId)
        ingredientList = get_ingredient_list(cursor)
        ingredients = get_recipe_ingredients(cursor, recipeId)
        steps = get_recipe_steps(cursor, recipeId)

        return render_template('add_recipe_details.html', recipe=recipe, ingredients = ingredients, 
                               steps = steps, ingredientList = ingredientList)
    
    except Exception as e:
        print("Error adding recipe ingredient", recipeId, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in add_recipe_ingredient!'

@app.route('/add_recipe_new_ingredient', methods=['POST'])
def add_recipe_new_ingredient():
    recipeId = request.form.get("recipeId")
    ingredientName = request.form.get('ingredientName')
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        print(
            "Adding new ingredient to", recipeId, ingredientName, request.form.get('amount'), 
            request.form.get('unit'), request.form.get('preperation'))

        cursor.execute(
            'SELECT name from Ingredient WHERE name = %s', (ingredientName,))
        if cursor.fetchone():
            recipe = get_basic_recipe(cursor, recipeId)
            ingredientList = get_ingredient_list(cursor)
            ingredients = get_recipe_ingredients(cursor, recipeId)
            steps = get_recipe_steps(cursor, recipeId)

            return render_template(
                'add_recipe_details.html', recipe=recipe, ingredients = ingredients, 
                steps = steps, ingredientList = ingredientList, dupError = True)
        print(request.form)
        cursor.execute(
            '''INSERT INTO Ingredient (name, defaultAmount, defaultUnit, calories)
            VALUES (%s, %s, %s, %s)''',
                (ingredientName, request.form.get("defaultAmount"), request.form.get("defaultUnit"), 
                 request.form.get("calories")))
        conn.commit()

        cursor.execute('SELECT ingredientId FROM Ingredient WHERE name = %s', (ingredientName,))
        newId = cursor.fetchone()['ingredientId'] 

        cursor.execute(
            '''INSERT INTO Recipe_Ingredient (recipeId, ingredientId, amount, unit, preperation)
            VALUES (%s, %s, %s, %s, %s)''',
                (recipeId, newId, request.form.get('amount'), 
                 request.form.get("unit"), request.form.get("preperation")))
        conn.commit()

        recipe = get_basic_recipe(cursor, recipeId)
        ingredientList = get_ingredient_list(cursor)
        ingredients = get_recipe_ingredients(cursor, recipeId)
        steps = get_recipe_steps(cursor, recipeId)

        return render_template('add_recipe_details.html', recipe=recipe, ingredients = ingredients, 
                               steps = steps, ingredientList = ingredientList)
    
    except Exception as e:
        print("Error adding recipe ingredient", recipeId, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in add_recipe_ingredient!'

@app.route('/add_recipe_step', methods=['POST'])
def add_recipe_step():
    recipeId = request.form.get("recipeId")
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        print("Adding step to", recipeId, request.form.get('step'), request.form.get('instruction'))

        cursor.execute('INSERT INTO Step (recipeId, step, instruction) VALUES (%s, %s, %s)',
                (recipeId, request.form.get('step'), request.form.get('instruction')))
        conn.commit()

        recipe = get_basic_recipe(cursor, recipeId)
        ingredientList = get_ingredient_list(cursor)
        ingredients = get_recipe_ingredients(cursor, recipeId)
        steps = get_recipe_steps(cursor, recipeId)

        return render_template('add_recipe_details.html', recipe=recipe, ingredients = ingredients, 
                               steps = steps, ingredientList = ingredientList)
    
    except Exception as e:
        print("Error adding recipe step", recipeId, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in add_recipe_step!'

@app.route('/change_recipe', methods=['POST'])
def change_recipe():
    recipeId = request.form.get("recipeId")
    changeType = request.form.get("changeType")
    source = request.form.get('source')
    newName = request.form.get("recipeName")
    changeError = ''
    print("Changing:", changeType, recipeId)
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        if changeType == 'name':
            cursor.execute(
                'SELECT name FROM Recipe WHERE name = %s and userId ='
                ' (SELECT userId FROM Recipe WHERE recipeId = %s)', (newName, recipeId))
            if cursor.fetchone():      # Already has a recipe named that
                recipe = get_recipe_details(cursor, recipeId)
                ingredientList = get_ingredient_list(cursor)
                ingredients = get_recipe_ingredients(cursor, recipeId)
                steps = get_recipe_steps(cursor, recipeId)
                sourceList = get_source_list(cursor)

                return render_template('update_recipe.html', recipe=recipe, ingredients=ingredients, 
                        steps=steps, sourceList=sourceList, ingredientList=ingredientList, 
                        dupName = True)

            cursor.execute('UPDATE Recipe SET name = %s WHERE recipeId = %s',
                (newName, recipeId))

        if changeType == 'change_source':
            cursor.execute('UPDATE Recipe SET sourceId = %s WHERE recipeId = %s',
                (source, recipeId))

        if changeType == 'add_source':
            cursor.execute('SELECT sourceId from Source WHERE name=%s', (source,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO Source (name, url) VALUES (%s, %s)',
                    (source, request.form.get('url')))
                conn.commit()
                cursor.execute('SELECT sourceId from Source WHERE name=%s', (source,))
                newId = cursor.fetchone()['sourceId']
                cursor.execute('UPDATE Recipe SET sourceId = %s WHERE recipeId = %s',
                    (newId, recipeId))
            else:
                changeError = 'duplicateSource'

        if changeType == 'change_ingredient' and request.form.get("action") == 'Edit':
            cursor.execute('''UPDATE Recipe_Ingredient SET amount=%s, unit=%s, preperation=%s
                    WHERE recipeId = %s and ingredientId=%s''', 
                    (request.form.get('amount'), request.form.get('unit'), request.form.get('preperation'), 
                     recipeId, request.form.get("ingredientId")))

        if changeType == 'change_ingredient' and request.form.get("action") == 'Delete':
            cursor.execute('''DELETE FROM Recipe_Ingredient WHERE recipeId = %s AND ingredientId=%s''', 
                    (recipeId, request.form.get("ingredientId")))

        if changeType == 'add_ingredient':
            cursor.execute('SELECT recipeId from Recipe_Ingredient WHERE recipeId = %s AND ingredientId=%s', 
                    (recipeId, request.form.get("ingredientId")))
            if not cursor.fetchone():
                cursor.execute('''INSERT INTO Recipe_Ingredient (recipeId, ingredientId, amount, unit, preperation)
                        VALUES (%s, %s, %s, %s, %s)''', (recipeId, request.form.get("ingredientId"),
                        request.form.get("amount"), request.form.get("unit"), 
                        request.form.get("preperation")))
            else:
                changeError = 'duplicateIngredient'

        if changeType == 'add_new_ingredient':
            cursor.execute('SELECT ingredientId FROM Ingredient WHERE name=%s', 
                           (request.form.get('ingredientName'),))
            if not cursor.fetchone():
                cursor.execute('''INSERT INTO Ingredient (name, defaultAmount, defaultUnit, calories) 
                    VALUES (%s, %s, %s, %s)''', (request.form.get('ingredientName'), 
                    request.form.get('defaultAmount'), request.form.get('defaultUnit'), 
                    request.form.get('calories')))
                conn.commit()
                cursor.execute('SELECT ingredientId from Ingredient WHERE name=%s', 
                               (request.form.get('ingredientName'),))
                newId = cursor.fetchone()['ingredientId']
                cursor.execute('''INSERT INTO Recipe_Ingredient (recipeId, ingredientId, amount, 
                        unit, preperation) VALUES (%s, %s, %s, %s, %s)''', (recipeId, newId,
                        request.form.get("amount"), request.form.get("unit"), 
                        request.form.get("preperation")))
            else:
                changeError = 'duplicateIngrName'

        if changeType == 'edit_step':
            cursor.execute('UPDATE Step SET instruction = %s WHERE recipeId=%s and step=%s',
                (request.form.get('instruction'), recipeId, request.form.get('step')))

        if changeType == 'delete_step':
            cursor.execute('DELETE FROM Step WHERE recipeId = %s and step = %s',
                           (recipeId, request.form.get('step')))

        if changeType == 'add_step':
            cursor.execute('INSERT INTO Step (recipeId, step, instruction) VALUES (%s, %s, %s)',
                           (recipeId, request.form.get('step'), (request.form.get('instruction'))))

        conn.commit()

        recipe = get_recipe_details(cursor, recipeId)
        ingredientList = get_ingredient_list(cursor)
        ingredients = get_recipe_ingredients(cursor, recipeId)
        steps = get_recipe_steps(cursor, recipeId)
        sourceList = get_source_list(cursor)

        return render_template('update_recipe.html', recipe=recipe, ingredients=ingredients, 
                steps=steps, sourceList=sourceList, ingredientList=ingredientList, 
                changeError = changeError)

    except Exception as e:
        print("Error changing recipe", recipeId, changeType, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in add_recipe_step!'

@app.route('/search_for', methods=['GET'])
def search_results():
    search_type = request.args.get('search_type')
    search_text = request.args.get('search_text')
    if not search_type or not search_text:
        print("Search ERROR", search_type, search_text)
        return redirect('/get_recipes')
    print("Searching", search_type, "for", search_text)
    search_text = '%' + search_text + '%'   # make search term SQL-compatible for LIKE
    
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        query = '''SELECT r.recipeId, r.name recipeName, r.date, u.name username, s.name sourceName 
        FROM Recipe r INNER JOIN User u ON u.userId = r.userId
        LEFT JOIN Source s ON s.sourceId = r.sourceId '''
        
        if search_type == 'Recipes':
            query += "WHERE r.name like %s;"

        if search_type == 'Ingredients':
            query += '''WHERE r.recipeId in (SELECT recipeId FROM Recipe_Ingredient
            LEFT JOIN Ingredient ON Ingredient.ingredientId = Recipe_Ingredient.ingredientId 
            WHERE Ingredient.name LIKE %s);'''

        if search_type == 'Usernames':
            query += 'WHERE u.name LIKE %s;'

        if search_type == 'Sources':
            query += 'WHERE s.name LIKE %s;'

        cursor.execute(query, (search_text, ))        
        recipes = cursor.fetchall()
        search_text = search_text[1:-1]     # remove % from search term

        return render_template('search_results.html', recipes= recipes, 
                search_type = search_type, search_text = search_text)
    
    except Exception as e:
        print("Error searching", search_type, search_text, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in search_for!'

@app.route('/admin_page', methods=["POST"])
def admin_page():
    username = request.form.get("username")
    password = request.form.get("password")
    print("Entering admin page",username,password)
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            'SELECT name, password, admin FROM User WHERE name = %s',
            (username,))    
        admin = cursor.fetchone()
        print(admin)

        if not admin:
            return render_template('admin_entry.html', nameError = True)
        elif admin['password'] != password:
            return render_template('admin_entry.html', passError = True)
        elif admin['admin'] == 0:
            return render_template('admin_entry.html', adminError = True)

        return render_template('admin_page.html', admin = admin['name'])
    
    except Exception as e:
        print("Error on admin_page", username, e)
    finally:
        cursor.close() 
        conn.close()

@app.route('/admin_users', methods=["POST"])
def admin_users():
    admin = request.form.get("admin")
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        userList = get_userlist(cursor)
        return render_template('admin_users.html', admin = admin, userList = userList)
    
    except Exception as e:
        print("Error on admin_users", e)
    finally:
        cursor.close() 
        conn.close()

@app.route('/admin_sources', methods=["POST"])
def admin_sources():
    admin = request.form.get("admin")
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        s_list = get_admin_sources(cursor)
   
        return render_template('admin_sources.html', admin = admin, s_list = s_list)
    
    except Exception as e:
        print("Error on admin_sources", e)
    finally:
        cursor.close() 
        conn.close()

@app.route('/edit_source', methods=["POST"])
def edit_source():
    admin = request.form.get("admin")
    sourceId = request.form.get("sourceId")
    sourceName = request.form.get("sourceName")
    newName = request.form.get("newName")
    url = request.form.get("url")
    print("Edit source:", sourceId, sourceName, newName, url)
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        if request.form.get("action") == 'Delete':  # Delete button
            cursor.execute(                         # Check in recipes
                'SELECT sourceId FROM Recipe WHERE sourceId = %s', (sourceId,))
            if cursor.fetchone():   # Error - source is in some existing recipes
                s_list = get_admin_sources(cursor)
                return render_template(
                    'admin_sources.html', admin = admin, s_list = s_list, inRecipes = True)
            else:
                cursor.execute(
                    'DELETE FROM Source WHERE sourceId = %s', (sourceId,))
                conn.commit()
                s_list = get_admin_sources(cursor)
                return render_template(
                    'admin_sources.html', admin = admin, s_list = s_list)

        # Edit Button
        if newName != sourceName:   # check for duplicate name before changing
            cursor.execute('SELECT name FROM Source WHERE name = %s', (newName,))
            if cursor.fetchone():   # this is a duplicate
                s_list = get_admin_sources(cursor)
                return render_template(
                    'admin_sources.html', admin = admin, s_list = s_list, dupName = True)

        cursor.execute(
            'UPDATE Source SET name = %s, url = %s WHERE sourceId = %s',
            (newName, url, sourceId))
        conn.commit()
        s_list = get_admin_sources(cursor)
   
        return render_template('admin_sources.html', admin = admin, s_list = s_list)
    
    except Exception as e:
        print("Error on edit_source", e)
    finally:
        cursor.close() 
        conn.close()

@app.route('/admin_ingr', methods=["POST"])
def admin_ingr():
    admin = request.form.get("admin")
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        ingrList = get_admin_ingr(cursor)

        return render_template('admin_ingr.html', admin = admin, ingrList = ingrList)
    
    except Exception as e:
        print("Error on admin_ingr", e)
    finally:
        cursor.close() 
        conn.close()

@app.route('/edit_ingr', methods=["POST"])
def edit_ingr():
    admin = request.form.get("admin")
    ingredientId = request.form.get("ingredientId")
    ingrName = request.form.get("ingrName")
    newName = request.form.get("newName")
    print("Edit ingredient:", ingredientId, ingrName, newName)
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        if request.form.get("action") == 'Delete':  # Delete button
            cursor.execute(                         # Check in recipes
                'SELECT ingredientId FROM Recipe_Ingredient WHERE ingredientId = %s', 
                (ingredientId,))
            if cursor.fetchone():   # Error - ingredient is in some existing recipes
                ingrList = get_admin_ingr(cursor)
                return render_template(
                    'admin_ingr.html', admin = admin, ingrList = ingrList, inRecipes = True)
            else:
                cursor.execute(
                    'DELETE FROM Ingredient WHERE ingredientId = %s', (ingredientId,))
                conn.commit()
                ingrList = get_admin_ingr(cursor)
                return render_template('admin_ingr.html', admin = admin, ingrList = ingrList)

        # Edit Button
        if newName != ingrName:   # check for duplicate name before changing
            cursor.execute(
                'SELECT name FROM Ingredient WHERE name = %s', (newName,))
            if cursor.fetchone():   # this is a duplicate
                ingrList = get_admin_ingr(cursor)
                return render_template(
                    'admin_ingr.html', admin = admin, ingrList = ingrList, dupName = True)

        cursor.execute(
            'UPDATE Ingredient SET name = %s, defaultAmount = %s, defaultUnit = %s,'
            ' calories = %s WHERE ingredientId = %s',
            (newName, request.form.get("amount"), request.form.get("unit"), 
             request.form.get("calories"), ingredientId))
        conn.commit()
        ingrList = get_admin_ingr(cursor)

        return render_template('admin_ingr.html', admin = admin, ingrList = ingrList)
    
    except Exception as e:
        print("Error on edit_ingredient", e)
    finally:
        cursor.close() 
        conn.close()

@app.route('/toggle_admin', methods=["POST"])
def toggle_admin():
    admin = request.form.get("admin")
    username = request.form.get("username")
    print("Toggling admin status for", username, request.form.get("status"))
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            'UPDATE User Set admin = %s WHERE name = %s',
            (1 if int(request.form.get("status")) == 0 else 0, username))
        conn.commit()
        userList = get_userlist(cursor)

        return render_template('admin_users.html', admin = admin, userList = userList)    
    except Exception as e:
        print("Error on toggle_admin", e)
    finally:
        cursor.close() 
        conn.close()

@app.route('/admin_delete_user', methods=["POST"])
def admin_delete_user():
    admin = request.form.get("admin")
    username = request.form.get("username")
    return render_template(
        'confirm_delete.html', username=username, admin=admin, deleteType='admin_user')

@app.route('/back_to_admin', methods=["POST"])
def back_to_admin():
    return render_template('admin_page.html', admin = request.form.get("admin"))

@app.route('/admin_entry')
def admin_entry():
    return render_template('admin_entry.html')

@app.route('/index.html')
@app.route('/')
def index():
    return render_template('index.html')

########################################
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6778)

