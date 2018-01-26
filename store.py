from bottle import route, run, template, static_file, get, post, delete, request
from sys import argv
import json
import pymysql
import time
from bson import json_util

connection=pymysql.connect(
    host='localhost',
    user='root',
    db='store_adv',
    passwd='root',
    cursorclass=pymysql.cursors.DictCursor
)

product_dummy_obj={"PRODUCTS":[{"title":"NO PRODUCT FOUND","id":"N/A","description":"description unavailable","price":0,
                                "img_url":"./images/np.jpg","favorite":0, "date_created":"N/A"}]}
default_store_object={"STORE":"Store Name Here"}

@get("/admin")
def admin_portal():
	return template("pages/admin.html")

@get("/")
def index():
    return template("index.html")


@get('/js/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='js')


@get('/css/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='css')


@get('/images/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='images')

@get('/store_name')
def loadStoreName():
    default_store_object={}
    with connection.cursor() as cursor:
        try:
            sql="select * from STORE_NAME"
            cursor.execute(sql)
            result=cursor.fetchone()
            if result["name"]=="":
                result["name"]=default_store_object["STORE"]
            default_store_object["STORE"]=result["name"]
            default_store_object["STATUS"]="SUCCESS"
            default_store_object["MSG"]="200- Success"
        except Exception as e:
            default_store_object["STATUS"] = "ERROR"
            default_store_object["MSG"] = "500 - Internal error"
    return json.dumps(default_store_object)

@post('/store')
def changeStoreName():
    answer_obj={}
    user_input=request.POST.get("STORE")
    if not user_input:
        answer_obj["STATUS"]="ERROR"
        answer_obj["MSG"]="No name entered. try again"
        return json.dumps(answer_obj)
    else:
        clear_table=clearTable('STORE_NAME')
        if clear_table["STATUS"]=="SUCCESS":
            with connection.cursor() as cursor:
                try:
                    sql = "insert into STORE_NAME(name) VALUES('{}')".format(user_input)
                    res=cursor.execute(sql)
                    connection.commit()
                    print res
                    answer_obj["STATUS"]="Success"
                    answer_obj["MSG"]="Store name changed successfully"
                    answer_obj["STORE"]=user_input
                except Exception as e:
                    answer_obj["STATUS"]="ERROR"
                    answer_obj["MSG"]="Database error"+repr(e)
            return json.dumps(answer_obj)
        else:
            return json.dumps(clear_table)


def clearTable(tablename):
    answer_obj={}
    with connection.cursor() as cursor:
        try:
            sql="DELETE FROM {0}".format(tablename)
            res=cursor.execute(sql)
            connection.commit()
            print res
            answer_obj["STATUS"]="SUCCESS"
            answer_obj["MSG"]="200- Success"
        except Exception as e:
            answer_obj["STATUS"] = "ERROR"
            answer_obj["MSG"] = "500 - Internal error on deleting from table "+repr(e)
    print answer_obj
    return answer_obj

@post('/category')
def addCategory():
    answer_obj={}
    new_category_name = request.POST.get('name')
    if new_category_name:
        categories_obj = fetchAllCategories()
        print categories_obj
        for category in categories_obj["CATEGORIES"]:
            if category["name"] == new_category_name:
                answer_obj["STATUS"]="ERROR"
                answer_obj["MSG"]="Category already exists"
                return json.dumps(answer_obj)
        answer_obj=insertNewCategory(new_category_name)
        print answer_obj

        amended_categories_obj = fetchAllCategories()
        for category in amended_categories_obj["CATEGORIES"]:
            if category["name"] == new_category_name:
                answer_obj["CAT_ID"] = category["id"]
        print answer_obj
    else:
        answer_obj["STATUS"]="ERROR"
        answer_obj["MSG"]="Please enter category name"
    return json.dumps(answer_obj)

def insertNewCategory(category):
    answer_obj = {}
    try:
        with connection.cursor() as cursor:
            sql = "insert into CATEGORIES(name) VALUES('{0}')".format(category)
            cursor.execute(sql)
            connection.commit()
            answer_obj["STATUS"] = "SUCCESS"
            answer_obj["MSG"] = "201 - category created/updated successfully"
    except Exception as e:
        answer_obj["STATUS"] = "ERROR"
        answer_obj["MSG"] = "Internal error"
    print answer_obj
    return answer_obj

@get('/categories')
def getCategories():
    categories_obj=fetchAllCategories()
    return json.dumps(categories_obj)

def fetchAllCategories():
    categories_obj_to_return = {}
    try:
        with connection.cursor() as cursor:
            sql = "select * from CATEGORIES;"
            cursor.execute(sql)
            result = cursor.fetchall()
            #print result
            categories_obj_to_return["STATUS"]="SUCCESS"
            categories_obj_to_return["CATEGORIES"]=result
    except Exception as e:
        categories_obj_to_return["STATUS"]="ERROR"
        categories_obj_to_return["MSG"]="500 - Internal Error"
        #print "something went wrong with the database"
    return categories_obj_to_return

@get('/category/<categoryID>/products')  #add sorted products
def getProducts(categoryID):
    categories_obj=fetchAllCategories()
    print categories_obj
    product_obj_to_return = {}
    category_name=""
    product_list=[]
    flag=False
    for category in categories_obj["CATEGORIES"]:
        if category["id"] == int(categoryID):
            flag=True
    print flag

    if not flag:
        product_obj_to_return["status"] = "ERROR"
        product_obj_to_return["MSG"] = "404 - category not found"
    else:
        try:
            with connection.cursor() as cursor:
                sql = "select * from PRODUCTS order by favorite desc, date_created desc"
                cursor.execute(sql)
                result = cursor.fetchall()
                print result
                #product_obj_list=result
                for product in result:
                    if product["category"]==int(categoryID):
                        product["date_created"]=''
                        product_list.append(product)
                print product_list
                if len(product_list)==0:
                    return json.dumps(product_dummy_obj)
                product_obj_to_return["PRODUCTS"]=product_list
                product_obj_to_return["STATUS"]="SUCCESS"
                product_obj_to_return["MSG"]="200-Success"
        except Exception as e:
            product_obj_to_return["status"]="ERROR"
            product_obj_to_return["MSG"]="500 - Internal Error"
    print product_obj_to_return
    return json.dumps(product_obj_to_return)

@route('/category/<catId>', method="DELETE")
def removeCategory(catId):
    answer_obj = {}
    flag=False
    categories_obj = fetchAllCategories()
    for category in categories_obj["CATEGORIES"]:
        if category["id"] == int(catId):
            flag=True
            break
    if flag:
        try:
            with connection.cursor() as cursor:
                sql = "delete from CATEGORIES where id={0}".format(int(catId))
                result = cursor.execute(sql)
                connection.commit()
                print result
                answer_obj["STATUS"] = "Success"
                answer_obj["MSG"] = "The category was successfully deleted"
        except Exception as e:
            answer_obj["STATUS"] = "ERROR"
            answer_obj["MSG"] = "Database foreign key error: cannot delete category, since it is associated with a number of products"
    else:
        answer_obj["STATUS"] = "ERROR"
        answer_obj["MSG"] = "The category does not exist"
    return answer_obj

def fetchAllProducts():
    products_obj_to_return = {}
    try:
        with connection.cursor() as cursor:
            sql = "select * from PRODUCTS;"
            cursor.execute(sql)
            result = cursor.fetchall()
            for product in result:
                product["date_created"]=''
            products_obj_to_return["STATUS"] = "SUCCESS"
            products_obj_to_return["MSG"] = "200-Success"
            products_obj_to_return["PRODUCTS"] = result
    except Exception as e:
        products_obj_to_return["STATUS"] = "ERROR"
        products_obj_to_return["MSG"] = "500 - Internal Error"
    return products_obj_to_return

@get('/products')
def getAllProducts():
    products_obj_to_return=fetchAllProducts()
    print products_obj_to_return
    return json.dumps(products_obj_to_return)
    #return json.dumps(products_server_db)

def insertOrUpdateProduct(product_obj, option):
    answer_obj={}
    sql=''
    print product_obj
    try:
        with connection.cursor() as cursor:
            if option==1:
                sql="insert into PRODUCTS(category,price,title,description,img_url,favorite, date_created) VALUES({0},{1},'{2}','{3}','{4}',{5},'{6}')"\
                    .format(product_obj.get('category'), product_obj.get('price'), product_obj.get('title'),
                            product_obj.get('description'), product_obj.get('img_url'), product_obj.get('favorite'),product_obj.get('date_created'))
            else:
                sql = "update PRODUCTS SET price={0}, description='{1}', img_url='{2}', favorite={3}, date_created='{6}' where title='{4}' and category={5}" \
                    .format(product_obj['price'], product_obj['description'], product_obj['img_url'],product_obj['favorite'],
                            product_obj['title'], product_obj['category'], product_obj['date_created'])
            cursor.execute(sql)
            connection.commit()
            answer_obj["STATUS"]="SUCCESS"
            answer_obj["MSG"]="201 - product created/updated successfully"
    except Exception as e:
            answer_obj["STATUS"]="ERROR"
            answer_obj["MSG"]="Internal error"+repr(e)
    print answer_obj
    return answer_obj

@post('/product')
def addProduct():
    answer_obj={}
    products_in_db = fetchAllProducts()
    form_data=request.forms
    product_data_to_add={}
    product_data_to_add['category']=int(form_data.get("category"))
    product_data_to_add['title']=form_data.get('title')
    product_data_to_add['description']=form_data.get('desc')

    try:
        product_data_to_add['price']=float(form_data.get('price'))
    except ValueError:
        answer_obj["STATUS"]="ERROR"
        answer_obj["MSG"]="Data error - enter a number in the price field"
        return json.dumps(answer_obj)

    product_data_to_add['favorite']=0 if form_data.get('favorite')==None else 1

    if './images/' in form_data.get('img_url'):
        product_data_to_add['img_url']=form_data.get('img_url')
    else:
        answer_obj["STATUS"]="ERROR"
        answer_obj["MSG"]="Data error - the url to image is not valid"
        return json.dumps(answer_obj)

    current_date = time.strftime("%Y-%m-%d")
    print current_date
    product_data_to_add['date_created']=current_date
    #print product_data_to_add

    if all([product_data_to_add['category'], product_data_to_add['title'], product_data_to_add['price'], product_data_to_add['img_url']]):
        #flag=False
        for product in products_in_db["PRODUCTS"]:
            if product_data_to_add["category"]==product["category"] and product_data_to_add["title"]==product["title"]:
                try:
                    answer_obj=insertOrUpdateProduct(product_data_to_add,0)
                    print answer_obj
                except Exception as e:
                    answer_obj["STATUS"] = "ERROR"
                    answer_obj["MSG"] = "500 - internal error. Failed to update product"
                return json.dumps(answer_obj)
        try:
            answer_obj=insertOrUpdateProduct(product_data_to_add,1)
            print answer_obj
        except Exception as e:
            answer_obj["STATUS"]="ERROR"
            answer_obj["MSG"]="500 - internal error. Failed to create product"
    else:
        answer_obj["STATUS"]="ERROR"
        answer_obj["MSG"]="400 - bad request: missing parameters"
    return json.dumps(answer_obj)

@get('/product/<id>')
def renderProducts(id):
    product_return = {}
    try:
        with connection.cursor() as cursor:
            sql = "select * from PRODUCTS where id={0}".format(int(id))
            tr=cursor.execute(sql)
            result = cursor.fetchall()
            for product in result:
                product['date_created']=''

            if tr==0:
                product_return["STATUS"]="ERROR"
                product_return["MSG"]="No such product exists"
            else:
                product_return["STATUS"]="SUCCESS"
                product_return["MSG"]="200-Sucessfull operation"
                product_return["PRODUCTS"] = result
    except Exception as e:
        product_return["STATUS"] = "ERROR"
        product_return["MSG"] = "500 - Internal Database Error"
    return json.dumps(product_return)

@delete('/product/<id>')
def delecteProduct(id):
    answer_return={}
    products_in_db = fetchAllProducts()
    flag=False
    for product in products_in_db["PRODUCTS"]:
        if product['id']==int(id):
            flag=True
            break
    if flag:
        try:
            with connection.cursor() as cursor:
                sql = "delete from PRODUCTS where id={0}".format(int(id))
                result = cursor.execute(sql)
                connection.commit()
                print result
                answer_return["STATUS"] = "Success"
                answer_return["MSG"] = "The product was successfully deleted"
        except Exception as e:
            answer_return["STATUS"] = "ERROR"
            answer_return["MSG"] = "500-Internal error"
    else:
        answer_return["STATUS"] = "ERROR"
        answer_return["MSG"] = "No such category exists"
    return answer_return

#run(host='0.0.0.0', port=argv[1])
def main():
    run(host="localhost", port=7800)

if __name__=="__main__":
    main()