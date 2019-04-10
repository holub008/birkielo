import React, {Fragment} from 'react';

import { Sankey, Hint } from 'react-vis';
import { callBackend, isEmpty } from "../util/data";

const BLURRED_LINK_OPACITY = 0.3;
const FOCUSED_LINK_OPACITY = 0.6;

const YEAR = 2018;

/*
inspired by: https://github.com/uber/react-vis/blob/master/showcase/sankey/link-event.js
*/
export default class EventSankey extends React.Component {
    state = {
        activeLink: null,
        nodes: [],
        links: [],
    };

    structureFlowData(data) {
        const dataWithSufficientVolume = data.filter(linkage => linkage.n_racers > 30);

        const eventToDate = {};
        dataWithSufficientVolume.forEach(linkage => {
            eventToDate[linkage.source_event] = linkage.source_date;
            eventToDate[linkage.target_event] = linkage.target_date;
        });

        const eventToIndex = {};
        const nodes = [];
        Object.keys(eventToDate)
            .map(eventName => {
                const date = eventToDate[eventName];
                return([eventName, date])
            })
            .sort((a,b) => {
                return(a[1] < b[1])
            })
            .forEach((event, ix) => {
                eventToIndex[event[0]] = ix;
                // note that, crucially, the insertion order must match the event index
                nodes.push({name: event[0]});
            });

        const links = dataWithSufficientVolume
            .map(linkage => ({
                                source: eventToIndex[linkage.source_event],
                                target: eventToIndex[linkage.target_event],
                                value: linkage.n_racers,
                            }));

        return {links:links, nodes: nodes};
    }

    componentDidMount() {
        callBackend(`/api/events/flow/${YEAR}`)
            .then(data => this.setState(this.structureFlowData(data.flowData)))
            .catch(error => console.log(error));
    }

    renderHint() {
        const {activeLink} = this.state;

        // calculate center x,y position of link for positioning of hint
        const x =
            activeLink.source.x1 + (activeLink.target.x0 - activeLink.source.x1) / 2;
        const y = activeLink.y0 - (activeLink.y0 - activeLink.y1) / 2;

        // because we opt for no node names (they are way too cluttered), we need to plumb them out
        // instead of using activeLink.source/target.name
        const link = this.state.links[activeLink.index];
        const sourceNode = this.state.nodes[link.source];
        const targetNode = this.state.nodes[link.target];

        const hintValue = {
            [`${sourceNode.name} ➞ ${
                targetNode.name
                }`]: `${activeLink.value} skiers`
        };

        return <Hint x={x} y={y} value={hintValue} />;
    }

    render() {
        const {activeLink} = this.state;

        return (this.state.nodes.length === 0) ?
                <Fragment/>
                :
                <Sankey
                    nodes={this.state.nodes.map(d => ({name: ""}))}
                    links={this.state.links.map((d, i) => ({
                        ...d,
                        opacity:
                            activeLink && i === activeLink.index
                                ? FOCUSED_LINK_OPACITY
                                : BLURRED_LINK_OPACITY
                    }))}
                    width={500}
                    height={400}
                    onLinkMouseOver={node => this.setState({activeLink: node})}
                    onLinkMouseOut={() => this.setState({activeLink: null})}
                >
                    {activeLink && this.renderHint()}
                </Sankey>
    }
}