import socket
import os
import configparser
import datetime

def read_file(file_path, mode='r'):
    try:
        with open(file_path, mode) as file:
            return file.read()
    except FileNotFoundError:
        return None

def get_content_type(file_path):
    if file_path.endswith(".html"):
        return "text/html"
    elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
        return "image/jpeg"
    elif file_path.endswith(".png"):
        return "image/png"
    else:
        return "application/octet-stream"

def log_request(ip_address, requested_file, error_code):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp}. {ip_address}, {requested_file}, {error_code}\n"
    with open('server_log.txt', 'a') as log_file:
        log_file.write(log_entry)

# Чтение файла настроек
config = configparser.ConfigParser()
config.read('server_config.ini')

# Получение настроек
port = int(config['Server']['Port'])
working_directory = config['Server']['WorkingDirectory']
max_request_size = int(config['Server']['MaxRequestSize'])

sock = socket.socket()
sock.bind(('', port))
print(f"Using port {port}")
sock.listen(5)

while True:
    conn, addr = sock.accept()
    print("Connected", addr)

    data = conn.recv(max_request_size)
    msg = data.decode()

    print(msg)

    try:
        request_line = msg.split('\r\n')[0]
        requested_file = os.path.join(working_directory, request_line.split(' ')[1][1:])

        if requested_file == working_directory + '/':
            requested_file = os.path.join(working_directory, 'index.html')
        print(requested_file)

        content_type = get_content_type(requested_file)

        if content_type.startswith("text/"):
            file_content = read_file(requested_file)
        else:
            file_content = read_file(requested_file, 'rb')

        if file_content is None:
            response = "HTTP/1.1 404 Not Found\r\n\r\n<h1>404 Not Found</h1>"
            error_code = 404
        else:
            response = "HTTP/1.1 200 OK\r\n"
            response += "Server: SelfMadeServer v0.0.1\r\n"
            response += f"Content-type: {content_type}\r\n"
            response += "Connection: close\r\n\r\n"
            error_code = 200

            if isinstance(file_content, str):
                response = response.encode() + file_content.encode()
            else:
                response = response.encode() + file_content

    except IndexError:
        response = "HTTP/1.1 400 Bad Request\r\n\r\n<h1>400 Bad Request</h1>"
        error_code = 400

    log_request(addr[0], requested_file, error_code)
    conn.send(response)
    conn.close()