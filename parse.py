# -*- coding: cp1252 -*-
from bencode import *
from struct import *
import hashlib
import requests
import socket

def client():
    filename = 'C:\Users\Xialin\Documents\CS 3251\BitTorrentClient\Anathema -- Vol18 [mininova].torrent'
    #Get information from .torrent file
        bencodeMetaInfo = get_torrent_info(filename)
        announceKey = get_announce(bencodeMetaInfo)
        length = get_length(bencodeMetaInfo)
        infoDict = get_info(bencodeMetaInfo)
    #Get information to connect to tracker
        encodedInfo = bencode_info(infoDict)
        sha1HashedInfo = hashlib.sha1(encodedInfo).digest()
        peerID = 'vincentlugli1.0sixty'
        announceUrl = announceKey + '?info_hash=' + sha1HashedInfo + '&peer_id=' + peerID + '&port=5100&uploaded=0&downloaded=0&left=' + str(length) + '&compact=1'
        #print(announceUrl)
        announceResponse = requests.get(announceUrl)
        #print(announceResponse.status_code)
    #Parse the tracker response
        content = bdecode(announceResponse.content)
        #print(content)
        peerList = content['peers']
        #print(peerList)
        peerIPs = get_peer_IP_list(peerList)
        peerPorts = get_peer_port_list(peerList)
        # print(peerIPs)
        # print(peerPorts)
    #Connect to peers
        sock = socket.socket()
        host = peerIPs[1]
        port = peerPorts[1]
        handshakeMessage = pack('b19s8s20s20s', 19, 'BitTorrent protocol', '', sha1HashedInfo, peerID)
        print(handshakeMessage)
        sock.connect((host, port))
        sock.send(handshakeMessage)
        print(sock.recv(4096))
        sock.close

def get_torrent_info(filename):
    metainfo_file = open(str(filename), 'rb')
    metainfo = bdecode(metainfo_file.read())
    info = metainfo['info']
    # torrentDir = info['name']
    return metainfo
    # metainfo_file.close()

    # info = metainfo['announce']
    # print info

    # info = metainfo['info']
    # torrentDir = info['name']
    # print torrentDir

    # This one I have output to a file called test.txt
    # info = metainfo['info']
    # print info

def get_announce(metainfo):
    return metainfo['announce']

def get_info(metainfo):
    return metainfo['info']

def get_length(metainfo):
    if ('files' in metainfo['info']):
        files = metainfo['info']['files']
        total = 0
        for filePart in files:
            total += filePart['length']
        return total        
    else:
        return metainfo['info']['length']

def bencode_info(info):
    encodedInfo = bencode(info)
    return encodedInfo

def get_peer_IP_list(hexPeerList):
    peerIPs = []
    ip = ''
    currentByte = 0
    for char in hexPeerList:
        if (currentByte < 4):
            if (currentByte == 0):
                ip = str(ord(char))
            else:
                ip += '.' + str(ord(char))
            currentByte += 1
        elif (currentByte == 4):
            peerIPs.append(ip)
            currentByte = 5
        else:
            currentByte = 0
    return peerIPs

def get_peer_port_list(hexPeerList):
    peerPorts = []
    portNumber = 0
    currentByte = 0
    for char in hexPeerList:
        if (currentByte > 3):
            if (currentByte == 4):
                portNumber = ord(char)*256
                currentByte = 5
            else:
                portNumber += ord(char)
                peerPorts.append(portNumber)
                currentByte = 0
        else:
            currentByte += 1
            
    return peerPorts

client()