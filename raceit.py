from threading import Barrier, Thread
import socket
import ssl
from http.client import parse_headers, HTTPResponse
from urllib.parse import urlparse
import argparse
from os.path import isfile

def init_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def init_sslSocket(host, port):
    context = ssl.create_default_context()

    sock =  socket.create_connection((host, port))
    ssock = context.wrap_socket(sock, server_hostname=host)
    return ssock

def run(req, host, port, scheme, barrier):
    s = init_socket(host, port) if scheme == "http" else init_sslSocket(host, port)
    s.sendall(req[:-2])
    barrier.wait()
    s.sendall(req[-2:])

    res = HTTPResponse(s)
    res.begin()
    s.close()

    status = res.status
    cl = res.getheader("Content-Length")

    print(f"[+] ({status}) content-length: {cl}")
    
    return 0

def single_file(nbThread, fReq, port, url):
    if not isfile(fReq):
        print("[-] - request file does not exist.")
        quit()

    threads = []

    req = open(fReq, "rb").read()

    barrier = Barrier(nbThread)
    for _ in range(nbThread):
        t = Thread(target=run, args=(req,url.hostname, port, url.scheme, barrier,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return 0

def multi_file(nbThread, fReq, port, url):

    for f in fReq:
        if not isfile(f):
            print("[-] - request file : %d does not exist." % f)
            quit()

    threads = []
    nbThread = len(fReq)
    
    barrier = Barrier(nbThread)
    for f in fReq:
        req = open(f, "rb").read()
        t = Thread(target=run, args=(req,url.hostname, port, url.scheme, barrier,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return 0

def main():

    desc = '''Just a simple tool to test race condition on engagement.
    You just take the request intercepted by burp, place it in a file, and provide the url.
    The tool will generate N thread, each one will initiate a socket with the server, and send all the request except the last byte, and wait using barrier.
    When all thread has reach the barrier, they all send the last byte at almost same time, that will enhance the probability of race condition.
    '''

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--thread", "-t",type=int, help="number of thread to use (30 by default)", default=30)
    parser.add_argument("request_file", type=str, help="file containing the raw HTTP request to race. CAUTION: No integrity check is done on the request and will be send as is.")
    parser.add_argument("target",type=str, help="the target URL, this one must conatain at least: scheme, hostname (ex: http://localhost:8080).")

    args = parser.parse_args()

    nbThread =  args.thread
    fReq = args.request_file
    target = args.target

    url = urlparse(target)
    if url.scheme in [None, ''] or url.scheme not in ['http', 'https']:
        print("[-] - URL scheme not supported : %s" % url.scheme)
        quit()
    
    if url.hostname in [None, '']:
        print("[-] - URL hostname not defined")
        quit()


    if url.port in [None, '']:
        port = 80 if url.scheme == "http" else 443
    else:
        port = url.port

    # check if fReq contains multiple request file :


    if "," in fReq:
        fReq = fReq.split(',')
        multi_file(nbThread, fReq, port, url)
    else:
        single_file(nbThread, fReq, port, url)
    
if __name__ == '__main__':
    main()
