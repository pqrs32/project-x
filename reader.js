const fs = require('fs');
const path = require('path');

const config = require('./config.json');


console.log('Config JSON-->', config);

const getLibraryWithFamilys = () => {
    const data = {};
    if (config.length) {
        config.forEach(item => {
            const libId = item.name.slice(0, 3);
            const familyId = item.name.slice(3, 10);
            data[libId] = libId in data ? [... new Set([...data[libId], familyId])] : [familyId];
        })
    }
    return data;
}

function fileReader(dir, files_) {
    files_ = files_ || [];
    var files = fs.readdirSync(dir);
    for (var i in files) {
        var name = path.join(dir + '/' + files[i]);
        if (fs.statSync(name).isDirectory()) {
            fileReader(name, files_);
        } else {
            files_.push(name.replace(path.join(dir + "/"), ''));
        }
    }
    return files_;
}

const getLibByFamilyId = (fid) => {
    return config.find(item => item.name.includes(fid));
}

const searchCellinFolder = (path) => {
    return fs.readdirSync(path).filter(function (file) {
        return fs.statSync(path + '/' + file).isDirectory();
    });
}

const searchCellsByFamily = (fids) => {
    const res = {};
    fids.forEach(family => {
        const libData = getLibByFamilyId(family);
        const cells = libData ? searchCellinFolder(libData.path) : [];
        res[family] = cells.filter(cell => cell.includes(family));
    })
    return res;
}

const findCellDataByIds = (cellIds) => {
    const res = {};
    cellIds.forEach(cell => {
        const libData = getLibByFamilyId(cell.slice(0, 10));
        const layer = libData.path ? fileReader(path.join(libData.path + "/" + cell)) : []
        res[cell] = {
            path: libData.name,
            layer,
        };
    })
    return res;
}

const searchRecords = (search) => {
    console.log(search);
    if (search.familyIds && search.familyIds.length) {
        return searchCellsByFamily(search.familyIds);
    }
    if (search.cellIds && search.cellIds.length) {
        return findCellDataByIds(search.cellIds)
    }

}

module.exports = { searchRecords, config, getLibraryWithFamilys }