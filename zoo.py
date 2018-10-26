from flask import Flask, render_template, request, redirect, url_for
from flaskext.mysql import MySQL

app = Flask(__name__)
db = MySQL(app)
db.init_app(app)

#MySQL config
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'koolkid96'
app.config['MYSQL_DATABASE_DB'] = 'ZooFood'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['TESTING'] = True

conn = db.connect()

@app.route('/animal/<species>')
def animalDiet(species=None):
    cursor = conn.cursor()
    details = getDietDetails(cursor, species)
    return render_template('animal.html', dietDetails=details, species=species)


def getDietDetails(cursor, species):
    dietDetails = []
    
    cursor.execute(
        '''SELECT food, amountPerAnimal FROM Diet
        WHERE speciesName = "''' + species + '"'
    )
    for detail in cursor.fetchall():
        dietDetail = {}
        foodDetail = {}
        cursor.execute(
            'SELECT units FROM Food WHERE name = "' + detail[0] + '"'
        )
        foodDetail['name'] = detail[0]
        foodDetail['unit'] = cursor.fetchall()[0][0]
        dietDetail['food'] = foodDetail
        dietDetail['amountPerAnimal'] = detail[1]
        dietDetails.append(dietDetail)
    return tuple(dietDetails)


@app.route('/animals')
def animals():
    cursor = conn.cursor()
    cursor.execute('SELECT name, numAnimals FROM Species')
    return render_template('animals.html', animals=cursor.fetchall())


@app.route('/addAnimal', methods=['GET', 'POST'])
def addAnimal():
    if request.method == 'POST':
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Species (name, numAnimals) VALUES ("' +
            request.form['name'] + '", ' + request.form['numAnimals'] + ')'
        )
        return redirect('animal/' + request.form['name'])
    elif request.method == 'GET':
        return render_template('addAnimal.html')


@app.route('/deleteAnimal/<species>')
def deleteAnimal(species):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Species WHERE name="' + species + '"')
    if(not cursor.fetchall()):
        return species + ' does not exist.'
    cursor.execute('DELETE FROM Species WHERE name="' + species + '"')
    return redirect('animals')


@app.route('/addFood/<species>', methods=['POST', 'GET'])
def addFood(species):
    cursor = conn.cursor()
    if request.method == 'POST':
        cursor.execute(
            'INSERT INTO Diet (speciesName, food, amountPerAnimal) VALUES ("' +
            species + '", "' + request.form['food'] + '", '
            + request.form['amountPerAnimal'] + ')'
        )
        return redirect('animal/' + species)
    elif request.method == 'GET':
        cursor.execute('SELECT name, units FROM Food') #make so it doesn't get everything
        return render_template(
            'addFoodToAnimal.html', species=species, foods=cursor.fetchall()
        )


@app.route('/food')
def foodList():
    cursor = conn.cursor()
    cursor.execute('SELECT name, units, amount FROM Food')
    return render_template('food.html', foods=cursor.fetchall())


@app.route('/food/<food>')
def food(food):
    cursor = conn.cursor()
    cursor.execute('SELECT units FROM Food WHERE name = "' + food + '"')
    units = cursor.fetchall()[0][0]
    cursor.execute(
        'SELECT speciesName, amountPerAnimal FROM Diet WHERE food = "'
        + food + '"'
    )
    return render_template(
        'food_item.html', name=food, animals=cursor.fetchall(), units=units
    )
