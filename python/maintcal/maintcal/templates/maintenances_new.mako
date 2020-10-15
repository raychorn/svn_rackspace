<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html>
  <head>
    <title>${c.title}</title>
  </head>
  <body>
    <h2>Create new Scheduled Maintenance</h2>
    ${h.start_form(h.url_for('maintenances'))} <br />
    Ticket: ${h.text_field('master_ticket')} <br />
    Description: ${h.text_area('description', size="25x3")} <br />
    Expedite Info: ${h.text_area('expedite_text', size="25x3")} <br />
    Billing Notes: ${h.text_area('billing_text', size="25x3")} <br />
    Additional Duration: ${h.text_field('additional_duration_minutes')} <br />
    Service Type: ${h.text_field('service_type_id')} <br />
    Employee Contact: ${h.text_field('employee_contact_id')}
    ${h.submit(value='Create')}
    ${h.end_form()}
  </body>
</html>
