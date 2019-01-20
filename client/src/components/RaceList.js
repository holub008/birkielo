import React from 'react';

import {
    Box,
    Collapsible,
    Button,
    Text,
} from "grommet";
import { FormDown, FormNext } from "grommet-icons";

import {Link} from 'react-router-dom';

const MenuButton = ({ label, open, submenu, ...rest }) => {
    const Icon = open ? FormDown : FormNext;
    return (
        <Button hoverIndicator="background" {...rest}>
            <Box
                margin={submenu ? { left: "small" } : undefined}
                direction="row"
                align="center"
                pad="xsmall"
            >
                <Icon color="brand" />
                <Text size="small">{label}</Text>
            </Box>
        </Button>
    );
};


class RaceList extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            selectedEventOccurrence: null,
        }
    }

    render() {
        const dateToRace = {};
        this.props.races.forEach(race => {
            const raceYear = (new Date(race.event_date)).getFullYear();
            if (!dateToRace[raceYear]) {
                dateToRace[raceYear] = [];
            }
            dateToRace[raceYear].push(race);
        });

        return(
            Object.keys(dateToRace)
                .sort((a,b) => b - a)
                .map(raceYear => {
                    const isOpen = this.state.selectedEventOccurrence === raceYear;

                    return (
                        <Box key={raceYear}>
                            <MenuButton
                                open={isOpen}
                                label={raceYear}
                                onClick={() => this.setState({selectedEventOccurrence: isOpen ? null : raceYear})}
                            />
                            <Collapsible open={isOpen}>
                                <ul>
                                {
                                    dateToRace[raceYear].map(race =>
                                        <li key={race.race_id}>
                                            <Link to={`/race/${race.race_id}`}
                                                  style={{textDecoration: "none", color:"rgb(144,96,235)"}}>
                                                {
                                                    `${parseFloat(race.distance).toFixed(0)}K - ${race.discipline}`
                                                }
                                            </Link>
                                        </li>
                                    )
                                }
                                </ul>
                            </Collapsible>
                        </Box>
                    );
                })
        );
    }
}

export default RaceList;