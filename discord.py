import os
import sys
import socket
import threading
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import  QDesktopWidget
from PyQt5.QtGui import QIcon
from datetime import datetime

client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
nickname=""
target_user=None
emoji_liste=["😀","🤣","☺️","😉","😌","😍","😝","🧐","🥳","😣","😡"]

class loginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Messenger'a giriş yapın")
        self.setWindowIcon(QIcon("dc.ico"))
        self.setGeometry(100, 100, 300, 150)
        self.center()
        #kullanıcıdan nickname isteme kısmı
        self.nickname_input=QtWidgets.QLineEdit(self)
        self.nickname_input.setPlaceholderText("Nickname'inizi girin..")
        self.nickname_input.setGeometry(QtCore.QRect(50,30,200,30))
        #giriş butonu
        self.login_button=QtWidgets.QPushButton("Giriş",self)
        self.login_button.setGeometry(QtCore.QRect(100,80,100,30))
        self.login_button.clicked.connect(self.login)

        #kullanıcının nicknamei girmesini sağladık
    def login(self):
        global nickname
        nickname=self.nickname_input.text()
        if nickname:
            self.close()
            self.chat_window=ChatWindow()
            receive_thread=threading.Thread(target=receive_messages,args=(self.chat_window,))
            receive_thread.start()



            self.chat_window.messega_input.setFocus()
            self.chat_window.show()




    #enter yada return tuşuna basılması halindede giriş sağlanacak
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Return or event.key()==QtCore.Qt.Key_Enter:
            self.login()


