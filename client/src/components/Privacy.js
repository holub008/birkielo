import React from 'react';

import { grommet } from "grommet/themes";

import {
    Box,
    Text,
    Anchor,
    Grommet,
    Heading,
} from "grommet";
import BirkieloLink from "./BirkieloLink";

function Privacy(props) {
    return(
      <Grommet theme={grommet}>
          <Box margin="small">
          <Heading margin="small">
              Privacy
          </Heading>
          <Heading size="small" margin="small">
              Results
          </Heading>
          <Text margin="small">
              All results displayed on this site have been obtained from publicly available resources. If you do not
              want your name shown in results or rankings, please&nbsp;
              <BirkieloLink to="/support">contact me</BirkieloLink>, and I'll remove you from the site.
          </Text>
          <Heading size="small" margin="small">
              Browsing
          </Heading>
          <Text margin="small">
              This site does not display third party ads, does not use third party tracking, and does not use cookies.
              Internally, it tracks two activities:
              <ul>
                  <li>
                      the initial page load - this is done to monitor site traffic (total volume, crawlers, etc.)
                  </li>
                  <li>
                      any racer profile page views (i.e. birkielo.com/racer/<i>xxxxx</i>) - this is
                      done in support of an analysis of which racers are typically viewed together
                  </li>
              </ul>
              The data tracked are:
              <ul>
                  <li>user agent</li>
                  <li>ip address</li>
                  <li>racer (for racer profile views)</li>
              </ul>
          </Text>
          </Box>
      </Grommet>
    );
}

export default Privacy;