import React from 'react';

import {
    DataTable,
    Text,
} from "grommet";
import {Link} from 'react-router-dom';

import {getClickableColor} from "../util/data";

const alwaysColumns = [
    {
        property: "first_name",
        header: "Racer",
        render: datum => {
            return(
                datum.highlight ?
                    <b>
                        {`${datum.first_name} ${datum.middle_name ? datum.middle_name : ""} ${datum.last_name}`}
                    </b>:
                    <Text align="center">
                        <Link to={`/racer/${datum.racer_id}`}
                              style={{textDecoration: "none", color: getClickableColor()}}>
                            {`${datum.first_name} ${datum.middle_name ? datum.middle_name : ""} ${datum.last_name}`}
                        </Link>
                    </Text>
            );
        },
    },
];

const defaultAdditionalColumns = [
    {
        property: "rank",
        header: "Rank",
        primary: true,
    },
    {
        property: "elo",
        header: "Birkielo",
        render: datum =>
            datum.elo.toFixed(1)
    },
];

function RacerList(props) {
    const additionalColumns = props.additionalColumns ? props.additionalColumns : defaultAdditionalColumns;
    const columns = alwaysColumns.slice().concat(additionalColumns);
    // note the DataTable render in RacerList is atrociously laggy when in react dev mode
    return(<DataTable columns={columns} data={props.racers} size="large"/>);
}

export default RacerList;