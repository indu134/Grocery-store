from flask import Flask,render_template,request,flash,redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  or_
from werkzeug.utils import secure_filename
from flask_restful import Resource, Api
import secrets
import os
from hashlib import sha256

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Database URI


cur = os.getcwd()
class Config(object):
    UPLOAD_FOLDER = os.path.join(cur, 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
session_u = []
session_m = []


db = SQLAlchemy(app)
from databases import *
app.secret_key = '!@#$%^&*)(*&^%)'
app.config.from_object(Config)
api = Api(app)
class curd_api(Resource):
    def get(sef,name,key):
        try:
            def obj_to_dict(product):
                return {"id":product.id,"name":product.name,"category":product.category,"price":product.price,"stock":product.stock,"manager":product.manager_name} 
            try:
                manager = db.session.execute(db.select(Manager).filter_by(username=name)).scalar_one()
                if manager.api_key == key:
                    products = manager.products
                    tmp = []
                    for i in range(len(products)):
                        tmp.append(obj_to_dict(products[i]))
                    products = jsonify(tmp)
                    return products
                else:
                    return jsonify()
            except:
                return jsonify()
        except:
            return jsonify()
    def post(self,name,key):
        try:
            manager = db.session.execute(db.select(Manager).filter_by(username=name)).scalar_one()
            if manager.api_key == key:
                name = request.form.get("name",None)
                if name is None or name == "":
                    ret = jsonify({
                        "error":"name field is required"
                    })
                    ret.status_code = 302
                    return ret
                category = request.form.get("category",None)
                if category is None or category == "":
                    ret = jsonify({
                        "error":"category field is required"
                    })
                    ret.status_code = 302
                    return ret
                

                stock = request.form.get("stock",None)
                if stock is None or stock == "":
                    ret = jsonify({
                        "error":"stock field is required"
                    })
                    ret.status_code = 302
                    return ret
                else:
                    stock = int(stock)
                price = request.form.get("price",None)
                if price is None or price == "":
                    ret = jsonify({
                        "error":"price field is required"
                    })
                    ret.status_code = 302
                    return ret
                else:
                    price = float(price)
                
                file = request.files.get("photo",None)
                if file is None or file == "":
                    ret = jsonify({"error":"photo field is required"})
                    ret.status_code = 302
                    return ret
                else:
                    ext = file.filename.split('.')
                    if ext[-1] in Config.ALLOWED_EXTENSIONS:
                        path = os.path.join(Config.UPLOAD_FOLDER, secure_filename(name+" "+manager.username+"."+ext[-1]))
                        file.save(path)
                        d = '../../static/uploads/'+secure_filename(name+" "+manager.username+"."+ext[-1])
                        add_product(name, category,stock, price,d, manager.username)
                        return jsonify({"message":"sucessfully added product"})
            else:
                return jsonify()
        except:
            return jsonify()
    def put(self,name,key,id):
        try:
            manager = db.session.execute(db.select(Manager).filter_by(username=name)).scalar_one()
            m = []
            if manager.api_key == key:
                try:
                    product = db.session.execute(db.select(Product).filter_by(manager_name=name,id=id)).scalar_one()
                except:
                    ret =jsonify({
                        "error":"Product Not Found"
                    })
                    ret.status_code = 404
                    return ret

                pname = request.form.get("name",None)
                if pname is None or pname == "":
                    pass
                else:
                    ext = product.photo_path.split('.')
                    prv = product.photo_path.split('/')
                    product.name = pname
                    new_path = os.path.join(Config.UPLOAD_FOLDER, secure_filename(pname+" "+manager.username+"."+ext[-1]))
                    prv_path = os.path.join(Config.UPLOAD_FOLDER, prv[-1])
                    os.rename(prv_path,new_path)
                    d = '../../static/uploads/'+secure_filename(pname+" "+manager.username+"."+ext[-1])
                    product.photo_path = d
                    db.session.commit()
                    m.append(
                        {
                            "m1":"Product name is sucessfully updated"
                        }
                    )
                pcategory = request.form.get("category",None)
                if pcategory is None or pcategory=="":
                    pass
                else:
                    product.category = pcategory
                    db.session.commit()
                    m.append(
                        {
                            "m2":"Product category is updated"
                        }
                    )
                pstock = request.form.get("stock",None)
                if pstock is None or pstock == "":
                    pass
                else:
                    try:
                        pstock = int(pstock)
                        product.stock = pstock
                        db.session.commit()
                        m.append({
                            "m3":"Product stock is updated"
                        })
                    except:
                        m.append({
                            "e1":"stock must be a integer"
                        })
                pprice = request.form.get("price",None)
                if pprice is None or pprice == "":
                    pass
                else:
                    try:
                        pprice = float(pprice)
                        product.price = pprice
                        db.session.commit()
                        m.append({
                            "m4":"Product price is updated"
                        })
                    except:
                        m.append({
                            "e2":"Product price must be float"
                        })
                file = request.files.get("photo",None)
                if file is None or file == "":
                    pass
                else:
                    ext = file.filename.split('.')
                    if ext[-1] in Config.ALLOWED_EXTENSIONS:
                        prv = product.photo_path.split('/')
                        path = os.path.join(Config.UPLOAD_FOLDER, secure_filename(product.name+" "+manager.username+"."+ext[-1]))
                        prv_path = os.path.join(Config.UPLOAD_FOLDER,prv[-1])
                        if os.path.exists(prv_path):
                            os.remove(prv_path)
                        file.save(path)
                        d = '../../static/uploads/'+secure_filename(product.name+" "+manager.username+"."+ext[-1])
                        product.photo_path = d
                        db.session.commit()
                        m.append({
                            "m5":"Product photo is updated"
                        })
                
                return jsonify(m)
            
                        


                
            else:
                return jsonify()
        except:
            return jsonify()
    

    def delete(self,name,key,id):
        try:
            manager = db.session.execute(db.select(Manager).filter_by(username=name)).scalar_one()
            if manager.api_key == key:
                try:
                    product = db.session.execute(db.select(Product).filter_by(manager_name=name,id=id)).scalar_one()
                except:
                    ret = jsonify({
                        "error":"Product Not Found"
                    })
                    ret.status_code = 404
                    return ret
                db.session.delete(product)
                db.session.commit()
                return jsonify({
                    "message":"Product is deleted"
                })
            else:
                return jsonify()
        except:
            return jsonify()







api.add_resource(curd_api,'/api/<string:name>/<string:key>','/api/<string:name>/<string:key>/<int:id>')



    


@app.route('/',methods=["GET","POST"])
def signin():
    if request.method == "POST":
        uname = request.form.get("username")
        password = request.form.get("password")
        print(uname)
        try:
            user = db.session.execute(db.select(User).filter_by(username=uname)).scalar_one()
            if user.check_password(password):
                session_u.append(uname)
                return redirect('/{}/{}'.format(uname,sha256(uname.encode()).hexdigest()))
            else:
                flash("wrong password")
        except:
            flash("wrong username")


    return render_template("signin.html")


@app.route('/managerLogin',methods=["GET","POST"])
def managerSignin():
    if request.method == "POST":
        uname = request.form.get("username")
        password = request.form.get("password")
        try:
            manager = db.session.execute(db.select(Manager).filter_by(username=uname)).scalar_one()
            if manager.check_password(password):
                session_m.append(uname)
                return redirect('/manager/{}/{}'.format(uname,sha256(uname.encode()).hexdigest()))
            else:
                flash("wrong password")
        except:
            flash("wrong username")
        


    return render_template("managerSignin.html")




@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method ==  "POST":
        allUname = User.query.with_entities(User.username).all()
        uname = request.form.get('uname')
        if (uname,) in allUname:
            flash("username already there")
            return redirect("/signup")
        
        allEmail = User.query.with_entities(User.email).all()
        email = request.form.get('email')
        if (email,) in allEmail:
            flash("email already there")
            return redirect("/signup")
        
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')
        if confirmPassword == password:
            add_user(uname, email, password)
            return redirect("/")
        else:
            flash("please check password")



    return render_template("signup.html")






@app.route('/<uname>/<uhash>',methods=["GET","POST"])
def main_page(uname,uhash):
    try:
        user = db.session.execute(db.select(User).filter_by(username=uname)).scalar_one()
        if sha256(user.username.encode()).hexdigest() == uhash and uname in session_u :
            products = Product.query.all()
            url = '/{}/{}'.format(uname,uhash)
            cart_url = '/{}/{}/cart'.format(uname,uhash)
            orders_url = url+'/orders'
            logout_url = '/{}/{}/logout'.format(uname,uhash)
            profile_url ='/{}/{}/profile'.format(uname,uhash)
            if request.method == "POST":
                search = request.form.get("search")
                if search:
                    searchProducts  = Product.query.filter(or_(Product.name.like("%"+search+"%") ,Product.category.like("%"+search+"%"))).all()
                else:
                    return redirect(url)

                return render_template('searchpage.html',user=user,products=searchProducts,url=url,cart_url=cart_url,orders_url=orders_url,logout_url=logout_url,profile_url=profile_url)
            return render_template('userPage.html',user=user,products=products,url=url,cart_url=cart_url,orders_url=orders_url,logout_url=logout_url,profile_url=profile_url)
        else:
            return redirect("/")
    except:
        return "something went wrong"
    

@app.route('/manager/<user>/<uhash>')
def main_manager_page(user,uhash):
    try:
        manager = db.session.execute(db.select(Manager).filter_by(username=user)).scalar_one()
        if sha256(manager.username.encode()).hexdigest() == uhash  and user in session_m :
            url = '/manager/{}/{}/add_product'.format(user,uhash)
            logout_url = '/manager/{}/{}/logout'.format(user,uhash)
            update_url = '/manager/{}/{}'.format(user,uhash)
            return render_template('managerPage.html',user=manager,url=url,logout_url=logout_url,update_url=update_url)
        else:
            return redirect('/managerLogin')
    except:
        return "something went wrong"



@app.route('/manager/<user>/<uhash>/add_product',methods=["GET","POST"])
def add_product_page(user,uhash):
    try:
        manager = db.session.execute(db.select(Manager).filter_by(username=user)).scalar_one()
        if sha256(manager.username.encode()).hexdigest() == uhash  and user in session_m:
            if request.method == "POST":
                name = request.form.get("name")
                category = request.form.get("category")
                stock = int(request.form.get("stock"))
                price = float(request.form.get("price"))
                file = request.files["photo"]
                if file.filename == "":
                    return "something went wrong"
                else:
                    ext = file.filename.split('.')
                    if ext[-1] in Config.ALLOWED_EXTENSIONS:
                        path = os.path.join(Config.UPLOAD_FOLDER, secure_filename(name+" "+manager.username+"."+ext[-1]))
                        file.save(path)
                        d = '../../static/uploads/'+secure_filename(name+" "+manager.username+"."+ext[-1])
                        add_product(name, category,stock, price,d, manager.username)
                        url = '/manager/{}/{}'.format(user,uhash)
                        return redirect(url)

                    

            return render_template('addProduct.html')
        else:
            return redirect('/managerLogin')
    except:
        return "something went wrong"
    



@app.route("/<uname>/<uhash>/<name>/<manager_name>",methods=["GET","POST"])
def add_cart_page(uname,uhash,name,manager_name):
    try:
        user = db.session.execute(db.select(User).filter_by(username=uname)).scalar_one()
        if sha256(user.username.encode()).hexdigest() == uhash and uname in session_u :
            product = db.session.execute(db.select(Product).filter_by(manager_name=manager_name,name=name)).scalar_one()
            if request.method == "POST":
                stock = request.form.get("stock")
                stock = int(stock)
                if stock > 0 and stock <= product.stock:
                    add_cart(name,product.category, stock,uname,manager_name)

                    return redirect("/{}/{}/cart".format(uname,uhash))
                    
            return render_template('addCart.html',product=product)
        else:
            return redirect("/")
    except:
        return "something went wrong"
        

@app.route("/<uname>/<uhash>/cart")
def cart_page(uname,uhash):
    try:
        user = db.session.execute(db.select(User).filter_by(username=uname)).scalar_one()
        if sha256(user.username.encode()).hexdigest() == uhash and uname in session_u:
            dashboard_url = '/{}/{}'.format(uname,uhash)
            placeorder_url = '/{}/{}/placeorder'.format(uname,uhash)
            orders_url = dashboard_url+'/orders'
            removecart_url = '/{}/{}/cartremove'.format(uname,uhash)
            logout_url = '/{}/{}/logout'.format(uname,uhash)
            profile_url ='/{}/{}/profile'.format(uname,uhash)
            return render_template('cartpage.html',user=user,dashboard_url = dashboard_url,placeorder_url=placeorder_url,orders_url=orders_url,removecart_url=removecart_url,logout_url=logout_url,profile_url=profile_url)
        else:
            return redirect("/")
    except:
        return "something went wrong"


@app.route("/<uname>/<uhash>/placeorder/<id>",methods=["GET","POST"])
def place_order_page(uname,uhash,id):
    try:
        user = db.session.execute(db.select(User).filter_by(username=uname)).scalar_one()
        if sha256(user.username.encode()).hexdigest() == uhash and uname in session_u :
            cart = db.session.execute(db.select(Cart).filter_by(id=id)).scalar_one()
            product = db.session.execute(db.select(Product).filter_by(manager_name=cart.manager_name,name=cart.name)).scalar_one()
            manager = db.session.execute(db.select(Manager).filter_by(username=cart.manager_name)).scalar_one()
            instock = True
            if cart.stock > product.stock:
                instock = False
            if request.method == "POST":
                if instock and user.wallet >= cart.stock*product.price:
                    place_order(cart.name,cart.category,cart.stock,uname,cart.manager_name)
                    user.wallet = user.wallet - cart.stock*product.price
                    manager.wallet = manager.wallet + cart.stock*product.price
                    product.stock = product.stock - cart.stock
                    delete(cart)
                    return redirect('/{}/{}/orders'.format(uname,uhash))
                else:
                    return "something went wrong"

            return render_template('placeOrder.html',product=cart,instock=instock,real=product,user=user)
        else:
            return redirect("/")
    except:
        return "something went wrong"
    

@app.route("/<uname>/<uhash>/orders")
def order_page(uname,uhash):
    try:
        user = db.session.execute(db.select(User).filter_by(username=uname)).scalar_one()
        if sha256(user.username.encode()).hexdigest() == uhash and uname in session_u :
            dashboard_url = '/{}/{}'.format(uname,uhash)
            cart_url = '/{}/{}/cart'.format(uname,uhash)
            cancleorder_url = '/{}/{}/orders'.format(uname,uhash)
            logout_url = '/{}/{}/logout'.format(uname,uhash)
            profile_url ='/{}/{}/profile'.format(uname,uhash)
            return render_template('ordersPage.html',user=user,cart_url=cart_url,dashboard_url=dashboard_url ,cancleorder_url=cancleorder_url,logout_url=logout_url,profile_url=profile_url)
        else:
            return redirect("/")
    except:
        return "something went wrong"
        

        

@app.route("/<uname>/<uhash>/orders/<id>")
def cancle_order(uname,uhash,id):
    try:
        user = db.session.execute(db.select(User).filter_by(username=uname)).scalar_one()
        if sha256(user.username.encode()).hexdigest() == uhash and uname in session_u :
            order = db.session.execute(db.select(Order).filter_by(id=id)).scalar_one()
            manager = db.session.execute(db.select(Manager).filter_by(username=order.manager_name)).scalar_one()
            product = db.session.execute(db.select(Product).filter_by(manager_name=order.manager_name,name=order.name)).scalar_one()
            url = '/{}/{}'.format(uname,uhash)
            orders_url = url+'/orders'
            user.wallet = user.wallet + order.price*order.stock
            manager.wallet = manager.wallet - order.price*order.stock
            product.stock = product.stock + order.stock
            delete(order)
            return redirect(orders_url)
        else:
            return redirect("/")
    except:
        return "something went wrong"
    

    
@app.route("/<uname>/<uhash>/cartremove/<id>")
def remove_cart(uname,uhash,id):
    try:
        user = db.session.execute(db.select(User).filter_by(username=uname)).scalar_one()
        if sha256(user.username.encode()).hexdigest() == uhash and uname in session_u :
            cart = db.session.execute(db.select(Cart).filter_by(id=id)).scalar_one()
            cart_url = '/{}/{}/cart'.format(uname,uhash)
            if cart in user.cart:
                delete(cart)
            return redirect(cart_url)
        else:
            return redirect("/")
    except:
        return "something went wrong"


@app.route("/manager/<user>/<uhash>/removeproduct/<id>")
def manager_remove_product(user,uhash,id):
    try:
        manager = db.session.execute(db.select(Manager).filter_by(username=user)).scalar_one()
        if sha256(manager.username.encode()).hexdigest() == uhash and user in session_m :
            product = db.session.execute(db.select(Product).filter_by(id=id)).scalar_one()
            if product in manager.products:
                n = product.photo_path.split('/')
                os.remove(os.path.join(Config.UPLOAD_FOLDER,n[-1]))
                delete(product)
            return redirect('/manager/{}/{}'.format(user,uhash))
        else:
            return redirect('/managerLogin')
    except:
        return "something went wrong"


@app.route('/<uname>/<uhash>/logout')
def logout(uname,uhash):
    if uname in session_u:
        try:
            user = db.session.execute(db.select(User).filter_by(username=uname)).scalar_one()
            if sha256(user.username.encode()).hexdigest() == uhash:
                session_u.remove(uname)
                return redirect('/')
            else:
                return redirect('/')
        except:
            return redirect('/')
    else:
        return redirect('/')
        

@app.route('/manager/<uname>/<uhash>/logout')
def manager_logout(uname,uhash):
    if uname in session_m:
        try:
            manager = db.session.execute(db.select(Manager).filter_by(username=uname)).scalar_one()
            if sha256(manager.username.encode()).hexdigest() == uhash  :
                session_m.remove(uname)
                return redirect('/managerLogin')
            else:
                return redirect('/managerLogin')
        except:
            return redirect('/managerLogin')
    else:
        return redirect('/managerLogin')


@app.route('/<uname>/<uhash>/profile')
def profile(uname,uhash):
    try:
        user = db.session.execute(db.select(User).filter_by(username=uname)).scalar_one()
        if sha256(user.username.encode()).hexdigest() == uhash and uname in session_u :
            return render_template('profile.html',user=user)
        else:
            return "something went wrong"
    except:
        return "something went wrong"


@app.route('/manager/<user>/<uhash>/<id>/updateProductName',methods=["GET","POST"])

def update_name(user,uhash,id):
    try:
        manager = db.session.execute(db.select(Manager).filter_by(username=user)).scalar_one()
        if sha256(manager.username.encode()).hexdigest() == uhash  and user in session_m :
            product = db.session.execute(db.select(Product).filter_by(id=id)).scalar_one()
            back_url = '/manager/{}/{}'.format(user,uhash)
            if request.method == "POST":
                name = request.form.get("name")
                ext = product.photo_path.split('.')
                prv = product.photo_path.split('/')
                product.name = name
                new_path = os.path.join(Config.UPLOAD_FOLDER, secure_filename(name+" "+manager.username+"."+ext[-1]))
                prv_path = os.path.join(Config.UPLOAD_FOLDER, prv[-1])
                os.rename(prv_path,new_path)
                d = '../../static/uploads/'+secure_filename(name+" "+manager.username+"."+ext[-1])
                product.photo_path = d
                db.session.commit()
                return redirect('/manager/{}/{}'.format(user,uhash))
            return render_template("updateProductName.html",product=product,back_url=back_url)
        else:
            return redirect('/managerLogin')
    except:
        return "something went wrong"



@app.route('/manager/<user>/<uhash>/<id>/updateProductStock',methods=["GET","POST"])

def update_stock(user,uhash,id):
    try:
        manager = db.session.execute(db.select(Manager).filter_by(username=user)).scalar_one()
        if sha256(manager.username.encode()).hexdigest() == uhash  and user in session_m :
            product = db.session.execute(db.select(Product).filter_by(id=id)).scalar_one()
            back_url = '/manager/{}/{}'.format(user,uhash)
            if request.method == "POST":
                stock = request.form.get("stock")
                product.stock = stock
                db.session.commit()
                return redirect('/manager/{}/{}'.format(user,uhash))
            return render_template("updateProductStock.html",product=product,back_url=back_url)
        else:
            return redirect('/managerLogin')
    except:
        return "something went wrong"
    


@app.route('/manager/<user>/<uhash>/<id>/updateProductPrice',methods=["GET","POST"])

def update_price(user,uhash,id):
    try:
        manager = db.session.execute(db.select(Manager).filter_by(username=user)).scalar_one()
        if sha256(manager.username.encode()).hexdigest() == uhash  and user in session_m :
            product = db.session.execute(db.select(Product).filter_by(id=id)).scalar_one()
            back_url = '/manager/{}/{}'.format(user,uhash)
            if request.method == "POST":
                price = request.form.get("price")
                product.price = price
                db.session.commit()
                return redirect('/manager/{}/{}'.format(user,uhash))
            return render_template("updateProductPrice.html",product=product,back_url=back_url)
        else:
            return redirect('/managerLogin')
    except:
        return "something went wrong"

@app.route('/manager/<user>/<uhash>/<id>/updateProductCategory',methods=["GET","POST"])

def update_category(user,uhash,id):
    try:
        manager = db.session.execute(db.select(Manager).filter_by(username=user)).scalar_one()
        if sha256(manager.username.encode()).hexdigest() == uhash  and user in session_m :
            product = db.session.execute(db.select(Product).filter_by(id=id)).scalar_one()
            back_url = '/manager/{}/{}'.format(user,uhash)
            if request.method == "POST":
                category = request.form.get("category")
                product.category = category
                db.session.commit()
                return redirect('/manager/{}/{}'.format(user,uhash))
            return render_template("updateProductCategory.html",product=product,back_url=back_url)
        else:
            return redirect('/managerLogin')
    except:
        return "something went wrong"


@app.route('/manager/<user>/<uhash>/<id>/updateProductPhoto',methods=["GET","POST"])

def update_photo(user,uhash,id):
        manager = db.session.execute(db.select(Manager).filter_by(username=user)).scalar_one()
        if sha256(manager.username.encode()).hexdigest() == uhash  and user in session_m :
            product = db.session.execute(db.select(Product).filter_by(id=id)).scalar_one()
            back_url = '/manager/{}/{}'.format(user,uhash)
            if request.method == "POST":
                file = request.files["photo"]
                if file.filename == "":
                    return "something went wrong"
                else:
                    ext = file.filename.split('.')
                    if ext[-1] in Config.ALLOWED_EXTENSIONS:
                        prv = product.photo_path.split('/')
                        path = os.path.join(Config.UPLOAD_FOLDER, secure_filename(product.name+" "+manager.username+"."+ext[-1]))
                        prv_path = os.path.join(Config.UPLOAD_FOLDER,prv[-1])
                        if os.path.exists(prv_path):
                            os.remove(prv_path)
                        file.save(path)
                        d = '../../static/uploads/'+secure_filename(product.name+" "+manager.username+"."+ext[-1])
                        product.photo_path = d
                        db.session.commit()


                return redirect('/manager/{}/{}'.format(user,uhash))
            return render_template("updateProductPhoto.html",product=product,back_url=back_url)
        else:
            return redirect('/managerLogin')


@app.route('/manager/<user>/<uhash>/<id>/conformation',methods=["GET","POST"])

def conformation(user,uhash,id):
    try:
        manager = db.session.execute(db.select(Manager).filter_by(username=user)).scalar_one()
        if sha256(manager.username.encode()).hexdigest() == uhash  and user in session_m :
            product = db.session.execute(db.select(Product).filter_by(id=id)).scalar_one()
            removeproduct_url = '/manager/{}/{}/removeproduct/{}'.format(user,uhash,id)
            back_url = '/manager/{}/{}'.format(user,uhash)
            return render_template("conformation.html",product=product,removeproduct_url=removeproduct_url,back_url=back_url)
        else:
            return redirect('/managerLogin')
    except:
        return "something went wrong"


@app.route('/manager/<user>/<uhash>/api')
def api(user,uhash):
    try:
        manager = db.session.execute(db.select(Manager).filter_by(username=user)).scalar_one()
        if sha256(manager.username.encode()).hexdigest() == uhash  and user in session_m :
            gen_url = '/manager/{}/{}/api/genarate'.format(user,uhash)
            return render_template("api.html",user=manager,gen_url=gen_url)
        else:
            return redirect('/managerLogin')
    except:
        return "something went wrong"
        
@app.route('/manager/<user>/<uhash>/api/genarate')
def api_genarate(user,uhash):
    try:
        manager = db.session.execute(db.select(Manager).filter_by(username=user)).scalar_one()
        if sha256(manager.username.encode()).hexdigest() == uhash  and user in session_m :
            key = secrets.token_urlsafe(16)
            manager.api_key = key
            db.session.commit()
            return redirect('/manager/{}/{}/api'.format(user,uhash))
        else:
            return redirect('/managerLogin')
    except:
        return "something went wrong"






























def add_user(username, email, password):
    try:
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return 'User added successfully!'
    except:
        return 'something went wrong,User not added'

@app.route('/add_manager/<username>/<email>/<password>')
def add_manager(username, email, password):
    try:    
        new_Manager = Manager(username=username, email=email, password=password)
        db.session.add(new_Manager)
        db.session.commit()
        return 'Manager added successfully!'
    except:
        return 'something went wrong,Manager not added'


def add_product(name,category, stock, price, photo_path, manager_name):
    stock = int(stock)
    price = float(price)
    manager = db.session.execute(db.select(Manager).filter_by(username=manager_name)).scalar_one()
    if manager:
        product = Product(name=name, category=category,stock=stock, price=price, photo_path=photo_path)
        manager.products.append(product)
        db.session.commit()
        return 'product added successfully'
    return None



def add_cart(name, category,stock, user_name,manager_name):
    product = db.session.execute(db.select(Product).filter_by(manager_name=manager_name,name=name)).scalar_one()
    user = db.session.execute(db.select(User).filter_by(username=user_name)).scalar_one()
    if user and product:
        cart = Cart(name=product.name,category=category, stock=stock, price=product.price, photo_path=product.photo_path,manager_name=manager_name)
        user.cart.append(cart)
        db.session.commit()
        return 'product added successfully'
    return None



def place_order(name, category,stock, user_name,manager_name):
    product = db.session.execute(db.select(Product).filter_by(manager_name=manager_name,name=name)).scalar_one()
    user = db.session.execute(db.select(User).filter_by(username=user_name)).scalar_one()
    if user and product:
        order = Order(name=product.name,category=category, stock=stock, price=product.price, photo_path=product.photo_path,manager_name=manager_name)
        user.orders.append(order)
        db.session.commit()
        return 'order placed'
    return None


def delete(o):
    db.session.delete(o)
    db.session.commit()



app.run(host="0.0.0.0")

