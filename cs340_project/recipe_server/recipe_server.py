#! usr/bin/python3
#########################################################################
# CS340-400-U19 Project Group 47 - Jason Moule - Tommy Armstrong
# 
# Recipe Sharing Database Web Backend Server
#   Python Flask App with various routes for CRUD implementation
#   using mariaDB database running on remote server
#
# Code adapted from course tutorial at: 
# https://github.com/knightsamar/CS340_starter_flask_app/
# and https://www.roytuts.com/python-web-application-crud-example-using-flask-and-mysql/
#########################################################################

import pymysql, datetime
from app import app
from db_connection import mysql
from flask import flash, render_template, request, redirect
from werkzeug import generate_password_hash, check_password_hash

@app.route('/get_recipes')
def get_recipes():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM Recipe;'
        )
        result = cursor.fetchall() or {'text':'Nothing in recipe!!'}
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
        cursor.execute(
            '''SELECT r.name rname, r.date, u.name uname, s.name sname FROM Recipe r
            INNER JOIN User u ON u.userId = r.userId
            INNER JOIN Source s ON s.sourceId = r.sourceId
            WHERE r.recipeId = %s''', (id,)
        )
        recipeInfo = cursor.fetchone() or {'rname':'Error'}

        cursor.execute(
            '''SELECT i.name, ri.amount, ri.unit, ri.preperation
            FROM Recipe_Ingredient ri
            INNER JOIN Ingredient i ON i.ingredientId = ri.ingredientId
            WHERE ri.recipeId = %s''', (id,)
        )
        ingredients = cursor.fetchall() or [{'name': 'ERROR'}]

        cursor.execute(
            '''SELECT instruction FROM Step WHERE recipeId = %s''', (id,)
        )
        steps = cursor.fetchall() or [{'instruction': 'ERROR'}]

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
        
@app.route('/update_recipe/<int:id>')
def update_recipe(id):

    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''SELECT r.name rname, r.date, u.name uname, s.name sname FROM Recipe r
            INNER JOIN User u ON u.userId = r.userId
            INNER JOIN Source s ON s.sourceId = r.sourceId
            WHERE r.recipeId = %s''', (id,)
        )
        recipeInfo = cursor.fetchone() or {'rname':'Error'}

        cursor.execute(
            '''SELECT i.name, ri.amount, ri.unit, ri.preperation
            FROM Recipe_Ingredient ri
            INNER JOIN Ingredient i ON i.ingredientId = ri.ingredientId
            WHERE ri.recipeId = %s''', (id,)
        )
        ingredients = cursor.fetchall() or [{'name': 'ERROR'}]

        cursor.execute(
            '''SELECT instruction FROM Step WHERE recipeId = %s''', (id,)
        )
        steps = cursor.fetchall() or [{'instruction': 'ERROR'}]

        print("Updating recipe details:", recipeInfo, ingredients, steps)
        return render_template('update_recipe.html', recipeInfo=recipeInfo,
                               ingredients=ingredients, steps=steps)
    except Exception as e:
        print("Error getting recipe",id, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in update_recipe!'

@app.route('/delete_recipe/<int:id>')
def delete_recipe(id):

    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''SELECT r.name FROM Recipe r WHERE r.recipeId = %s''', (id,)
        )
        recipe = cursor.fetchone() or {'rname':'Error'}

        print("Delete recipe?", recipe)
        return render_template('confirm_delete.html', recipe=recipe, recipeId=id)
    except Exception as e:
        print("Error getting recipe",id, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in delete_recipe!'

@app.route('/delete', methods=['POST'])
def delete():
    id = request.form['id']
    print("Delete processed for recipe id #",id)
    return redirect("/get_recipes")

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
        user = cursor.fetchone() or {'name':'Error'}

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
        cursor.execute('SELECT userId, name FROM User WHERE name = %s and password = %s', (username, password))
        user = cursor.fetchone()

        if not user:
            return render_template('user_entry.html', error=True)

        cursor.execute('SELECT recipeId, name, date FROM Recipe WHERE userId = %s', (user['userId'],))
        recipes = cursor.fetchall()

        return render_template('user_page.html', user=user, recipes=recipes)
    
    except Exception as e:
        print("Error getting user", username, e)
    finally:
        cursor.close() 
        conn.close()

    return 'Something went wrong in user_page!'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6778)

