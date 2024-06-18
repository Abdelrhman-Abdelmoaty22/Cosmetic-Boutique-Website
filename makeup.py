from flask import Flask,request,redirect,url_for,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cosmetic.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class person(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key as an integer
    username = db.Column(db.String(100), unique=True, nullable=False)  # Standard field name, made unique
    password = db.Column(db.String(255), nullable=False)  # Standard field name
    name = db.Column(db.String(100))  # Optional full name field

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(100))
    def __str__(self):
        return self.name

    def get_absolute_url(self, admin=False):
        return url_for('show_product', id=self.id, admin=admin)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    kind = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(150), nullable=True)
    expire_date = db.Column(db.Date)
    price = db.Column(db.Integer)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    brand = db.relationship('Brand', backref=db.backref('products', lazy=True))

    def __str__(self):
        return self.name

    def get_absolute_url(self, admin=False):
        return url_for('show_product', id=self.id, admin=admin)

@app.route('/')
def start():
    return render_template("Login.html")

@app.route('/home')
def home():
    admin = request.args.get('admin', default="false").lower() == 'true'
    total_brands = Brand.query.count()
    total_products = Product.query.count()
    base_template = 'base_generic_admin.html' if admin else 'base_generic.html'
    return render_template('index.html', total_brands=total_brands, total_products=total_products, admin=admin, base_template=base_template)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['pass']
        # Check for admin first
        if username == 'adminG4' and password == '123456':
            return redirect(url_for('home', admin=True))
        # Check for regular user credentials
        user = person.query.filter_by(username=username, password=password).first()
        if user:
            return redirect(url_for('home'))
        else:
            # Return to login with error message
            return render_template('Login.html', error="Invalid username or password")
    # Display login page initially or if not POST method
    return render_template('Login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['pass']
        name = request.form['name']
        if(username != 'admin'):
            new_user = person(username=username, password=password, name=name)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('Sign_up.html',error="This username is already in database")
    return render_template('Sign_up.html')

@app.route('/init_db')
def init_db():
    # Creating some sample brands
    brand1 = Brand(name='Loreal', origin='France')
    brand2 = Brand(name='Nivea', origin='Germany')

    # Adding brands to the session
    db.session.add(brand1)
    db.session.add(brand2)

    # Committing the changes to the database for brands
    db.session.commit()

    # Creating some products with additional attributes
    product1 = Product(
        name='Loreal Shampoo', 
        kind='Shampoo',
        description='A revitalizing shampoo for damaged hair.',
        expire_date=date(2025, 12, 31),
        price=15,
        brand_id=brand1.id
    )
    product2 = Product(
        name='Nivea Moisturizer', 
        kind='Moisturizer',
        description='A nourishing moisturizer for all skin types.',
        expire_date=date(2024, 10, 15),
        price=10,
        brand_id=brand2.id
    )

    # Adding products to the session
    db.session.add(product1)
    db.session.add(product2)

    # Committing the changes to the database for products
    db.session.commit()

    return 'Database initialized with brands and products!'


@app.route('/show_brands')
def show_brands():
    admin = request.args.get('admin', default="false").lower() == 'true'
    brands = Brand.query.all()
    base_template = 'base_generic_admin.html' if admin else 'base_generic.html'
    return render_template('brand_list.html', brands=brands, admin=admin,base_template=base_template)

@app.route('/show_products')
def show_products():
    admin = request.args.get('admin', default="false").lower() == 'true'
    products = Product.query.all()
    base_template = 'base_generic_admin.html' if admin else 'base_generic.html'
    return render_template('product_list.html', products=products, admin=admin, base_template=base_template)




@app.route('/brand_details/<int:id>')
def brand_details(id):
    admin = request.args.get('admin', default="false").lower() == 'true'
    brand = Brand.query.get_or_404(id)
    base_template = 'base_generic_admin.html' if admin else 'base_generic.html'
    return render_template('brand_details.html', brand=brand, admin=admin, base_template=base_template)


@app.route('/show_product/<int:id>')
def show_product(id):
    admin = request.args.get('admin', default="false").lower() == 'true'
    product = Product.query.get_or_404(id)
    base_template = 'base_generic_admin.html' if admin else 'base_generic.html'
    return render_template('product_details.html', product=product, admin=admin,base_template=base_template)


@app.route('/add_brand', methods=['GET', 'POST'])
def add_brand():
    admin = request.args.get('admin', default="false").lower() == 'true'
    if request.method == 'POST': 
        name = request.form['name']
        origin = request.form['origin']
        new_brand = Brand(name=name, origin=origin)
        db.session.add(new_brand)
        db.session.commit()
        return redirect(url_for('show_brands'))
    base_template = 'base_generic_admin.html' if admin else 'base_generic.html'
    return render_template('add_brand.html',admin=admin,base_template=base_template)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    admin = request.args.get('admin', default="false").lower() == 'true'
    if request.method == 'POST':
        name = request.form['name']
        kind = request.form['kind']
        description = request.form['description']
        expire_date = request.form['expire_date']
        price = request.form['price']
        brand_id = request.form['brand_id']
        new_product = Product(
            name=name,
            kind=kind,
            description=description,
            expire_date=date.fromisoformat(expire_date),
            price=int(price),
            brand_id=brand_id
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('show_products', admin=admin))
    else:
        brands = Brand.query.all()
        base_template = 'base_generic_admin.html' if admin else 'base_generic.html'
        return render_template('add_product.html', brands=brands, admin=admin, base_template=base_template)






if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables for our data models
    app.run(debug=True)
