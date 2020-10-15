Rack.app.maintcal.calendar.fillList = function (view, doc) {
    // Number of days to fetch at one time
    this.chunkSize = 7;
    this.doc = doc;
    this.range_start = null;
    this.range_end = null;
    this.calendar_id = null;
    this.currentTZ = null;
    this.hidden_states = null;
    this.has_data = false;

    // Use the existing ticket task
    this.getTicketsTask = new Rack.app.maintcal.ticket.getTickets(view, doc);

    this.start = function (start_year, start_month, calendar_id, 
            currentTZ, hidden_states) {
        // Note that the start_year and start_month params are ignored.
        if (!this.range_start) {
            this.range_start = new Date().clearTime();
        }
        if (!this.range_end) {
            this.range_end = this.range_start.add(Date.DAY, this.chunkSize);
        }
        this.range_start = new Date(Math.min(this.range_start, doc.range_start));
        this.range_end = new Date(Math.max(this.range_end, doc.range_end));
        if (calendar_id !== undefined) {
            this.calendar_id = calendar_id;
        }
        if (currentTZ !== undefined) {
            this.currentTZ = currentTZ;
        }
        if (hidden_states !== undefined) {
            this.hidden_states = hidden_states;
        }
        // Run the task
        this.getTicketsTask.start(this.range_start, this.range_end, this.calendar_id, 
            this.currentTZ, this.hidden_states, false);
        this.setGridTitle();
        this.has_data = true;
    };
    
    this.addMore = function () {
        var range_start = this.range_start;
        var range_end = this.range_end.add(Date.DAY, this.chunkSize);
        //Save the new range end 
        this.range_end = range_end;
        this.getTicketsTask.start(range_start, range_end, this.calendar_id, 
            this.currentTZ, this.hidden_states, false);
        this.setGridTitle();
    };

    this.restart = function() {
        // Only run if we've already fetched some data
        if (this.has_data) {
            this.start();
        }
    };

    this.setGridTitle = function() {
        // The view passed in is the calendar view. We want the list view
        view.listView.setTitle("Scheduled Services for " + this.range_start.format("M. d, Y") + 
            " - " + this.range_end.format("M. d, Y"));
    };
};

