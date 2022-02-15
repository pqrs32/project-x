
import json
from cmath import log
from flask import Flask, send_from_directory, request
import os

f = open('config.json')
masterData = json.load(f)

print('config provided :::::',masterData)

def getLibPath(path):
    for obj in masterData:
        print('obj', obj)
        if(path == obj["name"]):
            return obj["path"]


def getLibByFamilyId(fid):
    res = {}
    for obj in masterData:
        if(fid in obj.get("name")):
            res = obj
            break
    return res


def searchCellinFolder(path):
    return [f.path for f in os.scandir(path) if f.is_dir()]


def getCellsByPath(familyId, path):
    cellres = []
    cells = searchCellinFolder(path)
    for cell in cells:
        if(familyId in cell and familyId not in cellres):
            cellres.append(cell.replace(path+"/", ''))
    return cellres


def getLibraryWithFamilies():
    initData = {}
    for obj in masterData:
        libId = obj.get("name")[0:3]
        familyId = obj.get("name")[3:10]
        if (libId in initData) and (familyId not in initData[libId]):
            initData[libId].append(familyId)
        else:
            initData[libId] = [familyId]
    return initData


def searchCellsByFamily(fids):
    cellFinal = {}
    for family in fids:
        libData = getLibByFamilyId(family)
        if libData:
            cellFinal[family] = getCellsByPath(family, libData.get('path'))

    return cellFinal


def fileReader(path):
    return os.listdir(path)


def findCellDataByIds(cellIds):
    res = {}
    for cell in cellIds:
        libData = getLibByFamilyId(cell[0:10])
        layer = fileReader(libData.get('path') + "/" + cell)
        res[cell] = {
            "path": libData.get('name'),
            "layer": layer
        }
    return res


def searchRecords(req):
    if 'familyIds' in req and req.get('familyIds'):
        return searchCellsByFamily(req.get('familyIds'))
    elif 'cellIds' in req and req.get('cellIds'):
        return findCellDataByIds(req.get('cellIds'))


app = Flask(__name__)


@app.route("/init")
def init():
    return getLibraryWithFamilies()


@app.route("/filter", methods=['POST'])
def filter():
    return searchRecords(request.get_json())


@app.route("/<libId>/<cellID>/<layerId>")
def sendFile(libId, cellID, layerId):
    return send_from_directory(getLibPath(libId)+"/"+cellID+"/", layerId)


@app.route("/")
def index():
    return send_from_directory(os.getcwd(), "index.html")


if __name__ == "__main__":
    app.run(debug=True)
