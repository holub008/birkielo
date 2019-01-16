import React, {Fragment} from 'react';

import { RadialChart, Hint } from 'react-vis';
import {callBackend} from "../util/data";

export default class EventRadial extends React.Component {
    state = {
        pieSlices:[],
        hoveredSlice: null,
    };

    processToPieSlices(data) {
        return(data.map((event, ix) => ({
                theta: event.total_entrants,
                // this is a manually determined value (but note, it is close to our expected ELO) to build
                // an informative contrast between events
                color: event.mean_elo,
                name: event.event_name,
                mean_elo: event.mean_elo,
            })
        ));
    }

    componentDidMount() {
        callBackend(`/api/events/share/${this.props.year}`)
            .then(data => this.setState({ pieSlices: this.processToPieSlices(data.shareData) }))
            .catch(error => console.log(error));
    }

    renderSliceHint(){
        const displayData = {};
        displayData['Race'] = this.state.hoveredSlice.name;
        displayData[`${this.props.year} # of Skiers`] = this.state.hoveredSlice.theta;
        displayData['Mean Birkielo'] = this.state.hoveredSlice.mean_elo.toFixed(1);
        return(<Hint x={215} y={170} value={displayData}/>);
    }

    render() {
        if (!this.state.pieSlices) {
            return(<Fragment />);
        }

        return (
            <RadialChart
                innerRadius={95}
                radius={135}
                getAngle={d => d.theta}
                data={this.state.pieSlices}
                onValueMouseOver={v => this.setState({hoveredSlice: v})}
                onSeriesMouseOut={v => this.setState({hoveredSlice: null})}
                width={290}
                height={290}
                padAngle={0.04}
                colorRange={['white', '#12868d']}
                colorType="linear"
            >
                {this.state.hoveredSlice && this.renderSliceHint()}
            </RadialChart>
        );
    }
}