from flask import Flask,render_template,request,url_for,redirect,flash,session,Response
from flask_session import Session
import bcrypt
import mysql.connector
from otp import genotp
from cmail import sendmail
from keys import secret_key,salt1,salt2
from tokens import token
from itsdangerous import URLSafeTimedSerializer
import os
import stripe
import pdfkit
stripe.api_key="sk_test_51MMsHhSGj898WTbYXSx509gD14lhhXs8Hx8ipwegdytPB1Bkw0lJykMB0yGpCux95bdw1Gk9Gb9nJIWzPEEDxSqf00GEtCqZ8Y"

app=Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
Session(app)
#mydb=mysql.connector.connect(host='localhost',user='root',password='Admin',db='ecommy')
app.secret_key=b'\xa9P\x985\x15\xbf\xa9\x8b\t\x01'
#config=pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
user=os.environ.get('RDS_USERNAME')
db=os.environ.get('RDS_DB_NAME')
password=os.environ.get('RDS_PASSWORD')
host=os.environ.get('RDS_HOSTNAME')
port=os.environ.get('RDS_PORT')
with mysql.connector.connect(host=host,port=port,user=user,password=password,db=db) as conn:
    cursor=conn.cursor()
    cursor.execute("CREATE TABLE  if not exists vendor (email varchar(100) NOT NULL,v_name varchar(255) NOT NULL,mobile_no bigint NOT NULL,address text NOT NULL,password varbinary(255) DEFAULT NULL,PRIMARY KEY (email),UNIQUE KEY mobile_no (mobile_no))")
    cursor.execute("CREATE TABLE user (username varchar(255) NOT NULL,mobile_no bigint NOT NULL,email varchar(255) NOT NULL,address text NOT NULL,password varbinary(255) DEFAULT NULL,PRIMARY KEY (email),UNIQUE KEY mobile_no (mobile_no))")
    cursor.execute("CREATE TABLE additems (item_id binary(16) NOT NULL,item_name longtext NOT NULL,discription longtext,quantity int DEFAULT NULL,category enum(makeup,skincare,haircare,bodycare) DEFAULT NULL,price int DEFAULT NULL,addedby varchar(100) DEFAULT NULL,imgid varchar(200) DEFAULT NULL,PRIMARY KEY (item_id),KEY addedby (addedby),CONSTRAINT additems_ibfk_1 FOREIGN KEY (addedby) REFERENCES vendor (email) ON DELETE CASCADE ON UPDATE CASCADE)")
    cursor.execute("CREATE TABLE orders (ordid binary(16) NOT NULL,itemid binary(16) NOT NULL,item_name varchar(255) DEFAULT NULL,qty int DEFAULT NULL,total_price decimal(20,4) DEFAULT NULL,user varchar(255) DEFAULT NULL,category varchar(150) DEFAULT NULL,dis text,imgid varchar(255) DEFAULT NULL,PRIMARY KEY (ordid),KEY itemid (itemid),KEY user (user),CONSTRAINT orders_ibfk_1 FOREIGN KEY (itemid) REFERENCES additems (item_id) ON DELETE CASCADE, CONSTRAINT orders_ibfk_2 FOREIGN KEY (user) REFERENCES user (email) ON DELETE SET NULL ON UPDATE CASCADE)")
mydb=mysql.connector.connect(host=host,user=user,port=port,password=password,db=db)
@app.route('/')
def home():
    return render_template('welcome.html')
@app.route('/vendorsignup',methods=['GET','POST'])
def vendorsignup():
    if request.method=='POST':
        email=request.form['email']
        v_name=request.form['v_name']
        mobile_no=request.form['mobile_no']
        address=request.form['address']
        password=request.form['password']
       
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(*) from vendor where email=%s',[email])
            count=cursor.fetchone()[0]
            
            if count==1:
                raise Exception
        except Exception as e:
            
            flash('email already existed')
            return redirect(url_for('vendorsignup'))
        else:
            otp=genotp()
            data={'email':email,'v_name':v_name,'mobile_no':mobile_no,'address':address,'password':password,'otp':otp}
            subject='OTP for Ecom app'
            body=f'Verification otp for Ecom app {otp}'
            sendmail(to=email,subject=subject,body=body)
            flash('OTP has sent to your Email.')
            return redirect(url_for('otp',data=token(data,salt=salt1)))
    return render_template('vendorsignup.html')
