from turtle import bgcolor, color
import kivy 
import re
# Import kivy dependencies first
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout 
from kivy.uix.screenmanager import ScreenManager, Screen

# Import kivy UX components
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# Import other kivy stuff
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.logger import Logger
from kivy.lang import Builder

# Import standard dependencies
import cv2
import os

#aws
import boto3

#sql dependencies
from asyncio.windows_events import NULL
import mysql.connector
from mysql.connector import Error
import pandas as pd

#declaring global/ default variables
layout = BoxLayout
user_id=0
username=""
password=""
black = [0, 0, 0, 0] 
white=[1, 1, 1, 1]

#kivy app and layout
class FaceRecPage(layout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main layout components 
        self.verification_label = Label(size_hint=(1,.1))
        self.web_cam = Image(size_hint=(1,.8))
        self.button = Button(text="Verify", on_press=self.verify, size_hint=(1,.1))
        self.title_label = Label(text="Face Recognition", size_hint=(1,.2), font_size=22)

        # Add items to layout
        self.add_widget(self.title_label)
        self.add_widget(self.web_cam)
        self.add_widget(self.button)
        self.add_widget(self.verification_label)

        # Setup video capture device
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0/33.0)

    # Run continuously to get webcam feed
    def update(self, *args):

        # Read frame from opencv
        ret, frame = self.capture.read()
        frame = frame[120:120+250, 200:200+250, :]

        # Flip horizontall and convert image to texture
        buf = cv2.flip(frame, 0).tostring()
        img_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        img_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.web_cam.texture = img_texture

    def compare_faces(self, *args):

        cwd = str(os.getcwd())

        sourceFile=os.path.join(cwd, 'input_image', 'input_image.jpg')
        targetFile=cwd+'\input_image\input_image'+str(user_id)+'.jpg'

        client=boto3.client('rekognition')
    
        imageSource=open(sourceFile,'rb')
        imageTarget=open(targetFile,'rb')

        response=client.compare_faces(SimilarityThreshold=80,
                                    SourceImage={'Bytes': imageSource.read()},
                                    TargetImage={'Bytes': imageTarget.read()})
        
        for faceMatch in response['FaceMatches']:
            position = faceMatch['Face']['BoundingBox']
            similarity = str(faceMatch['Similarity'])
            print('The face at ' +
                str(position['Left']) + ' ' +
                str(position['Top']) +
                ' matches with ' + similarity + '% confidence')

        imageSource.close()
        imageTarget.close()     
        return len(response['FaceMatches']) 

    # Verification function to verify person
    def verify(self, *args):

        # save input image from our webcam
        cwd = str(os.getcwd())
        SAVE_PATH=os.path.join(cwd, 'input_image', 'input_image.jpg')
        ret, frame = self.capture.read()
        frame = frame[120:120+250, 200:200+250, :]
        cv2.imwrite(SAVE_PATH, frame)
        print("saved image")

        face_matches=self.compare_faces()
        if int(face_matches)!=0:
            cam_app.screen_manager.current = 'Home'
        else:
            cam_app.screen_manager.current = 'Login'
        print("Face matches: " + str(face_matches))

        return 0
    
    #mysql credentials verification
    def verify_cred(self, *args):
        self.create_server_connection("localhost","uname","pswd")

    def create_server_connection(self, host_name, user_name, user_password):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")
        
        #self.execute_query(connection, "CREATE DATABASE db;")
        self.execute_query(connection, "USE db;")

        #self.execute_query(connection, "create table tab(id int PRIMARY KEY AUTO_INCREMENT, username varchar(25) NOT NULL, password varchar(25) NOT NULL);")
        #self.execute_query(connection,'insert into tab(username, password) values("ashna","67@Secret");')

        query='select id from tab where username="'+str(username)+'" and password="'+str(password)+'";'
        #print(query)       

        mycursor = connection.cursor()

        try:
            mycursor.execute(query)
            myresult = mycursor.fetchall()
            global user_id
            user_id=int(myresult[0][0])
            print(user_id)
            cam_app.screen_manager.current = 'FaceRec'
            
        except Error as err:
            print(f"Error: '{err}'")
   
        return connection

    def execute_query(self, connection, query):
        
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            connection.commit()
            print("Query successful")
        except Error as err:
            print(f"Error: '{err}'")

class LoginPage(layout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main layout components 
        self.username = TextInput(text='Username', multiline=False, size_hint=(1,.1))
        self.password = TextInput(text='Password', multiline=False, password=True, size_hint=(1,.1))
        self.button = Button(text="Submit", on_press=self.submit, size_hint=(1,.1), background_color=black, font_size=18)
        self.title_label = Label(text="Login", size_hint=(1,.1), font_size=18)

        # Add items to layout
        self.add_widget(self.title_label)
        self.add_widget(self.username)
        self.add_widget(self.password)
        self.add_widget(self.button)

    def submit(self, *args):

        global username
        username=str(self.username.text)
        global password
        password=str(self.password.text)

        #password validation using regex
        #Conditions for a valid password are: Should have at least one number, Should have at least one uppercase and one lowercase character, Should have at least one special symbol, Should be between 6 to 20 characters long,
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        # compiling regex
        pat = re.compile(reg)
        # searching regex                 
        mat = re.search(pat, password)
        # validating conditions
        if mat and username!="":
            cam_app.facerec_page.verify_cred()
        else:
            print("Password or Username invalid !!")
            username=""
            password=""  

class HomePage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2

        # Add items to layout
        self.add_widget(Label(text ='Super', font_size=24))
        self.add_widget(Label(text ='App', font_size=24))
        self.add_widget(Button(text ='PhonePe'))
        self.add_widget(Button(text ='Decathlon', background_color=black))
        self.add_widget(Button(text ='Food Delivery', background_color=black))
        self.add_widget(Button(text ='Cab Booking'))

class CamApp(App):
    def build(self):

        self.screen_manager = ScreenManager()

        # Info page
        self.login_page = LoginPage()
        screen = Screen(name='Login')
        screen.add_widget(self.login_page)
        self.screen_manager.add_widget(screen)

        self.facerec_page= FaceRecPage()
        screen = Screen(name='FaceRec')
        screen.add_widget(self.facerec_page)
        self.screen_manager.add_widget(screen)

        self.home_page= HomePage()
        screen = Screen(name='Home')
        screen.add_widget(self.home_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

if __name__ == '__main__':
    cam_app=CamApp()
    cam_app.run()
