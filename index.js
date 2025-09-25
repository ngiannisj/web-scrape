const express = require('express');
const { MongoClient } = require('mongodb');
require('dotenv').config();
const app = express();
const port = 3000;

// Serve static files from "public" folder
app.use(express.static('public'));

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});

// MongoDB Atlas connection URI and database/collection names
const uri = process.env.MONGO_URI;
const dbName = 'grants_db';

// GET endpoint to retrieve data from MongoDB Atlas
app.get('/api/data', async (req, res) => {
  const client = new MongoClient(uri, { useUnifiedTopology: true });
  const collectionParam = req.query.collection
  try {
    await client.connect();
    const collection = client.db(dbName).collection(collectionParam);
    const data = await collection.find({}).toArray();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch data' });
  } finally {
    await client.close();
  }
});