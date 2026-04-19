import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product, Order, OrderItem, Address, Newsletter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    query = request.args.get('query')
    if query:
        products = Product.query.filter(Product.name.contains(query) | Product.description.contains(query)).all()
    else:
        products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    # Get some related products (simple implementation)
    related_products = Product.query.filter(Product.category == product.category, Product.id != product.id).limit(4).all()
    return render_template('product.html', product=product, related_products=related_products)

@app.route('/products')
def products_list():
    query = request.args.get('query')
    category = request.args.get('category')
    sort = request.args.get('sort', 'default')
    
    if query:
        products = Product.query.filter(Product.name.contains(query) | Product.description.contains(query))
    elif category:
        products = Product.query.filter_by(category=category)
    else:
        products = Product.query
    
    # Sorting
    if sort == 'price_low':
        products = products.order_by(Product.price.asc())
    elif sort == 'price_high':
        products = products.order_by(Product.price.desc())
    elif sort == 'name':
        products = products.order_by(Product.name.asc())
    
    products = products.all()
        
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('products.html', products=products, categories=categories, current_sort=sort)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/account')
@login_required
def account():
    # Fetch orders for the current user
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('account.html', user=current_user, orders=orders)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', 'error')
            return redirect(url_for('register'))
        new_user = User(email=email, name=name, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    products = []
    total = 0
    for product_id, quantity in cart_items.items():
        product = Product.query.get(int(product_id))
        if product:
            products.append({'product': product, 'quantity': quantity})
            total += product.price * quantity
    return render_template('cart.html', products=products, total=total)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    flash('Product added to cart!', 'success')
    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/update_cart_quantity/<int:product_id>/<string:action>')
def update_cart_quantity(product_id, action):
    cart = session.get('cart', {})
    pid_str = str(product_id)
    if pid_str in cart:
        if action == 'increment':
            cart[pid_str] += 1
        elif action == 'decrement':
            cart[pid_str] -= 1
            if cart[pid_str] < 1:
                del cart[pid_str]
        session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    name = request.form.get('name')
    email = request.form.get('email')
    
    if User.query.filter(User.email == email, User.id != current_user.id).first():
        flash('Email already in use.', 'error')
    else:
        current_user.name = name
        current_user.email = email
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    return redirect(url_for('account'))

@app.route('/add_address', methods=['POST'])
@login_required
def add_address():
    addr_type = request.form.get('type')
    full_address = request.form.get('full_address')
    
    new_address = Address(user_id=current_user.id, type=addr_type, full_address=full_address)
    db.session.add(new_address)
    db.session.commit()
    flash('Address added successfully!', 'success')
    return redirect(url_for('account'))

@app.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    email = request.form.get('email')
    if not email:
        flash('Please enter an email.', 'error')
        return redirect(request.referrer)
    
    if Newsletter.query.filter_by(email=email).first():
        flash('You are already subscribed!', 'info')
    else:
        new_sub = Newsletter(email=email)
        db.session.add(new_sub)
        db.session.commit()
        flash('Subscribed successfully! 🎉', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/apply_promo', methods=['POST'])
def apply_promo():
    code = request.form.get('promo_code', '').upper()
    if code == 'JAHNVI10':
        session['discount_percent'] = 10
        flash('Promo code applied! 10% discount added.', 'success')
    elif not code:
        flash('Please enter a code.', 'error')
    else:
        flash('Invalid promo code.', 'error')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = session.get('cart', {})
    if not cart_items:
        return redirect(url_for('index'))
    
    total = 0
    items_to_buy = []
    for product_id, quantity in cart_items.items():
        product = Product.query.get(int(product_id))
        if product:
            total += product.price * quantity
            items_to_buy.append((product, quantity))
            
    # Apply discount if any
    discount = session.get('discount_percent', 0)
    final_total = total * (1 - discount/100)
            
    if request.method == 'POST':
        order = Order(user_id=current_user.id, total_price=final_total)
        db.session.add(order)
        db.session.commit()
        
        for product, quantity in items_to_buy:
            order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=quantity, price=product.price)
            db.session.add(order_item)
        
        db.session.commit()
        session['cart'] = {}
        session.pop('discount_percent', None) # Clear discount after order
        flash('Order placed successfully!', 'success')
        return render_template('success.html')
        
    return render_template('checkout.html', total=final_total, discount=discount)

# Auto-initialize and seed DB on server refresh
with app.app_context():
    try:
        db.create_all()
        if Product.query.count() < 15:
            import db_init
            db_init.seed_db()
    except Exception as e:
        print(f"DB Auto-Init Error: {e}")

if __name__ == '__main__':
    app.run(debug=True)
