import socket
import threading
#ip adresimiz
HOST = 'localhost'
#bu porta istek atılacak
PORT=12345

#tcp socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sunucuyu başlatma
server.bind((HOST,PORT))
#gelen istekleri dinleme
server.listen()
#gelen istekleri altta tanımlı dizinleri içine atacaz

clients=[]
nicknames=[]

#bağlanan kişilere mesaj gönderme
def broadcast(message, exclude_client=None):
    for client in clients:
        if client != exclude_client:  #aynı kullanıcıya defalarca mesaj göndermeyecek
            client.send(f"{message}!".encode('utf-8'))

#target kullanıcıya gönderilecek mesaj gönderme
def send_private_message(target_nickname, message):
    if target_nickname in nicknames:
        index = nicknames.index(target_nickname)
        target_client = clients[index]
        target_client.send(f"{message}!".encode("utf-8"))

#bağlanan kullanıcıları yazdırma

def update_user_list():
    user_list = "USER_LIST:"+",".join(nicknames)
    broadcast(user_list)

def handle_client(client):

    while True:
        try:
            message = client.recv(1024).decode('utf-8') #PRİVATE:4:Battal nasılsın
            if message.startswith("PRIVATE:"):
                parts = message.split(":")
                target_nickname = parts[1]
                private_message = ":".join(parts[2:])
                send_private_message(target_nickname,private_message)
            else:
                broadcast(message,exclude_client=client)
        except :
            #eğer geridönüş olmamış ve hata varsa kullanıcı dahil olmayacak
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f"{nickname} ayrıldı!")
            nicknames.remove(nickname)
            update_user_list()
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Yeni Bağlantı: {str(address)}")
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        if nickname:
            nicknames.append(nickname)
            clients.append(client)
            print(f'Kullanıcı adı: {nickname}')
            broadcast(f'{nickname} sohbete katıldı!')
            client.send('Sunucuya bağlandın!'.encode('utf-8'))
            update_user_list()
            thread = threading.Thread(target=handle_client,args=(client,))
            thread.start()

print("Sunucu dinleniyor..")
receive()








