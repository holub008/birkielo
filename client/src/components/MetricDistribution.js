import React from 'react';

import {
    XYPlot,
    XAxis,
    YAxis,
    VerticalBarSeries
} from 'react-vis';

function MetricDistribution(props) {

    const metrics = props.totalDistribution.map(bin => {
        return({
            x: bin.lower,
            y: bin.count,
        })
    })

    const yDomain = metrics.reduce(
        (res, row) => {
            return {
                max: Math.max(res.max, row.y),
                min: Math.min(res.min, row.y)
            };
        },
        {max: -Infinity, min: Infinity}
    );

    return(
        <XYPlot
            width={300}
            height={300}
            yDomain={[yDomain.min, yDomain.max]}
        >
            <VerticalBarSeries className="vertical-bar-series-example" data={metrics} />
            <XAxis />
            <YAxis />
        </XYPlot>
    );
}

export default MetricDistribution;