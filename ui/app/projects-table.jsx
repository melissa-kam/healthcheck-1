import React from 'react';
import ResourceTable from './resource-table';

var ProjectsTable = React.createClass({

    columnTitles: ["Name"],
    columnKeys: ["name"],
    columnLinks: {
        "name": function(project) {
            return "/projects/" + project.id + "/canary";
        }
    },

    render: function() {
        return (
            <ResourceTable resources={this.props.projects}
                           columnTitles={this.columnTitles}
                           columnKeys={this.columnKeys}
                           columnLinks={this.columnLinks} />
        );
    },

});

export default ProjectsTable;
