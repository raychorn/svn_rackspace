<style type="text/css">
p.maintcal_maintenance{
    /*background:#CCCCCC none repeat scroll 0%;*/
    background-color:#CCCCCC;
    border:1px solid #999999;
    color:black;
    font-size:small;
    font-weight:600;
    padding:3px;
    /*vertical-align:top;*/
}
p.maintcal_maintenance a{
    cursor:pointer;
    text-decoration:underline;
    color:blue;
}
p.maintcal_maintenance+p.maintcal_maintenance{
    margin-top: 10px;
}
p.maintcal_service{
    font-size:small;
    margin-left:10px;
    padding:3px;
}
p.maintcal_service a{
    cursor:pointer;
    text-decoration:underline;
    color:blue;
}
</style>
<div>
%for maint in c.maintenances:
        <p class='maintcal_maintenance'>
            <a onclick=doPopUp("/maintcal/maintenance_view/?mid=${maint.id}","_new",912,763)>${maint.maintenance_category}: ${maint.service_type}</a> (${maint.state})<br />
        </p>
%endfor
%for serv in c.services:
        <p class='maintcal_maintenance'>
            <a onclick=doPopUp("/maintcal/maintenance_view/?mid=${serv.maintenance.id}","_new",912,763)>${serv.maintenance.maintenance_category}: ${serv.maintenance.service_type}</a> (${serv.maintenance.state})<br />
        </p
        <span class='maintcal_service'>
            <a onclick=doPopUp("/maintcal/maintenance_view/?mid=${serv.maintenance.id}&sid=${serv.id}","_new",912,763)>${serv.calendar}</a> (${serv.state})
        </span>
%endfor
</div>
