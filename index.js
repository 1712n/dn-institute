const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Welcome to the AI Product Development Kit!');
});

app.listen(port, () => {
  console.log(`AI Product Development Kit app listening at http://localhost:${port}`);
});

// TODO: Integrate AI models and functionalities here
// TODO: Connect to GitHub Models for extra functionality
// TODO: Attach social media and share your project with the community