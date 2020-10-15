<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html>
  <head>
    <title>${c.title}</title>
  </head>
  <body>
    <h2>Edit Scheduled Maintenance ${c.maint.id}</h2>
    ${h.start_form(h.url_for('maintenances', action='update', id=1), method="PUT")} <br />
    Ticket: ${h.text_field('master_ticket', value=str(c.maint.master_ticket))} <br />
    Description: ${h.text_area('description', size="25x3", content=c.maint.general_description)} <br />
    Expedite Info: ${h.text_area('expedite_text', size="25x3", content=c.maint.expedite)} <br />
    Additional Duration: ${h.text_field('additional_duration_minutes', value=c.maint.additional_duration)} <br />
    Service Type: ${h.text_field('service_type_id', value=c.maint.service_type_id)} <br />
    Employee Contact: ${h.text_field('employee_contact_id', value=c.maint.contact_id)}
    Servers: <br />
      ${h.check_box('servers', value='1')} Server 1 <br />
      ${h.check_box('servers', value='2')} Server 2 <br />
    ${h.submit(value='Update')}
    ${h.end_form()}
  </body>
</html>
