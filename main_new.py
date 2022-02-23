#! /nfs/site/disks/stdlib_infra_cadroot_opensource_0001/python/pyBin/bin/python

from urllib import request
from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
import random, threading, webbrowser
import argparse
import sys, os, csv, json

parser = argparse.ArgumentParser()
parser.add_argument("--cellname", "-c", help = "Enter the name of the cell after -c")
args = parser.parse_args()

app = Flask(__name__)
app.secret_key = 'Prodlib'
ALLOWED_EXTENSIONS = set(['svg'])



#reading config file
f = open('config_new.json')
masterData = json.load(f)

#reading config file
f2 = open('./map/family.map')
mapData = f2

def getRelationsFromMap(fam):
  op = {}
  for ln in mapData :
    if fam in ln:
      line = ln.split()
      op[line[0]] = line[1:]

  if not bool(op):
    f = []
    f.append("none")
    f.append(fam)
    op[fam] = f

  return op


def getLibPath(path):
    for obj in masterData:
        #print('obj', obj)
        if(path == obj["relation"]):
            return obj["path"]


def getLibByFamilyId(fid):
    res = {}
    for obj in masterData:
        if(fid in obj.get("relation")):
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
    print("mtomar",cellres)
    return cellres

def getLayers(cell,path):
    layers = []
    d = path + '/' + cell
    for f in os.listdir(d):
      if (os.path.isfile(d +'/' + f)) :
        layers.append(d +'/' + f)
    return layers

def getLibraryWithFamilies():
    initData = {}
    for obj in masterData:
        libId = obj.get("relation")[0:3]
        familyId = obj.get("relation")[3:10]
        if (libId in initData) and (familyId not in initData[libId]):
            initData[libId].append(familyId)
        else:
            initData[libId] = [familyId]
    return initData

def getRelatedCells(cell_in) :
    print("user provided cell is", cell_in)
    initData = []
    relation  = {}
    relationID = []
    patternID = []
    cells = []
    cell_fam = cell_in[3:10]
    print('cell_fam',cell_fam)
    relations = getRelationsFromMap(cell_fam)
    print('relations',relations)

    for k in relations :
      relationID  = k
      patternID   = relations[k]

    for obj in masterData:
        print( str(relationID),obj.get("relation")    )
        if (str(relationID) in obj.get("relation")):
          #print("I'm inside")
          #print(len(patternID))
          for pattern in patternID :
            #print("pattern",pattern)
            if pattern != "none":
              paths = []
              #print("pattern",pattern)
              paths = obj.get("path")
              #cells = (getCellsByPath(pattern, path))

              for path in paths :
                if len((getCellsByPath(pattern, path))) :
                  for cell in (getCellsByPath(pattern, path)):
                    cell_dict = {}
                    cell_dict["cell"] = cell
                    #cell_dict["path"] = path + '/' +
                    cell_dict["layers"] = getLayers(cell,path)
                    cells.append(cell_dict)


    initData = [relationID, cells]
    print("initData", initData)
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
            "path": libData.get('relation'),
            "layer": layer
        }
    return res


def searchRecords(req):
    print("printing_req", req)
    if 'familyIds' in req and req.get('familyIds'):
        return searchCellsByFamily(req.get('familyIds'))
    elif 'cellIds' in req and req.get('cellIds'):
        return findCellDataByIds(req.get('cellIds'))

def searchCellRecords(req):
    print("printing_req", req)
    if 'familyIds' in req and req.get('familyIds'):
        return searchCellsByFamily(req.get('familyIds'))
    elif 'cellIds' in req and req.get('cellIds'):
        return findCellDataByIds(req.get('cellIds'))

@app.route("/init")
def init():
    return getLibraryWithFamilies()

@app.route("/initRelationView")
def initRelationView():
    res  = {}
    data = getRelatedCells(args.cellname)
    res["relationID"] = data[0]
    res["cellsID"] = data[1]
    print(res)
    return res

@app.route("/initLayersView")
def initLayersView():
    res  = {}
    data = getRelatedCells(args.cellname)
    res["relationID"] = data[0]
    res["cellsID"] = data[1]
    print(res)
    return res

@app.route("/filter", methods=['POST'])
def filter():
    return searchRecords(request.get_json())

@app.route("/filter_input_cell")
def filter_input_cell():
    req = {}
    req["cellIds"]= ["g1iinv000at1n02x5"]
    print("input_cell",req)
    return searchCellRecords(req)


@app.route("/<libId>/<cellID>/<layerId>")
def sendFile(libId, cellID, layerId):
    return send_from_directory(getLibPath(libId)+"/"+cellID+"/", layerId)



@app.route("/file")
def retrunFileFromPath():
    layername = request.args.get('path').split("/")[-1]
    return send_from_directory(request.args.get('path').replace(layername,''),layername)


@app.route("/")
def index():
    if args.cellname:
      return render_template('relationPage.html')
    else:
      return render_template('index.html')


if __name__ == '__main__':
  try:
    port = 5000 + random.randint(0, 999)
    #port1 = 5000 + random.randint(0, 999)
    url = "http://127.0.0.1:{0}".format(port)
    #url1 = "http://127.0.0.1:{0}".format(port1)
    threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
    #threading.Timer(1.25, lambda: webbrowser.open(url1) ).start()
    app.run(port=port, debug=False)
    #app.run(port=port1, debug=False)
  except:
    print("Except")
    port = 5000 + random.randint(0, 999)
    url = "http://127.0.0.1:{0}".format(port)
    threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
    app.run(port=port, debug=False)
