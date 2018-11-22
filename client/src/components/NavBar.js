import React from 'react';

import {Link} from 'react-router-dom';

import '../styles/NavBar.css';

function NavBar(props) {
    return(
        <div className="navbar">
                <Link to="/">
                    <img className="navbar-logo" src="/images/logo.png" alt=""/>
                </Link>
        </div>
    );
}

export default NavBar;