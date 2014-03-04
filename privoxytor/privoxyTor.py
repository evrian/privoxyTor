import shutil
import errno
import os
import os.path
import sys
import time
import socket
from subprocess import Popen
import urllib2


class PrivoxyTor:
    # Class defining a proxy to work with Tor and Privoxy
    def __init__(self, controlPort, privoxyPort, instance, directory):
        # Creates a proxy based on a pair of a Tor's control port and
        # a Privoxy's listening port
        # controlPort: a Tor's control port
        # privoxyProt: a Privoxy's listening port
        self.proxyHandler = urllib2.ProxyHandler({"http": "127.0.0.1:%s" %
                                                  privoxyPort})
        self.privoxyPort = privoxyPort
        self.__controlPort = controlPort
        self.__path = directory + '/' + str(instance)
        # self.__instance = instance
        # self.__directory = directory

    def newId(self, wait=2):
        # Acquires a new Identity for our connection
        # wait: time to wait (in second)
        # return: nothing
        try:
            tor_ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tor_ctrl.connect(("127.0.0.1", self.__controlPort))
            tor_ctrl.send('AUTHENTICATE "{}"\r\nSIGNAL NEWNYM\r\n'
                          .format("123"))
            response = tor_ctrl.recv(1024)
            if response != '250 OK\r\n250 OK\r\n':
                sys.stderr.write('Unexpected response from Tor control port: \
                                    {}\n'.format(response))
        except Exception, e:
            sys.stderr.write('Error connecting to Tor control port: {}\n'
                             .format(repr(e)))
        time.sleep(wait)

    def killProxy(self):
        pivoxyPidFileName = self.__path + '/privoxy/privoxy.pid'
        privoxyPid = open(pivoxyPidFileName, 'r').read()
        torPidFileName = self.__path + '/tor/tor.pid'
        torPid = open(torPidFileName, 'r').read()
        print "Killing privoxy: %s;" % privoxyPid
        os.kill(int(privoxyPid), 9)
        print "Killing tor: %s;" % torPid
        os.kill(int(torPid), 9)


class PrivoxyTorManager:
    # Class automating the process of configuring and launching multiple
    # instances of Tor and Privoxy
    def __init__(self, controlPort, socksPort, privoxyPort):
        # Creates an instance of PrivoxyTorManager
        # controlPort: starting Control port for 1st Tor instance
        # socksPort: starting Socks port for 1st Tor instance
        # privoxyPort: starting port for 1st Privoxy instance to listen
        # return: Nothing
        self.controlPort = controlPort
        self.socksPort = socksPort
        self.privoxyPort = privoxyPort
        self.rootDir = '/'.join(self.__getWorkingDir().split('/')[:-1])

    def __copyDir(self, src, dst):
        # Copies a directory to another one
        # src: source directory
        # dst: destination one
        # return: Nothing
        try:
            shutil.copytree(src, dst)
        except OSError as exc:  # python >2.5
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else:
                raise

    def create(self, instanceNum):
        # Creates several instances of Tor-Privoxy connections
        # instanceNum: number of instances to create
        # return: a list of PrivoxyTor instances
        print self.rootDir
        directory = self.rootDir + '/instances'
        controlPort = self.controlPort
        privoxyPort = self.privoxyPort

        # remove the previous directory /instances
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

        for i in range(0, instanceNum):
            print 'Creating instance %s' % i
            self.__createInstance(i)

        # wait for circuits established
        time.sleep(10)

        # return list of PrivoxyTor instances
        proxies = {}
        for i in range(0, instanceNum):
            proxies[privoxyPort] = PrivoxyTor(controlPort, privoxyPort, i,
                                              directory)
            controlPort += 2
            privoxyPort += 2

        return proxies

    def __getWorkingDir(self):
        # Gets the current working directory of our script
        # return: The directory containing our script

        ret = os.path.abspath(os.path.join(__file__, os.pardir))
        ret = ret.replace('\\', '/')   # for windows
        return ret

    def __alterFileContent(self, path, newContent):
        # Alters the content of a specific file
        # path: path to the file
        # newContent: new content
        # return: Nothing
        try:
            f = open(path, "w")
            f.write(newContent)
            f.close()
        except:
            pass

    def __createInstance(self, index):
        # Create a new instance of Tor-Privoxy proxy
        # index: Index of the proxy
        # return: Nothing

        print 'Tor: controlPort = %s socksPort = %s\nPrivoxy listenPort=%s\n' \
            % (self.controlPort, self.socksPort, self.privoxyPort)
        directory = '%s/instances/%s' % (self.rootDir, index)

        # Copy the whole directory ./abstract to directory ./instances/<index>
        self.__copyDir(self.rootDir + '/abstract', directory)

        # open tor config file then start it
        with open(directory + '/tor/torrc', 'r') as content_file:
            content = content_file.read()
            content = content % (self.controlPort, self.socksPort)
            self.__alterFileContent(directory + '/tor/torrc', content)
            os.chdir(directory + '/tor/tor')
            cmd = 'src/or/tor -DataDirectory %s -PidFile % s -f ../torrc' % \
                (os.getcwd() + '/', 'tor.pid')
            Popen(cmd, shell=True)

        # do the same thing with privoxy
        with open(directory + '/privoxy/config_multi', 'r') as content_file:
            print directory + '/privoxy/config_multi\n'
            content = content_file.read()
            content = content % (self.privoxyPort, self.socksPort)
            self.__alterFileContent(directory +
                                    '/privoxy/privoxy/config_multi', content)
            os.chdir(directory + '/privoxy/privoxy/')
            print os.getcwd() + ' me\n'
            cmd = './privoxy --no-daemon --pidfile %s config_multi' % \
                (directory + '/privoxy/privoxy.pid')
            print cmd + '\n'
            Popen(cmd, shell=True)

        # Modify ports for the next PrivoxyTor instances
        self.controlPort += 2
        self.socksPort += 2
        self.privoxyPort += 2

        # Restore the working directory
        os.chdir(self.rootDir)
