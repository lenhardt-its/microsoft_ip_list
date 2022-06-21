import json
import os
import urllib.request
import uuid
# Helper für den Aufruf des Webservices und analysieren der Antwort
def webApiGet(methodName, instanceName, clientRequestId):
    ws = "https://endpoints.office.com"
    requestPath = ws + '/' + methodName + '/' + instanceName + '?clientRequestId=' + clientRequestId
    request = urllib.request.Request(requestPath)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())
# Pfad, wo Client ID, letzte Versionsnummer und alle Ergebnisfiles gespeichert werden
datapath = 'docs/o365/'
# Lese Client ID und Version ein, falls schon eine Datei existiert, andernfalls erstelle eine neue Datei
lastVersion = datapath + '/endpoints_clientid_latestversion.txt'
if os.path.exists(lastVersion):
    with open(lastVersion, 'r') as fin:
        clientRequestId = fin.readline().strip()
        latestVersion = fin.readline().strip()
else:
    clientRequestId = str(uuid.uuid4())
    latestVersion = '0000000000'
    with open(lastVersion, 'w') as fout:
        fout.write(clientRequestId + '\n' + latestVersion)
# Aufruf der Version-Methode zur Überprüfung der aktuellen Version. Wenn sie neuer ist, dann holen der neuen Informationen und eintragen der neuen Version
version = webApiGet('version', 'Worldwide', clientRequestId)
if version['latest'] > latestVersion:
    print('Neue Version der "Office 365 worldwide commercial service instance endpoints" gefunden')
    # Schreibe neue Versions-Nummer in den File
    with open(lastVersion, 'w') as fout:
        fout.write(clientRequestId + '\n' + version['latest'])
    # Rufe die endpoints Methode auf, um die neuen Daten zu bekommen
    endpointSets = webApiGet('endpoints', 'Worldwide', clientRequestId)
    # Filtern der Ergebnisse nach "Allow" und "Optimize" Endpunkten und übertragen des Ergebnisses in Tupel mit IPs, Ports und URLs
    flatIps = []
    for endpointSet in endpointSets:
        if endpointSet['category'] in ('Optimize', 'Allow'):
            ips = endpointSet['ips'] if 'ips' in endpointSet else []
            tcpPorts = endpointSet['tcpPorts'] if 'tcpPorts' in endpointSet else ''
            udpPorts = endpointSet['udpPorts'] if 'udpPorts' in endpointSet else ''
            flatIps.extend([(ip, tcpPorts, udpPorts) for ip in ips])
    # Einträge unique machen und sortieren
    flatIpsSet = set(flatIps)
    flatIps = list(flatIpsSet)
    flatIps.sort()
    # remove existing old lists
    os.system('rm -f ' + datapath + 'tcp*')
    os.system('rm -f ' + datapath + 'udp*')
    # Ausgabe der verschiedenen Port-Listen
    for flatP in flatIps:
        portFileName = ""
        if flatP[1] != "":   # TCP-Ports
            portFileName = portFileName + "tcp_" + flatP[1]
        if flatP[2] != "":   # UDP-Ports
            portFileName = portFileName + "udp_" + flatP[2]
        portfile = datapath + '/' + portFileName + ".txt"
        f = open(portfile, "a")
        f.write(flatP[0] + "\n")
        f.close()
    # Ausgabe der URL-Liste
    flatUrls = []
    for endpointSet in endpointSets:
        if endpointSet['category'] in ('Optimize', 'Allow'):
            urls = endpointSet['urls'] if 'urls' in endpointSet else []
            flatUrls.extend([(url) for url in urls])
    flatUrls.sort()
    urlfile = datapath + "/" + "url.txt"
    f = open(urlfile, "w")
    for flatUrl in flatUrls:
        writeUrl = flatUrl + "\n"
        f.write(writeUrl)
    f.close()
    print('Neue Listen erzeugt!')
else:
    print("Keine neue Version gefunden!")