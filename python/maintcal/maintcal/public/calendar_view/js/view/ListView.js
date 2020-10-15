/*
    The classes that make up the list view of the maintenance calendar
*/
Ext.namespace("Rack.app.maintcal.ListView");

var handleTicketAssignmentFromListView = function(serviceID) {
    this.listViewGrid.handleAssign(serviceID, this);
};

Rack.app.maintcal.ListView = function (calendar_view) {

    this.calendar_view = calendar_view;
    window.listViewGrid = this;

    this.addEvents({
        dataerror: true,
        activate: true,
        assignee_picked: true
    });

    // add listener to listen for data error events from ticket view thingies.
    this.on("dataerror", calendar_view.showDataError, calendar_view);
    this.on("assignee_picked", this.assignToTicket);
    var config = {};

    var timeSpanRenderer = function(value, meta, rec) {
        var start = timeTupleToDate(value);
        var startTZ = value.slice(-1);
        var ett = rec.get("end_time_time_tuple");
        var service_type = rec.get("service_type");
        var end = timeTupleToDate(ett);
        var endTZ = ett.slice(-1);
        var ret = "<b>" + start.format("g:i A ") + startTZ + " - " + end.format("g:i A ") + endTZ + "</b><br>" +
            "&nbsp;&nbsp;&nbsp;&nbsp;" + service_type;
        return ret;
    };

    var ticketLinkRenderer = function(value, meta, rec) {
        var ticketURL = rec.get("ticket_url");
        var ret = "<a href='" + ticketURL + "' target='new'>" + value + "</a>";
        return ret;
    };

    var accountRenderer = function(value, meta, rec) {
        var accountURL = rec.get("account_url");
        var accountName = rec.get("account_name");
        var ret = value + ": " + "<a href='" + accountURL + "' target='new'>" + Ext.util.Format.ellipsis(accountName, 34) + "</a>";
        return ret;
    };

    var assigneeRenderer = function(value, meta, rec) {
        if (!value) {
            ret = "<i>Unassigned</i>";
        } else {
            ret = value;
        }
        ret = "<a href='javascript:handleTicketAssignmentFromListView(" + rec.id + ")'>" + ret + "</a>";
        return ret;
    };

    var startDateRenderer = function(value, meta, rec) {
        var year = value.slice(0,4);
        var month = value.slice(4,6) - 1;
        var day = value.slice(6,8);
        var displayDate = new Date(year, month, day);
        var dateString = displayDate.format("M. d, Y");
        return dateString;
    };

    var cm = new Ext.grid.ColumnModel([
        {dataIndex: "start_date", header: "Scheduled services for", hidden: true, renderer: startDateRenderer},
        {dataIndex: "start_time_time_tuple", header: "Service", renderer: timeSpanRenderer, width: 180},
        {dataIndex: "ticket", header: "Ticket", renderer: ticketLinkRenderer, width: 85},
        {dataIndex: "ticket_assignee", header: "Assigned To", renderer: assigneeRenderer, width: 120},
        {dataIndex: "account_id", header: "Account", renderer: accountRenderer, width: 250},
        {dataIndex: "support_team", header: "Team", width: 50, renderer: function (team_name) { return team_name.slice(5); }},
        {dataIndex: "state", header: "State", width: 80}
    ]);

    var moreButton = new Ext.Button({
        text: "More...",
        handler: this.getMore,
        scope: this
    });

    Ext.apply(config, {
        monitorWindowResize: false,
        store: this.calendar_view.doc.tickets,
        cm: cm,
        view: new Ext.grid.GroupingView({
            forceFit: false,
            groupTextTpl: "{text}"
        }),
        buttons: [moreButton],
        frame:true,
        title: "Scheduled services",
        iconCls: 'icon-grid',
        autoScroll: true,
        stripeRows: true
    });
    Ext.grid.GridPanel.call(this, config);
};

