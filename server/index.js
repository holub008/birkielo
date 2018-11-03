const express = require('express');
const path = require('path');

const app = express();

const port = process.env.PORT || 5000;

/**
 * API endpoints
 */
app.get('/api/test/', (req, res) => {
    data = {
      text: 'Lorem Ipsum',
    };

    res.send(data);
});

/**
 * Serve the client side application
 * We don't expect this endpoint to be hit in dev, where webpack should be serving the hot-reloaded application
 * So, technically this gross conditional check isn't necessary, but it's kept on the off chance of weird bugs
 */
if (process.env.NODE_ENV === 'production') {
    app.use(express.static(path.join(__dirname, '../client/build')));

    // down the line, we need to consider how routing should be handled. for now, allow react to handle everything
    app.get('*', function(req, res) {
        res.sendFile(path.join(__dirname, '../client/build', 'index.html'));
    });
}

app.listen(port, () => console.log(`Listening on port ${port}`));
