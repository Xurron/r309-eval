"""
Information :
Utilisation de PyQt6
La gestion des erreurs se fait lors du lancement du serveur et vérifie si le port est déjà utilisé ou non.

Question 1 : Pour un arrêt parfait, il faudrait faire une boucle et la faire passer à False pour qu'il n'y ait plus de réception de message et arrêter proprement le processus.
Question 2 : Mon programme prend déjà en charge l'utilisation de plusieurs clients (c'est ce que j'ai fais durant tout mes TP, donc j'ai juste repris mon dernier code).
"""

import sys

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

import socket
import threading

class Server:
    def __init__(self, gui, host: str = '127.0.0.1', port: int = 10000, client_max: int = 5):
        self.host = host
        self.port = port
        self.client_max = client_max
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.state = False
        self.gui = gui

    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Serveur démarré sur {self.host}:{self.port} et accepte {self.client_max} clients maximums.")
            self.state = True
            self.__accept()
        except OSError:
            print(f"L'adresse est déjà utilisée ! Il faut changer de port pour continuer.")
        except Exception as e:
            print(f"Une erreur est survenue lors du lancement du serveur : {e}")

    def __accept(self):
        while self.state:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"Nouveau client connecté : {client_address}")
                self.clients.append(client_socket)
                threading.Thread(target=self.__reception, args=(client_socket,)).start()
            except:
                break

    def __reception(self, client_socket):
        while self.state:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message == "deco-server":
                    print(f"deco-server")
                print(f"Message reçu : {message}")
                MainWindow.AjouterMessage(self.gui, message)
            except:
                self.remove_client(client_socket)
                break

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)
            client_socket.close()

    def remove_all_client(self):
        for client in self.clients:
            self.remove_client(client)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        self.grid = QGridLayout()
        self.widget.setLayout(self.grid)

        self.setWindowTitle("Le serveur de tchat")

        self.Server = QLabel("Serveur")
        self.ServerValue = QLineEdit("")

        self.Port = QLabel("Port")
        self.PortValue = QLineEdit("")

        self.NombreClient = QLabel("Nombre de clients maximum")
        self.NombreClientValue = QLineEdit("")

        self.StatusServer = QPushButton("Démarrage du serveur")

        self.AffichageMessage = QTextEdit("")
        self.AffichageMessage.setReadOnly(True)

        self.Quitter = QPushButton("Quitter")

        self.grid.addWidget(self.Server, 0, 0)
        self.grid.addWidget(self.ServerValue, 0, 1)
        self.ServerValue.setText("0.0.0.0")

        self.grid.addWidget(self.Port, 1, 0)
        self.grid.addWidget(self.PortValue, 1, 1)
        self.PortValue.setText("4200")

        self.grid.addWidget(self.NombreClient, 2, 0)
        self.grid.addWidget(self.NombreClientValue, 2, 1)
        self.NombreClientValue.setText("5")

        self.grid.addWidget(self.StatusServer, 3, 0, 1, 0)
        self.StatusServer.sizeHint()

        self.grid.addWidget(self.AffichageMessage, 4, 0, 1, 0)

        self.grid.addWidget(self.Quitter, 5, 0, 1, 0)

        self.StatusServer.clicked.connect(self.__actionStatusServer)
        self.Quitter.clicked.connect(self.__actionQuitter)

        self.ThreadServer = None

    def __demarrage(self, host, port, clients):
        self.server = Server(self, host, port, clients)
        self.server.start()

    def __actionStatusServer(self):
        if self.StatusServer.text() == "Démarrage du serveur":
            self.StatusServer.setText(str("Arrêt du serveur"))

            host = self.ServerValue.text()
            port = int(self.PortValue.text())
            clients = int(self.NombreClientValue.text())

            print(host, port, clients)
            self.AjouterMessage(f"{host}, {port}, {clients}")

            self.ThreadServer = threading.Thread(target=self.__demarrage, args=(host, port, clients))
            self.ThreadServer.start()
        elif self.StatusServer.text() == "Arrêt du serveur":
            self.server.remove_all_client()
            self.ThreadServer.join(2)
            self.StatusServer.setText(str("Démarrage du serveur"))
            self.ThreadServer = None

    def __actionQuitter(self):
        if self.ThreadServer:
            self.server.remove_all_client()
            self.ThreadServer.join(2)
            self.StatusServer.setText(str("Démarrage du serveur"))
        else:
            pass
        QCoreApplication.exit(0)

    def AjouterMessage(self, message):
        self.AffichageMessage.insertPlainText(message + "\r")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()