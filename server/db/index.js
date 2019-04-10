const { Pool } = require('pg');

// note this relies on environment variables being set for host, port, user, and db
// in current deployment, password is injected via pgpass file
// if config fails, bounce will fail fast
const pool = new Pool();

module.exports = {
    query: async (preparedStatement) => {
        const start = Date.now();
        return pool.query(preparedStatement)
            .then(rs =>  {
                console.log('executed query', { queryName: preparedStatement.name,
                    duration: Date.now() - start, rowCount: rs ? rs.rowCount : -1 });
                return rs;
            });
    },
};