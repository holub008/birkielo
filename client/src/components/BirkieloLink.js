import React from 'react';

import { Link } from 'react-router-dom';

import {getClickableColor} from "../util/data";

function BirkieloLink(props) {
    return (
        <Link to={props.to}
              style={{textDecoration: "none", color: getClickableColor(), cursor: "pointer"}}>
            {
                props.children
            }
        </Link>
    )
}

export default BirkieloLink;