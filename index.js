const express = require('express');
const path = require('path');
const { prepairData, config } = require('./reader');

const app = express();
const port = process.env.PORT || "3000";
config.map(item => {
  app.use(`/${item.name}`, express.static(item.path));
})

const data = prepairData();

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname + '/index.html'));
});

app.get("/list", (req, res) => {
  console.log('datadata', data);
  res.send(data)
});

app.listen(port, () => {
  console.log(`Listening to requests on http://localhost:${port}`);
});