Ext.extend(Rack.app.maintcal.ListView, Ext.grid.GridPanel, {
    dateFormat: "M. d, Y",
    timeFormat: "G:i", 
    dateAbbrevFormat: "n/j",

    handleAssign: function(serviceID) {
        this._assignServiceID = serviceID;
        var store = this.getStore();
        var rec = store.getById(serviceID);
        var ticket = rec.get("ticket");
        this.assigneeID = null;
        this.showAssignDialog(ticket);
    },

    showAssignDialog: function(ticket) {
        var actorStore = new Ext.data.Store( {
            storeId: "actorStore",
            proxy: new Ext.data.HttpProxy({
                url: "/maintcal/tickets/actors_on_ticket/" + ticket,
                method: "GET"
            }),
            reader: new Ext.data.JsonReader({
                root: "rows",
                totalProperty: "total"
            })
        });
        actorStore.load();

        this.actorCombo = new Ext.form.ComboBox({
            store: actorStore,
            fieldLabel: "Assign To",
            typeAhead: true,
            typeAheadDelay: 100,
            displayField: "name",
            valueField: "id",
            mode: "local",
            hideTrigger: true,
            triggerAction: "all",
            selectOnFocus: true
        });
        this.assignButton = new Ext.Button({
            text: "Assign",
            tooltip: "Assign to the selected name",
            handler: function () {
                if (!this.validSelection()) {
                    alert("'" + this.actorCombo.getRawValue() + "' is not a valid name");
                    return;
                }
                this.assigneeID = this.actorCombo.getValue();
                dlg.close();
                this.fireEvent("assignee_picked", ticket);
            },
            scope: this
        });
        var fp = new Ext.form.FormPanel({
            autoWidth: true,
            autoHeight: true,
            labelWidth: 60,
            bodyStyle:'padding:15px 15px 0',
            buttons: [this.assignButton]
        });
        fp.add(this.actorCombo);

        var dlg = new Ext.Window({
            width: 400,
            height: 300,
            layout: "fit",
            title: "Assign Ticket #" + ticket,
            buttons: [
                {
                    text: "Assign to Me",
                    tooltip: "Take this ticket",
                    handler: function () {
                        this.assigneeID = "self";
                        dlg.close();
                        this.fireEvent("assignee_picked", ticket);
                    },
                    scope: this
                },
                {
                    text: "Unassign",
                    tooltip: "Unassign this ticket",
                    handler: function () {
                        this.assigneeID = -1;
                        dlg.close();
                        this.fireEvent("assignee_picked", ticket);
                    },
                    scope: this
                },
                {
                    text: "Cancel",
                    tooltip: "Exit without changing ticket assignment",
                    handler: function () {
                        this.assigneeID = null;
                        dlg.close();
                        this.fireEvent("assignee_picked", ticket);
                    },
                    scope: this
                }
            ]
        });
        dlg.add(fp);
        dlg.doLayout();
        this.assigneeID = null;

        dlg.show();
    },

    validSelection: function() {
        var store = this.actorCombo.store;
        var val = this.actorCombo.getValue();
        var rawval = this.actorCombo.getRawValue();
        var rec = store.getById(val);
        var validName = false;
        if (rec) {
            recname = rec.get("name");
            validName = (recname === rawval);
        }
        return validName;
    },

    assignToTicket: function(ticket) {
        id = this.assigneeID;
        if (!id) {
            return;
        }
        // Necessary for the AJAX call, as None cannot be marshalled across XMLRPC
        if (id === -1) {
            id = 0;
        }
        this.viewBody = Ext.get(document.body);
        if (!this.viewBody.isMasked()) {
            this.viewBody.mask("Assigning ticket ...");
        } else {
            this.viewBody = null;
        }
        Ext.Ajax.request({
            url: "/maintcal/tickets/assign/" + ticket + "/" + id,
            method: "POST",
            timeout: 60000,
            success: this.assign_success,
            failure: this.assign_failure,
            scope: this
        });
    },

    assign_success: function(resp, url) {
        var store = this.getStore();
        var rec = store.getById(this._assignServiceID);
        var assignee = resp.responseText;
        rec.set("ticket_assignee", assignee);
        if (this.viewBody && this.viewBody.isMasked()) {
            this.viewBody.unmask();
        }
        if (assignee === "") {
            alert("The ticket has been unassigned");
        } else {
            alert("The ticket has been assigned to: " + resp.responseText);
        }
    },

    assign_failure: function(errResponse, url) {
        alert("Could not assign ticket. Are you sure that you have permission to assign this ticket?");
        if (this.viewBody && this.viewBody.isMasked()) {
            this.viewBody.unmask();
        }
    },

    onActivate: function() {
        this.fillListTask.restart();
    },

    _restoreStore: function() {
        var grd = this._gridToUpdate;
        grd.reconfigure(grd._holdStore, grd._holdCM);
        grd.getView().refresh();
    },
    
    loadTickets: function() {
        this.hasData = false;
    },

    addTickets: function () {
        this.setTitle("Scheduled services for: " + this.calendar_view.getCurrentCalName());
    },

    getMore: function() {
        // This task was assigned by the calendarView, not in this file
        this.fillListTask.addMore(); 
    }
});


