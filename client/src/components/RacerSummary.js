import React from 'react';

import Spinner from './Spinner';

import {callBackend, isEmpty} from "../util/data";

class RacerSummary extends React.Component {

    state = {
        racerData: {},
    };

    componentDidMount() {
        callBackend("/api/racer/" + this.props.racerId)
            .then(data => this.setState({ racerData: data }))
            // TODO dumping to console isn't a great long term solution
            .catch(error => console.log(error));
    }

    render() {
        if (isEmpty(this.state.racerData)) {
            return(
                <Spinner/>
            );
        }

        return(
            <div>
                {
                    JSON.stringify(this.state.racerData)
                }
            </div>
        )
    }
}

export default RacerSummary;