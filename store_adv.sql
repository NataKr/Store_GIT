drop database if exists store_adv;
CREATE DATABASE store_adv;
use store_adv;

drop table if exists CATEGORIES;
create table CATEGORIES(
	id INT NOT NULL auto_increment,
	name varchar(30) NOT NULL UNIQUE,
    
	primary key(id)
)
engine=innoDB;

insert into CATEGORIES(name) VALUES('ropes');
insert into CATEGORIES(name) VALUES('clothes');
insert into CATEGORIES(name) VALUES('gear');

#select * from categories;

drop table if exists PRODUCTS;
create table PRODUCTS(
	id INT NOT NULL auto_increment, #for category id	
    category INT NOT NULL,
    price DOUBLE NOT NULL,
    title varchar(20) NOT NULL,
    description varchar(30),
    img_url varchar(50) NOT NULL,
    date_created date NOT NULL,
    favorite INT,
    primary key(id)
)
engine=innoDB;

alter table PRODUCTS add constraint FK_products1 
foreign key(category) references CATEGORIES(id)
on update cascade
on delete restrict; 

insert into PRODUCTS(category,price,title,description,img_url,favorite, date_created) VALUES(1,200.50,'dynamo','red','./images/image1.jpg',1,'2017-01-01');
insert into PRODUCTS(category,price,title,description,img_url,favorite, date_created) VALUES(2,150.50,'mytitle','yellow','./images/image2.jpg',0,'2017-06-06');
insert into PRODUCTS(category,price,title,description,img_url,favorite, date_created) VALUES(2,50.50,'jeans','cool jeans','./images/image3.jpg',0,'2017-12-31');
insert into PRODUCTS(category,price,title,description,img_url,favorite, date_created) VALUES(2,50.50,'hat','cool jeans','./images/image5.jpg',0,'2018-01-14');
insert into PRODUCTS(category,price,title,description,img_url,favorite, date_created) VALUES(2,50.50,'gloves','yo','./images/image2.jpg',1,'2018-01-16');

#use store_final;
#select * from PRODUCTS;
#select * from PRODUCTS order by favorite desc, date_created desc;
#describe products;

#delete from PRODUCTS where img_url='uuu';
#ALTER TABLE PRODUCTS MODIFY title varchar(20) NOT NULL ;
#update PRODUCTS SET price=150.0, description='new description', img_url='./images/image5.jpg', favorite=0 where title='dynamo' and category='1';


drop table if exists STORE_NAME;
create table STORE_NAME(
	id INT NOT NULL auto_increment,
	name varchar(30) NOT NULL UNIQUE,    
	primary key(id)
)
engine=innoDB; 

insert into STORE_NAME(name) VALUES('My Store Name Here');
#select * from STORE_NAME;
#DELETE FROM STORE_NAME;