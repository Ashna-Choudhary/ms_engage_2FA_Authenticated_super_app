# 2FA_Authenticated_super_app

Python

GUI: Kivy

Database: MySQL

Face recognition API: Amazon Rekognition


Requirements:

The default orientation of BoxLayout needs to be changed to vertical. This can be done by going to the definition of BoxLayout and changing orientation = OptionProperty('horizontal', options=('horizontal', 'vertical')) to orientation = OptionProperty('vertical', options=('horizontal', 'vertical')).


DB setup:

I have used MySQL db. A MySQL table needs to be set up in your local. This can be done by uncommenting the lines (139, 142, 143)/ using the queries in the create_server_connection class. These queries are:
self.execute_query(connection, "CREATE DATABASE db;")
self.execute_query(connection, "create table tab(id int PRIMARY KEY AUTO_INCREMENT, username varchar(25) NOT NULL, password varchar(25) NOT NULL);")
self.execute_query(connection,'insert into tab(username, password) values("ashna","67@Secret");')


Replace username and password in db call:

line 128 - self.create_server_connection("localhost","uname","pswd"): replace uname and pswd with the mysql username and password of your local db.


References:

https://www.youtube.com/watch?v=LKispFFQ5GU&t=4713s

