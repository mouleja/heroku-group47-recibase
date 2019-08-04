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
        WHERE ri.recipeId = %s''', (recipeId,)
    )
    ingredients = cursor.fetchall()
    return ingredients

def get_recipe_steps(cursor, recipeId):
    cursor.execute('SELECT step, instruction FROM Step WHERE recipeId = %s', (recipeId,))
    steps = cursor.fetchall()
    return steps

def get_source_list(cursor):
    cursor.execute('SELECT sourceId, name FROM Source')
    sourceList = cursor.fetchall()
    return sourceList

def get_users_recipes(cursor, userId):
    cursor.execute('SELECT * FROM Recipe WHERE userId = %s', (userId,))
    recipes = cursor.fetchall()
    return recipes

def get_ingredient_list(cursor):
    cursor.execute('SELECT ingredientId, name FROM Ingredient')
    ingredientList = cursor.fetchall()
    return ingredientList

def get_basic_recipe(cursor, recipeId):
    cursor.execute('SELECT * FROM Recipe WHERE recipeId = %s', (recipeId,))
    recipe = cursor.fetchone()
    return recipe


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
            LEFT JOIN Source s on s.sourceId = r.sourceId'''
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
    userId = request.form.get("userId")
    recipeId = request.form.get("recipeId")
    user = {'userId' : userId, 'name' : request.form.get('username')}
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT recipeId, name FROM Recipe WHERE recipeId = %s', (recipeId,))
        recipe = cursor.fetchone()

        print("Delete recipe?", recipe)
        return render_template('confirm_delete.html', recipe=recipe, user = user, deleteType='recipe')
    except Exception as e:
        print("Error deleting recipe", recipeId, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in delete_recipe!'

@app.route('/delete', methods=['POST'])
def delete():
    userId = request.form['userId']
    password = request.form['password']
    deleteType = request.form['deleteType']
    recipeId = request.form.get('recipeId')
    username = request.form.get('username')
    print("Deleting:", deleteType, userId, recipeId, username)
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE userId = %s and password = %s', (userId, password))
        checkpw = cursor.fetchone() # True if password wrong
        if not checkpw:
            user = {'userId' : userId, 'name' : username}
            return render_template('confirm_delete.html', 
                    user=user, deleteType=deleteType, recipeId=recipeId, pwError = True)

        if deleteType == 'recipe':
            print("Delete processed for recipe id #", recipeId)
            cursor.execute('DELETE FROM Recipe WHERE recipeId = %s', (recipeId,))
            conn.commit()
            return redirect("/get_recipes")

        if deleteType == 'user':
            cursor.execute('DELETE FROM User WHERE userId = %s', (userId,))
            conn.commit()
            print("Deleted user", userId, "from the database.")
            return redirect('/')

    except Exception as e:
        print("Error deleting", userId, recipeId, deleteType, e)
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
        cursor.execute('SELECT * FROM User WHERE name = %s and password = %s', (username, password))
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
    user = {'userId': userId, 'name': newName, 'password': request.form['password']}
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
    return render_template('confirm_delete.html', user={'userId':userId, 'name':username}, deleteType='user')

@app.route('/update_recipe', methods=['POST'])
def update_recipe():
    userId = request.form.get("userId")
    recipeId = request.form.get("recipeId")
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        recipe = get_recipe_details(cursor, recipeId)
        ingredients = get_recipe_ingredients(cursor, recipeId)
        steps = get_recipe_steps(cursor, recipeId)

        sourceList = get_source_list(cursor)

        ingredientList = get_ingredient_list(cursor)

        print("Updating recipe details:", recipe)
        #print(ingredients)
        #print(steps)
        #print(sourceList)
        #print(ingredientList)
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
    userId = request.form.get("userId")
    recipeName = request.form.get("recipeName")
    source = request.form.get('source')
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        if source == 'no_source':
            source = None
        elif source == 'new_source':
            new_name = request.form.get("new_name")
            if not new_name:    # treat new_source with no new_name as NULL source
                source = None
            else:
                cursor.execute('INSERT INTO Source (name, url) VALUES (%s, %s)',
                               (new_name, request.form.get('new_url')))
                conn.commit()
                cursor.execute('SELECT sourceId FROM Source WHERE name = %s', (new_name,))
                source = cursor.fetchone()['sourceId']

        cursor.execute('INSERT INTO Recipe (name, userId, sourceId) VALUES (%s, %s, %s)',
                               (recipeName, userId, source))
        conn.commit()
        cursor.execute('SELECT * FROM Recipe WHERE name = %s and userId = %s', (recipeName, userId))
        recipe = cursor.fetchall()[-1]  # No uniqueness requirement for recipe name, get last

        ingredientList = get_ingredient_list(cursor)

        return render_template('add_recipe_details.html', recipe=recipe, ingredients = [], 
                               steps = [], ingredientList = ingredientList)
    
    except Exception as e:
        print("Error adding recipe -", recipeName, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in add_recipe!'

@app.route('/add_recipe_ingredient', methods=['POST'])
def add_recipe_ingredient():
    recipeId = request.form.get("recipeId")
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        print("Adding ingredient to", recipeId, request.form.get('ingredient'), request.form.get('amount'), request.form.get('unit'), request.form.get('preperation'))

        cursor.execute(
            '''INSERT INTO Recipe_Ingredient (recipeId, ingredientId, amount, unit, preperation)
            VALUES (%s, %s, %s, %s, %s)''',
                (recipeId, request.form.get('ingredient'), request.form.get('amount'), 
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

        print("Adding new ingredient to", recipeId, request.form.get('ingredientName'), request.form.get('amount'), request.form.get('unit'), request.form.get('preperation'))

        cursor.execute(
            '''INSERT INTO Ingredient (name, defaultAmount, defaultUnit, calories)
            VALUES (%s, %s, %s, %s)''',
                (ingredientName, request.form.get("defaultAmount"), request.form.get("defaultUnit"), 
                 request.form.get("calories")))
        conn.commit()

        cursor.execute('SELECT ingredientId FROM Ingredient WHERE name = %s', (ingredientName,))
        newId = cursor.fetchall()[-1]['ingredientId']  # No uniqueness requirement for ingredient name, get last

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
    changeError = ''
    print("Changing:", changeType, recipeId)
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        if changeType == 'name':
            cursor.execute('UPDATE Recipe SET name = %s WHERE recipeId = %s',
                (request.form.get("recipeName"), recipeId))

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
    search_text = '%' + search_text + '%'
    
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
        search_text = search_text[1:-1]

        return render_template('search_results.html', recipes= recipes, 
                search_type = search_type, search_text = search_text)
    
    except Exception as e:
        print("Error searching", search_type, search_text, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in search_for!'




@app.route('/')
def index():
    return render_template('index.html')

########################################
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6778)