@app.route('/otp/<data>',methods=['GET','POST'])
def otp(data):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(data,salt='salt1',max_age=120)
    except Exception as e:
        print(e)
        flash('link expired')
        return redirect(url_for('vendorsignup'))
    else:
        if request.method=='POST':
            uotp=request.form['otp']
            if uotp==data['otp']:
                bytes= data['password'].encode('utf-8')
                # generating the salt
                salt= bcrypt.gensalt()

                #HAshing the password
                hash = bcrypt.hashpw(bytes, salt)
           
                cursor=mydb.cursor(buffered=True)
                cursor.execute('insert into vendor(email,v_name,mobile_no,address,password) values(%s,%s,%s,%s,%s)',[data['email'],data['v_name'],data['mobile_no'],data['address'],hash])
                mydb.commit()
                cursor.close()
                flash('Registration has successfully done')
                return redirect(url_for('vlogin'))
    return render_template('otp.html')
@app.route('/vlogin',methods=['GET','POST'])
def vlogin():
    if session.get('vendor'):
        return redirect(url_for('vendor_dashboard'))
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select password from vendor where email=%s',[email])
        hashed_password=cursor.fetchone()
        if hashed_password:
            hashed_password=hashed_password[0]
            if bcrypt.checkpw(password.encode('utf-8'),bytes(hashed_password)):
                session['vendor']=email
                if not session['vendor']:
                    session[email]={}
                return redirect(url_for('vendor_dashboard'))
            else:
                flash('Incorrect Password.')
                return redirect(url_for('vlogin'))
        else:
            flash('Email not registerd')
            return redirect (url_for('vendorsignup'))
            

    return render_template('vlogin.html')
@app.route('/vendor_dashboard')
def vendor_dashboard():
    if session.get('vendor'):
        return render_template('vdashboard.html')
    else:
        return redirect(url_for('vlogin'))
@app.route('/vlogout')
def vlogout():
    if session.get('vendor'):
        session.pop('vendor')
        return redirect(url_for('vlogin'))
    else:
        return redirect(url_for('vlogin'))
@app.route('/additems',methods=['GET','POST'])
def additems():
    if session.get('vendor'):
        if request.method=='POST':
            name=request.form['name']
            discription=request.form['desc']
            qyt=request.form['qyt']
            price=request.form['price']
            category=request.form['category']
            img=request.files['image']
            imgextension=img.filename.split('.')[-1]
           
            imgname=genotp()
            filename=imgname+'.'+imgextension
            path=os.path.dirname(os.path.abspath(__file__))
            static_path=os.path.join(path,'static')
            img.save(os.path.join(static_path,filename))
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into additems(item_id,item_name, discription, quantity, category, price, addedby, imgid) values(uuid_to_bin(uuid()),%s,%s,%s,%s,%s,%s,%s)',[name,discription,qyt,category,price,session.get('vendor'),filename])
            mydb.commit()
            cursor.close()
            flash('Item {name} successfully added.')
            return redirect(url_for('vendor_dashboard'))
    return render_template('items.html')
