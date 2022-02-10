const fs = require('fs');
const path = require('path');

const config = require('./config.json');



console.log('config json', config);


function fileReader(dir, files_) {
    files_ = files_ || [];
    var files = fs.readdirSync(dir);
    for (var i in files) {
        var name = path.join(dir + '/' + files[i]);
        if (fs.statSync(name).isDirectory()) {
            fileReader(name, files_);
        } else {
            files_.push(name);
        }
    }
    return files_;
}


function getFamilies(dir, files) {
    const families = [];
    files.map(file => {
        const f = file.replace(dir, '').slice(0, 7);
        f && families.push(f);
    })
    return [...new Set(families)];
}


const prepairData = () => {
    let res = [];
    if (config?.length) {
        config.forEach(item => {
            let dir = item.path;
            const files = fileReader(dir);
            const families = getFamilies(path.join(dir + "/" + item.name), files);
            res.push({
                id: item.name,
                families: families,
                files: files.map(file => file.replace(path.join(dir + "/"), ''))
            })
        })
    }
    return res;
}

module.exports = { prepairData, config }