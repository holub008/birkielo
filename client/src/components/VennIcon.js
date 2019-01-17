import React from 'react';

const HIGHLIGHT_COLOR = "rgb(144,96,235)";
const DULL_COLOR = "rgb(105,105,105)";

/**
 * the pinnacle of the synthesis art and programming...
 */
function VennIcon(props) {
    const fillColor = props.highlight ? HIGHLIGHT_COLOR : DULL_COLOR;

    return(
        props.join === 'inner' ?
            <svg width="35" height="25">
                <circle cx="12" cy="12" r="10" stroke="black" strokeWidth="1" fill="none" />
                <circle cx="22" cy="12" r="10" stroke="black" strokeWidth="1" fill="none" />
                <ellipse cx="17" cy="12" rx="5" ry="8" fill={fillColor} stroke="black" strokeWidth="1"/>
                Nubile browser does not support SVG.
            </svg>
            :
            <svg width="35" height="25">
                <circle cx="12" cy="12" r="10" stroke="black" strokeWidth="0" fill={fillColor} />
                <circle cx="22" cy="12" r="10" stroke="black" strokeWidth="0" fill={fillColor} />
                <circle cx="22" cy="12" r="10" stroke="black" strokeWidth="1" fill="none" />
                <circle cx="12" cy="12" r="10" stroke="black" strokeWidth="1" fill="none" />
                Nubile browser does not support SVG.
            </svg>

    )
}

export default VennIcon;