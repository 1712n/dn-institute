const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Welcome to the AI Product Development Kit!');
});

app.listen(port, () => {
  console.log(`AI Product Kit app listening at http://localhost:${port}`);
});