#giriş ekranını hizalama fonksiyonu
    def center(self):
        qr=self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class ChatWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        global emoji_liste
        global nickname
        screen=QDesktopWidget().screenGeometry()
        window_width= int(screen.width()/ 2)
        window_height = int(screen.height() / 2)

        #Pencere Ayarları
        self.setWindowTitle("Messenger")
        self.setWindowIcon(QIcon("dc.ico"))
        self.setGeometry(100,100,window_width,window_height)
        self.center()

        #sohbet başlığı ayarları
        self.chat_label=QtWidgets.QLabel("Sohbet",self)
        self.chat_label.setGeometry(QtCore.QRect(10,0,window_width-200,20))
        self.chat_label.setAlignment(QtCore.Qt.AlignCenter)


        #sohbet alanımız
        self.chat_area=QtWidgets.QTextEdit(self)
        self.chat_area.setGeometry(QtCore.QRect(10,30,window_width-200,window_height-180))
        self.chat_area.setReadOnly(1)
        self.chat_area.setStyleSheet("background-color: #F0F0F0; padding: 10px; font-size: 14px; border-radius: 5px;")

        #Aktif kullanıcı başlık etiketleri
        self.user_label=QtWidgets.QLabel("Aktif kullanıcılar",self)
        self.user_label.setGeometry(QtCore.QRect(window_width-180,0,160,20))
        self.user_label.setAlignment(QtCore.Qt.AlignCenter)

        #kullanıcı listesi
        self.user_list=QtWidgets.QListWidget(self)
        self.user_list.setGeometry(QtCore.QRect(window_width-180,30,160,window_height-180))
        self.user_list.setStyleSheet("background-color: #e8e8e8;padding: 10px;font-size: 12px;")
        #menü oluşturacağız
        self.user_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.user_list.customContextMenuRequested.connect(self.show_context_menu)
        #gösterilip gösterilmemesi seçilecek mesaj
        self.mesage_label=QtWidgets.QLabel("",self)
        self.mesage_label.setGeometry(QtCore.QRect(10,window_height-140,window_width-200,20))
        #mesajı herkese yollama
        self.clear_target_button=QtWidgets.QPushButton("X",self)
        self.clear_target_button.hide()
        self.clear_target_button.setGeometry(QtCore.QRect(window_width-180,window_height-140,30,20))
        self.clear_target_button.clicked.connect(self.clear_target)

        #Mesaj yazma kısmı
        self.messega_input=QtWidgets.QLineEdit(self)
        self.messega_input.setGeometry(QtCore.QRect(10,window_height-110,window_width-240,30))
        self.messega_input.setPlaceholderText("Mesajınızı girin:")
        self.messega_input.setStyleSheet("background-color: #fff; padding:5px; font-size: 14px;")

        #emoji butonu
        self.emoji_butonu=QtWidgets.QPushButton("😁",self)
        self.emoji_butonu.setGeometry(QtCore.QRect(window_width-220,window_height-110,40,30))
        self.emoji_butonu.clicked.connect(self.open_emoji_picker)

        #Gönder butonu
        self.send_button=QtWidgets.QPushButton("Mesaj Gönder",self)
        self.send_button.setGeometry(QtCore.QRect(window_width-160,window_height-110,100,30))
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("background-color: #4caf50;  color:#fff ; padding:5px; font-weight: bold; radius:5px")

    def show_context_menu(self,pos):
        menu=QtWidgets.QMenu(self)
        menu.setStyleSheet("QMenu {background-color: #333;color:#fff;}")
        private_msg_action=menu.addAction("Özel mesaj gönder")
        view_profile_action=menu.addAction("Kullanıcı profili görüntüle")
        action=menu.exec_(self.user_list.mapToGlobal(pos))
        if action==private_msg_action:
            self.set_private_message_target()
        elif action==view_profile_action:
            self.view_user_profile()

    def view_user_profile(self):
        selected_user=self.user_list.currentItem()
        if selected_user:
            user_profile=f"Kullanıcı:{selected_user.text()}\n"
            self.view_user_profile()


    def clear_target(self):
        global target_user
        target_user=None
        self.mesage_label.setText("")
        self.clear_target_button.hide()   #yazı yazması durumunda aktif hale getirilecek



    #özel mesaj gönderme
    def set_private_message_target(self):
        global target_user
        selected_user=self.user_list.currentItem()
        if selected_user:
            target_user=selected_user.text()
            if target_user==nickname:
                QtWidgets.QMessageBox.warning(self, "Hata","Kendine mesaj gönderemezsin..")
                target_user=None
                return
            else:
                self.mesage_label.setText(f"{target_user} adlı kişiye özel mesaj gönderiyorsunuz.")
                self.clear_target_button.show()

    def center(self):
        qr=self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def open_emoji_picker(self):
        emoji_dialog=QtWidgets.QDialog(self)
        emoji_dialog.setWindowTitle("Emoji Seçin")
        emoji_dialog.setGeometry(100,100,300,150)
        self.center()
        grid_layout = QtWidgets.QGridLayout(emoji_dialog)
        row,col=0,0
        for emoji in emoji_liste:
            button=QtWidgets.QPushButton(emoji,emoji_dialog)
            button.setFixedSize(40,40)
            button.clicked.connect(lambda _,e=emoji:self.add_emoji(e,emoji_dialog))
            grid_layout.addWidget(button,row,col)
            col+=1
            if col>4:
                col=0
                row+=1

        emoji_dialog.exec_()


    def add_emoji(self,emoji,dialog):
        self.messega_input.setText(self.messega_input.text()+ emoji)
        dialog.accept()

    def upğdate_user_list(self,message):
        users=message.split(':')[1].split(',')
        self.user_list.clear()
        self.user_list.addItems(users)

    def receive_message(self,message):
        if message.startwith("USER_LIST"):
            self.update_user_list(message)
        elif message.startswith("PRIVATE"):
            parts=message.split(":")
            target_user=parts[1]
            private_message=":".join(parts[2:])
            if target_user==nickname:
                self.chat_area.append(f"Size özel olarak gönderilen mesaj:{private_message}")
        else:
            self.chat_area.append(message)
    def closeEvent(self,event):
        client.close()
        event.accept()
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Return or event.key()==QtCore.Qt.Key_Enter:
            self.send_message()

    def send_message(self):
        global target_user
        message=self.messega_input.text()
        if message.strip():
            timestamp=datetime.now().strftime("%H:%M:%S")
            if target_user:
                full_message=f"[{timestamp}] [Özel] {nickname} -> {target_user} {message}]"
                client.send_message(f"PRIVATE{target_user}:{full_message}".encode("utf-8"))
                self.chat_area.append(f"Size özel oalrak {target_user} adlı kişiye mesaj gönderilid: {message}")
            else:
                full_message=f"[{timestamp}] {nickname} : {message}]"
                self.chat_area.append(full_message)
                client.send(full_message.encode("utf-8"))
            self.messega_input.clear()


def receive_messages(chat_window):
    while True:
        try:
            message=client.recv(1024).decode("utf-8")
            if message=="NICK":
                print(nickname)
                client.send(nickname.encode("utf-8"))
            else:
                messages=message.split("!")
                for msg in messages:
                    if msg:
                        chat_window.receive_message(msg)

        except :
            print("Sunucu ile bağlantı koptu..")
            client.close()
            break
def main():
    try:
        client.connect(('localhost',54321))
    except:
        print("Sunucuya bağlanılmadı!")
        sys.exit()

    app = QtWidgets.QApplication(sys.argv)
    login_window = loginWindow()
    login_window.show()
    sys.exit(app.exec_())

main()
