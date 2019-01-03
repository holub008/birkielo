import React from 'react';

import {XYPlot, XAxis, YAxis, HorizontalGridLines, LineSeries} from 'react-vis';
import '../../node_modules/react-vis/dist/style.css';

function MetricTimeline(props) {
    const dateToElo = props.timeline.map(point => {
        return({
            x: new Date(point.date).getTime(),
            y: point.elo,
        })
    });

    return(
        <XYPlot
            width={300}
            height={300}
            xType="time"
        >
            <HorizontalGridLines />
            <LineSeries data={dateToElo}/>
            <XAxis>Date</XAxis>
            <YAxis>Birkielo</YAxis>
        </XYPlot>
    );
}

export default MetricTimeline;