import React, {Fragment} from 'react';

import {XYPlot, XAxis, YAxis, HorizontalGridLines, LineSeries, DiscreteColorLegend} from 'react-vis';
import '../../node_modules/react-vis/dist/style.css';

export const EXTENDED_DISCRETE_COLOR_RANGE = [
    '#12939A',
    '#FF991F',
    '#223F9A',
    '#88572C',
    '#DA70BF',
    '#DDB27C',
    '#F15C17',
    '#125C77',
    '#4DC19C',
    '#776E57',
    '#19CDD7',
    '#17B8BE',
    '#F6D18A',
    '#B7885E',
    '#FFCB99',
    '#F89570',
    '#829AE3',
    '#E79FD5',
    '#1E96BE',
    '#89DAC1',
    '#B3AD9E'
];

function MetricTimeline(props) {

    if (props.timelines.length > EXTENDED_DISCRETE_COLOR_RANGE.length) {
        throw new Error("Attempted to  create a timeline plot with too many series");
    }

    if (props.names.length !== props.timelines.length) {
        throw new Error("Attempted to create a timeline plot with mismatched series and names");
    }

    const dateToEloList = props.timelines.map((timeline, index) => {

        const color = EXTENDED_DISCRETE_COLOR_RANGE[index];

        const pointSeries = timeline.map(point => {
            return({
                x: new Date(point.date).getTime(),
                y: point.elo,
            })
        });

        return({
            color: color,
            points: pointSeries
        });
    });

    const legendItems = props.names.map((name, index) => {
        const timeline = props.timelines[index];
        const latestElo = timeline[0].elo;
        return ({
            title: `${name}: ${latestElo.toFixed(1)}`,
            color: EXTENDED_DISCRETE_COLOR_RANGE[index],
        });
    });

    return(
        <XYPlot
            width={300}
            height={300}
            xType="time"
        >
            <HorizontalGridLines />
            {
                dateToEloList.map((dateToElo, index) => {
                   return(
                       <LineSeries
                        data={dateToElo.points}
                        key={index}
                        color={dateToElo.color}
                       />
                   );
                })
            }
            {
                dateToEloList.length > 1 ?
                    <DiscreteColorLegend items={legendItems} height={200} orientation="vertical"/>
                :
                    <Fragment />
            }
            <XAxis title="Date"/>
            <YAxis title="Birkielo"/>
        </XYPlot>
    );
}

export default MetricTimeline;