@app.route('/viewitems')
def viewitems():
    if session.get('vendor'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('''SELECT bin_to_uuid(item_id), item_name,discription,quantity, category, price, addedby,imgid from additems where addedby=%s''',[session.get('vendor')])
        count=cursor.fetchall()
        print (count)
        if count:
            return render_template('card.html',count=count)
        else:
            return render_template('card.html')
    else:
        return redirect(url_for('vlogin'))

@app.route('/deleteitem/<item_id>')
def deleteitem(item_id):
    if session.get('vendor'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('''SELECT imgid FROM additems where item_id=uuid_to_bin(%s) and addedby=%s''',[item_id,session.get('vendor')])
        count=cursor.fetchone()
        print(count)
        path=os.path.dirname(os.path.abspath(__file__))
        static_path=os.path.join(path,'static')
        file_path=os.path.join(static_path,count[0])
        os.remove(file_path)
        cursor.execute('delete from additems where item_id=uuid_to_bin(%s) and addedby=%s',[item_id,session.get('vendor')])


        mydb.commit()
        cursor.close()
        flash(f'item {item_id} deleted successfully')
        return redirect(url_for('viewitems'))
    return redirect(url_for('vlogin'))

@app.route('/updateitem/<item_id>',methods=['GET','POST'])
def updateitem(item_id):
    if session.get('vendor'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('''SELECT bin_to_uuid(item_id), item_name,discription,quantity, category, price, addedby,imgid from additems where item_id=uuid_to_bin(%s) and addedby=%s''',[item_id,session.get('vendor')])
        count=cursor.fetchall()
        print(count)
        if request.method=='POST':
            name=request.form['name']
            discription=request.form['desc']
            qyt=request.form['qyt']
            price=request.form['price']
            category=request.form['category']
            if request.files['image'].filename=='':
                filename=count[0][7]
            else:
                img=request.files['image']
                imgextension=img.filename.split('.')[-1]
                imgname=genotp()
                filename=imgname+'.'+imgextension
                path=os.path.dirname(os.path.abspath(__file__))
                static_path=os.path.join(path,'static')
                file_path=os.path.join(static_path,count[0][7])
                os.remove(file_path)
                img.save(os.path.join(static_path,filename))
            cursor=mydb.cursor(buffered=True)
            cursor.execute('update additems set item_name=%s,discription=%s,quantity=%s,category=%s,price=%s,imgid=%s where item_id=uuid_to_bin(%s)',[name,discription,qyt,category,price,filename,item_id])
            mydb.commit()
            cursor.close()
            
            
          
            
            flash(f'item {name} updated successfully')
            return redirect(url_for('viewitems'))
        return render_template('updateitem.html',count=count)
    return redirect(url_for('vlogin'))
@app.route('/forgot',methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        email=request.form['email']
        
        subject='Reset link for ecommy Appliccation'
        body=f"Reset link for forgot password of ecommy :{url_for('fconfirm',token=token(data=email,salt=salt2),_external=True)}"
        sendmail(to=email,subject=subject,body=body)
       
        flash('Reset link has sent to given Email pls check')
        return redirect(url_for('forgot'))
    return render_template('forgot.html')
@app.route('/fconfirm/<token>',methods=['GET','POST'])
def fconfirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        email=serializer.loads(token,salt=salt2,max_age=180)
    except Exception as e:
        return 'Link expired'
    else:
        if request.method=='POST':
            npassword=request.form['npassword']
            cnpassword=request.form['cnpassword']
            if npassword==cnpassword:
                bytes = npassword.encode('utf-8')
                # generating the salt
                salt = bcrypt.gensalt()
                 # Hashing the password
                hash = bcrypt.hashpw(bytes,salt)
                cursor=mydb.cursor(buffered=True)
                cursor.execute('update vendor set password=%s where email=%s',[hash,email])
                mydb.commit()
                cursor.close()
                return redirect(url_for('vlogin'))
            else:
                flash('password missmatch')
                return render_template('updatepassword.html')
    return render_template('updatepassword.html')
@app.route('/usersignup',methods=['GET','POST'])
def usersignup():
    if request.method=='POST':
        email=request.form['email']
        username=request.form['username']
        mobile_no=request.form['mobile_no']
        address=request.form['address']
        password=request.form['password']
       
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(*) from user where email=%s',[email])
            count=cursor.fetchone()[0]
            
            if count==1:
                raise Exception
        except Exception as e:
            
            flash('email already existed')
            return redirect(url_for('usersignup'))
           
        else:
            otp=genotp()
            data={'email':email,'username':username,'mobile_no':mobile_no,'address':address,'password':password,'otp':otp}
            subject='OTP for Ecom app'
            body=f'Verification otp for Ecom app {otp}'
            sendmail(to=email,subject=subject,body=body)
            flash('OTP has sent to your Email.')
            return redirect(url_for('otp_verification',data=token(data,salt=salt2)))
    return render_template('usersignup.html')



@app.route('/otp_verification/<data>',methods=['GET','POST'])
def otp_verification(data):
        try:
          serializer=URLSafeTimedSerializer(secret_key)
          data=serializer.loads(data,salt=salt2,max_age=120)
        except Exception:
            print(Exception)
            flash('OTP expired')
            return redirect(url_for('usersignup'))
        else:
            if request.method=='POST':
                uotp=request.form['otp']
                if uotp==data['otp']:
                    

                    bytes = data['password'].encode('utf-8')
                    salt = bcrypt.gensalt()
                    # hashing the password
                    hash = bcrypt.hashpw(bytes,salt)
                    cursor=mydb.cursor(buffered=True)
                    cursor.execute('insert into user(email,username,mobile_no,address,password) values(%s,%s,%s,%s,%s)',[data['email'],data['username'],data['mobile_no'],data['address'],hash])
                    mydb.commit()
                    cursor.close()
                    flash('Registration successfully done ')
                    return redirect(url_for('login'))
                else:
                        
                    
                    flash('otp was incorrect')
                    return redirect(url_for('usersignup'))
        return render_template('otp.html')
            
   
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('userdashboard'))
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select password from user where email=%s',[email])
        hashed_password=cursor.fetchone()
        if hashed_password:
            hashed_password=hashed_password[0]
            if bcrypt.checkpw(password.encode('utf-8'),bytes(hashed_password)):
                session['user']=email
                if not session.get(email):
                    session[email]={}
                return redirect(url_for('userdashboard'))
            else:
                flash('Incorrect Password.')
                return redirect(url_for('login'))
        else:
            flash('Email not registerd')
            return redirect (url_for('usersignup'))
            

    return render_template('login.html')


@app.route('/userdashboard')
def userdashboard():
    cursor=mydb.cursor(buffered=True)
    cursor.execute('select bin_to_uuid(item_id),item_name,discription,quantity,category,price,addedby,imgid  from additems')
    count=cursor.fetchall()
    if count:
        return render_template('dash.html',count=count)
    else:
        return render_template('dash.html')

@app.route('/userlogout')
def userlogout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/category/<type>')
def category(type):
    cursor=mydb.cursor(buffered=True)
    cursor.execute('select bin_to_uuid(item_id),item_name,discription,quantity,category,price,addedby,imgid from additems where category=%s',[type])
    count=cursor.fetchall()
    return render_template('dash.html' ,count=count)   


@app.route('/discription/<item_id>')
def discription(item_id):
    cursor=mydb.cursor(buffered=True)
    cursor.execute('select bin_to_uuid(item_id),item_name,dis,qyt,category,price,addedby,imgid  from additems where item_id=uuid_to_bin(%s)',[item_id])
    count=cursor.fetchone()
    print(count)
    return render_template('discription.html',count=count)

@app.route('/cart<item_id>/<item_name>/<dis>/<category>/<price>/<imgid>/<qyt>')
def cart(item_id,item_name,dis,category,price,imgid,qyt):
    if not session.get('user'):
        return redirect(url_for('login'))
    print(session[session.get('user')])
    if item_id not in session[session.get('user')]:
        session[session.get('user')][item_id]=[item_name,dis,category,price,imgid,int(qyt)]
        session.modified=True
        flash(f'{item_name} added to cart')
        return redirect(url_for('userdashboard'))
    print(type(session[session.get('user')][item_id][5]))
    session[session.get('user')][item_id][5] +=1
    return redirect(url_for('userdashboard'))



@app.route('/viewcart')
def viewcart():
    if not session.get('user'):
        return redirect(url_for('login'))
    count=session.get(session.get('user')) if session.get(session.get('user')) else 'empty'
    if count=='empty':
        return 'no products added'
    print(count)
    return render_template('cart.html',count=count)
@app.route('/removecart/<itemid>')
def removecart(itemid):
    if session.get('user'):
        print(session[session.get('user')])
        data1=session[session.get('user')].pop(itemid)
        flash(f'{data1[0]} has been removed from cart')
        return redirect(url_for('viewcart'))
    return redirect(url_for('login'))
@app.route('/payment/<itemid>/<itemname>/<int:price>/<category>/<imgid>/<dis>',methods=['GET','POST'])
def pay(itemid,itemname,price,category,imgid,dis):
    if session.get('user'):
        user=session.get('user')
        q=int(request.form['quantity']) if request.form['quantity'] else 1
        total=price*1
        checkout_session=stripe.checkout.Session.create(
            success_url=url_for('success',itemid=itemid,item_name=itemname,total=total,q=q,category=category,imgid=imgid,dis=dis,_external=True),
            line_items=[
                {
                    'price_data':{
                        'product_data':{
                            'name':itemname,
                        },
                        'unit_amount':price*100,
                        'currency':'inr',
                    },
                    'quantity':q
                },
            ],
            mode="payment",)
        return redirect(checkout_session.url)
    else:
        return redirect(url_for('login'))
@app.route('/success/<itemid>/<item_name>/<q>/<total>/<category>/<imgid>/<dis>') 
def success(itemid,item_name,q,total,category,imgid,dis):
    user=session.get('user') 
    cursor=mydb.cursor(buffered=True)
    print(itemid)
    cursor.execute(
    'insert into orders (ordid, itemid, item_name, qty, total_price, user, category, imgid, dis) '
    'values (uuid_to_bin(uuid()), uuid_to_bin(%s), %s, %s, %s, %s, %s, %s, %s)',
    [itemid, item_name, q, total, user, category, imgid, dis])

    mydb.commit()


    return redirect(url_for('userdashboard'))
@app.route('/orders')
def orders():
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select bin_to_uuid(ordid),bin_to_uuid(itemid),item_name,qty,total_price,user,category,imgid,dis from orders where user=%s',[session.get('user')])
        count=cursor.fetchall()
        return render_template('orders.html',count=count)
    return redirect(url_for('login'))
'''@app.route('/getinvoice/<ordid>.pdf')
def invoice(ordid):
    cursor=mydb.cursor(buffered=True)
    cursor.execute('select username,mobile_no,address,u.email,bin_to_uuid(ordid),bin_to_uuid(itemid),item_name,qty,total_price,category,imgid,dis from user u join orders o on u.email=o.user where ordid=uuid_to_bin(%s)',[ordid])
    count=cursor.fetchone()
    if count:
        html=render_template('bill.html',count=count)
        pdf=pdfkit.from_string(html,False,configuration=config)
        response=Response(pdf,content_type='application/pdf')
        response.headers['content-Disposition']='inline; filename=output.pdf'
        return response
    else:
        flash('Something Went Wrong')
        return redirect(url_for('orders'))'''


    




    

app.run(debug=True,use_reloader=True)
