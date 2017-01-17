import React from "react";
import {render} from "react-dom";
// import {Provider} from "react-redux";
import {Router, Route, IndexRoute, browserHistory} from "react-router";
// import App from './AppComponents/App';
// import Page from './AppComponents/Page';
// import Main from '../main/static/js/Main';

const rootRoute = {

    childRoutes: [{
        path: '/',
        component: require('./AppComponents/App').default,
        childRoutes: [
            require('../main/static').default
            // require('./routes/Course')
        ]
    }]
};


render((
    <Router history={browserHistory} routes={rootRoute}/>
), document.getElementById('react-app'));
