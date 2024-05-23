import docker
import time

# Initialisieren Sie den Docker-Client
client = docker.from_env()

# Ziehen Sie das neueste MySQL-Image
print("Pulling MySQL image...")
client.images.pull('mysql:latest')

# Starten Sie den MySQL-Container
print("Starting MySQL container...")
container = client.containers.run(
    'mysql:latest',
    name='mysql-server',
    environment={'MYSQL_ROOT_PASSWORD': 'admin'},
    ports={'3306/tcp': 3306},
    volumes={'mysql-data': {'bind': '/var/lib/mysql', 'mode': 'rw'}},
    detach=True
)

# Warten Sie ein paar Sekunden, damit der Container vollständig gestartet wird
time.sleep(10)

# Überprüfen Sie, ob der Container läuft
print("Checking if the MySQL container is running...")
running_containers = client.containers.list()
for c in running_containers:
    if c.name == 'mysql-server':
        print("MySQL container is running.")
        break
else:
    print("MySQL container is not running.")

# Optional: Verbinden Sie sich mit dem MySQL-Server im Container
# (Dies erfordert, dass Sie das MySQL-Client-Programm installiert haben)
print("Connecting to the MySQL server...")
exec_command = container.exec_run('mysql -u root -pmy-secret-pw', tty=True)
print(exec_command.output.decode())
