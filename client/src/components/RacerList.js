import React from 'react';

import {
    DataTable,
    Anchor,
} from "grommet";
import {Link} from 'react-router-dom';

const columns = [
    {
        property: "rank",
        header: "Rank",
        primary: true,
    },
    {
        property: "first_name",
        header: "Racer",
        render: datum =>
            <Anchor align="center">
                <Link to={`/racer/${datum.racer_id}`}
                      style={{color:"rgb(144,96,235)"}}>{
                    `${datum.first_name} ${datum.middle_name ? datum.middle_name : ""} ${datum.last_name}`}
                </Link>
            </Anchor>,
    },
    {
        property: "elo",
        header: "Birkielo",
        render: datum =>
            datum.elo.toFixed(1)
    },
];

function RacerList(props) {
    return(
        <DataTable columns={columns} data={props.racers} size="large"/>);
}

export default RacerList;