const { Pool } = require('pg');

// note this relies on environment variables being set for host, port, user, and db
// in current deployment, password is injected via pgpass file
// if config fails, bounce will fail fast
const pool = new Pool();

module.exports = {
    query: async (preparedStatement, errorHandler = (e) => { console.log(e) }) => {
        const start = Date.now();

        let resultSet;
        try {
            resultSet = await pool.query(preparedStatement);
            const duration = Date.now() - start;
            console.log('executed query', { queryName: preparedStatement.name, duration, rowCount: resultSet ? resultSet.rowCount : -1 });
        }
        catch(e) {
            errorHandler(e);
        }

        return(resultSet);
    },
};