const express = require('express');
const path = require('path');
const { searchRecords, config, getLibraryWithFamilys } = require('./reader');

const app = express();
const port = process.env.PORT || "3000";

app.use(
  express.urlencoded({
    extended: true
  })
)
app.use(express.json())


config.map(item => {
  app.use(`/${item.name}`, express.static(item.path));
})


app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname + '/index.html'));
});

app.get("/init", (req, res) => {
  res.send(getLibraryWithFamilys())
});

app.post("/filter", (req, res) => {
  res.send(searchRecords(req.body));
});



const server = app.listen(port, () => {
  const port = server.address().port;
  const url = `http://localhost:${port}`;
  console.log(`Listening to requests on -  ${url}`);
});

process.on('SIGTERM', () => {
  server.close(() => {
    console.log('Process terminated')
  })
})